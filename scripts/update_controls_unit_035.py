#!/usr/bin/env python3
"""Advance the durable O013 controls from public Unit 034 to public Unit 035.

This is a bounded, fail-closed transition. It verifies the exact pre-transition
control hashes, updates the two structured cursors, and appends one concise
state/decision/work record. It performs no Git or network operation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "00_control"
BASE = {
    "CURRENT_GOAL_AND_WORKFLOW.md": "1334c0bbf333980aa1d1e02e25a138e4153b92ba5aab90c9e5224f8945ca417d",
    "CURRENT_STATE.md": "023505b7d82bba442f8e8db7c86b5513e6c156dc1467e16e3ad3d1dc1cbe3128",
    "CURRENT_CURSOR.json": "44e4cc5e1346024c40a1e4d14959660836883bbcfbf9196abf3ec76c6b3dae63",
    "RECOVERY_POINTER.json": "997420de0ec587f7597d0fb82d598eb4725c18bb5add0699c08efa08b2425973",
    "DECISION_LOG.md": "58263380ba41a07b800bf47f3c07b38e3c4f3d53e25cdeb11427e226bdd85d04",
    "WORKLOG.jsonl": "dd037da4172b6a0afaca323713412f4b1efe61145a34b858cee4ab85f2965e27",
    "ADVERSE_LEDGER.jsonl": "bb6c3490ed98e82a256a859e79716bb53013da4cd72616f59a72194ded34686f",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        raise RuntimeError(f"append marker already present before transition: {marker}")
    path.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    cursor_path = CONTROL / "CURRENT_CURSOR.json"
    cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    if cursor.get("last_admitted_unit", {}).get("id") == "unit-035-bab-4-grup-dalam-kategori-dan-latihan":
        print("PASS_ALREADY_APPLIED")
        return 0

    for name, expected in BASE.items():
        actual = digest(CONTROL / name)
        if actual != expected:
            raise RuntimeError(f"base control drift: {name}: {actual}")

    recovery_path = CONTROL / "RECOVERY_POINTER.json"
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    if cursor.get("last_admitted_unit", {}).get("id") != "unit-034-bab-4-limit-dan-kompletisasi-grup":
        raise RuntimeError("CURRENT_CURSOR is not at Unit 034")
    if recovery.get("current_boundary", {}).get("unit") != "unit-034-bab-4-limit-dan-kompletisasi-grup":
        raise RuntimeError("RECOVERY_POINTER is not at Unit 034")

    unit = {
        "id": "unit-035-bab-4-grup-dalam-kategori-dan-latihan",
        "source": "chapter4.tex:1745-1898",
        "source_span_bytes": 14398,
        "source_span_sha256": "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287",
        "source_mapping": "authority lines 1745-1898 map to 154 target records at canonical lines 1740-1893",
        "candidate": "build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex",
        "candidate_bytes": 18089,
        "candidate_sha256": "5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca",
        "target": "repo/source/chapter4.tex:1740-1893",
        "target_full_bytes": 193626,
        "target_full_sha256": "2b682d67292e4c439ccc9f6d46f72d3d0eb7cb5bf8b3a3a5999210c45ef547c5",
        "reader": "artifacts/unit-035-bab-4-grup-dalam-kategori-dan-latihan-id.pdf",
        "reader_pages": 9,
        "reader_bytes": 135943,
        "reader_sha256": "1cf97dd523ae1a8c5185c4b22a8e6b0dab6e7514ab5387c34959c417f4e35442",
        "backend": "backend/data/unit-035-bab-4-grup-dalam-kategori-dan-latihan.json",
        "backend_bytes": 239379,
        "backend_sha256": "372a7dfa2ffc919b7fe5859b020c87f4bd143669331aeed1c0c270c65e9f02a7",
        "backend_validation": "qa/unit-035-evidence/backend-validation.json",
        "backend_validation_bytes": 2495,
        "backend_validation_sha256": "0b5699f7e7f7d576c80379781ec809f7d7f4a9cea008d3e999e0a87925922c88",
        "admission_receipt": "qa/UNIT_035_ADMISSION_20260828.md",
        "admission_receipt_bytes": 4373,
        "admission_receipt_sha256": "8edc8100d11bda120408c8209d5e4bc97de07bac9d744957fc70db4ab7d7ef82",
        "visual_qa": "all 9 pages inspected at once; eight diagrams, complete 26-exercise/36-item/five-hint block, embedded fonts, and safe PDF structure pass; the one wide diagram remains inside the page",
        "corrections": [
            "O013-LI-U035-COR-001 corrects the swapped subgroup/coset family bounds in the Neumann lemma exercise"
        ],
        "component_rights": "principal text/translation CC BY 4.0; AJbook fragment and unused Lanzhou image CC BY-SA 3.0; Noto OFL 1.1; Fandol 0.3 GPLv3 with font exception",
        "content_commit": "d50b8944116b4f40eef7bcd487e0125226b412b8",
        "content_tree": "dbb2b9dc64b5e6191cffd44d846a9acdba3f8445",
        "content_readback_path_fetches": 39,
        "content_readback_bytes": 4306859,
        "content_readback_inventory": "qa/PUBLICATION_GITHUB_UNIT_035_CONTENT_READBACK.json",
        "content_readback_inventory_bytes": 27026,
        "content_readback_inventory_sha256": "53cd5467adb34115a20ebcd7af82c269244ccead44652b5944997e761fa7df04",
        "receipt": "qa/PUBLICATION_GITHUB_UNIT_035_20260828.md",
        "receipt_bytes": 1744,
        "receipt_sha256": "a73369a4f3fb0c2dd4c002fa5b948aff015caff78b74342d46a526cdfa551d92",
        "receipt_commit": "0644fe36d85ceeef6a2f623a4a6831fba8f9ff94",
        "receipt_tree": "9eadd11dc1f57e7b6be0e02b66bb858b62653d6f",
        "receipt_readback_files": 3,
        "receipt_readback_bytes": 113817,
        "receipt_readback_inventory": "qa/PUBLICATION_GITHUB_UNIT_035_RECEIPT_READBACK.json",
        "receipt_readback_inventory_bytes": 3187,
        "receipt_readback_inventory_sha256": "9eb807244550abd1f0c1ca05fb4684e5a102edd15b299f0c92ef0bbb2e007a0d",
        "state": "public_readback_passed; complete Chapter 4",
    }
    chapter5 = {
        "component": "li-volume-1-complete",
        "completed_preservation_action": "Unit 035 content and receipt commits passed anonymous byte readback; complete Chapter 4 is public. Zenodo remains the nonduplicative 0.6.0 checkpoint pending the next substantial whole-reader checkpoint.",
        "next_admission_unit": "chapter-5-complete-bab-5-dasar-teori-gelanggang",
        "source_path": "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex",
        "source_line_start": 1,
        "source_line_end": 1382,
        "source_span_bytes": 122998,
        "source_span_sha256": "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143",
        "candidate_path": "build/unit-043-candidate/chapter5-complete-id.tex",
        "candidate_bytes": 156081,
        "candidate_sha256": "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c",
        "candidate_checker": "build/unit-043-candidate/check_chapter5_complete.py",
        "candidate_checker_bytes": 8694,
        "candidate_checker_sha256": "25bc78ea79586e33531820ebdbfed426af1451cc7750cdb59dc0a4a8143ab9f9",
        "terminology_delta": "build/unit-043-candidate/CHAPTER5_TERMINOLOGY_DELTA.id-ID.csv",
        "terminology_delta_rows": 22,
        "terminology_delta_bytes": 3197,
        "terminology_delta_sha256": "2c545102fe3a2be68c5ddc582b622d7a579ef1e8c221512ed08b194f6b14997d",
        "next_source_cursor": "chapter6.tex:1",
        "chapter": "Chapter 5 - foundations of ring theory",
        "parallel_translation": "Chapter 6 lines 1-337 are translated in build/chapter6-batch-candidate/chapter6-lines-0001-0337-id.tex, 28906 bytes / SHA-256 55d99163b73efef90d6a28ebe6a96faff4b68018e7ec5f04212d530cb80fee34; its next isolated cursor is chapter6.tex:338",
        "rule": "Promote and publish the complete Chapter 5 as one meaningful boundary with one terminology merge and one deterministic build/backend/visual gate; do not recreate Units 036-043 as separate publication ceremonies.",
    }

    cursor["updated"] = "2026-08-28"
    cursor["last_admitted_unit"] = unit
    cursor["next_source_boundary"] = chapter5
    publication = cursor["publication"]
    publication.update({
        "expected_remote_base": "0644fe36d85ceeef6a2f623a4a6831fba8f9ff94",
        "last_public_unit": unit["id"],
        "unit_035_content_commit": unit["content_commit"],
        "unit_035_content_tree": unit["content_tree"],
        "unit_035_public_readback_files": unit["content_readback_path_fetches"],
        "unit_035_public_readback_bytes": unit["content_readback_bytes"],
        "unit_035_content_readback": unit["content_readback_inventory"],
        "unit_035_content_readback_bytes": unit["content_readback_inventory_bytes"],
        "unit_035_content_readback_sha256": unit["content_readback_inventory_sha256"],
        "unit_035_receipt": unit["receipt"],
        "unit_035_receipt_bytes": unit["receipt_bytes"],
        "unit_035_receipt_sha256": unit["receipt_sha256"],
        "unit_035_receipt_commit": unit["receipt_commit"],
        "unit_035_receipt_tree": unit["receipt_tree"],
        "unit_035_receipt_readback_files": unit["receipt_readback_files"],
        "unit_035_receipt_readback_bytes": unit["receipt_readback_bytes"],
        "unit_035_receipt_readback_inventory": unit["receipt_readback_inventory"],
        "unit_035_receipt_readback_inventory_bytes": unit["receipt_readback_inventory_bytes"],
        "unit_035_receipt_readback_inventory_sha256": unit["receipt_readback_inventory_sha256"],
        "unit_035_state": "complete Chapter 4 public; content and receipt anonymous readback passed",
    })
    cursor["next_action"] = "Promote the already-passing complete Chapter 5 candidate in one batch, merge its 22-row terminology delta, generate one chapter-level reader/backend, run one bounded deterministic gate, publish/read back, and continue Chapter 6 from the already-translated lines 1-337 candidate. The full Li/Duncan/CRing/connective-mastery goal remains active."

    recovery["updated"] = "2026-08-28"
    recovery_unit = dict(unit)
    recovery_unit["unit"] = recovery_unit.pop("id")
    recovery_unit["pdf"] = recovery_unit.pop("reader")
    recovery_unit["pdf_pages"] = recovery_unit.pop("reader_pages")
    recovery_unit["pdf_bytes"] = recovery_unit.pop("reader_bytes")
    recovery_unit["pdf_sha256"] = recovery_unit.pop("reader_sha256")
    recovery_unit["model"] = "OpenAI Codex gpt-5.6-sol, Ultra"
    recovery["current_boundary"] = recovery_unit
    recovery["next_cursor"] = {
        "immediate_action": cursor["next_action"],
        "coverage": "complete prelude and Chapters 1-4 public; complete Chapter 5 translated and awaiting one chapter-level production boundary; Chapter 6 lines 1-337 translated in isolation",
        "next_admission_unit": chapter5["next_admission_unit"],
        "next_admission_source": "chapter5.tex:1-1382",
        "next_authority_bytes": chapter5["source_span_bytes"],
        "next_authority_sha256": chapter5["source_span_sha256"],
        "next_candidate": chapter5["candidate_path"],
        "next_candidate_bytes": chapter5["candidate_bytes"],
        "next_candidate_sha256": chapter5["candidate_sha256"],
        "next_candidate_checker": chapter5["candidate_checker"],
        "next_candidate_checker_bytes": chapter5["candidate_checker_bytes"],
        "next_candidate_checker_sha256": chapter5["candidate_checker_sha256"],
        "cursor_after_next_admission": "chapter6.tex:1; isolated translation already covers lines 1-337",
        "post_li_component": "complete admitted Duncan CC BY 4.0 repository, six exact repaired CRing GFDL spans, and separate connective/mastery layer; Etingof reference-only",
    }
    recovery["publication_resume"]["github"] = "Unit 035 completes public Chapter 4. Content commit d50b8944116b4f40eef7bcd487e0125226b412b8 / tree dbb2b9dc64b5e6191cffd44d846a9acdba3f8445 passed 39-path / 4306859-byte anonymous readback. Receipt commit 0644fe36d85ceeef6a2f623a4a6831fba8f9ff94 / tree 9eadd11dc1f57e7b6be0e02b66bb858b62653d6f passed 3-path / 113817-byte anonymous readback. Do not duplicate the repository or publication lineage."

    write_json(cursor_path, cursor)
    write_json(recovery_path, recovery)

    append_once(
        CONTROL / "CURRENT_GOAL_AND_WORKFLOW.md",
        "## Live cursor after complete Chapter 4 — 2026-08-28",
        """## Live cursor after complete Chapter 4 — 2026-08-28

