#!/usr/bin/env python3
"""Fail-closed durable transition: public complete Chapter 6 -> Chapter 7."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_COMMIT = "9b5fb65446413db03e9f6a877a92d622ef8b577e"
RECEIPT_COMMIT = "9831714187f74b8cc0ff9bc4e9ddc1e8041f5a1a"
RELEASE_PREP_COMMIT = "8176740c69faa6f24c8c5052ad94655fe75d846a"


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def exact(relative: str, size: int, checksum: str) -> dict[str, object]:
    path = ROOT / relative
    require(path.is_file(), f"missing control input: {relative}")
    require(path.stat().st_size == size, f"byte count drifted: {relative}")
    require(sha(path) == checksum, f"SHA-256 drifted: {relative}")
    return {"path": relative, "bytes": size, "sha256": checksum}


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write_json(relative: str, value: object) -> None:
    (ROOT / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )


def append_once(relative: str, marker: str, block: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8", newline="\n")


def append_jsonl_once(relative: str, event_id: str, record: dict) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if event_id not in text:
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            if text and not text.endswith("\n"):
                stream.write("\n")
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
        text=True, encoding="utf-8", stdout=subprocess.PIPE,
    ).stdout.strip()
    require(head == RELEASE_PREP_COMMIT, f"unexpected repository head: {head}")

    chapter6 = exact("repo/source/chapter6.tex", 193563, "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14")
    chapter6_reader = exact("artifacts/unit-044-bab-6-modul-id.pdf", 465036, "2c493005920fdd757e5786477fdf99b20aced1653348be7a076fa7a829a5c1d3")
    combined_reader = exact("output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf", 6750492, "ff8a1fdb65e36bfa8dbb47dd707c96e10daf2d6bf33363ecd2da6f73f6d2f4cd")
    backend = exact("backend/data/unit-044-bab-6-teori-modul.json", 225398, "aaf3db8135914ca8ceaef457883666da8b2f814833147792b819f0f09c2a5eac")
    backend_validation = exact("qa/unit-044-evidence/backend-validation.json", 2539, "68656b8a7c6a4d6b8ad8ec9c70a113935dc00e02362d15268616239013d970d3")
    admission = exact("qa/UNIT_044_CHAPTER_6_ADMISSION_20260828.md", 4395, "90f6f61464943db541beea28beb1786631dc9c2142d7b1dcd1e3af6e1bde2e7e")
    content_readback = exact("qa/PUBLICATION_GITHUB_UNIT_044_CONTENT_READBACK.json", 19836, "599df8e7aa3e2f65e8835a59d99969eaae4cd17b8fdc28993c95763cc4c118c6")
    release_readback = exact("qa/PUBLICATION_GITHUB_UNIT_044_RELEASE_PREP_READBACK.json", 3419, "da5c75c57cb09db7feb540ae11eaacc7703e2a805246f8a0232534b2ccc8ce3b")
    zenodo_receipt = exact("qa/PUBLICATION_ZENODO_0.8.0_20260828.md", 1710, "1d84281aec56c34e413b7df5c5fb80ac0b44122ffa75e1e128d9792b731dc35d")
    zenodo_readback = exact("qa/ZENODO_0.8.0_PUBLIC_READBACK_20260828.json", 3552, "3b1c7c2bb65ac5e101a15eb2fd77a5268162c11b7a3ad1649d796661fce64d40")

    github_public = load("qa/PUBLICATION_GITHUB_UNIT_044_CONTENT_READBACK.json")
    require(github_public.get("commit") == CONTENT_COMMIT and github_public.get("all_match") is True,
            "Chapter 6 GitHub content readback is not the expected PASS")
    zenodo_public = load("qa/ZENODO_0.8.0_PUBLIC_READBACK_20260828.json")
    require(zenodo_public.get("result") == "PASS" and zenodo_public.get("total_bytes") == 75934888,
            "Zenodo public readback is not the expected PASS")

    boundary = {
        "id": "unit-044-complete-chapter-6",
        "component": "li-volume-1-complete",
        "source": "chapter6.tex:1-1994",
        "authority_records": 1994,
        "authority_bytes": 160950,
        "authority_sha256": "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49",
        "target": chapter6,
        "chapter_reader": {**chapter6_reader, "pages": 75},
        "combined_reader_through_chapter_6": {**combined_reader, "pages": 460},
        "backend": backend,
        "backend_validation": backend_validation,
        "admission_receipt": admission,
        "content_commit": CONTENT_COMMIT,
        "content_tree": "e6d75ec61a697ecb5667378d246a286eb7c18d79",
        "content_readback": content_readback,
        "content_readback_paths": 46,
        "content_readback_bytes": 8857965,
        "receipt_commit": RECEIPT_COMMIT,
        "receipt_tree": "f0ed69cb0765680aa28c157ae837ae343ccb791b",
        "release_prep_commit": RELEASE_PREP_COMMIT,
        "release_prep_tree": "ce1bb5cf203a70d2f934e3c44425fd83408211cf",
        "release_prep_readback": release_readback,
        "zenodo_record_id": 22150334,
        "zenodo_doi": "10.5281/zenodo.22150334",
        "zenodo_concept_doi": "10.5281/zenodo.22059759",
        "zenodo_public_bytes": 75934888,
        "zenodo_receipt": zenodo_receipt,
        "zenodo_readback": zenodo_readback,
        "state": "public_github_and_zenodo_anonymous_full_byte_readback_passed",
        "coverage": "complete prelude and complete Li Chapters 1-6",
        "model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    next_cursor = {
        "immediate_action": "Finish and integrate complete Chapter 7 in source order, then Chapters 8-10 in chapter-sized translation batches. Run one bounded deterministic gate per substantial chapter boundary; do not reopen passing Chapter 6 QA.",
        "next_admission_unit": "chapter-7-complete-field-theory",
        "next_admission_source": "chapter7.tex:1-1224",
        "next_authority_bytes": 111676,
        "next_authority_sha256": "18c0f3c91db7f3e4d73fb0b79e4bc719f70475e83af3123f4b0dd0fd4e2ccee6",
        "parallel_translation": "complete Chapters 7-9 are in isolated chapter-level production",
        "cursor_after_li": "complete Duncan, six selected repaired CRing spans, and separate connective/mastery layer",
        "terminal_scope": "all Li Volume 1, complete Duncan, six selected repaired CRing spans, and separate connective/mastery layer",
    }

    cursor = load("00_control/CURRENT_CURSOR.json")
    cursor["updated"] = "2026-08-28"
    cursor["li_authority"] = {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_path": "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter7.tex",
        "source_records": 1224,
        "source_bytes": 111676,
        "source_sha256": "18c0f3c91db7f3e4d73fb0b79e4bc719f70475e83af3123f4b0dd0fd4e2ccee6",
    }
    cursor["last_admitted_unit"] = boundary
    cursor["next_cursor"] = next_cursor
    write_json("00_control/CURRENT_CURSOR.json", cursor)

    recovery = load("00_control/RECOVERY_POINTER.json")
    recovery["updated"] = "2026-08-28"
    recovery["current_boundary"] = boundary
    recovery["next_cursor"] = next_cursor
    recovery["publication_resume"] = {
        "github": f"Complete Chapter 6 content commit {CONTENT_COMMIT}, receipt commit {RECEIPT_COMMIT}, and release-prep commit {RELEASE_PREP_COMMIT} passed anonymous readback. Do not duplicate the repository or lineage.",
        "zenodo": "Version 0.8.0 is public at DOI 10.5281/zenodo.22150334 under concept DOI 10.5281/zenodo.22059759. All five files / 75934888 bytes passed anonymous SHA-256 readback. Do not create a duplicate concept.",
        "figshare": "Retain the existing item only; mixed component rights require the established metadata/link route rather than false-license byte mirroring.",
        "next": "Integrate and publish complete Chapter 7, then continue Chapters 8-10 without reopening Chapter 6.",
    }
    write_json("00_control/RECOVERY_POINTER.json", recovery)

    state = {
        "schema_version": 3,
        "updated": "2026-08-28",
        "state": "published_reader_filename_primary_v0_8_0_anonymous_full_byte_readback_pass",
        "record_id": 22150334,
        "concept_record_id": 22059759,
        "doi": "10.5281/zenodo.22150334",
        "concept_doi": "10.5281/zenodo.22059759",
        "public_url": "https://zenodo.org/records/22150334",
        "version": "0.8.0",
        "title": "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia",
        "edition_commit": RELEASE_PREP_COMMIT,
        "checkpoint_content_commit": CONTENT_COMMIT,
        "status": "partial_public_active",
        "coverage": "Complete prelude and complete Li Chapters 1-6; Chapters 7-10, Duncan, selected CRing spans, and connective/mastery material remain unfinished.",
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        "creator_names": ["Li, Wen-Wei"],
        "contributors": [{"name": "TTP", "type": "ProjectMember"}],
        "independent_nonendorsed": True,
        "access_right": "open",
        "license_metadata": "other-open",
        "language": "ind",
        "publication_date": "2026-08-28",
        "file_count": 5,
        "public_bytes_verified": 75934888,
        "reader_filename_primary": True,
        "api_array_order_is_not_a_presentation_contract": True,
        "anonymous_public_api_readback": True,
        "anonymous_all_file_sha256_readback": True,
        "publication_receipt": zenodo_receipt,
        "metadata_and_file_readback": zenodo_readback,
        "files": zenodo_public["files"],
        "previous_public_record_id": 22149764,
        "previous_public_doi": "10.5281/zenodo.22149764",
        "previous_public_version": "0.7.0",
        "next_action": next_cursor["immediate_action"],
    }
    write_json("00_control/ZENODO_PUBLICATION_STATE.json", state)

    live_block = f"""
