#!/usr/bin/env python3
"""Build the compact, reader-first checkpoint 0.3.0 release payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.0"
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-0.3.0-reader.pdf"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.3.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

UNIT_PDFS = [
    "unit-001-pendahuluan.pdf",
    "unit-002-bab-1-zfc.pdf",
    "unit-003-bab-1-struktur-urutan-dan-ordinal.pdf",
    "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf",
    "unit-005-bab-1-kardinal.pdf",
    "unit-006-bab-1-semesta-grothendieck.pdf",
    "unit-007-bab-1-latihan.pdf",
    "unit-008-bab-2-pengantar-teori-kategori.pdf",
    "unit-009-bab-2-kategori-dan-morfisme.pdf",
]

ARCHIVE_PATHS = [
    ".gitattributes",
    "README.md",
    "LICENSES.md",
    "00_control/BUILD_BASELINE.md",
    "00_control/RIGHTS_COMPONENTS.csv",
    "00_control/SOURCE_AUTHORITY.md",
    "00_control/SOURCE_MANIFEST.csv",
    "00_control/SOURCE_SELECTION.md",
    "00_control/TERMINOLOGY.id-ID.csv",
    "backend",
    "repo",
    "scripts",
    "qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md",
]
for number in range(1, 10):
    ARCHIVE_PATHS.extend(
        [
            next(
                str(path.relative_to(ROOT)).replace("\\", "/")
                for path in (ROOT / "qa").glob(f"UNIT_{number:03d}_ADMISSION_*.md")
            ),
            f"qa/unit-{number:03d}-evidence/build-log-summary.txt",
        ]
    )


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "name": path.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def pdf_facts(path: Path) -> dict[str, object]:
    reader = PdfReader(str(path))
    named = len(reader.named_destinations)
    goto = uri = widgets = javascript = launch = gotor = 0
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            if annotation.get("/Subtype") == "/Widget":
                widgets += 1
            action_ref = annotation.get("/A")
            if not action_ref:
                continue
            action = action_ref.get_object()
            kind = str(action.get("/S", ""))
            goto += kind == "/GoTo"
            uri += kind == "/URI"
            javascript += kind == "/JavaScript"
            launch += kind == "/Launch"
            gotor += kind == "/GoToR"
    return {
        "pages": len(reader.pages),
        "language": str(reader.trailer["/Root"].get("/Lang", "")),
        "tagged_pdf": "/StructTreeRoot" in reader.trailer["/Root"],
        "named_destinations": named,
        "goto_actions": goto,
        "uri_actions": uri,
        "widgets": widgets,
        "javascript_actions": javascript,
        "launch_actions": launch,
        "gotor_actions": gotor,
    }


def git_archive(commit: str, output: Path) -> None:
    command = [
        "git",
        "archive",
        "--format=zip",
        f"--output={output}",
        commit,
        "--",
        *ARCHIVE_PATHS,
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--zenodo-doi", required=True)
    parser.add_argument("--figshare-doi", required=True)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=ROOT / "tmp" / "release-0.3.0-20260822",
    )
    args = parser.parse_args()

    stage = args.output_directory.resolve()
    common = stage / "common"
    zenodo = stage / "zenodo"
    figshare = stage / "figshare"
    for directory in (common, zenodo, figshare):
        directory.mkdir(parents=True, exist_ok=True)

    reader_source = ROOT / "output" / "pdf" / READER_NAME
    if pdf_facts(reader_source)["pages"] != 96:
        raise SystemExit("Checkpoint reader must contain exactly 96 pages")
    shutil.copy2(reader_source, common / READER_NAME)
    shutil.copy2(ROOT / "LICENSES.md", common / LICENSE_NAME)
    git_archive(args.commit, common / ZIP_NAME)

    with zipfile.ZipFile(common / ZIP_NAME) as archive:
        zip_entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        zip_expanded_bytes = sum(entry.file_size for entry in zip_entries)
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise SystemExit(f"Corrupt ZIP member: {corrupt_member}")

    reader_entry = digest(common / READER_NAME)
    reader_entry.update({"role": "primary_reader", **pdf_facts(common / READER_NAME)})
    zip_entry = digest(common / ZIP_NAME)
    zip_entry.update(
        {
            "role": "compact_resumable_source_backend",
            "entries": len(zip_entries),
            "expanded_bytes": zip_expanded_bytes,
        }
    )
    license_entry = digest(common / LICENSE_NAME)
    license_entry["role"] = "controlling_component_rights_notice"

    manifest = {
        "schema": "metode-aljabar-checkpoint/v2",
        "release_date": "2026-08-22",
        "version": VERSION,
        "work": {
            "title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Edisi Bahasa Indonesia",
            "source_title": "Methods of Algebra, Volume 1",
            "source_author": "Wen-Wei Li",
            "language": "id-ID",
            "status": "partial_public_active",
            "coverage": "Pendahuluan lengkap; Bab 1 lengkap; pengantar Bab 2 dan Bagian 2.1 lengkap dalam Unit 001-009. Bagian 2.2 dan sesudahnya belum disertakan.",
            "independent_nonendorsed": True,
            "model": MODEL,
        },
        "authority": {
            "source_repository": "https://github.com/wenweili/AlJabr-1",
            "source_commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "source_tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "official_pdf_pages": 445,
            "official_pdf_sha256": "dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38",
            "edition_content_commit": args.commit,
        },
        "preservation": {
            "zenodo_version_doi": args.zenodo_doi,
            "zenodo_concept_doi": "10.5281/zenodo.22059759",
            "figshare_doi": args.figshare_doi,
            "figshare_article_id": 33314766,
            "figshare_project_id": 280296,
            "figshare_collection_id": 8668413,
        },
        "rights": [
            {
                "component": "principal source text and Indonesian adaptation",
                "license": "CC BY 4.0",
            },
            {
                "component": "credited Lanzhou.png and credited AJbook.cls fragment",
                "license": "CC BY-SA 3.0",
            },
            {"component": "bundled Noto fonts", "license": "SIL OFL 1.1"},
        ],
        "files": [reader_entry, zip_entry, license_entry],
        "qa": {
            "reader_pages": 96,
            "source_unit_pages": 95,
            "source_to_merged_pages_compared": 95,
            "source_to_merged_pages_pixel_identical": 95,
            "all_pages_visually_inspected": True,
            "untagged_pdf_disclosed": True,
        },
    }
    (common / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sum_paths = [common / name for name in (READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME)]
    sums = "".join(f"{digest(path)['sha256']}  {path.name}\n" for path in sum_paths)
    (common / SUMS_NAME).write_text(sums, encoding="utf-8", newline="\n")

    common_names = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
    for name in common_names:
        shutil.copy2(common / name, figshare / name)
        shutil.copy2(common / name, zenodo / name)
    for name in UNIT_PDFS:
        shutil.copy2(ROOT / "artifacts" / name, zenodo / name)

    inventory = {
        "commit": args.commit,
        "common": [digest(common / name) for name in common_names],
        "figshare_payload_bytes": sum((figshare / name).stat().st_size for name in common_names),
        "zenodo": [digest(path) for path in sorted(zenodo.iterdir())],
        "zip_entries": len(zip_entries),
        "zip_expanded_bytes": zip_expanded_bytes,
    }
    (stage / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if inventory["figshare_payload_bytes"] > 500_000_000:
        raise SystemExit("Figshare work-level payload exceeds 500,000,000 bytes")
    print(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
