#!/usr/bin/env python3
"""Build or validate the reader-first Zenodo 0.7.0 preservation payload.

Preparation and commit-bound modes are intentionally non-publishable.  They prove the payload shape,
reader identity, component-rights notice, compact source/backend archive, and cap
without inventing Git or Zenodo identities.  Commit-bound mode binds immutable
commits and public evidence while leaving only the new-version DOI/draft pending.
Final mode also binds the DOI reserved by a new-version draft in the existing
Zenodo concept.
"""

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
from typing import Any, Iterable

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.0"
RELEASE_DATE = "2026-08-28"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
MANIFEST_TITLE = TITLE.replace("—", "-")
CONCEPT_DOI = "10.5281/zenodo.22059759"
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-through-bab-5-reader.pdf"
READER_REL = f"output/pdf/{READER_NAME}"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.7.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
EXPECTED_NAMES = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
BUILD_EVIDENCE_REL = "qa/unit-043-evidence/checkpoint-through-bab-5-build.json"
BACKEND_EVIDENCE_REL = "qa/unit-043-evidence/backend-validation.json"
PENDING_COMMIT = "PENDING_GIT_COMMIT"
PENDING_DOI = "PENDING_ZENODO_VERSION_DOI"
EXPECTED_PAGES = 385
EXPECTED_COMPONENTS = 36
EXPECTED_SOURCE_PAGES = 384
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
DOI = re.compile(r"10\.5281/zenodo\.(\d+)\Z")

RIGHTS = [
    {
        "component": "principal source text and Indonesian adaptation",
        "license": "CC BY 4.0",
    },
    {
        "component": "Lanzhou.png",
        "license": "CC BY-SA 3.0",
    },
    {
        "component": "credited AJbook.cls DeclareSourcemap fragment",
        "license": "CC BY-SA 3.0",
    },
    {
        "component": "bundled Noto fonts",
        "license": "SIL OFL 1.1",
    },
    {
        "component": "Fandol 0.3 fonts",
        "license": "GPLv3 with Fandol font exception",
    },
]

ARCHIVE_ROOTS = [
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
    "qa",
]
QA_TEXT_SUFFIXES = {".json", ".md", ".txt"}
GENERATED_SUFFIXES = {
    ".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls", ".ilg",
    ".ind", ".idx", ".log", ".out", ".pdf", ".run.xml", ".synctex.gz",
    ".toc", ".xdv",
}
FIXED_ZIP_TIME = (2026, 8, 28, 0, 0, 0)


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def digest(path: Path) -> dict[str, object]:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"Could not read valid JSON from {path}: {error}")
    require(isinstance(value, dict), f"Expected a JSON object in {path}")
    return value


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
        fail(f"Missing committed blob {commit}:{path}: {error}")


def pdf_facts(path: Path) -> dict[str, object]:
    try:
        reader = PdfReader(str(path), strict=True)
        root = reader.trailer["/Root"]
    except Exception as error:
        fail(f"Strict PDF parse failed for {path}: {error}")
    annotations: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    widgets = 0
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            subtype = str(annotation.get("/Subtype", ""))
            annotations[subtype] += 1
            widgets += subtype == "/Widget"
            action_ref = annotation.get("/A")
            if action_ref:
                action = action_ref.get_object()
                actions[str(action.get("/S", ""))] += 1
            elif annotation.get("/Dest") is not None:
                actions["/GoTo"] += 1
    unsafe = sum(actions[item] for item in ("/JavaScript", "/Launch", "/GoToR"))
    return {
        "pages": len(reader.pages),
        "language": str(root.get("/Lang", "")),
        "tagged_pdf": "/StructTreeRoot" in root,
        "named_destinations": len(reader.named_destinations),
        "annotation_subtypes": dict(sorted(annotations.items())),
        "actions": dict(sorted(actions.items())),
        "widgets": widgets,
        "unsafe_actions": unsafe,
        "open_action": root.get("/OpenAction") is not None,
        "acroform": root.get("/AcroForm") is not None,
        "title": str((reader.metadata or {}).get("/Title", "")),
        "author": str((reader.metadata or {}).get("/Author", "")),
        "creator": str((reader.metadata or {}).get("/Creator", "")),
    }


