#!/usr/bin/env python3
"""Build the compact reader-first Zenodo/Figshare checkpoint 0.5.0 payload."""

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
VERSION = "0.5.0"
RELEASE_DATE = "2026-08-24"
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-0.5.0-reader.pdf"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.5.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

ARCHIVE_BASE_PATHS = [
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
]
QA_TEXT_SUFFIXES = {".json", ".log", ".md", ".txt"}


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "name": path.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def pdf_facts(path: Path) -> dict[str, object]:
    reader = PdfReader(str(path))
    root = reader.trailer["/Root"]
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
        "language": str(root.get("/Lang", "")),
        "tagged_pdf": "/StructTreeRoot" in root,
        "named_destinations": len(reader.named_destinations),
        "goto_actions": goto,
        "uri_actions": uri,
        "widgets": widgets,
        "javascript_actions": javascript,
        "launch_actions": launch,
        "gotor_actions": gotor,
    }


def qa_text_paths(commit: str) -> list[str]:
    raw = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "-z", commit, "--", "qa"],
        cwd=ROOT,
    )
    paths = [item.decode("utf-8") for item in raw.split(b"\0") if item]
    return sorted(path for path in paths if Path(path).suffix.lower() in QA_TEXT_SUFFIXES)


def git_archive(commit: str, output: Path) -> list[str]:
    paths = ARCHIVE_BASE_PATHS + qa_text_paths(commit)
    command = [
        "git",
        "archive",
        "--format=zip",
        f"--output={output}",
        commit,
        "--",
        *paths,
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True, help="published checkpoint receipt commit")
    parser.add_argument("--zenodo-concept-doi", default="10.5281/zenodo.22059759")
    parser.add_argument("--zenodo-version-doi", default="10.5281/zenodo.22071178")
    parser.add_argument("--figshare-article-doi", default="10.6084/m9.figshare.33314766.v3")
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    stage = args.output_directory.resolve()
    if stage.exists() and any(stage.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty release stage: {stage}")
    common, zenodo, figshare = (stage / name for name in ("common", "zenodo", "figshare"))
    for directory in (common, zenodo, figshare):
        directory.mkdir(parents=True, exist_ok=True)

    reader_source = ROOT / "output" / "pdf" / READER_NAME
    facts = pdf_facts(reader_source)
    if facts != {
        "pages": 183,
        "language": "id-ID",
        "tagged_pdf": False,
        "named_destinations": 585,
        "goto_actions": 329,
        "uri_actions": 69,
        "widgets": 0,
        "javascript_actions": 0,
        "launch_actions": 0,
        "gotor_actions": 0,
    }:
        raise SystemExit(f"Checkpoint PDF facts drifted: {facts}")

    shutil.copy2(reader_source, common / READER_NAME)
    shutil.copy2(ROOT / "LICENSES.md", common / LICENSE_NAME)
    archived_paths = git_archive(args.commit, common / ZIP_NAME)

    with zipfile.ZipFile(common / ZIP_NAME) as archive:
        members = [entry for entry in archive.infolist() if not entry.is_dir()]
        expanded_bytes = sum(entry.file_size for entry in members)
        corrupt = archive.testzip()
        if corrupt is not None:
            raise SystemExit(f"Corrupt ZIP member: {corrupt}")

    reader_entry = digest(common / READER_NAME)
    reader_entry.update({"role": "primary_reader", **facts})
    zip_entry = digest(common / ZIP_NAME)
    zip_entry.update(
        {
            "role": "compact_resumable_source_backend",
            "entries": len(members),
            "expanded_bytes": expanded_bytes,
            "archive_pathspec_count": len(archived_paths),
            "excludes_bulk_render_images": True,
        }
    )
    license_entry = digest(common / LICENSE_NAME)
    license_entry["role"] = "controlling_component_rights_notice"

    manifest = {
        "schema": "metode-aljabar-checkpoint/v3",
        "release_date": RELEASE_DATE,
        "version": VERSION,
        "work": {
            "title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Edisi Bahasa Indonesia",
            "source_title": "Methods of Algebra, Volume 1",
            "source_author": "Wen-Wei Li",
            "language": "id-ID",
            "status": "partial_public_active",
            "coverage": (
                "Pendahuluan lengkap; Bab 1 lengkap; Bab 2 lengkap termasuk latihan "
                "dalam Unit 001-018. Bab 3-10, OCW Etingof, asesmennya, dan span CRing "
                "terpilih belum disertakan."
            ),
            "independent_nonendorsed": True,
            "model": MODEL,
        },
        "authority": {
            "source_repository": "https://github.com/wenweili/AlJabr-1",
            "source_commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "source_tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "official_pdf_pages": 445,
            "official_pdf_sha256": "dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38",
            "edition_receipt_commit": args.commit,
            "checkpoint_content_commit": "1c3479a8fdf8c23c2f72789db2bbc969a4b9b639",
        },
        "preservation": {
            "zenodo_concept_doi": args.zenodo_concept_doi,
            "zenodo_version_doi": args.zenodo_version_doi,
            "figshare_article_lineage_doi": args.figshare_article_doi,
            "figshare_article_id": 33314766,
            "figshare_project_id": 280296,
            "figshare_collection_id": 8668413,
        },
        "rights": [
            {"component": "principal source text and Indonesian adaptation", "license": "CC BY 4.0"},
            {"component": "credited Lanzhou.png and credited AJbook.cls fragment", "license": "CC BY-SA 3.0"},
            {"component": "bundled Noto fonts", "license": "SIL OFL 1.1"},
        ],
        "files": [reader_entry, zip_entry, license_entry],
        "qa": {
            "reader_pages": 183,
            "source_unit_pages": 182,
            "source_to_merged_pages_compared": 182,
            "source_to_merged_pages_pixel_identical": 182,
            "all_pages_visually_inspected": True,
            "named_destinations": 585,
            "links": 398,
            "embedded_font_objects": 446,
            "untagged_pdf_disclosed": True,
            "github_public_byte_readback": True,
        },
    }
    (common / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    sum_paths = [common / name for name in (READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME)]
    (common / SUMS_NAME).write_text(
        "".join(f"{digest(path)['sha256']}  {path.name}\n" for path in sum_paths),
        encoding="utf-8",
        newline="\n",
    )

    common_names = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
    for name in common_names:
        shutil.copy2(common / name, figshare / name)
        shutil.copy2(common / name, zenodo / name)

    inventory = {
        "commit": args.commit,
        "common": [digest(common / name) for name in common_names],
        "figshare_payload_bytes": sum((figshare / name).stat().st_size for name in common_names),
        "zenodo_payload_bytes": sum((zenodo / name).stat().st_size for name in common_names),
        "zenodo": [digest(path) for path in sorted(zenodo.iterdir())],
        "zip_entries": len(members),
        "zip_expanded_bytes": expanded_bytes,
        "bulk_render_images_in_source_zip": False,
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
