#!/usr/bin/env python3
"""Two-build PDF/render preflight scaffold for O013 Li Unit 034.

This script authors no PDF and writes only a provisional packet under
``build``. It refuses to proceed unless canonical integration/terminology pass
``check_unit_034_structure.py`` and the observed nonfatal underfull-box count
has been supplied explicitly.
"""

from __future__ import annotations

from collections import Counter
import argparse
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
from pypdf import PdfReader

import generate_unit_030_evidence as render_base


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
CANDIDATE_ID = (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62")
PDF_NAME = "unit-034-bab-4-limit-dan-kompletisasi-grup.pdf"
DEFAULT_BUILDS = {
    "build-i": ROOT / "build/unit-034-final-i" / PDF_NAME,
    "build-j": ROOT / "build/unit-034-final-j" / PDF_NAME,
}
EXPECTED_METADATA = {
    "/Creator": "LaTeX with hyperref",
    "/Title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Unit 34: Limit dan Pelengkapan Grup",
    "/Subject": "Terjemahan Bahasa Indonesia independen; Bagian 4.10 lengkap",
    "/Author": "Wen-Wei Li",
    "/Keywords": "aljabar, teori grup, limit proyektif, grup topologis, grup profinit, pelengkapan, bilangan bulat p-adik, modul Tate, id-ID",
    "/Producer": "MiKTeX-dvipdfmx (20260404)",
    "/CreationDate": "D:20260827000000Z",
}
EXPECTED_OUTLINE_TITLES = [
    "4.10 Limit dan Pelengkapan Grup",
    "Daftar Pustaka",
    "Indeks Istilah",
    "Indeks Simbol",
]
FORBIDDEN_LOG_PATTERNS = {
    "fatal_error": r"fatal error",
    "emergency_stop": r"emergency stop",
    "undefined_control_sequence": r"undefined control sequence",
    "latex_error": r"! LaTeX Error",
    "undefined_references": r"undefined references|Reference .* undefined",
    "undefined_citations": r"undefined citations|Citation .* undefined",
    "missing_character": r"missing character",
    "overfull": r"overfull \\[hv]box",
    "empty_link_target": r"empty link target",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def identity(path: Path) -> dict[str, Any]:
    return {"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def require_admitted_candidate() -> dict[str, Any]:
    record = identity(CANDIDATE)
    assert (record["bytes"], record["sha256"]) == CANDIDATE_ID, record
    data = CANDIDATE.read_bytes()
    assert b"\r" not in data and data.endswith(b"\n") and not data.endswith(b"\n\n")
    checks = []
    for script in ("check_unit_034_candidate.py", "check_unit_034_structure.py"):
        run = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        assert run.returncode == 0 and run.stderr == "", (script, run.stdout, run.stderr)
        checks.append({"script": f"scripts/{script}", "stdout": run.stdout})
    record["bounded_checks"] = checks
    return record


def inspect_log(path: Path, pages: int, expected_underfull_hboxes: int) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    diagnostics = {
        key: len(re.findall(pattern, text, re.I))
        for key, pattern in FORBIDDEN_LOG_PATTERNS.items()
    }
    assert not any(diagnostics.values()), diagnostics
    underfull_hboxes = len(re.findall(r"underfull \\hbox", text, re.I))
    assert underfull_hboxes == expected_underfull_hboxes, (
        underfull_hboxes,
        expected_underfull_hboxes,
    )
    markers = re.findall(
        r"Output written on .*?\((\d+)\s+p\s*a\s*g\s*e\s*s?\)\.",
        text,
        re.S,
    )
    assert markers and int(markers[-1]) == pages
    return {
        "identity": identity(path),
        "page_marker": pages,
        "forbidden_diagnostics": diagnostics,
        "nonfatal_underfull_hboxes": underfull_hboxes,
        "warning_counts": {
            "latex_release": text.count("LaTeX Warning: You have requested release"),
            "xecjk": text.count("Package xeCJK Warning"),
            "braids": text.count("Package braids Warning"),
            "fontspec_cjk": text.count("Script 'CJK' not explicitly supported"),
        },
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    assert not reader.is_encrypted and len(reader.pages) >= 3
    assert path.read_bytes().startswith(b"%PDF-1.7")
    root = render_base.dereference(reader.trailer["/Root"])
    assert str(root.get("/Lang")) == "id-ID"
    assert {str(key): str(value) for key, value in (reader.metadata or {}).items()} == EXPECTED_METADATA
    assert root.get("/AcroForm") is None and root.get("/AA") is None
    names = render_base.dereference(root.get("/Names")) or {}
    assert names.get("/JavaScript") is None and names.get("/EmbeddedFiles") is None
    outline = render_base.outline_records(reader)
    assert [row["title"] for row in outline] == EXPECTED_OUTLINE_TITLES, outline
    assert all(row["depth"] == 0 and 1 <= row["page"] <= len(reader.pages) for row in outline)
    destinations = {
        str(key): reader.get_destination_page_number(value) + 1
        for key, value in reader.named_destinations.items()
    }
    assert destinations and all(1 <= page <= len(reader.pages) for page in destinations.values())

    action_counts: Counter[str] = Counter()
    fonts: dict[str, dict[str, Any]] = {}
    pypdf_pages: list[str] = []
    for page in reader.pages:
        assert [round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2)] == [498.9, 708.66]
        assert list(map(float, page.mediabox)) == list(map(float, page.cropbox))
        assert int(page.get("/Rotate", 0)) == 0 and page.get("/AA") is None
        pypdf_pages.append(page.extract_text() or "")
        resources = render_base.dereference(page.get("/Resources")) or {}
        for reference in (render_base.dereference(resources.get("/Font")) or {}).values():
            record = render_base.font_record(reference)
            fonts[record["object"] or record["basefont"]] = record
        for annotation_reference in render_base.dereference(page.get("/Annots")) or []:
            annotation = render_base.dereference(annotation_reference)
            assert str(annotation.get("/Subtype")) == "/Link" and annotation.get("/AA") is None
            action = render_base.dereference(annotation.get("/A"))
            assert action is not None
            kind = str(action.get("/S"))
            action_counts[kind] += 1
            if kind == "/GoTo":
                assert str(action.get("/D")) in destinations
            elif kind == "/URI":
                assert str(action.get("/URI")).startswith("https://")
            else:
                raise AssertionError(f"unsafe action: {kind}")
    assert fonts and all(record["embedded"] for record in fonts.values())
    pypdf_text = "\f".join(pypdf_pages)
    assert "\ufffd" not in pypdf_text

    mupdf_pages: list[str] = []
    with fitz.open(path) as document:
        assert len(document) == len(reader.pages)
        for page in document:
            mupdf_pages.append(page.get_text("text"))
            for block in page.get_text("blocks"):
                x0, y0, x1, y1 = block[:4]
                assert x0 >= page.rect.x0 - 1 and y0 >= page.rect.y0 - 1
                assert x1 <= page.rect.x1 + 1 and y1 <= page.rect.y1 + 1
    mupdf_text = "\f".join(mupdf_pages)
    assert "\ufffd" not in mupdf_text

    return {
        "identity": identity(path),
        "pages": len(reader.pages),
        "metadata": EXPECTED_METADATA,
        "outline": outline,
        "named_destinations": destinations,
        "action_counts": dict(action_counts),
        "fonts": {
            "unique": len(fonts),
            "all_embedded": True,
            "semantic_projection": [
                {key: row[key] for key in ("normalized", "subtype", "embedded", "streams", "to_unicode")}
                for row in sorted(fonts.values(), key=lambda item: (item["normalized"], item["object"] or ""))
            ],
        },
        "text": {
            "pypdf_sha256": hashlib.sha256(pypdf_text.encode()).hexdigest(),
            "mupdf_sha256": hashlib.sha256(mupdf_text.encode()).hexdigest(),
            "pypdf_nul_characters": pypdf_text.count("\x00"),
            "mupdf_nul_characters": mupdf_text.count("\x00"),
            "replacement_characters": 0,
        },
        "tagged": False,
        "safe": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-i", type=Path, default=DEFAULT_BUILDS["build-i"])
    parser.add_argument("--build-j", type=Path, default=DEFAULT_BUILDS["build-j"])
    parser.add_argument("--output", type=Path, default=ROOT / "build/unit-034-preflight")
    parser.add_argument(
        "--expected-underfull-hboxes",
        type=int,
        required=True,
        help="exact observed nonfatal underfull-hbox count after all overfull/error repairs",
    )
    args = parser.parse_args()
    assert args.expected_underfull_hboxes >= 0
    builds = {"build-i": args.build_i.resolve(), "build-j": args.build_j.resolve()}
    out = args.output.resolve()
    assert out.parent == (ROOT / "build").resolve() and out.name.startswith("unit-034-preflight")
    assert not out.exists(), f"preflight output must be absent: {out}"
    for name, pdf in builds.items():
        assert pdf.is_file() and pdf.name == PDF_NAME, (name, pdf)

    candidate = require_admitted_candidate()
    documents = {name: inspect_pdf(path) for name, path in builds.items()}
    pages = documents["build-i"]["pages"]
    assert documents["build-j"]["pages"] == pages
    for key in ("metadata", "outline", "named_destinations", "action_counts", "fonts", "text"):
        assert documents["build-i"][key] == documents["build-j"][key], key
    logs = {
        name: inspect_log(pdf.with_suffix(".log"), pages, args.expected_underfull_hboxes)
        for name, pdf in builds.items()
    }

    out.mkdir()
    render_base.ROOT = ROOT
    render_base.OUT = out
    render_base.DPI = 144
    render_base.PAGES = pages
    render_base.PIXEL_SIZE = (998, 1418)
    renderings: dict[str, dict[str, Any]] = {"poppler": {}, "mupdf": {}}
    contact_sheets = []
    with tempfile.TemporaryDirectory(prefix="unit034-preflight-") as temporary:
        work = Path(temporary)
        for engine in renderings:
            for name, pdf in builds.items():
                rendered = render_base.render(engine, name, pdf, work)
                renderings[engine][name] = rendered
                contact_sheets.append(render_base.contact_sheet(engine, name, rendered["pages"]))
    comparisons: dict[str, Any] = {}
    for engine in renderings:
        rows = [
            {
                "page": left["page"],
                "decoded_pixel_identical": left["decoded_rgb_sha256"] == right["decoded_rgb_sha256"],
            }
            for left, right in zip(
                renderings[engine]["build-i"]["pages"],
                renderings[engine]["build-j"]["pages"],
                strict=True,
            )
        ]
        assert len(rows) == pages and all(row["decoded_pixel_identical"] for row in rows)
        comparisons[engine] = rows
    all_pages = [page for engine in renderings.values() for doc in engine.values() for page in doc["pages"]]
    assert not any(page["outer_3px_ink_pixels"] for page in all_pages)
    poppler_version = " ".join(" ".join(render_base.run([shutil.which("pdftoppm"), "-v"])).split())
    mupdf_version = " ".join(" ".join(render_base.run([shutil.which("mutool"), "-v"])).split())
    packet = {
        "schema_version": 1,
        "unit": "O013-LI-U034",
        "status": "PASS_PROVISIONAL_NOT_VISUAL_ADMISSION",
        "configuration": {"expected_underfull_hboxes": args.expected_underfull_hboxes},
        "candidate": candidate,
        "documents": documents,
        "logs": logs,
        "renderer_versions": {"poppler": poppler_version, "mupdf": mupdf_version},
        "renderers": renderings,
        "contact_sheets": contact_sheets,
        "decoded_pixel_comparisons": comparisons,
        "edge_gate": {"outer_band_pixels": 3, f"all_{len(all_pages)}_zero_ink": True},
        "next": "Inspect every full-resolution Poppler and MuPDF page, bind one finding per page, create the byte-identical artifact from build-j, then run generate_unit_034_evidence.py.",
    }
    destination = out / "preflight-observation.json"
    dump(destination, packet)
    print("PASS_PROVISIONAL_NOT_VISUAL_ADMISSION")
    print(relative(destination))
    print(relative(out / "renders/poppler/build-j"))
    print(relative(out / "renders/mupdf/build-j"))


if __name__ == "__main__":
    main()
