#!/usr/bin/env python3
"""Fail-closed Unit 034 -> Unit 035 durable-control transition.

Default mode validates the frozen local/public proof bundle and renders the
eight durable controls in memory. Only ``--apply`` may atomically replace the
controls. The gate performs bounded object/ref checks and immutable anonymous
raw-byte reads; it never scans the repository working tree.
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
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "00_control"
REPOSITORY = "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id"
SLUG = "KokunoYumeto/metode-aljabar-jilid-1-id"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
DATE_VALUE = "2026-08-28"

CONTROL_TARGETS = (
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md",
    "00_control/CURRENT_STATE.md",
    "00_control/CURRENT_CURSOR.json",
    "00_control/RECOVERY_POINTER.json",
    "00_control/DECISION_LOG.md",
    "00_control/WORKLOG.jsonl",
    "00_control/ADVERSE_LEDGER.jsonl",
    "00_control/RIGHTS_COMPONENTS.csv",
)
BASE_HASHES = {
    "00_control/CURRENT_GOAL_AND_WORKFLOW.md": "34c50bd9b526a0b8af59094017baf7a9b26e86d48a1a3df93794d63d9dd12eb5",
    "00_control/CURRENT_STATE.md": "ea183c8f3c03b35b5f20d872c3923c9ace0a41c6028c6d5b1d9ee2b5f6217cfc",
    "00_control/CURRENT_CURSOR.json": "e6af7bf7338331ab6509ba01367a9f54fc599c424e66f2d3da3ff00660ff6a4d",
    "00_control/RECOVERY_POINTER.json": "69f639cd4304731a733bb260c0cc5cf8a3714eafe5fc41efa47042b98bb88dab",
    "00_control/DECISION_LOG.md": "8454c004bb2ab490900064e4be3fe762d1fb271e71da052831865dec27375fec",
    "00_control/WORKLOG.jsonl": "2a12192bfafd7970d7a5460858716b7d0923f208d25e563f07edcbbc4e876c3c",
    "00_control/ADVERSE_LEDGER.jsonl": "d201d1003b5bc5e5b14fc167923d71f5f65034f04bce99474bd1a1f222a3dd1a",
    "00_control/RIGHTS_COMPONENTS.csv": "7fce03694ecb7ffedc2bbb13d3a16a0f6e2f7d796b22400e41e187c305809965",
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

UNIT_ID = "unit-034-bab-4-limit-dan-kompletisasi-grup"
SOURCE_PATH = (
    "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/"
    "chapter4.tex"
)
SOURCE_RANGE = "chapter4.tex:1609-1744"
SOURCE_BYTES = 15_005
SOURCE_SHA = "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab"

UNIT_PATHS = {
    "candidate": "build/unit-034-candidate/chapter4-group-limits-completions-id.tex",
    "target": "repo/source/chapter4.tex",
    "reader": "artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf",
    "backend": "backend/data/unit-034-bab-4-limit-dan-kompletisasi-grup.json",
    "backend_validation": "qa/unit-034-evidence/backend-validation.json",
    "admission_receipt": "qa/UNIT_034_ADMISSION_20260828.md",
    "final_audit": "qa/UNIT_034_FINAL_AUDIT_20260828.md",
    "visual_receipt": "qa/UNIT_034_VISUAL_QA_20260827.md",
    "build_log": "qa/UNIT_034_BUILD_FINAL.log",
    "terminology_audit": "qa/UNIT_034_TERMINOLOGY_AUDIT_20260827.md",
    "terminology_delta": "build/unit-034-staging/terminology-delta.csv",
    "glossary": "00_control/TERMINOLOGY.id-ID.csv",
    "digital_reflow": "qa/UNIT_034_DIGITAL_REFLOW_20260827.md",
    "structure_pdf_evidence": "qa/unit-034-evidence/structure-and-pdf-qa.json",
    "render_inventory": "qa/unit-034-evidence/render-hash-inventory.json",
    "fandol_authority": "repo/fonts/FANDOL-AUTHORITY.json",
    "fandol_license": "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt",
    "fandol_readme": "repo/fonts/FANDOL-README.txt",
}
EXPECTED_UNIT_IDENTITIES = {
    "candidate": (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62"),
    "target": (189_935, "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569"),
    "reader": (136_702, "e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272"),
    "backend": (341_684, "c475108a1d6ed5d4c2084adc00c122e1a3294b5d44e6af3e302d39a06d7a6c35"),
    "backend_validation": (6_315, "41e019eaca9e2af1363b1ed573817e7d08ae2c895547fb57153ffb41c98a2eaf"),
    "admission_receipt": (6_376, "518043b82d0a3396b10019d7efcad0e1db728f88832681482e4a3e5aeb0798ef"),
    "final_audit": (6_715, "d542ca6aa5bc79f406c5490114cb07ebbeed15b74aac247a2c8aa8feab8b5517"),
    "visual_receipt": (5_015, "ceefb6b40c21b99ca4a673e32223323dcdb19373dbcdcf6822a79c8e0111a2a6"),
    "build_log": (77_357, "bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d"),
    "terminology_audit": (8_808, "7b0cedcff9f1747cc56371b9b64a7529f357c426fbec0de55ed1e34c52e39b55"),
    "terminology_delta": (6_613, "077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659"),
    "glossary": (82_586, "59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955"),
    "digital_reflow": (8_792, "dbf1fa80899a626843e01b8561132e8a849adeaa9abcb08302211038fed5447a"),
    "structure_pdf_evidence": (31_319, "4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d"),
    "render_inventory": (41_802, "c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba"),
    "fandol_authority": (2_557, "1b74145b289d1c87f79f2e633934f10404adf9a4c02349c7db523de63b892a1f"),
    "fandol_license": (35_737, "853b586f0d520493390e571431afaf36a5fbb27dcfd239338a7ee9b0505cb004"),
    "fandol_readme": (645, "32537e063f4c7d4aebf016d5c8279cbce13f34fc8970f24b2578a3c04d0f8ca6"),
}

CONTENT_PARENT = "932dc5eb41c82d616eb38f36ba19319889bd50ce"
CONTENT_COMMIT = "6ce7def3bb18fc272b1b3054fa96e14fec4c49a7"
CONTENT_TREE = "69020f506d514ea74ffb01f6b898edc0e84bbfa5"
CONTENT_RB = "qa/PUBLICATION_GITHUB_UNIT_034_CONTENT_READBACK.json"
CONTENT_RB_ID = (42_018, "bf5893caa2ade62ab1dfe4d01a217798352d216ef40c3a533e1d49691a8cad95")
CONTENT_FETCHES = 61
CONTENT_BYTES = 5_186_751
RECEIPT_PATH = "qa/PUBLICATION_GITHUB_UNIT_034_20260828.md"
RECEIPT_ID = (1_814, "b000820c57c018b2d56f38c769d4b6c2c635736ea602b21ba87191bfb528b997")
RECEIPT_COMMIT = "73dcdb7186d0be22e6a6436d9fd592e8a1b33c53"
RECEIPT_TREE = "b88f16c0607b23b3f6c31f651b2ea40beaf74872"
RECEIPT_RB = "qa/PUBLICATION_GITHUB_UNIT_034_RECEIPT_READBACK.json"
RECEIPT_RB_ID = (3_187, "00f360782a266e46c9b9a008a777ca6c892f83f942171c243e503a5cd8018b45")
RECEIPT_FETCHES = 3
RECEIPT_BYTES = 126_143

NEXT_ID = "unit-035-bab-4-grup-dalam-kategori-dan-latihan"
NEXT_RANGE = "chapter4.tex:1745-1898"
NEXT_BYTES = 14_398
NEXT_SHA = "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287"
NEXT_CANDIDATE = "build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex"
NEXT_CANDIDATE_ID = (18_078, "9030e1850cb5e8be4e3129d3b0080daa24ba9c676d917ecd975ecd441dcd6ed5")
NEXT_CHECKER = "scripts/check_unit_035_candidate.py"
NEXT_CHECKER_ID = (16_565, "612b7b6e0379848f8f55f858d9835a675d10011d9529917750d4423e0f34727d")
NEXT_REVIEW = "qa/UNIT_035_TRANSLATION_REVIEW_20260825.md"
NEXT_REVIEW_ID = (6_826, "c2a11c116e0e99b544223729e20cf32116aa402a385ba1103c82e006faafcb7a")

FANDOL_RIGHTS_ROW = (
    '"Fandol 0.3 fonts","Clerk Ma and Jie Su; CTAN package fandol",'
    '"GPLv3 with Fandol font exception","Retain GPLv3 and the font exception; '
    'record embedded-font use separately; do not relicense as CC BY 4.0 or OFL 1.1."'
)
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
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read strict JSON {path}: {exc}") from exc


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def repo_path(relative: str) -> Path:
    need(isinstance(relative, str) and relative, "repository path must be nonempty")
    need(not Path(relative).is_absolute() and "\\" not in relative, f"unsafe path: {relative}")
    result = (ROOT / relative).resolve(strict=False)
    try:
        result.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GateError(f"path escapes lane root: {relative}") from exc
    return result


def require_keys(value: Mapping[str, Any], keys: Iterable[str], context: str) -> None:
    missing = sorted(set(keys) - set(value))
    need(not missing, f"{context} missing keys: {', '.join(missing)}")


def validate_base() -> dict[str, bytes]:
    originals: dict[str, bytes] = {}
    for relative in CONTROL_TARGETS:
        path = repo_path(relative)
        need(path.is_file(), f"control missing: {relative}")
        payload = path.read_bytes()
        need(digest(payload) == BASE_HASHES[relative], f"Unit 033 control base drift: {relative}")
        originals[relative] = payload

    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    need(cursor.get("goal_status") == recovery.get("goal_status") == "active", "durable goal is not active")
    need(cursor.get("selected_architecture") == ARCHITECTURE, "architecture drift")
    authority = cursor.get("architecture_authority", {})
    need(authority.get("path") == ARCH_AUTHORITY and authority.get("sha256") == ARCH_SHA, "architecture authority drift")
    need(authority.get("etingof_state") == "reference_only", "Etingof state drift")
    need(cursor.get("duncan_authority_admitted", {}).get("commit") == DUNCAN_COMMIT, "Duncan authority drift")
    need(cursor.get("last_admitted_unit", {}).get("id") == "unit-033-bab-4-grup-simetris", "cursor is not at Unit 033")
    need(cursor.get("next_source_boundary", {}).get("next_admission_unit") == UNIT_ID, "cursor is not pointed at Unit 034")
    need(recovery.get("current_boundary", {}).get("unit") == "unit-033-bab-4-grup-simetris", "recovery is not at Unit 033")
    need(recovery.get("next_cursor", {}).get("next_admission_unit") == UNIT_ID, "recovery is not pointed at Unit 034")
    need(cursor.get("publication", {}).get("last_public_unit") == "unit-033-bab-4-grup-simetris", "public cursor drift")

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    for phrase in ("Wen-Wei Li", "Duncan", "CRing", "mastery layer", "The goal is complete only when"):
        need(phrase in goal, f"durable goal lost architecture phrase: {phrase}")
    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    need("## D090" in decision and "## D091" not in decision, "decision cursor is not exactly D090")
    work_lines = originals["00_control/WORKLOG.jsonl"].decode("utf-8").splitlines()
    need(json.loads(work_lines[-1], object_pairs_hook=no_duplicate_keys).get("event") == "unit_033_published_and_read_back", "worklog tail drift")
    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    need('"id":"O013-ADV-0102"' in adverse and "O013-ADV-0103" not in adverse, "adverse cursor drift")
    rights = originals["00_control/RIGHTS_COMPONENTS.csv"].decode("utf-8")
    need("Fandol" not in rights, "Fandol row already present in base rights control")
    return originals


def validate_identity(raw: Mapping[str, Any], expected_path: str, context: str) -> dict[str, Any]:
    require_keys(raw, ("path", "bytes", "sha256"), context)
    need(raw["path"] == expected_path, f"{context}.path mismatch")
    need(isinstance(raw["bytes"], int) and raw["bytes"] >= 0, f"{context}.bytes invalid")
    need(isinstance(raw["sha256"], str) and HEX64.fullmatch(raw["sha256"]), f"{context}.sha256 invalid")
    actual = identity(repo_path(expected_path))
    need(actual == (raw["bytes"], raw["sha256"]), f"{context} local identity mismatch: {actual}")
    return {"path": expected_path, "bytes": actual[0], "sha256": actual[1]}


def git_value(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT).decode("ascii").strip()


def verify_commit(commit: str, tree: str, parent: str, context: str) -> None:
    need(HEX40.fullmatch(commit) is not None and HEX40.fullmatch(tree) is not None, f"{context} malformed IDs")
    need(git_value("rev-parse", f"{commit}^{{commit}}") == commit, f"{context} commit missing")
    need(git_value("rev-parse", f"{commit}^{{tree}}") == tree, f"{context} tree mismatch")
    need(git_value("rev-parse", f"{commit}^") == parent, f"{context} parent mismatch")


def validate_inventory(
    path: str,
    commit: str,
    tree: str,
    parent: str,
    count: int,
    byte_total: int,
    context: str,
) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
    data = load_json(repo_path(path))
    need(data.get("repository") == REPOSITORY and data.get("branch") == "main", f"{context} repository mismatch")
    need((data.get("commit"), data.get("tree"), data.get("parent")) == (commit, tree, parent), f"{context} topology mismatch")
    need(data.get("anonymous") is True and data.get("authorization_header_used") is False, f"{context} is not anonymous")
    remote_before = data.get("remote_branch_before", data.get("remote_main_before"))
    remote_after = data.get("remote_branch_after", data.get("remote_main_after"))
    need(
        data.get("all_match") is True
        and remote_before == commit
        and remote_after == commit
        and data.get("remote_branch_matches_commit", data.get("remote_main_matches_commit")) is True,
        f"{context} public state mismatch",
    )
    records = data.get("records")
    need(isinstance(records, list) and len(records) == count, f"{context} record count mismatch")
    need(data.get("path_fetch_count") == count and data.get("total_bytes_fetched") == byte_total, f"{context} totals mismatch")
    mapped: dict[str, Mapping[str, Any]] = {}
    for record in records:
        need(isinstance(record, dict), f"{context} record invalid")
        require_keys(record, ("path", "bytes", "sha256", "http_status"), context)
        relative = record["path"]
        need(relative not in mapped and record["http_status"] == 200, f"{context} duplicate/non-200: {relative}")
        need(record.get("matches_committed_blob", True) is True, f"{context} blob mismatch: {relative}")
        mapped[relative] = record
    need(sum(int(record["bytes"]) for record in records) == byte_total, f"{context} byte sum mismatch")
    return data, mapped


def require_record(records: Mapping[str, Mapping[str, Any]], spec: Mapping[str, Any], context: str) -> None:
    record = records.get(str(spec["path"]))
    need(record is not None, f"{context} missing {spec['path']}")
    need((record.get("bytes"), record.get("sha256")) == (spec["bytes"], spec["sha256"]), f"{context} identity mismatch: {spec['path']}")


def fetch_raw(commit: str, relative: str) -> bytes:
    quoted = urllib.parse.quote(relative, safe="/")
    url = f"https://raw.githubusercontent.com/{SLUG}/{commit}/{quoted}"
    request = urllib.request.Request(url, headers={"User-Agent": "O013-control-transition/1.0"})
    last: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                need(response.status == 200, f"HTTP {response.status}: {relative}")
                return response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise GateError(f"anonymous raw read failed: {relative}: {last}")


def remote_main() -> str:
    endpoint = f"https://github.com/{SLUG}.git"
    payload = subprocess.check_output(
        ["git", "-c", "credential.helper=", "ls-remote", "--heads", endpoint, "refs/heads/main"],
        cwd=ROOT,
    ).decode("ascii").strip().split()
    need(len(payload) == 2 and payload[1] == "refs/heads/main", "anonymous remote-main query malformed")
    return payload[0]


def validate_backend(specs: Mapping[str, Mapping[str, Any]]) -> None:
    receipt = load_json(repo_path(UNIT_PATHS["backend_validation"]))
    need(receipt.get("status") == "PASS" and receipt.get("unit") == UNIT_ID, "backend receipt status/unit mismatch")
    counts = receipt.get("counts", {})
    expected = {
        "environment_pairs": 25,
        "labels": 11,
        "ordinary_references": 16,
        "citation_occurrences": 6,
        "protected_math_zones": 276,
        "diagrams": 1,
        "diagram_arrows": 12,
        "index_entries": 6,
        "terminology_rows": 37,
        "source_corrections": 1,
        "digital_reflows": 1,
        "exercises": 0,
        "hints": 0,
        "solutions": 0,
        "concepts": 419,
        "uuidv5_entities_audited": 482,
        "csv_projections": 6,
    }
    for key, value in expected.items():
        need(counts.get(key) == value, f"backend count mismatch: {key}")
    need(receipt.get("checks", {}).get("validation_mutated_outputs") is False, "backend validator mutation flag")
    need(receipt.get("artifact") == {
        "path": specs["reader"]["path"],
        "pages": 9,
        "bytes": specs["reader"]["bytes"],
        "sha256": specs["reader"]["sha256"],
    }, "backend artifact mismatch")
    backend = repo_path(UNIT_PATHS["backend"]).read_text(encoding="utf-8")
    for phrase in ("O013-LI-U034-COR-001", "O013-LI-U034-REFLOW-001", "rights/fandol-gpl-3.0-with-font-exception", MODEL):
        need(phrase in backend, f"backend provenance/rights missing: {phrase}")
    log = repo_path(UNIT_PATHS["build_log"]).read_text(encoding="utf-8")
    need(len(log.splitlines()) == 2_274, "final log record count drift")
    need("Overfull \\hbox" not in log and "Underfull \\hbox" not in log, "final log box diagnostics drift")


def validate_next_unit() -> None:
    for relative, expected in (
        (NEXT_CANDIDATE, NEXT_CANDIDATE_ID),
        (NEXT_CHECKER, NEXT_CHECKER_ID),
        (NEXT_REVIEW, NEXT_REVIEW_ID),
    ):
        path = repo_path(relative)
        need(path.is_file() and identity(path) == expected, f"Unit 035 cursor identity drift: {relative}")
    authority = repo_path(SOURCE_PATH)
    need(identity(authority) == (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"), "authority identity drift")
    records = authority.read_text(encoding="utf-8").splitlines()
    selected = records[1744:1898]
    payload = ("\n".join(selected) + "\n").encode("utf-8")
    need(len(selected) == 154 and (len(payload), digest(payload)) == (NEXT_BYTES, NEXT_SHA), "Unit 035 authority span drift")
    checked = subprocess.run(
        [sys.executable, str(repo_path(NEXT_CHECKER))],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    need(checked.returncode == 0 and "PASS: O013-LI-U035" in checked.stdout, "Unit 035 checker failed")
    need("next source cursor: chapter5.tex line 1" in checked.stdout, "Unit 035 next-cursor marker absent")


def validate_bundle(path: Path) -> dict[str, Any]:
    bundle = load_json(path)
    need(isinstance(bundle, dict) and bundle.get("schema_version") == 1 and bundle.get("date") == DATE_VALUE, "proof bundle schema/date mismatch")
    raw_unit = bundle.get("unit")
    publication = bundle.get("publication")
    need(isinstance(raw_unit, dict) and set(raw_unit) == set(UNIT_PATHS), "proof bundle unit key set mismatch")
    need(isinstance(publication, dict), "proof bundle publication missing")

    specs: dict[str, dict[str, Any]] = {}
    for key, relative in UNIT_PATHS.items():
        need(isinstance(raw_unit[key], dict), f"unit.{key} invalid")
        specs[key] = validate_identity(raw_unit[key], relative, f"unit.{key}")
        need((specs[key]["bytes"], specs[key]["sha256"]) == EXPECTED_UNIT_IDENTITIES[key], f"hard-bound Unit 034 identity changed: {key}")
    need(raw_unit["reader"].get("pages") == 9, "reader page count mismatch")
    specs["reader"]["pages"] = 9
    validate_backend(specs)
    validate_next_unit()

    expected_public = {
        "content_commit": CONTENT_COMMIT,
        "content_tree": CONTENT_TREE,
        "receipt_commit": RECEIPT_COMMIT,
        "receipt_tree": RECEIPT_TREE,
    }
    for key, value in expected_public.items():
        need(publication.get(key) == value, f"publication.{key} mismatch")
    content_spec = validate_identity(publication["content_readback"], CONTENT_RB, "content readback identity")
    receipt_spec = validate_identity(publication["receipt"], RECEIPT_PATH, "receipt identity")
    receipt_rb_spec = validate_identity(publication["receipt_readback"], RECEIPT_RB, "receipt readback identity")
    need((content_spec["bytes"], content_spec["sha256"]) == CONTENT_RB_ID, "content readback hard identity drift")
    need((receipt_spec["bytes"], receipt_spec["sha256"]) == RECEIPT_ID, "receipt hard identity drift")
    need((receipt_rb_spec["bytes"], receipt_rb_spec["sha256"]) == RECEIPT_RB_ID, "receipt readback hard identity drift")

    verify_commit(CONTENT_COMMIT, CONTENT_TREE, CONTENT_PARENT, "content commit")
    verify_commit(RECEIPT_COMMIT, RECEIPT_TREE, CONTENT_COMMIT, "receipt commit")
    _, content_records = validate_inventory(CONTENT_RB, CONTENT_COMMIT, CONTENT_TREE, CONTENT_PARENT, CONTENT_FETCHES, CONTENT_BYTES, "content readback")
    _, receipt_records = validate_inventory(RECEIPT_RB, RECEIPT_COMMIT, RECEIPT_TREE, CONTENT_COMMIT, RECEIPT_FETCHES, RECEIPT_BYTES, "receipt readback")
    for spec in specs.values():
        require_record(content_records, spec, "content readback")
    require_record(receipt_records, receipt_spec, "receipt readback")
    require_record(receipt_records, content_spec, "receipt readback")
    need(remote_main() == RECEIPT_COMMIT, "remote main is not the verified Unit 034 receipt commit")

    live_content_keys = (
        "candidate", "target", "reader", "backend", "admission_receipt",
        "final_audit", "fandol_authority", "fandol_license", "fandol_readme",
    )
    for key in live_content_keys:
        spec = specs[key]
        need(fetch_raw(CONTENT_COMMIT, spec["path"]) == repo_path(spec["path"]).read_bytes(), f"live public bytes drift: {spec['path']}")
    for spec in (receipt_spec, content_spec):
        need(fetch_raw(RECEIPT_COMMIT, spec["path"]) == repo_path(spec["path"]).read_bytes(), f"live receipt bytes drift: {spec['path']}")

    publication["content_readback"] = content_spec
    publication["receipt"] = receipt_spec
    publication["receipt_readback"] = receipt_rb_spec
    bundle["unit"] = specs
    bundle["publication"] = publication
    return bundle


def replace_between(text: str, start: str, end: str, replacement: str, context: str) -> str:
    need(text.count(start) == 1, f"{context}: start-anchor count is {text.count(start)}")
    left = text.index(start)
    right = text.find(end, left + len(start))
    need(right >= 0, f"{context}: end anchor absent")
    return text[:left] + replacement.rstrip() + "\n\n" + text[right:]


def ident(spec: Mapping[str, Any]) -> str:
    return f"{spec['bytes']:,} bytes / SHA-256 {spec['sha256']}"


def public_summary(bundle: Mapping[str, Any]) -> str:
    unit = bundle["unit"]
    publication = bundle["publication"]
    return f"""Current admitted boundary: Li Units 001-034 through complete Section 4.10.
