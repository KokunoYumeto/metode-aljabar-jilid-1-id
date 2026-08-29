#!/usr/bin/env python3
"""Build the reader-first Zenodo 1.0.0 payload for complete Li Volume 1."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any, Iterable

from pypdf import PdfReader

import build_release_0_8_0 as base
import build_release_0_7_0 as foundation


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
RELEASE_DATE = "2026-08-29"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
CONCEPT_DOI = "10.5281/zenodo.22059759"
READER_NAME = "00-metode-aljabar-jilid-1-id-lengkap.pdf"
READER_REL = "artifacts/metode-aljabar-jilid-1-id-lengkap.pdf"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-1.0.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
EXPECTED_NAMES = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
ADMISSION_REL = "qa/LI_COMPLETE_ADMISSION_20260829.md"
FREEZE_REL = "qa/LI_COMPLETE_TRANSLATION_FREEZE.json"
EXPECTED_PAGES = 521
EXPECTED_COMPONENTS = 11
EXPECTED_SOURCE_PAGES = 445
EXPECTED_READER_BYTES = 2_875_853
EXPECTED_READER_SHA256 = "c2994530e3da1711d44f8c36315c40874e87f1968d1a81c1432105de2251c2ee"
ARCHIVE_ROOTS = [
    ".gitattributes",
    "README.md",
    "LICENSES.md",
    "00_control/BUILD_BASELINE.md",
    "00_control/CURRENT_CURSOR.json",
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md",
    "00_control/CURRENT_STATE.md",
    "00_control/RIGHTS_COMPONENTS.csv",
    "00_control/SOURCE_AUTHORITY.md",
    "00_control/SOURCE_MANIFEST.csv",
    "00_control/SOURCE_SELECTION.md",
    "00_control/TERMINOLOGY.id-ID.csv",
    "backend",
    "repo",
    "scripts/build_li_complete.ps1",
    "scripts/build_release_1_0_0.py",
    "scripts/check_li_complete_translation.py",
    "scripts/generate_li_final_chapters_backend.py",
    "scripts/publish_zenodo_1_0_0.py",
    "scripts/reserve_zenodo_1_0_0.py",
    "scripts/validate_backend.py",
    "scripts/verify_github_commit_readback.py",
    "scripts/verify_zenodo_1_0_0_readback.py",
    "scripts/write_li_complete_freeze.py",
    "scripts/write_li_final_admission.py",
    "qa/LI_COMPLETE_ADMISSION_20260829.md",
    "qa/LI_COMPLETE_TRANSLATION_FREEZE.json",
    "qa/LI_COMPLETE_VISUAL_QA_20260829.json",
    "qa/PUBLICATION_GITHUB_LI_COMPLETE_CONTENT_READBACK.json",
    "qa/li-complete-evidence/unit-045-backend-validation.json",
    "qa/li-complete-evidence/unit-046-backend-validation.json",
    "qa/li-complete-evidence/unit-047-backend-validation.json",
    "qa/li-complete-evidence/unit-048-backend-validation.json",
]
ORIGINAL_WRITE_DETERMINISTIC_ZIP = foundation.write_deterministic_zip


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def committed_archive_roots(commit: str) -> list[str]:
    """Return the intentionally small, reproducible release pathspec."""
    for relative in ARCHIVE_ROOTS:
        probe = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}:{relative}"],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        require(probe.returncode == 0, f"missing committed release path: {relative}")
    return list(ARCHIVE_ROOTS)


def write_release_zip(
    destination: Path,
    paths: Iterable[str],
    *,
    commit: str | None,
) -> tuple[int, int, int]:
    """Use one Git archive transaction instead of one process per blob."""
    entries = list(paths)
    if commit is None:
        return ORIGINAL_WRITE_DETERMINISTIC_ZIP(destination, entries, commit=None)
    require(entries == ARCHIVE_ROOTS, "release archive pathspec drifted")
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={destination}", commit, "--", *entries],
        cwd=ROOT,
        check=True,
    )
    with zipfile.ZipFile(destination) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        require(bool(members) and archive.testzip() is None, "release ZIP is empty or corrupt")
        for item in members:
            member = PurePosixPath(item.filename)
            require(not member.is_absolute() and ".." not in member.parts,
                    f"unsafe ZIP member: {item.filename}")
        expanded = sum(item.file_size for item in members)
    return len(members), expanded, len(entries)


def validate_reader_and_base_evidence() -> tuple[dict[str, object], list[dict[str, object]]]:
    reader_path = ROOT / READER_REL
    admission_path = ROOT / ADMISSION_REL
    freeze_path = ROOT / FREEZE_REL
    require(reader_path.is_file(), f"missing complete Li reader: {reader_path}")
    require(admission_path.is_file(), f"missing complete Li admission: {admission_path}")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    require(freeze.get("schema") == "o013.li-complete-translation-freeze.v1", "unexpected Li freeze schema")
    require(freeze.get("result") == "pass", "complete Li translation freeze did not pass")
    files = freeze.get("files")
    require(isinstance(files, list) and len(files) == 11, "complete Li source inventory drifted")
    aggregate = freeze.get("target_aggregate_topology", {})
    require(aggregate.get("top_level_exercises") == 161, "Li exercise closure drifted")
    require(aggregate.get("hints") == 51, "Li hint closure drifted")

    identity = foundation.digest(reader_path)
    require(identity["bytes"] == EXPECTED_READER_BYTES, "complete reader byte count drifted")
    require(identity["sha256"] == EXPECTED_READER_SHA256, "complete reader SHA-256 drifted")
    facts = foundation.pdf_facts(reader_path)
    require(facts["pages"] == EXPECTED_PAGES, "complete reader page count drifted")
    require(facts["language"] == "id-ID", "complete reader /Lang is not id-ID")
    require(facts["widgets"] == 0 and facts["unsafe_actions"] == 0, "complete reader contains unsafe actions")
    require(not facts["acroform"], "complete reader contains an AcroForm")
    require(facts["author"] == "Wen-Wei Li", "complete reader author metadata drifted")
    require("Metode Aljabar" in facts["title"], "complete reader title metadata drifted")
    admission = admission_path.read_text(encoding="utf-8")
    require("Result: **PASS" in admission and EXPECTED_READER_SHA256 in admission,
            "complete Li admission is not a passing hash-bound receipt")
    identity.update({"role": "primary_reader", **facts})

    evidence = [
        foundation.evidence_entry(admission_path, "complete_li_admission"),
        foundation.evidence_entry(freeze_path, "complete_li_translation_freeze"),
    ]
    for unit in range(45, 49):
        path = ROOT / f"qa/li-complete-evidence/unit-{unit:03d}-backend-validation.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        require(value.get("result") == "pass", f"Unit {unit:03d} backend did not pass")
        evidence.append(foundation.evidence_entry(path, f"unit_{unit:03d}_backend_validation"))
    return identity, evidence


def validate_stage(stage: Path, *, allow_preparation: bool) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    zenodo = stage / "zenodo"
    require(zenodo.is_dir(), f"missing Zenodo payload directory: {zenodo}")
    files = sorted(path for path in zenodo.iterdir() if path.is_file())
    require([path.name for path in files] == EXPECTED_NAMES,
            f"unexpected payload inventory: {[path.name for path in files]}")
    expected = {path.name: foundation.digest(path) for path in files}
    require(sum(int(item["bytes"]) for item in expected.values()) <= 500_000_000,
            "payload exceeds 500,000,000 bytes")
    manifest = json.loads((zenodo / MANIFEST_NAME).read_text(encoding="utf-8"))
    require(manifest.get("version") == VERSION and manifest.get("release_date") == RELEASE_DATE,
            "manifest version/date drifted")
    require(manifest.get("work", {}).get("title") == TITLE.replace("—", "-"), "manifest title drifted")
    require(manifest.get("work", {}).get("model") == MODEL, "model provenance drifted")
    require(manifest.get("preservation", {}).get("zenodo_concept_doi") == CONCEPT_DOI,
            "competing concept detected")
    require(manifest.get("rights") == foundation.RIGHTS, "component rights drifted")
    require("TTP" not in json.dumps(manifest.get("work", {}), ensure_ascii=False),
            "organization label leaked into work prose")
    ready = manifest.get("publication_ready") is True
    if not allow_preparation:
        require(ready, "stage is not publication-ready")
    if ready:
        doi = str(manifest.get("preservation", {}).get("zenodo_version_doi", ""))
        require(foundation.DOI.fullmatch(doi) is not None and doi != CONCEPT_DOI,
                "reserved version DOI is invalid")
    by_name = {item.get("name"): item for item in manifest.get("files", []) if isinstance(item, dict)}
    require(set(by_name) == {READER_NAME, ZIP_NAME, LICENSE_NAME}, "manifest file inventory drifted")
    for name, item in by_name.items():
        require(item.get("bytes") == expected[name]["bytes"] and item.get("sha256") == expected[name]["sha256"],
                f"manifest identity drifted: {name}")
    require(by_name[READER_NAME].get("role") == "primary_reader", "reader is not primary")
    require(by_name[READER_NAME].get("pages") == EXPECTED_PAGES, "reader page count drifted")
    with foundation.zipfile.ZipFile(zenodo / ZIP_NAME) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        require(bool(members) and archive.testzip() is None, "source/backend ZIP is empty or corrupt")
        for item in members:
            member = foundation.PurePosixPath(item.filename)
            require(not member.is_absolute() and ".." not in member.parts, f"unsafe ZIP member {item.filename}")
    sums = foundation.checksum_map(zenodo / SUMS_NAME)
    require(set(sums) == {READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME}, "checksum inventory drifted")
    for name, value in sums.items():
        require(value == expected[name]["sha256"], f"checksum drifted: {name}")
    return manifest, expected


def finalize_stage(stage: Path) -> dict[str, Any]:
    zenodo = stage / "zenodo"
    manifest_path = zenodo / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["work"]["status"] = "complete_public"
    manifest["work"]["coverage"] = (
        "Pendahuluan dan Bab 1-10 lengkap: seluruh Methods in Algebra, Volume 1 karya "
        "Wen-Wei Li dalam satu pembaca 521 halaman. Komponen O013 terpisah (Duncan, "
        "enam span CRing, serta lapisan konektif/penguasaan) bukan bagian dari edisi buku ini."
    )
    qa = manifest["qa"]
    qa.pop("chapter_5_backend_validation", None)
    qa["complete_li_translation_freeze"] = "pass"
    qa["complete_li_admission"] = "pass"
    qa["final_chapter_backends"] = {"unit_045": "pass", "unit_046": "pass", "unit_047": "pass", "unit_048": "pass"}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksum_paths = [zenodo / name for name in (READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME)]
    (zenodo / SUMS_NAME).write_text(
        "".join(f"{foundation.sha256_file(path)}  {path.name}\n" for path in checksum_paths),
        encoding="utf-8", newline="\n",
    )
    inventory_path = stage / "inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["zenodo"] = [foundation.digest(zenodo / name) for name in EXPECTED_NAMES]
    inventory["zenodo_payload_bytes"] = sum(int(item["bytes"]) for item in inventory["zenodo"])
    inventory["under_cap"] = inventory["zenodo_payload_bytes"] <= 500_000_000
    inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    final_manifest, _ = validate_stage(stage, allow_preparation=not bool(inventory.get("publication_ready")))
    coverage = final_manifest["work"]["coverage"]
    for phrase in ("Bab 1-10 lengkap", "521 halaman", "Duncan", "CRing"):
        require(phrase in coverage, f"coverage lacks {phrase!r}")
    require(final_manifest["work"]["status"] == "complete_public", "complete status drifted")
    return inventory


def configure() -> None:
    for name, value in {
        "VERSION": VERSION,
        "RELEASE_DATE": RELEASE_DATE,
        "MODEL": MODEL,
        "TITLE": TITLE,
        "CONCEPT_DOI": CONCEPT_DOI,
        "READER_NAME": READER_NAME,
        "READER_REL": READER_REL,
        "ZIP_NAME": ZIP_NAME,
        "LICENSE_NAME": LICENSE_NAME,
        "MANIFEST_NAME": MANIFEST_NAME,
        "SUMS_NAME": SUMS_NAME,
        "EXPECTED_NAMES": EXPECTED_NAMES,
        "BUILD_EVIDENCE_REL": ADMISSION_REL,
        "BACKEND_EVIDENCE_REL": FREEZE_REL,
        "EXPECTED_PAGES": EXPECTED_PAGES,
        "EXPECTED_COMPONENTS": EXPECTED_COMPONENTS,
        "EXPECTED_SOURCE_PAGES": EXPECTED_SOURCE_PAGES,
    }.items():
        setattr(base, name, value)
    base.validate_reader_and_base_evidence = validate_reader_and_base_evidence
    base.validate_stage = validate_stage
    base.finalize_stage = finalize_stage
    foundation.ARCHIVE_ROOTS = list(ARCHIVE_ROOTS)
    foundation.committed_paths = committed_archive_roots
    foundation.write_deterministic_zip = write_release_zip


def main() -> None:
    configure()
    base.main()


if __name__ == "__main__":
    main()
