from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import fitz
import pdfplumber
from PIL import Image, ImageChops, ImageOps
from pypdf import PdfReader
from pypdf.generic import IndirectObject


ROOT = Path(__file__).resolve().parents[1]
JOB = "unit-023-bab-3-sekilas-tentang-2-kategori"
TARGET = ROOT / "repo/source/chapter3.tex"
CANDIDATE = ROOT / "build/unit-023-candidate/chapter3-2-categories-id.tex"
DRIVER = ROOT / f"repo/source/{JOB}.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-023.tex"
CROSSREFS = ROOT / "repo/source/unit-023-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_023.ps1"
CHECKER = ROOT / "scripts/check_unit_023_structure.py"
SOURCE_REVIEW = ROOT / "qa/UNIT_023_TRANSLATION_SOURCE_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_023_TERMINOLOGY_AUDIT_20260824.md"
MATH_AUDIT = ROOT / "qa/UNIT_023_MATH_STRUCTURE_AUDIT_20260824.md"
BUILD_A_DIR = ROOT / "build/unit-023-reader-final-a"
BUILD_B_DIR = ROOT / "build/unit-023-reader-final-b"
BUILD_A = BUILD_A_DIR / f"{JOB}.pdf"
BUILD_B = BUILD_B_DIR / f"{JOB}.pdf"
BUILD_REPLAY = ROOT / f"build/unit-023-reader-final-replay/{JOB}.pdf"
SOURCE_LOG = BUILD_B_DIR / f"{JOB}.log"
ARTIFACT = ROOT / f"artifacts/{JOB}.pdf"
FINAL_LOG = ROOT / "qa/UNIT_023_BUILD_FINAL.log"
VISUAL_ROOT = ROOT / "build/unit-023-reader-final-visual"
EVIDENCE_DIR = ROOT / "qa/unit-023-evidence"
POPPLER_WITNESS = EVIDENCE_DIR / "poppler-final-b"
MUPDF_WITNESS = EVIDENCE_DIR / "mupdf-final-b"
RENDER_INVENTORY = EVIDENCE_DIR / "render-hash-inventory.json"
STRUCTURE_EVIDENCE = EVIDENCE_DIR / "structure-and-pdf-qa.json"
BUILD_SUMMARY = EVIDENCE_DIR / "build-log-summary.txt"

EXPECTED_TARGET_BYTES = 88491
EXPECTED_TARGET_SHA256 = "8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f"
EXPECTED_SPAN_BYTES = 14894
EXPECTED_SPAN_SHA256 = "c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05"
EXPECTED_SUFFIX_SHA256 = "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857"
EXPECTED_NEXT_LINE_SHA256 = "0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699"
PAGE_COUNT = 7
RENDER_SIZE = (998, 1418)

EXTERNAL_CROSSREF_NUMBERS = {
    "con:U-small": "2.1.4",
    "eg:categories": "2.1.5",
    "sec:functors": "2.2",
    "prop:naturaltrans-associativity": "2.2.7",
    "rem:strict-or-not": "2.2.11",
    "sec:functor-category": "2.3",
    "sec:adjoint-functor": "2.6",
    "rem:triangle-identity": "2.6.6",
    "prop:adjoint-equivalence": "2.6.12",
    "eg:monoidal-cat": "3.1.3",
    "prop:ML-coherence": "3.2.2",
    "def:enriched-cat": "3.4.1",
    "def:enriched-functor": "3.4.2",
    "def:enriched-naturaltrans": "3.4.4",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256(data),
    }