Unit 035 and complete Chapter 4 are public and byte-verified at content commit
`d50b8944116b4f40eef7bcd487e0125226b412b8` and receipt commit
`0644fe36d85ceeef6a2f623a4a6831fba8f9ff94`. Complete Chapter 5 is already a
single passing 1,382-record candidate at
`build/unit-043-candidate/chapter5-complete-id.tex`, 156,081 bytes / SHA-256
`33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c`.
Promote, build, backend-index, and publish it as one chapter boundary rather
than eight unit ceremonies. Chapter 6 lines 1–337 are already translated in
isolation; continue from line 338 in parallel. The complete finite terminal
condition remains all Li, Duncan, six CRing spans, and separate connective and
mastery material built, indexed, and publicly preserved.""",
    )
    append_once(
        CONTROL / "CURRENT_STATE.md",
        "## 2026-08-28 live state — Chapter 4 public; Chapter 5 translation complete",
        """## 2026-08-28 live state — Chapter 4 public; Chapter 5 translation complete

Unit 035 closes Chapter 4 and passed its single source, reader, backend, visual,
publication, and anonymous byte-readback boundary. Content is public at
`d50b8944116b4f40eef7bcd487e0125226b412b8`; its receipt is public at
`0644fe36d85ceeef6a2f623a4a6831fba8f9ff94`.

