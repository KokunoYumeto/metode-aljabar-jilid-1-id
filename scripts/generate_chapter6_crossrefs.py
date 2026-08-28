#!/usr/bin/env python3
"""Freeze exact external Chapter 6 labels from a full-corpus aux witness."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "repo/source/chapter6.tex"
OUTPUT = ROOT / "repo/source/chapter6-crossrefs.aux"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aux-directory", type=Path, required=True)
    args = parser.parse_args()
    aux_directory = args.aux_directory.resolve()
    text = CHAPTER.read_text(encoding="utf-8")
    local = set(re.findall(r"\\label\{([^}]+)\}", text))
    needed: list[str] = []
    for key in re.findall(r"\\(?:ref|eqref|rref|cref)\{([^}]+)\}", text):
        if key not in local and key not in needed:
            needed.append(key)

    mapping: dict[str, str] = {}
    sources: dict[str, str] = {}
    for name in ("prelude.aux", *(f"chapter{number}.aux" for number in range(1, 11))):
        path = aux_directory / name
        if not path.is_file():
            raise RuntimeError(f"missing full-corpus aux witness: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"\\newlabel\{([^}]+)\}(\{.*\})", line)
            if not match:
                continue
            key, payload = match.groups()
            if key in mapping and mapping[key] != payload:
                raise RuntimeError(f"conflicting label witness: {key}")
            mapping[key] = payload
            sources[key] = name
    missing = [key for key in needed if key not in mapping]
    if missing:
        raise RuntimeError(f"missing external labels: {missing}")
    lines = ["\\relax"] + [f"\\newlabel{{{key}}}{mapping[key]}" for key in needed]
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    OUTPUT.write_bytes(payload)
    print(f"external_labels={len(needed)}")
    print(f"bytes={len(payload)}")
    print(f"sha256={hashlib.sha256(payload).hexdigest()}")
    for key in needed:
        print(f"{key}\t{sources[key]}")


if __name__ == "__main__":
    main()