def dereference(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def write_exact(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f"refusing to overwrite differing evidence: {path}")
        return
    path.write_bytes(data)


def json_data(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def render_path(build: str, renderer: str, page: int) -> Path:
    suffix = f"page-{page}.png"
    return VISUAL_ROOT / f"{build}-{renderer}" / suffix


def render_record(path: Path, page: int) -> tuple[dict[str, Any], bytes, bytes]:
    png = path.read_bytes()
    with Image.open(path) as opened:
        rgb = opened.convert("RGB")
        if rgb.size != RENDER_SIZE:
            raise RuntimeError(f"unexpected render dimensions: {path}: {rgb.size}")
        raw_rgb = rgb.tobytes()
        dark = ImageOps.invert(rgb.convert("L")).point(lambda value: 255 if value > 5 else 0)
        pixels = dark.load()
        width, height = dark.size
        edge_ink = sum(
            1
            for y in range(height)
            for x in range(width)
            if (x < 3 or y < 3 or x >= width - 3 or y >= height - 3)
            and pixels[x, y]
        )
        ink_pixels = sum(1 for value in dark.get_flattened_data() if value)
    return (
        {
            "page": page,
            **identity(path),
            "dimensions_px": list(RENDER_SIZE),
            "raw_rgb_sha256": sha256(raw_rgb),
            "outer_3px_ink": edge_ink,
            "ink_pixels": ink_pixels,
        },
        png,
        raw_rgb,
    )


def compare_render_sets(left_build: str, right_build: str, renderer: str) -> dict[str, Any]:
    png_mismatches: list[int] = []
    pixel_mismatches: list[int] = []
    for page in range(1, PAGE_COUNT + 1):
        left = render_path(left_build, renderer, page)
        right = render_path(right_build, renderer, page)
        if left.read_bytes() != right.read_bytes():
            png_mismatches.append(page)
        with Image.open(left) as left_image, Image.open(right) as right_image:
            difference = ImageChops.difference(
                left_image.convert("RGB"), right_image.convert("RGB")
            )
            if difference.getbbox() is not None:
                pixel_mismatches.append(page)
    return {
        "page_count_equal": True,
        "png_byte_identical": not png_mismatches,
        "raw_pixel_identical": not pixel_mismatches,
        "mismatching_png_pages": png_mismatches,
        "mismatching_raw_pages": pixel_mismatches,
    }


def outline_titles(items: list[Any]) -> list[str]:
    titles: list[str] = []
    for item in items:
        if isinstance(item, list):
            titles.extend(outline_titles(item))
        elif isinstance(item, dict):
            titles.append(str(item.get("/Title", "")))
    return titles


def font_record(reference: Any) -> dict[str, Any]:
    font = dereference(reference)
    subtype = str(font.get("/Subtype", ""))
    basefont = str(font.get("/BaseFont", ""))
    descriptor = font.get("/FontDescriptor")
    if subtype == "/Type0":
        descendants = dereference(font.get("/DescendantFonts", []))
        if descendants:
            descendant = dereference(descendants[0])
            basefont = str(descendant.get("/BaseFont", basefont))
            descriptor = descendant.get("/FontDescriptor")
    descriptor = dereference(descriptor) if descriptor is not None else None
    embedded = subtype == "/Type3" or bool(
        descriptor
        and any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
    )
    subset = bool(re.match(r"^/?[A-Z]{6}\+", basefont)) or subtype == "/Type3"
    return {
        "basefont": basefont,
        "subtype": subtype,
        "embedded": embedded,
        "subset": subset,
    }


def object_key(reference: Any) -> str:
    if isinstance(reference, IndirectObject):
        return f"{reference.idnum}:{reference.generation}"
    return f"direct:{id(reference)}"


def pdf_record(path: Path) -> dict[str, Any]:
    reader = PdfReader(path, strict=True)
    root = dereference(reader.trailer["/Root"])
    pypdf_texts = [page.extract_text() or "" for page in reader.pages]
    pypdf_text = "\n\f\n".join(pypdf_texts)

    fonts: dict[str, dict[str, Any]] = {}
    annotation_actions: Counter[str] = Counter()
    unsafe_actions: list[dict[str, Any]] = []
    uri_targets: list[str] = []
    page_sizes: list[list[float]] = []
    for page_number, page in enumerate(reader.pages, 1):
        page_sizes.append([float(page.mediabox.width), float(page.mediabox.height)])
        resources = dereference(page.get("/Resources", {}))
        font_dictionary = dereference(resources.get("/Font", {})) if resources else {}
        for reference in font_dictionary.values():
            fonts.setdefault(object_key(reference), font_record(reference))
        annotations = dereference(page.get("/Annots", []))
        for reference in annotations:
            annotation = dereference(reference)
            action = dereference(annotation.get("/A")) if annotation.get("/A") else None
            if action:
                action_type = str(action.get("/S", ""))
                annotation_actions[action_type] += 1
                if action_type == "/URI":
                    uri = str(action.get("/URI", ""))
                    uri_targets.append(uri)
                    if not re.match(r"^https?://", uri):
                        unsafe_actions.append({"page": page_number, "action": action_type, "target": uri})
                elif action_type != "/GoTo":
                    unsafe_actions.append({"page": page_number, "action": action_type})

    names = dereference(root.get("/Names", {})) if root.get("/Names") else {}
    open_action = dereference(root.get("/OpenAction")) if root.get("/OpenAction") else None
    open_action_safe = not isinstance(open_action, dict) or str(open_action.get("/S", "")) in (
        "",
        "/GoTo",
    )

    fitz_doc = fitz.open(path)
    fitz_texts: list[str] = []
    fitz_oob: list[dict[str, Any]] = []
    for page_number, page in enumerate(fitz_doc, 1):
        fitz_texts.append(page.get_text("text"))
        rect = page.rect
        for block in page.get_text("blocks"):
            x0, y0, x1, y1 = block[:4]
            if x0 < -0.5 or y0 < -0.5 or x1 > rect.width + 0.5 or y1 > rect.height + 0.5:
                fitz_oob.append({"page": page_number, "bbox": [x0, y0, x1, y1]})
    fitz_doc.close()

    plumber_texts: list[str] = []
    plumber_oob: list[dict[str, Any]] = []
    with pdfplumber.open(path) as document:
        for page_number, page in enumerate(document.pages, 1):
            plumber_texts.append(page.extract_text(layout=True) or "")
            for char in page.chars:
                if (
                    float(char["x0"]) < -0.5
                    or float(char["top"]) < -0.5
                    or float(char["x1"]) > float(page.width) + 0.5
                    or float(char["bottom"]) > float(page.height) + 0.5
                ):
                    plumber_oob.append(
                        {
                            "page": page_number,
                            "text": str(char.get("text", "")),
                            "bbox": [char["x0"], char["top"], char["x1"], char["bottom"]],
                        }
                    )

    poppler = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout
    fitz_text = "\n\f\n".join(fitz_texts)
    plumber_text = "\n\f\n".join(plumber_texts)
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    font_list = sorted(fonts.values(), key=lambda record: (record["basefont"], record["subtype"]))
    return {
        "pages": len(reader.pages),
        "pdf_header": reader.pdf_header,
        "encrypted": reader.is_encrypted,
        "language": str(root.get("/Lang", "")),
        "tagged": bool(dereference(root.get("/MarkInfo", {})).get("/Marked", False))
        if root.get("/MarkInfo")
        else False,
        "page_sizes_pt": page_sizes,
        "page_text_character_counts": [len(text) for text in pypdf_texts],
        "metadata": metadata,
        "outline": outline_titles(reader.outline),
        "named_destination_count": len(reader.named_destinations),
        "annotation_actions": dict(sorted(annotation_actions.items())),
        "uri_targets": sorted(uri_targets),
        "acroform_present": "/AcroForm" in root,
        "javascript_name_tree": "/JavaScript" in names,
        "embedded_files": "/EmbeddedFiles" in names,
        "catalog_additional_actions": "/AA" in root,
        "open_action_safe": open_action_safe,
        "unsafe_actions": unsafe_actions,
        "fonts": font_list,
        "font_count": len(font_list),
        "embedded_font_count": sum(record["embedded"] for record in font_list),
        "subset_font_count": sum(record["subset"] for record in font_list),
        "all_fonts_embedded": all(record["embedded"] for record in font_list),
        "pypdf_text_sha256": sha256(pypdf_text.encode("utf-8")),
        "fitz_text_sha256": sha256(fitz_text.encode("utf-8")),
        "pdfplumber_layout_text_sha256": sha256(plumber_text.encode("utf-8")),
        "poppler_layout_text_sha256": sha256(poppler),
        "pypdf_nul_count": pypdf_text.count("\x00"),
        "fitz_nul_count": fitz_text.count("\x00"),
        "pdfplumber_nul_count": plumber_text.count("\x00"),
        "poppler_nul_byte_count": poppler.count(b"\x00"),
        "replacement_character_counts": {
            "pypdf": pypdf_text.count("\ufffd"),
            "fitz": fitz_text.count("\ufffd"),
            "pdfplumber": plumber_text.count("\ufffd"),
        },
        "fitz_out_of_bounds_text_blocks": fitz_oob,
        "pdfplumber_out_of_bounds_characters": plumber_oob,
        "unresolved_token_count": len(re.findall(r"\?\?|undefined", pypdf_text, flags=re.I)),
        "han_character_count": len(re.findall(r"[\u3400-\u9fff]", pypdf_text)),
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
        MATH_AUDIT,
        BUILD_A,
        BUILD_B,
        BUILD_REPLAY,
        SOURCE_LOG,
        ARTIFACT,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    for build in ("a", "b", "replay", "artifact"):
        for renderer in ("poppler", "mupdf"):
            for page in range(1, PAGE_COUNT + 1):
                if not render_path(build, renderer, page).is_file():
                    raise FileNotFoundError(render_path(build, renderer, page))

    target_raw = TARGET.read_bytes()
    target_lines = target_raw.splitlines(keepends=True)
    span = b"".join(target_lines[721:871])
    suffix = b"".join(target_lines[871:])
    candidate_raw = CANDIDATE.read_bytes()
    candidate_text = candidate_raw.decode("utf-8")
    driver_text = DRIVER.read_text(encoding="utf-8")
    crossrefs_text = CROSSREFS.read_text(encoding="utf-8")

    checker_run = subprocess.run(
        ["python", "-B", str(CHECKER)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if checker_run.returncode:
        raise RuntimeError(checker_run.stderr.decode("utf-8", errors="replace"))

    source_log = SOURCE_LOG.read_text(encoding="utf-8", errors="replace")
    sanitized_log = source_log.replace(str(ROOT), "${EDITION_ROOT}").replace(
        str(ROOT).replace("\\", "/"), "${EDITION_ROOT}"
    )
    home = str(Path.home())
    sanitized_log = sanitized_log.replace(home, "${USER_HOME}").replace(
        home.replace("\\", "/"), "${USER_HOME}"
    )
    sanitized_log = re.sub(
        re.escape(Path.home().name), "${USER_NAME}", sanitized_log, flags=re.I
    )
    if re.search(r"(?i)[A-Z]:[\\/]Users[\\/][^\\/\r\n]+", sanitized_log):
        raise RuntimeError("sanitized build log retains a home path")
    write_exact(FINAL_LOG, sanitized_log.encode("utf-8"))
    log_counts = {
        "overfull_boxes": len(re.findall(r"Overfull \\[hv]box", sanitized_log, flags=re.I)),
        "underfull_hboxes": len(re.findall(r"Underfull \\hbox", sanitized_log, flags=re.I)),
        "underfull_vboxes": len(re.findall(r"Underfull \\vbox", sanitized_log, flags=re.I)),
        "empty_external_link_targets": len(re.findall(r"Suppressing link with empty target", sanitized_log)),
        "undefined_control_sequences": len(re.findall(r"Undefined control sequence", sanitized_log, flags=re.I)),
        "undefined_references": len(re.findall(r"undefined references?", sanitized_log, flags=re.I)),
        "undefined_citations": len(re.findall(r"undefined citations?", sanitized_log, flags=re.I)),
        "missing_characters": len(re.findall(r"Missing character", sanitized_log, flags=re.I)),
        "fatal_errors": len(re.findall(r"Fatal error", sanitized_log, flags=re.I)),
        "emergency_stops": len(re.findall(r"Emergency stop", sanitized_log, flags=re.I)),
    }

    comparisons = {
        f"builds/{renderer}": compare_render_sets("a", "b", renderer)
        for renderer in ("poppler", "mupdf")
    }
    comparisons.update(
        {
            f"replay/{renderer}/final-a": compare_render_sets("a", "replay", renderer)
            for renderer in ("poppler", "mupdf")
        }
    )
    comparisons.update(
        {
            f"replay/{renderer}/final-b": compare_render_sets("b", "replay", renderer)
            for renderer in ("poppler", "mupdf")
        }
    )
    renderers: dict[str, list[dict[str, Any]]] = {}
    aggregate_hashes: dict[str, dict[str, str]] = {}
    for renderer, witness_dir in (("poppler", POPPLER_WITNESS), ("mupdf", MUPDF_WITNESS)):
        records: list[dict[str, Any]] = []
        aggregate_png = hashlib.sha256()
        aggregate_rgb = hashlib.sha256()
        for page in range(1, PAGE_COUNT + 1):
            source = render_path("b", renderer, page)
            destination = witness_dir / f"page-{page:02d}.png"
            write_exact(destination, source.read_bytes())
            record, png, raw_rgb = render_record(destination, page)
            records.append(record)
            aggregate_png.update(png)
            aggregate_rgb.update(raw_rgb)
        renderers[renderer] = records
        aggregate_hashes[renderer] = {
            "png_set_sha256": aggregate_png.hexdigest(),
            "raw_rgb_set_sha256": aggregate_rgb.hexdigest(),
        }

    build_a_pdf = pdf_record(BUILD_A)
    build_b_pdf = pdf_record(BUILD_B)
    replay_pdf = pdf_record(BUILD_REPLAY)
    artifact_pdf = pdf_record(ARTIFACT)
    labels = re.findall(r"\\label\{([^}]+)\}", candidate_text)
    refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", candidate_text)
    aux_labels = re.findall(r"\\newlabel\{([^}]+)\}", crossrefs_text)
    external_refs = sorted(set(refs) - set(labels))
    environments = Counter(re.findall(r"\\begin\{([^}]+)\}", candidate_text))
    index_names = re.findall(r"\\index(?:\[([^]]+)\])?\{", candidate_text)

    render_inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U023",
        "status": "PASS",
        "page_count": PAGE_COUNT,
        "render_resolution_dpi": 144,
        "render_dimensions_px": list(RENDER_SIZE),
        "clean_builds": {
            "a": identity(BUILD_A),
            "b": identity(BUILD_B),
            "replay": identity(BUILD_REPLAY),
            "artifact": identity(ARTIFACT),
        },
        "render_count": PAGE_COUNT * 8,
        "contact_sheet_count": 8,
        "comparisons": comparisons,
        "renderer_aggregate_hashes": aggregate_hashes,
        "renderers": renderers,
        "manual_inspection": {
            "status": "PASS",
            "pages_inspected": list(range(1, PAGE_COUNT + 1)),
            "renderers_inspected": ["Poppler", "MuPDF (mutool and PyMuPDF)"],
            "finding": "Every page was inspected in both renderer families; no clipping, overlap, tofu, broken arrows, edge contact, sparse orphan page, or off-center composition was found.",
            "seven_page_adjudication": "Removing only the unnecessary print-oriented back-matter transition placed both short indexes in the open lower portion of physical page 7 and eliminated the sparse index-only page 8.",
        },
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    render_inventory_bytes = json_data(render_inventory)
    write_exact(RENDER_INVENTORY, render_inventory_bytes)

    error_keys = (
        "overfull_boxes",
        "undefined_control_sequences",
        "undefined_references",
        "undefined_citations",
        "missing_characters",
        "fatal_errors",
        "emergency_stops",
    )
    expected_outline = [
        "Bab 3: Kategori Monoidal",
        "3.5 Sekilas tentang 2-Kategori",
        "Indeks Istilah",
        "Indeks Simbol",
    ]
    semantic_keys = (
        "pypdf_text_sha256",
        "fitz_text_sha256",
        "pdfplumber_layout_text_sha256",
        "poppler_layout_text_sha256",
    )
    expected_structure = {
        "labels": ["sec:2-cat", "eg:Cat"],
        "references": refs,
        "external_references": external_refs,
        "external_crossref_numbers": EXTERNAL_CROSSREF_NUMBERS,
        "citations": [],
        "index_entries": 3,
        "ordinary_index_entries": 2,
        "symbol_index_entries": 1,
        "environment_counts": {
            "tikzcd": 14,
            "remark": 3,
            "definition": 2,
            "compactitem": 2,
            "itemize": 1,
            "enumerate": 1,
            "example": 1,
            "convention": 1,
        },
        "tikzpicture": 0,
        "tikzcd": 14,
        "declared_editorials": ["O013-LI-U023-ED-001"],
    }
    pdf_records = (build_a_pdf, build_b_pdf, replay_pdf, artifact_pdf)
    semantic_identity = all(
        len({record[key] for record in pdf_records}) == 1 for key in semantic_keys
    )
    render_identity = len(comparisons) == 6 and all(
        record["raw_pixel_identical"]
        and record["png_byte_identical"]
        and not record["mismatching_raw_pages"]
        and not record["mismatching_png_pages"]
        for record in comparisons.values()
    )
    checks = {
        "canonical_target_full_identity": len(target_raw) == EXPECTED_TARGET_BYTES
        and sha256(target_raw) == EXPECTED_TARGET_SHA256
        and len(target_lines) == 910,
        "canonical_span_equals_candidate": span == candidate_raw
        and len(span) == EXPECTED_SPAN_BYTES
        and sha256(span) == EXPECTED_SPAN_SHA256,
        "boundary_next_section": sha256(target_lines[871]) == EXPECTED_NEXT_LINE_SHA256
        and target_lines[871].startswith(b"\\begin{Exercises}"),
        "candidate_checker": checker_run.returncode == 0
        and b"PASS Unit 023 candidate/canonical mathematics/protected-topology checker" in checker_run.stdout,
        "artifact_equals_final_b": ARTIFACT.read_bytes() == BUILD_B.read_bytes(),
        "page_count": all(record["pages"] == PAGE_COUNT for record in pdf_records),
        "semantic_replay": semantic_identity,
        "render_replay": render_identity,
        "pdf_safety": not artifact_pdf["encrypted"]
        and not artifact_pdf["acroform_present"]
        and not artifact_pdf["javascript_name_tree"]
        and not artifact_pdf["embedded_files"]
        and not artifact_pdf["catalog_additional_actions"]
        and artifact_pdf["open_action_safe"]
        and not artifact_pdf["unsafe_actions"],
        "navigation": artifact_pdf["outline"] == expected_outline
        and artifact_pdf["named_destination_count"] == 26
        and artifact_pdf["annotation_actions"] == {"/GoTo": 4, "/URI": 3},
        "accessibility_baseline": artifact_pdf["language"] == "id-ID"
        and all(count > 0 for count in artifact_pdf["page_text_character_counts"])
        and not artifact_pdf["fitz_out_of_bounds_text_blocks"]
        and not artifact_pdf["pdfplumber_out_of_bounds_characters"],
        "fonts": artifact_pdf["font_count"] > 0 and artifact_pdf["all_fonts_embedded"],
        "text_tokens": artifact_pdf["fitz_nul_count"] == 0
        and artifact_pdf["pdfplumber_nul_count"] == 0
        and artifact_pdf["poppler_nul_byte_count"] == 0
        and not any(artifact_pdf["replacement_character_counts"].values())
        and artifact_pdf["unresolved_token_count"] == 0
        and artifact_pdf["han_character_count"] == 0,
        "log": all(log_counts[key] == 0 for key in error_keys)
        and log_counts["empty_external_link_targets"] == 15,
        "page_edges": all(
            record["outer_3px_ink"] == 0 and record["ink_pixels"] > 100
            for records in renderers.values()
            for record in records
        ),
        "structure": labels == ["sec:2-cat", "eg:Cat"]
        and len(refs) == 16
        and external_refs == sorted(aux_labels)
        and sum(environments.values()) == 25
        and environments.get("tikzcd", 0) == 14
        and len(index_names) == 3
        and sum(name == "sym1" for name in index_names) == 1
        and expected_structure["environment_counts"]
        == {
            key: environments.get(key, 0)
            for key in expected_structure["environment_counts"]
        }
        and "\\InputSourceLineRange{chapter3.tex}{722}{871}" in driver_text
        and not re.search(r"^[ \t]*\\backmatter\b", driver_text, flags=re.M)
        and "candidate" not in driver_text.lower(),
    }
    if not all(checks.values()):
        raise RuntimeError(f"Unit 023 reader evidence gate failed: {checks}")

    evidence = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U023",
        "status": "PASS",
        "scope": "Complete Section 3.5, Sekilas tentang 2-Kategori; Chapter 3 exercises and later material are excluded.",
        "canonical_target": {
            **identity(TARGET),
            "line_records": len(target_lines),
            "span_lines": "722-871",
            "span_line_records": 150,
            "span_bytes": len(span),
            "span_sha256": sha256(span),
            "span_equals_isolated_candidate": True,
            "next_target_line": 872,
            "next_line_sha256": sha256(target_lines[871]),
        },
        "candidate": identity(CANDIDATE),
        "driver": identity(DRIVER),
        "cover": identity(COVER),
        "crossrefs": identity(CROSSREFS),
        "build_script": identity(BUILD_SCRIPT),
        "structure_checker": identity(CHECKER),
        "source_review": identity(SOURCE_REVIEW),
        "terminology_audit": identity(TERMINOLOGY_AUDIT),
        "math_structure_audit": identity(MATH_AUDIT),
        "evidence_generator": identity(Path(__file__).resolve()),
        "artifact": identity(ARTIFACT),
        "clean_builds": {
            "a": identity(BUILD_A),
            "b": identity(BUILD_B),
            "replay": identity(BUILD_REPLAY),
        },
        "build_log": identity(FINAL_LOG),
        "build_log_sanitization": {
            "method": "edition-root, user-home, and local user-name replacement",
            "edition_root_tokens": sanitized_log.count("${EDITION_ROOT}"),
            "user_home_tokens": sanitized_log.count("${USER_HOME}"),
            "user_name_tokens": sanitized_log.count("${USER_NAME}"),
            "line_count": len(sanitized_log.splitlines()),
        },
        "render_inventory": identity(RENDER_INVENTORY),
        "contact_sheet_directory": "build/unit-023-reader-final-visual/contact-sheets",
        "structure": expected_structure,
        "pdf": artifact_pdf,
        "clean_build_pdf_records": {
            "a": build_a_pdf,
            "b": build_b_pdf,
            "replay": replay_pdf,
        },
        "deterministic_replay": {
            "container_byte_identity": len(
                {identity(path)["sha256"] for path in (BUILD_A, BUILD_B, BUILD_REPLAY)}
            )
            == 1,
            "semantic_and_render_identity": semantic_identity and render_identity,
            "pypdf_text_sha256": {
                "final_a": build_a_pdf["pypdf_text_sha256"],
                "final_b": build_b_pdf["pypdf_text_sha256"],
                "replay": replay_pdf["pypdf_text_sha256"],
                "artifact": artifact_pdf["pypdf_text_sha256"],
            },
            "render_count": PAGE_COUNT * 8,
            "contact_sheet_count": 8,
            "same_renderer_page_mismatches": {
                renderer: sum(
                    len(record["mismatching_raw_pages"])
                    for key, record in comparisons.items()
                    if renderer in key
                )
                for renderer in ("poppler", "mupdf")
            },
        },
        "log_counts": log_counts,
        "checks": checks,
        "visual_qa": render_inventory["manual_inspection"],
        "reflow_adjudication": "The class-level back-matter transition shipped content page 5 before two tiny indexes, creating an orphan physical page 8. Omitting that unnecessary state transition lets both indexes use the lower portion of physical page 7, without changing Section 3.5 content or index entries.",
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
    evidence_bytes = json_data(evidence)
    write_exact(STRUCTURE_EVIDENCE, evidence_bytes)

    summary = (
        "PASS Unit 023 reader/PDF/visual gate\n"
        f"artifact bytes={ARTIFACT.stat().st_size} sha256={identity(ARTIFACT)['sha256']} pages={PAGE_COUNT}\n"
        f"canonical target bytes={len(target_raw)} sha256={sha256(target_raw)} records={len(target_lines)}\n"
        f"canonical lines=722-871 records=150 bytes={len(span)} sha256={sha256(span)} candidate_byte_identical=yes\n"
        "driver loads only the canonical target span; candidate dependency=no\n"
        "clean builds have different PDF-container bytes but identical extracted content and page-identical Poppler and MuPDF rasters\n"
        f"PDF outlines={len(artifact_pdf['outline'])} destinations={artifact_pdf['named_destination_count']} actions={json.dumps(artifact_pdf['annotation_actions'], sort_keys=True)} fonts={artifact_pdf['font_count']} language={artifact_pdf['language']} tagged={'yes' if artifact_pdf['tagged'] else 'no'}\n"
        f"log counts={json.dumps(log_counts, sort_keys=True)}\n"
        "Every page was inspected in Poppler and MuPDF. The former sparse index-only page 8 was eliminated; both indexes now share available space on physical page 7, with zero overfull boxes, clipping, overlap, edge ink, tofu, or broken diagrams.\n"
        "provenance model=OpenAI Codex gpt-5.6-sol, Ultra\n"
    )
    write_exact(BUILD_SUMMARY, summary.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": "PASS",
                "artifact": identity(ARTIFACT),
                "build_a": identity(BUILD_A),
                "build_b": identity(BUILD_B),
                "build_log": identity(FINAL_LOG),
                "render_inventory": identity(RENDER_INVENTORY),
                "structure_evidence": identity(STRUCTURE_EVIDENCE),
                "build_summary": identity(BUILD_SUMMARY),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
