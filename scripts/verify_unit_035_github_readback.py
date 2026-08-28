#!/usr/bin/env python3
"""Fail-closed anonymous GitHub immutable-byte verifier for Unit 035.

Run this script once for each publication boundary, immediately after that
boundary becomes the public ``main`` head: ``content``, then ``receipt``, then
``controls``.  Every invocation requires an independently prepared JSON
manifest whose records contain the exact path, byte count, and SHA-256 for the
complete changed-path inventory.  See ``--help`` for the manifest schema and
exact invocation structure.

Successful runs write one boundary-specific, deterministic JSON inventory in
``qa/``.  The inventory intentionally contains no wall-clock timestamp, local
filesystem path, credential, response header, or transient retry detail.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "KokunoYumeto/metode-aljabar-jilid-1-id"
BRANCH = "main"
UNIT = "035"
BOUNDARIES = ("content", "receipt", "controls")
OUTPUTS = {
    boundary: ROOT
    / "qa"
    / f"PUBLICATION_GITHUB_UNIT_{UNIT}_{boundary.upper()}_READBACK.json"
    for boundary in BOUNDARIES
}
GIT_SHA1 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
RAW_HOST = "raw.githubusercontent.com"
USER_AGENT = "O013-unit-035-public-byte-verifier/2.0"
RETRYABLE_HTTP_STATUS = {408, 425, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class ExpectedRecord:
    path: str
    bytes: int
    sha256: str


class RejectRedirects(HTTPRedirectHandler):
    """Turn every HTTP redirect into an HTTPError instead of following it."""

    def redirect_request(  # type: ignore[override]
        self,
        request: Request,
        file_pointer: Any,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> None:
        return None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def safe_repository_path(value: object) -> str:
    require(isinstance(value, str), "manifest record path must be a string")
    require(value not in {"", ".", ".."}, f"unsafe repository path: {value!r}")
    require(
        not any(ord(character) < 0x20 or ord(character) == 0x7F for character in value),
        f"control character in repository path: {value!r}",
    )
    path = PurePosixPath(value)
    require(
        value == path.as_posix()
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value,
        f"unsafe or non-canonical repository path: {value!r}",
    )
    return value


def read_manifest(path: Path, boundary: str) -> tuple[list[ExpectedRecord], str]:
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise RuntimeError("unable to read the expected-byte manifest") from error
    require(
        0 < len(payload) <= MAX_MANIFEST_BYTES,
        f"manifest size must be 1..{MAX_MANIFEST_BYTES} bytes",
    )
    try:
        document = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_json_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(f"invalid UTF-8 JSON manifest: {error}") from error

    require(isinstance(document, dict), "manifest root must be a JSON object")
    required_keys = {"schema_version", "unit", "boundary", "records"}
    require(
        set(document) == required_keys,
        f"manifest keys must be exactly {sorted(required_keys)}",
    )
    require(document["schema_version"] == "1.0.0", "unsupported manifest schema")
    require(document["unit"] == UNIT, f"manifest unit must be {UNIT}")
    require(document["boundary"] == boundary, "manifest boundary differs from --boundary")
    raw_records = document["records"]
    require(isinstance(raw_records, list) and raw_records, "manifest records must be a non-empty array")

    records: list[ExpectedRecord] = []
    for index, raw_record in enumerate(raw_records):
        require(isinstance(raw_record, dict), f"manifest record {index} must be an object")
        require(
            set(raw_record) == {"path", "bytes", "sha256"},
            f"manifest record {index} keys must be path, bytes, and sha256",
        )
        record_path = safe_repository_path(raw_record["path"])
        byte_count = raw_record["bytes"]
        digest = raw_record["sha256"]
        require(
            type(byte_count) is int and byte_count >= 0,
            f"manifest bytes for {record_path!r} must be a non-negative integer",
        )
        require(
            isinstance(digest, str) and SHA256.fullmatch(digest) is not None,
            f"manifest SHA-256 for {record_path!r} must be 64 lowercase hex characters",
        )
        records.append(ExpectedRecord(record_path, byte_count, digest))

    paths = [record.path for record in records]
    require(len(paths) == len(set(paths)), "manifest contains duplicate paths")
    records.sort(key=lambda record: record.path.encode("utf-8"))
    canonical_manifest = {
        "schema_version": "1.0.0",
        "unit": UNIT,
        "boundary": boundary,
        "records": [
            {"path": record.path, "bytes": record.bytes, "sha256": record.sha256}
            for record in records
        ],
    }
    return records, sha256(canonical_json_bytes(canonical_manifest)).hexdigest()


def git_bytes(*arguments: str, timeout: int = 60) -> bytes:
    try:
        process = subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("bounded local Git command timed out") from error
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", "replace").strip()[:500]
        raise RuntimeError(f"bounded local Git command failed: {detail or 'no diagnostic'}")
    return process.stdout


def require_full_git_id(value: str, label: str) -> None:
    require(
        GIT_SHA1.fullmatch(value) is not None,
        f"{label} must be a full 40-character lowercase Git SHA-1",
    )


def verify_local_boundary(
    expected_commit: str,
    expected_tree: str,
    expected_parent: str,
    expected_records: list[ExpectedRecord],
) -> list[tuple[ExpectedRecord, bytes]]:
    for value, label in (
        (expected_commit, "--expected-commit"),
        (expected_tree, "--expected-tree"),
        (expected_parent, "--expected-parent"),
    ):
        require_full_git_id(value, label)

    resolved_commit = git_bytes(
        "rev-parse", "--verify", f"{expected_commit}^{{commit}}"
    ).decode("ascii").strip()
    require(resolved_commit == expected_commit, "expected commit did not resolve exactly")
    resolved_parent = git_bytes(
        "rev-parse", "--verify", f"{expected_parent}^{{commit}}"
    ).decode("ascii").strip()
    require(resolved_parent == expected_parent, "expected parent did not resolve exactly")

    actual_tree = git_bytes("rev-parse", f"{expected_commit}^{{tree}}").decode("ascii").strip()
    require(actual_tree == expected_tree, f"unexpected commit tree: {actual_tree}")
    parents = git_bytes("show", "-s", "--format=%P", expected_commit).decode("ascii").split()
    require(len(parents) == 1, f"publication boundary must have exactly one parent; got {len(parents)}")
    require(parents[0] == expected_parent, f"unexpected commit parent: {parents[0]}")

    raw_paths = git_bytes(
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "--no-renames",
        "-r",
        "-z",
        expected_commit,
    )
    try:
        changed_paths = [
            safe_repository_path(field.decode("utf-8"))
            for field in raw_paths.split(b"\0")
            if field
        ]
    except UnicodeDecodeError as error:
        raise RuntimeError("commit contains a changed path that is not UTF-8") from error
    require(
        len(changed_paths) == len(set(changed_paths)),
        "commit changed-path inventory contains duplicates",
    )
    expected_paths = [record.path for record in expected_records]
    changed_set = set(changed_paths)
    expected_set = set(expected_paths)
    require(
        changed_set == expected_set and len(changed_paths) == len(expected_paths),
        "manifest differs from the complete commit inventory: "
        f"missing={sorted(changed_set - expected_set)!r}, "
        f"unexpected={sorted(expected_set - changed_set)!r}",
    )

    local_records: list[tuple[ExpectedRecord, bytes]] = []
    for record in expected_records:
        object_name = f"{expected_commit}:{record.path}"
        try:
            local_size = int(git_bytes("cat-file", "-s", object_name).decode("ascii").strip())
        except ValueError as error:
            raise RuntimeError(f"malformed local blob size: {record.path}") from error
        require(
            local_size == record.bytes,
            f"local blob byte count differs from manifest: {record.path}",
        )
        blob = git_bytes("cat-file", "blob", object_name)
        actual_digest = sha256(blob).hexdigest()
        require(
            len(blob) == record.bytes,
            f"local blob byte count differs from manifest: {record.path}",
        )
        require(
            actual_digest == record.sha256,
            f"local blob SHA-256 differs from manifest: {record.path}",
        )
        local_records.append((record, blob))
    return local_records


def anonymous_git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    forbidden = {
        "ALL_PROXY",
        "AUTHORIZATION",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_HTTP_PROXY_AUTHMETHOD",
        "HTTP_AUTHORIZATION",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "PROXY_AUTHORIZATION",
    }
    for key in list(environment):
        upper = key.upper()
        if upper in forbidden or upper.startswith("GIT_CONFIG_KEY_") or upper.startswith("GIT_CONFIG_VALUE_"):
            environment.pop(key, None)
    environment.update(
        {
            "GIT_CEILING_DIRECTORIES": str(ROOT),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_ASKPASS": "",
            "SSH_ASKPASS": "",
        }
    )
    return environment


def anonymous_remote_head() -> tuple[str, str]:
    endpoint = f"https://github.com/{REPOSITORY}.git"
    ref = f"refs/heads/{BRANCH}"
    command = [
        "git",
        "-c",
        "credential.helper=",
        "-c",
        "credential.interactive=never",
        "-c",
        "core.askPass=",
        "-c",
        "http.extraHeader=",
        "-c",
        "http.https://github.com/.extraHeader=",
        "-c",
        "http.proxy=",
        "ls-remote",
        "--heads",
        endpoint,
        ref,
    ]
    last_error = "no result"
    for attempt in range(3):
        try:
            process = subprocess.run(
                command,
                cwd=ROOT / "scripts",
                env=anonymous_git_environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            last_error = "timeout"
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            break
        if process.returncode == 0:
            try:
                lines = [line for line in process.stdout.decode("ascii").splitlines() if line]
            except UnicodeDecodeError as error:
                raise RuntimeError("anonymous ls-remote returned non-ASCII output") from error
            require(len(lines) == 1, f"unexpected anonymous branch inventory count: {len(lines)}")
            fields = lines[0].split("\t")
            require(len(fields) == 2 and fields[1] == ref, "unexpected anonymous branch ref")
            require(GIT_SHA1.fullmatch(fields[0]) is not None, "malformed anonymous branch SHA")
            return fields[0], endpoint
        last_error = process.stderr.decode("utf-8", "replace").strip()[:500]
        if attempt < 2:
            time.sleep(1 + attempt)
    raise RuntimeError(f"anonymous git ls-remote failed after three attempts: {last_error}")


def immutable_raw_url(commit: str, path: str) -> str:
    return f"https://{RAW_HOST}/{REPOSITORY}/{commit}/{quote(path, safe='/')}"


def fetch_anonymously(url: str, expected_bytes: int) -> tuple[bytes, int, str]:
    parsed = urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname == RAW_HOST
        and parsed.username is None
        and parsed.password is None
        and parsed.fragment == "",
        "refusing a non-immutable or credential-bearing raw URL",
    )
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream"},
        method="GET",
    )
    request_header_names = {name.lower() for name, _ in request.header_items()}
    require(
        not request_header_names.intersection(
            {"authorization", "proxy-authorization", "cookie"}
        ),
        "authentication-bearing request header detected",
    )
    opener = build_opener(ProxyHandler({}), RejectRedirects())
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with opener.open(request, timeout=45) as response:
                status = response.getcode()
                final_url = response.geturl()
                require(status == 200, f"unexpected HTTP status {status}")
                require(final_url == url, f"redirect or endpoint drift detected: {final_url}")
                require(response.headers.get("Location") is None, "unexpected Location response header")
                final = urlsplit(final_url)
                require(
                    final.scheme == "https"
                    and final.hostname == RAW_HOST
                    and final.username is None
                    and final.password is None,
                    "unexpected immutable-readback endpoint",
                )
                payload = response.read(expected_bytes + 1)
                require(
                    len(payload) <= expected_bytes,
                    "public response exceeds the manifest byte bound",
                )
                return payload, status, final_url
        except HTTPError as error:
            if 300 <= error.code < 400:
                raise RuntimeError(f"redirect refused for immutable raw URL: HTTP {error.code}") from error
            if error.code not in RETRYABLE_HTTP_STATUS:
                raise RuntimeError(f"anonymous immutable readback failed: HTTP {error.code}") from error
            last_error = error
        except (URLError, TimeoutError, OSError) as error:
            last_error = error
        if attempt < 2:
            time.sleep(1 + attempt)
    raise RuntimeError(
        "anonymous immutable readback failed after three attempts: "
        f"{type(last_error).__name__ if last_error else 'unknown error'}"
    )


def fetch_record(
    item: tuple[ExpectedRecord, bytes], expected_commit: str
) -> dict[str, object]:
    expected, committed_blob = item
    url = immutable_raw_url(expected_commit, expected.path)
    public, status, final_url = fetch_anonymously(url, expected.bytes)
    public_digest = sha256(public).hexdigest()
    require(len(public) == expected.bytes, f"public byte count differs: {expected.path}")
    require(public_digest == expected.sha256, f"public SHA-256 differs: {expected.path}")
    require(public == committed_blob, f"public bytes differ from committed blob: {expected.path}")
    return {
        "path": expected.path,
        "bytes": len(public),
        "sha256": public_digest,
        "http_status": status,
        "url": url,
        "final_url": final_url,
        "redirects_followed": 0,
        "matches_expected_manifest": True,
        "matches_committed_blob": True,
    }


def build_parser() -> argparse.ArgumentParser:
    epilog = """\
