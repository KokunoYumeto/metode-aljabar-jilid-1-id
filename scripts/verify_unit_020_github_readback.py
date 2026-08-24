#!/usr/bin/env python3
"""Anonymously verify every path in the immutable Unit 020 GitHub commit."""

from __future__ import annotations

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
COMMIT = "84df4314c6291a60856b671009f433cdf52b4cf1"
REPOSITORY = "KokunoYumeto/metode-aljabar-jilid-1-id"
EXPECTED_PARENT = "43225b2a2c37db92af6f09fbb643a79cbbcf75b9"
EXPECTED_PATH_COUNT = 41
OUTPUT = ROOT / "qa" / "PUBLICATION_GITHUB_UNIT_020_CONTENT_READBACK.json"


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


def main() -> int:
    head = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    if head != COMMIT:
        raise RuntimeError(f"local HEAD drift: {head} != {COMMIT}")
    parent = git_bytes("rev-parse", f"{COMMIT}^").decode("ascii").strip()
    if parent != EXPECTED_PARENT:
        raise RuntimeError(f"unexpected Unit 020 parent: {parent}")

    raw_names = git_bytes("diff-tree", "--no-commit-id", "--name-only", "-r", COMMIT)
    paths = [line.decode("utf-8") for line in raw_names.splitlines() if line]
    if len(paths) != EXPECTED_PATH_COUNT or len(set(paths)) != len(paths):
        raise RuntimeError(f"unexpected commit path inventory: {len(paths)}")

    records: list[dict[str, object]] = []
    total_bytes = 0
    for path in paths:
        blob = git_bytes("cat-file", "blob", f"{COMMIT}:{path}")
        url = (
            f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/"
            f"{quote(path, safe='/')}"
        )
        public, final_url, status = fetch(url)
        if status != 200:
            raise RuntimeError(f"HTTP {status} for {path}")
        if public != blob:
            raise RuntimeError(f"public bytes differ from committed blob: {path}")
        total_bytes += len(public)
        records.append(
            {
                "path": path,
                "bytes": len(public),
                "sha256": sha256(public).hexdigest(),
                "http_status": status,
                "final_url": final_url,
                "matches_committed_blob": True,
            }
        )

    result = {
        "schema_version": "1.0.0",
        "checked_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": f"https://github.com/{REPOSITORY}",
        "branch": "main",
        "commit": COMMIT,
        "parent": EXPECTED_PARENT,
        "anonymous": True,
        "authorization_header_used": False,
        "path_count": len(records),
        "total_bytes": total_bytes,
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
                "paths": len(records),
                "bytes": total_bytes,
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
