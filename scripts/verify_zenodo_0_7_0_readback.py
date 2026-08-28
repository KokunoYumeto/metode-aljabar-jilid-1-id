#!/usr/bin/env python3
"""Anonymously verify the already-public Zenodo 0.7.0 checkpoint.

This is deliberately read-only.  It verifies the existing concept/version,
metadata boundary, exact five-file inventory, and every public file byte
against the immutable final release stage, then writes sanitized evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
RECORD_ID = 22149764
VERSION_DOI = "10.5281/zenodo.22149764"
CONCEPT_DOI = "10.5281/zenodo.22059759"
VERSION = "0.7.0"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
READER = "00-metode-aljabar-jilid-1-id-checkpoint-through-bab-5-reader.pdf"
EXPECTED_NAMES = {
    READER,
    "10-metode-aljabar-jilid-1-id-source-backend-0.7.0.zip",
    "20-LICENSES.md",
    "30-MANIFEST.json",
    "40-SHA256SUMS.txt",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def download_hash(session: requests.Session, url: str) -> tuple[int, str]:
    response = session.get(url, timeout=(30, 300), stream=True)
    require(response.status_code == 200, f"Anonymous download failed: HTTP {response.status_code}")
    value = hashlib.sha256()
    size = 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            size += len(chunk)
            value.update(chunk)
    return size, value.hexdigest()


def selected_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    license_value = metadata.get("license")
    if isinstance(license_value, dict):
        license_value = license_value.get("id")
    return {
        "title": metadata.get("title"),
        "version": metadata.get("version"),
        "publication_date": metadata.get("publication_date"),
        "access_right": metadata.get("access_right"),
        "language": metadata.get("language"),
        "license": license_value,
        "creators": metadata.get("creators"),
        "contributors": metadata.get("contributors"),
        "keywords": metadata.get("keywords"),
        "related_identifiers": metadata.get("related_identifiers"),
        "notes": metadata.get("notes"),
        "resource_type": metadata.get("resource_type"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--metadata-evidence", type=Path, required=True)
    args = parser.parse_args()

    stage = args.stage.resolve()
    zenodo = stage / "zenodo"
    inventory = json.loads((stage / "inventory.json").read_text(encoding="utf-8"))
    require(inventory.get("publication_ready") is True, "Local release stage is not final")
    require(inventory.get("version") == VERSION, "Local release version drifted")
    require(inventory.get("zenodo_version_doi") == VERSION_DOI, "Local DOI drifted")
    local = {item["name"]: item for item in inventory.get("zenodo", [])}
    require(set(local) == EXPECTED_NAMES, f"Local inventory drifted: {sorted(local)}")
    for name, item in local.items():
        path = zenodo / name
        require(path.is_file(), f"Missing local release file: {name}")
        require(path.stat().st_size == item["bytes"], f"Local byte count drifted: {name}")
        require(sha256_file(path) == item["sha256"], f"Local SHA-256 drifted: {name}")

    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": "Codex O013 anonymous Zenodo 0.7.0 verifier"})
    response = session.get(f"https://zenodo.org/api/records/{RECORD_ID}", timeout=(30, 90))
    require(response.status_code == 200, f"Public record readback failed: HTTP {response.status_code}")
    record = response.json()
    require(record.get("id") == RECORD_ID, "Public record ID drifted")
    require(record.get("doi") == VERSION_DOI, "Public DOI drifted")
    require(record.get("conceptdoi") == CONCEPT_DOI, "Public concept DOI drifted")
    metadata = record.get("metadata")
    require(isinstance(metadata, dict), "Public metadata is absent")
    require(metadata.get("title") == TITLE, "Public title drifted")
    require(metadata.get("version") == VERSION, "Public version drifted")
    require(metadata.get("access_right") == "open", "Public access is not open")
    require(metadata.get("language") == "ind", "Public language drifted")
    require([item.get("name") for item in metadata.get("creators", [])] == ["Li, Wen-Wei"],
            "Creator metadata drifted")
    contributors = metadata.get("contributors", [])
    require(sum(item.get("name") == "TTP" for item in contributors) == 1,
            "Expected one organization contributor")
    require("TTP" not in metadata.get("title", "")
            and "TTP" not in metadata.get("description", "")
            and "TTP" not in metadata.get("notes", ""),
            "Organization label leaked into work title or prose metadata")

    public_files = record.get("files")
    require(isinstance(public_files, list), "Public file inventory is absent")
    by_name = {item.get("key"): item for item in public_files}
    require(set(by_name) == EXPECTED_NAMES and len(public_files) == len(EXPECTED_NAMES),
            f"Public inventory drifted: {sorted(by_name)}")
    # Zenodo's API array order is not a presentation contract.  The explicit
    # 00- prefix makes the reader lexicographically first and uniquely primary.
    require(sorted(EXPECTED_NAMES)[0] == READER, "Reader is not filename-primary")

    readback: list[dict[str, Any]] = []
    for name in sorted(EXPECTED_NAMES):
        item = by_name[name]
        size, checksum = download_hash(session, item["links"]["self"])
        require(size == local[name]["bytes"], f"Public byte count mismatch: {name}")
        require(checksum == local[name]["sha256"], f"Public SHA-256 mismatch: {name}")
        readback.append({
            "name": name,
            "bytes": size,
            "sha256": checksum,
            "file_id": item.get("id"),
            "anonymous_http_status": 200,
        })

    evidence = {
        "schema_version": "1.0.0",
        "record_id": RECORD_ID,
        "doi": VERSION_DOI,
        "concept_doi": CONCEPT_DOI,
        "version": VERSION,
        "public_url": f"https://zenodo.org/records/{RECORD_ID}",
        "anonymous": True,
        "access_right": "open",
        "reader_filename_primary": True,
        "api_array_order_is_not_used_as_presentation_order": True,
        "file_count": len(readback),
        "total_bytes": sum(item["bytes"] for item in readback),
        "files": readback,
        "metadata": selected_metadata(metadata),
        "result": "PASS",
    }
    metadata_path = args.metadata_evidence
    if not metadata_path.is_absolute():
        metadata_path = ROOT / metadata_path
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    receipt_path = args.receipt
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zenodo publication receipt — version 0.7.0",
        "",
        "Status: **PUBLIC; ANONYMOUS FULL-BYTE READBACK PASS.**",
        "",
        f"- Record: <https://zenodo.org/records/{RECORD_ID}>",
        f"- Version DOI: `{VERSION_DOI}`.",
        f"- Concept DOI: `{CONCEPT_DOI}` (existing lineage; no duplicate concept).",
        "- Access: open.",
        "- Coverage: complete prelude and Li Chapters 1–5; 385-page reader; later corpus components remain unfinished.",
        "- Reader-first convention: the primary reader has the unique `00-` filename prefix. Zenodo's public API returned an unordered file array, so array position was correctly not treated as presentation metadata.",
        "",
        "| File | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for item in readback:
        lines.append(f"| `{item['name']}` | {item['bytes']:,} | `{item['sha256']}` |")
    lines.extend([
        "",
        f"All {len(readback)} public files ({evidence['total_bytes']:,} bytes) were downloaded without credentials and matched the final release stage byte-for-byte.",
        "",
        "Rights remain component-specific: principal text/adaptation CC BY 4.0; Lanzhou image and AJbook fragment CC BY-SA 3.0; Noto OFL 1.1; Fandol GPLv3 with its font exception. The edition is independent and non-endorsed.",
        "",
        "Production provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Source-author and human-contributor credits remain intact.",
    ])
    receipt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({key: evidence[key] for key in (
        "record_id", "doi", "concept_doi", "file_count", "total_bytes", "result"
    )}, indent=2))


if __name__ == "__main__":
    main()
