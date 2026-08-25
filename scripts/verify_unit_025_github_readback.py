#!/usr/bin/env python3
"""Anonymously verify every path in the Unit 025 GitHub content commit."""

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
COMMIT = "6b3fbd5fb93fe7b19feae386204c282b40d5dcfc"
PARENT = "3246f128b3dafe935342dc304093c9e11d25d23d"
TREE = "afa41d8fee5984be37c319bf61eddcedbc886002"
EXPECTED_PATH_COUNT = 52
EXPECTED_TOTAL_BYTES = 5_396_723
OUTPUT = ROOT / "qa" / "PUBLICATION_GITHUB_UNIT_025_CONTENT_READBACK.json"


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


def fetch_record(item: tuple[str, bytes]) -> dict[str, object]:
    path, blob = item
    url = (
        f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/"
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
    local_head = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    if local_head != COMMIT:
        raise RuntimeError(f"local HEAD drift before readback: {local_head}")
    parent = git_bytes("rev-parse", f"{COMMIT}^").decode("ascii").strip()
    if parent != PARENT:
        raise RuntimeError(f"unexpected content parent: {parent}")
    tree = git_bytes("rev-parse", f"{COMMIT}^{{tree}}").decode("ascii").strip()
    if tree != TREE:
        raise RuntimeError(f"unexpected content tree: {tree}")

    raw_names = git_bytes(
        "diff-tree", "--no-commit-id", "--name-only", "-r", COMMIT
    )
    paths = [line.decode("utf-8") for line in raw_names.splitlines() if line]
    if len(paths) != EXPECTED_PATH_COUNT or len(set(paths)) != len(paths):
        raise RuntimeError(f"unexpected path inventory: {len(paths)}")
    local_blobs = [
        (path, git_bytes("cat-file", "blob", f"{COMMIT}:{path}")) for path in paths
    ]
    local_total = sum(len(blob) for _, blob in local_blobs)
    if local_total != EXPECTED_TOTAL_BYTES:
        raise RuntimeError(
            f"unexpected local blob total: {local_total} != {EXPECTED_TOTAL_BYTES}"
        )

    remote_main_before, ref_endpoint = read_remote_main()
    if remote_main_before != COMMIT:
        raise RuntimeError(f"remote main drift before readback: {remote_main_before}")
    with ThreadPoolExecutor(max_workers=8) as pool:
        records = list(pool.map(fetch_record, local_blobs))
    public_total = sum(int(record["bytes"]) for record in records)
    if public_total != EXPECTED_TOTAL_BYTES:
        raise RuntimeError(
            f"unexpected public-byte total: {public_total} != {EXPECTED_TOTAL_BYTES}"
        )

    remote_main_after, ref_endpoint_after = read_remote_main()
    if remote_main_after != COMMIT:
        raise RuntimeError(f"remote main drift after readback: {remote_main_after}")
    if ref_endpoint_after != ref_endpoint:
        raise RuntimeError("remote main endpoint changed during readback")

    result = {
        "schema_version": "1.0.0",
        "checked_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": f"https://github.com/{REPOSITORY}",
        "branch": "main",
        "commit": COMMIT,
        "parent": PARENT,
        "tree": TREE,
        "remote_main_ref_endpoint": ref_endpoint,
        "remote_main_ref_method": (
            "anonymous git ls-remote with credential helper disabled"
        ),
        "remote_main_before": remote_main_before,
        "remote_main_after": remote_main_after,
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
                "commit": COMMIT,
                "remote_main": remote_main_after,
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
