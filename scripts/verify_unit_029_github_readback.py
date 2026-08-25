#!/usr/bin/env python3
"""Anonymously verify every path changed by the Unit 029 content commit.

The commit is supplied explicitly after publication. The verifier reads only
that immutable commit and its parent, fetches every changed blob from the
public raw endpoint without credentials, and records a complete receipt.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "KokunoYumeto/metode-aljabar-jilid-1-id"
OUTPUT = ROOT / "qa" / "PUBLICATION_GITHUB_UNIT_029_CONTENT_READBACK.json"


def git_bytes(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def fetch(url: str) -> tuple[bytes, str, int]:
    request = Request(url, headers={"User-Agent": "O013-public-byte-verifier/1.0"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read(), response.geturl(), response.status
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(1 + attempt)
    raise RuntimeError(
        f"anonymous readback failed after three attempts: {url}: {last_error}"
    )


def read_remote_main() -> tuple[str, str]:
    endpoint = f"https://github.com/{REPOSITORY}.git"
    payload = subprocess.check_output(
        [
            "git",
            "-c",
            "credential.helper=",
            "ls-remote",
            "--heads",
            endpoint,
            "refs/heads/main",
        ],
        cwd=ROOT,
    ).decode("ascii").strip()
    fields = payload.split()
    if len(fields) != 2 or fields[1] != "refs/heads/main":
        raise RuntimeError(f"unexpected anonymous ls-remote result: {payload!r}")
    return fields[0], endpoint


def fetch_record(item: tuple[str, bytes], commit: str) -> dict[str, object]:
    path, blob = item
    url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/"
        f"{quote(path, safe='/')}"
    )
    public, final_url, status = fetch(url)
    if status != 200:
        raise RuntimeError(f"HTTP {status} for {path}")
    if public != blob:
        raise RuntimeError(f"public bytes differ from committed blob: {path}")
    return {
        "path": path,
        "bytes": len(public),
        "sha256": sha256(public).hexdigest(),
        "http_status": status,
        "final_url": final_url,
        "matches_committed_blob": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--expected-paths", required=True, type=int)
    parser.add_argument("--expected-bytes", required=True, type=int)
    args = parser.parse_args()

    commit = git_bytes("rev-parse", f"{args.commit}^{{commit}}").decode("ascii").strip()
    if commit != args.commit:
        raise RuntimeError(f"commit was not supplied as a full immutable ID: {commit}")
    parent = git_bytes("rev-parse", f"{commit}^").decode("ascii").strip()
    if parent != args.expected_parent:
        raise RuntimeError(f"unexpected content parent: {parent}")
    tree = git_bytes("rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()

    raw_names = git_bytes("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    paths = [line.decode("utf-8") for line in raw_names.splitlines() if line]
    if len(paths) != args.expected_paths or len(paths) != len(set(paths)):
        raise RuntimeError(f"unexpected path inventory: {len(paths)}")
    local_blobs = [
        (path, git_bytes("cat-file", "blob", f"{commit}:{path}")) for path in paths
    ]
    local_total = sum(len(blob) for _, blob in local_blobs)
    if local_total != args.expected_bytes:
        raise RuntimeError(
            f"unexpected local blob total: {local_total} != {args.expected_bytes}"
        )

    remote_before, ref_endpoint = read_remote_main()
    if remote_before != commit:
        raise RuntimeError(f"remote main drift before readback: {remote_before}")
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(lambda item: fetch_record(item, commit), local_blobs))
    public_total = sum(int(record["bytes"]) for record in records)
    if public_total != args.expected_bytes:
        raise RuntimeError(
            f"unexpected public-byte total: {public_total} != {args.expected_bytes}"
        )
    remote_after, ref_endpoint_after = read_remote_main()
    if remote_after != commit or ref_endpoint_after != ref_endpoint:
        raise RuntimeError("public main changed during readback")

    result = {
        "schema_version": "1.0.0",
        "checked_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": f"https://github.com/{REPOSITORY}",
        "branch": "main",
        "commit": commit,
        "parent": parent,
        "tree": tree,
        "remote_main_ref_endpoint": ref_endpoint,
        "remote_main_ref_method": "anonymous git ls-remote with credential helper disabled",
        "remote_main_before": remote_before,
        "remote_main_after": remote_after,
        "remote_main_matches_commit": True,
        "anonymous": True,
        "authorization_header_used": False,
        "path_fetch_count": len(records),
        "total_bytes_fetched": public_total,
        "all_match": True,
        "records": records,
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "commit": commit,
                "remote_main": remote_after,
                "paths": len(records),
                "bytes": public_total,
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "output_bytes": OUTPUT.stat().st_size,
                "output_sha256": sha256(OUTPUT.read_bytes()).hexdigest(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
