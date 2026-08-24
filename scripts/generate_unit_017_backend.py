#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 017.

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
TEMPLATE = ROOT / "backend/data/unit-016-bab-2-limit.json"
OUTPUT = ROOT / "backend/data/unit-017-bab-2-kelengkapan.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-017-bab-2-kelengkapan.tex"
COVER = "repo/source/coverpage-id-unit-017.tex"
CROSSREF = "repo/source/unit-017-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_017.ps1"
STRUCTURE_GATE = "scripts/check_unit_017_structure.py"
SUMMARY = "qa/unit-017-evidence/build-log-summary.txt"
REVIEW = "qa/UNIT_017_TRANSLATION_SOURCE_REVIEW_20260824.md"
FINAL_LOG = "qa/UNIT_017_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-017-bab-2-kelengkapan.pdf"
STRUCTURE_QA = "qa/unit-017-evidence/structure-and-pdf-qa.json"
FINAL_AUX = "build/unit-017-build-g/unit-017-bab-2-kelengkapan.aux"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 1406, 1602
SOURCE_FULL = (
    139_983,
    "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840",
)
TARGET_FULL = (
    165_139,
    "be7c571d574e7c8608f535f59627c47118cdb7f00a44aaf1e7d85eb11ea60e35",
)
SOURCE_SPAN = (
    15_810,
    "ccc5a17cbf856e59e7b8abbff8fd542c5deb399e58b6fc7a5a0f448c7c019e92",
)
TARGET_SPAN = (
    18_633,
    "e27dba97355122446714b8e58f71f80edbb1d74e6160f99ba0b8160e7c3ec30b",
)

LABELS = (
    "def:completeness",
    "prop:preorder-complete",
    "prop:limit-buildingblocks",
    "eqn:lim-as-ker",
    "prop:completeness-criterion",
    "eg:complete-cocomplete",
    "def:preservation-limit",
    "rem:preservation-limit",
    "eg:preservation-limit",
    "prop:Hom-exact",
    "prop:adjuncion-limit",
)
REFERENCES = (
    "eg:set-limits",
    "eg:categories",
    "prop:Cantor",
    "eg:set-limits",
    "prop:lim-Yoneda",
    "prop:lim-as-fct",
    "prop:limit-buildingblocks",
    "eg:set-limits",
    "eg:top-limits",
    "prop:completeness-criterion",
    "def:monoid-times",
    "def:free-product",
    "prop:completeness-criterion",
    "prop:monoid-direct-sum",
    "prop:preorder-complete",
    "prop:lim-as-fct",
    "prop:lim-Yoneda",
    "prop:Yoneda-lemma",
    "prop:lim-Yoneda",
    "eg:set-limits",
    "prop:lim-as-fct",
    "prop:limit-buildingblocks",
    "eg:top-limits",
    "prop:lim-Yoneda",
    "prop:lim-as-fct",
    "sec:adjoint-functor",
    "rem:lim-duality",
    "prop:lim-Yoneda",
    "prop:lim-as-fct",
    "def:preservation-limit",
    "def:preservation-limit",
    "eg:preservation-limit",
    "eg:top-adjunction",
    "eg:forgetful-adjunction",
    "prop:abelianization",
)
EQUATION_REFERENCES = (
    "eqn:lim-diagrams",
    "eqn:lim-as-ker",
    "eqn:lim-diagrams",
    "eqn:lim-diagrams",
    "eqn:lim-as-ker",
)
CITATIONS = ()
INDEX_SLUGS = (
    "complete-category",
    "cocomplete-category",
    "pullback",
    "fiber-product",
    "pushout",
    "fiber-coproduct",
    "pullback-repeat",
    "pushout-repeat",
    "adjunction",
)
INDEX_TOPOLOGY = (
    ("main", 1409),
    ("main", 1409),
    ("main", 1463),
    ("main", 1463),
    ("main", 1464),
    ("main", 1464),
    ("main", 1483),
    ("main", 1483),
    ("main", 1569),
)
CORRECTIONS = (
    (
        "O013-LI-U017-COR-001",
        1525,
        "The left comparison leg starts at F alpha(i), but the authority labels it with alpha(j); the target changes only that label to alpha(i).",
    ),
    (
        "O013-LI-U017-COR-002",
        1554,
        "The authority calls the coproduct in Ab a direct product; the target correctly says direct sum.",
    ),
    (
        "O013-LI-U017-COR-003",
        1585,
        "The authority quantifies j over Obj(i); the target repairs the category index to Obj(I).",
    ),
    (
        "O013-LI-U017-COR-004",
        1588,
        "Two Hom terms with F(-) and beta(j) are ill-typed over C1; the target changes both subscripts to C2 on lines 1588-1589.",
    ),
    (
        "O013-LI-U017-COR-005",
        1589,
        "The two canonical limit projections need not be surjective; the target removes the twoheadrightarrow arrowheads on lines 1589-1590.",
    ),
    (
        "O013-LI-U017-COR-006",
        1547,
        "The C2 existence claim omits F from the projective-limit diagram; the target repairs it to lim(F beta).",
    ),
)
EXPECTED_AUX = (
    r"\newlabel{eg:categories}{{2.1.{5}}{3}}",
    r"\newlabel{prop:Cantor}{{1.4.{3}}{13}}",
    r"\newlabel{sec:adjoint-functor}{{2.6}{1}}",
    r"\newlabel{eg:top-adjunction}{{2.6.{7}}{1}}",
    r"\newlabel{eg:forgetful-adjunction}{{2.6.{8}}{1}}",
    r"\newlabel{eqn:lim-diagrams}{{2.10}{2}}",
    r"\newlabel{rem:lim-duality}{{2.7.{3}}{2}}",
    r"\newlabel{eg:set-limits}{{2.7.{5}}{3}}",
    r"\newlabel{eg:top-limits}{{2.7.{7}}{5}}",
    r"\newlabel{prop:lim-Yoneda}{{2.7.{8}}{6}}",
    r"\newlabel{prop:lim-as-fct}{{2.7.{9}}{7}}",
    r"\newlabel{def:monoid-times}{{4.3.{1}}{0}}",
    r"\newlabel{prop:abelianization}{{4.7.{3}}{0}}",
    r"\newlabel{def:free-product}{{4.8.{9}}{0}}",
    r"\newlabel{prop:monoid-direct-sum}{{4.8.{11}}{0}}",
)
EXPECTED_EQUATION_NUMBERING = {
    "eqn:lim-as-ker": "2.14",
    "status": (
        "matches source-order Chapter 2 identifiers after setting the standalone "
        "equation counter to 13"
    ),
}
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-017-{name}.csv"
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
        raise SystemExit(f"Unit 017 backend refused: identity drift for {relative}")


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
        raise SystemExit("Unit 017 backend refused: unpaired inline-math delimiter")
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


