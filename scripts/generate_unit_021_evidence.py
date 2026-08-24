from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JOB = "unit-021-bab-3-struktur-kepang"
TARGET = ROOT / "repo/source/chapter3.tex"
CANDIDATE = ROOT / "build/unit-021-candidate/chapter3-braiding-id.tex"
DRIVER = ROOT / f"repo/source/{JOB}.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-021.tex"
CROSSREFS = ROOT / "repo/source/unit-021-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_021.ps1"
CHECKER = ROOT / "scripts/check_unit_021_candidate.py"
SOURCE_REVIEW = ROOT / "qa/UNIT_021_TRANSLATION_SOURCE_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_021_TERMINOLOGY_AUDIT_20260824.md"
BUILD_A = ROOT / f"build/unit-021-final-a/{JOB}.pdf"
BUILD_B = ROOT / f"build/unit-021-final-b/{JOB}.pdf"
ARTIFACT = ROOT / f"artifacts/{JOB}.pdf"
SOURCE_LOG = ROOT / f"build/unit-021-final-b/{JOB}.log"
FINAL_LOG = ROOT / "qa/UNIT_021_BUILD_FINAL.log"
VISUAL_PROBE = ROOT / "build/unit-021-visual-qa/qa_probe.py"
VISUAL_MANIFEST = ROOT / "build/unit-021-visual-qa/qa-manifest.json"
EVIDENCE_DIR = ROOT / "qa/unit-021-evidence"
RENDER_INVENTORY = EVIDENCE_DIR / "render-hash-inventory.json"
BUILD_SUMMARY = EVIDENCE_DIR / "build-log-summary.txt"
OUTPUT = EVIDENCE_DIR / "structure-and-pdf-qa.json"

