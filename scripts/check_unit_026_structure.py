#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 026."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter4.tex"
)
UNIT_025 = ROOT / "build" / "unit-025-candidate" / "chapter4-group-basics-id.tex"
UNIT_026 = ROOT / "build" / "unit-026-candidate" / "chapter4-homomorphisms-quotients-id.tex"
TARGET = ROOT / "repo" / "source" / "chapter4.tex"
GLOSSARY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build" / "unit-026-staging" / "terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts" / "check_unit_026_candidate.py"

AUTHORITY_ID = (
    154_744,
    "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3",
)
UNIT_025_ID = (
    20_464,
    "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a",
)
UNIT_026_ID = (
    19_424,
    "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87",
)
SOURCE_SLICE_ID = (
    15_360,
    "4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8",
)
SOURCE_SUFFIX_ID = (
    123_856,
    "377766774741a5a3e13776bf59c09780b18ee6dd08c42bdd6282335847a060f1",
)
TARGET_ID = (
    163_745,
    "fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463",
)
OLD_GLOSSARY_ID = (
    51_472,
    "3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1",
)
DELTA_ID = (
    7_238,
    "29da42f631cb8290e54335142e589c71939040e6f874a0e7f026b9d70caad408",
)
GLOSSARY_ID = (
    58_658,
    "5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17",
)
CANDIDATE_CHECKER_ID = (
    13_906,
    "42d3c8b669ac12ff5b29eb458c33123a04ad29e27f94acb2048d1cc72e0e92b5",
)

SOURCE_START = 177
SOURCE_END = 364
SOURCE_SUFFIX_START = 365
UNIT_025_TARGET_END = 178
UNIT_026_TARGET_START = 179
UNIT_026_TARGET_END = 365

GLOSSARY_HEADER = "source_term,target_term,status,scope,note"
DELTA_HEADER = '"source_term","target_term","status","scope","note"'

EXPECTED_DELTA_TERMS = {
    "semigroup homomorphism": "homomorfisme semigrup",
    "identity map": "peta identitas",
    "trivial homomorphism": "homomorfisme trivial",
    "inverse": "invers",
    "isomorphic": "isomorfik",
    "automorphism group": "grup automorfisme",
    "group homomorphism": "homomorfisme grup",
    "group isomorphism": "isomorfisme grup",
    "group automorphism": "automorfisme grup",
    "inner automorphism": "automorfisme dalam",
    "adjoint automorphism": "automorfisme adjoin",
    "image of a homomorphism": "bayangan homomorfisme",
    "kernel": "kernel",
    "quotient map": "peta hasil bagi",
    "well-defined": "terdefinisi dengan baik",
    "quotient structure": "struktur hasil bagi",
    "quotient monoid": "monoid hasil bagi",
    "induced homomorphism": "homomorfisme terimbas",
    "surjective": "surjektif",
    "quotient group": "grup hasil bagi",
    "quotient homomorphism": "homomorfisme hasil bagi",
    "coset space": "ruang koset",
    "surjectivity": "surjektivitas",
    "inclusion relation": "relasi pencakupan",
    "generator": "pembangkit",
    "cyclic subgroup": "subgrup siklik",
    "congruence": "kongruensi",
    "commutative monoid": "monoid komutatif",
    "monoid homomorphism": "homomorfisme monoid",
    "Grothendieck group": "grup Grothendieck",
    "cancellation law": "hukum pembatalan",
    "additive inverse": "invers aditif",
    "U-category": "kategori-U",
}

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-026 candidate admission",
        "authority=chapter4.tex:177-364",
        "authority_slice_records=188",
        "authority_slice_bytes=15360",
        "authority_slice_sha256=4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8",
        "candidate_records=187",
        "candidate_bytes=19424",
        "candidate_sha256=a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87",
        "environments=72",
        "labels=12",
        "refs_eqrefs=24",
        "citations=1",
        "indexes=10",
        "han_residue=0",
        "declared_source_corrections=4",
        "",
    )
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(data: bytes) -> tuple[int, str]:
    return len(data), digest(data)


def fail(message: str) -> None:
    print(f"UNIT 026 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def strict_utf8(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    require(not data.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {path}")
    require(b"\r" not in data, f"CR/CRLF detected: {path}")
    try:
        return data, data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(f"strict UTF-8 decode failed for {path}: {exc}")


def rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(text.splitlines()))


