#!/usr/bin/env python3
"""Fail-closed, idempotent promotion of O013 Li Unit 031.

Only the Unit 031 terminology rows and the exact authority span
chapter4.tex:936-1107 are mutable. All preceding admitted units and the
authority suffix beginning at Section 4.8 are reconstructed from pinned
inputs before either canonical file is replaced. The two canonical files are
validated independently because the terminology rows were admitted before
the source splice.
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
DELTA = ROOT / "build/unit-031-staging/terminology-delta.csv"
UNIT_FILES = [
    ROOT / "build/unit-025-candidate/chapter4-group-basics-id.tex",
    ROOT / "build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex",
    ROOT / "build/unit-027-candidate/chapter4-products-group-extensions-id.tex",
    ROOT / "build/unit-028-candidate/chapter4-group-actions-counting-id.tex",
    ROOT / "build/unit-029-candidate/chapter4-sylow-theorems-id.tex",
    ROOT / "build/unit-030-candidate/chapter4-group-composition-series-id.tex",
]
UNIT_031 = ROOT / "build/unit-031-candidate/chapter4-solvable-nilpotent-groups-id.tex"

AUTHORITY_ID = (154744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_IDS = [
    (20464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a"),
    (19424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87"),
    (12675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563"),
    (13017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd"),
    (10028, "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d"),
    (10044, "7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b"),
]
UNIT_031_ID = (19855, "6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81")
PREFIX_ID = (85652, "8048414405bf831ce6b7f016caa2189ca0dac78799a77ee8a94f7484fe6f31c2")
SOURCE_SLICE_ID = (16048, "647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b")
OLD_SUFFIX_ID = (87073, "2507535ca192117452f9dd6b980842b8bdc1103b5b456be0a5a9d8d496448ed5")
NEW_SUFFIX_ID = (71025, "689476021d6233cc21a35f84081244e083f6f673ad9b91ee0077b5e8480aca16")
OLD_TARGET_ID = (172726, "245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc")
NEW_TARGET_ID = (176533, "440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f")
OLD_GLOSSARY_ID = (66908, "2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991")
DELTA_ID = (2766, "9939372a066946a23b644e6ed3a78abb9bbbc44d1a33879d3c63c9ef97147116")
NEW_GLOSSARY_ID = (69632, "6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f")


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 031 promotion refused: " + message)


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".unit031.tmp")
    require(not temporary.exists(), f"stale exact temporary path exists: {temporary}")
    temporary.write_bytes(payload)
    require(identity(temporary.read_bytes()) == identity(payload), f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def main() -> None:
    authority = AUTHORITY.read_bytes()
    units = [path.read_bytes() for path in UNIT_FILES]
    unit_031 = UNIT_031.read_bytes()
    current_target = TARGET.read_bytes()
    current_glossary = GLOSSARY.read_bytes()
    delta = DELTA.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "authority identity drifted")
    for got, expected, path in zip((identity(data) for data in units), UNIT_IDS, UNIT_FILES):
        require(got == expected, f"{path.name} identity drifted: {got}")
    require(identity(unit_031) == UNIT_031_ID, "Unit 031 candidate identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    require(b"\r" not in b"".join(units) + unit_031 + delta, "CR/CRLF detected in promoted inputs")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1898, "authority record topology drifted")
    require(authority_lines[1105] == b"\\end{example}\n", "authority line 1106 closing boundary drifted")
    require(authority_lines[1106] == b"\n", "authority line 1107 is no longer the blank boundary")
    require(
        authority_lines[1107].decode("utf-8") == "\\section{自由群}\\label{sec:free-group}\n",
        "authority line 1108 Section 4.8 boundary drifted",
    )
    source_slice = b"".join(authority_lines[935:1107])
    old_suffix = b"".join(authority_lines[935:])
    new_suffix = b"".join(authority_lines[1107:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 936-1107 drifted")
    require(identity(old_suffix) == OLD_SUFFIX_ID, "authority suffix from line 936 drifted")
    require(identity(new_suffix) == NEW_SUFFIX_ID, "authority suffix from line 1108 drifted")

    prefix = b"".join(units)
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-030 prefix drifted")
    expected_old_target = prefix + old_suffix + b"\n"
    expected_target = prefix + unit_031 + new_suffix + b"\n"
    require(identity(expected_old_target) == OLD_TARGET_ID, "computed pre-Unit-031 target identity drifted")
    require(identity(expected_target) == NEW_TARGET_ID, "computed promoted target identity drifted")
    expected_lines = expected_target.decode("utf-8", errors="strict").splitlines()
    require(
        expected_lines[932] == "\\section{Grup Solvabel dan Grup Nilpoten}\\label{sec:solvable-groups}",
        "Unit 031 heading drifted",
    )
    require(expected_lines[1102] == "\\end{example}", "Unit 031 closing record drifted")
    require(
        expected_lines[1057]
        == "\t\t= \\text{suku konstan} + \\text{suku yang hanya memuat $q$} \\\\ {}+ \\text{suku yang hanya memuat $v$} + \\text{suku yang memuat $qv$}.",
        "Unit 031 declared digital display reflow drifted",
    )
    require(
        expected_lines[1103] == "\\section{自由群}\\label{sec:free-group}",
        "Unit 031 suffix sentinel drifted",
    )

    delta_lines = delta.splitlines(keepends=True)
    require(len(delta_lines) == 15, "terminology delta row topology drifted")
    require(
        delta_lines[0].decode("utf-8").strip() == "source_term,target_term,status,scope,note",
        "terminology delta header drifted",
    )

    target_old = identity(current_target) == OLD_TARGET_ID
    target_new = identity(current_target) == NEW_TARGET_ID
    glossary_old = identity(current_glossary) == OLD_GLOSSARY_ID
    glossary_new = identity(current_glossary) == NEW_GLOSSARY_ID
    require(target_old or target_new, "canonical target is neither pinned old nor promoted state")
    require(glossary_old or glossary_new, "controlled glossary is neither pinned old nor promoted state")

    if glossary_old:
        old_glossary = current_glossary
    else:
        current_lines = current_glossary.splitlines(keepends=True)
        require(len(current_lines) == 436, "promoted glossary row topology drifted")
        old_glossary = b"".join(current_lines[:422])
        require(identity(old_glossary) == OLD_GLOSSARY_ID, "pre-Unit-031 glossary prefix drifted")
    expected_glossary = old_glossary + b"".join(delta_lines[1:])
    require(identity(expected_glossary) == NEW_GLOSSARY_ID, "computed glossary identity drifted")
    if glossary_new:
        require(current_glossary == expected_glossary, "promoted glossary differs from exact old-plus-delta construction")

    old_rows = list(csv.DictReader(old_glossary.decode("utf-8").splitlines()))
    delta_rows = list(csv.DictReader(delta.decode("utf-8").splitlines()))
    require(len(old_rows) == 421 and len(delta_rows) == 14, "terminology row counts drifted")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta contains a non-admitted row")
    old_terms = {row["source_term"] for row in old_rows}
    delta_terms = [row["source_term"] for row in delta_rows]
    require(len(old_terms) == len(old_rows), "controlled glossary already has duplicate source terms")
    require(len(set(delta_terms)) == len(delta_terms), "terminology delta has duplicate source terms")
    require(not old_terms.intersection(delta_terms), "terminology delta collides with controlled glossary")

    if target_new and glossary_new:
        print("UNIT 031 PROMOTION: ALREADY COMPLETE")
        return

    changed_glossary = False
    if glossary_old:
        atomic_write(GLOSSARY, expected_glossary)
        changed_glossary = True
    try:
        if target_old:
            atomic_write(TARGET, expected_target)
    except Exception:
        if changed_glossary:
            atomic_write(GLOSSARY, old_glossary)
        raise

    require(identity(GLOSSARY.read_bytes()) == NEW_GLOSSARY_ID, "promoted glossary readback failed")
    require(identity(TARGET.read_bytes()) == NEW_TARGET_ID, "promoted target readback failed")
    print("UNIT 031 PROMOTION: PASS")
    print(f"target_bytes={NEW_TARGET_ID[0]}")
    print(f"target_sha256={NEW_TARGET_ID[1]}")
    print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
    print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
    print(f"glossary_rows={len(old_rows) + len(delta_rows)}")


if __name__ == "__main__":
    main()
