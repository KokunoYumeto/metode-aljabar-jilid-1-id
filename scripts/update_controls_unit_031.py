#!/usr/bin/env python3
"""Fail-closed Unit 031 durable-control transition for O013.

Default mode verifies the exact local/public proof bundle and renders all seven
new controls in memory. --apply is required to replace the controls. The tool
uses only credential-disabled, read-only Git identity checks and cannot write
outside CONTROL_TARGETS.
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
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md": "02d9d31b2c044ad767bf4e1f0057ed4a0d6466ac1d484a4b499efae75c68b9f6",
    "00_control/CURRENT_STATE.md": "c06753e9b8eb7d144bcf4c94e47d8718e87d6184b7445cbe5ca9177591735180",
    "00_control/CURRENT_CURSOR.json": "299092b82ac2f918a5cf81e5fc132e156ba6efc872a9383ac9c539fc19b9ead6",
    "00_control/RECOVERY_POINTER.json": "c545058941efef0889226a6d517ddf40502855f92cca538a730018959dffb710",
    "00_control/DECISION_LOG.md": "ec523c0853f01b2036409d6e519badd1327fb08996dea768f955a3cd5033aeff",
    "00_control/WORKLOG.jsonl": "0a4724cc86ec4fcb35a2efbbbad05f0251dbcc30b3b333c4915f02e9c38ccff6",
    "00_control/ADVERSE_LEDGER.jsonl": "511403f77ff42575fe9a38dd81aa0f80e62fc4e0b274226f17a9ba54dd41ee87",
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

UNIT_ID = "unit-031-bab-4-grup-solvabel-dan-nilpoten"
PROVISIONAL_CURSOR_ID = "unit-031-bab-4-grup-terpecahkan-dan-nilpoten"
SOURCE_PATH = (
    "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/"
    "chapter4.tex"
)
SOURCE_RANGE = "chapter4.tex:936-1107"
SOURCE_BYTES = 16048
SOURCE_SHA = "647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b"
UNIT_PATHS = {
    "candidate": "build/unit-031-candidate/chapter4-solvable-nilpotent-groups-id.tex",
    "target": "repo/source/chapter4.tex",
    "reader": "artifacts/unit-031-bab-4-grup-solvabel-dan-nilpoten-id.pdf",
    "backend": "backend/data/unit-031-bab-4-grup-solvabel-dan-nilpoten.json",
    "backend_validation": "qa/unit-031-evidence/backend-validation.json",
    "admission_receipt": "qa/UNIT_031_ADMISSION_20260826.md",
    "final_audit": "qa/UNIT_031_FINAL_AUDIT_20260826.md",
    "visual_receipt": "qa/UNIT_031_VISUAL_QA_20260826.md",
    "build_log": "qa/UNIT_031_BUILD_FINAL.log",
    "terminology_audit": "qa/UNIT_031_TERMINOLOGY_AUDIT_20260826.md",
    "terminology_delta": "build/unit-031-staging/terminology-delta.csv",
    "glossary": "00_control/TERMINOLOGY.id-ID.csv",
}
CONTENT_RB = "qa/PUBLICATION_GITHUB_UNIT_031_CONTENT_READBACK.json"
RECEIPT = "qa/PUBLICATION_GITHUB_UNIT_031_20260826.md"
RECEIPT_RB = "qa/PUBLICATION_GITHUB_UNIT_031_RECEIPT_READBACK.json"
CONTENT_PARENT = "049b8a29613f66a63ebede0763a91ee22c956187"

NEXT_ID = "unit-032-bab-4-grup-bebas"
NEXT_RANGE = "chapter4.tex:1108-1388"
NEXT_BYTES = 22547
NEXT_SHA = "5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af"
NEXT_CANDIDATE = "build/unit-032-candidate/chapter4-free-groups-id.tex"
NEXT_CANDIDATE_BYTES = 27685
NEXT_CANDIDATE_SHA = "19583aa71814bbed580d51f39eeaf113a399ec13fef5773a39b6e6cf16289140"
NEXT_CHECKER = "scripts/check_unit_032_candidate.py"
NEXT_CHECKER_BYTES = 16756
NEXT_CHECKER_SHA = "5bbaa33eb27b6acf6f1530f5473926cb0a2a9b6216ff4c492f88840795ab4d89"
NEXT_REVIEW = "qa/UNIT_032_TRANSLATION_REVIEW_20260825.md"
NEXT_REVIEW_BYTES = 11308
NEXT_REVIEW_SHA = "ac778073e22b728f11cf6085f748339d7649094f8d4f66eca46ceb87daf1fea1"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DATE = re.compile(r"^20[0-9]{2}-[01][0-9]-[0-3][0-9]$")


class GateError(RuntimeError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_identity(path: Path) -> tuple[int, str]:
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
    need(isinstance(relative, str) and relative, "path must be nonempty")
    need(not Path(relative).is_absolute(), f"absolute path rejected: {relative}")
    need("\\" not in relative, f"use forward slashes in repository path: {relative}")
    resolved = (ROOT / relative).resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GateError(f"path escapes lane root: {relative}") from exc
    return resolved


def require_keys(obj: Mapping[str, Any], keys: Iterable[str], context: str) -> None:
    missing = sorted(set(keys) - set(obj))
    need(not missing, f"{context} missing keys: {', '.join(missing)}")


def validate_identity(
    raw: Mapping[str, Any], expected_path: str, context: str
) -> dict[str, Any]:
    require_keys(raw, ("path", "bytes", "sha256"), context)
    need(raw["path"] == expected_path, f"{context}.path must be {expected_path}")
    need(isinstance(raw["bytes"], int) and raw["bytes"] > 0, f"{context}.bytes invalid")
    need(isinstance(raw["sha256"], str) and HEX64.fullmatch(raw["sha256"]), f"{context}.sha256 invalid")
    path = repo_path(expected_path)
    need(path.is_file(), f"{context} file missing: {expected_path}")
    actual = file_identity(path)
    need(actual == (raw["bytes"], raw["sha256"]), f"{context} local identity mismatch: {actual}")
    return {"path": expected_path, "bytes": actual[0], "sha256": actual[1]}


def validate_inventory(
    raw: Mapping[str, Any],
    path: str,
    commit: str,
    tree: str,
    parent: str | None,
    context: str,
) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    local = validate_identity(raw, path, context)
    data = load_json(repo_path(path))
    need(isinstance(data, dict), f"{context} root is not an object")
    need(data.get("repository") == REPOSITORY, f"{context} repository mismatch")
    need(data.get("branch") == BRANCH, f"{context} branch mismatch")
    need(data.get("commit") == commit, f"{context} commit mismatch")
    need(data.get("tree") == tree, f"{context} tree mismatch")
    if parent is not None:
        need(data.get("parent") == parent, f"{context} parent mismatch")
    need(data.get("anonymous") is True, f"{context} is not anonymous")
    need(data.get("authorization_header_used") is False, f"{context} used authorization")
    need(data.get("all_match") is True, f"{context} all_match is not true")
    if "status" in data:
        need(data["status"] == "PASS", f"{context} status is not PASS")
    need(data.get("remote_main_before") == commit, f"{context} remote_main_before mismatch")
    need(data.get("remote_main_after") == commit, f"{context} remote_main_after mismatch")
    records = data.get("records")
    need(isinstance(records, list) and records, f"{context} records missing")
    need(data.get("path_fetch_count") == len(records), f"{context} path count mismatch")
    need(
        data.get("total_bytes_fetched") == sum(record.get("bytes", -1) for record in records),
        f"{context} fetched-byte total mismatch",
    )
    mapped: dict[str, Mapping[str, Any]] = {}
    for index, record in enumerate(records):
        need(isinstance(record, dict), f"{context} record {index} invalid")
        require_keys(record, ("path", "bytes", "sha256", "http_status"), f"{context} record {index}")
        rel = record["path"]
        need(isinstance(rel, str) and rel not in mapped, f"{context} duplicate path: {rel!r}")
        need(record["http_status"] == 200, f"{context} non-200 record: {rel}")
        need(isinstance(record["bytes"], int) and record["bytes"] >= 0, f"{context} bad bytes: {rel}")
        need(isinstance(record["sha256"], str) and HEX64.fullmatch(record["sha256"]), f"{context} bad hash: {rel}")
        if "matches_committed_blob" in record:
            need(record["matches_committed_blob"] is True, f"{context} blob mismatch: {rel}")
        mapped[rel] = record
    return local, mapped


def require_record(records: Mapping[str, Mapping[str, Any]], spec: Mapping[str, Any], context: str) -> None:
    record = records.get(spec["path"])
    need(record is not None, f"{context} lacks {spec['path']}")
    need(
        (record["bytes"], record["sha256"]) == (spec["bytes"], spec["sha256"]),
        f"{context} identity mismatch for {spec['path']}",
    )


def http_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "o013-unit031-control-gate/1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            need(getattr(response, "status", 200) == 200, f"anonymous HTTP failure: {url}")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GateError(f"anonymous public fetch failed: {url}: {exc}") from exc


def http_json(url: str) -> Mapping[str, Any]:
    try:
        value = json.loads(http_bytes(url).decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"invalid public JSON from {url}: {exc}") from exc
    need(isinstance(value, dict), f"public JSON root invalid: {url}")
    return value


def raw_url(commit: str, path: str) -> str:
    quoted = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return f"https://raw.githubusercontent.com/{SLUG}/{commit}/{quoted}"


def verify_live_public(
    content_commit: str,
    content_tree: str,
    receipt_commit: str,
    receipt_tree: str,
    content_specs: Iterable[Mapping[str, Any]],
    receipt_specs: Iterable[Mapping[str, Any]],
) -> None:
    remote_url = f"https://github.com/{SLUG}.git"
    try:
        ref_output = subprocess.check_output(
            [
                "git",
                "-c",
                "credential.helper=",
                "ls-remote",
                "--heads",
                remote_url,
                f"refs/heads/{BRANCH}",
            ],
            cwd=ROOT,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GateError(f"anonymous public ref lookup failed: {exc}") from exc
    fields = ref_output.split()
    need(
        len(fields) == 2
        and fields[0] == receipt_commit
        and fields[1] == f"refs/heads/{BRANCH}",
        "live public main is not the receipt commit",
    )
    for commit, tree, label in (
        (content_commit, content_tree, "content"),
        (receipt_commit, receipt_tree, "receipt"),
    ):
        try:
            local_commit = subprocess.check_output(
                ["git", "rev-parse", f"{commit}^{{commit}}"], cwd=ROOT, text=True
            ).strip()
            local_tree = subprocess.check_output(
                ["git", "rev-parse", f"{commit}^{{tree}}"], cwd=ROOT, text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise GateError(f"local immutable {label} identity lookup failed: {exc}") from exc
        need(local_commit == commit, f"local {label} commit mismatch")
        need(local_tree == tree, f"local {label} tree mismatch")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", content_commit, receipt_commit],
        cwd=ROOT,
        check=False,
    )
    need(ancestor.returncode == 0, "content commit is not an ancestor of receipt commit")
    for commit, specs, label in (
        (content_commit, content_specs, "content"),
        (receipt_commit, receipt_specs, "receipt"),
    ):
        for spec in specs:
            payload = http_bytes(raw_url(commit, spec["path"]))
            need(
                (len(payload), digest(payload)) == (spec["bytes"], spec["sha256"]),
                f"live {label} identity mismatch: {spec['path']}",
            )


def validate_base() -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    for rel in CONTROL_TARGETS:
        path = repo_path(rel)
        need(path.is_file(), f"control target missing: {rel}")
        payload = path.read_bytes()
        need(digest(payload) == BASE_HASHES[rel], f"published Unit 030 control base drift: {rel}")
        originals[rel] = payload
    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    need(cursor.get("goal_status") == "active", "cursor goal not active")
    need(cursor.get("selected_architecture") == ARCHITECTURE, "architecture drift")
    need(cursor.get("architecture_authority", {}).get("path") == ARCH_AUTHORITY, "architecture authority path drift")
    need(cursor.get("architecture_authority", {}).get("sha256") == ARCH_SHA, "architecture authority hash drift")
    need(cursor.get("architecture_authority", {}).get("etingof_state") == "reference_only", "Etingof state drift")
    need(cursor.get("duncan_authority_admitted", {}).get("commit") == DUNCAN_COMMIT, "Duncan authority drift")
    need(cursor.get("last_admitted_unit", {}).get("id") == "unit-030-bab-4-deret-komposisi-grup", "cursor not at Unit 030")
    next_boundary = cursor.get("next_source_boundary", {})
    need(
        next_boundary.get("next_admission_unit") == PROVISIONAL_CURSOR_ID,
        "Unit 031 provisional cursor identity drift",
    )
    need(
        next_boundary.get("source_line_start") == 936
        and next_boundary.get("source_line_end") == 1107
        and next_boundary.get("candidate_path") == UNIT_PATHS["candidate"],
        "Unit 031 source/candidate cursor drift",
    )
    need(recovery.get("current_boundary", {}).get("unit") == "unit-030-bab-4-deret-komposisi-grup", "recovery not at Unit 030")
    terminal = recovery.get("terminal_condition", "")
    for phrase in ("complete Li Volume 1", "Duncan", "six selected CRing spans", "connective/mastery layer", "Etingof reference-only"):
        need(phrase in terminal, f"terminal architecture missing: {phrase}")
    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    for phrase in ("Wen-Wei Li", "Duncan", "CRing", "connective", "mastery layer", "The goal is complete only when"):
        need(phrase in goal, f"durable goal scope missing: {phrase}")
    return originals


def validate_backend(specs: Mapping[str, Mapping[str, Any]]) -> None:
    data = load_json(repo_path(UNIT_PATHS["backend_validation"]))
    need(data.get("status") == "PASS", "backend validation is not PASS")
    need(data.get("unit") == UNIT_ID, "backend unit mismatch")
    need(data.get("authority") == "chapter4.tex:936-1107 (blank line 1107 omitted from mapping)", "backend authority mismatch")
    need(data.get("target") == "chapter4.tex:933-1103", "backend target mismatch")
    need(data.get("provenance_model") == MODEL, "backend model provenance mismatch")
    need(
        data.get("artifact") == {
            "path": specs["reader"]["path"],
            "pages": 9,
            "bytes": specs["reader"]["bytes"],
            "sha256": specs["reader"]["sha256"],
        },
        "backend artifact identity mismatch",
    )
    exact_counts = {
        "active_environment_pairs": 31,
        "labels": 6,
        "ordinary_references": 7,
        "citations": 1,
        "protected_math_zones": 326,
        "diagrams": 3,
        "diagram_arrows": 3,
        "index_entries": 9,
        "terminology_rows": 14,
        "source_corrections": 1,
        "digital_reflows": 1,
        "protected_text_localizations": 8,
        "exercises": 0,
        "hints": 0,
        "answers": 0,
        "solutions": 0,
        "csv_projections": 6,
    }
    for key, expected in exact_counts.items():
        need(data.get("counts", {}).get(key) == expected, f"backend count mismatch: {key}")
    checks = data.get("checks", {})
    need(checks.get("validation_mutated_outputs") is False, "backend validation mutated outputs")
    need(all(value == "PASS" for key, value in checks.items() if key != "validation_mutated_outputs"), "backend validation contains failed check")
    need(
        data.get("identities", {}).get(UNIT_PATHS["backend"])
        == {"bytes": specs["backend"]["bytes"], "sha256": specs["backend"]["sha256"]},
        "validator does not bind backend identity",
    )
    backend_text = repo_path(UNIT_PATHS["backend"]).read_text(encoding="utf-8")
    for phrase in ("O013-LI-U031-COR-001", "O013-LI-U031-REFLOW-001", "42.13312 pt", MODEL):
        need(phrase in backend_text, f"backend provenance missing: {phrase}")
    visual = repo_path(UNIT_PATHS["visual_receipt"]).read_text(encoding="utf-8")
    for phrase in ("All three PDFs contain\n9 pages", "tanpa halaman kesepuluh yang jarang", "zero actionable defects", MODEL):
        need(phrase in visual, f"visual closure missing: {phrase!r}")
    build_log = repo_path(UNIT_PATHS["build_log"]).read_text(encoding="utf-8")
    need("Overfull \\hbox" not in build_log, "final log still has overfull hbox")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = load_json(path)
    need(isinstance(bundle, dict), "proof bundle root invalid")
    require_keys(bundle, ("schema_version", "date", "unit", "publication"), "proof bundle")
    need(bundle["schema_version"] == 1, "proof bundle schema_version must be 1")
    need(isinstance(bundle["date"], str) and DATE.fullmatch(bundle["date"]), "proof bundle date invalid")
    raw_unit = bundle["unit"]
    pub = bundle["publication"]
    need(isinstance(raw_unit, dict) and isinstance(pub, dict), "proof bundle sections invalid")
    require_keys(raw_unit, UNIT_PATHS, "proof bundle unit")
    require_keys(
        pub,
        (
            "content_commit",
            "content_tree",
            "content_readback",
            "receipt",
            "receipt_commit",
            "receipt_tree",
            "receipt_readback",
        ),
        "proof bundle publication",
    )
    for key in ("content_commit", "content_tree", "receipt_commit", "receipt_tree"):
        need(isinstance(pub[key], str) and HEX40.fullmatch(pub[key]), f"publication.{key} invalid")
    need(pub["content_commit"] != pub["receipt_commit"], "content and receipt commits must differ")
    specs: dict[str, dict[str, Any]] = {}
    for key, expected_path in UNIT_PATHS.items():
        need(isinstance(raw_unit[key], dict), f"unit.{key} invalid")
        specs[key] = validate_identity(raw_unit[key], expected_path, f"unit.{key}")
    need(raw_unit["reader"].get("pages") == 9, "unit.reader.pages must be 9")
    specs["reader"]["pages"] = 9
    need(
        (specs["terminology_delta"]["bytes"], specs["terminology_delta"]["sha256"])
        == (2766, "9939372a066946a23b644e6ed3a78abb9bbbc44d1a33879d3c63c9ef97147116"),
        "terminology delta identity changed",
    )
    validate_backend(specs)

    content_local, content_records = validate_inventory(
        pub["content_readback"], CONTENT_RB, pub["content_commit"], pub["content_tree"], CONTENT_PARENT, "content readback"
    )
    receipt_local = validate_identity(pub["receipt"], RECEIPT, "receipt")
    receipt_rb_local, receipt_records = validate_inventory(
        pub["receipt_readback"], RECEIPT_RB, pub["receipt_commit"], pub["receipt_tree"], pub["content_commit"], "receipt readback"
    )
    for spec in specs.values():
        require_record(content_records, spec, "content readback")
    require_record(receipt_records, receipt_local, "receipt readback")
    require_record(receipt_records, content_local, "receipt readback")
    pub["content_readback"] = content_local
    pub["receipt"] = receipt_local
    pub["receipt_readback"] = receipt_rb_local
    bundle["unit"] = specs
    bundle["publication"] = pub

    verify_live_public(
        pub["content_commit"],
        pub["content_tree"],
        pub["receipt_commit"],
        pub["receipt_tree"],
        specs.values(),
        (receipt_local, content_local),
    )
    return bundle


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def replace_between(text: str, start: str, end: str, replacement: str, context: str) -> str:
    need(text.count(start) == 1, f"{context}: start anchor count {text.count(start)}")
    left = text.index(start)
    right = text.find(end, left + len(start))
    need(right >= 0, f"{context}: end anchor missing")
    return text[:left] + replacement.rstrip() + "\n\n" + text[right:]


def boundary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    unit = bundle["unit"]
    pub = bundle["publication"]
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))
    return {
        "id": UNIT_ID,
        "source": SOURCE_RANGE,
        "source_span_bytes": SOURCE_BYTES,
        "source_span_sha256": SOURCE_SHA,
        "source_mapping": "authority lines 936-1106 map one-for-one to 171 target records at canonical lines 933-1103; blank boundary line 1107 is omitted",
        "candidate": unit["candidate"]["path"],
        "candidate_bytes": unit["candidate"]["bytes"],
        "candidate_sha256": unit["candidate"]["sha256"],
        "target": "repo/source/chapter4.tex:933-1103",
        "target_full_bytes": unit["target"]["bytes"],
        "target_full_sha256": unit["target"]["sha256"],
        "reader": unit["reader"]["path"],
        "reader_pages": 9,
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
        "visual_qa": "9/9 pages inspected in Poppler and MuPDF; 54 renders cover two clean builds and the artifact; all same-renderer decoded pixels agree, all edge checks have zero ink, 37 named destinations and 14 GoTo actions resolve, three HTTPS URIs are intended, and 29 fonts are embedded; untagged PDF disclosed",
        "corrections": ["O013-LI-U031-COR-001 completes the induced supersolvable-series proof with explicit trivial or prime-cyclic factors and removal of repeated adjacent terms"],
        "digital_reflow": "O013-LI-U031-REFLOW-001 splits the four-term display that measured 42.13312 pt overfull without changing equality, signs, terms, or order; compact final indexes remove the sparse tenth page",
        "protected_text_localizations": 8,
        "terminology_rows": 14,
        "content_commit": pub["content_commit"],
        "content_tree": pub["content_tree"],
        "content_readback_path_fetches": content["path_fetch_count"],
        "content_readback_bytes": content["total_bytes_fetched"],
        "content_readback_inventory": pub["content_readback"]["path"],
        "content_readback_inventory_bytes": pub["content_readback"]["bytes"],
        "content_readback_inventory_sha256": pub["content_readback"]["sha256"],
        "receipt": pub["receipt"]["path"],
        "receipt_bytes": pub["receipt"]["bytes"],
        "receipt_sha256": pub["receipt"]["sha256"],
        "receipt_commit": pub["receipt_commit"],
        "receipt_tree": pub["receipt_tree"],
        "receipt_readback_files": receipt["path_fetch_count"],
        "receipt_readback_bytes": receipt["total_bytes_fetched"],
        "receipt_readback_inventory": pub["receipt_readback"]["path"],
        "receipt_readback_inventory_bytes": pub["receipt_readback"]["bytes"],
        "receipt_readback_inventory_sha256": pub["receipt_readback"]["sha256"],
        "state": "public_readback_passed; complete Section 4.7",
    }


def next_boundary(pub: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "component": "li-volume-1-complete",
        "completed_preservation_action": (
            f"Unit 031 content commit {pub['content_commit']} and receipt commit "
            f"{pub['receipt_commit']} passed anonymous readback. Zenodo remains "
            "the nonduplicative 0.6.0 checkpoint through Unit 024 and complete Chapter 3."
        ),
        "next_admission_unit": NEXT_ID,
        "source_path": SOURCE_PATH,
        "source_line_start": 1108,
        "source_line_end": 1388,
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
        "next_source_cursor": "chapter4.tex:1389",
        "chapter": "Chapter 4 - group theory",
        "prepared_isolated_units": "Units 032-042 are translated candidates and remain outside canonical repo/source until admitted in order; Units 032-035 finish Chapter 4 and Units 036-042 continue through the complete Chapter 5 unique-factorization section.",
        "latest_isolated_candidate": "build/unit-042-candidate/chapter5-unique-factorization-id.tex",
        "latest_authority_span": "chapter5.tex:958-1182",
        "latest_authority_bytes": 22981,
        "latest_authority_sha256": "2e3758fa4b4175eeba5969159a89ccb40895c173c12699a8c2211e68a1e94b2a",
        "latest_candidate_bytes": 29674,
        "latest_candidate_sha256": "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a",
        "latest_candidate_checker": "scripts/check_unit_042_candidate.py",
        "latest_candidate_checker_bytes": 21414,
        "latest_candidate_checker_sha256": "583bd404e4ff529c2231f287a3451a808d3f85144383d02fddfcecb65699e198",
        "latest_candidate_review": "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md",
        "latest_candidate_review_bytes": 8214,
        "latest_candidate_review_sha256": "bd4898df0f7cedfbd05f6806f8329a85fedeee1ef9c2cead6619779c6242c927",
        "latest_corrections": ["O013-LI-U042-COR-001 through O013-LI-U042-COR-007 remain isolated and may not skip Units 032-041"],
        "translation_cursor_after_prepared_candidates": "chapter5.tex:1184; line 1183 is the excluded blank separator; Unit 043 has not started",
        "rule": "Admit Units 032-042 sequentially with terminology, canonical integration, reader, backend, build, visual QA, narrow publication, and public-byte readback while continuing isolated translation from chapter5.tex:1184 when it does not delay admission.",
    }


def ident(spec: Mapping[str, Any]) -> str:
    return f"{spec['bytes']:,} bytes / SHA-256 {spec['sha256']}"


def public_summary(bundle: Mapping[str, Any]) -> str:
    unit = bundle["unit"]
    pub = bundle["publication"]
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))
    return f"""Current admitted boundary: Li Units 001-031 through complete Section 4.7.
