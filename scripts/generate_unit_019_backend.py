#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 019.

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
TEMPLATE = ROOT / "backend/data/unit-018-bab-2-latihan.json"
OUTPUT = ROOT / "backend/data/unit-019-bab-3-definisi-dasar.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-019-bab-3-definisi-dasar.tex"
COVER = "repo/source/coverpage-id-unit-019.tex"
CROSSREF = "repo/source/unit-019-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_019.ps1"
STRUCTURE_GATE = "scripts/check_unit_019_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_019_evidence.py"
SUMMARY = "qa/unit-019-evidence/build-log-summary.txt"
RENDER_INVENTORY = "qa/unit-019-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-019-evidence/structure-and-pdf-qa.json"
STRUCTURE_OUTPUT = "qa/unit-019-evidence/structure-check.txt"
REVIEW = "qa/UNIT_019_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_019_MATH_STRUCTURE_AUDIT_20260824.md"
VISUAL_REVIEW = "qa/UNIT_019_VISUAL_QA_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_QA_CATEGORY = "qa/TERMINOLOGY_QA_INDONESIAN_CATEGORY_ALGEBRA_20260822.md"
TERMINOLOGY_QA_GRADUATE = "qa/TERMINOLOGY_QA_INDONESIAN_GRADUATE_ALGEBRA_20260824.md"
FINAL_LOG = "qa/UNIT_019_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-019-bab-3-definisi-dasar.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
SOURCE_START, SOURCE_END = 1, 227
TARGET_START, TARGET_END = 1, 226
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    21_745,
    "4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a",
)
TARGET_SPAN = (
    25_868,
    "6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac",
)
CORRECTIONS = (
    (
        "O013-LI-U019-COR-001",
        155,
        "The authority's lower-right Kelly-diagram node uses the undefined literal 1; "
        "the target restores the monoidal unit macro \\munit required by the associator.",
        "O013-ADV-0051",
    ),
)
LABELS = (
    "sec:monoidal-cat",
    "sec:monoidal-cat-def",
    "def:monoidal-cat",
    "def:monoidal-constraints",
    "eg:monoidal-cat",
    "eg:cob-cat",
    "prop:Kelly",
    "eqn:unit-coherence-2a",
    "eqn:unit-coherence-2b",
    "eqn:unit-coherence-2c",
    "eqn:monoidal-cat-unit",
    "eqn:unit-coherence-1",
    "eqn:unit-coherence-3",
    "eqn:coherence-aux0",
    "def:monoidal-functor",
    "eqn:monoidal-functor-units",
)
REFERENCES = (
    ("ordinary", "sec:module-tensor-prod", 12),
    ("ordinary", "sec:braiding", 13),
    ("ordinary", "sec:enriched-cat", 16),
    ("ordinary", "sec:2-cat", 16),
    ("ordinary", "sec:enriched-cat", 21),
    ("ordinary", "sec:modules", 23),
    ("ordinary", "rem:strict-or-not", 60),
    ("ordinary", "prop:product-associativity", 79),
    ("ordinary", "prop:module-monoidal-cat", 82),
    ("ordinary", "def:monoidal-cat", 106),
    ("ordinary", "def:monoidal-constraints", 106),
    ("ordinary", "def:monoidal-cat", 106),
    ("ordinary", "sec:coherence", 106),
    ("equation", "eqn:unit-coherence-2a", 136),
    ("equation", "eqn:unit-coherence-2b", 141),
    ("equation", "eqn:unit-coherence-2a", 149),
    ("equation", "eqn:monoidal-cat-unit", 149),
    ("equation", "eqn:monoidal-cat-unit", 149),
    ("equation", "eqn:unit-coherence-2c", 149),
    ("equation", "eqn:monoidal-cat-unit", 157),
    ("equation", "eqn:unit-coherence-1", 162),
    ("equation", "eqn:unit-coherence-1", 162),
    ("equation", "eqn:unit-coherence-3", 164),
    ("equation", "eqn:monoidal-cat-unit", 174),
    ("equation", "eqn:monoidal-functor-units", 210),
    ("equation", "eqn:monoidal-functor-units", 210),
    ("ordinary", "def:preservation-limit", 214),
    ("ordinary", "def:cat-equivalence", 226),
)
CITATIONS = (
    ("", "EGNO15", 18),
    (r"\S 2.1", "EGNO15", 29),
    ("", "ML98", 174),
    ("Proposition 2.4.3", "EGNO15", 198),
)
ITEM_LINES = (12, 13, 34, 35, 36, 53, 54, 65, 67, 79, 80, 81, 82)
INDEX_SPECS = (
    ("tensor-category", "main", 25, "zhangliangfanchou@kategori tensor (tensor category)"),
    ("monoidal-category", "main", 31, "yaobanfanchou@kategori monoidal (monoidal category)"),
    ("tensor-symbol", "sym1", 31, r"1otimes@$\otimes$"),
    ("unit-object", "main", 53, "objek!objek satuan (unit object)"),
    ("associativity-constraint", "main", 58, "jieheyueshu@kendala asosiativitas"),
    ("mac-lane-pentagon", "main", 58, "MacLane@aksioma segilima Mac Lane (pentagon axiom)"),
    (
        "monoidal-subcategory",
        "main",
        74,
        "yaobanfanchou@kategori monoidal (monoidal category)!subkategori monoidal (monoidal subcategory)",
    ),
    ("monoidal-functor", "main", 177, "yaobanhanzi@fungtor monoidal (monoidal functor)"),
    (
        "lax-monoidal-functors",
        "main",
        210,
        "yaobanhanzi@fungtor monoidal!longgar-kiri/longgar-kanan (left-lax/right-lax)",
    ),
    ("monoidal-natural-transformation", "main", 217, "ziranbianhuan@transformasi natural!kasus monoidal"),
    ("monoidal-equivalence", "main", 226, "fanchoudengjia@ekuivalensi kategori!kasus monoidal"),
)
DIAGRAM_SPECS = (
    ("tikzpicture", 1, 39, 52),
    ("tikzpicture", 2, 89, 93),
    ("tikzpicture", 3, 96, 100),
    ("tikzcd", 1, 116, 119),
    ("tikzcd", 2, 121, 124),
    ("tikzcd", 3, 125, 128),
    ("tikzcd", 4, 130, 133),
    ("tikzcd", 5, 137, 140),
    ("tikzcd", 6, 144, 148),
    ("tikzcd", 7, 152, 156),
    ("tikzcd", 8, 158, 161),
    ("tikzcd", 9, 165, 169),
    ("tikzcd", 10, 181, 185),
    ("tikzcd", 11, 190, 193),
    ("tikzcd", 12, 194, 197),
    ("tikzcd", 13, 199, 202),
    ("tikzcd", 14, 203, 206),
    ("tikzcd", 15, 219, 222),
)
TERMINOLOGY_SPECS = (
    ("unit object", "objek satuan"),
    ("unit constraint", "kendala satuan"),
    ("pentagon axiom", "aksioma segilima Mac Lane"),
    ("triangle axiom (monoidal category)", "aksioma segitiga kategori monoidal"),
    ("monoidal subcategory", "subkategori monoidal"),
    ("braid category", "kategori kepang"),
    ("enriched category", "kategori diperkaya"),
    ("additive category", "kategori aditif"),
    ("biproduct", "biproduk"),
    ("monoidal functor", "fungtor monoidal"),
    ("strong monoidal functor", "fungtor monoidal kuat"),
    ("right-lax monoidal functor", "fungtor monoidal longgar-kanan"),
    ("left-lax monoidal functor", "fungtor monoidal longgar-kiri"),
    ("monoidal equivalence", "ekuivalensi monoidal"),
    ("tensor category", "kategori tensor"),
)
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-019-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 019 backend refused: identity drift for {relative}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    lines = (ROOT / relative).read_bytes().decode("utf-8").splitlines()
    if len(lines) < last:
        raise SystemExit(
            f"Unit 019 backend refused: {relative} has {len(lines)} lines; "
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
        raise SystemExit("Unit 019 backend refused: unpaired inline-math delimiter")
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
                "Unit 019 backend refused: ambiguous localized inline formula at "
                f"line {source_items[source_index][1]}"
            )
        chosen = candidates[0]
        unused.remove(chosen)
        pairs[source_index] = chosen
    if unused:
        raise SystemExit("Unit 019 backend refused: unpaired target inline formulae")
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
                f"Unit 019 backend refused: terminology row {source_term!r} is not unique"
            )
        row = matches[0]
        if row.get("target_term") != target_term:
            raise SystemExit(
                f"Unit 019 backend refused: terminology target drift for {source_term!r}"
            )
        if row.get("status") != "admitted":
            raise SystemExit(
                "Unit 019 backend scaffold is ready but terminology admission is pending: "
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
        raise SystemExit("Unit 019 backend refused: pdfinfo failed\n" + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 019 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def exact_target_admission_identity(evidence: dict[str, object]) -> tuple[int, str]:
    target = evidence.get("target", {})
    if not isinstance(target, dict):
        raise SystemExit("Unit 019 backend refused: malformed structured target evidence")
    reported_bytes = target.get("target_file_bytes")
    reported_hash = target.get("target_file_sha256")
    if reported_bytes is not None or reported_hash is not None:
        try:
            candidate = (int(reported_bytes), str(reported_hash))
        except (TypeError, ValueError) as exc:
            raise SystemExit("Unit 019 backend refused: malformed target-file identity") from exc
        if not re.fullmatch(r"[0-9a-f]{64}", candidate[1]):
            raise SystemExit("Unit 019 backend refused: malformed target-file hash")
    elif OUTPUT.is_file():
        prior = json.loads(OUTPUT.read_text(encoding="utf-8"))["unit"]["target_binding"]
        candidate = (int(prior["bytes"]), str(prior["sha256"]))
    else:
        candidate = identity(TARGET)
    if not OUTPUT.is_file() and identity(TARGET) != candidate:
        raise SystemExit("Unit 019 backend refused: admission-time target identity is not live")
    return candidate


def gate_structured_evidence() -> tuple[int, tuple[int, str], tuple[int, str], tuple[int, str]]:
    try:
        evidence = json.loads((ROOT / STRUCTURE_QA).read_text(encoding="utf-8"))
        renders = json.loads((ROOT / RENDER_INVENTORY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Unit 019 backend refused: unreadable structured evidence: {exc}") from exc
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U019":
        raise SystemExit("Unit 019 backend refused: structured QA status/unit drift")
    if evidence.get("authority") != {
        "commit": "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
        "tree": "0f9fd52748165ec89a85ba602ccb949a2ce04694",
        "source_file": "chapter3.tex",
        "source_lines": "1-227",
        "source_span_bytes": SOURCE_SPAN[0],
        "source_span_sha256": SOURCE_SPAN[1],
    }:
        raise SystemExit("Unit 019 backend refused: structured authority drift")
    target = evidence.get("target", {})
    if not isinstance(target, dict):
        raise SystemExit("Unit 019 backend refused: malformed structured target evidence")
    required_target = {
        "target_span_bytes": TARGET_SPAN[0],
        "target_span_sha256": TARGET_SPAN[1],
        "han_residue": 0,
    }
    if any(target.get(key) != value for key, value in required_target.items()):
        raise SystemExit("Unit 019 backend refused: structured target span drift")
    if "target_lines" in target and target["target_lines"] != "1-226":
        raise SystemExit("Unit 019 backend refused: structured target line range drift")
    if "correction_ids" in target and target["correction_ids"] != [CORRECTIONS[0][0]]:
        raise SystemExit("Unit 019 backend refused: structured correction inventory drift")
    target_admission_id = exact_target_admission_identity(evidence)
    expected_structure = {
        "authority_file": {"bytes": SOURCE_FULL[0], "sha256": SOURCE_FULL[1]},
        "authority_span": {"bytes": SOURCE_SPAN[0], "sha256": SOURCE_SPAN[1]},
        "target_file_at_admission": {
            "bytes": target_admission_id[0],
            "sha256": target_admission_id[1],
        },
        "target_span": {"bytes": TARGET_SPAN[0], "sha256": TARGET_SPAN[1]},
        "target_lines": "1-226",
        "next_target_line": 227,
        "han_residue": 0,
        "external_reference_count": 11,
    }
    if evidence.get("structure") != expected_structure:
        raise SystemExit("Unit 019 backend refused: structured source/target closure drift")
    if evidence.get("provenance_model") != MODEL:
        raise SystemExit("Unit 019 backend refused: model provenance drift")
    expected_rights = {
        "principal_text_and_translation": "CC BY 4.0",
        "AJbook_class_fragment": "CC BY-SA 3.0",
        "bundled_noto_fonts": "SIL OFL 1.1",
        "Lanzhou_png_in_wider_closure": "CC BY-SA 3.0; not used by this reader",
    }
    if evidence.get("rights") != expected_rights:
        raise SystemExit("Unit 019 backend refused: component-rights evidence drift")
    artifact = evidence.get("artifact", {})
    try:
        artifact_id = (int(artifact["bytes"]), str(artifact["sha256"]))
        page_count = int(evidence["pdf"]["pages"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit("Unit 019 backend refused: malformed artifact/page evidence") from exc
    if artifact.get("path") != ARTIFACT or page_count < 1:
        raise SystemExit("Unit 019 backend refused: artifact path/page drift")
    if not re.fullmatch(r"[0-9a-f]{64}", artifact_id[1]):
        raise SystemExit("Unit 019 backend refused: malformed artifact hash")
    require_identity(ARTIFACT, artifact_id)
    log_id = identity(FINAL_LOG)
    if evidence.get("build_log") != {
        "path": FINAL_LOG,
        "bytes": log_id[0],
        "sha256": log_id[1],
    }:
        raise SystemExit("Unit 019 backend refused: final build-log identity drift")
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
            raise SystemExit(f"Unit 019 backend refused: {key} binding drift")
    visual = evidence.get("visual_qa", {})
    if (
        visual.get("status") != "PASS"
        or visual.get("pages_inspected") != list(range(1, page_count + 1))
        or visual.get("renderers_inspected") != ["Poppler", "MuPDF"]
    ):
        raise SystemExit("Unit 019 backend refused: all-page visual evidence drift")
    if renders.get("unit_id") != "O013-LI-U019" or renders.get("page_count") != page_count:
        raise SystemExit("Unit 019 backend refused: render-inventory unit/page drift")
    render_replay = renders.get("deterministic_replay", {})
    mismatches = render_replay.get("same_renderer_page_mismatches", {})
    if mismatches.get("poppler") != 0 or mismatches.get("mupdf") != 0:
        raise SystemExit("Unit 019 backend refused: deterministic raster replay drift")
    extracted_hashes = [
        value
        for key, value in render_replay.items()
        if key.startswith("extracted_text_sha256_")
    ]
    if len(extracted_hashes) < 2 or len(set(extracted_hashes)) != 1:
        raise SystemExit("Unit 019 backend refused: deterministic text replay drift")
    for renderer in ("poppler", "mupdf"):
        pages = renders.get("renderers", {}).get(renderer, [])
        if (
            [item.get("page") for item in pages] != list(range(1, page_count + 1))
            or not all(item.get("visually_inspected") is True for item in pages)
            or not all(item.get("matches_clean_build_a") is True for item in pages)
            or not all(item.get("matches_clean_build_b") is True for item in pages)
        ):
            raise SystemExit(f"Unit 019 backend refused: {renderer} render inventory drift")
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
            raise SystemExit(f"Unit 019 backend refused: nonzero build blocker {key}")
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
        VISUAL_REVIEW,
        TERMINOLOGY,
        TERMINOLOGY_QA_CATEGORY,
        TERMINOLOGY_QA_GRADUATE,
        FINAL_LOG,
        ARTIFACT,
    )
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(
            "Unit 019 backend scaffold is complete but final inputs are missing:\n  - "
            + "\n  - ".join(missing)
        )
    require_identity(SOURCE, SOURCE_FULL)
    if (len(normalized_span(SOURCE, SOURCE_START, SOURCE_END)), digest(normalized_span(SOURCE, SOURCE_START, SOURCE_END))) != SOURCE_SPAN:
        raise SystemExit("Unit 019 backend refused: source span drift")
    if (len(normalized_span(TARGET, TARGET_START, TARGET_END)), digest(normalized_span(TARGET, TARGET_START, TARGET_END))) != TARGET_SPAN:
        raise SystemExit("Unit 019 backend refused: target span drift")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    target_lines = (ROOT / TARGET).read_text(encoding="utf-8").splitlines()
    if len(source_lines) < 228 or len(target_lines) < 227 or source_lines[227] != target_lines[226]:
        raise SystemExit("Unit 019 backend refused: next-section boundary is not preserved")

    check = subprocess.run(
        [sys.executable, "-B", str(ROOT / STRUCTURE_GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 019 backend refused: structure checker failed\n" + check.stdout + check.stderr)
    for needle in ("PASS", "Unit 019", SOURCE_SPAN[1], TARGET_SPAN[1]):
        if needle not in check.stdout:
            raise SystemExit(f"Unit 019 backend refused: structure-check output lacks {needle!r}")

    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    if tuple(label for label, _ in source_labels) != LABELS or source_labels != target_labels:
        raise SystemExit("Unit 019 backend refused: sixteen-label topology drift")
    if reference_occurrences(source_text) != REFERENCES or reference_occurrences(target_text) != REFERENCES:
        raise SystemExit("Unit 019 backend refused: 28-reference topology drift")
    if citation_occurrences(source_text) != CITATIONS or citation_occurrences(target_text) != CITATIONS:
        raise SystemExit("Unit 019 backend refused: four-citation topology drift")
    if occurrence_lines(source_text, r"\\item(?![A-Za-z])") != ITEM_LINES or occurrence_lines(target_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        raise SystemExit("Unit 019 backend refused: thirteen-item topology drift")

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    if tuple((item[0], item[2]) for item in source_indexes) != tuple((item[1], item[2]) for item in INDEX_SPECS):
        raise SystemExit("Unit 019 backend refused: source index topology drift")
    if tuple((item[0], item[2], item[1]) for item in target_indexes) != tuple((item[1], item[2], item[3]) for item in INDEX_SPECS):
        raise SystemExit("Unit 019 backend refused: localized index topology drift")
    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    if source_diagrams != DIAGRAM_SPECS or target_diagrams != DIAGRAM_SPECS:
        raise SystemExit("Unit 019 backend refused: 18-diagram topology drift")

    surface_specs = (
        (r"\\arrow(?![A-Za-z])", 75, "arrow"),
        (r"\\node(?![A-Za-z])", 11, "node"),
        (r"\\path(?![A-Za-z])", 1, "path"),
    )
    for pattern, expected, name in surface_specs:
        source_occurrences = occurrence_lines(source_text, pattern)
        target_occurrences = occurrence_lines(target_text, pattern)
        if source_occurrences != target_occurrences or len(source_occurrences) != expected:
            raise SystemExit(f"Unit 019 backend refused: {expected}-{name} topology drift")

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    if len(source_inline) != 167 or len(target_inline) != 167:
        raise SystemExit("Unit 019 backend refused: 167-inline-formula topology drift")
    inline_pairs = pair_inline_formula_occurrences(source_inline, target_inline)
    inline_changes = tuple(
        (source_item[1], source_item[2], target_item[2])
        for source_item, target_item in inline_pairs
        if source_item[2] != target_item[2]
    )
    if len(inline_changes) != 1 or inline_changes[0][0] != 214 or r"\text{objek terminal}" not in inline_changes[0][2]:
        raise SystemExit("Unit 019 backend refused: undeclared inline-math localization drift")
    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    if len(source_brackets) != 9 or len(target_brackets) != 9 or tuple(item[:3] for item in source_brackets) != tuple(item[:3] for item in target_brackets):
        raise SystemExit("Unit 019 backend refused: nine-display-bracket topology drift")
    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    if len(source_env) != 8 or len(target_env) != 8 or tuple(item[:4] for item in source_env) != tuple(item[:4] for item in target_env):
        raise SystemExit("Unit 019 backend refused: eight-environment-formula topology drift")
    environment_changes = tuple(
        (source_item[2], source_item[4], target_item[4])
        for source_item, target_item in zip(source_env, target_env, strict=True)
        if canonical_formula(source_item[4]) != canonical_formula(target_item[4])
    )
    if len(environment_changes) != 1 or environment_changes[0][0] != 152 or r"(\munit \otimes X)" not in environment_changes[0][2]:
        raise SystemExit("Unit 019 backend refused: correction-surface drift")

    external_refs = {label for kind, label, _ in REFERENCES if label not in LABELS}
    crossref_text = (ROOT / CROSSREF).read_text(encoding="utf-8")
    crossref_labels = set(re.findall(r"\\newlabel\{([^{}]+)\}", crossref_text))
    if not external_refs.issubset(crossref_labels):
        raise SystemExit(
            "Unit 019 backend refused: unresolved frozen crossrefs: "
            + ", ".join(sorted(external_refs - crossref_labels))
        )
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    for needle in (
        r"\InputSourceLineRange{chapter3.tex}{1}{226}",
        r"\setstretch{1.2}",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ):
        if needle not in driver:
            raise SystemExit(f"Unit 019 backend refused: driver lacks {needle!r}")
    bibliography = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8", errors="replace")
    for bib_key in {item[1] for item in CITATIONS}:
        if not re.search(r"@[A-Za-z]+\s*\{\s*" + re.escape(bib_key) + r"\s*,", bibliography):
            raise SystemExit(f"Unit 019 backend refused: bibliography lacks {bib_key}")

    terminology_rows = read_terminology_rows()
    page_count, artifact_id, log_id, target_admission_id = gate_structured_evidence()
    if pdfinfo_page_count() != page_count:
        raise SystemExit("Unit 019 backend refused: live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(
        r"Output written on .*?\((\d+)\s+pages?\)\.", final_log, re.DOTALL
    )
    if not log_pages or int(log_pages[-1]) != page_count:
        raise SystemExit("Unit 019 backend refused: final log page count drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    for needle in ("PASS", "Unit 019", f"pages={page_count}", artifact_id[1], MODEL):
        if needle not in summary:
            raise SystemExit(f"Unit 019 backend refused: build summary lacks {needle!r}")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    math_review = (ROOT / MATH_REVIEW).read_text(encoding="utf-8")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for needle in ("Status: **PASS**", "chapter3.tex:1-227", TARGET_SPAN[1], MODEL, CORRECTIONS[0][0], "CC BY 4.0"):
        if needle not in review:
            raise SystemExit(f"Unit 019 backend refused: source review lacks {needle!r}")
    for needle in ("PASS", "16", "28", "75", CORRECTIONS[0][0]):
        if needle not in math_review:
            raise SystemExit(f"Unit 019 backend refused: math review lacks {needle!r}")
    for needle in ("PASS", str(page_count), "Poppler", "MuPDF", artifact_id[1]):
        if needle not in visual_review:
            raise SystemExit(f"Unit 019 backend refused: visual review lacks {needle!r}")
    return page_count, artifact_id, log_id, target_admission_id, terminology_rows


def main() -> None:
    page_count, artifact_id, log_id, target_admission_id, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-3-definisi-dasar"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/kategori-monoidal-dan-definisi-dasar"
    section_id = uid(section_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    core_specs = (
        ("concept/monoidal-category", "幺半范畴", "kategori monoidal"),
        ("concept/tensor-product", "张量积", "hasil kali tensor"),
        ("concept/unit-object", "幺对象", "objek satuan"),
        ("concept/associativity-constraint", "结合约束", "kendala asosiativitas"),
        ("concept/unit-constraint", "幺约束", "kendala satuan"),
        ("concept/mac-lane-pentagon-axiom", "Mac Lane 五角形公理", "aksioma segilima Mac Lane"),
        ("concept/monoidal-triangle-axiom", "幺半范畴三角形公理", "aksioma segitiga kategori monoidal"),
        ("concept/monoidal-subcategory", "幺半子范畴", "subkategori monoidal"),
        ("concept/braid-category", "辫范畴", "kategori kepang"),
        ("concept/enriched-category", "充实范畴", "kategori diperkaya"),
        ("concept/additive-category", "加性范畴", "kategori aditif"),
        ("concept/biproduct", "双积", "biproduk"),
        ("concept/monoidal-functor", "幺半函子", "fungtor monoidal"),
        ("concept/strong-monoidal-functor", "强幺半函子", "fungtor monoidal kuat"),
        ("concept/right-lax-monoidal-functor", "右松幺半函子", "fungtor monoidal longgar-kanan"),
        ("concept/left-lax-monoidal-functor", "左松幺半函子", "fungtor monoidal longgar-kiri"),
        ("concept/monoidal-natural-transformation", "幺半自然变换", "transformasi natural monoidal"),
        ("concept/monoidal-equivalence", "幺半等价", "ekuivalensi monoidal"),
        ("concept/tensor-category", "张量范畴", "kategori tensor"),
        ("concept/cobordism-category", "配边范畴", "kategori kobordisme"),
        ("concept/kelly-coherence-lemma", "Kelly 相容性引理", "Lema koherensi Kelly"),
    )
    concepts = [surface_concept(uid, *spec) for spec in core_specs]

    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_labels, target_labels, strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        concepts.append(surface_concept(uid, f"surface/unit-019/label/{ordinal:03d}", f"TeX 标签 {ordinal:03d}: {label}; 源行 {source_line}", f"label TeX {ordinal:03d}: {label}; baris target {target_line}"))

    for ordinal, (source_item, target_item) in enumerate(zip(reference_occurrences(source_text), reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        concepts.append(surface_concept(uid, f"surface/unit-019/reference/{kind}/{ordinal:03d}", f"引用 {ordinal:03d}: {label}; 源行 {source_line}", f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_line}"))

    for ordinal, (locator, bib_key, line) in enumerate(CITATIONS, 1):
        locator_source = locator or "无定位符"
        locator_target = locator or "tanpa lokator"
        concepts.append(surface_concept(uid, f"surface/unit-019/citation-occurrence/{ordinal:03d}", f"引文出现 {ordinal:03d}: {bib_key}; {locator_source}; 源行 {line}", f"kemunculan sitasi {ordinal:03d}: {bib_key}; {locator_target}; baris target {line}"))

    for ordinal, line in enumerate(ITEM_LINES, 1):
        concepts.append(surface_concept(uid, f"surface/unit-019/item/{ordinal:03d}", f"列表项目 {ordinal:03d}; 源行 {line}", f"butir daftar {ordinal:03d}; baris target {line}"))

    inline_pairs = pair_inline_formula_occurrences(inline_formula_occurrences(source_text), inline_formula_occurrences(target_text))
    for source_item, target_item in inline_pairs:
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-019/formula/inline/{ordinal:03d}", f"行内公式 {ordinal:03d}; 源行 {source_line}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus sebaris {ordinal:03d}; baris target {target_line}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-019/formula/display-bracket/{ordinal:03d}", f"陈列公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus pajang {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    for source_item, target_item in zip(source_env, target_env, strict=True):
        ordinal, environment, source_first, source_last, source_formula = source_item
        _, _, target_first, target_last, target_formula = target_item
        concepts.append(surface_concept(uid, f"surface/unit-019/formula/display-environment/{ordinal:03d}", f"{environment} 公式 {ordinal:03d}; 源行 {source_first}-{source_last}; SHA-256 {digest(source_formula.encode('utf-8'))}", f"rumus {environment} {ordinal:03d}; baris target {target_first}-{target_last}; SHA-256 {digest(target_formula.encode('utf-8'))}"))

    for kind, pattern, source_name, target_name in (
        ("arrow", r"\\arrow(?![A-Za-z])", "图表箭头", "panah diagram"),
        ("node", r"\\node(?![A-Za-z])", "图表节点", "simpul diagram"),
        ("path", r"\\path(?![A-Za-z])", "图表路径", "lintasan diagram"),
    ):
        source_lines = occurrence_lines(source_text, pattern)
        target_lines = occurrence_lines(target_text, pattern)
        for ordinal, (source_line, target_line) in enumerate(zip(source_lines, target_lines, strict=True), 1):
            concepts.append(surface_concept(uid, f"surface/unit-019/diagram-{kind}/{ordinal:03d}", f"{source_name} {ordinal:03d}; 源行 {source_line}", f"{target_name} {ordinal:03d}; baris target {target_line}"))

    for correction_id, line, issue, adverse_id in CORRECTIONS:
        concepts.append(surface_concept(uid, f"correction/{correction_id.casefold()}", f"声明的源文本更正 {correction_id}; 源行 {line}", f"koreksi sumber terdeklarasi {correction_id}; baris {line}; {issue} Ledger: {adverse_id}."))

    for ordinal, row in enumerate(terminology_rows, 1):
        concepts.append(surface_concept(uid, f"surface/unit-019/terminology-row/{ordinal:03d}", f"术语记录 {ordinal:03d}: {row['source_term']}", f"baris terminologi {ordinal:03d}: {row['source_term']} -> {row['target_term']}; status admitted; scope {row['scope']}"))

    concept_ids = [item["id"] for item in concepts]
    selected_prerequisite_keys = {
        "prerequisite/vector-spaces",
        "prerequisite/point-set-topology",
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
        "prerequisite/universal-properties-and-comma-categories",
        "prerequisite/limits-and-colimits",
    }
    prerequisite_ids = [item["id"] for item in data["prerequisites"] if item["stable_key"] in selected_prerequisite_keys]
    if len(prerequisite_ids) != len(selected_prerequisite_keys):
        raise SystemExit("Unit 019 backend refused: prerequisite inventory drift")
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    principal = rights_by_key["rights/principal-cc-by-4.0"]
    unit_rights = [principal, rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"], rights_by_key["rights/noto-fonts-ofl-1.1"]]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter3.tex:1-227",
        "titles": [{"language": "zh-Hans", "text": "第三章：幺半范畴；基本定义"}, {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Definisi Dasar"}],
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
        key = f"citation/unit-019/{bib_key.casefold()}"
        citations.append({
            "id": uid(key), "stable_key": key, "entity_type": "citation",
            "bib_key": bib_key, "bibliography_path": BIBLIOGRAPHY,
            "bibliography_sha256": bibliography_hash, "source_line": line,
            "target_line": line, "section_id": section_id,
        })

    base.SPAN_START = 1
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (spec, source_index, target_index) in enumerate(zip(INDEX_SPECS, source_indexes, target_indexes, strict=True), 1):
        slug, _, _, _ = spec
        key = f"index-entry/unit-019/{slug}"
        index_entries.append({
            "id": uid(key), "stable_key": key, "entity_type": "index_entry",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_key": source_index[1], "target_key": target_index[1],
            "source_binding": source_binding(SOURCE, source_index[2], source_index[2]),
            "target_binding": target_binding(target_index[2], target_index[2], target_admission_id),
            "provenance_state": "source_key_preserved_target_key_localized",
        })

    source_diagrams = base.diagram_occurrences(source_text)
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-019/{source_format}-{occurrence:02d}"
        diagrams.append({
            "id": uid(key), "stable_key": key, "entity_type": "diagram",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_format": source_format, "source_occurrence_index": occurrence,
            "source_binding": source_binding(SOURCE, source_first, source_last),
            "target_binding": target_binding(target_first, target_last, target_admission_id),
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
        "id": uid("build-surface/unit-019-pdf"), "stable_key": "build-surface/unit-019-pdf",
        "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_019.ps1 -OutputDirectory build/unit-019-replay",
        "artifact_path": ARTIFACT, "artifact_binding": source_binding(ARTIFACT),
        "log_binding": source_binding(FINAL_LOG), "build_script": source_binding(BUILD_SCRIPT),
        "page_count": page_count, "status": "pass", "driver": source_binding(DRIVER),
        "input_bindings": [source_binding(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution", "TeX Gyre Heros", "TikZ and tikz-cd",
            "TikZ tqft library", "packages loaded by the Unit 019 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    formula_total = len(inline_pairs) + len(source_brackets) + len(source_env)
    qa_admission = {
        "id": uid("qa/unit-019/admission-gate"), "stable_key": "qa/unit-019/admission-gate",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and all-page admission of chapter3.tex authority lines 1-227 "
            "to target lines 1-226: 16 labels, 28 ref/eqref occurrences, four citations, 13 list items, "
            "15 tikzcd and three tikzpicture structures, 75 arrows, 11 explicit nodes, one explicit path, "
            f"167 inline plus 17 display formula surfaces ({formula_total} total), and 11 localized index entries. "
            "Correction O013-LI-U019-COR-001 is disclosed and mapped to O013-ADV-0051. Fifteen reviewed "
            "terminology rows were promoted from candidate at admission. Component rights remain CC BY 4.0 "
            "for principal text/translation, CC BY-SA 3.0 for the AJbook fragment, and OFL 1.1 for bundled "
            f"fonts. Production provenance is {MODEL}, separate from Wen-Wei Li's authorship and human credit."
        ),
        "witness": STRUCTURE_QA, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(STRUCTURE_QA),
    }
    qa_source = {
        "id": uid("qa/unit-019/source-review"), "stable_key": "qa/unit-019/source-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent translation/source review of the exact authority and target spans, including terminology, formula, citation, index, diagram, and correction preservation.",
        "witness": REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(REVIEW),
    }
    qa_math = {
        "id": uid("qa/unit-019/math-structure-review"), "stable_key": "qa/unit-019/math-structure-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent mathematical-topology audit of every protected surface and the minimal Kelly-diagram repair.",
        "witness": MATH_REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(MATH_REVIEW),
    }
    qa_structure = {
        "id": uid("qa/unit-019/structure-check"), "stable_key": "qa/unit-019/structure-check",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Machine structure check binds the source/target boundary, external-reference closure, protected-surface census, and zero Han residue.",
        "witness": STRUCTURE_OUTPUT, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(STRUCTURE_OUTPUT),
    }
    qa_replay = {
        "id": uid("qa/unit-019/render-replay"), "stable_key": "qa/unit-019/render-replay",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Deterministic extracted-text and same-renderer Poppler/MuPDF replay, with all pages visually inspected.",
        "witness": RENDER_INVENTORY, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(RENDER_INVENTORY),
    }
    qa_visual = {
        "id": uid("qa/unit-019/all-page-visual-review"), "stable_key": "qa/unit-019/all-page-visual-review",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent all-page visual review of the final reader in Poppler and MuPDF after the final reflow boundary.",
        "witness": VISUAL_REVIEW, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(VISUAL_REVIEW),
    }
    qa_terms = {
        "id": uid("qa/unit-019/terminology-control"), "stable_key": "qa/unit-019/terminology-control",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live id-ID glossary binding for the fifteen Unit 019 monoidal-category rows, with category-algebra and graduate-algebra Indonesian terminology QA retained separately.",
        "witness": TERMINOLOGY, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(TERMINOLOGY),
    }
    qa_term_evidence = {
        "id": uid("qa/unit-019/terminology-evidence"), "stable_key": "qa/unit-019/terminology-evidence",
        "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity",
        "result": "pass",
        "scope": f"Bound Indonesian field-usage QA; its category-algebra companion remains {TERMINOLOGY_QA_CATEGORY}.",
        "witness": TERMINOLOGY_QA_GRADUATE, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": source_binding(TERMINOLOGY_QA_GRADUATE),
    }

    data["dataset_stable_key"] = "dataset/unit-019/id-id"
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
        "order": 19, "source_local_id": "chapter3.tex:1-227",
        "titles": [{"language": "zh-Hans", "text": "第三章：幺半范畴；基本定义"}, {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Definisi Dasar"}],
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
            qa_admission["id"], qa_source["id"], qa_math["id"],
            qa_structure["id"], qa_replay["id"], qa_visual["id"], qa_terms["id"],
            qa_term_evidence["id"],
        ],
        "outcome_keys": [
            "outcome/define-monoidal-category-data-and-coherence",
            "outcome/use-associativity-and-unit-constraints",
            "outcome/recognize-cartesian-cocartesian-module-and-cobordism-examples",
            "outcome/apply-kelly-unit-coherence-identities",
            "outcome/read-and-verify-monoidal-coherence-diagrams",
            "outcome/define-strong-and-lax-monoidal-functors",
            "outcome/construct-monoidal-natural-transformations-and-equivalences",
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
        qa_admission, qa_source, qa_math, qa_structure, qa_replay, qa_visual, qa_terms,
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
        raise SystemExit("Unit 019 backend refused: missing CSV projection")
    print(json.dumps({
        "path": OUTPUT.relative_to(ROOT).as_posix(), "bytes": OUTPUT.stat().st_size,
        "sha256": digest(OUTPUT.read_bytes()), "concepts": len(concepts),
        "labels": 16, "references": 28, "citation_occurrences": 4,
        "native_bibliography_records": 2, "items": 13,
        "formula_entities": formula_total, "diagrams": 18, "arrows": 75,
        "nodes": 11, "paths": 1, "index_entries": 11, "corrections": 1,
        "terminology_rows": 15,
        "artifact": {"pages": page_count, "bytes": artifact_id[0], "sha256": artifact_id[1]},
        "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
        "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
