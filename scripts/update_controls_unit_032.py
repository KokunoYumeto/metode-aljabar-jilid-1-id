#!/usr/bin/env python3
"""Fail-closed Unit 032 durable-control transition for O013.

Default mode verifies the exact local/public proof bundle and renders all seven
new controls in memory. --apply is required to replace the controls. The tool
uses anonymous HTTPS reads only (no Git command) and cannot write outside
CONTROL_TARGETS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
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
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md": "3e4d7bd0cca512d7eac274a1c3d661efc672e354598e1aee983453c4fb462904",
    "00_control/CURRENT_STATE.md": "3868f3ea64b12629176b441e47cdf6809b7bdb1686570c4773f60a9b96e97260",
    "00_control/CURRENT_CURSOR.json": "02fb0796f6d590275456b65cdda32117dfbb8e8fabc8ca2c7274c43349ed34f4",
    "00_control/RECOVERY_POINTER.json": "ac7aead0c0e680a7680e78c8d9be513933e34e9781d1adef23208d0669bb6bf2",
    "00_control/DECISION_LOG.md": "2cc135adb5fd95986fa0e94aa838ae4116d26bc6074535413211283dc9c90df2",
    "00_control/WORKLOG.jsonl": "635b2060c75a193acbf3fb1cc91cc09989a245cfab5b7e5adf781513751a8df2",
    "00_control/ADVERSE_LEDGER.jsonl": "d7b1e4fb2ddf7df2fe8dbad18ae0f148776e31f49f535611935808877f745a17",
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

UNIT_ID = "unit-032-bab-4-grup-bebas"
PROVISIONAL_CURSOR_ID = UNIT_ID
SOURCE_PATH = (
    "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/"
    "chapter4.tex"
)
SOURCE_RANGE = "chapter4.tex:1108-1388"
SOURCE_BYTES = 22547
SOURCE_SHA = "5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af"
UNIT_PATHS = {
    "candidate": "build/unit-032-candidate/chapter4-free-groups-id.tex",
    "target": "repo/source/chapter4.tex",
    "reader": "artifacts/unit-032-bab-4-grup-bebas-id.pdf",
    "backend": "backend/data/unit-032-bab-4-grup-bebas.json",
    "backend_validation": "qa/unit-032-evidence/backend-validation.json",
    "admission_receipt": "qa/UNIT_032_ADMISSION_20260826.md",
    "final_audit": "qa/UNIT_032_FINAL_AUDIT_20260826.md",
    "visual_receipt": "qa/UNIT_032_VISUAL_QA_20260826.md",
    "build_log": "qa/UNIT_032_BUILD_FINAL.log",
    "terminology_audit": "qa/UNIT_032_TERMINOLOGY_AUDIT_20260826.md",
    "terminology_delta": "build/unit-032-staging/terminology-delta.csv",
    "glossary": "00_control/TERMINOLOGY.id-ID.csv",
}
EXPECTED_UNIT_IDENTITIES = {
    "candidate": (27910, "28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc"),
    "target": (181896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680"),
    "reader": (149624, "904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf"),
    "backend": (460681, "a3f68cd45d5fc44720e769c7a12d745a4af78d7a361e6e8b81a1c5019be1a030"),
    "backend_validation": (5422, "b66c40151489b4d162e63e9edef3da1d7c593362002bb8e0b9a6f5ba3410be6d"),
    "admission_receipt": (4274, "065bba6285a1668abdd29f8d349f9f905b048755dc429e8e8d08d7944dc5c1f0"),
    "final_audit": (5421, "e8d214df7a0feaf60a14a93e2b554db8fe881379caf98109737a9947f5d9e9e5"),
    "visual_receipt": (5996, "8f0e63c07a43e1c8e96415ccda97507c6a1e1a81b4cf2c344b9fb761a653a976"),
    "build_log": (78679, "3da283cc2d95f15148c6a5c5392951134235c104b7bd8fdee7844ea4217d2a31"),
    "terminology_audit": (3255, "2dc5c4ed17f810c5b15fa4c16db491530dce6e3d0597344118fd4f5bd5668b83"),
    "terminology_delta": (4745, "3d742473a35c0bdd890fecbfe3f0dc37e8dc96f8452287c6fadc35dda46d6fad"),
    "glossary": (74335, "bb58d18ad5802c5c2159db092f0fc322761f8f9559ea7efd3789ab8d7317e582"),
}
CONTENT_RB = "qa/PUBLICATION_GITHUB_UNIT_032_CONTENT_READBACK.json"
RECEIPT = "qa/PUBLICATION_GITHUB_UNIT_032_20260826.md"
RECEIPT_RB = "qa/PUBLICATION_GITHUB_UNIT_032_RECEIPT_READBACK.json"
CONTENT_PARENT = "8a2112a6a2d3d0e8bbedef7e30c6cc8bff5aa7b9"
CONTENT_COMMIT = "bc5e43a75925d522a80600724d6d95e40ad55f75"
CONTENT_TREE = "13afc9751570e15d24a77063606a455dc420f69a"
RECEIPT_COMMIT = "5780621108e60521427b20a77090114590abe6b0"
RECEIPT_TREE = "1f88e8d6901c01eed57ecb602484eb6c2bff1b87"
CONTENT_READBACK_IDENTITY = (28096, "09a04f7d85ca36da65fd856cdf9b203ceefa63579ea9766574351bff1cde8e5c")
RECEIPT_IDENTITY = (1711, "c59915bc05e2e26f4828daafbad1442b7923c47e5e5f0289f2409072d91ee32e")
RECEIPT_READBACK_IDENTITY = (2069, "161c67848ab6652e8f4e95c43e05ecbeb4340b640fc68f183f6cb2dc52e17f49")

NEXT_ID = "unit-033-bab-4-grup-simetris"
NEXT_RANGE = "chapter4.tex:1389-1608"
NEXT_BYTES = 19076
NEXT_SHA = "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a"
NEXT_CANDIDATE = "build/unit-033-candidate/chapter4-symmetric-groups-id.tex"
NEXT_CANDIDATE_BYTES = 23074
NEXT_CANDIDATE_SHA = "09e8ec87919a6620e5baac6a07b470b2d03d24a5775d8c66bf6de9af43dc1953"
NEXT_CHECKER = "scripts/check_unit_033_candidate.py"
NEXT_CHECKER_BYTES = 16727
NEXT_CHECKER_SHA = "670016f2f054139c5da78fb2c412f68f7836d2bc4c1dab0282a4041e3a6baa4f"
NEXT_REVIEW = "qa/UNIT_033_TRANSLATION_REVIEW_20260825.md"
NEXT_REVIEW_BYTES = 9677
NEXT_REVIEW_SHA = "fe27be28e24d220aa8d3bc9312e2cc51f991c6d727abac89ec52a84cd51f43ae"

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
            "User-Agent": "o013-unit032-control-gate/1",
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
    api = f"https://api.github.com/repos/{SLUG}"
    ref = http_json(f"{api}/git/ref/heads/{BRANCH}")
    need(ref.get("object", {}).get("sha") == receipt_commit, "live public main is not the receipt commit")
    for commit, tree, parent, label in (
        (content_commit, content_tree, CONTENT_PARENT, "content"),
        (receipt_commit, receipt_tree, content_commit, "receipt"),
    ):
        public_commit = http_json(f"{api}/git/commits/{commit}")
        need(public_commit.get("sha") == commit, f"public {label} commit mismatch")
        need(public_commit.get("tree", {}).get("sha") == tree, f"public {label} tree mismatch")
        parents = public_commit.get("parents")
        need(isinstance(parents, list) and len(parents) == 1, f"public {label} parent topology mismatch")
        need(parents[0].get("sha") == parent, f"public {label} parent mismatch")
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
        need(digest(payload) == BASE_HASHES[rel], f"published Unit 031 control base drift: {rel}")
        originals[rel] = payload
    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    need(cursor.get("goal_status") == "active", "cursor goal not active")
    need(cursor.get("selected_architecture") == ARCHITECTURE, "architecture drift")
    need(cursor.get("architecture_authority", {}).get("path") == ARCH_AUTHORITY, "architecture authority path drift")
    need(cursor.get("architecture_authority", {}).get("sha256") == ARCH_SHA, "architecture authority hash drift")
    need(cursor.get("architecture_authority", {}).get("etingof_state") == "reference_only", "Etingof state drift")
    need(cursor.get("duncan_authority_admitted", {}).get("commit") == DUNCAN_COMMIT, "Duncan authority drift")
    need(cursor.get("last_admitted_unit", {}).get("id") == "unit-031-bab-4-grup-solvabel-dan-nilpoten", "cursor not at Unit 031")
    next_boundary = cursor.get("next_source_boundary", {})
    need(
        next_boundary.get("next_admission_unit") == PROVISIONAL_CURSOR_ID,
        "Unit 032 cursor identity drift",
    )
    need(
        next_boundary.get("source_line_start") == 1108
        and next_boundary.get("source_line_end") == 1388
        and next_boundary.get("candidate_path") == UNIT_PATHS["candidate"],
        "Unit 032 source/candidate cursor drift",
    )
    need(recovery.get("current_boundary", {}).get("unit") == "unit-031-bab-4-grup-solvabel-dan-nilpoten", "recovery not at Unit 031")
    terminal = recovery.get("terminal_condition", "")
    for phrase in ("complete Li Volume 1", "Duncan", "six selected CRing spans", "connective/mastery layer", "Etingof reference-only"):
        need(phrase in terminal, f"terminal architecture missing: {phrase}")
    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    for phrase in ("Wen-Wei Li", "Duncan", "CRing", "connective", "mastery layer", "The goal is complete only when"):
        need(phrase in goal, f"durable goal scope missing: {phrase}")
    for rel, expected in (
        (NEXT_CANDIDATE, (NEXT_CANDIDATE_BYTES, NEXT_CANDIDATE_SHA)),
        (NEXT_CHECKER, (NEXT_CHECKER_BYTES, NEXT_CHECKER_SHA)),
        (NEXT_REVIEW, (NEXT_REVIEW_BYTES, NEXT_REVIEW_SHA)),
    ):
        path = repo_path(rel)
        need(path.is_file(), f"Unit 033 cursor file missing: {rel}")
        need(file_identity(path) == expected, f"Unit 033 cursor identity drift: {rel}")
    authority = repo_path(SOURCE_PATH).read_text(encoding="utf-8").splitlines()
    next_records = authority[1388:1608]
    need(len(next_records) == 220 and next_records[-1] == "", "Unit 033 authority record boundary drift")
    next_payload = ("\n".join(next_records) + "\n").encode("utf-8")
    need((len(next_payload), digest(next_payload)) == (NEXT_BYTES, NEXT_SHA), "Unit 033 authority slice drift")
    return originals


def validate_backend(specs: Mapping[str, Mapping[str, Any]]) -> None:
    data = load_json(repo_path(UNIT_PATHS["backend_validation"]))
    need(data.get("status") == "PASS", "backend validation is not PASS")
    need(data.get("unit") == UNIT_ID, "backend unit mismatch")
    need(data.get("authority") == "chapter4.tex:1108-1388 (blank line 1388 omitted from mapping)", "backend authority mismatch")
    need(data.get("target") == "chapter4.tex:1104-1383", "backend target mismatch")
    need(data.get("provenance_model") == MODEL, "backend model provenance mismatch")
    need(
        data.get("artifact") == {
            "path": specs["reader"]["path"],
            "pages": 13,
            "bytes": specs["reader"]["bytes"],
            "sha256": specs["reader"]["sha256"],
        },
        "backend artifact identity mismatch",
    )
    exact_counts = {
        "environment_pairs": 52,
        "environment_markers": 104,
        "labels": 10,
        "ordinary_references": 14,
        "equation_references": 6,
        "citations": 6,
        "protected_math_zones": 367,
        "diagrams": 11,
        "diagram_arrows": 28,
        "drawing_commands": 8,
        "index_entries": 7,
        "terminology_rows": 30,
        "source_corrections": 2,
        "digital_reflows": 2,
        "protected_text_localizations": 13,
        "citation_locator_localizations": 4,
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
    for phrase in ("O013-LI-U032-COR-001", "O013-LI-U032-COR-002", "O013-LI-U032-REFLOW-001", "O013-LI-U032-REFLOW-002", MODEL):
        need(phrase in backend_text, f"backend provenance missing: {phrase}")
    visual = repo_path(UNIT_PATHS["visual_receipt"]).read_text(encoding="utf-8")
    for phrase in ("all three PDFs contain 13 pages", "Exactly 3 nonfatal underfull hboxes", "zero actionable defects", MODEL):
        need(phrase in visual, f"visual closure missing: {phrase!r}")
    build_log = repo_path(UNIT_PATHS["build_log"]).read_text(encoding="utf-8")
    need("Overfull \\hbox" not in build_log, "final log still has overfull hbox")
    need(build_log.count("Underfull \\hbox") == 3, "final log must disclose exactly three underfull hboxes")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = load_json(path)
    need(isinstance(bundle, dict), "proof bundle root invalid")
    require_keys(bundle, ("schema_version", "date", "unit", "publication"), "proof bundle")
    need(bundle["schema_version"] == 1, "proof bundle schema_version must be 1")
    need(isinstance(bundle["date"], str) and DATE.fullmatch(bundle["date"]), "proof bundle date invalid")
    need(bundle["date"] == "2026-08-26", "proof bundle date changed")
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
    need(pub["content_commit"] == CONTENT_COMMIT, "content commit changed")
    need(pub["content_tree"] == CONTENT_TREE, "content tree changed")
    need(pub["receipt_commit"] == RECEIPT_COMMIT, "receipt commit changed")
    need(pub["receipt_tree"] == RECEIPT_TREE, "receipt tree changed")
    specs: dict[str, dict[str, Any]] = {}
    for key, expected_path in UNIT_PATHS.items():
        need(isinstance(raw_unit[key], dict), f"unit.{key} invalid")
        specs[key] = validate_identity(raw_unit[key], expected_path, f"unit.{key}")
        need(
            (specs[key]["bytes"], specs[key]["sha256"]) == EXPECTED_UNIT_IDENTITIES[key],
            f"hard-bound Unit 032 identity changed: {key}",
        )
    need(raw_unit["reader"].get("pages") == 13, "unit.reader.pages must be 13")
    specs["reader"]["pages"] = 13
    validate_backend(specs)

    content_local, content_records = validate_inventory(
        pub["content_readback"], CONTENT_RB, pub["content_commit"], pub["content_tree"], CONTENT_PARENT, "content readback"
    )
    receipt_local = validate_identity(pub["receipt"], RECEIPT, "receipt")
    receipt_rb_local, receipt_records = validate_inventory(
        pub["receipt_readback"], RECEIPT_RB, pub["receipt_commit"], pub["receipt_tree"], pub["content_commit"], "receipt readback"
    )
    need((content_local["bytes"], content_local["sha256"]) == CONTENT_READBACK_IDENTITY, "content readback identity changed")
    need((receipt_local["bytes"], receipt_local["sha256"]) == RECEIPT_IDENTITY, "receipt identity changed")
    need((receipt_rb_local["bytes"], receipt_rb_local["sha256"]) == RECEIPT_READBACK_IDENTITY, "receipt readback identity changed")
    need(load_json(repo_path(CONTENT_RB)).get("path_fetch_count") == 64, "content readback path count changed")
    need(load_json(repo_path(CONTENT_RB)).get("total_bytes_fetched") == 6515805, "content readback byte count changed")
    need(load_json(repo_path(RECEIPT_RB)).get("path_fetch_count") == 3, "receipt readback path count changed")
    need(load_json(repo_path(RECEIPT_RB)).get("total_bytes_fetched") == 104435, "receipt readback byte count changed")
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
        "source_mapping": "authority lines 1108-1387 map one-for-one to 280 target records at canonical lines 1104-1383; blank boundary line 1388 is omitted",
        "candidate": unit["candidate"]["path"],
        "candidate_bytes": unit["candidate"]["bytes"],
        "candidate_sha256": unit["candidate"]["sha256"],
        "target": "repo/source/chapter4.tex:1104-1383",
        "target_full_bytes": unit["target"]["bytes"],
        "target_full_sha256": unit["target"]["sha256"],
        "reader": unit["reader"]["path"],
        "reader_pages": 13,
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
        "visual_qa": "13/13 pages inspected in Poppler and MuPDF; 78 renders cover two clean builds and the artifact; all same-renderer decoded pixels agree, all edge checks have zero ink, 30 internal actions and six safe HTTPS URI actions resolve, and 28 fonts are embedded; exactly three visually non-actionable underfull hboxes and the untagged PDF are disclosed",
        "corrections": [
            "O013-LI-U032-COR-001 changes the normal-closure endpoint from generator count w_n to relation count w_m",
            "O013-LI-U032-COR-002 repairs Guranlnick to Guralnick",
        ],
        "digital_reflow": "O013-LI-U032-REFLOW-001 and O013-LI-U032-REFLOW-002 split finite-support set-builder displays that measured 22.16992 pt and 27.03485 pt overfull while preserving set membership, quantifiers, finite-support conditions, and term order",
        "protected_text_localizations": 13,
        "citation_locator_localizations": 4,
        "terminology_rows": 30,
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
        "state": "public_readback_passed; complete Section 4.8",
    }


def next_boundary(pub: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "component": "li-volume-1-complete",
        "completed_preservation_action": (
            f"Unit 032 content commit {pub['content_commit']} and receipt commit "
            f"{pub['receipt_commit']} passed anonymous readback. Zenodo remains "
            "the nonduplicative 0.6.0 checkpoint through Unit 024 and complete Chapter 3."
        ),
        "next_admission_unit": NEXT_ID,
        "source_path": SOURCE_PATH,
        "source_line_start": 1389,
        "source_line_end": 1608,
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
        "next_source_cursor": "chapter4.tex:1609",
        "chapter": "Chapter 4 - group theory",
        "prepared_isolated_units": "Units 033-042 are translated candidates and remain outside canonical repo/source until admitted in order; Units 033-035 finish Chapter 4 and Units 036-042 continue through the complete Chapter 5 unique-factorization section.",
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
        "rule": "Admit Units 033-042 sequentially with terminology, canonical integration, reader, backend, build, visual QA, narrow publication, and public-byte readback while continuing isolated translation from chapter5.tex:1184 when it does not delay admission.",
    }


def ident(spec: Mapping[str, Any]) -> str:
    return f"{spec['bytes']:,} bytes / SHA-256 {spec['sha256']}"


def public_summary(bundle: Mapping[str, Any]) -> str:
    unit = bundle["unit"]
    pub = bundle["publication"]
    content = load_json(repo_path(CONTENT_RB))
    receipt = load_json(repo_path(RECEIPT_RB))
    return f"""Current admitted boundary: Li Units 001-032 through complete Section 4.8.