Unit 031 authority is {SOURCE_RANGE}, 172 normalized-LF records / {SOURCE_BYTES:,}
bytes / SHA-256 {SOURCE_SHA}; blank boundary line 1107 is excluded from the
171-record target mapping at canonical lines 933-1103. The final candidate is
{ident(unit['candidate'])}; canonical chapter4.tex is {ident(unit['target'])}.
Its centered nine-page reader is {ident(unit['reader'])}, and its schema-valid
backend is {ident(unit['backend'])}. Backend validation is
{ident(unit['backend_validation'])}; the admission receipt is
{ident(unit['admission_receipt'])}; and the final audit is
{ident(unit['final_audit'])}.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U031-COR-001 is separately provenanced. The first reader exposed
a 42.13312 pt overflow in a four-term display; target-only reflow
O013-LI-U031-REFLOW-001 splits it without changing equality, signs, terms, or
order. Compact final indexes remove the sparse tenth page. The final reader has
nine centered pages and no actionable visual or build defect; its untagged
accessibility limitation is disclosed.

Content commit {pub['content_commit']}, tree {pub['content_tree']}, passed
anonymous readback for {content['path_fetch_count']} paths /
{content['total_bytes_fetched']:,} bytes. Receipt commit {pub['receipt_commit']},
tree {pub['receipt_tree']}, passed anonymous readback for
{receipt['path_fetch_count']} paths / {receipt['total_bytes_fetched']:,} bytes
and is the verified remote base. The 229-page checkpoint reader 0.6.0 remains
the nonduplicative Zenodo preservation release."""


def next_summary() -> str:
    return f"""Unit 031 and complete Section 4.7 are public and byte-verified.
