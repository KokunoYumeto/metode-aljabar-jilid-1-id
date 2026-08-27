#!/usr/bin/env python3
"""Fail-closed Unit 033 durable-control transition for O013.

Default mode validates the exact local/public proof bundle and renders all
seven controls in memory.  Only ``--apply`` may replace those controls.  The
gate uses anonymous raw-byte reads plus bounded Git object/ref queries; it
never scans the repository working tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "00_control"
REPOSITORY = "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id"
SLUG = "KokunoYumeto/metode-aljabar-jilid-1-id"
BRANCH = "main"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
DATE_VALUE = "2026-08-26"

CONTROL_TARGETS = (
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md",
    "00_control/CURRENT_STATE.md",
    "00_control/CURRENT_CURSOR.json",
    "00_control/RECOVERY_POINTER.json",
    "00_control/DECISION_LOG.md",
    "00_control/WORKLOG.jsonl",
    "00_control/ADVERSE_LEDGER.jsonl",
)
BASE_HASHES = {
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md": "4c7882f2c8522de4a401de37099b830f0eb16d0fe89f7ee43a67074813063b40",
    "00_control/CURRENT_STATE.md": "0e1d28b74fda0543983badb04b26c8a0a3ee76c07d9f99a7f0e7a7da1a350f80",
    "00_control/CURRENT_CURSOR.json": "b6e2ae5ce562d22a80b2ddc60a3c5838b48e550180d8816b3a14a02ff4ab48da",
    "00_control/RECOVERY_POINTER.json": "5892608784a0b2e2ceeb929e407cdd9a0ea95db33799171a46882cc83432e167",
    "00_control/DECISION_LOG.md": "eeea1005005a261d3eeaa72af906c21234af3d0baa883cd162079da38be4ef83",
    "00_control/WORKLOG.jsonl": "affe6652f228ba186330a420815a729a6ac0e1ea5c667db2e20cec7223e8e6a9",
    "00_control/ADVERSE_LEDGER.jsonl": "2777d666d9ad5ceee4a8dfff689bc4a4e313e870be785e94e487f06ffa7eeb3e",
}

ARCHITECTURE = [
    "li-volume-1-complete",
    "duncan-representation-theory-complete-licensed-repository",
    "cring-six-selected-spans-only",
    "original-connective-and-mastery-layer",
]
ARCH_AUTHORITY = (
    "outputs/01a01ec1-e685-70d0-b022-211396334723/"
    "curriculum_logbook/76_SOURCE_SELECTION_REOPENED_AUDIT_20260824.json"
)
ARCH_SHA = "af18f08683fcd33c947571884c54c5f62e7499489db82ec6ae55a35d4d61fd1c"
DUNCAN_COMMIT = "c62d36f41189da4bd3da4671668f68720df54ff7"

UNIT_ID = "unit-033-bab-4-grup-simetris"
SOURCE_PATH = (
    "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/"
    "chapter4.tex"
)
SOURCE_RANGE = "chapter4.tex:1389-1608"
SOURCE_BYTES = 19_076
SOURCE_SHA = "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a"

UNIT_PATHS = {
    "candidate": "build/unit-033-candidate/chapter4-symmetric-groups-id.tex",
    "target": "repo/source/chapter4.tex",
    "reader": "artifacts/unit-033-bab-4-grup-simetris-id.pdf",
    "backend": "backend/data/unit-033-bab-4-grup-simetris.json",
    "backend_validation": "qa/unit-033-evidence/backend-validation.json",
    "admission_receipt": "qa/UNIT_033_ADMISSION_20260826.md",
    "final_audit": "qa/UNIT_033_FINAL_AUDIT_20260826.md",
    "visual_receipt": "qa/UNIT_033_VISUAL_QA_20260826.md",
    "build_log": "qa/UNIT_033_BUILD_FINAL.log",
    "terminology_audit": "qa/UNIT_033_TERMINOLOGY_AUDIT_20260826.md",
    "terminology_delta": "build/unit-033-staging/terminology-delta.csv",
    "glossary": "00_control/TERMINOLOGY.id-ID.csv",
    "digital_reflow": "qa/UNIT_033_DIGITAL_REFLOW_20260826.md",
    "structure_pdf_evidence": "qa/unit-033-evidence/structure-and-pdf-qa.json",
    "render_inventory": "qa/unit-033-evidence/render-hash-inventory.json",
}
EXPECTED_UNIT_IDENTITIES = {
    "candidate": (23_099, "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76"),
    "target": (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde"),
    "reader": (118_964, "0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d"),
    "backend": (396_355, "edc5812ffd5d46d0fee21748dabbe1b75e71dd1226d3261c073db8930bebe4d7"),
    "backend_validation": (5_827, "3a9d9d832d6ce69d5db364355cf38aceef7e4c8a68c9eeb0ba750203bd0a2fcb"),
    "admission_receipt": (5_246, "0e709035df89517191f6115ba04f2df966134ff598562f352310dc1b1ad83240"),
    "final_audit": (5_721, "96ae3fd16d2019497883176a6ef154689e7a0051d1547c3fd483b4fd73c80aec"),
    "visual_receipt": (5_285, "c6380aa1402c7571242b21a08275e758ed7c189cf16b2e637e1220a01ec14e36"),
    "build_log": (75_964, "ecc90e94457ba8e47e08329ed38a342e58576546a0c2c1733756cf470be702e8"),
    "terminology_audit": (3_699, "efdb7d0cfd43484e2b6b36604e13c7bbcc4dcee188745c637703b164f8abae13"),
    "terminology_delta": (1_987, "783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b"),
    "glossary": (76_280, "9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c"),
    "digital_reflow": (2_112, "804ca5d503d08eeeae0cc6f1a9b0cbe8f4edf47ff9a95e4bf901e5f34ffa0f87"),
    "structure_pdf_evidence": (27_516, "8edbcd847cedeb88f6f464d699e823864a77a8c4c077ec846228c51b177e707c"),
    "render_inventory": (46_048, "7e0bc3fd33a0d1d8c44f6ec7bb43016eb9ea1b281139ae28b69ded144954b915"),
}

CONTENT_RB = "qa/PUBLICATION_GITHUB_UNIT_033_CONTENT_READBACK.json"
RECEIPT_PATH = "qa/PUBLICATION_GITHUB_UNIT_033_20260826.md"
RECEIPT_RB = "qa/PUBLICATION_GITHUB_UNIT_033_RECEIPT_READBACK.json"
CONTENT_PARENT = "5e21b0bd8fa93b37ea721c9842f59ac75fcc3d1a"
CONTENT_COMMIT = "486965a43410fc2b815b0955486771f3048fdd36"
CONTENT_TREE = "5ecad82be506ddaa6d14e232c41d693e3d11318e"
RECEIPT_COMMIT = "7176f4fe4a29dc6680703cb80ff9b01d0f4fe7cd"
RECEIPT_TREE = "7f6b8ce86c47d26c39e791fe2ee3ec2613d96792"
CONTENT_READBACK_IDENTITY = (25_393, "73ed0432a83c12ed978ff150dc4ca4b9422c0181213ae614d46d6ddff28cf195")
RECEIPT_IDENTITY = (1_726, "7b5f4bdd02d76cb9cb83934596aa2de5aa04b6a8c4c02291d6554a470780974b")
RECEIPT_READBACK_IDENTITY = (2_069, "25907bbac9615103001bdbb6c9bfae68b680866eb8c6ab4e3b5fe6b3c000174d")
CONTENT_FETCHES = 58
CONTENT_FETCHED_BYTES = 5_065_986
RECEIPT_FETCHES = 3
RECEIPT_FETCHED_BYTES = 105_259

NEXT_ID = "unit-034-bab-4-limit-dan-kompletisasi-grup"
NEXT_RANGE = "chapter4.tex:1609-1744"
NEXT_BYTES = 15_005
NEXT_SHA = "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab"
NEXT_CANDIDATE = "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
NEXT_CANDIDATE_BYTES = 19_001
NEXT_CANDIDATE_SHA = "4bcbe121f0ec5ac80f05db74d5ae30a71a9ee5c8ff24f8ebf10e42250b6dd076"
NEXT_CHECKER = "scripts/check_unit_034_candidate.py"
NEXT_CHECKER_BYTES = 15_508
NEXT_CHECKER_SHA = "be0444bed3bbf76d3402d637db7dba4e534bdeb8eb7ba2306dc75db5f183051a"
NEXT_REVIEW = "qa/UNIT_034_TRANSLATION_REVIEW_20260825.md"
NEXT_REVIEW_BYTES = 9_911
NEXT_REVIEW_SHA = "2d15ba51456d7b2aad3d071cb534b8b17be5da5f7cf18a64110c58e4c4733548"

PROVISIONAL_CANDIDATE_ID = (23_074, "09e8ec87919a6620e5baac6a07b470b2d03d24a5775d8c66bf6de9af43dc1953")
PROVISIONAL_CHECKER_ID = (16_727, "670016f2f054139c5da78fb2c412f68f7836d2bc4c1dab0282a4041e3a6baa4f")
PROVISIONAL_REVIEW_ID = (9_677, "fe27be28e24d220aa8d3bc9312e2cc51f991c6d727abac89ec52a84cd51f43ae")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class GateError(RuntimeError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), digest(payload)


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        need(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=no_duplicate_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read strict JSON {path}: {exc}") from exc


def repo_path(relative: str) -> Path:
    need(isinstance(relative, str) and relative, "repository path must be nonempty")
    need(not Path(relative).is_absolute(), f"absolute path rejected: {relative}")
    need("\\" not in relative, f"backslash path rejected: {relative}")
    result = (ROOT / relative).resolve(strict=False)
    try:
        result.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GateError(f"path escapes lane root: {relative}") from exc
    return result


def require_keys(value: Mapping[str, Any], keys: Iterable[str], context: str) -> None:
    missing = sorted(set(keys) - set(value))
    need(not missing, f"{context} missing keys: {', '.join(missing)}")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def validate_base() -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    for relative in CONTROL_TARGETS:
        path = repo_path(relative)
        need(path.is_file(), f"control missing: {relative}")
        payload = path.read_bytes()
        need(digest(payload) == BASE_HASHES[relative], f"Unit 032 control base drift: {relative}")
        originals[relative] = payload

    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    need(cursor.get("goal_status") == "active", "cursor goal is not active")
    need(recovery.get("goal_status") == "active", "recovery goal is not active")
    need(cursor.get("selected_architecture") == ARCHITECTURE, "architecture drift")
    authority = cursor.get("architecture_authority", {})
    need(authority.get("path") == ARCH_AUTHORITY and authority.get("sha256") == ARCH_SHA, "architecture authority drift")
    need(authority.get("etingof_state") == "reference_only", "Etingof state drift")
    need(cursor.get("duncan_authority_admitted", {}).get("commit") == DUNCAN_COMMIT, "Duncan authority drift")
    need(cursor.get("last_admitted_unit", {}).get("id") == "unit-032-bab-4-grup-bebas", "cursor is not at Unit 032")
    need(recovery.get("current_boundary", {}).get("unit") == "unit-032-bab-4-grup-bebas", "recovery is not at Unit 032")

    nxt = cursor.get("next_source_boundary", {})
    need(nxt.get("next_admission_unit") == UNIT_ID, "cursor is not pointed at Unit 033")
    need(nxt.get("source_line_start") == 1389 and nxt.get("source_line_end") == 1608, "Unit 033 cursor range drift")
    need(nxt.get("candidate_path") == UNIT_PATHS["candidate"], "Unit 033 cursor path drift")
    need((nxt.get("candidate_bytes"), nxt.get("candidate_sha256")) == PROVISIONAL_CANDIDATE_ID, "recorded provisional candidate drift")
    need((nxt.get("candidate_checker_bytes"), nxt.get("candidate_checker_sha256")) == PROVISIONAL_CHECKER_ID, "recorded provisional checker drift")
    need((nxt.get("candidate_review_bytes"), nxt.get("candidate_review_sha256")) == PROVISIONAL_REVIEW_ID, "recorded provisional review drift")
    # The preceding three identities are historical cursor facts.  Deliberately
    # do not compare them to evolved final Unit 033 files; the proof bundle does.

    rnext = recovery.get("next_cursor", {})
    need(rnext.get("next_admission_unit") == UNIT_ID, "recovery is not pointed at Unit 033")
    need(rnext.get("next_admission_source") == SOURCE_RANGE, "recovery Unit 033 range drift")
    need(cursor.get("publication", {}).get("last_public_unit") == "unit-032-bab-4-grup-bebas", "public cursor drift")

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    for phrase in ("Wen-Wei Li", "Duncan", "CRing", "mastery layer", "The goal is complete only when"):
        need(phrase in goal, f"durable goal lost architecture phrase: {phrase}")
    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    need("## D089" in decision and "## D090" not in decision, "decision cursor is not exactly D089")
    work_lines = originals["00_control/WORKLOG.jsonl"].decode("utf-8").splitlines()
    need(bool(work_lines), "worklog is empty")
    need(json.loads(work_lines[-1], object_pairs_hook=no_duplicate_keys).get("event") == "unit_032_published_and_read_back", "worklog tail drift")
    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    need('"id":"O013-ADV-0099"' in adverse and "O013-ADV-0100" not in adverse, "adverse cursor drift")

    for relative, expected in (
        (NEXT_CANDIDATE, (NEXT_CANDIDATE_BYTES, NEXT_CANDIDATE_SHA)),
        (NEXT_CHECKER, (NEXT_CHECKER_BYTES, NEXT_CHECKER_SHA)),
        (NEXT_REVIEW, (NEXT_REVIEW_BYTES, NEXT_REVIEW_SHA)),
    ):
        path = repo_path(relative)
        need(path.is_file() and identity(path) == expected, f"Unit 034 cursor identity drift: {relative}")

    source = repo_path(SOURCE_PATH)
    need(identity(source) == (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"), "authority identity drift")
    records = source.read_text(encoding="utf-8").splitlines()
    selected = records[1608:1744]
    need(len(selected) == 136 and selected[-1] == "", "Unit 034 blank boundary drift")
    payload = ("\n".join(selected) + "\n").encode("utf-8")
    need((len(payload), digest(payload)) == (NEXT_BYTES, NEXT_SHA), "Unit 034 authority slice drift")
    need(records[1744] == r"\section{范畴中的群}\label{sec:group-in-cat}", "Unit 034 next sentinel drift")

    checked = subprocess.run(
        [sys.executable, str(repo_path(NEXT_CHECKER))],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    need(checked.returncode == 0, f"Unit 034 checker failed: {checked.stderr.strip()}")
    need("PASS: O013-LI-U034" in checked.stdout, "Unit 034 checker PASS marker absent")
    return originals


def validate_identity(raw: Mapping[str, Any], expected_path: str, context: str) -> dict[str, Any]:
    require_keys(raw, ("path", "bytes", "sha256"), context)
    need(raw["path"] == expected_path, f"{context}.path mismatch")
    need(isinstance(raw["bytes"], int) and raw["bytes"] >= 0, f"{context}.bytes invalid")
    need(isinstance(raw["sha256"], str) and HEX64.fullmatch(raw["sha256"]), f"{context}.sha256 invalid")
    path = repo_path(expected_path)
    need(path.is_file(), f"{context} file missing")
    actual = identity(path)
    need(actual == (raw["bytes"], raw["sha256"]), f"{context} local identity mismatch: {actual}")
    return {"path": expected_path, "bytes": actual[0], "sha256": actual[1]}


def validate_backend(specs: Mapping[str, Mapping[str, Any]]) -> None:
    data = load_json(repo_path(UNIT_PATHS["backend_validation"]))
    need(data.get("status") == "PASS" and data.get("unit") == UNIT_ID, "backend validation status/unit mismatch")
    need(data.get("authority") == "chapter4.tex:1389-1608 (blank line 1608 omitted from mapping)", "backend authority mismatch")
    need(data.get("target") == "chapter4.tex:1384-1602", "backend target mismatch")
    need(data.get("provenance_model") == MODEL, "backend model provenance mismatch")
    need(data.get("artifact") == {
        "path": specs["reader"]["path"],
        "pages": 10,
        "bytes": specs["reader"]["bytes"],
        "sha256": specs["reader"]["sha256"],
    }, "backend artifact mismatch")
    exact_counts = {
        "environment_pairs": 43,
        "environment_markers": 86,
        "labels": 10,
        "ordinary_references": 10,
        "equation_references": 10,
        "citations": 0,
        "protected_math_zones": 311,
        "diagrams": 12,
        "diagram_arrows": 4,
        "braid_commands": 9,
        "drawing_commands": 22,
        "index_entries": 9,
        "terminology_rows": 13,
        "source_corrections": 2,
        "terminology_normalizations": 2,
        "digital_reflows": 1,
        "protected_text_localizations": 5,
        "citation_locator_localizations": 0,
        "driver_rendering_workarounds": 1,
        "exercises": 0,
        "hints": 0,
        "answers": 0,
        "solutions": 0,
        "csv_projections": 6,
        "concepts": 485,
        "uuidv5_entities_audited": 561,
    }
    for key, expected in exact_counts.items():
        need(data.get("counts", {}).get(key) == expected, f"backend count mismatch: {key}")
    checks = data.get("checks", {})
    need(checks.get("validation_mutated_outputs") is False, "backend validation mutated outputs")
    need(all(value == "PASS" for key, value in checks.items() if key != "validation_mutated_outputs"), "backend contains failed check")
    need(data.get("identities", {}).get(UNIT_PATHS["backend"]) == {
        "bytes": specs["backend"]["bytes"],
        "sha256": specs["backend"]["sha256"],
    }, "backend identity is not validator-bound")
    backend_text = repo_path(UNIT_PATHS["backend"]).read_text(encoding="utf-8")
    for phrase in ("O013-LI-U033-COR-001", "O013-LI-U033-COR-002", "O013-LI-U033-REFLOW-001", "xlongequal", MODEL):
        need(phrase in backend_text, f"backend provenance missing: {phrase}")
    visual = repo_path(UNIT_PATHS["visual_receipt"]).read_text(encoding="utf-8")
    for phrase in ("all three PDFs contain 10 pages", "Exactly 1 nonfatal underfull hboxes", "zero actionable defects", MODEL):
        need(phrase in visual, f"visual closure missing: {phrase}")
    log = repo_path(UNIT_PATHS["build_log"]).read_text(encoding="utf-8")
    need("Overfull \\hbox" not in log, "final log has overfull hbox")
    need(log.count("Underfull \\hbox") == 1, "final log must contain exactly one underfull hbox")


def validate_inventory(
    raw: Mapping[str, Any],
    expected_path: str,
    commit: str,
    tree: str,
    parent: str,
    expected_count: int,
    expected_bytes: int,
    context: str,
) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    local = validate_identity(raw, expected_path, context)
    data = load_json(repo_path(expected_path))
    need(data.get("repository") == REPOSITORY and data.get("branch") == BRANCH, f"{context} repository mismatch")
    need(data.get("commit") == commit and data.get("tree") == tree and data.get("parent") == parent, f"{context} topology mismatch")
    need(data.get("anonymous") is True and data.get("authorization_header_used") is False, f"{context} is not anonymous")
    need(data.get("all_match") is True, f"{context} all_match is not true")
    need(data.get("status") in (None, "PASS"), f"{context} status invalid")
    need(data.get("remote_main_before") == commit and data.get("remote_main_after") == commit, f"{context} remote head mismatch")
    records = data.get("records")
    need(isinstance(records, list) and len(records) == expected_count, f"{context} record count mismatch")
    need(data.get("path_fetch_count") == expected_count, f"{context} path_fetch_count mismatch")
    need(data.get("total_bytes_fetched") == expected_bytes, f"{context} fetched-byte total mismatch")
    need(sum(record.get("bytes", -1) for record in records) == expected_bytes, f"{context} record-byte sum mismatch")
    mapped: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(records):
        need(isinstance(record, dict), f"{context} record {index} invalid")
        require_keys(record, ("path", "bytes", "sha256", "http_status"), f"{context} record {index}")
        relative = record["path"]
        need(isinstance(relative, str) and relative not in mapped, f"{context} duplicate path")
        need(record["http_status"] == 200, f"{context} non-200 record: {relative}")
        need(isinstance(record["sha256"], str) and HEX64.fullmatch(record["sha256"]), f"{context} bad hash: {relative}")
        need(record.get("matches_committed_blob", True) is True, f"{context} blob mismatch: {relative}")
        mapped[relative] = record
    return local, mapped


def require_record(records: Mapping[str, Mapping[str, Any]], spec: Mapping[str, Any], context: str) -> None:
    record = records.get(spec["path"])
    need(record is not None, f"{context} lacks {spec['path']}")
    need((record["bytes"], record["sha256"]) == (spec["bytes"], spec["sha256"]), f"{context} identity mismatch: {spec['path']}")


def http_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "o013-unit033-control-gate/1",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            need(getattr(response, "status", 200) == 200, f"anonymous HTTP failure: {url}")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GateError(f"anonymous public fetch failed: {url}: {exc}") from exc


def http_json(url: str) -> Mapping[str, Any]:
    try:
        result = json.loads(http_bytes(url).decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"invalid public JSON: {url}: {exc}") from exc
    need(isinstance(result, dict), f"public JSON root invalid: {url}")
    return result


def raw_url(commit: str, path: str) -> str:
    quoted = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"https://raw.githubusercontent.com/{SLUG}/{commit}/{quoted}"


def git_bytes(*arguments: str) -> bytes:
    environment = os.environ.copy()
    environment["GIT_TERMINAL_PROMPT"] = "0"
    completed = subprocess.run(
        ["git", "-c", "credential.helper=", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
    )
    need(
        completed.returncode == 0,
        "bounded Git metadata query failed: "
        + " ".join(arguments)
        + ": "
        + completed.stderr.decode("utf-8", errors="replace").strip(),
    )
    return completed.stdout


def verify_live_public(specs: Iterable[Mapping[str, Any]], receipt: Mapping[str, Any], content_rb: Mapping[str, Any]) -> None:
    ref_payload = git_bytes(
        "ls-remote", f"{REPOSITORY}.git", f"refs/heads/{BRANCH}"
    ).decode("ascii", errors="strict").strip()
    need(
        ref_payload.split() == [RECEIPT_COMMIT, f"refs/heads/{BRANCH}"],
        "public main is not Unit 033 receipt commit",
    )
    for commit, tree, parent, label in (
        (CONTENT_COMMIT, CONTENT_TREE, CONTENT_PARENT, "content"),
        (RECEIPT_COMMIT, RECEIPT_TREE, CONTENT_COMMIT, "receipt"),
    ):
        local_tree = git_bytes("rev-parse", f"{commit}^{{tree}}").decode("ascii", errors="strict").strip()
        local_parents = git_bytes("show", "-s", "--format=%P", commit).decode("ascii", errors="strict").split()
        need(local_tree == tree, f"bounded {label} tree identity mismatch")
        need(local_parents == [parent], f"bounded {label} parent mismatch")
    for spec in specs:
        payload = http_bytes(raw_url(CONTENT_COMMIT, spec["path"]))
        need((len(payload), digest(payload)) == (spec["bytes"], spec["sha256"]), f"public content byte mismatch: {spec['path']}")
    for spec in (receipt, content_rb):
        payload = http_bytes(raw_url(RECEIPT_COMMIT, spec["path"]))
        need((len(payload), digest(payload)) == (spec["bytes"], spec["sha256"]), f"public receipt byte mismatch: {spec['path']}")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = load_json(path)
    need(isinstance(bundle, dict), "proof bundle root invalid")
    require_keys(bundle, ("schema_version", "date", "unit", "publication"), "proof bundle")
    need(bundle["schema_version"] == 1 and bundle["date"] == DATE_VALUE, "proof bundle schema/date mismatch")
    raw_unit = bundle["unit"]
    publication = bundle["publication"]
    need(isinstance(raw_unit, dict) and isinstance(publication, dict), "proof bundle sections invalid")
    need(set(raw_unit) == set(UNIT_PATHS), "proof bundle unit key set mismatch")
    require_keys(publication, ("content_commit", "content_tree", "content_readback", "receipt", "receipt_commit", "receipt_tree", "receipt_readback"), "publication")
    expected_public = {
        "content_commit": CONTENT_COMMIT,
        "content_tree": CONTENT_TREE,
        "receipt_commit": RECEIPT_COMMIT,
        "receipt_tree": RECEIPT_TREE,
    }
    for key, expected in expected_public.items():
        need(isinstance(publication[key], str) and HEX40.fullmatch(publication[key]) and publication[key] == expected, f"publication.{key} mismatch")

    specs: dict[str, dict[str, Any]] = {}
    for key, expected_path in UNIT_PATHS.items():
        need(isinstance(raw_unit[key], dict), f"unit.{key} invalid")
        specs[key] = validate_identity(raw_unit[key], expected_path, f"unit.{key}")
        need((specs[key]["bytes"], specs[key]["sha256"]) == EXPECTED_UNIT_IDENTITIES[key], f"hard-bound Unit 033 identity changed: {key}")
    need(raw_unit["reader"].get("pages") == 10, "reader pages must be ten")
    specs["reader"]["pages"] = 10
    validate_backend(specs)

    content_local, content_records = validate_inventory(
        publication["content_readback"], CONTENT_RB, CONTENT_COMMIT, CONTENT_TREE,
        CONTENT_PARENT, CONTENT_FETCHES, CONTENT_FETCHED_BYTES, "content readback",
    )
    receipt_local = validate_identity(publication["receipt"], RECEIPT_PATH, "publication receipt")
    receipt_rb_local, receipt_records = validate_inventory(
        publication["receipt_readback"], RECEIPT_RB, RECEIPT_COMMIT, RECEIPT_TREE,
        CONTENT_COMMIT, RECEIPT_FETCHES, RECEIPT_FETCHED_BYTES, "receipt readback",
    )
    need((content_local["bytes"], content_local["sha256"]) == CONTENT_READBACK_IDENTITY, "content readback identity drift")
    need((receipt_local["bytes"], receipt_local["sha256"]) == RECEIPT_IDENTITY, "receipt identity drift")
    need((receipt_rb_local["bytes"], receipt_rb_local["sha256"]) == RECEIPT_READBACK_IDENTITY, "receipt readback identity drift")
    for spec in specs.values():
        require_record(content_records, spec, "content readback")
    require_record(receipt_records, receipt_local, "receipt readback")
    require_record(receipt_records, content_local, "receipt readback")

    verify_live_public(specs.values(), receipt_local, content_local)
    publication["content_readback"] = content_local
    publication["receipt"] = receipt_local
    publication["receipt_readback"] = receipt_rb_local
    bundle["unit"] = specs
    bundle["publication"] = publication
    return bundle


def replace_between(text: str, start: str, end: str, replacement: str, context: str) -> str:
    need(text.count(start) == 1, f"{context}: start-anchor count is {text.count(start)}")
    left = text.index(start)
    right = text.find(end, left + len(start))
    need(right >= 0, f"{context}: end anchor absent")
    return text[:left] + replacement.rstrip() + "\n\n" + text[right:]


def boundary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    unit = bundle["unit"]
    publication = bundle["publication"]
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))
    return {
        "id": UNIT_ID,
        "source": SOURCE_RANGE,
        "source_span_bytes": SOURCE_BYTES,
        "source_span_sha256": SOURCE_SHA,
        "source_mapping": "authority lines 1389-1607 map one-for-one to 219 target records at canonical lines 1384-1602; blank boundary line 1608 is omitted",
        "candidate": unit["candidate"]["path"],
        "candidate_bytes": unit["candidate"]["bytes"],
        "candidate_sha256": unit["candidate"]["sha256"],
        "target": "repo/source/chapter4.tex:1384-1602",
        "target_full_bytes": unit["target"]["bytes"],
        "target_full_sha256": unit["target"]["sha256"],
        "reader": unit["reader"]["path"],
        "reader_pages": 10,
        "reader_bytes": unit["reader"]["bytes"],
        "reader_sha256": unit["reader"]["sha256"],
        "backend": unit["backend"]["path"],
        "backend_bytes": unit["backend"]["bytes"],
        "backend_sha256": unit["backend"]["sha256"],
        "backend_validation": unit["backend_validation"]["path"],
        "backend_validation_bytes": unit["backend_validation"]["bytes"],
        "backend_validation_sha256": unit["backend_validation"]["sha256"],
        "admission_receipt": unit["admission_receipt"]["path"],
        "admission_receipt_bytes": unit["admission_receipt"]["bytes"],
        "admission_receipt_sha256": unit["admission_receipt"]["sha256"],
        "final_audit": unit["final_audit"]["path"],
        "final_audit_bytes": unit["final_audit"]["bytes"],
        "final_audit_sha256": unit["final_audit"]["sha256"],
        "visual_qa": "10/10 pages inspected in Poppler and MuPDF; 60 renders cover two clean builds and the artifact; all defined same-renderer decoded-pixel comparisons agree, all edge checks are clear, 35 destinations resolve, 22 internal and three safe URI actions pass, and 27 fonts are embedded; exactly one visually non-actionable underfull hbox and the untagged PDF are disclosed",
        "corrections": [
            "O013-LI-U033-COR-001 repairs the braid-generator endpoint from tau_n to tau_{n-1}",
            "O013-LI-U033-COR-002 supplies missing cardinality bars around S'_n",
        ],
        "digital_reflow": "O013-LI-U033-REFLOW-001 promotes the unchanged Klein-four equality to display mathematics, removing a measured 11.9841 pt overflow without changing its mathematical zones",
        "driver_rendering_workaround": "The reader driver robustly redefines xlongequal because Poppler dropped dvipdfmx's extensible rule; the same labelled equality is retained with an embedded glyph and candidate/canonical mathematics are unchanged",
        "protected_text_localizations": 5,
        "terminology_normalizations": 2,
        "citation_locator_localizations": 0,
        "terminology_rows": 13,
        "content_commit": publication["content_commit"],
        "content_tree": publication["content_tree"],
        "content_readback_path_fetches": content["path_fetch_count"],
        "content_readback_bytes": content["total_bytes_fetched"],
        "content_readback_inventory": publication["content_readback"]["path"],
        "content_readback_inventory_bytes": publication["content_readback"]["bytes"],
        "content_readback_inventory_sha256": publication["content_readback"]["sha256"],
        "receipt": publication["receipt"]["path"],
        "receipt_bytes": publication["receipt"]["bytes"],
        "receipt_sha256": publication["receipt"]["sha256"],
        "receipt_commit": publication["receipt_commit"],
        "receipt_tree": publication["receipt_tree"],
        "receipt_readback_files": receipt["path_fetch_count"],
        "receipt_readback_bytes": receipt["total_bytes_fetched"],
        "receipt_readback_inventory": publication["receipt_readback"]["path"],
        "receipt_readback_inventory_bytes": publication["receipt_readback"]["bytes"],
        "receipt_readback_inventory_sha256": publication["receipt_readback"]["sha256"],
        "state": "public_readback_passed; complete Section 4.9",
    }


def next_boundary(publication: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "component": "li-volume-1-complete",
        "completed_preservation_action": (
            f"Unit 033 content commit {publication['content_commit']} and receipt commit "
            f"{publication['receipt_commit']} passed anonymous readback. Zenodo remains "
            "the nonduplicative 0.6.0 checkpoint through Unit 024 and complete Chapter 3."
        ),
        "next_admission_unit": NEXT_ID,
        "source_path": SOURCE_PATH,
        "source_line_start": 1609,
        "source_line_end": 1744,
        "source_span_bytes": NEXT_BYTES,
        "source_span_sha256": NEXT_SHA,
        "candidate_path": NEXT_CANDIDATE,
        "candidate_bytes": NEXT_CANDIDATE_BYTES,
        "candidate_sha256": NEXT_CANDIDATE_SHA,
        "candidate_checker": NEXT_CHECKER,
        "candidate_checker_bytes": NEXT_CHECKER_BYTES,
        "candidate_checker_sha256": NEXT_CHECKER_SHA,
        "candidate_review": NEXT_REVIEW,
        "candidate_review_bytes": NEXT_REVIEW_BYTES,
        "candidate_review_sha256": NEXT_REVIEW_SHA,
        "next_source_cursor": "chapter4.tex:1745",
        "chapter": "Chapter 4 - group theory",
        "prepared_isolated_units": "Units 034-042 are translated candidates and remain outside canonical repo/source until admitted in order; Units 034-035 finish Chapter 4 and Units 036-042 continue through complete Chapter 5 unique factorization.",
        "latest_isolated_candidate": "build/unit-042-candidate/chapter5-unique-factorization-id.tex",
        "latest_authority_span": "chapter5.tex:958-1182",
        "latest_authority_bytes": 22_981,
        "latest_authority_sha256": "2e3758fa4b4175eeba5969159a89ccb40895c173c12699a8c2211e68a1e94b2a",
        "latest_candidate_bytes": 29_674,
        "latest_candidate_sha256": "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a",
        "latest_candidate_checker": "scripts/check_unit_042_candidate.py",
        "latest_candidate_checker_bytes": 21_414,
        "latest_candidate_checker_sha256": "583bd404e4ff529c2231f287a3451a808d3f85144383d02fddfcecb65699e198",
        "latest_candidate_review": "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md",
        "latest_candidate_review_bytes": 8_214,
        "latest_candidate_review_sha256": "bd4898df0f7cedfbd05f6806f8329a85fedeee1ef9c2cead6619779c6242c927",
        "latest_corrections": ["O013-LI-U042-COR-001 through O013-LI-U042-COR-007 remain isolated and may not skip Units 034-041"],
        "translation_cursor_after_prepared_candidates": "chapter5.tex:1184; line 1183 is the excluded blank separator; Unit 043 has not started",
        "rule": "Admit Units 034-042 sequentially with terminology, canonical integration, reader, backend, build, visual QA, narrow publication, and public-byte readback while continuing isolated translation from chapter5.tex:1184 when it does not delay admission.",
    }


def ident(spec: Mapping[str, Any]) -> str:
    return f"{spec['bytes']:,} bytes / SHA-256 {spec['sha256']}"


def public_summary(bundle: Mapping[str, Any]) -> str:
    unit = bundle["unit"]
    publication = bundle["publication"]
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))
    return f"""Current admitted boundary: Li Units 001-033 through complete Section 4.9.