def evidence_entry(path: Path, role: str) -> dict[str, object]:
    require(path.is_file(), f"Missing evidence: {path}")
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        fail(f"Evidence must remain inside the repository: {path}")
    result = digest(path)
    result.update({"path": relative, "role": role})
    result.pop("name", None)
    return result


def validate_reader_and_base_evidence() -> tuple[dict[str, object], list[dict[str, object]]]:
    reader_path = ROOT / READER_REL
    build_path = ROOT / BUILD_EVIDENCE_REL
    backend_path = ROOT / BACKEND_EVIDENCE_REL
    require(reader_path.is_file(), f"Missing Chapter 5 reader: {reader_path}")
    build = load_json(build_path)
    backend = load_json(backend_path)
    reader_identity = digest(reader_path)
    facts = pdf_facts(reader_path)

    require(build.get("schema") == "o013-checkpoint-through-chapter-5-build-v1",
            "Unexpected Chapter 5 reader-build schema")
    require(build.get("result") == "pass", "Chapter 5 reader build did not pass")
    require(build.get("component_count") == EXPECTED_COMPONENTS,
            "Chapter 5 component count drifted")
    inputs = build.get("inputs")
    require(isinstance(inputs, list) and len(inputs) == EXPECTED_COMPONENTS,
            "Chapter 5 build receipt lacks the exact input inventory")
    require(sum(int(item.get("pages", -1)) for item in inputs if isinstance(item, dict))
            == EXPECTED_SOURCE_PAGES, "Chapter 5 source-page total drifted")
    output = build.get("output")
    require(isinstance(output, dict), "Chapter 5 build receipt lacks output identity")
    require(output.get("path") == READER_REL, "Chapter 5 reader path drifted")
    require(output.get("pages") == EXPECTED_PAGES, "Build receipt page count drifted")
    require(output.get("bytes") == reader_identity["bytes"], "Build receipt byte count drifted")
    require(output.get("sha256") == reader_identity["sha256"], "Build receipt hash drifted")

    require(backend.get("schema") == "o013-unit-backend-validation-v1",
            "Unexpected Unit 043 backend-validation schema")
    require(backend.get("unit") == "O013-LI-U043" and backend.get("result") == "pass",
            "Unit 043 backend validation did not pass")
    require(backend.get("rights_components") == 5,
            "Unit 043 backend does not bind five component-rights records")
    require(backend.get("build_surfaces") == 2,
            "Unit 043 backend does not bind both build surfaces")

    require(facts["pages"] == EXPECTED_PAGES, "Strict PDF page count drifted")
    require(facts["language"] == "id-ID", "Reader /Lang is not id-ID")
    require(facts["widgets"] == 0 and facts["unsafe_actions"] == 0,
            "Reader contains widgets or unsafe actions")
    require(facts["open_action"] is False and facts["acroform"] is False,
            "Reader contains an unexpected OpenAction or AcroForm")
    require(facts["author"] == "Wen-Wei Li", "Reader author metadata drifted")
    require(facts["creator"] in {MODEL, MODEL + "."}, "Reader model provenance drifted")
    reader_identity.update({"role": "primary_reader", **facts})
    return reader_identity, [
        evidence_entry(build_path, "checkpoint_build"),
        evidence_entry(backend_path, "unit_043_backend_validation"),
    ]


def generated_or_bulk(path: str) -> bool:
    normalized = path.lower()
    if normalized.startswith("qa/") and Path(normalized).suffix not in QA_TEXT_SUFFIXES:
        return True
    return any(normalized.endswith(suffix) for suffix in GENERATED_SUFFIXES)


def working_tree_paths() -> list[str]:
    result: set[str] = set()
    for item in ARCHIVE_ROOTS:
        source = ROOT / item
        if source.is_file():
            result.add(PurePosixPath(item).as_posix())
            continue
        require(source.is_dir(), f"Missing archive root: {source}")
        for path in source.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            if not generated_or_bulk(relative):
                result.add(safe_repo_path(relative))
    return sorted(result)


def committed_paths(commit: str) -> list[str]:
    raw = git_output("ls-tree", "-r", "--name-only", "-z", commit, "--", *ARCHIVE_ROOTS)
    return sorted(
        safe_repo_path(item.decode("utf-8"))
        for item in raw.split(b"\0")
        if item and not generated_or_bulk(item.decode("utf-8"))
    )