The following source-order admission boundary is Unit 032 at {NEXT_RANGE}; its
{NEXT_CANDIDATE_BYTES:,}-byte isolated candidate has SHA-256
{NEXT_CANDIDATE_SHA}. Its checker has SHA-256 {NEXT_CHECKER_SHA}. The candidate
remains isolated until Unit 032 terminology, integration, reader, backend,
build, all-page visual, publication, and anonymous-readback gates pass. The
active cursor is chapter4.tex:1108 and the cursor after Unit 032 will be
chapter4.tex:1389. Units 032-042 remain strictly source-ordered. The isolated
translation cursor remains chapter5.tex:1184; Unit 043 has not started."""


def make_updates(originals: Mapping[str, bytes], bundle: Mapping[str, Any]) -> dict[str, bytes]:
    unit = bundle["unit"]
    pub = bundle["publication"]
    bound = boundary(bundle)
    content = load_json(repo_path(CONTENT_RB))
    receipt_rb = load_json(repo_path(RECEIPT_RB))

    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    cursor["updated"] = bundle["date"]
    cursor["last_admitted_unit"] = bound
    cursor["next_source_boundary"] = next_boundary(pub)
    cursor["terminology_qa"].update({
        "path": unit["terminology_audit"]["path"],
        "bytes": unit["terminology_audit"]["bytes"],
        "sha256": unit["terminology_audit"]["sha256"],
        "previous_path": "qa/UNIT_030_TERMINOLOGY_AUDIT_20260826.md",
        "previous_sha256": "45e11fd3eb0da54792fff0a7c7c5e5ffcb6207c053dec39b310dc46c338d49f6",
        "glossary": unit["glossary"]["path"],
        "glossary_bytes": unit["glossary"]["bytes"],
        "glossary_sha256": unit["glossary"]["sha256"],
        "glossary_delta": "14 Unit 031 rows covering solvable, supersolvable, and nilpotent groups; commutators and series; symplectic forms; directional derivatives; canonical commutation; Heisenberg groups; upper-triangular matrix groups; and Fourier transforms",
        "model": MODEL,
    })
    cursor["publication"].update({
        "expected_remote_base": pub["receipt_commit"],
        "last_public_unit": UNIT_ID,
        "unit_031_content_commit": pub["content_commit"],
        "unit_031_content_tree": pub["content_tree"],
        "unit_031_public_readback_files": content["path_fetch_count"],
        "unit_031_public_readback_bytes": content["total_bytes_fetched"],
        "unit_031_content_readback": pub["content_readback"]["path"],
        "unit_031_content_readback_bytes": pub["content_readback"]["bytes"],
        "unit_031_content_readback_sha256": pub["content_readback"]["sha256"],
        "unit_031_receipt": pub["receipt"]["path"],
        "unit_031_receipt_bytes": pub["receipt"]["bytes"],
        "unit_031_receipt_sha256": pub["receipt"]["sha256"],
        "unit_031_receipt_commit": pub["receipt_commit"],
        "unit_031_receipt_tree": pub["receipt_tree"],
        "unit_031_receipt_readback_files": receipt_rb["path_fetch_count"],
        "unit_031_receipt_readback_bytes": receipt_rb["total_bytes_fetched"],
        "unit_031_receipt_readback_inventory": pub["receipt_readback"]["path"],
        "unit_031_receipt_readback_inventory_bytes": pub["receipt_readback"]["bytes"],
        "unit_031_receipt_readback_inventory_sha256": pub["receipt_readback"]["sha256"],
        "unit_031_state": "content and sanitized receipt public; anonymous readback passed",
    })
    cursor["next_action"] = (
        "Admit Unit 032 at chapter4.tex:1108-1388 and continue strictly through "
        "the isolated Unit 042 candidate; Unit 042 may not skip Units 032-041. "
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
        "immediate_action": "admit Chapter 4 Unit 032 at chapter4.tex:1108-1388 and continue strictly in source order",
        "builder": "scripts/build_unit_032.ps1",
        "coverage": "complete prelude, Chapters 1-3, and Chapter 4 opening through complete Section 4.7 in 31 admitted units; later Chapter 4 and Chapters 5-10 remain unadmitted",
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
        "cursor_after_next_admission": "chapter4.tex:1389",
        "prepared_isolated_units": "Units 032-042; Units 032-035 finish Chapter 4 and Units 036-042 continue Chapter 5 through complete unique factorization",
        "latest_isolated_candidate": "build/unit-042-candidate/chapter5-unique-factorization-id.tex",
        "latest_candidate_bytes": 29674,
        "latest_candidate_sha256": "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a",
        "latest_candidate_checker": "scripts/check_unit_042_candidate.py",
        "latest_candidate_checker_bytes": 21414,
        "latest_candidate_checker_sha256": "583bd404e4ff529c2231f287a3451a808d3f85144383d02fddfcecb65699e198",
        "latest_candidate_review": "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md",
        "latest_candidate_review_bytes": 8214,
        "latest_candidate_review_sha256": "bd4898df0f7cedfbd05f6806f8329a85fedeee1ef9c2cead6619779c6242c927",
        "translation_cursor_after_staging": "chapter5.tex:1184; line 1183 is excluded blank; Unit 043 has not started",
        "post_li_component": "complete admitted Duncan CC BY 4.0 repository, six exact repaired CRing GFDL spans, and separate connective/mastery layer; Etingof reference-only",
    }
    recovery["publication_resume"]["github"] = (
        f"Unit 031 content is public at commit {pub['content_commit']} "
        f"(tree {pub['content_tree']}); its content inventory passed. Receipt "
        f"commit {pub['receipt_commit']} (tree {pub['receipt_tree']}) and its "
        "receipt inventory also passed anonymous byte readback. Checkpoint 0.6.0 "
        "remains public and nonduplicative."
    )

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    goal = replace_between(
        goal,
        "Current admitted boundary: Li Units 001-030 through complete Section 4.6.\n",
        "A bounded Indonesian field-usage check",
        public_summary(bundle),
        "goal current progress",
    )
    goal = replace_between(
        goal,
        "Unit 030 content and sanitized\nreceipt are public and byte-verified.",
        "The Duncan source/build gate",
        next_summary(),
        "goal next-boundary tail",
    )
    need("b6bc5e41ed428dfde4526558b9a3ef36117cc55a7c0386bc360affa78b82fb01" not in goal, "stale pre-reflow candidate remains in goal")
    need("5557a3c54146d0e5fffe09406874ab252443d943f938448cfd3e534eb35b384b" not in goal, "stale pre-reflow checker remains in goal")
    for phrase in ("The goal is complete only when", "Duncan", "CRing", "Etingof remains reference-only"):
        need(phrase in goal, f"goal architecture lost: {phrase}")

    state = originals["00_control/CURRENT_STATE.md"].decode("utf-8")
    state = replace_between(
        state,
        "## Exact next action\n",
        "## Not complete\n",
        "## Unit 031 public boundary\n\n" + public_summary(bundle) + "\n\n## Exact next action\n\n" + next_summary(),
        "CURRENT_STATE tail",
    )
    need("## Not complete\n" in state, "CURRENT_STATE lost not-complete section")

    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    need("## D087" in decision and "## D088" not in decision, "decision cursor is not exactly D087")
    decision += f"""
