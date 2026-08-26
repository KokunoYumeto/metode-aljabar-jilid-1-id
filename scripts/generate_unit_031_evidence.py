#!/usr/bin/env python3
"""Generate fail-closed PDF and all-page render evidence for O013 Unit 031.

The renderer/contact-sheet primitives are reused from the admitted Unit 030
generator. Unit-specific identities, structure, diagnostics, and visual
findings are independently bound below; unresolved placeholders refuse to run.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import fitz
from PIL import Image
from pypdf import PdfReader

import generate_unit_030_evidence as base


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa/unit-031-evidence"
REPORT = ROOT / "qa/UNIT_031_VISUAL_QA_20260826.md"
PREFLIGHT = ROOT / "qa/UNIT_031_VISUAL_PREFLIGHT_20260826.md"
DPI = 144

# These values are replaced only after two clean builds, the release artifact,
# and sanitized final log have stable, independently verified bytes.
CONFIG_READY = True
PAGES = 9
PIXEL_SIZE = (998, 1418)
PDF_NAME = "unit-031-bab-4-grup-solvabel-dan-nilpoten.pdf"
DOCS = {
    "build-i": (
        ROOT / "build/unit-031-clean-i" / PDF_NAME,
        126_051,
        "9802661e5558d1879616703538f848a3091b668383fa2b0679c8913337566a43",
    ),
    "build-j": (
        ROOT / "build/unit-031-clean-j" / PDF_NAME,
        126_053,
        "313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb",
    ),
    "artifact": (
        ROOT / "artifacts/unit-031-bab-4-grup-solvabel-dan-nilpoten-id.pdf",
        126_053,
        "313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb",
    ),
}
FINAL_LOG = (
    ROOT / "qa/UNIT_031_BUILD_FINAL.log",
    77_142,
    "47dd6cc5677888afeee4b7e0e7fb4800f16790125746b0f32c9a40216a79a548",
)
RAW_FINAL_LOG = ROOT / "build/unit-031-clean-j" / "unit-031-bab-4-grup-solvabel-dan-nilpoten.log"
EXPECTED_METADATA: dict[str, str] = {
    "/Creator": "LaTeX with hyperref",
    "/Title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 31: Grup Solvabel dan Grup Nilpoten",
    "/Subject": "Terjemahan Bahasa Indonesia independen; Bagian 4.7 lengkap",
    "/Author": "Wen-Wei Li",
    "/Keywords": "aljabar, teori grup, grup solvabel, grup nilpoten, abelianisasi, Feit-Thompson, grup Heisenberg, id-ID",
    "/Producer": "MiKTeX-dvipdfmx (20260404)",
    "/CreationDate": "D:20260825000000Z",
}
EXPECTED_OUTLINE: list[tuple[str, int]] = [
    ("4.7 Grup Solvabel dan Grup Nilpoten", 3),
    ("Daftar Pustaka", 9),
    ("Indeks Istilah", 9),
    ("Indeks Simbol", 9),
]
EXPECTED_DESTINATIONS = 37
EXPECTED_ACTIONS: Counter[str] = Counter({"/GoTo": 14, "/URI": 3})
EXPECTED_FONTS = 29
EXPECTED_WARNING_COUNTS: dict[str, int] = {
    "latex_release": 3,
    "xecjk": 1,
    "braids": 1,
    "fontspec_cjk": 6,
}
VISUAL_FINDINGS: list[str] = [
    "Hierarki judul dan subjudul terpusat; panel cakupan berupa prosa eksplisit, terbaca jelas, dan bukan blok kemajuan terisi/kosong yang ambigu.",
    "Identitas edisi dan sumber, hak, non-endorsement, provenance model, tautan, dan ikon CC seluruhnya terbaca, berada dalam batas halaman, dan tidak bertabrakan.",
    "Judul Bagian 4.7, definisi awal, daftar, rumus komutator, serta kedua diagram kurung deret tersusun jelas tanpa tumpang tindih.",
    "Diagram abelianisasi, lema, rujukan, teks pembuktian, dan tanda akhir bukti tetap tajam serta memiliki jarak yang aman.",
    "Lema dan pembuktian yang padat, perbaikan pembuktian yang dinyatakan, serta deret-deret tampil utuh tanpa orphan, tabrakan, atau tepi terpotong.",
    "Sitasi Feit--Thompson, kedua tampilan matriks segitiga, rumus ruang vektor, dan prosa sekelilingnya mengalir alami dalam lebar teks.",
    "Tampilan empat suku yang diperbaiki seimbang dalam dua baris; tanda sama dengan, seluruh tanda tambah, dan keempat suku utuh, sementara rumus sejajar berikutnya tetap muat.",
    "Deret sentral menaik, bukti p-grup, konstruksi Heisenberg, dan semua tampilan matematis terbaca jelas dengan margin aman.",
    "Rumus penutup, bibliografi, indeks istilah enam entri, dan indeks simbol tiga entri terbaca pada satu halaman yang terisi wajar tanpa halaman kesepuluh yang jarang.",
]


def configure_base() -> None:
    base.ROOT = ROOT
    base.OUT = OUT
    base.DPI = DPI
    base.PAGES = PAGES
    base.PIXEL_SIZE = PIXEL_SIZE
    base.DOCS = DOCS


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


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def file_identity(path: Path) -> dict[str, object]:
    return {"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def assert_configuration(*, require_findings: bool) -> None:
    assert CONFIG_READY, "Unit 031 build identities are not yet bound"
    assert PAGES > 0 and all(PIXEL_SIZE)
    if require_findings:
        assert len(VISUAL_FINDINGS) == PAGES
    assert EXPECTED_METADATA and EXPECTED_OUTLINE
    assert EXPECTED_DESTINATIONS > 0 and EXPECTED_ACTIONS and EXPECTED_FONTS > 0
    assert set(EXPECTED_WARNING_COUNTS) == {
        "latex_release",
        "xecjk",
        "braids",
        "fontspec_cjk",
    }
    for _, expected_bytes, expected_hash in (*DOCS.values(), FINAL_LOG):
        assert expected_bytes > 0 and re.fullmatch(r"[0-9a-f]{64}", expected_hash)


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


def render_gate(renderings: dict[str, Any]) -> dict[str, Any]:
    comparisons: dict[str, Any] = {}
    for engine in ("poppler", "mupdf"):
        comparisons[engine] = {}
        for left, right, key in (
            ("build-i", "build-j", "build-i_vs_build-j"),
            ("build-j", "artifact", "build-j_vs_artifact"),
        ):
            rows = []
            for left_page, right_page in zip(
                renderings[engine][left]["pages"],
                renderings[engine][right]["pages"],
                strict=True,
            ):
                rows.append(
                    {
                        "page": left_page["page"],
                        "decoded_pixel_identical": left_page["decoded_rgb_sha256"]
                        == right_page["decoded_rgb_sha256"],
                        "png_byte_identical": left_page["png_sha256"] == right_page["png_sha256"],
                    }
                )
            assert len(rows) == PAGES and all(row["decoded_pixel_identical"] for row in rows)
            comparisons[engine][key] = {
                f"all_{PAGES}_decoded_pixel_identical": True,
                "pages": rows,
            }
    edge_pages = [
        page
        for engine in renderings.values()
        for document in engine.values()
        for page in document["pages"]
    ]
    assert len(edge_pages) == 2 * 3 * PAGES
    assert not any(page["outer_3px_ink_pixels"] for page in edge_pages)
    return comparisons


def outline_records(reader: PdfReader) -> list[dict[str, Any]]:
    return base.outline_records(reader)


def inspect_document(name: str, path: Path, work: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    assert not reader.is_encrypted and len(reader.pages) == PAGES
    root = base.dereference(reader.trailer["/Root"])
    assert str(root.get("/Lang")) == "id-ID"
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    assert metadata == EXPECTED_METADATA
    assert path.read_bytes().startswith(b"%PDF-1.7")
    names = base.dereference(root.get("/Names")) or {}
    assert sorted(map(str, names.keys())) == ["/Dests"]
    assert names.get("/JavaScript") is None and names.get("/EmbeddedFiles") is None
    assert root.get("/AcroForm") is None and root.get("/AA") is None
    open_action = base.safe_open_action(reader, root)
    destinations = {
        str(key): reader.get_destination_page_number(value) + 1
        for key, value in reader.named_destinations.items()
    }
    assert len(destinations) == EXPECTED_DESTINATIONS
    assert all(1 <= page <= PAGES for page in destinations.values())
    outline = outline_records(reader)
    assert outline == [
        {"title": title, "page": page, "depth": 0}
        for title, page in EXPECTED_OUTLINE
    ]

    fonts: dict[str, dict[str, Any]] = {}
    pypdf_pages: list[str] = []
    links: list[dict[str, Any]] = []
    action_counts: Counter[str] = Counter()
    bad_rectangles: list[dict[str, Any]] = []
    broken_destinations: list[dict[str, Any]] = []
    unsafe_actions: list[dict[str, Any]] = []
    uri_targets: list[str] = []
    goto_targets: list[str] = []
    page_geometry: list[dict[str, Any]] = []
    page_additional_actions = 0
    annotation_additional_actions = 0
    for page_number, page in enumerate(reader.pages, 1):
        page_additional_actions += page.get("/AA") is not None
        media = [float(value) for value in page.mediabox]
        crop = [float(value) for value in page.cropbox]
        assert media == crop and int(page.get("/Rotate", 0)) == 0
        assert [round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)] == [498.9, 708.66]
        page_geometry.append(
            {"page": page_number, "media_box": media, "crop_box": crop, "rotate": int(page.get("/Rotate", 0))}
        )
        pypdf_pages.append(page.extract_text() or "")
        resources = base.dereference(page.get("/Resources")) or {}
        for reference in (base.dereference(resources.get("/Font")) or {}).values():
            record = base.font_record(reference)
            fonts[record["object"] or record["basefont"]] = record
        for ordinal, annotation_reference in enumerate(base.dereference(page.get("/Annots")) or [], 1):
            annotation = base.dereference(annotation_reference)
            annotation_additional_actions += annotation.get("/AA") is not None
            assert str(annotation.get("/Subtype")) == "/Link"
            rectangle = [float(value) for value in annotation.get("/Rect", [])]
            width, height = float(page.mediabox.width), float(page.mediabox.height)
            if not (
                len(rectangle) == 4
                and -0.5 <= rectangle[0] <= rectangle[2] <= width + 0.5
                and -0.5 <= rectangle[1] <= rectangle[3] <= height + 0.5
            ):
                bad_rectangles.append({"page": page_number, "rect": rectangle})
            action = base.dereference(annotation.get("/A"))
            assert action is not None
            action_type = str(action.get("/S"))
            action_counts[action_type] += 1
            if action_type == "/GoTo":
                target = str(action.get("/D"))
                goto_targets.append(target)
                if target not in destinations:
                    broken_destinations.append({"page": page_number, "target": target})
            elif action_type == "/URI":
                target = str(action.get("/URI"))
                uri_targets.append(target)
                if not target.startswith("https://"):
                    unsafe_actions.append({"page": page_number, "action": action_type, "target": target})
            else:
                target = ""
                unsafe_actions.append({"page": page_number, "action": action_type})
            links.append(
                {"page": page_number, "ordinal_on_page": ordinal, "rect": rectangle, "action": action_type, "target": target}
            )
    assert action_counts == EXPECTED_ACTIONS
    assert not bad_rectangles and not broken_destinations and not unsafe_actions
    assert not page_additional_actions and not annotation_additional_actions

    pypdf_text = "\f".join(pypdf_pages)
    text_path = work / f"{name}.txt"
    pdftotext = shutil.which("pdftotext")
    pdffonts = shutil.which("pdffonts")
    pdfinfo = shutil.which("pdfinfo")
    assert pdftotext and pdffonts and pdfinfo
    _, text_stderr = base.run([pdftotext, "-layout", "-enc", "UTF-8", str(path), str(text_path)])
    poppler_bytes = text_path.read_bytes()
    poppler_text = poppler_bytes.decode("utf-8", "replace")
    fonts_stdout, fonts_stderr = base.run([pdffonts, str(path)])
    info_stdout, info_stderr = base.run([pdfinfo, str(path)])
    font_rows = [
        line
        for line in fonts_stdout.splitlines()
        if re.search(r"\s(?:yes|no)\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", line)
    ]
    info = {
        key.strip(): value.strip()
        for line in info_stdout.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }
    assert info.get("Pages") == str(PAGES) and info.get("Tagged") == "no"

    mupdf_pages: list[str] = []
    out_of_bounds_text_blocks: list[dict[str, Any]] = []
    with fitz.open(path) as document:
        assert len(document) == PAGES
        for page_number, page in enumerate(document, 1):
            mupdf_pages.append(page.get_text("text"))
            for block in page.get_text("blocks"):
                x0, y0, x1, y1 = block[:4]
                rectangle = page.rect
                if not (
                    x0 >= rectangle.x0 - 1
                    and y0 >= rectangle.y0 - 1
                    and x1 <= rectangle.x1 + 1
                    and y1 <= rectangle.y1 + 1
                ):
                    out_of_bounds_text_blocks.append({"page": page_number, "bbox": [x0, y0, x1, y1]})
    assert not out_of_bounds_text_blocks
    mupdf_text = "\f".join(mupdf_pages)
    font_records = sorted(fonts.values(), key=lambda item: (item["normalized"], item["object"] or ""))
    assert len(font_records) == EXPECTED_FONTS and all(item["embedded"] for item in font_records)
    assert len(font_rows) == EXPECTED_FONTS
    assert all(re.search(r"\syes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", row) for row in font_rows)
    assert "�" not in pypdf_text + poppler_text + mupdf_text
    nul_counts = {
        "pypdf": pypdf_text.count("\0"),
        "pdftotext_layout": poppler_text.count("\0"),
        "mupdf": mupdf_text.count("\0"),
    }
    assert nul_counts == {"pypdf": 17, "pdftotext_layout": 0, "mupdf": 0}
    return {
        "identity": file_identity(path),
        "pages": PAGES,
        "pdf_header": "%PDF-1.7",
        "language": "id-ID",
        "tagged": False,
        "encrypted": False,
        "metadata": metadata,
        "catalog_keys": sorted(map(str, root.keys())),
        "name_tree_keys": sorted(map(str, names.keys())),
        "open_action": open_action,
        "page_geometry": page_geometry,
        "outline": outline,
        "named_destinations": dict(sorted(destinations.items())),
        "actions": {
            "counts": dict(sorted(action_counts.items())),
            "links": links,
            "uris": uri_targets,
            "gotos": goto_targets,
            "broken_destinations": broken_destinations,
            "unsafe": unsafe_actions,
            "out_of_bounds_rectangles": bad_rectangles,
            "all_uris_https": all(uri.startswith("https://") for uri in uri_targets),
            "catalog_additional_action": False,
            "page_additional_actions": page_additional_actions,
            "annotation_additional_actions": annotation_additional_actions,
        },
        "payloads": {"forms": False, "javascript": False, "embedded_files": False},
        "fonts": {
            "pypdf_unique": len(font_records),
            "pypdf_all_embedded": True,
            "records": font_records,
            "pdffonts_rows": len(font_rows),
            "pdffonts_all_embedded": True,
            "pdffonts_stderr": fonts_stderr.strip(),
        },
        "text": {
            "pypdf_sha256": bytes_sha256(pypdf_text.encode("utf-8")),
            "pypdf_page_sha256": [bytes_sha256(text.encode("utf-8")) for text in pypdf_pages],
            "pdftotext_layout_sha256": bytes_sha256(poppler_bytes),
            "mupdf_sha256": bytes_sha256(mupdf_text.encode("utf-8")),
            "nul_characters": nul_counts,
            "replacement_characters": 0,
        },
        "geometry": {"fitz_text_blocks_out_of_bounds": out_of_bounds_text_blocks},
        "pdfinfo": info,
        "tool_diagnostics": {"pdfinfo_stderr": info_stderr.strip(), "pdftotext_stderr": text_stderr.strip()},
        "checks": {
            "page_count": True,
            "language_id_ID": True,
            "untagged_disclosed": True,
            "metadata_exact": True,
            "outline_exact": True,
            "named_destinations_exact": True,
            "action_counts_exact": True,
            "link_closure": True,
            "safe_actions": True,
            "rectangles_in_bounds": True,
            "text_blocks_in_bounds": True,
            "no_active_payloads": True,
            "fonts_embedded": True,
            "text_has_no_replacement_characters": True,
            "known_math_font_nul_census": True,
        },
    }


def semantic_font_projection(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            key: item[key]
            for key in ("object", "normalized", "subtype", "embedded", "streams", "to_unicode")
        }
        for item in document["fonts"]["records"]
    ]


def sanitized_build_log(raw_text: str) -> tuple[str, dict[str, int]]:
    assert "\r" not in raw_text
    original_newlines = raw_text.count("\n")
    miktex_prefix = str(Path.home() / "AppData/Local/Programs/MiKTeX")
    absolute_build_prefix = str((ROOT / "build/unit-031-clean-j").resolve())
    relative_build_prefix = r"build\unit-031-clean-j"
    sanitized = raw_text
    miktex_occurrences = sanitized.count(miktex_prefix)
    assert miktex_occurrences > 0
    sanitized = sanitized.replace(miktex_prefix, "<MIKTEX_ROOT>")

    lane_prefix = str(ROOT.resolve())
    lane_replacements = sanitized.count(lane_prefix)
    sanitized = sanitized.replace(lane_prefix, "<LANE_ROOT>")
    for split_at in range(1, len(lane_prefix)):
        wrapped = lane_prefix[:split_at] + "\n" + lane_prefix[split_at:]
        occurrences = sanitized.count(wrapped)
        if occurrences:
            sanitized = sanitized.replace(wrapped, "<LANE_ROOT>\n")
            lane_replacements += occurrences

    relative_replacements = sanitized.count(absolute_build_prefix)
    sanitized = sanitized.replace(absolute_build_prefix, relative_build_prefix)
    for split_at in range(1, len(absolute_build_prefix)):
        wrapped = absolute_build_prefix[:split_at] + "\n" + absolute_build_prefix[split_at:]
        occurrences = sanitized.count(wrapped)
        if occurrences:
            sanitized = sanitized.replace(wrapped, relative_build_prefix + "\n")
            relative_replacements += occurrences

    assert sanitized.count("\n") == original_newlines
    assert re.search(r"[A-Za-z]:\\Users\\", sanitized, re.I) is None
    assert Path.home().name.lower() not in sanitized.lower()
    return sanitized, {
        "miktex_placeholder_occurrences": miktex_occurrences,
        "lane_root_placeholder_occurrences": lane_replacements,
        "relative_build_prefix_occurrences": relative_replacements,
        "line_records_preserved": original_newlines + 1,
        "windows_user_path_occurrences": 0,
        "profile_name_occurrences": 0,
    }


def final_log_record() -> dict[str, Any]:
    path, expected_bytes, expected_sha256 = FINAL_LOG
    published_bytes = path.read_bytes()
    text = published_bytes.decode("utf-8")
    raw_text = RAW_FINAL_LOG.read_text(encoding="utf-8")
    reproduced, sanitization = sanitized_build_log(raw_text)
    assert reproduced.encode("utf-8") == published_bytes
    assert len(published_bytes) == expected_bytes and sha256(path) == expected_sha256
    forbidden_patterns = {
        "fatal_error": r"fatal error",
        "emergency_stop": r"emergency stop",
        "undefined_control_sequence": r"undefined control sequence",
        "latex_error": r"! LaTeX Error",
        "undefined_references": r"undefined references|Reference .* undefined",
        "undefined_citations": r"undefined citations|Citation .* undefined",
        "missing_character": r"missing character",
        "overfull": r"overfull \\[hv]box",
        "underfull": r"underfull \\[hv]box",
        "empty_link_target": r"empty link target",
    }
    diagnostics = {
        key: len(re.findall(pattern, text, re.I))
        for key, pattern in forbidden_patterns.items()
    }
    assert not any(diagnostics.values()), diagnostics
    page_markers = re.findall(r"Output written on .*?\((\d+)\s+p\s*ages?\)\.", text, re.S)
    assert page_markers and int(page_markers[-1]) == PAGES
    warning_counts = {
        "latex_release": text.count("LaTeX Warning: You have requested release"),
        "xecjk": text.count("Package xeCJK Warning"),
        "braids": text.count("Package braids Warning"),
        "fontspec_cjk": text.count("Script 'CJK' not explicitly supported"),
    }
    assert warning_counts == EXPECTED_WARNING_COUNTS
    assert len(re.findall(r"[A-Za-z]:\\Users\\", text, re.I)) == 0
    assert text.lower().count(Path.home().name.lower()) == 0
    return {
        "identity": {"path": relative(path), "bytes": expected_bytes, "sha256": expected_sha256},
        "page_marker": PAGES,
        "forbidden_diagnostics": diagnostics,
        "warning_counts": warning_counts,
        "sanitization": sanitization,
        "sanitized_log_reproduced_from_build_j": True,
        "evidence_sanitized": True,
    }


def write_reports(
    identities: dict[str, Any],
    comparisons: dict[str, Any],
    documents: dict[str, Any],
    log: dict[str, Any],
) -> None:
    identity_rows = "\n".join(
        f"| `{value['path']}` | {value['bytes']:,} | `{value['sha256']}` |"
        for value in identities.values()
        if isinstance(value, dict)
    )
    comparison_rows = "\n".join(
        f"- {engine} {pair.replace('_', ' ')}: seluruh {PAGES} halaman RGB terdekode identik."
        for engine in comparisons
        for pair in comparisons[engine]
    )
    page_rows = "\n".join(
        f"| {page} | {VISUAL_FINDINGS[page - 1]} |"
        for page in range(1, PAGES + 1)
    )
    artifact_pages = {
        engine: documents["artifact-renders"][engine]["pages"]
        for engine in ("poppler", "mupdf")
    }
    pixel_rows = "\n".join(
        f"| {page} | `{artifact_pages['poppler'][page - 1]['decoded_rgb_sha256']}` | "
        f"`{artifact_pages['mupdf'][page - 1]['decoded_rgb_sha256']}` |"
        for page in range(1, PAGES + 1)
    )
    artifact = documents["artifact"]
    report = f"""# Unit 031 visual and PDF QA — 2026-08-26

