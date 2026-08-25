#!/usr/bin/env python3
"""Regenerate and fail-closed validate the canonical Unit 026 backend."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_026_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_026_backend.py"
SHARED_VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
EVIDENCE = ROOT / "qa/unit-026-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-026-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)

EXPECTED_PREFIX_COUNTS = {
    "concept/": 23,
    "surface/unit-026/environment/": 36,
    "surface/unit-026/label/": 12,
    "surface/unit-026/reference/ordinary/": 18,
    "surface/unit-026/reference/equation/": 6,
    "surface/unit-026/item/": 12,
    "surface/unit-026/diagram-arrow/": 12,
    "surface/unit-026/protected-math-zone/": 275,
    "surface/unit-026/protected-math-zone/001-inline": 1,
    "surface/unit-026/terminology-row/": 33,
    "editorial/o013-li-u026-commented-alternative-proof": 1,
    "correction/o013-li-u026-cor-": 4,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}
EXPECTED_QA = {
    "qa/unit-026/admission-gate",
    "qa/unit-026/source-review",
    "qa/unit-026/candidate-artifact",
    "qa/unit-026/candidate-check",
    "qa/unit-026/canonical-integration",
    "qa/unit-026/source-corrections",
    "qa/unit-026/terminology-control",
    "qa/unit-026/terminology-delta",
    "qa/unit-026/terminology-evidence",
    "qa/unit-026/terminology-recommendation",
    "qa/unit-026/prepromotion-evidence",
    "qa/unit-026/build-log",
    "qa/unit-026/structure-and-pdf-qa",
    "qa/unit-026/render-hash-inventory",
    "qa/unit-026/all-page-visual-review",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 026 backend validation refused: " + message)


def run(command: list[str]) -> str:
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
            "Unit 026 backend validation refused:\n"
            + completed.stdout
            + completed.stderr
        )
    return completed.stdout


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    require(
        not missing,
        "missing generated outputs: "
        + ", ".join(path.relative_to(ROOT).as_posix() for path in missing),
    )
    return {
        path.relative_to(ROOT).as_posix(): (path.stat().st_size, sha256(path))
        for path in paths
    }


def audit_uuidv5(value: object, namespace: uuid.UUID) -> int:
    count = 0

    def visit(node: object) -> None:
        nonlocal count
        if isinstance(node, dict):
            stable_key = node.get("stable_key")
            entity_id = node.get("id")
            if isinstance(stable_key, str) and isinstance(entity_id, str):
                expected = "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))
                require(entity_id == expected, f"UUIDv5 drift for {stable_key}")
                count += 1
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    require(count > 0, "no stable UUIDv5 entities audited")
    return count


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
    paths: set[str] = set()
    full_count = 0
    span_count = 0
    for item in bindings:
        relative = str(item["path"])
        path = ROOT / relative
        require(path.is_file(), f"bound file missing: {relative}")
        require(
            (int(item["bytes"]), str(item["sha256"]))
            == (path.stat().st_size, sha256(path)),
            f"full-file binding drift: {relative}",
        )
        paths.add(relative)
        span_fields = {
            "line_start",
            "line_end",
            "span_sha256",
            "span_hash_algorithm",
        }
        if span_fields.intersection(item):
            require(span_fields.issubset(item), f"incomplete span binding: {relative}")
            first = int(item["line_start"])
            last = int(item["line_end"])
            require(1 <= first <= last, f"invalid span: {relative}:{first}-{last}")
            require(
                item["span_hash_algorithm"] == "sha256-utf8-lines-lf-v1",
                f"span algorithm drift: {relative}:{first}-{last}",
            )
            require(
                sha256_bytes(gen.normalized_span(relative, first, last))
                == item["span_sha256"],
                f"span digest drift: {relative}:{first}-{last}",
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

    # The first run is allowed to materialize the canonical projections.  The
    # second must reproduce all seven byte streams exactly.
    first_stdout = run([sys.executable, "-B", str(GENERATOR)])
    require('"concepts": 432' in first_stdout, "generator census marker drift")
    first = identities(canonical_paths)
    second_stdout = run([sys.executable, "-B", str(GENERATOR)])
    require('"concepts": 432' in second_stdout, "second generator census marker drift")
    second = identities(canonical_paths)
    require(first == second, "deterministic regeneration changed canonical outputs")

    run(
        [
            sys.executable,
            "-B",
            str(SHARED_VALIDATOR),
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
    after_shared = identities(canonical_paths)
    require(second == after_shared, "shared validator mutated generated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    namespace = uuid.UUID(
        data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:")
    )
    uuid_count = audit_uuidv5(data, namespace)
    require(
        data["dataset_stable_key"] == "dataset/unit-026/id-id"
        and data["dataset_id"]
        == "urn:uuid:"
        + str(uuid.uuid5(namespace, "dataset/unit-026/id-id")),
        "dataset identity drift",
    )
    require(
        data["workflow"]
        == {
            "responsible_task": str(
                uuid.uuid5(namespace, "task/o013-li-u026-backend")
            ),
            "updated": "2026-08-25",
            "status": "admitted",
            "admission_state": "admitted",
            "translation_state": "visually_checked",
            "qa_state": "translation_math_backend_build_visual_pass",
        },
        "workflow state or model-independent task identity drift",
    )

    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-4-homomorfisme-dan-grup-hasil-bagi", "unit key drift")
    require(unit["order"] == 26, "unit order drift")
    require(
        unit["source_local_id"]
        == "chapter4.tex:177-364; substantive record map 177-363",
        "authority description drift",
    )
    require(
        unit["source_binding"]["line_start"] == 177
        and unit["source_binding"]["line_end"] == 364
        and unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1]
        and (unit["source_binding"]["bytes"], unit["source_binding"]["sha256"])
        == gen.SOURCE_FULL,
        "authority binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 179
        and unit["target_binding"]["line_end"] == 365
        and unit["target_binding"]["span_sha256"] == gen.CANDIDATE_FULL[1]
        and (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"])
        == gen.TARGET_FULL,
        "canonical target binding drift",
    )
    require(
        unit["translation_state"] == "visually_checked"
        and unit["admission_state"] == "admitted",
        "unit admission state drift",
    )

    sections = data["sections"]
    require(len(sections) == 1, "expected one complete natural section")
    section = sections[0]
    require(
        section["stable_key"]
        == "unit/bab-4-homomorfisme-dan-grup-hasil-bagi/section/01"
        and section["order"] == 1
        and section["source_binding"]["line_start"] == 177
        and section["source_binding"]["line_end"] == 364
        and section["target_binding"]["line_start"] == 179
        and section["target_binding"]["line_end"] == 365,
        "section boundary or order drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concepts) == 432, f"expected 432 concept-compatible entities, got {len(concepts)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any(
            token in key
            for key in concept_keys
            for token in ("/exercise/", "/hint/", "/answer/", "/solution/")
        ),
        "invented exercise, hint, answer, or solution entity",
    )
    require(
        {key for key in concept_keys if key.startswith("concept/")}
        == {item[0] for item in gen.CORE_SPECS},
        "core concept inventory drift",
    )
    concept_by_key = {item["stable_key"]: item for item in concepts}
    for stable_key, source_label, target_label, _ in gen.CORE_SPECS:
        require(
            concept_by_key[stable_key]["labels"]
            == [
                {"language": "zh-Hans", "text": source_label},
                {"language": "id-ID", "text": target_label},
            ],
            f"core concept label drift: {stable_key}",
        )
    for ordinal, (source_term, target_term) in enumerate(gen.TERMINOLOGY_PAIRS, 1):
        labels = concept_by_key[
            f"surface/unit-026/terminology-row/{ordinal:03d}"
        ]["labels"]
        combined = " ".join(item["text"] for item in labels)
        require(
            [item["language"] for item in labels] == ["en", "id-ID"]
            and source_term in combined
            and target_term in combined
            and "status admitted" in combined,
            f"terminology provenance drift: {source_term}",
        )
    for correction_id, source_lines, target_lines, _, _ in gen.CORRECTIONS:
        key = f"correction/{correction_id.casefold()}"
        text = " ".join(item["text"] for item in concept_by_key[key]["labels"])
        for token in (
            correction_id,
            gen.REVIEW,
            *(str(line) for line in source_lines),
            *(str(line) for line in target_lines),
        ):
            require(token in text, f"{correction_id} provenance lacks {token!r}")

    require(
        section["concept_ids"] == [item["id"] for item in concepts]
        and unit["concept_ids"] == [item["id"] for item in concepts],
        "section or unit concept ownership drift",
    )
    prerequisite_by_id = {
        item["id"]: item["stable_key"] for item in data["prerequisites"]
    }
    require(
        tuple(prerequisite_by_id[item] for item in unit["prerequisite_ids"])
        == gen.PREREQUISITES
        and section["prerequisite_ids"] == unit["prerequisite_ids"],
        "prerequisite ownership drift",
    )

    citations = data["citations"]
    require(
        len(citations) == 1
        and (
            citations[0]["bib_key"],
            citations[0]["source_line"],
            citations[0]["target_line"],
        )
        == ("DN00", 346, 348)
        and citations[0]["bibliography_path"] == gen.BIBLIOGRAPHY
        and citations[0]["bibliography_sha256"] == gen.BIBLIOGRAPHY_ID[1],
        "DN00 citation provenance drift",
    )
    diagrams = data["diagrams"]
    require(len(diagrams) == 3, "expected three native diagram records")
    for diagram, spec in zip(diagrams, gen.DIAGRAM_SPECS, strict=True):
        _, occurrence, source_first, source_last, target_first, target_last = spec
        require(
            diagram["source_occurrence_index"] == occurrence
            and diagram["source_binding"]["line_start"] == source_first
            and diagram["source_binding"]["line_end"] == source_last
            and diagram["target_binding"]["line_start"] == target_first
            and diagram["target_binding"]["line_end"] == target_last
            and diagram["state"] == "audited_preserved",
            f"diagram {occurrence} topology drift",
        )
    indexes = data["index_entries"]
    require(len(indexes) == 10, "expected ten native index records")
    require(
        Counter("sym1" if "/sym1/" in item["stable_key"] else "main" for item in indexes)
        == Counter({"main": 9, "sym1": 1}),
        "main/sym1 index census drift",
    )
    require(
        [item["ordinal_in_unit"] for item in indexes] == list(range(1, 11))
        and all(
            item["provenance_state"]
            == "source_key_preserved_target_key_localized"
            for item in indexes
        ),
        "index order or provenance-state drift",
    )

    require(
        unit["section_ids"] == [section["id"]]
        and unit["citation_ids"] == [item["id"] for item in citations]
        and unit["diagram_ids"] == [item["id"] for item in diagrams]
        and unit["index_entry_ids"] == [item["id"] for item in indexes]
        and unit["build_surface_ids"]
        == [item["id"] for item in data["build_surfaces"]]
        and unit["qa_event_ids"] == [item["id"] for item in data["qa_events"]],
        "unit entity-ID arrays drift from emitted order",
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
            "diagrams": 3,
            "index_entries": 10,
        },
        "surface compatibility census drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights inventory drift")
    require(
        {key: item["applies_to_unit"] for key, item in rights.items()}
        == EXPECTED_RIGHTS,
        "rights applicability drift",
    )
    principal_paths = {
        item["path"]
        for item in rights["rights/principal-cc-by-4.0"]["bindings"]
    }
    require(
        principal_paths
        == {
            gen.SOURCE,
            gen.CANDIDATE,
            gen.TARGET,
            "repo/source/LICENSE",
            "repo/source/ccby.png",
        },
        "authority, candidate, target, or principal-rights binding drift",
    )
    rights_key_by_id = {item["id"]: key for key, item in rights.items()}
    require(
        {rights_key_by_id[item] for item in unit["rights_component_ids"]}
        == {
            "rights/principal-cc-by-4.0",
            "rights/ajbook-fragment-cc-by-sa-3.0",
            "rights/noto-fonts-ofl-1.1",
        },
        "unit rights flattening or Lanzhou applicability drift",
    )

    require(len(data["build_surfaces"]) == 1, "build-surface count drift")
    build = data["build_surfaces"][0]
    artifact = ROOT / gen.ARTIFACT
    require(
        build["artifact_path"] == gen.ARTIFACT
        and build["status"] == "pass"
        and build["page_count"] == 9
        and (build["artifact_binding"]["bytes"], build["artifact_binding"]["sha256"])
        == gen.ARTIFACT_ID
        and (artifact.stat().st_size, sha256(artifact)) == gen.ARTIFACT_ID,
        "final reader artifact or page binding drift",
    )
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical target absent from build closure")
    require(gen.CANDIDATE not in input_paths, "reader build depends on isolated candidate")
    require(gen.SOURCE not in input_paths, "reader build depends on authority source")
    require(gen.BIBLIOGRAPHY in input_paths, "bibliography absent from build closure")

    qa = {item["stable_key"]: item for item in data["qa_events"]}
    require(set(qa) == EXPECTED_QA, "QA event topology drift")
    require(
        all(
            item["result"] == "pass"
            and item["translation_audit_state"] == "pass"
            and item["build_state"] == "pass"
            and item["visual_state"] == "pass"
            for item in qa.values()
        ),
        "QA pass-state drift",
    )
    admission_scope = qa["qa/unit-026/admission-gate"]["scope"]
    for token in (
        MODEL,
        "177-364",
        "187-record",
        "36 textual environment pairs",
        "35 active pairs",
        "12 labels",
        "18 ordinary",
        "six equation",
        "DN00",
        "12 list items",
        "275 protected mathematical zones",
        "ten indexes",
        "three tikzcd diagrams",
        "12 arrows",
        "33 admitted terminology rows",
        "four declared corrections",
        "no exercises, hints, answers, or solutions",
    ):
        require(token in admission_scope, f"admission scope lacks {token!r}")
    witness_by_qa = {
        "qa/unit-026/admission-gate": gen.VISUAL_REVIEW,
        "qa/unit-026/source-review": gen.REVIEW,
        "qa/unit-026/candidate-artifact": gen.CANDIDATE,
        "qa/unit-026/candidate-check": gen.CANDIDATE_GATE,
        "qa/unit-026/canonical-integration": gen.STRUCTURE_GATE,
        "qa/unit-026/source-corrections": gen.REVIEW,
        "qa/unit-026/terminology-control": gen.TERMINOLOGY,
        "qa/unit-026/terminology-delta": gen.TERMINOLOGY_DELTA,
        "qa/unit-026/terminology-evidence": gen.TERMINOLOGY_AUDIT,
        "qa/unit-026/terminology-recommendation": gen.TERMINOLOGY_RECOMMENDATION,
        "qa/unit-026/prepromotion-evidence": gen.PREPROMOTION_AUDIT,
        "qa/unit-026/build-log": gen.FINAL_LOG,
        "qa/unit-026/structure-and-pdf-qa": gen.STRUCTURE_PDF_QA,
        "qa/unit-026/render-hash-inventory": gen.RENDER_HASH_INVENTORY,
        "qa/unit-026/all-page-visual-review": gen.VISUAL_REVIEW,
    }
    for key, relative in witness_by_qa.items():
        witness = ROOT / relative
        binding = qa[key]["witness_binding"]
        require(
            binding["path"] == relative
            and (binding["bytes"], binding["sha256"])
            == (witness.stat().st_size, sha256(witness)),
            f"QA witness binding drift: {key}",
        )

    binding_audit = audit_bindings(data)
    require(binding_audit["line_span_occurrences"] > 0, "no line-span binding audited")
    for required_path in (
        gen.SOURCE,
        gen.CANDIDATE,
        gen.TARGET,
        gen.ARTIFACT,
        gen.VISUAL_REVIEW,
        gen.STRUCTURE_PDF_QA,
        gen.RENDER_HASH_INVENTORY,
    ):
        require(
            required_path in binding_audit["paths"],
            f"required provenance path absent: {required_path}",
        )

    report = {
        "status": "PASS",
        "unit": "unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi",
        "authority": "chapter4.tex:177-364 (blank line 364 omitted from 177-363 mapping)",
        "target": "chapter4.tex:179-365",
        "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "provenance_model": MODEL,
        "artifact": {
            "path": gen.ARTIFACT,
            "pages": 9,
            "bytes": gen.ARTIFACT_ID[0],
            "sha256": gen.ARTIFACT_ID[1],
        },
        "counts": {
            "sections": 1,
            "concepts": 432,
            "textual_environment_markers": 72,
            "textual_environment_pairs": 36,
            "active_environment_pairs": 35,
            "commented_environment_pairs": 1,
            "labels": 12,
            "ordinary_references": 18,
            "equation_references": 6,
            "citations": 1,
            "list_items": 12,
            "protected_math_zones": 275,
            "diagrams": 3,
            "diagram_arrows": 12,
            "index_entries": 10,
            "terminology_rows": 33,
            "corrections": 4,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "csv_projections": 6,
            "uuidv5_entities_audited": uuid_count,
        },
        "checks": {
            "deterministic_regeneration_one": "PASS",
            "deterministic_regeneration_two": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "exact_authority_candidate_target_boundary": "PASS",
            "complete_tex_surface_topology": "PASS",
            "native_citation_diagram_and_index_provenance": "PASS",
            "four_declared_corrections": "PASS",
            "no_invented_exercise_or_solution_surfaces": "PASS",
            "component_rights_and_non_endorsement": "PASS",
            "build_and_all_page_visual_bindings": "PASS",
            "terminology_binding": "PASS",
            "all_full_file_and_line_span_bindings": "PASS",
            "validation_mutated_outputs": False,
        },
        "binding_audit": binding_audit,
        "identities": {
            key: {"bytes": value[0], "sha256": value[1]}
            for key, value in after_shared.items()
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
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
