#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 021 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import generate_unit_021_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_021_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-021-bab-3-struktur-kepang.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
STRUCTURE_QA = ROOT / "qa/unit-021-evidence/structure-and-pdf-qa.json"
VISUAL_REVIEW = ROOT / "qa/UNIT_021_VISUAL_QA_20260824.md"
MATH_REVIEW = ROOT / "qa/UNIT_021_MATH_STRUCTURE_AUDIT_20260824.md"
CORRECTION_REVIEW = ROOT / "qa/UNIT_021_SOURCE_CORRECTIONS_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_021_TERMINOLOGY_AUDIT_20260824.md"
EVIDENCE = ROOT / "qa/unit-021-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-021-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "surface/unit-021/label/": 9,
    "surface/unit-021/reference/ordinary/": 10,
    "surface/unit-021/reference/equation/": 3,
    "surface/unit-021/citation-occurrence/": 2,
    "surface/unit-021/formula/inline/": 144,
    "surface/unit-021/formula/display-bracket/": 6,
    "surface/unit-021/formula/display-environment/": 6,
    "surface/unit-021/diagram-arrow/": 26,
    "surface/unit-021/diagram-node/": 30,
    "surface/unit-021/diagram-coordinate/": 2,
    "surface/unit-021/diagram-draw/": 32,
    "surface/unit-021/diagram-path/": 0,
    "surface/unit-021/diagram-edge/": 15,
    "surface/unit-021/diagram-braid/": 10,
    "surface/unit-021/diagram-hline/": 3,
    "surface/unit-021/terminology-row/": 9,
    "correction/o013-li-u021-cor-001": 1,
    "correction/o013-li-u021-cor-002": 1,
    "correction/o013-li-u021-ed-001": 1,
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
            "Unit 021 round-trip validation refused: missing canonical outputs; "
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
            "Unit 021 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 021 round-trip validation refused: " + message)


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_one = identities(canonical_paths)
    require(
        before == after_generation_one,
        "first deterministic regeneration changed "
        + ", ".join(
            sorted(key for key in before if before[key] != after_generation_one[key])
        ),
    )
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_two = identities(canonical_paths)
    require(
        after_generation_one == after_generation_two,
        "second deterministic regeneration changed "
        + ", ".join(
            sorted(
                key
                for key in after_generation_one
                if after_generation_one[key] != after_generation_two[key]
            )
        ),
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
    require(after_generation_two == after_validation, "shared validation mutated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    require(data["dataset_stable_key"] == "dataset/unit-021/id-id", "dataset key drift")
    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-3-struktur-kepang", "unit key drift")
    require(unit["order"] == 21, "unit order drift")
    require(unit["source_local_id"] == "chapter3.tex:307-512", "authority range drift")
    require(
        unit["source_binding"]["line_start"] == 307
        and unit["source_binding"]["line_end"] == 512,
        "source binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 306
        and unit["target_binding"]["line_end"] == 511,
        "target binding drift",
    )
    require(unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1], "source span hash drift")
    require(unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1], "target span hash drift")
    require(
        (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"])
        == gen.TARGET_FULL,
        "target full-file admission identity drift",
    )
    require(unit["translation_state"] == "visually_checked", "translation state drift")
    require(unit["admission_state"] == "admitted", "admission state drift")

    require(len(data["sections"]) == 1, "expected one contiguous section")
    section = data["sections"][0]
    require(
        section["stable_key"] == "unit/bab-3-struktur-kepang/section/struktur-kepang",
        "section key drift",
    )
    require(
        section["source_binding"]["line_start"] == 307
        and section["source_binding"]["line_end"] == 512
        and section["target_binding"]["line_start"] == 306
        and section["target_binding"]["line_end"] == 511,
        "section boundary drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(
        len(concept_keys) == 334,
        f"expected 334 concept-compatible entities, got {len(concept_keys)}",
    )
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key or "/hint/" in key for key in concept_keys),
        "invented answer, solution, or hint entity",
    )
    correction_expectations = {
        "correction/o013-li-u021-cor-001": ("487", "486", "naturality"),
        "correction/o013-li-u021-cor-002": ("450 and 452", "449 and 451", "objects"),
        "correction/o013-li-u021-ed-001": ("508", "507", "duplicated"),
    }
    concepts_by_key = {item["stable_key"]: item for item in concepts}
    for key, tokens in correction_expectations.items():
        text = " ".join(label["text"] for label in concepts_by_key[key]["labels"])
        require(gen.CORRECTION_REVIEW in text, f"{key} evidence path drift")
        for token in tokens:
            require(token in text, f"{key} lacks {token!r}")

    citations = data["citations"]
    require(len(citations) == 1, "expected one native bibliography-key record")
    require(
        (
            citations[0]["bib_key"],
            citations[0]["source_line"],
            citations[0]["target_line"],
        )
        == ("JS93", 308, 307),
        "native citation first-occurrence binding drift",
    )

    diagrams = data["diagrams"]
    require(len(diagrams) == 23, "expected twenty-three diagrams")
    require(
        sum(item["source_format"] == "tikzcd" for item in diagrams) == 6
        and sum(item["source_format"] == "tikzpicture" for item in diagrams) == 17,
        "six-tikzcd/seventeen-tikzpicture split drift",
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
    require(
        all(item["state"] == "audited_preserved" for item in diagrams),
        "diagram audit state drift",
    )

    indexes = data["index_entries"]
    require(len(indexes) == 8, "expected eight localized index entries")
    require(
        tuple((item["target_binding"]["line_start"], item["target_key"]) for item in indexes)
        == tuple(
            (gen.TARGET_START + line - 1, target_key)
            for _, _, line, target_key in gen.INDEX_SPECS
        ),
        "localized index topology drift",
    )
    require(
        all(
            item["provenance_state"] == "source_key_preserved_target_key_localized"
            for item in indexes
        ),
        "index provenance drift",
    )

    require(
        unit["surface_counts"]
        == {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 1,
            "diagrams": 23,
            "index_entries": 8,
        },
        "native/compatibility surface-count drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights-component inventory drift")
    require(
        {key: rights[key]["applies_to_unit"] for key in rights} == EXPECTED_RIGHTS,
        "rights applicability drift",
    )
    principal_paths = {item["path"] for item in rights["rights/principal-cc-by-4.0"]["bindings"]}
    require(
        principal_paths == {gen.SOURCE, "repo/source/LICENSE", "repo/source/ccby.png"},
        "principal-rights source/license binding drift",
    )
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
    require(build["page_count"] == 9, "final reader must be the admitted nine-page layout")
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical integrated reader input is not bound")
    require(
        gen.CANDIDATE not in input_paths,
        "public reader build must not depend on the isolated review candidate",
    )

    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    require(
        set(qa_by_key)
        == {
            "qa/unit-021/admission-gate",
            "qa/unit-021/source-review",
            "qa/unit-021/math-structure-review",
            "qa/unit-021/source-corrections",
            "qa/unit-021/structure-check",
            "qa/unit-021/render-replay",
            "qa/unit-021/all-page-visual-review",
            "qa/unit-021/terminology-control",
            "qa/unit-021/terminology-evidence",
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
    admission_scope = qa_by_key["qa/unit-021/admission-gate"]["scope"]
    for token in (
        MODEL,
        "O013-LI-U021-COR-001",
        "O013-LI-U021-COR-002",
        "O013-LI-U021-ED-001",
        "twenty-six tikzcd arrows",
        "thirty TikZ nodes",
        "fifteen edge tokens",
        "ten braid commands",
        "Exactly nine terminology rows",
    ):
        require(token in admission_scope, f"admission provenance/topology token missing: {token}")

    bound_witnesses = {
        "qa/unit-021/terminology-control": GLOSSARY,
        "qa/unit-021/math-structure-review": MATH_REVIEW,
        "qa/unit-021/source-corrections": CORRECTION_REVIEW,
        "qa/unit-021/terminology-evidence": TERMINOLOGY_AUDIT,
    }
    for key, path in bound_witnesses.items():
        binding = qa_by_key[key]["witness_binding"]
        require(
            binding["path"] == path.relative_to(ROOT).as_posix()
            and binding["bytes"] == path.stat().st_size
            and binding["sha256"] == sha256(path),
            f"{key} witness binding drift",
        )

    report = {
        "status": "PASS",
        "unit": "unit-021-bab-3-struktur-kepang",
        "authority": "chapter3.tex:307-512",
        "target": "chapter3.tex:306-511",
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
            "labels": 9,
            "ordinary_references": 10,
            "equation_references": 3,
            "citation_occurrences": 2,
            "native_bibliography_records": 1,
            "items": 0,
            "inline_formulae": 144,
            "bracket_display_formulae": 6,
            "environment_display_formulae": 6,
            "tikzcd": 6,
            "tikzpicture": 17,
            "arrows": 26,
            "nodes": 30,
            "coordinates": 2,
            "draws": 32,
            "paths": 0,
            "edges": 15,
            "braids": 10,
            "hlines": 3,
            "index_entries": 8,
            "terminology_rows": 9,
            "corrections": 3,
            "csv_projections": 6,
        },
        "checks": {
            "deterministic_regeneration_one": "PASS",
            "deterministic_regeneration_two": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "source_candidate_target_line_boundary": "PASS",
            "protected_surface_topology": "PASS",
            "correction_provenance": "PASS",
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
            path.relative_to(ROOT).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (
                GLOSSARY,
                STRUCTURE_QA,
                VISUAL_REVIEW,
                MATH_REVIEW,
                CORRECTION_REVIEW,
                TERMINOLOGY_AUDIT,
            )
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