def write_deterministic_zip(
    destination: Path,
    paths: Iterable[str],
    *,
    commit: str | None,
) -> tuple[int, int, int]:
    entries = list(paths)
    require(entries, "Source/backend archive inventory is empty")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in entries:
            data = committed_blob(commit, relative) if commit else (ROOT / relative).read_bytes()
            info = zipfile.ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, data)
    with zipfile.ZipFile(destination) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        require(archive.testzip() is None, "Source/backend ZIP contains a corrupt member")
        require([item.filename for item in members] == entries,
                "Source/backend ZIP inventory/order drifted")
        for item in members:
            member = PurePosixPath(item.filename)
            require(not member.is_absolute() and ".." not in member.parts,
                    f"Unsafe ZIP member: {item.filename}")
        expanded = sum(item.file_size for item in members)
    return len(members), expanded, len(entries)


def validate_final_evidence(path: Path, reader_identity: dict[str, object], role: str) -> None:
    if path.suffix.lower() == ".json":
        data = load_json(path)
        require(
            data.get("result") == "pass"
            or data.get("status") == "PASS"
            or data.get("all_match") is True,
            f"{role} does not record a passing result",
        )
        serialized = json.dumps(data, ensure_ascii=False)
        require(str(reader_identity["sha256"]) in serialized,
                f"{role} does not bind the Chapter 5 reader SHA-256")
    else:
        text = path.read_text(encoding="utf-8")
        require("PASS" in text.upper(), f"{role} does not record PASS")
        if role == "all_page_visual_review":
            require(READER_REL in text and str(EXPECTED_PAGES) in text,
                    f"{role} does not bind the Chapter 5 reader path/page count")
        else:
            require(str(reader_identity["sha256"]) in text,
                    f"{role} does not bind the Chapter 5 reader SHA-256")


def checksum_map(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"Malformed SHA256SUMS line: {line!r}")
        checksum, name = match.groups()
        require(name not in result, f"Duplicate SHA256SUMS entry: {name}")
        result[name] = checksum
    return result


