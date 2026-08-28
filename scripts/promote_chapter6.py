#!/usr/bin/env python3
"""Idempotently promote complete Chapter 6 and merge its terminology once."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex"
CANONICAL = ROOT / "repo/source/chapter6.tex"
CANDIDATE = ROOT / "build/chapter6-batch-candidate/chapter6-complete-id.tex"
CHECKER = ROOT / "build/chapter6-batch-candidate/check_chapter6_complete.py"
DELTAS = (
    ROOT / "build/chapter6-batch-candidate/terminology-delta.csv",
    ROOT / "build/chapter6-batch-candidate/terminology-delta-0338-0973.csv",
    ROOT / "build/chapter6-batch-candidate/terminology-delta-0974-1663.csv",
)
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"

AUTHORITY_SHA256 = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
CANDIDATE_SHA256 = "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14"
CHECKER_SHA256 = "d19acd54cd5bb96abe66fe678c8d5a8070fb6de5d681b8a81d6bc0c9c5001a86"
DELTA_SHA256 = (
    "b32f373bd5b96f8422f3667e92217ca60097e8876d0524d35eac03fb8a3b9d22",
    "bbe7f365bd15444395cd11076bec2e83d82efbfa969f01b4452aa8d523fc2027",
    "99dc3522c253f863206e3d13cd395392cd49981e00ad89062acfb48d83b38cbc",
)
INPUT_GLOSSARY_SHA256 = "08c3af159fbad0acf050d175e615db334dede9c1747a66a59962f4e199d5f51c"
OUTPUT_GLOSSARY_SHA256 = "92b6aa981d5631ecb4b57379b7f38b7f3ed8f63c70bc12d05ed206550823c342"
FIELDS = ("source_term", "target_term", "status", "scope", "note")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(path: Path) -> bytes:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise RuntimeError(f"noncanonical UTF-8/LF file: {path}")
    data.decode("utf-8", errors="strict")
    return data


def rows(data: bytes, label: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if tuple(reader.fieldnames or ()) != FIELDS:
        raise RuntimeError(f"{label} field drift")
    result = list(reader)
    keys = [item["source_term"] for item in result]
    if len(keys) != len(set(keys)):
        raise RuntimeError(f"duplicate source_term in {label}")
    return result


def encode(items: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    output.write(",".join(FIELDS) + "\n")
    writer = csv.DictWriter(output, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(items)
    return output.getvalue().encode("utf-8")


def replace(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".chapter6-promote.tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary: {temporary}")
    temporary.write_bytes(data)
    if strict(temporary) != data:
        raise RuntimeError(f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if digest(strict(AUTHORITY)) != AUTHORITY_SHA256:
        raise RuntimeError("authority drift")
    candidate = strict(CANDIDATE)
    if digest(candidate) != CANDIDATE_SHA256:
        raise RuntimeError("candidate drift")
    if digest(strict(CHECKER)) != CHECKER_SHA256:
        raise RuntimeError("checker drift")
    for path, expected in zip(DELTAS, DELTA_SHA256):
        if digest(strict(path)) != expected:
            raise RuntimeError(f"terminology delta drift: {path.name}")
    check = subprocess.run(["python", str(CHECKER)], cwd=ROOT, check=False)
    if check.returncode:
        raise RuntimeError("complete Chapter 6 checker failed")

    canonical = strict(CANONICAL)
    if digest(canonical) not in {AUTHORITY_SHA256, CANDIDATE_SHA256}:
        raise RuntimeError("canonical Chapter 6 is neither authority nor candidate")
    glossary = strict(GLOSSARY)
    if digest(glossary) not in {INPUT_GLOSSARY_SHA256, OUTPUT_GLOSSARY_SHA256}:
        raise RuntimeError("shared glossary drift")
    merged = [dict(item) for item in rows(glossary, "glossary")]
    positions = {item["source_term"]: index for index, item in enumerate(merged)}
    retained = added = 0
    for path in DELTAS:
        for delta in rows(strict(path), path.name):
            term = delta["source_term"]
            if term in positions:
                current = merged[positions[term]]
                if current["target_term"] != delta["target_term"]:
                    raise RuntimeError(f"terminology conflict: {term}")
                current["status"] = "admitted"
                retained += 1
            else:
                item = dict(delta)
                item["status"] = "admitted"
                positions[term] = len(merged)
                merged.append(item)
                added += 1
    output = encode(merged)
    if digest(output) != OUTPUT_GLOSSARY_SHA256 or len(merged) != 591:
        raise RuntimeError("deterministic merged glossary drift")
    print(
        f"PLAN: chapter6 {digest(canonical)} -> {CANDIDATE_SHA256}; glossary "
        f"{digest(glossary)} -> {OUTPUT_GLOSSARY_SHA256}; rows {len(rows(glossary, 'glossary'))} "
        f"-> {len(merged)}; retained={retained}; added={added}"
    )
    if args.dry_run:
        return
    if glossary != output:
        replace(GLOSSARY, output)
    if canonical != candidate:
        replace(CANONICAL, candidate)
    if digest(strict(GLOSSARY)) != OUTPUT_GLOSSARY_SHA256 or digest(strict(CANONICAL)) != CANDIDATE_SHA256:
        raise RuntimeError("post-promotion verification failed")
    print("PROMOTED: complete Chapter 6 and terminology")


if __name__ == "__main__":
    main()
