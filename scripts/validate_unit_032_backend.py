#!/usr/bin/env python3
"""Regenerate and fail-closed validate the canonical Unit 032 backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_032_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_032_backend.py"
SHARED_VALIDATOR = ROOT / "scripts/validate_backend.py"
DATA = ROOT / gen.OUTPUT
SCHEMA = ROOT / gen.SCHEMA
EVIDENCE = ROOT / gen.EVIDENCE
CSV_FILES = tuple(ROOT / path for path in gen.CSV_OUTPUTS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 032 backend validation refused: " + message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", check=False,
    )
    require(completed.returncode == 0, completed.stdout + completed.stderr)
    return completed.stdout


def audit_uuidv5(value: object, namespace: uuid.UUID) -> int:
    count = 0

    def visit(node: object) -> None:
        nonlocal count
        if isinstance(node, dict):
            stable_key, entity_id = node.get("stable_key"), node.get("id")
            if isinstance(stable_key, str) and isinstance(entity_id, str):
                expected = "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))
                require(entity_id == expected, f"UUIDv5 drift: {stable_key}")
                count += 1
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    require(count > 0, "no stable UUIDv5 entity found")
    return count


def audit_live_bindings(value: object) -> dict[str, object]:
    found: list[dict[str, object]] = []

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if {"path", "bytes", "sha256"}.issubset(node):
                found.append(node)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    paths: set[str] = set()
    spans = 0
    for item in found:
        relative = str(item["path"])
        path = ROOT / relative
        require(path.is_file(), f"bound path missing: {relative}")
        require((path.stat().st_size, sha256(path)) == (int(item["bytes"]), str(item["sha256"])),
                f"full-file binding drift: {relative}")
        paths.add(relative)
        span_fields = {"line_start", "line_end", "span_sha256", "span_hash_algorithm"}
        if span_fields.intersection(item):
            require(span_fields.issubset(item), f"incomplete span binding: {relative}")
            first, last = int(item["line_start"]), int(item["line_end"])
            require(item["span_hash_algorithm"] == "sha256-utf8-lines-lf-v1", "span algorithm drift")
            actual = hashlib.sha256(gen.normalized_span(relative, first, last)).hexdigest()
            require(actual == item["span_sha256"], f"span digest drift: {relative}:{first}-{last}")
            spans += 1
    require(found and spans, "backend lacks live full-file and line-span bindings")
    return {"occurrences": len(found), "line_span_occurrences": spans,
            "unique_paths": len(paths), "paths": sorted(paths)}


def scaffold_check() -> dict[str, object]:
    first = gen.scaffold_check()
    second = gen.scaffold_check()
    require(first == second, "read-only scaffold check is nondeterministic")
    require(first["counts"] == gen.EXPECTED_COUNTS, "generator/validator count contract drift")
    require(first["namespace_uuid"] == "5d74a443-839a-5a09-b2c6-0bc48a097f2b", "namespace drift")
    require(len(gen.CSV_OUTPUTS) == 6 and len(set(gen.CSV_OUTPUTS)) == 6, "six-projection contract drift")
    for key, value in first["stable_uuidv5_preview"].items():
        require(value == gen.uuidv5(key), f"preview UUIDv5 drift: {key}")
    require(first["production_freeze_state"] == "frozen", "production freeze state drift")
    return {
        "status": "PASS_SCAFFOLD_ONLY",
        "generator": GENERATOR.relative_to(ROOT).as_posix(),
        "generator_identity": {"bytes": GENERATOR.stat().st_size, "sha256": sha256(GENERATOR)},
        "authority": first["authority"], "candidate": first["candidate"],
        "target_state": first["target_state"], "counts": first["counts"],
        "namespace_uuid": first["namespace_uuid"], "csv_outputs": first["csv_outputs"],
        "writes_performed": False,
    }


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    require(all(path.is_file() for path in paths), "one or more generated outputs are missing")
    return {path.relative_to(ROOT).as_posix(): (path.stat().st_size, sha256(path)) for path in paths}


def production_validate() -> dict[str, object]:
    require(gen.FREEZE_STATE == "frozen", "production is not frozen; use --scaffold-check")
    canonical = (DATA, *CSV_FILES)
    first_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in ('"concepts": 589', '"diagrams": 11', '"protected_math_zones": 367', '"citation_occurrences": 6', '"digital_reflows": 2'):
        require(marker in first_stdout, f"first generator census marker drift: {marker}")
    first = identities(canonical)
    second_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in ('"concepts": 589', '"diagrams": 11', '"protected_math_zones": 367', '"citation_occurrences": 6', '"digital_reflows": 2'):
        require(marker in second_stdout, f"second generator census marker drift: {marker}")
    second = identities(canonical)
    require(first == second, "deterministic regeneration drift")
    require(first_stdout == second_stdout, "deterministic generator report drift")
    run([
        sys.executable, "-B", str(SHARED_VALIDATOR), "--lane-root", str(ROOT),
        "--data", str(DATA), "--schema", str(SCHEMA),
        "--csv-dir", str(ROOT / "backend/csv"),
    ])
    require(second == identities(canonical), "shared validator mutated projections")
    combined = b"\n".join(path.read_bytes() for path in canonical)
    for stale in (b"unit-026", b"u026", b"unit-029", b"u029", b"unit-030", b"u030", b"unit-031", b"u031"):
        require(stale not in combined.lower(), f"stale prior-unit identifier leaked: {stale.decode()}")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    require(data["dataset_stable_key"] == gen.DATASET_KEY, "dataset key drift")
    require(data["unit"]["stable_key"] == gen.UNIT_KEY and data["unit"]["order"] == 32,
            "Unit 032 identity/order drift")
    require(data["unit"]["source_binding"]["line_start"] == gen.SOURCE_START
            and data["unit"]["source_binding"]["line_end"] == gen.SOURCE_END,
            "authority boundary drift")
    require(data["unit"]["target_binding"]["line_start"] == gen.TARGET_START
            and data["unit"]["target_binding"]["line_end"] == gen.TARGET_END,
            "target boundary drift")
    require(data["workflow"] == {
        "responsible_task": str(uuid.uuid5(namespace, gen.TASK_KEY)), "updated": "2026-08-26",
        "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked",
        "qa_state": "translation_math_backend_build_visual_pass",
    }, "workflow state drift")
    require(data["unit"]["translation_state"] == "visually_checked" and data["unit"]["admission_state"] == "admitted", "unit admission-state drift")
    require(len(data["sections"]) == 1 and data["sections"][0]["admission_state"] == "admitted", "section admission drift")

    concepts = data["concepts"]
    keys = tuple(item["stable_key"] for item in concepts)
    prefix_counts = {
        "concept/": 41, "surface/unit-032/environment/": 52, "surface/unit-032/label/": 10,
        "surface/unit-032/reference/ordinary/": 14, "surface/unit-032/reference/equation/": 6,
        "surface/unit-032/item/": 11, "surface/unit-032/diagram-arrow/": 28,
        "surface/unit-032/drawing-command/": 8, "surface/unit-032/protected-math-zone/": 367,
        "surface/unit-032/terminology-row/": 30, "correction/o013-li-u032-cor-": 2,
        "protected-text-localization/o013-li-u032-loc-": 13,
        "citation-locator-localization/o013-li-u032-citeloc-": 4,
        "digital-reflow/o013-li-u032-reflow-": 2, "provenance/o013-li-u032-production": 1,
    }
    require(len(concepts) == 589 and len(keys) == len(set(keys)), f"concept census/uniqueness drift: {len(concepts)}")
    for prefix, expected in prefix_counts.items():
        require(sum(key.startswith(prefix) for key in keys) == expected, f"concept prefix census drift: {prefix}")
    require({key for key in keys if key.startswith("concept/")} == set(gen.CORE_STABLE_KEYS), "core concept inventory drift")
    require(not any(token in key for key in keys for token in ("/exercise/", "/hint/", "/answer/", "/solution/")), "invented learner-support surface")
    concept_by_key = {item["stable_key"]: item for item in concepts}
    provenance = " ".join(item["text"] for item in concept_by_key["provenance/o013-li-u032-production"]["labels"])
    require(gen.MODEL in provenance and "user's instruction" in provenance, "production provenance drift")
    require(data["unit"]["concept_ids"] == [item["id"] for item in concepts] == data["sections"][0]["concept_ids"], "concept ownership/order drift")

    require([item["bib_key"] for item in data["citations"]] == ["GM12", "De11", "You"], "native citation closure/order drift")
    require(len(data["diagrams"]) == 11 and len(data["index_entries"]) == 7, "diagram/index census drift")
    require(data["unit"]["surface_counts"] == {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 3, "diagrams": 11, "index_entries": 7}, "native surface census drift")
    require(data["unit"]["citation_ids"] == [item["id"] for item in data["citations"]], "citation ID ownership drift")
    require(data["unit"]["diagram_ids"] == [item["id"] for item in data["diagrams"]], "diagram ID ownership drift")
    require(data["unit"]["index_entry_ids"] == [item["id"] for item in data["index_entries"]], "index ID ownership drift")

    rights = {item["stable_key"]: item for item in data["rights"]}
    expected_rights = {"rights/principal-cc-by-4.0": True, "rights/lanzhou-cc-by-sa-3.0": False, "rights/ajbook-fragment-cc-by-sa-3.0": True, "rights/noto-fonts-ofl-1.1": True}
    require({key: item["applies_to_unit"] for key, item in rights.items()} == expected_rights, "component-rights applicability drift")
    principal_paths = {item["path"] for item in rights["rights/principal-cc-by-4.0"]["bindings"]}
    require(principal_paths == {gen.SOURCE, gen.CANDIDATE, gen.TARGET, gen.BIBLIOGRAPHY, "repo/source/LICENSE", "repo/source/ccby.png"}, "principal-rights bindings drift")
    require("imply no endorsement" in rights["rights/principal-cc-by-4.0"]["required_treatment"], "non-endorsement treatment drift")

    require(len(data["build_surfaces"]) == 1, "build-surface count drift")
    build = data["build_surfaces"][0]
    require(build["artifact_path"] == gen.ARTIFACT and build["page_count"] == gen.EXPECTED_PAGE_COUNT and build["status"] == "pass", "build surface drift")
    require((build["artifact_binding"]["bytes"], build["artifact_binding"]["sha256"]) == gen.FROZEN_IDENTITIES[gen.ARTIFACT], "artifact binding drift")
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths and gen.BIBLIOGRAPHY in input_paths and gen.CANDIDATE not in input_paths and gen.SOURCE not in input_paths, "reader build-closure boundary drift")
    require(len(data["qa_events"]) == 18 and all(item["result"] == item["translation_audit_state"] == item["build_state"] == item["visual_state"] == "pass" for item in data["qa_events"]), "QA event topology/state drift")

    uuid_count = audit_uuidv5(data, namespace)
    binding_audit = audit_live_bindings(data)
    for path in (gen.SOURCE, gen.CANDIDATE, gen.TARGET, gen.BIBLIOGRAPHY, gen.ARTIFACT, gen.FINAL_LOG, gen.VISUAL_PREFLIGHT, gen.VISUAL_REVIEW, gen.STRUCTURE_PDF_QA, gen.RENDER_HASH_INVENTORY, gen.REVIEW, gen.TERMINOLOGY):
        require(path in binding_audit["paths"], f"required provenance path absent: {path}")

    report = {
        "status": "PASS", "unit": "unit-032-bab-4-grup-bebas",
        "authority": "chapter4.tex:1108-1388 (blank line 1388 omitted from mapping)",
        "target": "chapter4.tex:1104-1383", "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(), "provenance_model": gen.MODEL,
        "provenance_actor": "Codex acting on the user's instruction",
        "artifact": {"path": gen.ARTIFACT, "pages": gen.EXPECTED_PAGE_COUNT, "bytes": gen.FROZEN_IDENTITIES[gen.ARTIFACT][0], "sha256": gen.FROZEN_IDENTITIES[gen.ARTIFACT][1]},
        "counts": {**gen.EXPECTED_COUNTS, "concepts": 589, "native_citations": 3, "citation_occurrences": 6, "terminology_rows": 30, "qa_events": 18, "uuidv5_entities_audited": uuid_count},
        "checks": {
            "deterministic_regeneration_one": "PASS", "deterministic_regeneration_two": "PASS",
            "shared_schema_uuidv5_and_exact_csv": "PASS", "exact_589_entity_topology": "PASS",
            "authority_candidate_target_boundary": "PASS", "two_declared_source_corrections": "PASS",
            "two_target_only_digital_reflows": "PASS", "thirteen_protected_text_localizations": "PASS",
            "four_citation_locator_localizations": "PASS", "component_rights_and_non_endorsement": "PASS",
            "reader_build_and_all_page_visual_bindings": "PASS", "validation_mutated_outputs": False,
        },
        "binding_audit": binding_audit,
        "identities": {key: {"bytes": value[0], "sha256": value[1]} for key, value in second.items()},
        "tools": {
            GENERATOR.relative_to(ROOT).as_posix(): {"bytes": GENERATOR.stat().st_size, "sha256": sha256(GENERATOR)},
            Path(__file__).resolve().relative_to(ROOT).as_posix(): {"bytes": Path(__file__).resolve().stat().st_size, "sha256": sha256(Path(__file__).resolve())},
        },
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scaffold-check", action="store_true")
    args = parser.parse_args()
    if args.scaffold_check:
        print(json.dumps(scaffold_check(), ensure_ascii=False, sort_keys=True))
        return
    print(json.dumps(production_validate(), ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
