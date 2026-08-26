#!/usr/bin/env python3
"""Fail-closed, idempotent promotion of O013 Li Unit 030.

Only the Unit 030 terminology rows and the exact authority span
chapter4.tex:796-935 are mutable.  All preceding admitted units and the
authority suffix beginning at Section 4.7 are reconstructed from pinned
inputs before either canonical file is replaced.
"""

from __future__ import annotations

import csv
import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-030-staging/terminology-delta.csv"
UNIT_FILES = [
    ROOT / "build/unit-025-candidate/chapter4-group-basics-id.tex",
    ROOT / "build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex",
    ROOT / "build/unit-027-candidate/chapter4-products-group-extensions-id.tex",
    ROOT / "build/unit-028-candidate/chapter4-group-actions-counting-id.tex",
    ROOT / "build/unit-029-candidate/chapter4-sylow-theorems-id.tex",
]
UNIT_030 = ROOT / "build/unit-030-candidate/chapter4-group-composition-series-id.tex"

AUTHORITY_ID = (154744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_IDS = [
    (20464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a"),
    (19424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87"),
    (12675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563"),
    (13017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd"),
    (10028, "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d"),
]
UNIT_030_ID = (10044, "7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b")
PREFIX_ID = (75608, "299d9d6f1df324b7c4f3724e465b02978f60a6eb994b7102bfaa0a2393711f44")
SOURCE_SLICE_ID = (7981, "7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1")
OLD_SUFFIX_ID = (95054, "79bffb7c169bc99af3e7b4354cba883ae036abb6287421099dc5d930f06895d1")
NEW_SUFFIX_ID = (87073, "2507535ca192117452f9dd6b980842b8bdc1103b5b456be0a5a9d8d496448ed5")
OLD_TARGET_ID = (170663, "8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc")
NEW_TARGET_ID = (172726, "245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc")
OLD_GLOSSARY_ID = (65573, "adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3")
DELTA_ID = (1377, "fe0b91971953c8d14568fd1144f0799d8c36b6c6a7cc09be8dd11d688de3c7a4")
NEW_GLOSSARY_ID = (66908, "2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991")


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 030 promotion refused: " + message)


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".unit030.tmp")
    require(not temporary.exists(), f"stale exact temporary path exists: {temporary}")
    temporary.write_bytes(payload)
    require(identity(temporary.read_bytes()) == identity(payload), f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def main() -> None:
    authority = AUTHORITY.read_bytes()
    units = [path.read_bytes() for path in UNIT_FILES]
    unit_030 = UNIT_030.read_bytes()
    current_target = TARGET.read_bytes()
    current_glossary = GLOSSARY.read_bytes()
    delta = DELTA.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "authority identity drifted")
    for got, expected, path in zip((identity(x) for x in units), UNIT_IDS, UNIT_FILES):
        require(got == expected, f"{path.name} identity drifted: {got}")
    require(identity(unit_030) == UNIT_030_ID, "Unit 030 candidate identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    require(b"\r" not in b"".join(units) + unit_030 + delta, "CR/CRLF detected in promoted inputs")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1898, "authority record topology drifted")
    require(authority_lines[934] == b"\n", "authority line 935 is no longer the blank boundary")
    require(
        authority_lines[935].decode("utf-8") == "\\section{可解群与幂零群}\\label{sec:solvable-groups}\n",
        "authority line 936 Section 4.7 boundary drifted",
    )
    source_slice = b"".join(authority_lines[795:935])
    old_suffix = b"".join(authority_lines[795:])
    new_suffix = b"".join(authority_lines[935:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 796-935 drifted")
    require(identity(old_suffix) == OLD_SUFFIX_ID, "authority suffix from line 796 drifted")
    require(identity(new_suffix) == NEW_SUFFIX_ID, "authority suffix from line 936 drifted")

    prefix = b"".join(units)
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-029 prefix drifted")
    expected_old_target = prefix + old_suffix + b"\n"
    expected_target = prefix + unit_030 + new_suffix + b"\n"
    require(identity(expected_old_target) == OLD_TARGET_ID, "computed pre-Unit-030 target identity drifted")
    require(identity(expected_target) == NEW_TARGET_ID, "computed promoted target identity drifted")
    require(expected_target.decode("utf-8", errors="strict").splitlines()[793] == "\\section{Deret Komposisi Grup}\\label{sec:composition-series-grp}", "Unit 030 heading drifted")
    require(expected_target.decode("utf-8", errors="strict").splitlines()[932] == "\\section{可解群与幂零群}\\label{sec:solvable-groups}", "Unit 030 suffix sentinel drifted")

    delta_lines = delta.splitlines(keepends=True)
    require(len(delta_lines) == 9, "terminology delta row topology drifted")
    require(delta_lines[0].decode("utf-8").strip() == "source_term,target_term,status,scope,note", "terminology delta header drifted")

    old_state = identity(current_target) == OLD_TARGET_ID and identity(current_glossary) == OLD_GLOSSARY_ID
    new_state = identity(current_target) == NEW_TARGET_ID and identity(current_glossary) == NEW_GLOSSARY_ID
    require(old_state or new_state, "canonical target/glossary are neither pinned old nor promoted state")
    if new_state:
        print("UNIT 030 PROMOTION: ALREADY COMPLETE")
        return

    old_rows = list(csv.DictReader(current_glossary.decode("utf-8").splitlines()))
    delta_rows = list(csv.DictReader(delta.decode("utf-8").splitlines()))
    require(len(old_rows) == 413 and len(delta_rows) == 8, "terminology row counts drifted")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta contains a non-admitted row")
    old_terms = {row["source_term"] for row in old_rows}
    delta_terms = [row["source_term"] for row in delta_rows]
    require(len(old_terms) == len(old_rows), "controlled glossary already has duplicate source terms")
    require(len(set(delta_terms)) == len(delta_terms), "terminology delta has duplicate source terms")
    require(not old_terms.intersection(delta_terms), "terminology delta collides with controlled glossary")
    expected_glossary = current_glossary + b"".join(delta_lines[1:])
    require(identity(expected_glossary) == NEW_GLOSSARY_ID, "computed glossary identity drifted")

    atomic_write(GLOSSARY, expected_glossary)
    try:
        atomic_write(TARGET, expected_target)
    except Exception:
        atomic_write(GLOSSARY, current_glossary)
        raise
    require(identity(GLOSSARY.read_bytes()) == NEW_GLOSSARY_ID, "promoted glossary readback failed")
    require(identity(TARGET.read_bytes()) == NEW_TARGET_ID, "promoted target readback failed")
    print("UNIT 030 PROMOTION: PASS")
    print(f"target_bytes={NEW_TARGET_ID[0]}")
    print(f"target_sha256={NEW_TARGET_ID[1]}")
    print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
    print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
    print(f"glossary_rows={len(old_rows) + len(delta_rows)}")


if __name__ == "__main__":
    main()