The complete Chapter 5 authority is 1,382 records / 122,998 bytes / SHA-256
`e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143`.
Its complete Indonesian candidate is 156,081 bytes / SHA-256
`33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c`;
the whole-chapter checker passes with 480 environment markers, 80 labels, 112
references, seven citations, 74 indexes, 112 items, 22 top-level exercises / 31
including subitems, 11 hints, and no source solutions. The 22-row terminology
delta is frozen. The next action is one complete-chapter production boundary.

Chapter 6 lines 1–337 are translated in isolation at 28,906 bytes / SHA-256
`55d99163b73efef90d6a28ebe6a96faff4b68018e7ec5f04212d530cb80fee34`;
the parallel translation cursor is line 338.""",
    )
    append_once(
        CONTROL / "DECISION_LOG.md",
        "## D093 — 2026-08-28 — Complete Chapter 4 public; Chapter 5 becomes one production boundary",
        """## D093 — 2026-08-28 — Complete Chapter 4 public; Chapter 5 becomes one production boundary

Unit 035 and complete Chapter 4 are published and anonymously byte-verified.
The already-passing Units 036–043 have been consolidated, in exact source
order, into one complete 1,382-record Chapter 5 candidate. The production lane
will promote/build/index/publish that chapter once, rather than reproduce the
retired microscopic per-unit cadence. This changes cadence, not mathematical
scope, rights, authority, or the full O013 terminal condition.""",
    )

    work = {
        "date": "2026-08-28",
        "event": "unit_035_published_and_chapter5_batch_ready",
        "result": "Unit035 and complete Chapter4 are public. Content d50b8944116b4f40eef7bcd487e0125226b412b8 / tree dbb2b9dc64b5e6191cffd44d846a9acdba3f8445 passed 39-path / 4306859-byte anonymous readback; receipt 0644fe36d85ceeef6a2f623a4a6831fba8f9ff94 / tree 9eadd11dc1f57e7b6be0e02b66bb858b62653d6f passed 3-path / 113817-byte readback. Complete Chapter5 candidate is 156081 bytes / 33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c and its single whole-chapter checker passes. Chapter6 lines1-337 are translated; full goal remains active.",
    }
    adverse = {
        "id": "O013-ADV-0108",
        "date": "2026-08-28",
        "severity": "P2",
        "surface": "li_unit_035_neumann_lemma_bounds",
        "status": "corrected_and_provenanced_before_publication",
        "summary": "The authority swapped the n-subgroup and m-coset family bounds in the Neumann lemma exercise. O013-LI-U035-COR-001 uses i<=n and j<=m, matching the declared H_1,...,H_n family and the proof hint; no other mathematics changed.",
    }
    for name, record in (("WORKLOG.jsonl", work), ("ADVERSE_LEDGER.jsonl", adverse)):
        path = CONTROL / name
        text = path.read_text(encoding="utf-8").rstrip()
        path.write_text(text + "\n" + json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    for name in BASE:
        json_name = name.endswith(".json") or name.endswith(".jsonl")
        if json_name and name.endswith(".json"):
            json.loads((CONTROL / name).read_text(encoding="utf-8"))
    print("PASS_APPLIED: Unit 035 controls; next boundary complete Chapter 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
