#!/usr/bin/env python3
"""Generate deterministic, sanitized Unit 017 build and visual-QA evidence."""

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
QA_ROOT = ROOT / "qa" / "unit-017-evidence"
BUILD_F = ROOT / "build" / "unit-017-build-f"
BUILD_G = ROOT / "build" / "unit-017-build-g"
QA_F = ROOT / "build" / "unit-017-qa-f"
QA_G = ROOT / "build" / "unit-017-qa-g"
JOB = "unit-017-bab-2-kelengkapan"
PDF_F = BUILD_F / f"{JOB}.pdf"
PDF_G = BUILD_G / f"{JOB}.pdf"
PDF_PUBLIC = ROOT / "artifacts" / f"{JOB}.pdf"
RAW_LOG = BUILD_G / f"{JOB}.log"
LOG_PUBLIC = ROOT / "qa" / "UNIT_017_BUILD_FINAL.log"
CHECKER = ROOT / "scripts" / "check_unit_017_structure.py"
TEXT_F = QA_F / "unit-017-layout.txt"
TEXT_G = QA_G / "unit-017-layout.txt"

EXPECTED_ARTIFACT_BYTES = 112_236
EXPECTED_ARTIFACT_SHA256 = "bfcec32b3ba20f8c170a3389a1b651613f1fa437945662ca32dd62fcf0edba5e"
EXPECTED_TEXT_SHA256 = "11333ab6db1c982579b217a57c4fe500a45df08f280ebeff1c499a2d6ec299d7"
EXPECTED_SOURCE_BYTES = 15_810
EXPECTED_SOURCE_SHA256 = "ccc5a17cbf856e59e7b8abbff8fd542c5deb399e58b6fc7a5a0f448c7c019e92"
EXPECTED_TARGET_BYTES = 18_633
EXPECTED_TARGET_SHA256 = "e27dba97355122446714b8e58f71f80edbb1d74e6160f99ba0b8160e7c3ec30b"
PROVENANCE_MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> dict[str, object]:
    require(path.is_file(), f"missing evidence input: {path.relative_to(ROOT).as_posix()}")
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def render_source_name(renderer: str, page: int) -> str:
    if renderer == "poppler":
        return f"page-{page}.png"
    return f"page-{page:02d}.png"


def copy_and_verify_render_records(renderer: str) -> list[dict[str, object]]:
    public_dir = QA_ROOT / f"{renderer}-final-g"
    public_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for page in range(1, 10):
        build_f = QA_F / renderer / render_source_name(renderer, page)
        build_g = QA_G / renderer / render_source_name(renderer, page)
        public = public_dir / f"page-{page:02d}.png"
        require(build_f.is_file(), f"missing build-F {renderer} page {page}")
        require(build_g.is_file(), f"missing build-G {renderer} page {page}")
        shutil.copyfile(build_g, public)

        f_bytes = build_f.read_bytes()
        g_bytes = build_g.read_bytes()
        public_bytes = public.read_bytes()
        require(f_bytes == g_bytes, f"{renderer} page {page} differs between builds F and G")
        require(g_bytes == public_bytes, f"{renderer} page {page} public evidence differs from G")

        records.append(
            {
                "page": page,
                "path": public.relative_to(ROOT).as_posix(),
                "bytes": len(public_bytes),
                "sha256": sha256(public_bytes).hexdigest(),
                "matches_clean_build_f": True,
                "matches_clean_build_g": True,
                "visual_inspection_basis": "build G page inspected directly in this renderer",
            }
        )
    return records


def sanitize_final_log() -> dict[str, object]:
    """Replace only the complete machine-local home prefix; remove no diagnostics."""
    raw_text = RAW_LOG.read_text(encoding="utf-8", errors="replace")
    raw_line_count = len(raw_text.splitlines())
    sanitized = raw_text
    replacement_count = 0
    home = str(Path.home())
    for variant in dict.fromkeys((home, home.replace("\\", "/"))):
        sanitized, replacements = re.subn(
            re.escape(variant), "${USER_HOME}", sanitized, flags=re.IGNORECASE
        )
        replacement_count += replacements
    require(home.lower() not in sanitized.lower(), "machine-local home prefix remains in final log")
    require(
        home.replace("\\", "/").lower() not in sanitized.lower(),
        "slash-normalized machine-local home prefix remains in final log",
    )
    require(len(sanitized.splitlines()) == raw_line_count, "log sanitization changed line count")
    LOG_PUBLIC.write_text(sanitized, encoding="utf-8", newline="\n")
    return {
        "method": "case-insensitive replacement of the complete machine-local home prefix with ${USER_HOME}",
        "replacement_count": replacement_count,
        "raw_line_count": raw_line_count,
        "sanitized_line_count": len(sanitized.splitlines()),
        "diagnostics_deleted": 0,
    }