def validate_stage(stage: Path, *, allow_preparation: bool) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    zenodo = stage / "zenodo"
    require(zenodo.is_dir(), f"Missing Zenodo payload directory: {zenodo}")
    files = sorted(item for item in zenodo.iterdir() if item.is_file())
    require([item.name for item in files] == EXPECTED_NAMES,
            f"Unexpected Zenodo inventory: {[item.name for item in files]}")
    require(not any(item.is_dir() for item in zenodo.iterdir()),
            "Zenodo payload contains an unexpected directory")
    expected = {item.name: digest(item) for item in files}
    total = sum(int(item["bytes"]) for item in expected.values())
    require(total <= 500_000_000, "Zenodo payload exceeds 500,000,000 bytes")

    manifest = load_json(zenodo / MANIFEST_NAME)
    require(manifest.get("schema") == "metode-aljabar-checkpoint/v5",
            "Unexpected 0.7.0 manifest schema")
    require(manifest.get("version") == VERSION and manifest.get("release_date") == RELEASE_DATE,
            "Manifest version/date drifted")
    require(manifest.get("work", {}).get("title") == MANIFEST_TITLE,
            "Manifest work title drifted")
    require(manifest.get("work", {}).get("model") == MODEL,
            "Manifest model provenance drifted")
    require(manifest.get("work", {}).get("status") == "partial_public_active",
            "Manifest status drifted")
    coverage = str(manifest.get("work", {}).get("coverage", ""))
    for phrase in ("Bab 1-5 lengkap", "Unit 001-043", "Bab 6-10", "Duncan", "CRing"):
        require(phrase in coverage, f"Manifest coverage lacks {phrase!r}")
    require("TTP" not in json.dumps(manifest.get("work", {}), ensure_ascii=False),
            "Organization label leaked into work metadata")
    require(manifest.get("rights") == RIGHTS, "Manifest five-component rights drifted")
    require(manifest.get("preservation", {}).get("zenodo_concept_doi") == CONCEPT_DOI,
            "Manifest points to a competing Zenodo concept")

    ready = manifest.get("publication_ready") is True
    mode = str(manifest.get("preparation", {}).get("mode", ""))
    require(mode in {"prepare", "bound", "final"}, "Unknown release-stage mode")
    if not allow_preparation:
        require(ready, "Preparation stage is not publishable")
    authority = manifest.get("authority", {})
    version_doi = str(manifest.get("preservation", {}).get("zenodo_version_doi", ""))
    if ready:
        require(mode == "final", "Only final mode may be publication-ready")
        require(bool(HEX40.fullmatch(str(authority.get("edition_receipt_commit", "")))),
                "Final manifest lacks a full edition commit")
        require(bool(HEX40.fullmatch(str(authority.get("checkpoint_content_commit", "")))),
                "Final manifest lacks a full checkpoint content commit")
        require(DOI.fullmatch(version_doi) is not None and version_doi != CONCEPT_DOI,
                "Final manifest lacks a reserved version DOI")
    elif mode == "prepare":
        require(authority.get("edition_receipt_commit") == PENDING_COMMIT,
                "Preparation manifest invents an edition commit")
        require(authority.get("checkpoint_content_commit") == PENDING_COMMIT,
                "Preparation manifest invents a checkpoint commit")
        require(version_doi == PENDING_DOI,
                "Preparation manifest invents a Zenodo version DOI")
    else:
        require(mode == "bound", "Non-ready stage is neither prepare nor bound")
        require(bool(HEX40.fullmatch(str(authority.get("edition_receipt_commit", "")))),
                "Commit-bound manifest lacks a full edition commit")
        require(bool(HEX40.fullmatch(str(authority.get("checkpoint_content_commit", "")))),
                "Commit-bound manifest lacks a full checkpoint content commit")
        require(version_doi == PENDING_DOI,
                "Commit-bound manifest invents a Zenodo version DOI")

    manifest_files = manifest.get("files")
    require(isinstance(manifest_files, list) and len(manifest_files) == 3,
            "Manifest must describe reader, source/backend ZIP, and license")
    by_name = {item.get("name"): item for item in manifest_files if isinstance(item, dict)}
    require(set(by_name) == {READER_NAME, ZIP_NAME, LICENSE_NAME},
            "Manifest file inventory drifted")
    for name in by_name:
        require(by_name[name].get("bytes") == expected[name]["bytes"],
                f"Manifest byte count drifted for {name}")
        require(by_name[name].get("sha256") == expected[name]["sha256"],
                f"Manifest hash drifted for {name}")
    require(by_name[READER_NAME].get("role") == "primary_reader",
            "Reader is not the primary manifest file")
    require(by_name[READER_NAME].get("pages") == EXPECTED_PAGES,
            "Manifest reader page count drifted")
    require(by_name[READER_NAME].get("widgets") == 0
            and by_name[READER_NAME].get("unsafe_actions") == 0,
            "Manifest reader safety facts drifted")
    require(by_name[LICENSE_NAME].get("role") == "controlling_component_rights_notice",
            "License is not the controlling rights notice")

    license_text = (zenodo / LICENSE_NAME).read_text(encoding="utf-8")
    for phrase in (
        "Wen-Wei Li", "Creative Commons Attribution 4.0 International",
        "Lanzhou.png", "AJbook.cls", "CC BY-SA 3.0", "SIL Open Font License 1.1",
        "Fandol 0.3", "GPL versi 3", "pengecualian font",
        "GPL-3.0-with-Fandol-font-exception.txt", "FANDOL-AUTHORITY.json",
        "independen serta tidak disahkan",
    ):
        require(phrase in license_text, f"License notice lacks required phrase: {phrase}")
    require("TTP" not in license_text, "Organization label leaked into license prose")

    with zipfile.ZipFile(zenodo / ZIP_NAME) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        require(bool(members) and archive.testzip() is None,
                "Source/backend ZIP is empty or corrupt")
        for item in members:
            member = PurePosixPath(item.filename)
            require(not member.is_absolute() and ".." not in member.parts,
                    f"Unsafe ZIP member: {item.filename}")

    sums = checksum_map(zenodo / SUMS_NAME)
    require(set(sums) == {READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME},
            "SHA256SUMS inventory drifted")
    for name, checksum in sums.items():
        require(checksum == expected[name]["sha256"], f"SHA256SUMS drifted for {name}")

    inventory = load_json(stage / "inventory.json")
    require(inventory.get("version") == VERSION, "Inventory version drifted")
    require(inventory.get("publication_ready") is ready,
            "Inventory/manifest publication state differs")
    require(inventory.get("zenodo_payload_bytes") == total,
            "Inventory payload byte total drifted")
    return manifest, expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("prepare", "bound", "final"), default="prepare")
    parser.add_argument("--edition-commit", default=PENDING_COMMIT)
    parser.add_argument("--checkpoint-content-commit", default=PENDING_COMMIT)
    parser.add_argument("--zenodo-concept-doi", default=CONCEPT_DOI)
    parser.add_argument("--zenodo-version-doi", default=PENDING_DOI)
    parser.add_argument("--checkpoint-qa", type=Path)
    parser.add_argument("--visual-review", type=Path)
    parser.add_argument("--github-readback", type=Path)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()

    require(args.zenodo_concept_doi == CONCEPT_DOI,
            f"Refusing a competing Zenodo concept: {args.zenodo_concept_doi}")
    final = args.mode == "final"
    commit_bound = args.mode in {"bound", "final"}
    reader_entry, evidence = validate_reader_and_base_evidence()

    optional = [
        (args.checkpoint_qa, "checkpoint_machine_qa"),
        (args.visual_review, "all_page_visual_review"),
        (args.github_readback, "anonymous_github_public_byte_readback"),
    ]
    if commit_bound:
        require(all(path is not None for path, _ in optional),
                "Commit-bound/final mode requires --checkpoint-qa, --visual-review, and --github-readback")
        verify_commit(args.edition_commit)
        verify_commit(args.checkpoint_content_commit)
        require(subprocess.run(
            ["git", "merge-base", "--is-ancestor", args.checkpoint_content_commit,
             args.edition_commit], cwd=ROOT, check=False
        ).returncode == 0, "Checkpoint content commit is not an ancestor of edition commit")
        if final:
            require(DOI.fullmatch(args.zenodo_version_doi) is not None
                    and args.zenodo_version_doi != CONCEPT_DOI,
                    "Final mode requires a valid reserved Zenodo version DOI")
        else:
            require(args.zenodo_version_doi == PENDING_DOI,
                    "Commit-bound mode must leave the Zenodo version DOI pending")
        require(committed_blob(args.checkpoint_content_commit, READER_REL)
                == (ROOT / READER_REL).read_bytes(),
                "Checkpoint content commit does not contain the validated reader bytes")
        require(committed_blob(args.edition_commit, READER_REL)
                == (ROOT / READER_REL).read_bytes(),
                "Edition commit does not contain the validated reader bytes")
    else:
        require(args.edition_commit == PENDING_COMMIT
                and args.checkpoint_content_commit == PENDING_COMMIT,
                "Preparation mode must not assert Git identities")
        require(args.zenodo_version_doi == PENDING_DOI,
                "Preparation mode must not assert a Zenodo version DOI")

    for path, role in optional:
        if path is None:
            continue
        resolved = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
        validate_final_evidence(resolved, reader_entry, role)
        evidence.append(evidence_entry(resolved, role))
        if commit_bound:
            relative = resolved.relative_to(ROOT).as_posix()
            require(committed_blob(args.edition_commit, relative) == resolved.read_bytes(),
                    f"Edition commit does not contain the validated {role}")

    if commit_bound:
        roles = {item["role"] for item in evidence}
        require({
            "checkpoint_machine_qa", "all_page_visual_review",
            "anonymous_github_public_byte_readback",
        }.issubset(roles), "Final evidence role inventory is incomplete")

    stage = args.output_directory.resolve()
    if stage.exists() and not stage.is_dir():
        fail(f"Release stage exists but is not a directory: {stage}")
    if stage.exists() and any(stage.iterdir()):
        fail(f"Refusing to overwrite non-empty release stage: {stage}")
    zenodo = stage / "zenodo"
    zenodo.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ROOT / READER_REL, zenodo / READER_NAME)
    shutil.copy2(ROOT / "LICENSES.md", zenodo / LICENSE_NAME)
    archive_paths = committed_paths(args.edition_commit) if commit_bound else working_tree_paths()
    zip_count, zip_expanded, path_count = write_deterministic_zip(
        zenodo / ZIP_NAME, archive_paths, commit=args.edition_commit if commit_bound else None
    )

    reader_file = digest(zenodo / READER_NAME)
    reader_file.update({key: value for key, value in reader_entry.items() if key != "name"})
    zip_file = digest(zenodo / ZIP_NAME)
    zip_file.update({
        "role": "compact_resumable_source_backend",
        "entries": zip_count,
        "expanded_bytes": zip_expanded,
        "archive_pathspec_count": path_count,
        "archive_authority": "immutable_edition_commit" if commit_bound else "working_tree_preview",
        "excludes_bulk_renders_and_generated_build_files": True,
    })
    license_file = digest(zenodo / LICENSE_NAME)
    license_file["role"] = "controlling_component_rights_notice"
    coverage = (
        "Pendahuluan dan Bab 1-5 lengkap dalam Unit 001-043 (36 komponen pembaca). "
        "Bab 6-10 Li, komponen teori representasi Duncan, enam span CRing, dan "
        "lapisan konektif/penguasaan belum disertakan."
    )
    if final:
        required_final_inputs = []
    elif commit_bound:
        required_final_inputs = ["reserved_zenodo_version_doi_and_matching_draft_id"]
    else:
        required_final_inputs = [
            "edition_receipt_commit",
            "checkpoint_content_commit",
            "checkpoint_machine_qa_path",
            "all_page_visual_review_path",
            "anonymous_github_public_byte_readback_path",
            "reserved_zenodo_version_doi_and_matching_draft_id",
        ]
    manifest = {
        "schema": "metode-aljabar-checkpoint/v5",
        "release_date": RELEASE_DATE,
        "version": VERSION,
        "publication_ready": final,
        "preparation": {
            "mode": args.mode,
            "required_final_inputs": required_final_inputs,
            "warning": None if final else (
                "Commit/evidence-bound proof; reserve the existing-concept new-version DOI and rebuild in final mode before upload."
                if commit_bound else
                "Preparation proof only; rebuild in bound or final mode before any upload."
            ),
        },
        "work": {
            "title": MANIFEST_TITLE,
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
            "official_pdf_sha256": (
                "dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38"
            ),
            "edition_receipt_commit": args.edition_commit,
            "checkpoint_content_commit": args.checkpoint_content_commit,
        },
        "preservation": {
            "zenodo_concept_doi": CONCEPT_DOI,
            "zenodo_version_doi": args.zenodo_version_doi,
        },
        "rights": RIGHTS,
        "files": [reader_file, zip_file, license_file],
        "evidence": evidence,
        "qa": {
            "reader_pages": EXPECTED_PAGES,
            "reader_components": EXPECTED_COMPONENTS,
            "source_component_pages": EXPECTED_SOURCE_PAGES,
            "reader_strict_parse": True,
            "language": "id-ID",
            "widgets": 0,
            "unsafe_actions": 0,
            "untagged_pdf_disclosed": not bool(reader_entry["tagged_pdf"]),
            "chapter_5_backend_validation": "pass",
            "github_public_byte_readback": commit_bound,
        },
    }
    require("TTP" not in json.dumps(manifest["work"], ensure_ascii=False),
            "Organization label leaked into work metadata")
    (zenodo / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    sum_paths = [zenodo / name for name in (READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME)]
    (zenodo / SUMS_NAME).write_text(
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in sum_paths),
        encoding="utf-8", newline="\n",
    )
    payload = [digest(zenodo / name) for name in EXPECTED_NAMES]
    total_bytes = sum(int(item["bytes"]) for item in payload)
    inventory = {
        "schema": "metode-aljabar-release-inventory/v5",
        "version": VERSION,
        "mode": args.mode,
        "publication_ready": final,
        "edition_commit": args.edition_commit,
        "checkpoint_content_commit": args.checkpoint_content_commit,
        "zenodo_concept_doi": CONCEPT_DOI,
        "zenodo_version_doi": args.zenodo_version_doi,
        "zenodo": payload,
        "zenodo_payload_bytes": total_bytes,
        "payload_cap_bytes": 500_000_000,
        "under_cap": total_bytes <= 500_000_000,
        "zip_entries": zip_count,
        "zip_expanded_bytes": zip_expanded,
        "source_archive_authority": zip_file["archive_authority"],
        "required_final_inputs": required_final_inputs,
    }
    (stage / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    validate_stage(stage, allow_preparation=not final)
    print(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
