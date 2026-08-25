#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 027."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
UNIT_025 = ROOT / "build/unit-025-candidate/chapter4-group-basics-id.tex"
UNIT_026 = ROOT / "build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex"
UNIT_027 = ROOT / "build/unit-027-candidate/chapter4-products-group-extensions-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-027-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_027_candidate.py"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_025_ID = (20_464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a")
UNIT_026_ID = (19_424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87")
UNIT_027_ID = (12_675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563")
SOURCE_SLICE_ID = (10_209, "bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8")
SOURCE_SUFFIX_ID = (113_647, "c9d69fabd6720d01a02b52c11e995065b58b12851a40510dccf17ccec956d7f4")
TARGET_ID = (166_211, "5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420")
DELTA_ID = (1_959, "5a661682e425f53ed0bd25a3f1badd6cdc83b396946901573bcb0c7d8e1a977e")
GLOSSARY_ID = (60_575, "61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97")
CANDIDATE_CHECKER_ID = (14_054, "a98d407c23ce2ae28f3fbe1776387c96b9d2cc4db6c987e089227fbc92fd556e")

SOURCE_START, SOURCE_END = 365, 517
TARGET_START, TARGET_END = 366, 517

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-027 candidate admission",
        "authority=chapter4.tex:365-517",
        "authority_slice_records=153",
        "authority_slice_bytes=10209",
        "authority_slice_sha256=bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8",
        "candidate_records=152",
        "candidate_bytes=12675",
        "candidate_sha256=aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563",
        "environment_markers=56",
        "labels=8",
        "refs_eqrefs=5",
        "citations=0",
        "indexes=6",
        "protected_math_zones=171",
        "han_residue=0",
        "declared_source_corrections=2",
        "translation_precision_repairs=1",
        "next_boundary=chapter4.tex:518",
        "",
    )
)


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 027 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def strict(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    require(not data.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {path}")
    require(b"\r" not in data, f"CR/CRLF detected: {path}")
    try:
        return data, data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(f"strict UTF-8 decode failed for {path}: {exc}")


def main() -> None:
    authority, authority_text = strict(AUTHORITY)
    unit_025, unit_025_text = strict(UNIT_025)
    unit_026, unit_026_text = strict(UNIT_026)
    unit_027, unit_027_text = strict(UNIT_027)
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()

    for got, expected, label in (
        (identity(authority), AUTHORITY_ID, "authority"),
        (identity(unit_025), UNIT_025_ID, "Unit 025 prefix"),
        (identity(unit_026), UNIT_026_ID, "Unit 026 prefix"),
        (identity(unit_027), UNIT_027_ID, "Unit 027 candidate"),
        (identity(target), TARGET_ID, "canonical Chapter 4"),
        (identity(glossary), GLOSSARY_ID, "controlled glossary"),
        (identity(delta), DELTA_ID, "terminology delta"),
        (identity(checker), CANDIDATE_CHECKER_ID, "candidate checker"),
    ):
        require(got == expected, f"{label} identity drifted: {got}")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    target_lines = target_text.splitlines()
    candidate_lines = unit_027_text.splitlines()
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(target_lines) == 1_898, "target line topology drifted")
    require(len(candidate_lines) == 152, "candidate line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target lacks exactly one final LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_END:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 365-517 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 517 is not blank")
    require(authority_lines[SOURCE_END].startswith(r"\section{"), "authority line 518 is not the next section")
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 518 drifted")

    expected_target = unit_025 + unit_026 + unit_027 + source_suffix + b"\n"
    require(target == expected_target, "canonical target is not exact admitted prefix plus authority suffix")
    require(target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines,
            "canonical target lines 366-517 differ from Unit 027")
    require(target_lines[TARGET_END].startswith(r"\section{"), "target line 518 is not untranslated Section 4.4")

    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 383 and len(delta_rows) == 9, "glossary/delta row counts drifted")
    require(glossary_rows[-9:] == delta_rows, "controlled glossary tail differs from Unit 027 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    require(all(row["target_term"] in unit_027_text for row in delta_rows),
            "not every Unit 027 target term occurs in the candidate")

    first = subprocess.run(
        [sys.executable, str(CANDIDATE_CHECKER)], cwd=ROOT,
        text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    second = subprocess.run(
        [sys.executable, str(CANDIDATE_CHECKER)], cwd=ROOT,
        text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    require(first.returncode == second.returncode == 0, "candidate checker failed")
    require(first.stderr == second.stderr == "", "candidate checker emitted stderr")
    require(first.stdout == second.stdout == EXPECTED_CANDIDATE_OUTPUT,
            "candidate checker output drifted or was nondeterministic")

    print("UNIT 027 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={UNIT_027_ID[0]}")
    print(f"canonical_span_sha256={UNIT_027_ID[1]}")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")


if __name__ == "__main__":
    main()
