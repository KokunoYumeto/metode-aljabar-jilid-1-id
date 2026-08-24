#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 015."""

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
TEMPLATE = ROOT / "backend/data/unit-014-bab-2-fungtor-adjoin-dasar.json"
OUTPUT = ROOT / "backend/data/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.tex"
COVER = "repo/source/coverpage-id-unit-015.tex"
CROSSREF = "repo/source/unit-015-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_015.ps1"
STRUCTURE_GATE = "scripts/check_unit_015_structure.py"
SUMMARY = "qa/unit-015-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_015_ADMISSION_20260824.md"
FINAL_LOG = "qa/UNIT_015_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.pdf"
STRUCTURE_QA = "qa/unit-015-evidence/structure-and-pdf-qa.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 910, 1110
SOURCE_FULL = (
    139983,
    "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840",
)
TARGET_FULL = (
    158252,
    "a106ec94b9c2b4a276371e6527b0c7c86dfd84538dde0be8e31848d59d2caf8c",
)
SOURCE_SPAN = (
    16925,
    "49c812f4cdb1929cf11e1bc3e5d916d21e82051d17a686f826c1b171a1f33062",
)
TARGET_SPAN = (
    19355,
    "df3c65bfea7f7272a31809b96b5ae18fdf966afe22e9ab38a0d8f9d35680520f",
)
ARTIFACT_ID = (
    120466,
    "6f2a9be12465300ac7af2ea086b643b6891b1f9e23af66241a40086ac476c8ef",
)
FINAL_LOG_ID = (
    84703,
    "6d7fa510890ee32c19b65b2b51046b771f8e93570f6d6f1a9f17f0745fcc5874",
)
PAGE_COUNT = 10

LABELS = (
    "eg:top-adjunction",
    "eg:forgetful-adjunction",
    "prop:adjunction-pointwise",
    "prop:adjunction-uniqueness",
    "prop:adjunction-composition",
    "prop:adjoint-equivalence",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
    "eqn:adj-equiv-two-expression",
)
REFERENCES = (
    "def:free-group",
    "prop:adjunction-uniqueness",
    "eg:metric-completion",
    "prop:representable-functor-uniqueness",
    "prop:adjunction-pointwise",
    "def:cat-equivalence",
    "prop:naturaltrans-associativity",
    "sec:braiding",
)
EQUATION_REFERENCES = (
    "eqn:unit-counit-relation",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-2",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-2",
    "eqn:adj-zigzag-1",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
)
CITATIONS = (("[Chapter 4]", "Co11", 1109),)
INDEX_SLUGS = (
    "adjunction-composition",
    "category-equivalence",
    "adjoint-equivalence",
)
CORRECTIONS = (
    (
        "O013-LI-U015-COR-001",
        962,
        "The prime is attached after the comma in the second adjunction tuple.",
    ),
    (
        "O013-LI-U015-COR-002",
        997,
        "The baseline midpoint refers to A1 from a preceding picture instead of local node A2.",
    ),
)
EXPECTED_AUX = (
    r"\newlabel{def:free-group}{{4.8.{2}}{130}}",
    r"\newlabel{eg:metric-completion}{{2.4.{6}}{3}}",
    r"\newlabel{prop:representable-functor-uniqueness}{{2.5.{4}}{2}}",
    r"\newlabel{def:cat-equivalence}{{2.2.{8}}{6}}",
    r"\newlabel{eqn:unit-counit-relation}{{2.6}{3}}",
    r"\newlabel{prop:naturaltrans-associativity}{{2.2.{7}}{4}}",
    r"\newlabel{sec:braiding}{{3.3}{82}}",
)
EXPECTED_EQUATION_NUMBERING = {
    "eqn:adj-zigzag-1": "2.7",
    "eqn:adj-zigzag-2": "2.8",
    "eqn:adj-equiv-two-expression": "2.9",
    "status": (
        "matches source-order Chapter 2 identifiers after setting the standalone "
        "equation counter to 6"
    ),
}
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-015-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
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
        raise SystemExit(f"Unit 015 backend refused: identity drift for {relative}")


