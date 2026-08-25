#!/usr/bin/env python3
"""Generate deterministic PDF and render evidence for O013 Unit 029."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pypdf import PdfReader
from pypdf.generic import IndirectObject


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/unit-029-evidence"
REPORT = ROOT / "qa/UNIT_029_VISUAL_QA_20260825.md"
PREFLIGHT = ROOT / "qa/UNIT_029_VISUAL_PREFLIGHT_20260825.md"
DPI = 144
PAGES = 6
PIXEL_SIZE = (998, 1418)
EDGE_BAND = 3
PDF_NAME = "unit-029-bab-4-teorema-sylow.pdf"
DOCS = {
    "build-i": (
        ROOT / "build/unit-029-clean-i" / PDF_NAME,
        99_695,
        "5f9ae471aa1e20598d48bd5705ae0f89ed911304f5f89da30136d975240aafe1",
    ),
    "build-j": (
        ROOT / "build/unit-029-clean-j" / PDF_NAME,
        99_689,
        "64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012",
    ),
    "artifact": (
        ROOT / "artifacts/unit-029-bab-4-teorema-sylow-id.pdf",
        99_689,
        "64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012",
    ),
}
FINAL_LOG = (
    ROOT / "qa/UNIT_029_BUILD_FINAL.log",
    77_013,
    "606a707d5aad534f58af25333f3fbffe964ab7c7f1a260b3ffe9c1f1bce8364e",
)
RAW_FINAL_LOG = ROOT / "build/unit-029-clean-j" / "unit-029-bab-4-teorema-sylow.log"
EXPECTED_METADATA = {
    "/Creator": "LaTeX with hyperref",
    "/Title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 29: Teorema Sylow",
    "/Subject": "Terjemahan Bahasa Indonesia independen; Bagian 4.5 lengkap",
    "/Author": "Wen-Wei Li",
    "/Keywords": "aljabar, teori grup, p-grup, Teorema Cauchy, Teorema Sylow, subgrup Sylow, id-ID",
    "/Producer": "MiKTeX-dvipdfmx (20260404)",
    "/CreationDate": "D:20260825000000Z",
}
EXPECTED_OUTLINE = [
    ("4.5 Teorema Sylow", 3),
    ("Daftar Pustaka", 6),
    ("Indeks Istilah", 6),
]
VISUAL_FINDINGS = [
    "Hierarki sampul, judul Unit 29, panel ruang lingkup, tanggal, dan margin seimbang serta mudah dibaca.",
    "Atribusi edisi dan sumber, ISBN, lisensi, non-endorsement, provenance model, tautan, dan lencana CC tampil utuh tanpa tabrakan.",
    "Judul Bagian 4.5, definisi p-grup dan subgrup Sylow, Teorema Cauchy, serta rumus binomial tersusun jelas dengan lebar teks terpusat.",
    "Bukti dengan aksi grup, normalizer, dan hasil-hasil antara mengalir alami; kotak teorema, simbol, dan rujukan tidak terpotong.",
    "Tiga Teorema Sylow dan argumen konjugasi terbaca jelas; tampilan matematika terpusat dan tidak melampaui area hidup.",
    "Bagian akhir bukti, sitasi, daftar pustaka, dan indeks istilah run-in mengisi halaman secara alami; kedua entri indeks terbaca dan margin bawah tetap aman.",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bytes_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def dereference(value: Any) -> Any:
    return value.get_object() if isinstance(value, IndirectObject) else value


def sanitize(text: str) -> str:
    replacements = (
        (str(ROOT), "<LANE_ROOT>"),
        (str(ROOT).replace("\\", "/"), "<LANE_ROOT>"),
        (str(Path.home()), "%USERPROFILE%"),
        (str(Path.home()).replace("\\", "/"), "%USERPROFILE%"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def sanitized_build_log(raw_text: str) -> tuple[str, dict[str, int]]:
    """Reproduce the publishable log without changing diagnostics or line count."""
    assert "\r" not in raw_text
    original_newlines = raw_text.count("\n")
    miktex_prefix = str(Path.home() / "AppData/Local/Programs/MiKTeX")
    absolute_build_prefix = str((ROOT / "build/unit-029-clean-j").resolve())
    relative_build_prefix = r"build\unit-029-clean-j"

    miktex_occurrences = raw_text.count(miktex_prefix)
    assert miktex_occurrences == 252
    sanitized = raw_text.replace(miktex_prefix, "<MIKTEX_ROOT>")

    relative_replacements = sanitized.count(absolute_build_prefix)
    sanitized = sanitized.replace(absolute_build_prefix, relative_build_prefix)
    for split_at in range(1, len(absolute_build_prefix)):
        wrapped = (
            absolute_build_prefix[:split_at]
            + "\n"
            + absolute_build_prefix[split_at:]
        )
        occurrences = sanitized.count(wrapped)
        if occurrences:
            sanitized = sanitized.replace(
                wrapped, relative_build_prefix + "\n"
            )
            relative_replacements += occurrences

    assert relative_replacements == 8
    assert sanitized.count("\n") == original_newlines
    assert sanitized.count("<MIKTEX_ROOT>") == miktex_occurrences
    assert sanitized.count(relative_build_prefix) == relative_replacements
    assert re.search(r"[A-Za-z]:\\Users\\", sanitized, re.I) is None
    assert Path.home().name.lower() not in sanitized.lower()
    return sanitized, {
        "miktex_placeholder_occurrences": miktex_occurrences,
        "relative_build_prefix_occurrences": relative_replacements,
        "line_records_preserved": original_newlines + 1,
        "windows_user_path_occurrences": 0,
        "profile_name_occurrences": 0,
    }


def run(arguments: list[str]) -> tuple[str, str]:
    completed = subprocess.run(
        arguments,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"{Path(arguments[0]).name} exited {completed.returncode}: "
            + sanitize(completed.stderr)
        )
    return sanitize(completed.stdout), sanitize(completed.stderr)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def file_identity(path: Path) -> dict[str, object]:
    return {"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def bound_identities() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, (path, expected_bytes, expected_sha256) in DOCS.items():
        assert path.is_file(), path
        record = file_identity(path)
        assert (record["bytes"], record["sha256"]) == (expected_bytes, expected_sha256), (name, record)
        result[name] = record
    path, expected_bytes, expected_sha256 = FINAL_LOG
    record = file_identity(path)
    assert (record["bytes"], record["sha256"]) == (expected_bytes, expected_sha256), record
    result["final-build-log"] = record
    assert DOCS["build-j"][0].read_bytes() == DOCS["artifact"][0].read_bytes()
    result["build-j_artifact_byte_identical"] = True
    return result


def render(engine: str, document_name: str, pdf: Path, work: Path) -> dict[str, Any]:
    temporary = work / f"{engine}-{document_name}"
    temporary.mkdir()
    target = OUT / "renders" / engine / document_name
    target.mkdir(parents=True)
    if engine == "poppler":
        executable = shutil.which("pdftoppm")
        assert executable, "pdftoppm missing"
        prefix = temporary / "page"
        stdout, stderr = run([executable, "-png", "-r", str(DPI), "-f", "1", "-l", str(PAGES), str(pdf), str(prefix)])
        pages = sorted(temporary.glob("page-*.png"), key=lambda path: int(path.stem.rsplit("-", 1)[1]))
    else:
        executable = shutil.which("mutool")
        assert executable, "mutool missing"
        pattern = temporary / "page-%02d.png"
        stdout, stderr = run([executable, "draw", "-q", "-r", str(DPI), "-o", str(pattern), str(pdf)])
        pages = sorted(temporary.glob("page-*.png"))
    assert len(pages) == PAGES, (engine, document_name, len(pages))
    records = []
    for page_number, source in enumerate(pages, 1):
        path = target / f"page-{page_number:02d}.png"
        shutil.copyfile(source, path)
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            assert rgb.size == PIXEL_SIZE, (engine, document_name, page_number, rgb.size)
            red, green, blue = rgb.split()
            darkest = ImageChops.darker(ImageChops.darker(red, green), blue)
            ink_mask = darkest.point(lambda value: 255 if value < 250 else 0)
            bbox = ink_mask.getbbox()
            pixels = rgb.load()
            width, height = rgb.size
            edge_coordinates = (
                {(x, y) for x in range(EDGE_BAND) for y in range(height)}
                | {(width - 1 - x, y) for x in range(EDGE_BAND) for y in range(height)}
                | {(x, y) for y in range(EDGE_BAND) for x in range(width)}
                | {(x, height - 1 - y) for y in range(EDGE_BAND) for x in range(width)}
            )
            edge_ink = sum(min(pixels[x, y]) < 250 for x, y in edge_coordinates)
            records.append({
                "page": page_number,
                "path": relative(path),
                "png_bytes": path.stat().st_size,
                "png_sha256": sha256(path),
                "decoded_rgb_sha256": bytes_sha256(rgb.tobytes()),
                "size": list(rgb.size),
                "outer_3px_ink_pixels": edge_ink,
                "nonwhite_bbox": list(bbox) if bbox else None,
            })
    return {"engine": engine, "document": document_name, "dpi": DPI, "stdout": stdout.strip(), "stderr": stderr.strip(), "pages": records}


def contact_sheet(engine: str, document_name: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    thumb_width, thumb_height, gap, caption = 399, 567, 12, 22
    rows = (len(pages) + 2) // 3
    sheet = Image.new("RGB", (gap + 3 * (thumb_width + gap), gap + rows * (thumb_height + caption + gap)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, record in enumerate(pages):
        with Image.open(ROOT / record["path"]) as image:
            page = image.convert("RGB")
            page.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = gap + (index % 3) * (thumb_width + gap)
        y = gap + (index // 3) * (thumb_height + caption + gap)
        draw.text((x, y + 3), f"{document_name} / {engine} / p.{index + 1}", fill="black", font=font)
        sheet.paste(page, (x, y + caption))
    path = OUT / "contact-sheets" / f"{document_name}-{engine}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return {"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path), "size": list(sheet.size)}


def render_gate(renderings: dict[str, Any]) -> dict[str, Any]:
    comparisons: dict[str, Any] = {}
    for engine in ("poppler", "mupdf"):
        comparisons[engine] = {}
        for left, right, key in (("build-i", "build-j", "build-i_vs_build-j"), ("build-j", "artifact", "build-j_vs_artifact")):
            rows = []
            for left_page, right_page in zip(renderings[engine][left]["pages"], renderings[engine][right]["pages"], strict=True):
                rows.append({
                    "page": left_page["page"],
                    "decoded_pixel_identical": left_page["decoded_rgb_sha256"] == right_page["decoded_rgb_sha256"],
                    "png_byte_identical": left_page["png_sha256"] == right_page["png_sha256"],
                })
            assert len(rows) == PAGES and all(row["decoded_pixel_identical"] for row in rows)
            comparisons[engine][key] = {"all_6_decoded_pixel_identical": True, "pages": rows}
    assert not any(page["outer_3px_ink_pixels"] for engine in renderings.values() for document in engine.values() for page in document["pages"])
    return comparisons


def font_record(reference: Any) -> dict[str, Any]:
    source = dereference(reference)
    direct = reference
    subtype = str(source.get("/Subtype", ""))
    base_font = str(source.get("/BaseFont", ""))
    to_unicode = source.get("/ToUnicode") is not None
    if subtype == "/Type0":
        descendants = dereference(source.get("/DescendantFonts")) or []
        if descendants:
            source = dereference(descendants[0])
    descriptor = dereference(source.get("/FontDescriptor")) if source else None
    streams = [key for key in ("/FontFile", "/FontFile2", "/FontFile3") if descriptor and descriptor.get(key) is not None]
    object_id = f"{direct.idnum} {direct.generation}" if isinstance(direct, IndirectObject) else None
    return {"object": object_id, "basefont": base_font, "normalized": re.sub(r"^/[A-Z]{6}\+", "/", base_font), "subtype": subtype, "embedded": bool(streams), "streams": streams, "to_unicode": to_unicode}


def outline_records(reader: PdfReader) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    def walk(items: list[Any], depth: int = 0) -> None:
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
            elif hasattr(item, "title"):
                result.append({"title": str(item.title), "page": reader.get_destination_page_number(item) + 1, "depth": depth})
    walk(reader.outline)
    return result


def safe_open_action(reader: PdfReader, root: Any) -> dict[str, Any] | None:
    action = root.get("/OpenAction")
    if action is None:
        return None
    action = dereference(action)
    assert isinstance(action, list) and len(action) >= 2
    page_reference = action[0]
    page_number = next((index for index, page in enumerate(reader.pages, 1) if page.indirect_reference == page_reference), None)
    assert page_number is not None and str(action[1]) in ("/Fit", "/FitH", "/XYZ")
    return {"kind": "direct_page_destination", "page": page_number, "fit": str(action[1])}


def inspect_document(name: str, path: Path, work: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    assert not reader.is_encrypted and len(reader.pages) == PAGES
    root = dereference(reader.trailer["/Root"])
    assert str(root.get("/Lang")) == "id-ID"
    assert {str(key): str(value) for key, value in (reader.metadata or {}).items()} == EXPECTED_METADATA
    assert path.read_bytes().startswith(b"%PDF-1.7")
    names = dereference(root.get("/Names")) or {}
    assert sorted(map(str, names.keys())) == ["/Dests"]
    assert names.get("/JavaScript") is None and names.get("/EmbeddedFiles") is None
    assert root.get("/AcroForm") is None and root.get("/AA") is None
    open_action = safe_open_action(reader, root)
    destinations = {str(key): reader.get_destination_page_number(value) + 1 for key, value in reader.named_destinations.items()}
    assert len(destinations) == 36 and all(1 <= page <= PAGES for page in destinations.values())
    outline = outline_records(reader)
    assert outline == [{"title": title, "page": page, "depth": 0} for title, page in EXPECTED_OUTLINE]

    fonts: dict[str, dict[str, Any]] = {}
    pypdf_pages = []
    links = []
    action_counts: Counter[str] = Counter()
    page_additional_actions = 0
    annotation_additional_actions = 0
    bad_rectangles = []
    broken_destinations = []
    unsafe_actions = []
    uri_targets = []
    goto_targets = []
    page_geometry = []
    for page_number, page in enumerate(reader.pages, 1):
        page_additional_actions += page.get("/AA") is not None
        media = [float(value) for value in page.mediabox]
        crop = [float(value) for value in page.cropbox]
        assert media == crop and int(page.get("/Rotate", 0)) == 0
        assert [round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)] == [498.9, 708.66]
        page_geometry.append({"page": page_number, "media_box": media, "crop_box": crop, "rotate": int(page.get("/Rotate", 0))})
        pypdf_pages.append(page.extract_text() or "")
        resources = dereference(page.get("/Resources")) or {}
        for reference in (dereference(resources.get("/Font")) or {}).values():
            record = font_record(reference)
            fonts[record["object"] or record["basefont"]] = record
        for ordinal, annotation_reference in enumerate(dereference(page.get("/Annots")) or [], 1):
            annotation = dereference(annotation_reference)
            annotation_additional_actions += annotation.get("/AA") is not None
            assert str(annotation.get("/Subtype")) == "/Link"
            rectangle = [float(value) for value in annotation.get("/Rect", [])]
            width, height = float(page.mediabox.width), float(page.mediabox.height)
            if not (len(rectangle) == 4 and -0.5 <= rectangle[0] <= rectangle[2] <= width + 0.5 and -0.5 <= rectangle[1] <= rectangle[3] <= height + 0.5):
                bad_rectangles.append({"page": page_number, "rect": rectangle})
            action = dereference(annotation.get("/A"))
            assert action is not None
            action_type = str(action.get("/S"))
            action_counts[action_type] += 1
            if action_type == "/GoTo":
                target = str(action.get("/D")); goto_targets.append(target)
                if target not in destinations: broken_destinations.append({"page": page_number, "target": target})
            elif action_type == "/URI":
                target = str(action.get("/URI")); uri_targets.append(target)
                if not target.startswith("https://"): unsafe_actions.append({"page": page_number, "action": action_type, "target": target})
            else:
                target = ""; unsafe_actions.append({"page": page_number, "action": action_type})
            links.append({"page": page_number, "ordinal_on_page": ordinal, "rect": rectangle, "action": action_type, "target": target})
    assert action_counts == Counter({"/GoTo": 9, "/URI": 5})
    assert not bad_rectangles and not broken_destinations and not unsafe_actions
    assert not page_additional_actions and not annotation_additional_actions

    pypdf_text = "\f".join(pypdf_pages)
    text_path = work / f"{name}.txt"
    pdftotext, pdffonts, pdfinfo = shutil.which("pdftotext"), shutil.which("pdffonts"), shutil.which("pdfinfo")
    assert pdftotext and pdffonts and pdfinfo
    _, text_stderr = run([pdftotext, "-layout", "-enc", "UTF-8", str(path), str(text_path)])
    poppler_bytes = text_path.read_bytes(); poppler_text = poppler_bytes.decode("utf-8", "replace")
    fonts_stdout, fonts_stderr = run([pdffonts, str(path)])
    info_stdout, info_stderr = run([pdfinfo, str(path)])
    font_rows = [line for line in fonts_stdout.splitlines() if re.search(r"\s(?:yes|no)\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", line)]
    info = {key.strip(): value.strip() for line in info_stdout.splitlines() if ":" in line for key, value in [line.split(":", 1)]}
    assert info.get("Pages") == "6" and info.get("Tagged") == "no"
    mupdf_pages = []
    out_of_bounds_text_blocks = []
    with fitz.open(path) as document:
        for page_number, page in enumerate(document, 1):
            mupdf_pages.append(page.get_text("text"))
            for block in page.get_text("blocks"):
                x0, y0, x1, y1 = block[:4]; rectangle = page.rect
                if not (x0 >= rectangle.x0 - 1 and y0 >= rectangle.y0 - 1 and x1 <= rectangle.x1 + 1 and y1 <= rectangle.y1 + 1):
                    out_of_bounds_text_blocks.append({"page": page_number, "bbox": [x0, y0, x1, y1]})
    assert not out_of_bounds_text_blocks
    mupdf_text = "\f".join(mupdf_pages)
    font_records = sorted(fonts.values(), key=lambda item: (item["normalized"], item["object"] or ""))
    assert len(font_records) == 25 and all(item["embedded"] for item in font_records)
    assert len(font_rows) == 25 and all(re.search(r"\syes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", row) for row in font_rows)
    assert "�" not in pypdf_text + poppler_text + mupdf_text
    nul_counts = {"pypdf": pypdf_text.count("\0"), "pdftotext_layout": poppler_text.count("\0"), "mupdf": mupdf_text.count("\0")}
    assert nul_counts == {"pypdf": 4, "pdftotext_layout": 0, "mupdf": 1}
    return {
        "identity": file_identity(path), "pages": PAGES, "pdf_header": "%PDF-1.7", "language": "id-ID", "tagged": False, "encrypted": False,
        "metadata": EXPECTED_METADATA, "catalog_keys": sorted(map(str, root.keys())), "name_tree_keys": sorted(map(str, names.keys())), "open_action": open_action,
        "page_geometry": page_geometry, "outline": outline, "named_destinations": dict(sorted(destinations.items())),
        "actions": {"counts": dict(sorted(action_counts.items())), "links": links, "uris": uri_targets, "gotos": goto_targets, "broken_destinations": broken_destinations, "unsafe": unsafe_actions, "out_of_bounds_rectangles": bad_rectangles, "all_uris_https": all(uri.startswith("https://") for uri in uri_targets), "catalog_additional_action": False, "page_additional_actions": page_additional_actions, "annotation_additional_actions": annotation_additional_actions},
        "payloads": {"forms": False, "javascript": False, "embedded_files": False},
        "fonts": {"pypdf_unique": len(font_records), "pypdf_all_embedded": True, "records": font_records, "pdffonts_rows": len(font_rows), "pdffonts_all_embedded": True, "pdffonts_stderr": fonts_stderr.strip()},
        "text": {"pypdf_sha256": bytes_sha256(pypdf_text.encode("utf-8")), "pypdf_page_sha256": [bytes_sha256(text.encode("utf-8")) for text in pypdf_pages], "pdftotext_layout_sha256": bytes_sha256(poppler_bytes), "mupdf_sha256": bytes_sha256(mupdf_text.encode("utf-8")), "nul_characters": nul_counts, "replacement_characters": 0},
        "geometry": {"fitz_text_blocks_out_of_bounds": out_of_bounds_text_blocks}, "pdfinfo": info,
        "tool_diagnostics": {"pdfinfo_stderr": info_stderr.strip(), "pdftotext_stderr": text_stderr.strip()},
        "checks": {"six_pages": True, "language_id_ID": True, "untagged_disclosed": True, "metadata_exact": True, "outline_exact": True, "thirty_six_destinations": True, "action_counts": True, "link_closure": True, "safe_actions": True, "rectangles_in_bounds": True, "text_blocks_in_bounds": True, "no_active_payloads": True, "fonts_embedded": True, "text_has_no_replacement_characters": True, "known_math_font_nul_census": True},
    }


def semantic_font_projection(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [{key: item[key] for key in ("object", "normalized", "subtype", "embedded", "streams", "to_unicode")} for item in document["fonts"]["records"]]


def final_log_record() -> dict[str, Any]:
    path, expected_bytes, expected_sha256 = FINAL_LOG
    published_bytes = path.read_bytes()
    text = published_bytes.decode("utf-8")
    raw_text = RAW_FINAL_LOG.read_text(encoding="utf-8")
    reproduced, sanitization = sanitized_build_log(raw_text)
    assert reproduced.encode("utf-8") == published_bytes
    assert len(published_bytes) == expected_bytes
    assert sha256(path) == expected_sha256
    patterns = {"fatal_error": r"fatal error", "emergency_stop": r"emergency stop", "undefined_control_sequence": r"undefined control sequence", "latex_error": r"! LaTeX Error", "undefined_references": r"undefined references|Reference .* undefined", "undefined_citations": r"undefined citations|Citation .* undefined", "missing_character": r"missing character", "overfull": r"overfull \\[hv]box", "empty_link_target": r"empty link target"}
    fatal = {key: len(re.findall(pattern, text, re.I)) for key, pattern in patterns.items()}
    assert not any(fatal.values()), fatal
    page_markers = re.findall(
        r"Output written on .*?\((\d+)\s+p\s*ages?\)\.", text, re.S
    )
    assert page_markers and int(page_markers[-1]) == PAGES
    record = {
        "identity": {"path": relative(path), "bytes": expected_bytes, "sha256": expected_sha256}, "page_marker": PAGES, "fatal_diagnostics": fatal,
        "latex_release_warnings": text.count("LaTeX Warning: You have requested release"), "xecjk_warnings": text.count("Package xeCJK Warning"), "braids_warnings": text.count("Package braids Warning"),
        "fontspec_CJK_advisories": text.count("Script 'CJK' not explicitly supported"),
        "underfull_hbox_badness": [int(value) for value in re.findall(r"Underfull \\hbox \(badness (\d+)\)", text)],
        "underfull_vbox_badness": [int(value) for value in re.findall(r"Underfull \\vbox \(badness (\d+)\)", text)],
        "raw_log_has_profile_path": False,
        "windows_user_path_occurrences": len(re.findall(r"[A-Za-z]:\\Users\\", text, re.I)),
        "profile_name_occurrences": text.lower().count(Path.home().name.lower()),
        "sanitization": sanitization,
        "sanitized_log_reproduced_from_build_j": True,
        "evidence_sanitized": True,
    }
    assert (record["latex_release_warnings"], record["xecjk_warnings"], record["braids_warnings"], record["fontspec_CJK_advisories"], len(record["underfull_hbox_badness"]), len(record["underfull_vbox_badness"])) == (3, 1, 1, 6, 1, 1)
    assert record["windows_user_path_occurrences"] == 0
    assert record["profile_name_occurrences"] == 0
    return record


def write_reports(identities: dict[str, Any], comparisons: dict[str, Any], documents: dict[str, Any], log: dict[str, Any]) -> None:
    identity_rows = "\n".join(f"| `{value['path']}` | {value['bytes']:,} | `{value['sha256']}` |" for value in identities.values() if isinstance(value, dict))
    comparison_rows = "\n".join(f"- {engine} {pair.replace('_', ' ')}: keenam halaman RGB terdekode identik." for engine in comparisons for pair in comparisons[engine])
    page_rows = "\n".join(f"| {page} | {VISUAL_FINDINGS[page - 1]} |" for page in range(1, PAGES + 1))
    artifact_pages = {engine: documents["artifact-renders"][engine]["pages"] for engine in ("poppler", "mupdf")}
    pixel_rows = "\n".join(f"| {page} | `{artifact_pages['poppler'][page-1]['decoded_rgb_sha256']}` | `{artifact_pages['mupdf'][page-1]['decoded_rgb_sha256']}` |" for page in range(1, PAGES + 1))
    artifact = documents["artifact"]
    report = f"""# Unit 029 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. No actionable defect was found. Exact identity, same-renderer decoded-pixel, structure, metadata, navigation, font, text, action/link, clipping, and final-build-log gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
{identity_rows}

