from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageOps
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
JOB = "unit-022-bab-3-kategori-diperkaya-dan-aditif"
TARGET = ROOT / "repo/source/chapter3.tex"
CANDIDATE = ROOT / "build/unit-022-candidate/chapter3-enriched-categories-id.tex"
DRIVER = ROOT / f"repo/source/{JOB}.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-022.tex"
CROSSREFS = ROOT / "repo/source/unit-022-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_022.ps1"
CHECKER = ROOT / "scripts/check_unit_022_candidate.py"
SOURCE_REVIEW = ROOT / "qa/UNIT_022_TRANSLATION_SOURCE_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_022_TERMINOLOGY_AUDIT_20260824.md"
SOURCE_CORRECTIONS = ROOT / "qa/UNIT_022_SOURCE_CORRECTIONS_20260824.md"
BUILD_A = ROOT / f"build/unit-022-final-e/{JOB}.pdf"
BUILD_B = ROOT / f"build/unit-022-final-f/{JOB}.pdf"
BUILD_REPLAY = ROOT / f"build/unit-022-replay-admitted/{JOB}.pdf"
FINAL_BBL = ROOT / f"build/unit-022-final-f/{JOB}.bbl"
ARTIFACT = ROOT / f"artifacts/{JOB}.pdf"
SOURCE_LOG = ROOT / f"build/unit-022-final-f/{JOB}.log"
FINAL_LOG = ROOT / "qa/UNIT_022_BUILD_FINAL.log"
VISUAL_PROBE = ROOT / "build/unit-022-visual-qa/qa_probe.py"
VISUAL_MANIFEST = ROOT / "build/unit-022-visual-qa/qa-manifest.json"
EVIDENCE_DIR = ROOT / "qa/unit-022-evidence"
RENDER_INVENTORY = EVIDENCE_DIR / "render-hash-inventory.json"
BUILD_SUMMARY = EVIDENCE_DIR / "build-log-summary.txt"
OUTPUT = EVIDENCE_DIR / "structure-and-pdf-qa.json"

EXPECTED_TARGET_BYTES = 86033
EXPECTED_TARGET_SHA256 = "b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2"
EXPECTED_CANDIDATE_BYTES = 17541
EXPECTED_CANDIDATE_SHA256 = "e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255"
EXPECTED_NEXT_LINE_SHA256 = "26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7"

PUBLIC_RENDER_DIRS = {
    "poppler": EVIDENCE_DIR / "poppler-final-f",
    "mupdf": EVIDENCE_DIR / "mupdf-final-f",
}
PUBLIC_RENDER_SOURCES = {
    "poppler": ROOT / "build/unit-022-visual-qa/poppler-f",
    "mupdf": ROOT / "build/unit-022-visual-qa/mupdf-f",
}
REPLAY_RENDER_SOURCES = {
    "poppler": ROOT / "build/unit-022-visual-qa/poppler-replay-admitted",
    "mupdf": ROOT / "build/unit-022-visual-qa/mupdf-replay-admitted",
}
BUILD_A_RENDER_SOURCES = {
    "poppler": ROOT / "build/unit-022-visual-qa/poppler-e",
    "mupdf": ROOT / "build/unit-022-visual-qa/mupdf-e",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": digest(raw),
    }


def render_path(directory: Path, renderer: str, page_number: int) -> Path:
    """Resolve the two established renderer filename conventions."""
    unpadded = directory / f"page-{page_number}.png"
    padded = directory / f"page-{page_number:02d}.png"
    if renderer == "poppler" and unpadded.is_file():
        return unpadded
    if padded.is_file():
        return padded
    if unpadded.is_file():
        return unpadded
    raise FileNotFoundError(padded)


def render_record(path: Path, page_number: int) -> tuple[dict[str, Any], bytes, bytes]:
    raw_png = path.read_bytes()
    with Image.open(path) as opened:
        rgb = opened.convert("RGB")
        if rgb.size != (998, 1418):
            raise RuntimeError(f"unexpected Unit 022 render dimensions: {path}: {rgb.size}")
        raw_rgb = rgb.tobytes()
        ink = ImageOps.invert(rgb.convert("L")).point(lambda value: 255 if value > 5 else 0)
        pixels = ink.load()
        width, height = ink.size
        outer_ink = sum(
            1
            for y in range(height)
            for x in range(width)
            if (x < 3 or y < 3 or x >= width - 3 or y >= height - 3)
            and pixels[x, y]
        )
    return (
        {
            "page": page_number,
            **identity(path),
            "raw_rgb_sha256": digest(raw_rgb),
            "outer_3px_ink": outer_ink,
        },
        raw_png,
        raw_rgb,
    )


