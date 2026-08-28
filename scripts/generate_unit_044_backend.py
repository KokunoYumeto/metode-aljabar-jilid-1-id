#!/usr/bin/env python3
"""Generate the complete-Chapter-6 modular backend for O013 Li Unit 044."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_unit_043_backend as common
import validate_backend as backend_validator


SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
TEMPLATE = ROOT / "backend/data/unit-043-bab-5-pengantar-teori-gelanggang.json"
SOURCE = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex"
CANDIDATE = ROOT / "build/chapter6-batch-candidate/chapter6-complete-id.tex"
TARGET = ROOT / "repo/source/chapter6.tex"
CHECKER = ROOT / "build/chapter6-batch-candidate/check_chapter6_complete.py"
CHAPTER_PDF = ROOT / "artifacts/unit-044-bab-6-modul-id.pdf"
CHAPTER_LOG = ROOT / "qa/CHAPTER_6_BUILD_FINAL.log"
CHAPTER_QA = ROOT / "qa/CHAPTER_6_PDF_STRUCTURAL_QA.json"
DRIVER = ROOT / "repo/source/chapter-6-reader.tex"
COVER = ROOT / "repo/source/coverpage-id-chapter-6.tex"
CROSSREF = ROOT / "repo/source/chapter6-crossrefs.aux"
READER_SOURCE = ROOT / "build/chapter6-reader-source/chapter6-reader-reflow.tex"
READER_SOURCE_BUILDER = ROOT / "scripts/prepare_chapter6_reader_source.py"
BUILD_SCRIPT = ROOT / "scripts/build_chapter6.ps1"
COMBINED_PDF = ROOT / "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf"
COMBINED_SCRIPT = ROOT / "scripts/build_checkpoint_reader_through_chapter_6.py"
COMBINED_RECEIPT = ROOT / "qa/unit-044-evidence/checkpoint-through-bab-6-build.json"
COMBINED_QA = ROOT / "qa/unit-044-evidence/checkpoint-through-bab-6-structural-qa.json"
OUTPUT = ROOT / "backend/data/unit-044-bab-6-teori-modul.json"
VALIDATION = ROOT / "qa/unit-044-evidence/backend-validation.json"
CSV_PATHS = {
    name: ROOT / f"backend/csv/unit-044-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
}

UNIT_KEY = "unit/bab-6-teori-modul"
SECTION_SPECS = [
    (1, 1, 209, "第六章导言与基本概念", "Pengantar Bab 6 dan Konsep Dasar", "module-basics"),
    (2, 210, 337, "模的基本操作", "Operasi Dasar pada Modul", "module-operations"),
    (3, 338, 468, "自由模", "Modul Bebas", "free-modules"),
    (4, 469, 549, "向量空间", "Ruang Vektor", "vector-spaces"),
    (5, 550, 791, "模的张量积", "Hasil Kali Tensor Modul", "tensor-products"),
    (6, 792, 973, "环变换", "Perubahan Gelanggang", "change-of-rings"),
    (7, 974, 1190, "主理想环上的有限生成模", "Modul Terbangkitkan Hingga atas Daerah Ideal Utama", "pid-modules"),
    (8, 1191, 1372, "正合列入门", "Pengantar Barisan Eksak", "exact-sequences"),
    (9, 1373, 1534, "投射模、内射模、平坦模", "Modul Projektif, Modul Injektif, dan Modul Datar", "projective-injective-flat"),
    (10, 1535, 1663, "链条件和模的合成列", "Syarat Rantai dan Deret Komposisi Modul", "chain-conditions"),
    (11, 1664, 1764, "半单模", "Modul Semisederhana", "semisimple-modules"),
    (12, 1765, 1994, "不可分解模与第六章习题", "Modul Tak Terurai dan Latihan Bab 6", "indecomposable-modules"),
]


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


def section_index(line: int) -> int:
    for index, (_, first, last, _, _, _) in enumerate(SECTION_SPECS):
        if first <= line <= last:
            return index
    raise RuntimeError(f"line outside Chapter 6 closure: {line}")


def topology(text: str) -> dict[str, int]:
    exercises = text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    values = {
        "environment_starts": len(re.findall(r"\\begin\{[^{}]+\}", text)),
        "environment_ends": len(re.findall(r"\\end\{[^{}]+\}", text)),
        "labels": len(re.findall(r"\\label\{[^{}]+\}", text)),
        "references": len(re.findall(r"\\(?:ref|eqref|rref|cref)\{[^{}]+\}", text)),
        "citations": len(re.findall(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}", text)),
        "indexes": len(common.parse_indexes_with_lines(text)),
        "items": len(re.findall(r"\\item\b", text)),
        "top_level_exercises": len(re.findall(r"(?m)^\t\\item\b", exercises)),
        "exercise_items": len(re.findall(r"\\item\b", exercises)),
        "hints": len(re.findall(r"\\begin\{hint\}|\\hint\{", exercises)),
        "tikzcd": text.count(r"\begin{tikzcd}"),
        "tikzpicture": text.count(r"\begin{tikzpicture}"),
    }
    expected = {
        "environment_starts": 363, "environment_ends": 363,
        "labels": 98, "references": 224, "citations": 6,
        "indexes": 70, "items": 132, "top_level_exercises": 14,
        "exercise_items": 22, "hints": 8, "tikzcd": 37, "tikzpicture": 7,
    }
    require(values == expected, f"whole-chapter topology drift: {values}")
    return values


def make_backend() -> tuple[dict[str, object], dict[str, bytes], dict[str, object]]:
    require(identity(SOURCE) == (160950, "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"), "authority drift")
    require(identity(CANDIDATE) == (193563, "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14"), "candidate drift")
    require(TARGET.read_bytes() == CANDIDATE.read_bytes(), "canonical Chapter 6 is not candidate-identical")
    require(identity(READER_SOURCE) == (193613, "e83fc702c2a2839c1e3941b9ab0a83c67b474bd72c2846433dac854c959f8f28"), "reader reflow drift")
    source_text = SOURCE.read_text(encoding="utf-8")
    target_text = TARGET.read_text(encoding="utf-8")
    counts = topology(target_text)
    require(topology(source_text) == counts, "source/target topology mismatch")

    base = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    program, course, resource, edition = [copy.deepcopy(base[key]) for key in ("program", "course", "resource", "edition")]
    prerequisites = copy.deepcopy(base["prerequisites"])
    rights = copy.deepcopy(base["rights"])
    unit_id = common.uid(UNIT_KEY)

    sections: list[dict[str, object]] = []
    for order, first, last, source_title, target_title, _ in SECTION_SPECS:
        key = f"{UNIT_KEY}/section/{order:02d}"
        sections.append(
            {
                "id": common.uid(key), "stable_key": key, "entity_type": "section",
                "parent_id": unit_id, "order": order,
                "source_local_id": f"chapter6.tex:{first}-{last}",
                "titles": [common.label("zh-Hans", source_title), common.label("id-ID", target_title)],
                "source_binding": common.line_binding(SOURCE, first, last),
                "target_binding": common.line_binding(TARGET, first, last),
                "concept_ids": [], "prerequisite_ids": [],
                "rights_component_ids": [common.uid("rights/principal-cc-by-4.0")],
                "translation_state": "visually_checked", "admission_state": "admitted",
            }
        )

    concepts: list[dict[str, object]] = []
    for index, (_, _, _, source_title, target_title, slug) in enumerate(SECTION_SPECS):
        record = common.entity(f"concept/o013-li-chapter6/{slug}", "concept", source_title, target_title)
        concepts.append(record)
        sections[index]["concept_ids"].append(record["id"])
    for kind, count, en, indonesian in (
        ("exercise", 14, "exercise", "latihan"),
        ("hint", 8, "hint", "petunjuk"),
    ):
        for number in range(1, count + 1):
            record = common.entity(
                f"surface/unit-044/{kind}/{number:03d}", "concept",
                f"Unit 044 {en} occurrence {number:03d}",
                f"Unit 044 kemunculan {indonesian} {number:03d}",
            )
            concepts.append(record)
            sections[-1]["concept_ids"].append(record["id"])

    source_diagrams = common.diagram_spans(source_text)
    target_diagrams = common.diagram_spans(target_text)
    require([(x[1], x[2]) for x in source_diagrams] == [(x[1], x[2]) for x in target_diagrams], "diagram sequence drift")
    diagrams = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_diagrams, target_diagrams), 1):
        _, fmt, occurrence, source_first, source_last = source_item
        _, _, _, target_first, target_last = target_item
        key = f"diagram/unit-044/{fmt}-{occurrence:02d}"
        diagrams.append(
            {
                "id": common.uid(key), "stable_key": key, "entity_type": "diagram",
                "section_id": sections[section_index(target_first)]["id"],
                "ordinal_in_unit": ordinal, "source_format": fmt,
                "source_occurrence_index": occurrence,
                "source_binding": common.line_binding(SOURCE, source_first, source_last),
                "target_binding": common.line_binding(TARGET, target_first, target_last),
                "rights_component_id": common.uid("rights/principal-cc-by-4.0"),
                "state": "audited_preserved",
            }
        )

    source_indexes = common.parse_indexes_with_lines(source_text)
    target_indexes = common.parse_indexes_with_lines(target_text)
    require([item[0] for item in source_indexes] == [item[0] for item in target_indexes], "index-stream sequence drift")
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes), 1):
        stream, source_key, source_line = source_item
        _, target_key, target_line = target_item
        key = f"index-entry/unit-044/{stream or 'main'}/{ordinal:03d}"
        index_entries.append(
            {
                "id": common.uid(key), "stable_key": key, "entity_type": "index_entry",
                "section_id": sections[section_index(target_line)]["id"],
                "ordinal_in_unit": ordinal, "source_key": source_key, "target_key": target_key,
                "source_binding": common.line_binding(SOURCE, source_line, source_line),
                "target_binding": common.line_binding(TARGET, target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    bib = ROOT / "repo/source/Al-jabr.bib"
    bib_hash = identity(bib)[1]
    source_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", source_text))
    target_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", target_text))
    require([item.group(1) for item in source_cites] == [item.group(1) for item in target_cites], "citation sequence drift")
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
        key = f"citation/unit-044/{ordinal:02d}-{re.sub(r'[^a-z0-9]+', '-', bib_key.lower())}"
        citations.append(
            {
                "id": common.uid(key), "stable_key": key, "entity_type": "citation",
                "bib_key": bib_key, "bibliography_path": rel(bib),
                "bibliography_sha256": bib_hash, "source_line": source_line,
                "target_line": target_line, "section_id": sections[section_index(target_line)]["id"],
            }
        )

    rights_by_key = {item["stable_key"]: item for item in rights}
    for record in rights:
        if record["stable_key"] == "rights/principal-cc-by-4.0":
            record["bindings"] = [
                common.file_binding(SOURCE), common.file_binding(CANDIDATE),
                common.file_binding(TARGET), common.file_binding(ROOT / "repo/source/LICENSE"),
            ]
        elif record["stable_key"] == "rights/ajbook-fragment-cc-by-sa-3.0":
            record["bindings"] = [common.file_binding(ROOT / "repo/source/AJbook.cls")]
        elif record["stable_key"] == "rights/noto-fonts-ofl-1.1":
            record["bindings"] = [common.file_binding(ROOT / "repo/fonts/OFL-1.1-Noto-CJK.txt")]
        elif record["stable_key"] == "rights/fandol-gpl-3.0-with-font-exception":
            record["bindings"] = [
                common.file_binding(ROOT / "repo/fonts/FANDOL-AUTHORITY.json"),
                common.file_binding(ROOT / "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt"),
                common.file_binding(CHAPTER_PDF), common.file_binding(COMBINED_PDF),
            ]
        elif record["stable_key"] == "rights/lanzhou-cc-by-sa-3.0":
            record["bindings"] = [common.file_binding(ROOT / "repo/source/Lanzhou.png")]
            record["applies_to_unit"] = False
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    common_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
        rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
        rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"],
    ]
    aggregate_rights = common_rights + [rights_by_key["rights/lanzhou-cc-by-sa-3.0"]["id"]]

    surfaces = [
        {
            "id": common.uid("build-surface/unit-044-chapter-pdf"),
            "stable_key": "build-surface/unit-044-chapter-pdf", "entity_type": "build_surface",
            "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
            "command": "pwsh -NoProfile -File scripts/build_chapter6.ps1",
            "artifact_path": rel(CHAPTER_PDF), "artifact_binding": common.file_binding(CHAPTER_PDF),
            "log_binding": common.file_binding(CHAPTER_LOG), "build_script": common.file_binding(BUILD_SCRIPT),
            "page_count": 75, "status": "pass", "driver": common.file_binding(DRIVER),
            "input_bindings": [
                common.file_binding(COVER), common.file_binding(CROSSREF), common.file_binding(TARGET),
                common.file_binding(READER_SOURCE_BUILDER), common.file_binding(READER_SOURCE), common.file_binding(bib),
            ],
            "external_dependencies": ["XeLaTeX", "Biber", "makeindex", "Noto CJK fonts", "Fandol 0.3 toolchain fonts"],
            "rights_component_ids": common_rights,
        },
        {
            "id": common.uid("build-surface/unit-044-combined-checkpoint-pdf"),
            "stable_key": "build-surface/unit-044-combined-checkpoint-pdf", "entity_type": "build_surface",
            "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
            "command": "python scripts/build_checkpoint_reader_through_chapter_6.py",
            "artifact_path": rel(COMBINED_PDF), "artifact_binding": common.file_binding(COMBINED_PDF),
            "log_binding": common.file_binding(COMBINED_RECEIPT), "build_script": common.file_binding(COMBINED_SCRIPT),
            "page_count": 460, "status": "pass", "driver": common.file_binding(COMBINED_SCRIPT),
            "input_bindings": [common.file_binding(CHAPTER_PDF), common.file_binding(COMBINED_RECEIPT)],
            "external_dependencies": ["Python", "pypdf", "ReportLab", "Noto Sans fonts"],
            "rights_component_ids": aggregate_rights,
        },
    ]

    qa_specs = [
        ("structure", CHECKER, "Complete Chapter 6 structure, identifiers, protected mathematics, exercises, hints, citations, diagrams, and indexes passed."),
        ("chapter-build", CHAPTER_LOG, "Hash-gated 75-page Chapter 6 XeLaTeX/Biber/makeindex build passed with zero overfull boxes and zero unresolved references or citations."),
        ("chapter-visual", CHAPTER_QA, "All 75 Chapter 6 pages passed structural PDF checks and one all-page visual inspection."),
        ("combined-build", COMBINED_RECEIPT, "Reader-first 460-page checkpoint through complete Chapter 6 passed 37-component byte validation."),
        ("combined-visual", COMBINED_QA, "The combined reader inherited 384 exact prior pages and 75 exact Chapter 6 pages; cover and transition boundaries passed visual inspection."),
        ("rights", COVER, "Attribution, changes, non-endorsement, model provenance, and separate component rights are explicit."),
    ]
    qa_events = []
    for order, (slug, witness, scope) in enumerate(qa_specs, 1):
        key = f"qa/unit-044/{order:02d}-{slug}"
        qa_events.append(
            {
                "id": common.uid(key), "stable_key": key, "entity_type": "qa_event",
                "unit_id": unit_id, "check_type": "admission_gate" if order == 1 else "backend_integrity",
                "result": "pass", "scope": scope, "witness": rel(witness),
                "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass",
                "witness_binding": common.file_binding(witness),
            }
        )

    unit = {
        "id": unit_id, "stable_key": UNIT_KEY, "entity_type": "unit",
        "program_id": program["id"], "course_id": course["id"],
        "resource_id": resource["id"], "edition_id": edition["id"], "order": 44,
        "source_local_id": "chapter6.tex:1-1994; complete Chapter 6",
        "titles": [common.label("zh-Hans", "第六章 模论"), common.label("id-ID", "Bab 6: Teori Modul")],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": common.line_binding(SOURCE, 1, 1994),
        "target_binding": common.line_binding(TARGET, 1, 1994),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [item["id"] for item in prerequisites],
        "rights_component_ids": common_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [item["id"] for item in surfaces],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [item[5] for item in SECTION_SPECS],
        "surface_counts": {
            "sections": 12, "exercises": 14, "hints": 8, "answers": 0, "solutions": 0,
            "citations": len(citations), "diagrams": len(diagrams), "index_entries": len(index_entries),
        },
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    document = {
        "$schema": "../schema/open-math-corpus-unit.schema.v1.json",
        "schema_name": "open-math-corpus-unit", "schema_version": "1.1.0",
        "profile": "curriculum-modular-backend-v0",
        "dataset_id": common.uid("dataset/unit-044/id-id"),
        "dataset_stable_key": "dataset/unit-044/id-id",
        "id_namespace": copy.deepcopy(base["id_namespace"]),
        "workflow": {
            "responsible_task": common.uid("task/o013-li-u044-backend"),
            "updated": "2026-08-28", "status": "admitted", "admission_state": "admitted",
            "translation_state": "visually_checked", "qa_state": "translation_math_backend_build_visual_pass",
        },
        "program": program, "course": course, "resource": resource, "edition": edition,
        "unit": unit, "sections": sections, "concepts": concepts,
        "prerequisites": prerequisites, "rights": rights, "citations": citations,
        "diagrams": diagrams, "index_entries": index_entries,
        "build_surfaces": surfaces, "qa_events": qa_events,
    }

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(document)
    result = backend_validator.Validation()
    backend_validator.semantic_validation(document, ROOT, result)
    require(not result.errors, "semantic backend validation failed: " + "; ".join(result.errors))
    rendered = backend_validator.render_csvs(document)
    csv_outputs = {
        name: rendered[f"unit-044-{name}.csv"]
        for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
    }
    validation = {
        "schema": "o013-unit-backend-validation-v1", "unit": "O013-LI-U044",
        "result": "pass", "generated": "2026-08-28",
        "authority": {"range": "chapter6.tex:1-1994", "bytes": identity(SOURCE)[0], "sha256": identity(SOURCE)[1]},
        "target": {"range": "chapter6.tex:1-1994", "bytes": identity(TARGET)[0], "sha256": identity(TARGET)[1], "candidate_identical": True},
        "reader_reflow": {"bytes": identity(READER_SOURCE)[0], "sha256": identity(READER_SOURCE)[1], "layout_only_changes": 3},
        "topology": counts, "sections": 12, "rights_components": len(rights),
        "build_surfaces": 2, "qa_events": len(qa_events),
        "schema_validation": "pass", "semantic_validation": "pass", "csv_projections": 6,
    }
    return document, csv_outputs, validation


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document, csv_outputs, validation = make_backend()
    json_bytes = encode(document)
    validation["backend"] = {"path": rel(OUTPUT), "bytes": len(json_bytes), "sha256": hashlib.sha256(json_bytes).hexdigest()}
    validation["csv"] = {
        name: {"path": rel(CSV_PATHS[name]), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
        for name, payload in csv_outputs.items()
    }
    validation["generator"] = common.file_binding(Path(__file__))
    validation_bytes = encode(validation)
    expected = {OUTPUT: json_bytes, VALIDATION: validation_bytes, **{CSV_PATHS[name]: payload for name, payload in csv_outputs.items()}}
    if args.check:
        for path, payload in expected.items():
            require(path.is_file() and path.read_bytes() == payload, f"generated output drift: {rel(path)}")
        print(json.dumps({"result": "PASS", "backend": validation["backend"], "csv_projections": 6}, indent=2))
        return 0
    for path, payload in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(json.dumps({"result": "PASS_WRITTEN", "backend": validation["backend"], "csv_projections": 6}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
