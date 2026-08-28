#!/usr/bin/env python3
"""Generate and validate the compact modular backend for O013 Li Unit 035."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
import sys
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
TEMPLATE = ROOT / "backend/data/unit-034-bab-4-limit-dan-kompletisasi-grup.json"
SOURCE = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = ROOT / "build/unit-035-candidate/chapter4-groups-in-categories-and-exercises-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
DELTA = ROOT / "build/unit-035-staging/terminology-delta.csv"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
ARTIFACT = ROOT / "artifacts/unit-035-bab-4-grup-dalam-kategori-dan-latihan-id.pdf"
BUILD_LOG = ROOT / "qa/UNIT_035_BUILD_FINAL.log"
REVIEW = ROOT / "qa/UNIT_035_TRANSLATION_REVIEW_20260825.md"
VISUAL = ROOT / "qa/UNIT_035_VISUAL_QA_20260828.md"
RENDER_INVENTORY = ROOT / "qa/unit-035-evidence/render-hash-inventory.json"
DRIVER = ROOT / "repo/source/unit-035-bab-4-grup-dalam-kategori-dan-latihan.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-035.tex"
CROSSREF = ROOT / "repo/source/unit-035-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_035.ps1"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_035_candidate.py"
OUTPUT = ROOT / "backend/data/unit-035-bab-4-grup-dalam-kategori-dan-latihan.json"
VALIDATION = ROOT / "qa/unit-035-evidence/backend-validation.json"
CSV_PATHS = {
    name: ROOT / f"backend/csv/unit-035-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
}

NAMESPACE = uuid.UUID("5d74a443-839a-5a09-b2c6-0bc48a097f2b")
UNIT_KEY = "unit/bab-4-grup-dalam-kategori-dan-latihan"
SECTION_KEYS = (f"{UNIT_KEY}/section/01", f"{UNIT_KEY}/section/02")
CRITICAL = {
    SOURCE: (154744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"),
    CANDIDATE: (18089, "5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca"),
    TARGET: (193626, "2b682d67292e4c439ccc9f6d46f72d3d0eb7cb5bf8b3a3a5999210c45ef547c5"),
    DELTA: (1841, "4575404e7c19740e2cbef2f5c70ff712df0774962483d1705cea13ef126002f9"),
    GLOSSARY: (84385, "933c064ca77fe92a19742e4df72b088bd81e3db9ff8db62740516a6389478d6d"),
    ARTIFACT: (135943, "1cf97dd523ae1a8c5185c4b22a8e6b0dab6e7514ab5387c34959c417f4e35442"),
    BUILD_LOG: (87586, "1b87602c47d5b602a71b788ea14a18f10f4816ae1c0522bbd828dc51b02a2a7a"),
    SCHEMA: (21358, "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3"),
}


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def identity(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), sha(payload)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def uid(key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(NAMESPACE, key))


def file_binding(path: Path) -> dict[str, object]:
    size, digest = identity(path)
    return {"path": rel(path), "bytes": size, "sha256": digest}


def span_payload(path: Path, first: int, last: int) -> bytes:
    text = path.read_text(encoding="utf-8")
    require("\r" not in text, f"CR line ending forbidden: {rel(path)}")
    lines = text.splitlines()
    require(1 <= first <= last <= len(lines), f"invalid span {rel(path)}:{first}-{last}")
    return ("\n".join(lines[first - 1 : last]) + "\n").encode("utf-8")


def line_binding(path: Path, first: int, last: int) -> dict[str, object]:
    base = file_binding(path)
    base.update(
        {
            "line_start": first,
            "line_end": last,
            "span_sha256": sha(span_payload(path, first, last)),
            "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
        }
    )
    return base


def label(language: str, text: str) -> dict[str, str]:
    return {"language": language, "text": text}


def entity(key: str, kind: str, text: str, *, Indonesian: str | None = None) -> dict[str, object]:
    labels = [label("en", text)]
    if Indonesian is not None:
        labels.append(label("id-ID", Indonesian))
    return {"id": uid(key), "stable_key": key, "entity_type": kind, "labels": labels}


def csv_bytes(fieldnames: list[str], rows: list[dict[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def topology(candidate_text: str) -> dict[str, int]:
    begin = re.findall(r"\\begin\{([^{}]+)\}", candidate_text)
    end = re.findall(r"\\end\{([^{}]+)\}", candidate_text)
    require(len(begin) == len(end) == 30, "environment-pair census drift")
    require(len(re.findall(r"\\label\{[^{}]+\}", candidate_text)) == 3, "label census drift")
    require(len(re.findall(r"\\(?:eqref|ref)\{[^{}]+\}", candidate_text)) == 15, "reference census drift")
    require(candidate_text.count(r"\begin{tikzcd}") == 8, "diagram census drift")
    require(len(re.findall(r"\\arrow", candidate_text)) == 35, "diagram-arrow census drift")
    require(len(re.findall(r"\\item\b", candidate_text)) == 41, "item census drift")
    require(candidate_text.count(r"\begin{hint}") == 5, "hint census drift")
    require(len(re.findall(r"\\index(?:\[[^]]+\])?\{", candidate_text)) == 2, "index census drift")
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_unit_035_candidate as checker  # type: ignore

    zones = checker.math_zones(candidate_text)
    require(len(zones) == 247, "protected-math census drift")
    exercise = candidate_text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    top = sum(1 for line in exercise.splitlines() if re.match(r"^\t\\item\b", line))
    require(top == 26 and len(re.findall(r"\\item\b", exercise)) == 36, "exercise census drift")
    return {
        "environment_pairs": 30,
        "labels": 3,
        "references": 15,
        "external_references": 14,
        "protected_math_zones": 247,
        "diagrams": 8,
        "diagram_arrows": 35,
        "list_items": 41,
        "top_level_exercises": 26,
        "exercise_items": 36,
        "hints": 5,
        "indexes": 2,
    }


def make_backend() -> tuple[dict[str, object], dict[str, bytes], dict[str, object]]:
    for path, expected in CRITICAL.items():
        require(identity(path) == expected, f"critical identity drift: {rel(path)}")
    source_span = span_payload(SOURCE, 1745, 1898)
    target_span = span_payload(TARGET, 1740, 1893)
    candidate_bytes = CANDIDATE.read_bytes()
    require(target_span == candidate_bytes, "canonical target span differs from candidate")
    require((len(source_span), sha(source_span)) == (14398, "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287"), "source span drift")
    counts = topology(candidate_bytes.decode("utf-8"))

    with DELTA.open(encoding="utf-8", newline="") as handle:
        terms = list(csv.DictReader(handle))
    require(len(terms) == 11 and all(row["status"] == "admitted" for row in terms), "terminology delta drift")

    base = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    program = copy.deepcopy(base["program"])
    course = copy.deepcopy(base["course"])
    resource = copy.deepcopy(base["resource"])
    edition = copy.deepcopy(base["edition"])
    prerequisites = copy.deepcopy(base["prerequisites"])
    rights = copy.deepcopy(base["rights"])

    unit_id = uid(UNIT_KEY)
    sections = [
        {
            "id": uid(SECTION_KEYS[0]), "stable_key": SECTION_KEYS[0], "entity_type": "section",
            "parent_id": unit_id, "order": 1, "source_local_id": "chapter4.tex:1745-1844",
            "titles": [label("zh-Hans", "范畴中的群"), label("id-ID", "Grup dalam Kategori")],
            "source_binding": line_binding(SOURCE, 1745, 1844), "target_binding": line_binding(TARGET, 1740, 1839),
            "concept_ids": [], "prerequisite_ids": [], "rights_component_ids": [uid("rights/principal-cc-by-4.0")],
            "translation_state": "visually_checked", "admission_state": "admitted",
        },
        {
            "id": uid(SECTION_KEYS[1]), "stable_key": SECTION_KEYS[1], "entity_type": "section",
            "parent_id": unit_id, "order": 2, "source_local_id": "chapter4.tex:1845-1898",
            "titles": [label("zh-Hans", "第四章习题"), label("id-ID", "Latihan Bab 4")],
            "source_binding": line_binding(SOURCE, 1845, 1898), "target_binding": line_binding(TARGET, 1840, 1893),
            "concept_ids": [], "prerequisite_ids": [], "rights_component_ids": [uid("rights/principal-cc-by-4.0")],
            "translation_state": "visually_checked", "admission_state": "admitted",
        },
    ]

    concepts: list[dict[str, object]] = []
    for row in terms:
        key = "concept/term/" + re.sub(r"[^a-z0-9]+", "-", row["source_term"].lower()).strip("-")
        concepts.append(entity(key, "concept", row["source_term"], Indonesian=row["target_term"]))
    occurrence_labels = {
        "environment": "lingkungan",
        "label": "label",
        "reference": "rujukan",
        "formula": "rumus",
        "list-item": "butir daftar",
        "exercise": "latihan",
        "hint": "petunjuk",
        "correction": "koreksi",
    }
    for kind, count in (
        ("environment", 30), ("label", 3), ("reference", 15), ("formula", 247),
        ("list-item", 41), ("exercise", 26), ("hint", 5), ("correction", 1),
    ):
        for number in range(1, count + 1):
            key = f"surface/unit-035/{kind}/{number:03d}"
            concepts.append(
                entity(
                    key,
                    "concept",
                    f"Unit 035 {kind} occurrence {number:03d}",
                    Indonesian=f"Unit 035 kemunculan {occurrence_labels[kind]} {number:03d}",
                )
            )
    sections[0]["concept_ids"] = [item["id"] for item in concepts if "/exercise/" not in item["stable_key"] and "/hint/" not in item["stable_key"]]
    sections[1]["concept_ids"] = [item["id"] for item in concepts if "/exercise/" in item["stable_key"] or "/hint/" in item["stable_key"]]

    source_diagrams = [(1759, 1762), (1765, 1769), (1771, 1775), (1781, 1781), (1784, 1784), (1778, 1787), (1809, 1814), (1837, 1840)]
    target_diagrams = [(1754, 1757), (1760, 1764), (1766, 1770), (1776, 1776), (1779, 1779), (1773, 1782), (1804, 1809), (1832, 1835)]
    diagrams = []
    for ordinal, (source_range, target_range) in enumerate(zip(source_diagrams, target_diagrams), 1):
        key = f"diagram/unit-035/tikzcd-{ordinal:02d}"
        diagrams.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "diagram", "section_id": sections[0]["id"],
                "ordinal_in_unit": ordinal, "source_format": "tikzcd", "source_occurrence_index": ordinal,
                "source_binding": line_binding(SOURCE, *source_range), "target_binding": line_binding(TARGET, *target_range),
                "rights_component_id": uid("rights/principal-cc-by-4.0"), "state": "audited_preserved",
            }
        )

    index_entries = []
    for ordinal, (source_line, target_line, source_key, target_key) in enumerate(
        [
            (1750, 1745, "duixiang!群对象 (group object)", "duixiang!objek grup (group object)"),
            (1855, 1850, "zitonggou!外自同构 (outer automorphism)", "zitonggou!automorfisme luar (outer automorphism)"),
        ], 1,
    ):
        key = f"index-entry/unit-035/main/{ordinal:03d}"
        index_entries.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "index_entry", "section_id": sections[0 if ordinal == 1 else 1]["id"],
                "ordinal_in_unit": ordinal, "source_key": source_key, "target_key": target_key,
                "source_binding": line_binding(SOURCE, source_line, source_line), "target_binding": line_binding(TARGET, target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    rights_by_key = {record["stable_key"]: record for record in rights}
    principal_id = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    for record in rights:
        if record["stable_key"] == "rights/principal-cc-by-4.0":
            record["bindings"] = [file_binding(SOURCE), file_binding(CANDIDATE), file_binding(TARGET), file_binding(ROOT / "repo/source/LICENSE")]
        elif record["stable_key"] == "rights/ajbook-fragment-cc-by-sa-3.0":
            record["bindings"] = [file_binding(ROOT / "repo/source/AJbook.cls")]
        elif record["stable_key"] == "rights/noto-fonts-ofl-1.1":
            record["bindings"] = [file_binding(ROOT / "repo/fonts/OFL-1.1-Noto-CJK.txt")]
        elif record["stable_key"] == "rights/fandol-gpl-3.0-with-font-exception":
            record["bindings"] = [file_binding(ROOT / "repo/fonts/FANDOL-AUTHORITY.json"), file_binding(ROOT / "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt"), file_binding(ARTIFACT)]
        elif record["stable_key"] == "rights/lanzhou-cc-by-sa-3.0":
            record["bindings"] = [file_binding(ROOT / "repo/source/Lanzhou.png")]
            record["applies_to_unit"] = False
    require(len(rights) == 5, "rights-component census drift")

    surface_key = "build-surface/unit-035-pdf"
    surface = {
        "id": uid(surface_key), "stable_key": surface_key, "entity_type": "build_surface", "unit_id": unit_id,
        "kind": "pdf", "working_directory": ".", "command": "pwsh -NoProfile -File scripts/build_unit_035.ps1 -OutputDirectory build/unit-035-replay",
        "artifact_path": rel(ARTIFACT), "artifact_binding": file_binding(ARTIFACT), "log_binding": file_binding(BUILD_LOG),
        "build_script": file_binding(BUILD_SCRIPT), "page_count": 9, "status": "pass", "driver": file_binding(DRIVER),
        "input_bindings": [file_binding(COVER), file_binding(TARGET), file_binding(CROSSREF), file_binding(ROOT / "repo/source/AJbook.cls")],
        "external_dependencies": ["XeLaTeX", "Biber", "makeindex", "Poppler", "Noto CJK fonts", "Fandol 0.3 toolchain fonts"],
        "rights_component_ids": [
            principal_id,
            rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
            rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
            rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"],
        ],
    }

    qa_specs = [
        ("candidate", "admission_gate", REVIEW, "Exact source/target topology, protected mathematics, identifiers, exercises, hints, terminology, and correction pass."),
        ("structure", "backend_integrity", CANDIDATE_CHECKER, f"Topology pass: {json.dumps(counts, sort_keys=True)}"),
        ("build", "backend_integrity", BUILD_LOG, "Hash-gated XeLaTeX/Biber/makeindex build passes with no unresolved reference or citation."),
        ("visual", "backend_integrity", VISUAL, "All nine pages inspected; diagrams, exercises, hints, cover, rights notice, and index are legible and unclipped."),
        ("render", "backend_integrity", RENDER_INVENTORY, "Nine deterministic 120-dpi page renders and contact-sheet inventory bind the published reader."),
        ("rights", "backend_integrity", COVER, "Five component-rights records remain separate; attribution, changes, non-endorsement, and model provenance are explicit."),
        ("correction", "backend_integrity", REVIEW, "O013-LI-U035-COR-001 swaps the erroneous Neumann family-index bounds at authority line 1858 / target line 1853."),
    ]
    qa_events = []
    for order, (slug, check_type, witness, scope) in enumerate(qa_specs, 1):
        key = f"qa/unit-035/{order:02d}-{slug}"
        qa_events.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "qa_event", "unit_id": unit_id,
                "check_type": check_type, "result": "pass", "scope": scope, "witness": rel(witness),
                "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass",
                "witness_binding": file_binding(witness),
            }
        )

    rights_ids = [
        principal_id,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
        rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
        rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"],
    ]
    unit = {
        "id": unit_id, "stable_key": UNIT_KEY, "entity_type": "unit", "program_id": program["id"], "course_id": course["id"],
        "resource_id": resource["id"], "edition_id": edition["id"], "order": 35,
        "source_local_id": "chapter4.tex:1745-1898; complete Section 4.11 and Chapter 4 Exercises",
        "titles": [label("zh-Hans", "范畴中的群与第四章习题"), label("id-ID", "Grup dalam Kategori dan Latihan Bab 4")],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": line_binding(SOURCE, 1745, 1898), "target_binding": line_binding(TARGET, 1740, 1893),
        "section_ids": [item["id"] for item in sections], "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [item["id"] for item in prerequisites], "rights_component_ids": rights_ids,
        "citation_ids": [], "diagram_ids": [item["id"] for item in diagrams], "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [surface["id"]], "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": ["group-objects", "group-functors", "chapter-4-exercises", "chapter-4-completion"],
        "surface_counts": {"sections": 2, "exercises": 26, "hints": 5, "answers": 0, "solutions": 0, "citations": 0, "diagrams": 8, "index_entries": 2},
        "translation_state": "visually_checked", "admission_state": "admitted",
    }

    document = {
        "$schema": "../schema/open-math-corpus-unit.schema.v1.json", "schema_name": "open-math-corpus-unit", "schema_version": "1.1.0",
        "profile": "curriculum-modular-backend-v0", "dataset_id": uid("dataset/unit-035/id-id"), "dataset_stable_key": "dataset/unit-035/id-id",
        "id_namespace": copy.deepcopy(base["id_namespace"]),
        "workflow": {"responsible_task": uid("task/o013-li-u035-backend"), "updated": "2026-08-28", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_math_backend_build_visual_pass"},
        "program": program, "course": course, "resource": resource, "edition": edition, "unit": unit,
        "sections": sections, "concepts": concepts, "prerequisites": prerequisites, "rights": rights,
        "citations": [], "diagrams": diagrams, "index_entries": index_entries, "build_surfaces": [surface], "qa_events": qa_events,
    }

    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(document)
    all_entities = [program, course, resource, edition, unit, *sections, *concepts, *prerequisites, *rights, *diagrams, *index_entries, surface, *qa_events]
    ids = [item["id"] for item in all_entities]
    require(len(ids) == len(set(ids)) and all(item["id"] == uid(item["stable_key"]) for item in all_entities), "UUIDv5 identity drift")
    require(set(unit["section_ids"]) == {item["id"] for item in sections}, "section closure drift")
    require(set(unit["concept_ids"]) == {item["id"] for item in concepts}, "concept closure drift")

    def binding_row(owner_key: str, kind: str, binding: dict[str, object]) -> dict[str, object]:
        return {
            "owner_key": owner_key,
            "kind": kind,
            "path": binding["path"],
            "bytes": binding["bytes"],
            "sha256": binding["sha256"],
            "line_start": binding.get("line_start", ""),
            "line_end": binding.get("line_end", ""),
            "span_sha256": binding.get("span_sha256", ""),
        }

    bindings: list[dict[str, object]] = []
    for owner in [unit, *sections, *diagrams, *index_entries]:
        for field in ("source_binding", "target_binding"):
            if field in owner:
                binding = owner[field]
                bindings.append(binding_row(owner["stable_key"], field, binding))
    for owner in [surface, *qa_events, *rights]:
        candidates = []
        if "artifact_binding" in owner: candidates.append(("artifact_binding", owner["artifact_binding"]))
        if "log_binding" in owner: candidates.append(("log_binding", owner["log_binding"]))
        if "build_script" in owner: candidates.append(("build_script", owner["build_script"]))
        if "driver" in owner: candidates.append(("driver", owner["driver"]))
        if "witness_binding" in owner: candidates.append(("witness_binding", owner["witness_binding"]))
        candidates += [("input_binding", value) for value in owner.get("input_bindings", [])]
        candidates += [("rights_binding", value) for value in owner.get("bindings", [])]
        for kind, binding in candidates:
            bindings.append(binding_row(owner["stable_key"], kind, binding))

    entity_rows = [{"id": item["id"], "stable_key": item["stable_key"], "entity_type": item["entity_type"], "label": (item.get("label") or item.get("component") or (item.get("labels") or item.get("titles") or [{"text": ""}])[-1]["text"])} for item in all_entities]
    relation_rows: list[dict[str, object]] = []
    for field in ("section_ids", "concept_ids", "prerequisite_ids", "rights_component_ids", "diagram_ids", "index_entry_ids", "build_surface_ids", "qa_event_ids"):
        for object_id in unit.get(field, []): relation_rows.append({"relation": field, "subject_id": unit_id, "object_id": object_id})
    qa_rows = [{"id": item["id"], "stable_key": item["stable_key"], "check_type": item["check_type"], "result": item["result"], "witness": item["witness"]} for item in qa_events]
    rights_rows = [{"id": item["id"], "stable_key": item["stable_key"], "component": item["component"], "license": item["license"], "applies_to_unit": str(item["applies_to_unit"]).lower()} for item in rights]
    surface_rows = [{"id": surface["id"], "stable_key": surface["stable_key"], "kind": surface["kind"], "path": surface["artifact_path"], "bytes": surface["artifact_binding"]["bytes"], "sha256": surface["artifact_binding"]["sha256"]}]
    import validate_backend as backend_validator  # type: ignore

    rendered_csvs = backend_validator.render_csvs(document)
    csv_outputs = {
        name: rendered_csvs[f"unit-035-{name}.csv"]
        for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
    }

    validation = {
        "schema": "o013-unit-backend-validation-v1", "unit": "O013-LI-U035", "result": "pass", "generated": "2026-08-28",
        "authority": {"range": "chapter4.tex:1745-1898", "bytes": len(source_span), "sha256": sha(source_span)},
        "target": {"range": "chapter4.tex:1740-1893", "bytes": len(target_span), "sha256": sha(target_span), "candidate_identical": True},
        "topology": counts, "terminology_rows": 11, "corrections": ["O013-LI-U035-COR-001"],
        "rights_components": 5, "schema_validation": "pass", "uuidv5_uniqueness": "pass", "reference_closure": "pass",
        "json_entities": len(all_entities), "csv_projections": 6,
    }
    return document, csv_outputs, validation


def encode_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate current generated bytes without rewriting")
    args = parser.parse_args()
    document, csv_outputs, validation = make_backend()
    json_bytes = encode_json(document)
    validation["backend"] = {"path": rel(OUTPUT), "bytes": len(json_bytes), "sha256": sha(json_bytes)}
    validation["csv"] = {name: {"path": rel(CSV_PATHS[name]), "bytes": len(payload), "sha256": sha(payload)} for name, payload in csv_outputs.items()}
    validation["generator"] = file_binding(Path(__file__))
    validation_bytes = encode_json(validation)
    expected = {OUTPUT: json_bytes, VALIDATION: validation_bytes, **{CSV_PATHS[name]: payload for name, payload in csv_outputs.items()}}
    if args.check:
        for path, payload in expected.items():
            require(path.is_file() and path.read_bytes() == payload, f"generated output drift: {rel(path)}")
        print(json.dumps({"result": "PASS", "backend": validation["backend"], "csv_projections": 6, "entities": validation["json_entities"]}, indent=2))
        return 0
    for path, payload in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(json.dumps({"result": "PASS_WRITTEN", "backend": validation["backend"], "validation": {"path": rel(VALIDATION), "bytes": len(validation_bytes), "sha256": sha(validation_bytes)}, "csv_projections": 6, "entities": validation["json_entities"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