Status: **PASS WITH WARNINGS**. Exact identity, decoded-pixel, metadata,
navigation, font, extraction, action/link, geometry, diagnostics, and all-page
visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
{identity_rows}

Build J and the release artifact are byte-identical. All three PDFs contain
{PAGES} pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at {DPI} dpi
({PIXEL_SIZE[0]} × {PIXEL_SIZE[1]} pixels per page). Equality uses decoded RGB
pixels, not PNG compression.

{comparison_rows}

All {2 * 3 * PAGES} renders have zero ink in their outer three-pixel band.
Six contact sheets and every render identity are recorded in
`qa/unit-031-evidence/render-hash-inventory.json`.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
{pixel_rows}

## PDF and diagnostic gate

- PDF `{artifact['pdf_header']}`; `/Lang id-ID`; {PAGES} pages; unencrypted;
  exact metadata; no form, JavaScript, additional action, or embedded file.
- The outline has {len(EXPECTED_OUTLINE)} entries and all
  {EXPECTED_DESTINATIONS} named destinations resolve.
- Action inventory is exact: {dict(EXPECTED_ACTIONS)}. Every `/GoTo` closes
  over the destination inventory and every URI is HTTPS.
- Link rectangles and MuPDF text blocks are in bounds. All
  {artifact['fonts']['pypdf_unique']} pypdf font objects and
  {artifact['fonts']['pdffonts_rows']} `pdffonts` rows are embedded.