EXPECTED_TARGET_BYTES = 83581
EXPECTED_TARGET_SHA256 = "ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9"
EXPECTED_CANDIDATE_BYTES = 17968
EXPECTED_CANDIDATE_SHA256 = "57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085"
EXPECTED_NEXT_LINE_SHA256 = "c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": digest(raw),
    }


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
        BUILD_A,
        BUILD_B,
        ARTIFACT,
        SOURCE_LOG,
        VISUAL_PROBE,
        VISUAL_MANIFEST,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    if FINAL_LOG.exists():
        raise FileExistsError(f"Unit 021 final log target must be absent: {FINAL_LOG}")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    generated_targets = (
        RENDER_INVENTORY,
        BUILD_SUMMARY,
        OUTPUT,
        EVIDENCE_DIR / "poppler-final-b",
        EVIDENCE_DIR / "mupdf-final-b",
    )
    existing_targets = [path for path in generated_targets if path.exists()]
    if existing_targets:
        raise FileExistsError(
            "Unit 021 owned evidence targets must be absent for a clean generation: "
            + ", ".join(str(path) for path in existing_targets)
        )

    target_raw = TARGET.read_bytes()
    target_lines = target_raw.splitlines(keepends=True)
    span = b"".join(target_lines[305:511])
    next_line = target_lines[511]
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
    sanitized = source_log_text.replace(home, "${USER_HOME}").replace(
        home.replace("\\", "/"), "${USER_HOME}"
    )
    FINAL_LOG.write_text(sanitized, encoding="utf-8", newline="\n")
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
    artifact_pdf = visual["pdf"]["final-b"]
    deterministic_keys = (
        "replay/poppler/final-a",
        "replay/poppler/final-b",
        "builds/poppler",
        "replay/mupdf/final-a",
        "replay/mupdf/final-b",
        "builds/mupdf",
    )
    render_pass = all(
        visual["comparisons"][key]["raw_pixel_identical"]
        and visual["comparisons"][key]["png_byte_identical"]
        for key in deterministic_keys
    )
    render_count = sum(group["page_count"] for group in visual["renders"].values())
    contact_sheet_count = len(list((ROOT / "build/unit-021-visual-qa/contact-sheets").rglob("*.png")))

    admitted_renders: dict[str, list[dict[str, Any]]] = {}
    for renderer in ("poppler", "mupdf"):
        destination_dir = EVIDENCE_DIR / f"{renderer}-final-b"
        destination_dir.mkdir()
        admitted_renders[renderer] = []
        source_records = visual["renders"][f"{renderer}/final-b/run-1"]["pages"]
        for page_number, page in enumerate(source_records, 1):
            source = ROOT / page["path"]
            destination = destination_dir / f"page-{page_number:02d}.png"
            shutil.copyfile(source, destination)
            copied = identity(destination)
            if copied["bytes"] != page["bytes"] or copied["sha256"] != page["sha256"]:
                raise RuntimeError(f"render witness copy mismatch: {destination}")
            admitted_renders[renderer].append(
                {
                    "page": page_number,
                    **copied,
                    "raw_rgb_sha256": page["raw_rgb_sha256"],
                    "outer_3px_ink": page["ink_pixels_in_outer_3px"],
                }
            )

    inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U021",
        "status": "PASS",
        "page_count": 9,
        "render_resolution_dpi": visual["render_dpi"],
        "build_a": identity(BUILD_A),
        "build_b": identity(BUILD_B),
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_count": render_count,
        "contact_sheet_count": contact_sheet_count,
        "comparisons": {key: visual["comparisons"][key] for key in deterministic_keys},
        "renderer_aggregate_hashes": {
            renderer: {
                "raw_rgb": visual["renders"][f"{renderer}/final-b/run-1"]["aggregate_raw_rgb_sha256"],
                "png_set": visual["renders"][f"{renderer}/final-b/run-1"]["aggregate_png_set_sha256"],
            }
            for renderer in ("poppler", "mupdf")
        },
        "renderers": admitted_renders,
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    RENDER_INVENTORY.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    expected_labels = [
        "sec:braiding",
        "def:braiding",
        "eqn:hexagon-axiom-1",
        "eqn:hexagon-axiom-2",
        "rem:hexagon-axiom-strict",
        "def:symm-monoidal-cat",
        "prop:YBE-cat-strict",
        "rem:YBE-cat-strict",
        "eg:braid",
    ]
    expected_refs = [
        "eg:braid",
        "eqn:hexagon-axiom-1",
        "eqn:hexagon-axiom-2",
        "def:strict-monoidal-cat",
        "eg:monoidal-cat",
        "prop:product-commutativity",
        "sec:module-tensor-prod",
        "eg:fundamental-groupoid",
        "sec:symmetric-group",
        "eqn:braid-presentation",
        "rem:hexagon-axiom-strict",
        "rem:YBE-cat-strict",
        "def:braiding",
    ]
    expected_outline = [
        "Bab 3: Kategori Monoidal",
        "3.3 Struktur Kepang",
        "Daftar Pustaka",
        "Indeks Istilah",
        "Indeks Simbol",
    ]
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
        and digest(target_raw) == EXPECTED_TARGET_SHA256,
        "canonical_span_equals_candidate": span == candidate_raw
        and len(span) == EXPECTED_CANDIDATE_BYTES
        and digest(span) == EXPECTED_CANDIDATE_SHA256,
        "boundary_next_section": digest(next_line) == EXPECTED_NEXT_LINE_SHA256
        and next_line.startswith(b"\\section{"),
        "candidate_checker": checker_run.returncode == 0
        and checker_run.stdout.startswith(b"PASS Unit 021 isolated candidate checker"),
        "artifact_equals_final_b": ARTIFACT.read_bytes() == BUILD_B.read_bytes(),
        "nine_pages": visual["pdf"]["final-a"]["pages"]
        == visual["pdf"]["final-b"]["pages"]
        == 9,
        "semantic_replay": not visual["semantic_differences"],
        "render_replay": render_pass and render_count == 72 and contact_sheet_count == 8,
        "pdf_safety": not artifact_pdf["encrypted"]
        and not artifact_pdf["acroform_present"]
        and not artifact_pdf["javascript_name_tree"]
        and not artifact_pdf["embedded_files"]
        and not artifact_pdf["catalog_additional_actions"]
        and not artifact_pdf["unsafe_actions"],
        "navigation": [entry["title"] for entry in artifact_pdf["outline"]] == expected_outline
        and len(artifact_pdf["named_destinations"]) == 29
        and artifact_pdf["annotation_actions"] == {"/URI": 4, "/GoTo": 18},
        "accessibility_baseline": artifact_pdf["language"] == "id-ID"
        and all(count > 0 for count in artifact_pdf["page_text_character_counts"])
        and not artifact_pdf["fitz_out_of_bounds_text_blocks"]
        and not artifact_pdf["pdfplumber_out_of_bounds_characters"],
        "fonts": artifact_pdf["font_count"] == 30
        and artifact_pdf["all_fonts_embedded_and_subset"],
        "text_tokens": artifact_pdf["unresolved_token_count"] == 0
        and artifact_pdf["fitz_nul_character_count"] == 0
        and artifact_pdf["pdfplumber_nul_character_count"] == 0
        and artifact_pdf["poppler_layout_nul_byte_count"] == 0,
        "log": zero_error_log and log_counts["empty_external_link_targets"] == 7,
        "page_edges": not visual["edge_ink_paths"],
        "structure": labels == expected_labels
        and refs == expected_refs
        and cites == [("", "JS93"), ("Corollary 2.6", "JS93")]
        and len(indexes) == 8,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Unit 021 evidence gate failed: {checks}")

    summary = (
        "PASS Unit 021 final build and visual replay\n"
        f"artifact bytes={ARTIFACT.stat().st_size} sha256={identity(ARTIFACT)['sha256']} pages=9\n"
        f"canonical target bytes={len(target_raw)} sha256={digest(target_raw)}\n"
        f"canonical lines=306-511 records=206 bytes={len(span)} sha256={digest(span)} candidate_byte_identical=yes\n"
        "same-renderer replay and cross-build: Poppler all pages identical; PyMuPDF all pages identical\n"
        f"PDF: outlines={len(artifact_pdf['outline'])} destinations={len(artifact_pdf['named_destinations'])} "
        f"GoTo={artifact_pdf['annotation_actions'].get('/GoTo', 0)} URI={artifact_pdf['annotation_actions'].get('/URI', 0)} "
        f"fonts={artifact_pdf['font_count']} language={artifact_pdf['language']} tagged={'yes' if artifact_pdf['tagged'] else 'no'}\n"
        f"log counts: {json.dumps(log_counts, sort_keys=True)}\n"
        "Nine pages retained: attempted same-page back-matter merge produced a 21.58pt overfull vbox; the clean layout combines bibliography and both indexes on page 9.\n"
        "PyPDF maps two visible long-arrow glyphs to NUL; Poppler, PyMuPDF, and pdfplumber extract them without NUL/replacement/control characters.\n"
        "provenance model: OpenAI Codex gpt-5.6-sol, Ultra\n"
    )
    BUILD_SUMMARY.write_text(summary, encoding="utf-8", newline="\n")

    evidence = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U021",
        "status": "PASS",
        "scope_note": "Canonical target integration is observed and hash-bound; admission/publication actions remain outside this visual lane.",
        "canonical_target": {
            **identity(TARGET),
            "span_lines": "306-511",
            "span_line_records": 206,
            "span_bytes": len(span),
            "span_sha256": digest(span),
            "span_equals_isolated_candidate": True,
            "next_target_line": 512,
            "next_line_sha256": digest(next_line),
        },
        "candidate": identity(CANDIDATE),
        "artifact": identity(ARTIFACT),
        "clean_builds": {"final_a": identity(BUILD_A), "final_b": identity(BUILD_B)},
        "driver": identity(DRIVER),
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
        "visual_probe": identity(VISUAL_PROBE),
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_inventory": identity(RENDER_INVENTORY),
        "evidence_generator": identity(Path(__file__).resolve()),
        "structure": {
            "labels": labels,
            "references": refs,
            "citations": [{"locator": locator, "key": key} for locator, key in cites],
            "index_entries": len(indexes),
            "ordinary_index_entries": sum(1 for name in indexes if not name),
            "symbol_index_entries": sum(1 for name in indexes if name == "sym1"),
            "environment_counts": dict(environments),
            "tikzpicture": environments.get("tikzpicture", 0),
            "tikzcd": environments.get("tikzcd", 0),
            "declared_corrections": [
                "O013-LI-U021-COR-001",
                "O013-LI-U021-COR-002",
                "O013-LI-U021-ED-001",
            ],
        },
        "pdf": artifact_pdf,
        "deterministic_replay": {
            "container_byte_identity": BUILD_A.read_bytes() == BUILD_B.read_bytes(),
            "semantic_and_render_identity": True,
            "render_count": render_count,
            "contact_sheet_count": contact_sheet_count,
            "same_renderer_page_mismatches": {"poppler": 0, "mupdf": 0},
        },
        "log_counts": log_counts,
        "checks": checks,
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": list(range(1, 10)),
            "renderers_inspected": ["Poppler", "PyMuPDF"],
            "finding": "Centered scope-explicit cover; readable full-width Section 3.3; intact hexagons, Yang--Baxter cycle, braid diagrams, and naturality square; bibliography and both short indexes combined legibly on concluding page 9.",
            "nine_page_adjudication": "Retained because an attempted eight-page same-page merge produced a 21.58pt overfull vbox; the restored nine-page layout has zero overfull boxes.",
        },
        "extraction_note": {
            "pypdf_nul_character_count": artifact_pdf["pypdf_nul_character_count"],
            "interpretation": "PyPDF-only ToUnicode mapping limitation for two rendered long-arrow glyphs; zero NUL/replacement/control characters in Poppler, PyMuPDF, and pdfplumber extraction.",
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
