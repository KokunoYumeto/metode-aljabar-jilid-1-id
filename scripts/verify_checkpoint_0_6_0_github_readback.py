#!/usr/bin/env python3
"""Anonymously verify an immutable checkpoint 0.6.0 GitHub content commit."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = "KokunoYumeto/metode-aljabar-jilid-1-id"
BRANCH = "main"
READER_PATH = "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf"
REQUIRED_PATHS = {
    "README.md",
    READER_PATH,
    "qa/CHECKPOINT_READER_0_6_0_20260825.md",
    "qa/checkpoint-0.6.0-evidence/VISUAL_REVIEW.md",
    "qa/checkpoint-0.6.0-evidence/structure-text-navigation-font-render-qa.json",
    "scripts/build_checkpoint_reader_0_6_0.py",
    "scripts/qa_checkpoint_reader_0_6_0.py",
}
DEFAULT_OUTPUT = ROOT / "qa" / "PUBLICATION_GITHUB_CHECKPOINT_0.6.0_CONTENT_READBACK.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    require(
        value == path.as_posix()
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in value,
        f"Unsafe repository path: {value!r}",
    )
    return value


def git_bytes(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def verify_local_commit(commit: str) -> None:
    require(bool(HEX40.fullmatch(commit)), f"Commit must be a full lowercase SHA-1: {commit}")
    resolved = git_bytes("rev-parse", "--verify", f"{commit}^{{commit}}").decode("ascii").strip()
    require(resolved == commit, f"Commit did not resolve exactly: {resolved} != {commit}")


def anonymous_remote_head(repository: str, branch: str) -> str:
    url = f"https://github.com/{repository}.git"
    env = os.environ.copy()
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_ASKPASS": "",
            "SSH_ASKPASS": "",
        }
    )
    last_error = "no result"
    for attempt in range(3):
        process = subprocess.run(
            [
                "git",
                "-c", "credential.helper=",
                "-c", "http.extraHeader=",
                "ls-remote",
                "--heads",
                url,
                f"refs/heads/{branch}",
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=60,
        )
        if process.returncode == 0:
            lines = [line for line in process.stdout.decode("ascii").splitlines() if line]
            require(len(lines) == 1, f"Unexpected public branch inventory: {lines}")
            remote_sha, remote_ref = lines[0].split("\t", 1)
            require(remote_ref == f"refs/heads/{branch}", f"Unexpected public ref: {remote_ref}")
            require(bool(HEX40.fullmatch(remote_sha)), f"Malformed public branch SHA: {remote_sha}")
            return remote_sha
        last_error = process.stderr.decode("utf-8", "replace")[:500]
        if attempt < 2:
            time.sleep(2 + attempt)
    raise RuntimeError(f"Anonymous public branch lookup failed: {last_error}")


def fetch(url: str) -> tuple[bytes, str, int]:
    request = Request(url, headers={"User-Agent": "O013-public-byte-verifier/1.0"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                final_url = response.geturl()
                parsed = urlparse(final_url)
                require(parsed.scheme == "https" and parsed.hostname == "raw.githubusercontent.com",
                        f"Unexpected immutable-readback endpoint: {final_url}")
                return response.read(), final_url, response.status
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(1 + attempt)
    raise RuntimeError(
        f"anonymous readback failed after three attempts: {url}: {last_error}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True,
                        help="immutable checkpoint content commit currently published on main")
    parser.add_argument("--expected-parent", required=True, help="full parent commit SHA-1")
    parser.add_argument(
        "--expected-path",
        action="append",
        required=True,
        dest="expected_paths",
        help="one exact changed path; repeat for the complete intended commit inventory",
    )
    parser.add_argument("--repository", default=REPOSITORY)
    parser.add_argument("--branch", default=BRANCH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository) is not None,
            f"Malformed GitHub repository: {args.repository}")
    require(re.fullmatch(r"[A-Za-z0-9._/-]+", args.branch) is not None and ".." not in args.branch,
            f"Malformed branch name: {args.branch}")
    verify_local_commit(args.commit)
    verify_local_commit(args.expected_parent)
    head = git_bytes("rev-parse", "HEAD").decode("ascii").strip()
    require(head == args.commit, f"Local HEAD drift: {head} != {args.commit}")
    parent = git_bytes("rev-parse", f"{args.commit}^").decode("ascii").strip()
    require(parent == args.expected_parent, f"Unexpected checkpoint parent: {parent}")

    expected_paths = [safe_path(path) for path in args.expected_paths]
    require(len(expected_paths) == len(set(expected_paths)), "Duplicate --expected-path argument")
    expected_set = set(expected_paths)
    require(REQUIRED_PATHS.issubset(expected_set),
            f"Explicit commit inventory omits required paths: {sorted(REQUIRED_PATHS - expected_set)}")
    raw_names = git_bytes("diff-tree", "--no-commit-id", "--name-only", "-r", args.commit)
    paths = [line.decode("utf-8") for line in raw_names.splitlines() if line]
    require(len(paths) == len(set(paths)), "Commit path inventory contains duplicates")
    require(set(paths) == expected_set and len(paths) == len(expected_paths),
            f"Commit path inventory differs: expected {sorted(expected_set)}, got {sorted(paths)}")

    remote_head = anonymous_remote_head(args.repository, args.branch)
    require(remote_head == args.commit,
            f"Public {args.branch} head differs: {remote_head} != {args.commit}")

    records: list[dict[str, object]] = []
    total_bytes = 0
    for path in paths:
        blob = git_bytes("cat-file", "blob", f"{args.commit}:{path}")
        url = (
            f"https://raw.githubusercontent.com/{args.repository}/{args.commit}/"
            f"{quote(path, safe='/')}"
        )
        public, final_url, status = fetch(url)
        require(status == 200, f"HTTP {status} for {path}")
        require(public == blob, f"Public bytes differ from committed blob: {path}")
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

    output = args.output.resolve() if args.output.is_absolute() else (ROOT / args.output).resolve()
    try:
        output.relative_to(ROOT)
    except ValueError as error:
        raise RuntimeError(f"Readback output must remain inside the edition repository: {output}") from error
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": "2.0.0",
        "checked_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": f"https://github.com/{args.repository}",
        "branch": args.branch,
        "commit": args.commit,
        "parent": args.expected_parent,
        "public_branch_head": remote_head,
        "anonymous": True,
        "authorization_header_used": False,
        "git_credential_helper_disabled_for_remote_ref_check": True,
        "path_count": len(records),
        "total_bytes": total_bytes,
        "all_match": True,
        "records": records,
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "commit": args.commit,
                "paths": len(records),
                "bytes": total_bytes,
                "output": output.relative_to(ROOT).as_posix(),
                "output_bytes": output.stat().st_size,
                "output_sha256": sha256(output.read_bytes()).hexdigest(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
