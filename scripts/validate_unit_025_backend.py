#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 025 backend round trip."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import generate_unit_025_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_025_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-025-bab-4-semigrup-monoid-dan-grup.json"
EVIDENCE = ROOT / "qa/unit-025-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-025-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "concept/": 20,
    "surface/unit-025/environment/": 27,
    "surface/unit-025/label/": 10,
    "surface/unit-025/reference/ordinary/": 11,
    "surface/unit-025/reference/equation/": 0,
    "surface/unit-025/item/": 24,
    "surface/unit-025/formula/inline/": 271,
    "surface/unit-025/formula/display-bracket/": 8,
    "surface/unit-025/formula/display-environment/": 1,
    "surface/unit-025/terminology-row/": 30,
    "localization/o013-li-u025-index-hierarchy-repair": 1,
    "correction/o013-li-u025-cor-001": 1,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 025 round-trip validation refused: " + message)


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 025 round-trip validation refused: missing canonical outputs; run the admission-gated generator after final reader QA:\n  - "
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
            "Unit 025 round-trip validation refused:\n"
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
    require(bindings, "no file bindings found")
    return {
        "occurrences": len(bindings),
        "full_file_occurrences": full_count,
        "line_span_occurrences": span_count,
        "unique_paths": len(paths),
        "paths": sorted(paths),
    }


