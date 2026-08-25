#!/usr/bin/env python3
"""Regenerate and fail-closed validate the canonical Unit 027 backend."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_027_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_027_backend.py"
SHARED_VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.json"
EVIDENCE = ROOT / "qa/unit-027-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-027-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)

EXPECTED_PREFIX_COUNTS = {
    "concept/": 17,
    "surface/unit-027/environment/": 28,
    "surface/unit-027/label/": 8,
    "surface/unit-027/reference/ordinary/": 4,
    "surface/unit-027/reference/equation/": 1,
    "surface/unit-027/item/": 15,
    "surface/unit-027/diagram-arrow/": 30,
    "surface/unit-027/polygon-drawing-command/": 15,
    "surface/unit-027/protected-math-zone/": 171,
    "surface/unit-027/terminology-row/": 9,
    "correction/o013-li-u027-cor-": 2,
    "translation-precision/o013-li-u027-tr-001": 1,
    "style-normalization/o013-li-u027-style-": 2,
    "provenance/o013-li-u027-production": 1,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}
EXPECTED_QA = {
    "qa/unit-027/admission-gate",
    "qa/unit-027/source-review",
    "qa/unit-027/candidate-artifact",
    "qa/unit-027/candidate-check",
    "qa/unit-027/canonical-integration",
    "qa/unit-027/source-corrections",
    "qa/unit-027/translation-precision",
    "qa/unit-027/terminology-control",
    "qa/unit-027/terminology-delta",
    "qa/unit-027/terminology-evidence",
    "qa/unit-027/prepromotion-evidence",
    "qa/unit-027/build-log",
    "qa/unit-027/visual-preflight",
    "qa/unit-027/structure-and-pdf-qa",
    "qa/unit-027/render-hash-inventory",
    "qa/unit-027/all-page-visual-review",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 027 backend validation refused: " + message)


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
            "Unit 027 backend validation refused:\n"
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
    for marker in ('"concepts": 304', '"diagrams": 7', '"protected_math_zones": 171'):
        require(marker in first_stdout, f"generator census marker drift: {marker}")
    first = identities(canonical_paths)
    second_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in ('"concepts": 304', '"diagrams": 7', '"protected_math_zones": 171'):
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
    require(b"unit-026" not in all_generated, "stale Unit 026 identifier leaked into Unit 027 outputs")
    require(b"u026" not in all_generated.lower(), "stale U026 identifier leaked into Unit 027 outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uuid_count = audit_uuidv5(data, namespace)
    require(
        data["dataset_stable_key"] == "dataset/unit-027/id-id"
        and data["dataset_id"] == "urn:uuid:" + str(uuid.uuid5(namespace, "dataset/unit-027/id-id")),
        "dataset identity drift",
    )
    require(
        data["workflow"]
        == {
            "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u027-backend")),
            "updated": "2026-08-25",
            "status": "admitted",
            "admission_state": "admitted",
            "translation_state": "visually_checked",
            "qa_state": "translation_math_backend_build_visual_pass",
        },
        "workflow state drift",
    )

    unit = data["unit"]
    require(unit["stable_key"] == "unit/bab-4-produk-langsung-semilangsung-dan-ekstensi-grup", "unit key drift")
    require(unit["order"] == 27, "unit order drift")
    require(
        unit["source_local_id"] == "chapter4.tex:365-517; substantive record map 365-516",
        "authority description drift",
    )
    require(
        unit["source_binding"]["line_start"] == 365
        and unit["source_binding"]["line_end"] == 517
        and unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1]
        and (unit["source_binding"]["bytes"], unit["source_binding"]["sha256"]) == gen.SOURCE_FULL,
        "authority binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 366
        and unit["target_binding"]["line_end"] == 517
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
        section["stable_key"] == "unit/bab-4-produk-langsung-semilangsung-dan-ekstensi-grup/section/01"
        and section["order"] == 1
        and section["source_binding"]["line_start"] == 365
        and section["source_binding"]["line_end"] == 517
        and section["target_binding"]["line_start"] == 366
        and section["target_binding"]["line_end"] == 517,
        "section boundary or order drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(len(concepts) == 304, f"expected 304 concept-compatible entities, got {len(concepts)}")
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
        labels = concept_by_key[f"surface/unit-027/terminology-row/{ordinal:03d}"]["labels"]
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
    repair = concept_by_key["translation-precision/o013-li-u027-tr-001"]
    require(
        "O013-LI-U027-TR-001" in " ".join(item["text"] for item in repair["labels"])
        and "need not be inner on N" in repair["labels"][0]["text"],
        "TR-001 type-precision provenance drift",
    )
    provenance_text = " ".join(item["text"] for item in concept_by_key["provenance/o013-li-u027-production"]["labels"])
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

    require(data["citations"] == [] and unit["citation_ids"] == [], "unexpected citation record")
    diagrams = data["diagrams"]
    require(len(diagrams) == 7, "expected seven native diagram records")
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
    require(len(indexes) == 6, "expected six native index records")
    require(
        Counter("sym1" if "/sym1/" in item["stable_key"] else "main" for item in indexes)
        == Counter({"main": 5, "sym1": 1}),
        "main/sym1 index census drift",
    )
    require(
        [item["ordinal_in_unit"] for item in indexes] == list(range(1, 7))
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
            "citations": 0,
            "diagrams": 7,
            "index_entries": 6,
        },
        "surface compatibility census drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights inventory drift")
    require({key: item["applies_to_unit"] for key, item in rights.items()} == EXPECTED_RIGHTS, "rights applicability drift")
    principal_paths = {item["path"] for item in rights["rights/principal-cc-by-4.0"]["bindings"]}
    require(
        principal_paths
        == {gen.SOURCE, gen.CANDIDATE, gen.TARGET, "repo/source/LICENSE", "repo/source/ccby.png"},
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
        and build["page_count"] == 7
        and (build["artifact_binding"]["bytes"], build["artifact_binding"]["sha256"]) == gen.ARTIFACT_ID
        and (artifact.stat().st_size, sha256(artifact)) == gen.ARTIFACT_ID,
        "final reader artifact or page binding drift",
    )
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical target absent from build closure")
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
    admission_scope = qa["qa/unit-027/admission-gate"]["scope"]
    for token in (
        MODEL,
        "365-517",
        "152-record",
        "28 active environment pairs",
        "eight labels",
        "four ordinary",
        "one equation reference",
        "15 list items",
        "171 protected mathematical zones",
        "six indexes",
        "four tikzcd diagrams",
        "30 arrows",
        "three polygon drawings",
        "15 drawing commands",
        "nine admitted terminology rows",
        "two declared source corrections",
        "one translation-precision repair",
        "two controlled-style normalizations",
        "no citations, exercises, hints, answers, or solutions",
        "no endorsement",
        "user's instruction",
    ):
        require(token in admission_scope, f"admission scope lacks {token!r}")
    witness_by_qa = {
        "qa/unit-027/admission-gate": gen.VISUAL_REVIEW,
        "qa/unit-027/source-review": gen.REVIEW,
        "qa/unit-027/candidate-artifact": gen.CANDIDATE,
        "qa/unit-027/candidate-check": gen.CANDIDATE_GATE,
        "qa/unit-027/canonical-integration": gen.STRUCTURE_GATE,
        "qa/unit-027/source-corrections": gen.REVIEW,
        "qa/unit-027/translation-precision": gen.REVIEW,
        "qa/unit-027/terminology-control": gen.TERMINOLOGY,
        "qa/unit-027/terminology-delta": gen.TERMINOLOGY_DELTA,
        "qa/unit-027/terminology-evidence": gen.TERMINOLOGY_AUDIT,
        "qa/unit-027/prepromotion-evidence": gen.PREPROMOTION_AUDIT,
        "qa/unit-027/build-log": gen.FINAL_LOG,
        "qa/unit-027/visual-preflight": gen.VISUAL_PREFLIGHT,
        "qa/unit-027/structure-and-pdf-qa": gen.STRUCTURE_PDF_QA,
        "qa/unit-027/render-hash-inventory": gen.RENDER_HASH_INVENTORY,
        "qa/unit-027/all-page-visual-review": gen.VISUAL_REVIEW,
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
        "unit": "unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup",
        "authority": "chapter4.tex:365-517 (blank line 517 omitted from 365-516 mapping)",
        "target": "chapter4.tex:366-517",
        "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "provenance_model": MODEL,
        "provenance_actor": "Codex acting on the user's instruction",
        "artifact": {"path": gen.ARTIFACT, "pages": 7, "bytes": gen.ARTIFACT_ID[0], "sha256": gen.ARTIFACT_ID[1]},
        "counts": {
            "sections": 1,
            "concepts": 304,
            "textual_environment_markers": 56,
            "textual_environment_pairs": 28,
            "active_environment_pairs": 28,
            "labels": 8,
            "ordinary_references": 4,
            "equation_references": 1,
            "citations": 0,
            "list_items": 15,
            "protected_math_zones": 171,
            "diagrams": 7,
            "tikzcd_diagrams": 4,
            "polygon_drawings": 3,
            "diagram_arrows": 30,
            "polygon_drawing_commands": 15,
            "index_entries": 6,
            "terminology_rows": 9,
            "source_corrections": 2,
            "translation_precision_repairs": 1,
            "style_normalizations": 2,
            "qa_events": 16,
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
            "native_diagram_and_index_provenance": "PASS",
            "two_source_corrections": "PASS",
            "translation_precision_tr_001": "PASS",
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
