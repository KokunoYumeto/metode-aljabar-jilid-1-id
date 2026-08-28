#!/usr/bin/env python3
"""Build the reader-first checkpoint through complete Chapter 6."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts/build_checkpoint_reader_through_chapter_5.py"
OUTPUT = ROOT / "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf"
COVER = ROOT / "tmp/pdfs/checkpoint-through-bab-6-cover.pdf"
RECEIPT = ROOT / "qa/unit-044-evidence/checkpoint-through-bab-6-build.json"
PAGE_SIZE = (498.9, 708.66)
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR_FONT = "CheckpointChapter6NotoSans"
BOLD_FONT = "CheckpointChapter6NotoSans-Bold"
ITALIC_FONT = "CheckpointChapter6NotoSans-Italic"


def load_base():
    spec = importlib.util.spec_from_file_location("checkpoint_chapter_5", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()
UNITS = list(BASE.UNITS) + [
    (
        "Bab 6 - Teori Modul (lengkap)",
        "unit-044-bab-6-modul-id.pdf",
        75,
        "2c493005920fdd757e5786477fdf99b20aced1653348be7a076fa7a829a5c1d3",
    )
]
GROUPS = list(BASE.GROUPS) + [("Bab 6 - Teori Modul", 36, 37)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sources() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for title, filename, expected_pages, expected_sha in UNITS:
        path = ROOT / "artifacts" / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_sha = sha256(path)
        actual_pages = len(PdfReader(str(path), strict=True).pages)
        if actual_sha != expected_sha or actual_pages != expected_pages:
            raise RuntimeError(
                f"{filename}: pages={actual_pages}/{expected_pages}, sha256={actual_sha}/{expected_sha}"
            )
        records.append(
            {
                "title": title,
                "path": path.relative_to(ROOT).as_posix(),
                "pages": actual_pages,
                "bytes": path.stat().st_size,
                "sha256": actual_sha,
            }
        )
    return records


def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, width: float,
                 font: str, size: float, leading: float) -> float:
    words = text.split()
    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if stringWidth(candidate, font, size) <= width:
            line = candidate
            continue
        c.drawString(x, y, line)
        y -= leading
        line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def group_start_pages() -> list[int]:
    return [2 + sum(item[2] for item in UNITS[:start]) for _, start, _ in GROUPS]


def make_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont(REGULAR_FONT, str(FONT_DIR / "NotoSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD_FONT, str(FONT_DIR / "NotoSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(ITALIC_FONT, str(FONT_DIR / "NotoSans-Italic.ttf")))
    width, height = PAGE_SIZE
    c = canvas.Canvas(
        str(path), pagesize=PAGE_SIZE, invariant=1, pageCompression=1,
        initialFontName=REGULAR_FONT, initialFontSize=12, initialLeading=14.4,
    )
    navy, blue, gray, light = (
        HexColor("#152A45"), HexColor("#316B9B"),
        HexColor("#4B5563"), HexColor("#D7DEE7"),
    )
    c.setFillColor(navy)
    c.rect(0, height - 126, width, 126, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont(BOLD_FONT, 10)
    c.drawString(42, height - 38, "CHECKPOINT PEMBACA - MELALUI BAB 6")
    c.setFont(BOLD_FONT, 25)
    c.drawString(42, height - 73, "Metode Aljabar, Jilid 1")
    c.setFont(REGULAR_FONT, 13)
    c.drawString(42, height - 97, "Edisi Bahasa Indonesia")
    c.setFont(REGULAR_FONT, 8.7)
    c.drawString(42, height - 116, "Karya asli: Wen-Wei Li  |  28 Agustus 2026")

    y = height - 157
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 11)
    c.drawString(42, y, "Cakupan checkpoint")
    c.setStrokeColor(blue)
    c.setLineWidth(1)
    c.line(42, y - 8, width - 42, y - 8)
    y -= 25
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 9.2)
    y = draw_wrapped(
        c,
        "Pendahuluan serta Bab 1 sampai Bab 6 lengkap. Bab 7 sampai Bab 10 belum "
        "disertakan; ini adalah checkpoint parsial yang aktif dikembangkan.",
        42, y, width - 84, REGULAR_FONT, 9.2, 11.5,
    )

    y -= 10
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 10.5)
    c.drawString(42, y, "Jalur baca")
    y -= 16
    c.setFont(REGULAR_FONT, 8.5)
    for (title, start, end), page in zip(GROUPS, group_start_pages()):
        c.setFillColor(blue)
        c.drawString(44, y, f"{start + 1:02d}-{end:02d}")
        c.setFillColor(gray)
        c.drawString(82, y, title)
        c.setFillColor(blue)
        c.drawRightString(width - 44, y, f"hlm. {page}")
        y -= 15

    y -= 2
    c.setStrokeColor(light)
    c.setLineWidth(0.65)
    c.line(42, y, width - 42, y)
    y -= 17
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 9)
    c.drawString(42, y, "Sumber, atribusi, dan hak")
    y -= 14
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 7.4)
    y = draw_wrapped(
        c,
        "Diadaptasi secara independen dari Methods of Algebra, Volume 1 karya "
        "Wen-Wei Li, commit sumber c4f7a01f68f5f407906b4b970640cddbbad85f6b. "
        "Teks utama dan adaptasi Indonesia: CC BY 4.0. Fragmen AJbook yang "
        "dikreditkan: CC BY-SA 3.0. Font Noto: OFL 1.1. Font Fandol: GPLv3 "
        "dengan pengecualian font. Pemberitahuan per komponen mengendalikan.",
        42, y, width - 84, REGULAR_FONT, 7.4, 9.2,
    )
    y -= 3
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 7.4)
    c.drawString(42, y, "OpenAI Codex gpt-5.6-sol, Ultra.")
    y -= 12
    c.setFillColor(gray)
    c.setFont(ITALIC_FONT, 7.2)
    draw_wrapped(
        c,
        "Terjemahan independen; bukan edisi resmi dan tidak disahkan oleh penulis "
        "atau pihak hulu. PDF belum bertag; aksesibilitas PDF bertag penuh tidak diklaim.",
        42, y, width - 84, ITALIC_FONT, 7.2, 8.8,
    )
    c.setStrokeColor(blue)
    c.setLineWidth(0.7)
    c.line(42, 28, width - 42, 28)
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 6.6)
    c.drawString(42, 17, "37 komponen | Pendahuluan + Bab 1-6 lengkap | pembaca parsial")
    c.showPage()
    c.save()


def build() -> dict[str, object]:
    inputs = validate_sources()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    make_cover(COVER)
    writer = PdfWriter()
    cover_reader = PdfReader(str(COVER), strict=True)
    writer.add_page(cover_reader.pages[0])
    writer.add_named_destination("checkpoint-through-chapter-6-cover", 0)
    writer.add_outline_item("Cakupan dan jalur baca", 0)

    group_by_start = {start: title for title, start, _ in GROUPS}
    current_group = None
    for index, (title, filename, _, _) in enumerate(UNITS):
        reader = PdfReader(str(ROOT / "artifacts" / filename), strict=True)
        prefix = f"u{index + 1:03d}:"
        BASE.prefix_named_page_links(reader, prefix)
        page_offset = len(writer.pages)
        if index in group_by_start:
            current_group = writer.add_outline_item(group_by_start[index], page_offset)
        for page in reader.pages:
            writer.add_page(page)
        unit_parent = writer.add_outline_item(title, page_offset, parent=current_group)
        BASE.add_source_outline(writer, reader, reader.outline, unit_parent, page_offset)
        for name, destination in reader.named_destinations.items():
            source_page = reader.get_destination_page_number(destination)
            if source_page >= 0:
                writer.add_named_destination(prefix + name, page_offset + source_page)

    writer.add_metadata(
        {
            "/Title": "Metode Aljabar, Jilid 1 - Edisi Bahasa Indonesia - Checkpoint melalui Bab 6",
            "/Author": "Wen-Wei Li",
            "/Subject": "Checkpoint parsial: pendahuluan serta Bab 1 sampai Bab 6 lengkap",
            "/Keywords": "aljabar, teori himpunan, teori kategori, kategori monoidal, teori grup, teori gelanggang, teori modul, Bahasa Indonesia",
            "/Creator": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "/Producer": "ReportLab and pypdf",
            "/CreationDate": "D:20260828000000+02'00'",
            "/ModDate": "D:20260828000000+02'00'",
        }
    )
    writer.root_object[NameObject("/Lang")] = TextStringObject("id-ID")
    writer.root_object[NameObject("/PageMode")] = NameObject("/UseOutlines")
    with OUTPUT.open("wb") as stream:
        writer.write(stream)

    output_bytes = OUTPUT.read_bytes()
    output_pages = len(PdfReader(str(OUTPUT), strict=True).pages)
    expected_pages = 1 + sum(item[2] for item in UNITS)
    if output_pages != expected_pages:
        raise RuntimeError(f"checkpoint pages={output_pages}, expected={expected_pages}")
    receipt = {
        "schema": "o013-checkpoint-through-chapter-6-build-v1",
        "result": "pass",
        "coverage": "Pendahuluan and complete Chapters 1-6",
        "component_count": len(UNITS),
        "inputs": inputs,
        "output": {
            "path": OUTPUT.relative_to(ROOT).as_posix(),
            "pages": output_pages,
            "bytes": len(output_bytes),
            "sha256": hashlib.sha256(output_bytes).hexdigest(),
        },
        "builder": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "bytes": Path(__file__).stat().st_size,
            "sha256": sha256(Path(__file__).resolve()),
        },
    }
    RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    return receipt


if __name__ == "__main__":
    result = build()
    print(json.dumps(result["output"], ensure_ascii=False, indent=2))
