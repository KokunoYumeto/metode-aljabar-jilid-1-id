#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 020.

The shared v1.1.0 schema has no first-class TeX-label, reference-occurrence,
formula, list-item, diagram-edge/node, terminology-row, or correction record.
Those protected surfaces are therefore represented by deterministic
concept-compatible UUIDv5 entities.  Native citation, diagram, index, build,
rights, and QA records remain native.  Nothing is written until the frozen
source/target topology and the final build/admission evidence all pass.
"""

from __future__ import annotations

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


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-019-bab-3-definisi-dasar.json"
OUTPUT = ROOT / "backend/data/unit-020-bab-3-keketatan-dan-teorema-koherensi.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-020-bab-3-keketatan-dan-teorema-koherensi.tex"
COVER = "repo/source/coverpage-id-unit-020.tex"
CROSSREF = "repo/source/unit-020-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_020.ps1"
STRUCTURE_GATE = "scripts/check_unit_020_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_020_evidence.py"
SUMMARY = "qa/unit-020-evidence/build-log-summary.txt"
RENDER_INVENTORY = "qa/unit-020-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-020-evidence/structure-and-pdf-qa.json"
STRUCTURE_OUTPUT = "qa/unit-020-evidence/structure-check.txt"
REVIEW = "qa/UNIT_020_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_020_MATH_STRUCTURE_AUDIT_20260824.md"
CORRECTION_REVIEW = "qa/UNIT_020_SOURCE_CORRECTION_20260824.md"
VISUAL_REVIEW = "qa/UNIT_020_VISUAL_QA_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_QA_CATEGORY = "qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md"
TERMINOLOGY_QA_GRADUATE = "qa/TERMINOLOGY_QA_INDONESIAN_GRADUATE_ALGEBRA_20260824.md"
TERMINOLOGY_AUDIT = "qa/UNIT_020_TERMINOLOGY_AUDIT_20260824.md"
FINAL_LOG = "qa/UNIT_020_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-020-bab-3-keketatan-dan-teorema-koherensi.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
SOURCE_START, SOURCE_END = 228, 306
TARGET_START, TARGET_END = 227, 305
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    6_071,
    "86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737",
)
TARGET_SPAN = (
    7_266,
    "25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270",
)
CORRECTIONS = (
    (
        "O013-LI-U020-COR-001",
        299,
        "Authority line 299 writes the undefined datum (F,m); the target restores "
        "the defined object datum (F,rho) used throughout the construction.",
        CORRECTION_REVIEW,
    ),
)
LABELS = (
    "sec:coherence",
    "def:strict-monoidal-cat",
    "prop:ML-coherence",
)
REFERENCES = (
    ("ordinary", "def:monoidal-cat", 5),
    ("ordinary", "sec:monoidal-cat-def", 19),
    ("ordinary", "eg:monoidal-cat", 19),
    ("ordinary", "prop:ML-coherence", 25),
    ("ordinary", "prop:ML-coherence", 78),
)
CITATIONS = (
    ("VII.2", "ML98", 19),
    ("pp.26--27", "JS93", 25),
    (r"\S 2.8", "EGNO15", 25),
)
ITEM_LINES = (4, 5, 12, 13, 27, 44, 50, 51, 72, 73)
INDEX_SPECS = (
    (
        "strict-monoidal-category",
        "main",
        9,
        "yaobanfanchou@kategori monoidal (monoidal category)!kategori monoidal ketat (strict monoidal category)",
    ),
    (
        "mac-lane-coherence-theorem",
        "main",
        21,
        "MacLane@Teorema koherensi Mac Lane (Mac Lane's Coherence Theorem)",
    ),
)
DIAGRAM_SPECS = (
    ("tikzpicture", 1, 30, 43),
    ("tikzcd", 1, 45, 48),
)
TERMINOLOGY_SPECS = (
    ("strict monoidal category", "kategori monoidal ketat"),
    ("strictness (monoidal category)", "keketatan"),
    ("coherence (category theory)", "koherensi"),
    ("Mac Lane's coherence theorem", "teorema koherensi Mac Lane"),
)
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-020-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 020 backend refused: identity drift for {relative}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    lines = (ROOT / relative).read_bytes().decode("utf-8").splitlines()
    if len(lines) < last:
        raise SystemExit(
            f"Unit 020 backend refused: {relative} has {len(lines)} lines; "
            f"cannot bind {first}-{last}"
        )
    return ("\n".join(lines[first - 1 : last]) + "\n").encode("utf-8")


def source_binding(relative: str, first: int | None = None, last: int | None = None):
    return base.binding(relative, first, last)


def target_binding(
    first: int,
    last: int,
    admission_identity: tuple[int, str],
) -> dict[str, object]:
    selected = normalized_span(TARGET, first, last)
    return {
        "path": TARGET,
        "bytes": admission_identity[0],
        "sha256": admission_identity[1],
        "line_start": first,
        "line_end": last,
        "span_sha256": digest(selected),
        "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
    }


def span_text(relative: str, first: int, last: int) -> str:
    return normalized_span(relative, first, last).decode("utf-8")


def line_at(text: str, position: int, first: int = 1) -> int:
    return first + text.count("\n", 0, position)


def label_occurrences(text: str):
    return tuple(
        (match.group(1), line_at(text, match.start()))
        for match in re.finditer(r"\\label\{([^{}]+)\}", text)
    )


def reference_occurrences(text: str):
    return tuple(
        (
            "equation" if match.group(1) else "ordinary",
            match.group(2),
            line_at(text, match.start()),
        )
        for match in re.finditer(r"\\(eq)?ref\{([^{}]+)\}", text)
    )


def citation_occurrences(text: str):
    return tuple(
        (
            match.group(1) or "",
            match.group(2),
            line_at(text, match.start()),
        )
        for match in re.finditer(r"\\cite(?:\[([^]\r\n]*)\])?\{([^{}]+)\}", text)
    )


def occurrence_lines(text: str, pattern: str):
    return tuple(line_at(text, match.start()) for match in re.finditer(pattern, text))


def is_escaped(text: str, position: int) -> bool:
    count = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        count += 1
        position -= 1
    return count % 2 == 1


def inline_formula_occurrences(text: str):
    delimiters = tuple(
        position
        for position, character in enumerate(text)
        if character == "$" and not is_escaped(text, position)
    )
    if len(delimiters) % 2:
        raise SystemExit("Unit 020 backend refused: unpaired inline-math delimiter")
    return tuple(
        (
            ordinal,
            line_at(text, delimiters[offset]),
            text[delimiters[offset] + 1 : delimiters[offset + 1]],
        )
        for ordinal, offset in enumerate(range(0, len(delimiters), 2), 1)
    )


def pair_inline_formula_occurrences(source_items, target_items):
    """Pair exact same-line formulae before localized same-line formulae."""

    unused = set(range(len(target_items)))
    pairs: dict[int, int] = {}
    deferred: list[int] = []
    for source_index, source_item in enumerate(source_items):
        candidates = [
            target_index
            for target_index in unused
            if target_items[target_index][1] == source_item[1]
            and target_items[target_index][2] == source_item[2]
        ]
        if candidates:
            chosen = min(candidates)
            unused.remove(chosen)
            pairs[source_index] = chosen
        else:
            deferred.append(source_index)
    for source_index in deferred:
        candidates = [
            target_index
            for target_index in unused
            if target_items[target_index][1] == source_items[source_index][1]
        ]
        if len(candidates) != 1:
            raise SystemExit(
                "Unit 020 backend refused: ambiguous localized inline formula at "
                f"line {source_items[source_index][1]}"
            )
        chosen = candidates[0]
        unused.remove(chosen)
        pairs[source_index] = chosen
    if unused:
        raise SystemExit("Unit 020 backend refused: unpaired target inline formulae")
    return tuple(
        (source_item, target_items[pairs[source_index]])
        for source_index, source_item in enumerate(source_items)
    )


def bracket_formula_occurrences(text: str):
    return tuple(
        (
            ordinal,
            line_at(text, match.start()),
            line_at(text, match.end() - 1),
            match.group(1),
        )
        for ordinal, match in enumerate(re.finditer(r"\\\[(.*?)\\\]", text, re.DOTALL), 1)
    )


def environment_formula_occurrences(text: str):
    pattern = re.compile(
        r"\\begin\{(equation\*?|align\*?|gather\*?)\}(.*?)\\end\{\1\}",
        re.DOTALL,
    )
    return tuple(
        (
            ordinal,
            match.group(1),
            line_at(text, match.start()),
            line_at(text, match.end() - 1),
            match.group(2),
        )
        for ordinal, match in enumerate(pattern.finditer(text), 1)
    )


def canonical_formula(text: str) -> str:
    """Normalize layout-only TeX whitespace without changing command content."""

    return re.sub(r"\s+", " ", text).strip()


def read_terminology_rows() -> tuple[dict[str, str], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    selected = []
    for source_term, target_term in TERMINOLOGY_SPECS:
        matches = [row for row in rows if row.get("source_term") == source_term]
        if len(matches) != 1:
            raise SystemExit(
                f"Unit 020 backend refused: terminology row {source_term!r} is not unique"
            )
        row = matches[0]
        if row.get("target_term") != target_term:
            raise SystemExit(
                f"Unit 020 backend refused: terminology target drift for {source_term!r}"
            )
        if row.get("status") != "admitted":
            raise SystemExit(
                "Unit 020 backend scaffold is ready but terminology admission is pending: "
                f"{source_term!r} remains {row.get('status')!r}"
            )
        selected.append(row)
    return tuple(selected)


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
        raise SystemExit("Unit 020 backend refused: pdfinfo failed\n" + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 020 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def exact_target_admission_identity(evidence: dict[str, object]) -> tuple[int, str]:
    target = evidence.get("target", {})
    if not isinstance(target, dict):
        raise SystemExit("Unit 020 backend refused: malformed structured target evidence")
    reported_bytes = target.get("target_file_bytes")
    reported_hash = target.get("target_file_sha256")
    if reported_bytes is not None or reported_hash is not None:
        try:
            candidate = (int(reported_bytes), str(reported_hash))
        except (TypeError, ValueError) as exc:
            raise SystemExit("Unit 020 backend refused: malformed target-file identity") from exc
        if not re.fullmatch(r"[0-9a-f]{64}", candidate[1]):
            raise SystemExit("Unit 020 backend refused: malformed target-file hash")
    elif OUTPUT.is_file():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))["unit"]["target_binding"]
        candidate = (int(prior["bytes"]), str(prior["sha256"]))
    else:
        candidate = identity(TARGET)
    if not OUTPUT.is_file() and identity(TARGET) != candidate:
        raise SystemExit("Unit 020 backend refused: admission-time target identity is not live")
    return candidate


def gate_structured_evidence() -> tuple[int, tuple[int, str], tuple[int, str], tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
        renders = json.loads((ROOT / RENDER_INVENTORY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unit 020 backend refused: unreadable structured evidence: {exc}") from exc
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U020":
        raise SystemExit("Unit 020 backend refused: structured QA status/unit drift")
    target = evidence.get("target", {})
    if not isinstance(target, dict):
        raise SystemExit("Unit 020 backend refused: malformed structured target evidence")
    required_target = {
        "path": TARGET,
        "lines": "227-305",
        "line_records": 79,
        "bytes": TARGET_SPAN[0],
        "sha256": TARGET_SPAN[1],
        "next_target_line": 306,
        "next_line_sha256": "0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8",
        "correction_ids": [CORRECTIONS[0][0]],
    }
    if target != required_target:
        raise SystemExit("Unit 020 backend refused: structured target span drift")
    target_admission_id = exact_target_admission_identity(evidence)
    expected_structure = {
        "labels": list(LABELS),
        "references": [label for _, label, _ in REFERENCES],
        "citations": [bib_key for _, bib_key, _ in CITATIONS],
        "index_entries": 2,
        "tikzpicture": 1,
        "tikzcd": 1,
    }
    if evidence.get("structure") != expected_structure:
        raise SystemExit("Unit 020 backend refused: structured source/target closure drift")
    if evidence.get("provenance_model") != MODEL:
        raise SystemExit("Unit 020 backend refused: model provenance drift")
    expected_rights = {
        "principal_text_and_translation": "CC BY 4.0",
        "AJbook_class_fragment": "CC BY-SA 3.0",
        "bundled_noto_fonts": "SIL OFL 1.1",
        "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
    }
    if evidence.get("rights") != expected_rights:
        raise SystemExit("Unit 020 backend refused: component-rights evidence drift")
    artifact = evidence.get("artifact", {})
    try:
        artifact_id = (int(artifact["bytes"]), str(artifact["sha256"]))
        page_count = int(evidence["pdf"]["pages"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit("Unit 020 backend refused: malformed artifact/page evidence") from exc
    if artifact.get("path") != ARTIFACT or page_count < 1:
        raise SystemExit("Unit 020 backend refused: artifact path/page drift")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_id[1]):
        raise SystemExit("Unit 020 backend refused: malformed artifact hash")
    require_identity(ARTIFACT, artifact_id)
    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        raise SystemExit("Unit 020 backend refused: final build-log identity drift")
    for key, relative in (
        ("evidence_generator", EVIDENCE_GENERATOR),
        ("render_inventory", RENDER_INVENTORY),
    ):
        expected = {
            "path": relative,
            "bytes": identity(relative)[0],
            "sha256": identity(relative)[1],
        }
        if evidence.get(key) != expected:
            raise SystemExit(f"Unit 020 backend refused: {key} binding drift")
    visual = evidence.get("visual_qa", {})
    if (
        visual.get("status") != "PASS"
        or visual.get("pages_inspected") != list(range(1, page_count + 1))
        or visual.get("renderers_inspected") != ["Poppler", "MuPDF"]
    ):
        raise SystemExit("Unit 020 backend refused: all-page visual evidence drift")
    if (
        renders.get("unit_id") != "O013-LI-U020"
        or renders.get("page_count") != page_count
        or renders.get("provenance_model") != MODEL
    ):
        raise SystemExit("Unit 020 backend refused: render-inventory unit/page drift")
    render_replay = evidence.get("deterministic_replay", {})
    mismatches = render_replay.get("same_renderer_page_mismatches", {})
    if (
        render_replay.get("semantic_and_render_identity") is not True
        or mismatches.get("poppler") != 0
        or mismatches.get("mupdf") != 0
        or render_replay.get("layout_text_sha256_e")
        != render_replay.get("layout_text_sha256_f")
    ):
        raise SystemExit("Unit 020 backend refused: deterministic semantic replay drift")
    comparisons = renders.get("comparisons", {})
    if len(comparisons) != 6 or not all(
        item.get("page_count_match") is True
        and item.get("raw_pixel_identical") is True
        and item.get("png_byte_identical") is True
        and item.get("raw_pixel_mismatch_pages") == []
        and item.get("png_byte_mismatch_pages") == []
        and item.get("dimension_mismatch_pages") == []
        for item in comparisons.values()
    ):
        raise SystemExit("Unit 020 backend refused: deterministic raster replay drift")
    if renders.get("render_count") != 40 or renders.get("contact_sheet_count") != 8:
        raise SystemExit("Unit 020 backend refused: deterministic text replay drift")
    for renderer in ("poppler", "mupdf"):
        pages = renders.get("renderers", {}).get(renderer, [])
        if (
            [item.get("page") for item in pages] != list(range(1, page_count + 1))
            or not all(item.get("outer_3px_ink") == 0 for item in pages)
            or not all(re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256"))) for item in pages)
            or not all(re.fullmatch(r"[0-9a-f]{64}", str(item.get("raw_rgb_sha256"))) for item in pages)
        ):
            raise SystemExit(f"Unit 020 backend refused: {renderer} render inventory drift")
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
            raise SystemExit(f"Unit 020 backend refused: nonzero build blocker {key}")
    return page_count, artifact_id, log_id, target_admission_id


def gate() -> tuple[
    int,
    tuple[int, str],
    tuple[int, str],
    tuple[int, str],
    tuple[dict[str, str], ...],
]:
    required = (
        TEMPLATE.relative_to(ROOT).as_posix(),
        DRIVER,
        COVER,
        CROSSREF,
        BIBLIOGRAPHY,
        BUILD_SCRIPT,
        STRUCTURE_GATE,
        EVIDENCE_GENERATOR,
        SUMMARY,
        RENDER_INVENTORY,
        STRUCTURE_QA,
        STRUCTURE_OUTPUT,
        REVIEW,
        MATH_REVIEW,
        CORRECTION_REVIEW,
        VISUAL_REVIEW,
        TERMINOLOGY,
        TERMINOLOGY_QA_CATEGORY,
        TERMINOLOGY_QA_GRADUATE,
        TERMINOLOGY_AUDIT,
        FINAL_LOG,
        ARTIFACT,
    )
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(
            "Unit 020 backend scaffold is complete but final inputs are missing:\n  - "
            + "\n  - ".join(missing)
        )
    require_identity(SOURCE, SOURCE_FULL)
    if (len(normalized_span(SOURCE, SOURCE_START, SOURCE_END)), digest(normalized_span(SOURCE, SOURCE_START, SOURCE_END))) != SOURCE_SPAN:
        raise SystemExit("Unit 020 backend refused: source span drift")
    if (len(normalized_span(TARGET, TARGET_START, TARGET_END)), digest(normalized_span(TARGET, TARGET_START, TARGET_END))) != TARGET_SPAN:
        raise SystemExit("Unit 020 backend refused: target span drift")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    target_lines = (ROOT / TARGET).read_text(encoding="utf-8").splitlines()
    if len(source_lines) < 307 or len(target_lines) < 306 or source_lines[306] != target_lines[305]:
        raise SystemExit("Unit 020 backend refused: next-section boundary is not preserved")

    check = subprocess.run(
        [sys.executable, "-B", str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 020 backend refused: structure checker failed\n" + check.stdout + check.stderr)
    for needle in ("PASS", "Unit 020", SOURCE_SPAN[1], TARGET_SPAN[1]):
        if needle not in check.stdout:
            raise SystemExit(f"Unit 020 backend refused: structure-check output lacks {needle!r}")

    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    if tuple(label for label, _ in source_labels) != LABELS or source_labels != target_labels:
        raise SystemExit("Unit 020 backend refused: three-label topology drift")
    if reference_occurrences(source_text) != REFERENCES or reference_occurrences(target_text) != REFERENCES:
        raise SystemExit("Unit 020 backend refused: five-reference topology drift")
    if citation_occurrences(source_text) != CITATIONS or citation_occurrences(target_text) != CITATIONS:
        raise SystemExit("Unit 020 backend refused: three-citation topology drift")
    if occurrence_lines(source_text, r"\\item(?![A-Za-z])") != ITEM_LINES or occurrence_lines(target_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        raise SystemExit("Unit 020 backend refused: ten-item topology drift")

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    if tuple((item[0], item[2]) for item in source_indexes) != tuple((item[1], item[2]) for item in INDEX_SPECS):
        raise SystemExit("Unit 020 backend refused: source index topology drift")
    if tuple((item[0], item[2], item[1]) for item in target_indexes) != tuple((item[1], item[2], item[3]) for item in INDEX_SPECS):
        raise SystemExit("Unit 020 backend refused: localized index topology drift")
    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    if source_diagrams != DIAGRAM_SPECS or target_diagrams != DIAGRAM_SPECS:
        raise SystemExit("Unit 020 backend refused: two-diagram topology drift")

    surface_specs = (
        (r"\\arrow(?![A-Za-z])", 4, "arrow"),
        (r"\\node(?![A-Za-z])", 5, "node"),
        (r"\\path(?![A-Za-z])", 1, "path"),
        (r"(?<![A-Za-z])edge(?![A-Za-z])", 5, "edge"),
    )
    for pattern, expected, name in surface_specs:
        source_occurrences = occurrence_lines(source_text, pattern)
        target_occurrences = occurrence_lines(target_text, pattern)
        if source_occurrences != target_occurrences or len(source_occurrences) != expected:
            raise SystemExit(f"Unit 020 backend refused: {expected}-{name} topology drift")

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    if len(source_inline) != 64 or len(target_inline) != 64:
        raise SystemExit("Unit 020 backend refused: 64-inline-formula topology drift")
    inline_pairs = pair_inline_formula_occurrences(source_inline, target_inline)
    inline_changes = tuple(
        (source_item[1], source_item[2], target_item[2])
        for source_item, target_item in inline_pairs
        if canonical_formula(source_item[2]) != canonical_formula(target_item[2])
    )
    if (
        len(inline_changes) != 1
        or inline_changes[0][0] != 72
        or inline_changes[0][1] != r"(F, m) \simeq L(F(\munit))"
        or inline_changes[0][2] != r"(F, \rho) \simeq L(F(\munit))"
    ):
        raise SystemExit("Unit 020 backend refused: declared inline correction drift")
    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    if len(source_brackets) != 5 or len(target_brackets) != 5 or tuple(item[:3] for item in source_brackets) != tuple(item[:3] for item in target_brackets):
        raise SystemExit("Unit 020 backend refused: five-display-bracket topology drift")
    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    if source_env or target_env:
        raise SystemExit("Unit 020 backend refused: unexpected equation/align display environment")

    external_refs = {label for kind, label, _ in REFERENCES if label not in LABELS}
    crossref_text = (ROOT / CROSSREF).read_text(encoding="utf-8")
    crossref_labels = set(re.findall(r"\\newlabel\{([^{}]+)\}", crossref_text))
    if not external_refs.issubset(crossref_labels):
        raise SystemExit(
            "Unit 020 backend refused: unresolved frozen crossrefs: "
            + ", ".join(sorted(external_refs - crossref_labels))
        )
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\InputSourceLineRange{chapter3.tex}{227}{305}",
        r"\setstretch{1.16}",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 020 backend refused: driver lacks {needle!r}")
    bibliography = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8", errors="replace")
    for bib_key in {item[1] for item in CITATIONS}:
        if not re.search(r"@[A-Za-z]+\s*\{\s*" + re.escape(bib_key) + r"\s*,", bibliography):
            raise SystemExit(f"Unit 020 backend refused: bibliography lacks {bib_key}")

    terminology_rows = read_terminology_rows()
    page_count, artifact_id, log_id, target_admission_id = gate_structured_evidence()
    if pdfinfo_page_count() != page_count:
        raise SystemExit("Unit 020 backend refused: live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(
        r"Output written on .*?\((\d+)\s+pages?\)\.", final_log, re.DOTALL
    )
    if not log_pages or int(log_pages[-1]) != page_count:
        raise SystemExit("Unit 020 backend refused: final log page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    for needle in ("PASS", "Unit 020", f"pages={page_count}", artifact_id[1], MODEL):
        if needle not in summary:
            raise SystemExit(f"Unit 020 backend refused: build summary lacks {needle!r}")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    math_review = (ROOT / MATH_REVIEW).read_text(encoding="utf-8")
    correction_review = (ROOT / CORRECTION_REVIEW).read_text(encoding="utf-8")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for needle in ("Status: **PASS after three isolated candidate repairs**", "lines 228-306", TARGET_SPAN[1], MODEL, CORRECTIONS[0][0]):
        if needle not in review:
            raise SystemExit(f"Unit 020 backend refused: source review lacks {needle!r}")
    for needle in ("PASS", "13", "64", "five bracket displays", "four-arrow", CORRECTIONS[0][0]):
        if needle not in math_review:
            raise SystemExit(f"Unit 020 backend refused: math review lacks {needle!r}")
    for needle in ("APPLIED AND VERIFIED", CORRECTIONS[0][0], "$(F, m)$", "$(F, \\rho)$", MODEL):
        if needle not in correction_review:
            raise SystemExit(f"Unit 020 backend refused: correction review lacks {needle!r}")
    for needle in (
        "strict monoidal category",
        "strictness (monoidal category)",
        "coherence (category theory)",
        "Mac Lane's coherence theorem",
        "kekoherenan",
        "koherensi",
        MODEL,
    ):
        if needle not in terminology_audit:
            raise SystemExit(f"Unit 020 backend refused: terminology audit lacks {needle!r}")
    for needle in ("PASS", str(page_count), "Poppler", "MuPDF", artifact_id[1]):
        if needle not in visual_review:
            raise SystemExit(f"Unit 020 backend refused: visual review lacks {needle!r}")
    return page_count, artifact_id, log_id, target_admission_id, terminology_rows


def main() -> None:
    page_count, artifact_id, log_id, target_admission_id, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-3-keketatan-dan-teorema-koherensi"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/keketatan-dan-teorema-koherensi"
    section_id = uid(section_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_absolute = lambda line: SOURCE_START + line - 1
    target_absolute = lambda line: TARGET_START + line - 1

    core_specs = (
        ("concept/monoidal-category", "幺半范畴", "kategori monoidal"),
        ("concept/strict-monoidal-category", "严格幺半范畴", "kategori monoidal ketat"),
        ("concept/strictness-monoidal-category", "幺半范畴的严格性", "keketatan kategori monoidal"),
        ("concept/mac-lane-coherence-theorem", "Mac Lane 融贯定理", "Teorema koherensi Mac Lane"),
        ("concept/coherence-category-theory", "范畴论中的融贯性", "koherensi dalam teori kategori"),
        ("concept/tensor-product", "张量积", "hasil kali tensor"),
        ("concept/unit-object", "幺对象", "objek satuan"),
        ("concept/associativity-constraint", "结合约束", "kendala asosiativitas"),
        ("concept/unit-constraint", "幺约束", "kendala satuan"),
        ("concept/mac-lane-pentagon-axiom", "Mac Lane 五角形公理", "aksioma segilima Mac Lane"),
        ("concept/monoidal-functor", "幺半函子", "fungtor monoidal"),
        ("concept/monoidal-equivalence", "幺半等价", "ekuivalensi monoidal"),
        ("concept/full-functor", "满函子", "fungtor penuh"),
        ("concept/faithful-functor", "忠实函子", "fungtor setia"),
        ("concept/essentially-surjective-functor", "本质满函子", "fungtor surjektif secara esensial"),
        ("concept/natural-transformation", "自然变换", "transformasi natural"),
        ("concept/category-e-of-v", "范畴 e(V)", "kategori e(V)"),
        ("concept/strictification-functor-l", "函子 L", "fungtor L"),
    )
    concepts = [surface_concept(uid, *spec) for spec in core_specs]

    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_labels, target_labels, strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        concepts.append(surface_concept(uid, f"surface/unit-020/label/{ordinal:03d}", f"TeX 标签 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}", f"label TeX {ordinal:03d}: {label}; baris target {target_absolute(target_line)}"))

    for ordinal, (source_item, target_item) in enumerate(zip(reference_occurrences(source_text), reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        concepts.append(surface_concept(uid, f"surface/unit-020/reference/{kind}/{ordinal:03d}", f"引用 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}", f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_absolute(target_line)}"))

    for ordinal, (locator, bib_key, line) in enumerate(CITATIONS, 1):
        locator_source = locator or "无定位符"
        locator_target = locator or "tanpa lokator"
        concepts.append(surface_concept(uid, f"surface/unit-020/citation-occurrence/{ordinal:03d}", f"引文出现 {ordinal:03d}: {bib_key}; {locator_source}; 源行 {source_absolute(line)}", f"kemunculan sitasi {ordinal:03d}: {bib_key}; {locator_target}; baris target {target_absolute(line)}"))

    for ordinal, line in enumerate(ITEM_LINES, 1):
        concepts.append(surface_concept(uid, f"surface/unit-020/item/{ordinal:03d}", f"列表项目 {ordinal:03d}; 源行 {source_absolute(line)}", f"butir daftar {ordinal:03d}; baris target {target_absolute(line)}"))

    inline_pairs = pair_inline_formula_occurrences(inline_formula_occurrences(source_text), inline_formula_occurrences(target_text))
    for source_item, target_item in inline_pairs:
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-020/formula/inline/{ordinal:03d}", f"行内公式 {ordinal:03d}; 源行 {source_absolute(source_line)}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus sebaris {ordinal:03d}; baris target {target_absolute(target_line)}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-020/formula/display-bracket/{ordinal:03d}", f"陈列公式 {ordinal:03d}; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus pajang {ordinal:03d}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_env, target_env, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-020/formula/display-environment/{ordinal:03d}", f"{environment} 公式 {ordinal:03d}; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus {environment} {ordinal:03d}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    for kind, pattern, source_name, target_name in (
        ("arrow", r"\\arrow(?![A-Za-z])", "图表箭头", "panah diagram"),
        ("node", r"\\node(?![A-Za-z])", "图表节点", "simpul diagram"),
        ("path", r"\\path(?![A-Za-z])", "图表路径", "lintasan diagram"),
        ("edge", r"(?<![A-Za-z])edge(?![A-Za-z])", "图表边", "sisi diagram"),
    ):
        source_lines = occurrence_lines(source_text, pattern)
        target_lines = occurrence_lines(target_text, pattern)
        for ordinal, (source_line, target_line) in enumerate(zip(source_lines, target_lines, strict=True), 1):
            concepts.append(surface_concept(uid, f"surface/unit-020/diagram-{kind}/{ordinal:03d}", f"{source_name} {ordinal:03d}; 源行 {source_absolute(source_line)}", f"{target_name} {ordinal:03d}; baris target {target_absolute(target_line)}"))

    for correction_id, line, issue, evidence_path in CORRECTIONS:
        concepts.append(surface_concept(uid, f"correction/{correction_id.casefold()}", f"声明的源文本更正 {correction_id}; 源行 {line}", f"koreksi sumber terdeklarasi {correction_id}; baris sumber {line}; {issue} Bukti: {evidence_path}."))

    for ordinal, row in enumerate(terminology_rows, 1):
        concepts.append(surface_concept(uid, f"surface/unit-020/terminology-row/{ordinal:03d}", f"术语记录 {ordinal:03d}: {row['source_term']}", f"baris terminologi {ordinal:03d}: {row['source_term']} -> {row['target_term']}; status admitted; scope {row['scope']}"))

    concept_ids = [item["id"] for item in concepts]
    selected_prerequisite_keys = {
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
    }
    prerequisite_ids = [item["id"] for item in data["prerequisites"] if item["stable_key"] in selected_prerequisite_keys]
    if len(prerequisite_ids) != len(selected_prerequisite_keys):
        raise SystemExit("Unit 020 backend refused: prerequisite inventory drift")
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    principal = rights_by_key["rights/principal-cc-by-4.0"]
    unit_rights = [principal, rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"], rights_by_key["rights/noto-fonts-ofl-1.1"]]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter3.tex:228-306",
        "titles": [{"language": "zh-Hans", "text": "第三章：幺半范畴；严格性与融贯定理"}, {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Keketatan dan Teorema Koherensi"}],
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END, target_admission_id),
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    bibliography_hash = identity(BIBLIOGRAPHY)[1]
    citations = []
    seen_bib_keys: set[str] = set()
    for locator, bib_key, line in CITATIONS:
        if bib_key in seen_bib_keys:
            continue
        seen_bib_keys.add(bib_key)
        key = f"citation/unit-020/{bib_key.casefold()}"
        citations.append({
            "id": uid(key), "stable_key": key, "entity_type": "citation",
            "bib_key": bib_key, "bibliography_path": BIBLIOGRAPHY,
            "bibliography_sha256": bibliography_hash, "source_line": source_absolute(line),
            "target_line": target_absolute(line), "section_id": section_id,
        })

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (spec, source_index, target_index) in enumerate(zip(INDEX_SPECS, source_indexes, target_indexes, strict=True), 1):
        slug, _, _, _ = spec
        key = f"index-entry/unit-020/{slug}"
        index_entries.append({
            "id": uid(key), "stable_key": key, "entity_type": "index_entry",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_key": source_index[1], "target_key": target_index[1],
            "source_binding": source_binding(SOURCE, source_absolute(source_index[2]), source_absolute(source_index[2])),
            "target_binding": target_binding(target_absolute(target_index[2]), target_absolute(target_index[2]), target_admission_id),
            "provenance_state": "source_key_preserved_target_key_localized",
        })

    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-020/{source_format}-{occurrence:02d}"
        diagrams.append({
            "id": uid(key), "stable_key": key, "entity_type": "diagram",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_format": source_format, "source_occurrence_index": occurrence,
            "source_binding": source_binding(SOURCE, source_absolute(source_first), source_absolute(source_last)),
            "target_binding": target_binding(target_absolute(target_first), target_absolute(target_last), target_admission_id),
            "rights_component_id": principal, "state": "audited_preserved",
        })

    inputs = [
        COVER, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls",
        "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex",
        "repo/source/titles-setup.tex", "repo/source/mycommand.sty",
        "repo/source/myarrows.sty", BIBLIOGRAPHY, "repo/source/ccby.png",
        CROSSREF, "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf", "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-020-pdf"), "stable_key": "build-surface/unit-020-pdf",
        "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_020.ps1 -OutputDirectory build/unit-020-replay",
        "artifact_path": ARTIFACT, "artifact_binding": source_binding(ARTIFACT),
        "log_binding": source_binding(FINAL_LOG), "build_script": source_binding(BUILD_SCRIPT),
        "page_count": page_count, "status": "pass", "driver": source_binding(DRIVER),
        "input_bindings": [source_binding(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution", "TeX Gyre Heros", "TikZ and tikz-cd",
            "TikZ tqft library", "packages loaded by the Unit 020 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    formula_total = len(inline_pairs) + len(source_brackets) + len(source_env)
    qa_admission = {
        "id": uid("qa/unit-020/admission-gate"), "stable_key": "qa/unit-020/admission-gate",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and all-page admission of chapter3.tex authority lines 228-306 "
            "to target lines 227-305: three labels, five ordinary references, three citations, ten list items, "
            "one tikzcd and one tikzpicture structure, four tikzcd arrows, five TikZ nodes, one path and five "
            f"edges, 64 inline plus five bracket-display formula surfaces ({formula_total} total), and two "
            "localized index entries. Correction O013-LI-U020-COR-001 discloses the minimal (F,m)-to-(F,rho) "
            "repair and binds its separate correction record. Exactly four reviewed terminology rows were "
            "admitted only after the final reader and visual gate, with the kekoherenan/koherensi disagreement "
            "recorded without claiming direct same-field attestation. Component rights remain CC BY 4.0 "
            "for principal text/translation, CC BY-SA 3.0 for the AJbook fragment, and OFL 1.1 for bundled "
            f"fonts. Production provenance is {MODEL}, separate from Wen-Wei Li's authorship and human credit."
        ),
        "witness": STRUCTURE_QA, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(STRUCTURE_QA),
    }
    qa_source = {
        "id": uid("qa/unit-020/source-review"), "stable_key": "qa/unit-020/source-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent translation/source review of the exact authority and target spans, including terminology, formula, citation, index, diagram, and correction preservation.",
        "witness": REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(REVIEW),
    }
    qa_math = {
        "id": uid("qa/unit-020/math-structure-review"), "stable_key": "qa/unit-020/math-structure-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent mathematical-topology audit of every protected surface and the minimal (F,m)-to-(F,rho) source correction.",
        "witness": MATH_REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(MATH_REVIEW),
    }
    qa_correction = {
        "id": uid("qa/unit-020/source-correction"), "stable_key": "qa/unit-020/source-correction",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Separate provenance and deterministic adjudication for O013-LI-U020-COR-001 at authority line 299 and target line 298.",
        "witness": CORRECTION_REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(CORRECTION_REVIEW),
    }
    qa_structure = {
        "id": uid("qa/unit-020/structure-check"), "stable_key": "qa/unit-020/structure-check",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Machine structure check binds the source/target boundary, external-reference closure, protected-surface census, and zero Han residue.",
        "witness": STRUCTURE_OUTPUT, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(STRUCTURE_OUTPUT),
    }
    qa_replay = {
        "id": uid("qa/unit-020/render-replay"), "stable_key": "qa/unit-020/render-replay",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Deterministic extracted-text and same-renderer Poppler/MuPDF replay, with all pages visually inspected.",
        "witness": RENDER_INVENTORY, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(RENDER_INVENTORY),
    }
    qa_visual = {
        "id": uid("qa/unit-020/all-page-visual-review"), "stable_key": "qa/unit-020/all-page-visual-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent all-page visual review of the final reader in Poppler and MuPDF after the final reflow boundary.",
        "witness": VISUAL_REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(VISUAL_REVIEW),
    }
    qa_terms = {
        "id": uid("qa/unit-020/terminology-control"), "stable_key": "qa/unit-020/terminology-control",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live id-ID glossary binding for exactly four Unit 020 terminology additions; all other specialized terms reuse admitted mappings.",
        "witness": TERMINOLOGY, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(TERMINOLOGY),
    }
    qa_term_evidence = {
        "id": uid("qa/unit-020/terminology-evidence"), "stable_key": "qa/unit-020/terminology-evidence",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": (
            "Bound Unit 020 terminology adjudication records the 2008 glossary's kekoherenan alternative, "
            f"retains corpus koherensi without direct-attestation overclaim, and preserves {TERMINOLOGY_QA_CATEGORY} "
            f"and {TERMINOLOGY_QA_GRADUATE} as separate scope evidence."
        ),
        "witness": TERMINOLOGY_AUDIT, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(TERMINOLOGY_AUDIT),
    }

    data["dataset_stable_key"] = "dataset/unit-020/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-24", "status": "admitted", "admission_state": "admitted",
        "translation_state": "visually_checked", "qa_state": "translation_math_backend_build_visual_pass",
    }
    data["unit"] = {
        "id": unit_id, "stable_key": unit_key, "entity_type": "unit",
        "program_id": data["program"]["id"], "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"],
        "order": 20, "source_local_id": "chapter3.tex:228-306",
        "titles": [{"language": "zh-Hans", "text": "第三章：幺半范畴；严格性与融贯定理"}, {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Keketatan dan Teorema Koherensi"}],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END, target_admission_id),
        "section_ids": [section_id], "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [
            qa_admission["id"], qa_source["id"], qa_math["id"], qa_correction["id"],
            qa_structure["id"], qa_replay["id"], qa_visual["id"], qa_terms["id"],
            qa_term_evidence["id"],
        ],
        "outcome_keys": [
            "outcome/define-strict-monoidal-category",
            "outcome/state-and-use-mac-lane-coherence",
            "outcome/construct-strict-monoidal-category-e-of-v",
            "outcome/analyze-strictification-functor-l",
            "outcome/verify-full-faithful-essentially-surjective-criterion",
        ],
        "surface_counts": {
            "sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0,
            "citations": len(citations), "diagrams": len(diagrams), "index_entries": len(index_entries),
        },
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = [
        qa_admission, qa_source, qa_math, qa_correction, qa_structure, qa_replay, qa_visual, qa_terms,
        qa_term_evidence,
    ]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([
        sys.executable, str(ROOT / "scripts/validate_backend.py"), "--lane-root", str(ROOT),
        "--data", str(OUTPUT), "--schema", str(ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"),
        "--csv-dir", str(ROOT / "backend/csv"), "--write-csv",
    ], cwd=ROOT, check=True)
    missing_csv = [path for path in CSV_OUTPUTS if not path.is_file()]
    if missing_csv:
        raise SystemExit("Unit 020 backend refused: missing CSV projection")
    print(json.dumps({
        "path": OUTPUT.relative_to(ROOT).as_posix(), "bytes": OUTPUT.stat().st_size,
        "sha256": digest(OUTPUT.read_bytes()), "concepts": len(concepts),
        "labels": 3, "references": 5, "citation_occurrences": 3,
        "native_bibliography_records": 3, "items": 10,
        "formula_entities": formula_total, "diagrams": 2, "arrows": 4,
        "nodes": 5, "paths": 1, "edges": 5, "index_entries": 2, "corrections": 1,
        "terminology_rows": 4,
        "artifact": {"pages": page_count, "bytes": artifact_id[0], "sha256": artifact_id[1]},
        "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
        "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