Unit 034 authority is {SOURCE_RANGE}, 136 normalized-LF records / {SOURCE_BYTES:,}
bytes / SHA-256 {SOURCE_SHA}; blank boundary line 1744 is excluded from the
135-record target mapping at canonical lines 1604-1738. The final candidate is
{ident(unit['candidate'])}; canonical chapter4.tex is {ident(unit['target'])}.
Its centered nine-page reader is {ident(unit['reader'])}, and its schema-valid
backend is {ident(unit['backend'])}. Backend validation is
{ident(unit['backend_validation'])}; the admission receipt is
{ident(unit['admission_receipt'])}; and the final audit is
{ident(unit['final_audit'])}.

All deterministic source, mathematics, terminology, topology, build, PDF,
dual-renderer visual, backend, rights, privacy, and independent-audit gates
pass. O013-LI-U034-COR-001 and O013-LI-U034-REFLOW-001 are separately
provenanced. The reflow removes a measured 26.11896 pt overflow without
changing mathematics. The final reader has nine centered pages, 39 resolved
destinations, 20 internal and five safe HTTPS actions, 31 embedded font
objects, and no actionable defect. Its untagged-PDF and mathematics-font text
extraction limitations are disclosed. Fandol 0.3 remains a separate GPLv3
component with its document-embedding font exception; it is not flattened into
the principal CC BY 4.0 or Noto OFL rights.