## D088 — {bundle['date']} — Unit 031 published and cursor advanced

Publish complete Section 4.7 at authority {SOURCE_RANGE} only after the final
nine-page reader, schema-valid backend, independent admission audit, content
commit, receipt commit, and both anonymous readback inventories agree. Content
commit {pub['content_commit']}, tree {pub['content_tree']}, and receipt commit
{pub['receipt_commit']}, tree {pub['receipt_tree']}, are the exact public
boundary. The initial 42.13312 pt display overflow is closed by separately
provenanced target-only reflow O013-LI-U031-REFLOW-001; compact indexes remove
the sparse tenth page. These are resolved reader defects, not blockers. Advance
to Unit 032 at chapter4.tex:1108 while preserving the full Li, Duncan,
selected-CRing, and separate connective/mastery architecture with Etingof
reference-only.
"""

    worklog = originals["00_control/WORKLOG.jsonl"].decode("utf-8")
    work_event = {
        "date": bundle["date"],
        "event": "unit_031_published_and_read_back",
        "result": (
            f"Section4.7 at {SOURCE_RANGE} is canonically integrated and public. "
            f"Candidate {unit['candidate']['bytes']} bytes / {unit['candidate']['sha256']}; "
            f"chapter4.tex {unit['target']['bytes']} bytes / {unit['target']['sha256']}; "
            f"reader 9 pages / {unit['reader']['bytes']} bytes / {unit['reader']['sha256']}; "
            f"backend {unit['backend']['bytes']} bytes / {unit['backend']['sha256']}. "
            "All deterministic gates pass. O013-LI-U031-COR-001 is explicit. "
            "O013-LI-U031-REFLOW-001 removes a measured 42.13312 pt overflow "
            "without changing mathematics; compact indexes remove the sparse tenth page. "
            f"Content {pub['content_commit']} / tree {pub['content_tree']} and receipt "
            f"{pub['receipt_commit']} / tree {pub['receipt_tree']} passed anonymous "
            "readback. Cursor advances to Unit032 chapter4.tex:1108; full goal remains active."
        ),
    }
    worklog += json.dumps(work_event, ensure_ascii=False, separators=(",", ":")) + "\n"

    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    events = (
        {
            "id": "O013-ADV-0095",
            "date": bundle["date"],
            "severity": "P2",
            "surface": "li_unit_031_four_term_display_overflow",
            "status": "closed_by_separate_target_only_digital_reflow",
            "summary": "The first Unit031 reader measured a 42.13312 pt overflow in a four-term display. O013-LI-U031-REFLOW-001 inserts a readable line break while preserving equality, every sign, all terms, and their order; the final log has zero overfull diagnostics. This is digital reflow, not a source correction.",
        },
        {
            "id": "O013-ADV-0096",
            "date": bundle["date"],
            "severity": "P3",
            "surface": "li_unit_031_sparse_tenth_index_page",
            "status": "closed_by_compact_indexes",
            "summary": "The initial Unit031 reader left a sparse tenth page for short indexes. Compact final indexes place six term entries and three symbol entries on a normally filled ninth page without removing content; all nine pages pass dual-renderer visual and edge checks.",
        },
    )
    for event in events:
        need(event["id"] not in adverse, f"adverse ID exists: {event['id']}")
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
    need(cursor["last_admitted_unit"]["id"] == UNIT_ID, "Unit 031 not admitted")
    need(cursor["next_source_boundary"]["source_line_start"] == 1108, "cursor not advanced to 1108")
    need(recovery["next_cursor"]["next_admission_unit"] == NEXT_ID, "recovery not advanced to Unit 032")
    need(cursor["publication"]["expected_remote_base"] == bundle["publication"]["receipt_commit"], "remote base mismatch")
    for rel in ("00_control/CURRENT_GOAL_AND_WORKFLOW.md", "00_control/CURRENT_STATE.md"):
        text = updates[rel].decode("utf-8")
        need("42.13312 pt" in text and "sparse tenth page" in text, f"{rel} lost layout history")
        need("Unit 032" in text and "chapter4.tex:1108" in text, f"{rel} lost next cursor")
    for rel in ("00_control/WORKLOG.jsonl", "00_control/ADVERSE_LEDGER.jsonl"):
        ids: set[str] = set()
        for line_no, line in enumerate(updates[rel].decode("utf-8").splitlines(), 1):
            value = json.loads(line, object_pairs_hook=no_duplicate_keys)
            need(isinstance(value, dict), f"{rel}:{line_no} invalid")
            if "id" in value:
                need(value["id"] not in ids, f"{rel} duplicate ID {value['id']}")
                ids.add(value["id"])


def atomic_write(updates: Mapping[str, bytes], originals: Mapping[str, bytes]) -> None:
    temps: dict[str, Path] = {}
    replaced: list[str] = []
    try:
        for rel, payload in updates.items():
            target = repo_path(rel)
            fd, name = tempfile.mkstemp(prefix=f".{target.name}.u031-", suffix=".tmp", dir=target.parent)
            temp = Path(name)
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            need(file_identity(temp) == (len(payload), digest(payload)), f"temporary write failed: {rel}")
            temps[rel] = temp
        for rel in CONTROL_TARGETS:
            os.replace(temps.pop(rel), repo_path(rel))
            replaced.append(rel)
        for rel, payload in updates.items():
            need(repo_path(rel).read_bytes() == payload, f"post-write mismatch: {rel}")
    except Exception:
        for rel in reversed(replaced):
            target = repo_path(rel)
            fd, name = tempfile.mkstemp(prefix=f".{target.name}.rollback-", suffix=".tmp", dir=target.parent)
            with os.fdopen(fd, "wb") as stream:
                stream.write(originals[rel])
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, target)
        raise
    finally:
        for temp in temps.values():
            try:
                temp.unlink()
            except FileNotFoundError:
                pass


def template() -> dict[str, Any]:
    def blank(path: str, **extra: Any) -> dict[str, Any]:
        return {"path": path, "bytes": 0, "sha256": "", **extra}
    return {
        "schema_version": 1,
        "date": "2026-08-26",
        "unit": {
            key: blank(path, **({"pages": 9} if key == "reader" else {}))
            for key, path in UNIT_PATHS.items()
        },
        "publication": {
            "content_commit": "",
            "content_tree": "",
            "content_readback": blank(CONTENT_RB),
            "receipt": blank(RECEIPT),
            "receipt_commit": "",
            "receipt_tree": "",
            "receipt_readback": blank(RECEIPT_RB),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-bundle", type=Path, help="strict JSON with exact Unit 031 local and public identities")
    parser.add_argument("--apply", action="store_true", help="replace exactly seven controls after all gates pass")
    parser.add_argument("--print-template", action="store_true", help="print required proof-bundle shape and exit")
    args = parser.parse_args()
    if args.print_template:
        need(args.proof_bundle is None and not args.apply, "--print-template cannot be combined")
        print(json.dumps(template(), ensure_ascii=False, indent=2))
        return 0
    need(args.proof_bundle is not None, "--proof-bundle is required")
    bundle_path = args.proof_bundle.resolve()
    need(bundle_path.is_file(), f"proof bundle missing: {bundle_path}")
    originals = validate_base()
    bundle = validate_bundle(bundle_path)
    updates = make_updates(originals, bundle)
    validate_updates(updates, bundle)
    if args.apply:
        atomic_write(updates, originals)
    report = {
        "status": "PASS",
        "mode": "apply" if args.apply else "dry-run",
        "unit": UNIT_ID,
        "next_unit": NEXT_ID,
        "next_source_cursor": "chapter4.tex:1108",
        "content_commit": bundle["publication"]["content_commit"],
        "receipt_commit": bundle["publication"]["receipt_commit"],
        "targets": [
            {"path": rel, "bytes": len(updates[rel]), "sha256": digest(updates[rel])}
            for rel in CONTROL_TARGETS
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
