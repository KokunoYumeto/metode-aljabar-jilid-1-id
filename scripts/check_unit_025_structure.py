#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 025."""

from __future__ import annotations

import csv
import hashlib
import re
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
CANDIDATE = ROOT / "build" / "unit-025-candidate" / "chapter4-group-basics-id.tex"
TARGET = ROOT / "repo" / "source" / "chapter4.tex"
GLOSSARY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

AUTHORITY_BYTES = 154_744
AUTHORITY_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_END_LINE = 176
SOURCE_SUFFIX_BYTES = 139_216
SOURCE_SUFFIX_SHA256 = "20e588a6d9f8361acad3deb3cdbfbb7e0d2a2495156c458bfe15897d21289b68"
CANDIDATE_BYTES = 20_464
CANDIDATE_SHA256 = "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a"
TARGET_BYTES = 159_681
TARGET_SHA256 = "b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419"
GLOSSARY_BYTES = 51_472
GLOSSARY_SHA256 = "3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1"

EXPECTED_TERMS = {
    "binary operation": "operasi biner",
    "semigroup": "semigrup",
    "monoid": "monoid",
    "submonoid": "submonoid",
    "identity element": "unsur identitas",
    "left cancellation law": "hukum pembatalan kiri",
    "right cancellation law": "hukum pembatalan kanan",
    "unit group": "grup unit",
    "subgroup": "subgrup",
    "normal subgroup": "subgrup normal",
    "simple group": "grup sederhana",
    "cyclic group": "grup siklik",
    "group order": "orde grup",
    "element order": "orde unsur",
    "coset": "koset",
    "left coset": "koset kiri",
    "right coset": "koset kanan",
    "double coset": "koset ganda",
    "center (group theory)": "pusat",
    "centralizer": "sentralisator",
    "normalizer": "normalisator",
    "symmetric group": "grup simetris",
    "alternating group": "grup selang-seling",
    "permutation group": "grup permutasi",
    "general linear group": "grup linear umum",
    "Lagrange's theorem": "teorema Lagrange",
}

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 025 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    authority = AUTHORITY.read_bytes()
    candidate = CANDIDATE.read_bytes()
    target = TARGET.read_bytes()
    glossary = GLOSSARY.read_bytes()

    require((len(authority), digest(authority)) == (AUTHORITY_BYTES, AUTHORITY_SHA256),
            "frozen authority identity drifted")
    require((len(candidate), digest(candidate)) == (CANDIDATE_BYTES, CANDIDATE_SHA256),
            "candidate identity drifted")
    require((len(target), digest(target)) == (TARGET_BYTES, TARGET_SHA256),
            "canonical target identity drifted")
    require((len(glossary), digest(glossary)) == (GLOSSARY_BYTES, GLOSSARY_SHA256),
            "controlled glossary identity drifted")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    suffix = b"".join(authority_lines[SOURCE_END_LINE:])
    require((len(suffix), digest(suffix)) == (SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256),
            "authority suffix identity drifted")
    require(target == candidate + suffix + b"\n",
            "target is not exact candidate + unchanged authority suffix + terminal LF")
    require(target.startswith(candidate), "candidate is not the exact canonical prefix")
    require(target[len(candidate):len(candidate) + len(suffix)] == suffix,
            "authority suffix changed during integration")
    require(target.endswith(b"\\end{Exercises}\n"), "canonical target lacks one terminal LF")

    candidate_text = candidate.decode("utf-8")
    require(not HAN_RE.search(candidate_text), "integrated Indonesian prefix contains Han residue")
    require("grup alternasi" not in candidate_text and "hukum kanselasi" not in candidate_text,
            "superseded terminology remains in the integrated prefix")
    require(candidate_text.lower().count("grup selang-seling") == 2,
            "alternating-group terminology occurrence count drifted")
    require(candidate_text.count("hukum pembatalan") == 4,
            "cancellation-law terminology occurrence count drifted")
    require("O013-LI-U025-COR-001" in candidate_text,
            "declared mathematical correction marker is absent")

    rows = list(csv.DictReader(glossary.decode("utf-8").splitlines()))
    require(len(rows) == 341, "controlled glossary row count drifted")
    by_source = {row["source_term"]: row for row in rows}
    require(len(by_source) == len(rows), "controlled glossary has duplicate source terms")
    for source, target_term in EXPECTED_TERMS.items():
        row = by_source.get(source)
        require(row is not None and row["target_term"] == target_term,
                f"missing or drifted terminology row: {source}")
        require(row["status"] == "admitted" and row["scope"] and row["note"],
                f"incomplete terminology metadata: {source}")

    candidate_check = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_unit_025_candidate.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(candidate_check.returncode == 0, "pinned candidate checker no longer passes")

    print("UNIT 025 STRUCTURE CHECK: PASS")
    print(f"target_bytes={len(target)}")
    print(f"target_sha256={digest(target)}")
    print(f"candidate_prefix_bytes={len(candidate)}")
    print(f"authority_suffix_bytes={len(suffix)}")
    print("terminal_lf_normalization=1")
    print(f"glossary_rows={len(rows)}")
    print(f"controlled_unit_terms={len(EXPECTED_TERMS)}")


if __name__ == "__main__":
    main()
