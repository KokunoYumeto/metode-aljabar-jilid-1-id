#!/usr/bin/env python3
"""Build the reader-first 0.5.0 checkpoint PDF from admitted unit PDFs."""

from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "00-metode-aljabar-jilid-1-id-checkpoint-0.5.0-reader.pdf"
COVER = ROOT / "tmp" / "pdfs" / "checkpoint-0.5.0-cover.pdf"
PAGE_SIZE = (498.9, 708.66)
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR_FONT = "CheckpointNotoSans"
BOLD_FONT = "CheckpointNotoSans-Bold"
ITALIC_FONT = "CheckpointNotoSans-Italic"

UNITS = [
    ("Pendahuluan", "unit-001-pendahuluan.pdf"),
    ("Bab 1 - ZFC", "unit-002-bab-1-zfc.pdf"),
    ("Bab 1 - Struktur Urutan dan Bilangan Ordinal", "unit-003-bab-1-struktur-urutan-dan-ordinal.pdf"),
    ("Bab 1 - Rekursi Transfinit dan Penerapannya", "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf"),
    ("Bab 1 - Bilangan Kardinal", "unit-005-bab-1-kardinal.pdf"),
    ("Bab 1 - Semesta Grothendieck", "unit-006-bab-1-semesta-grothendieck.pdf"),
    ("Bab 1 - Latihan", "unit-007-bab-1-latihan.pdf"),
    ("Bab 2 - Pengantar Teori Kategori", "unit-008-bab-2-pengantar-teori-kategori.pdf"),
    ("Bab 2 - Kategori dan Morfisme (2.1)", "unit-009-bab-2-kategori-dan-morfisme.pdf"),
    ("Bab 2 - Fungtor dan Transformasi Natural (2.2)", "unit-010-bab-2-fungtor-dan-transformasi-natural.pdf"),
    ("Bab 2 - Kategori Fungtor (2.3)", "unit-011-bab-2-kategori-fungtor.pdf"),
    ("Bab 2 - Sifat Universal dan Kategori Koma (2.4)", "unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf"),
    ("Bab 2 - Fungtor Representabel dan Lema Yoneda (2.5)", "unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf"),
    ("Bab 2 - Dasar-Dasar Fungtor Adjoin (2.6)", "unit-014-bab-2-fungtor-adjoin-dasar.pdf"),
    ("Bab 2 - Contoh, Keunikan, dan Ekuivalensi Adjoin (2.6)", "unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf"),
    ("Bab 2 - Limit (2.7)", "unit-016-bab-2-limit.pdf"),
    ("Bab 2 - Kelengkapan (2.8)", "unit-017-bab-2-kelengkapan.pdf"),
    ("Bab 2 - Latihan", "unit-018-bab-2-latihan.pdf"),
]


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


def unit_start_pages() -> list[int]:
    """Return 1-based checkpoint page numbers for unit starts."""
    starts: list[int] = []
    next_page = 2  # checkpoint cover is physical page 1
    for _, filename in UNITS:
        starts.append(next_page)
        reader = PdfReader(str(ROOT / "artifacts" / filename))
        next_page += len(reader.pages)
    return starts


def make_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont(REGULAR_FONT, str(FONT_DIR / "NotoSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(BOLD_FONT, str(FONT_DIR / "NotoSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(ITALIC_FONT, str(FONT_DIR / "NotoSans-Italic.ttf")))
    width, height = PAGE_SIZE
    c = canvas.Canvas(
        str(path),
        pagesize=PAGE_SIZE,
        invariant=1,
        pageCompression=1,
        initialFontName=REGULAR_FONT,
        initialFontSize=12,
        initialLeading=14.4,
    )
    navy = HexColor("#152A45")
    blue = HexColor("#316B9B")
    gray = HexColor("#4B5563")
    light_gray = HexColor("#D7DEE7")

    # The only filled region is the unmistakable title masthead. Status and
    # contents use typography and rules, not ambiguous filled/unfilled blocks.
    c.setFillColor(navy)
    c.rect(0, height - 126, width, 126, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont(BOLD_FONT, 10)
    c.drawString(42, height - 38, "CHECKPOINT PEMBACA 0.5.0")
    c.setFont(BOLD_FONT, 25)
    c.drawString(42, height - 73, "Metode Aljabar, Jilid 1")
    c.setFont(REGULAR_FONT, 13)
    c.drawString(42, height - 97, "Edisi Bahasa Indonesia")
    c.setFont(REGULAR_FONT, 8.7)
    c.drawString(42, height - 116, "Karya asli: Wen-Wei Li  |  24 Agustus 2026")

    y = height - 157
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 11)
    c.drawString(42, y, "Cakupan checkpoint")
    c.setStrokeColor(blue)
    c.setLineWidth(1.0)
    c.line(42, y - 8, width - 42, y - 8)
    y -= 24
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 9.2)
    y = draw_wrapped(
        c,
        "Pendahuluan, Bab 1, dan Bab 2 lengkap dalam delapan belas unit. "
        "Bab 3-10 belum disertakan; checkpoint ini merupakan edisi parsial yang aktif dikembangkan.",
        42,
        y,
        width - 84,
        REGULAR_FONT,
        9.2,
        11.5,
    )

    y -= 8
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 10.5)
    c.drawString(42, y, "Isi checkpoint")
    y -= 14
    starts = unit_start_pages()
    c.setFont(REGULAR_FONT, 7.25)
    for unit_number, ((title, _), page) in enumerate(zip(UNITS, starts), start=1):
        c.setFillColor(blue)
        c.drawString(44, y, f"{unit_number:02d}")
        c.setFillColor(gray)
        c.drawString(62, y, title)
        c.setFillColor(blue)
        c.drawRightString(width - 44, y, f"hlm. {page}")
        y -= 9.35

    y -= 1
    c.setStrokeColor(light_gray)
    c.setLineWidth(0.65)
    c.line(42, y, width - 42, y)
    y -= 14
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 8.4)
    c.drawString(42, y, "Sumber, atribusi, dan hak")
    y -= 12
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 6.85)
    y = draw_wrapped(
        c,
        "Diadaptasi secara independen dari Methods of Algebra, Volume 1 karya Wen-Wei Li, "
        "sumber edisi commit c4f7a01f68f5f407906b4b970640cddbbad85f6b. Teks utama dan "
        "adaptasi Indonesia: CC BY 4.0. Lanzhou.png dan fragmen AJbook.cls yang dikreditkan: "
        "CC BY-SA 3.0. Font Noto: OFL 1.1. Pemberitahuan per komponen mengendalikan.",
        42,
        y,
        width - 84,
        REGULAR_FONT,
        6.85,
        8.35,
    )
    y -= 1
    c.setFillColor(navy)
    c.setFont(BOLD_FONT, 6.9)
    c.drawString(42, y, "OpenAI Codex gpt-5.6-sol, Ultra.")
    y -= 10
    c.setFillColor(gray)
    c.setFont(ITALIC_FONT, 6.8)
    draw_wrapped(
        c,
        "Terjemahan independen; bukan edisi resmi dan tidak disahkan oleh penulis atau pihak hulu. "
        "PDF belum bertag; aksesibilitas PDF bertag penuh tidak diklaim.",
        42,
        y,
        width - 84,
        ITALIC_FONT,
        6.8,
        8.3,
    )

    c.setStrokeColor(blue)
    c.setLineWidth(0.7)
    c.line(42, 28, width - 42, 28)
    c.setFillColor(gray)
    c.setFont(REGULAR_FONT, 6.6)
    c.drawString(42, 17, "18 unit | Pendahuluan + Bab 1 + Bab 2 | build, struktur, backend, dan visual telah diperiksa")
    c.showPage()
    c.save()


