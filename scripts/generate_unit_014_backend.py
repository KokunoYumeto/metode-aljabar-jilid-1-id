#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 014."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_009_backend as base


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.json"
OUTPUT = ROOT / "backend/data/unit-014-bab-2-fungtor-adjoin-dasar.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-014-bab-2-fungtor-adjoin-dasar.tex"
COVER = "repo/source/coverpage-id-unit-014.tex"
CROSSREF = "repo/source/unit-014-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_014.ps1"
STRUCTURE_GATE = "scripts/check_unit_014_structure.py"
SUMMARY = "qa/unit-014-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_014_ADMISSION_20260823.md"
FINAL_LOG = "qa/UNIT_014_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-014-bab-2-fungtor-adjoin-dasar.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 766, 909
SOURCE_FULL = (
    139983,
    "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840",
)
TARGET_FULL = (
    155822,
    "bcf19c8d261947fa619c0257351c29217f401bc1c9453ad91286ff96c1bd69a5",
)
SOURCE_SPAN = (
    10365,
    "930232390be4aed3aea2155ae1779e95eae621bb7b23ea9c6899828b46ce2960",
)
TARGET_SPAN = (
    11655,
    "5526e8eb99dba9dc3e0eebbd1ddd278eb6343fd50a1d18cf0f6715f09f6e1ed2",
)

ARTIFACT_ID: tuple[int, str] | None = (
    121651,
    "a8acee26ef75f172336d4e729e055ca6c8d222c548748d9c4a58a4ee976cb403",
)
FINAL_LOG_ID: tuple[int, str] | None = (
    85830,
    "61d3d9236755d0384c2dc0e08acd9fb0c4b0f67c2367dd6967ef6b6016296b07",
)
PAGE_COUNT: int | None = 9

LABELS = (
    "sec:adjoint-functor",
    "def:adjunction-pair",
    "def:adjunction-unit-counit",
    "eqn:unit-adjunction",
    "eqn:unit-counit-relation",
    "rem:triangle-identity",
)
EXPECTED_REFERENCES = (
    "eg:functors",
    "eg:vectf-duality",
    "sec:functors",
    "sec:functors",
    "sec:2-cat",
)
INDEX_SLUGS = ("adjunction-pair", "adjunction-unit-counit")
EXPECTED_CITATIONS = (("[p.107]", "ML98", 767),)
CORRECTIONS = (
    (
        "O013-LI-U014-COR-001",
        785,
        "The subscript switches from varphi_{V,W} to varphi_{VW} without changing the indexed family.",
    ),
    (
        "O013-LI-U014-COR-002",
        789,
        "The finite-dimensional restriction is a functor on the opposite finite-dimensional category.",
    ),
    (
        "O013-LI-U014-COR-003",
        789,
        "The displayed domain uses the inconsistent form Vect(k)_f instead of Vect_f(k).",
    ),
    (
        "O013-LI-U014-COR-004",
        799,
        "Counit components belong to objects Y of C_2, not the X-index convention for C_1.",
    ),
)
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-014-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def diagram_blocks(text: str) -> tuple[tuple[str, int, str], ...]:
    """Return whitespace-normalized diagram blocks in source order."""
    pattern = re.compile(r"\\begin\{(tikzcd|tikzpicture)\}.*?\\end\{\1\}", re.DOTALL)
    return tuple(
        (match.group(1), ordinal, re.sub(r"\s+", "", match.group(0)))
        for ordinal, match in enumerate(pattern.finditer(text), 1)
    )


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def span(relative: str) -> bytes:
    return base.normalized_span(relative, START, END)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 014 backend refused: identity drift for {relative}")


def citation_occurrences(text: str) -> tuple[tuple[str, str, int], ...]:
    """Return citation option, key, and absolute source line in occurrence order."""
    pattern = re.compile(r"\\cite(\[[^]]+\])?\{([^}]+)\}")
    return tuple(
        (
            match.group(1) or "",
            match.group(2),
            START + text.count("\n", 0, match.start()),
        )
        for match in pattern.finditer(text)
    )