Content commit {publication['content_commit']}, tree {publication['content_tree']},
passed anonymous readback for {CONTENT_FETCHES} paths / {CONTENT_BYTES:,} bytes.
Receipt commit {publication['receipt_commit']}, tree {publication['receipt_tree']},
passed anonymous readback for {RECEIPT_FETCHES} paths / {RECEIPT_BYTES:,} bytes
and is the verified remote base. The 229-page checkpoint reader 0.6.0 remains
the nonduplicative Zenodo preservation release."""


def next_summary() -> str:
    return f"""Unit 034 and complete Section 4.10 are public and byte-verified.
The following source-order admission boundary is Unit 035 at {NEXT_RANGE}; its
{NEXT_CANDIDATE_ID[0]:,}-byte isolated candidate has SHA-256
{NEXT_CANDIDATE_ID[1]}. Its checker has SHA-256 {NEXT_CHECKER_ID[1]} and passes
with 26 top-level exercises, 36 exercise/subitems, five hints, eight diagrams,
and no solutions. The candidate remains isolated until Unit 035 terminology,
integration, reader, backend, build, all-page visual, publication, and
anonymous-readback gates pass. The active cursor is chapter4.tex:1745 and the
cursor after Unit 035 will be chapter5.tex:1. Units 035-042 remain strictly
source-ordered. The isolated translation cursor remains chapter5.tex:1184;
Unit 043 has not started."""


def boundary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    unit = bundle["unit"]
    publication = bundle["publication"]
    return {
        "id": UNIT_ID,
        "source": SOURCE_RANGE,
        "source_span_bytes": SOURCE_BYTES,
        "source_span_sha256": SOURCE_SHA,
        "source_mapping": "authority lines 1609-1743 map to 135 target records at canonical lines 1604-1738; blank boundary line 1744 is omitted",
        "candidate": unit["candidate"]["path"],
        "candidate_bytes": unit["candidate"]["bytes"],
        "candidate_sha256": unit["candidate"]["sha256"],
        "target": "repo/source/chapter4.tex:1604-1738",
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
        "visual_qa": "9/9 pages inspected in Poppler and MuPDF; 54 renders cover two clean builds and the artifact; all same-renderer comparisons agree, all edges are clear, 39 destinations resolve, 20 internal and five safe HTTPS actions pass, and 31 font objects are embedded; the untagged PDF and extraction limitations are disclosed",
        "corrections": ["O013-LI-U034-COR-001 aligns the p-adic compatible-family index with the declared nonnegative index set"],
        "digital_reflow": "O013-LI-U034-REFLOW-001 splits one unchanged neighborhood-basis display into three centered rows and removes a measured 26.11896 pt overflow",
        "component_rights": "principal text/translation CC BY 4.0; AJbook fragment and unused Lanzhou image CC BY-SA 3.0; Noto OFL 1.1; Fandol 0.3 GPLv3 with font exception",
        "content_commit": publication["content_commit"],
        "content_tree": publication["content_tree"],
        "content_readback_path_fetches": CONTENT_FETCHES,
        "content_readback_bytes": CONTENT_BYTES,
        "content_readback_inventory": publication["content_readback"]["path"],
        "content_readback_inventory_bytes": publication["content_readback"]["bytes"],
        "content_readback_inventory_sha256": publication["content_readback"]["sha256"],
        "receipt": publication["receipt"]["path"],
        "receipt_bytes": publication["receipt"]["bytes"],
        "receipt_sha256": publication["receipt"]["sha256"],
        "receipt_commit": publication["receipt_commit"],
        "receipt_tree": publication["receipt_tree"],
        "receipt_readback_files": RECEIPT_FETCHES,
        "receipt_readback_bytes": RECEIPT_BYTES,
        "receipt_readback_inventory": publication["receipt_readback"]["path"],
        "receipt_readback_inventory_bytes": publication["receipt_readback"]["bytes"],
        "receipt_readback_inventory_sha256": publication["receipt_readback"]["sha256"],
        "state": "public_readback_passed; complete Section 4.10",
    }


def next_boundary(publication: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "component": "li-volume-1-complete",
        "completed_preservation_action": (
            f"Unit 034 content commit {publication['content_commit']} and receipt commit "
            f"{publication['receipt_commit']} passed anonymous readback. Zenodo remains "
            "the nonduplicative 0.6.0 checkpoint through Unit 024 and complete Chapter 3."
        ),
        "next_admission_unit": NEXT_ID,
        "source_path": SOURCE_PATH,
        "source_line_start": 1745,
        "source_line_end": 1898,
        "source_span_bytes": NEXT_BYTES,
        "source_span_sha256": NEXT_SHA,
        "candidate_path": NEXT_CANDIDATE,
        "candidate_bytes": NEXT_CANDIDATE_ID[0],
        "candidate_sha256": NEXT_CANDIDATE_ID[1],
        "candidate_checker": NEXT_CHECKER,
        "candidate_checker_bytes": NEXT_CHECKER_ID[0],
        "candidate_checker_sha256": NEXT_CHECKER_ID[1],
        "candidate_review": NEXT_REVIEW,
        "candidate_review_bytes": NEXT_REVIEW_ID[0],
        "candidate_review_sha256": NEXT_REVIEW_ID[1],
        "next_source_cursor": "chapter5.tex:1",
        "chapter": "Chapter 4 - group theory",
        "prepared_isolated_units": "Units 035-042 are translated candidates and remain outside canonical repo/source until admitted in order; Unit 035 finishes Chapter 4 and Units 036-042 continue through complete Chapter 5 unique factorization.",
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
        "latest_corrections": ["O013-LI-U042-COR-001 through O013-LI-U042-COR-007 remain isolated and may not skip Units 035-041"],
        "translation_cursor_after_prepared_candidates": "chapter5.tex:1184; line 1183 is the excluded blank separator; Unit 043 has not started",
        "rule": "Admit Units 035-042 sequentially with terminology, canonical integration, reader, backend, build, visual QA, narrow publication, and public-byte readback while continuing isolated translation from chapter5.tex:1184 when it does not delay admission.",
    }


def make_updates(originals: Mapping[str, bytes], bundle: Mapping[str, Any]) -> dict[str, bytes]:
    unit = bundle["unit"]
    publication = bundle["publication"]
    bound = boundary(bundle)

    cursor = load_json(CONTROL / "CURRENT_CURSOR.json")
    cursor["updated"] = DATE_VALUE
    cursor["last_admitted_unit"] = bound
    cursor["next_source_boundary"] = next_boundary(publication)
    cursor["terminology_qa"].update({
        "path": unit["terminology_audit"]["path"],
        "bytes": unit["terminology_audit"]["bytes"],
        "sha256": unit["terminology_audit"]["sha256"],
        "previous_path": "qa/UNIT_033_TERMINOLOGY_AUDIT_20260826.md",
        "previous_sha256": "efdb7d0cfd43484e2b6b36604e13c7bbcc4dcee188745c637703b164f8abae13",
        "glossary": unit["glossary"]["path"],
        "glossary_bytes": unit["glossary"]["bytes"],
        "glossary_sha256": unit["glossary"]["sha256"],
        "glossary_delta": "37 Unit 034 rows covering projective limits, topological groups, completions, Cauchy sequences, p-adic integers, Tate modules, and elliptic curves",
        "model": MODEL,
    })
    cursor["publication"].update({
        "expected_remote_base": RECEIPT_COMMIT,
        "last_public_unit": UNIT_ID,
        "unit_034_content_commit": CONTENT_COMMIT,
        "unit_034_content_tree": CONTENT_TREE,
        "unit_034_public_readback_files": CONTENT_FETCHES,
        "unit_034_public_readback_bytes": CONTENT_BYTES,
        "unit_034_content_readback": CONTENT_RB,
        "unit_034_content_readback_bytes": CONTENT_RB_ID[0],
        "unit_034_content_readback_sha256": CONTENT_RB_ID[1],
        "unit_034_receipt": RECEIPT_PATH,
        "unit_034_receipt_bytes": RECEIPT_ID[0],
        "unit_034_receipt_sha256": RECEIPT_ID[1],
        "unit_034_receipt_commit": RECEIPT_COMMIT,
        "unit_034_receipt_tree": RECEIPT_TREE,
        "unit_034_receipt_readback_files": RECEIPT_FETCHES,
        "unit_034_receipt_readback_bytes": RECEIPT_BYTES,
        "unit_034_receipt_readback_inventory": RECEIPT_RB,
        "unit_034_receipt_readback_inventory_bytes": RECEIPT_RB_ID[0],
        "unit_034_receipt_readback_inventory_sha256": RECEIPT_RB_ID[1],
        "unit_034_state": "content and sanitized receipt public; anonymous readback passed",
    })
    cursor["next_action"] = (
        "Admit Unit 035 at chapter4.tex:1745-1898, completing Chapter 4, and "
        "continue strictly through the isolated Unit 042 candidate; Unit 042 may "
        "not skip Units 035-041. Continue isolated translation from "
        "chapter5.tex:1184 only when it does not delay admission. Duncan remains "
        "the post-Li component, CRing remains six selected repaired spans, "
        "Etingof remains reference-only, and the connective/mastery layer remains "
        "separately provenanced."
    )

    recovery = load_json(CONTROL / "RECOVERY_POINTER.json")
    recovery["updated"] = DATE_VALUE
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
        "component_rights": bound["component_rights"],
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
        "immediate_action": "admit Chapter 4 Unit 035 at chapter4.tex:1745-1898, completing Chapter 4, and continue strictly in source order",
        "builder": "scripts/build_unit_035.ps1",
        "coverage": "complete prelude, Chapters 1-3, and Chapter 4 opening through complete Section 4.10 in 34 admitted units; Section 4.11/exercises and Chapters 5-10 remain unadmitted",
        "next_admission_unit": NEXT_ID,
        "next_admission_source": NEXT_RANGE,
        "next_authority_bytes": NEXT_BYTES,
        "next_authority_sha256": NEXT_SHA,
        "next_candidate": NEXT_CANDIDATE,
        "next_candidate_bytes": NEXT_CANDIDATE_ID[0],
        "next_candidate_sha256": NEXT_CANDIDATE_ID[1],
        "next_candidate_checker": NEXT_CHECKER,
        "next_candidate_checker_bytes": NEXT_CHECKER_ID[0],
        "next_candidate_checker_sha256": NEXT_CHECKER_ID[1],
        "next_candidate_review": NEXT_REVIEW,
        "next_candidate_review_bytes": NEXT_REVIEW_ID[0],
        "next_candidate_review_sha256": NEXT_REVIEW_ID[1],
        "cursor_after_next_admission": "chapter5.tex:1",
        "prepared_isolated_units": "Units 035-042; Unit 035 finishes Chapter 4 and Units 036-042 continue Chapter 5 through complete unique factorization",
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
        f"Unit 034 content is public at commit {CONTENT_COMMIT} (tree {CONTENT_TREE}); "
        f"its content inventory passed. Receipt commit {RECEIPT_COMMIT} (tree "
        f"{RECEIPT_TREE}) and its receipt inventory also passed anonymous byte "
        "readback. Checkpoint 0.6.0 remains public and nonduplicative."
    )

    goal = originals["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    goal = replace_between(
        goal,
        "Current admitted boundary: Li Units 001-033 through complete Section 4.9.\n",
        "A bounded Indonesian field-usage check",
        public_summary(bundle),
        "goal progress",
    )
    goal = replace_between(
        goal,
        "Unit 033 and complete Section 4.9 are public and byte-verified.",
        "The Duncan source/build gate",
        next_summary(),
        "goal next action",
    )
    old_rights = (
        "Li closure exceptions remain explicit: the credited `AJbook.cls`\n"
        "fragment and `Lanzhou.png` are CC BY-SA 3.0, and bundled Noto fonts are OFL\n"
        "1.1. State independent/non-endorsed derivative status."
    )
    new_rights = (
        "Li closure exceptions remain explicit: the credited `AJbook.cls`\n"
        "fragment and `Lanzhou.png` are CC BY-SA 3.0, bundled Noto fonts are OFL\n"
        "1.1, and Fandol 0.3 is GPLv3 with its document-embedding font exception.\n"
        "Keep all component rights separate. State independent/non-endorsed\n"
        "derivative status."
    )
    need(goal.count(old_rights) == 1, "goal rights anchor drift")
    goal = goal.replace(old_rights, new_rights)

    state = originals["00_control/CURRENT_STATE.md"].decode("utf-8")
    state_top = f"""Updated: {DATE_VALUE}  