Manifest schema (UTF-8 JSON; keys are exact and duplicate keys are rejected):
  {
    "schema_version": "1.0.0",
    "unit": "035",
    "boundary": "content",
    "records": [
      {"path": "README.md", "bytes": 123, "sha256": "<64 lowercase hex>"}
    ]
  }

Invoke separately, in publication order, while each commit is public main:
  python scripts/verify_unit_035_github_readback.py --boundary content \\
    --expected-commit <40hex> --expected-tree <40hex> \\
    --expected-parent <40hex> --manifest <content-manifest.json>
  python scripts/verify_unit_035_github_readback.py --boundary receipt \\
    --expected-commit <40hex> --expected-tree <40hex> \\
    --expected-parent <40hex> --manifest <receipt-manifest.json>
  python scripts/verify_unit_035_github_readback.py --boundary controls \\
    --expected-commit <40hex> --expected-tree <40hex> \\
    --expected-parent <40hex> --manifest <controls-manifest.json>

Use --offline-validate to check identities, the complete changed-path set, and
all local blob bytes/hashes without network access or output-file creation.
"""
    parser = argparse.ArgumentParser(
        description="Verify one Unit 035 GitHub publication boundary byte-for-byte.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--boundary", required=True, choices=BOUNDARIES)
    parser.add_argument("--expected-commit", required=True, metavar="40HEX")
    parser.add_argument("--expected-tree", required=True, metavar="40HEX")
    parser.add_argument("--expected-parent", required=True, metavar="40HEX")
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        metavar="JSON",
        help="explicit complete path/bytes/SHA-256 manifest (relative paths resolve from repository root)",
    )
    parser.add_argument(
        "--offline-validate",
        action="store_true",
        help="validate the local commit and manifest only; do not access GitHub or write a receipt",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest.is_absolute()
        else (ROOT / args.manifest).resolve()
    )
    expected_records, manifest_digest = read_manifest(manifest_path, args.boundary)
    local_records = verify_local_boundary(
        args.expected_commit,
        args.expected_tree,
        args.expected_parent,
        expected_records,
    )
    expected_total = sum(record.bytes for record in expected_records)

    if args.offline_validate:
        print(
            json.dumps(
                {
                    "status": "PASS_OFFLINE",
                    "unit": UNIT,
                    "boundary": args.boundary,
                    "commit": args.expected_commit,
                    "tree": args.expected_tree,
                    "parent": args.expected_parent,
                    "manifest_sha256": manifest_digest,
                    "paths": len(expected_records),
                    "bytes": expected_total,
                    "network_accessed": False,
                    "output_written": False,
                },
                indent=2,
            )
        )
        return 0

    output = OUTPUTS[args.boundary]
    require(output.parent == ROOT / "qa", "internal output boundary error")
    require(not output.exists(), f"refusing to overwrite existing receipt: {output.name}")

    remote_before, endpoint = anonymous_remote_head()
    require(
        remote_before == args.expected_commit,
        f"public {BRANCH} drift before readback: {remote_before}",
    )
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(
            pool.map(
                lambda item: fetch_record(item, args.expected_commit),
                local_records,
            )
        )
    require(len(records) == len(expected_records), "public record count drift")
    public_total = sum(int(record["bytes"]) for record in records)
    require(public_total == expected_total, "public total byte count drift")

    remote_after, endpoint_after = anonymous_remote_head()
    require(endpoint_after == endpoint, "anonymous branch endpoint changed during readback")
    require(
        remote_after == args.expected_commit,
        f"public {BRANCH} drift after readback: {remote_after}",
    )

    result = {
        "schema_version": "2.0.0",
        "unit": UNIT,
        "boundary": args.boundary,
        "repository": f"https://github.com/{REPOSITORY}",
        "branch": BRANCH,
        "commit": args.expected_commit,
        "tree": args.expected_tree,
        "parent": args.expected_parent,
        "expected_manifest": {
            "schema_version": "1.0.0",
            "canonical_sha256": manifest_digest,
            "path_count": len(expected_records),
            "total_bytes": expected_total,
        },
        "remote_branch_ref_endpoint": endpoint,
        "remote_branch_ref_method": (
            "anonymous git ls-remote with credential helper, prompts, extra headers, and proxies disabled"
        ),
        "remote_branch_before": remote_before,
        "remote_branch_after": remote_after,
        "remote_branch_matches_commit": True,
        "rest_api_used": False,
        "anonymous": True,
        "authorization_header_used": False,
        "proxy_authorization_header_used": False,
        "ambient_proxy_used": False,
        "redirects_followed": 0,
        "deterministic_inventory": True,
        "path_fetch_count": len(records),
        "total_bytes_fetched": public_total,
        "all_match": True,
        "records": records,
    }
    output_bytes = (
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    with output.open("xb") as handle:
        handle.write(output_bytes)
        handle.flush()
        os.fsync(handle.fileno())

    print(
        json.dumps(
            {
                "status": "PASS",
                "unit": UNIT,
                "boundary": args.boundary,
                "commit": args.expected_commit,
                "tree": args.expected_tree,
                "parent": args.expected_parent,
                "remote_main": remote_after,
                "manifest_sha256": manifest_digest,
                "paths": len(records),
                "bytes": public_total,
                "output": output.relative_to(ROOT).as_posix(),
                "output_bytes": len(output_bytes),
                "output_sha256": sha256(output_bytes).hexdigest(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
