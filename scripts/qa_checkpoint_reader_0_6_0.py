#!/usr/bin/env python3
"""Deterministic structural, navigation, accessibility, safety, and render QA for 0.6.0."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageStat
from pypdf import PdfReader
from pypdf.generic import DictionaryObject, IndirectObject

import build_checkpoint_reader_0_6_0 as checkpoint_builder


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf" / "00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf"
REBUILD = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-deterministic-rebuild.pdf"
RENDER_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-mupdf-final"
POPPLER_RENDER_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-poppler-final"
REFERENCE_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-unit-reference"
EVIDENCE_DIR = ROOT / "qa" / "checkpoint-0.6.0-evidence"
STRUCTURE_JSON = EVIDENCE_DIR / "structure-text-navigation-font-render-qa.json"
VISUAL_REVIEW = EVIDENCE_DIR / "VISUAL_REVIEW.md"
WARNING_EQUIV_DIR = ROOT / "tmp" / "pdfs" / "checkpoint-0.6.0-poppler-warning-equivalence"

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
EXPECTED_STARTS = [
    2, 23, 35, 46, 54, 66, 75, 79, 84, 97, 112, 119,
    129, 136, 145, 155, 171, 180, 184, 196, 201, 210, 219, 226,
]
EXPECTED_TOTAL_PAGES = 229
EXPECTED_SOURCE_PAGES = 228
EXPECTED_BLANK_PAGES = [5]
EXPECTED_CONTACT_SHEETS = 20
EXPECTED_MODEL = "OpenAI Codex gpt-5.6-sol, Ultra."
EXPECTED_TITLE = "Metode Aljabar, Jilid 1 - Edisi Bahasa Indonesia - Checkpoint 0.6.0"
EXPECTED_COVER_PHRASES = [
    "Pendahuluan, Bab 1, Bab 2, dan Bab 3 lengkap dalam dua puluh empat unit",
    "Bab 4-10 belum disertakan",
    "edisi parsial yang aktif dikembangkan",
    "Wen-Wei Li",
    "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
    "CC BY 4.0",
    "CC BY-SA 3.0",
    "OFL 1.1",
    EXPECTED_MODEL,
    "bukan edisi resmi dan tidak disahkan",
]
EXPECTED_KEYWORDS = [
    "kategori monoidal",
    "koherensi",
    "struktur kepang",
    "kategori diperkaya",
    "kategori aditif",
    "2-kategori",
    "Bahasa Indonesia",
    "checkpoint 0.6.0",
]
UNSAFE_ACTIONS = {
    "/JavaScript", "/Launch", "/GoToR", "/GoToE", "/SubmitForm",
    "/ImportData", "/ResetForm", "/Movie", "/Sound", "/Rendition",
}
UNSAFE_ANNOTATION_SUBTYPES = {
    "/FileAttachment", "/Movie", "/Screen", "/Sound", "/RichMedia",
}
UNSAFE_NAME_TREES = {"/JavaScript", "/EmbeddedFiles"}


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


def collect_fonts(
    resources: Any,
    found: dict[str, dict[str, Any]],
    seen_resources: set[str],
) -> None:
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


def clear_pngs(directory: Path, pattern: str = "*.png") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for stale in directory.glob(pattern):
        stale.unlink()


def validate_source_closure() -> list[dict[str, Any]]:
    """Independently pin all 24 admitted source PDFs before any rebuild."""
    if checkpoint_builder.UNITS != UNITS:
        raise RuntimeError("builder manifest differs from independent QA manifest")
    source_records: list[dict[str, Any]] = []
    page_total = 0
    for title, filename, expected_pages, expected_sha256 in UNITS:
        source = ROOT / "artifacts" / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        actual_sha256 = sha256(source)
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"{filename}: sha256 {actual_sha256}, expected {expected_sha256}"
            )
        source_reader = PdfReader(str(source), strict=True)
        actual_pages = len(source_reader.pages)
        if actual_pages != expected_pages:
            raise RuntimeError(
                f"{filename}: {actual_pages} pages, expected {expected_pages}"
            )
        page_total += actual_pages
        source_records.append(
            {
                "title": title,
                "filename": filename,
                "pages": actual_pages,
                "bytes": source.stat().st_size,
                "sha256": actual_sha256,
            }
        )
    if page_total != EXPECTED_SOURCE_PAGES:
        raise RuntimeError(
            f"source closure has {page_total} pages, expected {EXPECTED_SOURCE_PAGES}"
        )
    return source_records


def verify_deterministic_rebuild() -> dict[str, Any]:
    """Rebuild to a separate temp path and require byte-for-byte identity."""
    REBUILD.parent.mkdir(parents=True, exist_ok=True)
    if REBUILD.exists():
        REBUILD.unlink()
    checkpoint_builder.build(REBUILD)
    rebuilt_reader = PdfReader(str(REBUILD), strict=True)
    rebuilt_sha256 = sha256(REBUILD)
    final_sha256 = sha256(PDF)
    if len(rebuilt_reader.pages) != EXPECTED_TOTAL_PAGES:
        raise RuntimeError(
            f"deterministic rebuild has {len(rebuilt_reader.pages)} pages, "
            f"expected {EXPECTED_TOTAL_PAGES}"
        )
    if REBUILD.stat().st_size != PDF.stat().st_size or rebuilt_sha256 != final_sha256:
        raise RuntimeError(
            "deterministic rebuild differs from final artifact: "
            f"final={PDF.stat().st_size}/{final_sha256}; "
            f"rebuilt={REBUILD.stat().st_size}/{rebuilt_sha256}"
        )
    result = {
        "status": "PASS",
        "method": "independent builder invocation to a separate temporary path",
        "bytes": REBUILD.stat().st_size,
        "final_sha256": final_sha256,
        "rebuilt_sha256": rebuilt_sha256,
        "byte_identical": True,
    }
    REBUILD.unlink()
    return result


def render_unit_references() -> list[Path]:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    for _, filename, expected_pages, _ in UNITS:
        source = ROOT / "artifacts" / filename
        unit_dir = REFERENCE_DIR / source.stem
        clear_pngs(unit_dir, "page-*.png")
        subprocess.run(
            [
                "mutool", "draw", "-q", "-r", "120", "-o",
                str(unit_dir / "page-%03d.png"), str(source),
            ],
            check=True,
        )
        pages = sorted(unit_dir.glob("page-*.png"))
        if len(pages) != expected_pages:
            raise RuntimeError(
                f"{filename}: rendered {len(pages)}, expected {expected_pages}"
            )
        rendered.extend(pages)
    return rendered


def render_checkpoint() -> dict[str, list[str]]:
    """Render every checkpoint page with two independent engines."""
    messages: dict[str, list[str]] = {}
    clear_pngs(RENDER_DIR, "page-*.png")
    clear_pngs(POPPLER_RENDER_DIR, "page-*.png")
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
    messages["mupdf_stderr"] = [
        line for line in mupdf.stderr.splitlines() if line.strip()
    ]
    messages["poppler_stderr"] = [
        line for line in poppler.stderr.splitlines() if line.strip()
    ]
    return messages


def normalize_poppler_message(message: str) -> str:
    """Remove file-offset noise while retaining the diagnostic identity."""
    return re.sub(r"Syntax Error \(\d+\):", "Syntax Error (offset):", message.strip())


def poppler_warning_equivalence() -> dict[str, Any]:
    """Prove Poppler warnings are inherited rather than merge regressions."""
    WARNING_EQUIV_DIR.mkdir(parents=True, exist_ok=True)
    clear_pngs(WARNING_EQUIV_DIR, "*.png")

    def render_messages(pdf: Path, stem: str) -> Counter[str]:
        result = subprocess.run(
            [
                "pdftoppm", "-png", "-r", "10", str(pdf),
                str(WARNING_EQUIV_DIR / stem),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        messages = Counter(
            normalize_poppler_message(line)
            for line in result.stderr.splitlines()
            if line.strip()
        )
        clear_pngs(WARNING_EQUIV_DIR, f"{stem}-*.png")
        return messages

    checkpoint_messages = render_messages(PDF, "checkpoint")
    source_messages: Counter[str] = Counter()
    for _, filename, _, _ in UNITS:
        source = ROOT / "artifacts" / filename
        source_messages.update(render_messages(source, source.stem))
    try:
        WARNING_EQUIV_DIR.rmdir()
    except OSError:
        pass
    if checkpoint_messages != source_messages:
        raise RuntimeError(
            "Poppler warning multiset differs from admitted source closure: "
            f"source_only={source_messages - checkpoint_messages}; "
            f"checkpoint_only={checkpoint_messages - source_messages}"
        )
    return {
        "status": "PASS",
        "checkpoint_warning_lines": sum(checkpoint_messages.values()),
        "source_warning_lines": sum(source_messages.values()),
        "normalized_multiset_equal": True,
        "normalized_warning_counts": dict(checkpoint_messages.most_common()),
        "interpretation": (
            "All Poppler warnings are inherited exactly from admitted unit PDFs; "
            "the checkpoint merge introduced no new warning class or count."
        ),
    }


def make_contact_sheets(page_paths: list[Path]) -> list[dict[str, Any]]:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    for stale in EVIDENCE_DIR.glob("contact-*.png"):
        stale.unlink()
    output: list[dict[str, Any]] = []
    columns, rows = 3, 4
    thumb_width, thumb_height = 560, 798
    pad, label_height = 16, 26
    per_sheet = columns * rows
    for sheet_index in range(math.ceil(len(page_paths) / per_sheet)):
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
            draw.text(
                (x, y + 4),
                f"Checkpoint page {page_number:03d}",
                fill="#111827",
            )
        first = sheet_index * per_sheet + 1
        last = first + len(batch) - 1
        path = (
            EVIDENCE_DIR
            / f"contact-{sheet_index + 1:02d}-pages-{first:03d}-{last:03d}.png"
        )
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


def page_content_bytes(page: Any) -> bytes:
    contents = page.get_contents()
    return b"" if contents is None else contents.get_data()


def main() -> None:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    source_records = validate_source_closure()
    deterministic_rebuild = verify_deterministic_rebuild()
    reader = PdfReader(str(PDF), strict=True)
    if len(reader.pages) != EXPECTED_TOTAL_PAGES:
        raise RuntimeError(
            f"page count is {len(reader.pages)}, expected {EXPECTED_TOTAL_PAGES}"
        )

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
        page_sizes[
            (
                round(float(page.mediabox.width), 2),
                round(float(page.mediabox.height), 2),
            )
        ] += 1
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
            subtype = str(annotation.get("/Subtype", ""))
            annotation_subtypes[subtype] += 1
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
    malformed_named_links = sorted(
        target
        for target in named_link_targets
        if target != "checkpoint-cover"
        and not re.fullmatch(r"u\d{3}:.+", target)
    )
    malformed_named_destinations = sorted(
        name
        for name in named_destination_names
        if name != "checkpoint-cover"
        and not re.fullmatch(r"u\d{3}:.+", name)
    )
    invalid_destination_pages: list[dict[str, Any]] = []
    for name, destination in named_destinations.items():
        try:
            destination_page = reader.get_destination_page_number(destination)
        except Exception as error:
            invalid_destination_pages.append(
                {"name": name, "error": type(error).__name__}
            )
            continue
        if not 0 <= destination_page < EXPECTED_TOTAL_PAGES:
            invalid_destination_pages.append(
                {"name": name, "page_index": destination_page}
            )

    unsafe_seen = sorted(action for action in actions if action in UNSAFE_ACTIONS)
    unsafe_annotations = sorted(
        subtype
        for subtype in annotation_subtypes
        if subtype in UNSAFE_ANNOTATION_SUBTYPES
    )
    root_names = resolve(root.get("/Names", {}))
    unsafe_name_trees = sorted(
        str(name) for name in root_names if str(name) in UNSAFE_NAME_TREES
    )
    if unsafe_seen:
        raise RuntimeError(f"unsafe actions: {unsafe_seen}")
    if unsafe_annotations:
        raise RuntimeError(f"unsafe annotation subtypes: {unsafe_annotations}")
    if unsafe_name_trees:
        raise RuntimeError(f"unsafe root name trees: {unsafe_name_trees}")
    if broken_named_links:
        raise RuntimeError(f"broken named link targets: {broken_named_links}")
    if malformed_named_links:
        raise RuntimeError(f"unprefixed named link targets: {malformed_named_links}")
    if malformed_named_destinations:
        raise RuntimeError(
            f"unprefixed named destinations: {malformed_named_destinations}"
        )
    if invalid_destination_pages:
        raise RuntimeError(
            f"named destinations outside the page tree: {invalid_destination_pages}"
        )
    if (
        root.get("/OpenAction")
        or root.get("/AA")
        or root.get("/AcroForm")
        or root.get("/Collection")
    ):
        raise RuntimeError("unexpected root action, form, or collection")
    if page_additional_actions:
        raise RuntimeError(
            f"page/annotation additional actions: {page_additional_actions}"
        )

    cover_text = reader.pages[0].extract_text() or ""
    normalized_cover_text = " ".join(cover_text.split())
    missing_cover_phrases = [
        phrase for phrase in EXPECTED_COVER_PHRASES
        if phrase not in normalized_cover_text
    ]
    if missing_cover_phrases:
        raise RuntimeError(f"cover phrases missing: {missing_cover_phrases}")
    if "STATUS:" in normalized_cover_text:
        raise RuntimeError("legacy ambiguous STATUS block label remains on cover")
    metadata = reader.metadata
    if str(metadata.get("/Creator", "")) != EXPECTED_MODEL:
        raise RuntimeError("creator metadata does not match exact model string")
    if str(metadata.get("/Title", "")) != EXPECTED_TITLE:
        raise RuntimeError("title metadata does not match the 0.6.0 checkpoint")
    keywords = str(metadata.get("/Keywords", ""))
    missing_keywords = [
        keyword for keyword in EXPECTED_KEYWORDS if keyword not in keywords
    ]
    if missing_keywords:
        raise RuntimeError(f"metadata keywords missing: {missing_keywords}")
    subject = str(metadata.get("/Subject", ""))
    if "Bab 3 lengkap" not in subject or "24 unit" not in subject:
        raise RuntimeError("subject metadata does not state the complete 24-unit scope")
    if str(root.get("/Lang", "")) != "id-ID":
        raise RuntimeError("document language is not id-ID")
    if str(root.get("/PageMode", "")) != "/UseOutlines":
        raise RuntimeError("document does not open with the outline pane")
    if page_sizes != Counter({(498.9, 708.66): EXPECTED_TOTAL_PAGES}):
        raise RuntimeError(f"unexpected page geometry: {page_sizes}")
    if rotations != Counter({0: EXPECTED_TOTAL_PAGES}):
        raise RuntimeError(f"unexpected rotations: {rotations}")
    if any(not item["embedded"] for item in fonts.values()):
        missing = [
            item["base_font"] for item in fonts.values() if not item["embedded"]
        ]
        raise RuntimeError(f"unembedded fonts: {missing}")

    mark_info = resolve(root.get("/MarkInfo", {}))
    tagged_pdf = bool(mark_info.get("/Marked")) if mark_info else False
    has_structure_tree = bool(root.get("/StructTreeRoot"))
    if tagged_pdf or has_structure_tree:
        raise RuntimeError(
            "cover says the PDF is untagged, but tagging structures are present"
        )

    combined_index = 1
    content_mismatches: list[dict[str, Any]] = []
    starts: list[int] = []
    transition_pages: list[dict[str, Any]] = []
    for unit_number, (title, filename, expected_pages, _) in enumerate(
        UNITS,
        start=1,
    ):
        source = ROOT / "artifacts" / filename
        source_reader = PdfReader(str(source), strict=True)
        starts.append(combined_index + 1)
        transition_pages.append(
            {
                "unit": unit_number,
                "title": title,
                "previous_page": combined_index if combined_index > 1 else 1,
                "start_page": combined_index + 1,
                "start_text_prefix": " ".join(
                    (source_reader.pages[0].extract_text() or "").split()
                )[:180],
            }
        )
        for source_index, source_page in enumerate(source_reader.pages):
            combined_page = reader.pages[combined_index]
            if page_content_bytes(source_page) != page_content_bytes(combined_page):
                content_mismatches.append(
                    {
                        "unit": filename,
                        "source_page": source_index + 1,
                        "checkpoint_page": combined_index + 1,
                    }
                )
            combined_index += 1
        if len(source_reader.pages) != expected_pages:
            raise RuntimeError(
                f"{filename}: {len(source_reader.pages)} pages, "
                f"expected {expected_pages}"
            )
    if starts != EXPECTED_STARTS:
        raise RuntimeError(f"unit starts {starts}, expected {EXPECTED_STARTS}")
    if combined_index != EXPECTED_TOTAL_PAGES:
        raise RuntimeError(f"source page closure ended at index {combined_index}")
    if content_mismatches:
        raise RuntimeError(f"unit content streams changed: {content_mismatches}")

    renderer_messages = render_checkpoint()
    rendered_pages = sorted(RENDER_DIR.glob("page-*.png"))
    if len(rendered_pages) != EXPECTED_TOTAL_PAGES:
        raise RuntimeError(f"MuPDF rendered {len(rendered_pages)} pages")
    poppler_rendered_pages = sorted(POPPLER_RENDER_DIR.glob("page-*.png"))
    if len(poppler_rendered_pages) != EXPECTED_TOTAL_PAGES:
        raise RuntimeError(
            f"Poppler rendered {len(poppler_rendered_pages)} pages"
        )
    reference_pages = render_unit_references()
    if len(reference_pages) != EXPECTED_SOURCE_PAGES:
        raise RuntimeError(
            f"unit references rendered {len(reference_pages)} pages"
        )
    warning_equivalence = poppler_warning_equivalence()

    raster_mismatches: list[dict[str, Any]] = []
    for checkpoint_page, source_page in zip(rendered_pages[1:], reference_pages):
        with (
            Image.open(checkpoint_page) as checkpoint_image,
            Image.open(source_page) as source_image,
        ):
            checkpoint_rgb = checkpoint_image.convert("RGB")
            source_rgb = source_image.convert("RGB")
            if (
                checkpoint_rgb.size != source_rgb.size
                or ImageChops.difference(checkpoint_rgb, source_rgb).getbbox()
            ):
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
    edge_touch_pages: list[int] = []
    for page_number, path in enumerate(rendered_pages, start=1):
        with Image.open(path) as image:
            grayscale = image.convert("L")
            stat = ImageStat.Stat(grayscale)
            content_mask = grayscale.point(lambda value: 0 if value >= 250 else 255)
            bbox = content_mask.getbbox()
            if bbox is None:
                blank_pages.append(page_number)
            elif (
                bbox[0] <= 1
                or bbox[1] <= 1
                or bbox[2] >= image.width - 1
                or bbox[3] >= image.height - 1
            ):
                edge_touch_pages.append(page_number)
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
    if blank_pages != EXPECTED_BLANK_PAGES:
        raise RuntimeError(f"unexpected blank-page inventory: {blank_pages}")

    with Image.open(rendered_pages[0]) as cover_image:
        cover_gray = cover_image.convert("L")
        header_pixels = round(130 / 708.66 * cover_image.height)
        cover_body = cover_gray.crop(
            (0, header_pixels, cover_image.width, cover_image.height)
        )
        cover_body_mask = cover_body.point(
            lambda value: 0 if value >= 250 else 255
        )
        body_bbox = cover_body_mask.getbbox()
        if body_bbox is None:
            raise RuntimeError("cover body rendered blank")
        body_margins = {
            "left": body_bbox[0],
            "top_below_masthead": body_bbox[1],
            "right": cover_image.width - body_bbox[2],
            "bottom": cover_body.height - body_bbox[3],
        }
        if min(body_margins.values()) < 20:
            raise RuntimeError(f"cover body margin too small: {body_margins}")

    contact_sheets = make_contact_sheets(rendered_pages)
    if len(contact_sheets) != EXPECTED_CONTACT_SHEETS:
        raise RuntimeError(
            f"contact sheet count is {len(contact_sheets)}, "
            f"expected {EXPECTED_CONTACT_SHEETS}"
        )
    if not VISUAL_REVIEW.is_file():
        raise RuntimeError(f"manual visual-review receipt is missing: {VISUAL_REVIEW}")

    prefix_counts = {
        f"u{unit_number:03d}": sum(
            1
            for name in named_destination_names
            if name.startswith(f"u{unit_number:03d}:")
        )
        for unit_number in range(1, len(UNITS) + 1)
    }
    if any(count == 0 for count in prefix_counts.values()):
        raise RuntimeError(f"unit with no namespaced destination: {prefix_counts}")
    top_level_outline_titles = [
        str(getattr(item, "title", item))
        for item in reader.outline
        if not isinstance(item, list)
    ]
    expected_outline_titles = [
        "Cakupan dan isi checkpoint",
        *[item[0] for item in UNITS],
    ]
    if top_level_outline_titles != expected_outline_titles:
        raise RuntimeError("top-level outline does not match 24-unit source order")

    pages_with_empty_text = [
        page for page, length in enumerate(text_lengths, start=1) if length == 0
    ]
    if pages_with_empty_text != EXPECTED_BLANK_PAGES:
        raise RuntimeError(
            f"unexpected empty extracted-text pages: {pages_with_empty_text}"
        )

    result = {
        "status": "PASS",
        "artifact": {
            "path": PDF.relative_to(ROOT).as_posix(),
            "bytes": PDF.stat().st_size,
            "sha256": sha256(PDF),
            "pages": len(reader.pages),
        },
        "deterministic_rebuild": deterministic_rebuild,
        "coverage": (
            "Pendahuluan lengkap; Bab 1 lengkap; Bab 2 lengkap; Bab 3 lengkap; "
            "24 unit; Bab 4-10 belum disertakan."
        ),
        "unit_start_pages_1_based": starts,
        "source_units": source_records,
        "source_content_stream_identity": {
            "pages_checked": EXPECTED_SOURCE_PAGES,
            "mismatches": 0,
        },
        "render_qa": {
            "renderer": "MuPDF mutool, 120 dpi",
            "secondary_renderer": "Poppler pdftoppm, 120 dpi",
            "checkpoint_pages_rendered": len(rendered_pages),
            "secondary_renderer_pages": len(poppler_rendered_pages),
            "renderer_message_counts": {
                name: len(lines) for name, lines in renderer_messages.items()
            },
            "renderer_message_summaries": {
                name: dict(
                    Counter(
                        normalize_poppler_message(line) for line in lines
                    ).most_common()
                )
                for name, lines in renderer_messages.items()
            },
            "poppler_warning_equivalence": warning_equivalence,
            "source_unit_pages_rendered": len(reference_pages),
            "source_to_checkpoint_pixel_identical_pages": EXPECTED_SOURCE_PAGES,
            "raster_mismatches": 0,
            "blank_pages": blank_pages,
            "edge_touch_pages": edge_touch_pages,
            "clipping_deterministic_result": (
                "PASS: all 228 admitted source pages are pixel-identical after "
                "merge; the bespoke cover body clears deterministic margins, "
                "while its title masthead intentionally bleeds."
            ),
            "cover_body_bbox_below_masthead": list(body_bbox),
            "cover_body_margins_pixels": body_margins,
            "page_records": rendered_records,
            "contact_sheets": contact_sheets,
            "transition_pages": transition_pages,
            "visual_review": {
                "status": "PASS",
                "path": VISUAL_REVIEW.relative_to(ROOT).as_posix(),
                "bytes": VISUAL_REVIEW.stat().st_size,
                "sha256": sha256(VISUAL_REVIEW),
                "scope": (
                    "All 229 pages via 20 contact sheets; full-resolution cover; "
                    "all 24 unit transitions and the Bab 3 sequence inspected."
                ),
            },
        },
        "structure": {
            "page_sizes": {
                f"{width}x{height}": count
                for (width, height), count in page_sizes.items()
            },
            "rotations": dict(rotations),
            "language": str(root.get("/Lang", "")),
            "page_mode": str(root.get("/PageMode", "")),
            "named_destinations": len(named_destination_names),
            "named_destination_prefix_counts": prefix_counts,
            "invalid_named_destination_pages": invalid_destination_pages,
            "broken_named_links": broken_named_links,
            "malformed_named_links": malformed_named_links,
            "malformed_named_destinations": malformed_named_destinations,
            "top_level_outline_titles": top_level_outline_titles,
            "annotation_subtypes": dict(annotation_subtypes),
            "actions": dict(actions),
            "unsafe_actions": unsafe_seen,
            "unsafe_annotation_subtypes": unsafe_annotations,
            "unsafe_name_trees": unsafe_name_trees,
            "additional_actions": page_additional_actions,
            "open_action": bool(root.get("/OpenAction")),
            "acroform": bool(root.get("/AcroForm")),
            "collection": bool(root.get("/Collection")),
        },
        "accessibility": {
            "language": str(root.get("/Lang", "")),
            "tagged_pdf_claimed": False,
            "marked": tagged_pdf,
            "structure_tree": has_structure_tree,
            "pages_with_empty_extracted_text": pages_with_empty_text,
            "intentional_blank_pages": EXPECTED_BLANK_PAGES,
        },
        "fonts": {
            "unique_font_objects": len(fonts),
            "embedded": sum(1 for item in fonts.values() if item["embedded"]),
            "unembedded": sum(
                1 for item in fonts.values() if not item["embedded"]
            ),
            "to_unicode": sum(
                1 for item in fonts.values() if item["to_unicode"]
            ),
            "without_to_unicode": sorted(
                {
                    item["base_font"]
                    for item in fonts.values()
                    if not item["to_unicode"]
                }
            ),
        },
        "text": {
            "cover_phrases_checked": EXPECTED_COVER_PHRASES,
            "missing_cover_phrases": missing_cover_phrases,
            "metadata_keywords_checked": EXPECTED_KEYWORDS,
            "missing_metadata_keywords": missing_keywords,
            "legacy_status_block_label_absent": True,
            "creator_metadata": str(metadata.get("/Creator", "")),
            "title_metadata": str(metadata.get("/Title", "")),
            "subject_metadata": subject,
            "keywords_metadata": keywords,
            "pages_with_empty_extracted_text": pages_with_empty_text,
        },
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    STRUCTURE_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("status=PASS")
    print(f"artifact_bytes={PDF.stat().st_size}")
    print(f"artifact_sha256={sha256(PDF)}")
    print(f"pages={len(reader.pages)}")
    print(f"unit_starts={starts}")
    print(f"named_destinations={len(named_destination_names)}")
    print(f"actions={dict(actions)}")
    print(
        f"fonts={len(fonts)} "
        f"embedded={sum(1 for item in fonts.values() if item['embedded'])}"
    )
    print(f"blank_pages={blank_pages}")
    print(f"contact_sheets={len(contact_sheets)}")
    print(f"evidence={STRUCTURE_JSON}")


if __name__ == "__main__":
    main()
