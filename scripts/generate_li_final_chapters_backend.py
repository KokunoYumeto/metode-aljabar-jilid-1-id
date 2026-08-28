#!/usr/bin/env python3
"""Generate deterministic modular backends for complete Li Chapters 7--10."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_unit_043_backend as common
import validate_backend as backend_validator


SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
TEMPLATE = ROOT / "backend/data/unit-044-bab-6-teori-modul.json"
AUTHORITY_ROOT = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
FINAL_PDF = ROOT / "artifacts/metode-aljabar-jilid-1-id-lengkap.pdf"
BUILD_LOG = ROOT / "qa/LI_COMPLETE_BUILD_FINAL.log"
TRANSLATION_FREEZE = ROOT / "qa/LI_COMPLETE_TRANSLATION_FREEZE.json"
VISUAL_QA = ROOT / "qa/LI_COMPLETE_VISUAL_QA_20260829.json"
DRIVER = ROOT / "repo/source/full-reader-id.tex"
BUILD_SCRIPT = ROOT / "scripts/build_li_complete.ps1"
EVIDENCE_DIR = ROOT / "qa/li-complete-evidence"

CHAPTERS = {
    7: {"order": 45, "slug": "aljabar-asosiatif", "id_title": "Bab 7: Aljabar Asosiatif"},
    8: {"order": 46, "slug": "teori-medan", "id_title": "Bab 8: Teori Medan"},
    9: {"order": 47, "slug": "teori-galois", "id_title": "Bab 9: Teori Galois"},
    10: {"order": 48, "slug": "valuasi-dan-pelengkapan", "id_title": "Bab 10: Valuasi dan Pelengkapan"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def identity(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def command_argument(line: str, command: str) -> str:
    marker = "\\" + command + "{"
    start = line.find(marker)
    require(start >= 0, f"missing {marker!r} in {line!r}")
    index = start + len(marker)
    depth = 1
    out: list[str] = []
    while index < len(line):
        char = line[index]
        if char == "{" and (index == 0 or line[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or line[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return "".join(out)
        out.append(char)
        index += 1
    raise RuntimeError(f"unclosed argument for {command}: {line!r}")


def section_specs(source_text: str, target_text: str, chapter: int) -> list[dict[str, object]]:
    source_lines = source_text.splitlines()
    target_lines = target_text.splitlines()
    require(len(source_lines) == len(target_lines), f"chapter {chapter} record-count drift")
    source_hits = [(i + 1, command_argument(line, "section")) for i, line in enumerate(source_lines) if line.lstrip().startswith(r"\section{")]
    target_hits = [(i + 1, command_argument(line, "section")) for i, line in enumerate(target_lines) if line.lstrip().startswith(r"\section{")]
    require([line for line, _ in source_hits] == [line for line, _ in target_hits], f"chapter {chapter} section topology drift")
    require(source_hits, f"chapter {chapter} has no sections")
    specs: list[dict[str, object]] = [{
        "order": 1,
        "first": 1,
        "last": source_hits[0][0] - 1,
        "source_title": f"第{chapter}章导言",
        "target_title": f"Pengantar Bab {chapter}",
        "outcome": f"chapter-{chapter}-introduction",
    }]
    for index, ((first, source_title), (_, target_title)) in enumerate(zip(source_hits, target_hits), 1):
        last = source_hits[index][0] - 1 if index < len(source_hits) else len(source_lines)
        specs.append({
            "order": index + 1,
            "first": first,
            "last": last,
            "source_title": source_title,
            "target_title": target_title,
            "outcome": f"chapter-{chapter}-section-{index:02d}",
        })
    return specs


def topology(text: str) -> dict[str, int]:
    exercise_block = ""
    if r"\begin{Exercises}" in text:
        exercise_block = text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    return {
        "records": len(text.splitlines()),
        "environment_starts": len(re.findall(r"\\begin\{[^{}]+\}", text)),
        "environment_ends": len(re.findall(r"\\end\{[^{}]+\}", text)),
        "labels": len(re.findall(r"\\label\{[^{}]+\}", text)),
        "references": len(re.findall(r"\\(?:ref|eqref|rref|cref)\{[^{}]+\}", text)),
        "citations": len(re.findall(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}", text)),
        "indexes": len(common.parse_indexes_with_lines(text)),
        "items": len(re.findall(r"\\item\b", text)),
        "top_level_exercises": len(re.findall(r"(?m)^\t\\item\b", exercise_block)),
        "exercise_items": len(re.findall(r"\\item\b", exercise_block)),
        "hints": len(re.findall(r"\\begin\{hint\}|\\hint\{", exercise_block)),
        "tikzcd": text.count(r"\begin{tikzcd}"),
        "tikzpicture": text.count(r"\begin{tikzpicture}"),
    }


def section_index(specs: list[dict[str, object]], line: int) -> int:
    for index, spec in enumerate(specs):
        if int(spec["first"]) <= line <= int(spec["last"]):
            return index
    raise RuntimeError(f"line outside chapter closure: {line}")


def make_document(chapter: int) -> tuple[dict[str, object], dict[str, bytes], dict[str, object]]:
    config = CHAPTERS[chapter]
    order = int(config["order"])
    slug = str(config["slug"])
    source = AUTHORITY_ROOT / f"chapter{chapter}.tex"
    target = ROOT / f"repo/source/chapter{chapter}.tex"
    candidate = ROOT / f"build/chapter{chapter}-batch-candidate/chapter{chapter}-complete-id.tex"
    if chapter == 10:
        candidate = ROOT / "build/chapter10-batch-candidate/chapter10-complete-id-final.tex"
    source_text = source.read_text(encoding="utf-8")
    target_text = target.read_text(encoding="utf-8")
    require(target.read_bytes() == candidate.read_bytes(), f"chapter {chapter} canonical target is not final-candidate-identical")
    source_topology = topology(source_text)
    target_topology = topology(target_text)
    require(source_topology == target_topology, f"chapter {chapter} topology drift: {source_topology} != {target_topology}")
    specs = section_specs(source_text, target_text, chapter)

    base = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    program, course, resource, edition = [copy.deepcopy(base[key]) for key in ("program", "course", "resource", "edition")]
    prerequisites = copy.deepcopy(base["prerequisites"])
    rights = copy.deepcopy(base["rights"])
    unit_key = f"unit/bab-{chapter}-{slug}"
    unit_id = common.uid(unit_key)

    sections: list[dict[str, object]] = []
    concepts: list[dict[str, object]] = []
    for spec in specs:
        section_order = int(spec["order"])
        key = f"{unit_key}/section/{section_order:02d}"
        concept = common.entity(
            f"concept/o013-li-chapter{chapter}/section-{section_order:02d}",
            "concept", str(spec["source_title"]), str(spec["target_title"]),
        )
        concepts.append(concept)
        sections.append({
            "id": common.uid(key), "stable_key": key, "entity_type": "section",
            "parent_id": unit_id, "order": section_order,
            "source_local_id": f"chapter{chapter}.tex:{spec['first']}-{spec['last']}",
            "titles": [common.label("zh-Hans", str(spec["source_title"])), common.label("id-ID", str(spec["target_title"]))],
            "source_binding": common.line_binding(source, int(spec["first"]), int(spec["last"])),
            "target_binding": common.line_binding(target, int(spec["first"]), int(spec["last"])),
            "concept_ids": [concept["id"]], "prerequisite_ids": [],
            "rights_component_ids": [common.uid("rights/principal-cc-by-4.0")],
            "translation_state": "visually_checked", "admission_state": "admitted",
        })

    for kind, count, en, indonesian in (
        ("exercise", target_topology["top_level_exercises"], "exercise", "latihan"),
        ("hint", target_topology["hints"], "hint", "petunjuk"),
    ):
        for number in range(1, count + 1):
            record = common.entity(
                f"surface/unit-{order:03d}/{kind}/{number:03d}", "concept",
                f"Unit {order:03d} {en} occurrence {number:03d}",
                f"Unit {order:03d} kemunculan {indonesian} {number:03d}",
            )
            concepts.append(record)
            sections[-1]["concept_ids"].append(record["id"])

    source_diagrams = common.diagram_spans(source_text)
    target_diagrams = common.diagram_spans(target_text)
    require([(item[1], item[2]) for item in source_diagrams] == [(item[1], item[2]) for item in target_diagrams], f"chapter {chapter} diagram drift")
    diagrams = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_diagrams, target_diagrams), 1):
        _, fmt, occurrence, source_first, source_last = source_item
        _, _, _, target_first, target_last = target_item
        key = f"diagram/unit-{order:03d}/{fmt}-{occurrence:02d}"
        diagrams.append({
            "id": common.uid(key), "stable_key": key, "entity_type": "diagram",
            "section_id": sections[section_index(specs, target_first)]["id"],
            "ordinal_in_unit": ordinal, "source_format": fmt, "source_occurrence_index": occurrence,
            "source_binding": common.line_binding(source, source_first, source_last),
            "target_binding": common.line_binding(target, target_first, target_last),
            "rights_component_id": common.uid("rights/principal-cc-by-4.0"), "state": "audited_preserved",
        })

    source_indexes = common.parse_indexes_with_lines(source_text)
    target_indexes = common.parse_indexes_with_lines(target_text)
    require([item[0] for item in source_indexes] == [item[0] for item in target_indexes], f"chapter {chapter} index-stream drift")
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes), 1):
        stream, source_key, source_line = source_item
        _, target_key, target_line = target_item
        key = f"index-entry/unit-{order:03d}/{stream or 'main'}/{ordinal:03d}"
        index_entries.append({
            "id": common.uid(key), "stable_key": key, "entity_type": "index_entry",
            "section_id": sections[section_index(specs, target_line)]["id"], "ordinal_in_unit": ordinal,
            "source_key": source_key, "target_key": target_key,
            "source_binding": common.line_binding(source, source_line, source_line),
            "target_binding": common.line_binding(target, target_line, target_line),
            "provenance_state": "source_key_preserved_target_key_localized",
        })

    bib = ROOT / "repo/source/Al-jabr.bib"
    bib_hash = identity(bib)[1]
    source_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", source_text))
    target_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", target_text))
    require([item.group(1) for item in source_cites] == [item.group(1) for item in target_cites], f"chapter {chapter} citation drift")
    citations = []
    seen: set[str] = set()
    for source_match, target_match in zip(source_cites, target_cites):
        bib_key = target_match.group(1)
        if bib_key in seen:
            continue
        seen.add(bib_key)
        ordinal = len(citations) + 1
        source_line = line_of(source_text, source_match.start())
        target_line = line_of(target_text, target_match.start())
        safe_key = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", bib_key).encode("ascii", "ignore").decode().lower()).strip("-")
        key = f"citation/unit-{order:03d}/{ordinal:02d}-{safe_key}"
        citations.append({
            "id": common.uid(key), "stable_key": key, "entity_type": "citation", "bib_key": bib_key,
            "bibliography_path": rel(bib), "bibliography_sha256": bib_hash,
            "source_line": source_line, "target_line": target_line,
            "section_id": sections[section_index(specs, target_line)]["id"],
        })

    rights_by_key = {item["stable_key"]: item for item in rights}
    for record in rights:
        if record["stable_key"] == "rights/principal-cc-by-4.0":
            record["bindings"] = [common.file_binding(source), common.file_binding(candidate), common.file_binding(target), common.file_binding(ROOT / "repo/source/LICENSE")]
        elif record["stable_key"] == "rights/ajbook-fragment-cc-by-sa-3.0":
            record["bindings"] = [common.file_binding(ROOT / "repo/source/AJbook.cls")]
        elif record["stable_key"] == "rights/noto-fonts-ofl-1.1":
            record["bindings"] = [common.file_binding(ROOT / "repo/fonts/OFL-1.1-Noto-CJK.txt")]
        elif record["stable_key"] == "rights/fandol-gpl-3.0-with-font-exception":
            record["bindings"] = [common.file_binding(ROOT / "repo/fonts/FANDOL-AUTHORITY.json"), common.file_binding(ROOT / "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt"), common.file_binding(FINAL_PDF)]
        elif record["stable_key"] == "rights/lanzhou-cc-by-sa-3.0":
            record["bindings"] = [common.file_binding(ROOT / "repo/source/Lanzhou.png")]
            record["applies_to_unit"] = False
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    unit_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
        rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
        rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"],
    ]

    surface_key = f"build-surface/unit-{order:03d}-complete-li-pdf"
    surfaces = [{
        "id": common.uid(surface_key), "stable_key": surface_key, "entity_type": "build_surface",
        "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_li_complete.ps1",
        "artifact_path": rel(FINAL_PDF), "artifact_binding": common.file_binding(FINAL_PDF),
        "log_binding": common.file_binding(BUILD_LOG), "build_script": common.file_binding(BUILD_SCRIPT),
        "page_count": 521, "status": "pass", "driver": common.file_binding(DRIVER),
        "input_bindings": [common.file_binding(target), common.file_binding(DRIVER), common.file_binding(bib)],
        "external_dependencies": ["XeLaTeX", "Biber", "makeindex", "Noto CJK fonts", "Fandol 0.3 toolchain fonts"],
        "rights_component_ids": unit_rights,
    }]

    qa_specs = [
        ("translation", TRANSLATION_FREEZE, "Complete Li source/target topology, mathematics, identifiers, exercises, and hints passed the single final translation freeze."),
        ("build", BUILD_LOG, "The deterministic 521-page XeLaTeX/Biber/makeindex build completed without fatal or unresolved diagnostics."),
        ("visual", VISUAL_QA, "All 521 pages passed the bounded overview and targeted high-resolution readability inspection."),
        ("rights", ROOT / "repo/source/coverpage-id-full.tex", "Attribution, independent-edition status, changes, non-endorsement, license, and model provenance are explicit."),
    ]
    qa_events = []
    for qa_order, (qa_slug, witness, scope) in enumerate(qa_specs, 1):
        key = f"qa/unit-{order:03d}/{qa_order:02d}-{qa_slug}"
        qa_events.append({
            "id": common.uid(key), "stable_key": key, "entity_type": "qa_event", "unit_id": unit_id,
            "check_type": "admission_gate" if qa_order == 1 else "backend_integrity", "result": "pass", "scope": scope,
            "witness": rel(witness), "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass",
            "witness_binding": common.file_binding(witness),
        })

    source_chapter_title = next(command_argument(line, "chapter") for line in source_text.splitlines() if line.lstrip().startswith(r"\chapter{"))
    unit = {
        "id": unit_id, "stable_key": unit_key, "entity_type": "unit",
        "program_id": program["id"], "course_id": course["id"], "resource_id": resource["id"], "edition_id": edition["id"],
        "order": order, "source_local_id": f"chapter{chapter}.tex:1-{source_topology['records']}; complete Chapter {chapter}",
        "titles": [common.label("zh-Hans", source_chapter_title), common.label("id-ID", str(config["id_title"]))],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": common.line_binding(source, 1, source_topology["records"]),
        "target_binding": common.line_binding(target, 1, target_topology["records"]),
        "section_ids": [item["id"] for item in sections], "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [item["id"] for item in prerequisites], "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations], "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries], "build_surface_ids": [item["id"] for item in surfaces],
        "qa_event_ids": [item["id"] for item in qa_events], "outcome_keys": [str(spec["outcome"]) for spec in specs],
        "surface_counts": {
            "sections": len(sections), "exercises": target_topology["top_level_exercises"], "hints": target_topology["hints"],
            "answers": 0, "solutions": 0, "citations": len(citations), "diagrams": len(diagrams), "index_entries": len(index_entries),
        },
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    document = {
        "$schema": "../schema/open-math-corpus-unit.schema.v1.json", "schema_name": "open-math-corpus-unit",
        "schema_version": "1.1.0", "profile": "curriculum-modular-backend-v0",
        "dataset_id": common.uid(f"dataset/unit-{order:03d}/id-id"), "dataset_stable_key": f"dataset/unit-{order:03d}/id-id",
        "id_namespace": copy.deepcopy(base["id_namespace"]),
        "workflow": {
            "responsible_task": common.uid(f"task/o013-li-u{order:03d}-backend"), "updated": "2026-08-29",
            "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked",
            "qa_state": "translation_math_backend_build_visual_pass",
        },
        "program": program, "course": course, "resource": resource, "edition": edition, "unit": unit,
        "sections": sections, "concepts": concepts, "prerequisites": prerequisites, "rights": rights,
        "citations": citations, "diagrams": diagrams, "index_entries": index_entries,
        "build_surfaces": surfaces, "qa_events": qa_events,
    }

    Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(document)
    semantic = backend_validator.Validation()
    backend_validator.semantic_validation(document, ROOT, semantic)
    require(not semantic.errors, "semantic validation failed: " + "; ".join(semantic.errors))
    rendered = backend_validator.render_csvs(document)
    csv_outputs = {kind: rendered[f"unit-{order:03d}-{kind}.csv"] for kind in ("bindings", "entities", "qa", "relations", "rights", "surfaces")}
    validation = {
        "schema": "o013-li-final-chapter-backend-validation-v1", "unit": f"O013-LI-U{order:03d}", "result": "pass",
        "generated": "2026-08-29", "chapter": chapter,
        "authority": {"range": f"chapter{chapter}.tex:1-{source_topology['records']}", "bytes": identity(source)[0], "sha256": identity(source)[1]},
        "target": {"range": f"chapter{chapter}.tex:1-{target_topology['records']}", "bytes": identity(target)[0], "sha256": identity(target)[1], "candidate_identical": True},
        "topology": target_topology, "sections": len(sections), "rights_components": len(rights),
        "build_surfaces": len(surfaces), "qa_events": len(qa_events), "schema_validation": "pass",
        "semantic_validation": "pass", "csv_projections": 6,
    }
    return document, csv_outputs, validation


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected: dict[Path, bytes] = {}
    summary = []
    for chapter in CHAPTERS:
        config = CHAPTERS[chapter]
        order = int(config["order"])
        slug = str(config["slug"])
        document, csv_outputs, validation = make_document(chapter)
        backend_path = ROOT / f"backend/data/unit-{order:03d}-bab-{chapter}-{slug}.json"
        validation_path = EVIDENCE_DIR / f"unit-{order:03d}-backend-validation.json"
        json_bytes = encode(document)
        validation["backend"] = {"path": rel(backend_path), "bytes": len(json_bytes), "sha256": hashlib.sha256(json_bytes).hexdigest()}
        validation["csv"] = {}
        for kind, payload in csv_outputs.items():
            path = ROOT / f"backend/csv/unit-{order:03d}-{kind}.csv"
            expected[path] = payload
            validation["csv"][kind] = {"path": rel(path), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        validation["generator"] = common.file_binding(Path(__file__))
        expected[backend_path] = json_bytes
        expected[validation_path] = encode(validation)
        summary.append(validation["backend"])
    if args.check:
        for path, payload in expected.items():
            require(path.is_file() and path.read_bytes() == payload, f"generated output drift: {rel(path)}")
        print(json.dumps({"result": "PASS", "backends": summary, "csv_projections": 24}, indent=2))
        return 0
    for path, payload in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(json.dumps({"result": "PASS_WRITTEN", "backends": summary, "csv_projections": 24}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