Unit 032 authority is {SOURCE_RANGE}, 281 normalized-LF records / {SOURCE_BYTES:,}
bytes / SHA-256 {SOURCE_SHA}; blank boundary line 1388 is excluded from the
280-record target mapping at canonical lines 1104-1383. The final candidate is
{ident(unit['candidate'])}; canonical chapter4.tex is {ident(unit['target'])}.
Its centered thirteen-page reader is {ident(unit['reader'])}, and its schema-valid
backend is {ident(unit['backend'])}. Backend validation is
{ident(unit['backend_validation'])}; the admission receipt is
{ident(unit['admission_receipt'])}; and the final audit is
{ident(unit['final_audit'])}.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U032-COR-001 and O013-LI-U032-COR-002 are separately provenanced.
The first reader exposed 22.16992 pt and 27.03485 pt overflows in finite-support
set-builder displays; target-only reflows O013-LI-U032-REFLOW-001 and
O013-LI-U032-REFLOW-002 remove them without changing set membership,
quantifiers, finite-support conditions, or term order. The final reader has
thirteen centered pages and no actionable visual or build defect. Exactly three
visually non-actionable underfull hboxes and its untagged-PDF accessibility
limitation are disclosed.

Content commit {pub['content_commit']}, tree {pub['content_tree']}, passed
anonymous readback for {content['path_fetch_count']} paths /
{content['total_bytes_fetched']:,} bytes. Receipt commit {pub['receipt_commit']},
tree {pub['receipt_tree']}, passed anonymous readback for
{receipt['path_fetch_count']} paths / {receipt['total_bytes_fetched']:,} bytes
and is the verified remote base. The 229-page checkpoint reader 0.6.0 remains
the nonduplicative Zenodo preservation release."""


def next_summary() -> str:
    return f"""Unit 032 and complete Section 4.8 are public and byte-verified.
