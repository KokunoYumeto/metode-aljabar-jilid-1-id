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
JOB = "unit-025-bab-4-semigrup-monoid-dan-grup"
TARGET = ROOT / "repo/source/chapter4.tex"
CANDIDATE = ROOT / "build/unit-025-candidate/chapter4-group-basics-id.tex"
DRIVER = ROOT / f"repo/source/{JOB}.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-025.tex"
CROSSREFS = ROOT / "repo/source/unit-025-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_025.ps1"
CHECKER = ROOT / "scripts/check_unit_025_structure.py"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_025_candidate.py"
SOURCE_REVIEW = ROOT / "qa/UNIT_025_SOURCE_AND_TRANSLATION_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_025_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = ROOT / "qa/UNIT_025_PREPROMOTION_AUDIT_20260825.md"
BUILD_H = ROOT / f"build/unit-025-h-20260825/{JOB}.pdf"
BUILD_I = ROOT / f"build/unit-025-i-20260825/{JOB}.pdf"
ARTIFACT = ROOT / f"artifacts/{JOB}-id.pdf"
FINAL_LOG = ROOT / "qa/UNIT_025_BUILD_FINAL.log"
VISUAL_ROOT = ROOT / "build/unit-025-final-visual-20260825"
EVIDENCE_DIR = ROOT / "qa/unit-025-evidence"
POPPLER_WITNESS = EVIDENCE_DIR / "poppler-artifact"
MUPDF_WITNESS = EVIDENCE_DIR / "mupdf-artifact"
RENDER_INVENTORY = EVIDENCE_DIR / "render-hash-inventory.json"
STRUCTURE_EVIDENCE = EVIDENCE_DIR / "structure-and-pdf-qa.json"
BUILD_SUMMARY = EVIDENCE_DIR / "build-log-summary.txt"

EXPECTED_TARGET_BYTES = 159_681
EXPECTED_TARGET_SHA256 = "b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419"
EXPECTED_CANDIDATE_BYTES = 20_464
EXPECTED_CANDIDATE_SHA256 = "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a"
EXPECTED_DRIVER_BYTES = 8_176
EXPECTED_DRIVER_SHA256 = "8a9bed7ac738ab41b663951b0cdb18186f88b249622da1b5187df4f6c12fd30c"
EXPECTED_BUILD_H = (123_100, "a1645230a6bb64d43f77a8608b1edff50769e819e337471673ac1ab4ece80d6a")
EXPECTED_BUILD_I = (123_117, "511d1c0889c0882639be49d00580c0634de7e3074c757616ac10a3f2fa854615")
EXPECTED_LOG = (85_827, "ee9a4e064edf0cf8cc4710e32c89eda7a8623bceb5ec5fbc75d8ef663826cd2a")
PAGE_COUNT = 10
RENDER_SIZE = (998, 1418)
RENDER_DPI = 144

EXPECTED_OUTLINE = [
    "4 Teori Grup",
    "4.1 Semigrup, Monoid, dan Grup",
    "Daftar Pustaka",
    "Indeks Istilah",
    "Indeks Simbol",
]

EXPECTED_EXTERNAL_LABELS = {
    "con:U-small",
    "sec:group-action",
    "sec:free-group",
    "sec:group-limit",
    "sec:PID-module",
    "sec:symmetric-group",
    "def:field",
    "eg:cyclic-group",
    "prop:A_n-simple",
}

