#!/usr/bin/env python3
"""Fail-closed canonical integration check for O013 Li Unit 032."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = ROOT / "build/unit-032-candidate/chapter4-free-groups-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-032-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_032_candidate.py"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (22_547, "5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af")
PREFIX_ID = (105_507, "32001596ab4f033872ca17f077676dce7a0e2f0b03fc5cf00191fe6dbb04e712")
SUFFIX_ID = (48_479, "c3573106a6b5cb62e3d7008de782696679f632e608f1f07c240f41e2d1b1aedd")
CANDIDATE_ID = (27_910, "28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc")
CHECKER_ID = (18_668, "318a57bf22d50baef5102ebc07bb9fd83943682b44d01dac4de5150e770a2cc0")
TARGET_ID = (181_896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680")
OLD_GLOSSARY_ID = (69_632, "6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f")
DELTA_ID = (4_745, "3d742473a35c0bdd890fecbfe3f0dc37e8dc96f8452287c6fadc35dda46d6fad")
GLOSSARY_ID = (74_335, "bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582")

SOURCE_START, SOURCE_END = 1_108, 1_388
TARGET_START, TARGET_END = 1_104, 1_383


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 032 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
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
    candidate, candidate_text = strict(CANDIDATE)
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()

    for got, expected, label in (
        (identity(authority), AUTHORITY_ID, "authority"),
        (identity(candidate), CANDIDATE_ID, "candidate"),
        (identity(checker), CHECKER_ID, "candidate checker"),
        (identity(target), TARGET_ID, "canonical target"),
        (identity(glossary), GLOSSARY_ID, "controlled glossary"),
        (identity(delta), DELTA_ID, "terminology delta"),
    ):
        require(got == expected, f"{label} identity drifted: {got}")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    target_lines_bytes = target.splitlines(keepends=True)
    target_lines = target_text.splitlines()
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(candidate_lines) == 280, "candidate line topology drifted")
    require(len(target_lines) == 1_893, "target line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target final-LF topology drifted")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1:SOURCE_END])
    suffix = b"".join(authority_lines_bytes[SOURCE_END:]) + b"\n"
    prefix = b"".join(target_lines_bytes[:TARGET_START - 1])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 1108-1388 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 1388 is not blank")
    require(authority_lines[SOURCE_END] == r"\section{对称群}\label{sec:symmetric-group}", "authority line 1389 drifted")
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-031 prefix drifted")
    require(identity(suffix) == SUFFIX_ID, "authority suffix from line 1389 drifted")
    require(target == prefix + candidate + suffix, "canonical target is not exact prefix plus Unit 032 plus authority suffix")
    require(target_lines[TARGET_START - 1:TARGET_END] == candidate_lines, "canonical Unit 032 span differs from candidate")
    require(target_lines[TARGET_START - 1] == r"\section{Grup Bebas}\label{sec:free-group}", "Unit 032 heading drifted")
    require(target_lines[TARGET_END - 1] == r"\end{proof}", "Unit 032 closing record drifted")
    require(target_lines[TARGET_END] == r"\section{对称群}\label{sec:symmetric-group}", "Section 4.9 target sentinel drifted")

    glossary_lines = glossary.splitlines(keepends=True)
    require(len(glossary_lines) == 466, "controlled glossary physical-row topology drifted")
    require(identity(b"".join(glossary_lines[:436])) == OLD_GLOSSARY_ID, "pre-Unit-032 glossary prefix drifted")
    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 465 and len(delta_rows) == 30, "glossary/delta row counts drifted")
    require(glossary_rows[-30:] == delta_rows, "controlled glossary tail differs from Unit 032 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    evidence_text = re.sub(r"\\emph\{([^{}]+)\}", r"\1", candidate_text).casefold()
    evidence_aliases = {
        "normal closure": "subgrup normal terkecil",
        "finitely generated group": "dibangkitkan secara berhingga",
        "finitely presented group": "dipresentasikan secara berhingga",
        "fundamental group": r"\pi_1",
    }
    for row in delta_rows:
        surface = evidence_aliases.get(row["source_term"], row["target_term"])
        require(surface.casefold() in evidence_text, f"candidate lacks evidence surface for {row['source_term']!r}")

    runs = [
        subprocess.run(
            [sys.executable, str(CANDIDATE_CHECKER)], cwd=ROOT, text=True,
            encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        for _ in range(2)
    ]
    require(all(run.returncode == 0 for run in runs), "candidate checker failed")
    require(all(run.stderr == "" for run in runs), "candidate checker emitted stderr")
    require(runs[0].stdout == runs[1].stdout, "candidate checker output was nondeterministic")
    require("candidate: 280 records, 27910 bytes" in runs[0].stdout, "candidate checker output identity drifted")

    print("UNIT 032 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={CANDIDATE_ID[0]}")
    print(f"canonical_span_sha256={CANDIDATE_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print(f"next_section_sentinel_line={TARGET_END + 1}")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")


if __name__ == "__main__":
    main()