Unit 033 authority is {SOURCE_RANGE}, 220 normalized-LF records / {SOURCE_BYTES:,}
bytes / SHA-256 {SOURCE_SHA}; blank boundary line 1608 is excluded from the
219-record target mapping at canonical lines 1384-1602. The final candidate is
{ident(unit['candidate'])}; canonical chapter4.tex is {ident(unit['target'])}.
Its centered ten-page reader is {ident(unit['reader'])}, and its schema-valid
backend is {ident(unit['backend'])}. Backend validation is
{ident(unit['backend_validation'])}; the admission receipt is
{ident(unit['admission_receipt'])}; and the final audit is
{ident(unit['final_audit'])}.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U033-COR-001 and O013-LI-U033-COR-002 are separately provenanced.
O013-LI-U033-REFLOW-001 removes a measured 11.9841 pt Klein-four equality
overflow without changing mathematics. A driver-only robust xlongequal repair
retains the same labelled equality in Poppler and MuPDF after Poppler dropped
dvipdfmx's extensible rule; no candidate or canonical formula changed. The
final reader has ten centered pages and no actionable defect. Exactly one
visually non-actionable underfull hbox and its untagged-PDF limitation are
disclosed.

Content commit {publication['content_commit']}, tree {publication['content_tree']},
passed anonymous readback for {content['path_fetch_count']} paths /
{content['total_bytes_fetched']:,} bytes. Receipt commit
{publication['receipt_commit']}, tree {publication['receipt_tree']}, passed
anonymous readback for {receipt['path_fetch_count']} paths /
{receipt['total_bytes_fetched']:,} bytes and is the verified remote base. The
229-page checkpoint reader 0.6.0 remains the nonduplicative Zenodo preservation
release."""


def next_summary() -> str:
    return f"""Unit 033 and complete Section 4.9 are public and byte-verified.
