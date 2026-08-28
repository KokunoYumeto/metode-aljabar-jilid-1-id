#!/usr/bin/env python3
"""Fail-closed promotion of complete Li Chapters 7–10 and one glossary merge."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "build/li-final-batch-candidate/ADMISSION_INPUTS.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
FIELDS = ("source_term", "target_term", "status", "scope", "note")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def strict(path: Path) -> bytes:
    payload = path.read_bytes()
    if payload.startswith(b"\xef\xbb\xbf") or b"\r" in payload:
        raise RuntimeError(f"noncanonical UTF-8/LF file: {path}")
    payload.decode("utf-8", errors="strict")
    return payload


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def csv_rows(payload: bytes, label: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    require(tuple(reader.fieldnames or ()) == FIELDS, f"CSV field drift: {label}")
    result = list(reader)
    keys = [item["source_term"].casefold() for item in result]
    require(len(keys) == len(set(keys)), f"duplicate source term: {label}")
    return result


def encode(items: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    output.write(",".join(FIELDS) + "\n")
    writer = csv.DictWriter(output, fieldnames=FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(items)
    return output.getvalue().encode("utf-8")


def replace(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".li-final-promote.tmp")
    require(not temporary.exists(), f"stale temporary: {temporary}")
    temporary.write_bytes(payload)
    require(strict(temporary) == payload, f"temporary verification failed: {temporary}")
    os.replace(temporary, path)


def checked(relative: str, expected_bytes: int, expected_sha: str) -> bytes:
    path = ROOT / relative
    require(path.is_file(), f"missing admission input: {relative}")
    payload = strict(path)
    require(len(payload) == expected_bytes and sha(payload) == expected_sha,
            f"admission input identity drift: {relative}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("schema") == "o013.li-final-chapters-admission.v1", "manifest schema drift")
    require(manifest.get("authority_commit") == "c4f7a01f68f5f407906b4b970640cddbbad85f6b", "authority commit drift")
    entries = manifest.get("chapters", [])
    require([item.get("chapter") for item in entries] == [7, 8, 9, 10], "chapter closure/order drift")

    glossary_payload = strict(GLOSSARY)
    require(sha(glossary_payload) == manifest.get("input_glossary_sha256"), "input glossary drift")
    merged = [dict(item) for item in csv_rows(glossary_payload, "controlled glossary")]
    positions = {item["source_term"].casefold(): index for index, item in enumerate(merged)}
    candidates: dict[Path, bytes] = {}
    retained = added = 0

    for item in entries:
        authority = checked(item["authority_path"], item["authority_bytes"], item["authority_sha256"])
        candidate = checked(item["candidate_path"], item["candidate_bytes"], item["candidate_sha256"])
        checked(item["checker_path"], item["checker_bytes"], item["checker_sha256"])
        delta_payload = checked(item["delta_path"], item["delta_bytes"], item["delta_sha256"])
        result = subprocess.run(["python", str(ROOT / item["checker_path"])], cwd=ROOT, check=False)
        require(result.returncode == 0, f"candidate checker failed: Chapter {item['chapter']}")
        canonical = ROOT / item["canonical_path"]
        canonical_payload = strict(canonical)
        require(sha(canonical_payload) in {sha(authority), sha(candidate)},
                f"canonical is neither authority nor candidate: Chapter {item['chapter']}")
        candidates[canonical] = candidate
        for delta in csv_rows(delta_payload, item["delta_path"]):
            key = delta["source_term"].casefold()
            if key in positions:
                current = merged[positions[key]]
                require(current["target_term"].casefold() == delta["target_term"].casefold(),
                        f"terminology conflict for {delta['source_term']!r}: {current['target_term']!r} != {delta['target_term']!r}")
                current["status"] = "admitted"
                retained += 1
            else:
                row = dict(delta)
                row["status"] = "admitted"
                positions[key] = len(merged)
                merged.append(row)
                added += 1

    output_glossary = encode(merged)
    require(sha(output_glossary) == manifest.get("output_glossary_sha256"), "merged glossary hash drift")
    require(len(merged) == manifest.get("output_glossary_rows"), "merged glossary row-count drift")
    print(json.dumps({
        "result": "PASS_DRY_RUN" if args.dry_run else "PASS_PROMOTED",
        "chapters": [7, 8, 9, 10],
        "glossary_input_rows": len(csv_rows(glossary_payload, "controlled glossary")),
        "glossary_output_rows": len(merged),
        "retained_terms": retained,
        "added_terms": added,
        "output_glossary_sha256": sha(output_glossary),
    }, indent=2))
    if args.dry_run:
        return 0
    for path, payload in candidates.items():
        if strict(path) != payload:
            replace(path, payload)
    if strict(GLOSSARY) != output_glossary:
        replace(GLOSSARY, output_glossary)
    for path, payload in candidates.items():
        require(strict(path) == payload, f"post-promotion drift: {path.name}")
    require(strict(GLOSSARY) == output_glossary, "post-promotion glossary drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
