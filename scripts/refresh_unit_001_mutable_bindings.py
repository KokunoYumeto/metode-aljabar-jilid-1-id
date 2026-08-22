#!/usr/bin/env python3
"""Refresh Unit 001's mutable file bindings without touching authority bytes.

Unit 001 predates the per-unit backend generators.  This bounded helper updates
only live derivative/build/QA bindings already present in its canonical JSON;
stable IDs, semantic records, rights, and immutable authority bindings remain
unchanged.  A line binding always carries both the full-file identity and the
normalized inclusive-span identity, so both are refreshed together.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "backend" / "data" / "unit-001-pendahuluan.json"
MUTABLE_PREFIXES = ("00_control/", "repo/", "artifacts/", "qa/", "scripts/")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def safe_path(relative: str) -> Path:
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        raise SystemExit(f"unsafe binding path: {relative!r}")
    candidate = (ROOT / Path(*posix.parts)).resolve()
    candidate.relative_to(ROOT.resolve())
    return candidate


def refresh(value: Any) -> None:
    if isinstance(value, dict):
        if {"path", "bytes", "sha256"}.issubset(value):
            relative = value["path"]
            if relative.startswith("authority/"):
                pass
            elif relative.startswith(MUTABLE_PREFIXES):
                path = safe_path(relative)
                payload = path.read_bytes()
                value["bytes"] = len(payload)
                value["sha256"] = sha256(payload)
                if "line_start" in value:
                    lines = payload.decode("utf-8").splitlines()
                    start = value["line_start"]
                    end = value["line_end"]
                    if not (1 <= start <= end <= len(lines)):
                        raise SystemExit(
                            f"invalid line range {start}-{end} for {relative}"
                        )
                    span = ("\n".join(lines[start - 1 : end]) + "\n").encode("utf-8")
                    value["span_sha256"] = sha256(span)
            else:
                raise SystemExit(f"unclassified non-authority binding: {relative!r}")
        for item in value.values():
            refresh(item)
    elif isinstance(value, list):
        for item in value:
            refresh(item)


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    refresh(data)
    DATA.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
