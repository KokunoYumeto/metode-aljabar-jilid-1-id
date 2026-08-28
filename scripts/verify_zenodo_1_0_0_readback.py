#!/usr/bin/env python3
"""Anonymously verify the public Zenodo 1.0.0 complete-Li release."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import build_release_1_0_0 as release
import verify_zenodo_0_7_0_readback as base


def extract_record_id() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--record-id", type=int, required=True)
    known, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]
    return known.record_id


def configure(record_id: int) -> None:
    base.ROOT = release.ROOT
    base.RECORD_ID = record_id
    base.VERSION_DOI = f"10.5281/zenodo.{record_id}"
    base.CONCEPT_DOI = release.CONCEPT_DOI
    base.VERSION = release.VERSION
    base.TITLE = release.TITLE
    base.READER = release.READER_NAME
    base.EXPECTED_NAMES = set(release.EXPECTED_NAMES)


def receipt_path() -> Path | None:
    if "--receipt" not in sys.argv:
        return None
    index = sys.argv.index("--receipt")
    if index + 1 >= len(sys.argv):
        return None
    path = Path(sys.argv[index + 1])
    return path if path.is_absolute() else release.ROOT / path


def normalize_receipt(path: Path | None) -> None:
    if path is None or not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace("version 0.7.0", "version 1.0.0")
    text = text.replace(
        "complete prelude and Li Chapters 1–5; 385-page reader; later corpus components remain unfinished.",
        "complete prelude and Li Chapters 1–10; 521-page reader; separate O013 companion components are outside this book release.",
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    record_id = extract_record_id()
    configure(record_id)
    receipt = receipt_path()
    base.main()
    normalize_receipt(receipt)


if __name__ == "__main__":
    main()
