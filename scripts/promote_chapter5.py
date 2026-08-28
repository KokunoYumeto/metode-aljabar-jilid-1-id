#!/usr/bin/env python3
"""Idempotently promote the checked complete Chapter 5 candidate and terms."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "repo/source/chapter5.tex"
CANDIDATE = ROOT / "build/unit-043-candidate/chapter5-complete-id.tex"
CHECKER = ROOT / "build/unit-043-candidate/check_chapter5_complete.py"
DELTA = ROOT / "build/unit-043-candidate/CHAPTER5_TERMINOLOGY_DELTA.id-ID.csv"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"

AUTHORITY_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
CANDIDATE_SHA256 = "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c"
CHECKER_SHA256 = "25bc78ea79586e33531820ebdbfed426af1451cc7750cdb59dc0a4a8143ab9f9"
DELTA_SHA256 = "2c545102fe3a2be68c5ddc582b622d7a579ef1e8c221512ed08b194f6b14997d"
INPUT_GLOSSARY_SHA256 = "933c064ca77fe92a19742e4df72b088bd81e3db9ff8db62740516a6389478d6d"
OUTPUT_GLOSSARY_SHA256 = "08c3af159fbad0acf050d175e615db334dede9c1747a66a59962f4e199d5f51c"
FIELDS = ("source_term", "target_term", "status", "scope", "note")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise SystemExit(f"non-canonical UTF-8/LF file: {path}")
    data.decode("utf-8", errors="strict")
    return data


def parse_csv(data: bytes, label: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise SystemExit(f"{label} field drift: {reader.fieldnames!r}")
    rows = list(reader)
    terms = [row["source_term"] for row in rows]
    if len(terms) != len(set(terms)):
        raise SystemExit(f"duplicate source_term in {label}")
    return rows


def encode_csv(rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    output.write(",".join(FIELDS) + "\n")
    writer = csv.DictWriter(
        output,
        fieldnames=FIELDS,
        quoting=csv.QUOTE_ALL,
        lineterminator="\n",
    )
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def merge_terms(
    glossary_rows: list[dict[str, str]], delta_rows: list[dict[str, str]]
) -> tuple[list[dict[str, str]], int, int]:
    merged = [dict(row) for row in glossary_rows]
    positions = {row["source_term"]: index for index, row in enumerate(merged)}
    retained = 0
    added = 0
    for delta in delta_rows:
        term = delta["source_term"]
        target = delta["target_term"]
        if term in positions:
            row = merged[positions[term]]
            if row["target_term"] != target:
                raise SystemExit(
                    f"terminology conflict for {term!r}: "
                    f"{row['target_term']!r} != {target!r}"
                )
            if row["status"] != "admitted":
                row["status"] = "admitted"
            retained += 1
            continue
        admitted = dict(delta)
        admitted["status"] = "admitted"
        positions[term] = len(merged)
        merged.append(admitted)
        added += 1
    return merged, retained, added


def replace_exact(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".chapter5-promote.tmp")
    if temporary.exists():
        raise SystemExit(f"stale promotion temporary exists: {temporary}")
    temporary.write_bytes(data)
    if strict_bytes(temporary) != data:
        raise SystemExit(f"temporary write verification failed: {temporary}")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    candidate_data = strict_bytes(CANDIDATE)
    checker_data = strict_bytes(CHECKER)
    delta_data = strict_bytes(DELTA)
    if digest(candidate_data) != CANDIDATE_SHA256:
        raise SystemExit("complete Chapter 5 candidate identity drift")
    if digest(checker_data) != CHECKER_SHA256:
        raise SystemExit("complete Chapter 5 checker identity drift")
    if digest(delta_data) != DELTA_SHA256:
        raise SystemExit("Chapter 5 terminology delta identity drift")

    canonical_data = strict_bytes(CANONICAL)
    glossary_data = strict_bytes(GLOSSARY)
    canonical_sha = digest(canonical_data)
    glossary_sha = digest(glossary_data)
    if canonical_sha not in (AUTHORITY_SHA256, CANDIDATE_SHA256):
        raise SystemExit("canonical chapter5.tex is neither frozen authority nor candidate")
    allowed_glossary_hashes = {INPUT_GLOSSARY_SHA256}
    if not OUTPUT_GLOSSARY_SHA256.startswith("__"):
        allowed_glossary_hashes.add(OUTPUT_GLOSSARY_SHA256)
    if glossary_sha not in allowed_glossary_hashes:
        raise SystemExit("shared glossary identity drift")

    glossary_rows = parse_csv(glossary_data, "shared glossary")
    delta_rows = parse_csv(delta_data, "Chapter 5 terminology delta")
    if len(glossary_rows) not in (524, 543) or len(delta_rows) != 22:
        raise SystemExit("terminology row-count drift")
    merged_rows, retained, added = merge_terms(glossary_rows, delta_rows)
    merged_data = encode_csv(merged_rows)
    merged_sha = digest(merged_data)
    if not OUTPUT_GLOSSARY_SHA256.startswith("__") and merged_sha != OUTPUT_GLOSSARY_SHA256:
        raise SystemExit("deterministic merged glossary identity drift")

    print(
        f"PLAN: canonical {canonical_sha} -> {CANDIDATE_SHA256}; "
        f"glossary {glossary_sha} -> {merged_sha}; "
        f"rows {len(glossary_rows)} -> {len(merged_rows)}; "
        f"delta retained={retained}, added={added}"
    )
    if args.dry_run:
        return
    if glossary_data != merged_data:
        replace_exact(GLOSSARY, merged_data)
    if canonical_data != candidate_data:
        replace_exact(CANONICAL, candidate_data)
    if digest(strict_bytes(GLOSSARY)) != merged_sha:
        raise SystemExit("post-promotion glossary verification failed")
    if digest(strict_bytes(CANONICAL)) != CANDIDATE_SHA256:
        raise SystemExit("post-promotion canonical Chapter 5 verification failed")
    print("PROMOTED: complete Chapter 5 and merged terminology delta")


if __name__ == "__main__":
    main()
