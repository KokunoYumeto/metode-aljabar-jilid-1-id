#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 019 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import generate_unit_019_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_019_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-019-bab-3-definisi-dasar.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
STRUCTURE_QA = ROOT / "qa/unit-019-evidence/structure-and-pdf-qa.json"
VISUAL_REVIEW = ROOT / "qa/UNIT_019_VISUAL_QA_20260824.md"
EVIDENCE = ROOT / "qa/unit-019-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-019-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "surface/unit-019/label/": 16,
    "surface/unit-019/reference/ordinary/": 15,
    "surface/unit-019/reference/equation/": 13,
    "surface/unit-019/citation-occurrence/": 4,
    "surface/unit-019/item/": 13,
    "surface/unit-019/formula/inline/": 167,
    "surface/unit-019/formula/display-bracket/": 9,
    "surface/unit-019/formula/display-environment/": 8,
    "surface/unit-019/diagram-arrow/": 75,
    "surface/unit-019/diagram-node/": 11,
    "surface/unit-019/diagram-path/": 1,
    "surface/unit-019/terminology-row/": 15,
    "correction/o013-li-u019-cor-001": 1,
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
            "Unit 019 round-trip validation refused: missing canonical outputs; "
            "run the admission-gated generator after final QA:\n  - "
            + "\n  - ".join(path.relative_to(ROOT).as_posix() for path in missing)
        )
    return {
        path.relative_to(ROOT).as_posix(): (path.stat().st_size, sha256(path))
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
            "Unit 019 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 019 round-trip validation refused: " + message)


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)
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
    require(data["dataset_stable_key"] == "dataset/unit-019/id-id", "dataset key drift")
    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-3-definisi-dasar", "unit key drift")
    require(unit["order"] == 19, "unit order drift")
    require(unit["source_local_id"] == "chapter3.tex:1-227", "authority range drift")
    require(unit["source_binding"]["line_start"] == 1 and unit["source_binding"]["line_end"] == 227, "source binding drift")
    require(unit["target_binding"]["line_start"] == 1 and unit["target_binding"]["line_end"] == 226, "target binding drift")
    require(unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1], "source span hash drift")
    require(unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1], "target span hash drift")
    require(unit["translation_state"] == "visually_checked", "translation state drift")
    require(unit["admission_state"] == "admitted", "admission state drift")

    require(len(data["sections"]) == 1, "expected one contiguous section")
    section = data["sections"][0]
    require(section["stable_key"] == "unit/bab-3-definisi-dasar/section/kategori-monoidal-dan-definisi-dasar", "section key drift")
    require(section["source_binding"]["line_end"] == 227 and section["target_binding"]["line_end"] == 226, "section boundary drift")

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concept_keys) == 369, f"expected 369 concept-compatible entities, got {len(concept_keys)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key or "/hint/" in key for key in concept_keys),
        "invented answer, solution, or hint entity",
    )
    correction = next(item for item in concepts if item["stable_key"] == "correction/o013-li-u019-cor-001")
    correction_text = " ".join(label["text"] for label in correction["labels"])
    require("O013-ADV-0051" in correction_text and "155" in correction_text, "correction/adverse binding drift")

    citations = data["citations"]
    require(len(citations) == 2, "expected two native bibliography-key records")
    require(
        tuple((item["bib_key"], item["source_line"], item["target_line"]) for item in citations)
        == (("EGNO15", 18, 18), ("ML98", 174, 174)),
        "native citation-key ordering or first-line binding drift",
    )
    require(len({item["id"] for item in citations}) == 2, "native citation IDs are not unique")

    diagrams = data["diagrams"]
    require(len(diagrams) == 18, "expected eighteen diagrams")
    require(
        sum(item["source_format"] == "tikzcd" for item in diagrams) == 15
        and sum(item["source_format"] == "tikzpicture" for item in diagrams) == 3,
        "15 tikzcd / 3 tikzpicture split drift",
    )
    require(
        tuple(
            (
                item["source_format"],
                item["source_occurrence_index"],
                item["source_binding"]["line_start"],
                item["source_binding"]["line_end"],
            )
            for item in diagrams
        )
        == gen.DIAGRAM_SPECS,
        "diagram occurrence bindings drift",
    )

    indexes = data["index_entries"]
    require(len(indexes) == 11, "expected eleven localized index entries")
    require(
        tuple((item["target_binding"]["line_start"], item["target_key"]) for item in indexes)
        == tuple((line, target_key) for _, _, line, target_key in gen.INDEX_SPECS),
        "localized index topology drift",
    )
    require(all(item["provenance_state"] == "source_key_preserved_target_key_localized" for item in indexes), "index provenance drift")

    require(
        unit["surface_counts"]
        == {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 2,
            "diagrams": 18,
            "index_entries": 11,
        },
        "native/compatibility surface-count drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights-component inventory drift")
    require({key: rights[key]["applies_to_unit"] for key in rights} == EXPECTED_RIGHTS, "rights applicability drift")
    rights_id_to_key = {item["id"]: key for key, item in rights.items()}
    require(
        {rights_id_to_key[item] for item in unit["rights_component_ids"]}
        == {
            "rights/principal-cc-by-4.0",
            "rights/ajbook-fragment-cc-by-sa-3.0",
            "rights/noto-fonts-ofl-1.1",
        },
        "unit rights flattening or Lanzhou applicability drift",
    )

    require(len(data["build_surfaces"]) == 1, "build-surface count drift")
    build = data["build_surfaces"][0]
    require(build["artifact_path"] == gen.ARTIFACT and build["status"] == "pass", "artifact path/state drift")
    artifact_path = ROOT / gen.ARTIFACT
    require(
        build["artifact_binding"]["bytes"] == artifact_path.stat().st_size
        and build["artifact_binding"]["sha256"] == sha256(artifact_path),
        "live artifact identity drift",
    )
    require(build["page_count"] >= 1, "invalid reader page count")

    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    require(
        set(qa_by_key)
        == {
            "qa/unit-019/admission-gate",
            "qa/unit-019/source-review",
            "qa/unit-019/math-structure-review",
            "qa/unit-019/structure-check",
            "qa/unit-019/render-replay",
            "qa/unit-019/all-page-visual-review",
            "qa/unit-019/terminology-control",
            "qa/unit-019/terminology-evidence",
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
    admission_scope = qa_by_key["qa/unit-019/admission-gate"]["scope"]
    for token in (MODEL, "O013-LI-U019-COR-001", "O013-ADV-0051", "75 arrows", "11 explicit nodes"):
        require(token in admission_scope, f"admission provenance/topology token missing: {token}")
    term_binding = qa_by_key["qa/unit-019/terminology-control"]["witness_binding"]
    require(
        term_binding["path"] == "00_control/TERMINOLOGY.id-ID.csv"
        and term_binding["bytes"] == GLOSSARY.stat().st_size
        and term_binding["sha256"] == sha256(GLOSSARY),
        "live glossary binding drift",
    )

    report = {
        "status": "PASS",
        "unit": "unit-019-bab-3-definisi-dasar",
        "authority": "chapter3.tex:1-227",
        "target": "chapter3.tex:1-226",
        "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "provenance_model": MODEL,
        "artifact": {
            "path": gen.ARTIFACT,
            "pages": build["page_count"],
            "bytes": artifact_path.stat().st_size,
            "sha256": sha256(artifact_path),
        },
        "counts": {
            "concepts": len(concepts),
            "labels": 16,
            "references": 28,
            "citation_occurrences": 4,
            "native_bibliography_records": 2,
            "items": 13,
            "inline_formulae": 167,
            "display_formulae": 17,
            "tikzcd": 15,
            "tikzpicture": 3,
            "arrows": 75,
            "nodes": 11,
            "paths": 1,
            "index_entries": 11,
            "terminology_rows": 15,
            "corrections": 1,
            "csv_projections": 6,
        },
        "checks": {
            "deterministic_regeneration": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "source_target_line_boundary": "PASS",
            "protected_surface_topology": "PASS",
            "component_rights": "PASS",
            "build_and_visual_bindings": "PASS",
            "terminology_binding": "PASS",
            "validation_mutated_outputs": False,
        },
        "identities": {
            key: {"bytes": value[0], "sha256": value[1]}
            for key, value in after_validation.items()
        },
        "bound_inputs": {
            GLOSSARY.relative_to(ROOT).as_posix(): {
                "bytes": GLOSSARY.stat().st_size,
                "sha256": sha256(GLOSSARY),
            },
            STRUCTURE_QA.relative_to(ROOT).as_posix(): {
                "bytes": STRUCTURE_QA.stat().st_size,
                "sha256": sha256(STRUCTURE_QA),
            },
            VISUAL_REVIEW.relative_to(ROOT).as_posix(): {
                "bytes": VISUAL_REVIEW.stat().st_size,
                "sha256": sha256(VISUAL_REVIEW),
            },
        },
        "tools": {
            GENERATOR.relative_to(ROOT).as_posix(): {
                "bytes": GENERATOR.stat().st_size,
                "sha256": sha256(GENERATOR),
            },
            Path(__file__).resolve().relative_to(ROOT).as_posix(): {
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