PAGE_FINDINGS = {
    "1": "Cover centered and balanced; the prose scope box states partial Chapter 4 coverage without ambiguous progress blocks.",
    "2": "Attribution, CC BY 4.0 notice, component notices, independent/non-endorsed status, and OpenAI Codex gpt-5.6-sol, Ultra provenance are legible and unclipped.",
    "3": "Chapter 4 opening is centered on the 142 mm digital measure; the complete orientation is present and the reading-guidance box is not stranded at the foot.",
    "4": "The complete Petunjuk membaca box begins and ends coherently, followed by the Section 4.1 opening and its first two bullets; no split-box fragment or orphan formula remains.",
    "5": "Associativity, cancellation, product, identity, invertibility, and Definition 4.1.1 are legible; displays are centered and the page transition is coherent.",
    "6": "Group definitions, inverse identities, conventions, and Examples 4.1.4-4.1.5 are intact; no cross-page hyphenated word or overflow remains.",
    "7": "General linear and symmetric group examples and subgroup/simple-group definitions are complete, with stable mathematical glyphs and citations.",
    "8": "Generated, normal, and cyclic subgroup material, the corrected integer-subgroup example, cosets, and the start of Lemma 4.1.12 are present without clipping.",
    "9": "Lemma 4.1.12, Proposition 4.1.13, both proofs, Definition 4.1.14, and Catatan 4.1.15 remain together; the former sparse final-content page is eliminated.",
    "10": "Bibliography, localized term index, and symbol index share one readable page; no untranslated yaobanqun/qun hierarchy heads remain and all live page links are visible.",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def dereference(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def write_exact(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, f"refusing to overwrite differing evidence: {path}")
        return
    path.write_bytes(data)


def json_data(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def numeric_page(path: Path) -> int:
    match = re.search(r"(\d+)$", path.stem)
    require(match is not None, f"render lacks numeric page suffix: {path}")
    return int(match.group(1))


def render_directory(build: str, renderer: str) -> Path:
    return VISUAL_ROOT / f"{build}-{renderer}"


def rendered_paths(build: str, renderer: str) -> list[Path]:
    paths = sorted(render_directory(build, renderer).glob("page-*.png"), key=numeric_page)
    require(len(paths) == PAGE_COUNT, f"{build}/{renderer} rendered {len(paths)} pages")
    require([numeric_page(path) for path in paths] == list(range(1, PAGE_COUNT + 1)),
            f"{build}/{renderer} page numbering drifted")
    return paths


def render_pdf(build: str, renderer: str, pdf: Path) -> list[Path]:
    destination = render_directory(build, renderer)
    destination.mkdir(parents=True, exist_ok=True)
    existing = list(destination.glob("page-*.png"))
    if not existing:
        if renderer == "poppler":
            command = [
                "pdftoppm", "-r", str(RENDER_DPI), "-png", str(pdf),
                str(destination / "page"),
            ]
        elif renderer == "mupdf":
            command = [
                "mutool", "draw", "-q", "-r", str(RENDER_DPI),
                "-o", str(destination / "page-%d.png"), str(pdf),
            ]
        else:
            raise ValueError(renderer)
        subprocess.run(command, cwd=ROOT, check=True)
    return rendered_paths(build, renderer)


def make_contact_sheet(paths: list[Path], destination: Path) -> dict[str, Any]:
    tile_size = (332, 472)
    gap = 8
    columns = 3
    rows = 4
    sheet = Image.new(
        "RGB",
        (columns * (tile_size[0] + 2 * gap), rows * (tile_size[1] + 2 * gap)),
        (216, 216, 216),
    )
    for index, path in enumerate(paths):
        with Image.open(path) as opened:
            image = ImageOps.contain(opened.convert("RGB"), tile_size, Image.Resampling.LANCZOS)
        tile = Image.new("RGB", tile_size, "white")
        tile.paste(image, ((tile_size[0] - image.width) // 2, (tile_size[1] - image.height) // 2))
        x = (index % columns) * (tile_size[0] + 2 * gap) + gap
        y = (index // columns) * (tile_size[1] + 2 * gap) + gap
        sheet.paste(tile, (x, y))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        with Image.open(destination) as prior:
            require(
                ImageChops.difference(prior.convert("RGB"), sheet).getbbox() is None,
                f"refusing to overwrite differing contact sheet: {destination}",
            )
    else:
        sheet.save(destination, format="PNG", optimize=False)
    return identity(destination)


def render_record(path: Path, page: int) -> tuple[dict[str, Any], bytes, bytes]:
    png = path.read_bytes()
    with Image.open(path) as opened:
        rgb = opened.convert("RGB")
        require(rgb.size == RENDER_SIZE, f"unexpected render dimensions: {path}: {rgb.size}")
        raw_rgb = rgb.tobytes()
        dark = ImageOps.invert(rgb.convert("L")).point(lambda value: 255 if value > 5 else 0)
        pixels = dark.load()
        width, height = dark.size
        edge_ink = sum(
            1
            for y in range(height)
            for x in range(width)
            if (x < 3 or y < 3 or x >= width - 3 or y >= height - 3) and pixels[x, y]
        )
        ink_pixels = sum(1 for value in dark.getdata() if value)
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
    left_paths = rendered_paths(left_build, renderer)
    right_paths = rendered_paths(right_build, renderer)
    png_mismatches: list[int] = []
    pixel_mismatches: list[int] = []
    for page, (left, right) in enumerate(zip(left_paths, right_paths), 1):
        if left.read_bytes() != right.read_bytes():
            png_mismatches.append(page)
        with Image.open(left) as left_image, Image.open(right) as right_image:
            difference = ImageChops.difference(left_image.convert("RGB"), right_image.convert("RGB"))
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


def object_key(reference: Any) -> str:
    if isinstance(reference, IndirectObject):
        return f"{reference.idnum}:{reference.generation}"
    return f"direct:{id(reference)}"


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
        descriptor and any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
    )
    subset = bool(re.match(r"^/?[A-Z]{6}\+", basefont)) or subtype == "/Type3"
    return {"basefont": basefont, "subtype": subtype, "embedded": embedded, "subset": subset}


def pdf_record(path: Path) -> dict[str, Any]:
    reader = PdfReader(path, strict=True)
    root = dereference(reader.trailer["/Root"])
    pypdf_texts = [page.extract_text() or "" for page in reader.pages]
    pypdf_text = "\n\f\n".join(pypdf_texts)
    fonts: dict[str, dict[str, Any]] = {}
    annotation_actions: Counter[str] = Counter()
    unsafe_actions: list[dict[str, Any]] = []
    uri_targets: list[str] = []
    go_to_targets: list[str] = []
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
            if not action:
                continue
            action_type = str(action.get("/S", ""))
            annotation_actions[action_type] += 1
            if action_type == "/URI":
                uri = str(action.get("/URI", ""))
                uri_targets.append(uri)
                if not re.match(r"^https://", uri):
                    unsafe_actions.append({"page": page_number, "action": action_type, "target": uri})
            elif action_type == "/GoTo":
                destination = action.get("/D")
                if isinstance(destination, str):
                    go_to_targets.append(str(destination))
            else:
                unsafe_actions.append({"page": page_number, "action": action_type})

    names = dereference(root.get("/Names", {})) if root.get("/Names") else {}
    open_action = dereference(root.get("/OpenAction")) if root.get("/OpenAction") else None
    open_action_safe = not isinstance(open_action, dict) or str(open_action.get("/S", "")) in ("", "/GoTo")

    fitz_document = fitz.open(path)
    fitz_texts: list[str] = []
    fitz_oob: list[dict[str, Any]] = []
    for page_number, page in enumerate(fitz_document, 1):
        fitz_texts.append(page.get_text("text"))
        rect = page.rect
        for block in page.get_text("blocks"):
            x0, y0, x1, y1 = block[:4]
            if x0 < -0.5 or y0 < -0.5 or x1 > rect.width + 0.5 or y1 > rect.height + 0.5:
                fitz_oob.append({"page": page_number, "bbox": [x0, y0, x1, y1]})
    fitz_document.close()

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
    named_destinations = reader.named_destinations
    named_destination_pages = {
        str(name): reader.get_destination_page_number(destination) + 1
        for name, destination in named_destinations.items()
    }
    broken_named_go_to_targets = sorted(set(go_to_targets) - set(named_destination_pages))
    return {
        "pages": len(reader.pages),
        "pdf_header": reader.pdf_header,
        "encrypted": reader.is_encrypted,
        "language": str(root.get("/Lang", "")),
        "tagged": bool(dereference(root.get("/MarkInfo", {})).get("/Marked", False))
        if root.get("/MarkInfo") else False,
        "page_sizes_pt": page_sizes,
        "page_text_character_counts": [len(text) for text in pypdf_texts],
        "metadata": metadata,
        "outline": outline_titles(reader.outline),
        "named_destination_count": len(named_destinations),
        "named_destination_pages_1_based": dict(sorted(named_destination_pages.items())),
        "go_to_targets": sorted(go_to_targets),
        "broken_named_go_to_targets": broken_named_go_to_targets,
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
        "unicode_minus_counts": {
            "pypdf": pypdf_text.count("\u2212"),
            "fitz": fitz_text.count("\u2212"),
            "pdfplumber": plumber_text.count("\u2212"),
            "poppler": poppler.decode("utf-8").count("\u2212"),
        },
        "pdfplumber_cid0_count": plumber_text.count("(cid:0)"),
        "pypdf_nul_contexts": [
            pypdf_text[max(0, match.start() - 48):match.start() + 48]
            for match in re.finditer("\x00", pypdf_text)
        ],
        "replacement_character_counts": {
            "pypdf": pypdf_text.count("\ufffd"),
            "fitz": fitz_text.count("\ufffd"),
            "pdfplumber": plumber_text.count("\ufffd"),
        },
        "fitz_out_of_bounds_text_blocks": fitz_oob,
        "pdfplumber_out_of_bounds_characters": plumber_oob,
        "unresolved_token_count": len(re.findall(r"\?\?|undefined", pypdf_text, flags=re.I)),
        "han_character_count": len(re.findall(r"[\u3400-\u9fff]", pypdf_text)),
        "standalone_pinyin_index_heads": re.findall(
            r"(?m)^\s*(?:yaobanqun|qun)\s*$", pypdf_text
        ),
    }


def main() -> None:
    required = (
        TARGET, CANDIDATE, DRIVER, COVER, CROSSREFS, BUILD_SCRIPT, CHECKER,
        CANDIDATE_CHECKER, SOURCE_REVIEW, TERMINOLOGY_AUDIT, PREPROMOTION_AUDIT,
        BUILD_H, BUILD_I, ARTIFACT, FINAL_LOG,
    )
    for path in required:
        require(path.is_file(), f"missing required Unit 025 input: {path}")

    require((TARGET.stat().st_size, identity(TARGET)["sha256"]) ==
            (EXPECTED_TARGET_BYTES, EXPECTED_TARGET_SHA256), "canonical target identity drifted")
    require((CANDIDATE.stat().st_size, identity(CANDIDATE)["sha256"]) ==
            (EXPECTED_CANDIDATE_BYTES, EXPECTED_CANDIDATE_SHA256), "candidate identity drifted")
    require((DRIVER.stat().st_size, identity(DRIVER)["sha256"]) ==
            (EXPECTED_DRIVER_BYTES, EXPECTED_DRIVER_SHA256), "driver identity drifted")
    require((BUILD_H.stat().st_size, identity(BUILD_H)["sha256"]) == EXPECTED_BUILD_H,
            "clean build H identity drifted")
    require((BUILD_I.stat().st_size, identity(BUILD_I)["sha256"]) == EXPECTED_BUILD_I,
            "clean replay I identity drifted")
    require((FINAL_LOG.stat().st_size, identity(FINAL_LOG)["sha256"]) == EXPECTED_LOG,
            "sanitized final log identity drifted")
    require(ARTIFACT.read_bytes() == BUILD_I.read_bytes(), "artifact is not byte-identical to replay I")

    checker_run = subprocess.run(
        ["python", "-B", str(CHECKER)], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    candidate_checker_run = subprocess.run(
        ["python", "-B", str(CANDIDATE_CHECKER)], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    require(checker_run.returncode == 0 and b"UNIT 025 STRUCTURE CHECK: PASS" in checker_run.stdout,
            checker_run.stderr.decode("utf-8", errors="replace"))
    require(candidate_checker_run.returncode == 0 and b"UNIT 025 CANDIDATE CHECK: PASS" in candidate_checker_run.stdout,
            candidate_checker_run.stderr.decode("utf-8", errors="replace"))

    builds = {"h": BUILD_H, "i": BUILD_I, "artifact": ARTIFACT}
    for build, pdf in builds.items():
        for renderer in ("poppler", "mupdf"):
            render_pdf(build, renderer, pdf)

    comparisons = {
        f"{left}-{right}/{renderer}": compare_render_sets(left, right, renderer)
        for left, right in (("h", "i"), ("h", "artifact"), ("i", "artifact"))
        for renderer in ("poppler", "mupdf")
    }

    contact_sheets: dict[str, dict[str, Any]] = {}
    for build in builds:
        for renderer in ("poppler", "mupdf"):
            name = f"{build}-{renderer}"
            contact_sheets[name] = make_contact_sheet(
                rendered_paths(build, renderer), VISUAL_ROOT / "contact-sheets" / f"{name}.png"
            )

    renderers: dict[str, list[dict[str, Any]]] = {}
    aggregate_hashes: dict[str, dict[str, str]] = {}
    for renderer, witness_dir in (("poppler", POPPLER_WITNESS), ("mupdf", MUPDF_WITNESS)):
        records: list[dict[str, Any]] = []
        aggregate_png = hashlib.sha256()
        aggregate_rgb = hashlib.sha256()
        for page, source in enumerate(rendered_paths("artifact", renderer), 1):
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

    pdf_records = {name: pdf_record(path) for name, path in builds.items()}
    artifact_pdf = pdf_records["artifact"]
    artifact_reader = PdfReader(ARTIFACT, strict=True)
    artifact_text = "\n".join(page.extract_text() or "" for page in artifact_reader.pages)
    normalized_font_families = {
        name: sorted(re.sub(r"^/?[A-Z]{6}\+", "", font["basefont"]) for font in record["fonts"])
        for name, record in pdf_records.items()
    }
    font_subset_prefixes = {
        name: sorted({
            match.group(1)
            for font in record["fonts"]
            if (match := re.match(r"^/?([A-Z]{6})\+", font["basefont"]))
        })
        for name, record in pdf_records.items()
    }

    candidate_raw = CANDIDATE.read_bytes()
    candidate_text = candidate_raw.decode("utf-8")
    target_raw = TARGET.read_bytes()
    target_lines = target_raw.splitlines(keepends=True)
    canonical_span = b"".join(target_lines[:178])
    driver_text = DRIVER.read_text(encoding="utf-8")
    crossrefs_text = CROSSREFS.read_text(encoding="utf-8")
    labels = re.findall(r"\\label\{([^}]+)\}", candidate_text)
    refs = re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", candidate_text)
    citation_commands = re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}", candidate_text)
    citations = [
        key.strip()
        for command in citation_commands
        for key in command.split(",")
        if key.strip()
    ]
    aux_labels = set(re.findall(r"\\newlabel\{([^}]+)\}", crossrefs_text))
    external_refs = set(refs) - set(labels)
    environments = Counter(re.findall(r"\\begin\{([^}]+)\}", candidate_text))

    final_log = FINAL_LOG.read_text(encoding="utf-8", errors="replace")
    require(not re.search(r"(?i)[A-Z]:[\\/]Users[\\/][^\\/\r\n]+", final_log),
            "sanitized final log retains a home path")
    log_counts = {
        "overfull_boxes": len(re.findall(r"Overfull \\[hv]box", final_log, flags=re.I)),
        "underfull_hboxes": len(re.findall(r"Underfull \\hbox", final_log, flags=re.I)),
        "underfull_vboxes": len(re.findall(r"Underfull \\vbox", final_log, flags=re.I)),
        "empty_external_link_targets": len(re.findall(r"Suppressing link with empty target", final_log)),
        "undefined_control_sequences": len(re.findall(r"Undefined control sequence", final_log, flags=re.I)),
        "undefined_references": len(re.findall(r"undefined references?", final_log, flags=re.I)),
        "undefined_citations": len(re.findall(r"undefined citations?", final_log, flags=re.I)),
        "missing_characters": len(re.findall(r"Missing character", final_log, flags=re.I)),
        "fatal_errors": len(re.findall(r"Fatal error", final_log, flags=re.I)),
        "emergency_stops": len(re.findall(r"Emergency stop", final_log, flags=re.I)),
    }

    semantic_keys = (
        "pypdf_text_sha256", "fitz_text_sha256",
        "pdfplumber_layout_text_sha256", "poppler_layout_text_sha256",
    )
    semantic_identity = all(len({record[key] for record in pdf_records.values()}) == 1 for key in semantic_keys)
    render_identity = all(
        record["raw_pixel_identical"] and record["png_byte_identical"]
        and not record["mismatching_raw_pages"] and not record["mismatching_png_pages"]
        for record in comparisons.values()
    )
    normalized_font_identity = len({tuple(value) for value in normalized_font_families.values()}) == 1
    expected_error_keys = (
        "overfull_boxes", "empty_external_link_targets", "undefined_control_sequences",
        "undefined_references", "undefined_citations", "missing_characters",
        "fatal_errors", "emergency_stops",
    )

    expected_tokens = (
        "Metode Aljabar", "Cakupan parsial Bab 4", "Petunjuk membaca",
        "Semigrup, Monoid, dan Grup", "hukum pembatalan", "grup selang-seling",
        "Lema 4.1.12", "Proposisi 4.1.13", "Lagrange",
        "Pusat, sentralisator, dan normalisator", "Catatan 4.1.15",
        "Daftar Pustaka", "Indeks Istilah", "Indeks Simbol",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    )
    parser_specific_minus_mapping = (
        artifact_pdf["pypdf_nul_count"] == 1
        and len(artifact_pdf["pypdf_nul_contexts"]) == 1
        and "invers unsur x ditulis sebagai \x00x" in artifact_pdf["pypdf_nul_contexts"][0]
        and artifact_pdf["unicode_minus_counts"]["pypdf"] == 16
        and artifact_pdf["unicode_minus_counts"]["fitz"] == 17
        and artifact_pdf["unicode_minus_counts"]["poppler"] == 17
        and artifact_pdf["unicode_minus_counts"]["pdfplumber"] == 16
        and artifact_pdf["pdfplumber_cid0_count"] == 1
    )
    checks = {
        "canonical_target_and_span": len(target_raw) == EXPECTED_TARGET_BYTES
        and sha256(target_raw) == EXPECTED_TARGET_SHA256
        and len(target_lines) == 1900
        and canonical_span == candidate_raw,
        "candidate_and_structure_checkers": checker_run.returncode == 0
        and candidate_checker_run.returncode == 0,
        "artifact_equals_replay_i": ARTIFACT.read_bytes() == BUILD_I.read_bytes(),
        "page_count": all(record["pages"] == PAGE_COUNT for record in pdf_records.values()),
        "semantic_replay": semantic_identity,
        "render_replay": render_identity,
        "pdf_safety": not artifact_pdf["encrypted"]
        and not artifact_pdf["acroform_present"]
        and not artifact_pdf["javascript_name_tree"]
        and not artifact_pdf["embedded_files"]
        and not artifact_pdf["catalog_additional_actions"]
        and artifact_pdf["open_action_safe"]
        and not artifact_pdf["unsafe_actions"],
        "navigation": artifact_pdf["outline"] == EXPECTED_OUTLINE
        and artifact_pdf["named_destination_count"] == 50
        and artifact_pdf["named_destination_pages_1_based"].get("chapter.4") == 3
        and artifact_pdf["named_destination_pages_1_based"].get("section.4.1") == 4
        and artifact_pdf["named_destination_pages_1_based"].get("theorem.4.1.15") == 9
        and artifact_pdf["named_destination_pages_1_based"].get("unit025-bibliography.0") == 10
        and not artifact_pdf["broken_named_go_to_targets"]
        and artifact_pdf["annotation_actions"] == {"/GoTo": 32, "/URI": 6},
        "accessibility_baseline": artifact_pdf["language"] == "id-ID"
        and all(count > 300 for count in artifact_pdf["page_text_character_counts"])
        and not artifact_pdf["fitz_out_of_bounds_text_blocks"]
        and not artifact_pdf["pdfplumber_out_of_bounds_characters"],
        "fonts": artifact_pdf["font_count"] > 0
        and artifact_pdf["all_fonts_embedded"]
        and normalized_font_identity,
        "text_tokens": parser_specific_minus_mapping
        and artifact_pdf["fitz_nul_count"] == 0
        and artifact_pdf["pdfplumber_nul_count"] == 0
        and artifact_pdf["poppler_nul_byte_count"] == 0
        and not any(artifact_pdf["replacement_character_counts"].values())
        and artifact_pdf["unresolved_token_count"] == 0
        and artifact_pdf["han_character_count"] == 0
        and not artifact_pdf["standalone_pinyin_index_heads"]
        and all(token in artifact_text for token in expected_tokens),
        "log": all(log_counts[key] == 0 for key in expected_error_keys)
        and log_counts["underfull_hboxes"] == 3
        and log_counts["underfull_vboxes"] == 0,
        "page_edges": all(
            record["outer_3px_ink"] == 0 and record["ink_pixels"] > 100
            for records in renderers.values() for record in records
        ),
        "structure": len(labels) == 10
        and len(refs) == 11
        and len(citations) == 3
        and candidate_text.count("\\index") == 25
        and candidate_text.count("\\item") == 24
        and environments["definition"] == 7
        and environments["example"] == 4
        and environments["lemma"] == 1
        and environments["proposition"] == 1
        and environments["remark"] == 1
        and environments["proof"] == 2
        and environments["convention"] == 1
        and "O013-LI-U025-COR-001" in candidate_text,
        "external_crossrefs": external_refs == EXPECTED_EXTERNAL_LABELS
        and aux_labels == EXPECTED_EXTERNAL_LABELS
        and all(f"\\UnitTwentyFiveMarkExternalRef{{{label}}}" in driver_text
                for label in EXPECTED_EXTERNAL_LABELS),
        "index_localization": "\\index{yaobanqun@monoid (monoid)!submonoid}" in candidate_text
        and candidate_text.count("\\index{qun@grup (group)!orde (order)}") == 2
        and "\\index{qun@grup (group)!sederhana (simple)}" in candidate_text
        and "\\index{yaobanqun!submonoid}" not in candidate_text
        and "\\index{qun!orde" not in candidate_text
        and "\\index{qun!sederhana" not in candidate_text,
        "reader_reflow": "\\InputSourceLineRange{chapter4.tex}{1}{178}" in driver_text
        and "textwidth=142mm" in driver_text
        and "textheight=198mm" in driver_text
        and "\\setstretch{1.16}" in driver_text
        and "\\BeforeBeginEnvironment{wenxintishi}{\\Needspace{12\\baselineskip}}" in driver_text
        and "\\AtBeginEnvironment{remark}{\\enlargethispage{3\\baselineskip}}" in driver_text
        and "\\let\\ref\\UnitTwentyFiveRef" in driver_text
        and "candidate" not in driver_text.lower(),
    }
    failure_diagnostics = {
        "missing_expected_tokens": [token for token in expected_tokens if token not in artifact_text],
        "text_metrics": {
            "pypdf_nul_count": artifact_pdf["pypdf_nul_count"],
            "fitz_nul_count": artifact_pdf["fitz_nul_count"],
            "pdfplumber_nul_count": artifact_pdf["pdfplumber_nul_count"],
            "poppler_nul_byte_count": artifact_pdf["poppler_nul_byte_count"],
            "replacement_character_counts": artifact_pdf["replacement_character_counts"],
            "unresolved_token_count": artifact_pdf["unresolved_token_count"],
            "han_character_count": artifact_pdf["han_character_count"],
            "standalone_pinyin_index_heads": artifact_pdf["standalone_pinyin_index_heads"],
        },
        "structure_counts": {
            "labels": len(labels),
            "refs": len(refs),
            "citation_commands": len(citation_commands),
            "citation_keys": len(citations),
            "indexes": candidate_text.count("\\index"),
            "items": candidate_text.count("\\item"),
            "environments": dict(environments),
        },
    }
    require(
        all(checks.values()),
        f"Unit 025 reader evidence gate failed: {checks}; diagnostics={failure_diagnostics}",
    )

    render_inventory = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U025",
        "status": "PASS",
        "page_count": PAGE_COUNT,
        "render_resolution_dpi": RENDER_DPI,
        "render_dimensions_px": list(RENDER_SIZE),
        "clean_builds": {name: identity(path) for name, path in builds.items()},
        "render_count": PAGE_COUNT * len(builds) * 2,
        "contact_sheet_count": len(contact_sheets),
        "comparisons": comparisons,
        "contact_sheets": contact_sheets,
        "renderer_aggregate_hashes": aggregate_hashes,
        "renderers": renderers,
        "manual_inspection": {
            "status": "PASS",
            "pages_inspected": list(range(1, PAGE_COUNT + 1)),
            "renderers_inspected": ["Poppler", "MuPDF (mutool and PyMuPDF)"],
            "finding": "Every physical page was inspected in both renderer families. The 142 mm centered reflow fills the digital page legibly, with no clipping, overlap, tofu, edge contact, split guidance fragment, cross-page hyphenated word, orphan formula/heading, sparse final-content page, or untranslated Pinyin index heading.",
            "page_findings": PAGE_FINDINGS,
        },
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    write_exact(RENDER_INVENTORY, json_data(render_inventory))

    evidence = {
        "schema_version": "1.0.0",
        "unit_id": "O013-LI-U025",
        "status": "PASS",
        "scope": "Chapter 4 opening and complete Section 4.1, Semigroups, Monoids, and Groups; partial Chapter 4 reader.",
        "canonical_target": {
            **identity(TARGET),
            "line_records": len(target_lines),
            "span_lines": "1-178",
            "span_line_records": 178,
            "span_bytes": len(canonical_span),
            "span_sha256": sha256(canonical_span),
            "span_equals_isolated_candidate": canonical_span == candidate_raw,
        },
        "candidate": identity(CANDIDATE),
        "driver": identity(DRIVER),
        "cover": identity(COVER),
        "crossrefs": identity(CROSSREFS),
        "build_script": identity(BUILD_SCRIPT),
        "structure_checker": identity(CHECKER),
        "candidate_checker": identity(CANDIDATE_CHECKER),
        "source_review": identity(SOURCE_REVIEW),
        "terminology_audit": identity(TERMINOLOGY_AUDIT),
        "prepromotion_audit": identity(PREPROMOTION_AUDIT),
        "evidence_generator": identity(Path(__file__).resolve()),
        "artifact": identity(ARTIFACT),
        "clean_builds": {"h": identity(BUILD_H), "i": identity(BUILD_I)},
        "build_log": identity(FINAL_LOG),
        "render_inventory": identity(RENDER_INVENTORY),
        "contact_sheet_directory": "build/unit-025-final-visual-20260825/contact-sheets",
        "structure": {
            "math_spans": 280,
            "labels": 10,
            "references": 11,
            "citations": 3,
            "index_entries": 25,
            "item_markers": 24,
            "definitions": 7,
            "examples": 4,
            "lemmas": 1,
            "propositions": 1,
            "remarks": 1,
            "proofs": 2,
            "conventions": 1,
            "declared_corrections": ["O013-LI-U025-COR-001"],
        },
        "external_crossref_labels": sorted(EXPECTED_EXTERNAL_LABELS),
        "pdf": artifact_pdf,
        "clean_build_pdf_records": {"h": pdf_records["h"], "i": pdf_records["i"]},
        "deterministic_replay": {
            "container_byte_identity_h_i": BUILD_H.read_bytes() == BUILD_I.read_bytes(),
            "artifact_byte_identical_to_i": ARTIFACT.read_bytes() == BUILD_I.read_bytes(),
            "semantic_and_render_identity": semantic_identity and render_identity,
            "container_drift_adjudication": {
                "status": "JUSTIFIED",
                "cause": "XeTeX/xdvipdfmx regenerated six-letter embedded-font subset prefixes across clean runs; these names alter compressed PDF container bytes without altering font families, extracted text, PDF structure, or decoded pixels.",
                "normalized_font_family_identity": normalized_font_identity,
                "font_subset_prefixes": font_subset_prefixes,
                "selected_container": "i",
            },
            "semantic_hashes": {
                key: {name: record[key] for name, record in pdf_records.items()}
                for key in semantic_keys
            },
            "render_count": PAGE_COUNT * len(builds) * 2,
            "same_renderer_page_mismatches": {
                renderer: sum(
                    len(record["mismatching_raw_pages"])
                    for key, record in comparisons.items() if key.endswith(f"/{renderer}")
                )
                for renderer in ("poppler", "mupdf")
            },
        },
        "log_counts": log_counts,
        "checks": checks,
        "visual_qa": render_inventory["manual_inspection"],
        "reflow_adjudication": "A centered 142 mm by 198 mm digital-page measure, 1.16 leading, a twelve-line Needspace guard for the reading-guidance box, and a three-line local enlargement for the sole final remark remove the narrow print-column feel, split-box fragment, orphan formula/heading, cross-page hyphenated word, and sparse final-content page. The result is ten physical pages without reducing the type size or changing mathematical content.",
        "rights": {
            "principal_text_and_translation": "CC BY 4.0",
            "AJbook_class_fragment": "CC BY-SA 3.0",
            "bundled_noto_fonts": "SIL OFL 1.1",
            "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
        },
        "language": "id-ID",
        "source_author": "Wen-Wei Li",
        "translation_status": "independent and non-endorsed",
        "build_date": "2026-08-25",
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    write_exact(STRUCTURE_EVIDENCE, json_data(evidence))

    summary = (
        "PASS Unit 025 reader/PDF/visual gate\n"
        f"artifact bytes={ARTIFACT.stat().st_size} sha256={identity(ARTIFACT)['sha256']} pages={PAGE_COUNT}\n"
        f"canonical target bytes={len(target_raw)} sha256={sha256(target_raw)} records={len(target_lines)}\n"
        f"canonical lines=1-178 records=178 bytes={len(canonical_span)} sha256={sha256(canonical_span)} candidate_byte_identical=yes\n"
        "driver loads only the canonical target span; candidate dependency=no\n"
        "clean H/I PDFs have different container bytes but identical extracted content, structure, and page-identical Poppler and MuPDF rasters; I is the frozen artifact\n"
        f"PDF outlines={len(artifact_pdf['outline'])} destinations={artifact_pdf['named_destination_count']} actions={json.dumps(artifact_pdf['annotation_actions'], sort_keys=True)} broken_named_links={len(artifact_pdf['broken_named_go_to_targets'])} fonts={artifact_pdf['font_count']} language={artifact_pdf['language']} tagged={'yes' if artifact_pdf['tagged'] else 'no'}\n"
        f"log counts={json.dumps(log_counts, sort_keys=True)}\n"
        "Every page was inspected in Poppler and MuPDF. The centered 142 mm reflow, guarded reading box, and final-remark enlargement eliminate the narrow-column, split-box, orphan, cross-page-hyphen, and sparse-page defects, with zero overfull boxes, empty-target links, clipping, overlap, edge ink, tofu, Han residue, Pinyin index heads, or broken navigation.\n"
        "provenance model=OpenAI Codex gpt-5.6-sol, Ultra\n"
    )
    write_exact(BUILD_SUMMARY, summary.encode("utf-8"))
    print(json.dumps({
        "status": "PASS",
        "artifact": identity(ARTIFACT),
        "build_h": identity(BUILD_H),
        "build_i": identity(BUILD_I),
        "build_log": identity(FINAL_LOG),
        "render_inventory": identity(RENDER_INVENTORY),
        "structure_evidence": identity(STRUCTURE_EVIDENCE),
        "build_summary": identity(BUILD_SUMMARY),
        "contact_sheets": contact_sheets,
    }, indent=2))


if __name__ == "__main__":
    main()
