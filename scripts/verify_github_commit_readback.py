#!/usr/bin/env python3
"""Verify one narrow public GitHub commit boundary without credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "metode-aljabar-jilid-1-id"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE,
        **({} if binary else {"text": True, "encoding": "utf-8"}),
    )
    return result.stdout


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--parent", required=True)
    parser.add_argument("--boundary", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--path", action="append", required=True)
    parser.add_argument(
        "--allow-descendant-main", action="store_true",
        help="accept public main at a descendant when verifying an older immutable commit",
    )
    args = parser.parse_args()

    require(len(args.commit) == 40 and len(args.parent) == 40, "commit identities must be full hashes")
    actual_parent = str(git("rev-parse", f"{args.commit}^" )).strip()
    require(actual_parent == args.parent, "parent identity drifted")
    changed = {
        line for line in str(git("diff-tree", "--no-commit-id", "--name-only", "-r", args.commit)).splitlines()
        if line
    }
    expected_paths = set(args.path)
    require(changed == expected_paths,
            f"changed-path set drifted; missing={sorted(expected_paths-changed)}, extra={sorted(changed-expected_paths)}")

    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": "Codex O013 anonymous GitHub readback"})
    ref = session.get(
        f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/git/ref/heads/main",
        timeout=(30, 90),
    )
    require(ref.status_code == 200, f"anonymous branch ref failed: HTTP {ref.status_code}")
    remote = ref.json().get("object", {}).get("sha")
    if remote != args.commit:
        require(args.allow_descendant_main,
                f"public main points to {remote}, not {args.commit}")
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", args.commit, str(remote)],
            cwd=ROOT, check=False,
        )
        require(ancestry.returncode == 0,
                f"public main {remote} is not a descendant of {args.commit}")

    records: list[dict[str, Any]] = []
    for path in sorted(expected_paths):
        local = git("show", f"{args.commit}:{path}", binary=True)
        require(isinstance(local, bytes), "local blob read was not binary")
        url = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/{args.commit}/{path}"
        response = session.get(url, timeout=(30, 180))
        require(response.status_code == 200, f"anonymous raw fetch failed for {path}: HTTP {response.status_code}")
        require(response.content == local, f"public bytes differ for {path}")
        records.append({
            "path": path,
            "bytes": len(local),
            "sha256": digest(local),
            "http_status": response.status_code,
            "url": url,
            "matches_committed_blob": True,
        })

    evidence = {
        "schema_version": "1.0.0",
        "boundary": args.boundary,
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "branch": "main",
        "commit": args.commit,
        "tree": str(git("rev-parse", f"{args.commit}^{{tree}}" )).strip(),
        "parent": args.parent,
        "remote_branch": remote,
        "anonymous": True,
        "authorization_header_used": False,
        "path_fetch_count": len(records),
        "total_bytes_fetched": sum(item["bytes"] for item in records),
        "all_match": True,
        "records": records,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({key: evidence[key] for key in (
        "boundary", "commit", "tree", "parent", "path_fetch_count",
        "total_bytes_fetched", "all_match"
    )}, indent=2))


if __name__ == "__main__":
    main()