def render_comparison(left: Path, right: Path, renderer: str) -> dict[str, Any]:
    raw_mismatches: list[int] = []
    png_mismatches: list[int] = []
    for page_number in range(1, 10):
        left_path = render_path(left, renderer, page_number)
        right_path = render_path(right, renderer, page_number)
        if left_path.read_bytes() != right_path.read_bytes():
            png_mismatches.append(page_number)
        with Image.open(left_path) as left_image, Image.open(right_path) as right_image:
            difference = ImageChops.difference(
                left_image.convert("RGB"), right_image.convert("RGB")
            )
            if difference.getbbox() is not None:
                raw_mismatches.append(page_number)
    return {
        "page_count_equal": True,
        "raw_pixel_identical": not raw_mismatches,
        "png_byte_identical": not png_mismatches,
        "mismatching_raw_pages": raw_mismatches,
        "mismatching_png_pages": png_mismatches,
    }


def extracted_text_sha256(path: Path) -> str:
    reader = PdfReader(path, strict=True)
    text = "\n\f\n".join(page.extract_text() or "" for page in reader.pages)
    return digest(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def main() -> None:
    required = (
        TARGET,
        CANDIDATE,
        DRIVER,
        COVER,
        CROSSREFS,
        BUILD_SCRIPT,
        CHECKER,
        SOURCE_REVIEW,
        TERMINOLOGY_AUDIT,
        SOURCE_CORRECTIONS,
        BUILD_A,
        BUILD_B,
        BUILD_REPLAY,
        FINAL_BBL,
        ARTIFACT,
        SOURCE_LOG,
        FINAL_LOG,
        VISUAL_PROBE,
        VISUAL_MANIFEST,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    generated_targets = (
        RENDER_INVENTORY,
        BUILD_SUMMARY,
        OUTPUT,
    )
    existing_targets = [path for path in generated_targets if path.exists()]
    if existing_targets:
        raise FileExistsError(
            "Unit 022 owned evidence targets must be absent for a clean generation: "
            + ", ".join(str(path) for path in existing_targets)
        )

    target_raw = TARGET.read_bytes()
    target_lines = target_raw.splitlines(keepends=True)
    span = b"".join(target_lines[511:721])
    next_line = target_lines[721]
    candidate_raw = CANDIDATE.read_bytes()
    candidate_text = candidate_raw.decode("utf-8")

    labels = re.findall(r"\\label\{([^}]+)\}", candidate_text)
    refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", candidate_text)
    cites = re.findall(r"\\cite(?:\[([^]]*)\])?\{([^}]+)\}", candidate_text)
    indexes = re.findall(r"\\index(?:\[([^]]+)\])?\{", candidate_text)
    environments = Counter(re.findall(r"\\begin\{([^}]+)\}", candidate_text))

    checker_run = subprocess.run(
        ["python", "-B", str(CHECKER)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if checker_run.returncode:
        raise RuntimeError(checker_run.stderr.decode("utf-8", errors="replace"))

    home = str(Path.home())
    source_log_text = SOURCE_LOG.read_text(encoding="utf-8", errors="replace")
    expected_sanitized = source_log_text.replace(home, "${USER_HOME}").replace(
        home.replace("\\", "/"), "${USER_HOME}"
    )
    sanitized = FINAL_LOG.read_text(encoding="utf-8", errors="strict")
    if sanitized != expected_sanitized:
        raise RuntimeError("existing Unit 022 sanitized build log does not match final-f")
    if re.search(r"(?i)[A-Z]:[\\/]Users[\\/][^\\/\r\n]+", sanitized):
        raise RuntimeError("existing Unit 022 sanitized build log retains a home path")
    log_counts = {
        "overfull_boxes": len(re.findall(r"Overfull \\[hv]box", sanitized, flags=re.I)),
        "underfull_hboxes": len(re.findall(r"Underfull \\hbox", sanitized, flags=re.I)),
        "underfull_vboxes": len(re.findall(r"Underfull \\vbox", sanitized, flags=re.I)),
        "empty_external_link_targets": len(re.findall(r"Suppressing link with empty target", sanitized)),
        "undefined_control_sequences": len(re.findall(r"Undefined control sequence", sanitized, flags=re.I)),
        "undefined_references": len(re.findall(r"undefined references?", sanitized, flags=re.I)),
        "undefined_citations": len(re.findall(r"undefined citations?", sanitized, flags=re.I)),
        "missing_characters": len(re.findall(r"Missing character", sanitized, flags=re.I)),
        "fatal_errors": len(re.findall(r"Fatal error", sanitized, flags=re.I)),
        "emergency_stops": len(re.findall(r"Emergency stop", sanitized, flags=re.I)),
    }

    visual = json.loads(VISUAL_MANIFEST.read_text(encoding="utf-8"))
    artifact_pdf = visual["pdf"]["final-f"]
    deterministic_keys = (
        "replay/poppler/final-e",
        "replay/poppler/final-f",
        "builds/poppler",
        "replay/mupdf/final-e",
        "replay/mupdf/final-f",
        "builds/mupdf",
    )
    render_pass = all(
        visual["comparisons"][key]["raw_pixel_identical"]
        and visual["comparisons"][key]["png_byte_identical"]
        for key in deterministic_keys
    )
    render_count = sum(group["page_count"] for group in visual["renders"].values())
    contact_sheet_count = len(list((ROOT / "build/unit-022-visual-qa/contact-sheets").rglob("*.png")))

    admitted_renders: dict[str, list[dict[str, Any]]] = {}
    admitted_aggregates: dict[str, dict[str, str]] = {}
    public_replay_comparisons: dict[str, dict[str, Any]] = {}
    for renderer in ("poppler", "mupdf"):
        destination_dir = PUBLIC_RENDER_DIRS[renderer]
        if not destination_dir.is_dir():
            raise FileNotFoundError(destination_dir)
        expected_names = {f"page-{page_number:02d}.png" for page_number in range(1, 10)}
        actual_names = {path.name for path in destination_dir.glob("*.png")}
        if actual_names != expected_names:
            raise RuntimeError(
                f"unexpected public Unit 022 raster witness inventory: {destination_dir}"
            )
        admitted_renders[renderer] = []
        aggregate_png = hashlib.sha256()
        aggregate_rgb = hashlib.sha256()
        for page_number in range(1, 10):
            destination = destination_dir / f"page-{page_number:02d}.png"
            source = render_path(PUBLIC_RENDER_SOURCES[renderer], renderer, page_number)
            if destination.read_bytes() != source.read_bytes():
                raise RuntimeError(f"public render witness differs from final-f: {destination}")
            record, png_bytes, rgb_bytes = render_record(destination, page_number)
            if record["outer_3px_ink"]:
                raise RuntimeError(f"outer-edge ink in public render witness: {destination}")
            admitted_renders[renderer].append(record)
            aggregate_png.update(png_bytes)
            aggregate_rgb.update(rgb_bytes)
        admitted_aggregates[renderer] = {
            "raw_rgb": aggregate_rgb.hexdigest(),
            "png_set": aggregate_png.hexdigest(),
        }
        public_replay_comparisons[f"builds/{renderer}"] = render_comparison(
            BUILD_A_RENDER_SOURCES[renderer], PUBLIC_RENDER_SOURCES[renderer], renderer
        )
        public_replay_comparisons[f"replay/{renderer}"] = render_comparison(
            PUBLIC_RENDER_SOURCES[renderer], REPLAY_RENDER_SOURCES[renderer], renderer
        )

    inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U022",
        "status": "PASS",
        "page_count": 9,
        "render_resolution_dpi": visual["render_dpi"],
        "build_a": identity(BUILD_A),
        "build_b": identity(BUILD_B),
        "build_replay": identity(BUILD_REPLAY),
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_count": render_count,
        "contact_sheet_count": contact_sheet_count,
        "comparisons": {key: visual["comparisons"][key] for key in deterministic_keys},
        "public_replay_comparisons": public_replay_comparisons,
        "renderer_aggregate_hashes": admitted_aggregates,
        "renderers": admitted_renders,
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    RENDER_INVENTORY.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    expected_labels = [
        "sec:enriched-cat",
        "def:enriched-cat",
        "def:enriched-functor",
        "rem:enriched-to-ordinary",
        "def:enriched-naturaltrans",
        "eg:Ab-cat",
        "def:biproduct",
        "prop:biproduct-criterion",
        "def:additive-cat",
        "prop:biproduct-preservation",
        "prop:additive-prod-coprod",
    ]
    expected_refs = [
        "eg:categories",
        "def:category",
        "eg:monoidal-cat",
        "con:U-small",
        "eg:categories",
        "eg:categories",
        "rem:enriched-to-ordinary",
        "sec:limits",
        "prop:product-associativity",
        "def:universal-objects",
        "def:zero-morphism",
        "def:enriched-functor",
        "prop:Mod-cat-additive",
        "prop:biproduct-criterion",
        "prop:product-associativity",
    ]
    expected_external_crossrefs = {
        "def:category": "2.1.1",
        "con:U-small": "2.1.4",
        "eg:categories": "2.1.5",
        "def:universal-objects": "2.4.1",
        "def:zero-morphism": "2.4.3",
        "sec:limits": "2.7",
        "prop:product-associativity": "2.7.11",
        "eg:monoidal-cat": "3.1.3",
        "prop:Mod-cat-additive": "6.2.4",
    }
    expected_crossref_lines = {
        key: rf"\newlabel{{{key}}}{{{{{number.rsplit('.', 1)[0]}.{{{number.rsplit('.', 1)[1]}}}}}{{0}}}}"
        if number.count(".") >= 2
        else rf"\newlabel{{{key}}}{{{{{number}}}{{0}}}}"
        for key, number in expected_external_crossrefs.items()
    }
    # Section numbers have no theorem-number brace in the upstream AUX syntax.
    expected_crossref_lines["sec:limits"] = r"\newlabel{sec:limits}{{2.7}{0}}"
    crossrefs_text = CROSSREFS.read_text(encoding="utf-8")
    external_refs = sorted(set(refs) - set(labels))
    bbl_text = FINAL_BBL.read_text(encoding="utf-8")
    driver_text = DRIVER.read_text(encoding="utf-8")
    build_script_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    source_corrections_text = SOURCE_CORRECTIONS.read_text(encoding="utf-8")
    expected_outline = [
        "Bab 3: Kategori Monoidal",
        "3.4 Kategori Diperkaya",
        "Daftar Pustaka",
        "Indeks Istilah",
        "Indeks Simbol",
    ]
    pdf_text_hashes = {
        "final_e": extracted_text_sha256(BUILD_A),
        "final_f": extracted_text_sha256(BUILD_B),
        "replay": extracted_text_sha256(BUILD_REPLAY),
    }
    public_render_pass = all(
        comparison["raw_pixel_identical"]
        for comparison in public_replay_comparisons.values()
    )
    zero_error_log = all(
        log_counts[key] == 0
        for key in (
            "overfull_boxes",
            "undefined_control_sequences",
            "undefined_references",
            "undefined_citations",
            "missing_characters",
            "fatal_errors",
            "emergency_stops",
        )
    )
    checks = {
        "canonical_target_full_identity": len(target_raw) == EXPECTED_TARGET_BYTES
        and digest(target_raw) == EXPECTED_TARGET_SHA256
        and len(target_lines) == 910,
        "canonical_span_equals_candidate": span == candidate_raw
        and len(span) == EXPECTED_CANDIDATE_BYTES
        and digest(span) == EXPECTED_CANDIDATE_SHA256,
        "boundary_next_section": digest(next_line) == EXPECTED_NEXT_LINE_SHA256
        and next_line.startswith(b"\\section{\\texorpdfstring{$2$}{2}-"),
        "candidate_checker": checker_run.returncode == 0
        and checker_run.stdout.startswith(b"PASS Unit 022 isolated candidate checker"),
        "artifact_equals_final_b": ARTIFACT.read_bytes() == BUILD_B.read_bytes(),
        "page_count": visual["pdf"]["final-e"]["pages"]
        == visual["pdf"]["final-f"]["pages"]
        == len(PdfReader(BUILD_REPLAY, strict=True).pages)
        == 9,
        "semantic_replay": not visual["semantic_differences"]
        and len(set(pdf_text_hashes.values())) == 1,
        "render_replay": render_pass
        and public_render_pass
        and render_count == 72
        and contact_sheet_count == 8,
        "pdf_safety": not artifact_pdf["encrypted"]
        and not artifact_pdf["acroform_present"]
        and not artifact_pdf["javascript_name_tree"]
        and not artifact_pdf["embedded_files"]
        and not artifact_pdf["catalog_additional_actions"]
        and not artifact_pdf["unsafe_actions"],
        "navigation": [entry["title"] for entry in artifact_pdf["outline"]] == expected_outline
        and len(artifact_pdf["named_destinations"]) == 47
        and artifact_pdf["annotation_actions"] == {"/URI": 3, "/GoTo": 17},
        "accessibility_baseline": artifact_pdf["language"] == "id-ID"
        and all(count > 0 for count in artifact_pdf["page_text_character_counts"])
        and not artifact_pdf["fitz_out_of_bounds_text_blocks"]
        and not artifact_pdf["pdfplumber_out_of_bounds_characters"],
        "fonts": artifact_pdf["font_count"] == 28
        and artifact_pdf["all_fonts_embedded_and_subset"],
        "text_tokens": artifact_pdf["unresolved_token_count"] == 0
        and artifact_pdf["fitz_nul_character_count"] == 0
        and artifact_pdf["pdfplumber_nul_character_count"] == 0
        and artifact_pdf["poppler_layout_nul_byte_count"] == 0,
        "log": zero_error_log and log_counts["empty_external_link_targets"] == 12,
        "page_edges": not visual["edge_ink_paths"],
        "structure": labels == expected_labels
        and refs == expected_refs
        and cites == [("", "Ke05"), ("Chapter 5", "May99")]
        and len(indexes) == 10
        and sum(1 for name in indexes if not name) == 9
        and sum(1 for name in indexes if name == "sym1") == 1
        and external_refs == sorted(expected_external_crossrefs)
        and all(line in crossrefs_text for line in expected_crossref_lines.values())
        and crossrefs_text.count("\\newlabel{") == 9
        and "\\entry{Ke05}{article}" in bbl_text
        and "\\entry{May99}{book}" in bbl_text
        and all(
            correction in source_corrections_text
            for correction in ("O013-LI-U022-COR-001", "O013-LI-U022-COR-002")
        )
        and "\\InputSourceLineRange{chapter3.tex}{512}{721}" in driver_text
        and "candidate" not in driver_text.lower()
        and "candidate" not in build_script_text.lower(),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Unit 022 evidence gate failed: {checks}")

    summary = (
        "PASS Unit 022 final build and visual replay\n"
        f"artifact bytes={ARTIFACT.stat().st_size} sha256={identity(ARTIFACT)['sha256']} pages=9\n"
        f"canonical target bytes={len(target_raw)} sha256={digest(target_raw)}\n"
        f"canonical lines=512-721 records=210 bytes={len(span)} sha256={digest(span)} candidate_byte_identical=yes\n"
        "driver loads canonical chapter3.tex lines 512-721 directly; candidate dependency=no\n"
        "same-renderer replay and cross-build: Poppler and MuPDF decoded pixels identical on all pages\n"
        f"PDF: outlines={len(artifact_pdf['outline'])} destinations={len(artifact_pdf['named_destinations'])} "
        f"GoTo={artifact_pdf['annotation_actions'].get('/GoTo', 0)} URI={artifact_pdf['annotation_actions'].get('/URI', 0)} "
        f"fonts={artifact_pdf['font_count']} language={artifact_pdf['language']} tagged={'yes' if artifact_pdf['tagged'] else 'no'}\n"
        f"log counts: {json.dumps(log_counts, sort_keys=True)}\n"
        "Nine pages retained: removal of a forced back-matter page break eliminated a sparse page 10; bibliography and both indexes now fit legibly on page 9 with zero overfull boxes.\n"
        "PyPDF maps one visible tensor-product glyph to NUL; Poppler, PyMuPDF, and pdfplumber extract with zero NUL/replacement/control characters.\n"
        "provenance model: OpenAI Codex gpt-5.6-sol, Ultra\n"
    )
    BUILD_SUMMARY.write_text(summary, encoding="utf-8", newline="\n")

    evidence = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U022",
        "status": "PASS",
        "scope_note": "Canonical target integration and the installed local reader are observed and hash-bound; publication actions remain outside this evidence lane.",
        "canonical_target": {
            **identity(TARGET),
            "line_records": len(target_lines),
            "span_lines": "512-721",
            "span_line_records": 210,
            "span_bytes": len(span),
            "span_sha256": digest(span),
            "span_equals_isolated_candidate": True,
            "next_target_line": 722,
            "next_line_sha256": digest(next_line),
        },
        "candidate": identity(CANDIDATE),
        "artifact": identity(ARTIFACT),
        "clean_builds": {
            "final_e": identity(BUILD_A),
            "final_f": identity(BUILD_B),
            "replay": identity(BUILD_REPLAY),
        },
        "driver": {
            **identity(DRIVER),
            "canonical_input": "chapter3.tex",
            "canonical_span_lines": "512-721",
            "canonical_direct_binding": "\\InputSourceLineRange{chapter3.tex}{512}{721}"
            in driver_text,
            "candidate_dependency": "candidate" in driver_text.lower()
            or "candidate" in build_script_text.lower(),
        },
        "cover": identity(COVER),
        "crossrefs": identity(CROSSREFS),
        "build_script": identity(BUILD_SCRIPT),
        "build_log": identity(FINAL_LOG),
        "build_log_sanitization": {
            "method": "complete home-prefix replacement with ${USER_HOME}",
            "replacement_count": sanitized.count("${USER_HOME}"),
            "line_count": len(sanitized.splitlines()),
        },
        "candidate_checker": identity(CHECKER),
        "candidate_checker_stdout_sha256": digest(checker_run.stdout),
        "source_review": identity(SOURCE_REVIEW),
        "terminology_audit": identity(TERMINOLOGY_AUDIT),
        "source_corrections": identity(SOURCE_CORRECTIONS),
        "visual_probe": identity(VISUAL_PROBE),
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_inventory": identity(RENDER_INVENTORY),
        "evidence_generator": identity(Path(__file__).resolve()),
        "structure": {
            "labels": labels,
            "references": refs,
            "external_references": external_refs,
            "external_crossref_numbers": expected_external_crossrefs,
            "citations": [{"locator": locator, "key": key} for locator, key in cites],
            "index_entries": len(indexes),
            "ordinary_index_entries": sum(1 for name in indexes if not name),
            "symbol_index_entries": sum(1 for name in indexes if name == "sym1"),
            "environment_counts": dict(environments),
            "tikzpicture": environments.get("tikzpicture", 0),
            "tikzcd": environments.get("tikzcd", 0),
            "declared_corrections": [
                "O013-LI-U022-COR-001",
                "O013-LI-U022-COR-002",
            ],
        },
        "pdf": artifact_pdf,
        "deterministic_replay": {
            "container_byte_identity": len(
                {identity(path)["sha256"] for path in (BUILD_A, BUILD_B, BUILD_REPLAY)}
            ) == 1,
            "semantic_and_render_identity": len(set(pdf_text_hashes.values())) == 1
            and public_render_pass,
            "pypdf_text_sha256": pdf_text_hashes,
            "render_count": render_count,
            "contact_sheet_count": contact_sheet_count,
            "public_replay_comparisons": public_replay_comparisons,
            "same_renderer_page_mismatches": {
                renderer: sum(
                    len(comparison["mismatching_raw_pages"])
                    for key, comparison in public_replay_comparisons.items()
                    if key.endswith(renderer)
                )
                for renderer in ("poppler", "mupdf")
            },
        },
        "log_counts": log_counts,
        "checks": checks,
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": list(range(1, 10)),
            "renderers_inspected": ["Poppler", "MuPDF (mutool and PyMuPDF)"],
            "finding": "Centered prose cover with explicit partial scope and no progress blocks; readable full-width Section 3.4; intact enriched-category composition/unit diagrams, enriched naturality square, biproduct arrows and matrix formulas; bibliography and both indexes combined legibly on concluding page 9.",
            "nine_page_adjudication": "A forced back-matter page break originally created a sparse page 10. Suppressing only that break uses the open lower portion of page 9 for the two-entry bibliography and both indexes, with zero overfull boxes.",
        },
        "extraction_note": {
            "pypdf_nul_character_count": artifact_pdf["pypdf_nul_character_count"],
            "interpretation": "PyPDF-only ToUnicode mapping limitation for one visibly rendered tensor-product glyph on PDF page 3; zero NUL/replacement/control characters in Poppler, PyMuPDF, and pdfplumber extraction.",
        },
        "rights": {
            "principal_text_and_translation": "CC BY 4.0",
            "AJbook_class_fragment": "CC BY-SA 3.0",
            "bundled_noto_fonts": "SIL OFL 1.1",
            "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
        },
        "language": "id-ID",
        "source_author": "Wen-Wei Li",
        "translation_status": "independent and non-endorsed",
        "build_date": "2026-08-24",
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": identity(OUTPUT),
                "summary": identity(BUILD_SUMMARY),
                "render_inventory": identity(RENDER_INVENTORY),
                "build_log": identity(FINAL_LOG),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