def citation_occurrences(text: str) -> tuple[tuple[str, str, int], ...]:
    pattern = re.compile(r"\\cite(\[[^]]+\])?\{([^}]+)\}")
    return tuple(
        (
            match.group(1) or "",
            match.group(2),
            START + text.count("\n", 0, match.start()),
        )
        for match in pattern.finditer(text)
    )


def ordinary_references(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"(?<!eq)\\ref\{([^}]+)\}", text))


def equation_references(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\\eqref\{([^}]+)\}", text))


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
            "Unit 015 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 015 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate_structure_qa() -> None:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"Unit 015 backend refused: structured QA witness is unreadable: {exc}"
        ) from exc
    if evidence.get("equation_numbering") != EXPECTED_EQUATION_NUMBERING:
        raise SystemExit(
            "Unit 015 backend refused: published equation-numbering evidence drift"
        )
    expected_artifact = {
        "path": ARTIFACT,
        "pages": PAGE_COUNT,
        "bytes": ARTIFACT_ID[0],
        "sha256": ARTIFACT_ID[1],
    }
    artifact = evidence.get("artifact", {})
    if any(artifact.get(key) != value for key, value in expected_artifact.items()):
        raise SystemExit("Unit 015 backend refused: structured artifact evidence drift")
    if evidence.get("full_target") != {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
    }:
        raise SystemExit("Unit 015 backend refused: structured target evidence drift")
    if evidence.get("structure", {}).get("status") != "pass":
        raise SystemExit("Unit 015 backend refused: structured topology status is not pass")
    if evidence.get("digital_reflow", {}).get("line_spacing") != "1.30":
        raise SystemExit("Unit 015 backend refused: structured reflow evidence drift")
    if evidence.get("model") != MODEL:
        raise SystemExit("Unit 015 backend refused: structured model provenance drift")


