#!/usr/bin/env python3
"""Fail-closed durable transition: public complete Chapter 5 -> Chapter 6."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT_COMMIT = "77272543e77851dc799215bebbbcefad9c3b05fc"
RECEIPT_COMMIT = "ed841157313e5a57f8dad5c4983c9ae0d54fd54f"


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
    require(head == RECEIPT_COMMIT, f"unexpected repository head: {head}")

    chapter5 = exact("repo/source/chapter5.tex", 156081, "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c")
    chapter5_reader = exact("artifacts/unit-043-bab-5-pengantar-teori-gelanggang-id.pdf", 714227, "08fc765af88eea5bb1cb2181223c4217cbeee17a5ec28621cb79193491196762")
    combined_reader = exact("output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-5-reader.pdf", 6133398, "44f866552abbd52dfc17ed942fb291c9b58457d7452c409ec7808a48a3318bc4")
    backend = exact("backend/data/unit-043-bab-5-pengantar-teori-gelanggang.json", 226984, "50fe8288e70ae62f378a5f4091f8e5d337c450db9fe3fd2c531abd0bfeab6061")
    backend_validation = exact("qa/unit-043-evidence/backend-validation.json", 3131, "22bced23609b160b30c3c6af1b67d3cca48a4d381e0406f392c80b015b854717")
    admission = exact("qa/UNIT_043_CHAPTER_5_ADMISSION_20260828.md", 5521, "29c56a6148c480553639d5e3304afb2a79809a410d73c8c8770085b484b33f87")
    receipt_readback = exact("qa/PUBLICATION_GITHUB_UNIT_043_RECEIPT_READBACK.json", 3187, "564f21b04c12c95a7853753d2af67f95d93c9ff9c300a9286cafbd0a47a9d351")
    zenodo_receipt = exact("qa/PUBLICATION_ZENODO_0.7.0_20260828.md", 1734, "4e03fdfd5faf09f6541b5b7692846c25bac131e9547885a3855d044cd082f4e4")
    zenodo_readback = exact("qa/ZENODO_0.7.0_PUBLIC_READBACK_20260828.json", 3530, "c4614ffd8e527427abd48a5da437bf9724c68f9e88a485eae2b03c311212f0df")
    chapter6 = exact("build/chapter6-batch-candidate/chapter6-complete-id.tex", 193563, "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14")
    chapter6_checker = exact("build/chapter6-batch-candidate/check_chapter6_complete.py", 4866, "d19acd54cd5bb96abe66fe678c8d5a8070fb6de5d681b8a81d6bc0c9c5001a86")

    public = load("qa/ZENODO_0.7.0_PUBLIC_READBACK_20260828.json")
    require(public.get("result") == "PASS" and public.get("total_bytes") == 75149703,
            "Zenodo public readback is not the expected PASS")

    boundary = {
        "id": "unit-043-complete-chapter-5",
        "component": "li-volume-1-complete",
        "source": "chapter5.tex:1-1382",
        "authority_records": 1382,
        "authority_bytes": 122998,
        "authority_sha256": "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143",
        "target": chapter5,
        "chapter_reader": chapter5_reader,
        "combined_reader_through_chapter_5": {**combined_reader, "pages": 385},
        "backend": backend,
        "backend_validation": backend_validation,
        "admission_receipt": admission,
        "content_commit": CONTENT_COMMIT,
        "content_tree": "f7505b3dceb651adce89f6c0637e38b4df002e05",
        "content_readback_paths": 71,
        "content_readback_bytes": 18916874,
        "receipt_commit": RECEIPT_COMMIT,
        "receipt_tree": "078c3c705d43c1380248cf66c9f0a70135bc0674",
        "receipt_readback": receipt_readback,
        "zenodo_record_id": 22149764,
        "zenodo_doi": "10.5281/zenodo.22149764",
        "zenodo_concept_doi": "10.5281/zenodo.22059759",
        "zenodo_public_bytes": 75149703,
        "zenodo_receipt": zenodo_receipt,
        "zenodo_readback": zenodo_readback,
        "state": "public_github_and_zenodo_anonymous_full_byte_readback_passed",
        "coverage": "complete prelude and complete Li Chapters 1-5",
        "model": "OpenAI Codex gpt-5.6-sol, Ultra",
    }
    next_cursor = {
        "immediate_action": "Promote the passing complete Chapter 6 candidate, merge its terminology deltas once, generate one chapter-level backend and reader, run one bounded deterministic gate, publish/read back, then continue complete Chapter 7. Translation remains dominant.",
        "next_admission_unit": "chapter-6-complete-modules",
        "next_admission_source": "chapter6.tex:1-1994",
        "next_authority_bytes": 160950,
        "next_authority_sha256": "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49",
        "next_candidate": chapter6,
        "next_candidate_checker": chapter6_checker,
        "candidate_result": "PASS; all four segment checkers and whole-chapter closure pass; 1994 records, 12 sections, 98 labels, 224 references, 6 citations, 70 indexes, 132 item tokens",
        "cursor_after_next_admission": "chapter7.tex:1",
        "parallel_translation": "complete Chapters 7-9 are in isolated chapter-level production",
        "terminal_scope": "remaining Li Chapters 7-10, complete Duncan, six selected repaired CRing spans, and separate connective/mastery layer",
    }

    cursor = load("00_control/CURRENT_CURSOR.json")
    cursor["updated"] = "2026-08-28"
    cursor["li_authority"] = {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_path": "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex",
        "source_records": 1994,
        "source_bytes": 160950,
        "source_sha256": "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49",
    }
    cursor["last_admitted_unit"] = boundary
    cursor["next_cursor"] = next_cursor
    write_json("00_control/CURRENT_CURSOR.json", cursor)

    recovery = load("00_control/RECOVERY_POINTER.json")
    recovery["updated"] = "2026-08-28"
    recovery["current_boundary"] = boundary
    recovery["next_cursor"] = next_cursor
    recovery["publication_resume"] = {
        "github": f"Complete Chapter 5 content commit {CONTENT_COMMIT} and receipt commit {RECEIPT_COMMIT} passed anonymous byte readback. Do not duplicate the repository or lineage.",
        "zenodo": "Version 0.7.0 is public at DOI 10.5281/zenodo.22149764 under concept DOI 10.5281/zenodo.22059759. All five files / 75149703 bytes passed anonymous SHA-256 readback. Do not create a duplicate concept.",
        "figshare": "Retain the existing item only; mixed component rights require the established metadata/link route rather than false-license byte mirroring.",
        "next": "Promote and publish complete Chapter 6 as one boundary; complete Chapter 7 translation continues in parallel.",
    }
    write_json("00_control/RECOVERY_POINTER.json", recovery)

    state = {
        "schema_version": 3,
        "updated": "2026-08-28",
        "state": "published_reader_filename_primary_v0_7_0_anonymous_full_byte_readback_pass",
        "record_id": 22149764,
        "concept_record_id": 22059759,
        "doi": "10.5281/zenodo.22149764",
        "concept_doi": "10.5281/zenodo.22059759",
        "public_url": "https://zenodo.org/records/22149764",
        "version": "0.7.0",
        "title": "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia",
        "edition_commit": RECEIPT_COMMIT,
        "checkpoint_content_commit": CONTENT_COMMIT,
        "status": "partial_public_active",
        "coverage": "Complete prelude and complete Li Chapters 1-5; Chapters 6-10, Duncan, selected CRing spans, and connective/mastery material remain unfinished.",
        "model_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        "creator_names": ["Li, Wen-Wei"],
        "contributors": [{"name": "TTP", "type": "ProjectMember"}],
        "independent_nonendorsed": True,
        "access_right": "open",
        "license_metadata": "other-open",
        "language": "ind",
        "publication_date": "2026-08-28",
        "file_count": 5,
        "public_bytes_verified": 75149703,
        "reader_filename_primary": True,
        "api_array_order_is_not_a_presentation_contract": True,
        "anonymous_public_api_readback": True,
        "anonymous_all_file_sha256_readback": True,
        "publication_receipt": zenodo_receipt,
        "metadata_and_file_readback": zenodo_readback,
        "files": public["files"],
        "previous_public_record_id": 22088395,
        "previous_public_doi": "10.5281/zenodo.22088395",
        "previous_public_version": "0.6.0",
        "next_action": next_cursor["immediate_action"],
    }
    write_json("00_control/ZENODO_PUBLICATION_STATE.json", state)

    live_block = f"""
