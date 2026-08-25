#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 025.

Unit 025 is the Chapter 4 opening and complete Section 4.1.  The shared
schema has no first-class TeX-environment, label, reference occurrence, list
item, formula, terminology-row, or correction record, so those surfaces are
represented by deterministic UUIDv5 concept-compatible entities.  Citations
and index entries retain their native schema records.  Generation is refused
until the frozen authority/target topology, final PDF build, and all-page
visual receipt are present and pass.
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

import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-024-bab-3-latihan.json"
OUTPUT = ROOT / "backend/data/unit-025-bab-4-semigrup-monoid-dan-grup.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-025-candidate/chapter4-group-basics-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-025-bab-4-semigrup-monoid-dan-grup.tex"
COVER = "repo/source/coverpage-id-unit-025.tex"
CROSSREF = "repo/source/unit-025-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_025.ps1"
CANDIDATE_GATE = "scripts/check_unit_025_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_025_structure.py"
REVIEW = "qa/UNIT_025_SOURCE_AND_TRANSLATION_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = "qa/UNIT_025_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = "qa/UNIT_025_PREPROMOTION_AUDIT_20260825.md"
FINAL_LOG = "qa/UNIT_025_BUILD_FINAL.log"
VISUAL_REVIEW = "qa/UNIT_025_VISUAL_QA_20260825.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
ARTIFACT = "artifacts/unit-025-bab-4-semigrup-monoid-dan-grup-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_START, SOURCE_END = 1, 176
TARGET_START, TARGET_END = 1, 178
SOURCE_FULL = (
    154_744,
    "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3",
)
SOURCE_SPAN = (
    15_528,
    "d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52",
)
CANDIDATE_FULL = (
    20_464,
    "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a",
)
TARGET_FULL = (
    159_681,
    "b1b055416d392a66708047afb20a14175566c7839286979baac6289d3d125419",
)
TARGET_SPAN = CANDIDATE_FULL
BIBLIOGRAPHY_ID = (
    29_580,
    "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e",
)
CANDIDATE_GATE_ID = (
    12_628,
    "bd146f046b09c104460572d5817a486541449a45ad6de37809a1341a1622cbbb",
)
STRUCTURE_GATE_ID = (
    6_106,
    "899e18526193008895af1241bea1b5fd3c3aa1586f9fcae8ff8bc8a452a39a60",
)
REVIEW_ID = (
    7_278,
    "6808b93200f40a987182320ae67e59fefdab7515588b061835b1037523807086",
)
TERMINOLOGY_AUDIT_ID = (
    3_501,
    "6b1180e019297141038bd548653b9d4c7130388111c5441fec96218633822a0e",
)
PREPROMOTION_AUDIT_ID = (
    2_133,
    "39fab50288570c8a9ce3be52c39639e0a2a7da8f7066a826266dbf7e6570908d",
)
TERMINOLOGY_ID = (
    51_472,
    "3ed2a7a30aa06e9e574e36b237bf13ab6cec6779703ce91bc3238a107fe526b1",
)

