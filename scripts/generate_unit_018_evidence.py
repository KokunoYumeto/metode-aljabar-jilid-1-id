#!/usr/bin/env python3
"""Generate deterministic Unit 018 build/PDF evidence after two clean builds."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
QA_ROOT = ROOT / "qa/unit-018-evidence"
BUILD_A = ROOT / "build/unit-018-build-d"
BUILD_B = ROOT / "build/unit-018-build-e"
QA_A = ROOT / "build/unit-018-qa-a"
QA_B = ROOT / "build/unit-018-qa-b"
JOB = "unit-018-bab-2-latihan"
PDF_A = BUILD_A / f"{JOB}.pdf"
PDF_B = BUILD_B / f"{JOB}.pdf"
PDF_PUBLIC = ROOT / "artifacts" / f"{JOB}.pdf"
RAW_LOG = BUILD_B / f"{JOB}.log"
LOG_PUBLIC = ROOT / "qa/UNIT_018_BUILD_FINAL.log"
CHECKER = ROOT / "scripts/check_unit_018_structure.py"

# Fail-closed placeholders: bind these only after two clean builds, artifact
# installation, PDF inspection, and the all-page visual pass.
EXPECTED_ARTIFACT_BYTES = 83_578
EXPECTED_ARTIFACT_SHA256 = "4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c"
EXPECTED_PAGE_COUNT = 4
EXPECTED_OUTLINES: tuple[str, ...] = ("Latihan",)
EXPECTED_NAMED_DESTINATIONS = 18
EXPECTED_GOTO_ACTIONS = 0
EXPECTED_URI_ACTIONS = 3
VISUALLY_INSPECTED_PAGES: tuple[int, ...] = (1, 2, 3, 4)

EXPECTED_SOURCE_BYTES = 5_197
EXPECTED_SOURCE_SHA256 = "24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce"
EXPECTED_TARGET_BYTES = 6_523
EXPECTED_TARGET_SHA256 = "d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55"
PROVENANCE_MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> dict[str, object]:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT).as_posix()}")
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


def configured() -> None:
    require(EXPECTED_ARTIFACT_BYTES > 0, "bind EXPECTED_ARTIFACT_BYTES after artifact installation")
    require(
        re.fullmatch(r"[0-9a-f]{64}", EXPECTED_ARTIFACT_SHA256) is not None,
        "bind EXPECTED_ARTIFACT_SHA256 after artifact installation",
    )
    require(EXPECTED_PAGE_COUNT > 0, "bind EXPECTED_PAGE_COUNT after the clean build")
    require(EXPECTED_OUTLINES, "bind EXPECTED_OUTLINES after PDF inspection")
    require(EXPECTED_NAMED_DESTINATIONS > 0, "bind named-destination count")
    require(EXPECTED_URI_ACTIONS > 0, "bind URI-action count")
    require(
        VISUALLY_INSPECTED_PAGES == tuple(range(1, EXPECTED_PAGE_COUNT + 1)),
        "record a complete all-page visual pass before final evidence generation",
    )


def sanitize_log() -> dict[str, object]:
    text = RAW_LOG.read_text(encoding="utf-8", errors="replace")
    original_lines = len(text.splitlines())
    replacements = 0
    home = str(Path.home())
    for variant in dict.fromkeys((home, home.replace("\\", "/"))):
        text, count = re.subn(re.escape(variant), "${USER_HOME}", text, flags=re.IGNORECASE)
        replacements += count
    require(home.lower() not in text.lower(), "machine-local home prefix remains in log")
    require(len(text.splitlines()) == original_lines, "log sanitization changed line count")
    LOG_PUBLIC.write_text(text, encoding="utf-8", newline="\n")
    return {
        "method": "complete home-prefix replacement with ${USER_HOME}",
        "replacement_count": replacements,
        "diagnostics_deleted": 0,
        "line_count": original_lines,
    }


def ensure_replay_evidence(build: Path, qa: Path) -> tuple[Path, dict[str, list[Path]]]:
    pdf = build / f"{JOB}.pdf"
    require(pdf.is_file(), f"missing clean build: {pdf}")
    poppler = qa / "poppler"
    mupdf = qa / "mupdf"
    poppler.mkdir(parents=True, exist_ok=True)
    mupdf.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", str(pdf), str(poppler / "page")],
        check=True,
    )
    subprocess.run(
        ["mutool", "draw", "-q", "-r", "150", "-o", str(mupdf / "page-%02d.png"), str(pdf)],
        check=True,
    )
    text = qa / "layout.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(text)], check=True)
    renders = {
        "poppler": sorted(poppler.glob("page-*.png")),
        "mupdf": sorted(mupdf.glob("page-*.png")),
    }
    for renderer, pages in renders.items():
        require(len(pages) == EXPECTED_PAGE_COUNT, f"{renderer}: unexpected render count")
    return text, renders


def copy_render_inventory(
    a: dict[str, list[Path]], b: dict[str, list[Path]]
) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    for renderer in ("poppler", "mupdf"):
        public_dir = QA_ROOT / f"{renderer}-final-b"
        public_dir.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, object]] = []
        for page, (path_a, path_b) in enumerate(zip(a[renderer], b[renderer], strict=True), 1):
            bytes_a = path_a.read_bytes()
            bytes_b = path_b.read_bytes()
            require(bytes_a == bytes_b, f"{renderer} page {page}: clean replay differs")
            public = public_dir / f"page-{page:02d}.png"
            shutil.copyfile(path_b, public)
            require(public.read_bytes() == bytes_b, f"{renderer} page {page}: evidence copy differs")
            records.append(
                {
                    "page": page,
                    "path": public.relative_to(ROOT).as_posix(),
                    "bytes": len(bytes_b),
                    "sha256": sha256(bytes_b).hexdigest(),
                    "matches_clean_build_a": True,
                    "matches_clean_build_b": True,
                    "visually_inspected": page in VISUALLY_INSPECTED_PAGES,
                }
            )
        result[renderer] = records
    return result


def flatten_outlines(items: object) -> list[str]:
    output: list[str] = []
    for item in items:
        if isinstance(item, list):
            output.extend(flatten_outlines(item))
        else:
            output.append(str(getattr(item, "title", item)))
    return output


def pdf_facts(pdf: Path) -> dict[str, object]:
    reader = PdfReader(pdf)
    root = reader.trailer["/Root"]
    mark_info = root.get("/MarkInfo")
    tagged = bool(mark_info and mark_info.get_object().get("/Marked"))
    actions: Counter[str] = Counter()
    subtypes: Counter[str] = Counter()
    annotations: list[int] = []
    for page in reader.pages:
        refs = page.get("/Annots")
        records = refs.get_object() if refs else []
        annotations.append(len(records))
        for ref in records:
            record = ref.get_object()
            subtypes[str(record.get("/Subtype"))] += 1
            action = record.get("/A")
            if action:
                actions[str(action.get_object().get("/S"))] += 1
            elif record.get("/Dest") is not None:
                actions["/Dest"] += 1
    facts = {
        "pages": len(reader.pages),
        "language": str(root.get("/Lang")),
        "encrypted": reader.is_encrypted,
        "tagged": tagged,
        "metadata": {str(key): str(value) for key, value in (reader.metadata or {}).items()},
        "outlines": flatten_outlines(reader.outline),
        "named_destination_count": len(reader.named_destinations),
        "page_text_character_counts": [len(page.extract_text() or "") for page in reader.pages],
        "page_annotation_counts": annotations,
        "annotation_subtypes": dict(subtypes),
        "annotation_actions": dict(actions),
        "page_sizes_points": [
            [round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)]
            for page in reader.pages
        ],
    }
    require(facts["pages"] == EXPECTED_PAGE_COUNT, "PDF page count changed")
    require(facts["language"] == "id-ID", "PDF language is not id-ID")
    require(not facts["encrypted"], "PDF is encrypted")
    require(not facts["tagged"], "PDF unexpectedly claims tagged structure")
    require(all(facts["page_text_character_counts"]), "blank/nonextractable PDF page")
    require(tuple(facts["outlines"]) == EXPECTED_OUTLINES, "outline sequence changed")
    require(facts["named_destination_count"] == EXPECTED_NAMED_DESTINATIONS, "destination count changed")
    require(actions["/GoTo"] == EXPECTED_GOTO_ACTIONS, "GoTo action count changed")
    require(actions["/URI"] == EXPECTED_URI_ACTIONS, "URI action count changed")
    require(
        facts["metadata"].get("/Title")
        == "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 18: Latihan Bab 2",
        "PDF title metadata changed",
    )
    require(facts["metadata"].get("/Author") == "Wen-Wei Li", "PDF author metadata changed")
    return facts


def font_count(pdf: Path) -> int:
    output = subprocess.run(
        ["pdffonts", str(pdf)], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout
    rows = [line for line in output.splitlines()[2:] if line.strip()]
    require(rows, "no fonts reported")
    for row in rows:
        match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", row)
        require(match is not None, f"unparseable pdffonts row: {row}")
        require(match.group(1) == match.group(2) == "yes", "font is not embedded/subset")
    return len(rows)


def log_counts(text: str) -> dict[str, int]:
    patterns = {
        "overfull_boxes": r"Overfull \[hv]box",
        "underfull_hboxes": r"Underfull \\hbox",
        "underfull_vboxes": r"Underfull \\vbox",
        "empty_external_link_targets": r"Suppressing link with empty target",
        "undefined_control_sequences": r"Undefined control sequence",
        "undefined_references": r"undefined references|Reference .* undefined",
        "undefined_citations": r"Citation .* undefined",
        "missing_characters": r"Missing character",
        "fatal_errors": r"Fatal error",
        "emergency_stops": r"Emergency stop",
    }
    counts = {name: len(re.findall(pattern, text, flags=re.IGNORECASE)) for name, pattern in patterns.items()}
    for critical in (
        "overfull_boxes", "undefined_control_sequences", "undefined_references",
        "undefined_citations", "missing_characters", "fatal_errors", "emergency_stops",
    ):
        require(counts[critical] == 0, f"critical log gate failed: {critical}")
    return counts


def main() -> int:
    configured()
    QA_ROOT.mkdir(parents=True, exist_ok=True)

    checker = subprocess.run(
        [sys.executable, "-B", str(CHECKER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(checker.stdout.startswith("PASS Unit 018 structural checker"), "structure checker failed")
    (QA_ROOT / "structure-check.txt").write_text(checker.stdout, encoding="utf-8", newline="\n")

    artifact = PDF_PUBLIC.read_bytes()
    require(len(artifact) == EXPECTED_ARTIFACT_BYTES, "artifact byte count changed")
    require(sha256(artifact).hexdigest() == EXPECTED_ARTIFACT_SHA256, "artifact hash changed")
    require(artifact == PDF_B.read_bytes(), "installed artifact does not equal clean build B")
    container_byte_identity = PDF_A.read_bytes() == PDF_B.read_bytes()

    text_a, renders_a = ensure_replay_evidence(BUILD_A, QA_A)
    text_b, renders_b = ensure_replay_evidence(BUILD_B, QA_B)
    require(text_a.read_bytes() == text_b.read_bytes(), "clean extracted-text replay differs")
    renders = copy_render_inventory(renders_a, renders_b)

    sanitization = sanitize_log()
    counts = log_counts(LOG_PUBLIC.read_text(encoding="utf-8", errors="replace"))
    facts = pdf_facts(PDF_PUBLIC)
    fonts = font_count(PDF_PUBLIC)

    inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U018",
        "page_count": EXPECTED_PAGE_COUNT,
        "render_resolution_dpi": 150,
        "build_a": digest(PDF_A),
        "build_b": digest(PDF_B),
        "container_byte_identity": container_byte_identity,
        "extracted_text_sha256_a": sha256(text_a.read_bytes()).hexdigest(),
        "extracted_text_sha256_b": sha256(text_b.read_bytes()).hexdigest(),
        "same_renderer_page_mismatches": {"poppler": 0, "mupdf": 0},
        "renderers": renders,
        "provenance_model": PROVENANCE_MODEL,
    }
    (QA_ROOT / "render-hash-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    qa = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U018",
        "status": "PASS",
        "authority": {
            "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "source_file": "chapter2.tex",
            "source_lines": "1603-1645",
            "source_span_bytes": EXPECTED_SOURCE_BYTES,
            "source_span_sha256": EXPECTED_SOURCE_SHA256,
        },
        "target": {
            "target_span_bytes": EXPECTED_TARGET_BYTES,
            "target_span_sha256": EXPECTED_TARGET_SHA256,
            "han_residue": 0,
        },
        "artifact": digest(PDF_PUBLIC),
        "build_log": digest(LOG_PUBLIC),
        "build_log_sanitization": sanitization,
        "structure_checker": digest(CHECKER),
        "structure_check_output": digest(QA_ROOT / "structure-check.txt"),
        "evidence_generator": digest(Path(__file__)),
        "render_inventory": digest(QA_ROOT / "render-hash-inventory.json"),
        "pdf": facts,
        "embedded_subset_font_count": fonts,
        "log_counts": counts,
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": list(VISUALLY_INSPECTED_PAGES),
            "renderers_inspected": ["Poppler", "MuPDF"],
            "finding": (
                "The centered cover uses an explicit coverage panel without ambiguous filled/unfilled "
                "blocks; all exercise pages use the available text width, and the reader ends with "
                "Exercise 13 without sparse generated back matter."
            ),
        },
        "rights": {
            "principal_text_and_translation": "CC BY 4.0",
            "AJbook_class_fragment": "CC BY-SA 3.0",
            "bundled_noto_fonts": "SIL OFL 1.1",
            "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
        },
        "provenance_model": PROVENANCE_MODEL,
    }
    (QA_ROOT / "structure-and-pdf-qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    summary = "\n".join(
        (
            "PASS Unit 018 final build and replay",
            f"artifact bytes={len(artifact)} sha256={sha256(artifact).hexdigest()} pages={EXPECTED_PAGE_COUNT}",
            f"build A bytes={PDF_A.stat().st_size} sha256={sha256(PDF_A.read_bytes()).hexdigest()}",
            f"build B bytes={PDF_B.stat().st_size} sha256={sha256(PDF_B.read_bytes()).hexdigest()}",
            "same-renderer replay: Poppler all pages identical; MuPDF all pages identical",
            f"extracted-text replay sha256={sha256(text_a.read_bytes()).hexdigest()}",
            f"PDF: outlines={len(EXPECTED_OUTLINES)} destinations={EXPECTED_NAMED_DESTINATIONS} GoTo={EXPECTED_GOTO_ACTIONS} URI={EXPECTED_URI_ACTIONS} tagged=no language=id-ID",
            f"log counts: {json.dumps(counts, sort_keys=True)}",
            "visual QA: all pages inspected in Poppler and MuPDF; no sparse trailing back matter",
            f"provenance model: {PROVENANCE_MODEL}",
            "",
        )
    )
    (QA_ROOT / "build-log-summary.txt").write_text(summary, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "artifact": digest(PDF_PUBLIC)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
