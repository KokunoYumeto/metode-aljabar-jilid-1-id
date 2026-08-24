#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 023.

The shared v1.1.0 schema has no first-class TeX-label, reference-occurrence,
formula, diagram primitive, terminology-row, or editorial record. Those
protected surfaces are represented by deterministic concept-compatible
UUIDv5 entities. Native citation, diagram, index, build, rights, and QA records
remain native. Nothing is written until source/target topology and final
reader/build/visual evidence all pass.
"""

from __future__ import annotations

from collections import Counter, defaultdict
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
TEMPLATE = ROOT / "backend/data/unit-022-bab-3-kategori-diperkaya-dan-aditif.json"
OUTPUT = ROOT / "backend/data/unit-023-bab-3-sekilas-tentang-2-kategori.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
CANDIDATE = "build/unit-023-candidate/chapter3-2-categories-id.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-023-bab-3-sekilas-tentang-2-kategori.tex"
COVER = "repo/source/coverpage-id-unit-023.tex"
CROSSREF = "repo/source/unit-023-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_023.ps1"
STRUCTURE_GATE = "scripts/check_unit_023_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_023_evidence.py"
RENDER_INVENTORY = "qa/unit-023-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-023-evidence/structure-and-pdf-qa.json"
REVIEW = "qa/UNIT_023_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_023_MATH_STRUCTURE_AUDIT_20260824.md"
VISUAL_REVIEW = "qa/UNIT_023_VISUAL_QA_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_023_TERMINOLOGY_AUDIT_20260824.md"
FINAL_LOG = "qa/UNIT_023_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-023-bab-3-sekilas-tentang-2-kategori.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_START, SOURCE_END = 723, 872
TARGET_START, TARGET_END = 722, 871
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    12_436,
    "2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856",
)
CANDIDATE_FULL = (
    14_894,
    "c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05",
)
TARGET_FULL = (
    88_491,
    "8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f",
)
TARGET_SPAN = CANDIDATE_FULL
NEXT_LINE_SHA256 = "0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699"
STRUCTURE_GATE_ID = (
    6_280,
    "b7e9df6eb08298f0376cc4f897115fa8af37bca572c98f3fa8d7393ce5013b73",
)
REVIEW_ID = (
    9_303,
    "970adde88fdbdebd292bd0a3bcadd3dafd51c3d507edd50e90e2e7832fdc1b10",
)
MATH_REVIEW_ID = (
    7_114,
    "d356e204a81d32c84bba1cb6eda45a5fac036bf98c95b97ac6747f8135ba977f",
)
TERMINOLOGY_ID = (
    45_230,
    "9e2d946520a1c9f8984abd1b78935c2fe052e5bfdf79e9c9091d41a29b7cd68a",
)
TERMINOLOGY_AUDIT_ID = (
    7_901,
    "792d5fe6b28161c17f74f15294944bcaef5f6df0d50ee4edfd300f09da731fa8",
)

EDITORIALS = (
    (
        "O013-LI-U023-ED-001",
        "865",
        "864",
        "The target preserves the authority's romanized adjunction sort key and adds "
        "only the learner-visible Indonesian display payload 'pasangan adjoin'.",
    ),
)

LABELS = (
    "sec:2-cat",
    "eg:Cat",
)
REFERENCES = (
    ("ordinary", "eg:Cat", 4),
    ("ordinary", "rem:strict-or-not", 85),
    ("ordinary", "prop:ML-coherence", 85),
    ("ordinary", "con:U-small", 89),
    ("ordinary", "prop:naturaltrans-associativity", 96),
    ("ordinary", "eg:categories", 99),
    ("ordinary", "eg:monoidal-cat", 99),
    ("ordinary", "sec:functor-category", 102),
    ("ordinary", "def:enriched-cat", 116),
    ("ordinary", "def:enriched-functor", 120),
    ("ordinary", "def:enriched-naturaltrans", 120),
    ("ordinary", "sec:functors", 125),
    ("ordinary", "rem:triangle-identity", 129),
    ("ordinary", "sec:adjoint-functor", 144),
    ("ordinary", "rem:triangle-identity", 148),
    ("ordinary", "prop:adjoint-equivalence", 148),
)
CITATIONS = ()
ITEM_LINES = (9, 10, 11, 15, 17, 32, 45, 53, 54, 67, 91, 92, 93, 94, 106, 107, 108, 110, 112)

INDEX_SPECS = (
    ("2-category", "main", 6, "$2$-kategori"),
    ("cat-symbol", "sym1", 88, r"Cat@$\cate{Cat}$"),
    ("adjunction", "main", 143, "bansuidui@pasangan adjoin"),
)

DIAGRAM_SPECS = (
    ("tikzcd", 1, 18, 24),
    ("tikzcd", 2, 26, 31),
    ("tikzcd", 3, 32, 32),
    ("tikzcd", 4, 32, 32),
    ("tikzcd", 5, 33, 37),
    ("tikzcd", 6, 39, 44),
    ("tikzcd", 7, 46, 51),
    ("tikzcd", 8, 55, 59),
    ("tikzcd", 9, 61, 66),
    ("tikzcd", 10, 68, 78),
    ("tikzcd", 11, 126, 128),
    ("tikzcd", 12, 130, 133),
    ("tikzcd", 13, 135, 140),
    ("tikzcd", 14, 145, 147),
)

TERMINOLOGY_SPECS = (
    ("higher category", "kategori tingkat lebih tinggi"),
    ("2-category", "2-kategori"),
    ("strict 2-category", "2-kategori ketat"),
    ("weak 2-category", "2-kategori lemah"),
    ("bicategory", "bikategori"),
    ("0-morphism", "0-morfisme"),
    ("1-morphism", "1-morfisme"),
    ("2-morphism", "2-morfisme"),
    ("2-functor", "2-fungtor"),
    ("pseudofunctor", "pseudofungtor"),
    ("2-natural transformation", "2-transformasi natural"),
    ("pseudonatural transformation", "transformasi pseudonatural"),
    ("modification", "modifikasi"),
    ("interchange law", "hukum pertukaran"),
    ("vertical category", "kategori vertikal"),
    ("horizontal identity", "identitas horizontal"),
    ("vertical identity", "identitas vertikal"),
    ("2-cell", "2-sel"),
    ("vertical composition", "komposisi vertikal"),
    ("horizontal composition", "komposisi horizontal"),
)

SURFACE_SPECS = (
    ("arrow", r"\\arrow(?![A-Za-z])", 64, "图表箭头", "panah diagram"),
    ("node", r"\\node(?![A-Za-z])", 0, "图表节点", "simpul diagram"),
    ("coordinate", r"\\coordinate(?![A-Za-z])", 0, "图表坐标", "koordinat diagram"),
    ("draw", r"\\draw(?![A-Za-z])", 0, "绘图命令", "perintah gambar"),
    ("path", r"\\path(?![A-Za-z])", 0, "图表路径", "lintasan diagram"),
    ("edge", r"(?<![A-Za-z])edge(?![A-Za-z])", 0, "图表边", "sisi diagram"),
    ("braid", r"\\braid(?![A-Za-z])", 0, "辫图命令", "perintah diagram kepang"),
    ("hline", r"\\hline(?![A-Za-z])", 0, "表格横线", "garis mendatar tabel"),
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-023-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 023 backend refused: " + message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        refuse(f"identity drift for {relative}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    lines = (ROOT / relative).read_bytes().decode("utf-8").splitlines()
    if len(lines) < last:
        refuse(f"{relative} has {len(lines)} lines; cannot bind {first}-{last}")
    return ("\n".join(lines[first - 1 : last]) + "\n").encode("utf-8")


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


def line_at(text: str, position: int) -> int:
    return 1 + text.count("\n", 0, position)


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
        (match.group(1) or "", match.group(2), line_at(text, match.start()))
        for match in re.finditer(r"\\cite(?:\[([^]\r\n]*)\])?\{([^{}]+)\}", text)
    )


def environment_occurrences(text: str):
    records: list[list[object]] = []
    stack: list[tuple[str, int]] = []
    per_kind: Counter[str] = Counter()
    for match in re.finditer(r"\\(begin|end)\{([^{}]+)\}", text):
        event, environment = match.groups()
        line = line_at(text, match.start())
        if event == "begin":
            per_kind[environment] += 1
            records.append([environment, per_kind[environment], line, None])
            stack.append((environment, len(records) - 1))
        else:
            if not stack or stack[-1][0] != environment:
                refuse(f"unbalanced environment event for {environment} at relative line {line}")
            _, record_index = stack.pop()
            records[record_index][3] = line
    if stack or any(record[3] is None for record in records):
        refuse("unclosed environment in selected span")
    return tuple(tuple(record) for record in records)


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
        refuse("unpaired inline-math delimiter")
    return tuple(
        (
            ordinal,
            line_at(text, delimiters[offset]),
            text[delimiters[offset] + 1 : delimiters[offset + 1]],
        )
        for ordinal, offset in enumerate(range(0, len(delimiters), 2), 1)
    )


def pair_inline_formula_occurrences(source_items, target_items):
    """Pair exact same-line formulae first, then the sole localized remainder."""

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
            refuse(
                "ambiguous localized inline formula at relative line "
                f"{source_items[source_index][1]}"
            )
        chosen = candidates[0]
        unused.remove(chosen)
        pairs[source_index] = chosen
    if unused:
        refuse("unpaired target inline formulae")
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
        r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}(.*?)\\end\{\1\}",
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


def localized_math(text: str, repair_source: bool = False) -> str:
    del repair_source
    text = re.sub(r"\\text\{[^{}]*\}", r"\\text{<localized>}", text)
    return re.sub(r"\s+", "", text)


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


def read_terminology_rows() -> tuple[dict[str, str], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    selected = []
    for source_term, target_term in TERMINOLOGY_SPECS:
        matches = [row for row in rows if row.get("source_term") == source_term]
        if len(matches) != 1:
            refuse(f"terminology row {source_term!r} is not unique")
        row = matches[0]
        if row.get("target_term") != target_term:
            refuse(f"terminology target drift for {source_term!r}")
        if row.get("status") != "admitted":
            refuse(f"terminology row {source_term!r} remains {row.get('status')!r}")
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


def gate_structured_evidence() -> tuple[int, tuple[int, str], tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
        renders = json.loads((ROOT / RENDER_INVENTORY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        refuse(f"unreadable structured evidence: {exc}")
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U023":
        refuse("structured QA status/unit drift")

    required_target = {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
        "line_records": 910,
        "span_lines": "722-871",
        "span_line_records": 150,
        "span_bytes": TARGET_SPAN[0],
        "span_sha256": TARGET_SPAN[1],
        "span_equals_isolated_candidate": True,
        "next_target_line": 872,
        "next_line_sha256": NEXT_LINE_SHA256,
    }
    if evidence.get("canonical_target") != required_target:
        refuse("structured target span drift")
    if evidence.get("candidate") != {
        "path": CANDIDATE,
        "bytes": CANDIDATE_FULL[0],
        "sha256": CANDIDATE_FULL[1],
    }:
        refuse("structured candidate identity drift")

    expected_structure = {
        "labels": list(LABELS),
        "references": [label for _, label, _ in REFERENCES],
        "external_references": [
            "con:U-small",
            "def:enriched-cat",
            "def:enriched-functor",
            "def:enriched-naturaltrans",
            "eg:categories",
            "eg:monoidal-cat",
            "prop:ML-coherence",
            "prop:adjoint-equivalence",
            "prop:naturaltrans-associativity",
            "rem:strict-or-not",
            "rem:triangle-identity",
            "sec:adjoint-functor",
            "sec:functor-category",
            "sec:functors",
        ],
        "external_crossref_numbers": {
            "con:U-small": "2.1.4",
            "eg:categories": "2.1.5",
            "sec:functors": "2.2",
            "prop:naturaltrans-associativity": "2.2.7",
            "rem:strict-or-not": "2.2.11",
            "sec:functor-category": "2.3",
            "sec:adjoint-functor": "2.6",
            "rem:triangle-identity": "2.6.6",
            "prop:adjoint-equivalence": "2.6.12",
            "eg:monoidal-cat": "3.1.3",
            "prop:ML-coherence": "3.2.2",
            "def:enriched-cat": "3.4.1",
            "def:enriched-functor": "3.4.2",
            "def:enriched-naturaltrans": "3.4.4",
        },
        "citations": [
            {"locator": locator, "key": bib_key}
            for locator, bib_key, _ in CITATIONS
        ],
        "index_entries": 3,
        "ordinary_index_entries": 2,
        "symbol_index_entries": 1,
        "environment_counts": {
            "tikzcd": 14,
            "remark": 3,
            "definition": 2,
            "compactitem": 2,
            "itemize": 1,
            "enumerate": 1,
            "example": 1,
            "convention": 1,
        },
        "tikzpicture": 0,
        "tikzcd": 14,
        "declared_editorials": [item[0] for item in EDITORIALS],
    }
    if evidence.get("structure") != expected_structure:
        refuse("structured source/target closure drift")
    if evidence.get("provenance_model") != MODEL:
        refuse("model provenance drift")
    expected_rights = {
        "principal_text_and_translation": "CC BY 4.0",
        "AJbook_class_fragment": "CC BY-SA 3.0",
        "bundled_noto_fonts": "SIL OFL 1.1",
        "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
    }
    if evidence.get("rights") != expected_rights:
        refuse("component-rights evidence drift")

    artifact = evidence.get("artifact", {})
    try:
        artifact_id = (int(artifact["bytes"]), str(artifact["sha256"]))
        page_count = int(evidence["pdf"]["pages"])
    except (KeyError, TypeError, ValueError) as exc:
        refuse(f"malformed artifact/page evidence: {exc}")
    if artifact.get("path") != ARTIFACT or page_count < 1:
        refuse("artifact path/page drift")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_id[1]):
        refuse("malformed artifact hash")
    require_identity(ARTIFACT, artifact_id)

    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        refuse("final build-log identity drift")
    for key, relative in (
        ("evidence_generator", EVIDENCE_GENERATOR),
        ("render_inventory", RENDER_INVENTORY),
    ):
        if evidence.get(key) != {
            "path": relative,
            "bytes": identity(relative)[0],
            "sha256": identity(relative)[1],
        }:
            refuse(f"{key} binding drift")

    visual = evidence.get("visual_qa", {})
    if (
        visual.get("status") != "PASS"
        or visual.get("pages_inspected") != list(range(1, page_count + 1))
        or visual.get("renderers_inspected")
        != ["Poppler", "MuPDF (mutool and PyMuPDF)"]
    ):
        refuse("all-page visual evidence drift")
    if (
        renders.get("unit_id") != "O013-LI-U023"
        or renders.get("status") != "PASS"
        or renders.get("page_count") != page_count
        or renders.get("provenance_model") != MODEL
    ):
        refuse("render-inventory unit/page drift")

    replay = evidence.get("deterministic_replay", {})
    mismatches = replay.get("same_renderer_page_mismatches", {})
    if (
        replay.get("semantic_and_render_identity") is not True
        or mismatches.get("poppler") != 0
        or mismatches.get("mupdf") != 0
        or replay.get("render_count") != page_count * 8
        or replay.get("contact_sheet_count") != 8
    ):
        refuse("deterministic semantic replay drift")

    comparisons = renders.get("comparisons", {})
    if len(comparisons) != 6 or not all(
        item.get("page_count_equal") is True
        and item.get("raw_pixel_identical") is True
        and item.get("png_byte_identical") is True
        and item.get("mismatching_raw_pages") == []
        and item.get("mismatching_png_pages") == []
        for item in comparisons.values()
    ):
        refuse("deterministic raster replay drift")
    if renders.get("render_count") != page_count * 8 or renders.get("contact_sheet_count") != 8:
        refuse("render/contact-sheet census drift")
    for renderer in ("poppler", "mupdf"):
        pages = renders.get("renderers", {}).get(renderer, [])
        if (
            [item.get("page") for item in pages] != list(range(1, page_count + 1))
            or not all(item.get("outer_3px_ink") == 0 for item in pages)
            or not all(re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256"))) for item in pages)
            or not all(re.fullmatch(r"[0-9a-f]{64}", str(item.get("raw_rgb_sha256"))) for item in pages)
        ):
            refuse(f"{renderer} render inventory drift")
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
            refuse(f"nonzero build blocker {key}")
    required_checks = {
        "canonical_target_full_identity",
        "canonical_span_equals_candidate",
        "boundary_next_section",
        "candidate_checker",
        "artifact_equals_final_b",
        "page_count",
        "semantic_replay",
        "render_replay",
        "pdf_safety",
        "navigation",
        "accessibility_baseline",
        "fonts",
        "text_tokens",
        "log",
        "page_edges",
        "structure",
    }
    if set(evidence.get("checks", {})) != required_checks or not all(
        evidence["checks"].values()
    ):
        refuse("structured PASS-check inventory drift")
    return page_count, artifact_id, log_id


def gate() -> tuple[
    int,
    tuple[int, str],
    tuple[int, str],
    tuple[dict[str, str], ...],
]:
    required = (
        TEMPLATE.relative_to(ROOT).as_posix(),
        CANDIDATE,
        DRIVER,
        COVER,
        CROSSREF,
        BIBLIOGRAPHY,
        BUILD_SCRIPT,
        STRUCTURE_GATE,
        EVIDENCE_GENERATOR,
        RENDER_INVENTORY,
        STRUCTURE_QA,
        REVIEW,
        MATH_REVIEW,
        VISUAL_REVIEW,
        TERMINOLOGY,
        TERMINOLOGY_AUDIT,
        FINAL_LOG,
        ARTIFACT,
    )
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    if missing:
        refuse(
            "scaffold is complete but final inputs are missing:\n  - "
            + "\n  - ".join(missing)
        )

    require_identity(SOURCE, SOURCE_FULL)
    require_identity(CANDIDATE, CANDIDATE_FULL)
    require_identity(TARGET, TARGET_FULL)
    require_identity(STRUCTURE_GATE, STRUCTURE_GATE_ID)
    require_identity(REVIEW, REVIEW_ID)
    require_identity(MATH_REVIEW, MATH_REVIEW_ID)
    require_identity(TERMINOLOGY, TERMINOLOGY_ID)
    require_identity(TERMINOLOGY_AUDIT, TERMINOLOGY_AUDIT_ID)

    source_span = normalized_span(SOURCE, SOURCE_START, SOURCE_END)
    target_span = normalized_span(TARGET, TARGET_START, TARGET_END)
    if (len(source_span), digest(source_span)) != SOURCE_SPAN:
        refuse("source span drift")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    target_lines = (ROOT / TARGET).read_text(encoding="utf-8").splitlines()
    if (
        len(source_lines) != 911
        or len(target_lines) != 910
        or source_lines[871].strip() != ""
        or target_lines[870].strip() != ""
        or source_lines[872] != target_lines[871]
        or digest((source_lines[872] + "\n").encode("utf-8")) != NEXT_LINE_SHA256
    ):
        refuse("next-section boundary is not preserved")
    source_suffix = ("\n".join(source_lines[872:]) + "\n").encode("utf-8")
    target_suffix = ("\n".join(target_lines[871:]) + "\n").encode("utf-8")
    if source_suffix != target_suffix:
        refuse("post-Unit-023 canonical remainder differs from authority")

    check = subprocess.run(
        [sys.executable, "-B", str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        refuse("structure checker failed\n" + check.stdout + check.stderr)
    for needle in (
        "PASS Unit 023",
        SOURCE_SPAN[1],
        TARGET_SPAN[1],
        TARGET_FULL[1],
        *(item[0] for item in EDITORIALS),
    ):
        if needle not in check.stdout:
            refuse(f"structure-check output lacks {needle!r}")

    source_text = source_span.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_environments = environment_occurrences(source_text)
    target_environments = environment_occurrences(target_text)
    if (
        len(source_environments) != 25
        or source_environments != target_environments
    ):
        refuse("twenty-five-environment occurrence topology drift")
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    if tuple(label for label, _ in source_labels) != LABELS or source_labels != target_labels:
        refuse("two-label topology drift")
    if reference_occurrences(source_text) != REFERENCES or reference_occurrences(target_text) != REFERENCES:
        refuse("sixteen-reference topology drift")
    if citation_occurrences(source_text) != CITATIONS or citation_occurrences(target_text) != CITATIONS:
        refuse("zero-citation topology drift")
    if occurrence_lines(source_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        refuse("unexpected source list item")
    if occurrence_lines(target_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        refuse("unexpected target list item")

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    if tuple((item[0], item[2]) for item in source_indexes) != tuple(
        (item[1], item[2]) for item in INDEX_SPECS
    ):
        refuse("source index topology drift")
    if tuple((item[0], item[2], item[1]) for item in target_indexes) != tuple(
        (item[1], item[2], item[3]) for item in INDEX_SPECS
    ):
        refuse("localized index topology drift")
    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    if source_diagrams != DIAGRAM_SPECS or target_diagrams != DIAGRAM_SPECS:
        refuse("fourteen-diagram topology drift")

    for kind, pattern, expected, _, _ in SURFACE_SPECS:
        source_occurrences = occurrence_lines(source_text, pattern)
        target_occurrences = occurrence_lines(target_text, pattern)
        if source_occurrences != target_occurrences or len(source_occurrences) != expected:
            refuse(f"{expected}-{kind} topology drift")

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    if len(source_inline) != 156 or len(target_inline) != 156:
        refuse("156-inline-formula topology drift")
    source_by_line: dict[int, list[str]] = defaultdict(list)
    target_by_line: dict[int, list[str]] = defaultdict(list)
    for _, line, formula in source_inline:
        source_by_line[line].append(localized_math(formula, repair_source=True))
    for _, line, formula in target_inline:
        target_by_line[line].append(localized_math(formula))
    if source_by_line.keys() != target_by_line.keys():
        refuse("inline formula line topology drift")
    reorder_lines = []
    for line in source_by_line:
        if Counter(source_by_line[line]) != Counter(target_by_line[line]):
            refuse(f"inline formula drift at relative line {line}")
        if source_by_line[line] != target_by_line[line]:
            reorder_lines.append(line)
    if tuple(reorder_lines) != ():
        refuse(f"reviewed formula reorder topology drift: {reorder_lines}")
    inline_pairs = pair_inline_formula_occurrences(source_inline, target_inline)
    if len(inline_pairs) != 156:
        refuse("inline pairing census drift")

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    if (
        len(source_brackets) != 11
        or len(target_brackets) != 11
        or tuple(item[:3] for item in source_brackets)
        != tuple(item[:3] for item in target_brackets)
        or tuple(localized_math(item[3], repair_source=True) for item in source_brackets)
        != tuple(localized_math(item[3]) for item in target_brackets)
    ):
        refuse("eleven bracket-display formula topology drift")
    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    if (
        len(source_env) != 0
        or len(target_env) != 0
        or tuple(item[:4] for item in source_env) != tuple(item[:4] for item in target_env)
        or tuple(localized_math(item[4], repair_source=True) for item in source_env)
        != tuple(localized_math(item[4]) for item in target_env)
    ):
        refuse("environment-display formula topology drift")

    external_refs = {label for _, label, _ in REFERENCES if label not in LABELS}
    crossref_text = (ROOT / CROSSREF).read_text(encoding="utf-8")
    crossref_labels = set(re.findall(r"\\newlabel\{([^{}]+)\}", crossref_text))
    if not external_refs.issubset(crossref_labels):
        refuse(
            "unresolved frozen crossrefs: "
            + ", ".join(sorted(external_refs - crossref_labels))
        )
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\InputSourceLineRange{chapter3.tex}{722}{871}",
        r"\setstretch{1.16}",
        MODEL,
    ):
        if needle not in driver:
            refuse(f"driver lacks {needle!r}")
    if "unit-023-candidate" in driver or Path(CANDIDATE).name in driver:
        refuse("public reader driver still depends on the isolated build candidate")
    bibliography = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8", errors="replace")
    del bibliography

    terminology_rows = read_terminology_rows()
    page_count, artifact_id, log_id = gate_structured_evidence()
    if pdfinfo_page_count() != page_count:
        refuse("live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+)\s+pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != page_count:
        refuse("final log page count drift")

    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    math_review = (ROOT / MATH_REVIEW).read_text(encoding="utf-8")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for needle in ("PASS", "723–872", TARGET_SPAN[1], MODEL, *(item[0] for item in EDITORIALS)):
        if needle not in review:
            refuse(f"source review lacks {needle!r}")
    for needle in (
        "PASS",
        "25 balanced environment pairs",
        "156 dollar-delimited inline formula",
        "All 14 diagrams",
        "64 `\\arrow`",
        *(item[0] for item in EDITORIALS),
    ):
        if needle not in math_review:
            refuse(f"math review lacks {needle!r}")
    for source_term, target_term in TERMINOLOGY_SPECS:
        if source_term not in terminology_audit or target_term not in terminology_audit:
            refuse(f"terminology audit lacks {source_term!r} / {target_term!r}")
    for needle in ("PASS", str(page_count), "Poppler", "MuPDF", artifact_id[1]):
        if needle not in visual_review:
            refuse(f"visual review lacks {needle!r}")
    return page_count, artifact_id, log_id, terminology_rows


def main() -> None:
    page_count, artifact_id, log_id, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-3-sekilas-tentang-2-kategori"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/sekilas-tentang-2-kategori"
    section_id = uid(section_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_absolute = lambda line: SOURCE_START + line - 1
    target_absolute = lambda line: TARGET_START + line - 1

    core_specs = (
        ("concept/higher-category", "高阶范畴", "kategori tingkat lebih tinggi"),
        ("concept/zero-category", "0-范畴", "0-kategori"),
        ("concept/one-category", "1-范畴", "1-kategori"),
        ("concept/two-category", "2-范畴", "2-kategori"),
        ("concept/strict-two-category", "严格 2-范畴", "2-kategori ketat"),
        ("concept/zero-morphism", "0-态射", "0-morfisme"),
        ("concept/one-morphism", "1-态射", "1-morfisme"),
        ("concept/two-morphism", "2-态射", "2-morfisme"),
        ("concept/two-cell", "2-胞腔", "2-sel"),
        ("concept/vertical-composition", "纵合成", "komposisi vertikal"),
        ("concept/horizontal-composition", "横合成", "komposisi horizontal"),
        ("concept/horizontal-identity", "横恒等", "identitas horizontal"),
        ("concept/vertical-identity", "纵恒等", "identitas vertikal"),
        ("concept/interchange-law", "交换律", "hukum pertukaran"),
        ("concept/bicategory", "双范畴", "bikategori"),
        ("concept/coherence-theorem", "融贯定理", "teorema koherensi"),
        ("concept/cat-two-category", "2-范畴 Cat", "2-kategori Cat"),
        ("concept/cartesian-monoidal-structure", "笛卡尔幺半结构", "struktur monoidal Kartesius"),
        ("concept/vertical-category", "纵范畴", "kategori vertikal"),
        ("concept/functor-category", "函子范畴", "kategori fungtor"),
        ("concept/cat-enriched-category", "Cat-充实范畴", "kategori yang diperkaya atas Cat"),
        ("concept/two-functor", "2-函子", "2-fungtor"),
        ("concept/two-natural-transformation", "2-自然变换", "2-transformasi natural"),
        ("concept/diagrammatic-convention", "图示约定", "konvensi diagramatik"),
        ("concept/adjunction-in-two-category", "2-范畴中的伴随对", "pasangan adjoin dalam 2-kategori"),
        ("concept/adjunction-unit", "伴随单位", "unit adjoin"),
        ("concept/adjunction-counit", "伴随余单位", "kounit adjoin"),
        ("concept/triangle-identities", "三角等式", "identitas segitiga"),
        ("concept/adjoint-equivalence", "伴随等价", "ekuivalensi adjoin"),
    )
    concepts = [surface_concept(uid, *spec) for spec in core_specs]

    for ordinal, (source_item, target_item) in enumerate(
        zip(
            environment_occurrences(source_text),
            environment_occurrences(target_text),
            strict=True,
        ),
        1,
    ):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        environment_slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/environment/{ordinal:03d}-{environment_slug}-{occurrence:02d}",
                f"环境 {ordinal:03d}: {environment} 第 {occurrence} 次; "
                f"源行 {source_absolute(source_first)}-{source_absolute(source_last)}",
                f"lingkungan {ordinal:03d}: {environment} kemunculan {occurrence}; "
                f"baris target {target_absolute(target_first)}-{target_absolute(target_last)}",
            )
        )

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
                f"surface/unit-023/label/{ordinal:03d}",
                f"TeX 标签 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}",
                f"label TeX {ordinal:03d}: {label}; baris target {target_absolute(target_line)}",
            )
        )

    for ordinal, (source_item, target_item) in enumerate(
        zip(reference_occurrences(source_text), reference_occurrences(target_text), strict=True),
        1,
    ):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/reference/{kind}/{ordinal:03d}",
                f"引用 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}",
                f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_absolute(target_line)}",
            )
        )

    for ordinal, (locator, bib_key, line) in enumerate(CITATIONS, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/citation-occurrence/{ordinal:03d}",
                f"引文出现 {ordinal:03d}: {bib_key}; {locator or '无定位符'}; 源行 {source_absolute(line)}",
                f"kemunculan sitasi {ordinal:03d}: {bib_key}; {locator or 'tanpa lokator'}; baris target {target_absolute(line)}",
            )
        )

    for ordinal, line in enumerate(ITEM_LINES, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/item/{ordinal:03d}",
                f"列表项 {ordinal:03d}; 源行 {source_absolute(line)}",
                f"butir daftar {ordinal:03d}; baris target {target_absolute(line)}",
            )
        )

    inline_pairs = pair_inline_formula_occurrences(
        inline_formula_occurrences(source_text), inline_formula_occurrences(target_text)
    )
    for source_item, target_item in inline_pairs:
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/formula/inline/{ordinal:03d}",
                f"行内公式 {ordinal:03d}; 源行 {source_absolute(source_line)}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus sebaris {ordinal:03d}; baris target {target_absolute(target_line)}; SHA-256 {digest(target_formula.encode('utf-8'))}",
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
                f"surface/unit-023/formula/display-bracket/{ordinal:03d}",
                f"陈列公式 {ordinal:03d}; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus pajang {ordinal:03d}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )

    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_env, target_env, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/formula/display-environment/{ordinal:03d}",
                f"{environment} 公式 {ordinal:03d}; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}; SHA-256 {digest(source_formula.encode('utf-8'))}",
                f"rumus {environment} {ordinal:03d}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            )
        )

    for kind, pattern, _, source_name, target_name in SURFACE_SPECS:
        source_lines = occurrence_lines(source_text, pattern)
        target_lines = occurrence_lines(target_text, pattern)
        for ordinal, (source_line, target_line) in enumerate(
            zip(source_lines, target_lines, strict=True), 1
        ):
            concepts.append(
                surface_concept(
                    uid,
                    f"surface/unit-023/diagram-{kind}/{ordinal:03d}",
                    f"{source_name} {ordinal:03d}; 源行 {source_absolute(source_line)}",
                    f"{target_name} {ordinal:03d}; baris target {target_absolute(target_line)}",
                )
            )

    for editorial_id, source_line, target_line, issue in EDITORIALS:
        concepts.append(
            surface_concept(
                uid,
                f"editorial/{editorial_id.casefold()}",
                f"声明的编辑规范化 {editorial_id}; 源行 {source_line}",
                f"normalisasi editorial terdeklarasi {editorial_id}; baris sumber {source_line}; "
                f"baris target {target_line}; {issue} Bukti: {REVIEW}.",
            )
        )

    for ordinal, row in enumerate(terminology_rows, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-023/terminology-row/{ordinal:03d}",
                f"术语记录 {ordinal:03d}: {row['source_term']}",
                f"baris terminologi {ordinal:03d}: {row['source_term']} -> {row['target_term']}; "
                f"status admitted; scope {row['scope']}",
            )
        )

    concept_ids = [item["id"] for item in concepts]
    selected_prerequisite_keys = {
        "prerequisite/elementary-set-theory",
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
        "prerequisite/universal-properties-and-comma-categories",
        "prerequisite/point-set-topology",
    }
    prerequisite_ids = [
        item["id"]
        for item in data["prerequisites"]
        if item["stable_key"] in selected_prerequisite_keys
    ]
    if len(prerequisite_ids) != len(selected_prerequisite_keys):
        refuse("prerequisite inventory drift")

    rights_by_key = {item["stable_key"]: item for item in data["rights"]}
    if set(rights_by_key) != {
        "rights/principal-cc-by-4.0",
        "rights/lanzhou-cc-by-sa-3.0",
        "rights/ajbook-fragment-cc-by-sa-3.0",
        "rights/noto-fonts-ofl-1.1",
    }:
        refuse("rights-component inventory drift")
    rights_by_key["rights/principal-cc-by-4.0"]["bindings"] = [
        source_binding(SOURCE),
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

    titles = [
        {"language": "zh-Hans", "text": "第三章：幺半范畴；2-范畴一瞥"},
        {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Sekilas tentang 2-Kategori"},
    ]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter3.tex:723-872",
        "titles": titles,
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END),
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    bibliography_hash = identity(BIBLIOGRAPHY)[1]
    citations = []
    seen_bib_keys: set[str] = set()
    for _, bib_key, line in CITATIONS:
        if bib_key in seen_bib_keys:
            continue
        seen_bib_keys.add(bib_key)
        key = f"citation/unit-023/{bib_key.casefold()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": bib_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": bibliography_hash,
                "source_line": source_absolute(line),
                "target_line": target_absolute(line),
                "section_id": section_id,
            }
        )

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (spec, source_index, target_index) in enumerate(
        zip(INDEX_SPECS, source_indexes, target_indexes, strict=True), 1
    ):
        slug, _, _, _ = spec
        key = f"index-entry/unit-023/{slug}"
        index_entries.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "index_entry",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_key": source_index[1],
                "target_key": target_index[1],
                "source_binding": source_binding(
                    SOURCE,
                    source_absolute(source_index[2]),
                    source_absolute(source_index[2]),
                ),
                "target_binding": target_binding(
                    target_absolute(target_index[2]), target_absolute(target_index[2])
                ),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(
        zip(source_diagrams, target_diagrams, strict=True), 1
    ):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-023/{source_format}-{occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": occurrence,
                "source_binding": source_binding(
                    SOURCE,
                    source_absolute(source_first),
                    source_absolute(source_last),
                ),
                "target_binding": target_binding(
                    target_absolute(target_first), target_absolute(target_last)
                ),
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
        "id": uid("build-surface/unit-023-pdf"),
        "stable_key": "build-surface/unit-023-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_023.ps1 -OutputDirectory build/unit-023-replay",
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
            "PowerShell 7",
            "biber",
            "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "TikZ and tikz-cd",
            "packages loaded by the Unit 023 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    formula_total = len(inline_pairs) + len(source_brackets) + len(source_env)
    qa_admission = {
        "id": uid("qa/unit-023/admission-gate"),
        "stable_key": "qa/unit-023/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and all-page admission of chapter3.tex authority lines "
            "723-872 to target lines 722-871: two labels, sixteen ordinary references, no equation "
            "references, no citation occurrences, nineteen list items, twenty-five environment pairs, "
            "fourteen tikzcd structures and no tikzpicture structures, sixty-four tikzcd arrows, no TikZ "
            "nodes, draws, paths, edges, coordinates, braids, or hlines, 156 inline plus eleven "
            f"bracket-display and zero environment-display formula surfaces ({formula_total} total), and "
            "three localized index entries. O013-LI-U023-ED-001 preserves the adjunction sort key while "
            "adding only a readable Indonesian display payload; no mathematical source correction occurs. "
            "Exactly twenty applicable terminology rows are bound: seventeen new Unit 023 records and "
            "three previously admitted records, with evidentiary limits intact. "
            "Component rights remain CC BY 4.0 for principal text/translation, CC BY-SA 3.0 for the AJbook "
            "fragment, and OFL 1.1 for bundled fonts. Production provenance is "
            f"{MODEL}, separate from Wen-Wei Li's authorship and human credit."
        ),
        "witness": STRUCTURE_QA,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(STRUCTURE_QA),
    }
    qa_source = {
        "id": uid("qa/unit-023/source-review"),
        "stable_key": "qa/unit-023/source-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent translation/source review of the exact authority and target spans, including terminology, formulas, references, indexes, diagrams, and the disclosed index-only editorial normalization.",
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(REVIEW),
    }
    qa_math = {
        "id": uid("qa/unit-023/math-structure-review"),
        "stable_key": "qa/unit-023/math-structure-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent mathematical/protected-topology audit of every formula, identifier, reference, list item, index, diagram primitive, and the sole declared editorial normalization.",
        "witness": MATH_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(MATH_REVIEW),
    }
    qa_editorial = {
        "id": uid("qa/unit-023/editorial-normalization"),
        "stable_key": "qa/unit-023/editorial-normalization",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Separate deterministic provenance for O013-LI-U023-ED-001, the index-only learner-display normalization from raw romanized sort key to pasangan adjoin.",
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(REVIEW),
    }
    qa_structure = {
        "id": uid("qa/unit-023/structure-check"),
        "stable_key": "qa/unit-023/structure-check",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Fail-closed machine structure check binds source/candidate/canonical identities, next-exercise boundary, all protected surfaces, the sole declared editorial normalization, and zero Han residue.",
        "witness": STRUCTURE_GATE,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(STRUCTURE_GATE),
    }
    qa_replay = {
        "id": uid("qa/unit-023/render-replay"),
        "stable_key": "qa/unit-023/render-replay",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Deterministic extracted-text and same-renderer Poppler/MuPDF replay, with all pages visually inspected.",
        "witness": RENDER_INVENTORY,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(RENDER_INVENTORY),
    }
    qa_visual = {
        "id": uid("qa/unit-023/all-page-visual-review"),
        "stable_key": "qa/unit-023/all-page-visual-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent all-page visual review of the final reader in Poppler and MuPDF after final reflow.",
        "witness": VISUAL_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(VISUAL_REVIEW),
    }
    qa_terms = {
        "id": uid("qa/unit-023/terminology-control"),
        "stable_key": "qa/unit-023/terminology-control",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live id-ID glossary binding for exactly twenty applicable admitted Unit 023 terminology rows: seventeen new records and three reused category-theory records.",
        "witness": TERMINOLOGY,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY),
    }
    qa_term_evidence = {
        "id": uid("qa/unit-023/terminology-evidence"),
        "stable_key": "qa/unit-023/terminology-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Bound terminology adjudication compares Indonesian higher-category usage for 2-kategori, morphism/cell levels, vertical and horizontal composition, bicategory, 2-functor, 2-natural transformation, and related weak structures without overclaiming uniform usage.",
        "witness": TERMINOLOGY_AUDIT,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY_AUDIT),
    }

    data["dataset_stable_key"] = "dataset/unit-023/id-id"
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
        "order": 23,
        "source_local_id": "chapter3.tex:723-872",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END),
        "section_ids": [section_id],
        "concept_ids": concept_ids,
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [
            qa_admission["id"],
            qa_source["id"],
            qa_math["id"],
            qa_editorial["id"],
            qa_structure["id"],
            qa_replay["id"],
            qa_visual["id"],
            qa_terms["id"],
            qa_term_evidence["id"],
        ],
        "outcome_keys": [
            "outcome/define-strict-two-categories-by-zero-one-two-morphisms",
            "outcome/compose-two-cells-vertically-and-horizontally",
            "outcome/apply-the-interchange-law-and-identity-axioms",
            "outcome/identify-cat-as-a-two-category-and-cartesian-monoidal-category",
            "outcome/reformulate-two-categories-as-cat-enriched-categories",
            "outcome/interpret-two-functors-two-natural-transformations-and-adjunctions",
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
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = [
        qa_admission,
        qa_source,
        qa_math,
        qa_editorial,
        qa_structure,
        qa_replay,
        qa_visual,
        qa_terms,
        qa_term_evidence,
    ]

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
                "concepts": len(concepts),
                "environments": 25,
                "labels": 2,
                "ordinary_references": 16,
                "equation_references": 0,
                "citation_occurrences": 0,
                "native_bibliography_records": len(citations),
                "items": 19,
                "formula_entities": formula_total,
                "diagrams": len(diagrams),
                "arrows": 64,
                "nodes": 0,
                "coordinates": 0,
                "draws": 0,
                "paths": 0,
                "edges": 0,
                "braids": 0,
                "hlines": 0,
                "index_entries": 3,
                "editorials": 1,
                "terminology_rows": 20,
                "artifact": {
                    "pages": page_count,
                    "bytes": artifact_id[0],
                    "sha256": artifact_id[1],
                },
                "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
                "csv_projections": [
                    path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
