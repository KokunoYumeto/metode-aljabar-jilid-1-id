#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 016 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_016_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-016-bab-2-limit.json"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-016-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 016 round-trip validation refused: missing canonical outputs: "
            + ", ".join(str(path.relative_to(ROOT)) for path in missing)
        )
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): (path.stat().st_size, sha256(path))
        for path in paths
    }


def run(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(
            "Unit 016 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)

    # Regeneration proves that the frozen inputs map deterministically to the
    # same canonical JSON and projections rather than merely validating a
    # hand-edited record.
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation = identities(canonical_paths)
    if before != after_generation:
        changed = sorted(key for key in before if before[key] != after_generation[key])
        raise SystemExit(
            "Unit 016 round-trip validation refused: deterministic regeneration changed "
            + ", ".join(changed)
        )

    # The shared validator applies the JSON Schema, validates every UUIDv5,
    # binding, reference and count, then compares all six CSV projections
    # byte-for-byte without rewriting them.
    run(
        [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "--lane-root",
            str(ROOT),
            "--data",
            str(DATA),
            "--schema",
            str(SCHEMA),
            "--csv-dir",
            str(ROOT / "backend/csv"),
        ]
    )
    after_validation = identities(canonical_paths)
    if after_generation != after_validation:
        raise SystemExit("Unit 016 round-trip validation refused: validation mutated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    concept_keys = tuple(item["stable_key"] for item in data["concepts"])
    expected_prefix_counts = {
        "surface/unit-016/label/": 17,
        "surface/unit-016/reference/ordinary/": 21,
        "surface/unit-016/reference/equation/": 7,
        "surface/unit-016/formula/inline/": 287,
        "surface/unit-016/formula/display-bracket/": 12,
        "surface/unit-016/formula/display-environment/": 14,
        "correction/o013-li-u016-cor-": 3,
    }
    for prefix, expected in expected_prefix_counts.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        if actual != expected:
            raise SystemExit(
                f"Unit 016 round-trip validation refused: {prefix} expected {expected}, got {actual}"
            )
    if data["unit"]["order"] != 16 or data["unit"]["source_local_id"] != "chapter2.tex:1111-1405":
        raise SystemExit("Unit 016 round-trip validation refused: unit identity/range drift")
    if data["unit"]["surface_counts"] != {
        "sections": 1,
        "exercises": 0,
        "hints": 0,
        "answers": 0,
        "solutions": 0,
        "citations": 1,
        "diagrams": 23,
        "index_entries": 13,
    }:
        raise SystemExit("Unit 016 round-trip validation refused: native surface-count drift")
    if len(data["citations"]) != 1 or len(data["diagrams"]) != 23 or len(data["index_entries"]) != 13:
        raise SystemExit("Unit 016 round-trip validation refused: native surface-array drift")

    print(
        json.dumps(
            {
                "status": "pass",
                "data": str(DATA.relative_to(ROOT)).replace("\\", "/"),
                "schema": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"),
                "concepts": len(data["concepts"]),
                "formula_entities": 313,
                "labels": 17,
                "ordinary_references": 21,
                "equation_references": 7,
                "citations": 1,
                "diagrams": 23,
                "index_entries": 13,
                "corrections": 3,
                "csv_projections": 6,
                "identities": {
                    key: {"bytes": value[0], "sha256": value[1]}
                    for key, value in after_validation.items()
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
