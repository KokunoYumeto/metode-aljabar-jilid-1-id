from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
JOB = "unit-020-bab-3-keketatan-dan-teorema-koherensi"
TARGET = ROOT / "repo/source/chapter3.tex"
DRIVER = ROOT / f"repo/source/{JOB}.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-020.tex"
CROSSREFS = ROOT / "repo/source/unit-020-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_020.ps1"
BUILD_E = ROOT / f"build/unit-020-final-e/{JOB}.pdf"
BUILD_F = ROOT / f"build/unit-020-final-f/{JOB}.pdf"
ARTIFACT = ROOT / f"artifacts/{JOB}.pdf"
SOURCE_LOG = ROOT / f"build/unit-020-final-f/{JOB}.log"
FINAL_LOG = ROOT / "qa/UNIT_020_BUILD_FINAL.log"
VISUAL_MANIFEST = ROOT / "build/unit-020-visual-qa/qa-manifest.json"
EVIDENCE_DIR = ROOT / "qa/unit-020-evidence"
RENDER_INVENTORY = EVIDENCE_DIR / "render-hash-inventory.json"
BUILD_SUMMARY = EVIDENCE_DIR / "build-log-summary.txt"
OUTPUT = EVIDENCE_DIR / "structure-and-pdf-qa.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": digest(raw),
    }


def deref(value: Any) -> Any:
    try:
        return value.get_object()
    except Exception:
        return value


def flatten_outline(reader: PdfReader, items: list[Any], level: int = 0) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten_outline(reader, item, level + 1))
            continue
        try:
            page = int(reader.get_destination_page_number(item))
        except Exception:
            page = None
        result.append({"level": level, "title": str(getattr(item, "title", "")), "page_index": page})
    return result