Status: active; Li Units 001-034 are public and byte-verified through complete
Chapter 4 Section 4.10. Unit 034 is public at content commit
`{CONTENT_COMMIT}`; all {CONTENT_FETCHES} paths / {CONTENT_BYTES:,} bytes passed
anonymous readback. Receipt commit `{RECEIPT_COMMIT}` and all {RECEIPT_FETCHES}
paths / {RECEIPT_BYTES:,} bytes also passed. The canonical next boundary is
Unit 035 at `chapter4.tex:1745`; isolated translation reaches Unit 042 and
`chapter5.tex:1184`, while Unit 043 has not started. The full active objective
continues from the complete Li edition through complete licensed Duncan,
selected repaired CRing spans, and the separately provenanced connective and
mastery layer; this boundary is not a completion claim."""
    state = replace_between(state, "Updated: 2026-08-26  \nStatus:", "## Completed\n", state_top, "state top")
    state = replace_between(
        state,
        "## Unit 033 public boundary\n",
        "## Not complete\n",
        "## Unit 034 public boundary\n\n" + public_summary(bundle) + "\n\n## Exact next action\n\n" + next_summary(),
        "state boundary",
    )

    decision = originals["00_control/DECISION_LOG.md"].decode("utf-8")
    decision += f"""
## D091 — {DATE_VALUE} — Unit 034 published and cursor advanced

