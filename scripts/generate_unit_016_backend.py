#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 016.

Schema v1.1.0 has native citation, diagram, index-entry, build, and QA records,
but no first-class TeX-label, reference-occurrence, formula, or correction
record.  Those protected surfaces are therefore represented by deterministic
concept-compatible UUIDv5 entities whose stable keys explicitly identify the
compatibility surface.  The generator binds every native surface to exact
source/target lines and verifies the complete compatibility topology before it
writes the canonical JSON and six CSV projections.
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
TEMPLATE = ROOT / "backend/data/unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin.json"
OUTPUT = ROOT / "backend/data/unit-016-bab-2-limit.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-016-bab-2-limit.tex"
COVER = "repo/source/coverpage-id-unit-016.tex"
CROSSREF = "repo/source/unit-016-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_016.ps1"
STRUCTURE_GATE = "scripts/check_unit_016_structure.py"
SUMMARY = "qa/unit-016-evidence/build-log-summary.txt"
REVIEW = "qa/UNIT_016_TRANSLATION_SOURCE_REVIEW_20260824.md"
FINAL_LOG = "qa/UNIT_016_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-016-bab-2-limit.pdf"
STRUCTURE_QA = "qa/unit-016-evidence/structure-and-pdf-qa.json"
FINAL_AUX = "build/unit-016-final-c/unit-016-bab-2-limit.aux"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 1111, 1405
SOURCE_FULL = (
    139_983,
    "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840",
)
TARGET_FULL = (
    162_316,
    "644f98e065dae5761ae6cd41a334704ca890837537e4eb0d90fb2ed794536a0b",
)
SOURCE_SPAN = (
    24_790,
    "48abd6c33ecdc32591a05ecfbdc7381637027963a61cb3015016909a8faacf82",
)
TARGET_SPAN = (
    28_854,
    "fe5e54d56824e8f1a76f93e1732220813c654ab16eb2d7c8daa8dcdde17f5c81",
)

LABELS = (
    "sec:limits",
    "def:diagonal-functor",
    "def:limit",
    "eqn:lim-diagrams",
    "rem:lim-duality",
    "prop:lim-functoriality",
    "eg:set-limits",
    "def:filtrant-cat",
    "eqn:filtrant-equiv",
    "eg:top-limits",
    "prop:lim-Yoneda",
    "prop:lim-as-fct",
    "prop:lim-Fubini",
    "eqn:equalizer",
    "eqn:coequalizer",
    "prop:product-associativity",
    "prop:product-commutativity",
)
REFERENCES = (
    "def:comma-category",
    "prop:initial-obj-uniqueness",
    "rem:op-functor",
    "con:U-small",
    "hyp:universe",
    "prop:preorder-complete",
    "sec:group-limit",
    "eg:set-limits",
    "eg:set-limits",
    "eg:set-limits",
    "def:filtrant-cat",
    "sec:representable-functors",
    "prop:lim-functoriality",
    "prop:lim-functoriality",
    "sec:representable-functors",
    "prop:Yoneda-lemma",
    "prop:lim-as-fct",
    "prop:lim-functoriality",
    "prop:lim-as-fct",
    "eg:set-limits",
    "prop:lim-Fubini",
)
EQUATION_REFERENCES = (
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:equalizer",
)
CITATIONS = ((r"\S 3.1, \S 3.4", "Xiong", 1263),)
INDEX_SLUGS = (
    "inductive-limit",
    "projective-limit",
    "inductive-limit-symbol",
    "projective-limit-symbol",
    "filtered-category",
    "coproduct",
    "product",
    "coequalizer",
    "equalizer",
    "kernel-symbol",
    "cokernel-symbol",
    "associativity-constraint",
    "commutativity-constraint",
)
INDEX_TOPOLOGY = (
    ("main", 1131),
    ("main", 1131),
    ("sym1", 1131),
    ("sym1", 1131),
    ("main", 1232),
    ("main", 1347),
    ("main", 1347),
    ("main", 1365),
    ("main", 1365),
    ("sym1", 1365),
    ("sym1", 1365),
    ("main", 1381),
    ("main", 1390),
)
CORRECTIONS = (
    (
        "O013-LI-U016-COR-001",
        1177,
        "The authority duplicates p_i before an arrow already labelled p_i; the target removes the duplicate.",
    ),
    (
        "O013-LI-U016-COR-002",
        1343,
        "The proof constructs the right iterated limit first while the authority prose says left; the target repairs only the prose order.",
    ),
    (
        "O013-LI-U016-COR-003",
        1348,
        "The authority leaves the product and coproduct index i free; the target supplies explicit i-in-I binders.",
    ),
)
EXPECTED_AUX = (
    r"\newlabel{def:comma-category}{{2.4.{7}}{3}}",
    r"\newlabel{prop:initial-obj-uniqueness}{{2.4.{2}}{1}}",
    r"\newlabel{rem:op-functor}{{2.2.{2}}{1}}",
    r"\newlabel{con:U-small}{{2.1.{4}}{3}}",
    r"\newlabel{hyp:universe}{{1.5.{2}}{24}}",
    r"\newlabel{prop:preorder-complete}{{2.8.{2}}{66}}",
    r"\newlabel{sec:group-limit}{{4.10}{0}}",
    r"\newlabel{sec:representable-functors}{{2.5}{1}}",
    r"\newlabel{prop:Yoneda-lemma}{{2.5.{1}}{1}}",
)
EXPECTED_EQUATION_NUMBERING = {
    "eqn:lim-diagrams": "2.10",
    "eqn:filtrant-equiv": "2.11",
    "eqn:equalizer": "2.12",
    "eqn:coequalizer": "2.13",
    "status": (
        "matches source-order Chapter 2 identifiers after setting the standalone "
        "equation counter to 9"
    ),
}
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-016-{name}.csv"
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
        raise SystemExit(f"Unit 016 backend refused: identity drift for {relative}")


