#!/usr/bin/env python3
"""Generate deterministic Unit 019 build, PDF, and visual-QA evidence."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
QA_ROOT = ROOT / "qa/unit-019-evidence"
BUILD_A = ROOT / "build/unit-019-final-c"
BUILD_B = ROOT / "build/unit-019-final-d"
QA_A = ROOT / "build/unit-019-final-qa-c"
QA_B = ROOT / "build/unit-019-final-qa-d"
JOB = "unit-019-bab-3-definisi-dasar"
PDF_A = BUILD_A / f"{JOB}.pdf"
PDF_B = BUILD_B / f"{JOB}.pdf"
PDF_PUBLIC = ROOT / "artifacts" / f"{JOB}.pdf"
RAW_LOG = BUILD_B / f"{JOB}.log"
LOG_PUBLIC = ROOT / "qa/UNIT_019_BUILD_FINAL.log"
AUTHORITY_SOURCE = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
)
TARGET_SOURCE = ROOT / "repo/source/chapter3.tex"
DRIVER = ROOT / "repo/source/unit-019-bab-3-definisi-dasar.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-019.tex"
CROSSREFS = ROOT / "repo/source/unit-019-crossrefs.aux"

# Fail-closed admission bindings. Bind the PDF/topology values only after two
# clean builds, artifact installation, and an all-page visual pass.
EXPECTED_ARTIFACT_BYTES = 125_710
EXPECTED_ARTIFACT_SHA256 = "af7a4561db5e8ab1798d4475c589beb42f9fb84795bd167c0ffc17241866783a"
EXPECTED_PAGE_COUNT = 12
EXPECTED_OUTLINES: tuple[str, ...] = (
    "3 Kategori Monoidal",
    "3.1 Definisi Dasar",
    "Daftar Pustaka",
    "Indeks Istilah",
    "Indeks Simbol",
)
EXPECTED_NAMED_DESTINATIONS = 52
EXPECTED_GOTO_ACTIONS = 35
EXPECTED_URI_ACTIONS = 3
VISUALLY_INSPECTED_PAGES: tuple[int, ...] = tuple(range(1, 13))

EXPECTED_AUTHORITY_BYTES = 75_571
EXPECTED_AUTHORITY_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
EXPECTED_SOURCE_SPAN_BYTES = 21_745
EXPECTED_SOURCE_SPAN_SHA256 = "4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a"
EXPECTED_TARGET_FILE_BYTES = 79_694
EXPECTED_TARGET_FILE_SHA256 = "bfe5d4745f9a3ac1062b79ee429356a17f3d5bff9be02ef0093eab6978f98e60"
EXPECTED_TARGET_SPAN_BYTES = 25_868
EXPECTED_TARGET_SPAN_SHA256 = "6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac"
PROVENANCE_MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CORRECTION_IDS = ("O013-LI-U019-COR-001",)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def raw_digest(raw: bytes) -> dict[str, object]:
    return {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def digest(path: Path) -> dict[str, object]:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT).as_posix()}")
    result = raw_digest(path.read_bytes())
    result["path"] = path.relative_to(ROOT).as_posix()
    return result


def span_bytes(path: Path, first: int, last: int) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    require(1 <= first <= last <= len(lines), f"invalid span {first}-{last}: {path}")
    return b"".join(lines[first - 1 : last])


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
        "record the complete all-page visual pass before final evidence generation",
    )


def structural_check() -> dict[str, object]:
    authority = AUTHORITY_SOURCE.read_bytes()
    target = TARGET_SOURCE.read_bytes()
    source_span = span_bytes(AUTHORITY_SOURCE, 1, 227)
    target_span = span_bytes(TARGET_SOURCE, 1, 226)
    require(raw_digest(authority) == {"bytes": EXPECTED_AUTHORITY_BYTES, "sha256": EXPECTED_AUTHORITY_SHA256}, "authority file identity changed")
    require(raw_digest(source_span) == {"bytes": EXPECTED_SOURCE_SPAN_BYTES, "sha256": EXPECTED_SOURCE_SPAN_SHA256}, "authority span identity changed")
    require(raw_digest(target) == {"bytes": EXPECTED_TARGET_FILE_BYTES, "sha256": EXPECTED_TARGET_FILE_SHA256}, "admission-time target file identity changed")
    require(raw_digest(target_span) == {"bytes": EXPECTED_TARGET_SPAN_BYTES, "sha256": EXPECTED_TARGET_SPAN_SHA256}, "target span identity changed")
    require(re.search(rb"[\xe4-\xe9][\x80-\xbf]{2}", target_span) is None, "possible Han residue in target span")

    target_lines = target.splitlines()
    require(len(target_lines) >= 227, "target boundary line is missing")
    require(target_lines[226].startswith("\\section{".encode()), "target line 227 is not the next section")

    driver = DRIVER.read_text(encoding="utf-8")
    cover = COVER.read_text(encoding="utf-8")
    refs = CROSSREFS.read_text(encoding="utf-8")
    require("\\InputSourceLineRange{chapter3.tex}{1}{226}" in driver, "driver range changed")
    require("{1}{227}" not in driver, "driver includes the next section")
    require(PROVENANCE_MODEL in driver and PROVENANCE_MODEL in cover, "model provenance missing")
    require("CC BY 4.0" in driver and "CC BY 4.0" in cover, "license notice missing")
    require("Cakupan parsial unit" in cover, "explicit partial-scope panel missing")
    require("Bagian 3.2" in cover and "belum termasuk" in cover, "partial boundary is not explicit")
    require("filled" not in cover.lower() and "unfilled" not in cover.lower(), "ambiguous progress-block language present")

    internal_labels = set(re.findall(r"\\label\{([^}]+)\}", target_span.decode("utf-8")))
    all_refs = set(re.findall(r"\\(?:ref|eqref|pageref|rref|cref|Cref)\{([^}]+)\}", target_span.decode("utf-8")))
    external_refs = all_refs - internal_labels
    frozen_refs = set(re.findall(r"\\newlabel\{([^}]+)\}", refs))
    require(external_refs == frozen_refs, f"frozen reference closure differs: expected={sorted(external_refs)} actual={sorted(frozen_refs)}")

    output = {
        "authority_file": raw_digest(authority),
        "authority_span": raw_digest(source_span),
        "target_file_at_admission": raw_digest(target),
        "target_span": raw_digest(target_span),
        "target_lines": "1-226",
        "next_target_line": 227,
        "han_residue": 0,
        "external_reference_count": len(external_refs),
    }
    text = (
        "PASS Unit 019 structural check\n"
        f"authority lines=1-227 bytes={len(source_span)} sha256={sha256(source_span).hexdigest()}\n"
        f"target lines=1-226 bytes={len(target_span)} sha256={sha256(target_span).hexdigest()} Han=0\n"
        f"external references={len(external_refs)} frozen exactly; next target line=227 excluded\n"
    )
    (QA_ROOT / "structure-check.txt").write_text(text, encoding="utf-8", newline="\n")
    return output


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
    subprocess.run(["pdftoppm", "-png", "-r", "150", str(pdf), str(poppler / "page")], check=True)
    subprocess.run(["mutool", "draw", "-q", "-r", "150", "-o", str(mupdf / "page-%02d.png"), str(pdf)], check=True)
    text = qa / "layout.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(text)], check=True)
    renders = {
        "poppler": sorted(poppler.glob("page-*.png")),
        "mupdf": sorted(mupdf.glob("page-*.png")),
    }
    for renderer, pages in renders.items():
        require(len(pages) == EXPECTED_PAGE_COUNT, f"{renderer}: unexpected render count")
    return text, renders


def copy_render_inventory(a: dict[str, list[Path]], b: dict[str, list[Path]]) -> dict[str, list[dict[str, object]]]:
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
        == "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 19: Kategori Monoidal - Definisi Dasar",
        "PDF title metadata changed",
    )
    require(facts["metadata"].get("/Author") == "Wen-Wei Li", "PDF author metadata changed")
    return facts


def font_count(pdf: Path) -> int:
    output = subprocess.run(["pdffonts", str(pdf)], check=True, capture_output=True, text=True, encoding="utf-8").stdout
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
    structure = structural_check()

    artifact = PDF_PUBLIC.read_bytes()
    require(len(artifact) == EXPECTED_ARTIFACT_BYTES, "artifact byte count changed")
    require(sha256(artifact).hexdigest() == EXPECTED_ARTIFACT_SHA256, "artifact hash changed")
    require(artifact == PDF_B.read_bytes(), "installed artifact does not equal clean build B")
    bytes_a = PDF_A.read_bytes()
    bytes_b = PDF_B.read_bytes()

    text_a, renders_a = ensure_replay_evidence(BUILD_A, QA_A)
    text_b, renders_b = ensure_replay_evidence(BUILD_B, QA_B)
    require(text_a.read_bytes() == text_b.read_bytes(), "clean extracted-text replay differs")
    renders = copy_render_inventory(renders_a, renders_b)

    sanitization = sanitize_log()
    counts = log_counts(LOG_PUBLIC.read_text(encoding="utf-8", errors="replace"))
    facts = pdf_facts(PDF_PUBLIC)
    fonts = font_count(PDF_PUBLIC)
    container_byte_identity = bytes_a == bytes_b
    deterministic_replay = {
        "semantic_and_render_identity": True,
        "container_byte_identity": container_byte_identity,
        "container_size_delta_b_minus_a": len(bytes_b) - len(bytes_a),
        "container_differing_aligned_byte_count": sum(
            byte_a != byte_b for byte_a, byte_b in zip(bytes_a, bytes_b, strict=False)
        ),
        "container_note": (
            "Raw XeLaTeX PDF containers differ despite fixed metadata; extracted text and every "
            "Poppler/MuPDF page render are identical. No byte-identical container claim is made."
        ),
        "build_a_sha256": sha256(bytes_a).hexdigest(),
        "build_b_sha256": sha256(bytes_b).hexdigest(),
        "extracted_text_sha256_a": sha256(text_a.read_bytes()).hexdigest(),
        "extracted_text_sha256_b": sha256(text_b.read_bytes()).hexdigest(),
        "same_renderer_page_mismatches": {"poppler": 0, "mupdf": 0},
    }

    inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U019",
        "page_count": EXPECTED_PAGE_COUNT,
        "render_resolution_dpi": 150,
        "build_a": digest(PDF_A),
        "build_b": digest(PDF_B),
        "deterministic_replay": deterministic_replay,
        "renderers": renders,
        "provenance_model": PROVENANCE_MODEL,
    }
    (QA_ROOT / "render-hash-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    qa = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U019",
        "status": "PASS",
        "authority": {
            "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "source_file": "chapter3.tex",
            "source_lines": "1-227",
            "source_span_bytes": EXPECTED_SOURCE_SPAN_BYTES,
            "source_span_sha256": EXPECTED_SOURCE_SPAN_SHA256,
        },
        "target": {
            "target_file": "repo/source/chapter3.tex",
            "target_lines": "1-226",
            "target_file_bytes": EXPECTED_TARGET_FILE_BYTES,
            "target_file_sha256": EXPECTED_TARGET_FILE_SHA256,
            "target_span_bytes": EXPECTED_TARGET_SPAN_BYTES,
            "target_span_sha256": EXPECTED_TARGET_SPAN_SHA256,
            "correction_ids": list(CORRECTION_IDS),
            "han_residue": 0,
        },
        "structure": structure,
        "artifact": digest(PDF_PUBLIC),
        "build_log": digest(LOG_PUBLIC),
        "build_log_sanitization": sanitization,
        "final_aux": digest(BUILD_B / f"{JOB}.aux"),
        "evidence_generator": digest(Path(__file__)),
        "render_inventory": digest(QA_ROOT / "render-hash-inventory.json"),
        "pdf": facts,
        "topology": {
            "outlines": len(facts["outlines"]),
            "named_destinations": facts["named_destination_count"],
            "goto_actions": facts["annotation_actions"].get("/GoTo", 0),
            "uri_actions": facts["annotation_actions"].get("/URI", 0),
        },
        "deterministic_replay": deterministic_replay,
        "embedded_subset_font_count": fonts,
        "log_counts": counts,
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": list(VISUALLY_INSPECTED_PAGES),
            "renderers_inspected": ["Poppler", "MuPDF"],
            "finding": (
                "The centered cover states the partial boundary in prose without ambiguous progress blocks; "
                "all content pages use the available reading width, and the short bibliography, term index, and "
                "symbol index share one concluding page rather than occupying sparse back-matter pages."
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
            "PASS Unit 019 final build and replay",
            f"artifact bytes={len(artifact)} sha256={sha256(artifact).hexdigest()} pages={EXPECTED_PAGE_COUNT}",
            f"authority lines=1-227 sha256={EXPECTED_SOURCE_SPAN_SHA256}",
            f"target lines=1-226 sha256={EXPECTED_TARGET_SPAN_SHA256} Han=0",
            "same-renderer replay: Poppler all pages identical; MuPDF all pages identical",
            f"PDF: outlines={len(EXPECTED_OUTLINES)} destinations={EXPECTED_NAMED_DESTINATIONS} GoTo={EXPECTED_GOTO_ACTIONS} URI={EXPECTED_URI_ACTIONS} tagged=no language=id-ID",
            f"log counts: {json.dumps(counts, sort_keys=True)}",
            f"provenance model: {PROVENANCE_MODEL}",
            "",
        )
    )
    (QA_ROOT / "build-log-summary.txt").write_text(summary, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "artifact": digest(PDF_PUBLIC)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
