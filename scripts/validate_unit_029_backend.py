#!/usr/bin/env python3
"""Regenerate and fail-closed validate the canonical Unit 029 backend."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_029_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_029_backend.py"
SHARED_VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-029-bab-4-teorema-sylow.json"
EVIDENCE = ROOT / "qa/unit-029-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-029-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)

EXPECTED_PREFIX_COUNTS = {
    "concept/": 13,
    "surface/unit-029/environment/": 25,
    "surface/unit-029/label/": 6,
    "surface/unit-029/reference/ordinary/": 16,
    "surface/unit-029/item/": 2,
    "surface/unit-029/protected-math-zone/": 211,
    "surface/unit-029/terminology-row/": 5,
    "protected-text-localization/o013-li-u029-loc-": 1,
    "provenance/o013-li-u029-production": 1,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}
EXPECTED_QA = {
    "qa/unit-029/admission-gate",
    "qa/unit-029/source-review",
    "qa/unit-029/candidate-artifact",
    "qa/unit-029/candidate-check",
    "qa/unit-029/canonical-integration",
    "qa/unit-029/source-corrections",
    "qa/unit-029/protected-text-localizations",
    "qa/unit-029/terminology-control",
    "qa/unit-029/terminology-delta",
    "qa/unit-029/terminology-evidence",
    "qa/unit-029/prepromotion-evidence",
    "qa/unit-029/citation-closure",
    "qa/unit-029/build-log",
    "qa/unit-029/visual-preflight",
    "qa/unit-029/structure-and-pdf-qa",
    "qa/unit-029/render-hash-inventory",
    "qa/unit-029/all-page-visual-review",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 029 backend validation refused: " + message)


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
            "Unit 029 backend validation refused:\n"
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
        span_fields = {"line_start", "line_end", "span_sha256", "span_hash_algorithm"}
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
                sha256_bytes(gen.normalized_span(relative, first, last)) == item["span_sha256"],
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

    first_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in ('"concepts": 280', '"diagrams": 0', '"protected_math_zones": 211', '"citations": 1'):
        require(marker in first_stdout, f"generator census marker drift: {marker}")
    first = identities(canonical_paths)
    second_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in ('"concepts": 280', '"diagrams": 0', '"protected_math_zones": 211', '"citations": 1'):
        require(marker in second_stdout, f"second generator census marker drift: {marker}")
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

    all_generated = b"\n".join(path.read_bytes() for path in canonical_paths)
    require(b"unit-026" not in all_generated, "stale Unit 026 identifier leaked into Unit 029 outputs")
    require(b"u026" not in all_generated.lower(), "stale U026 identifier leaked into Unit 029 outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uuid_count = audit_uuidv5(data, namespace)
    require(
        data["dataset_stable_key"] == "dataset/unit-029/id-id"
        and data["dataset_id"] == "urn:uuid:" + str(uuid.uuid5(namespace, "dataset/unit-029/id-id")),
        "dataset identity drift",
    )
    require(
        data["workflow"]
        == {
            "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u029-backend")),
            "updated": "2026-08-26",
            "status": "admitted",
            "admission_state": "admitted",
            "translation_state": "visually_checked",
            "qa_state": "translation_math_backend_build_visual_pass",
        },
        "workflow state drift",
    )

    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-4-teorema-sylow", "unit key drift")
    require(unit["order"] == 29, "unit order drift")
    require(
        unit["source_local_id"] == "chapter4.tex:666-795; substantive authority map 666-794 to target 665-793",
        "authority description drift",
    )
    require(
        unit["source_binding"]["line_start"] == 666
        and unit["source_binding"]["line_end"] == 795
        and unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1]
        and (unit["source_binding"]["bytes"], unit["source_binding"]["sha256"]) == gen.SOURCE_FULL,
        "authority binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 665
        and unit["target_binding"]["line_end"] == 793
        and unit["target_binding"]["span_sha256"] == gen.CANDIDATE_FULL[1]
        and (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"]) == gen.TARGET_FULL,
        "canonical target binding drift",
    )
    require(
        unit["translation_state"] == "visually_checked" and unit["admission_state"] == "admitted",
        "unit admission state drift",
    )

    sections = data["sections"]
    require(len(sections) == 1, "expected one complete natural section")
    section = sections[0]
    require(
        section["stable_key"] == "unit/bab-4-teorema-sylow/section/01"
        and section["order"] == 1
        and section["source_binding"]["line_start"] == 666
        and section["source_binding"]["line_end"] == 795
        and section["target_binding"]["line_start"] == 665
        and section["target_binding"]["line_end"] == 793,
        "section boundary or order drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concepts) == 280, f"expected 280 concept-compatible entities, got {len(concepts)}")
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any(token in key for key in concept_keys for token in ("/exercise/", "/hint/", "/answer/", "/solution/")),
        "invented exercise, hint, answer, or solution entity",
    )
    require(
        {key for key in concept_keys if key.startswith("concept/")} == {item[0] for item in gen.CORE_SPECS},
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
        labels = concept_by_key[f"surface/unit-029/terminology-row/{ordinal:03d}"]["labels"]
        combined = " ".join(item["text"] for item in labels)
        require(
            [item["language"] for item in labels] == ["en", "id-ID"]
            and source_term in combined
            and target_term in combined
            and "status admitted" in combined,
            f"terminology provenance drift: {source_term}",
        )
    for correction_id, source_lines, target_lines, _, _ in gen.SOURCE_CORRECTIONS:
        key = f"correction/{correction_id.casefold()}"
        text = " ".join(item["text"] for item in concept_by_key[key]["labels"])
        for token in (correction_id, gen.REVIEW, *(str(line) for line in source_lines), *(str(line) for line in target_lines)):
            require(token in text, f"{correction_id} provenance lacks {token!r}")
    for localization_id, source_line, target_line, source_text, target_text in gen.PROTECTED_TEXT_LOCALIZATIONS:
        key = f"protected-text-localization/{localization_id.casefold()}"
        labels = concept_by_key[key]["labels"]
        combined = " ".join(item["text"] for item in labels)
        for token in (localization_id, str(source_line), str(target_line), source_text, target_text, gen.REVIEW):
            require(token in combined, f"{localization_id} provenance lacks {token!r}")
    provenance_text = " ".join(item["text"] for item in concept_by_key["provenance/o013-li-u029-production"]["labels"])
    require(MODEL in provenance_text and "user's instruction" in provenance_text, "production provenance drift")

    require(
        section["concept_ids"] == [item["id"] for item in concepts]
        and unit["concept_ids"] == [item["id"] for item in concepts],
        "section or unit concept ownership drift",
    )
    prerequisite_by_id = {item["id"]: item["stable_key"] for item in data["prerequisites"]}
    require(
        tuple(prerequisite_by_id[item] for item in unit["prerequisite_ids"]) == gen.PREREQUISITES
        and section["prerequisite_ids"] == unit["prerequisite_ids"],
        "prerequisite ownership drift",
    )
    internal_prerequisite = next(
        item for item in data["prerequisites"]
        if item["stable_key"] == "prerequisite/group-homomorphisms-kernels-and-quotients"
    )
    require(
        internal_prerequisite["source_evidence"] == {"path": gen.SOURCE, "line_start": 177, "line_end": 364},
        "Unit 026 prerequisite evidence drift",
    )
    group_action_prerequisite = next(
        item for item in data["prerequisites"]
        if item["stable_key"] == "prerequisite/group-actions-orbits-and-stabilizers"
    )
    require(
        group_action_prerequisite["source_evidence"] == {"path": gen.SOURCE, "line_start": 518, "line_end": 665},
        "Unit 028 prerequisite evidence drift",
    )

    citations = data["citations"]
    require(len(citations) == 1, "expected one native citation record")
    require(
        [item["bib_key"] for item in citations] == ["Lang02"]
        and [item["source_line"] for item in citations] == [743]
        and [item["target_line"] for item in citations] == [742]
        and all(item["bibliography_path"] == gen.BIBLIOGRAPHY for item in citations)
        and all(item["bibliography_sha256"] == gen.BIBLIOGRAPHY_ID[1] for item in citations)
        and unit["citation_ids"] == [item["id"] for item in citations],
        "Lang02 citation closure drift",
    )
    diagrams = data["diagrams"]
    require(diagrams == [], "expected zero native diagram records")
    for diagram, spec in zip(diagrams, gen.DIAGRAM_SPECS, strict=True):
        source_format, occurrence, source_first, source_last, target_first, target_last = spec
        require(
            diagram["source_format"] == source_format
            and diagram["source_occurrence_index"] == occurrence
            and diagram["source_binding"]["line_start"] == source_first
            and diagram["source_binding"]["line_end"] == source_last
            and diagram["target_binding"]["line_start"] == target_first
            and diagram["target_binding"]["line_end"] == target_last
            and diagram["state"] == "audited_preserved",
            f"diagram {source_format}-{occurrence} topology drift",
        )
    indexes = data["index_entries"]
    require(len(indexes) == 2, "expected two native index records")
    require(
        Counter("sym1" if "/sym1/" in item["stable_key"] else "main" for item in indexes)
        == Counter({"main": 2}),
        "main index census drift",
    )
    require(
        [item["ordinal_in_unit"] for item in indexes] == [1, 2]
        and all(item["provenance_state"] == "source_key_preserved_target_key_localized" for item in indexes),
        "index order or provenance-state drift",
    )

    require(
        unit["section_ids"] == [section["id"]]
        and unit["diagram_ids"] == [item["id"] for item in diagrams]
        and unit["index_entry_ids"] == [item["id"] for item in indexes]
        and unit["build_surface_ids"] == [item["id"] for item in data["build_surfaces"]]
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
            "diagrams": 0,
            "index_entries": 2,
        },
        "surface compatibility census drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights inventory drift")
    require({key: item["applies_to_unit"] for key, item in rights.items()} == EXPECTED_RIGHTS, "rights applicability drift")
    principal_paths = {item["path"] for item in rights["rights/principal-cc-by-4.0"]["bindings"]}
    require(
        principal_paths
        == {gen.SOURCE, gen.CANDIDATE, gen.TARGET, gen.BIBLIOGRAPHY, "repo/source/LICENSE", "repo/source/ccby.png"},
        "principal-rights binding drift",
    )
    rights_key_by_id = {item["id"]: key for key, item in rights.items()}
    require(
        {rights_key_by_id[item] for item in unit["rights_component_ids"]}
        == {"rights/principal-cc-by-4.0", "rights/ajbook-fragment-cc-by-sa-3.0", "rights/noto-fonts-ofl-1.1"},
        "unit rights flattened or closure exceptions lost",
    )
    require("imply no endorsement" in rights["rights/principal-cc-by-4.0"]["required_treatment"], "non-endorsement treatment drift")

    require(len(data["build_surfaces"]) == 1, "build-surface count drift")
    build = data["build_surfaces"][0]
    artifact = ROOT / gen.ARTIFACT
    require(
        build["artifact_path"] == gen.ARTIFACT
        and build["status"] == "pass"
        and build["page_count"] == gen.EXPECTED_PAGE_COUNT
        and (build["artifact_binding"]["bytes"], build["artifact_binding"]["sha256"]) == gen.ARTIFACT_ID
        and (artifact.stat().st_size, sha256(artifact)) == gen.ARTIFACT_ID,
        "final reader artifact or page binding drift",
    )
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical target absent from build closure")
    require(gen.BIBLIOGRAPHY in input_paths, "bibliography absent from build closure")
    require(gen.CANDIDATE not in input_paths, "reader build depends on isolated candidate")
    require(gen.SOURCE not in input_paths, "reader build depends on authority source")

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
    admission_scope = qa["qa/unit-029/admission-gate"]["scope"]
    for token in (
        MODEL,
        "666-795",
        "129-record",
        "25 active environment pairs",
        "six labels",
        "16 ordinary references",
        "one citation",
        "Lang02",
        "two list items",
        "211 protected mathematical zones",
        "two main indexes",
        "five admitted terminology rows",
        "zero source corrections",
        "one protected-text localization",
        "zero diagrams",
        "no exercises, hints, answers, or solutions",
        "no endorsement",
        "user's instruction",
    ):
        require(token in admission_scope, f"admission scope lacks {token!r}")
    witness_by_qa = {
        "qa/unit-029/admission-gate": gen.VISUAL_REVIEW,
        "qa/unit-029/source-review": gen.REVIEW,
        "qa/unit-029/candidate-artifact": gen.CANDIDATE,
        "qa/unit-029/candidate-check": gen.CANDIDATE_GATE,
        "qa/unit-029/canonical-integration": gen.STRUCTURE_GATE,
        "qa/unit-029/source-corrections": gen.REVIEW,
        "qa/unit-029/protected-text-localizations": gen.REVIEW,
        "qa/unit-029/terminology-control": gen.TERMINOLOGY,
        "qa/unit-029/terminology-delta": gen.TERMINOLOGY_DELTA,
        "qa/unit-029/terminology-evidence": gen.TERMINOLOGY_AUDIT,
        "qa/unit-029/prepromotion-evidence": gen.PREPROMOTION_AUDIT,
        "qa/unit-029/citation-closure": gen.BIBLIOGRAPHY,
        "qa/unit-029/build-log": gen.FINAL_LOG,
        "qa/unit-029/visual-preflight": gen.VISUAL_PREFLIGHT,
        "qa/unit-029/structure-and-pdf-qa": gen.STRUCTURE_PDF_QA,
        "qa/unit-029/render-hash-inventory": gen.RENDER_HASH_INVENTORY,
        "qa/unit-029/all-page-visual-review": gen.VISUAL_REVIEW,
    }
    for key, relative in witness_by_qa.items():
        witness = ROOT / relative
        bound = qa[key]["witness_binding"]
        require(
            bound["path"] == relative
            and (bound["bytes"], bound["sha256"]) == (witness.stat().st_size, sha256(witness)),
            f"QA witness binding drift: {key}",
        )

    binding_audit = audit_bindings(data)
    require(binding_audit["line_span_occurrences"] > 0, "no line-span binding audited")
    for required_path in (
        gen.SOURCE,
        gen.CANDIDATE,
        gen.TARGET,
        gen.BIBLIOGRAPHY,
        gen.ARTIFACT,
        gen.FINAL_LOG,
        gen.VISUAL_PREFLIGHT,
        gen.VISUAL_REVIEW,
        gen.STRUCTURE_PDF_QA,
        gen.RENDER_HASH_INVENTORY,
        gen.REVIEW,
        gen.TERMINOLOGY,
    ):
        require(required_path in binding_audit["paths"], f"required provenance path absent: {required_path}")

    report = {
        "status": "PASS",
        "unit": "unit-029-bab-4-teorema-sylow",
        "authority": "chapter4.tex:666-795 (blank line 795 omitted from mapping)",
        "target": "chapter4.tex:665-793",
        "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "provenance_model": MODEL,
        "provenance_actor": "Codex acting on the user's instruction",
        "artifact": {"path": gen.ARTIFACT, "pages": gen.EXPECTED_PAGE_COUNT, "bytes": gen.ARTIFACT_ID[0], "sha256": gen.ARTIFACT_ID[1]},
        "counts": {
            "sections": 1,
            "concepts": 280,
            "textual_environment_markers": 50,
            "textual_environment_pairs": 25,
            "active_environment_pairs": 25,
            "labels": 6,
            "ordinary_references": 16,
            "equation_references": 0,
            "citations": 1,
            "list_items": 2,
            "protected_math_zones": 211,
            "diagrams": 0,
            "tikzcd_diagrams": 0,
            "polygon_drawings": 0,
            "diagram_arrows": 0,
            "polygon_drawing_commands": 0,
            "index_entries": 2,
            "terminology_rows": 5,
            "source_corrections": 0,
            "protected_text_localizations": 1,
            "qa_events": 17,
            "visual_qa_witnesses": 4,
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
            "exact_csv_projection": "PASS",
            "no_stale_unit_026_ids_or_data": "PASS",
            "exact_authority_candidate_target_boundary": "PASS",
            "complete_tex_surface_topology": "PASS",
            "native_citation_and_index_provenance": "PASS",
            "zero_source_corrections": "PASS",
            "one_protected_text_localization": "PASS",
            "no_invented_exercise_or_solution_surfaces": "PASS",
            "component_rights_non_endorsement_and_closure_exceptions": "PASS",
            "build_pdf_and_visual_preflight_bindings": "PASS",
            "canonical_structure_pdf_and_render_bindings": "PASS",
            "independent_preflight_preserved_separately": "PASS",
            "terminology_binding": "PASS",
            "all_full_file_and_line_span_bindings": "PASS",
            "validation_mutated_outputs": False,
        },
        "binding_audit": binding_audit,
        "identities": {key: {"bytes": value[0], "sha256": value[1]} for key, value in after_shared.items()},
        "tools": {
            GENERATOR.relative_to(ROOT).as_posix(): {"bytes": GENERATOR.stat().st_size, "sha256": sha256(GENERATOR)},
            Path(__file__).resolve().relative_to(ROOT).as_posix(): {
                "bytes": Path(__file__).resolve().stat().st_size,
                "sha256": sha256(Path(__file__).resolve()),
            },
        },
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
