#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 033.

``--scaffold-check`` proves the frozen authority/candidate identities and the
anticipated prefix + candidate + suffix target identity before integration.
The default admission check additionally requires the live glossary and Unit
033 terminology-delta identities to be bound in the adjacent constants below.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = ROOT / "build/unit-033-candidate/chapter4-symmetric-groups-id.tex"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_033_candidate.py"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-033-staging/terminology-delta.csv"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (19_076, "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a")
CANDIDATE_ID = (23_099, "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76")
CANDIDATE_CHECKER_ID = (18_099, "643b1ccc5fe1f47aa185cbb8d2813e971c1381cbcc032fac8cc01c2c941c2a1d")

# Exact Unit 032 predecessor and the deterministic Unit 033 composition.
PREDECESSOR_TARGET_ID = (181_896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680")
PREFIX_ID = (133_417, "f6a268a51163777b42809e5689c6dfc413ab362c029eabbac8d211b3b3faea7e")
SUFFIX_ID = (29_403, "7ef27bb3573237cc1c566b79385b1ffcfe75adb4358f6b1aac5bf9ac1d567ab8")
TARGET_ID = (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde")

# Final 13-row terminology admission prepared independently before canonical
# source integration. These identities remain fail-closed in the default gate.
GLOSSARY_ID: tuple[int, str] | None = (
    76_280,
    "9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c",
)
DELTA_ID: tuple[int, str] | None = (
    1_987,
    "783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b",
)
DELTA_ROWS: int | None = 13

SOURCE_START, SOURCE_END = 1_389, 1_608
TARGET_START, TARGET_END = 1_384, 1_602
BOUNDARY_BLANK = 1_603
NEXT_SENTINEL = 1_604


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 033 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
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


def run_candidate_checker() -> str:
    checker = CANDIDATE_CHECKER.read_bytes()
    require(identity(checker) == CANDIDATE_CHECKER_ID, "candidate checker identity drifted")
    runs = [
        subprocess.run(
            [sys.executable, str(CANDIDATE_CHECKER)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        for _ in range(2)
    ]
    require(all(run.returncode == 0 for run in runs), "candidate checker failed")
    require(all(run.stderr == "" for run in runs), "candidate checker emitted stderr")
    require(runs[0].stdout == runs[1].stdout, "candidate checker output was nondeterministic")
    require(
        runs[0].stdout.startswith("PASS: O013-LI-U033 isolated complete Section 4.9 candidate\n"),
        "candidate checker verdict drifted",
    )
    require(
        "candidate: 219 records, 23099 bytes, sha256=1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76"
        in runs[0].stdout,
        "candidate checker identity output drifted",
    )
    require("declared_digital_reflows=1" in runs[0].stdout, "candidate reflow census missing")
    return runs[0].stdout


def frozen_inputs() -> tuple[bytes, str, bytes, str, list[bytes]]:
    authority, authority_text = strict(AUTHORITY)
    candidate, candidate_text = strict(CANDIDATE)
    require(identity(authority) == AUTHORITY_ID, "frozen Chapter 4 authority identity drifted")
    require(identity(candidate) == CANDIDATE_ID, "Unit 033 candidate identity drifted")
    require(candidate.endswith(b"\n") and not candidate.endswith(b"\n\n"), "candidate final-LF topology drifted")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(candidate_lines) == 219, "candidate line topology drifted")
    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 1389-1608 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 1608 is not blank")
    require(
        authority_lines[SOURCE_END] == r"\section{群的极限和完备化}\label{sec:group-limit}",
        "authority line 1609 Section 4.10 sentinel drifted",
    )
    require(candidate_lines[0] == r"\section{Grup Simetris}\label{sec:symmetric-group}", "candidate heading drifted")
    require(candidate_lines[-1].endswith(r"\index{grup Coxeter (Coxeter group)}"), "candidate closing record drifted")
    run_candidate_checker()
    return authority, authority_text, candidate, candidate_text, authority_lines_bytes


def anticipated_composition(
    predecessor: bytes,
    candidate: bytes,
    authority_lines_bytes: list[bytes],
) -> tuple[bytes, bytes, bytes]:
    predecessor_lines_bytes = predecessor.splitlines(keepends=True)
    prefix = b"".join(predecessor_lines_bytes[: TARGET_START - 1])
    suffix = b"".join(authority_lines_bytes[SOURCE_END:]) + b"\n"
    require(identity(prefix) == PREFIX_ID, "admitted Unit 025-032 prefix identity drifted")
    require(identity(suffix) == SUFFIX_ID, "authority suffix from line 1609 drifted")
    # Preserve the authority's blank line 1608 as the one-record separator
    # between the translated Section 4.9 candidate and Section 4.10.
    expected = prefix + candidate + b"\n" + suffix
    require(identity(expected) == TARGET_ID, "anticipated Unit 033 target identity drifted")
    require(expected.count(b"\n") == 1_893, "anticipated target LF-record topology drifted")
    return prefix, suffix, expected


def scaffold_check() -> None:
    _, _, candidate, _, authority_lines_bytes = frozen_inputs()
    live_target, _ = strict(TARGET)
    live_id = identity(live_target)
    if live_id == PREDECESSOR_TARGET_ID:
        predecessor = live_target
    elif live_id == TARGET_ID:
        prefix = b"".join(live_target.splitlines(keepends=True)[: TARGET_START - 1])
        predecessor = prefix + b"".join(authority_lines_bytes[SOURCE_START - 1 :]) + b"\n"
        require(identity(predecessor) == PREDECESSOR_TARGET_ID, "reconstructed predecessor identity drifted")
    else:
        fail(f"live target is neither predecessor nor final Unit 033 target: {live_id}")
    _, _, anticipated = anticipated_composition(predecessor, candidate, authority_lines_bytes)
    if live_id == TARGET_ID:
        require(live_target == anticipated, "live Unit 033 target differs from the anticipated composition")
    print("UNIT 033 STRUCTURE SCAFFOLD CHECK: PASS")
    print(f"predecessor_target_bytes={PREDECESSOR_TARGET_ID[0]}")
    print(f"predecessor_target_sha256={PREDECESSOR_TARGET_ID[1]}")
    print(f"anticipated_target_bytes={TARGET_ID[0]}")
    print(f"anticipated_target_sha256={TARGET_ID[1]}")
    print(f"anticipated_target_records={1_893}")
    print(f"anticipated_span_lines={TARGET_START}-{TARGET_END}")
    print(f"preserved_blank_boundary_line={BOUNDARY_BLANK}")
    print(f"next_section_sentinel_line={NEXT_SENTINEL}")
    print(f"terminology_delta_rows={DELTA_ROWS}")
    print(f"terminology_delta_sha256={DELTA_ID[1] if DELTA_ID else 'unbound'}")
    print(f"glossary_sha256={GLOSSARY_ID[1] if GLOSSARY_ID else 'unbound'}")
    print(
        "canonical_integration=verified_final"
        if live_id == TARGET_ID
        else "canonical_integration=pending_fail_closed"
    )


def admission_check() -> None:
    require(GLOSSARY_ID is not None, "bind GLOSSARY_ID after Unit 033 terminology admission")
    require(DELTA_ID is not None, "bind DELTA_ID after Unit 033 terminology admission")
    require(DELTA_ROWS is not None and DELTA_ROWS > 0, "bind positive DELTA_ROWS after terminology admission")

    _, _, candidate, candidate_text, authority_lines_bytes = frozen_inputs()
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    require(identity(target) == TARGET_ID, "canonical target identity drifted")
    require(identity(glossary) == GLOSSARY_ID, "controlled glossary identity drifted")
    require(identity(delta) == DELTA_ID, "Unit 033 terminology-delta identity drifted")

    predecessor_prefix = b"".join(target.splitlines(keepends=True)[: TARGET_START - 1])
    predecessor = predecessor_prefix + b"".join(authority_lines_bytes[SOURCE_START - 1 :]) + b"\n"
    require(identity(predecessor) == PREDECESSOR_TARGET_ID, "reconstructed Unit 032 predecessor identity drifted")
    _, _, expected = anticipated_composition(predecessor, candidate, authority_lines_bytes)
    require(target == expected, "canonical target is not exact prefix + Unit 033 + authority suffix")

    target_lines = target_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    require(len(target_lines) == 1_893, "canonical target record topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "canonical target final-LF topology drifted")
    require(target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines, "canonical Unit 033 span differs from candidate")
    require(target_lines[BOUNDARY_BLANK - 1] == "", "canonical blank section-boundary record drifted")
    require(
        target_lines[NEXT_SENTINEL - 1] == r"\section{群的极限和完备化}\label{sec:group-limit}",
        "canonical Section 4.10 sentinel drifted",
    )

    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(delta_rows) == DELTA_ROWS, "terminology-delta row count drifted")
    require(glossary_rows[-DELTA_ROWS:] == delta_rows, "live glossary tail differs from Unit 033 delta")
    require(all(row.get("status") == "admitted" for row in delta_rows), "terminology delta has non-admitted row")
    source_terms = [row["source_term"] for row in glossary_rows]
    require(len(source_terms) == len(set(source_terms)), "controlled glossary has duplicate source terms")
    evidence_text = re.sub(r"\\emph\{([^{}]+)\}", r"\1", candidate_text).casefold()
    for row in delta_rows:
        surface = row["target_term"].casefold()
        require(surface in evidence_text, f"candidate lacks terminology evidence surface for {row['source_term']!r}")

    print("UNIT 033 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print("canonical_target_records=1893")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={CANDIDATE_ID[0]}")
    print(f"canonical_span_sha256={CANDIDATE_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print(f"preserved_blank_boundary_line={BOUNDARY_BLANK}")
    print(f"next_section_sentinel_line={NEXT_SENTINEL}")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scaffold-check",
        action="store_true",
        help="prove frozen inputs and anticipated target identity before integration",
    )
    args = parser.parse_args()
    if args.scaffold_check:
        scaffold_check()
    else:
        admission_check()


if __name__ == "__main__":
    main()
