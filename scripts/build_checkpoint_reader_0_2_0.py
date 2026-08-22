#!/usr/bin/env python3
"""Build the reader-first 0.2.0 checkpoint PDF from admitted unit PDFs."""

from __future__ import annotations

import hashlib
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "00-metode-aljabar-jilid-1-id-checkpoint-0.2.0-reader.pdf"
COVER = ROOT / "tmp" / "pdfs" / "checkpoint-0.2.0-cover.pdf"
PAGE_SIZE = (498.9, 708.66)

UNITS = [
    ("Pendahuluan", "unit-001-pendahuluan.pdf"),
    ("Bab 1 - ZFC", "unit-002-bab-1-zfc.pdf"),
    ("Bab 1 - Struktur Urutan dan Ordinal", "unit-003-bab-1-struktur-urutan-dan-ordinal.pdf"),
    ("Bab 1 - Rekursi Transfinit dan Penerapannya", "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf"),
    ("Bab 1 - Bilangan Kardinal", "unit-005-bab-1-kardinal.pdf"),
    ("Bab 1 - Semesta Grothendieck", "unit-006-bab-1-semesta-grothendieck.pdf"),
    ("Bab 1 - Latihan", "unit-007-bab-1-latihan.pdf"),
    ("Bab 2 - Pengantar Teori Kategori", "unit-008-bab-2-pengantar-teori-kategori.pdf"),
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


def make_cover(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = PAGE_SIZE
    c = canvas.Canvas(str(path), pagesize=PAGE_SIZE, invariant=1, pageCompression=1)
    navy = HexColor("#152A45")
    blue = HexColor("#316B9B")
    pale = HexColor("#EAF1F7")
    gray = HexColor("#4B5563")

    c.setFillColor(navy)
    c.rect(0, height - 142, width, 142, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(42, height - 42, "CHECKPOINT PEMBACA 0.2.0")
    c.setFont("Helvetica-Bold", 25)
    c.drawString(42, height - 78, "Metode Aljabar, Jilid 1")
    c.setFont("Helvetica", 14)
    c.drawString(42, height - 103, "Arsitektur Dasar - Edisi Bahasa Indonesia")
    c.setFont("Helvetica", 9)
    c.drawString(42, height - 125, "Karya asli: Wen-Wei Li  |  22 Agustus 2026")

    y = height - 174
    c.setFillColor(pale)
    c.roundRect(38, y - 78, width - 76, 82, 8, fill=1, stroke=0)
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(52, y - 18, "STATUS: PARSIAL PUBLIK AKTIF")
    c.setFont("Helvetica", 9.4)
    y2 = draw_wrapped(
        c,
        "Pendahuluan lengkap, Bab 1 lengkap, dan pengantar Bab 2. "
        "Bagian 2.1 dan seluruh bagian sesudahnya belum disertakan.",
        52,
        y - 38,
        width - 104,
        "Helvetica",
        9.4,
        12,
    )

    y = y2 - 24
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(42, y, "Isi checkpoint")
    y -= 18
    starts = [2, 23, 35, 46, 54, 66, 75, 79]
    c.setFont("Helvetica", 8.8)
    for (title, _), page in zip(UNITS, starts):
        c.setFillColor(gray)
        c.drawString(48, y, title)
        c.setFillColor(blue)
        c.drawRightString(width - 44, y, f"hlm. {page}")
        y -= 15

    y -= 8
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(42, y, "Preservasi dan hak")
    y -= 16
    c.setFillColor(gray)
    c.setFont("Helvetica", 8.2)
    y = draw_wrapped(
        c,
        "Versi preservasi: doi:10.5281/zenodo.22060005. Teks utama dan adaptasi "
        "Indonesia: CC BY 4.0. Lanzhou.png dan fragmen AJbook.cls yang dikreditkan: "
        "CC BY-SA 3.0. Font Noto: OFL 1.1. Pemberitahuan per komponen mengendalikan.",
        42,
        y,
        width - 84,
        "Helvetica",
        8.2,
        10.5,
    )
    c.linkURL(
        "https://doi.org/10.5281/zenodo.22060005",
        (42, y + 20, width - 42, y + 45),
        relative=0,
        thickness=0,
    )
    y -= 5
    c.setFont("Helvetica-Oblique", 7.8)
    y = draw_wrapped(
        c,
        "Terjemahan independen; bukan edisi resmi dan tidak disahkan oleh penulis "
        "atau pihak hulu. PDF belum bertag; aksesibilitas PDF bertag penuh tidak diklaim.",
        42,
        y,
        width - 84,
        "Helvetica-Oblique",
        7.8,
        10,
    )

    c.setStrokeColor(blue)
    c.setLineWidth(0.7)
    c.line(42, 34, width - 42, 34)
    c.setFillColor(gray)
    c.setFont("Helvetica", 7)
    c.drawString(42, 22, "Delapan unit yang telah melewati pemeriksaan build, struktur, backend, dan visual semua halaman.")
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
        previous = writer.add_outline_item(
            title,
            page_offset + source_page,
            parent=parent,
        )


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    make_cover(COVER)
    writer = PdfWriter()
    cover_reader = PdfReader(str(COVER))
    writer.add_page(cover_reader.pages[0])
    writer.add_named_destination("checkpoint-cover", 0)
    writer.add_outline_item("Status dan isi checkpoint", 0)
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
            "/Title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Edisi Bahasa Indonesia - Checkpoint 0.2.0",
            "/Author": "Wen-Wei Li",
            "/Subject": "Checkpoint parsial publik: pendahuluan, Bab 1, dan pengantar Bab 2",
            "/Keywords": "aljabar, teori kategori, Bahasa Indonesia, checkpoint 0.2.0",
            "/Creator": "Codex, on instructions of the user",
            "/Producer": "ReportLab and pypdf",
            "/CreationDate": "D:20260822000000+02'00'",
            "/ModDate": "D:20260822000000+02'00'",
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