SECTION_SPECS = (
    (1, 1, 26, 1, 28, "第四章导言", "Pengantar Bab 4"),
    (2, 27, 176, 29, 178, "半群、幺半群与群", "Semigrup, Monoid, dan Grup"),
)
CORE_SPECS = (
    ("concept/group-theory-framework", "群论的形式与具体面向", "kerangka formal dan konkret teori grup", 10),
    ("concept/binary-operation", "二元运算", "operasi biner", 28),
    ("concept/opposite-structure", "相反结构", "struktur lawan", 32),
    ("concept/semigroup", "半群", "semigrup", 46),
    ("concept/monoid", "幺半群", "monoid", 46),
    ("concept/invertible-element", "可逆元", "unsur invertibel", 43),
    ("concept/group", "群", "grup", 60),
    ("concept/unit-group", "单位群", "grup unit", 64),
    ("concept/general-linear-group", "一般线性群", "grup linear umum", 78),
    ("concept/symmetric-group", "对称群", "grup simetris", 84),
    ("concept/subgroup", "子群", "subgrup", 89),
    ("concept/normal-subgroup", "正规子群", "subgrup normal", 89),
    ("concept/simple-group", "单群", "grup sederhana", 99),
    ("concept/generated-subgroup", "生成子群", "subgrup yang dibangkitkan", 104),
    ("concept/cyclic-group", "循环群", "grup siklik", 110),
    ("concept/coset", "陪集", "koset", 118),
    ("concept/double-coset-decomposition", "双陪集分解", "dekomposisi koset ganda", 130),
    ("concept/lagrange-theorem", "Lagrange 定理", "teorema Lagrange", 143),
    ("concept/group-center-centralizer-normalizer", "中心、中心化子与正规化子", "pusat, sentralisator, dan normalisator", 160),
    ("concept/subgroup-product-normality", "子群乘积与正规性", "hasil kali subgrup dan kenormalan", 173),
)

# source term, admitted target term, representative authority line, target line
TERMINOLOGY_SPECS = (
    ("binary operation", "operasi biner", 28, 30),
    ("semigroup", "semigrup", 46, 48),
    ("monoid", "monoid", 46, 48),
    ("submonoid", "submonoid", 52, 54),
    ("identity element", "unsur identitas", 40, 42),
    ("left cancellation law", "hukum pembatalan kiri", 35, 37),
    ("right cancellation law", "hukum pembatalan kanan", 35, 37),
    ("unit group", "grup unit", 64, 66),
    ("subgroup", "subgrup", 89, 91),
    ("normal subgroup", "subgrup normal", 89, 91),
    ("trivial subgroup", "subgrup trivial", 95, 97),
    ("simple group", "grup sederhana", 99, 101),
    ("generated subgroup", "subgrup yang dibangkitkan", 104, 106),
    ("cyclic group", "grup siklik", 110, 112),
    ("group order", "orde grup", 60, 62),
    ("element order", "orde unsur", 108, 110),
    ("coset", "koset", 118, 121),
    ("left coset", "koset kiri", 121, 124),
    ("right coset", "koset kanan", 122, 125),
    ("double coset", "koset ganda", 123, 126),
    ("center (group theory)", "pusat", 160, 163),
    ("centralizer", "sentralisator", 160, 163),
    ("normalizer", "normalisator", 160, 163),
    ("symmetric group", "grup simetris", 84, 86),
    ("alternating group", "grup selang-seling", 102, 104),
    ("permutation group", "grup permutasi", 85, 87),
    ("general linear group", "grup linear umum", 78, 80),
    ("magma", "magma", 28, 30),
    ("index of a subgroup", "indeks subgrup", 125, 128),
    ("Lagrange's theorem", "teorema Lagrange", 146, 149),
)

CORRECTIONS = (
    (
        "O013-LI-U025-COR-001",
        115,
        118,
        "The source classifies subgroups of the additive group of integers but writes H as a subset of an undefined ambient G; the target repairs the ambient set to Z.",
    ),
)

# Four target-only repairs restore explicit parent display keys for nested
# index entries.  They change neither source mathematics nor the single
# source-correction inventory.
INDEX_HIERARCHY_REPAIRS = (
    (
        6,
        "yaobanqun!子幺半群",
        52,
        "yaobanqun@monoid (monoid)!submonoid",
        54,
    ),
    (
        8,
        "qun!阶 (order)",
        60,
        "qun@grup (group)!orde (order)",
        62,
    ),
    (
        15,
        "qun!单 (simple)",
        99,
        "qun@grup (group)!sederhana (simple)",
        101,
    ),
    (
        18,
        "qun!阶 (order)",
        108,
        "qun@grup (group)!orde (order)",
        110,
    ),
)

