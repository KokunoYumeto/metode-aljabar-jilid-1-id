#!/usr/bin/env python3
"""Fail-closed, idempotent promotion of O013 Li Unit 033.

Only the exact Unit 033 source span and its thirteen admitted terminology rows
are mutable. The admitted Unit 025-032 prefix, untouched authority suffix,
predecessor target/glossary, and final target/glossary are reconstructed and
hash-bound before either canonical file is replaced.
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
DELTA = ROOT / "build/unit-033-staging/terminology-delta.csv"
CANDIDATE = ROOT / "build/unit-033-candidate/chapter4-symmetric-groups-id.tex"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (19_076, "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a")
PREFIX_ID = (133_417, "f6a268a51163777b42809e5689c6dfc413ab362c029eabbac8d211b3b3faea7e")
SUFFIX_ID = (29_403, "7ef27bb3573237cc1c566b79385b1ffcfe75adb4358f6b1aac5bf9ac1d567ab8")
CANDIDATE_ID = (23_099, "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76")
OLD_TARGET_ID = (181_896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680")
NEW_TARGET_ID = (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde")
OLD_GLOSSARY_ID = (74_335, "bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582")
DELTA_ID = (1_987, "783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b")
NEW_GLOSSARY_ID = (76_280, "9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c")

SOURCE_START, SOURCE_END = 1_389, 1_608
TARGET_START, TARGET_END = 1_384, 1_602
BOUNDARY_BLANK = 1_603
NEXT_SENTINEL = 1_604
OLD_GLOSSARY_ROWS = 465
DELTA_ROWS = 13
NEW_GLOSSARY_ROWS = 478


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 033 promotion refused: " + message)


def strict_utf8(data: bytes, label: str) -> str:
    require(not data.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {label}")
    require(b"\r" not in data, f"CR/CRLF detected: {label}")
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Unit 033 promotion refused: strict UTF-8 decode failed for {label}: {exc}") from exc


def atomic_write(path: Path, payload: bytes) -> None:
    require(path in (TARGET, GLOSSARY), f"write target is outside the two-file canonical boundary: {path}")
    temporary = path.with_name(path.name + ".unit033.tmp")
    require(not temporary.exists(), f"stale exact temporary path exists: {temporary}")
    temporary.write_bytes(payload)
    require(identity(temporary.read_bytes()) == identity(payload), f"temporary verification failed: {temporary}")
    os.replace(temporary, path)
    require(identity(path.read_bytes()) == identity(payload), f"atomic replacement readback failed: {path}")


def main() -> None:
    authority = AUTHORITY.read_bytes()
    candidate = CANDIDATE.read_bytes()
    current_target = TARGET.read_bytes()
    current_glossary = GLOSSARY.read_bytes()
    delta = DELTA.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "authority identity drifted")
    require(identity(candidate) == CANDIDATE_ID, "candidate identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    authority_text = strict_utf8(authority, "authority")
    candidate_text = strict_utf8(candidate, "candidate")
    target_text = strict_utf8(current_target, "canonical target")
    glossary_text = strict_utf8(current_glossary, "controlled glossary")
    delta_text = strict_utf8(delta, "terminology delta")
    require(candidate.endswith(b"\n") and not candidate.endswith(b"\n\n"),
            "candidate final-LF topology drifted")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1_898, "authority record topology drifted")
    require(authority_lines[SOURCE_START - 1]
            == "\\section{对称群}\\label{sec:symmetric-group}\n".encode(),
            "authority line 1389 opening drifted")
    require(authority_lines[SOURCE_END - 1] == b"\n", "authority line 1608 is no longer blank")
    require(authority_lines[SOURCE_END]
            == "\\section{群的极限和完备化}\\label{sec:group-limit}\n".encode(),
            "authority line 1609 sentinel drifted")
    source_slice = b"".join(authority_lines[SOURCE_START - 1 : SOURCE_END])
    suffix = b"".join(authority_lines[SOURCE_END:]) + b"\n"
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 1389-1608 drifted")
    require(identity(suffix) == SUFFIX_ID, "authority suffix from line 1609 drifted")

    target_old = identity(current_target) == OLD_TARGET_ID
    target_new = identity(current_target) == NEW_TARGET_ID
    require(target_old or target_new, "canonical target is neither pinned Unit 032 nor final Unit 033 state")
    target_lines = current_target.splitlines(keepends=True)
    require(len(target_lines) == 1_893, "canonical target record topology drifted")
    prefix = b"".join(target_lines[: TARGET_START - 1])
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-032 prefix drifted")

    expected_old_target = prefix + source_slice + suffix
    require(identity(expected_old_target) == OLD_TARGET_ID, "reconstructed Unit 032 predecessor identity drifted")
    if target_old:
        require(current_target == expected_old_target, "pinned Unit 032 predecessor bytes differ from reconstruction")

    # Candidate ends with one LF; the additional LF preserves authority line
    # 1608 as the blank boundary before the untouched line-1609 suffix.
    expected_target = prefix + candidate + b"\n" + suffix
    require(identity(expected_target) == NEW_TARGET_ID, "computed Unit 033 target identity drifted")
    expected_lines = expected_target.decode("utf-8", errors="strict").splitlines()
    require(len(expected_lines) == 1_893, "final target record topology drifted")
    require(expected_lines[TARGET_START - 1]
            == r"\section{Grup Simetris}\label{sec:symmetric-group}",
            "Unit 033 opening drifted")
    require(expected_lines[TARGET_END - 1].endswith(r"\index{grup Coxeter (Coxeter group)}"),
            "Unit 033 closing record drifted")
    require(expected_lines[BOUNDARY_BLANK - 1] == "", "preserved target blank boundary drifted")
    require(expected_lines[NEXT_SENTINEL - 1]
            == r"\section{群的极限和完备化}\label{sec:group-limit}",
            "target Section 4.10 sentinel drifted")
    require(expected_lines[TARGET_START - 1 : TARGET_END] == candidate_text.splitlines(),
            "final target span differs from candidate")

    delta_lines = delta.splitlines(keepends=True)
    require(len(delta_lines) == DELTA_ROWS + 1, "terminology delta row topology drifted")
    require(delta_lines[0].decode().strip() == "source_term,target_term,status,scope,note",
            "delta header drifted")
    glossary_old = identity(current_glossary) == OLD_GLOSSARY_ID
    glossary_new = identity(current_glossary) == NEW_GLOSSARY_ID
    require(glossary_old or glossary_new,
            "controlled glossary is neither pinned Unit 032 nor final Unit 033 state")
    if glossary_new:
        glossary_lines = current_glossary.splitlines(keepends=True)
        require(len(glossary_lines) == NEW_GLOSSARY_ROWS + 1,
                "final glossary row topology drifted")
        old_glossary = b"".join(glossary_lines[: OLD_GLOSSARY_ROWS + 1])
        require(identity(old_glossary) == OLD_GLOSSARY_ID,
                "pre-Unit-033 glossary prefix drifted")
    else:
        old_glossary = current_glossary
    expected_glossary = old_glossary + b"".join(delta_lines[1:])
    require(identity(expected_glossary) == NEW_GLOSSARY_ID,
            "computed Unit 033 glossary identity drifted")

    old_rows = list(csv.DictReader(strict_utf8(old_glossary, "pre-Unit-033 glossary").splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(old_rows) == OLD_GLOSSARY_ROWS and len(delta_rows) == DELTA_ROWS,
            "terminology row counts drifted")
    require(all(row["status"] == "admitted" for row in delta_rows),
            "delta contains a non-admitted row")
    old_terms = {row["source_term"] for row in old_rows}
    delta_terms = [row["source_term"] for row in delta_rows]
    require(len(old_terms) == len(old_rows), "controlled glossary already has duplicate source terms")
    require(len(set(delta_terms)) == len(delta_terms), "terminology delta has duplicate source terms")
    require(not old_terms.intersection(delta_terms), "terminology delta collides with controlled glossary")

    if target_new and glossary_new:
        require(current_target == expected_target and current_glossary == expected_glossary,
                "final bytes differ from deterministic reconstruction")
        print("UNIT 033 PROMOTION: ALREADY COMPLETE")
        print(f"target_bytes={NEW_TARGET_ID[0]}")
        print(f"target_sha256={NEW_TARGET_ID[1]}")
        print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
        print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
        print(f"glossary_rows={NEW_GLOSSARY_ROWS}")
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

    require(identity(GLOSSARY.read_bytes()) == NEW_GLOSSARY_ID,
            "promoted glossary readback failed")
    require(identity(TARGET.read_bytes()) == NEW_TARGET_ID,
            "promoted target readback failed")
    print("UNIT 033 PROMOTION: PASS")
    print(f"target_bytes={NEW_TARGET_ID[0]}")
    print(f"target_sha256={NEW_TARGET_ID[1]}")
    print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
    print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
    print(f"glossary_rows={NEW_GLOSSARY_ROWS}")


if __name__ == "__main__":
    main()
