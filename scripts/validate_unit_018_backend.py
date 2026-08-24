#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 018 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_018_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-018-bab-2-latihan.json"
EVIDENCE = ROOT / "qa/unit-018-evidence/backend-validation.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
STRUCTURE_QA = ROOT / "qa/unit-018-evidence/structure-and-pdf-qa.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-018-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_SECTIONS = (
    (1, 1604, 1604),
    (2, 1605, 1615),
    (3, 1616, 1616),
    (4, 1617, 1623),
    (5, 1624, 1624),
    (6, 1625, 1625),
    (7, 1626, 1626),
    (8, 1627, 1637),
    (9, 1639, 1639),
    (10, 1640, 1640),
    (11, 1641, 1642),
    (12, 1643, 1643),
    (13, 1644, 1644),
)
EXPECTED_SUBPART_KEYS = {
    "unit/bab-2-latihan/exercise/04/subpart/i",
    "unit/bab-2-latihan/exercise/04/subpart/ii",
    "unit/bab-2-latihan/exercise/04/subpart/iii",
    "unit/bab-2-latihan/exercise/08/subpart/i",
    "unit/bab-2-latihan/exercise/08/subpart/ii",
}
EXPECTED_HINT_KEYS = {"unit/bab-2-latihan/exercise/08/hint/01"}
EXPECTED_CORRECTION_KEYS = {
    "correction/o013-li-u018-cor-001",
    "correction/o013-li-u018-cor-002",
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 018 round-trip validation refused: missing canonical outputs: "
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
            "Unit 018 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 018 round-trip validation refused: " + message)


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)

    # Prove deterministic derivation from the frozen source, target, artifact,
    # glossary, and admission evidence rather than merely validating hand edits.
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation = identities(canonical_paths)
    require(
        before == after_generation,
        "deterministic regeneration changed "
        + ", ".join(sorted(key for key in before if before[key] != after_generation[key])),
    )
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
    require(after_generation == after_validation, "shared validation mutated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    require(data["dataset_stable_key"] == "dataset/unit-018/id-id", "dataset key drift")
    require(data["unit"]["stable_key"] == "unit/bab-2-latihan", "unit key drift")
    require(data["unit"]["order"] == 18, "unit order drift")
    require(data["unit"]["source_local_id"] == "chapter2.tex:1603-1645", "unit range drift")
    require(data["unit"]["translation_state"] == "visually_checked", "translation state drift")
    require(data["unit"]["admission_state"] == "admitted", "admission state drift")

    sections = sorted(data["sections"], key=lambda item: item["order"])
    require(len(sections) == 13, "expected thirteen exercise sections")
    actual_sections = tuple(
        (
            section["order"],
            section["source_binding"]["line_start"],
            section["source_binding"]["line_end"],
        )
        for section in sections
    )
    require(actual_sections == EXPECTED_SECTIONS, "exercise line bindings drift")
    require(
        tuple(section["stable_key"] for section in sections)
        == tuple(f"unit/bab-2-latihan/exercise/{ordinal:02d}" for ordinal in range(1, 14)),
        "exercise stable keys drift",
    )
    require(
        all(
            section["source_binding"]["line_start"] == section["target_binding"]["line_start"]
            and section["source_binding"]["line_end"] == section["target_binding"]["line_end"]
            for section in sections
        ),
        "source/target exercise binding mismatch",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept key")
    require(
        {key for key in concept_keys if "/subpart/" in key} == EXPECTED_SUBPART_KEYS,
        "five-subpart compatibility topology drift",
    )
    require(
        {key for key in concept_keys if "/hint/" in key} == EXPECTED_HINT_KEYS,
        "one-hint compatibility topology drift",
    )
    require(
        {key for key in concept_keys if key.startswith("correction/")} == EXPECTED_CORRECTION_KEYS,
        "declared correction topology drift",
    )
    expected_prefix_counts = {
        "surface/unit-018/reference/ordinary/": 3,
        "surface/unit-018/formula/inline/": 80,
        "surface/unit-018/formula/display-bracket/": 2,
        "surface/unit-018/formula/display-environment/": 1,
    }
    for prefix, expected in expected_prefix_counts.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key for key in concept_keys),
        "invented answer/solution entity",
    )

    require(len(data["citations"]) == 0, "unexpected citation")
    require(len(data["index_entries"]) == 0, "unexpected index entry")
    require(len(data["diagrams"]) == 1, "expected one diagram")
    diagram = data["diagrams"][0]
    require(diagram["source_format"] == "tikzcd", "diagram format drift")
    require(
        (diagram["source_binding"]["line_start"], diagram["source_binding"]["line_end"])
        == (1633, 1636),
        "diagram binding drift",
    )
    require(
        data["unit"]["surface_counts"]
        == {
            "sections": 13,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 1,
            "index_entries": 0,
        },
        "native/compatibility surface-count drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights-component inventory drift")
    require(
        {key: rights[key]["applies_to_unit"] for key in rights} == EXPECTED_RIGHTS,
        "rights applies_to_unit boundary drift",
    )
    unit_right_keys = {
        rights_id: key for key, item in rights.items() for rights_id in (item["id"],)
    }
    require(
        {unit_right_keys[item] for item in data["unit"]["rights_component_ids"]}
        == {
            "rights/principal-cc-by-4.0",
            "rights/ajbook-fragment-cc-by-sa-3.0",
            "rights/noto-fonts-ofl-1.1",
        },
        "unit rights flattening or Lanzhou applicability drift",
    )

    require(len(data["build_surfaces"]) == 1, "build surface count drift")
    build = data["build_surfaces"][0]
    require(build["artifact_binding"] == {
        "path": "artifacts/unit-018-bab-2-latihan.pdf",
        "bytes": 83578,
        "sha256": "4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c",
    }, "artifact identity drift")
    require(build["page_count"] == 4 and build["status"] == "pass", "build admission drift")
    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    require(
        set(qa_by_key)
        == {
            "qa/unit-018/admission-gate",
            "qa/unit-018/source-and-math-review",
            "qa/unit-018/terminology-control",
        },
        "QA event topology drift",
    )
    require(
        all(
            item["result"] == "pass"
            and item["translation_audit_state"] == "pass"
            and item["build_state"] == "pass"
            and item["visual_state"] == "pass"
            for item in qa_by_key.values()
        ),
        "QA pass-state drift",
    )
    require(MODEL in qa_by_key["qa/unit-018/admission-gate"]["scope"], "model provenance missing")
    require(
        all(
            token in qa_by_key["qa/unit-018/admission-gate"]["scope"]
            for token in ("O013-ADV-0049", "O013-ADV-0050")
        ),
        "adverse-ledger correction mapping missing",
    )
    term_binding = qa_by_key["qa/unit-018/terminology-control"]["witness_binding"]
    require(
        term_binding["path"] == "00_control/TERMINOLOGY.id-ID.csv"
        and term_binding["bytes"] == GLOSSARY.stat().st_size
        and term_binding["sha256"] == sha256(GLOSSARY),
        "live glossary binding drift",
    )

    report = {
        "status": "PASS",
        "unit": "unit-018-bab-2-latihan",
        "source": "chapter2.tex:1603-1645",
        "data": str(DATA.relative_to(ROOT)).replace("\\", "/"),
        "schema": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"),
        "provenance_model": MODEL,
        "rights": {
            "principal_text_and_translation": "CC BY 4.0",
            "AJbook_class_fragment": "CC BY-SA 3.0",
            "bundled_noto_fonts": "SIL OFL 1.1",
            "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
        },
        "checks": {
            "deterministic_second_generation": "PASS",
            "json_schema": "PASS",
            "uuidv5": "PASS",
            "live_bindings": "PASS",
            "exercise_subpart_hint_topology": "PASS",
            "reference_formula_diagram_topology": "PASS",
            "correction_topology": "PASS",
            "component_rights": "PASS",
            "terminology_binding": "PASS",
            "six_csv_projections": "PASS",
            "validation_mutated_outputs": False,
        },
        "counts": {
            "entities": 172,
            "concepts": len(concepts),
            "exercise_sections": 13,
            "nested_items": 5,
            "hints": 1,
            "formula_entities": 83,
            "ordinary_references": 3,
            "citations": 0,
            "diagrams": 1,
            "index_entries": 0,
            "corrections": 2,
            "answers": 0,
            "solutions": 0,
            "csv_projections": 6,
        },
        "identities": {
            key: {"bytes": value[0], "sha256": value[1]}
            for key, value in after_validation.items()
        },
        "bound_inputs": {
            str(GLOSSARY.relative_to(ROOT)).replace("\\", "/"): {
                "bytes": GLOSSARY.stat().st_size,
                "sha256": sha256(GLOSSARY),
            },
            str(STRUCTURE_QA.relative_to(ROOT)).replace("\\", "/"): {
                "bytes": STRUCTURE_QA.stat().st_size,
                "sha256": sha256(STRUCTURE_QA),
            },
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
