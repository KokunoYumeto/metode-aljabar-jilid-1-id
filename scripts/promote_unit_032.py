#!/usr/bin/env python3
"""Fail-closed, idempotent promotion of O013 Li Unit 032.

Only the exact Unit 032 source span and its 30 admitted terminology rows are
mutable. The already-admitted prefix and the untouched authority suffix are
reconstructed and hash-bound before either canonical file is replaced.
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
DELTA = ROOT / "build/unit-032-staging/terminology-delta.csv"
CANDIDATE = ROOT / "build/unit-032-candidate/chapter4-free-groups-id.tex"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (22_547, "5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af")
PREFIX_ID = (105_507, "32001596ab4f033872ca17f077676dce7a0e2f0b03fc5cf00191fe6dbb04e712")
SUFFIX_ID = (48_479, "c3573106a6b5cb62e3d7008de782696679f632e608f1f07c240f41e2d1b1aedd")
CANDIDATE_ID = (27_910, "28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc")
OLD_TARGET_ID = (176_533, "440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f")
INTERIM_TARGET_IDS = (
    (181_808, "51055dcd6d8cf0df06cc2dde9059ecd9a327b0e20534011638fa5961d27aa699"),
    (181_898, "0a1bcec70db41c268f9d86387770a581460268263000b876905cdf47d152bb8b"),
)
NEW_TARGET_ID = (181_896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680")
OLD_GLOSSARY_ID = (69_632, "6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f")
DELTA_ID = (4_745, "3d742473a35c0bdd890fecbfe3f0dc37e8dc96f8452287c6fadc35dda46d6fad")
NEW_GLOSSARY_ID = (74_335, "bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582")


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 032 promotion refused: " + message)


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".unit032.tmp")
    require(not temporary.exists(), f"stale exact temporary path exists: {temporary}")
    temporary.write_bytes(payload)
    require(identity(temporary.read_bytes()) == identity(payload), f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def main() -> None:
    authority = AUTHORITY.read_bytes()
    candidate = CANDIDATE.read_bytes()
    current_target = TARGET.read_bytes()
    current_glossary = GLOSSARY.read_bytes()
    delta = DELTA.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "authority identity drifted")
    require(identity(candidate) == CANDIDATE_ID, "candidate identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    require(b"\r" not in authority + candidate + current_target + current_glossary + delta, "CR/CRLF detected")
    require(candidate.endswith(b"\n") and not candidate.endswith(b"\n\n"), "candidate final-LF topology drifted")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1_898, "authority record topology drifted")
    require(authority_lines[1_107] == "\\section{自由群}\\label{sec:free-group}\n".encode(), "authority line 1108 drifted")
    require(authority_lines[1_387] == b"\n", "authority line 1388 is no longer blank")
    require(authority_lines[1_388] == "\\section{对称群}\\label{sec:symmetric-group}\n".encode(), "authority line 1389 drifted")
    source_slice = b"".join(authority_lines[1_107:1_388])
    suffix = b"".join(authority_lines[1_388:]) + b"\n"
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 1108-1388 drifted")
    require(identity(suffix) == SUFFIX_ID, "authority suffix from line 1389 drifted")

    target_old = identity(current_target) in (OLD_TARGET_ID, *INTERIM_TARGET_IDS)
    target_new = identity(current_target) == NEW_TARGET_ID
    require(target_old or target_new, "canonical target is neither pinned old nor promoted state")
    target_lines = current_target.splitlines(keepends=True)
    prefix = b"".join(target_lines[:1_103])
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-031 prefix drifted")
    expected_target = prefix + candidate + suffix
    require(identity(expected_target) == NEW_TARGET_ID, "computed promoted target identity drifted")
    expected_lines = expected_target.decode("utf-8", errors="strict").splitlines()
    require(len(expected_lines) == 1_893, "promoted target record topology drifted")
    require(expected_lines[1_103] == r"\section{Grup Bebas}\label{sec:free-group}", "Unit 032 opening drifted")
    require(expected_lines[1_382] == r"\end{proof}", "Unit 032 closing drifted")
    require(expected_lines[1_383] == r"\section{对称群}\label{sec:symmetric-group}", "Section 4.9 sentinel drifted")

    delta_lines = delta.splitlines(keepends=True)
    require(len(delta_lines) == 31, "terminology delta row topology drifted")
    require(delta_lines[0].decode().strip() == "source_term,target_term,status,scope,note", "delta header drifted")
    glossary_old = identity(current_glossary) == OLD_GLOSSARY_ID
    glossary_new = identity(current_glossary) == NEW_GLOSSARY_ID
    require(glossary_old or glossary_new, "controlled glossary is neither pinned old nor promoted state")
    if glossary_new:
        glossary_lines = current_glossary.splitlines(keepends=True)
        require(len(glossary_lines) == 466, "promoted glossary row topology drifted")
        old_glossary = b"".join(glossary_lines[:436])
        require(identity(old_glossary) == OLD_GLOSSARY_ID, "pre-Unit-032 glossary prefix drifted")
    else:
        old_glossary = current_glossary
    expected_glossary = old_glossary + b"".join(delta_lines[1:])
    require(identity(expected_glossary) == NEW_GLOSSARY_ID, "computed promoted glossary identity drifted")

    old_rows = list(csv.DictReader(old_glossary.decode().splitlines()))
    delta_rows = list(csv.DictReader(delta.decode().splitlines()))
    require(len(old_rows) == 435 and len(delta_rows) == 30, "terminology row counts drifted")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta contains a non-admitted row")
    old_terms = {row["source_term"] for row in old_rows}
    delta_terms = [row["source_term"] for row in delta_rows]
    require(len(old_terms) == len(old_rows), "controlled glossary already has duplicate source terms")
    require(len(set(delta_terms)) == len(delta_terms), "terminology delta has duplicate source terms")
    require(not old_terms.intersection(delta_terms), "terminology delta collides with controlled glossary")

    if target_new and glossary_new:
        require(current_target == expected_target and current_glossary == expected_glossary, "promoted bytes differ from reconstruction")
        print("UNIT 032 PROMOTION: ALREADY COMPLETE")
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
    print("UNIT 032 PROMOTION: PASS")
    print(f"target_bytes={NEW_TARGET_ID[0]}")
    print(f"target_sha256={NEW_TARGET_ID[1]}")
    print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
    print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
    print(f"glossary_rows={len(old_rows) + len(delta_rows)}")


if __name__ == "__main__":
    main()