The following source-order admission boundary is Unit 034 at {NEXT_RANGE}; its
{NEXT_CANDIDATE_BYTES:,}-byte isolated candidate has SHA-256
{NEXT_CANDIDATE_SHA}. Its checker has SHA-256 {NEXT_CHECKER_SHA}. The candidate
remains isolated until Unit 034 terminology, integration, reader, backend,
build, all-page visual, publication, and anonymous-readback gates pass. The
active cursor is chapter4.tex:1609 and the cursor after Unit 034 will be
chapter4.tex:1745. Units 034-042 remain strictly source-ordered. The isolated
translation cursor remains chapter5.tex:1184; Unit 043 has not started."""


def make_updates(originals: Mapping[str, bytes], bundle: Mapping[str, Any]) -> dict[str, bytes]:
    unit = bundle["unit"]
    publication = bundle["publication"]
    bound = boundary(bundle)
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))

    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    cursor["updated"] = bundle["date"]
    cursor["last_admitted_unit"] = bound
    cursor["next_source_boundary"] = next_boundary(publication)
    cursor["terminology_qa"].update({
        "path": unit["terminology_audit"]["path"],
        "bytes": unit["terminology_audit"]["bytes"],
        "sha256": unit["terminology_audit"]["sha256"],
        "previous_path": "qa/UNIT_032_TERMINOLOGY_AUDIT_20260826.md",
        "previous_sha256": "2dc5c4ed17f810c5b15fa4c16db491530dce6e3d0597344118fd4f5bd5668b83",
        "glossary": unit["glossary"]["path"],
        "glossary_bytes": unit["glossary"]["bytes"],
        "glossary_sha256": unit["glossary"]["sha256"],
        "glossary_delta": "13 Unit 033 rows covering permutations, cycles and cycle type, parity, braid strands, and Coxeter groups",
        "model": MODEL,
    })
    cursor["publication"].update({
        "expected_remote_base": publication["receipt_commit"],
        "last_public_unit": UNIT_ID,
        "unit_033_content_commit": publication["content_commit"],
        "unit_033_content_tree": publication["content_tree"],
        "unit_033_public_readback_files": content["path_fetch_count"],
        "unit_033_public_readback_bytes": content["total_bytes_fetched"],
        "unit_033_content_readback": publication["content_readback"]["path"],
        "unit_033_content_readback_bytes": publication["content_readback"]["bytes"],
        "unit_033_content_readback_sha256": publication["content_readback"]["sha256"],
        "unit_033_receipt": publication["receipt"]["path"],
        "unit_033_receipt_bytes": publication["receipt"]["bytes"],
        "unit_033_receipt_sha256": publication["receipt"]["sha256"],
        "unit_033_receipt_commit": publication["receipt_commit"],
        "unit_033_receipt_tree": publication["receipt_tree"],
        "unit_033_receipt_readback_files": receipt["path_fetch_count"],
        "unit_033_receipt_readback_bytes": receipt["total_bytes_fetched"],
        "unit_033_receipt_readback_inventory": publication["receipt_readback"]["path"],
        "unit_033_receipt_readback_inventory_bytes": publication["receipt_readback"]["bytes"],
        "unit_033_receipt_readback_inventory_sha256": publication["receipt_readback"]["sha256"],
        "unit_033_state": "content and sanitized receipt public; anonymous readback passed",
    })
    cursor["next_action"] = (
        "Admit Unit 034 at chapter4.tex:1609-1744 and continue strictly through "
        "the isolated Unit 042 candidate; Unit 042 may not skip Units 034-041. "
        "Continue isolated translation from chapter5.tex:1184 only when it does "
        "not delay admission. Duncan remains the post-Li component, CRing remains "
        "six selected repaired spans, Etingof remains reference-only, and the "
        "connective/mastery layer remains separately provenanced."
    )

    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    recovery["updated"] = bundle["date"]
    recovery["current_boundary"] = {
        "unit": bound["id"],
        "state": bound["state"],
        "source": bound["source"],
        "source_span_bytes": bound["source_span_bytes"],
        "source_span_sha256": bound["source_span_sha256"],
        "source_mapping": bound["source_mapping"],
        "candidate": bound["candidate"],
        "candidate_bytes": bound["candidate_bytes"],
        "candidate_sha256": bound["candidate_sha256"],
        "target": bound["target"],
        "target_full_bytes": bound["target_full_bytes"],
        "target_full_sha256": bound["target_full_sha256"],
        "pdf": bound["reader"],
        "pdf_pages": bound["reader_pages"],
        "pdf_bytes": bound["reader_bytes"],
        "pdf_sha256": bound["reader_sha256"],
        "backend": bound["backend"],
        "backend_bytes": bound["backend_bytes"],
        "backend_sha256": bound["backend_sha256"],
        "backend_validation": bound["backend_validation"],
        "backend_validation_bytes": bound["backend_validation_bytes"],
        "backend_validation_sha256": bound["backend_validation_sha256"],
        "navigation": bound["visual_qa"],
        "admission_receipt": bound["admission_receipt"],
        "admission_receipt_bytes": bound["admission_receipt_bytes"],
        "admission_receipt_sha256": bound["admission_receipt_sha256"],
        "final_audit": bound["final_audit"],
        "final_audit_bytes": bound["final_audit_bytes"],
        "final_audit_sha256": bound["final_audit_sha256"],
        "digital_reflow": bound["digital_reflow"],
        "driver_rendering_workaround": bound["driver_rendering_workaround"],
        "content_commit": bound["content_commit"],
        "content_tree": bound["content_tree"],
        "content_readback_files": bound["content_readback_path_fetches"],
        "content_readback_bytes": bound["content_readback_bytes"],
        "content_readback_inventory": bound["content_readback_inventory"],
        "content_readback_inventory_bytes": bound["content_readback_inventory_bytes"],
        "content_readback_inventory_sha256": bound["content_readback_inventory_sha256"],
        "receipt": bound["receipt"],
        "receipt_bytes": bound["receipt_bytes"],
        "receipt_sha256": bound["receipt_sha256"],
        "receipt_commit": bound["receipt_commit"],
        "receipt_tree": bound["receipt_tree"],
        "receipt_readback_files": bound["receipt_readback_files"],
        "receipt_readback_bytes": bound["receipt_readback_bytes"],
        "receipt_readback_inventory": bound["receipt_readback_inventory"],
        "receipt_readback_inventory_bytes": bound["receipt_readback_inventory_bytes"],
        "receipt_readback_inventory_sha256": bound["receipt_readback_inventory_sha256"],
        "model": MODEL,
    }
    recovery["next_cursor"] = {
        "immediate_action": "admit Chapter 4 Unit 034 at chapter4.tex:1609-1744 and continue strictly in source order",
        "builder": "scripts/build_unit_034.ps1",
        "coverage": "complete prelude, Chapters 1-3, and Chapter 4 opening through complete Section 4.9 in 33 admitted units; later Chapter 4 and Chapters 5-10 remain unadmitted",
        "next_admission_unit": NEXT_ID,
        "next_admission_source": NEXT_RANGE,
        "next_authority_bytes": NEXT_BYTES,
        "next_authority_sha256": NEXT_SHA,
        "next_candidate": NEXT_CANDIDATE,
        "next_candidate_bytes": NEXT_CANDIDATE_BYTES,
        "next_candidate_sha256": NEXT_CANDIDATE_SHA,
        "next_candidate_checker": NEXT_CHECKER,
        "next_candidate_checker_bytes": NEXT_CHECKER_BYTES,
        "next_candidate_checker_sha256": NEXT_CHECKER_SHA,
        "next_candidate_review": NEXT_REVIEW,
        "next_candidate_review_bytes": NEXT_REVIEW_BYTES,
        "next_candidate_review_sha256": NEXT_REVIEW_SHA,
        "cursor_after_next_admission": "chapter4.tex:1745",
        "prepared_isolated_units": "Units 034-042; Units 034-035 finish Chapter 4 and Units 036-042 continue Chapter 5 through complete unique factorization",
        "latest_isolated_candidate": "build/unit-042-candidate/chapter5-unique-factorization-id.tex",
        "latest_candidate_bytes": 29_674,
        "latest_candidate_sha256": "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a",
        "latest_candidate_checker": "scripts/check_unit_042_candidate.py",
        "latest_candidate_checker_bytes": 21_414,
        "latest_candidate_checker_sha256": "583bd404e4ff529c2231f287a3451a808d3f85144383d02fddfcecb65699e198",
        "latest_candidate_review": "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md",
        "latest_candidate_review_bytes": 8_214,
        "latest_candidate_review_sha256": "bd4898df0f7cedfbd05f6806f8329a85fedeee1ef9c2cead6619779c6242c927",
        "translation_cursor_after_staging": "chapter5.tex:1184; line 1183 is excluded blank; Unit 043 has not started",
        "post_li_component": "complete admitted Duncan CC BY 4.0 repository, six exact repaired CRing GFDL spans, and separate connective/mastery layer; Etingof reference-only",
    }
    recovery["publication_resume"]["github"] = (
        f"Unit 033 content is public at commit {publication['content_commit']} "
        f"(tree {publication['content_tree']}); its content inventory passed. "
        f"Receipt commit {publication['receipt_commit']} (tree {publication['receipt_tree']}) "
        "and its receipt inventory also passed anonymous byte readback. Checkpoint "
        "0.6.0 remains public and nonduplicative."
    )

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    goal = replace_between(
        goal,
        "Current admitted boundary: Li Units 001-032 through complete Section 4.8.\n",
        "A bounded Indonesian field-usage check",
        public_summary(bundle),
        "goal progress",
    )
    goal = replace_between(
        goal,
        "Unit 032 and complete Section 4.8 are public and byte-verified.",
        "The Duncan source/build gate",
        next_summary(),
        "goal next action",
    )
    need(PROVISIONAL_CANDIDATE_ID[1] not in goal, "stale provisional Unit 033 identity remains in goal")

    state = originals["00_control/CURRENT_STATE.md"].decode("utf-8")
    state_top = f"""Updated: {bundle['date']}  