- pypdf, Poppler layout text, and MuPDF text agree independently across both
  builds and the artifact. No extractor contains a replacement character;
  Poppler and MuPDF contain no NUL, while pypdf has the exact stable count of
  17 from unmapped mathematics-font glyphs disclosed in the JSON evidence.
- The final log is byte-reproduced from the build-J log after path
  sanitization. Fatal/error, unresolved reference/citation, missing-character,
  empty-target, overfull, and underfull diagnostics are all zero.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
{page_rows}

No clipping, overlap, edge contact, broken glyph, unresolved reference,
unreadable formula, overfull/underfull residue, or unintended blank page remains.

## Disclosed warnings

The PDF is untagged, so no tagged-accessibility claim is made. pypdf exposes
17 stable NUL placeholders for unmapped mathematics-font glyphs; Poppler and
MuPDF expose none, all extractors have zero replacement characters, and both
renderers visibly reproduce the affected mathematics. Fixed toolchain
advisories are recorded exactly as {log['warning_counts']}; they do not concern
content, references, glyphs, or page layout. Build I and J may differ in
volatile font-subset tags, but normalized structure, extraction, and
same-renderer decoded pixels agree; build J and the artifact are byte-identical.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
"""
    REPORT.write_text(report, encoding="utf-8", newline="\n")
    preflight = f"""# Unit 031 visual preflight — 2026-08-26