def pair_inline_formula_occurrences(
    source_items: tuple[tuple[int, int, str], ...],
    target_items: tuple[tuple[int, int, str], ...],
) -> tuple[tuple[tuple[int, int, str], tuple[int, int, str]], ...]:
    """Pair reflowed inline formulae without confusing within-line reorderings.

    Exact formula text is matched first within the same physical line.  The
    structural checker separately proves the declared source corrections and
    translated ``text`` fragment; after exact matching each such line has one
    unambiguous unmatched source/target pair.
    """

    unused = set(range(len(target_items)))
    paired_by_source: dict[int, int] = {}
    unmatched_sources: list[int] = []
    for source_index, source_item in enumerate(source_items):
        _, source_line, source_formula = source_item
        candidates = [
            index
            for index in unused
            if target_items[index][1] == source_line
            and target_items[index][2] == source_formula
        ]
        if candidates:
            chosen = min(candidates)
        else:
            unmatched_sources.append(source_index)
            continue
        unused.remove(chosen)
        paired_by_source[source_index] = chosen
    for source_index in unmatched_sources:
        source_line = source_items[source_index][1]
        candidates = [index for index in unused if target_items[index][1] == source_line]
        if len(candidates) != 1:
            raise SystemExit(
                "Unit 017 backend refused: ambiguous corrected inline-formula pairing "
                f"at source line {source_line}"
            )
        chosen = candidates[0]
        unused.remove(chosen)
        paired_by_source[source_index] = chosen
    if unused:
        raise SystemExit("Unit 017 backend refused: unpaired target inline formulae")
    return tuple(
        (source_item, target_items[paired_by_source[source_index]])
        for source_index, source_item in enumerate(source_items)
    )


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
            "Unit 017 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 017 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate_structure_qa() -> tuple[int, tuple[int, str], tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"Unit 017 backend refused: structured QA witness is unreadable: {exc}"
        ) from exc
    if evidence.get("status") != "PASS":
        raise SystemExit("Unit 017 backend refused: structured QA status is not PASS")
    authority = evidence.get("authority", {})
    if authority != {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_file": "chapter2.tex",
        "source_lines": "1406-1602",
        "source_span_bytes": SOURCE_SPAN[0],
        "source_span_sha256": SOURCE_SPAN[1],
    }:
        raise SystemExit("Unit 017 backend refused: structured authority evidence drift")
    target = evidence.get("target", {})
    if target != {
        "target_span_bytes": TARGET_SPAN[0],
        "target_span_sha256": TARGET_SPAN[1],
        "correction_ids": [item[0] for item in CORRECTIONS],
        "translation_only_grammar_repair_line": 1410,
        "han_residue": 0,
    }:
        raise SystemExit("Unit 017 backend refused: structured target evidence drift")
    if evidence.get("provenance_model") != MODEL:
        raise SystemExit("Unit 017 backend refused: structured model provenance drift")
    if evidence.get("rights") != "CC BY 4.0":
        raise SystemExit("Unit 017 backend refused: structured principal-rights drift")
    artifact = evidence.get("artifact", {})
    try:
        page_count = int(evidence["pdf"]["pages"])
        artifact_id = (int(artifact["bytes"]), str(artifact["sha256"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit("Unit 017 backend refused: malformed structured artifact identity") from exc
    if artifact.get("path") != ARTIFACT or page_count < 1:
        raise SystemExit("Unit 017 backend refused: structured artifact path/page drift")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_id[1]):
        raise SystemExit("Unit 017 backend refused: malformed structured artifact hash")
    require_identity(ARTIFACT, artifact_id)
    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        raise SystemExit("Unit 017 backend refused: structured build-log evidence drift")
    replay = evidence.get("deterministic_replay", {})
    poppler_keys = tuple(
        key for key in replay if key.startswith("poppler_page_mismatches_")
    )
    mupdf_keys = tuple(key for key in replay if key.startswith("mupdf_page_mismatches_"))
    if len(poppler_keys) != 1 or len(mupdf_keys) != 1:
        raise SystemExit("Unit 017 backend refused: deterministic replay pair is ambiguous")
    replay_pair = poppler_keys[0].removeprefix("poppler_page_mismatches_")
    if mupdf_keys[0] != "mupdf_page_mismatches_" + replay_pair:
        raise SystemExit("Unit 017 backend refused: renderer replay pairs differ")
    pair_parts = replay_pair.split("_")
    if len(pair_parts) != 2 or any(not re.fullmatch(r"[a-z]", part) for part in pair_parts):
        raise SystemExit("Unit 017 backend refused: malformed deterministic replay suffix")
    if (
        replay.get(poppler_keys[0]) != 0
        or replay.get(mupdf_keys[0]) != 0
        or replay.get("pdftotext_layout_sha256_" + pair_parts[0])
        != replay.get("pdftotext_layout_sha256_" + pair_parts[1])
        or not re.fullmatch(
            r"[0-9a-f]{64}",
            str(replay.get("pdftotext_layout_sha256_" + pair_parts[0], "")),
        )
    ):
        raise SystemExit("Unit 017 backend refused: deterministic replay evidence drift")
    visual = evidence.get("visual_qa", {})
    if (
        visual.get("status") != "PASS"
        or visual.get("pages_inspected") != list(range(1, page_count + 1))
        or visual.get("renderers_inspected") != ["Poppler", "MuPDF"]
    ):
        raise SystemExit("Unit 017 backend refused: all-page visual evidence drift")
    blockers = evidence.get("log_counts", {})
    for key in (
        "overfull_boxes",
        "undefined_control_sequences",
        "undefined_references_summary",
        "undefined_reference_warnings",
        "undefined_citations",
        "missing_characters",
        "fatal_errors",
        "emergency_stops",
    ):
        if blockers.get(key) != 0:
            raise SystemExit(f"Unit 017 backend refused: nonzero build blocker {key}")
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
            "Unit 017 backend scaffold is complete but final evidence is not yet present: "
            + ", ".join(missing)
        )
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(TARGET, TARGET_FULL)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 017 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 017 backend refused: target span drift")

    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 017 backend refused: structure gate failed\n" + check.stderr)
    checker_needles = (
        "PASS Unit 017 structural checker",
        "source lines=197 bytes=15810 sha256=" + SOURCE_SPAN[1],
        "target lines=197 bytes=18633 sha256=" + TARGET_SPAN[1],
        "boundary line=1603 value=Exercises active_commands=749 raw_commands=806 comments=1531-1538",
        "active_begin=39 active_end=39 labels=11 refs=32 raw_refs=35 eqrefs=5 cites=0 indexes=9 items=21",
        "inline_math=185 raw_inline_math=199 bracket_displays=4 equations=3 align*=2 tikzcd=9 arrows=47 han=0",
        "corrections=O013-LI-U017-COR-001..006 prose_grammar_line=1410",
    )
    if any(needle not in check.stdout for needle in checker_needles):
        raise SystemExit("Unit 017 backend refused: structure-gate report drift")

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
        raise SystemExit("Unit 017 backend refused: label topology drift")
    if tuple(label for label, _ in source_refs) != REFERENCES or source_refs != target_refs:
        raise SystemExit("Unit 017 backend refused: ordinary-reference topology drift")
    if (
        tuple(label for label, _ in source_eqrefs) != EQUATION_REFERENCES
        or source_eqrefs != target_eqrefs
    ):
        raise SystemExit("Unit 017 backend refused: equation-reference topology drift")
    if citation_occurrences(source) != CITATIONS or citation_occurrences(target) != CITATIONS:
        raise SystemExit("Unit 017 backend refused: citation topology drift")

    source_indexes = base.index_occurrences(source)
    target_indexes = base.index_occurrences(target)
    if tuple((item[0], item[2]) for item in source_indexes) != INDEX_TOPOLOGY:
        raise SystemExit("Unit 017 backend refused: source index topology drift")
    if tuple((item[0], item[2]) for item in target_indexes) != INDEX_TOPOLOGY:
        raise SystemExit("Unit 017 backend refused: target index topology drift")
    if tuple(item[0] for item in source_indexes) != tuple(item[0] for item in target_indexes):
        raise SystemExit("Unit 017 backend refused: index namespace drift")
    if any(not item[1].strip() for item in target_indexes):
        raise SystemExit("Unit 017 backend refused: empty localized index key")

    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if source_diagrams != target_diagrams or len(source_diagrams) != 9:
        raise SystemExit("Unit 017 backend refused: diagram occurrence topology drift")

    source_inline = inline_formula_occurrences(source)
    target_inline = inline_formula_occurrences(target)
    if len(source_inline) != 199 or len(target_inline) != 199:
        raise SystemExit("Unit 017 backend refused: inline-formula count drift")
    if tuple(item[1] for item in source_inline) != tuple(sorted(item[1] for item in target_inline)):
        raise SystemExit("Unit 017 backend refused: inline-formula location drift")
    pair_inline_formula_occurrences(source_inline, target_inline)

    source_brackets = bracket_formula_occurrences(source)
    target_brackets = bracket_formula_occurrences(target)
    if len(source_brackets) != 4 or len(target_brackets) != 4:
        raise SystemExit("Unit 017 backend refused: bracket-display count drift")
    if tuple(item[:3] for item in source_brackets) != tuple(item[:3] for item in target_brackets):
        raise SystemExit("Unit 017 backend refused: bracket-display location drift")
    source_env_formulas = environment_formula_occurrences(source)
    target_env_formulas = environment_formula_occurrences(target)
    if len(source_env_formulas) != 6 or len(target_env_formulas) != 6:
        raise SystemExit("Unit 017 backend refused: environment-formula count drift")
    if tuple(item[:4] for item in source_env_formulas) != tuple(
        item[:4] for item in target_env_formulas
    ):
        raise SystemExit("Unit 017 backend refused: environment-formula location drift")

    actual_aux = tuple(
        line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    if actual_aux != EXPECTED_AUX:
        raise SystemExit("Unit 017 backend refused: external-reference map drift")
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\setcounter{chapter}{2}",
        r"\setcounter{section}{7}",
        r"\setcounter{theorem}{0}",
        r"\setcounter{equation}{13}",
        r"\setstretch{1.25}",
        r"\InputSourceLineRange{chapter2.tex}{1406}{1602}",
        r"\printindex",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 017 backend refused: driver lacks {needle!r}")

    final_aux = (ROOT / FINAL_AUX).read_text(encoding="utf-8")
    equation_numbering = {
        label: number
        for label, number in re.findall(
            r"\\newlabel\{(eqn:lim-as-ker)\}"
            r"\{\{([^{}]+)\}",
            final_aux,
        )
    }
    if equation_numbering != {
        key: value for key, value in EXPECTED_EQUATION_NUMBERING.items() if key != "status"
    }:
        raise SystemExit("Unit 017 backend refused: final-AUX equation numbering drift")

    page_count, artifact_id, log_id = gate_structure_qa()
    if pdfinfo_page_count() != page_count:
        raise SystemExit("Unit 017 backend refused: live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    # TeX wraps long transcript lines at a fixed column, including the word
    # "pages" itself (for example, ``pag\nes``).  Accept only whitespace
    # inserted within that fixed literal; do not loosen the surrounding gate.
    log_pages = re.findall(
        r"Output written on .*?\((\d+)\s+p\s*a\s*g\s*e\s*s?\)\.",
        final_log,
        re.DOTALL,
    )
    if not log_pages or int(log_pages[-1]) != page_count:
        raise SystemExit("Unit 017 backend refused: final build-log page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    summary_needles = (
        "PASS Unit 017 final build and replay",
        f"pages={page_count}",
        artifact_id[1],
        log_id[1],
        f"Poppler {page_count}/{page_count} identical",
        f"MuPDF {page_count}/{page_count} identical",
        f"visual QA: all {page_count} build-G pages inspected directly in Poppler and MuPDF",
        "provenance model: " + MODEL,
    )
    if any(needle not in summary for needle in summary_needles):
        raise SystemExit("Unit 017 backend refused: build summary is incomplete")
    review_needles = (
        "Status: **PASS**.",
        "chapter2.tex:1406-1602",
        TARGET_SPAN[1],
        MODEL,
        "Wen-Wei Li",
        "CC BY 4.0",
        "source and Indonesian derivative are",
        *(item[0] for item in CORRECTIONS),
    )
    if any(needle not in review for needle in review_needles):
        raise SystemExit("Unit 017 backend refused: translation/source review is incomplete")
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
    unit_key = "unit/bab-2-kelengkapan"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/kelengkapan"
    section_id = uid(section_key)

    core_specs = (
        ("concept/complete-category", "完备范畴", "kategori lengkap"),
        ("concept/cocomplete-category", "余完备范畴", "kategori kolengkap"),
        ("concept/small-limit", "小极限", "limit kecil"),
        ("concept/small-colimit", "小余极限", "kolimit kecil"),
        ("concept/small-category", "小范畴", "kategori kecil"),
        ("concept/preordered-category", "预序范畴", "kategori praterurut"),
        ("concept/infimum", "下确界", "infimum"),
        ("concept/freyd-small-completeness-theorem", "Freyd 小完备性定理", "teorema kelengkapan kecil Freyd"),
        ("concept/limit-building-blocks", "极限的构造块", "blok pembangun limit"),
        ("concept/product", "积", "produk"),
        ("concept/coproduct", "余积", "koproduk"),
        ("concept/equalizer", "等化子", "ekualiser"),
        ("concept/coequalizer", "余等化子", "koekualiser"),
        ("concept/finite-limit", "有限极限", "limit berhingga"),
        ("concept/finite-colimit", "有限余极限", "kolimit berhingga"),
        ("concept/initial-object", "始对象", "objek awal"),
        ("concept/terminal-object", "终对象", "objek terminal"),
        ("concept/fiber-product", "纤维积", "produk serat"),
        ("concept/pullback", "拉回", "tarik balik"),
        ("concept/fiber-coproduct", "纤维余积", "koproduk serat"),
        ("concept/pushout", "推出", "dorong keluar"),
        ("concept/cartesian-square", "Cartesius 图表", "diagram Kartesius"),
        ("concept/direct-product-of-groups", "群的直积", "produk langsung grup"),
        ("concept/free-product-of-groups", "群的自由积", "produk bebas grup"),
        ("concept/direct-sum-of-abelian-groups", "交换群的直和", "jumlah langsung grup abelian"),
        ("concept/group-coequalizer", "群同态的余等化子", "koekualiser homomorfisme grup"),
        ("concept/abelian-group-coequalizer", "交换群同态的余等化子", "koekualiser homomorfisme grup abelian"),
        ("concept/limit-preservation", "保持极限", "mempertahankan limit"),
        ("concept/colimit-preservation", "保持余极限", "mempertahankan kolimit"),
        ("concept/limit-comparison-morphism", "极限比较态射", "morfisme pembanding limit"),
        ("concept/colimit-comparison-morphism", "余极限比较态射", "morfisme pembanding kolimit"),
        ("concept/representability-of-limits", "极限的可表性", "representabilitas limit"),
        ("concept/hom-functor-limit-preservation", "Hom 函子保持极限", "fungtor Hom mempertahankan limit"),
        ("concept/adjunction", "伴随对", "pasangan adjoin"),
        ("concept/left-adjoint-preserves-colimits", "左伴随保持余极限", "adjoin kiri mempertahankan kolimit"),
        ("concept/right-adjoint-preserves-limits", "右伴随保持极限", "adjoin kanan mempertahankan limit"),
        ("concept/forgetful-functor", "忘却函子", "fungtor pelupa"),
        ("concept/abelianization", "交换化", "abelianisasi"),
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
                f"surface/unit-017/label/{ordinal:03d}",
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
                    f"surface/unit-017/reference/{kind}/{ordinal:03d}",
                    f"{source_name} {ordinal:03d}: {label}; 源行 {source_line}",
                    f"{target_name} {ordinal:03d}: {label}; baris target {target_line}",
                )
            )

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    for source_item, target_item in pair_inline_formula_occurrences(
        source_inline, target_inline
    ):
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-017/formula/inline/{ordinal:03d}",
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
                f"surface/unit-017/formula/display-bracket/{ordinal:03d}",
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
                f"surface/unit-017/formula/display-environment/{ordinal:03d}",
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
            "prerequisite/limits-and-colimits",
            "极限与余极限",
            "limit dan kolimit",
            1111,
            1405,
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
        "source_local_id": "chapter2.tex:1406-1602",
        "titles": [
            {"language": "zh-Hans", "text": "2.8 完备性"},
            {"language": "id-ID", "text": "2.8 Kelengkapan"},
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
        key = f"citation/unit-017/{bib_key.casefold()}"
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
        key = f"index-entry/unit-017/{slug}"
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
            raise SystemExit("Unit 017 backend refused: diagram binding drift")
        key = f"diagram/unit-017/{source_format}-{source_occurrence:02d}"
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
        "id": uid("build-surface/unit-017-pdf"),
        "stable_key": "build-surface/unit-017-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": (
            "pwsh -NoProfile -File scripts/build_unit_017.ps1 "
            "-OutputDirectory build/unit-017-replay"
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
            "makeindex (default index)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 017 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    correction_ids = ", ".join(item[0] for item in CORRECTIONS)
    formula_total = len(source_inline) + len(source_brackets) + len(source_env_formulas)
    qa = {
        "id": uid("qa/unit-017/admission-gate"),
        "stable_key": "qa/unit-017/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and semantic review of chapter2.tex lines "
            "1406-1602; 197 physical lines, 39 active balanced environments, 11 labels, "
            "35 raw ordinary-reference occurrences (32 active), five equation-reference "
            "occurrences, no citations, nine index entries, nine TikZ-CD diagrams with "
            f"47 arrows, 199 raw inline plus 10 display formula surfaces ({formula_total} "
            "total), 21 list "
            "items, and no exercises, hints, answers, or solutions. Mathematics is "
            f"preserved after six disclosed corrections ({correction_ids}); exact "
            "equation continuity is (2.14)-(2.16); the reader uses 1.25 digital reflow, "
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
        "id": uid("qa/unit-017/structured-public-evidence"),
        "stable_key": "qa/unit-017/structured-public-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": (
            "Structured QA binds the admitted target, final reader and log identities, "
            "complete label/reference/formula/index/diagram topology, six declared "
            "corrections, 1.25 digital reflow, exact model provenance, and source-order "
            "Chapter 2 equation identifiers (2.14)-(2.16)."
        ),
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": bind(REVIEW),
    }

    data["dataset_stable_key"] = "dataset/unit-017/id-id"
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
        "order": 17,
        "source_local_id": "chapter2.tex:1406-1602",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；完备性"},
            {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Kelengkapan"},
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
            "outcome/define-complete-and-cocomplete-categories",
            "outcome/apply-product-equalizer-completeness-criteria",
            "outcome/construct-pullbacks-and-pushouts",
            "outcome/prove-grp-and-ab-complete-and-cocomplete",
            "outcome/distinguish-direct-sum-and-free-product-coproducts",
            "outcome/construct-limit-and-colimit-comparison-morphisms",
            "outcome/test-preservation-via-products-and-equalizers",
            "outcome/apply-hom-functor-limit-preservation",
            "outcome/prove-adjoints-preserve-colimits-and-limits",
            "outcome/infer-adjoint-obstructions-from-coproduct-failure",
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
            "Unit 017 backend refused: CSV projection missing: "
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