Status: active; Li Units 001-033 are public and byte-verified through complete
Chapter 4 Section 4.9. Unit 033 is public at content commit
`{publication['content_commit']}`; all {content['path_fetch_count']} paths /
{content['total_bytes_fetched']:,} bytes passed anonymous readback. Receipt
commit `{publication['receipt_commit']}` and all {receipt['path_fetch_count']} paths /
{receipt['total_bytes_fetched']:,} bytes also passed. The canonical next
boundary is Unit 034 at `chapter4.tex:1609`; isolated translation reaches Unit
042 and `chapter5.tex:1184`, while Unit 043 has not started. The full active
objective continues from the complete Li edition through complete licensed
Duncan, selected repaired CRing spans, and the separately provenanced
connective and mastery layer; this boundary is not a completion claim."""
    state = replace_between(state, "Updated: 2026-08-26  \nStatus:", "## Completed\n", state_top, "state top")
    state = replace_between(
        state,
        "## Unit 032 public boundary\n",
        "## Not complete\n",
        "## Unit 033 public boundary\n\n" + public_summary(bundle) + "\n\n## Exact next action\n\n" + next_summary(),
        "state boundary",
    )

    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    need("## D089" in decision and "## D090" not in decision, "decision cursor changed")
    decision += f"""
## D090 — {bundle['date']} — Unit 033 published and cursor advanced

