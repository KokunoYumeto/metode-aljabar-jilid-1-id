#!/usr/bin/env python3
"""Reserve exactly one 1.0.0 draft in the existing Zenodo concept lineage."""

from __future__ import annotations

import json
import re
from pathlib import Path

import requests


TOKEN_PATH = Path(r"C:\Users\Floris\Documents\Obsidian notes\New zenodo token.md")
SOURCE_RECORD = 22150334
CONCEPT_RECORD = 22059759
CONCEPT_DOI = "10.5281/zenodo.22059759"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def token() -> str:
    text = TOKEN_PATH.read_text(encoding="utf-8").strip()
    match = re.search(r"([A-Za-z0-9._~-]{20,})", text)
    need(match is not None, "No usable Zenodo token found")
    return match.group(1)


def validate_draft(value: object) -> dict[str, object]:
    need(isinstance(value, dict), "Zenodo draft is not an object")
    draft = value
    draft_id = draft.get("id")
    need(isinstance(draft_id, int), "Zenodo draft lacks an integer ID")
    need(draft.get("state") == "unsubmitted" and not draft.get("submitted"),
         "Zenodo new-version target is not an unsubmitted draft")
    need(str(draft.get("conceptrecid", "")) == str(CONCEPT_RECORD),
         "Zenodo draft left the existing concept lineage")
    metadata = draft.get("metadata")
    need(isinstance(metadata, dict), "Zenodo draft lacks metadata")
    reserved = metadata.get("prereserve_doi")
    need(isinstance(reserved, dict), "Zenodo draft lacks a reserved DOI")
    doi = reserved.get("doi")
    need(doi == f"10.5281/zenodo.{draft_id}", "Reserved DOI does not match draft ID")
    need(str(reserved.get("recid", "")) == str(draft_id), "Reserved DOI record does not match draft ID")
    return {"draft_id": draft_id, "reserved_doi": doi}


def main() -> int:
    anonymous = requests.Session()
    anonymous.trust_env = False
    public = anonymous.get(f"https://zenodo.org/api/records/{SOURCE_RECORD}", timeout=(30, 90))
    need(public.status_code == 200, f"Source record is not public: HTTP {public.status_code}")
    record = public.json()
    need(record.get("conceptdoi") == CONCEPT_DOI, "Source record has the wrong concept DOI")
    need(record.get("metadata", {}).get("version") == "0.8.0", "Source record is no longer version 0.8.0")

    session = requests.Session()
    session.trust_env = False
    session.headers.update({
        "Authorization": f"Bearer {token()}",
        "User-Agent": "Codex O013 Zenodo 1.0.0 reservation client",
    })
    endpoint = f"https://zenodo.org/api/deposit/depositions/{SOURCE_RECORD}/actions/newversion"
    response = session.post(endpoint, timeout=(30, 120))
    if response.status_code in {200, 201, 202}:
        envelope = response.json()
    elif response.status_code == 400:
        source = session.get(f"https://zenodo.org/api/deposit/depositions/{SOURCE_RECORD}", timeout=(30, 90))
        need(source.status_code == 200, f"Cannot resolve existing new-version draft: HTTP {source.status_code}")
        envelope = source.json()
    else:
        raise RuntimeError(f"Zenodo newversion failed: HTTP {response.status_code}")
    links = envelope.get("links", {}) if isinstance(envelope, dict) else {}
    latest = links.get("latest_draft") if isinstance(links, dict) else None
    if latest:
        fetched = session.get(latest, timeout=(30, 90))
        need(fetched.status_code == 200, f"Cannot read latest draft: HTTP {fetched.status_code}")
        envelope = fetched.json()
    result = validate_draft(envelope)
    print(json.dumps({**result, "concept_doi": CONCEPT_DOI, "source_record": SOURCE_RECORD, "state": "unsubmitted"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
