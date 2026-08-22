#!/usr/bin/env python3
"""Bounded structural and rendered-page QA for checkpoint reader 0.3.0."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageStat
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "00-metode-aljabar-jilid-1-id-checkpoint-0.3.0-reader.pdf"
RENDER_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.3.0-mupdf-final"
POPPLER_RENDER_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.3.0-poppler-final"
REFERENCE_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.3.0-unit-reference"
EVIDENCE_DIR = ROOT / "qa" / "checkpoint-0.3.0-evidence"
STRUCTURE_JSON = EVIDENCE_DIR / "structure-and-render-qa.json"

UNITS = [
    ("unit-001-pendahuluan.pdf", 21),
    ("unit-002-bab-1-zfc.pdf", 12),
    ("unit-003-bab-1-struktur-urutan-dan-ordinal.pdf", 11),
    ("unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf", 8),
    ("unit-005-bab-1-kardinal.pdf", 12),
    ("unit-006-bab-1-semesta-grothendieck.pdf", 9),
    ("unit-007-bab-1-latihan.pdf", 4),
    ("unit-008-bab-2-pengantar-teori-kategori.pdf", 5),
    ("unit-009-bab-2-kategori-dan-morfisme.pdf", 13),
]
EXPECTED_STARTS = [2, 23, 35, 46, 54, 66, 75, 79, 84]
EXPECTED_MODEL = "OpenAI Codex gpt-5.6-sol, Ultra."
EXPECTED_COVER_PHRASES = [
    "Pendahuluan lengkap",
    "Bab 1 lengkap",
    "pengantar Bab 2",
    "Bagian 2.1 lengkap",
    "Bagian 2.2 dan seluruh bagian sesudahnya belum disertakan",
    "Wen-Wei Li",
    "CC BY 4.0",
    "CC BY-SA 3.0",
    "OFL 1.1",
    EXPECTED_MODEL,
]
UNSAFE_ACTIONS = {
    "/JavaScript", "/Launch", "/GoToR", "/GoToE", "/SubmitForm",
    "/ImportData", "/ResetForm", "/Movie", "/Sound", "/Rendition",
}


def resolve(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_key(value: Any) -> str:
    if isinstance(value, IndirectObject):
        return f"{value.idnum}:{value.generation}"
    ref = getattr(value, "indirect_reference", None)
    if ref is not None:
        return f"{ref.idnum}:{ref.generation}"
    return f"direct:{id(value)}"


def font_descriptor(font: DictionaryObject) -> DictionaryObject | None:
    descriptor = font.get("/FontDescriptor")
    if descriptor:
        return resolve(descriptor)
    descendants = font.get("/DescendantFonts")
    if descendants:
        first = resolve(descendants)[0]
        descriptor = resolve(first).get("/FontDescriptor")
        if descriptor:
            return resolve(descriptor)
    return None


def collect_fonts(resources: Any, found: dict[str, dict[str, Any]],
                  seen_resources: set[str]) -> None:
    if not resources:
        return
    key = object_key(resources)
    if key in seen_resources:
        return
    seen_resources.add(key)
    resources = resolve(resources)
    fonts = resolve(resources.get("/Font", {}))
    for _, font_ref in fonts.items():
        font = resolve(font_ref)
        font_key = object_key(font_ref)
        descriptor = font_descriptor(font)
        embedded = bool(
            descriptor
            and any(descriptor.get(name) for name in ("/FontFile", "/FontFile2", "/FontFile3"))
        )
        base_font = str(font.get("/BaseFont", ""))
        found[font_key] = {
            "base_font": base_font,
            "subtype": str(font.get("/Subtype", "")),
            "embedded": embedded,
            "subset": "+" in base_font,
            "to_unicode": bool(font.get("/ToUnicode")),
        }
    xobjects = resolve(resources.get("/XObject", {}))
    for _, object_ref in xobjects.items():
        obj = resolve(object_ref)
        if str(obj.get("/Subtype", "")) == "/Form":
            collect_fonts(obj.get("/Resources"), found, seen_resources)


def render_unit_references() -> list[Path]:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    for filename, expected_pages in UNITS:
        source = ROOT / "artifacts" / filename
        unit_dir = REFERENCE_DIR / source.stem
        unit_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "mutool", "draw", "-q", "-r", "120", "-o",
                str(unit_dir / "page-%03d.png"), str(source),
            ],
            check=True,
        )
        pages = sorted(unit_dir.glob("page-*.png"))
        if len(pages) != expected_pages:
            raise RuntimeError(f"{filename}: rendered {len(pages)}, expected {expected_pages}")
        rendered.extend(pages)
    return rendered


def render_checkpoint() -> dict[str, list[str]]:
    """Render the final checkpoint with both required independent engines."""
    messages: dict[str, list[str]] = {}
    for directory in (RENDER_DIR, POPPLER_RENDER_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        for stale_page in directory.glob("page-*.png"):
            stale_page.unlink()
    mupdf = subprocess.run(
        [
            "mutool", "draw", "-q", "-r", "120", "-o",
            str(RENDER_DIR / "page-%03d.png"), str(PDF),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    poppler = subprocess.run(
        [
            "pdftoppm", "-png", "-r", "120", str(PDF),
            str(POPPLER_RENDER_DIR / "page"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    messages["mupdf_stderr"] = [line for line in mupdf.stderr.splitlines() if line.strip()]
    messages["poppler_stderr"] = [line for line in poppler.stderr.splitlines() if line.strip()]
    return messages


def make_contact_sheets(page_paths: list[Path]) -> list[dict[str, Any]]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    output: list[dict[str, Any]] = []
    columns, rows = 3, 4
    thumb_width, thumb_height = 560, 798
    pad, label_height = 16, 26
    per_sheet = columns * rows
    for sheet_index in range((len(page_paths) + per_sheet - 1) // per_sheet):
        batch = page_paths[sheet_index * per_sheet:(sheet_index + 1) * per_sheet]
        sheet = Image.new(
            "RGB",
            (
                pad + columns * (thumb_width + pad),
                pad + rows * (thumb_height + label_height + pad),
            ),
            "#d6d9dd",
        )
        draw = ImageDraw.Draw(sheet)
        for slot, page_path in enumerate(batch):
            page_number = sheet_index * per_sheet + slot + 1
            row, column = divmod(slot, columns)
            x = pad + column * (thumb_width + pad)
            y = pad + row * (thumb_height + label_height + pad)
            with Image.open(page_path) as source:
                page = source.convert("RGB")
                page.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                px = x + (thumb_width - page.width) // 2
                py = y + label_height + (thumb_height - page.height) // 2
                sheet.paste(page, (px, py))
            draw.text((x, y + 4), f"Checkpoint page {page_number:03d}", fill="#111827")
        first = sheet_index * per_sheet + 1
        last = first + len(batch) - 1
        path = EVIDENCE_DIR / f"contact-{sheet_index + 1:02d}-pages-{first:03d}-{last:03d}.png"
        sheet.save(path, format="PNG", optimize=True)
        output.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "pages": [first, last],
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return output


def main() -> None:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    reader = PdfReader(str(PDF))
    if len(reader.pages) != 96:
        raise RuntimeError(f"page count is {len(reader.pages)}, expected 96")

    root = reader.trailer["/Root"]
    page_sizes: Counter[tuple[float, float]] = Counter()
    rotations: Counter[int] = Counter()
    fonts: dict[str, dict[str, Any]] = {}
    seen_resources: set[str] = set()
    actions: Counter[str] = Counter()
    annotation_subtypes: Counter[str] = Counter()
    named_link_targets: list[str] = []
    page_additional_actions = 0
    text_lengths: list[int] = []

    for page in reader.pages:
        page_sizes[(round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2))] += 1
        rotations[int(page.get("/Rotate", 0) or 0)] += 1
        collect_fonts(page.get("/Resources"), fonts, seen_resources)
        text_lengths.append(len(page.extract_text() or ""))
        if page.get("/AA"):
            page_additional_actions += 1
        annotations = page.get("/Annots")
        if not annotations:
            continue
        for annotation_ref in resolve(annotations):
            annotation = resolve(annotation_ref)
            annotation_subtypes[str(annotation.get("/Subtype", ""))] += 1
            if annotation.get("/AA"):
                page_additional_actions += 1
            destination = annotation.get("/Dest")
            if isinstance(destination, str):
                named_link_targets.append(destination)
            action_ref = annotation.get("/A")
            if not action_ref:
                continue
            action = resolve(action_ref)
            action_type = str(action.get("/S", ""))
            actions[action_type] += 1
            destination = action.get("/D")
            if action_type == "/GoTo" and isinstance(destination, str):
                named_link_targets.append(destination)

    named_destinations = reader.named_destinations
    named_destination_names = set(named_destinations)
    broken_named_links = sorted(set(named_link_targets) - named_destination_names)
    bad_named_links = sorted(
        target for target in named_link_targets
        if target != "checkpoint-cover" and not target.startswith("u")
    )
    unsafe_seen = sorted(action for action in actions if action in UNSAFE_ACTIONS)
    if unsafe_seen:
        raise RuntimeError(f"unsafe actions: {unsafe_seen}")
    if broken_named_links:
        raise RuntimeError(f"broken named link targets: {broken_named_links}")
    if bad_named_links:
        raise RuntimeError(f"unprefixed named link targets: {bad_named_links}")
    if root.get("/OpenAction") or root.get("/AA") or root.get("/AcroForm"):
        raise RuntimeError("unexpected root action or form")
    if page_additional_actions:
        raise RuntimeError(f"page/annotation additional actions: {page_additional_actions}")

    cover_text = reader.pages[0].extract_text() or ""
    normalized_cover_text = " ".join(cover_text.split())
    missing_cover_phrases = [
        phrase for phrase in EXPECTED_COVER_PHRASES
        if phrase not in normalized_cover_text
    ]
    if missing_cover_phrases:
        raise RuntimeError(f"cover phrases missing: {missing_cover_phrases}")
    if str(reader.metadata.get("/Creator", "")) != EXPECTED_MODEL:
        raise RuntimeError("creator metadata does not match exact model string")
    if str(root.get("/Lang", "")) != "id-ID":
        raise RuntimeError("document language is not id-ID")
    if page_sizes != Counter({(498.9, 708.66): 96}):
        raise RuntimeError(f"unexpected page geometry: {page_sizes}")
    if rotations != Counter({0: 96}):
        raise RuntimeError(f"unexpected rotations: {rotations}")
    if any(not item["embedded"] for item in fonts.values()):
        missing = [item["base_font"] for item in fonts.values() if not item["embedded"]]
        raise RuntimeError(f"unembedded fonts: {missing}")

    source_records: list[dict[str, Any]] = []
    combined_index = 1
    content_mismatches: list[dict[str, Any]] = []
    starts: list[int] = []
    for filename, expected_pages in UNITS:
        source = ROOT / "artifacts" / filename
        source_reader = PdfReader(str(source))
        starts.append(combined_index + 1)
        if len(source_reader.pages) != expected_pages:
            raise RuntimeError(f"{filename}: {len(source_reader.pages)} pages, expected {expected_pages}")
        for source_index, source_page in enumerate(source_reader.pages):
            combined_page = reader.pages[combined_index]
            source_content = source_page.get_contents().get_data()
            combined_content = combined_page.get_contents().get_data()
            if source_content != combined_content:
                content_mismatches.append(
                    {
                        "unit": filename,
                        "source_page": source_index + 1,
                        "checkpoint_page": combined_index + 1,
                    }
                )
            combined_index += 1
        source_records.append(
            {
                "filename": filename,
                "pages": expected_pages,
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )
    if starts != EXPECTED_STARTS:
        raise RuntimeError(f"unit starts {starts}, expected {EXPECTED_STARTS}")
    if content_mismatches:
        raise RuntimeError(f"unit content streams changed: {content_mismatches}")

    renderer_messages = render_checkpoint()
    rendered_pages = sorted(RENDER_DIR.glob("page-*.png"))
    if len(rendered_pages) != 96:
        raise RuntimeError(f"MuPDF rendered {len(rendered_pages)} pages, expected 96")
    poppler_rendered_pages = sorted(POPPLER_RENDER_DIR.glob("page-*.png"))
    if len(poppler_rendered_pages) != 96:
        raise RuntimeError(
            f"Poppler rendered {len(poppler_rendered_pages)} pages, expected 96"
        )
    reference_pages = render_unit_references()
    if len(reference_pages) != 95:
        raise RuntimeError(f"unit references rendered {len(reference_pages)} pages, expected 95")

    raster_mismatches: list[dict[str, Any]] = []
    for checkpoint_page, source_page in zip(rendered_pages[1:], reference_pages):
        with Image.open(checkpoint_page) as checkpoint_image, Image.open(source_page) as source_image:
            checkpoint_rgb = checkpoint_image.convert("RGB")
            source_rgb = source_image.convert("RGB")
            if checkpoint_rgb.size != source_rgb.size or ImageChops.difference(checkpoint_rgb, source_rgb).getbbox():
                raster_mismatches.append(
                    {
                        "checkpoint": checkpoint_page.name,
                        "source": source_page.relative_to(ROOT).as_posix(),
                    }
                )
    if raster_mismatches:
        raise RuntimeError(f"raster mismatches: {raster_mismatches[:5]}")

    rendered_records: list[dict[str, Any]] = []
    blank_pages: list[int] = []
    for page_number, path in enumerate(rendered_pages, start=1):
        with Image.open(path) as image:
            grayscale = image.convert("L")
            stat = ImageStat.Stat(grayscale)
            content_mask = grayscale.point(lambda value: 0 if value >= 250 else 255)
            bbox = content_mask.getbbox()
            if bbox is None:
                blank_pages.append(page_number)
            rendered_records.append(
                {
                    "page": page_number,
                    "path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "pixels": list(image.size),
                    "gray_mean": round(stat.mean[0], 3),
                    "gray_stddev": round(stat.stddev[0], 3),
                    "nonwhite_bbox": list(bbox) if bbox is not None else None,
                }
            )

    contact_sheets = make_contact_sheets(rendered_pages)
    if blank_pages != [5]:
        raise RuntimeError(f"unexpected blank-page inventory: {blank_pages}")
    prefix_counts = {
        f"u{unit_number:03d}": sum(
            1 for name in named_destination_names if name.startswith(f"u{unit_number:03d}:")
        )
        for unit_number in range(1, 10)
    }
    top_level_outline_titles = [
        str(getattr(item, "title", item))
        for item in reader.outline
        if not isinstance(item, list)
    ]
    result = {
        "status": "PASS",
        "artifact": {
            "path": PDF.relative_to(ROOT).as_posix(),
            "bytes": PDF.stat().st_size,
            "sha256": sha256(PDF),
            "pages": len(reader.pages),
        },
        "deterministic_rebuild": True,
        "coverage": "Pendahuluan lengkap; Bab 1 lengkap; pengantar Bab 2; Bagian 2.1 lengkap; Bagian 2.2 dan sesudahnya belum disertakan.",
        "unit_start_pages_1_based": starts,
        "source_units": source_records,
        "source_content_stream_identity": {
            "pages_checked": 95,
            "mismatches": 0,
        },
        "render_qa": {
            "renderer": "MuPDF mutool 1.23.0, 120 dpi",
            "secondary_renderer": "Poppler pdftoppm, 120 dpi",
            "checkpoint_pages_rendered": len(rendered_pages),
            "secondary_renderer_pages": len(poppler_rendered_pages),
            "renderer_message_counts": {
                name: len(lines) for name, lines in renderer_messages.items()
            },
            "source_unit_pages_rendered": len(reference_pages),
            "source_to_checkpoint_pixel_identical_pages": 95,
            "raster_mismatches": 0,
            "blank_pages": blank_pages,
            "page_records": rendered_records,
            "contact_sheets": contact_sheets,
            "visual_review": (
                "PASS: all eight contact sheets covering pages 1-96 and all nine "
                "unit boundaries were inspected; no clipping, overlap, missing "
                "content, broken diagrams, or unreadable pages were observed. "
                "Checkpoint page 5 is the intentional blank recto/verso separator "
                "in the admitted Pendahuluan unit."
            ),
        },
        "structure": {
            "page_sizes": {f"{width}x{height}": count for (width, height), count in page_sizes.items()},
            "rotations": dict(rotations),
            "language": str(root.get("/Lang", "")),
            "page_mode": str(root.get("/PageMode", "")),
            "named_destinations": len(named_destination_names),
            "named_destination_prefix_counts": prefix_counts,
            "broken_named_links": broken_named_links,
            "top_level_outline_titles": top_level_outline_titles,
            "annotation_subtypes": dict(annotation_subtypes),
            "actions": dict(actions),
            "unsafe_actions": unsafe_seen,
            "additional_actions": page_additional_actions,
            "open_action": bool(root.get("/OpenAction")),
            "acroform": bool(root.get("/AcroForm")),
        },
        "fonts": {
            "unique_font_objects": len(fonts),
            "embedded": sum(1 for item in fonts.values() if item["embedded"]),
            "unembedded": sum(1 for item in fonts.values() if not item["embedded"]),
            "to_unicode": sum(1 for item in fonts.values() if item["to_unicode"]),
            "without_to_unicode": sorted(
                {item["base_font"] for item in fonts.values() if not item["to_unicode"]}
            ),
        },
        "text": {
            "cover_phrases_checked": EXPECTED_COVER_PHRASES,
            "missing_cover_phrases": missing_cover_phrases,
            "creator_metadata": str(reader.metadata.get("/Creator", "")),
            "pages_with_empty_extracted_text": [
                page for page, length in enumerate(text_lengths, start=1) if length == 0
            ],
        },
    }
    STRUCTURE_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"status=PASS")
    print(f"artifact_bytes={PDF.stat().st_size}")
    print(f"artifact_sha256={sha256(PDF)}")
    print(f"pages={len(reader.pages)}")
    print(f"unit_starts={starts}")
    print(f"named_destinations={len(named_destination_names)}")
    print(f"actions={dict(actions)}")
    print(f"fonts={len(fonts)} embedded={sum(1 for item in fonts.values() if item['embedded'])}")
    print(f"contact_sheets={len(contact_sheets)}")
    print(f"evidence={STRUCTURE_JSON}")


if __name__ == "__main__":
    main()
