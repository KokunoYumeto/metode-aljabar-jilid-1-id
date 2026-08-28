from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "artifacts/unit-044-bab-6-modul-id.pdf"
RENDER_DIR = ROOT / "tmp/pdfs/chapter6-visual-final"
RECEIPT = ROOT / "qa/CHAPTER_6_PDF_STRUCTURAL_QA.json"
EXPECTED_PAGES = 75


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    reader = PdfReader(PDF, strict=True)
    failures: list[str] = []
    if len(reader.pages) != EXPECTED_PAGES:
        failures.append(f"page count {len(reader.pages)} != {EXPECTED_PAGES}")

    root = reader.trailer["/Root"]
    for key in ("/OpenAction", "/AA"):
        action = root.get(key)
        if action is None:
            continue
        resolved = action.get_object() if hasattr(action, "get_object") else action
        # A destination array such as [page, /Fit] is normal PDF navigation.
        # Reject executable/action dictionaries, not safe first-page destinations.
        if isinstance(resolved, dict) and resolved.get("/S") in {
            "/JavaScript", "/Launch", "/SubmitForm", "/ImportData"
        }:
            failures.append(f"forbidden catalog action {key}: {resolved.get('/S')}")
    names = root.get("/Names")
    if names:
        for key in ("/JavaScript", "/EmbeddedFiles"):
            if key in names:
                failures.append(f"forbidden catalog name tree {key}")

    text_lengths: list[int] = []
    link_count = 0
    out_of_bounds_links: list[dict[str, object]] = []
    page_sizes: list[tuple[float, float]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        page_sizes.append((round(width, 3), round(height, 3)))
        text_lengths.append(len(page.extract_text() or ""))
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            link_count += 1
            rect = [float(value) for value in annotation.get("/Rect", [])]
            if len(rect) == 4:
                x0, y0, x1, y1 = rect
                if x0 < -0.5 or y0 < -0.5 or x1 > width + 0.5 or y1 > height + 0.5:
                    out_of_bounds_links.append({"page": page_number, "rect": rect})
    if out_of_bounds_links:
        failures.append(f"{len(out_of_bounds_links)} link rectangles outside page bounds")
    if len(set(page_sizes)) != 1:
        failures.append("inconsistent page sizes")
    low_text_pages = [index + 1 for index, length in enumerate(text_lengths) if length < 25]

    rendered = sorted(RENDER_DIR.glob("page-*.png"))
    if len(rendered) != EXPECTED_PAGES:
        failures.append(f"rendered page count {len(rendered)} != {EXPECTED_PAGES}")

    contact_paths: list[Path] = []
    if len(rendered) == EXPECTED_PAGES:
        thumb_width = 330
        thumb_height = 440
        columns = 5
        rows = 3
        margin = 20
        label_height = 26
        per_sheet = columns * rows
        for sheet_index, start in enumerate(range(0, len(rendered), per_sheet), start=1):
            subset = rendered[start : start + per_sheet]
            canvas = Image.new(
                "RGB",
                (
                    margin + columns * (thumb_width + margin),
                    margin + rows * (thumb_height + label_height + margin),
                ),
                "#d9dde3",
            )
            draw = ImageDraw.Draw(canvas)
            for offset, image_path in enumerate(subset):
                page_number = start + offset + 1
                with Image.open(image_path) as source:
                    image = source.convert("RGB")
                    image.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                    column = offset % columns
                    row = offset // columns
                    x = margin + column * (thumb_width + margin)
                    y = margin + row * (thumb_height + label_height + margin)
                    canvas.paste(image, (x + (thumb_width - image.width) // 2, y))
                    draw.text((x, y + thumb_height + 3), f"PDF page {page_number}", fill="black")
            path = RENDER_DIR / f"contact-{sheet_index:02d}.png"
            canvas.save(path, optimize=True)
            contact_paths.append(path)

    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    receipt = {
        "schema": "o013.chapter6.pdf-structural-qa.v1",
        "status": "PASS" if not failures else "FAIL",
        "pdf": str(PDF.relative_to(ROOT)).replace("\\", "/"),
        "bytes": PDF.stat().st_size,
        "sha256": sha256(PDF),
        "pages": len(reader.pages),
        "page_size_points": list(page_sizes[0]) if page_sizes else None,
        "metadata": metadata,
        "minimum_extracted_text_characters": min(text_lengths) if text_lengths else 0,
        "low_text_pages_under_25_characters": low_text_pages,
        "link_annotations": link_count,
        "out_of_bounds_links": out_of_bounds_links,
        "rendered_pages": len(rendered),
        "contact_sheets": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in contact_paths
        ],
        "failures": failures,
        "visual_inspection": "PENDING_MODEL_INSPECTION",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