The following source-order admission boundary is Unit 033 at {NEXT_RANGE}; its
{NEXT_CANDIDATE_BYTES:,}-byte isolated candidate has SHA-256
{NEXT_CANDIDATE_SHA}. Its checker has SHA-256 {NEXT_CHECKER_SHA}. The candidate
remains isolated until Unit 033 terminology, integration, reader, backend,
build, all-page visual, publication, and anonymous-readback gates pass. The
active cursor is chapter4.tex:1389 and the cursor after Unit 033 will be
chapter4.tex:1609. Units 033-042 remain strictly source-ordered. The isolated
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
        "previous_path": "qa/UNIT_031_TERMINOLOGY_AUDIT_20260826.md",
        "previous_sha256": "16c039b657965f50110b16472818c8b49f82f40d492967a14edf251c87f09836",
        "glossary": unit["glossary"]["path"],
        "glossary_bytes": unit["glossary"]["bytes"],
        "glossary_sha256": unit["glossary"]["sha256"],
        "glossary_delta": "30 Unit 032 rows covering free groups and monoids, reduced words, universal properties, presentations, free products and amalgamated products, subgroup graphs, and Nielsen-Schreier theory",
        "model": MODEL,
    })
    cursor["publication"].update({
        "expected_remote_base": pub["receipt_commit"],
        "last_public_unit": UNIT_ID,
        "unit_032_content_commit": pub["content_commit"],
        "unit_032_content_tree": pub["content_tree"],
        "unit_032_public_readback_files": content["path_fetch_count"],
        "unit_032_public_readback_bytes": content["total_bytes_fetched"],
        "unit_032_content_readback": pub["content_readback"]["path"],
        "unit_032_content_readback_bytes": pub["content_readback"]["bytes"],
        "unit_032_content_readback_sha256": pub["content_readback"]["sha256"],
        "unit_032_receipt": pub["receipt"]["path"],
        "unit_032_receipt_bytes": pub["receipt"]["bytes"],
        "unit_032_receipt_sha256": pub["receipt"]["sha256"],
        "unit_032_receipt_commit": pub["receipt_commit"],
        "unit_032_receipt_tree": pub["receipt_tree"],
        "unit_032_receipt_readback_files": receipt_rb["path_fetch_count"],
        "unit_032_receipt_readback_bytes": receipt_rb["total_bytes_fetched"],
        "unit_032_receipt_readback_inventory": pub["receipt_readback"]["path"],
        "unit_032_receipt_readback_inventory_bytes": pub["receipt_readback"]["bytes"],
        "unit_032_receipt_readback_inventory_sha256": pub["receipt_readback"]["sha256"],
        "unit_032_state": "content and sanitized receipt public; anonymous readback passed",
    })
    cursor["next_action"] = (
        "Admit Unit 033 at chapter4.tex:1389-1608 and continue strictly through "
        "the isolated Unit 042 candidate; Unit 042 may not skip Units 033-041. "
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
        "immediate_action": "admit Chapter 4 Unit 033 at chapter4.tex:1389-1608 and continue strictly in source order",
        "builder": "scripts/build_unit_033.ps1",
        "coverage": "complete prelude, Chapters 1-3, and Chapter 4 opening through complete Section 4.8 in 32 admitted units; later Chapter 4 and Chapters 5-10 remain unadmitted",
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
        "cursor_after_next_admission": "chapter4.tex:1609",
        "prepared_isolated_units": "Units 033-042; Units 033-035 finish Chapter 4 and Units 036-042 continue Chapter 5 through complete unique factorization",
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
        f"Unit 032 content is public at commit {pub['content_commit']} "
        f"(tree {pub['content_tree']}); its content inventory passed. Receipt "
        f"commit {pub['receipt_commit']} (tree {pub['receipt_tree']}) and its "
        "receipt inventory also passed anonymous byte readback. Checkpoint 0.6.0 "
        "remains public and nonduplicative."
    )

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    goal = replace_between(
        goal,
        "Current admitted boundary: Li Units 001-031 through complete Section 4.7.\n",
        "A bounded Indonesian field-usage check",
        public_summary(bundle),
        "goal current progress",
    )
    goal = replace_between(
        goal,
        "Unit 031 and complete Section 4.7 are public and byte-verified.",
        "The Duncan source/build gate",
        next_summary(),
        "goal next-boundary tail",
    )
    need("19583aa71814bbed580d51f39eeaf113a399ec13fef5773a39b6e6cf16289140" not in goal, "stale provisional Unit 032 candidate remains in goal")
    for phrase in ("The goal is complete only when", "Duncan", "CRing", "Etingof remains reference-only"):
        need(phrase in goal, f"goal architecture lost: {phrase}")

    state = originals["00_control/CURRENT_STATE.md"].decode("utf-8")
    state_top = f"""Updated: {bundle['date']}{"  "}
Status: active; Li Units 001-032 are public and byte-verified through complete
Chapter 4 Section 4.8. Unit 032 is public at content commit
`{pub['content_commit']}`; all {content['path_fetch_count']} paths /
{content['total_bytes_fetched']:,} bytes passed anonymous readback. Receipt
commit `{pub['receipt_commit']}` and all {receipt_rb['path_fetch_count']} paths /
{receipt_rb['total_bytes_fetched']:,} bytes also passed. The canonical next
boundary is Unit 033 at `chapter4.tex:1389`; isolated translation reaches Unit
042 and `chapter5.tex:1184`, while Unit 043 has not started. The full active
objective continues from the complete Li edition through complete licensed
Duncan, selected repaired CRing spans, and the separately provenanced
connective and mastery layer; this boundary is not a completion claim."""
    state = replace_between(
        state,
        "Updated: 2026-08-26  \nStatus:",
        "## Completed\n",
        state_top,
        "CURRENT_STATE top",
    )
    state = replace_between(
        state,
        "## Unit 031 public boundary\n",
        "## Not complete\n",
        "## Unit 032 public boundary\n\n" + public_summary(bundle) + "\n\n## Exact next action\n\n" + next_summary(),
        "CURRENT_STATE tail",
    )
    need("## Not complete\n" in state, "CURRENT_STATE lost not-complete section")

    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    need("## D088" in decision and "## D089" not in decision, "decision cursor is not exactly D088")
    decision += f"""
## D089 — {bundle['date']} — Unit 032 published and cursor advanced

Publish complete Section 4.8 at authority {SOURCE_RANGE} only after the final
thirteen-page reader, schema-valid backend, independent admission audit, content
commit, receipt commit, and both anonymous readback inventories agree. Content
commit {pub['content_commit']}, tree {pub['content_tree']}, and receipt commit
{pub['receipt_commit']}, tree {pub['receipt_tree']}, are the exact public
boundary. Initial 22.16992 pt and 27.03485 pt set-builder display overflows are
closed by separately provenanced target-only reflows O013-LI-U032-REFLOW-001
and O013-LI-U032-REFLOW-002. Exactly three visually non-actionable underfull
hboxes and the untagged-PDF accessibility limitation remain disclosed. Advance
to Unit 033 at chapter4.tex:1389 while preserving the full Li, Duncan,
selected-CRing, and separate connective/mastery architecture with Etingof
reference-only.
"""

    worklog = originals["00_control/WORKLOG.jsonl"].decode("utf-8")
    work_event = {
        "date": bundle["date"],
        "event": "unit_032_published_and_read_back",
        "result": (
            f"Section4.8 at {SOURCE_RANGE} is canonically integrated and public. "
            f"Candidate {unit['candidate']['bytes']} bytes / {unit['candidate']['sha256']}; "
            f"chapter4.tex {unit['target']['bytes']} bytes / {unit['target']['sha256']}; "
            f"reader 13 pages / {unit['reader']['bytes']} bytes / {unit['reader']['sha256']}; "
            f"backend {unit['backend']['bytes']} bytes / {unit['backend']['sha256']}. "
            "All deterministic gates pass. O013-LI-U032-COR-001 and COR-002 are explicit. "
            "O013-LI-U032-REFLOW-001 and REFLOW-002 remove measured 22.16992 pt "
            "and 27.03485 pt overflows without changing mathematics. Exactly three "
            "visually non-actionable underfull hboxes and the untagged PDF are disclosed. "
            f"Content {pub['content_commit']} / tree {pub['content_tree']} and receipt "
            f"{pub['receipt_commit']} / tree {pub['receipt_tree']} passed anonymous "
            "readback. Cursor advances to Unit033 chapter4.tex:1389; full goal remains active."
        ),
    }
    worklog += json.dumps(work_event, ensure_ascii=False, separators=(",", ":")) + "\n"

    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    events = (
        {
            "id": "O013-ADV-0097",
            "date": bundle["date"],
            "severity": "P2",
            "surface": "li_unit_032_first_finite_support_display_overflow",
            "status": "closed_by_separate_target_only_digital_reflow",
            "summary": "The first Unit032 reader measured a 22.16992 pt overflow in a finite-support set-builder display. O013-LI-U032-REFLOW-001 inserts a readable aligned break while preserving set membership, quantifiers, the finite-support condition, and term order; the final log has zero overfull diagnostics. This is digital reflow, not a source correction.",
        },
        {
            "id": "O013-ADV-0098",
            "date": bundle["date"],
            "severity": "P2",
            "surface": "li_unit_032_second_finite_support_display_overflow",
            "status": "closed_by_separate_target_only_digital_reflow",
            "summary": "The first Unit032 reader measured a second 27.03485 pt overflow in a finite-support set-builder display. O013-LI-U032-REFLOW-002 inserts a readable aligned break while preserving set membership, quantifiers, the finite-support condition, and term order; the final log has zero overfull diagnostics. This is digital reflow, not a source correction.",
        },
        {
            "id": "O013-ADV-0099",
            "date": bundle["date"],
            "severity": "P3",
            "surface": "li_unit_032_reader_underfull_and_accessibility_limitations",
            "status": "closed_as_disclosed_nonblocking_limitations",
            "summary": "The thirteen-page Unit032 reader remains untagged and therefore carries no tagged-accessibility claim. Its final log contains exactly three underfull hboxes at visually inspected pages 5, 6, and 13; none clips, collides, touches an edge, removes content, or impairs reading. These are explicit nonblocking limitations, not hidden PASS conditions.",
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
    need(cursor["last_admitted_unit"]["id"] == UNIT_ID, "Unit 032 not admitted")
    need(cursor["next_source_boundary"]["source_line_start"] == 1389, "cursor not advanced to 1389")
    need(recovery["next_cursor"]["next_admission_unit"] == NEXT_ID, "recovery not advanced to Unit 033")
    need(cursor["publication"]["expected_remote_base"] == bundle["publication"]["receipt_commit"], "remote base mismatch")
    for rel in ("00_control/CURRENT_GOAL_AND_WORKFLOW.md", "00_control/CURRENT_STATE.md"):
        text = updates[rel].decode("utf-8")
        need("22.16992 pt" in text and "27.03485 pt" in text, f"{rel} lost overflow history")
        need("three" in text and "untagged" in text, f"{rel} lost disclosed limitations")
        need("Unit 033" in text and "chapter4.tex:1389" in text, f"{rel} lost next cursor")
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
            fd, name = tempfile.mkstemp(prefix=f".{target.name}.u032-", suffix=".tmp", dir=target.parent)
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
            key: blank(path, **({"pages": 13} if key == "reader" else {}))
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
    parser.add_argument("--proof-bundle", type=Path, help="strict JSON with exact Unit 032 local and public identities")
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
        "next_source_cursor": "chapter4.tex:1389",
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