PREREQUISITES_BY_SECTION = {
    1: (
        "prerequisite/basic-mathematical-literacy",
        "prerequisite/elementary-set-theory",
        "prerequisite/basic-group-theory",
    ),
    2: (
        "prerequisite/basic-mathematical-literacy",
        "prerequisite/elementary-set-theory",
        "prerequisite/basic-group-theory",
        "prerequisite/matrices",
    ),
}

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-025-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 025 backend refused: " + message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        refuse(f"identity drift for {relative}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    return common.normalized_span(relative, first, last)


def source_binding(relative: str, first: int | None = None, last: int | None = None):
    return base.binding(relative, first, last)


def target_binding(first: int, last: int) -> dict[str, object]:
    selected = normalized_span(TARGET, first, last)
    return {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
        "line_start": first,
        "line_end": last,
        "span_sha256": digest(selected),
        "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
    }


def span_text(relative: str, first: int, last: int) -> str:
    return normalized_span(relative, first, last).decode("utf-8")


def target_line_for_source(source_line: int) -> int:
    """Map authority lines to target lines across two provenance lines and correction disclosure."""

    if not SOURCE_START <= source_line <= SOURCE_END:
        refuse(f"authority line outside Unit 025: {source_line}")
    return source_line + (2 if source_line <= 114 else 3)


def section_ordinal_for_source_line(source_line: int) -> int:
    for ordinal, first, last, _, _, _, _ in SECTION_SPECS:
        if first <= source_line <= last:
            return ordinal
    refuse(f"no Unit 025 section owns authority line {source_line}")


