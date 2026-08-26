#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 031.

Unit 031 is complete Section 4.7: solvable and nilpotent groups.
The shared schema has no native records for TeX environments, labels,
reference/citation occurrences, list items, protected mathematical zones,
terminology rows, correction provenance, or protected-text localizations, so
those surfaces are represented as deterministic UUIDv5 concept-compatible
entities.  The bibliography remains a bound build input, while index entries
the FT63 citation remains bound to the bibliography, and two TikZ-picture
diagrams plus one TikZ-CD diagram retain native/schema-compatible records.
Generation fails closed unless every authority, candidate, canonical target,
terminology, build, rights, review, visual-preflight, and final-reader binding
has its reviewed identity.
"""

from __future__ import annotations

from collections import Counter
import copy
import csv
import hashlib
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

import check_unit_031_candidate as candidate_check
import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
OUTPUT = ROOT / "backend/data/unit-031-bab-4-grup-solvabel-dan-nilpoten.json"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-031-candidate/chapter4-solvable-nilpotent-groups-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-031-bab-4-grup-solvabel-dan-nilpoten.tex"
COVER = "repo/source/coverpage-id-unit-031.tex"
CROSSREF = "repo/source/unit-031-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_031.ps1"
CANDIDATE_GATE = "scripts/check_unit_031_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_031_structure.py"
REVIEW = "qa/UNIT_031_TRANSLATION_REVIEW_20260826.md"
TERMINOLOGY_AUDIT = "qa/UNIT_031_TERMINOLOGY_AUDIT_20260826.md"
PREPROMOTION_AUDIT = "qa/UNIT_031_PREPROMOTION_AUDIT_20260826.md"
TERMINOLOGY_DELTA = "build/unit-031-staging/terminology-delta.csv"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
FINAL_LOG = "qa/UNIT_031_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_031_VISUAL_PREFLIGHT_20260826.md"
VISUAL_REVIEW = "qa/UNIT_031_VISUAL_QA_20260826.md"
STRUCTURE_PDF_QA = "qa/unit-031-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-031-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-031-bab-4-grup-solvabel-dan-nilpoten-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_PAGE_COUNT = 9

# The frozen authority boundary includes blank separator line 1107.  The
# record-aligned target mapping contains only substantive authority lines
# 936--1106, integrated at canonical target lines 933--1103 after the omitted
# boundary record.
SOURCE_START, SOURCE_END = 936, 1107
SOURCE_CONTENT_END = 1106
TARGET_START, TARGET_END = 933, 1103

TEMPLATE_ID = (
    352_612,
    "cceb010d8569c01e9fd7fb4149765da798a0c00409cadeb743a0326d192df29c",
)
SCHEMA_ID = (
    21_358,
    "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3",
)
SOURCE_FULL = (
    154_744,
    "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3",
)
SOURCE_SPAN = (
    16_048,
    "647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b",
)
SOURCE_CONTENT_SPAN = (
    16_047,
    "c36dd132f889dde696cb3720aff72221ee844f56c01e942a2a66d74d826b60d8",
)
CANDIDATE_FULL = (
    19_855,
    "6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81",
)
TARGET_FULL = (
    176_533,
    "440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f",
)
TARGET_SPAN = CANDIDATE_FULL
ARTIFACT_ID = (
    126_053,
    "313667c3f87439ccaac3f8708653bb352af0ba7a16c9d09b159ad1b836cc32fb",
)
BIBLIOGRAPHY_ID = (
    29_580,
    "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e",
)
CANDIDATE_GATE_ID = (
    16_303,
    "64bb71b1ca1a301ab341dbf5ac6a25601663507df2c93a5028bc63cb1d64beb1",
)
STRUCTURE_GATE_ID = (
    10_542,
    "933d1d12f220ec09346a62e1c308ffd68c3fe3d0db550a760b42c792cbec8f83",
)
REVIEW_ID = (
    2_121,
    "13adefab9be1b71da8cd880c70baab23d1511011d5cfed9b3b04844de2956ac3",
)
TERMINOLOGY_AUDIT_ID = (
    2_468,
    "16c039b657965f50110b16472818c8b49f82f40d492967a14edf251c87f09836",
)
PREPROMOTION_AUDIT_ID = (
    2_886,
    "a2857680175bd1b58116a331f6495967f24d1ef740e7bd1c9102b4567ca9ee38",
)
TERMINOLOGY_DELTA_ID = (
    2_766,
    "9939372a066946a23b644e6ed3a78abb9bbbc44d1a33879d3c63c9ef97147116",
)
TERMINOLOGY_ID = (
    69_632,
    "6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f",
)
BUILD_SCRIPT_ID = (
    5_021,
    "98a2ef100255e4c9f206570f6fd6bc80987cdd5da98f7fd13c889b36de18db6f",
)
FINAL_LOG_ID = (
    77_142,
    "47dd6cc5677888afeee4b7e0e7fb4800f16790125746b0f32c9a40216a79a548",
)
DRIVER_ID = (
    5_956,
    "0f6fa939eb1a65e0305ade87af2269c9f0637aad392fdf365e2430fb332bab75",
)
COVER_ID = (
    3_731,
    "1154a699b64acd6b5d619547b9ea8cd4860e196ecf79a07bab6d4bab51ca1ff1",
)
CROSSREF_ID = (
    196,
    "72ccb7c1412785aabb359965c7ada1248a882e8de6292c43d9a02c5324e631f6",
)
VISUAL_PREFLIGHT_ID = (
    1_357,
    "b23626c608fa4f8afce30375f657a0def5f1e9180c11c1c8ba84cc33510ea391",
)
VISUAL_REVIEW_ID = (
    6_392,
    "1c30ff4dfc36b7e7647b8712cce795703915bc98745cf6199e7306393287b0be",
)
STRUCTURE_PDF_QA_ID = (
    70_700,
    "7ad6a8ef294147fd6b14dfac88f4982da768606eec48d45c0b30be6162021167",
)
RENDER_HASH_INVENTORY_ID = (
    42_967,
    "a7d7bb3cd8aa8e660de56a3a6c9e5f29e37840e2a56eafbcf89bf65f4c5e28e3",
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 2,
        "cases": 1,
        "compactenum": 1,
        "compactitem": 2,
        "definition": 2,
        "enumerate": 1,
        "equation*": 1,
        "example": 2,
        "gather*": 1,
        "itemize": 1,
        "lemma": 4,
        "multline*": 1,
        "pmatrix": 2,
        "proof": 5,
        "proposition": 1,
        "remark": 1,
        "tikzcd": 1,
        "tikzpicture": 2,
    }
)

DIAGRAM_SPECS = (
    ("tikzpicture", 1, 954, 957, 951, 954),
    ("tikzpicture", 2, 958, 961, 955, 958),
    ("tikzcd", 1, 976, 979, 973, 976),
)

CITATION_SPECS = (("", "", "FT63", 1033, 1030),)

CORE_SPECS = (
    ("concept/solvable-group", "可解群", "grup solvabel", 942),
    ("concept/supersolvable-group", "超可解群", "grup supersolvabel", 943),
    ("concept/nilpotent-group", "幂零群", "grup nilpoten", 944),
    ("concept/commutator", "对易子", "komutator", 949),
    ("concept/derived-series", "导出列", "deret turunan", 954),
    ("concept/lower-central-series", "降中心列", "deret sentral menurun", 958),
    ("concept/derived-subgroup", "导出子群", "subgrup turunan", 972),
    ("concept/abelianization", "交换化", "abelianisasi", 972),
    ("concept/solvable-nilpotent-characterization", "可解与幂零判别", "kriteria solvabilitas dan nilpotensi", 986),
    ("concept/solvable-extension-criterion", "可解群扩张判别", "kriteria ekstensi grup solvabel", 1006),
    ("concept/nilpotent-implies-supersolvable", "幂零蕴涵超可解", "nilpoten mengakibatkan supersolvabel", 1021),
    ("concept/feit-thompson-theorem", "Feit--Thompson 定理", "Teorema Feit--Thompson", 1033),
    ("concept/upper-triangular-matrix-group", "上三角矩阵群", "grup matriks segitiga atas", 1036),
    ("concept/upper-central-series", "升中心列", "deret sentral menaik", 1075),
    ("concept/finite-p-groups-nilpotent", "有限 p-群皆幂零", "grup-p berhingga bersifat nilpoten", 1078),
    ("concept/heisenberg-group", "Heisenberg 群", "grup Heisenberg", 1084),
    ("concept/symplectic-form", "辛形式", "bentuk simplektik", 1087),
    ("concept/canonical-commutation-relation", "典则对易关系", "relasi komutasi kanonik", 1105),
    ("concept/fourier-transform", "Fourier 变换", "transformasi Fourier", 1105),
)

TERMINOLOGY_PAIRS = (
    ("solvable group", "grup solvabel"),
    ("supersolvable group", "grup supersolvabel"),
    ("nilpotent group", "grup nilpoten"),
    ("commutator", "komutator"),
    ("derived series", "deret turunan"),
    ("lower central series", "deret sentral menurun"),
    ("derived subgroup", "subgrup turunan"),
    ("upper central series", "deret sentral menaik"),
    ("symplectic form", "bentuk simplektik"),
    ("directional derivative", "turunan berarah"),
    ("canonical commutation relation", "relasi komutasi kanonik"),
    ("Heisenberg group", "grup Heisenberg"),
    ("upper triangular matrix group", "grup matriks segitiga atas"),
    ("Fourier transform", "transformasi Fourier"),
)

TERMINOLOGY_EVIDENCE = {
    source_term: target_term for source_term, target_term in TERMINOLOGY_PAIRS
}

SOURCE_CORRECTIONS = (
    (
        "O013-LI-U031-COR-001",
        (1016,),
        (1013,),
        "the induced supersolvable series does not explicitly remove repeated adjacent terms",
        "states that induced subquotients are trivial or prime-order cyclic and deletes repeated terms, completing the proof without altering its theorem claim",
    ),
)

PROTECTED_TEXT_LOCALIZATIONS = (
    ("O013-LI-U031-LOC-001", 1014, 1011, "可解", "solvabel"),
    ("O013-LI-U031-LOC-002", 1014, 1011, "幂零", "nilpoten"),
    ("O013-LI-U031-LOC-003", 1061, 1058, "常数项", "suku konstan"),
    ("O013-LI-U031-LOC-004", 1061, 1058, "仅含 $q$ 的项", "suku yang hanya memuat $q$"),
    ("O013-LI-U031-LOC-005", 1061, 1058, "仅含 $v$ 的项", "suku yang hanya memuat $v$"),
    ("O013-LI-U031-LOC-006", 1061, 1058, "含 $qv$ 的项", "suku yang memuat $qv$"),
    ("O013-LI-U031-LOC-007", 1097, 1094, "逐点乘以 ", "perkalian titik demi titik dengan "),
    ("O013-LI-U031-LOC-008", 1098, 1095, "方向导数", "turunan berarah"),
)

# Digital reflow is publication-layout provenance, not a mathematical source
# correction.  The exact refreshed target lines and identity are populated
# after the independent display-line reflow is frozen.
DIGITAL_REFLOWS = (
    (
        "O013-LI-U031-REFLOW-001",
        (1061,),
        (1058,),
        "the four-term display right-hand side occupies one source row and measures 42.13312 pt overfull in the Indonesian reader",
        "inserts a TeX display break after the q-only term and an empty group before the continuation plus, preserving the equality, all signs, all terms, and their order",
    ),
)

PREREQUISITES = (
    "prerequisite/basic-mathematical-literacy",
    "prerequisite/elementary-set-theory",
    "prerequisite/basic-group-theory",
    "prerequisite/group-homomorphisms-kernels-and-quotients",
    "prerequisite/group-actions-orbits-and-stabilizers",
    "prerequisite/elementary-number-theory",
    "prerequisite/composition-series-and-jordan-holder-theory",
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-031-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 031 backend refused: " + message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str | Path) -> tuple[int, str]:
    path = relative if isinstance(relative, Path) else ROOT / relative
    payload = path.read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str | Path, expected: tuple[int, str]) -> None:
    path = relative if isinstance(relative, Path) else ROOT / relative
    if not path.is_file() or identity(path) != expected:
        refuse(f"identity drift for {path.relative_to(ROOT).as_posix()}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    return common.normalized_span(relative, first, last)


def binding(relative: str, first: int | None = None, last: int | None = None):
    return base.binding(relative, first, last)


def span_text(relative: str, first: int, last: int) -> str:
    return normalized_span(relative, first, last).decode("utf-8")


def line_at(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def normalized_source_content() -> str:
    lines = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END).splitlines()
    if len(lines) != 171:
        refuse("source substantive-record extraction drift")
    return "\n".join(
        candidate_check.normalize_authority_line(line, SOURCE_START + offset)
        for offset, line in enumerate(lines)
    ) + "\n"


def protected_math_occurrences(text: str):
    spans: list[tuple[int, str, str]] = []
    for kind, regex in (
        ("inline", candidate_check.INLINE_MATH_RE),
        ("display-bracket", candidate_check.DISPLAY_MATH_RE),
        ("display-environment", candidate_check.MATH_ENV_RE),
    ):
        for match in regex.finditer(text):
            content = match.group(2) if regex is candidate_check.MATH_ENV_RE else match.group(1)
            spans.append((match.start(), kind, candidate_check.normalize_math(content)))
    return tuple(
        (ordinal, kind, line_at(text, position), value)
        for ordinal, (position, kind, value) in enumerate(sorted(spans), 1)
    )


def drawing_command_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return tuple(
        (match.group(1), line_at(text, match.start()))
        for match in re.finditer(r"\\(foreach|draw|node)(?![A-Za-z])", text)
    )


def read_terminology_rows() -> tuple[tuple[dict[str, str], int, int], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 435 or len({row.get("source_term") for row in rows}) != 435:
        refuse("controlled glossary row/uniqueness drift")
    with (ROOT / TERMINOLOGY_DELTA).open("r", encoding="utf-8", newline="") as handle:
        delta = tuple(csv.DictReader(handle))
    if len(delta) != 14 or tuple(rows[-14:]) != delta:
        refuse("fourteen-row Unit 031 glossary delta drift")
    by_source = {row["source_term"]: row for row in rows}
    target_lines = span_text(TARGET, TARGET_START, TARGET_END).splitlines()
    selected = []
    for source_term, target_term in TERMINOLOGY_PAIRS:
        row = by_source.get(source_term)
        if row is None:
            refuse(f"terminology row missing: {source_term!r}")
        if (
            row.get("target_term") != target_term
            or row.get("status") != "admitted"
            or not row.get("scope")
            or not row.get("note")
        ):
            refuse(f"terminology admission drift for {source_term!r}")
        evidence_fragment = TERMINOLOGY_EVIDENCE.get(source_term, target_term)
        occurrences = [
            offset
            for offset, line in enumerate(target_lines)
            if evidence_fragment.casefold() in line.casefold()
        ]
        if not occurrences:
            refuse(f"admitted Unit 031 term absent: {source_term!r} -> {target_term!r}")
        relative = occurrences[0] + 1
        selected.append((row, SOURCE_START + relative - 1, TARGET_START + relative - 1))
    return tuple(selected)


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
        refuse("pdfinfo failed\n" + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        refuse("pdfinfo returned no page count")
    return int(match.group(1))


def gate() -> tuple[int, tuple[tuple[dict[str, str], int, int], ...]]:
    pinned = (
        (TEMPLATE, TEMPLATE_ID),
        (SCHEMA, SCHEMA_ID),
        (SOURCE, SOURCE_FULL),
        (CANDIDATE, CANDIDATE_FULL),
        (TARGET, TARGET_FULL),
        (BIBLIOGRAPHY, BIBLIOGRAPHY_ID),
        (DRIVER, DRIVER_ID),
        (COVER, COVER_ID),
        (CROSSREF, CROSSREF_ID),
        (BUILD_SCRIPT, BUILD_SCRIPT_ID),
        (CANDIDATE_GATE, CANDIDATE_GATE_ID),
        (STRUCTURE_GATE, STRUCTURE_GATE_ID),
        (REVIEW, REVIEW_ID),
        (TERMINOLOGY_AUDIT, TERMINOLOGY_AUDIT_ID),
        (PREPROMOTION_AUDIT, PREPROMOTION_AUDIT_ID),
        (TERMINOLOGY_DELTA, TERMINOLOGY_DELTA_ID),
        (TERMINOLOGY, TERMINOLOGY_ID),
        (FINAL_LOG, FINAL_LOG_ID),
        (VISUAL_PREFLIGHT, VISUAL_PREFLIGHT_ID),
        (VISUAL_REVIEW, VISUAL_REVIEW_ID),
        (STRUCTURE_PDF_QA, STRUCTURE_PDF_QA_ID),
        (RENDER_HASH_INVENTORY, RENDER_HASH_INVENTORY_ID),
        (ARTIFACT, ARTIFACT_ID),
    )
    for relative, expected in pinned:
        require_identity(relative, expected)

    source_span = normalized_span(SOURCE, SOURCE_START, SOURCE_END)
    source_content = normalized_span(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    target_span = normalized_span(TARGET, TARGET_START, TARGET_END)
    if (len(source_span), digest(source_span)) != SOURCE_SPAN:
        refuse("source boundary span drift")
    if (len(source_content), digest(source_content)) != SOURCE_CONTENT_SPAN:
        refuse("source substantive span drift")
    if source_span != source_content + b"\n":
        refuse("authority line 1107 is not exactly the omitted blank boundary record")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("canonical target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    source_records = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_records = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_records) != 1_898 or (ROOT / SOURCE).read_bytes().endswith(b"\n"):
        refuse("authority Chapter 4 record/EOF census drift")
    if len(target_records) != 1_894 or not (ROOT / TARGET).read_bytes().endswith(b"\n"):
        refuse("canonical Chapter 4 record/EOF census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "PASS unit-031 candidate admission",
            (
                SOURCE_SPAN[1],
                CANDIDATE_FULL[1],
                "declared_proof_repairs=1",
                "declared_digital_reflows=1",
                "protected_text_localizations=8",
            ),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 031 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1], TERMINOLOGY_ID[1], "glossary_rows=435", "terminology_delta_rows=14"),
        ),
    ):
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / relative)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if completed.returncode or marker not in completed.stdout:
            refuse(f"{relative} failed\n" + completed.stdout + completed.stderr)
        for token in tokens:
            if token not in completed.stdout:
                refuse(f"{relative} output lacks {token}")

    raw_source_text = source_content.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_env = common.environment_occurrences(raw_source_text)
    target_env = common.environment_occurrences(target_text)
    if (
        [(item[0], item[1]) for item in source_env]
        != [(item[0], item[1]) for item in target_env]
        or Counter(item[0] for item in source_env) != EXPECTED_ENVIRONMENTS
        or len(source_env) != 31
    ):
        refuse("31-pair textual environment topology drift")

    source_labels = common.label_occurrences(raw_source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 6:
        refuse("six-label topology drift")
    source_refs = common.reference_occurrences(raw_source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 7:
        refuse("seven-reference topology drift")
    if Counter(item[0] for item in source_refs) != Counter({"ordinary": 7}):
        refuse("reference-kind census drift")
    source_citations = common.citation_occurrences(raw_source_text)
    target_citations = common.citation_occurrences(target_text)
    if (
        tuple(
            (
                source_note,
                target_note,
                source_key,
                SOURCE_START + source_line - 1,
                TARGET_START + target_line - 1,
            )
            for (source_note, source_key, source_line), (target_note, target_key, target_line)
            in zip(source_citations, target_citations, strict=True)
            if source_key == target_key
        )
        != CITATION_SPECS
    ):
        refuse("citation topology drift")
    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if len(source_items) != 14 or len(target_items) != 14:
        refuse("fourteen-item topology drift")

    normalized_source = normalized_source_content()
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    if (
        [(item[1], item[3]) for item in source_math]
        != [(item[1], item[3]) for item in target_math]
        or len(source_math) != 326
    ):
        refuse("326-zone protected mathematics drift")

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    expected_source_diagrams = tuple(item[:4] for item in DIAGRAM_SPECS)
    expected_target_diagrams = tuple((item[0], item[1], item[4], item[5]) for item in DIAGRAM_SPECS)
    if source_diagrams != expected_source_diagrams or target_diagrams != expected_target_diagrams:
        refuse("three-diagram topology drift")
    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    if len(source_arrows) != 3 or len(target_arrows) != 3:
        refuse("three-arrow diagram surface drift")
    source_drawing = drawing_command_occurrences(raw_source_text)
    target_drawing = drawing_command_occurrences(target_text)
    if [item[0] for item in source_drawing] != ["node", "node"] or [item[0] for item in target_drawing] != ["node", "node"]:
        refuse("two-node drawing-command surface drift")

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    if len(source_indexes) != 9 or len(target_indexes) != 9 or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]:
        refuse("nine-index topology or stream drift")
    if Counter(item[0] for item in source_indexes) != Counter({"main": 6, "sym1": 3}):
        refuse("main/symbol index census drift")

    for environment in ("Exercises", "exercise", "problem", "hint", "answer", "solution"):
        if f"\\begin{{{environment}}}" in raw_source_text or f"\\begin{{{environment}}}" in target_text:
            refuse(f"invented or unexpected {environment} surface")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 031 target")

    terminology_rows = read_terminology_rows()
    bibliography_text = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8")
    if "@article {FT63," not in bibliography_text:
        refuse("FT63 bibliography closure drift")
    page_count = pdfinfo_page_count()
    if page_count != EXPECTED_PAGE_COUNT:
        refuse(f"final reader page count drift: {page_count}")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    # PTY capture can wrap the word ``pages`` between ``p`` and ``ages``.
    page_hits = re.findall(r"Output written on .*?\((\d+)\s+p\s*ages?", final_log, re.DOTALL)
    if not page_hits or int(page_hits[-1]) != page_count:
        refuse("final build-log page count drift")
    for token in (
        "Undefined control sequence",
        "There were undefined references",
        "Citation `",
        "! LaTeX Error",
        "Emergency stop",
        "Fatal error",
        "Overfull \\hbox",
        "Overfull \\vbox",
    ):
        if token in final_log:
            refuse(f"final build log contains blocker {token!r}")
    visual = (ROOT / VISUAL_PREFLIGHT).read_text(encoding="utf-8")
    for token in ("PASS WITH WARNINGS", MODEL, "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual:
            refuse(f"visual preflight lacks {token!r}")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS WITH WARNINGS", MODEL, "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual_review:
            refuse(f"canonical visual review lacks {token!r}")

    structure_qa = json.loads((ROOT / STRUCTURE_PDF_QA).read_text(encoding="utf-8"))
    if (
        structure_qa.get("status") != "PASS_WITH_WARNINGS"
        or structure_qa.get("actionable_defects") != []
        or structure_qa.get("cross_pdf_semantic_identity") is not True
        or structure_qa.get("documents", {}).get("artifact", {}).get("identity")
        != {"bytes": ARTIFACT_ID[0], "path": ARTIFACT, "sha256": ARTIFACT_ID[1]}
        or not all(structure_qa.get("documents", {}).get("artifact", {}).get("checks", {}).values())
        or structure_qa.get("final_build_log", {}).get("identity")
        != {"bytes": FINAL_LOG_ID[0], "path": FINAL_LOG, "sha256": FINAL_LOG_ID[1]}
        or any(structure_qa.get("final_build_log", {}).get("fatal_diagnostics", {}).values())
        or structure_qa.get("final_build_log", {}).get("page_marker") != EXPECTED_PAGE_COUNT
    ):
        refuse("canonical structure-and-PDF QA semantics drift")

    render_inventory = json.loads((ROOT / RENDER_HASH_INVENTORY).read_text(encoding="utf-8"))
    comparisons = render_inventory.get("decoded_pixel_comparisons", {})
    comparison_results = [
        comparisons.get(renderer, {}).get(pair, {}).get(f"all_{EXPECTED_PAGE_COUNT}_decoded_pixel_identical")
        for renderer in ("poppler", "mupdf")
        for pair in ("build-i_vs_build-j", "build-j_vs_artifact")
    ]
    manual = render_inventory.get("manual_visual_review", {})
    if (
        render_inventory.get("status") != "PASS_WITH_WARNINGS"
        or render_inventory.get("identities", {}).get("artifact")
        != {"bytes": ARTIFACT_ID[0], "path": ARTIFACT, "sha256": ARTIFACT_ID[1]}
        or render_inventory.get("identities", {}).get("final-build-log")
        != {"bytes": FINAL_LOG_ID[0], "path": FINAL_LOG, "sha256": FINAL_LOG_ID[1]}
        or render_inventory.get("identities", {}).get("build-j_artifact_byte_identical") is not True
        or comparison_results != [True, True, True, True]
        or render_inventory.get("edge_gate") != {f"all_{6 * EXPECTED_PAGE_COUNT}_zero_ink": True, "outer_band_pixels": 3}
        or manual.get("status") != "PASS"
        or manual.get("pages_per_document") != EXPECTED_PAGE_COUNT
        or manual.get("actionable_defects") != []
        or set(manual.get("renderers", [])) != {"Poppler", "MuPDF"}
        or len(manual.get("findings", {})) != EXPECTED_PAGE_COUNT
        or len(render_inventory.get("contact_sheets", [])) != 6
    ):
        refuse("canonical render-hash inventory semantics drift")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    if MODEL not in re.sub(r"\s+", " ", terminology_audit):
        refuse("terminology audit lacks exact production-model provenance")
    return page_count, terminology_rows


def main() -> None:
    page_count, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-4-grup-solvabel-dan-nilpoten"
    unit_id = uid(unit_key)
    raw_source_text = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    normalized_source = normalized_source_content()
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    supplemental_prerequisites = (
        (
            "prerequisite/group-homomorphisms-kernels-and-quotients",
            "群同态、核与商群",
            "homomorfisme grup, kernel, dan grup hasil bagi",
            177,
            364,
        ),
        (
            "prerequisite/group-actions-orbits-and-stabilizers",
            "群作用、轨道与稳定化子",
            "aksi grup, orbit, dan stabilisator",
            518,
            665,
        ),
        (
            "prerequisite/composition-series-and-jordan-holder-theory",
            "合成列与 Jordan--Hölder 理论",
            "deret komposisi dan teori Jordan--Hölder",
            796,
            935,
        ),
    )
    existing_prerequisites = {item["stable_key"] for item in data["prerequisites"]}
    for prerequisite_key, source_label, target_label, first, last in supplemental_prerequisites:
        if prerequisite_key in existing_prerequisites:
            continue
        data["prerequisites"].append(
            {
                "id": uid(prerequisite_key),
                "stable_key": prerequisite_key,
                "entity_type": "prerequisite",
                "labels": [
                    {"language": "zh-Hans", "text": source_label},
                    {"language": "id-ID", "text": target_label},
                ],
                "requiredness": "expected",
                "source_evidence": {"path": SOURCE, "line_start": first, "line_end": last},
            }
        )

    concepts: list[dict[str, object]] = []

    def add_concept(stable_key: str, source_label: str, target_label: str, *, source_language: str = "zh-Hans") -> None:
        concept = common.surface_concept(uid, stable_key, source_label, target_label)
        concept["labels"][0]["language"] = source_language
        concepts.append(concept)

    for stable_key, source_label, target_label, _ in CORE_SPECS:
        add_concept(stable_key, source_label, target_label)

    source_env = common.environment_occurrences(raw_source_text)
    target_env = common.environment_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-031/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}; state active",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}; keadaan aktif",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.label_occurrences(raw_source_text), common.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-031/label/{ordinal:03d}",
            f"label {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"label {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.reference_occurrences(raw_source_text), common.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-031/reference/{kind}/{ordinal:03d}",
            f"{kind} reference {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-031/item/{ordinal:03d}",
            f"list item {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"butir daftar {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(
            f"surface/unit-031/diagram-arrow/{ordinal:03d}",
            f"tikzcd arrow {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"panah tikzcd {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(drawing_command_occurrences(raw_source_text), drawing_command_occurrences(target_text), strict=True), 1):
        command, source_line = source_item
        target_command, target_line = target_item
        if command != target_command:
            refuse(f"drawing command {ordinal} pairing drift")
        add_concept(
            f"surface/unit-031/drawing-command/{ordinal:03d}-{command}",
            f"TikZ drawing command {ordinal:03d}: {command}; authority line {SOURCE_START + source_line - 1}",
            f"perintah gambar TikZ {ordinal:03d}: {command}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    for source_item, target_item in zip(source_math, target_math, strict=True):
        ordinal, kind, source_line, source_formula = source_item
        _, target_kind, target_line, target_formula = target_item
        if kind != target_kind or source_formula != target_formula:
            refuse(f"protected math zone {ordinal} pairing drift")
        add_concept(
            f"surface/unit-031/protected-math-zone/{ordinal:03d}-{kind}",
            f"protected {kind} mathematical zone {ordinal:03d}; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"zona matematika terlindungi {kind} {ordinal:03d}; baris target {TARGET_START + target_line - 1}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_language="en",
        )

    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PAIRS[ordinal - 1]
        add_concept(
            f"surface/unit-031/terminology-row/{ordinal:03d}",
            f"terminology row {ordinal:03d}: {source_term}; representative authority line {source_line}",
            f"baris terminologi {ordinal:03d}: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}",
            source_language="en",
        )

    for correction_id, source_lines_abs, target_lines_abs, source_issue, target_issue in SOURCE_CORRECTIONS:
        add_concept(
            f"correction/{correction_id.casefold()}",
            f"declared source correction {correction_id}; authority lines {','.join(map(str, source_lines_abs))}; {source_issue} Evidence: {REVIEW}.",
            f"koreksi sumber terdeklarasi {correction_id}; baris target {','.join(map(str, target_lines_abs))}; {target_issue} Bukti: {REVIEW}.",
            source_language="en",
        )

    for reflow_id, source_lines_abs, target_lines_abs, source_layout, target_layout in DIGITAL_REFLOWS:
        add_concept(
            f"digital-reflow/{reflow_id.casefold()}",
            f"target-only digital reflow {reflow_id}; authority lines {','.join(map(str, source_lines_abs))}; {source_layout} Evidence: {PREPROMOTION_AUDIT}.",
            f"reflow digital khusus target {reflow_id}; baris target {','.join(map(str, target_lines_abs))}; {target_layout} Bukti: {PREPROMOTION_AUDIT}.",
            source_language="en",
        )

    for localization_id, source_line, target_line, source_text, target_text_fragment in PROTECTED_TEXT_LOCALIZATIONS:
        add_concept(
            f"protected-text-localization/{localization_id.casefold()}",
            f"protected-text localization {localization_id}; authority line {source_line}; {source_text} localized without changing mathematical topology; evidence {REVIEW}",
            f"lokalisasi teks terlindungi {localization_id}; baris target {target_line}; {source_text} menjadi {target_text_fragment} tanpa mengubah topologi matematika; bukti {REVIEW}",
            source_language="en",
        )

    add_concept(
        "provenance/o013-li-u031-production",
        f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.",
        f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.",
        source_language="en",
    )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    if not set(PREREQUISITES).issubset(prerequisite_by_key):
        refuse("required Unit 031 prerequisite absent")

    rights_by_key = {item["stable_key"]: item for item in data["rights"]}
    expected_right_keys = {
        "rights/principal-cc-by-4.0",
        "rights/lanzhou-cc-by-sa-3.0",
        "rights/ajbook-fragment-cc-by-sa-3.0",
        "rights/noto-fonts-ofl-1.1",
    }
    if set(rights_by_key) != expected_right_keys:
        refuse("rights-component inventory drift")
    rights_by_key["rights/principal-cc-by-4.0"]["bindings"] = [
        binding(SOURCE),
        binding(CANDIDATE),
        binding(TARGET),
        binding(BIBLIOGRAPHY),
        binding("repo/source/LICENSE"),
        binding("repo/source/ccby.png"),
    ]
    rights_by_key["rights/principal-cc-by-4.0"]["applies_to_unit"] = True
    rights_by_key["rights/lanzhou-cc-by-sa-3.0"]["applies_to_unit"] = False
    rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["applies_to_unit"] = True
    rights_by_key["rights/noto-fonts-ofl-1.1"]["applies_to_unit"] = True
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    unit_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
        rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
    ]

    section_key = f"{unit_key}/section/01"
    section_id = uid(section_key)
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter4.tex:936-1107 (line 1107 blank boundary omitted from target mapping)",
        "titles": [
            {"language": "zh-Hans", "text": "可解群与幂零群"},
            {"language": "id-ID", "text": "Grup Solvabel dan Grup Nilpoten"},
        ],
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [prerequisite_by_key[key] for key in PREREQUISITES],
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    citations = []
    for ordinal, (source_item, target_item) in enumerate(
        zip(
            common.citation_occurrences(raw_source_text),
            common.citation_occurrences(target_text),
            strict=True,
        ),
        1,
    ):
        note, bib_key, source_line = source_item
        target_note, target_bib_key, target_line = target_item
        if bib_key != target_bib_key or source_line != target_line:
            refuse(f"citation {ordinal} pairing drift")
        key = f"citation/unit-031/{ordinal:02d}-{bib_key.casefold()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": bib_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": BIBLIOGRAPHY_ID[1],
                "source_line": SOURCE_START + source_line - 1,
                "target_line": TARGET_START + target_line - 1,
                "section_id": section_id,
            }
        )

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        stream, source_key, source_line = source_item
        target_stream, target_key, target_line = target_item
        if stream != target_stream:
            refuse(f"index stream drift at ordinal {ordinal}")
        key = f"index-entry/unit-031/{stream}/{ordinal:03d}"
        index_entries.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "index_entry",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_key": source_key,
                "target_key": target_key,
                "source_binding": binding(SOURCE, source_line, source_line),
                "target_binding": binding(TARGET, target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-031/{source_format}-{occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": occurrence,
                "source_binding": binding(SOURCE, source_first, source_last),
                "target_binding": binding(TARGET, target_first, target_last),
                "rights_component_id": principal,
                "state": "audited_preserved",
            }
        )

    inputs = [
        COVER,
        TARGET,
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
        "id": uid("build-surface/unit-031-pdf"),
        "stable_key": "build-surface/unit-031-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_031.ps1 -OutputDirectory build/unit-031-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(FINAL_LOG),
        "build_script": binding(BUILD_SCRIPT),
        "page_count": page_count,
        "status": "pass",
        "driver": binding(DRIVER),
        "input_bindings": [binding(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "Biber",
            "makeindex (main and sym1 streams)",
            "Poppler pdfinfo",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 031 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    def qa_event(key: str, check_type: str, scope: str, witness: str) -> dict[str, object]:
        return {
            "id": uid(key),
            "stable_key": key,
            "entity_type": "qa_event",
            "unit_id": unit_id,
            "check_type": check_type,
            "result": "pass",
            "scope": scope,
            "witness": witness,
            "translation_audit_state": "pass",
            "build_state": "pass",
            "visual_state": "pass",
            "witness_binding": binding(witness),
        }

    qa_events = [
        qa_event(
            "qa/unit-031/admission-gate",
            "admission_gate",
            "Complete source-order Section 4.7 admission: authority lines 936-1107 with blank boundary line 1107 omitted from the 171-record target mapping at canonical lines 933-1103; 31 active environment pairs, six labels, seven references, one FT63 citation, nine index entries, three diagram arrows across two tikzpicture diagrams and one tikzcd diagram, 326 protected mathematical zones, fourteen admitted terminology rows, one proof repair, one target-only digital reflow, eight protected-text localizations, and no exercises, hints, answers, or solutions. Principal CC BY 4.0 content rights remain separate from AJbook and Noto build-closure licenses; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.",
            VISUAL_REVIEW,
        ),
        qa_event("qa/unit-031/source-review", "backend_integrity", "Exact authority, translation, mathematics, identifiers, diagrams, indexes, corrections, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-031/candidate-artifact", "backend_integrity", "Exact isolated 171-record Indonesian candidate binding; evidence only, not a public-reader build input.", CANDIDATE),
        qa_event("qa/unit-031/candidate-check", "backend_integrity", "Fail-closed candidate checker binding 172 authority records, 171 target records, 326 protected mathematical zones, three diagrams with three arrows, nine index entries, fourteen terminology rows, one proof repair, one target-only digital reflow, and eight protected-text localizations.", CANDIDATE_GATE),
        qa_event("qa/unit-031/canonical-integration", "backend_integrity", "Fail-closed canonical integration binding the prior admitted prefix, Unit 031 candidate at lines 933-1103, omitted authority blank boundary, untouched Section 4.8 suffix, 435-row glossary, and fourteen-row delta.", STRUCTURE_GATE),
        qa_event("qa/unit-031/source-corrections", "backend_integrity", "Deterministic source adjudication records one declared supersolvability proof repair at authority line 1016 and target line 1013.", REVIEW),
        qa_event("qa/unit-031/digital-reflow", "backend_integrity", "One target-only display reflow at authority line 1061 and target line 1058 removes a measured 42.13312 pt overflow while preserving the equality, signs, terms, and order; it is not a source correction.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-031/protected-text-localizations", "backend_integrity", "Eight exact protected-text localizations at authority lines 1014, 1061, 1097, and 1098 and target lines 1011, 1058, 1094, and 1095 preserve surrounding mathematical topology.", REVIEW),
        qa_event("qa/unit-031/terminology-control", "backend_integrity", "Live id-ID glossary binding for exactly 435 unique rows including the fourteen admitted Unit 031 rows.", TERMINOLOGY),
        qa_event("qa/unit-031/terminology-delta", "backend_integrity", "Exact reviewed fourteen-row terminology delta reproduced as the controlled glossary tail without rewriting baseline rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-031/terminology-evidence", "backend_integrity", "Bound Unit 031 terminology audit, evidence limits, international-term decisions, and exact model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-031/prepromotion-evidence", "backend_integrity", "Exact splice arithmetic for target lines 933-1103, omission of authority blank line 1107, suffix continuity from Section 4.8, additive terminology append, and separate digital-reflow provenance.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-031/citation-closure", "backend_integrity", "The exact FT63 citation resolves in the complete bound Al-jabr.bib bibliography input.", BIBLIOGRAPHY),
        qa_event("qa/unit-031/build-log", "backend_integrity", f"Final deterministic XeLaTeX, Biber, and dual-index build log with {EXPECTED_PAGE_COUNT}-page output and no fatal, unresolved, citation, or overfull markers.", FINAL_LOG),
        qa_event("qa/unit-031/visual-preflight", "backend_integrity", "Preserved independent all-page Poppler and MuPDF preflight for both clean builds; decoded-pixel, PDF-structure, font, navigation, safety, and exact final-reader identity pass with only documented non-blocking warnings.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-031/structure-and-pdf-qa", "backend_integrity", f"Canonical machine-readable PDF structure, metadata, language, destinations, actions, fonts, text geometry, build-log, active-payload, and {EXPECTED_PAGE_COUNT}-page checks for the exact final artifact.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-031/render-hash-inventory", "backend_integrity", f"Canonical all-page Poppler and MuPDF render identities: {6 * EXPECTED_PAGE_COUNT} renders, four {EXPECTED_PAGE_COUNT}-page decoded-pixel comparisons, six contact sheets, and the zero-ink outer-edge gate.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-031/all-page-visual-review", "backend_integrity", f"Canonical independent full-resolution review of all {EXPECTED_PAGE_COUNT} pages in Poppler and MuPDF; zero actionable defects with documented accessibility and font-subset warnings.", VISUAL_REVIEW),
    ]

    prerequisite_ids = [prerequisite_by_key[key] for key in PREREQUISITES]
    titles = [
        {"language": "zh-Hans", "text": "第四章：可解群与幂零群"},
        {"language": "id-ID", "text": "Bab 4: Grup Solvabel dan Grup Nilpoten"},
    ]
    data["dataset_stable_key"] = "dataset/unit-031/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u031-backend")),
        "updated": "2026-08-26",
        "status": "admitted",
        "admission_state": "admitted",
        "translation_state": "visually_checked",
        "qa_state": "translation_math_backend_build_visual_pass",
    }
    data["unit"] = {
        "id": unit_id,
        "stable_key": unit_key,
        "entity_type": "unit",
        "program_id": data["program"]["id"],
        "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"],
        "edition_id": data["edition"]["id"],
        "order": 31,
        "source_local_id": "chapter4.tex:936-1107; substantive authority map 936-1106 to target 933-1103",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "section_ids": [section_id],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [
            "outcome/define-solvable-supersolvable-and-nilpotent-groups",
            "outcome/use-derived-and-central-series-and-abelianization",
            "outcome/apply-inheritance-and-solvable-extension-criteria",
            "outcome/analyze-triangular-matrix-finite-p-and-heisenberg-groups",
            "outcome/connect-symplectic-forms-commutation-and-fourier-transform",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 1,
            "diagrams": 3,
            "index_entries": 9,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = qa_events

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "scripts/validate_backend.py"),
            "--lane-root",
            str(ROOT),
            "--data",
            str(OUTPUT),
            "--schema",
            str(SCHEMA),
            "--csv-dir",
            str(ROOT / "backend/csv"),
            "--write-csv",
        ],
        cwd=ROOT,
        check=True,
    )
    missing_csv = [path for path in CSV_OUTPUTS if not path.is_file()]
    if missing_csv:
        refuse("missing CSV projection")
    print(
        json.dumps(
            {
                "path": OUTPUT.relative_to(ROOT).as_posix(),
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest(OUTPUT.read_bytes()),
                "sections": 1,
                "concepts": len(concepts),
                "textual_environment_pairs": len(source_env),
                "active_environment_pairs": len(source_env),
                "labels": len(common.label_occurrences(raw_source_text)),
                "references": len(common.reference_occurrences(raw_source_text)),
                "citations": len(citations),
                "items": len(source_items),
                "protected_math_zones": len(source_math),
                "diagrams": len(diagrams),
                "diagram_arrows": len(source_arrows),
                "drawing_commands": len(drawing_command_occurrences(raw_source_text)),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "source_corrections": len(SOURCE_CORRECTIONS),
                "digital_reflows": len(DIGITAL_REFLOWS),
                "protected_text_localizations": len(PROTECTED_TEXT_LOCALIZATIONS),
                "artifact": {"pages": page_count, "bytes": ARTIFACT_ID[0], "sha256": ARTIFACT_ID[1]},
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
