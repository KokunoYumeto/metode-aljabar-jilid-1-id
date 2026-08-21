#!/usr/bin/env python3
"""Validate the O013 modular backend using only the Python standard library.

The JSON document is canonical. CSV files are deterministic projections and
are compared byte-for-byte unless --write-csv is supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


UUID_URN_RE = re.compile(
    r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^}]*)\}")
REF_RE = re.compile(r"\\(?:ref|pageref)\{([^}]*)\}")
INDEX_RE = re.compile(r"\\index\{([^}]*)\}")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def uuid_from_urn(value: str) -> uuid.UUID:
    return uuid.UUID(value.removeprefix("urn:uuid:"))


def resolve_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"only internal JSON pointers are supported: {reference}")
    node: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"schema reference is not an object: {reference}")
    return node


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_against_schema(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    where: str,
    result: Validation,
) -> None:
    if "$ref" in schema:
        validate_against_schema(value, resolve_ref(root_schema, schema["$ref"]), root_schema, where, result)
        return

    expected_type = schema.get("type")
    if expected_type is not None:
        accepted = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(json_type_matches(value, item) for item in accepted):
            result.errors.append(f"{where}: expected type {accepted}, found {type(value).__name__}")
            return

    if "const" in schema:
        result.require(value == schema["const"], f"{where}: expected constant {schema['const']!r}, found {value!r}")
    if "enum" in schema:
        result.require(value in schema["enum"], f"{where}: value {value!r} is not in {schema['enum']!r}")

    if isinstance(value, str):
        if "minLength" in schema:
            result.require(len(value) >= schema["minLength"], f"{where}: string is shorter than minLength")
        if "pattern" in schema:
            result.require(re.fullmatch(schema["pattern"], value) is not None, f"{where}: value does not match {schema['pattern']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema:
        result.require(value >= schema["minimum"], f"{where}: value is below minimum {schema['minimum']}")

    if isinstance(value, list):
        if "minItems" in schema:
            result.require(len(value) >= schema["minItems"], f"{where}: array has fewer than {schema['minItems']} items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            result.require(len(serialized) == len(set(serialized)), f"{where}: array contains duplicates")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_against_schema(item, item_schema, root_schema, f"{where}[{index}]", result)

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            result.require(key in value, f"{where}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_against_schema(item, properties[key], root_schema, f"{where}.{key}", result)
            elif schema.get("additionalProperties") is False:
                result.errors.append(f"{where}: unexpected property {key!r}")


def entity_groups(data: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    return [
        ("program", [data["program"]]),
        ("course", [data["course"]]),
        ("resource", [data["resource"]]),
        ("edition", [data["edition"]]),
        ("unit", [data["unit"]]),
        ("section", data["sections"]),
        ("concept", data["concepts"]),
        ("prerequisite", data["prerequisites"]),
        ("rights", data["rights"]),
        ("citation", data["citations"]),
        ("diagram", data["diagrams"]),
        ("index_entry", data["index_entries"]),
        ("build_surface", data["build_surfaces"]),
        ("qa_event", data["qa_events"]),
    ]


def all_entities(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [entity for _, records in entity_groups(data) for entity in records]


def safe_lane_path(lane_root: Path, relative: str, result: Validation, where: str) -> Path | None:
    posix = PurePosixPath(relative)
    if posix.is_absolute() or ".." in posix.parts:
        result.errors.append(f"{where}: unsafe non-relative path {relative!r}")
        return None
    candidate = (lane_root / Path(*posix.parts)).resolve()
    try:
        candidate.relative_to(lane_root.resolve())
    except ValueError:
        result.errors.append(f"{where}: path escapes lane root: {relative!r}")
        return None
    return candidate


def validate_file_binding(
    binding: dict[str, Any],
    lane_root: Path,
    result: Validation,
    where: str,
    cache: dict[Path, tuple[int, str, list[str]]],
) -> None:
    path = safe_lane_path(lane_root, binding["path"], result, where)
    if path is None:
        return
    if not path.is_file():
        result.errors.append(f"{where}: bound file does not exist: {binding['path']}")
        return
    if path not in cache:
        payload = path.read_bytes()
        try:
            text = payload.decode("utf-8")
            lines = text.splitlines()
        except UnicodeDecodeError:
            lines = []
        cache[path] = (len(payload), sha256_bytes(payload), lines)
    actual_bytes, actual_hash, lines = cache[path]
    result.require(actual_bytes == binding["bytes"], f"{where}: byte count drift for {binding['path']}: expected {binding['bytes']}, found {actual_bytes}")
    result.require(actual_hash == binding["sha256"], f"{where}: SHA-256 drift for {binding['path']}: expected {binding['sha256']}, found {actual_hash}")

    if "line_start" in binding:
        start = binding["line_start"]
        end = binding["line_end"]
        result.require(bool(lines), f"{where}: line binding is not valid UTF-8 text")
        result.require(start <= end, f"{where}: line_start exceeds line_end")
        result.require(end <= len(lines), f"{where}: line_end {end} exceeds file length {len(lines)}")
        if lines and 1 <= start <= end <= len(lines):
            normalized = ("\n".join(lines[start - 1 : end]) + "\n").encode("utf-8")
            actual_span = sha256_bytes(normalized)
            result.require(
                actual_span == binding["span_sha256"],
                f"{where}: normalized line-span SHA-256 drift for {binding['path']}:{start}-{end}: expected {binding['span_sha256']}, found {actual_span}",
            )


def walk_bindings(value: Any, where: str = "$") -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        if {"path", "bytes", "sha256"}.issubset(value):
            yield where, value
        for key, item in value.items():
            yield from walk_bindings(item, f"{where}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_bindings(item, f"{where}[{index}]")


def refresh_derivative_bindings(value: Any, lane_root: Path, result: Validation, where: str = "$") -> None:
    """Refresh only explicit repo/ bindings; immutable authority bindings fail closed."""
    if isinstance(value, dict):
        if {"path", "bytes", "sha256"}.issubset(value) and value["path"].startswith("repo/"):
            path = safe_lane_path(lane_root, value["path"], result, where)
            if path is not None and path.is_file():
                payload = path.read_bytes()
                value["bytes"] = len(payload)
                value["sha256"] = sha256_bytes(payload)
                if "line_start" in value:
                    try:
                        lines = payload.decode("utf-8").splitlines()
                    except UnicodeDecodeError:
                        result.errors.append(f"{where}: derivative line binding is not UTF-8")
                    else:
                        start = value["line_start"]
                        end = value["line_end"]
                        if not (1 <= start <= end <= len(lines)):
                            result.errors.append(f"{where}: cannot refresh invalid line range {start}-{end} for {value['path']}")
                        else:
                            normalized = ("\n".join(lines[start - 1 : end]) + "\n").encode("utf-8")
                            value["span_sha256"] = sha256_bytes(normalized)
        for key, item in value.items():
            refresh_derivative_bindings(item, lane_root, result, f"{where}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            refresh_derivative_bindings(item, lane_root, result, f"{where}[{index}]")


def parse_citations(text: str) -> list[str]:
    values: list[str] = []
    for match in CITE_RE.finditer(text):
        values.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return values


def line_contains(path: Path, line_number: int, fragment: str) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    return 1 <= line_number <= len(lines) and fragment in lines[line_number - 1]


def expect_refs(
    source: dict[str, Any],
    field: str,
    expected_type: str,
    by_id: dict[str, dict[str, Any]],
    result: Validation,
) -> None:
    for identifier in source.get(field, []):
        target = by_id.get(identifier)
        result.require(target is not None, f"{source['stable_key']}.{field}: unresolved ID {identifier}")
        if target is not None:
            result.require(target["entity_type"] == expected_type, f"{source['stable_key']}.{field}: {identifier} is {target['entity_type']}, expected {expected_type}")


def semantic_validation(data: dict[str, Any], lane_root: Path, result: Validation) -> None:
    entities = all_entities(data)
    by_id = {entity["id"]: entity for entity in entities}
    by_key = {entity["stable_key"]: entity for entity in entities}
    result.require(len(by_id) == len(entities), "entity IDs are not unique")
    result.require(len(by_key) == len(entities), "stable keys are not unique")

    namespace_recorded = uuid_from_urn(data["id_namespace"]["namespace_uuid"])
    namespace_expected = uuid.uuid5(uuid.NAMESPACE_URL, data["id_namespace"]["name_root"])
    result.require(namespace_recorded == namespace_expected, "namespace UUID is not UUIDv5(URL namespace, name_root)")
    expected_dataset_id = "urn:uuid:" + str(uuid.uuid5(namespace_recorded, data["dataset_stable_key"]))
    result.require(data["dataset_id"] == expected_dataset_id, "dataset_id is not deterministic UUIDv5 of dataset_stable_key")
    for entity in entities:
        result.require(UUID_URN_RE.fullmatch(entity["id"]) is not None, f"{entity['stable_key']}: malformed UUIDv5 URN")
        expected = "urn:uuid:" + str(uuid.uuid5(namespace_recorded, entity["stable_key"]))
        result.require(entity["id"] == expected, f"{entity['stable_key']}: ID is not deterministic UUIDv5")

    expected_root_refs = [
        (data["course"], "program_id", data["program"]["id"]),
        (data["resource"], None, None),
        (data["edition"], "resource_id", data["resource"]["id"]),
        (data["unit"], "program_id", data["program"]["id"]),
        (data["unit"], "course_id", data["course"]["id"]),
        (data["unit"], "resource_id", data["resource"]["id"]),
        (data["unit"], "edition_id", data["edition"]["id"]),
    ]
    for entity, field, expected in expected_root_refs:
        if field is not None:
            result.require(entity[field] == expected, f"{entity['stable_key']}.{field}: incorrect root reference")

    expect_refs(data["course"], "prerequisite_ids", "prerequisite", by_id, result)
    expect_refs(data["resource"], "rights_component_ids", "rights", by_id, result)
    for field, expected_type in [
        ("section_ids", "section"),
        ("concept_ids", "concept"),
        ("prerequisite_ids", "prerequisite"),
        ("rights_component_ids", "rights"),
        ("citation_ids", "citation"),
        ("diagram_ids", "diagram"),
        ("index_entry_ids", "index_entry"),
        ("build_surface_ids", "build_surface"),
        ("qa_event_ids", "qa_event"),
    ]:
        expect_refs(data["unit"], field, expected_type, by_id, result)
    for section in data["sections"]:
        result.require(section["parent_id"] == data["unit"]["id"], f"{section['stable_key']}: parent is not Unit 001")
        expect_refs(section, "concept_ids", "concept", by_id, result)
        expect_refs(section, "prerequisite_ids", "prerequisite", by_id, result)
        expect_refs(section, "rights_component_ids", "rights", by_id, result)
    for citation in data["citations"]:
        result.require(by_id.get(citation["section_id"], {}).get("entity_type") == "section", f"{citation['stable_key']}: invalid section_id")
    for diagram in data["diagrams"]:
        result.require(by_id.get(diagram["section_id"], {}).get("entity_type") == "section", f"{diagram['stable_key']}: invalid section_id")
        result.require(by_id.get(diagram["rights_component_id"], {}).get("entity_type") == "rights", f"{diagram['stable_key']}: invalid rights_component_id")
    for entry in data["index_entries"]:
        result.require(by_id.get(entry["section_id"], {}).get("entity_type") == "section", f"{entry['stable_key']}: invalid section_id")
    for surface in data["build_surfaces"]:
        result.require(surface["unit_id"] == data["unit"]["id"], f"{surface['stable_key']}: invalid unit_id")
        expect_refs(surface, "rights_component_ids", "rights", by_id, result)
    for event in data["qa_events"]:
        result.require(event["unit_id"] == data["unit"]["id"], f"{event['stable_key']}: invalid unit_id")

    sections = sorted(data["sections"], key=lambda item: item["order"])
    result.require([item["order"] for item in sections] == list(range(1, len(sections) + 1)), "section order is not contiguous from 1")
    result.require(data["unit"]["section_ids"] == [item["id"] for item in sections], "unit.section_ids does not match ordered section records")
    for role in ("source_binding", "target_binding"):
        ranges = [(section[role]["line_start"], section[role]["line_end"]) for section in sections]
        result.require(all(ranges[index][1] < ranges[index + 1][0] for index in range(len(ranges) - 1)), f"section {role} ranges overlap or are unordered")

    counts = data["unit"]["surface_counts"]
    expected_counts = {
        "sections": len(data["sections"]),
        "exercises": 0,
        "hints": 0,
        "answers": 0,
        "solutions": 0,
        "citations": len(data["citations"]),
        "diagrams": len(data["diagrams"]),
        "index_entries": len(data["index_entries"]),
    }
    result.require(counts == expected_counts, f"unit.surface_counts mismatch: expected {expected_counts}, found {counts}")

    cache: dict[Path, tuple[int, str, list[str]]] = {}
    for where, binding in walk_bindings(data):
        validate_file_binding(binding, lane_root, result, where, cache)

    source_path = safe_lane_path(lane_root, data["unit"]["source_binding"]["path"], result, "unit.source_binding")
    target_path = safe_lane_path(lane_root, data["unit"]["target_binding"]["path"], result, "unit.target_binding")
    if source_path and target_path and source_path.is_file() and target_path.is_file():
        source_text = source_path.read_text(encoding="utf-8")
        target_text = target_path.read_text(encoding="utf-8")
        source_citations = sorted(set(parse_citations(source_text)))
        target_citations = sorted(set(parse_citations(target_text)))
        recorded_citations = sorted(item["bib_key"] for item in data["citations"])
        result.require(source_citations == recorded_citations, f"source citation closure mismatch: {source_citations} != {recorded_citations}")
        result.require(target_citations == recorded_citations, f"target citation closure mismatch: {target_citations} != {recorded_citations}")
        source_refs = sorted(set(REF_RE.findall(source_text)))
        target_refs = sorted(set(REF_RE.findall(target_text)))
        result.require(source_refs == target_refs, f"protected ref-key set drift: source={source_refs}, target={target_refs}")
        for citation in data["citations"]:
            needle = citation["bib_key"]
            result.require(line_contains(source_path, citation["source_line"], needle), f"{citation['stable_key']}: bib key absent from declared source line")
            result.require(line_contains(target_path, citation["target_line"], needle), f"{citation['stable_key']}: bib key absent from declared target line")
            bib_path = safe_lane_path(lane_root, citation["bibliography_path"], result, citation["stable_key"])
            if bib_path and bib_path.is_file():
                result.require(sha256_file(bib_path) == citation["bibliography_sha256"], f"{citation['stable_key']}: bibliography SHA-256 drift")
                bib_text = bib_path.read_text(encoding="utf-8")
                result.require(re.search(r"@\w+\s*\{\s*" + re.escape(needle) + r"\s*,", bib_text) is not None, f"{citation['stable_key']}: key missing from bibliography")

        for fmt in ("tikzcd", "tikzpicture"):
            source_count = source_text.count(f"\\begin{{{fmt}}}")
            target_count = target_text.count(f"\\begin{{{fmt}}}")
            records = sorted((item for item in data["diagrams"] if item["source_format"] == fmt), key=lambda item: item["source_occurrence_index"])
            result.require(source_count == len(records), f"source {fmt} count mismatch: {source_count} != {len(records)}")
            result.require(target_count == len(records), f"target {fmt} count mismatch: {target_count} != {len(records)}")
            result.require([item["source_occurrence_index"] for item in records] == list(range(1, len(records) + 1)), f"{fmt} occurrence indexes are not contiguous")
        result.require(sorted(item["ordinal_in_unit"] for item in data["diagrams"]) == list(range(1, len(data["diagrams"]) + 1)), "diagram ordinals are not contiguous")

        source_index = INDEX_RE.findall(source_text)
        target_index = INDEX_RE.findall(target_text)
        result.require([item["source_key"] for item in data["index_entries"]] == source_index, f"source index-entry provenance mismatch: {source_index}")
        result.require([item["target_key"] for item in data["index_entries"]] == target_index, f"target index-entry provenance mismatch: {target_index}")

    workflow = data["workflow"]
    if workflow["admission_state"] == "admitted":
        result.require(workflow["status"] == "admitted", "admitted workflow must have status=admitted")
        result.require(
            workflow["translation_state"] in {"visually_checked", "published"},
            "admitted workflow must be visually checked or published",
        )
        result.require(data["unit"]["admission_state"] == "admitted", "admitted workflow requires an admitted unit")
        result.require(
            data["unit"]["translation_state"] in {"visually_checked", "published"},
            "admitted unit must be visually checked or published",
        )
        for section in data["sections"]:
            result.require(section["admission_state"] == "admitted", f"{section['stable_key']}: admitted unit requires admitted sections")
            result.require(
                section["translation_state"] in {"visually_checked", "published"},
                f"{section['stable_key']}: admitted section must be visually checked or published",
            )
        for surface in data["build_surfaces"]:
            result.require(surface["status"] == "pass", f"{surface['stable_key']}: admitted unit requires a passed build")
            result.require(surface["artifact_path"] == surface["artifact_binding"]["path"], f"{surface['stable_key']}: artifact path/binding mismatch")
            result.require(surface["page_count"] > 0, f"{surface['stable_key']}: admitted build requires a positive page count")
        for event in data["qa_events"]:
            result.require(event["result"] == "pass", f"{event['stable_key']}: admitted unit requires passing QA")
            for field in ("translation_audit_state", "build_state", "visual_state"):
                result.require(event[field] == "pass", f"{event['stable_key']}: {field} must pass before admission")
    else:
        result.require(workflow["status"] == "candidate", "non-admitted workflow must have status=candidate")
        result.require(data["unit"]["admission_state"] == "not_admitted", "non-admitted workflow requires a non-admitted unit")


def localized_label(entity: dict[str, Any], locale: str = "id-ID") -> str:
    candidates = entity.get("titles") or entity.get("labels") or []
    for item in candidates:
        if item.get("language") == locale:
            return item.get("text", "")
    if candidates:
        return candidates[0].get("text", "")
    return entity.get("label") or entity.get("component") or entity.get("bib_key") or entity["stable_key"].rsplit("/", 1)[-1]


def csv_payload(fieldnames: list[str], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: "" if value is None else value for key, value in row.items()})
    return stream.getvalue().encode("utf-8")


def render_csvs(data: dict[str, Any]) -> dict[str, bytes]:
    entities = all_entities(data)
    by_id = {entity["id"]: entity for entity in entities}
    namespace = uuid_from_urn(data["id_namespace"]["namespace_uuid"])
    unit_status = f"{data['workflow']['status']}:{data['workflow']['admission_state']}"

    parent_by_type = {
        "course": data["program"]["id"],
        "edition": data["resource"]["id"],
        "unit": data["edition"]["id"],
    }
    entity_rows: list[dict[str, Any]] = []
    for entity in entities:
        entity_type = entity["entity_type"]
        parent = entity.get("parent_id") or entity.get("section_id") or entity.get("unit_id") or parent_by_type.get(entity_type, "")
        order = entity.get("order") or entity.get("ordinal_in_unit") or ""
        status = unit_status
        if entity_type == "rights":
            status = "applies" if entity["applies_to_unit"] else "retained_not_used_by_unit"
        elif entity_type == "build_surface":
            status = entity["status"]
        elif entity_type == "qa_event":
            status = entity["result"]
        entity_rows.append({
            "entity_type": entity_type,
            "id": entity["id"],
            "stable_key": entity["stable_key"],
            "parent_id": parent,
            "order": order,
            "label_id": localized_label(entity),
            "status": status,
        })
    entity_rows.sort(key=lambda row: (row["entity_type"], row["stable_key"]))

    relation_rows: list[dict[str, Any]] = []

    def add_relation(source_id: str, predicate: str, target_id: str, evidence: str = "") -> None:
        source_key = by_id[source_id]["stable_key"]
        target_key = by_id[target_id]["stable_key"]
        relation_key = f"relation/{source_key}/{predicate}/{target_key}"
        relation_rows.append({
            "relation_id": "urn:uuid:" + str(uuid.uuid5(namespace, relation_key)),
            "relation_key": relation_key,
            "source_id": source_id,
            "predicate": predicate,
            "target_id": target_id,
            "evidence": evidence,
        })

    add_relation(data["program"]["id"], "contains", data["course"]["id"])
    add_relation(data["course"]["id"], "uses-resource", data["resource"]["id"])
    add_relation(data["resource"]["id"], "has-edition", data["edition"]["id"])
    add_relation(data["edition"]["id"], "contains", data["unit"]["id"], data["unit"]["source_local_id"])
    for prerequisite_id in data["course"]["prerequisite_ids"]:
        add_relation(data["course"]["id"], "requires", prerequisite_id, "prelude.tex:49-60")
    for section in data["sections"]:
        add_relation(data["unit"]["id"], "contains", section["id"], section["source_local_id"])
        for concept_id in section["concept_ids"]:
            add_relation(section["id"], "covers", concept_id, section["source_local_id"])
        for prerequisite_id in section["prerequisite_ids"]:
            add_relation(section["id"], "requires", prerequisite_id, section["source_local_id"])
        for rights_id in section["rights_component_ids"]:
            add_relation(section["id"], "governed-by", rights_id)
    for concept_id in data["unit"]["concept_ids"]:
        add_relation(data["unit"]["id"], "covers", concept_id)
    for prerequisite_id in data["unit"]["prerequisite_ids"]:
        add_relation(data["unit"]["id"], "requires", prerequisite_id, "prelude.tex:49-60")
    for rights_id in data["unit"]["rights_component_ids"]:
        add_relation(data["unit"]["id"], "governed-by", rights_id)
    for citation in data["citations"]:
        add_relation(citation["section_id"], "cites", citation["id"], f"prelude.tex:{citation['source_line']}")
    for diagram in data["diagrams"]:
        add_relation(diagram["section_id"], "includes-diagram", diagram["id"], f"prelude.tex:{diagram['source_binding']['line_start']}-{diagram['source_binding']['line_end']}")
        add_relation(diagram["id"], "governed-by", diagram["rights_component_id"])
    for entry in data["index_entries"]:
        add_relation(entry["section_id"], "indexes", entry["id"], f"prelude.tex:{entry['source_binding']['line_start']}")
    for surface in data["build_surfaces"]:
        add_relation(data["unit"]["id"], "built-by", surface["id"])
        for rights_id in surface["rights_component_ids"]:
            add_relation(surface["id"], "governed-by", rights_id)
    for event in data["qa_events"]:
        add_relation(data["unit"]["id"], "checked-by", event["id"])
    relation_rows.sort(key=lambda row: row["relation_key"])

    binding_rows: list[dict[str, Any]] = []

    def add_binding(owner_id: str, role: str, binding: dict[str, Any], language: str = "") -> None:
        binding_rows.append({
            "owner_id": owner_id,
            "binding_role": role,
            "language": language,
            "path": binding["path"],
            "line_start": binding.get("line_start", ""),
            "line_end": binding.get("line_end", ""),
            "bytes": binding["bytes"],
            "sha256": binding["sha256"],
            "span_sha256": binding.get("span_sha256", ""),
            "span_hash_algorithm": binding.get("span_hash_algorithm", ""),
        })

    for role in ("archive", "official_pdf", "source_manifest"):
        add_binding(data["edition"]["id"], role, data["edition"][role])
    add_binding(data["unit"]["id"], "source", data["unit"]["source_binding"], data["unit"]["source_language"])
    add_binding(data["unit"]["id"], "target", data["unit"]["target_binding"], data["unit"]["target_language"])
    for section in data["sections"]:
        add_binding(section["id"], "source", section["source_binding"], data["unit"]["source_language"])
        add_binding(section["id"], "target", section["target_binding"], data["unit"]["target_language"])
    for rights in data["rights"]:
        for binding in rights["bindings"]:
            add_binding(rights["id"], "rights-component", binding)
    for diagram in data["diagrams"]:
        add_binding(diagram["id"], "source", diagram["source_binding"], data["unit"]["source_language"])
        add_binding(diagram["id"], "target", diagram["target_binding"], data["unit"]["target_language"])
    for entry in data["index_entries"]:
        add_binding(entry["id"], "source", entry["source_binding"], data["unit"]["source_language"])
        add_binding(entry["id"], "target", entry["target_binding"], data["unit"]["target_language"])
    for surface in data["build_surfaces"]:
        add_binding(surface["id"], "driver", surface["driver"])
        add_binding(surface["id"], "build-script", surface["build_script"])
        add_binding(surface["id"], "build-artifact", surface["artifact_binding"])
        add_binding(surface["id"], "build-log", surface["log_binding"])
        for binding in surface["input_bindings"]:
            add_binding(surface["id"], "build-input", binding)
    for event in data["qa_events"]:
        add_binding(event["id"], "qa-witness", event["witness_binding"])
    binding_rows.sort(key=lambda row: (row["owner_id"], row["binding_role"], row["path"], str(row["line_start"])))

    rights_rows = [
        {
            "id": item["id"],
            "stable_key": item["stable_key"],
            "component": item["component"],
            "holder_or_source": item["holder_or_source"],
            "license": item["license"],
            "applies_to_unit": str(item["applies_to_unit"]).lower(),
            "required_treatment": item["required_treatment"],
        }
        for item in sorted(data["rights"], key=lambda value: value["stable_key"])
    ]

    surface_rows: list[dict[str, Any]] = []
    for citation in data["citations"]:
        surface_rows.append({"entity_type": "citation", "id": citation["id"], "stable_key": citation["stable_key"], "section_id": citation["section_id"], "ordinal": "", "source_value": citation["bib_key"], "target_value": citation["bib_key"], "format": "biblatex-key", "status": "preserved"})
    for diagram in data["diagrams"]:
        surface_rows.append({"entity_type": "diagram", "id": diagram["id"], "stable_key": diagram["stable_key"], "section_id": diagram["section_id"], "ordinal": diagram["ordinal_in_unit"], "source_value": f"{diagram['source_binding']['line_start']}-{diagram['source_binding']['line_end']}", "target_value": f"{diagram['target_binding']['line_start']}-{diagram['target_binding']['line_end']}", "format": diagram["source_format"], "status": diagram["state"]})
    for entry in data["index_entries"]:
        surface_rows.append({"entity_type": "index_entry", "id": entry["id"], "stable_key": entry["stable_key"], "section_id": entry["section_id"], "ordinal": entry["ordinal_in_unit"], "source_value": entry["source_key"], "target_value": entry["target_key"], "format": "latex-index-key", "status": entry["provenance_state"]})
    for surface in data["build_surfaces"]:
        surface_rows.append({"entity_type": "build_surface", "id": surface["id"], "stable_key": surface["stable_key"], "section_id": "", "ordinal": "", "source_value": surface["command"], "target_value": surface["artifact_path"], "format": surface["kind"], "status": surface["status"]})
    surface_rows.sort(key=lambda row: (row["entity_type"], row["stable_key"]))

    qa_rows = [
        {
            "id": item["id"],
            "stable_key": item["stable_key"],
            "unit_id": item["unit_id"],
            "check_type": item["check_type"],
            "result": item["result"],
            "scope": item["scope"],
            "witness": item["witness"],
            "translation_audit_state": item["translation_audit_state"],
            "build_state": item["build_state"],
            "visual_state": item["visual_state"],
        }
        for item in sorted(data["qa_events"], key=lambda value: value["stable_key"])
    ]

    return {
        "unit-001-entities.csv": csv_payload(["entity_type", "id", "stable_key", "parent_id", "order", "label_id", "status"], entity_rows),
        "unit-001-relations.csv": csv_payload(["relation_id", "relation_key", "source_id", "predicate", "target_id", "evidence"], relation_rows),
        "unit-001-bindings.csv": csv_payload(["owner_id", "binding_role", "language", "path", "line_start", "line_end", "bytes", "sha256", "span_sha256", "span_hash_algorithm"], binding_rows),
        "unit-001-rights.csv": csv_payload(["id", "stable_key", "component", "holder_or_source", "license", "applies_to_unit", "required_treatment"], rights_rows),
        "unit-001-surfaces.csv": csv_payload(["entity_type", "id", "stable_key", "section_id", "ordinal", "source_value", "target_value", "format", "status"], surface_rows),
        "unit-001-qa.csv": csv_payload(["id", "stable_key", "unit_id", "check_type", "result", "scope", "witness", "translation_audit_state", "build_state", "visual_state"], qa_rows),
    }


def main() -> int:
    script_path = Path(__file__).resolve()
    lane_root_default = script_path.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane-root", type=Path, default=lane_root_default)
    parser.add_argument("--schema", type=Path, default=lane_root_default / "backend" / "schema" / "open-math-corpus-unit.schema.v1.json")
    parser.add_argument("--data", type=Path, default=lane_root_default / "backend" / "data" / "unit-001-pendahuluan.json")
    parser.add_argument("--csv-dir", type=Path, default=lane_root_default / "backend" / "csv")
    parser.add_argument("--write-csv", action="store_true", help="write deterministic CSV projections after validation")
    parser.add_argument(
        "--refresh-derivative-bindings",
        action="store_true",
        help="explicitly refresh repo/ byte and span hashes before validation; authority bindings are never changed",
    )
    args = parser.parse_args()

    result = Validation()
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        data = json.loads(args.data.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to load backend inputs: {exc}", file=sys.stderr)
        return 2

    if args.refresh_derivative_bindings:
        refresh_result = Validation()
        refresh_derivative_bindings(data, args.lane_root.resolve(), refresh_result)
        if refresh_result.errors:
            for error in refresh_result.errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        args.data.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    validate_against_schema(data, schema, schema, "$", result)
    if not result.errors:
        semantic_validation(data, args.lane_root.resolve(), result)

    csvs: dict[str, bytes] = {}
    if not result.errors:
        csvs = render_csvs(data)
        if args.write_csv:
            args.csv_dir.mkdir(parents=True, exist_ok=True)
            for name, payload in csvs.items():
                (args.csv_dir / name).write_bytes(payload)
        else:
            for name, expected in csvs.items():
                path = args.csv_dir / name
                if not path.is_file():
                    result.errors.append(f"missing deterministic CSV projection: {path}")
                    continue
                actual = path.read_bytes()
                if actual != expected:
                    result.errors.append(f"CSV projection drift: {path}; rerun with --write-csv after reviewing JSON changes")

    if result.errors:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAILED: {len(result.errors)} backend validation error(s)", file=sys.stderr)
        return 1

    report = {
        "result": "pass",
        "schema": {"path": str(args.schema), "bytes": args.schema.stat().st_size, "sha256": sha256_file(args.schema)},
        "data": {"path": str(args.data), "bytes": args.data.stat().st_size, "sha256": sha256_file(args.data)},
        "validator": {"path": str(script_path), "bytes": script_path.stat().st_size, "sha256": sha256_file(script_path)},
        "entity_count": len(all_entities(data)),
        "section_count": len(data["sections"]),
        "concept_count": len(data["concepts"]),
        "prerequisite_count": len(data["prerequisites"]),
        "citation_count": len(data["citations"]),
        "diagram_count": len(data["diagrams"]),
        "index_entry_count": len(data["index_entries"]),
        "csv": [
            {"path": str(args.csv_dir / name), "bytes": len(payload), "sha256": sha256_bytes(payload)}
            for name, payload in sorted(csvs.items())
        ],
        "workflow_state": data["workflow"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
