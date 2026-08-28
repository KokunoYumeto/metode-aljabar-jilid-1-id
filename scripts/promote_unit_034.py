#!/usr/bin/env python3
"""Fail-closed, idempotent promotion of O013 Li Unit 034."""

from __future__ import annotations

import csv
import hashlib
import io
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
CANDIDATE = ROOT / "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-034-staging/terminology-delta.csv"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (15_005, "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab")
OLD_TARGET_ID = (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde")
PREFIX_ID = (156_517, "d392f169663ed5b2179318ed5106f55181baba1f1b50b7928ae7d856e5faf339")
SUFFIX_ID = (14_398, "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287")
CANDIDATE_ID = (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62")
NEW_TARGET_ID = (189_935, "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569")
OLD_GLOSSARY_ID = (76_280, "9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c")
DELTA_ID = (6_613, "077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659")
NEW_GLOSSARY_ID = (82_586, "59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955")
FIELDS = ("source_term", "target_term", "status", "scope", "note")


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 034 promotion refused: " + message)


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".unit034.tmp")
    require(not temporary.exists(), f"stale exact temporary exists: {temporary}")
    temporary.write_bytes(payload)
    require(temporary.read_bytes() == payload, f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def parse_rows(payload: bytes, context: str) -> list[dict[str, str]]:
    require(b"\r" not in payload, f"CR/CRLF detected in {context}")
    text = payload.decode("utf-8", errors="strict")
    reader = csv.DictReader(text.splitlines())
    require(tuple(reader.fieldnames or ()) == FIELDS, f"header drifted in {context}")
    rows = list(reader)
    require(all(set(row) == set(FIELDS) and None not in row for row in rows), f"malformed row in {context}")
    return rows


def serialize(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    stream.write(",".join(FIELDS) + "\n")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n", quoting=csv.QUOTE_ALL)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main() -> None:
    authority = AUTHORITY.read_bytes()
    candidate = CANDIDATE.read_bytes()
    target = TARGET.read_bytes()
    glossary = GLOSSARY.read_bytes()
    delta = DELTA.read_bytes()

    require(identity(authority) == AUTHORITY_ID, "authority identity drifted")
    require(identity(candidate) == CANDIDATE_ID, "candidate identity drifted")
    require(identity(delta) == DELTA_ID, "terminology delta identity drifted")
    require(b"\r" not in authority + candidate + target + glossary + delta, "CR/CRLF detected")
    require(candidate.endswith(b"\n") and not candidate.endswith(b"\n\n"), "candidate LF topology drifted")

    authority_lines = authority.splitlines(keepends=True)
    require(len(authority_lines) == 1_898, "authority record topology drifted")
    require(authority_lines[1_608] == "\\section{群的极限和完备化}\\label{sec:group-limit}\n".encode(), "authority line 1609 drifted")
    require(authority_lines[1_743] == b"\n", "authority line 1744 is not blank")
    require(authority_lines[1_744] == "\\section{范畴中的群}\\label{sec:group-in-cat}\n".encode(), "authority line 1745 drifted")
    source_slice = b"".join(authority_lines[1_608:1_744])
    suffix = b"".join(authority_lines[1_744:]) + b"\n"
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 1609-1744 drifted")
    require(identity(suffix) == SUFFIX_ID, "authority suffix from line 1745 drifted")

    target_old = identity(target) == OLD_TARGET_ID
    target_new = identity(target) == NEW_TARGET_ID
    require(target_old or target_new, "canonical target is neither pinned old nor promoted state")
    target_lines = target.splitlines(keepends=True)
    prefix = b"".join(target_lines[:1_603])
    require(identity(prefix) == PREFIX_ID, "admitted Unit 001-033 prefix drifted")
    expected_target = prefix + candidate + b"\n" + suffix
    require(identity(expected_target) == NEW_TARGET_ID, "computed promoted target identity drifted")
    expected_lines = expected_target.decode("utf-8", errors="strict").splitlines()
    require(len(expected_lines) == 1_893, "promoted target record topology drifted")
    require(expected_lines[1_603] == r"\section{Limit dan Pelengkapan Grup}\label{sec:group-limit}", "Unit 034 opening drifted")
    require(expected_lines[1_737] == r"\end{example}", "Unit 034 closing drifted")
    require(expected_lines[1_738] == "", "Unit 034 blank boundary drifted")
    require(expected_lines[1_739] == r"\section{范畴中的群}\label{sec:group-in-cat}", "Section 4.11 sentinel drifted")

    old_glossary = identity(glossary) == OLD_GLOSSARY_ID
    new_glossary = identity(glossary) == NEW_GLOSSARY_ID
    require(old_glossary or new_glossary, "glossary is neither pinned old nor promoted state")
    delta_rows = parse_rows(delta, "delta")
    require(len(delta_rows) == 37, "terminology delta row count drifted")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta contains non-admitted row")
    require([row["source_term"] for row in delta_rows[:2]] == ["completion", "completeness"], "replacement rows drifted")
    require(len({row["source_term"] for row in delta_rows}) == 37, "duplicate source term in delta")

    if old_glossary:
        old_rows = parse_rows(glossary, "old glossary")
    else:
        promoted_rows = parse_rows(glossary, "promoted glossary")
        require(len(promoted_rows) == 513, "promoted glossary row count drifted")
        require(promoted_rows[15]["source_term"] == "completion", "promoted completion position drifted")
        require(promoted_rows[222]["source_term"] == "completeness", "promoted completeness position drifted")
        # Reconstruct the exact old state solely for deterministic comparison.
        old_rows = promoted_rows[:]
        old_rows[15] = {"source_term": "completion", "target_term": "kompletisasi", "status": "provisional", "scope": "chapter 10", "note": "Do not confuse with proof completion."}
        old_rows[222] = {"source_term": "completeness", "target_term": "kelengkapan", "status": "admitted", "scope": "category theory", "note": "Use for the property that all small projective limits exist; distinguish from metric completeness by context."}
        old_rows = old_rows[:478]
        require(identity(serialize(old_rows)) == OLD_GLOSSARY_ID, "promoted glossary does not reconstruct pinned old state")

    require(len(old_rows) == 478, "old glossary row count drifted")
    terms = [row["source_term"] for row in old_rows]
    require(len(set(terms)) == len(terms), "old glossary has duplicate source terms")
    positions = {term: terms.index(term) for term in ("completion", "completeness")}
    require(positions == {"completion": 15, "completeness": 222}, "replacement positions drifted")
    additions = delta_rows[2:]
    require(not set(row["source_term"] for row in additions).intersection(terms), "delta addition collides with glossary")
    expected_rows = old_rows[:]
    expected_rows[15] = delta_rows[0]
    expected_rows[222] = delta_rows[1]
    expected_rows.extend(additions)
    expected_glossary = serialize(expected_rows)
    require(identity(expected_glossary) == NEW_GLOSSARY_ID, "computed promoted glossary identity drifted")

    if target_new and new_glossary:
        require(target == expected_target and glossary == expected_glossary, "promoted bytes differ from reconstruction")
        print("UNIT 034 PROMOTION: ALREADY COMPLETE")
    else:
        wrote_glossary = False
        if old_glossary:
            atomic_write(GLOSSARY, expected_glossary)
            wrote_glossary = True
        try:
            if target_old:
                atomic_write(TARGET, expected_target)
        except Exception:
            if wrote_glossary:
                atomic_write(GLOSSARY, glossary)
            raise
        require(identity(GLOSSARY.read_bytes()) == NEW_GLOSSARY_ID, "glossary readback failed")
        require(identity(TARGET.read_bytes()) == NEW_TARGET_ID, "target readback failed")
        print("UNIT 034 PROMOTION: PASS")
    print(f"target_bytes={NEW_TARGET_ID[0]}")
    print(f"target_sha256={NEW_TARGET_ID[1]}")
    print(f"glossary_bytes={NEW_GLOSSARY_ID[0]}")
    print(f"glossary_sha256={NEW_GLOSSARY_ID[1]}")
    print("glossary_rows=513")


if __name__ == "__main__":
    main()