def main() -> None:
    authority, authority_text = strict_utf8(AUTHORITY)
    unit_025, unit_025_text = strict_utf8(UNIT_025)
    unit_026, unit_026_text = strict_utf8(UNIT_026)
    target, target_text = strict_utf8(TARGET)
    glossary, glossary_text = strict_utf8(GLOSSARY)
    delta, delta_text = strict_utf8(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "frozen authority identity drifted")
    require(identity(unit_025) == UNIT_025_ID, "Unit 025 prefix identity drifted")
    require(identity(unit_026) == UNIT_026_ID, "Unit 026 candidate identity drifted")
    require(identity(target) == TARGET_ID, "canonical Chapter 4 identity drifted")
    require(identity(glossary) == GLOSSARY_ID, "controlled glossary identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    require(identity(checker) == CANDIDATE_CHECKER_ID, "candidate checker identity drifted")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    unit_025_lines = unit_025_text.splitlines()
    unit_026_lines = unit_026_text.splitlines()
    target_lines = target_text.splitlines()

    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(unit_025_lines) == UNIT_025_TARGET_END, "Unit 025 target-line count drifted")
    require(len(unit_026_lines) == 187, "Unit 026 target-line count drifted")
    require(len(target_lines) == 1_899, "canonical target-line topology drifted")
    require(unit_025.endswith(b"\n") and not unit_025.endswith(b"\n\n"),
            "Unit 025 prefix lacks exactly one terminal LF")
    require(unit_026.endswith(b"\n") and not unit_026.endswith(b"\n\n"),
            "Unit 026 candidate lacks exactly one terminal LF")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"),
            "canonical target lacks exactly one terminal LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_SUFFIX_START - 1 :])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 177-364 drifted")
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 365 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 364 is no longer blank")
    require(authority_lines[SOURCE_SUFFIX_START - 1].startswith(r"\section{"),
            "authority line 365 is no longer the next section boundary")

    expected_target = unit_025 + unit_026 + source_suffix + b"\n"
    require(identity(expected_target) == TARGET_ID, "computed canonical identity drifted")
    require(target == expected_target,
            "canonical target is not exact Unit 025 + Unit 026 + authority suffix + LF")
    require(target_lines[:UNIT_025_TARGET_END] == unit_025_lines,
            "canonical target lines 1-178 differ from Unit 025")
    require(
        target_lines[UNIT_026_TARGET_START - 1 : UNIT_026_TARGET_END] == unit_026_lines,
        "canonical target lines 179-365 differ from Unit 026",
    )
    require(
        target_lines[UNIT_026_TARGET_END] == authority_lines[SOURCE_SUFFIX_START - 1],
        "authority source line 365 does not resume at canonical target line 366",
    )
    require(target_lines[178].startswith(r"\section{Homomorfisme dan grup hasil bagi}"),
            "Unit 026 opening section drifted from target line 179")

    glossary_lines = glossary.splitlines(keepends=True)
    delta_lines = delta.splitlines(keepends=True)
    require(len(glossary_lines) == 375, "controlled glossary physical-row count drifted")
    require(len(delta_lines) == 34, "terminology delta physical-row count drifted")
    require(
        glossary_lines[0].decode("utf-8").strip() == GLOSSARY_HEADER,
        "glossary header drifted",
    )
    require(delta_lines[0].decode("utf-8").strip() == DELTA_HEADER, "delta header drifted")

    old_glossary = b"".join(glossary_lines[:342])
    appended_delta = b"".join(delta_lines[1:])
    require(identity(old_glossary) == OLD_GLOSSARY_ID, "341-row glossary baseline drifted")
    require(glossary == old_glossary + appended_delta,
            "controlled glossary is not the exact baseline plus 33 delta rows")

    glossary_rows = rows(glossary_text)
    delta_rows = rows(delta_text)
    require(len(glossary_rows) == 374, "controlled glossary data-row count drifted")
    require(len(delta_rows) == 33, "terminology delta data-row count drifted")
    glossary_by_source = {row["source_term"]: row for row in glossary_rows}
    delta_by_source = {row["source_term"]: row for row in delta_rows}
    require(len(glossary_by_source) == len(glossary_rows),
            "controlled glossary contains duplicate source terms")
    require(len(delta_by_source) == len(delta_rows),
            "terminology delta contains duplicate source terms")
    require(
        {term: row["target_term"] for term, row in delta_by_source.items()}
        == EXPECTED_DELTA_TERMS,
        "the pinned set of 33 Unit 026 term mappings drifted",
    )
    for source_term, delta_row in delta_by_source.items():
        require(glossary_by_source.get(source_term) == delta_row,
                f"delta row not reproduced exactly in controlled glossary: {source_term}")
        require(
            delta_row["status"] == "admitted"
            and bool(delta_row["scope"])
            and bool(delta_row["note"]),
            f"incomplete admitted terminology metadata: {source_term}",
        )

    candidate_runs: list[subprocess.CompletedProcess[str]] = []
    for run_number in (1, 2):
        result = subprocess.run(
            [sys.executable, str(CANDIDATE_CHECKER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )
        candidate_runs.append(result)
        require(result.returncode == 0, f"candidate checker run {run_number} failed")
        require(result.stderr == "", f"candidate checker run {run_number} wrote stderr")
        require(result.stdout == EXPECTED_CANDIDATE_OUTPUT,
                f"candidate checker run {run_number} output drifted")
    require(candidate_runs[0].stdout == candidate_runs[1].stdout,
            "candidate checker outputs are not deterministic")

    print("UNIT 026 STRUCTURE CHECK: PASS")
    print(f"authority_bytes={len(authority)}")
    print(f"authority_sha256={digest(authority)}")
    print(f"authority_slice_bytes={len(source_slice)}")
    print(f"authority_slice_sha256={digest(source_slice)}")
    print(f"unit025_prefix_bytes={len(unit_025)}")
    print(f"unit025_prefix_sha256={digest(unit_025)}")
    print(f"unit026_candidate_bytes={len(unit_026)}")
    print(f"unit026_candidate_sha256={digest(unit_026)}")
    print(f"authority_suffix_bytes={len(source_suffix)}")
    print(f"authority_suffix_sha256={digest(source_suffix)}")
    print(f"target_bytes={len(target)}")
    print(f"target_sha256={digest(target)}")
    print("target_mapping=unit025:1-178;unit026:179-365;authority365:366")
    print(f"glossary_bytes={len(glossary)}")
    print(f"glossary_sha256={digest(glossary)}")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"delta_terms_verified={len(delta_rows)}")
    print("candidate_checker_runs=2")
    print(f"candidate_checker_output_sha256={digest(EXPECTED_CANDIDATE_OUTPUT.encode('utf-8'))}")


if __name__ == "__main__":
    main()
