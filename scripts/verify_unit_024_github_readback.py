#!/usr/bin/env python3
"""Anonymously verify every path in the corrected Unit 024 GitHub commit."""

from __future__ import annotations

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
BOUNDARIES = (
    {
        "role": "initial Unit 024 content",
        "commit": "bb913c53781e06b9a5fd0f57b981581faa7649c8",
        "parent": "8393b331180a4e87d52488801abcb53b413dd1b7",
        "tree": "dda48486a7cddb63d116510a5cef57078877ba41",
        "path_count": 38,
        "total_bytes": 2_071_731,
    },
    {
        "role": "index-destination correction",
        "commit": "b9909c801f7bc1123e274c8036bb5b75f4ed0414",
        "parent": "bb913c53781e06b9a5fd0f57b981581faa7649c8",
        "tree": "a53aa210afb56bcaf40246da82a45e87d5727f46",
        "path_count": 13,
        "total_bytes": 465_946,
    },
)
CURRENT_COMMIT = BOUNDARIES[-1]["commit"]
OUTPUT = ROOT / "qa" / "PUBLICATION_GITHUB_UNIT_024_CONTENT_READBACK.json"


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


def fetch_record(item: tuple[str, str, bytes]) -> dict[str, object]:
    commit, path, blob = item
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
        "commit": commit,
        "path": path,
        "bytes": len(public),
        "sha256": sha256(public).hexdigest(),
        "http_status": status,
        "final_url": final_url,
        "matches_committed_blob": True,
    }


def main() -> int:
    remote_main_before, ref_endpoint = read_remote_main()
    if remote_main_before != CURRENT_COMMIT:
        raise RuntimeError(f"remote main drift before readback: {remote_main_before}")

    verified_boundaries: list[dict[str, object]] = []
    all_records: list[dict[str, object]] = []
    for expected in BOUNDARIES:
        commit = str(expected["commit"])
        parent = git_bytes("rev-parse", f"{commit}^").decode("ascii").strip()
        if parent != expected["parent"]:
            raise RuntimeError(f"unexpected parent for {commit}: {parent}")
        tree = git_bytes("rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
        if tree != expected["tree"]:
            raise RuntimeError(f"unexpected tree for {commit}: {tree}")
        raw_names = git_bytes(
            "diff-tree", "--no-commit-id", "--name-only", "-r", commit
        )
        paths = [line.decode("utf-8") for line in raw_names.splitlines() if line]
        if len(paths) != expected["path_count"] or len(set(paths)) != len(paths):
            raise RuntimeError(f"unexpected path inventory for {commit}: {len(paths)}")
        local_blobs = [
            (commit, path, git_bytes("cat-file", "blob", f"{commit}:{path}"))
            for path in paths
        ]
        with ThreadPoolExecutor(max_workers=8) as pool:
            records = list(pool.map(fetch_record, local_blobs))
        total_bytes = sum(int(record["bytes"]) for record in records)
        if total_bytes != expected["total_bytes"]:
            raise RuntimeError(
                f"unexpected public-byte total for {commit}: "
                f"{total_bytes} != {expected['total_bytes']}"
            )
        all_records.extend(records)
        verified_boundaries.append(
            {
                **expected,
                "all_match": True,
                "records": records,
            }
        )

    remote_main_after, ref_endpoint_after = read_remote_main()
    if remote_main_after != CURRENT_COMMIT:
        raise RuntimeError(f"remote main drift after readback: {remote_main_after}")
    if ref_endpoint_after != ref_endpoint:
        raise RuntimeError("remote main endpoint changed during readback")

    result = {
        "schema_version": "1.1.0",
        "checked_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": f"https://github.com/{REPOSITORY}",
        "branch": "main",
        "current_commit": CURRENT_COMMIT,
        "boundaries": verified_boundaries,
        "remote_main_ref_endpoint": ref_endpoint,
        "remote_main_ref_method": "anonymous git ls-remote with credential helper disabled",
        "remote_main_before": remote_main_before,
        "remote_main_after": remote_main_after,
        "remote_main_matches_commit": True,
        "anonymous": True,
        "authorization_header_used": False,
        "path_fetch_count": len(all_records),
        "total_bytes_fetched": sum(int(record["bytes"]) for record in all_records),
        "all_match": True,
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
                "commit": CURRENT_COMMIT,
                "remote_main": remote_main_after,
                "boundaries": len(verified_boundaries),
                "paths": len(all_records),
                "bytes": sum(int(record["bytes"]) for record in all_records),
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