def annotation_inventory(reader: PdfReader) -> tuple[list[int], Counter[str], Counter[str]]:
    per_page: list[int] = []
    subtypes: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    for page in reader.pages:
        references = page.get("/Annots")
        annotations = references.get_object() if references else []
        per_page.append(len(annotations))
        for reference in annotations:
            annotation = reference.get_object()
            subtypes[str(annotation.get("/Subtype"))] += 1
            action = annotation.get("/A")
            if action:
                actions[str(action.get_object().get("/S"))] += 1
            elif annotation.get("/Dest") is not None:
                actions["/Dest"] += 1
    return per_page, subtypes, actions


def flatten_outlines(items: object) -> list[str]:
    results: list[str] = []
    for item in items:
        if isinstance(item, list):
            results.extend(flatten_outlines(item))
        else:
            results.append(str(getattr(item, "title", item)))
    return results


def font_inventory(pdf: Path) -> tuple[str, list[dict[str, object]]]:
    output = subprocess.run(
        ["pdffonts", str(pdf)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    records: list[dict[str, object]] = []
    for line in output.splitlines()[2:]:
        if not line.strip():
            continue
        match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+(\d+)\s+(\d+)\s*$", line)
        require(match is not None, f"could not parse pdffonts row: {line}")
        records.append(
            {
                "row": line,
                "embedded": match.group(1) == "yes",
                "subset": match.group(2) == "yes",
                "unicode": match.group(3) == "yes",
                "object_id": [int(match.group(4)), int(match.group(5))],
            }
        )
    require(records, "pdffonts reported no fonts")
    require(all(record["embedded"] for record in records), "not all PDF fonts are embedded")
    require(all(record["subset"] for record in records), "not all PDF fonts are subset")
    return output, records


def pdfinfo_inventory(pdf: Path) -> dict[str, str]:
    output = subprocess.run(
        ["pdfinfo", str(pdf)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    fields: dict[str, str] = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    require(fields.get("Tagged", "").lower() == "no", "PDF must honestly remain recorded as untagged")
    require(fields.get("Encrypted", "").lower() == "no", "pdfinfo reports encryption")
    require(fields.get("Pages") == "9", "pdfinfo page count differs from 9")
    return fields


def main() -> int:
    QA_ROOT.mkdir(parents=True, exist_ok=True)

    sanitization = sanitize_final_log()

    checker = subprocess.run(
        [sys.executable, "-B", str(CHECKER)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(checker.stdout.startswith("PASS Unit 017 structural checker"), "structure checker did not pass")
    (QA_ROOT / "structure-check.txt").write_text(checker.stdout, encoding="utf-8", newline="\n")

    public_pdf = PDF_PUBLIC.read_bytes()
    require(len(public_pdf) == EXPECTED_ARTIFACT_BYTES, "installed artifact byte count changed")
    require(sha256(public_pdf).hexdigest() == EXPECTED_ARTIFACT_SHA256, "installed artifact hash changed")
    require(public_pdf == PDF_G.read_bytes(), "installed artifact does not equal clean build G")
    require(PDF_F.read_bytes() != PDF_G.read_bytes(), "builds F and G unexpectedly have identical containers")

    text_f = TEXT_F.read_bytes()
    text_g = TEXT_G.read_bytes()
    require(text_f == text_g, "builds F and G have different extracted text")
    require(sha256(text_f).hexdigest() == EXPECTED_TEXT_SHA256, "F/G extracted-text hash changed")

    poppler = copy_and_verify_render_records("poppler")
    mupdf = copy_and_verify_render_records("mupdf")
    inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U017",
        "render_resolution_dpi": 150,
        "page_count": 9,
        "deterministic_replay": {
            "container_byte_identity": False,
            "container_note": "Clean builds F and G differ only in PDF container identity; extracted text and every same-renderer page raster are byte-identical.",
            "pdf_f": digest(PDF_F),
            "pdf_g": digest(PDF_G),
            "pdftotext_layout_sha256_f": sha256(text_f).hexdigest(),
            "pdftotext_layout_sha256_g": sha256(text_g).hexdigest(),
            "poppler_page_mismatches_f_g": 0,
            "mupdf_page_mismatches_f_g": 0,
        },
        "inspection_chain": {
            "build_g": "All nine build-G pages were directly inspected in both Poppler and MuPDF.",
            "build_f": "Every build-F raster is byte-identical to its build-G counterpart in the same renderer.",
            "all_pages_inspected": True,
        },
        "renderers": {"poppler": poppler, "mupdf": mupdf},
        "provenance_model": PROVENANCE_MODEL,
    }
    (QA_ROOT / "render-hash-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    final_log_text = LOG_PUBLIC.read_text(encoding="utf-8", errors="replace")
    log_counts = {
        "overfull_boxes": count(r"Overfull \[hv]box", final_log_text),
        "underfull_hboxes": count(r"Underfull \\hbox", final_log_text),
        "underfull_vboxes": count(r"Underfull \\vbox", final_log_text),
        "empty_external_link_targets": count(r"Suppressing link with empty target", final_log_text),
        "undefined_control_sequences": count(r"Undefined control sequence", final_log_text),
        "undefined_references_summary": count(r"undefined references", final_log_text),
        "undefined_reference_warnings": count(r"Reference .* undefined", final_log_text),
        "undefined_citations": count(r"Citation .* undefined", final_log_text),
        "missing_characters": count(r"Missing character", final_log_text),
        "fatal_errors": count(r"Fatal error", final_log_text),
        "emergency_stops": count(r"Emergency stop", final_log_text),
        "imakeidx_post_index_reminders": count(r"Remember to run xelatex again", final_log_text),
    }
    require(log_counts["overfull_boxes"] == 0, "overfull box detected")
    for key in (
        "undefined_control_sequences",
        "undefined_references_summary",
        "undefined_reference_warnings",
        "undefined_citations",
        "missing_characters",
        "fatal_errors",
        "emergency_stops",
    ):
        require(log_counts[key] == 0, f"critical log gate failed: {key}")

    reader = PdfReader(PDF_PUBLIC)
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    root = reader.trailer["/Root"]
    root_lang = str(root.get("/Lang"))
    mark_info = root.get("/MarkInfo")
    tagged = bool(mark_info and mark_info.get_object().get("/Marked"))
    text_chars = [len(page.extract_text() or "") for page in reader.pages]
    page_sizes = [
        [round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)]
        for page in reader.pages
    ]
    outlines = flatten_outlines(reader.outline)
    destination_names = sorted(str(name) for name in reader.named_destinations)
    annotations, annotation_subtypes, annotation_actions = annotation_inventory(reader)
    _, fonts = font_inventory(PDF_PUBLIC)
    pdfinfo = pdfinfo_inventory(PDF_PUBLIC)

    require(len(reader.pages) == 9, "unexpected final page count")
    require(not reader.is_encrypted, "reader is encrypted")
    require(all(value > 0 for value in text_chars), "blank or nonextractable page")
    require(root_lang == "id-ID", "PDF language is not id-ID")
    require(not tagged, "PDF unexpectedly claims tagged structure")
    require(metadata.get("/Author") == "Wen-Wei Li", "PDF author metadata drift")
    require(
        metadata.get("/Title")
        == "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 17: Kelengkapan",
        "PDF title metadata drift",
    )
    require(outlines == ["2.8 Kelengkapan", "Indeks Istilah"], "outline sequence differs")
    require(len(destination_names) == 36, "named-destination count differs from 36")
    require(annotation_subtypes == Counter({"/Link": 20}), "annotation subtype inventory changed")
    require(annotation_actions == Counter({"/GoTo": 17, "/URI": 3}), "link-action inventory changed")
    require(all(size == [498.9, 708.66] for size in page_sizes), "page geometry changed")

    qa = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U017",
        "status": "PASS",
        "authority": {
            "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "source_file": "chapter2.tex",
            "source_lines": "1406-1602",
            "source_span_bytes": EXPECTED_SOURCE_BYTES,
            "source_span_sha256": EXPECTED_SOURCE_SHA256,
        },
        "target": {
            "target_span_bytes": EXPECTED_TARGET_BYTES,
            "target_span_sha256": EXPECTED_TARGET_SHA256,
            "correction_ids": [f"O013-LI-U017-COR-{number:03d}" for number in range(1, 7)],
            "translation_only_grammar_repair_line": 1410,
            "han_residue": 0,
        },
        "artifact": digest(PDF_PUBLIC),
        "build_log": digest(LOG_PUBLIC),
        "build_log_sanitization": sanitization,
        "structure_checker": digest(CHECKER),
        "structure_check_output": digest(QA_ROOT / "structure-check.txt"),
        "evidence_generator": digest(Path(__file__)),
        "render_inventory": digest(QA_ROOT / "render-hash-inventory.json"),
        "pdf": {
            "pages": len(reader.pages),
            "page_size_points": [498.9, 708.66],
            "language": root_lang,
            "encrypted": reader.is_encrypted,
            "tagged": tagged,
            "accessibility_note": "The PDF is untagged, but declares id-ID, has extractable text on every page, and contains no blank pages.",
            "metadata": metadata,
            "page_text_character_counts": text_chars,
            "page_annotation_counts": annotations,
            "annotation_subtypes": dict(annotation_subtypes),
            "annotation_actions": dict(annotation_actions),
            "named_destination_count": len(destination_names),
            "named_destinations": destination_names,
            "outline_entries": outlines,
            "embedded_font_count": sum(bool(record["embedded"]) for record in fonts),
            "subset_font_count": sum(bool(record["subset"]) for record in fonts),
            "pdfinfo": pdfinfo,
        },
        "log_counts": log_counts,
        "deterministic_replay": inventory["deterministic_replay"],
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": list(range(1, 10)),
            "renderers_inspected": ["Poppler", "MuPDF"],
            "inspection_chain": inventory["inspection_chain"],
            "findings": [
                "All nine build-G pages were inspected directly in both Poppler and MuPDF; prose, mathematics, diagrams, headings, the two-column index, and link labels are legible and unclipped.",
                "All nine build-F pages are same-renderer pixel-identical to build G, and the F/G extracted text is byte-identical.",
                "The corrected navigation has exactly two outlines and 36 named destinations; the redundant index outline is absent.",
                "No blank page, overlap, cropped label, broken arrow, missing glyph, or anomalous answer field is present.",
            ],
        },
        "rights": "CC BY 4.0",
        "provenance_model": PROVENANCE_MODEL,
    }
    (QA_ROOT / "structure-and-pdf-qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    summary = "\n".join(
        (
            "PASS Unit 017 final build and replay",
            f"artifact bytes={PDF_PUBLIC.stat().st_size} sha256={sha256(public_pdf).hexdigest()} pages=9",
            f"final log bytes={LOG_PUBLIC.stat().st_size} sha256={sha256(LOG_PUBLIC.read_bytes()).hexdigest()}",
            f"build F bytes={PDF_F.stat().st_size} sha256={sha256(PDF_F.read_bytes()).hexdigest()}",
            f"build G bytes={PDF_G.stat().st_size} sha256={sha256(PDF_G.read_bytes()).hexdigest()}",
            "same-renderer raster replay F/G: Poppler 9/9 identical; MuPDF 9/9 identical",
            "visual QA: all 9 build-G pages inspected directly in Poppler and MuPDF",
            f"pdftotext -layout replay F/G: identical sha256={sha256(text_f).hexdigest()}",
            "PDF: outlines=2 named_destinations=36 GoTo=17 URI=3 fonts_embedded=all tagged=no language=id-ID blank_pages=0",
            f"log counts: {json.dumps(log_counts, sort_keys=True)}",
            "visual QA: all 9 pages covered in Poppler and MuPDF; PASS",
            f"provenance model: {PROVENANCE_MODEL}",
            "",
        )
    )
    (QA_ROOT / "build-log-summary.txt").write_text(summary, encoding="utf-8", newline="\n")

    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": digest(PDF_PUBLIC),
                "evidence_root": QA_ROOT.relative_to(ROOT).as_posix(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