def occurrences(text: str, pattern: str) -> tuple[tuple[str, int], ...]:
    compiled = re.compile(pattern)
    return tuple(
        (match.group(1), START + text.count("\n", 0, match.start()))
        for match in compiled.finditer(text)
    )


def label_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return occurrences(text, r"\\label\{([^{}]+)\}")


def ordinary_reference_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return occurrences(text, r"(?<!eq)\\ref\{([^{}]+)\}")


def equation_reference_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return occurrences(text, r"\\eqref\{([^{}]+)\}")


def citation_occurrences(text: str) -> tuple[tuple[str, str, int], ...]:
    pattern = re.compile(r"\\cite(?:\[([^]\r\n]*)\])?\{([^{}]+)\}")
    return tuple(
        (
            match.group(1) or "",
            match.group(2),
            START + text.count("\n", 0, match.start()),
        )
        for match in pattern.finditer(text)
    )


def is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def inline_formula_occurrences(text: str) -> tuple[tuple[int, int, str], ...]:
    delimiters = tuple(
        position
        for position, character in enumerate(text)
        if character == "$" and not is_escaped(text, position)
    )
    if len(delimiters) % 2:
        raise SystemExit("Unit 016 backend refused: unpaired inline-math delimiter")
    result: list[tuple[int, int, str]] = []
    for ordinal, offset in enumerate(range(0, len(delimiters), 2), 1):
        opening, closing = delimiters[offset : offset + 2]
        result.append(
            (
                ordinal,
                START + text.count("\n", 0, opening),
                text[opening + 1 : closing],
            )
        )
    return tuple(result)


def bracket_formula_occurrences(text: str) -> tuple[tuple[int, int, int, str], ...]:
    return tuple(
        (
            ordinal,
            START + text.count("\n", 0, match.start()),
            START + text.count("\n", 0, match.end() - 1),
            match.group(1),
        )
        for ordinal, match in enumerate(re.finditer(r"\\\[(.*?)\\\]", text, re.DOTALL), 1)
    )


