#!/usr/bin/env python3
"""Fail-closed Unit 035 canonical splice and terminology promotion."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = ROOT / "build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-035-staging/terminology-delta.csv"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
SOURCE_SLICE_ID = (14_398, "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287")
CANDIDATE_ID = (18_089, "5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca")
TARGET_BASE_ID = (189_935, "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569")
GLOSSARY_BASE_ID = (82_586, "59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955")
TARGET_FINAL_ID = (193_626, "2b682d67292e4c439ccc9f6d46f72d3d0eb7cb5bf8b3a3a5999210c45ef547c5")
GLOSSARY_FINAL_ID = (84_385, "933c064ca77fe92a19742e4df72b088bd81e3db9ff8db62740516a6389478d6d")
EXPECTED_TERMS = (
    "group object",
    "group functor",
    "finite product",
    "outer automorphism",
    "restricted product",
    "upper unitriangular matrices",
    "Ping-Pong lemma",
    "Wilson theorem",
    "Sylow subgroup",
    "equivariant morphism",
    "transfer",
)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), sha(payload)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def strict_text(path: Path, expected: tuple[int, str], *, lf_only: bool = True) -> tuple[bytes, str]:
    payload = path.read_bytes()
    need((len(payload), sha(payload)) == expected, f"identity drift: {path.relative_to(ROOT)}")
    if lf_only:
        need(payload.endswith(b"\n"), f"missing terminal newline: {path.relative_to(ROOT)}")
        need(b"\r" not in payload, f"line-ending drift: {path.relative_to(ROOT)}")
    return payload, payload.decode("utf-8", errors="strict")


def parse_csv(payload: bytes, context: str) -> list[dict[str, str]]:
    text = payload.decode("utf-8-sig", errors="strict")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    expected = ["source_term", "target_term", "status", "scope", "note"]
    need(reader.fieldnames == expected, f"{context} header drift")
    rows = list(reader)
    need(all(set(row) == set(expected) and all(value is not None for value in row.values()) for row in rows), f"{context} malformed row")
    return rows


def atomic_write(path: Path, payload: bytes) -> None:
    handle = tempfile.NamedTemporaryFile(prefix=path.name + ".", suffix=".tmp", dir=path.parent, delete=False)
    temp = Path(handle.name)
    try:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        handle.close()
        need(temp.read_bytes() == payload, f"temporary write mismatch: {path}")
        os.replace(temp, path)
    finally:
        if not handle.closed:
            handle.close()
        if temp.exists():
            temp.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, authority_text = strict_text(AUTHORITY, AUTHORITY_ID, lf_only=False)
    candidate_bytes, candidate_text = strict_text(CANDIDATE, CANDIDATE_ID)
    current_pair = (identity(TARGET), identity(GLOSSARY))
    base_pair = (TARGET_BASE_ID, GLOSSARY_BASE_ID)
    final_pair = (TARGET_FINAL_ID, GLOSSARY_FINAL_ID)
    need(current_pair in (base_pair, final_pair), "target/glossary state is neither pinned base nor pinned final")
    already_applied = current_pair == final_pair
    target_bytes, target_text = strict_text(TARGET, TARGET_FINAL_ID if already_applied else TARGET_BASE_ID)
    glossary_bytes, _ = strict_text(GLOSSARY, GLOSSARY_FINAL_ID if already_applied else GLOSSARY_BASE_ID)
    delta_bytes = DELTA.read_bytes()
    need(b"\r" not in delta_bytes and delta_bytes.endswith(b"\n"), "terminology delta line-ending drift")

    authority_lines = authority_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    target_lines = target_text.splitlines()
    need(len(authority_lines) == 1_898 and len(candidate_lines) == 154 and len(target_lines) == 1_893, "record-count drift")
    source_lines = authority_lines[1_744:1_898]
    source_bytes = ("\n".join(source_lines) + "\n").encode("utf-8")
    need((len(source_bytes), sha(source_bytes)) == SOURCE_SLICE_ID, "authority slice drift")
    if already_applied:
        need(target_lines[1_739:] == candidate_lines, "canonical admitted suffix drift")
    else:
        need(target_lines[1_739:] == source_lines, "canonical untranslated suffix drift")
    need(candidate_lines[0].startswith(r"\section{Grup dalam Kategori}"), "candidate opening drift")
    need(candidate_lines[-1] == r"\end{Exercises}", "candidate EOF drift")

    glossary_rows = parse_csv(glossary_bytes, "glossary")
    delta_rows = parse_csv(delta_bytes, "delta")
    need(len(glossary_rows) == (524 if already_applied else 513) and len(delta_rows) == len(EXPECTED_TERMS), "terminology row-count drift")
    need(tuple(row["source_term"] for row in delta_rows) == EXPECTED_TERMS, "terminology delta order/key drift")
    if already_applied:
        by_term = {row["source_term"]: row for row in glossary_rows}
        need(all(by_term.get(row["source_term"]) == row for row in delta_rows), "admitted terminology differs from delta")
        new_target = target_bytes
        new_glossary = glossary_bytes
    else:
        existing = {row["source_term"].casefold() for row in glossary_rows}
        need(all(row["source_term"].casefold() not in existing and row["status"] == "admitted" for row in delta_rows), "terminology delta conflict")
        new_target = ("\n".join(target_lines[:1_739] + candidate_lines) + "\n").encode("utf-8")
        delta_body = delta_bytes.split(b"\n", 1)[1]
        new_glossary = glossary_bytes + delta_body
    need(len(new_target.decode("utf-8").splitlines()) == 1_893, "promoted target record drift")
    promoted_lines = new_target.decode("utf-8").splitlines()
    need(promoted_lines[1_739:] == candidate_lines, "promoted candidate mismatch")
    promoted_rows = parse_csv(new_glossary, "promoted glossary")
    need(len(promoted_rows) == 524 and len({row["source_term"].casefold() for row in promoted_rows}) == 524, "promoted glossary uniqueness drift")
    need((len(new_target), sha(new_target)) == TARGET_FINAL_ID, "final target identity drift")
    need((len(new_glossary), sha(new_glossary)) == GLOSSARY_FINAL_ID, "final glossary identity drift")

    result = {
        "status": "PASS_ALREADY_APPLIED" if already_applied else ("PASS_APPLIED" if args.apply else "PASS_DRY_RUN"),
        "authority": {"range": "chapter4.tex:1745-1898", "bytes": SOURCE_SLICE_ID[0], "sha256": SOURCE_SLICE_ID[1]},
        "candidate": {"records": 154, "bytes": len(candidate_bytes), "sha256": sha(candidate_bytes)},
        "target_before": {"bytes": len(target_bytes), "sha256": sha(target_bytes)},
        "target_after": {"bytes": len(new_target), "sha256": sha(new_target)},
        "glossary_before": {"rows": len(glossary_rows), "bytes": len(glossary_bytes), "sha256": sha(glossary_bytes)},
        "glossary_after": {"rows": 524, "bytes": len(new_glossary), "sha256": sha(new_glossary)},
        "terminology_delta": {"rows": len(delta_rows), "bytes": len(delta_bytes), "sha256": sha(delta_bytes)},
        "next_cursor": "chapter5.tex:1",
        "writes_performed": bool(args.apply and not already_applied),
    }
    if args.apply and not already_applied:
        need(identity(TARGET) == TARGET_BASE_ID and identity(GLOSSARY) == GLOSSARY_BASE_ID, "base changed before apply")
        atomic_write(TARGET, new_target)
        atomic_write(GLOSSARY, new_glossary)
        need(TARGET.read_bytes() == new_target and GLOSSARY.read_bytes() == new_glossary, "applied bytes drift")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
