#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 020 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import generate_unit_020_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_020_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-020-bab-3-keketatan-dan-teorema-koherensi.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
STRUCTURE_QA = ROOT / "qa/unit-020-evidence/structure-and-pdf-qa.json"
VISUAL_REVIEW = ROOT / "qa/UNIT_020_VISUAL_QA_20260824.md"
CORRECTION_REVIEW = ROOT / "qa/UNIT_020_SOURCE_CORRECTION_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_020_TERMINOLOGY_AUDIT_20260824.md"
EVIDENCE = ROOT / "qa/unit-020-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-020-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "surface/unit-020/label/": 3,
    "surface/unit-020/reference/ordinary/": 5,
    "surface/unit-020/reference/equation/": 0,
    "surface/unit-020/citation-occurrence/": 3,
    "surface/unit-020/item/": 10,
    "surface/unit-020/formula/inline/": 64,
    "surface/unit-020/formula/display-bracket/": 5,
    "surface/unit-020/formula/display-environment/": 0,
    "surface/unit-020/diagram-arrow/": 4,
    "surface/unit-020/diagram-node/": 5,
    "surface/unit-020/diagram-path/": 1,
    "surface/unit-020/diagram-edge/": 5,
    "surface/unit-020/terminology-row/": 4,
    "correction/o013-li-u020-cor-001": 1,
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
            "Unit 020 round-trip validation refused: missing canonical outputs; "
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
            "Unit 020 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 020 round-trip validation refused: " + message)


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
    require(data["dataset_stable_key"] == "dataset/unit-020/id-id", "dataset key drift")
    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-3-keketatan-dan-teorema-koherensi", "unit key drift")
    require(unit["order"] == 20, "unit order drift")
    require(unit["source_local_id"] == "chapter3.tex:228-306", "authority range drift")
    require(unit["source_binding"]["line_start"] == 228 and unit["source_binding"]["line_end"] == 306, "source binding drift")
    require(unit["target_binding"]["line_start"] == 227 and unit["target_binding"]["line_end"] == 305, "target binding drift")
    require(unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1], "source span hash drift")
    require(unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1], "target span hash drift")
    require(unit["translation_state"] == "visually_checked", "translation state drift")
    require(unit["admission_state"] == "admitted", "admission state drift")

    require(len(data["sections"]) == 1, "expected one contiguous section")
    section = data["sections"][0]
    require(section["stable_key"] == "unit/bab-3-keketatan-dan-teorema-koherensi/section/keketatan-dan-teorema-koherensi", "section key drift")
    require(
        section["source_binding"]["line_start"] == 228
        and section["source_binding"]["line_end"] == 306
        and section["target_binding"]["line_start"] == 227
        and section["target_binding"]["line_end"] == 305,
        "section boundary drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concept_keys) == 128, f"expected 128 concept-compatible entities, got {len(concept_keys)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key or "/hint/" in key for key in concept_keys),
        "invented answer, solution, or hint entity",
    )
    correction = next(item for item in concepts if item["stable_key"] == "correction/o013-li-u020-cor-001")
    correction_text = " ".join(label["text"] for label in correction["labels"])
    require(
        "qa/UNIT_020_SOURCE_CORRECTION_20260824.md" in correction_text
        and "299" in correction_text
        and "(F,m)" in correction_text
        and "(F,rho)" in correction_text,
        "correction evidence binding drift",
    )

    citations = data["citations"]
    require(len(citations) == 3, "expected three native bibliography-key records")
    require(
        tuple((item["bib_key"], item["source_line"], item["target_line"]) for item in citations)
        == (
            ("ML98", 246, 245),
            ("JS93", 252, 251),
            ("EGNO15", 252, 251),
        ),
        "native citation-key ordering or first-line binding drift",
    )
    require(len({item["id"] for item in citations}) == 3, "native citation IDs are not unique")

    diagrams = data["diagrams"]
    require(len(diagrams) == 2, "expected two diagrams")
    require(
        sum(item["source_format"] == "tikzcd" for item in diagrams) == 1
        and sum(item["source_format"] == "tikzpicture" for item in diagrams) == 1,
        "one tikzcd / one tikzpicture split drift",
    )
    require(
        tuple(
            (
                item["source_format"],
                item["source_occurrence_index"],
                item["source_binding"]["line_start"] - gen.SOURCE_START + 1,
                item["source_binding"]["line_end"] - gen.SOURCE_START + 1,
            )
            for item in diagrams
        )
        == gen.DIAGRAM_SPECS,
        "diagram occurrence bindings drift",
    )

    indexes = data["index_entries"]
    require(len(indexes) == 2, "expected two localized index entries")
    require(
        tuple((item["target_binding"]["line_start"], item["target_key"]) for item in indexes)
        == tuple(
            (gen.TARGET_START + line - 1, target_key)
            for _, _, line, target_key in gen.INDEX_SPECS
        ),
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
            "citations": 3,
            "diagrams": 2,
            "index_entries": 2,
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
            "qa/unit-020/admission-gate",
            "qa/unit-020/source-review",
            "qa/unit-020/math-structure-review",
            "qa/unit-020/source-correction",
            "qa/unit-020/structure-check",
            "qa/unit-020/render-replay",
            "qa/unit-020/all-page-visual-review",
            "qa/unit-020/terminology-control",
            "qa/unit-020/terminology-evidence",
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
    admission_scope = qa_by_key["qa/unit-020/admission-gate"]["scope"]
    for token in (
        MODEL,
        "O013-LI-U020-COR-001",
        "(F,m)-to-(F,rho)",
        "four tikzcd arrows",
        "five TikZ nodes",
        "five edges",
        "kekoherenan/koherensi",
    ):
        require(token in admission_scope, f"admission provenance/topology token missing: {token}")
    term_binding = qa_by_key["qa/unit-020/terminology-control"]["witness_binding"]
    require(
        term_binding["path"] == "00_control/TERMINOLOGY.id-ID.csv"
        and term_binding["bytes"] == GLOSSARY.stat().st_size
        and term_binding["sha256"] == sha256(GLOSSARY),
        "live glossary binding drift",
    )
    correction_binding = qa_by_key["qa/unit-020/source-correction"]["witness_binding"]
    require(
        correction_binding["path"] == CORRECTION_REVIEW.relative_to(ROOT).as_posix()
        and correction_binding["bytes"] == CORRECTION_REVIEW.stat().st_size
        and correction_binding["sha256"] == sha256(CORRECTION_REVIEW),
        "source-correction witness binding drift",
    )
    terminology_evidence_binding = qa_by_key["qa/unit-020/terminology-evidence"]["witness_binding"]
    require(
        terminology_evidence_binding["path"] == TERMINOLOGY_AUDIT.relative_to(ROOT).as_posix()
        and terminology_evidence_binding["bytes"] == TERMINOLOGY_AUDIT.stat().st_size
        and terminology_evidence_binding["sha256"] == sha256(TERMINOLOGY_AUDIT),
        "terminology-audit witness binding drift",
    )

    report = {
        "status": "PASS",
        "unit": "unit-020-bab-3-keketatan-dan-teorema-koherensi",
        "authority": "chapter3.tex:228-306",
        "target": "chapter3.tex:227-305",
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
            "labels": 3,
            "references": 5,
            "citation_occurrences": 3,
            "native_bibliography_records": 3,
            "items": 10,
            "inline_formulae": 64,
            "display_formulae": 5,
            "tikzcd": 1,
            "tikzpicture": 1,
            "arrows": 4,
            "nodes": 5,
            "paths": 1,
            "edges": 5,
            "index_entries": 2,
            "terminology_rows": 4,
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
            CORRECTION_REVIEW.relative_to(ROOT).as_posix(): {
                "bytes": CORRECTION_REVIEW.stat().st_size,
                "sha256": sha256(CORRECTION_REVIEW),
            },
            TERMINOLOGY_AUDIT.relative_to(ROOT).as_posix(): {
                "bytes": TERMINOLOGY_AUDIT.stat().st_size,
                "sha256": sha256(TERMINOLOGY_AUDIT),
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