def environment_formula_occurrences(
    text: str,
) -> tuple[tuple[int, str, int, int, str], ...]:
    pattern = re.compile(
        r"\\begin\{(equation\*?|align\*|gather\*)\}(.*?)\\end\{\1\}",
        re.DOTALL,
    )
    return tuple(
        (
            ordinal,
            match.group(1),
            START + text.count("\n", 0, match.start()),
            START + text.count("\n", 0, match.end() - 1),
            match.group(2),
        )
        for ordinal, match in enumerate(pattern.finditer(text), 1)
    )


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
            "Unit 016 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 016 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate_structure_qa() -> tuple[int, tuple[int, str], tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"Unit 016 backend refused: structured QA witness is unreadable: {exc}"
        ) from exc
    if evidence.get("status") != "PASS":
        raise SystemExit("Unit 016 backend refused: structured QA status is not PASS")
    authority = evidence.get("authority", {})
    if authority != {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_file": "chapter2.tex",
        "source_lines": "1111-1405",
        "source_span_bytes": SOURCE_SPAN[0],
        "source_span_sha256": SOURCE_SPAN[1],
    }:
        raise SystemExit("Unit 016 backend refused: structured authority evidence drift")
    target = evidence.get("target", {})
    if target != {
        "target_span_bytes": TARGET_SPAN[0],
        "target_span_sha256": TARGET_SPAN[1],
        "correction_ids": [item[0] for item in CORRECTIONS],
        "han_residue": 0,
    }:
        raise SystemExit("Unit 016 backend refused: structured target evidence drift")
    if evidence.get("provenance_model") != MODEL:
        raise SystemExit("Unit 016 backend refused: structured model provenance drift")
    if evidence.get("rights") != "CC BY 4.0":
        raise SystemExit("Unit 016 backend refused: structured principal-rights drift")
    artifact = evidence.get("artifact", {})
    try:
        page_count = int(evidence["pdf"]["pages"])
        artifact_id = (int(artifact["bytes"]), str(artifact["sha256"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit("Unit 016 backend refused: malformed structured artifact identity") from exc
    if artifact.get("path") != ARTIFACT or page_count < 1:
        raise SystemExit("Unit 016 backend refused: structured artifact path/page drift")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_id[1]):
        raise SystemExit("Unit 016 backend refused: malformed structured artifact hash")
    require_identity(ARTIFACT, artifact_id)
    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        raise SystemExit("Unit 016 backend refused: structured build-log evidence drift")
    replay = evidence.get("deterministic_replay", {})
    if (
        replay.get("poppler_page_mismatches") != 0
        or replay.get("mupdf_page_mismatches") != 0
        or replay.get("pdftotext_layout_sha256_b")
        != replay.get("pdftotext_layout_sha256_c")
    ):
        raise SystemExit("Unit 016 backend refused: deterministic replay evidence drift")
    visual = evidence.get("visual_qa", {})
    if (
        visual.get("status") != "PASS"
        or visual.get("pages_inspected") != list(range(1, page_count + 1))
        or visual.get("renderers_inspected") != ["Poppler", "MuPDF"]
    ):
        raise SystemExit("Unit 016 backend refused: all-page visual evidence drift")
    blockers = evidence.get("log_counts", {})
    for key in (
        "overfull_boxes",
        "undefined_control_sequences",
        "undefined_references",
        "undefined_citations",
        "missing_characters",
        "fatal_errors",
        "emergency_stops",
    ):
        if blockers.get(key) != 0:
            raise SystemExit(f"Unit 016 backend refused: nonzero build blocker {key}")
    return page_count, artifact_id, log_id


def gate() -> tuple[int, tuple[int, str], tuple[int, str]]:
    base.SPAN_START = START
    base.SPAN_END = END
    missing = [
        path
        for path in (SUMMARY, REVIEW, STRUCTURE_QA, FINAL_LOG, ARTIFACT, FINAL_AUX)
        if not (ROOT / path).is_file()
    ]
    if missing:
        raise SystemExit(
            "Unit 016 backend scaffold is complete but final evidence is not yet present: "
            + ", ".join(missing)
        )
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(TARGET, TARGET_FULL)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 016 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 016 backend refused: target span drift")

    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 016 backend refused: structure gate failed\n" + check.stderr)
    checker_needles = (
        "PASS Unit 016 structural checker",
        "source lines=295 bytes=24790 sha256=" + SOURCE_SPAN[1],
        "target lines=295 bytes=28854 sha256=" + TARGET_SPAN[1],
        "inline_math=287/287 bracket_displays=12/12",
        "labels=17 refs=21 eqrefs=7 cite=1 indexes=13 items=9",
        "tikzcd=23 arrows=98 han=0",
        "corrections=O013-LI-U016-COR-001,002,003 official_errata=preserved",
    )
    if any(needle not in check.stdout for needle in checker_needles):
        raise SystemExit("Unit 016 backend refused: structure-gate report drift")

    source = span(SOURCE).decode("utf-8")
    target = span(TARGET).decode("utf-8")
    source_labels = label_occurrences(source)
    target_labels = label_occurrences(target)
    source_refs = ordinary_reference_occurrences(source)
    target_refs = ordinary_reference_occurrences(target)
    source_eqrefs = equation_reference_occurrences(source)
    target_eqrefs = equation_reference_occurrences(target)
    expected_labels = tuple((label, line) for label, line in source_labels)
    if tuple(label for label, _ in expected_labels) != LABELS or source_labels != target_labels:
        raise SystemExit("Unit 016 backend refused: label topology drift")
    if tuple(label for label, _ in source_refs) != REFERENCES or source_refs != target_refs:
        raise SystemExit("Unit 016 backend refused: ordinary-reference topology drift")
    if (
        tuple(label for label, _ in source_eqrefs) != EQUATION_REFERENCES
        or source_eqrefs != target_eqrefs
    ):
        raise SystemExit("Unit 016 backend refused: equation-reference topology drift")
    if citation_occurrences(source) != CITATIONS or citation_occurrences(target) != CITATIONS:
        raise SystemExit("Unit 016 backend refused: citation topology drift")

    source_indexes = base.index_occurrences(source)
    target_indexes = base.index_occurrences(target)
    if tuple((item[0], item[2]) for item in source_indexes) != INDEX_TOPOLOGY:
        raise SystemExit("Unit 016 backend refused: source index topology drift")
    if tuple((item[0], item[2]) for item in target_indexes) != INDEX_TOPOLOGY:
        raise SystemExit("Unit 016 backend refused: target index topology drift")
    if tuple((item[0], item[1].split("@", 1)[0]) for item in source_indexes) != tuple(
        (item[0], item[1].split("@", 1)[0]) for item in target_indexes
    ):
        raise SystemExit("Unit 016 backend refused: index namespace/sort-key drift")

    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if source_diagrams != target_diagrams or len(source_diagrams) != 23:
        raise SystemExit("Unit 016 backend refused: diagram occurrence topology drift")

    source_inline = inline_formula_occurrences(source)
    target_inline = inline_formula_occurrences(target)
    if len(source_inline) != 287 or len(target_inline) != 287:
        raise SystemExit("Unit 016 backend refused: inline-formula count drift")
    if tuple(item[:2] for item in source_inline) != tuple(item[:2] for item in target_inline):
        raise SystemExit("Unit 016 backend refused: inline-formula location drift")
    inline_mismatches = tuple(
        (source_item[1], source_item[2], target_item[2])
        for source_item, target_item in zip(source_inline, target_inline, strict=True)
        if source_item[2] != target_item[2]
    )
    if tuple(item[0] for item in inline_mismatches) != (1177, 1348, 1348):
        raise SystemExit("Unit 016 backend refused: undeclared inline-formula drift")

    source_brackets = bracket_formula_occurrences(source)
    target_brackets = bracket_formula_occurrences(target)
    if len(source_brackets) != 12 or len(target_brackets) != 12:
        raise SystemExit("Unit 016 backend refused: bracket-display count drift")
    if tuple(item[:3] for item in source_brackets) != tuple(item[:3] for item in target_brackets):
        raise SystemExit("Unit 016 backend refused: bracket-display location drift")
    source_env_formulas = environment_formula_occurrences(source)
    target_env_formulas = environment_formula_occurrences(target)
    if len(source_env_formulas) != 14 or len(target_env_formulas) != 14:
        raise SystemExit("Unit 016 backend refused: environment-formula count drift")
    if tuple(item[:4] for item in source_env_formulas) != tuple(
        item[:4] for item in target_env_formulas
    ):
        raise SystemExit("Unit 016 backend refused: environment-formula location drift")

    actual_aux = tuple(
        line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    if actual_aux != EXPECTED_AUX:
        raise SystemExit("Unit 016 backend refused: external-reference map drift")
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\setcounter{chapter}{2}",
        r"\setcounter{section}{6}",
        r"\setcounter{theorem}{0}",
        r"\setcounter{equation}{9}",
        r"\setstretch{1.25}",
        r"\InputSourceLineRange{chapter2.tex}{1111}{1405}",
        r"\printindex[sym1]",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 016 backend refused: driver lacks {needle!r}")

    final_aux = (ROOT / FINAL_AUX).read_text(encoding="utf-8")
    equation_numbering = {
        label: number
        for label, number in re.findall(
            r"\\newlabel\{(eqn:(?:lim-diagrams|filtrant-equiv|equalizer|coequalizer))\}"
            r"\{\{([^{}]+)\}",
            final_aux,
        )
    }
    if equation_numbering != {
        key: value for key, value in EXPECTED_EQUATION_NUMBERING.items() if key != "status"
    }:
        raise SystemExit("Unit 016 backend refused: final-AUX equation numbering drift")

    page_count, artifact_id, log_id = gate_structure_qa()
    if pdfinfo_page_count() != page_count:
        raise SystemExit("Unit 016 backend refused: live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+) pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != page_count:
        raise SystemExit("Unit 016 backend refused: final build-log page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    summary_needles = (
        "PASS Unit 016 final build and replay",
        f"pages={page_count}",
        artifact_id[1],
        log_id[1],
        f"Poppler {page_count}/{page_count} identical",
        f"MuPDF {page_count}/{page_count} identical",
        f"visual QA: all {page_count} pages inspected",
        "provenance model: " + MODEL,
    )
    if any(needle not in summary for needle in summary_needles):
        raise SystemExit("Unit 016 backend refused: build summary is incomplete")
    review_needles = (
        "Status: translation/source integration reviewed",
        "chapter2.tex:1111-1405",
        TARGET_SPAN[1],
        MODEL,
        "Wen-Wei Li",
        "CC BY 4.0",
        "independent derivative",
        *(item[0] for item in CORRECTIONS),
    )
    if any(needle not in review for needle in review_needles):
        raise SystemExit("Unit 016 backend refused: translation/source review is incomplete")
    return page_count, artifact_id, log_id


def surface_concept(
    uid,
    stable_key: str,
    source_label: str,
    target_label: str,
) -> dict[str, object]:
    return {
        "id": uid(stable_key),
        "stable_key": stable_key,
        "entity_type": "concept",
        "labels": [
            {"language": "zh-Hans", "text": source_label},
            {"language": "id-ID", "text": target_label},
        ],
    }


def main() -> None:
    page_count, artifact_id, log_id = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    bind = base.binding
    unit_key = "unit/bab-2-limit"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/limit"
    section_id = uid(section_key)

    core_specs = (
        ("concept/diagonal-functor", "对角函子", "fungtor diagonal"),
        ("concept/indexed-limit", "指标极限", "limit berindeks"),
        ("concept/inductive-limit", "归纳极限", "limit induktif"),
        ("concept/projective-limit", "投射极限", "limit proyektif"),
        ("concept/direct-limit", "直极限", "limit langsung"),
        ("concept/inverse-limit", "逆极限", "limit invers"),
        ("concept/colimit", "余极限", "kolimit"),
        ("concept/cone", "锥", "kerucut"),
        ("concept/cocone", "余锥", "kokerucut"),
        ("concept/universal-property-of-limits", "极限的泛性质", "sifat universal limit"),
        ("concept/limit-duality", "极限对偶性", "dualitas limit"),
        ("concept/limit-functoriality", "极限函子性", "funktorialitas limit"),
        ("concept/small-category", "小范畴", "kategori kecil"),
        ("concept/set-valued-limit", "集合值极限", "limit bernilai himpunan"),
        ("concept/disjoint-union", "无交并", "gabungan saling lepas"),
        ("concept/filtered-category", "滤过范畴", "kategori terarah ke atas"),
        ("concept/filtered-colimit", "滤过余极限", "kolimit terarah ke atas"),
        ("concept/quotient-topology", "商拓扑", "topologi hasil bagi"),
        ("concept/subspace-topology", "子空间拓扑", "topologi subruang"),
        ("concept/pointwise-limit", "逐点极限", "limit titik demi titik"),
        ("concept/representability-of-limits", "极限的可表性", "representabilitas limit"),
        ("concept/fubini-limit", "Fubini 型极限", "limit tipe Fubini"),
        ("concept/finite-limit", "有限极限", "limit berhingga"),
        ("concept/product", "积", "produk"),
        ("concept/coproduct", "余积", "koproduk"),
        ("concept/initial-object", "始对象", "objek awal"),
        ("concept/terminal-object", "终对象", "objek terminal"),
        ("concept/equalizer", "等化子", "ekualiser"),
        ("concept/coequalizer", "余等化子", "koekualiser"),
        ("concept/associativity-constraint", "结合约束", "kendala asosiativitas"),
        ("concept/commutativity-constraint", "交换约束", "kendala komutativitas"),
        ("concept/equalizer-monomorphism", "等化子单态射", "monomorfisme ekualiser"),
        ("concept/coequalizer-epimorphism", "余等化子满态射", "epimorfisme koekualiser"),
    )
    concepts = [
        surface_concept(uid, key, source_label, target_label)
        for key, source_label, target_label in core_specs
    ]

    source_text = span(SOURCE).decode("utf-8")
    target_text = span(TARGET).decode("utf-8")
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(
        zip(source_labels, target_labels, strict=True), 1
    ):
        label, source_line = source_item
        _, target_line = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-016/label/{ordinal:03d}",
                f"TeX 标签 {ordinal:03d}: {label}; 源行 {source_line}",
                f"label TeX {ordinal:03d}: {label}; baris target {target_line}",
            )
        )

    for kind, source_items, target_items, source_name, target_name in (
        (
            "ordinary",
            ordinary_reference_occurrences(source_text),
            ordinary_reference_occurrences(target_text),
            "普通引用",
            "rujukan biasa",
        ),
        (
            "equation",
            equation_reference_occurrences(source_text),
            equation_reference_occurrences(target_text),
            "公式引用",
            "rujukan persamaan",
        ),
    ):
        for ordinal, (source_item, target_item) in enumerate(
            zip(source_items, target_items, strict=True), 1
        ):
            label, source_line = source_item
            _, target_line = target_item
            concepts.append(
                surface_concept(
                    uid,
                    f"surface/unit-016/reference/{kind}/{ordinal:03d}",
                    f"{source_name} {ordinal:03d}: {label}; 源行 {source_line}",
                    f"{target_name} {ordinal:03d}: {label}; baris target {target_line}",
                )
            )

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    for source_item, target_item in zip(source_inline, target_inline, strict=True):
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-016/formula/inline/{ordinal:03d}",
                f"行内公式 {ordinal:03d}; 源行 {source_line}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus sebaris {ordinal:03d}; baris target {target_line}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-016/formula/display-bracket/{ordinal:03d}",
                f"陈列公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus pajang {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )

    source_env_formulas = environment_formula_occurrences(source_text)
    target_env_formulas = environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_env_formulas, target_env_formulas, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-016/formula/display-environment/{ordinal:03d}",
                f"{environment} 公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus {environment} {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )

    for correction_id, line, issue in CORRECTIONS:
        slug = correction_id.casefold()
        concepts.append(
            surface_concept(
                uid,
                f"correction/{slug}",
                f"声明的源文本更正 {correction_id}; 源行 {line}",
                f"koreksi sumber terdeklarasi {correction_id}; baris {line}: {issue}",
            )
        )

    concept_ids = [item["id"] for item in concepts]
    prerequisites = data["prerequisites"]
    existing_prerequisite_keys = {item["stable_key"] for item in prerequisites}
    prerequisite_specs = (
        (
            "prerequisite/functors-and-natural-transformations",
            "函子与自然变换",
            "fungtor dan transformasi natural",
            199,
            467,
        ),
        (
            "prerequisite/functor-categories",
            "函子范畴",
            "kategori fungtor",
            468,
            563,
        ),
        (
            "prerequisite/universal-properties-and-comma-categories",
            "泛性质与逗号范畴",
            "sifat universal dan kategori koma",
            564,
            677,
        ),
        (
            "prerequisite/representable-functors-and-yoneda",
            "可表函子与 Yoneda 引理",
            "fungtor representabel dan Lema Yoneda",
            678,
            765,
        ),
    )
    for key, source_label, target_label, first, last in prerequisite_specs:
        if key in existing_prerequisite_keys:
            continue
        prerequisites.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "prerequisite",
                "labels": [
                    {"language": "zh-Hans", "text": source_label},
                    {"language": "id-ID", "text": target_label},
                ],
                "requiredness": "expected",
                "source_evidence": {"path": SOURCE, "line_start": first, "line_end": last},
            }
        )
    prerequisite_ids = [item["id"] for item in prerequisites]
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
        "source_local_id": "chapter2.tex:1111-1405",
        "titles": [
            {"language": "zh-Hans", "text": "2.7 极限"},
            {"language": "id-ID", "text": "2.7 Limit"},
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
        key = f"citation/unit-016/{bib_key.casefold()}"
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

    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (slug, source_index, target_index) in enumerate(
        zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1
    ):
        key = f"index-entry/unit-016/{slug}"
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

    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(
        zip(source_diagrams, target_diagrams, strict=True), 1
    ):
        source_format, source_occurrence, source_first, source_last = source_diagram
        target_format, target_occurrence, target_first, target_last = target_diagram
        if source_diagram != target_diagram:
            raise SystemExit("Unit 016 backend refused: diagram binding drift")
        key = f"diagram/unit-016/{source_format}-{source_occurrence:02d}"
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
        "id": uid("build-surface/unit-016-pdf"),
        "stable_key": "build-surface/unit-016-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": (
            "pwsh -NoProfile -File scripts/build_unit_016.ps1 "
            "-OutputDirectory build/unit-016-replay"
        ),
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
            "biber",
            "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 016 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    correction_ids = ", ".join(item[0] for item in CORRECTIONS)
    formula_total = len(source_inline) + len(source_brackets) + len(source_env_formulas)
    qa = {
        "id": uid("qa/unit-016/admission-gate"),
        "stable_key": "qa/unit-016/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and semantic review of chapter2.tex lines "
            "1111-1405; 295 physical lines, 66 balanced environments, 17 labels, 21 "
            "ordinary-reference occurrences, seven equation-reference occurrences, one "
            "Xiong citation, 13 index entries, 23 TikZ-CD diagrams with 98 arrows, 287 "
            f"inline plus 26 display formula surfaces ({formula_total} total), nine list "
            "items, and no exercises, hints, answers, or solutions. Mathematics is "
            f"preserved after three disclosed corrections ({correction_ids}); exact "
            "equation continuity is (2.10)-(2.13); the reader uses 1.25 digital reflow, "
            "resolved frozen external references, and separate CC BY 4.0 principal-text, "
            "CC BY-SA 3.0 class-fragment, and OFL 1.1 font rights. Translation provenance "
            f"is {MODEL}, recorded separately from Wen-Wei Li's authorship and human credit."
        ),
        "witness": STRUCTURE_QA,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(STRUCTURE_QA),
    }
    structured_qa = {
        "id": uid("qa/unit-016/structured-public-evidence"),
        "stable_key": "qa/unit-016/structured-public-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": (
            "Structured QA binds the admitted target, final reader and log identities, "
            "complete label/reference/formula/index/diagram topology, three declared "
            "corrections, 1.25 digital reflow, exact model provenance, and source-order "
            "Chapter 2 equation identifiers (2.10)-(2.13)."
        ),
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(REVIEW),
    }

    data["dataset_stable_key"] = "dataset/unit-016/id-id"
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
        "order": 16,
        "source_local_id": "chapter2.tex:1111-1405",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；极限"},
            {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Limit"},
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
            "outcome/define-inductive-and-projective-limits",
            "outcome/read-cones-cocones-and-universal-diagrams",
            "outcome/use-duality-and-functoriality-of-limits",
            "outcome/construct-limits-in-set-and-top",
            "outcome/work-with-filtered-colimits",
            "outcome/compute-pointwise-functor-category-limits",
            "outcome/test-limit-existence-by-representability",
            "outcome/iterate-limits-via-fubini",
            "outcome/construct-finite-limits-from-products-and-equalizers",
            "outcome/apply-product-and-coproduct-coherence-constraints",
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
    data["prerequisites"] = prerequisites
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
            "Unit 016 backend refused: CSV projection missing: "
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
                "formula_entities": formula_total,
                "label_entities": len(source_labels),
                "ordinary_reference_entities": len(
                    ordinary_reference_occurrences(source_text)
                ),
                "equation_reference_entities": len(
                    equation_reference_occurrences(source_text)
                ),
                "correction_entities": len(CORRECTIONS),
                "citations": len(citations),
                "diagrams": len(diagrams),
                "index_entries": len(index_entries),
                "artifact": {
                    "pages": page_count,
                    "bytes": artifact_id[0],
                    "sha256": artifact_id[1],
                },
                "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
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