def reference_occurrences(text: str) -> tuple[str, ...]:
    """Return ordinary reference keys, excluding equation references."""
    return tuple(re.findall(r"\\ref\{([^}]+)\}", text))


def pdfinfo_page_count() -> int:
    completed = subprocess.run(
        ["pdfinfo", str(ROOT / ARTIFACT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(
            "Unit 014 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 014 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate() -> None:
    # Pin shared line-bearing occurrence parsers to this unit.
    base.SPAN_START = START
    base.SPAN_END = END
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(TARGET, TARGET_FULL)
    if ARTIFACT_ID is None or FINAL_LOG_ID is None or PAGE_COUNT is None:
        raise SystemExit(
            "Unit 014 backend scaffold is ready but admission is intentionally gated: "
            "record the final PDF/log byte identities and page count after visual QA, "
            "then fill ARTIFACT_ID, FINAL_LOG_ID, and PAGE_COUNT."
        )
    require_identity(FINAL_LOG, FINAL_LOG_ID)
    require_identity(ARTIFACT, ARTIFACT_ID)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 014 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 014 backend refused: target span drift")

    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 014 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass",
        "mathematics_source_count": 99,
        "mathematics_target_count": 100,
        "indonesian_math_segmentation_applied": True,
        "mathematics_multiset_exact_without_corrections": False,
        "mathematics_multiset_equivalent_after_declared_corrections": True,
        "environment_sequence_exact": True,
        "environment_begin_count": 30,
        "citation_signatures_exact": True,
        "index_source_count": 2,
        "index_target_count": 2,
        "index_topology_exact": True,
        "han_residue_count": 0,
        "next_boundary_ok": True,
        "target_sha256": TARGET_SPAN[1],
    }
    if any(report.get(key) != value for key, value in required.items()):
        raise SystemExit("Unit 014 backend refused: structural evidence drift")
    expected_command_counts = {
        "labels": 6,
        "references": 5,
        "equation_references": 9,
        "citations": 1,
    }
    command_report = report.get("commands", {})
    for name, count in expected_command_counts.items():
        occurrence = command_report.get(name, {})
        if occurrence != {
            "source_count": count,
            "target_count": count,
            "exact_argument_sequence": True,
        }:
            raise SystemExit(f"Unit 014 backend refused: {name} topology drift")
    expected_corrections = [
        {"id": correction_id, "source_line": line, "issue": issue, "applied": True}
        for correction_id, line, issue in CORRECTIONS
    ]
    if report.get("declared_source_corrections") != expected_corrections:
        raise SystemExit("Unit 014 backend refused: correction disclosure drift")

    source = span(SOURCE).decode()
    target = span(TARGET).decode()
    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if [(item[0], item[1]) for item in source_diagrams] != [
        (item[0], item[1]) for item in target_diagrams
    ]:
        raise SystemExit("Unit 014 backend refused: diagram order/format drift")
    if diagram_blocks(source) != diagram_blocks(target):
        raise SystemExit("Unit 014 backend refused: normalized diagram content drift")
    for text in (source, target):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit("Unit 014 backend refused: label drift")
        if len(base.index_occurrences(text)) != 2:
            raise SystemExit("Unit 014 backend refused: index drift")
        if len(base.diagram_occurrences(text)) != 13:
            raise SystemExit("Unit 014 backend refused: diagram drift")
        if citation_occurrences(text) != EXPECTED_CITATIONS:
            raise SystemExit("Unit 014 backend refused: citation identity drift")
        if reference_occurrences(text) != EXPECTED_REFERENCES:
            raise SystemExit("Unit 014 backend refused: external-reference drift")

    expected_aux_labels = (
        r"\newlabel{sec:functors}{{2.2}{1}}",
        r"\newlabel{eg:functors}{{2.2.{4}}{1}}",
        r"\newlabel{eg:vectf-duality}{{2.2.{14}}{9}}",
        r"\newlabel{sec:2-cat}{{3.5}{92}}",
    )
    actual_aux_labels = tuple(
        line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    if actual_aux_labels != expected_aux_labels:
        raise SystemExit(
            "Unit 014 backend refused: external-reference number/page map drift"
        )

    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    receipt = (ROOT / ADMISSION).read_text(encoding="utf-8")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+) pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != PAGE_COUNT:
        raise SystemExit("Unit 014 backend refused: final build-log page count drift")
    if pdfinfo_page_count() != PAGE_COUNT:
        raise SystemExit("Unit 014 backend refused: live PDF page count drift")
    for needle in (
        f"PDF pages: {PAGE_COUNT}",
        f"Functional replay: {PAGE_COUNT}/{PAGE_COUNT}",
        "Final-log blockers: zero",
        f"Visual QA: all {PAGE_COUNT} pages inspected",
    ):
        if needle not in summary:
            raise SystemExit(f"Unit 014 backend refused: summary lacks {needle!r}")
    receipt_needles = (
        "Status: admitted locally",
        "chapter2.tex:766-909",
        f"{PAGE_COUNT} pages",
        TARGET_SPAN[1],
        ARTIFACT_ID[1],
        FINAL_LOG_ID[1],
        MODEL,
        "Wen-Wei Li",
        "CC BY 4.0",
        "CC BY-SA 3.0",
        "OFL 1.1",
        "non-endorsed derivative",
        *(correction_id for correction_id, _line, _issue in CORRECTIONS),
    )
    for needle in receipt_needles:
        if needle not in receipt:
            raise SystemExit(f"Unit 014 backend refused: admission lacks {needle!r}")


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-2-fungtor-adjoin-dasar"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/fungtor-adjoin-dasar"
    section_id = uid(section_key)
    bind = base.binding

    source_citations = citation_occurrences(span(SOURCE).decode())
    target_citations = citation_occurrences(span(TARGET).decode())
    if source_citations != EXPECTED_CITATIONS or target_citations != EXPECTED_CITATIONS:
        raise SystemExit("Unit 014 backend refused: citation identity drift")

    concept_specs = [
        ("concept/adjunction", "伴随对", "pasangan adjoin"),
        ("concept/left-adjoint-functor", "左伴随函子", "fungtor adjoin kiri"),
        ("concept/right-adjoint-functor", "右伴随函子", "fungtor adjoin kanan"),
        ("concept/unit-of-adjunction", "单位", "unit"),
        ("concept/counit-of-adjunction", "余单位", "kounit"),
        ("concept/natural-transformation", "自然变换", "transformasi natural"),
        ("concept/naturality", "自然性", "naturalitas"),
        ("concept/triangle-identities", "三角等式", "identitas segitiga"),
        ("concept/two-cell", "2-胞腔", "2-sel"),
        ("concept/horizontal-composition", "横合成", "komposisi horizontal"),
        ("concept/vertical-composition", "纵合成", "komposisi vertikal"),
        ("concept/fully-faithful-functor", "全忠实函子", "fungtor penuh dan setia"),
        ("concept/dual-functor", "对偶函子", "fungtor dual"),
        ("concept/natural-isomorphism", "自然同构", "isomorfisme natural"),
    ]
    for label in LABELS:
        slug = label.replace(":", "-").lower()
        concept_specs.append(
            (f"surface/unit-014/label/{slug}", f"标签 {label}", f"label {label}")
        )
    for label in dict.fromkeys(EXPECTED_REFERENCES):
        slug = label.replace(":", "-").lower()
        concept_specs.append(
            (
                f"surface/unit-014/reference/{slug}",
                f"外部引用 {label}",
                f"rujukan eksternal {label}",
            )
        )
    concepts = [
        {
            "id": uid(key),
            "stable_key": key,
            "entity_type": "concept",
            "labels": [
                {"language": "zh-Hans", "text": zh},
                {"language": "id-ID", "text": id_text},
            ],
        }
        for key, zh, id_text in concept_specs
    ]
    concept_ids = [concept["id"] for concept in concepts]

    rights_map = {item["stable_key"]: item["id"] for item in data["rights"]}
    principal = rights_map["rights/principal-cc-by-4.0"]
    unit_rights = [
        principal,
        rights_map["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_map["rights/noto-fonts-ofl-1.1"],
    ]
    prerequisite_ids = [item["id"] for item in data["prerequisites"]]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter2.tex:766-909",
        "titles": [
            {"language": "zh-Hans", "text": "2.6 伴随函子"},
            {"language": "id-ID", "text": "2.6 Fungtor Adjoin"},
        ],
        "source_binding": bind(SOURCE, START, END),
        "target_binding": bind(TARGET, START, END),
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    bibliography_sha256 = identity(BIBLIOGRAPHY)[1]
    citations = []
    for ordinal, (source_citation, target_citation) in enumerate(
        zip(source_citations, target_citations, strict=True), 1
    ):
        source_option, source_key, source_line = source_citation
        target_option, target_key, target_line = target_citation
        if (source_option, source_key) != (target_option, target_key):
            raise SystemExit("Unit 014 backend refused: citation topology mismatch")
        key = f"citation/unit-014/{source_key.lower()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": source_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": bibliography_sha256,
                "source_line": source_line,
                "target_line": target_line,
                "section_id": section_id,
            }
        )

    source_indexes = base.index_occurrences(span(SOURCE).decode())
    target_indexes = base.index_occurrences(span(TARGET).decode())
    index_entries = []
    for ordinal, (slug, source_index, target_index) in enumerate(
        zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1
    ):
        if (source_index[0], source_index[2]) != (target_index[0], target_index[2]):
            raise SystemExit("Unit 014 backend refused: index topology mismatch")
        key = f"index-entry/unit-014/{slug}"
        index_entries.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "index_entry",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_key": source_index[1],
                "target_key": target_index[1],
                "source_binding": bind(SOURCE, source_index[2], source_index[2]),
                "target_binding": bind(TARGET, target_index[2], target_index[2]),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    diagrams = []
    source_diagrams = base.diagram_occurrences(span(SOURCE).decode())
    target_diagrams = base.diagram_occurrences(span(TARGET).decode())
    for ordinal, (source_diagram, target_diagram) in enumerate(
        zip(source_diagrams, target_diagrams, strict=True), 1
    ):
        source_format, source_occurrence, source_first, source_last = source_diagram
        target_format, target_occurrence, target_first, target_last = target_diagram
        if (source_format, source_occurrence) != (target_format, target_occurrence):
            raise SystemExit("Unit 014 backend refused: diagram binding drift")
        key = f"diagram/unit-014/{source_format}-{source_occurrence}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": source_occurrence,
                "source_binding": bind(SOURCE, source_first, source_last),
                "target_binding": bind(TARGET, target_first, target_last),
                "rights_component_id": principal,
                "state": "audited_preserved",
            }
        )

    build_key = "build-surface/unit-014-pdf"
    inputs = [
        COVER,
        "repo/source/font-setup-id.tex",
        "repo/source/AJbook.cls",
        "repo/source/titles-setup-id.tex",
        "repo/source/locale-ui-id.tex",
        "repo/source/titles-setup.tex",
        "repo/source/mycommand.sty",
        "repo/source/myarrows.sty",
        BIBLIOGRAPHY,
        "repo/source/ccby.png",
        CROSSREF,
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_014.ps1 -OutputDirectory build/unit-014-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": bind(ARTIFACT),
        "log_binding": bind(FINAL_LOG),
        "build_script": bind(BUILD_SCRIPT),
        "page_count": PAGE_COUNT,
        "status": "pass",
        "driver": bind(DRIVER),
        "input_bindings": [bind(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "biber",
            "makeindex (default index)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 014 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-014/admission-gate"
    correction_ids = ", ".join(item[0] for item in CORRECTIONS)
    qa = {
        "id": uid(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and semantic review of chapter2.tex lines "
            "766-909; 99 source and 100 reader-facing target normalized mathematics surfaces "
            "equivalent after one explicitly anchored Indonesian segmentation and four "
            f"disclosed source corrections ({correction_ids}); 30 balanced environments, six labels, "
            "five ordinary references, nine equation references, one ML98 citation, two "
            "default index entries, thirteen TikZ-CD diagrams, no exercises/hints/answers/"
            "solutions, resolved external references, separate component rights, functional "
            "replay, PDF checks, and all-page visual QA. Production provenance records "
            + MODEL
            + " separately from source authorship and human credit."
        ),
        "witness": ADMISSION,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(ADMISSION),
    }

    dataset_key = "dataset/unit-014/id-id"
    data["dataset_stable_key"] = dataset_key
    data["dataset_id"] = uid(dataset_key)
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-23",
        "status": "admitted",
        "admission_state": "admitted",
        "translation_state": "visually_checked",
        "qa_state": "translation_backend_build_visual_pass",
    }
    unit = {
        "id": unit_id,
        "stable_key": unit_key,
        "entity_type": "unit",
        "program_id": data["program"]["id"],
        "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"],
        "edition_id": data["edition"]["id"],
        "order": 14,
        "source_local_id": "chapter2.tex:766-909",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；伴随函子"},
            {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Fungtor Adjoin"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": bind(SOURCE, START, END),
        "target_binding": bind(TARGET, START, END),
        "section_ids": [section_id],
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [citation["id"] for citation in citations],
        "diagram_ids": [diagram["id"] for diagram in diagrams],
        "index_entry_ids": [entry["id"] for entry in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [qa["id"]],
        "outcome_keys": [
            "outcome/define-adjunctions",
            "outcome/identify-left-and-right-adjoints",
            "outcome/construct-units-and-counits",
            "outcome/verify-naturality",
            "outcome/apply-triangle-identities",
            "outcome/read-two-cell-pasting-diagrams",
            "outcome/distinguish-horizontal-and-vertical-composition",
            "outcome/characterize-full-faithfulness-from-unit-counit",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": len(citations),
            "diagrams": len(diagrams),
            "index_entries": len(index_entries),
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["unit"] = unit
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = [qa]

    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_backend.py"),
            "--lane-root",
            str(ROOT),
            "--data",
            str(OUTPUT),
            "--schema",
            str(ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"),
            "--csv-dir",
            str(ROOT / "backend/csv"),
            "--write-csv",
        ],
        cwd=ROOT,
        check=True,
    )
    missing_csv = [path for path in CSV_OUTPUTS if not path.is_file()]
    if missing_csv:
        missing = ", ".join(str(path.relative_to(ROOT)) for path in missing_csv)
        raise SystemExit(f"Unit 014 backend refused: CSV projection missing: {missing}")
    print(
        json.dumps(
            {
                "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest(OUTPUT.read_bytes()),
                "entities": (
                    5
                    + len(data["sections"])
                    + len(concepts)
                    + len(data["prerequisites"])
                    + len(data["rights"])
                    + len(citations)
                    + len(diagrams)
                    + len(index_entries)
                    + len(data["build_surfaces"])
                    + len(data["qa_events"])
                ),
                "concepts": len(concepts),
                "citations": len(citations),
                "diagrams": len(diagrams),
                "index_entries": len(index_entries),
                "csv_projections": [
                    str(path.relative_to(ROOT)).replace("\\", "/") for path in CSV_OUTPUTS
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
