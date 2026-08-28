#!/usr/bin/env python3
"""Freeze exact Chapter 7-10 admission inputs and predicted glossary output."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from promote_li_final_chapters import (
    GLOSSARY,
    MANIFEST,
    ROOT,
    csv_rows,
    encode,
    require,
    sha,
    strict,
)


FIXED = {
    7: (
        "build/chapter7-batch-candidate/chapter7-complete-id.tex",
        "build/chapter7-batch-candidate/check_candidate.py",
        "build/chapter7-batch-candidate/terminology-delta.csv",
    ),
    8: (
        "build/chapter8-batch-candidate/chapter8-complete-id.tex",
        "build/chapter8-batch-candidate/check_chapter8_complete.py",
        "build/chapter8-batch-candidate/TERMINOLOGY.delta.chapter8.id-ID.csv",
    ),
    9: (
        "build/chapter9-batch-candidate/chapter9-complete-id.tex",
        "build/chapter9-batch-candidate/check_chapter9_complete.py",
        "build/chapter9-batch-candidate/TERMINOLOGY.delta.chapter9.id-ID.csv",
    ),
}


def binding(relative: str) -> dict[str, object]:
    payload = strict(ROOT / relative)
    return {"path": relative, "bytes": len(payload), "sha256": sha(payload)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chapter10-candidate",
        default="build/chapter10-batch-candidate/chapter10-complete-id-final.tex",
    )
    parser.add_argument(
        "--chapter10-checker",
        default="build/chapter10-batch-candidate/check_chapter10_complete_final.py",
    )
    parser.add_argument(
        "--chapter10-delta",
        default="build/chapter10-batch-candidate/TERMINOLOGY.delta.chapter10.id-ID.csv",
    )
    args = parser.parse_args()
    mappings = dict(FIXED)
    mappings[10] = (args.chapter10_candidate, args.chapter10_checker, args.chapter10_delta)

    glossary_payload = strict(GLOSSARY)
    merged = [dict(item) for item in csv_rows(glossary_payload, "controlled glossary")]
    positions = {item["source_term"].casefold(): index for index, item in enumerate(merged)}
    chapters: list[dict[str, object]] = []
    for chapter in range(7, 11):
        candidate_path, checker_path, delta_path = mappings[chapter]
        authority_path = (
            "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/"
            f"chapter{chapter}.tex"
        )
        values = {
            "chapter": chapter,
            "canonical_path": f"repo/source/chapter{chapter}.tex",
            "authority_path": authority_path,
            "candidate_path": candidate_path,
            "checker_path": checker_path,
            "delta_path": delta_path,
        }
        for prefix, relative in (
            ("authority", authority_path),
            ("candidate", candidate_path),
            ("checker", checker_path),
            ("delta", delta_path),
        ):
            item = binding(relative)
            values[f"{prefix}_bytes"] = item["bytes"]
            values[f"{prefix}_sha256"] = item["sha256"]
        chapters.append(values)
        for delta in csv_rows(strict(ROOT / delta_path), delta_path):
            key = delta["source_term"].casefold()
            if key in positions:
                current = merged[positions[key]]
                require(
                    current["target_term"].casefold() == delta["target_term"].casefold(),
                    f"terminology conflict for {delta['source_term']!r}: "
                    f"{current['target_term']!r} != {delta['target_term']!r}",
                )
                current["status"] = "admitted"
            else:
                row = dict(delta)
                row["status"] = "admitted"
                positions[key] = len(merged)
                merged.append(row)

    output_glossary = encode(merged)
    manifest = {
        "schema": "o013.li-final-chapters-admission.v1",
        "authority_commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "input_glossary_sha256": sha(glossary_payload),
        "output_glossary_sha256": sha(output_glossary),
        "output_glossary_rows": len(merged),
        "chapters": chapters,
    }
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST.with_name(MANIFEST.name + ".tmp")
    require(not temporary.exists(), f"stale temporary: {temporary}")
    temporary.write_bytes(payload)
    require(temporary.read_bytes() == payload, "manifest write verification failed")
    os.replace(temporary, MANIFEST)
    print(json.dumps({"result": "PASS_WRITTEN", "path": str(MANIFEST), "bytes": len(payload)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