## Live cursor after public complete Chapter 6 — 2026-08-28

Complete Chapter 6 is public at GitHub content commit `{CONTENT_COMMIT}`, receipt
commit `{RECEIPT_COMMIT}`, and release-prep commit `{RELEASE_PREP_COMMIT}`. The
460-page combined reader is 6,750,492 bytes, SHA-256
`ff8a1fdb65e36bfa8dbb47dd707c96e10daf2d6bf33363ecd2da6f73f6d2f4cd`.
Zenodo version 0.8.0 is public in the existing concept at DOI
`10.5281/zenodo.22150334`; all five files / 75,934,888 bytes passed anonymous
SHA-256 readback.

The next source-order cursor is complete `chapter7.tex:1-1224`; Chapters 7-9
are already in isolated chapter-level translation. Integrate full chapters,
run one bounded gate per substantial boundary, and continue through Chapter 10,
Duncan, the six repaired CRing spans, and the connective/mastery layer. No
intermediate chapter completes the goal.
"""
    append_once("00_control/CURRENT_GOAL_AND_WORKFLOW.md", "## Live cursor after public complete Chapter 6", live_block)
    append_once("00_control/CURRENT_STATE.md", "## Public complete Chapter 6; Chapters 7-9 in production", live_block.replace("## Live cursor after public complete Chapter 6", "## Public complete Chapter 6; Chapters 7-9 in production"))
    append_once("00_control/DECISION_LOG.md", "## D096 — 2026-08-28 — Complete Chapter 6 preserved without reopening QA", f"""
