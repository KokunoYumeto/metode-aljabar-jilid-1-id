#!/usr/bin/env python3
"""Regenerate and fail-closed validate the canonical Unit 033 backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_033_backend as gen
import validate_backend as shared_contract


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_033_backend.py"
SHARED_VALIDATOR = ROOT / "scripts/validate_backend.py"
DATA = ROOT / gen.OUTPUT
SCHEMA = ROOT / gen.SCHEMA
EVIDENCE = ROOT / gen.EVIDENCE
CSV_FILES = tuple(ROOT / path for path in gen.CSV_OUTPUTS)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 033 backend validation refused: " + message)


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
    markers = (
        '"concepts": 485', '"diagrams": 12', '"protected_math_zones": 311',
        '"citation_occurrences": 0', '"digital_reflows": 1',
        '"terminology_normalizations": 2', '"driver_rendering_workarounds": 1',
        '"qa_events": 22',
    )
    for marker in markers:
        require(marker in first_stdout, f"first generator census marker drift: {marker}")
    first = identities(canonical)
    second_stdout = run([sys.executable, "-B", str(GENERATOR)])
    for marker in markers:
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
    for stale in (b"unit-026", b"u026", b"unit-029", b"u029", b"unit-030", b"u030", b"unit-031", b"u031", b"unit-032", b"u032"):
        require(stale not in combined.lower(), f"stale prior-unit identifier leaked: {stale.decode()}")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    require(data["dataset_stable_key"] == gen.DATASET_KEY, "dataset key drift")
    require(data["edition"]["commit"] == "c4f7a01f68f5f407906b4b970640cddbbad85f6b"
            and data["edition"]["tree"] == "0f9fd52748165ec89a85ba602ccb949a2ce04694",
            "edition authority commit/tree drift")
    require(data["unit"]["stable_key"] == gen.UNIT_KEY and data["unit"]["order"] == 33,
            "Unit 033 identity/order drift")
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
        "concept/": 41, "surface/unit-033/environment/": 43, "surface/unit-033/label/": 10,
        "surface/unit-033/reference/ordinary/": 10, "surface/unit-033/reference/equation/": 10,
        "surface/unit-033/item/": 10, "surface/unit-033/diagram-arrow/": 4,
        "surface/unit-033/drawing-command/": 22, "surface/unit-033/protected-math-zone/": 311,
        "surface/unit-033/terminology-row/": 13, "correction/o013-li-u033-cor-": 2,
        "protected-text-localization/o013-li-u033-loc-": 5,
        "terminology-normalization/o013-li-u033-termnorm-": 2,
        "citation-locator-localization/o013-li-u033-citeloc-": 0,
        "digital-reflow/o013-li-u033-reflow-": 1, "provenance/o013-li-u033-production": 1,
    }
    require(len(concepts) == 485 and len(keys) == len(set(keys)), f"concept census/uniqueness drift: {len(concepts)}")
    for prefix, expected in prefix_counts.items():
        require(sum(key.startswith(prefix) for key in keys) == expected, f"concept prefix census drift: {prefix}")
    require({key for key in keys if key.startswith("concept/")} == set(gen.CORE_STABLE_KEYS), "core concept inventory drift")
    require(not any(token in key for key in keys for token in ("/exercise/", "/hint/", "/answer/", "/solution/")), "invented learner-support surface")
    concept_by_key = {item["stable_key"]: item for item in concepts}
    provenance = " ".join(item["text"] for item in concept_by_key["provenance/o013-li-u033-production"]["labels"])
    require(gen.MODEL in provenance and "user's instruction" in provenance, "production provenance drift")
    require(data["unit"]["concept_ids"] == [item["id"] for item in concepts] == data["sections"][0]["concept_ids"], "concept ownership/order drift")
    exact_record_fragments = {
        "correction/o013-li-u033-cor-001": ("authority line 1580", "baris target 1575", "tilde-tau_{n-1}"),
        "correction/o013-li-u033-cor-002": ("authority line 1591", "baris target 1586", "cardinality |S'_n|"),
        "terminology-normalization/o013-li-u033-termnorm-001": ("aligned authority line 1407", "baris target 1402", "unsur identitas"),
        "terminology-normalization/o013-li-u033-termnorm-002": ("aligned authority line 1516", "baris target 1511", "unsur identitas"),
        "digital-reflow/o013-li-u033-reflow-001": ("authority line 1495", "baris target 1490", "matematika display"),
    }
    for key, fragments in exact_record_fragments.items():
        text = " ".join(label["text"] for label in concept_by_key[key]["labels"])
        require(all(fragment in text for fragment in fragments), f"correction/normalization/reflow record drift: {key}")

    require(data["citations"] == [], "Unit 033 invents native citations")
    require(data["unit"]["citation_ids"] == [], "Unit 033 citation ownership is not empty")
    require(len(data["diagrams"]) == 12 and len(data["index_entries"]) == 9, "diagram/index census drift")
    expected_diagram_keys = [
        *(f"diagram/unit-033/tikzpicture-{ordinal:02d}" for ordinal in range(1, 11)),
        "diagram/unit-033/tikzcd-01", "diagram/unit-033/tikzpicture-11",
    ]
    require([item["stable_key"] for item in data["diagrams"]] == expected_diagram_keys,
            "twelve-diagram format/order drift")
    require(all(item["provenance_state"] == "source_key_preserved_target_key_localized" for item in data["index_entries"]), "index-localization provenance drift")
    expected_index_pairs = [
        ("duichengqun", "duichengqun@grup simetris (symmetric group)"),
        ("xunhuan@循环 (cycle)", "xunhuan@siklus (cycle)"),
        ("duihuan@对换 (transposition)", "duihuan@transposisi (transposition)"),
        ("S_n@$\\mathfrak{S}_n$", "S_n@$\\mathfrak{S}_n$"),
        ("fenchai@分拆 (partition)", "fenchai@partisi (partition)"),
        ("sgn@$\\sgn$", "sgn@$\\sgn$"),
        ("A_n@$\\mathfrak{A}_n$", "A_n@$\\mathfrak{A}_n$"),
        ("kejiequn", "kejiequn@grup solvabel (solvable group)"),
        ("Coxeter 群", "grup Coxeter (Coxeter group)"),
    ]
    require([(item["source_key"], item["target_key"]) for item in data["index_entries"]]
            == expected_index_pairs, "nine-entry localized index order/value drift")
    expected_index_keys = [
        "index-entry/unit-033/main/001", "index-entry/unit-033/main/002",
        "index-entry/unit-033/main/003", "index-entry/unit-033/sym1/004",
        "index-entry/unit-033/main/005", "index-entry/unit-033/sym1/006",
        "index-entry/unit-033/sym1/007", "index-entry/unit-033/main/008",
        "index-entry/unit-033/main/009",
    ]
    require([item["stable_key"] for item in data["index_entries"]] == expected_index_keys,
            "nine-entry index stream/stable-key order drift")
    require(data["unit"]["surface_counts"] == {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 0, "diagrams": 12, "index_entries": 9}, "native surface census drift")
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
    require(build["driver"]["path"] == gen.DRIVER and build["build_script"]["path"] == gen.BUILD_SCRIPT,
            "reader driver/build-script binding drift")
    qa_keys = [item["stable_key"] for item in data["qa_events"]]
    expected_qa_keys = [
        "qa/unit-033/admission-gate", "qa/unit-033/source-review",
        "qa/unit-033/candidate-artifact", "qa/unit-033/candidate-check",
        "qa/unit-033/canonical-integration", "qa/unit-033/source-corrections",
        "qa/unit-033/terminology-normalizations", "qa/unit-033/digital-reflow",
        "qa/unit-033/protected-text-localizations", "qa/unit-033/index-localizations",
        "qa/unit-033/terminology-control", "qa/unit-033/terminology-delta",
        "qa/unit-033/terminology-evidence", "qa/unit-033/prepromotion-evidence",
        "qa/unit-033/build-log", "qa/unit-033/driver-poppler-xlongequal-workaround",
        "qa/unit-033/preflight-tool", "qa/unit-033/evidence-tool",
        "qa/unit-033/visual-preflight", "qa/unit-033/structure-and-pdf-qa",
        "qa/unit-033/render-hash-inventory", "qa/unit-033/all-page-visual-review",
    ]
    require(qa_keys == expected_qa_keys and len(data["qa_events"]) == 22,
            "QA event topology drift")
    require(data["unit"]["qa_event_ids"] == [item["id"] for item in data["qa_events"]],
            "QA event ownership/order drift")
    require(all(item["result"] == item["translation_audit_state"] == item["build_state"] == item["visual_state"] == "pass" for item in data["qa_events"]), "QA event state drift")

    uuid_count = audit_uuidv5(data, namespace)
    binding_audit = audit_live_bindings(data)
    require(uuid_count == 561, f"UUIDv5 entity census drift: {uuid_count}")
    require(
        binding_audit["occurrences"] == 104
        and binding_audit["line_span_occurrences"] == 46
        and binding_audit["unique_paths"] == 41,
        f"live binding census drift: {binding_audit!r}",
    )
    required_paths = (
        gen.SOURCE, gen.CANDIDATE, gen.CANDIDATE_GATE, gen.REVIEW, gen.TARGET,
        gen.TERMINOLOGY, gen.TERMINOLOGY_DELTA, gen.TERMINOLOGY_AUDIT,
        gen.PREPROMOTION_AUDIT, gen.STRUCTURE_GATE, gen.BUILD_SCRIPT,
        gen.PREFLIGHT_SCRIPT, gen.EVIDENCE_SCRIPT, gen.DRIVER, gen.COVER,
        gen.CROSSREF, gen.BIBLIOGRAPHY, gen.FINAL_LOG, gen.VISUAL_PREFLIGHT,
        gen.VISUAL_REVIEW, gen.STRUCTURE_PDF_QA, gen.RENDER_HASH_INVENTORY,
        gen.ARTIFACT,
    )
    for path in required_paths:
        require(path in binding_audit["paths"], f"required provenance path absent: {path}")

    # The shared validator's projection renderer is the canonical JSON-to-CSV
    # contract. Re-render in memory and compare all six files byte-for-byte;
    # parse/serialize the JSON independently to prove its lossless round trip.
    rendered_csvs = shared_contract.render_csvs(data)
    expected_csv_names = {path.name for path in CSV_FILES}
    require(set(rendered_csvs) == expected_csv_names, "six-file CSV name contract drift")
    for path in CSV_FILES:
        require(path.read_bytes() == rendered_csvs[path.name], f"JSON/CSV projection roundtrip drift: {path.name}")
    roundtrip = json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True))
    require(roundtrip == data, "canonical JSON parse/serialize roundtrip drift")

    report = {
        "status": "PASS", "unit": "unit-033-bab-4-grup-simetris",
        "authority": "chapter4.tex:1389-1608 (blank line 1608 omitted from mapping)",
        "target": "chapter4.tex:1384-1602", "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(), "provenance_model": gen.MODEL,
        "provenance_actor": "Codex acting on the user's instruction",
        "artifact": {"path": gen.ARTIFACT, "pages": gen.EXPECTED_PAGE_COUNT, "bytes": gen.FROZEN_IDENTITIES[gen.ARTIFACT][0], "sha256": gen.FROZEN_IDENTITIES[gen.ARTIFACT][1]},
        "counts": {**gen.EXPECTED_COUNTS, "concepts": 485, "native_citations": 0, "citation_occurrences": 0, "terminology_rows": 13, "qa_events": 22, "driver_rendering_workarounds": 1, "uuidv5_entities_audited": uuid_count},
        "checks": {
            "deterministic_regeneration_one": "PASS", "deterministic_regeneration_two": "PASS",
            "shared_schema_uuidv5_and_exact_csv": "PASS", "json_csv_roundtrip": "PASS", "exact_485_entity_topology": "PASS",
            "authority_candidate_target_boundary": "PASS", "two_declared_source_corrections": "PASS",
            "two_terminology_normalizations": "PASS", "one_source_target_digital_reflow": "PASS",
            "five_protected_text_localizations": "PASS", "nine_index_localizations": "PASS",
            "driver_only_xlongequal_workaround": "PASS", "component_rights_and_non_endorsement": "PASS",
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
