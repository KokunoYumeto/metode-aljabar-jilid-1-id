#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 024 backend round trip."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import generate_unit_024_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_024_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-024-bab-3-latihan.json"
GLOSSARY = ROOT / gen.TERMINOLOGY
STRUCTURE_QA = ROOT / gen.STRUCTURE_QA
VISUAL_REVIEW = ROOT / gen.VISUAL_REVIEW
SOURCE_REVIEW = ROOT / gen.REVIEW
MATH_REVIEW = ROOT / gen.MATH_REVIEW
TERMINOLOGY_AUDIT = ROOT / gen.TERMINOLOGY_AUDIT
EVIDENCE = ROOT / "qa/unit-024-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-024-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "surface/unit-024/environment/": 7,
    "surface/unit-024/label/": 0,
    "surface/unit-024/reference/ordinary/": 4,
    "surface/unit-024/reference/equation/": 0,
    "surface/unit-024/citation-occurrence/": 0,
    "surface/unit-024/item/": 11,
    "surface/unit-024/exercise/": 8,
    "surface/unit-024/nested-item/": 3,
    "surface/unit-024/hint/": 2,
    "surface/unit-024/formula/inline/": 69,
    "surface/unit-024/formula/display-bracket/": 6,
    "surface/unit-024/formula/display-environment/": 0,
    "surface/unit-024/diagram-arrow/": 8,
    "surface/unit-024/diagram-node/": 0,
    "surface/unit-024/diagram-coordinate/": 0,
    "surface/unit-024/diagram-draw/": 0,
    "surface/unit-024/diagram-path/": 0,
    "surface/unit-024/diagram-edge/": 0,
    "surface/unit-024/diagram-braid/": 0,
    "surface/unit-024/diagram-hline/": 0,
    "surface/unit-024/terminology-row/": 7,
    "correction/o013-li-u024-cor-001": 1,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}