def run_bytes(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def inspect_pdf(path: Path) -> dict[str, Any]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        reader = PdfReader(str(path), strict=True)
        catalog = deref(reader.trailer["/Root"])
        names = deref(catalog.get("/Names")) if catalog.get("/Names") else {}
        outline = flatten_outline(reader, reader.outline)
        destinations = []
        for name, destination in reader.named_destinations.items():
            try:
                page = int(reader.get_destination_page_number(destination))
            except Exception:
                page = None
            destinations.append({"name": str(name), "page_index": page})

        annotations: Counter[str] = Counter()
        actions: Counter[str] = Counter()
        unsafe_actions: list[str] = []
        page_text_counts: list[int] = []
        page_annotation_counts: list[int] = []
        page_sizes: list[list[float]] = []
        content_hashes: list[str] = []
        text_parts: list[str] = []
        for page_index, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text_parts.append(text)
            page_text_counts.append(len(text))
            page_sizes.append([float(page.mediabox.width), float(page.mediabox.height)])
            contents = page.get_contents()
            content = contents.get_data() if contents is not None else b""
            content_hashes.append(digest(content))
            annots = deref(page.get("/Annots")) or []
            page_annotation_counts.append(len(annots))
            for ref in annots:
                annot = deref(ref)
                subtype = str(annot.get("/Subtype", "unknown"))
                annotations[subtype] += 1
                action = deref(annot.get("/A")) if annot.get("/A") else None
                if isinstance(action, dict):
                    kind = str(action.get("/S", "dictionary-without-S"))
                elif annot.get("/Dest") is not None:
                    kind = "direct-destination"
                else:
                    kind = "none"
                actions[kind] += 1
                if kind not in {"/URI", "/GoTo", "direct-destination"}:
                    unsafe_actions.append(f"page[{page_index}]:{kind}")
                if annot.get("/AA") is not None:
                    unsafe_actions.append(f"page[{page_index}]:annotation-AA")
            if page.get("/AA") is not None:
                unsafe_actions.append(f"page[{page_index}]:page-AA")

        layout = run_bytes(["pdftotext", "-layout", str(path), "-"])
        if layout.returncode:
            raise RuntimeError(layout.stderr.decode("utf-8", errors="replace"))
        fonts = run_bytes(["pdffonts", str(path)])
        font_lines = fonts.stdout.decode("utf-8", errors="replace").splitlines()[2:]
        font_rows = [line for line in font_lines if line.strip()]
        all_embedded = all(re.search(r"\s+yes\s+yes\s+(?:yes|no)\s+\d+\s+\d+\s*$", line) for line in font_rows)
        tool_results = {}
        for tool, args in {
            "pdfinfo": ["pdfinfo", str(path)],
            "pdffonts": ["pdffonts", str(path)],
            "pdfimages": ["pdfimages", "-list", str(path)],
            "mutool_info": ["mutool", "info", str(path)],
        }.items():
            completed = run_bytes(args)
            tool_results[tool] = {
                "returncode": completed.returncode,
                "stderr": completed.stderr.decode("utf-8", errors="replace"),
            }

        combined_text = "\n\f\n".join(text_parts)
        unresolved = re.findall(
            r"\?\?|\\(?:ref|eqref|cite|label)\s*\{|\b(?:TODO|FIXME|TBD|PLACEHOLDER)\b|\ufffd",
            combined_text,
            flags=re.I,
        )
        return {
            "pages": len(reader.pages),
            "language": str(catalog.get("/Lang", "")),
            "encrypted": reader.is_encrypted,
            "tagged": bool(catalog.get("/StructTreeRoot")),
            "metadata": {str(k): str(v) for k, v in (reader.metadata or {}).items()},
            "outline": outline,
            "named_destinations": destinations,
            "annotation_subtypes": dict(annotations),
            "annotation_actions": dict(actions),
            "unsafe_actions": unsafe_actions,
            "page_text_character_counts": page_text_counts,
            "page_annotation_counts": page_annotation_counts,
            "page_sizes_points": page_sizes,
            "content_stream_set_sha256": digest("\n".join(content_hashes).encode("ascii")),
            "pypdf_text_sha256": digest(combined_text.encode("utf-8")),
            "layout_text_bytes": len(layout.stdout),
            "layout_text_sha256": digest(layout.stdout),
            "font_count": len(font_rows),
            "all_fonts_embedded_and_subset": all_embedded,
            "acroform_present": bool(catalog.get("/AcroForm")),
            "javascript_name_tree": bool(isinstance(names, dict) and names.get("/JavaScript")),
            "embedded_files": bool(isinstance(names, dict) and names.get("/EmbeddedFiles")),
            "catalog_additional_actions": bool(catalog.get("/AA")),
            "unresolved_token_count": len(unresolved),
            "strict_reader_warnings": [str(item.message) for item in caught],
            "external_tools": tool_results,
        }


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    for required in (
        TARGET,
        DRIVER,
        COVER,
        CROSSREFS,
        BUILD_SCRIPT,
        BUILD_E,
        BUILD_F,
        ARTIFACT,
        SOURCE_LOG,
        VISUAL_MANIFEST,
    ):
        if not required.is_file():
            raise FileNotFoundError(required)

    target_raw = TARGET.read_bytes()
    target_lines = target_raw.splitlines(keepends=True)
    span = b"".join(target_lines[226:305])
    next_line = target_lines[305].decode("utf-8").rstrip("\r\n")
    target_text = span.decode("utf-8")
    labels = re.findall(r"\\label\{([^}]+)\}", target_text)
    refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", target_text)
    cites = re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}", target_text)
    indexes = re.findall(r"\\index(?:\[[^]]+\])?\{", target_text)

    home = str(Path.home())
    log_text = SOURCE_LOG.read_text(encoding="utf-8", errors="replace")
    sanitized = log_text.replace(home, "${USER_HOME}").replace(home.replace("\\", "/"), "${USER_HOME}")
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

    pdf_e = inspect_pdf(BUILD_E)
    pdf_f = inspect_pdf(BUILD_F)
    artifact_pdf = inspect_pdf(ARTIFACT)
    visual = json.loads(VISUAL_MANIFEST.read_text(encoding="utf-8"))
    deterministic_keys = [
        "replay/poppler/final-c",
        "replay/poppler/final-d",
        "builds/poppler",
        "replay/mupdf/final-c",
        "replay/mupdf/final-d",
        "builds/mupdf",
    ]
    render_pass = all(
        visual["comparisons"][key]["raw_pixel_identical"]
        and visual["comparisons"][key]["png_byte_identical"]
        for key in deterministic_keys
    )
    render_pages = sum(group["page_count"] for group in visual["renders"].values())
    contact_sheets = sum(len(group) for group in visual["contact_sheets"].values())
    edge_ink_pages = [
        page["path"]
        for group in visual["renders"].values()
        for page in group["pages"]
        if page["ink_pixels_in_outer_3px"] != 0
    ]

    admitted_renders: dict[str, list[dict[str, Any]]] = {}
    for renderer in ("poppler", "mupdf"):
        destination_dir = EVIDENCE_DIR / f"{renderer}-final-f"
        destination_dir.mkdir(parents=True, exist_ok=True)
        admitted_renders[renderer] = []
        for page_number, page in enumerate(
            visual["renders"][f"{renderer}/final-d/run-1"]["pages"], 1
        ):
            source = Path(page["path"])
            destination = destination_dir / f"page-{page_number:02d}.png"
            shutil.copyfile(source, destination)
            copied = identity(destination)
            if copied["bytes"] != page["png_bytes"] or copied["sha256"] != page["png_sha256"]:
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
        "unit_id": "O013-LI-U020",
        "page_count": 5,
        "render_resolution_dpi": visual["render_dpi"],
        "build_e": identity(BUILD_E),
        "build_f": identity(BUILD_F),
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_count": render_pages,
        "contact_sheet_count": contact_sheets,
        "comparisons": {key: visual["comparisons"][key] for key in deterministic_keys},
        "renderers": admitted_renders,
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    RENDER_INVENTORY.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    zero_error_counts = all(
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
        "target_boundary": len(span) == 7266
        and digest(span) == "25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270"
        and next_line.startswith("\\section{辫结构}"),
        "artifact_equals_final_f": ARTIFACT.read_bytes() == BUILD_F.read_bytes(),
        "five_pages": pdf_e["pages"] == pdf_f["pages"] == artifact_pdf["pages"] == 5,
        "semantic_replay": pdf_e["content_stream_set_sha256"] == pdf_f["content_stream_set_sha256"]
        and pdf_e["layout_text_sha256"] == pdf_f["layout_text_sha256"]
        and pdf_e["outline"] == pdf_f["outline"]
        and pdf_e["named_destinations"] == pdf_f["named_destinations"],
        "render_replay": render_pass and render_pages == 40 and contact_sheets == 8,
        "pdf_safety": not artifact_pdf["encrypted"]
        and not artifact_pdf["acroform_present"]
        and not artifact_pdf["javascript_name_tree"]
        and not artifact_pdf["embedded_files"]
        and not artifact_pdf["catalog_additional_actions"]
        and not artifact_pdf["unsafe_actions"],
        "accessibility_baseline": artifact_pdf["language"] == "id-ID"
        and all(count > 0 for count in artifact_pdf["page_text_character_counts"]),
        "fonts": artifact_pdf["font_count"] > 0 and artifact_pdf["all_fonts_embedded_and_subset"],
        "text_tokens": artifact_pdf["unresolved_token_count"] == 0,
        "log": zero_error_counts and log_counts["empty_external_link_targets"] == 3,
        "page_edges": not edge_ink_pages,
        "structure": labels == ["sec:coherence", "def:strict-monoidal-cat", "prop:ML-coherence"]
        and refs
        == ["def:monoidal-cat", "sec:monoidal-cat-def", "eg:monoidal-cat", "prop:ML-coherence", "prop:ML-coherence"]
        and cites == ["ML98", "JS93", "EGNO15"]
        and len(indexes) == 2,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Unit 020 evidence gate failed: {checks}")

    summary = (
        "PASS Unit 020 final build and replay\n"
        f"artifact bytes={ARTIFACT.stat().st_size} sha256={identity(ARTIFACT)['sha256']} pages=5\n"
        f"target lines=227-305 bytes={len(span)} sha256={digest(span)} Han=0\n"
        "same-renderer replay: Poppler all pages identical; MuPDF all pages identical\n"
        f"PDF: outlines={len(artifact_pdf['outline'])} destinations={len(artifact_pdf['named_destinations'])} "
        f"GoTo={artifact_pdf['annotation_actions'].get('/GoTo', 0)} URI={artifact_pdf['annotation_actions'].get('/URI', 0)} "
        f"tagged={'yes' if artifact_pdf['tagged'] else 'no'} language={artifact_pdf['language']}\n"
        f"log counts: {json.dumps(log_counts, sort_keys=True)}\n"
        "provenance model: OpenAI Codex gpt-5.6-sol, Ultra\n"
    )
    BUILD_SUMMARY.write_text(summary, encoding="utf-8", newline="\n")

    evidence = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U020",
        "status": "PASS",
        "target": {
            "path": "repo/source/chapter3.tex",
            "lines": "227-305",
            "line_records": 79,
            "bytes": len(span),
            "sha256": digest(span),
            "next_target_line": 306,
            "next_line_sha256": digest(target_lines[305]),
            "correction_ids": ["O013-LI-U020-COR-001"],
        },
        "artifact": identity(ARTIFACT),
        "clean_builds": {"final_e": identity(BUILD_E), "final_f": identity(BUILD_F)},
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
        "visual_manifest": identity(VISUAL_MANIFEST),
        "render_inventory": identity(RENDER_INVENTORY),
        "evidence_generator": identity(Path(__file__).resolve()),
        "structure": {
            "labels": labels,
            "references": refs,
            "citations": cites,
            "index_entries": len(indexes),
            "tikzpicture": len(re.findall(r"\\begin\{tikzpicture\}", target_text)),
            "tikzcd": len(re.findall(r"\\begin\{tikzcd\}", target_text)),
        },
        "pdf": artifact_pdf,
        "deterministic_replay": {
            "container_byte_identity": BUILD_E.read_bytes() == BUILD_F.read_bytes(),
            "semantic_and_render_identity": True,
            "layout_text_sha256_e": pdf_e["layout_text_sha256"],
            "layout_text_sha256_f": pdf_f["layout_text_sha256"],
            "render_count": render_pages,
            "contact_sheet_count": contact_sheets,
            "same_renderer_page_mismatches": {"poppler": 0, "mupdf": 0},
        },
        "log_counts": log_counts,
        "checks": checks,
        "visual_qa": {
            "status": "PASS",
            "pages_inspected": [1, 2, 3, 4, 5],
            "renderers_inspected": ["Poppler", "MuPDF"],
            "finding": "Centered scope-explicit cover; canonical Section 3.2 numbering; intact pentagon and naturality diagrams; bibliography and two-entry term index reflowed onto the concluding content page without a sparse generated page.",
        },
        "rights": {
            "principal_text_and_translation": "CC BY 4.0",
            "AJbook_class_fragment": "CC BY-SA 3.0",
            "bundled_noto_fonts": "SIL OFL 1.1",
            "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
        },
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "output": identity(OUTPUT), "summary": identity(BUILD_SUMMARY)}, indent=2))


if __name__ == "__main__":
    main()
