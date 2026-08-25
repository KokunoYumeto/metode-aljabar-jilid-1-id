#!/usr/bin/env python3
"""Build the reader-first 0.6.0 checkpoint PDF from admitted unit PDFs."""

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
OUTPUT = ROOT / "output" / "pdf" / "00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf"
COVER = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-cover.pdf"
PAGE_SIZE = (498.9, 708.66)
FONT_DIR = Path("C:/Windows/Fonts")
REGULAR_FONT = "CheckpointNotoSans"
BOLD_FONT = "CheckpointNotoSans-Bold"
ITALIC_FONT = "CheckpointNotoSans-Italic"

UNITS = [
    ("Pendahuluan", "unit-001-pendahuluan.pdf", 21, "b3fca2af76b793a19877ffc822d6ec89c2494641f7e1dfa468b158c7bec30a3e"),
    ("Bab 1 - ZFC", "unit-002-bab-1-zfc.pdf", 12, "ff2eb3fd1ec5abaa7989d0c29c419c04f99368dc3f278799be460e30042bfe58"),
    ("Bab 1 - Struktur Urutan dan Bilangan Ordinal", "unit-003-bab-1-struktur-urutan-dan-ordinal.pdf", 11, "031e231bc5d2ac74cada865700d8f76dda327941c7f442e6d47324b848103df8"),
    ("Bab 1 - Rekursi Transfinit dan Penerapannya", "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf", 8, "e48aa97d15ad9c192df5d744bfc8290fc816c4b681322295352517a02e267c13"),
    ("Bab 1 - Bilangan Kardinal", "unit-005-bab-1-kardinal.pdf", 12, "205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de"),
    ("Bab 1 - Semesta Grothendieck", "unit-006-bab-1-semesta-grothendieck.pdf", 9, "1fe15c59de6021b376643269423f2ef12e7b986f048ae39a31d8b1df9f7562c4"),
    ("Bab 1 - Latihan", "unit-007-bab-1-latihan.pdf", 4, "e7d4d6745f88b56c7ef840499c8e1d759b2bbbc14a245e8fc477fb0a6504a2b1"),
    ("Bab 2 - Pengantar Teori Kategori", "unit-008-bab-2-pengantar-teori-kategori.pdf", 5, "0db18bfbae3ffd2194447781a77effb4f57f8bd8521baa3acb334b474f0773cd"),
    ("Bab 2 - Kategori dan Morfisme (2.1)", "unit-009-bab-2-kategori-dan-morfisme.pdf", 13, "1a71610ba997348ce22db69944fec3529d9d6e6c2ef6ece48faa30df90ac5ce6"),
    ("Bab 2 - Fungtor dan Transformasi Natural (2.2)", "unit-010-bab-2-fungtor-dan-transformasi-natural.pdf", 15, "a06c4152e6233270cfa138b6c99ae9f307246fe2e1eac6b72a9533c9d74bfce4"),
    ("Bab 2 - Kategori Fungtor (2.3)", "unit-011-bab-2-kategori-fungtor.pdf", 7, "f18ea37d945b08961f14e49581dd13a5a3024307fe3d33a77c7d5bb5631859fe"),
    ("Bab 2 - Sifat Universal dan Kategori Koma (2.4)", "unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf", 10, "1671beea4ab78c848d577f9b8428d5717de2ac55f309f4f075c455409fd878a9"),
    ("Bab 2 - Fungtor Representabel dan Lema Yoneda (2.5)", "unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf", 7, "03ced2b80bf14814d01bc73cf378bfab820ec40ad0571eaa33cf514d79d760cf"),
    ("Bab 2 - Dasar-Dasar Fungtor Adjoin (2.6)", "unit-014-bab-2-fungtor-adjoin-dasar.pdf", 9, "1241ca5ff345ff5315d5e3f4e6fcb1f37af2b0e948f458306c4b790035779d04"),
    ("Bab 2 - Contoh, Keunikan, dan Ekuivalensi Adjoin (2.6)", "unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf", 10, "6f2a9be12465300ac7af2ea086b643b6891b1f9e23af66241a40086ac476c8ef"),
    ("Bab 2 - Limit (2.7)", "unit-016-bab-2-limit.pdf", 16, "6d6838019efca962d7282c7be3df136f32abed3a8f111f2e4e5996bbeb4d789b"),
    ("Bab 2 - Kelengkapan (2.8)", "unit-017-bab-2-kelengkapan.pdf", 9, "bfcec32b3ba20f8c170a3389a1b651613f1fa437945662ca32dd62fcf0edba5e"),
    ("Bab 2 - Latihan", "unit-018-bab-2-latihan.pdf", 4, "4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c"),
    ("Bab 3 - Definisi Dasar (3.1)", "unit-019-bab-3-definisi-dasar.pdf", 12, "af7a4561db5e8ab1798d4475c589beb42f9fb84795bd167c0ffc17241866783a"),
    ("Bab 3 - Keketatan dan Teorema Koherensi (3.2)", "unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf", 5, "8d8a7c8f537681525d97952a7f163f95a5063275047989c26f0387f50172e1ed"),
    ("Bab 3 - Struktur Kepang (3.3)", "unit-021-bab-3-struktur-kepang.pdf", 9, "ff12bd0dbff7ba40d16050aef9f51b2b676dcfbeaa2e5808407373936fc37371"),
    ("Bab 3 - Kategori Diperkaya dan Aditif (3.4)", "unit-022-bab-3-kategori-diperkaya-dan-aditif.pdf", 9, "a9144221d3a4d8d01e186d5f7a81714b0ec240590f23dd9ea1dbf06b5252a323"),
    ("Bab 3 - Sekilas tentang 2-Kategori (3.5)", "unit-023-bab-3-sekilas-tentang-2-kategori.pdf", 7, "5fb682094a829d8abd878aaf3f5e36cda7763323d1a8417d4e36595a7959add4"),
    ("Bab 3 - Latihan", "unit-024-bab-3-latihan-kategori-monoidal.pdf", 4, "1b61a1e2b856f2ef5d9dbc800c6e593aeb776fd85e2480a53b26286639292e71"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_unit_sources() -> None:
    """Reject any drift from the exact 24-PDF admitted source closure."""
    for _, filename, expected_pages, expected_sha256 in UNITS:
        source = ROOT / "artifacts" / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        actual_sha256 = sha256(source)
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"{filename}: sha256 {actual_sha256}, expected {expected_sha256}"
            )
        actual_pages = len(PdfReader(str(source), strict=True).pages)
        if actual_pages != expected_pages:
            raise RuntimeError(
                f"{filename}: {actual_pages} pages, expected {expected_pages}"
            )


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
    validate_unit_sources()
    for _, _, expected_pages, _ in UNITS:
        starts.append(next_page)
        next_page += expected_pages
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
    c.drawString(42, height - 38, "CHECKPOINT PEMBACA 0.6.0")
    c.setFont(BOLD_FONT, 25)
    c.drawString(42, height - 73, "Metode Aljabar, Jilid 1")
    c.setFont(REGULAR_FONT, 13)
    c.drawString(42, height - 97, "Edisi Bahasa Indonesia")
    c.setFont(REGULAR_FONT, 8.7)
    c.drawString(42, height - 116, "Karya asli: Wen-Wei Li  |  25 Agustus 2026")

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
        "Pendahuluan, Bab 1, Bab 2, dan Bab 3 lengkap dalam dua puluh empat unit. "
        "Bab 4-10 belum disertakan; checkpoint ini merupakan edisi parsial yang aktif dikembangkan.",
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
    for unit_number, ((title, _, _, _), page) in enumerate(zip(UNITS, starts), start=1):
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
    c.drawString(42, 17, "24 unit | Pendahuluan + Bab 1 + Bab 2 + Bab 3 | build, struktur, backend, dan visual telah diperiksa")
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
    validate_unit_sources()
    output.parent.mkdir(parents=True, exist_ok=True)
    make_cover(COVER)
    writer = PdfWriter()
    cover_reader = PdfReader(str(COVER))
    writer.add_page(cover_reader.pages[0])
    writer.add_named_destination("checkpoint-cover", 0)
    writer.add_outline_item("Cakupan dan isi checkpoint", 0)
    for unit_number, (title, filename, _, _) in enumerate(UNITS, start=1):
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
            "/Title": "Metode Aljabar, Jilid 1 - Edisi Bahasa Indonesia - Checkpoint 0.6.0",
            "/Author": "Wen-Wei Li",
            "/Subject": "Checkpoint parsial publik: pendahuluan serta Bab 1, Bab 2, dan Bab 3 lengkap dalam 24 unit",
            "/Keywords": (
                "aljabar, teori himpunan, teori kategori, fungtor, adjoin, limit, "
                "kategori monoidal, koherensi, struktur kepang, kategori diperkaya, "
                "kategori aditif, 2-kategori, Bahasa Indonesia, checkpoint 0.6.0"
            ),
            "/Creator": "OpenAI Codex gpt-5.6-sol, Ultra.",
            "/Producer": "ReportLab and pypdf",
            "/CreationDate": "D:20260825000000+02'00'",
            "/ModDate": "D:20260825000000+02'00'",
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