def expected_concept_ownership() -> dict[int, set[str]]:
    """Independently reconstruct the exact exercise-to-concept partition."""

    owned = {ordinal: set() for ordinal in range(1, 9)}

    def assign(stable_key: str, relative_line: int) -> None:
        if relative_line in (1, 39):
            return
        ordinal = gen.exercise_for_source_line(gen.source_absolute(relative_line))
        owned[ordinal].add(stable_key)

    for stable_key, _, _, exercise in gen.CORE_SPECS:
        owned[exercise].add(stable_key)

    source_text = gen.span_text(gen.SOURCE, gen.SOURCE_START, gen.SOURCE_END)
    for ordinal, (environment, occurrence, first, _) in enumerate(
        gen.common.environment_occurrences(source_text), 1
    ):
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        assign(
            f"surface/unit-024/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            first,
        )
    for ordinal, (kind, _, line) in enumerate(gen.REFERENCES, 1):
        assign(f"surface/unit-024/reference/{kind}/{ordinal:03d}", line)
    for ordinal, line in enumerate(gen.ITEM_LINES, 1):
        assign(f"surface/unit-024/item/{ordinal:03d}", line)
    for ordinal in range(1, 9):
        owned[ordinal].add(f"surface/unit-024/exercise/{ordinal:03d}")
    for ordinal, line in enumerate(gen.NESTED_ITEM_LINES, 1):
        assign(f"surface/unit-024/nested-item/{ordinal:03d}", line)
    for ordinal, line in enumerate(gen.HINT_LINES, 1):
        assign(f"surface/unit-024/hint/{ordinal:03d}", line)
    for ordinal, line, _ in gen.common.inline_formula_occurrences(source_text):
        assign(f"surface/unit-024/formula/inline/{ordinal:03d}", line)
    for ordinal, first, _, _ in gen.common.bracket_formula_occurrences(source_text):
        assign(f"surface/unit-024/formula/display-bracket/{ordinal:03d}", first)
    for kind, pattern, _, _, _ in gen.SURFACE_SPECS:
        for ordinal, line in enumerate(gen.common.occurrence_lines(source_text, pattern), 1):
            assign(f"surface/unit-024/diagram-{kind}/{ordinal:03d}", line)
    for ordinal, (_, _, line) in enumerate(gen.TERMINOLOGY_SPECS, 1):
        assign(f"surface/unit-024/terminology-row/{ordinal:03d}", line)
    owned[4].add("correction/o013-li-u024-cor-001")
    return owned


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 024 round-trip validation refused: " + message)


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 024 round-trip validation refused: missing canonical outputs; run the admission-gated generator after final reader QA:\n  - "
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
            "Unit 024 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def audit_bindings(value: object) -> dict[str, object]:
    bindings: list[dict[str, object]] = []

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if {"path", "bytes", "sha256"}.issubset(node):
                bindings.append(node)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    full_count = 0
    span_count = 0
    paths: set[str] = set()
    for binding in bindings:
        relative = str(binding["path"])
        path = ROOT / relative
        require(path.is_file(), f"bound file missing: {relative}")
        require(
            (int(binding["bytes"]), str(binding["sha256"]))
            == (path.stat().st_size, sha256(path)),
            f"full-file binding drift: {relative}",
        )
        paths.add(relative)
        has_span = any(
            key in binding
            for key in ("line_start", "line_end", "span_sha256", "span_hash_algorithm")
        )
        if has_span:
            require(
                {"line_start", "line_end", "span_sha256", "span_hash_algorithm"}.issubset(binding),
                f"incomplete line-span binding: {relative}",
            )
            first = int(binding["line_start"])
            last = int(binding["line_end"])
            require(1 <= first <= last, f"invalid line span: {relative}:{first}-{last}")
            require(
                binding["span_hash_algorithm"] == "sha256-utf8-lines-lf-v1",
                f"unexpected span algorithm: {relative}:{first}-{last}",
            )
            require(
                sha256_bytes(gen.normalized_span(relative, first, last))
                == binding["span_sha256"],
                f"line-span binding drift: {relative}:{first}-{last}",
            )
            span_count += 1
        else:
            full_count += 1
    require(bindings, "no bindings found")
    return {
        "occurrences": len(bindings),
        "full_file_occurrences": full_count,
        "line_span_occurrences": span_count,
        "unique_paths": len(paths),
        "paths": sorted(paths),
    }


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_one = identities(canonical_paths)
    require(
        before == after_generation_one,
        "first deterministic regeneration changed "
        + ", ".join(sorted(key for key in before if before[key] != after_generation_one[key])),
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
    require(data["dataset_stable_key"] == "dataset/unit-024/id-id", "dataset key drift")
    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-3-latihan", "unit key drift")
    require(unit["order"] == 24, "unit order drift")
    require(unit["source_local_id"] == "chapter3.tex:873-911", "authority range drift")
    require(
        unit["source_binding"]["line_start"] == 873
        and unit["source_binding"]["line_end"] == 911,
        "source binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 872
        and unit["target_binding"]["line_end"] == 910,
        "target binding drift",
    )
    require(unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1], "source span hash drift")
    require(unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1], "target span hash drift")
    require(
        (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"])
        == gen.TARGET_FULL,
        "target full-file identity drift",
    )
    require(unit["translation_state"] == "visually_checked", "translation state drift")
    require(unit["admission_state"] == "admitted", "admission state drift")

    sections = data["sections"]
    require(len(sections) == 8, "expected eight ordered exercise sections")
    concept_id_to_key = {item["id"]: item["stable_key"] for item in data["concepts"]}
    prerequisite_id_to_key = {
        item["id"]: item["stable_key"] for item in data["prerequisites"]
    }
    expected_ownership = expected_concept_ownership()
    for section, spec in zip(sections, gen.EXERCISE_SPECS, strict=True):
        ordinal, source_first, source_last, target_first, target_last, _, _ = spec
        require(section["stable_key"] == f"unit/bab-3-latihan/exercise/{ordinal:02d}", f"exercise {ordinal} stable key drift")
        require(section["order"] == ordinal, f"exercise {ordinal} order drift")
        require(
            section["source_binding"]["line_start"] == source_first
            and section["source_binding"]["line_end"] == source_last
            and section["target_binding"]["line_start"] == target_first
            and section["target_binding"]["line_end"] == target_last,
            f"exercise {ordinal} source/target boundary drift",
        )
        require(
            {concept_id_to_key[item] for item in section["concept_ids"]}
            == expected_ownership[ordinal],
            f"exercise {ordinal} concept ownership drift",
        )
        require(
            tuple(prerequisite_id_to_key[item] for item in section["prerequisite_ids"])
            == gen.PREREQUISITES_BY_EXERCISE[ordinal],
            f"exercise {ordinal} prerequisite ownership drift",
        )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concept_keys) == 139, f"expected 139 concept-compatible entities, got {len(concept_keys)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key for key in concept_keys),
        "invented answer or solution entity",
    )
    concept_by_key = {item["stable_key"]: item for item in concepts}
    expected_core_keys = {item[0] for item in gen.CORE_SPECS}
    require(
        {key for key in concept_keys if key.startswith("concept/")} == expected_core_keys,
        "core concept inventory drift",
    )
    for stable_key, source_label, target_label, _ in gen.CORE_SPECS:
        require(
            concept_by_key[stable_key]["labels"]
            == [
                {"language": "zh-Hans", "text": source_label},
                {"language": "id-ID", "text": target_label},
            ],
            f"core concept labels drift: {stable_key}",
        )
    for ordinal, (source_term, target_term, _) in enumerate(gen.TERMINOLOGY_SPECS, 1):
        labels = concept_by_key[f"surface/unit-024/terminology-row/{ordinal:03d}"]["labels"]
        require(
            [item["language"] for item in labels] == ["en", "id-ID"]
            and source_term in labels[0]["text"]
            and source_term in labels[1]["text"]
            and target_term in labels[1]["text"],
            f"terminology label language/content drift: {source_term}",
        )
    correction = next(item for item in concepts if item["stable_key"] == "correction/o013-li-u024-cor-001")
    correction_text = " ".join(label["text"] for label in correction["labels"])
    require(
        [label["language"] for label in correction["labels"]] == ["en", "id-ID"],
        "correction label language metadata drift",
    )
    for token in (gen.REVIEW, "877", "876", "contoh tandingan"):
        require(token in correction_text, f"correction provenance lacks {token!r}")

    require(data["citations"] == [], "Unit 024 must contain no citation record")
    diagrams = data["diagrams"]
    require(len(diagrams) == 2, "expected two diagrams")
    require(all(item["source_format"] == "tikzcd" for item in diagrams), "diagram format drift")
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
        "diagram occurrence binding drift",
    )
    require(all(item["state"] == "audited_preserved" for item in diagrams), "diagram audit state drift")
    require(
        [item["section_id"] for item in diagrams]
        == [sections[5]["id"], sections[7]["id"]],
        "diagram section ownership drift",
    )

    indexes = data["index_entries"]
    require(len(indexes) == 1, "expected one index entry")
    index = indexes[0]
    require(
        index["source_key"] == index["target_key"] == "YBE"
        and index["source_binding"]["line_start"] == 890
        and index["source_binding"]["line_end"] == 890
        and index["target_binding"]["line_start"] == 889
        and index["target_binding"]["line_end"] == 889,
        "YBE index binding drift",
    )
    require(index["section_id"] == sections[4]["id"], "YBE index section ownership drift")
    expected_unit_prerequisites = {
        key
        for keys in gen.PREREQUISITES_BY_EXERCISE.values()
        for key in keys
    }
    require(
        unit["section_ids"] == [item["id"] for item in sections]
        and unit["concept_ids"] == [item["id"] for item in concepts]
        and unit["prerequisite_ids"]
        == [
            item["id"]
            for item in data["prerequisites"]
            if item["stable_key"] in expected_unit_prerequisites
        ]
        and unit["citation_ids"] == []
        and unit["diagram_ids"] == [item["id"] for item in diagrams]
        and unit["index_entry_ids"] == [item["id"] for item in indexes]
        and unit["build_surface_ids"]
        == [item["id"] for item in data["build_surfaces"]]
        and unit["qa_event_ids"] == [item["id"] for item in data["qa_events"]],
        "unit entity-ID arrays drift from emitted record order",
    )

    require(
        unit["surface_counts"]
        == {
            "sections": 8,
            "exercises": 8,
            "hints": 2,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 2,
            "index_entries": 1,
        },
        "shared-schema compatibility count drift",
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
        "principal-rights binding drift",
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
    artifact_path = ROOT / gen.ARTIFACT
    require(build["artifact_path"] == gen.ARTIFACT and build["status"] == "pass", "artifact path/state drift")
    require(
        build["artifact_binding"]["bytes"] == artifact_path.stat().st_size
        and build["artifact_binding"]["sha256"] == sha256(artifact_path),
        "live artifact identity drift",
    )
    require(isinstance(build["page_count"], int) and build["page_count"] >= 1, "invalid final page count")
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical integrated target absent from reader inputs")
    require(gen.CANDIDATE not in input_paths, "public reader depends on isolated candidate")

    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    expected_qa = {
        "qa/unit-024/admission-gate",
        "qa/unit-024/source-review",
        "qa/unit-024/math-structure-review",
        "qa/unit-024/source-correction",
        "qa/unit-024/structure-check",
        "qa/unit-024/render-replay",
        "qa/unit-024/all-page-visual-review",
        "qa/unit-024/terminology-control",
        "qa/unit-024/terminology-evidence",
    }
    require(set(qa_by_key) == expected_qa, "QA event topology drift")
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
    admission_scope = qa_by_key["qa/unit-024/admission-gate"]["scope"]
    for token in (
        MODEL,
        "eight exercises",
        "three nested items",
        "two hints",
        "69 inline",
        "six bracket-display",
        "two tikzcd",
        "eight arrows",
        "seven admitted terminology rows",
        "O013-LI-U024-COR-001",
    ):
        require(token in admission_scope, f"admission scope lacks {token!r}")
    bound_witnesses = {
        "qa/unit-024/source-review": SOURCE_REVIEW,
        "qa/unit-024/math-structure-review": MATH_REVIEW,
        "qa/unit-024/source-correction": SOURCE_REVIEW,
        "qa/unit-024/terminology-control": GLOSSARY,
        "qa/unit-024/terminology-evidence": TERMINOLOGY_AUDIT,
        "qa/unit-024/all-page-visual-review": VISUAL_REVIEW,
        "qa/unit-024/admission-gate": STRUCTURE_QA,
        "qa/unit-024/structure-check": ROOT / gen.STRUCTURE_GATE,
        "qa/unit-024/render-replay": ROOT / gen.RENDER_INVENTORY,
    }
    for key, path in bound_witnesses.items():
        binding = qa_by_key[key]["witness_binding"]
        require(
            binding["path"] == path.relative_to(ROOT).as_posix()
            and binding["bytes"] == path.stat().st_size
            and binding["sha256"] == sha256(path),
            f"{key} witness binding drift",
        )

    binding_audit = audit_bindings(data)
    require(binding_audit["line_span_occurrences"] >= 1, "no line-span binding audited")
    require(
        gen.SOURCE in binding_audit["paths"] and gen.TARGET in binding_audit["paths"],
        "authority or canonical target absent from binding audit",
    )

    report = {
        "status": "PASS",
        "unit": "unit-024-bab-3-latihan",
        "authority": "chapter3.tex:873-911",
        "target": "chapter3.tex:872-910",
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
            "total_entities": 5 + len(sections) + len(concepts) + len(data["prerequisites"]) + len(data["rights"]) + len(diagrams) + len(indexes) + len(data["build_surfaces"]) + len(data["qa_events"]),
            "concepts": len(concepts),
            "exercise_sections": 8,
            "exercise_entities": 8,
            "nested_items": 3,
            "hints": 2,
            "environments": 7,
            "labels": 0,
            "ordinary_references": 4,
            "equation_references": 0,
            "citations": 0,
            "items": 11,
            "inline_formulae": 69,
            "bracket_display_formulae": 6,
            "environment_display_formulae": 0,
            "tikzcd": 2,
            "arrows": 8,
            "index_entries": 1,
            "terminology_rows": 7,
            "corrections": 1,
            "csv_projections": 6,
        },
        "checks": {
            "deterministic_regeneration_one": "PASS",
            "deterministic_regeneration_two": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "authority_candidate_target_eof_boundary": "PASS",
            "exercise_hint_formula_reference_index_diagram_topology": "PASS",
            "exact_concept_section_prerequisite_and_unit_ownership": "PASS",
            "label_language_metadata": "PASS",
            "correction_provenance": "PASS",
            "component_rights": "PASS",
            "build_and_visual_bindings": "PASS",
            "terminology_binding": "PASS",
            "all_full_file_and_line_span_bindings": "PASS",
            "validation_mutated_outputs": False,
        },
        "binding_audit": binding_audit,
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
                SOURCE_REVIEW,
                MATH_REVIEW,
                TERMINOLOGY_AUDIT,
                ROOT / gen.STRUCTURE_GATE,
                ROOT / gen.RENDER_INVENTORY,
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
