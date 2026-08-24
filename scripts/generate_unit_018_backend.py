#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 018.

The shared v1.1.0 schema has no first-class exercise, subpart, hint, TeX
reference, formula, or correction records.  Unit 018 therefore follows the
already admitted compatibility convention: its thirteen top-level exercises
are ordered section entities; five nested items, one hint, every reference,
every formula, and both declared corrections are deterministic concept-
compatible UUIDv5 entities.  The generator proves the complete live topology
and all admission evidence before writing the canonical JSON and six CSV
projections.
"""

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
TEMPLATE = ROOT / "backend/data/unit-017-bab-2-kelengkapan.json"
OUTPUT = ROOT / "backend/data/unit-018-bab-2-latihan.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-018-bab-2-latihan.tex"
COVER = "repo/source/coverpage-id-unit-018.tex"
CROSSREF = "repo/source/unit-018-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_018.ps1"
STRUCTURE_GATE = "scripts/check_unit_018_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_018_evidence.py"
SUMMARY = "qa/unit-018-evidence/build-log-summary.txt"
RENDER_INVENTORY = "qa/unit-018-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-018-evidence/structure-and-pdf-qa.json"
REVIEW = "qa/UNIT_018_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_018_MATH_STRUCTURE_AUDIT_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_QA = "qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md"
FINAL_LOG = "qa/UNIT_018_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-018-bab-2-latihan.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 1603, 1645
SOURCE_FULL = (
    139_983,
    "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840",
)
TARGET_FULL = (
    166_465,
    "3ef0e0dd3a8a30f4e44d7f87d94a4a4343ac7097a1862180c8becaf3631cda16",
)
SOURCE_SPAN = (
    5_197,
    "24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce",
)
TARGET_SPAN = (
    6_523,
    "d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55",
)
ARTIFACT_ID = (
    83_578,
    "4fc2997e6eafc8f2e74d8a03e3351cb49d99a95ae96ff254a211fbf505f6e00c",
)
TOP_LEVEL_ITEM_LINES = (
    1604,
    1605,
    1616,
    1617,
    1624,
    1625,
    1626,
    1627,
    1639,
    1640,
    1641,
    1643,
    1644,
)
NESTED_ITEM_LINES = (1619, 1620, 1621, 1629, 1630)
HINT_LINES = (1632,)
REFERENCES = (
    ("eg:forgetful-adjunction", 1625),
    ("prop:Yoneda-lemma", 1637),
    ("def:diagonal-functor", 1639),
)
CORRECTIONS = (
    (
        "O013-LI-U018-COR-001",
        1640,
        "The authority redundantly says to let the field k be a field; the target removes only the duplicated predicate.",
    ),
    (
        "O013-LI-U018-COR-002",
        1644,
        "The authority uses U without binding the displayed forgetful functor to that name; the target explicitly binds U.",
    ),
)
ADVERSE_BY_CORRECTION = {
    "O013-LI-U018-COR-001": "O013-ADV-0049",
    "O013-LI-U018-COR-002": "O013-ADV-0050",
}
EXPECTED_AUX = (
    r"\newlabel{prop:Yoneda-lemma}{{2.5.{1}}{0}}",
    r"\newlabel{eg:forgetful-adjunction}{{2.6.{8}}{0}}",
    r"\newlabel{def:diagonal-functor}{{2.7.{1}}{0}}",
)
EXERCISE_SPECS = (
    (1, 1604, 1604, "同构的复合判别", "Kriteria Isomorfisme melalui Komposisi"),
    (2, 1605, 1615, "范畴的并", "Gabungan Kategori"),
    (3, 1616, 1616, "有限全序集范畴", "Kategori Himpunan Terurut Total Berhingga"),
    (4, 1617, 1623, "商范畴的泛性质", "Sifat Universal Kategori Hasil Bagi"),
    (5, 1624, 1624, "范畴等价的复合", "Komposisi Ekuivalensi Kategori"),
    (6, 1625, 1625, "伴随对的余单位", "Kounit Pasangan Adjoin"),
    (7, 1626, 1626, "含幺与非含幺环", "Gelanggang dengan dan tanpa Syarat Unsur Satuan"),
    (8, 1627, 1637, "全忠实函子的伴随判别", "Kriteria Adjoin untuk Fungtor Penuh dan Setia"),
    (9, 1639, 1639, "对角函子与极限", "Fungtor Diagonal dan Limit"),
    (10, 1640, 1640, "有限生成对象的归纳极限", "Limit Induktif Objek yang Dibangkitkan Berhingga"),
    (11, 1641, 1642, "全子范畴与函子范畴", "Subkategori Penuh dan Kategori Fungtor"),
    (12, 1643, 1643, "带基点范畴的完备性", "Kelengkapan Kategori Bertitik Dasar"),
    (13, 1644, 1644, "带基点集合的忘却函子", "Fungtor Pelupa Himpunan Bertitik Dasar"),
)
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-018-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 018 backend refused: identity drift for {relative}")


def span(relative: str) -> bytes:
    return base.normalized_span(relative, START, END)


def absolute_line(text: str, offset: int) -> int:
    return START + text.count("\n", 0, offset)


def occurrences(text: str, pattern: str) -> tuple[tuple[str, int], ...]:
    return tuple(
        (match.group(1), absolute_line(text, match.start()))
        for match in re.finditer(pattern, text)
    )


def ordinary_reference_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return occurrences(text, r"(?<!eq)\\ref\{([^{}]+)\}")


def is_escaped(text: str, position: int) -> bool:
    count = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        count += 1
        position -= 1
    return count % 2 == 1


def inline_formula_occurrences(text: str) -> tuple[tuple[int, int, str], ...]:
    delimiters = tuple(
        offset
        for offset, character in enumerate(text)
        if character == "$" and not is_escaped(text, offset)
    )
    if len(delimiters) % 2:
        raise SystemExit("Unit 018 backend refused: unpaired inline-math delimiter")
    result = []
    for ordinal, offset in enumerate(range(0, len(delimiters), 2), 1):
        opening, closing = delimiters[offset : offset + 2]
        result.append(
            (ordinal, absolute_line(text, opening), text[opening + 1 : closing])
        )
    return tuple(result)


def pair_inline_formula_occurrences(source_items, target_items):
    """Pair exact same-line formulae first, then the disclosed corrected one."""

    unused = set(range(len(target_items)))
    paired: dict[int, int] = {}
    deferred = []
    for source_index, source_item in enumerate(source_items):
        _, source_line, source_formula = source_item
        candidates = [
            target_index
            for target_index in unused
            if target_items[target_index][1] == source_line
            and target_items[target_index][2] == source_formula
        ]
        if not candidates:
            deferred.append(source_index)
            continue
        chosen = min(candidates)
        unused.remove(chosen)
        paired[source_index] = chosen
    for source_index in deferred:
        source_line = source_items[source_index][1]
        candidates = [index for index in unused if target_items[index][1] == source_line]
        if len(candidates) != 1:
            raise SystemExit(
                "Unit 018 backend refused: ambiguous corrected formula pairing at "
                f"line {source_line}"
            )
        chosen = candidates[0]
        unused.remove(chosen)
        paired[source_index] = chosen
    if unused:
        raise SystemExit("Unit 018 backend refused: unpaired target inline formulae")
    return tuple(
        (source_item, target_items[paired[source_index]])
        for source_index, source_item in enumerate(source_items)
    )


def bracket_formula_occurrences(text: str):
    return tuple(
        (
            ordinal,
            absolute_line(text, match.start()),
            absolute_line(text, match.end() - 1),
            match.group(1),
        )
        for ordinal, match in enumerate(re.finditer(r"\\\[(.*?)\\\]", text, re.DOTALL), 1)
    )


def environment_formula_occurrences(text: str):
    pattern = re.compile(
        r"\\begin\{(equation\*?|align\*|gather\*)\}(.*?)\\end\{\1\}",
        re.DOTALL,
    )
    return tuple(
        (
            ordinal,
            match.group(1),
            absolute_line(text, match.start()),
            absolute_line(text, match.end() - 1),
            match.group(2),
        )
        for ordinal, match in enumerate(pattern.finditer(text), 1)
    )


def surface_concept(uid, stable_key: str, source_label: str, target_label: str):
    return {
        "id": uid(stable_key),
        "stable_key": stable_key,
        "entity_type": "concept",
        "labels": [
            {"language": "zh-Hans", "text": source_label},
            {"language": "id-ID", "text": target_label},
        ],
    }


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
        raise SystemExit("Unit 018 backend refused: pdfinfo failed\n" + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 018 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate_structured_evidence() -> tuple[int, tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
        renders = json.loads((ROOT / RENDER_INVENTORY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unit 018 backend refused: unreadable structured evidence: {exc}") from exc
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U018":
        raise SystemExit("Unit 018 backend refused: structured QA status/unit drift")
    if evidence.get("authority") != {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_file": "chapter2.tex",
        "source_lines": "1603-1645",
        "source_span_bytes": SOURCE_SPAN[0],
        "source_span_sha256": SOURCE_SPAN[1],
    }:
        raise SystemExit("Unit 018 backend refused: structured authority drift")
    if evidence.get("target") != {
        "target_span_bytes": TARGET_SPAN[0],
        "target_span_sha256": TARGET_SPAN[1],
        "han_residue": 0,
    }:
        raise SystemExit("Unit 018 backend refused: structured target drift")
    if evidence.get("artifact") != {
        "path": ARTIFACT,
        "bytes": ARTIFACT_ID[0],
        "sha256": ARTIFACT_ID[1],
    }:
        raise SystemExit("Unit 018 backend refused: structured artifact drift")
    require_identity(ARTIFACT, ARTIFACT_ID)
    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        raise SystemExit("Unit 018 backend refused: structured build-log drift")
    if evidence.get("provenance_model") != MODEL:
        raise SystemExit("Unit 018 backend refused: model provenance drift")
    if evidence.get("rights") != {
        "principal_text_and_translation": "CC BY 4.0",
        "AJbook_class_fragment": "CC BY-SA 3.0",
        "bundled_noto_fonts": "SIL OFL 1.1",
        "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
    }:
        raise SystemExit("Unit 018 backend refused: component rights drift")
    page_count = int(evidence.get("pdf", {}).get("pages", 0))
    visual = evidence.get("visual_qa", {})
    if (
        page_count != 4
        or visual.get("status") != "PASS"
        or visual.get("pages_inspected") != [1, 2, 3, 4]
        or visual.get("renderers_inspected") != ["Poppler", "MuPDF"]
    ):
        raise SystemExit("Unit 018 backend refused: all-page visual evidence drift")
    for key in (
        "overfull_boxes",
        "undefined_control_sequences",
        "undefined_references",
        "undefined_citations",
        "missing_characters",
        "fatal_errors",
        "emergency_stops",
    ):
        if evidence.get("log_counts", {}).get(key) != 0:
            raise SystemExit(f"Unit 018 backend refused: nonzero build blocker {key}")
    if (
        renders.get("unit_id") != "O013-LI-U018"
        or renders.get("page_count") != page_count
        or renders.get("same_renderer_page_mismatches") != {"poppler": 0, "mupdf": 0}
        or renders.get("extracted_text_sha256_a") != renders.get("extracted_text_sha256_b")
        or renders.get("build_b", {}).get("sha256") != ARTIFACT_ID[1]
        or renders.get("provenance_model") != MODEL
    ):
        raise SystemExit("Unit 018 backend refused: deterministic render evidence drift")
    for renderer in ("poppler", "mupdf"):
        pages = renders.get("renderers", {}).get(renderer, [])
        if [item.get("page") for item in pages] != [1, 2, 3, 4] or any(
            not item.get("matches_clean_build_a")
            or not item.get("matches_clean_build_b")
            or not item.get("visually_inspected")
            for item in pages
        ):
            raise SystemExit(f"Unit 018 backend refused: {renderer} page evidence drift")
    return page_count, log_id


def gate() -> tuple[int, tuple[int, str]]:
    base.SPAN_START = START
    base.SPAN_END = END
    required = (
        SUMMARY,
        RENDER_INVENTORY,
        STRUCTURE_QA,
        REVIEW,
        MATH_REVIEW,
        TERMINOLOGY,
        TERMINOLOGY_QA,
        FINAL_LOG,
        ARTIFACT,
    )
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("Unit 018 backend refused: missing " + ", ".join(missing))
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(TARGET, TARGET_FULL)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 018 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 018 backend refused: target span drift")

    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 018 backend refused: structure gate failed\n" + check.stdout + check.stderr)
    checker_needles = (
        "PASS Unit 018 structural checker",
        "source lines=43 bytes=5197 sha256=" + SOURCE_SPAN[1],
        "target lines=43 bytes=6523 sha256=" + TARGET_SPAN[1],
        "top_level_exercises=13 nested_items=5 items=18 hints=1 refs=3 labels=0 eqrefs=0 cites=0 indexes=0",
        "inline_math=80 bracket_displays=2 align*=1 tikzcd=1 arrows=10 braces=124/124",
        "correction=O013-LI-U018-COR-002-explicit-U-domain",
    )
    if any(needle not in check.stdout for needle in checker_needles):
        raise SystemExit("Unit 018 backend refused: structure-check report drift")

    source = span(SOURCE).decode("utf-8")
    target = span(TARGET).decode("utf-8")
    source_items = tuple(absolute_line(source, match.start()) for match in re.finditer(r"\\item\b", source))
    target_items = tuple(absolute_line(target, match.start()) for match in re.finditer(r"\\item\b", target))
    expected_items = tuple(sorted((*TOP_LEVEL_ITEM_LINES, *NESTED_ITEM_LINES)))
    if source_items != expected_items or target_items != expected_items:
        raise SystemExit("Unit 018 backend refused: exercise/subpart topology drift")
    source_hints = tuple(absolute_line(source, match.start()) for match in re.finditer(r"\\hint\{", source))
    target_hints = tuple(absolute_line(target, match.start()) for match in re.finditer(r"\\hint\{", target))
    if source_hints != HINT_LINES or target_hints != HINT_LINES:
        raise SystemExit("Unit 018 backend refused: hint topology drift")
    if ordinary_reference_occurrences(source) != REFERENCES or ordinary_reference_occurrences(target) != REFERENCES:
        raise SystemExit("Unit 018 backend refused: reference topology drift")
    for forbidden in (r"\\label\{", r"\\eqref\{", r"\\cite", r"\\index"):
        if re.search(forbidden, source) or re.search(forbidden, target):
            raise SystemExit(f"Unit 018 backend refused: unexpected protected surface {forbidden}")

    source_inline = inline_formula_occurrences(source)
    target_inline = inline_formula_occurrences(target)
    if len(source_inline) != 80 or len(target_inline) != 80:
        raise SystemExit("Unit 018 backend refused: inline-formula count drift")
    pair_inline_formula_occurrences(source_inline, target_inline)
    source_brackets = bracket_formula_occurrences(source)
    target_brackets = bracket_formula_occurrences(target)
    if len(source_brackets) != 2 or len(target_brackets) != 2:
        raise SystemExit("Unit 018 backend refused: bracket-display count drift")
    if tuple(item[:3] for item in source_brackets) != tuple(item[:3] for item in target_brackets):
        raise SystemExit("Unit 018 backend refused: bracket-display location drift")
    source_env = environment_formula_occurrences(source)
    target_env = environment_formula_occurrences(target)
    if len(source_env) != 1 or len(target_env) != 1 or tuple(item[:4] for item in source_env) != tuple(item[:4] for item in target_env):
        raise SystemExit("Unit 018 backend refused: display-environment topology drift")
    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if source_diagrams != (("tikzcd", 1, 1633, 1636),) or target_diagrams != source_diagrams:
        raise SystemExit("Unit 018 backend refused: diagram topology drift")

    source_lines = source.splitlines()
    target_lines = target.splitlines()
    if "设域 $\\Bbbk$ 为域" not in source_lines[1640 - START] or "Misalkan $\\Bbbk$ medan." not in target_lines[1640 - START]:
        raise SystemExit("Unit 018 backend refused: correction COR-001 drift")
    if "U: \\cate{Set}_\\bullet \\to \\cate{Set}" not in target_lines[1644 - START]:
        raise SystemExit("Unit 018 backend refused: correction COR-002 drift")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", target):
        raise SystemExit("Unit 018 backend refused: Han residue")

    actual_aux = tuple(
        line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    if actual_aux != EXPECTED_AUX:
        raise SystemExit("Unit 018 backend refused: external-reference map drift")
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\setcounter{chapter}{2}",
        r"\setstretch{1.2}",
        r"\InputSourceLineRange{chapter2.tex}{1603}{1645}",
        MODEL,
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 018 backend refused: driver lacks {needle!r}")

    page_count, log_id = gate_structured_evidence()
    if pdfinfo_page_count() != page_count:
        raise SystemExit("Unit 018 backend refused: live PDF page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    for needle in (
        "PASS Unit 018 final build and replay",
        f"artifact bytes={ARTIFACT_ID[0]} sha256={ARTIFACT_ID[1]} pages={page_count}",
        "same-renderer replay: Poppler all pages identical; MuPDF all pages identical",
        "visual QA: all pages inspected in Poppler and MuPDF",
        "provenance model: " + MODEL,
    ):
        if needle not in summary:
            raise SystemExit("Unit 018 backend refused: build summary is incomplete")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    math_review = (ROOT / MATH_REVIEW).read_text(encoding="utf-8")
    for text, needles, name in (
        (
            review,
            ("Status: **PASS**", "chapter2.tex:1603-1645", TARGET_SPAN[1], MODEL, "Wen-Wei Li", "CC BY 4.0", *(item[0] for item in CORRECTIONS)),
            REVIEW,
        ),
        (
            math_review,
            (
                "Status: **PASS**",
                "| Top-level exercises | 13 | 13 | preserved |",
                "| Nested exercise items | 5 | 5 | preserved |",
                "| Hints | 1 | 1 | preserved at line 1632 / record 30 |",
                *(item[0] for item in CORRECTIONS),
            ),
            MATH_REVIEW,
        ),
    ):
        if any(needle not in text for needle in needles):
            raise SystemExit(f"Unit 018 backend refused: review incomplete: {name}")
    glossary = (ROOT / TERMINOLOGY).read_text(encoding="utf-8")
    for source_term, target_term in (
        ("category union (star construction)", "gabungan kategori"),
        ("quotient category", "kategori hasil bagi"),
        ("full subcategory", "subkategori penuh"),
        ("pointed set", "himpunan bertitik dasar"),
        ("pointed topological space", "ruang topologis bertitik dasar"),
        ("unital ring", "gelanggang dengan unsur satuan"),
        ("nonunital ring", "gelanggang tanpa syarat unsur satuan"),
        ("finitely generated abelian group", "grup abelian yang dibangkitkan secara berhingga"),
    ):
        if f'"{source_term}","{target_term}","admitted"' not in glossary:
            raise SystemExit(f"Unit 018 backend refused: controlled term missing: {source_term}")
    return page_count, log_id


def main() -> None:
    page_count, log_id = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    bind = base.binding
    unit_key = "unit/bab-2-latihan"
    unit_id = uid(unit_key)

    core_specs = (
        ("concept/isomorphism", "同构", "isomorfisme", (1,)),
        ("concept/category-join", "范畴的并", "gabungan kategori", (2,)),
        ("concept/full-subcategory", "全子范畴", "subkategori penuh", (2, 11)),
        ("concept/finite-ordinal-category", "有限序数范畴", "kategori ordinal berhingga", (2,)),
        ("concept/grothendieck-universe", "Grothendieck 宇宙", "semesta Grothendieck", (3,)),
        ("concept/category-skeleton", "范畴的骨架", "kerangka kategori", (3,)),
        ("concept/quotient-category", "商范畴", "kategori hasil bagi", (4,)),
        ("concept/universal-property", "泛性质", "sifat universal", (4,)),
        ("concept/category-equivalence", "范畴等价", "ekuivalensi kategori", (5,)),
        ("concept/quasi-inverse-functor", "逆拟函子", "fungtor kuasi-invers", (5,)),
        ("concept/adjunction", "伴随对", "pasangan adjoin", (6, 8, 9, 13)),
        ("concept/adjunction-unit", "伴随的单位", "unit adjoin", (8, 9)),
        ("concept/adjunction-counit", "伴随的余单位", "kounit adjoin", (6, 8, 9)),
        ("concept/unital-ring", "含幺环", "gelanggang dengan unsur satuan", (7,)),
        ("concept/nonunital-ring", "非含幺环", "gelanggang tanpa syarat unsur satuan", (7,)),
        ("concept/fully-faithful-functor", "全忠实函子", "fungtor penuh dan setia", (8,)),
        ("concept/yoneda-lemma", "米田引理", "Lema Yoneda", (8,)),
        ("concept/complete-category", "完备范畴", "kategori lengkap", (9, 12)),
        ("concept/cocomplete-category", "余完备范畴", "kategori kolengkap", (9, 12)),
        ("concept/diagonal-functor", "对角函子", "fungtor diagonal", (9,)),
        ("concept/inductive-limit", "归纳极限", "limit induktif", (9, 10)),
        ("concept/projective-limit", "投射极限", "limit proyektif", (9,)),
        ("concept/finite-dimensional-vector-space", "有限维向量空间", "ruang vektor berdimensi hingga", (10,)),
        ("concept/finitely-generated-abelian-group", "有限生成交换群", "grup abelian yang dibangkitkan secara berhingga", (10,)),
        ("concept/functor-category", "函子范畴", "kategori fungtor", (11,)),
        ("concept/horizontal-composition", "横合成", "komposisi horizontal", (11,)),
        ("concept/product", "积", "produk", (12,)),
        ("concept/coproduct", "余积", "koproduk", (12,)),
        ("concept/pointed-set", "带基点的集合", "himpunan bertitik dasar", (12, 13)),
        ("concept/pointed-topological-space", "带基点的拓扑空间", "ruang topologis bertitik dasar", (12,)),
        ("concept/forgetful-functor", "忘却函子", "fungtor pelupa", (13,)),
        ("concept/left-adjoint", "左伴随", "adjoin kiri", (7, 9, 13)),
        ("concept/right-adjoint", "右伴随", "adjoin kanan", (9, 13)),
    )
    concepts = [surface_concept(uid, key, source_label, target_label) for key, source_label, target_label, _ in core_specs]
    concept_exercises: dict[str, set[int]] = {
        key: set(exercises) for key, _, _, exercises in core_specs
    }

    compatibility_specs = (
        (f"{unit_key}/exercise/04/subpart/i", "练习 4(i)", "Latihan 4(i)", 1619, 4),
        (f"{unit_key}/exercise/04/subpart/ii", "练习 4(ii)", "Latihan 4(ii)", 1620, 4),
        (f"{unit_key}/exercise/04/subpart/iii", "练习 4(iii)", "Latihan 4(iii)", 1621, 4),
        (f"{unit_key}/exercise/08/subpart/i", "练习 8(i)", "Latihan 8(i)", 1629, 8),
        (f"{unit_key}/exercise/08/subpart/ii", "练习 8(ii)", "Latihan 8(ii)", 1630, 8),
        (f"{unit_key}/exercise/08/hint/01", "练习 8 的提示", "Petunjuk Latihan 8", 1632, 8),
    )
    concept_lines: dict[str, int] = {}
    for key, source_label, target_label, line, exercise in compatibility_specs:
        concepts.append(surface_concept(uid, key, source_label, target_label))
        concept_lines[key] = line
        concept_exercises[key] = {exercise}

    source_text = span(SOURCE).decode("utf-8")
    target_text = span(TARGET).decode("utf-8")
    for ordinal, (source_item, target_item) in enumerate(
        zip(ordinary_reference_occurrences(source_text), ordinary_reference_occurrences(target_text), strict=True),
        1,
    ):
        label, source_line = source_item
        _, target_line = target_item
        key = f"surface/unit-018/reference/ordinary/{ordinal:03d}"
        concepts.append(
            surface_concept(
                uid,
                key,
                f"普通引用 {ordinal:03d}: {label}; 源行 {source_line}",
                f"rujukan biasa {ordinal:03d}: {label}; baris target {target_line}",
            )
        )
        concept_lines[key] = source_line

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    for source_item, target_item in pair_inline_formula_occurrences(source_inline, target_inline):
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        key = f"surface/unit-018/formula/inline/{ordinal:03d}"
        concepts.append(
            surface_concept(
                uid,
                key,
                f"行内公式 {ordinal:03d}; 源行 {source_line}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus sebaris {ordinal:03d}; baris target {target_line}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )
        concept_lines[key] = source_line

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        key = f"surface/unit-018/formula/display-bracket/{ordinal:03d}"
        concepts.append(
            surface_concept(
                uid,
                key,
                f"陈列公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus pajang {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )
        concept_lines[key] = source_first

    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_env, target_env, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        key = f"surface/unit-018/formula/display-environment/{ordinal:03d}"
        concepts.append(
            surface_concept(
                uid,
                key,
                f"{environment} 公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus {environment} {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )
        concept_lines[key] = source_first

    for correction_id, line, issue in CORRECTIONS:
        key = f"correction/{correction_id.casefold()}"
        concepts.append(
            surface_concept(
                uid,
                key,
                f"声明的源文本更正 {correction_id}; 源行 {line}",
                f"koreksi sumber terdeklarasi {correction_id}; ledger {ADVERSE_BY_CORRECTION[correction_id]}; baris {line}: {issue}",
            )
        )
        concept_lines[key] = line

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        raise SystemExit("Unit 018 backend refused: duplicate concept stable key")
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    principal = rights_by_key["rights/principal-cc-by-4.0"]
    unit_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_by_key["rights/noto-fonts-ofl-1.1"],
    ]
    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    prerequisite_keys = (
        "prerequisite/elementary-set-theory",
        "prerequisite/vector-spaces",
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
        "prerequisite/universal-properties-and-comma-categories",
        "prerequisite/representable-functors-and-yoneda",
        "prerequisite/limits-and-colimits",
    )
    prerequisite_ids = [prerequisite_by_key[key] for key in prerequisite_keys]

    sections = []
    for ordinal, first, last, source_title, target_title in EXERCISE_SPECS:
        section_key = f"{unit_key}/exercise/{ordinal:02d}"
        local_keys = [
            key
            for key, exercises in concept_exercises.items()
            if ordinal in exercises
        ]
        local_keys.extend(
            key for key, line in concept_lines.items() if first <= line <= last
        )
        local_keys = list(dict.fromkeys(local_keys))
        sections.append(
            {
                "id": uid(section_key),
                "stable_key": section_key,
                "entity_type": "section",
                "parent_id": unit_id,
                "order": ordinal,
                "source_local_id": f"chapter2.tex:{first}-{last}",
                "titles": [
                    {"language": "zh-Hans", "text": f"练习 {ordinal}：{source_title}"},
                    {"language": "id-ID", "text": f"Latihan {ordinal}: {target_title}"},
                ],
                "source_binding": bind(SOURCE, first, last),
                "target_binding": bind(TARGET, first, last),
                "concept_ids": [concept_by_key[key] for key in local_keys],
                "prerequisite_ids": prerequisite_ids,
                "rights_component_ids": [principal],
                "translation_state": "visually_checked",
                "admission_state": "admitted",
            }
        )
    section_by_line = {
        line: section["id"]
        for section, (_, first, last, _, _) in zip(sections, EXERCISE_SPECS, strict=True)
        for line in range(first, last + 1)
    }
    diagrams = []
    for ordinal, source_diagram in enumerate(base.diagram_occurrences(source_text), 1):
        source_format, source_occurrence, source_first, source_last = source_diagram
        key = f"diagram/unit-018/{source_format}-{source_occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_by_line[source_first],
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": source_occurrence,
                "source_binding": bind(SOURCE, source_first, source_last),
                "target_binding": bind(TARGET, source_first, source_last),
                "rights_component_id": principal,
                "state": "audited_preserved",
            }
        )

    inputs = (
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
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    )
    build = {
        "id": uid("build-surface/unit-018-pdf"),
        "stable_key": "build-surface/unit-018-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_018.ps1 -OutputDirectory build/unit-018-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": bind(ARTIFACT),
        "log_binding": bind(FINAL_LOG),
        "build_script": bind(BUILD_SCRIPT),
        "page_count": page_count,
        "status": "pass",
        "driver": bind(DRIVER),
        "input_bindings": [bind(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 018 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_admission = {
        "id": uid("qa/unit-018/admission-gate"),
        "stable_key": "qa/unit-018/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order Chapter 2 exercise translation, math review, build, and all-page visual admission for chapter2.tex lines 1603-1645. "
            "The compatibility topology binds 13 top-level exercises as ordered sections, five nested items and one hint as stable concept entities, three ordinary references, 80 inline and three display-formula entities, one preserved TikZ-CD diagram with ten arrows, zero labels/citations/index entries/answers/solutions, and two disclosed repairs O013-LI-U018-COR-001 and O013-LI-U018-COR-002. "
            "The repair records map respectively to durable adverse-ledger entries O013-ADV-0049 and O013-ADV-0050. "
            "The reader has component-level rights: principal text/translation CC BY 4.0, AJbook fragment CC BY-SA 3.0, and bundled fonts OFL 1.1; Lanzhou.png remains a separately licensed closure asset and is not used. "
            f"Production provenance is {MODEL}, separate from Wen-Wei Li's authorship and all human credits."
        ),
        "witness": STRUCTURE_QA,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(STRUCTURE_QA),
    }
    qa_review = {
        "id": uid("qa/unit-018/source-and-math-review"),
        "stable_key": "qa/unit-018/source-and-math-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent source/translation and mathematical-topology reviews bind all 13 exercises, five subparts, one hint, references, formulas, diagram, terminology, and disclosed corrections.",
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(REVIEW),
    }
    qa_terms = {
        "id": uid("qa/unit-018/terminology-control"),
        "stable_key": "qa/unit-018/terminology-control",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live controlled id-ID glossary binding, including the eight dedicated Unit 018 terminology rows and the bounded Indonesian field-usage QA record.",
        "witness": TERMINOLOGY,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(TERMINOLOGY),
    }

    formula_total = len(source_inline) + len(source_brackets) + len(source_env)
    data["dataset_stable_key"] = "dataset/unit-018/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-24",
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
        "order": 18,
        "source_local_id": "chapter2.tex:1603-1645",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：习题"},
            {"language": "id-ID", "text": "Bab 2: Latihan"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": bind(SOURCE, START, END),
        "target_binding": bind(TARGET, START, END),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [qa_admission["id"], qa_review["id"], qa_terms["id"]],
        "outcome_keys": [
            "outcome/solve-category-isomorphism-and-equivalence-exercises",
            "outcome/construct-category-joins-skeletons-and-quotients",
            "outcome/analyze-adjunction-units-counits-and-full-faithfulness",
            "outcome/construct-adjoints-for-ring-and-pointed-set-forgetful-functors",
            "outcome/relate-diagonal-functors-to-limits-and-colimits",
            "outcome/express-vector-spaces-and-abelian-groups-as-inductive-limits",
            "outcome/prove-completeness-of-pointed-set-and-topological-categories",
        ],
        # Compatibility values required by the shared validator.  The true
        # 13/5/1 exercise/subpart/hint topology is encoded by stable entities,
        # asserted by both generators, and disclosed in the QA events.
        "surface_counts": {
            "sections": 13,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 1,
            "index_entries": 0,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = []
    data["diagrams"] = diagrams
    data["index_entries"] = []
    data["build_surfaces"] = [build]
    data["qa_events"] = [qa_admission, qa_review, qa_terms]

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
        raise SystemExit("Unit 018 backend refused: missing CSV projection")
    print(
        json.dumps(
            {
                "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest(OUTPUT.read_bytes()),
                "entities": 5
                + len(sections)
                + len(concepts)
                + len(data["prerequisites"])
                + len(data["rights"])
                + len(diagrams)
                + len(data["build_surfaces"])
                + len(data["qa_events"]),
                "exercises": 13,
                "subparts": 5,
                "hints": 1,
                "concepts": len(concepts),
                "formula_entities": formula_total,
                "ordinary_reference_entities": len(REFERENCES),
                "correction_entities": len(CORRECTIONS),
                "diagrams": len(diagrams),
                "artifact": {"pages": page_count, "bytes": ARTIFACT_ID[0], "sha256": ARTIFACT_ID[1]},
                "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
                "terminology": {"bytes": identity(TERMINOLOGY)[0], "sha256": identity(TERMINOLOGY)[1]},
                "csv_projections": [str(path.relative_to(ROOT)).replace("\\", "/") for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
