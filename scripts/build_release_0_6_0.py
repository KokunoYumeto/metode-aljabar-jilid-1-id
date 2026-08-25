#!/usr/bin/env python3
"""Build the fail-closed reader-first checkpoint 0.6.0 release payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.6.0"
RELEASE_DATE = "2026-08-25"
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf"
READER_REL = f"output/pdf/{READER_NAME}"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.6.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
QA_REL = "qa/checkpoint-0.6.0-evidence/structure-text-navigation-font-render-qa.json"
VISUAL_REL = "qa/checkpoint-0.6.0-evidence/VISUAL_REVIEW.md"
GITHUB_READBACK_REL = "qa/PUBLICATION_GITHUB_CHECKPOINT_0.6.0_CONTENT_READBACK.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CONCEPT_DOI = "10.5281/zenodo.22059759"

EXPECTED_UNIT_FILES = [
    "unit-001-pendahuluan.pdf",
    "unit-002-bab-1-zfc.pdf",
    "unit-003-bab-1-struktur-urutan-dan-ordinal.pdf",
    "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf",
    "unit-005-bab-1-kardinal.pdf",
    "unit-006-bab-1-semesta-grothendieck.pdf",
    "unit-007-bab-1-latihan.pdf",
    "unit-008-bab-2-pengantar-teori-kategori.pdf",
    "unit-009-bab-2-kategori-dan-morfisme.pdf",
    "unit-010-bab-2-fungtor-dan-transformasi-natural.pdf",
    "unit-011-bab-2-kategori-fungtor.pdf",
    "unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf",
    "unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf",
    "unit-014-bab-2-fungtor-adjoin-dasar.pdf",
    "unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf",
    "unit-016-bab-2-limit.pdf",
    "unit-017-bab-2-kelengkapan.pdf",
    "unit-018-bab-2-latihan.pdf",
    "unit-019-bab-3-definisi-dasar.pdf",
    "unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf",
    "unit-021-bab-3-struktur-kepang.pdf",
    "unit-022-bab-3-kategori-diperkaya-dan-aditif.pdf",
    "unit-023-bab-3-sekilas-tentang-2-kategori.pdf",
    "unit-024-bab-3-latihan-kategori-monoidal.pdf",
]
EXPECTED_UNIT_STARTS = [
    2, 23, 35, 46, 54, 66, 75, 79, 84, 97, 112, 119,
    129, 136, 145, 155, 171, 180, 184, 196, 201, 210, 219, 226,
]
EXPECTED_READER_PAGES = 229
EXPECTED_SOURCE_PAGES = 228

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
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
DOI = re.compile(r"10\.5281/zenodo\.\d+\Z")


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(path: Path) -> dict[str, object]:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"Could not read valid JSON from {path}: {error}")
    if not isinstance(value, dict):
        fail(f"Expected a JSON object in {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def safe_repo_path(value: str) -> str:
    path = PurePosixPath(value)
    require(
        value == path.as_posix()
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value,
        f"Unsafe repository path: {value!r}",
    )
    return value


def git_output(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def verify_commit(commit: str) -> None:
    require(bool(HEX40.fullmatch(commit)), f"Commit must be a full lowercase SHA-1: {commit}")
    resolved = git_output("rev-parse", "--verify", f"{commit}^{{commit}}").decode("ascii").strip()
    require(resolved == commit, f"Commit did not resolve exactly: {resolved} != {commit}")


def committed_blob(commit: str, path: str) -> bytes:
    safe_repo_path(path)
    try:
        return git_output("cat-file", "blob", f"{commit}:{path}")
    except subprocess.CalledProcessError as error:
        fail(f"Required committed blob is absent at {commit}:{path}: {error}")


def pdf_facts(path: Path) -> dict[str, object]:
    try:
        reader = PdfReader(str(path), strict=True)
        root = reader.trailer["/Root"]
        named_destinations = len(reader.named_destinations)
    except Exception as error:
        fail(f"Strict PDF parse failed for {path}: {error}")

    annotation_subtypes: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    widgets = 0
    for page_number, page in enumerate(reader.pages, start=1):
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            subtype = str(annotation.get("/Subtype", ""))
            annotation_subtypes[subtype] += 1
            widgets += subtype == "/Widget"
            action_ref = annotation.get("/A")
            if action_ref:
                action = action_ref.get_object()
                actions[str(action.get("/S", ""))] += 1
            elif annotation.get("/Dest") is not None:
                actions["/GoTo"] += 1

    unsafe = sum(actions[kind] for kind in ("/JavaScript", "/Launch", "/GoToR"))
    return {
        "pages": len(reader.pages),
        "language": str(root.get("/Lang", "")),
        "tagged_pdf": "/StructTreeRoot" in root,
        "named_destinations": named_destinations,
        "annotation_subtypes": dict(sorted(annotation_subtypes.items())),
        "actions": dict(sorted(actions.items())),
        "widgets": widgets,
        "unsafe_actions": unsafe,
        "open_action": root.get("/OpenAction") is not None,
        "acroform": root.get("/AcroForm") is not None,
    }


def validate_qa(reader_path: Path, qa_path: Path) -> tuple[dict[str, Any], dict[str, object]]:
    qa = load_json(qa_path)
    require(qa.get("status") == "PASS", "Checkpoint QA status is not PASS")
    require(qa.get("deterministic_rebuild") is True, "Deterministic rebuild did not pass")
    require(qa.get("unit_start_pages_1_based") == EXPECTED_UNIT_STARTS, "Unit starts drifted")

    artifact = qa.get("artifact")
    require(isinstance(artifact, dict), "Checkpoint QA lacks artifact identity")
    actual_digest = digest(reader_path)
    require(artifact.get("path") == READER_REL, f"Unexpected QA artifact path: {artifact.get('path')}")
    require(artifact.get("pages") == EXPECTED_READER_PAGES, "Checkpoint page count drifted")
    require(artifact.get("bytes") == actual_digest["bytes"], "Checkpoint bytes differ from QA")
    require(artifact.get("sha256") == actual_digest["sha256"], "Checkpoint SHA-256 differs from QA")

    source_units = qa.get("source_units")
    require(isinstance(source_units, list), "Checkpoint QA lacks source_units")
    require(
        [item.get("filename") for item in source_units if isinstance(item, dict)]
        == EXPECTED_UNIT_FILES,
        "Checkpoint QA source-unit inventory or order drifted",
    )
    require(sum(int(item.get("pages", -1)) for item in source_units) == EXPECTED_SOURCE_PAGES,
            "Source-unit page total drifted")
    for item in source_units:
        require(isinstance(item, dict), "Malformed source-unit QA entry")
        unit_path = ROOT / "artifacts" / str(item["filename"])
        require(unit_path.is_file(), f"Missing admitted source unit: {unit_path}")
        unit_digest = digest(unit_path)
        require(unit_digest["bytes"] == item.get("bytes"), f"Unit bytes drifted: {unit_path.name}")
        require(unit_digest["sha256"] == item.get("sha256"), f"Unit hash drifted: {unit_path.name}")
        try:
            pages = len(PdfReader(str(unit_path), strict=True).pages)
        except Exception as error:
            fail(f"Strict PDF parse failed for {unit_path}: {error}")
        require(pages == item.get("pages"), f"Unit page count drifted: {unit_path.name}")

    identity = qa.get("source_content_stream_identity", {})
    require(identity.get("pages_checked") == EXPECTED_SOURCE_PAGES, "Content-stream coverage drifted")
    require(identity.get("mismatches") == 0, "Content-stream comparison has mismatches")

    render = qa.get("render_qa", {})
    require(render.get("checkpoint_pages_rendered") == EXPECTED_READER_PAGES,
            "Primary-renderer checkpoint coverage drifted")
    require(render.get("secondary_renderer_pages") == EXPECTED_READER_PAGES,
            "Secondary-renderer checkpoint coverage drifted")
    require(render.get("source_unit_pages_rendered") == EXPECTED_SOURCE_PAGES,
            "Source-unit render coverage drifted")
    require(render.get("source_to_checkpoint_pixel_identical_pages") == EXPECTED_SOURCE_PAGES,
            "Not every source page is pixel-identical in the checkpoint")
    require(render.get("raster_mismatches") == 0, "Raster mismatches are present")
    visual = render.get("visual_review", {})
    require(visual.get("status") == "PASS", "All-page visual review is not PASS")
    require(visual.get("path") == VISUAL_REL, "Visual-review path drifted")
    visual_path = ROOT / VISUAL_REL
    require(visual_path.is_file(), f"Missing visual-review receipt: {visual_path}")
    visual_digest = digest(visual_path)
    require(visual.get("bytes") == visual_digest["bytes"], "Visual-review bytes drifted")
    require(visual.get("sha256") == visual_digest["sha256"], "Visual-review hash drifted")

    structure = qa.get("structure", {})
    require(structure.get("language") == "id-ID", "QA language is not id-ID")
    require(structure.get("broken_named_links") == [], "Broken named links are present")
    require(structure.get("unsafe_actions") == [], "Unsafe PDF actions are present")
    require(structure.get("additional_actions") == 0, "Additional PDF actions are present")
    require(structure.get("open_action") is False, "PDF OpenAction is present")
    require(structure.get("acroform") is False, "Unexpected AcroForm is present")
    require(len(structure.get("top_level_outline_titles", [])) == 25,
            "Expected cover plus 24 top-level unit outlines")

    fonts = qa.get("fonts", {})
    require(fonts.get("unembedded") == 0, "Unembedded fonts are present")
    require(fonts.get("embedded") == fonts.get("unique_font_objects"), "Font embedding census drifted")
    text = qa.get("text", {})
    require(text.get("missing_cover_phrases") == [], "Required cover phrases are missing")
    require(text.get("legacy_status_block_label_absent") is True,
            "Legacy ambiguous cover status block reappeared")
    require(text.get("creator_metadata") == MODEL, "Exact model provenance drifted")

    coverage = str(qa.get("coverage", ""))
    for phrase in ("Bab 1 lengkap", "Bab 2 lengkap", "Bab 3 lengkap", "24 unit"):
        require(phrase in coverage, f"QA coverage lacks required phrase: {phrase}")

    facts = pdf_facts(reader_path)
    require(facts["pages"] == EXPECTED_READER_PAGES, "Strict PDF page count drifted")
    require(facts["language"] == "id-ID", "PDF /Lang is not id-ID")
    require(facts["named_destinations"] == structure.get("named_destinations"),
            "Named-destination census differs from QA")
    require(facts["annotation_subtypes"] == structure.get("annotation_subtypes"),
            "Annotation census differs from QA")
    require(facts["actions"] == structure.get("actions"), "Action census differs from QA")
    require(facts["widgets"] == 0 and facts["unsafe_actions"] == 0,
            "Interactive or unsafe PDF actions are present")
    require(facts["open_action"] is False and facts["acroform"] is False,
            "Unexpected PDF open action or form is present")
    return qa, facts


def validate_github_readback(
    path: Path,
    checkpoint_commit: str,
    reader_entry: dict[str, object],
) -> dict[str, Any]:
    readback = load_json(path)
    require(readback.get("schema_version") == "2.0.0", "Unexpected GitHub readback schema")
    require(readback.get("commit") == checkpoint_commit, "GitHub readback commit drifted")
    require(readback.get("public_branch_head") == checkpoint_commit,
            "GitHub readback did not verify the checkpoint as public branch head")
    require(readback.get("anonymous") is True, "GitHub readback was not anonymous")
    require(readback.get("authorization_header_used") is False,
            "GitHub readback reports an authorization header")
    require(readback.get("all_match") is True, "GitHub public-byte readback did not pass")
    records = readback.get("records")
    require(isinstance(records, list) and records, "GitHub readback has no path records")
    require(readback.get("path_count") == len(records), "GitHub readback path count drifted")
    require(readback.get("total_bytes") == sum(int(item.get("bytes", -1)) for item in records),
            "GitHub readback byte total drifted")
    by_path = {item.get("path"): item for item in records if isinstance(item, dict)}
    require(len(by_path) == len(records), "GitHub readback paths are malformed or duplicated")
    require(READER_REL in by_path, "GitHub readback omits the checkpoint reader")
    public_reader = by_path[READER_REL]
    require(public_reader.get("matches_committed_blob") is True,
            "GitHub reader did not match its committed blob")
    require(public_reader.get("http_status") == 200, "GitHub reader readback was not HTTP 200")
    require(public_reader.get("bytes") == reader_entry["bytes"], "GitHub reader bytes drifted")
    require(public_reader.get("sha256") == reader_entry["sha256"], "GitHub reader hash drifted")
    return readback


def qa_text_paths(commit: str) -> list[str]:
    raw = git_output("ls-tree", "-r", "--name-only", "-z", commit, "--", "qa")
    paths = [item.decode("utf-8") for item in raw.split(b"\0") if item]
    return sorted(
        safe_repo_path(path)
        for path in paths
        if Path(path).suffix.lower() in QA_TEXT_SUFFIXES
    )


def git_archive(commit: str, output: Path) -> list[str]:
    paths = ARCHIVE_BASE_PATHS + qa_text_paths(commit)
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={output}", commit, "--", *paths],
        cwd=ROOT,
        check=True,
    )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition-commit", required=True, help="commit archived in the source/backend ZIP")
    parser.add_argument("--checkpoint-content-commit", required=True,
                        help="immutable commit that first publishes the 0.6.0 reader and QA")
    parser.add_argument("--zenodo-concept-doi", default=CONCEPT_DOI)
    parser.add_argument("--zenodo-version-doi", required=True,
                        help="DOI reserved by the existing-concept 0.6.0 version draft")
    parser.add_argument("--figshare-article-doi", default="10.6084/m9.figshare.33314766.v3")
    parser.add_argument("--github-readback", type=Path, default=ROOT / GITHUB_READBACK_REL,
                        help="anonymous immutable-commit readback JSON emitted by the 0.6.0 verifier")
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    require(args.zenodo_concept_doi == CONCEPT_DOI,
            f"Refusing a competing Zenodo concept: {args.zenodo_concept_doi}")
    require(bool(DOI.fullmatch(args.zenodo_version_doi)),
            f"Malformed Zenodo version DOI: {args.zenodo_version_doi}")
    require(args.zenodo_version_doi != CONCEPT_DOI, "Version DOI cannot equal the concept DOI")
    verify_commit(args.edition_commit)
    verify_commit(args.checkpoint_content_commit)
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", args.checkpoint_content_commit, args.edition_commit],
        cwd=ROOT,
        check=False,
    )
    require(ancestor.returncode == 0, "Checkpoint content commit is not an ancestor of edition commit")

    reader_source = ROOT / READER_REL
    qa_path = ROOT / QA_REL
    require(reader_source.is_file(), f"Missing checkpoint reader: {reader_source}")
    require(qa_path.is_file(), f"Missing checkpoint QA record: {qa_path}")
    qa, facts = validate_qa(reader_source, qa_path)
    reader_bytes = reader_source.read_bytes()
    require(committed_blob(args.checkpoint_content_commit, READER_REL) == reader_bytes,
            "Checkpoint content commit does not contain the validated reader bytes")
    require(committed_blob(args.edition_commit, READER_REL) == reader_bytes,
            "Edition commit does not contain the validated reader bytes")
    for evidence_rel in (QA_REL, VISUAL_REL):
        evidence_bytes = (ROOT / evidence_rel).read_bytes()
        require(committed_blob(args.checkpoint_content_commit, evidence_rel) == evidence_bytes,
                f"Checkpoint content commit does not contain validated evidence: {evidence_rel}")
        require(committed_blob(args.edition_commit, evidence_rel) == evidence_bytes,
                f"Edition commit does not contain validated evidence: {evidence_rel}")
    reader_identity = digest(reader_source)
    github_readback_path = (
        args.github_readback.resolve()
        if args.github_readback.is_absolute()
        else (ROOT / args.github_readback).resolve()
    )
    try:
        github_readback_path.relative_to(ROOT)
    except ValueError:
        fail(f"GitHub readback must remain inside the edition repository: {github_readback_path}")
    require(github_readback_path.is_file(), f"Missing GitHub readback: {github_readback_path}")
    validate_github_readback(github_readback_path, args.checkpoint_content_commit, reader_identity)
    github_readback_rel = github_readback_path.relative_to(ROOT).as_posix()
    require(committed_blob(args.edition_commit, github_readback_rel) == github_readback_path.read_bytes(),
            "Edition commit does not contain the validated GitHub readback")
    for script_rel in (
        "scripts/build_release_0_6_0.py",
        "scripts/publish_zenodo_0_6_0.py",
        "scripts/verify_checkpoint_0_6_0_github_readback.py",
    ):
        require(committed_blob(args.edition_commit, script_rel) == (ROOT / script_rel).read_bytes(),
                f"Edition commit does not contain the live release script: {script_rel}")

    stage = args.output_directory.resolve()
    if stage.exists() and not stage.is_dir():
        fail(f"Release stage exists but is not a directory: {stage}")
    if stage.exists() and any(stage.iterdir()):
        fail(f"Refusing to overwrite non-empty release stage: {stage}")
    common, zenodo, figshare = (stage / name for name in ("common", "zenodo", "figshare"))
    for directory in (common, zenodo, figshare):
        directory.mkdir(parents=True, exist_ok=True)

    shutil.copy2(reader_source, common / READER_NAME)
    shutil.copy2(ROOT / "LICENSES.md", common / LICENSE_NAME)
    archived_paths = git_archive(args.edition_commit, common / ZIP_NAME)
    with zipfile.ZipFile(common / ZIP_NAME) as archive:
        members = [entry for entry in archive.infolist() if not entry.is_dir()]
        require(bool(members), "Source/backend ZIP is empty")
        require(archive.testzip() is None, "Source/backend ZIP has a corrupt member")
        for entry in members:
            member = PurePosixPath(entry.filename)
            require(not member.is_absolute() and ".." not in member.parts,
                    f"Unsafe ZIP member: {entry.filename}")
        expanded_bytes = sum(entry.file_size for entry in members)

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
    qa_entry = digest(qa_path)
    qa_entry.update({"path": QA_REL, "role": "checkpoint_machine_qa"})
    visual_entry = digest(ROOT / VISUAL_REL)
    visual_entry.update({"path": VISUAL_REL, "role": "all_page_visual_review"})
    github_entry = digest(github_readback_path)
    github_entry.update(
        {
            "path": github_readback_path.relative_to(ROOT).as_posix(),
            "role": "anonymous_github_public_byte_readback",
        }
    )

    structure = qa["structure"]
    render = qa["render_qa"]
    fonts = qa["fonts"]
    coverage = (
        "Pendahuluan lengkap; Bab 1 lengkap; Bab 2 lengkap; Bab 3 lengkap termasuk "
        "latihan dalam Unit 001-024. Bab 4-10 Li, komponen representasi Duncan, "
        "enam span CRing, dan lapisan konektif/penguasaan belum disertakan."
    )
    manifest = {
        "schema": "metode-aljabar-checkpoint/v4",
        "release_date": RELEASE_DATE,
        "version": VERSION,
        "work": {
            "title": "Metode Aljabar, Jilid 1: Arsitektur Dasar - Edisi Bahasa Indonesia",
            "source_title": "Methods in Algebra, Volume 1",
            "source_author": "Wen-Wei Li",
            "language": "id-ID",
            "status": "partial_public_active",
            "coverage": coverage,
            "independent_nonendorsed": True,
            "model": MODEL,
        },
        "authority": {
            "source_repository": "https://github.com/wenweili/AlJabr-1",
            "source_commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
            "source_tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "official_pdf_pages": 445,
            "official_pdf_sha256": "dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38",
            "edition_receipt_commit": args.edition_commit,
            "checkpoint_content_commit": args.checkpoint_content_commit,
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
        "evidence": [qa_entry, visual_entry, github_entry],
        "qa": {
            "reader_pages": EXPECTED_READER_PAGES,
            "source_units": len(EXPECTED_UNIT_FILES),
            "source_unit_pages": EXPECTED_SOURCE_PAGES,
            "source_to_merged_pages_compared": qa["source_content_stream_identity"]["pages_checked"],
            "source_to_merged_pages_pixel_identical": render["source_to_checkpoint_pixel_identical_pages"],
            "all_pages_visually_inspected": True,
            "named_destinations": structure["named_destinations"],
            "links": sum(structure["annotation_subtypes"].values()),
            "embedded_font_objects": fonts["embedded"],
            "untagged_pdf_disclosed": not bool(facts["tagged_pdf"]),
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
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in sum_paths),
        encoding="utf-8",
        newline="\n",
    )

    common_names = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
    for name in common_names:
        shutil.copy2(common / name, figshare / name)
        shutil.copy2(common / name, zenodo / name)

    inventory = {
        "version": VERSION,
        "edition_commit": args.edition_commit,
        "checkpoint_content_commit": args.checkpoint_content_commit,
        "common": [digest(common / name) for name in common_names],
        "figshare_payload_bytes": sum((figshare / name).stat().st_size for name in common_names),
        "zenodo_payload_bytes": sum((zenodo / name).stat().st_size for name in common_names),
        "zenodo": [digest(path) for path in sorted(zenodo.iterdir())],
        "zip_entries": len(members),
        "zip_expanded_bytes": expanded_bytes,
        "bulk_render_images_in_source_zip": False,
        "qa_record": qa_entry,
        "visual_receipt": visual_entry,
        "github_public_readback": github_entry,
    }
    (stage / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    require(inventory["figshare_payload_bytes"] <= 500_000_000,
            "Figshare work-level payload exceeds 500,000,000 bytes")
    print(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