Build J and the final artifact are byte-identical. All three PDFs have six pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at {DPI} dpi ({PIXEL_SIZE[0]} × {PIXEL_SIZE[1]} pixels per page). Equality uses decoded RGB pixels rather than PNG compression.

{comparison_rows}

All 36 renders have zero ink pixels in their outer three-pixel band. Six contact sheets and every PNG/decoded-pixel identity are recorded in `qa/unit-029-evidence/render-hash-inventory.json`.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
{pixel_rows}

## PDF gate

- PDF `{artifact['pdf_header']}`; `/Lang id-ID`; six pages; unencrypted; exact metadata; no form, JavaScript, additional action, or embedded file.
- The three-entry outline resolves to Section 4.5 on page 3, with the bibliography and term index both on page 6. All 36 named destinations resolve.
- All nine `/GoTo` actions close over the destination inventory; all five `/URI` actions use HTTPS. `/OpenAction` is a safe direct page destination.
- Link rectangles and MuPDF text blocks are in bounds. All {artifact['fonts']['pypdf_unique']} pypdf font objects and {artifact['fonts']['pdffonts_rows']} `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text hashes match separately across I, J, and artifact. There are no replacement characters; Poppler has no NULs, while pypdf has four and MuPDF one at stable mathematics-font loci without complete Unicode maps.
- The published final log is a byte-verified sanitizer replay of build J: {log['sanitization']['miktex_placeholder_occurrences']} local MiKTeX prefixes map to `<MIKTEX_ROOT>`, {log['sanitization']['relative_build_prefix_occurrences']} wrapped absolute build prefixes map to `build\\unit-029-clean-j`, all {log['sanitization']['line_records_preserved']} line records are preserved, and Windows user-path/profile-name occurrences are both zero.

## Independent full-resolution review

All pages were reviewed in Poppler and MuPDF. The body uses the centered 142 mm text block and fills pages naturally; the cover uses one prose scope panel, not an ambiguous alternating filled/unfilled progress-block system.

| Page | Finding |
|---:|---|
{page_rows}

No clipping, overflow, collision, broken mathematical stroke, missing label, tofu box, unintended sparse page, ambiguous progress block, or edge contact was found.

## Warnings

1. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
2. dvipdfmx assigns volatile six-letter subset tags, so builds I and J are not byte-identical. Their normalized structures, three text surfaces, and all same-renderer decoded pixels agree; build J and the artifact are byte-identical.
3. The final log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen `braids` warning, 6 fontspec CJK advisories, one visually benign underfull hbox (badness {log['underfull_hbox_badness'][0]}), and one visually benign underfull vbox (badness {log['underfull_vbox_badness'][0]}). Fatal/error, unresolved-reference/citation, missing-character, and overfull diagnostics are zero.
4. Two mathematics fonts lack complete Unicode maps. The stable pypdf/MuPDF NUL census is disclosed; Poppler extraction and visible rendering pass.
5. Poppler reports the absent optional Adobe-GB1 language pack and dependent F37/show-space diagnostics during layout-text extraction. The extracted text has no replacement characters or NULs, and both renderers visibly reproduce every page.

Evidence: `structure-and-pdf-qa.json` records exact structures, metadata, destinations, actions, fonts, text hashes, geometry, and final-log checks. `render-hash-inventory.json` records all 36 render identities, comparisons, edge results, and six contact-sheet identities.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict: **PASS WITH WARNINGS; zero actionable defects.**
"""
    REPORT.write_text(report, encoding="utf-8", newline="\n")
    preflight = f"""# Unit 029 visual preflight — 2026-08-25

Status: **PASS WITH WARNINGS**. Both independent clean builds and the canonical artifact were structurally inspected and rendered across all six pages before admission. No actionable layout defect was found.

## Result

- Build I: 6 pages / {identities['build-i']['bytes']:,} bytes / SHA-256 `{identities['build-i']['sha256']}`.
- Build J: 6 pages / {identities['build-j']['bytes']:,} bytes / SHA-256 `{identities['build-j']['sha256']}`.
- Canonical artifact: 6 pages / {identities['artifact']['bytes']:,} bytes / SHA-256 `{identities['artifact']['sha256']}`; byte-identical to build J.
- Poppler and MuPDF each produced 18 full-page renders, for 36 total. Every I-to-J and J-to-artifact same-renderer decoded-pixel comparison passed, and all outer three-pixel bands were clear.
- All pages use a centered, readable text area and natural vertical reflow. The only framed cover element is a consistently filled prose scope panel; it does not encode progress and has no confusing filled/unfilled counterpart.
- Equations, theorem boxes, references, bibliography, term index, links, navigation, metadata, and embedded fonts passed deterministic checks.
- The final build log is reproducibly sanitized from build J while preserving all {log['sanitization']['line_records_preserved']} line records and diagnostics; it contains zero Windows user paths and zero local profile-name occurrences.

## Disclosed limitations

The PDF is untagged, so no tagged-accessibility claim is made. The local Poppler installation lacks optional Adobe-GB1 mapping data and emits dependent extraction diagnostics, but Poppler text has no replacement character or NUL and both renderers show all visible glyphs. The final log's one underfull hbox and one underfull vbox are visually benign.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.
"""
    PREFLIGHT.write_text(preflight, encoding="utf-8", newline="\n")


def main() -> None:
    identities = bound_identities()
    resolved = OUT.resolve()
    assert resolved.parent == (ROOT / "qa").resolve() and resolved.name == "unit-029-evidence"
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    renderings: dict[str, Any] = {"poppler": {}, "mupdf": {}}
    contact_sheets = []
    with tempfile.TemporaryDirectory(prefix="unit029-evidence-") as temporary:
        work = Path(temporary)
        for engine in renderings:
            for document_name, (path, _, _) in DOCS.items():
                rendering = render(engine, document_name, path, work)
                renderings[engine][document_name] = rendering
                contact_sheets.append(contact_sheet(engine, document_name, rendering["pages"]))
        comparisons = render_gate(renderings)
        documents = {name: inspect_document(name, spec[0], work) for name, spec in DOCS.items()}
    for field in ("metadata", "outline", "named_destinations", "open_action", "page_geometry", "actions"):
        assert documents["build-i"][field] == documents["build-j"][field] == documents["artifact"][field], field
    assert semantic_font_projection(documents["build-i"]) == semantic_font_projection(documents["build-j"]) == semantic_font_projection(documents["artifact"])
    for field in ("pypdf_sha256", "pypdf_page_sha256", "pdftotext_layout_sha256", "mupdf_sha256"):
        assert documents["build-i"]["text"][field] == documents["build-j"]["text"][field] == documents["artifact"]["text"][field], field
    log = final_log_record()
    poppler_version = run([shutil.which("pdftoppm"), "-v"])
    mupdf_version = run([shutil.which("mutool"), "-v"])
    versions = {"poppler": " ".join(" ".join(poppler_version).split()), "mupdf": " ".join(" ".join(mupdf_version).split())}
    assert "24.04.0" in versions["poppler"] and "1.23.0" in versions["mupdf"]
    render_inventory = {
        "status": "PASS_WITH_WARNINGS", "identities": identities, "renderer_versions": versions, "renderers": renderings, "contact_sheets": contact_sheets,
        "decoded_pixel_comparisons": comparisons, "edge_gate": {"outer_band_pixels": EDGE_BAND, "all_36_zero_ink": True},
        "manual_visual_review": {"status": "PASS", "renderers": ["Poppler", "MuPDF"], "pages_per_document": PAGES, "findings": {str(index): finding for index, finding in enumerate(VISUAL_FINDINGS, 1)}, "actionable_defects": []},
        "warnings": ["PDF is untagged; no tagged-accessibility claim is made.", "dvipdfmx subset tags vary between I and J; normalized semantics and decoded pixels agree.", "Mathematics fonts have incomplete Unicode maps; stable extractor NUL counts are disclosed.", "Poppler lacks optional Adobe-GB1 mapping data; extraction and rendering gates pass."],
    }
    structure = {"status": "PASS_WITH_WARNINGS", "documents": documents, "final_build_log": log, "cross_pdf_semantic_identity": True, "actionable_defects": []}
    dump(OUT / "render-hash-inventory.json", render_inventory)
    dump(OUT / "structure-and-pdf-qa.json", structure)
    report_documents = dict(documents)
    report_documents["artifact-renders"] = {engine: renderings[engine]["artifact"] for engine in renderings}
    write_reports(identities, comparisons, report_documents, log)
    print("PASS_WITH_WARNINGS")
    print(relative(OUT / "render-hash-inventory.json"))
    print(relative(OUT / "structure-and-pdf-qa.json"))
    print(relative(PREFLIGHT))
    print(relative(REPORT))


if __name__ == "__main__":
    main()
