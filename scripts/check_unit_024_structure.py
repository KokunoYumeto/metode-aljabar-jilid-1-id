#!/usr/bin/env python3
"""Fail-closed canonical-boundary check for Li Unit 024."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
AUTHORITY = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter3.tex"
)
CANDIDATE = ROOT / "build" / "unit-024-candidate" / "chapter3-exercises-id.tex"
TARGET = ROOT / "repo" / "source" / "chapter3.tex"
CANDIDATE_CHECKER = ROOT / "scripts" / "check_unit_024_candidate.py"

AUTHORITY_BYTES = 75_571
AUTHORITY_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
AUTHORITY_LINES = 911
SOURCE_START = 873
SOURCE_END = 911
SOURCE_SPAN_BYTES = 4_954
SOURCE_SPAN_SHA256 = "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857"

CANDIDATE_BYTES = 6_071
CANDIDATE_SHA256 = "576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a"
CANDIDATE_LINES = 39

TARGET_BYTES = 89_608
TARGET_SHA256 = "443b71b515aef66c6ba8e259e65083604d227370c1ee7ca3ed49bdb5996f45fb"
TARGET_LINES = 910
TARGET_START = 872
TARGET_END = 910
PRESERVED_PREFIX_BYTES = 83_537
PRESERVED_PREFIX_SHA256 = "96da59f64d8c6ec8185bd1e35fa434ada484cfd9f3d533a7069d8aef95728542"


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def require(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise RuntimeError(f"{name} drift: {actual!r} != {expected!r}")


def read(name: str, path: Path, expected_bytes: int, expected_hash: str) -> bytes:
    require(f"{name} exists", path.is_file(), True)
    data = path.read_bytes()
    require(f"{name} bytes", len(data), expected_bytes)
    require(f"{name} SHA-256", digest(data), expected_hash)
    return data


def records(name: str, data: bytes, expected: int) -> list[bytes]:
    require(f"{name} terminal LF", data.endswith(b"\n"), True)
    require(f"{name} CR absence", b"\r" in data, False)
    rows = data.splitlines(keepends=True)
    require(f"{name} LF records", len(rows), expected)
    require(f"{name} complete records", all(row.endswith(b"\n") for row in rows), True)
    return rows


def main() -> int:
    require("arguments", sys.argv[1:], [])
    candidate_check = subprocess.run(
        [sys.executable, "-B", str(CANDIDATE_CHECKER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if candidate_check.returncode != 0:
        raise RuntimeError(
            "isolated candidate checker failed:\n"
            + candidate_check.stdout
            + candidate_check.stderr
        )

    authority = read("authority", AUTHORITY, AUTHORITY_BYTES, AUTHORITY_SHA256)
    candidate = read("candidate", CANDIDATE, CANDIDATE_BYTES, CANDIDATE_SHA256)
    target = read("canonical target", TARGET, TARGET_BYTES, TARGET_SHA256)
    authority_rows = records("authority", authority, AUTHORITY_LINES)
    candidate_rows = records("candidate", candidate, CANDIDATE_LINES)
    target_rows = records("canonical target", target, TARGET_LINES)

    source_span = b"".join(authority_rows[SOURCE_START - 1 : SOURCE_END])
    require("source span bytes", len(source_span), SOURCE_SPAN_BYTES)
    require("source span SHA-256", digest(source_span), SOURCE_SPAN_SHA256)
    require("source span begins Exercises", authority_rows[SOURCE_START - 1], b"\\begin{Exercises}\n")
    require("source span ends Exercises", authority_rows[SOURCE_END - 1], b"\\end{Exercises}\n")
    require("authority suffix after Unit 024", b"".join(authority_rows[SOURCE_END:]), b"")

    prefix = b"".join(target_rows[: TARGET_START - 1])
    integrated = b"".join(target_rows[TARGET_START - 1 : TARGET_END])
    suffix = b"".join(target_rows[TARGET_END:])
    require("preserved admitted prefix bytes", len(prefix), PRESERVED_PREFIX_BYTES)
    require("preserved admitted prefix SHA-256", digest(prefix), PRESERVED_PREFIX_SHA256)
    require("integrated Unit 024 bytes", integrated, candidate)
    require("integrated Unit 024 SHA-256", digest(integrated), CANDIDATE_SHA256)
    require("canonical suffix after Unit 024", suffix, b"")
    require("candidate begins Exercises", candidate_rows[0], b"\\begin{Exercises}\n")
    require("candidate ends Exercises", candidate_rows[-1], b"\\end{Exercises}\n")

    print("PASS Unit 024 canonical structure")
    print(f"authority_span=chapter3.tex:{SOURCE_START}-{SOURCE_END}")
    print(f"authority_span_bytes={len(source_span)}")
    print(f"authority_span_sha256={digest(source_span)}")
    print(f"target_span_lines={TARGET_START}-{TARGET_END}")
    print(f"target_span_bytes={len(integrated)}")
    print(f"target_span_sha256={digest(integrated)}")
    print(f"target_full_bytes={len(target)}")
    print(f"target_full_sha256={digest(target)}")
    print("post_span_suffix=empty; Chapter 3 complete")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FAIL Unit 024 canonical structure: {error}", file=sys.stderr)
        raise SystemExit(1)