def expected_concept_ownership() -> dict[int, set[str]]:
    owned = {1: set(), 2: set()}

    def assign(key: str, source_line: int) -> None:
        owned[gen.section_ordinal_for_source_line(source_line)].add(key)

    for stable_key, _, _, source_line in gen.CORE_SPECS:
        assign(stable_key, source_line)
    source_text = gen.span_text(gen.SOURCE, gen.SOURCE_START, gen.SOURCE_END)
    for ordinal, (environment, occurrence, first, _) in enumerate(
        gen.common.environment_occurrences(source_text), 1
    ):
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        assign(
            f"surface/unit-025/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            first,
        )
    for ordinal, (_, line) in enumerate(gen.common.label_occurrences(source_text), 1):
        assign(f"surface/unit-025/label/{ordinal:03d}", line)
    for ordinal, (kind, _, line) in enumerate(gen.common.reference_occurrences(source_text), 1):
        assign(f"surface/unit-025/reference/{kind}/{ordinal:03d}", line)
    for ordinal, line in enumerate(gen.common.occurrence_lines(source_text, r"\\item(?![A-Za-z])"), 1):
        assign(f"surface/unit-025/item/{ordinal:03d}", line)
    for ordinal, line, _ in gen.common.inline_formula_occurrences(source_text):
        assign(f"surface/unit-025/formula/inline/{ordinal:03d}", line)
    for ordinal, first, _, _ in gen.common.bracket_formula_occurrences(source_text):
        assign(f"surface/unit-025/formula/display-bracket/{ordinal:03d}", first)
    for ordinal, environment, first, _, _ in gen.common.environment_formula_occurrences(source_text):
        environment_slug = re.sub(
            r"[^a-z0-9._/-]+", "-", environment.casefold()
        ).strip("-")
        assign(
            f"surface/unit-025/formula/display-environment/{ordinal:03d}-{environment_slug}",
            first,
        )
    for ordinal, (_, _, source_line, _) in enumerate(gen.TERMINOLOGY_SPECS, 1):
        assign(f"surface/unit-025/terminology-row/{ordinal:03d}", source_line)
    assign("localization/o013-li-u025-index-hierarchy-repair", 52)
    assign("correction/o013-li-u025-cor-001", 115)
    return owned


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_one = identities(canonical_paths)
    require(before == after_generation_one, "first deterministic regeneration changed canonical outputs")
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_two = identities(canonical_paths)
    require(after_generation_one == after_generation_two, "second deterministic regeneration changed canonical outputs")
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
    require(data["dataset_stable_key"] == "dataset/unit-025/id-id", "dataset key drift")
    require(data["workflow"] == {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-25",
        "status": "admitted",
        "admission_state": "admitted",
        "translation_state": "visually_checked",
        "qa_state": "translation_math_backend_build_visual_pass",
    }, "workflow state drift")
    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-4-semigrup-monoid-dan-grup", "unit key drift")
    require(unit["order"] == 25, "unit order drift")
    require(unit["source_local_id"] == "chapter4.tex:1-176", "authority range drift")
    require(
        unit["source_binding"]["line_start"] == 1
        and unit["source_binding"]["line_end"] == 176
        and unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1],
        "source binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 1
        and unit["target_binding"]["line_end"] == 178
        and unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1]
        and (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"])
        == gen.TARGET_FULL,
        "target binding drift",
    )
    require(
        unit["translation_state"] == "visually_checked"
        and unit["admission_state"] == "admitted",
        "unit admission state drift",
    )

    sections = data["sections"]
    require(len(sections) == 2, "expected two natural sections")
    concept_id_to_key = {item["id"]: item["stable_key"] for item in data["concepts"]}
    prerequisite_id_to_key = {
        item["id"]: item["stable_key"] for item in data["prerequisites"]
    }
    expected_ownership = expected_concept_ownership()
    for section, spec in zip(sections, gen.SECTION_SPECS, strict=True):
        ordinal, source_first, source_last, target_first, target_last, _, _ = spec
        require(section["stable_key"] == f"unit/bab-4-semigrup-monoid-dan-grup/section/{ordinal:02d}", f"section {ordinal} stable key drift")
        require(section["order"] == ordinal, f"section {ordinal} order drift")
        require(
            section["source_binding"]["line_start"] == source_first
            and section["source_binding"]["line_end"] == source_last
            and section["target_binding"]["line_start"] == target_first
            and section["target_binding"]["line_end"] == target_last,
            f"section {ordinal} source/target boundary drift",
        )
        require(
            {concept_id_to_key[item] for item in section["concept_ids"]}
            == expected_ownership[ordinal],
            f"section {ordinal} concept ownership drift",
        )
        require(
            tuple(prerequisite_id_to_key[item] for item in section["prerequisite_ids"])
            == gen.PREREQUISITES_BY_SECTION[ordinal],
            f"section {ordinal} prerequisite ownership drift",
        )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concepts) == 404, f"expected 404 concept-compatible entities, got {len(concepts)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/exercise/" in key or "/hint/" in key or "/answer/" in key or "/solution/" in key for key in concept_keys),
        "invented exercise, hint, answer, or solution entity",
    )
    concept_by_key = {item["stable_key"]: item for item in concepts}
    expected_core = {item[0] for item in gen.CORE_SPECS}
    require(
        {key for key in concept_keys if key.startswith("concept/")} == expected_core,
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
    for ordinal, (source_term, target_term, _, _) in enumerate(gen.TERMINOLOGY_SPECS, 1):
        labels = concept_by_key[f"surface/unit-025/terminology-row/{ordinal:03d}"]["labels"]
        require(
            [item["language"] for item in labels] == ["en", "id-ID"]
            and source_term in labels[0]["text"]
            and source_term in labels[1]["text"]
            and target_term in labels[1]["text"],
            f"terminology label metadata drift: {source_term}",
        )
    correction = concept_by_key["correction/o013-li-u025-cor-001"]
    correction_text = " ".join(label["text"] for label in correction["labels"])
    require(
        [label["language"] for label in correction["labels"]] == ["en", "id-ID"],
        "correction label language metadata drift",
    )
    for token in (gen.REVIEW, "115", "118", "ambient", "Z"):
        require(token in correction_text, f"correction provenance lacks {token!r}")
    localization = concept_by_key["localization/o013-li-u025-index-hierarchy-repair"]
    localization_text = " ".join(label["text"] for label in localization["labels"])
    for token in ("target-only", "52", "60", "99", "108", "unchanged"):
        require(token in localization_text, f"index-localization provenance lacks {token!r}")

    citations = data["citations"]
    require(len(citations) == 3, "expected three native citation records")
    require(
        [(item["bib_key"], item["source_line"], item["target_line"]) for item in citations]
        == [("Har00", 24, 26), ("Bou-Alg1", 28, 30), ("Wil09", 102, 104)],
        "citation key/line topology drift",
    )
    require(
        all(
            item["bibliography_path"] == gen.BIBLIOGRAPHY
            and item["bibliography_sha256"] == gen.BIBLIOGRAPHY_ID[1]
            for item in citations
        ),
        "citation bibliography provenance drift",
    )
    require(data["diagrams"] == [], "Unit 025 must contain no diagram record")
    indexes = data["index_entries"]
    require(len(indexes) == 25, "expected 25 index entries")
    require([item["ordinal_in_unit"] for item in indexes] == list(range(1, 26)), "index ordinal drift")
    require(
        sum("/main/" in item["stable_key"] for item in indexes) == 17
        and sum("/sym1/" in item["stable_key"] for item in indexes) == 8,
        "main/sym1 index-stream census drift",
    )
    for ordinal, source_key, source_line, target_key, target_line in gen.INDEX_HIERARCHY_REPAIRS:
        item = indexes[ordinal - 1]
        require(
            item["source_key"] == source_key
            and item["target_key"] == target_key
            and item["source_binding"]["line_start"] == source_line
            and item["target_binding"]["line_start"] == target_line,
            f"index hierarchy repair drift at ordinal {ordinal}",
        )
    require(
        all(item["provenance_state"] == "source_key_preserved_target_key_localized" for item in indexes),
        "index provenance-state drift",
    )

    prerequisite_keys = {
        key for values in gen.PREREQUISITES_BY_SECTION.values() for key in values
    }
    require(
        unit["section_ids"] == [item["id"] for item in sections]
        and unit["concept_ids"] == [item["id"] for item in concepts]
        and unit["prerequisite_ids"]
        == [item["id"] for item in data["prerequisites"] if item["stable_key"] in prerequisite_keys]
        and unit["citation_ids"] == [item["id"] for item in citations]
        and unit["diagram_ids"] == []
        and unit["index_entry_ids"] == [item["id"] for item in indexes]
        and unit["build_surface_ids"] == [item["id"] for item in data["build_surfaces"]]
        and unit["qa_event_ids"] == [item["id"] for item in data["qa_events"]],
        "unit entity-ID arrays drift from emitted record order",
    )
    require(
        unit["surface_counts"]
        == {
            "sections": 2,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 3,
            "diagrams": 0,
            "index_entries": 25,
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
        principal_paths
        == {gen.SOURCE, gen.TARGET, "repo/source/LICENSE", "repo/source/ccby.png"},
        "source, target, translation-expression, or principal-rights provenance drift",
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
    require(
        build["artifact_path"] == gen.ARTIFACT and build["status"] == "pass",
        "artifact path/state drift",
    )
    require(
        build["artifact_binding"]["bytes"] == artifact_path.stat().st_size
        and build["artifact_binding"]["sha256"] == sha256(artifact_path),
        "live artifact identity drift",
    )
    require(isinstance(build["page_count"], int) and build["page_count"] >= 1, "invalid final page count")
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical integrated target absent from reader inputs")
    require(gen.CANDIDATE not in input_paths, "public reader depends on isolated candidate")
    require(gen.BIBLIOGRAPHY in input_paths, "bibliography absent from build closure")

    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    expected_qa = {
        "qa/unit-025/admission-gate",
        "qa/unit-025/source-review",
        "qa/unit-025/candidate-check",
        "qa/unit-025/canonical-integration",
        "qa/unit-025/source-correction",
        "qa/unit-025/terminology-control",
        "qa/unit-025/terminology-evidence",
        "qa/unit-025/prepromotion-evidence",
        "qa/unit-025/index-hierarchy-localization",
        "qa/unit-025/build-log",
        "qa/unit-025/all-page-visual-review",
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
    admission_scope = qa_by_key["qa/unit-025/admission-gate"]["scope"]
    for token in (
        MODEL,
        "two natural sections",
        "27 environments",
        "ten labels",
        "eleven ordinary references",
        "three citations",
        "24 list items",
        "271 inline",
        "eight bracket",
        "one align",
        "25 index",
        "thirty admitted terminology",
        "four target-only index hierarchy repairs",
        "O013-LI-U025-COR-001",
    ):
        require(token in admission_scope, f"admission scope lacks {token!r}")
    bound_witnesses = {
        "qa/unit-025/source-review": ROOT / gen.REVIEW,
        "qa/unit-025/candidate-check": ROOT / gen.CANDIDATE_GATE,
        "qa/unit-025/canonical-integration": ROOT / gen.STRUCTURE_GATE,
        "qa/unit-025/source-correction": ROOT / gen.REVIEW,
        "qa/unit-025/terminology-control": ROOT / gen.TERMINOLOGY,
        "qa/unit-025/terminology-evidence": ROOT / gen.TERMINOLOGY_AUDIT,
        "qa/unit-025/prepromotion-evidence": ROOT / gen.PREPROMOTION_AUDIT,
        "qa/unit-025/index-hierarchy-localization": ROOT / gen.STRUCTURE_GATE,
        "qa/unit-025/build-log": ROOT / gen.FINAL_LOG,
        "qa/unit-025/all-page-visual-review": ROOT / gen.VISUAL_REVIEW,
        "qa/unit-025/admission-gate": ROOT / gen.VISUAL_REVIEW,
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
        gen.SOURCE in binding_audit["paths"]
        and gen.TARGET in binding_audit["paths"],
        "authority or canonical target absent from binding audit",
    )

    report = {
        "status": "PASS",
        "unit": "unit-025-bab-4-semigrup-monoid-dan-grup",
        "authority": "chapter4.tex:1-176",
        "target": "chapter4.tex:1-178",
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
            "sections": 2,
            "environments": 27,
            "labels": 10,
            "ordinary_references": 11,
            "citations": 3,
            "items": 24,
            "inline_formulae": 271,
            "bracket_display_formulae": 8,
            "environment_display_formulae": 1,
            "formulae_total": 280,
            "index_entries": 25,
            "terminology_rows": 30,
            "corrections": 1,
            "exercises": 0,
            "hints": 0,
            "diagrams": 0,
            "csv_projections": 6,
        },
        "checks": {
            "deterministic_regeneration_one": "PASS",
            "deterministic_regeneration_two": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "authority_candidate_target_boundary": "PASS",
            "complete_tex_surface_topology": "PASS",
            "exact_concept_section_prerequisite_and_unit_ownership": "PASS",
            "citation_and_index_provenance": "PASS",
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