Publish complete Section 4.9 at authority {SOURCE_RANGE} only after the final
ten-page reader, schema-valid backend, independent admission audit, content
commit, receipt commit, and both anonymous readback inventories agree. Content
commit {publication['content_commit']}, tree {publication['content_tree']}, and
receipt commit {publication['receipt_commit']}, tree {publication['receipt_tree']},
are the exact public boundary. O013-LI-U033-REFLOW-001 removes the measured
11.9841 pt Klein-four equality overflow without changing mathematics. A
reader-driver-only robust xlongequal definition closes Poppler's loss of the
dvipdfmx extensible rule while preserving the labelled relation and leaving
candidate/canonical mathematics unchanged. Exactly one visually non-actionable
underfull hbox and the untagged-PDF limitation remain disclosed. Advance to
Unit 034 at chapter4.tex:1609 while preserving the full Li, Duncan,
selected-CRing, and separate connective/mastery architecture with Etingof
reference-only.
"""

    worklog = originals["00_control/WORKLOG.jsonl"].decode("utf-8")
    work_event = {
        "date": bundle["date"],
        "event": "unit_033_published_and_read_back",
        "result": (
            f"Section4.9 at {SOURCE_RANGE} is canonically integrated and public. "
            f"Candidate {unit['candidate']['bytes']} bytes / {unit['candidate']['sha256']}; "
            f"chapter4.tex {unit['target']['bytes']} bytes / {unit['target']['sha256']}; "
            f"reader 10 pages / {unit['reader']['bytes']} bytes / {unit['reader']['sha256']}; "
            f"backend {unit['backend']['bytes']} bytes / {unit['backend']['sha256']}. "
            "All deterministic gates pass. O013-LI-U033-COR-001 and COR-002 are explicit. "
            "O013-LI-U033-REFLOW-001 removes a measured 11.9841 pt overflow without changing mathematics. "
            "A driver-only robust xlongequal repair preserves the labelled equality in both renderers without source-math change. "
            "Exactly one visually non-actionable underfull hbox and the untagged PDF are disclosed. "
            f"Content {publication['content_commit']} / tree {publication['content_tree']} and receipt "
            f"{publication['receipt_commit']} / tree {publication['receipt_tree']} passed anonymous readback. "
            "Cursor advances to Unit034 chapter4.tex:1609; full goal remains active."
        ),
    }
    worklog += json.dumps(work_event, ensure_ascii=False, separators=(",", ":")) + "\n"

    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    events = (
        {
            "id": "O013-ADV-0100",
            "date": bundle["date"],
            "severity": "P2",
            "surface": "li_unit_033_klein_four_display_overflow",
            "status": "closed_by_separate_target_only_digital_reflow",
            "summary": "The first Unit033 reader measured an 11.9841 pt overflow in the inline Klein-four equality. O013-LI-U033-REFLOW-001 promotes the exact equality and unchanged set to display mathematics; the final log has zero overfull diagnostics. This is digital reflow, not a source correction.",
        },
        {
            "id": "O013-ADV-0101",
            "date": bundle["date"],
            "severity": "P2",
            "surface": "li_unit_033_poppler_xlongequal_rule_loss",
            "status": "closed_by_reader_surface_renderer_repair",
            "summary": "Poppler dropped dvipdfmx's extensible rule for a labelled xlongequal in the braid diagram. The Unit033 reader driver locally substitutes the same labelled equality using a standard embedded glyph. Poppler and MuPDF show it visibly and unclipped; candidate and canonical-source mathematics are unchanged.",
        },
        {
            "id": "O013-ADV-0102",
            "date": bundle["date"],
            "severity": "P3",
            "surface": "li_unit_033_reader_underfull_and_accessibility_limitations",
            "status": "closed_as_disclosed_nonblocking_limitations",
            "summary": "The ten-page Unit033 reader remains untagged and therefore carries no tagged-accessibility claim. Its final log contains exactly one visually inspected underfull hbox; it does not clip, collide, touch an edge, remove content, or impair reading. These are explicit nonblocking limitations.",
        },
    )
    for event in events:
        need(event["id"] not in adverse, f"adverse ID already exists: {event['id']}")
        adverse += json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    updates = {
        "00_control/CURRENT_GOAL_AND_WORKFLOW.md": goal.encode("utf-8"),
        "00_control/CURRENT_STATE.md": state.encode("utf-8"),
        "00_control/CURRENT_CURSOR.json": json_bytes(cursor),
        "00_control/RECOVERY_POINTER.json": json_bytes(recovery),
        "00_control/DECISION_LOG.md": decision.encode("utf-8"),
        "00_control/WORKLOG.jsonl": worklog.encode("utf-8"),
        "00_control/ADVERSE_LEDGER.jsonl": adverse.encode("utf-8"),
    }
    need(set(updates) == set(CONTROL_TARGETS), "internal control target set changed")
    need(all(payload.endswith(b"\n") for payload in updates.values()), "rendered control lacks terminal LF")
    return updates


def validate_updates(updates: Mapping[str, bytes], bundle: Mapping[str, Any]) -> None:
    cursor = json.loads(updates["00_control/CURRENT_CURSOR.json"].decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    recovery = json.loads(updates["00_control/RECOVERY_POINTER.json"].decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    need(cursor["goal_status"] == "active" and recovery["goal_status"] == "active", "goal status changed")
    need(cursor["selected_architecture"] == ARCHITECTURE, "architecture changed")
    need(cursor["last_admitted_unit"]["id"] == UNIT_ID, "Unit 033 was not admitted")
    need(cursor["last_admitted_unit"]["state"] == "public_readback_passed; complete Section 4.9", "Unit 033 state mismatch")
    need(cursor["next_source_boundary"]["next_admission_unit"] == NEXT_ID, "cursor not advanced to Unit 034")
    need(cursor["next_source_boundary"]["source_line_start"] == 1609, "cursor not advanced to line 1609")
    need(cursor["publication"]["expected_remote_base"] == bundle["publication"]["receipt_commit"], "remote base mismatch")
    need(recovery["current_boundary"]["unit"] == UNIT_ID, "recovery did not admit Unit 033")
    need(recovery["next_cursor"]["next_admission_unit"] == NEXT_ID, "recovery not advanced to Unit 034")
    need(recovery["next_cursor"]["cursor_after_next_admission"] == "chapter4.tex:1745", "recovery after-cursor mismatch")
    for relative in ("00_control/CURRENT_GOAL_AND_WORKFLOW.md", "00_control/CURRENT_STATE.md"):
        text = updates[relative].decode("utf-8")
        for phrase in ("Unit 033", "Section 4.9", "11.9841 pt", "xlongequal", "Unit 034", "chapter4.tex:1609", "untagged"):
            need(phrase in text, f"{relative} lost required phrase: {phrase}")
        need(PROVISIONAL_CANDIDATE_ID[1] not in text, f"{relative} retains provisional candidate hash")
    goal = updates["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    for phrase in ("The goal is complete only when", "Duncan", "CRing", "Etingof remains reference-only"):
        need(phrase in goal, f"durable goal lost architecture phrase: {phrase}")
    decision = updates["00_control/DECISION_LOG.md"].decode("utf-8")
    need(decision.count("## D090") == 1, "D090 missing or duplicated")
    for relative in ("00_control/WORKLOG.jsonl", "00_control/ADVERSE_LEDGER.jsonl"):
        seen: set[str] = set()
        for line_number, line in enumerate(updates[relative].decode("utf-8").splitlines(), 1):
            value = json.loads(line, object_pairs_hook=no_duplicate_keys)
            need(isinstance(value, dict), f"{relative}:{line_number} is not an object")
            if "id" in value:
                need(value["id"] not in seen, f"{relative} duplicate ID: {value['id']}")
                seen.add(value["id"])
    adverse = updates["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    for event_id in ("O013-ADV-0100", "O013-ADV-0101", "O013-ADV-0102"):
        need(adverse.count(event_id) == 1, f"adverse event missing or duplicated: {event_id}")


def atomic_write(updates: Mapping[str, bytes], originals: Mapping[str, bytes]) -> None:
    temps: dict[str, Path] = {}
    replaced: list[str] = []
    try:
        need(set(originals) == set(CONTROL_TARGETS), "original control snapshot set changed")
        for relative in CONTROL_TARGETS:
            need(
                repo_path(relative).read_bytes() == originals[relative],
                f"control drifted after validation: {relative}",
            )
        for relative, payload in updates.items():
            target = repo_path(relative)
            descriptor, name = tempfile.mkstemp(prefix=f".{target.name}.u033-", suffix=".tmp", dir=target.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            need(identity(temporary) == (len(payload), digest(payload)), f"temporary write failed: {relative}")
            temps[relative] = temporary
        for relative in CONTROL_TARGETS:
            need(
                repo_path(relative).read_bytes() == originals[relative],
                f"control drifted while staging replacements: {relative}",
            )
        for relative in CONTROL_TARGETS:
            os.replace(temps.pop(relative), repo_path(relative))
            replaced.append(relative)
        for relative, payload in updates.items():
            need(repo_path(relative).read_bytes() == payload, f"post-write mismatch: {relative}")
    except Exception:
        for relative in reversed(replaced):
            target = repo_path(relative)
            descriptor, name = tempfile.mkstemp(prefix=f".{target.name}.rollback-", suffix=".tmp", dir=target.parent)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(originals[relative])
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, target)
        raise
    finally:
        for temporary in temps.values():
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-bundle", type=Path, required=True, help="strict Unit 033 local/public proof JSON")
    parser.add_argument("--apply", action="store_true", help="atomically replace exactly seven controls")
    args = parser.parse_args()
    proof = args.proof_bundle.resolve()
    need(proof.is_file(), f"proof bundle missing: {proof}")
    originals = validate_base()
    bundle = validate_bundle(proof)
    updates = make_updates(originals, bundle)
    validate_updates(updates, bundle)
    if args.apply:
        atomic_write(updates, originals)
    report = {
        "status": "PASS",
        "mode": "apply" if args.apply else "dry-run",
        "unit": UNIT_ID,
        "next_unit": NEXT_ID,
        "next_source_cursor": "chapter4.tex:1609",
        "cursor_after_next_admission": "chapter4.tex:1745",
        "content_commit": bundle["publication"]["content_commit"],
        "receipt_commit": bundle["publication"]["receipt_commit"],
        "targets": [
            {"path": relative, "bytes": len(updates[relative]), "sha256": digest(updates[relative])}
            for relative in CONTROL_TARGETS
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
