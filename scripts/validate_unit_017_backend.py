#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 017 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_017_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-017-bab-2-kelengkapan.json"
EVIDENCE = ROOT / "qa/unit-017-evidence/backend-validation.json"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-017-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 017 round-trip validation refused: missing canonical outputs: "
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
            "Unit 017 round-trip validation refused:\n"
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
            "Unit 017 round-trip validation refused: deterministic regeneration changed "
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
        raise SystemExit("Unit 017 round-trip validation refused: validation mutated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    concept_keys = tuple(item["stable_key"] for item in data["concepts"])
    expected_prefix_counts = {
        "surface/unit-017/label/": 11,
        "surface/unit-017/reference/ordinary/": 35,
        "surface/unit-017/reference/equation/": 5,
        "surface/unit-017/formula/inline/": 199,
        "surface/unit-017/formula/display-bracket/": 4,
        "surface/unit-017/formula/display-environment/": 6,
        "correction/o013-li-u017-cor-": 6,
    }
    for prefix, expected in expected_prefix_counts.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        if actual != expected:
            raise SystemExit(
                f"Unit 017 round-trip validation refused: {prefix} expected {expected}, got {actual}"
            )
    if data["unit"]["order"] != 17 or data["unit"]["source_local_id"] != "chapter2.tex:1406-1602":
        raise SystemExit("Unit 017 round-trip validation refused: unit identity/range drift")
    if data["unit"]["surface_counts"] != {
        "sections": 1,
        "exercises": 0,
        "hints": 0,
        "answers": 0,
        "solutions": 0,
        "citations": 0,
        "diagrams": 9,
        "index_entries": 9,
    }:
        raise SystemExit("Unit 017 round-trip validation refused: native surface-count drift")
    if len(data["citations"]) != 0 or len(data["diagrams"]) != 9 or len(data["index_entries"]) != 9:
        raise SystemExit("Unit 017 round-trip validation refused: native surface-array drift")

    report = {
        "status": "PASS",
        "unit": "unit-017-bab-2-kelengkapan",
        "source": "chapter2.tex:1406-1602",
        "data": str(DATA.relative_to(ROOT)).replace("\\", "/"),
        "schema": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"),
        "provenance_model": "OpenAI Codex gpt-5.6-sol, Ultra",
        "rights": "CC BY 4.0",
        "checks": {
            "deterministic_second_generation": "PASS",
            "json_schema": "PASS",
            "uuidv5": "PASS",
            "live_bindings": "PASS",
            "references_and_counts": "PASS",
            "six_csv_projections": "PASS",
            "validation_mutated_outputs": False,
        },
        "counts": {
            "concepts": len(data["concepts"]),
            "formula_entities": 209,
            "labels": 11,
            "ordinary_references": 35,
            "equation_references": 5,
            "citations": 0,
            "diagrams": 9,
            "index_entries": 9,
            "corrections": 6,
            "csv_projections": 6,
        },
        "identities": {
            key: {"bytes": value[0], "sha256": value[1]}
            for key, value in after_validation.items()
        },
        "tools": {
            str(GENERATOR.relative_to(ROOT)).replace("\\", "/"): {
                "bytes": GENERATOR.stat().st_size,
                "sha256": sha256(GENERATOR),
            },
            str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"): {
                "bytes": Path(__file__).resolve().stat().st_size,
                "sha256": sha256(Path(__file__).resolve()),
            },
        },
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