def read_terminology_rows() -> tuple[dict[str, str], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 341 or len({row.get("source_term") for row in rows}) != 341:
        refuse("controlled glossary row/uniqueness drift")
    selected = []
    for source_term, target_term, _, _ in TERMINOLOGY_SPECS:
        matches = [row for row in rows if row.get("source_term") == source_term]
        if len(matches) != 1:
            refuse(f"terminology row {source_term!r} is not unique")
        row = matches[0]
        if (
            row.get("target_term") != target_term
            or row.get("status") != "admitted"
            or not row.get("scope")
            or not row.get("note")
        ):
            refuse(f"terminology admission drift for {source_term!r}")
        selected.append(row)
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


def gate() -> tuple[int, tuple[dict[str, str], ...]]:
    required = (
        TEMPLATE.relative_to(ROOT).as_posix(),
        SOURCE,
        CANDIDATE,
        TARGET,
        DRIVER,
        COVER,
        CROSSREF,
        BIBLIOGRAPHY,
        BUILD_SCRIPT,
        CANDIDATE_GATE,
        STRUCTURE_GATE,
        REVIEW,
        TERMINOLOGY_AUDIT,
        PREPROMOTION_AUDIT,
        TERMINOLOGY,
        FINAL_LOG,
        VISUAL_REVIEW,
        ARTIFACT,
    )
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    if missing:
        refuse("final inputs are missing:\n  - " + "\n  - ".join(missing))

    require_identity(SOURCE, SOURCE_FULL)
    require_identity(CANDIDATE, CANDIDATE_FULL)
    require_identity(TARGET, TARGET_FULL)
    require_identity(BIBLIOGRAPHY, BIBLIOGRAPHY_ID)
    require_identity(CANDIDATE_GATE, CANDIDATE_GATE_ID)
    require_identity(STRUCTURE_GATE, STRUCTURE_GATE_ID)
    require_identity(REVIEW, REVIEW_ID)
    require_identity(TERMINOLOGY_AUDIT, TERMINOLOGY_AUDIT_ID)
    require_identity(PREPROMOTION_AUDIT, PREPROMOTION_AUDIT_ID)
    require_identity(TERMINOLOGY, TERMINOLOGY_ID)

    source_span = normalized_span(SOURCE, SOURCE_START, SOURCE_END)
    target_span = normalized_span(TARGET, TARGET_START, TARGET_END)
    if (len(source_span), digest(source_span)) != SOURCE_SPAN:
        refuse("source span drift")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    if len((ROOT / SOURCE).read_bytes().splitlines(keepends=True)) != 1_898:
        refuse("authority Chapter 4 line-record census drift")
    if len((ROOT / TARGET).read_bytes().splitlines(keepends=True)) != 1_900:
        refuse("canonical Chapter 4 line-record census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "UNIT 025 CANDIDATE CHECK: PASS",
            (SOURCE_SPAN[1], CANDIDATE_FULL[1]),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 025 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1],),
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

    source_text = source_span.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_env = common.environment_occurrences(source_text)
    target_env = common.environment_occurrences(target_text)
    expected_env_counts = Counter(
        {
            "definition": 7,
            "compactenum": 4,
            "example": 4,
            "inparaenum": 2,
            "proof": 2,
            "wenxintishi": 1,
            "itemize": 1,
            "convention": 1,
            "compactitem": 1,
            "lemma": 1,
            "proposition": 1,
            "align*": 1,
            "remark": 1,
        }
    )
    if (
        [(item[0], item[1]) for item in source_env]
        != [(item[0], item[1]) for item in target_env]
        or Counter(item[0] for item in source_env) != expected_env_counts
        or len(source_env) != 27
    ):
        refuse("27-environment topology drift")
    source_labels = common.label_occurrences(source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 10:
        refuse("ten-label topology drift")
    source_refs = common.reference_occurrences(source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 11:
        refuse("eleven-reference topology drift")
    source_cites = common.citation_occurrences(source_text)
    target_cites = common.citation_occurrences(target_text)
    if [item[:2] for item in source_cites] != [item[:2] for item in target_cites] or len(source_cites) != 3:
        refuse("three-citation topology drift")
    source_items = common.occurrence_lines(source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if len(source_items) != 24 or len(target_items) != 24:
        refuse("24-item topology drift")
    source_inline = common.inline_formula_occurrences(source_text)
    target_inline = common.inline_formula_occurrences(target_text)
    source_brackets = common.bracket_formula_occurrences(source_text)
    target_brackets = common.bracket_formula_occurrences(target_text)
    source_environment_formulae = common.environment_formula_occurrences(source_text)
    target_environment_formulae = common.environment_formula_occurrences(target_text)
    if not (
        len(source_inline) == len(target_inline) == 271
        and len(source_brackets) == len(target_brackets) == 8
        and len(source_environment_formulae) == len(target_environment_formulae) == 1
    ):
        refuse("280-formula topology drift")
    base.SPAN_START = 1
    if base.diagram_occurrences(source_text) or base.diagram_occurrences(target_text):
        refuse("unexpected diagram surface")
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    if (
        len(source_indexes) != 25
        or len(target_indexes) != 25
        or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]
    ):
        refuse("25-index topology or stream drift")
    for ordinal, source_key, source_line, target_key, target_line in INDEX_HIERARCHY_REPAIRS:
        if source_indexes[ordinal - 1] != ("main", source_key, source_line):
            refuse(f"source index-hierarchy repair witness drift at ordinal {ordinal}")
        if target_indexes[ordinal - 1] != ("main", target_key, target_line):
            refuse(f"target index-hierarchy repair drift at ordinal {ordinal}")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 025 target")

    terms = read_terminology_rows()
    target_lines = target_text.splitlines()
    for row, spec in zip(terms, TERMINOLOGY_SPECS, strict=True):
        _, target_term, _, target_line = spec
        visible = re.sub(r"\\(?:emph|text)\{([^{}]*)\}", r"\1", target_lines[target_line - 1])
        relaxed = {
            "generated subgroup": "subgrup yang",
            "group order": "orde",
            "element order": "orde",
            "index of a subgroup": "indeks",
        }.get(row["source_term"], target_term)
        if relaxed.casefold() not in visible.casefold():
            refuse(f"representative target line lacks terminology row {row['source_term']!r}")

    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    prepromotion = (ROOT / PREPROMOTION_AUDIT).read_text(encoding="utf-8")
    for token in ("PASS", "1–176", MODEL, CORRECTIONS[0][0], "280"):
        if token not in review:
            refuse(f"source review lacks {token!r}")
    for token in ("PASS", "thirty", MODEL, TERMINOLOGY_ID[1]):
        if token not in terminology_audit:
            refuse(f"terminology audit lacks {token!r}")
    for token in (
        "PASS",
        "a1a60706d405f7f672b2cbcf99598911db93c1b4fa079779c7501ce4c00b7665",
        "6d2ebda2e8b291bcc0d104d00af0eea06bfb2c88b6bfa479d1c5e07147deebe1",
    ):
        if token not in prepromotion:
            refuse(f"prepromotion audit lacks {token!r}")

    page_count = pdfinfo_page_count()
    if page_count < 1:
        refuse("invalid final PDF page count")
    artifact_hash = identity(ARTIFACT)[1]
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    page_hits = re.findall(r"Output written on .*?\((\d+)\s+pages?", final_log, re.DOTALL)
    if not page_hits or int(page_hits[-1]) != page_count:
        refuse("final build log page count drift")
    for token in (
        "Undefined control sequence",
        "There were undefined references",
        "Citation `",
        "! LaTeX Error",
        "Emergency stop",
        "Fatal error",
    ):
        if token in final_log:
            refuse(f"final build log contains blocker {token!r}")
    visual = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS", str(page_count), "Poppler", "MuPDF", artifact_hash):
        if token not in visual:
            refuse(f"visual review lacks {token!r}")
    return page_count, terms


def main() -> None:
    page_count, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-4-semigrup-monoid-dan-grup"
    unit_id = uid(unit_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    concepts: list[dict[str, object]] = []
    concept_sections: dict[str, set[int]] = {}

    def add_concept(
        stable_key: str,
        source_label: str,
        target_label: str,
        *,
        source_line: int | None = None,
        source_language: str = "zh-Hans",
        target_language: str = "id-ID",
    ) -> None:
        concept = common.surface_concept(uid, stable_key, source_label, target_label)
        concept["labels"][0]["language"] = source_language
        concept["labels"][1]["language"] = target_language
        concepts.append(concept)
        if source_line is not None:
            concept_sections.setdefault(stable_key, set()).add(section_ordinal_for_source_line(source_line))

    for stable_key, source_label, target_label, source_line in CORE_SPECS:
        add_concept(stable_key, source_label, target_label, source_line=source_line)

    source_env = common.environment_occurrences(source_text)
    target_env = common.environment_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-025/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"环境 {ordinal:03d}: {environment} 第 {occurrence} 次; 源行 {source_first}-{source_last}",
            f"lingkungan {ordinal:03d}: {environment} kemunculan {occurrence}; baris target {target_first}-{target_last}",
            source_line=source_first,
        )

    for ordinal, (source_item, target_item) in enumerate(
        zip(common.label_occurrences(source_text), common.label_occurrences(target_text), strict=True), 1
    ):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-025/label/{ordinal:03d}",
            f"标签 {ordinal:03d}: {label}; 源行 {source_line}",
            f"label {ordinal:03d}: {label}; baris target {target_line}",
            source_line=source_line,
        )

    for ordinal, (source_item, target_item) in enumerate(
        zip(common.reference_occurrences(source_text), common.reference_occurrences(target_text), strict=True), 1
    ):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-025/reference/{kind}/{ordinal:03d}",
            f"引用 {ordinal:03d}: {label}; 源行 {source_line}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_line}",
            source_line=source_line,
        )

    source_items = common.occurrence_lines(source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-025/item/{ordinal:03d}",
            f"列表项 {ordinal:03d}; 源行 {source_line}",
            f"butir daftar {ordinal:03d}; baris target {target_line}",
            source_line=source_line,
        )

    source_inline = common.inline_formula_occurrences(source_text)
    target_inline = common.inline_formula_occurrences(target_text)
    for source_item, target_item in zip(source_inline, target_inline, strict=True):
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        add_concept(
            f"surface/unit-025/formula/inline/{ordinal:03d}",
            f"行内公式 {ordinal:03d}; 源行 {source_line}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"rumus sebaris {ordinal:03d}; baris target {target_line}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_line=source_line,
        )
    source_brackets = common.bracket_formula_occurrences(source_text)
    target_brackets = common.bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        add_concept(
            f"surface/unit-025/formula/display-bracket/{ordinal:03d}",
            f"陈列公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"rumus pajang {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_line=source_first,
        )
    source_environment_formulae = common.environment_formula_occurrences(source_text)
    target_environment_formulae = common.environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_environment_formulae, target_environment_formulae, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        environment_slug = re.sub(
            r"[^a-z0-9._/-]+", "-", environment.casefold()
        ).strip("-")
        add_concept(
            f"surface/unit-025/formula/display-environment/{ordinal:03d}-{environment_slug}",
            f"环境陈列公式 {ordinal:03d}: {environment}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"rumus pajang lingkungan {ordinal:03d}: {environment}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_line=source_first,
        )

    for ordinal, (row, spec) in enumerate(zip(terminology_rows, TERMINOLOGY_SPECS, strict=True), 1):
        source_term, target_term, source_line, target_line = spec
        add_concept(
            f"surface/unit-025/terminology-row/{ordinal:03d}",
            f"terminology row {ordinal:03d}: {source_term}; authority line {source_line}",
            f"baris terminologi {ordinal:03d}: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}",
            source_line=source_line,
            source_language="en",
        )

    add_concept(
        "localization/o013-li-u025-index-hierarchy-repair",
        "target-only index localization repair; four nested entries at source lines 52, 60, 99, and 108 receive explicit parent display keys; source TeX and mathematics are unchanged",
        "perbaikan lokalisasi indeks khusus target; empat entri bersarang pada baris target 54, 62, 101, dan 110 diberi kunci tampilan induk eksplisit; TeX sumber dan matematika tidak berubah",
        source_line=52,
        source_language="en",
    )

    for correction_id, source_line, target_line, issue in CORRECTIONS:
        add_concept(
            f"correction/{correction_id.casefold()}",
            f"declared source correction {correction_id}; source line {source_line}; target line {target_line}; {issue} Evidence: {REVIEW}.",
            f"koreksi sumber terdeklarasi {correction_id}; baris sumber {source_line}; baris target {target_line}; pembatas ambien H pada contoh grup aditif bilangan bulat diperbaiki dari G yang tidak terdefinisi menjadi Z. Bukti: {REVIEW}.",
            source_line=source_line,
            source_language="en",
        )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    basic_group_key = "prerequisite/basic-group-theory"
    if basic_group_key not in prerequisite_by_key:
        basic_group = {
            "id": uid(basic_group_key),
            "stable_key": basic_group_key,
            "entity_type": "prerequisite",
            "labels": [
                {"language": "zh-Hans", "text": "群论基础知识"},
                {"language": "id-ID", "text": "pengetahuan dasar tentang grup"},
            ],
            "requiredness": "expected",
            "source_evidence": {
                "path": SOURCE,
                "line_start": 17,
                "line_end": 17,
            },
        }
        data["prerequisites"].append(basic_group)
        prerequisite_by_key[basic_group_key] = basic_group["id"]

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
        source_binding(SOURCE),
        source_binding(TARGET),
        source_binding("repo/source/LICENSE"),
        source_binding("repo/source/ccby.png"),
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

    sections = []
    for ordinal, source_first, source_last, target_first, target_last, source_title, target_title in SECTION_SPECS:
        section_key = f"{unit_key}/section/{ordinal:02d}"
        local_keys = [key for key, owners in concept_sections.items() if ordinal in owners]
        sections.append(
            {
                "id": uid(section_key),
                "stable_key": section_key,
                "entity_type": "section",
                "parent_id": unit_id,
                "order": ordinal,
                "source_local_id": f"chapter4.tex:{source_first}-{source_last}",
                "titles": [
                    {"language": "zh-Hans", "text": source_title},
                    {"language": "id-ID", "text": target_title},
                ],
                "source_binding": source_binding(SOURCE, source_first, source_last),
                "target_binding": target_binding(target_first, target_last),
                "concept_ids": [concept_by_key[key] for key in local_keys],
                "prerequisite_ids": [
                    prerequisite_by_key[key] for key in PREREQUISITES_BY_SECTION[ordinal]
                ],
                "rights_component_ids": [principal],
                "translation_state": "visually_checked",
                "admission_state": "admitted",
            }
        )
    section_by_ordinal = {item["order"]: item["id"] for item in sections}

    citations = []
    for ordinal, (source_item, target_item) in enumerate(
        zip(common.citation_occurrences(source_text), common.citation_occurrences(target_text), strict=True), 1
    ):
        note, bib_key, source_line = source_item
        _, _, target_line = target_item
        key = f"citation/unit-025/{ordinal:02d}-{bib_key.casefold()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": bib_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": BIBLIOGRAPHY_ID[1],
                "source_line": source_line,
                "target_line": target_line,
                "section_id": section_by_ordinal[section_ordinal_for_source_line(source_line)],
            }
        )

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        stream, source_key, source_line = source_item
        target_stream, target_key, target_line = target_item
        if stream != target_stream:
            refuse(f"index stream drift at ordinal {ordinal}")
        key = f"index-entry/unit-025/{stream}/{ordinal:03d}"
        index_entries.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "index_entry",
                "section_id": section_by_ordinal[section_ordinal_for_source_line(source_line)],
                "ordinal_in_unit": ordinal,
                "source_key": source_key,
                "target_key": target_key,
                "source_binding": source_binding(SOURCE, source_line, source_line),
                "target_binding": target_binding(target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
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
        "repo/source/ccby.png",
        CROSSREF,
        BIBLIOGRAPHY,
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-025-pdf"),
        "stable_key": "build-surface/unit-025-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_025.ps1 -OutputDirectory build/unit-025-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": source_binding(ARTIFACT),
        "log_binding": source_binding(FINAL_LOG),
        "build_script": source_binding(BUILD_SCRIPT),
        "page_count": page_count,
        "status": "pass",
        "driver": source_binding(DRIVER),
        "input_bindings": [source_binding(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX",
            "Biber",
            "PowerShell 7",
            "makeindex (main and sym1 streams)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 025 driver and AJbook.cls",
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
            "witness_binding": source_binding(witness),
        }

    qa_events = [
        qa_event(
            "qa/unit-025/admission-gate",
            "admission_gate",
            "Complete source-order Chapter 4 opening and Section 4.1 admission: two natural sections, 27 environments, ten labels, eleven ordinary references, three citations, 24 list items, 271 inline formulae, eight bracket displays, one align display, 25 index entries, thirty admitted terminology rows, four target-only index hierarchy repairs, and correction O013-LI-U025-COR-001. There are no exercises, hints, answers, solutions, or diagrams. Source, translation, model provenance, and component rights remain distinct. Production provenance is " + MODEL + ".",
            VISUAL_REVIEW,
        ),
        qa_event(
            "qa/unit-025/source-review",
            "backend_integrity",
            "Continuous source, translation, mathematical, identifier, formula, citation, index, and correction review for authority lines 1-176.",
            REVIEW,
        ),
        qa_event(
            "qa/unit-025/candidate-check",
            "backend_integrity",
            "Fail-closed isolated candidate checker preserving 280 mathematical spans, ten labels, eleven references, three citations, 25 index entries, 24 items, the exact correction, and zero Han residue.",
            CANDIDATE_GATE,
        ),
        qa_event(
            "qa/unit-025/canonical-integration",
            "backend_integrity",
            "Fail-closed canonical integration binds the exact Indonesian prefix, unchanged authority suffix, terminal-LF normalization, and controlled terminology.",
            STRUCTURE_GATE,
        ),
        qa_event(
            "qa/unit-025/source-correction",
            "backend_integrity",
            "Deterministic provenance for O013-LI-U025-COR-001: the subgroup-classification example repairs the undefined ambient G to the explicitly governing additive group Z.",
            REVIEW,
        ),
        qa_event(
            "qa/unit-025/terminology-control",
            "backend_integrity",
            "Live id-ID glossary binding for exactly thirty admitted Unit 025 foundational group-theory rows.",
            TERMINOLOGY,
        ),
        qa_event(
            "qa/unit-025/terminology-evidence",
            "backend_integrity",
            "Bound Unit 025 terminology audit records official evidence, semantic adjudication, consistency repairs, schema integrity, uniqueness, and exact hashes.",
            TERMINOLOGY_AUDIT,
        ),
        qa_event(
            "qa/unit-025/prepromotion-evidence",
            "backend_integrity",
            "Exact prepromotion arithmetic binds the pre-index-localization candidate baseline, untouched source suffix, canonical target prediction, and disclosed terminal-LF normalization; the later target-only index hierarchy repair is separately provenanced.",
            PREPROMOTION_AUDIT,
        ),
        qa_event(
            "qa/unit-025/index-hierarchy-localization",
            "backend_integrity",
            "One bounded target-only localization event restores explicit parent display keys for four nested index occurrences at target lines 54, 62, 101, and 110; index streams, mathematics, source TeX, and source-correction inventory remain unchanged.",
            STRUCTURE_GATE,
        ),
        qa_event(
            "qa/unit-025/build-log",
            "backend_integrity",
            "Final clean XeLaTeX, Biber, and two-index build log with no undefined controls, references, citations, or fatal errors.",
            FINAL_LOG,
        ),
        qa_event(
            "qa/unit-025/all-page-visual-review",
            "backend_integrity",
            "All-page Poppler and MuPDF visual review of the final deterministic Unit 025 reader.",
            VISUAL_REVIEW,
        ),
    ]

    prerequisite_keys = {
        key for values in PREREQUISITES_BY_SECTION.values() for key in values
    }
    prerequisite_ids = [
        item["id"] for item in data["prerequisites"] if item["stable_key"] in prerequisite_keys
    ]
    if len(prerequisite_ids) != len(prerequisite_keys):
        refuse("unit prerequisite inventory drift")

    titles = [
        {"language": "zh-Hans", "text": "第四章：半群、幺半群与群"},
        {"language": "id-ID", "text": "Bab 4: Semigrup, Monoid, dan Grup"},
    ]
    data["dataset_stable_key"] = "dataset/unit-025/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-25",
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
        "order": 25,
        "source_local_id": "chapter4.tex:1-176",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [
            "outcome/recognize-semigroups-monoids-and-groups",
            "outcome/analyze-invertibility-and-opposite-structures",
            "outcome/work-with-subgroups-normality-and-generation",
            "outcome/decompose-groups-into-cosets-and-apply-lagrange",
            "outcome/compute-centers-centralizers-and-normalizers",
        ],
        "surface_counts": {
            "sections": 2,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 3,
            "diagrams": 0,
            "index_entries": 25,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = []
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = qa_events

    OUTPUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
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
        refuse("missing CSV projection")
    print(
        json.dumps(
            {
                "path": OUTPUT.relative_to(ROOT).as_posix(),
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest(OUTPUT.read_bytes()),
                "sections": len(sections),
                "concepts": len(concepts),
                "environments": len(source_env),
                "labels": len(common.label_occurrences(source_text)),
                "references": len(common.reference_occurrences(source_text)),
                "citations": len(citations),
                "items": len(source_items),
                "formula_entities": len(source_inline) + len(source_brackets) + len(source_environment_formulae),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "corrections": len(CORRECTIONS),
                "artifact": {
                    "pages": page_count,
                    "bytes": identity(ARTIFACT)[0],
                    "sha256": identity(ARTIFACT)[1],
                },
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