Status: **PASS WITH WARNINGS**. Two independent clean builds and the release
artifact were structurally inspected and rendered across all {PAGES} pages.
No actionable defect remains.

- Build I: {PAGES} pages / {identities['build-i']['bytes']:,} bytes / SHA-256
  `{identities['build-i']['sha256']}`.
- Build J: {PAGES} pages / {identities['build-j']['bytes']:,} bytes / SHA-256
  `{identities['build-j']['sha256']}`.
- Artifact: {PAGES} pages / {identities['artifact']['bytes']:,} bytes / SHA-256
  `{identities['artifact']['sha256']}`; byte-identical to build J.
- Poppler and MuPDF produced {2 * 3 * PAGES} full-page renders. Every
  same-renderer decoded-pixel comparison passed and every outer edge was clear.
- Metadata, outline, destinations, links, safe actions, embedded fonts, three
  extraction surfaces, page geometry, and all-page visual review passed.
- Final diagnostics contain zero errors, unresolved references/citations,
  missing characters, empty targets, overfull boxes, or underfull boxes.

The PDF is untagged, so no tagged-accessibility claim is made. pypdf's exact
17-NUL mathematics-font extraction limitation is disclosed; Poppler and MuPDF
contain no NUL or replacement characters. Fixed toolchain advisories are
retained in the evidence log.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.
"""
    PREFLIGHT.write_text(preflight, encoding="utf-8", newline="\n")


def main() -> None:
    render_only = sys.argv[1:] == ["--render-only"]
    assert not sys.argv[1:] or render_only, "usage: generate_unit_031_evidence.py [--render-only]"
    assert_configuration(require_findings=not render_only)
    configure_base()
    identities = bound_identities()
    resolved = OUT.resolve()
    assert resolved.parent == (ROOT / "qa").resolve() and resolved.name == "unit-031-evidence"
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    renderings: dict[str, Any] = {"poppler": {}, "mupdf": {}}
    contact_sheets: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="unit031-evidence-") as temporary:
        work = Path(temporary)
        for engine in renderings:
            for document_name, (path, _, _) in DOCS.items():
                rendering = base.render(engine, document_name, path, work)
                renderings[engine][document_name] = rendering
                contact_sheets.append(base.contact_sheet(engine, document_name, rendering["pages"]))
        comparisons = render_gate(renderings)
        documents = {
            name: inspect_document(name, specification[0], work)
            for name, specification in DOCS.items()
        }
    for field in ("metadata", "outline", "named_destinations", "open_action", "page_geometry", "actions"):
        assert documents["build-i"][field] == documents["build-j"][field] == documents["artifact"][field], field
    assert semantic_font_projection(documents["build-i"]) == semantic_font_projection(documents["build-j"]) == semantic_font_projection(documents["artifact"])
    for field in ("pypdf_sha256", "pypdf_page_sha256", "pdftotext_layout_sha256", "mupdf_sha256"):
        assert documents["build-i"]["text"][field] == documents["build-j"]["text"][field] == documents["artifact"]["text"][field], field
    log = final_log_record()
    if render_only:
        print("RENDER_ONLY_PASS")
        print(relative(OUT / "renders" / "poppler" / "artifact"))
        print(relative(OUT / "renders" / "mupdf" / "artifact"))
        return
    poppler_version = base.run([shutil.which("pdftoppm"), "-v"])
    mupdf_version = base.run([shutil.which("mutool"), "-v"])
    versions = {
        "poppler": " ".join(" ".join(poppler_version).split()),
        "mupdf": " ".join(" ".join(mupdf_version).split()),
    }
    assert "24.04.0" in versions["poppler"] and "1.23.0" in versions["mupdf"]
    render_inventory = {
        "status": "PASS_WITH_WARNINGS",
        "identities": identities,
        "renderer_versions": versions,
        "renderers": renderings,
        "contact_sheets": contact_sheets,
        "decoded_pixel_comparisons": comparisons,
        "edge_gate": {"outer_band_pixels": 3, f"all_{2 * 3 * PAGES}_zero_ink": True},
        "manual_visual_review": {
            "status": "PASS",
            "renderers": ["Poppler", "MuPDF"],
            "pages_per_document": PAGES,
            "findings": {str(index): finding for index, finding in enumerate(VISUAL_FINDINGS, 1)},
            "actionable_defects": [],
        },
        "warnings": [
            "PDF is untagged; no tagged-accessibility claim is made.",
            "dvipdfmx subset tags may vary between I and J; normalized semantics and decoded pixels agree.",
            "Fixed toolchain advisories are retained exactly in the sanitized log.",
            "pypdf has 17 stable NUL placeholders for unmapped mathematics-font glyphs; Poppler and MuPDF have zero.",
        ],
    }
    structure = {
        "status": "PASS_WITH_WARNINGS",
        "documents": documents,
        "final_build_log": log,
        "cross_pdf_semantic_identity": True,
        "actionable_defects": [],
    }
    dump(OUT / "render-hash-inventory.json", render_inventory)
    dump(OUT / "structure-and-pdf-qa.json", structure)
    report_documents = dict(documents)
    report_documents["artifact-renders"] = {
        engine: renderings[engine]["artifact"] for engine in renderings
    }
    write_reports(identities, comparisons, report_documents, log)
    print("PASS_WITH_WARNINGS")
    print(relative(OUT / "render-hash-inventory.json"))
    print(relative(OUT / "structure-and-pdf-qa.json"))
    print(relative(PREFLIGHT))
    print(relative(REPORT))


if __name__ == "__main__":
    main()