## D096 — 2026-08-28 — Complete Chapter 6 preserved without reopening QA

Publish complete Chapter 6 once at content commit `{CONTENT_COMMIT}` and preserve
the 460-page reader plus compact resumable source/backend package as Zenodo 0.8.0
at DOI `10.5281/zenodo.22150334` in the existing concept. Anonymous readback
proved all five files / 75,934,888 bytes. The API file array is unordered; the
unique `00-` filename remains the deterministic reader-first contract. Advance
directly to complete Chapter 7 and do not reopen the passing Chapter 6 gate.
""")
    append_jsonl_once("00_control/WORKLOG.jsonl", "chapter6_public_zenodo_0_8_0", {
        "date": "2026-08-28", "event": "chapter6_public_zenodo_0_8_0",
        "result": "Complete Chapter 6 public at GitHub content 9b5fb654, receipt 98317141, release-prep 8176740c; Zenodo 0.8.0 DOI 10.5281/zenodo.22150334 in existing concept; five files / 75934888 bytes anonymous SHA-256 readback PASS; next complete Chapter 7."
    })
    append_jsonl_once("00_control/ADVERSE_LEDGER.jsonl", "O013-ADV-0110", {
        "id": "O013-ADV-0110", "date": "2026-08-28", "severity": "P3",
        "surface": "zenodo_public_file_array_order",
        "status": "closed_after_publication_without_byte_or_metadata_change",
        "summary": "Publication succeeded, then the client falsely treated Zenodo API array order as presentation order. The API is unordered; exact five-file inventory and all public bytes passed, the reader is the unique 00-prefixed and only PDF, and the assertion was corrected without republishing."
    })
    print(json.dumps({"result": "PASS", "last_public": "complete Chapter 6", "next": "complete Chapter 7"}, indent=2))


if __name__ == "__main__":
    main()