## Live cursor after public complete Chapter 5 — 2026-08-28

Complete Chapter 5 is public at content commit `{CONTENT_COMMIT}` and receipt
commit `{RECEIPT_COMMIT}`. The 385-page combined reader is 6,133,398 bytes,
SHA-256 `44f866552abbd52dfc17ed942fb291c9b58457d7452c409ec7808a48a3318bc4`.
Zenodo version 0.7.0 is public in the existing concept at DOI
`10.5281/zenodo.22149764`; all five files / 75,149,703 bytes passed anonymous
SHA-256 readback.

Complete Chapter 6 is now a passing 1,994-record isolated candidate at
`build/chapter6-batch-candidate/chapter6-complete-id.tex`, 193,563 bytes,
SHA-256 `15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14`.
All four segment checkers and the whole-chapter closure checker pass. Promote,
index, build, and publish it as one chapter boundary. Chapters 7-9 are being
translated in parallel. The terminal condition remains all Li, complete
Duncan, six selected repaired CRing spans, and the separate connective/mastery
layer; no intermediate chapter completes the goal.
"""
    append_once("00_control/CURRENT_GOAL_AND_WORKFLOW.md", "## Live cursor after public complete Chapter 5", live_block)
    append_once("00_control/CURRENT_STATE.md", "## Public complete Chapter 5 and passing complete Chapter 6 candidate", live_block.replace("## Live cursor after public complete Chapter 5", "## Public complete Chapter 5 and passing complete Chapter 6 candidate"))

    append_once("00_control/DECISION_LOG.md", "## D094 — 2026-08-28 — Complete Chapter 5 preserved in existing Zenodo lineage", f"""