def prefix_named_page_links(reader: PdfReader, prefix: str) -> None:
    """Namespace named GoTo links before pages from separate PDFs are merged."""
    for page in reader.pages:
        annotations = page.get("/Annots")
        if not annotations:
            continue
        for annotation_ref in annotations.get_object():
            annotation = annotation_ref.get_object()
            destination = annotation.get("/Dest")
            if isinstance(destination, (str, TextStringObject)):
                annotation[NameObject("/Dest")] = TextStringObject(prefix + str(destination))
            action_ref = annotation.get("/A")
            if not action_ref:
                continue
            action = action_ref.get_object()
            if action.get("/S") != "/GoTo":
                continue
            destination = action.get("/D")
            if isinstance(destination, (str, TextStringObject)):
                action[NameObject("/D")] = TextStringObject(prefix + str(destination))


def add_source_outline(writer: PdfWriter, reader: PdfReader, items: list,
                       parent: object, page_offset: int) -> None:
    """Rebuild a source outline below the unit-level checkpoint bookmark."""
    previous = None
    for item in items:
        if isinstance(item, list):
            if previous is not None:
                add_source_outline(writer, reader, item, previous, page_offset)
            continue
        try:
            source_page = reader.get_destination_page_number(item)
        except Exception:
            previous = None
            continue
        if source_page < 0:
            previous = None
            continue
        title = getattr(item, "title", str(item))
        previous = writer.add_outline_item(title, page_offset + source_page, parent=parent)


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    make_cover(COVER)
    writer = PdfWriter()
    cover_reader = PdfReader(str(COVER))
    writer.add_page(cover_reader.pages[0])
    writer.add_named_destination("checkpoint-cover", 0)
    writer.add_outline_item("Cakupan dan isi checkpoint", 0)
    for unit_number, (title, filename) in enumerate(UNITS, start=1):
        source = ROOT / "artifacts" / filename
        reader = PdfReader(str(source))
        prefix = f"u{unit_number:03d}:"
        prefix_named_page_links(reader, prefix)
        page_offset = len(writer.pages)
        for page in reader.pages:
            writer.add_page(page)
        unit_parent = writer.add_outline_item(title, page_offset)
        add_source_outline(writer, reader, reader.outline, unit_parent, page_offset)
        for name, destination in reader.named_destinations.items():
            source_page = reader.get_destination_page_number(destination)
            if source_page >= 0:
                writer.add_named_destination(prefix + name, page_offset + source_page)
    writer.add_metadata(
        {
            "/Title": "Metode Aljabar, Jilid 1 - Edisi Bahasa Indonesia - Checkpoint 0.5.0",
            "/Author": "Wen-Wei Li",
            "/Subject": "Checkpoint parsial publik: pendahuluan serta Bab 1 dan Bab 2 lengkap dalam 18 unit",
            "/Keywords": "aljabar, teori himpunan, teori kategori, fungtor, adjoin, limit, Bahasa Indonesia, checkpoint 0.5.0",
            "/Creator": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "/Producer": "ReportLab and pypdf",
            "/CreationDate": "D:20260824000000+02'00'",
            "/ModDate": "D:20260824000000+02'00'",
        }
    )
    writer.root_object[NameObject("/Lang")] = TextStringObject("id-ID")
    writer.root_object[NameObject("/PageMode")] = NameObject("/UseOutlines")
    with output.open("wb") as stream:
        writer.write(stream)


if __name__ == "__main__":
    build(OUTPUT)
    data = OUTPUT.read_bytes()
    reader = PdfReader(str(OUTPUT))
    print(f"path={OUTPUT}")
    print(f"pages={len(reader.pages)}")
    print(f"bytes={len(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