def gate() -> None:
    base.SPAN_START = START
    base.SPAN_END = END
    missing = [
        path
        for path in (SUMMARY, ADMISSION, STRUCTURE_QA)
        if not (ROOT / path).is_file()
    ]
    if missing:
        raise SystemExit(
            "Unit 015 backend scaffold is complete but final evidence is not yet present: "
            + ", ".join(missing)
        )
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(TARGET, TARGET_FULL)
    require_identity(ARTIFACT, ARTIFACT_ID)
    require_identity(FINAL_LOG, FINAL_LOG_ID)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 015 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 015 backend refused: target span drift")

    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 015 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass",
        "line_start": START,
        "line_end": END,
        "line_count": 201,
        "source_bytes": SOURCE_SPAN[0],
        "source_sha256": SOURCE_SPAN[1],
        "target_bytes": TARGET_SPAN[0],
        "target_sha256": TARGET_SPAN[1],
        "mathematics_source_count": 232,
        "mathematics_target_count": 232,
        "mathematics_multiset_equivalent_after_declared_corrections": True,
        "environment_sequence_exact": True,
        "environment_begin_count": 35,
        "citation_signatures_exact": True,
        "index_source_count": 3,
        "index_target_count": 3,
        "index_topology_exact": True,
        "diagram_blocks_exact_after_declared_corrections": True,
        "han_residue_count": 0,
        "next_boundary_ok": True,
    }
    if any(report.get(key) != value for key, value in required.items()):
        raise SystemExit("Unit 015 backend refused: structural evidence drift")
    expected_commands = {
        "labels": 9,
        "references": 8,
        "equation_references": 12,
    }
    for name, count in expected_commands.items():
        if report.get("commands", {}).get(name) != {
            "source_count": count,
            "target_count": count,
            "exact_argument_sequence": True,
        }:
            raise SystemExit(f"Unit 015 backend refused: {name} topology drift")
    if report.get("diagram_counts") != {"tikzcd": 4, "tikzpicture": 16}:
        raise SystemExit("Unit 015 backend refused: diagram count drift")
    if report.get("declared_source_corrections") != [
        {"id": item[0], "source_line": item[1], "issue": item[2], "applied": True}
        for item in CORRECTIONS
    ]:
        raise SystemExit("Unit 015 backend refused: correction disclosure drift")

    source = span(SOURCE).decode()
    target = span(TARGET).decode()
    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if source_diagrams != target_diagrams or len(source_diagrams) != 20:
        raise SystemExit("Unit 015 backend refused: diagram occurrence topology drift")
    for text in (source, target):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit("Unit 015 backend refused: label topology drift")
        if ordinary_references(text) != REFERENCES:
            raise SystemExit("Unit 015 backend refused: ordinary-reference topology drift")
        if equation_references(text) != EQUATION_REFERENCES:
            raise SystemExit("Unit 015 backend refused: equation-reference topology drift")
        if citation_occurrences(text) != CITATIONS:
            raise SystemExit("Unit 015 backend refused: citation topology drift")
    source_indexes = base.index_occurrences(source)
    target_indexes = base.index_occurrences(target)
    if [(item[0], item[2]) for item in source_indexes] != [
        ("main", 955), ("main", 972), ("main", 972)
    ]:
        raise SystemExit("Unit 015 backend refused: source index topology drift")
    if [(item[0], item[2]) for item in target_indexes] != [
        ("main", 955), ("main", 972), ("main", 972)
    ]:
        raise SystemExit("Unit 015 backend refused: target index topology drift")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    target_lines = (ROOT / TARGET).read_text(encoding="utf-8").splitlines()
    if "(F', G,'" not in source_lines[961] or "(F', G'," not in target_lines[961]:
        raise SystemExit("Unit 015 backend refused: COR-001 evidence drift")
    if "(A0)!.5!(A1)" not in source_lines[996] or "(A0)!.5!(A2)" not in target_lines[996]:
        raise SystemExit("Unit 015 backend refused: COR-002 evidence drift")

    actual_aux = tuple(
        line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    if actual_aux != EXPECTED_AUX:
        raise SystemExit("Unit 015 backend refused: external-reference map drift")
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\setcounter{chapter}{2}",
        r"\setcounter{section}{6}",
        r"\setcounter{theorem}{6}",
        r"\setcounter{equation}{6}",
        r"\setstretch{1.30}",
        r"\InputSourceLineRange{chapter2.tex}{910}{1110}",
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 015 backend refused: driver lacks {needle!r}")
    gate_structure_qa()

    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+) pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != PAGE_COUNT:
        raise SystemExit("Unit 015 backend refused: final build-log page count drift")
    if pdfinfo_page_count() != PAGE_COUNT:
        raise SystemExit("Unit 015 backend refused: live PDF page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    admission = (ROOT / ADMISSION).read_text(encoding="utf-8")
    summary_needles = (
        f"PDF pages: {PAGE_COUNT}",
        f"Functional replay: {PAGE_COUNT}/{PAGE_COUNT} MuPDF pages and {PAGE_COUNT}/{PAGE_COUNT} Poppler pages",
        "Final-log blockers: zero",
        f"Visual QA: all {PAGE_COUNT} pages were personally inspected",
        "eqn:adj-zigzag-1",
        "(2.7)",
        "eqn:adj-zigzag-2",
        "(2.8)",
        "eqn:adj-equiv-two-expression",
        "(2.9)",
    )
    if any(needle not in summary for needle in summary_needles):
        raise SystemExit("Unit 015 backend refused: build summary is incomplete")
    admission_needles = (
        "Status: admitted locally",
        "chapter2.tex:910-1110",
        "source printed pages 54-58",
        "physical pages 60-64 of the official PDF",
        f"{PAGE_COUNT} pages",
        TARGET_SPAN[1],
        ARTIFACT_ID[1],
        FINAL_LOG_ID[1],
        "1.30",
        MODEL,
        "Wen-Wei Li",
        "CC BY 4.0",
        "CC BY-SA 3.0",
        "OFL 1.1",
        "non-endorsed derivative",
        "(2.7)",
        "(2.8)",
        "(2.9)",
        *(item[0] for item in CORRECTIONS),
    )
    if any(needle not in admission for needle in admission_needles):
        raise SystemExit("Unit 015 backend refused: admission receipt is incomplete")


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    bind = base.binding
    unit_key = "unit/bab-2-contoh-keunikan-dan-ekuivalensi-adjoin"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/contoh-keunikan-dan-ekuivalensi-adjoin"
    section_id = uid(section_key)

    concept_specs = [
        ("concept/adjunction-example", "伴随例", "contoh pasangan adjoin"),
        ("concept/free-forgetful-adjunction", "自由与遗忘伴随", "adjoin bebas--pelupa"),
        ("concept/discrete-topology", "离散拓扑", "topologi diskret"),
        ("concept/indiscrete-topology", "平凡拓扑", "topologi takdiskret"),
        ("concept/free-group", "自由群", "grup bebas"),
        ("concept/free-module", "自由模", "modul bebas"),
        ("concept/polynomial-ring", "多项式环", "gelanggang polinomial"),
        ("concept/abelianization", "交换化", "abelianisasi"),
        ("concept/compactification", "紧化", "pengompakan"),
        ("concept/stone-cech-compactification", "Stone--Čech 紧化", "pengompakan Stone--Čech"),
        ("concept/pointwise-adjunction", "逐对象伴随", "adjoin secara objek demi objek"),
        ("concept/adjunction-uniqueness", "伴随的唯一性", "keunikan adjoin"),
        ("concept/adjunction-composition", "伴随对的合成", "komposisi pasangan adjoin"),
        ("concept/adjoint-equivalence", "伴随等价", "ekuivalensi adjoin"),
        ("concept/category-equivalence", "范畴等价", "ekuivalensi kategori"),
        ("concept/quasi-inverse", "拟逆", "kuasi-invers"),
        ("concept/string-diagram", "弦图", "diagram untai (string diagram)"),
        ("concept/unit-of-adjunction", "单位", "unit"),
        ("concept/counit-of-adjunction", "余单位", "kounit"),
    ]
    for label in LABELS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-015/label/{slug}", f"标签 {label}", f"label {label}"))
    for label in dict.fromkeys(REFERENCES + ("eqn:unit-counit-relation",)):
        slug = label.replace(":", "-").lower()
        concept_specs.append(
            (f"surface/unit-015/reference/{slug}", f"外部引用 {label}", f"rujukan eksternal {label}")
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
    concept_ids = [item["id"] for item in concepts]
    prerequisite_ids = [item["id"] for item in data["prerequisites"]]
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    principal = rights_by_key["rights/principal-cc-by-4.0"]
    unit_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_by_key["rights/noto-fonts-ofl-1.1"],
    ]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter2.tex:910-1110",
        "titles": [
            {"language": "zh-Hans", "text": "2.6 伴随函子（续）"},
            {"language": "id-ID", "text": "2.6 Fungtor Adjoin (lanjutan)"},
        ],
        "source_binding": bind(SOURCE, START, END),
        "target_binding": bind(TARGET, START, END),
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    bibliography_hash = identity(BIBLIOGRAPHY)[1]
    citations = []
    for option, bib_key, line in CITATIONS:
        key = f"citation/unit-015/{bib_key.lower()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": bib_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": bibliography_hash,
                "source_line": line,
                "target_line": line,
                "section_id": section_id,
            }
        )

    source_indexes = base.index_occurrences(span(SOURCE).decode())
    target_indexes = base.index_occurrences(span(TARGET).decode())
    index_entries = []
    for ordinal, (slug, source_index, target_index) in enumerate(
        zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1
    ):
        key = f"index-entry/unit-015/{slug}"
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

    source_diagrams = base.diagram_occurrences(span(SOURCE).decode())
    target_diagrams = base.diagram_occurrences(span(TARGET).decode())
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(
        zip(source_diagrams, target_diagrams, strict=True), 1
    ):
        source_format, source_occurrence, source_first, source_last = source_diagram
        target_format, target_occurrence, target_first, target_last = target_diagram
        if (source_format, source_occurrence, source_first, source_last) != (
            target_format,
            target_occurrence,
            target_first,
            target_last,
        ):
            raise SystemExit("Unit 015 backend refused: diagram binding drift")
        key = f"diagram/unit-015/{source_format}-{source_occurrence}"
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
        "id": uid("build-surface/unit-015-pdf"),
        "stable_key": "build-surface/unit-015-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": (
            "pwsh -NoProfile -File scripts/build_unit_015.ps1 "
            "-OutputDirectory build/unit-015-replay"
        ),
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
            "packages loaded by the Unit 015 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    correction_ids = ", ".join(item[0] for item in CORRECTIONS)
    qa = {
        "id": uid("qa/unit-015/admission-gate"),
        "stable_key": "qa/unit-015/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and semantic review of chapter2.tex lines "
            "910-1110 (source pages 54-58; physical official-PDF pages 60-64); "
            "232 source and 232 target mathematics surfaces equivalent after two disclosed "
            f"source corrections ({correction_ids}); 35 balanced environments, nine labels, "
            "eight ordinary references, twelve equation references, one Co11 citation, "
            "three default index entries, twenty diagrams (four TikZ-CD and sixteen TikZ), "
            "no exercises, hints, answers, or solutions; exact equation continuity (2.7)-"
            "(2.9); 1.30 digital reflow; resolved frozen external references; separate "
            "CC BY 4.0 principal-text, CC BY-SA 3.0 class-fragment, and OFL 1.1 font "
            "rights; clean functional replay, PDF checks, and all-page visual QA. "
            "Translation provenance is "
            + MODEL
            + ", recorded separately from Wen-Wei Li's authorship and other human credit."
        ),
        "witness": ADMISSION,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(ADMISSION),
    }
    structured_qa = {
        "id": uid("qa/unit-015/structured-public-evidence"),
        "stable_key": "qa/unit-015/structured-public-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": (
            "Published structured QA binds the admitted target and reader identities, "
            "topology status, 1.30 digital reflow, exact model provenance, and source-order "
            "Chapter 2 equation identifiers eqn:adj-zigzag-1=(2.7), "
            "eqn:adj-zigzag-2=(2.8), and eqn:adj-equiv-two-expression=(2.9)."
        ),
        "witness": STRUCTURE_QA,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(STRUCTURE_QA),
    }

    data["dataset_stable_key"] = "dataset/unit-015/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-24",
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
        "order": 15,
        "source_local_id": "chapter2.tex:910-1110",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；伴随例、唯一性与伴随等价"},
            {
                "language": "id-ID",
                "text": "Bab 2: Dasar-Dasar Teori Kategori; Contoh, Keunikan, dan Ekuivalensi Adjoin",
            },
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": bind(SOURCE, START, END),
        "target_binding": bind(TARGET, START, END),
        "section_ids": [section_id],
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [qa["id"], structured_qa["id"]],
        "outcome_keys": [
            "outcome/recognize-free-forgetful-adjunctions",
            "outcome/construct-topological-adjunctions",
            "outcome/apply-pointwise-adjunctions",
            "outcome/prove-uniqueness-of-adjoints",
            "outcome/compose-adjunctions",
            "outcome/characterize-adjoint-equivalences",
            "outcome/read-string-diagram-proofs",
            "outcome/track-unit-counit-zigzags",
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
    data["qa_events"] = [qa, structured_qa]

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
        raise SystemExit(
            "Unit 015 backend refused: CSV projection missing: "
            + ", ".join(str(path.relative_to(ROOT)) for path in missing_csv)
        )
    print(
        json.dumps(
            {
                "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest(OUTPUT.read_bytes()),
                "entities": 5
                + len(data["sections"])
                + len(concepts)
                + len(data["prerequisites"])
                + len(data["rights"])
                + len(citations)
                + len(diagrams)
                + len(index_entries)
                + len(data["build_surfaces"])
                + len(data["qa_events"]),
                "concepts": len(concepts),
                "citations": len(citations),
                "diagrams": len(diagrams),
                "index_entries": len(index_entries),
                "csv_projections": [
                    str(path.relative_to(ROOT)).replace("\\", "/")
                    for path in CSV_OUTPUTS
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