Publish complete Section 4.10 at authority {SOURCE_RANGE} only after the final
nine-page reader, schema-valid backend, independent audit, explicit Fandol
rights repair, content commit, receipt commit, and both anonymous readback
inventories agree. Content commit {CONTENT_COMMIT}, tree {CONTENT_TREE}, and
receipt commit {RECEIPT_COMMIT}, tree {RECEIPT_TREE}, are the exact public
boundary. O013-LI-U034-COR-001 aligns the p-adic index with the declared index
set. O013-LI-U034-REFLOW-001 removes the measured 26.11896 pt overflow without
changing mathematics. Fandol remains GPLv3 with its document-embedding font
exception, separately recorded from CC BY and OFL components. Advance to Unit
035 at chapter4.tex:1745 while preserving the full Li, Duncan, selected-CRing,
and separate connective/mastery architecture with Etingof reference-only.
"""

    worklog = originals["00_control/WORKLOG.jsonl"].decode("utf-8")
    work_event = {
        "date": DATE_VALUE,
        "event": "unit_034_published_and_read_back",
        "result": (
            f"Section4.10 at {SOURCE_RANGE} is canonically integrated and public. "
            f"Candidate {unit['candidate']['bytes']} bytes / {unit['candidate']['sha256']}; "
            f"chapter4.tex {unit['target']['bytes']} bytes / {unit['target']['sha256']}; "
            f"reader 9 pages / {unit['reader']['bytes']} bytes / {unit['reader']['sha256']}; "
            f"backend {unit['backend']['bytes']} bytes / {unit['backend']['sha256']}. "
            "All deterministic gates pass. O013-LI-U034-COR-001 and REFLOW-001 are explicit. "
            "The Fandol 0.3 GPLv3 font exception and embedded-font evidence are separately bound. "
            f"Content {CONTENT_COMMIT} / tree {CONTENT_TREE} and receipt {RECEIPT_COMMIT} / tree "
            f"{RECEIPT_TREE} passed anonymous readback. Cursor advances to Unit035 chapter4.tex:1745; "
            "the full goal remains active."
        ),
    }
    worklog += json.dumps(work_event, ensure_ascii=False, separators=(",", ":")) + "\n"

    adverse = originals["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    events = (
        {"id": "O013-ADV-0103", "date": DATE_VALUE, "severity": "P2", "surface": "li_unit_034_p_adic_index", "status": "closed_by_declared_source_correction", "summary": "The compatible-family index began at 1 despite the same example declaring a nonnegative index set. O013-LI-U034-COR-001 changes it to i>=0, consistent with H_i=p^{i+1}Z and Z/p^{i+1}Z."},
        {"id": "O013-ADV-0104", "date": DATE_VALUE, "severity": "P2", "surface": "li_unit_034_neighborhood_basis_overflow", "status": "closed_by_separate_target_only_digital_reflow", "summary": "The first Unit034 reader measured a 26.11896 pt overflow in the neighborhood-basis display. O013-LI-U034-REFLOW-001 splits the unchanged mathematics into three centered rows; the final log has zero overfull diagnostics."},
        {"id": "O013-ADV-0105", "date": DATE_VALUE, "severity": "P1", "surface": "li_unit_034_embedded_fandol_rights", "status": "closed_before_publication", "summary": "Independent audit found embedded FandolHei while the first backend draft omitted Fandol rights. The final reader, LICENSES, CTAN authority record, GPLv3-plus-font-exception text, backend fifth rights record, PDF evidence, and durable rights control now bind Fandol separately."},
        {"id": "O013-ADV-0106", "date": DATE_VALUE, "severity": "P2", "surface": "li_unit_034_build_log_record_count", "status": "closed_before_publication", "summary": "The first evidence generator counted a trailing LF as an extra record. It now uses splitlines(), proves exactly 2,274 records, and the regenerated evidence/backend/documents agree."},
        {"id": "O013-ADV-0107", "date": DATE_VALUE, "severity": "P3", "surface": "li_unit_034_accessibility_limitations", "status": "closed_as_disclosed_nonblocking_limitations", "summary": "The nine-page Unit034 reader remains untagged and carries no tagged-accessibility claim. Mathematics-font text extraction limitations are disclosed; both renderers show complete readable content with no actionable defect."},
    )
    for event in events:
        need(event["id"] not in adverse, f"adverse ID already exists: {event['id']}")
        adverse += json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    rights = originals["00_control/RIGHTS_COMPONENTS.csv"].decode("utf-8")
    external = '"External TeX packages","Respective upstream maintainers","Multiple dependency licenses","Treat as build dependencies; do not claim them as CC BY 4.0 book content."'
    need(rights.count(external) == 1 and FANDOL_RIGHTS_ROW not in rights, "rights insertion anchor drift")
    rights = rights.replace(external, FANDOL_RIGHTS_ROW + "\n" + external)

    updates = {
        "00_control/CURRENT_GOAL_AND_WORKFLOW.md": goal.encode("utf-8"),
        "00_control/CURRENT_STATE.md": state.encode("utf-8"),
        "00_control/CURRENT_CURSOR.json": json_bytes(cursor),
        "00_control/RECOVERY_POINTER.json": json_bytes(recovery),
        "00_control/DECISION_LOG.md": decision.encode("utf-8"),
        "00_control/WORKLOG.jsonl": worklog.encode("utf-8"),
        "00_control/ADVERSE_LEDGER.jsonl": adverse.encode("utf-8"),
        "00_control/RIGHTS_COMPONENTS.csv": rights.encode("utf-8"),
    }
    need(set(updates) == set(CONTROL_TARGETS), "internal control target set changed")
    need(all(payload.endswith(b"\n") for payload in updates.values()), "rendered control lacks terminal LF")
    return updates


def validate_updates(updates: Mapping[str, bytes]) -> None:
    cursor = json.loads(updates["00_control/CURRENT_CURSOR.json"], object_pairs_hook=no_duplicate_keys)
    recovery = json.loads(updates["00_control/RECOVERY_POINTER.json"], object_pairs_hook=no_duplicate_keys)
    need(cursor["goal_status"] == recovery["goal_status"] == "active", "updated goal inactive")
    need(cursor["selected_architecture"] == ARCHITECTURE, "updated architecture drift")
    need(cursor["last_admitted_unit"]["id"] == UNIT_ID, "updated cursor not at Unit 034")
    need(cursor["next_source_boundary"]["next_admission_unit"] == NEXT_ID, "updated cursor not pointed at Unit 035")
    need(cursor["next_source_boundary"]["source_span_sha256"] == NEXT_SHA, "updated Unit 035 authority drift")
    need(cursor["publication"]["expected_remote_base"] == RECEIPT_COMMIT, "updated public base drift")
    need(cursor["publication"]["last_public_unit"] == UNIT_ID, "updated public unit drift")
    need(recovery["current_boundary"]["unit"] == UNIT_ID, "updated recovery boundary drift")
    need(recovery["next_cursor"]["next_admission_unit"] == NEXT_ID, "updated recovery cursor drift")
    need(recovery["next_cursor"]["cursor_after_next_admission"] == "chapter5.tex:1", "updated post-Unit035 cursor drift")
    goal = updates["00_control/CURRENT_GOAL_AND_WORKFLOW.md"].decode("utf-8")
    state = updates["00_control/CURRENT_STATE.md"].decode("utf-8")
    decision = updates["00_control/DECISION_LOG.md"].decode("utf-8")
    rights = updates["00_control/RIGHTS_COMPONENTS.csv"].decode("utf-8")
    for phrase in ("Li Units 001-034", "Unit 035", "Duncan", "CRing", "The goal is complete only when", "Fandol 0.3"):
        need(phrase in goal, f"updated goal missing {phrase}")
    need("Unit 034 public boundary" in state and "Unit 035" in state and "not a completion claim" in state, "updated state drift")
    need(decision.count("## D091") == 1, "updated decision count drift")
    work = updates["00_control/WORKLOG.jsonl"].decode("utf-8").splitlines()
    need(json.loads(work[-1], object_pairs_hook=no_duplicate_keys)["event"] == "unit_034_published_and_read_back", "updated worklog tail drift")
    adverse = updates["00_control/ADVERSE_LEDGER.jsonl"].decode("utf-8")
    need(all(f'"id":"O013-ADV-{n:04d}"' in adverse for n in range(103, 108)), "updated adverse ledger gap")
    need(rights.count(FANDOL_RIGHTS_ROW) == 1 and "GPLv3 with Fandol font exception" in rights, "updated Fandol rights drift")


def apply_updates(updates: Mapping[str, bytes]) -> None:
    temporary: list[tuple[Path, Path]] = []
    try:
        for relative, payload in updates.items():
            destination = repo_path(relative)
            handle = tempfile.NamedTemporaryFile(prefix=destination.name + ".", suffix=".tmp", dir=destination.parent, delete=False)
            temp_path = Path(handle.name)
            try:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            finally:
                handle.close()
            need(temp_path.read_bytes() == payload, f"temporary write mismatch: {relative}")
            temporary.append((temp_path, destination))
        for temp_path, destination in temporary:
            os.replace(temp_path, destination)
        for relative, payload in updates.items():
            need(repo_path(relative).read_bytes() == payload, f"applied control mismatch: {relative}")
    finally:
        for temp_path, _ in temporary:
            if temp_path.exists():
                temp_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=ROOT / "build/unit-034-controls/proof-bundle.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        originals = validate_base()
        bundle_path = args.bundle.resolve()
        need(bundle_path.is_file(), "proof bundle missing")
        bundle = validate_bundle(bundle_path)
        updates = make_updates(originals, bundle)
        validate_updates(updates)
        result = {
            "status": "PASS_APPLIED" if args.apply else "PASS_DRY_RUN",
            "unit": "034",
            "from": "chapter4.tex:1609",
            "to": "chapter4.tex:1745",
            "next_unit": "035",
            "next_source": NEXT_RANGE,
            "remote_main": RECEIPT_COMMIT,
            "bundle": str(bundle_path.relative_to(ROOT)).replace("\\", "/"),
            "bundle_bytes": bundle_path.stat().st_size,
            "bundle_sha256": digest(bundle_path.read_bytes()),
            "controls": {
                relative: {
                    "before_sha256": BASE_HASHES[relative],
                    "after_bytes": len(payload),
                    "after_sha256": digest(payload),
                }
                for relative, payload in updates.items()
            },
            "writes_performed": bool(args.apply),
        }
        if args.apply:
            for relative in CONTROL_TARGETS:
                need(digest(repo_path(relative).read_bytes()) == BASE_HASHES[relative], f"base changed before apply: {relative}")
            apply_updates(updates)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (GateError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