## D094 — 2026-08-28 — Complete Chapter 5 preserved in existing Zenodo lineage

Publish complete Chapter 5 once at GitHub content commit `{CONTENT_COMMIT}` and
receipt commit `{RECEIPT_COMMIT}`, then preserve the 385-page reader and compact
resumable source/backend package as Zenodo 0.7.0 at DOI
`10.5281/zenodo.22149764` under the existing concept. Anonymous readback proves
all five files / 75,149,703 bytes. Zenodo's API array order is not presentation
metadata; the unique `00-` filename makes the reader filename-primary. Advance
to complete Chapter 6 without reopening Chapter 5 QA.
""")
    append_once("00_control/DECISION_LOG.md", "## D095 — 2026-08-28 — Chapter 6 remains one production boundary", """
## D095 — 2026-08-28 — Chapter 6 remains one production boundary

The four contiguous Chapter 6 translations assemble to one 1,994-record
candidate. A real duplicate-paragraph/math-token assembly defect was corrected
once; all four segment checkers and the whole-chapter closure now pass. Promote,
backend-index, build, visually inspect, and publish Chapter 6 once rather than
returning to microscopic unit ceremonies.
""")
    append_jsonl_once("00_control/WORKLOG.jsonl", "chapter5_public_zenodo_0_7_0", {
        "date": "2026-08-28", "event": "chapter5_public_zenodo_0_7_0",
        "result": "Complete Chapter 5 public at GitHub content 77272543 and receipt ed841157; Zenodo 0.7.0 DOI 10.5281/zenodo.22149764 in existing concept; five files / 75149703 bytes anonymous SHA-256 readback PASS; next complete Chapter 6."
    })
    append_jsonl_once("00_control/WORKLOG.jsonl", "chapter6_complete_translation_candidate", {
        "date": "2026-08-28", "event": "chapter6_complete_translation_candidate",
        "result": "Complete 1994-record Chapter 6 Indonesian candidate 193563 bytes SHA-256 15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14; four segment checkers plus whole-chapter closure PASS; ready for single chapter promotion/build/backend/publication gate."
    })
    append_jsonl_once("00_control/ADVERSE_LEDGER.jsonl", "O013-ADV-0109", {
        "id": "O013-ADV-0109", "date": "2026-08-28", "severity": "P2",
        "surface": "li_chapter6_tail_assembly",
        "status": "closed_before_canonical_promotion",
        "summary": "The first Chapter 6 tail assembly duplicated an already translated Hom-matrix consequence and rearranged two protected inline math fragments plus one display order. The duplicate was removed, protected topology restored, assembler made idempotent, and all segment and whole-chapter checks now pass."
    })
    print(json.dumps({"result": "PASS", "last_public": "complete Chapter 5", "next": "complete Chapter 6"}, indent=2))


if __name__ == "__main__":
    main()
