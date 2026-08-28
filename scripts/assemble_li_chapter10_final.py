#!/usr/bin/env python3
"""Assemble the three independently edited Chapter 10 record ranges."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    (ROOT / "build/chapter10-batch-candidate/final-parts/part-001-500.tex", 500),
    (ROOT / "build/chapter10-batch-candidate/final-parts/part-501-1000.tex", 500),
    (ROOT / "build/chapter10-batch-candidate/final-parts/part-1001-1472.tex", 472),
)
OUTPUT = ROOT / "build/chapter10-batch-candidate/chapter10-complete-id-final.tex"


def main() -> int:
    records: list[str] = []
    for path, expected in PARTS:
        payload = path.read_bytes()
        if payload.startswith(b"\xef\xbb\xbf") or b"\r" in payload:
            raise RuntimeError(f"noncanonical part: {path}")
        rows = payload.decode("utf-8", errors="strict").splitlines()
        if len(rows) != expected:
            raise RuntimeError(f"record drift: {path} has {len(rows)}, expected {expected}")
        records.extend(rows)
    if len(records) != 1472:
        raise RuntimeError(f"aggregate record drift: {len(records)}")
    payload = ("\n".join(records) + "\n").encode("utf-8")
    temporary = OUTPUT.with_name(OUTPUT.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"stale temporary: {temporary}")
    temporary.write_bytes(payload)
    if temporary.read_bytes() != payload:
        raise RuntimeError("temporary readback differs")
    os.replace(temporary, OUTPUT)
    print(f"records=1472 bytes={len(payload)} sha256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
