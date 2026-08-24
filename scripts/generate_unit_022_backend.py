#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 022.

The shared v1.1.0 schema has no first-class TeX-label, reference-occurrence,
formula, diagram primitive, terminology-row, or correction record. Those
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
TEMPLATE = ROOT / "backend/data/unit-020-bab-3-keketatan-dan-teorema-koherensi.json"
OUTPUT = ROOT / "backend/data/unit-022-bab-3-kategori-diperkaya-dan-aditif.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
CANDIDATE = "build/unit-022-candidate/chapter3-enriched-categories-id.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-022-bab-3-kategori-diperkaya-dan-aditif.tex"
COVER = "repo/source/coverpage-id-unit-022.tex"
CROSSREF = "repo/source/unit-022-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_022.ps1"
STRUCTURE_GATE = "scripts/check_unit_022_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_022_evidence.py"
RENDER_INVENTORY = "qa/unit-022-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-022-evidence/structure-and-pdf-qa.json"
REVIEW = "qa/UNIT_022_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_022_MATH_STRUCTURE_AUDIT_20260824.md"
CORRECTION_REVIEW = "qa/UNIT_022_SOURCE_CORRECTIONS_20260824.md"
VISUAL_REVIEW = "qa/UNIT_022_VISUAL_QA_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_022_TERMINOLOGY_AUDIT_20260824.md"
FINAL_LOG = "qa/UNIT_022_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-022-bab-3-kategori-diperkaya-dan-aditif.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_START, SOURCE_END = 513, 722
TARGET_START, TARGET_END = 512, 721
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    15_089,
    "85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d",
)
CANDIDATE_FULL = (
    17_541,
    "e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255",
)
TARGET_FULL = (
    86_033,
    "b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2",
)
TARGET_SPAN = CANDIDATE_FULL
NEXT_LINE_SHA256 = "26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7"
STRUCTURE_GATE_ID = (
    6_084,
    "981d558ed0d237b002f014db390469046ce1a0f6034c22e5442f5bda6571380a",
)
REVIEW_ID = (
    9_175,
    "36d7650aa142da19d998dc8f1b6d39f24a94e2a19e51e988cbd2187691f56e9f",
)
MATH_REVIEW_ID = (
    7_050,
    "28b72b44a016d953a5e984383919249510ed7a11d36bb861192ffdb4bea9aa1a",
)
CORRECTION_REVIEW_ID = (
    5_197,
    "960ad14d54b9cc5e1d85dbcab6fd6447a6a692fd489164e747e056e2684fe52e",
)
TERMINOLOGY_ID = (
    41_824,
    "bbe7c8906aa94a96766bb1aacbf1425527593d514fbe83649eea96095ff0d882",
)
TERMINOLOGY_AUDIT_ID = (
    7_325,
    "f277588412dbf1dfe22237f0fe70f86ccd02e20bab04cb33a6314cb2ca9fcb76",
)

CORRECTIONS = (
    (
        "O013-LI-U022-COR-001",
        "588",
        "587",
        "The authority uses a tensor product between ordinary Hom-sets; the target "
        "uses their Cartesian product so the induced composition map is well-typed.",
    ),
    (
        "O013-LI-U022-COR-002",
        "665",
        "664",
        "The authority gives both biproduct injections domain X_1; the target uses "
        "X_i, as required by p_i iota_i = identity_{X_i}.",
    ),
)

LABELS = (
    "sec:enriched-cat",
    "def:enriched-cat",
    "def:enriched-functor",
    "rem:enriched-to-ordinary",
    "def:enriched-naturaltrans",
    "eg:Ab-cat",
    "def:biproduct",
    "prop:biproduct-criterion",
    "def:additive-cat",
    "prop:biproduct-preservation",
    "prop:additive-prod-coprod",
)
REFERENCES = (
    ("ordinary", "eg:categories", 7),
    ("ordinary", "def:category", 57),
    ("ordinary", "eg:monoidal-cat", 93),
    ("ordinary", "con:U-small", 93),
    ("ordinary", "eg:categories", 97),
    ("ordinary", "eg:categories", 97),
    ("ordinary", "rem:enriched-to-ordinary", 115),
    ("ordinary", "sec:limits", 118),
    ("ordinary", "prop:product-associativity", 142),
    ("ordinary", "def:universal-objects", 185),
    ("ordinary", "def:zero-morphism", 185),
    ("ordinary", "def:enriched-functor", 192),
    ("ordinary", "prop:Mod-cat-additive", 195),
    ("ordinary", "prop:biproduct-criterion", 208),
    ("ordinary", "prop:product-associativity", 208),
)
CITATIONS = (
    ("", "Ke05", 13),
    ("Chapter 5", "May99", 97),
)
ITEM_LINES = (4, 5, 18, 19, 20, 23, 103, 104, 105, 106, 136, 137, 138, 180, 181, 182, 183)

INDEX_SPECS = (
    ("enriched-category", "main", 15, "chongshifanchou@kategori diperkaya (enriched category)"),
    ("enriched-hom-symbol", "sym1", 16, r"HomCi@$\iHom_{\mathcal{C}}(X, Y)$"),
    ("enriched-functor", "main", 59, "hanzi@fungtor!kasus diperkaya"),
    ("enriched-natural-transformation", "main", 82, "ziranbianhuan@transformasi natural!kasus diperkaya"),
    ("enriched-equivalence", "main", 90, "fanchoudengjia@ekuivalensi kategori!kasus diperkaya"),
    ("topological-category", "main", 96, "tuopufanchou@kategori topologis (topological category)"),
    ("ab-enriched-category", "main", 100, r"Ab-fanchou@kategori-$\cate{Ab}$"),
    ("biproduct", "main", 120, "shuangji@biproduk (biproduct)"),
    ("additive-category", "main", 191, "jiaxingfanchou@kategori aditif (additive category)"),
    ("additive-functor", "main", 191, "hanzi@fungtor!kasus aditif"),
)

DIAGRAM_SPECS = (
    ("tikzpicture", 1, 8, 12),
    ("tikzpicture", 2, 27, 39),
    ("tikzpicture", 3, 40, 54),
    ("tikzcd", 1, 61, 64),
    ("tikzcd", 2, 65, 68),
    ("tikzcd", 3, 75, 79),
    ("tikzcd", 4, 84, 88),
    ("tikzcd", 5, 122, 124),
    ("tikzcd", 6, 127, 127),
)

TERMINOLOGY_SPECS = (
    ("enriched category", "kategori diperkaya"),
    ("enriched functor", "fungtor diperkaya"),
    ("enriched natural transformation", "transformasi natural diperkaya"),
    ("enriched category equivalence", "ekuivalensi kategori diperkaya"),
    ("Hom-object", "objek-Hom"),
    ("topological category", "kategori topologis"),
    ("Ab-enriched category", "kategori-Ab"),
    ("preadditive category", "kategori praaditif"),
    ("additive category", "kategori aditif"),
    ("biproduct", "biproduk"),
    ("additive functor", "fungtor aditif"),
)

SURFACE_SPECS = (
    ("arrow", r"\\arrow(?![A-Za-z])", 21, "图表箭头", "panah diagram"),
    ("node", r"\\node(?![A-Za-z])", 14, "图表节点", "simpul diagram"),
    ("coordinate", r"\\coordinate(?![A-Za-z])", 0, "图表坐标", "koordinat diagram"),
    ("draw", r"\\draw(?![A-Za-z])", 11, "绘图命令", "perintah gambar"),
    ("path", r"\\path(?![A-Za-z])", 0, "图表路径", "lintasan diagram"),
    ("edge", r"(?<![A-Za-z])edge(?![A-Za-z])", 13, "图表边", "sisi diagram"),
    ("braid", r"\\braid(?![A-Za-z])", 0, "辫图命令", "perintah diagram kepang"),
    ("hline", r"\\hline(?![A-Za-z])", 0, "表格横线", "garis mendatar tabel"),
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-022-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 022 backend refused: " + message)


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
    if repair_source:
        text = text.replace(
            r"\right) \otimes \Hom_{\mathcal{V}}\left(",
            r"\right) \times \Hom_{\mathcal{V}}\left(",
        )
        text = text.replace(r"\iota_i: X_1 \to Z", r"\iota_i: X_i \to Z")
        text = text.replace(
            r"{\otimes \;\text{的函子性}}",
            r"{\text{fungtorialitas }\;\otimes}",
        )
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
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U022":
        refuse("structured QA status/unit drift")

    required_target = {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
        "line_records": 910,
        "span_lines": "512-721",
        "span_line_records": 210,
        "span_bytes": TARGET_SPAN[0],
        "span_sha256": TARGET_SPAN[1],
        "span_equals_isolated_candidate": True,
        "next_target_line": 722,
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
            "def:category",
            "def:universal-objects",
            "def:zero-morphism",
            "eg:categories",
            "eg:monoidal-cat",
            "prop:Mod-cat-additive",
            "prop:product-associativity",
            "sec:limits",
        ],
        "external_crossref_numbers": {
            "def:category": "2.1.1",
            "con:U-small": "2.1.4",
            "eg:categories": "2.1.5",
            "def:universal-objects": "2.4.1",
            "def:zero-morphism": "2.4.3",
            "sec:limits": "2.7",
            "prop:product-associativity": "2.7.11",
            "eg:monoidal-cat": "3.1.3",
            "prop:Mod-cat-additive": "6.2.4",
        },
        "citations": [
            {"locator": locator, "key": bib_key}
            for locator, bib_key, _ in CITATIONS
        ],
        "index_entries": 10,
        "ordinary_index_entries": 9,
        "symbol_index_entries": 1,
        "environment_counts": {
            "tikzcd": 6,
            "definition": 5,
            "proof": 4,
            "tikzpicture": 3,
            "example": 3,
            "align*": 3,
            "cases": 3,
            "compactitem": 2,
            "center": 2,
            "remark": 2,
            "compactenum": 2,
            "proposition": 2,
            "enumerate": 1,
            "gather*": 1,
            "theorem": 1,
            "lemma": 1,
        },
        "tikzpicture": 3,
        "tikzcd": 6,
        "declared_corrections": [item[0] for item in CORRECTIONS],
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
        renders.get("unit_id") != "O013-LI-U022"
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
        CORRECTION_REVIEW,
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
    require_identity(CORRECTION_REVIEW, CORRECTION_REVIEW_ID)
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
        or source_lines[721] != ""
        or target_lines[720] != ""
        or source_lines[722] != target_lines[721]
        or digest((source_lines[722] + "\n").encode("utf-8")) != NEXT_LINE_SHA256
    ):
        refuse("next-section boundary is not preserved")
    source_suffix = ("\n".join(source_lines[722:]) + "\n").encode("utf-8")
    target_suffix = ("\n".join(target_lines[721:]) + "\n").encode("utf-8")
    if source_suffix != target_suffix:
        refuse("post-Unit-022 canonical remainder differs from authority")

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
        "PASS Unit 022",
        SOURCE_SPAN[1],
        TARGET_SPAN[1],
        TARGET_FULL[1],
        *(item[0] for item in CORRECTIONS),
    ):
        if needle not in check.stdout:
            refuse(f"structure-check output lacks {needle!r}")

    source_text = source_span.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_environments = environment_occurrences(source_text)
    target_environments = environment_occurrences(target_text)
    if (
        len(source_environments) != 41
        or source_environments != target_environments
    ):
        refuse("forty-one-environment occurrence topology drift")
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    if tuple(label for label, _ in source_labels) != LABELS or source_labels != target_labels:
        refuse("eleven-label topology drift")
    if reference_occurrences(source_text) != REFERENCES or reference_occurrences(target_text) != REFERENCES:
        refuse("fifteen-reference topology drift")
    if citation_occurrences(source_text) != CITATIONS or citation_occurrences(target_text) != CITATIONS:
        refuse("two-citation topology drift")
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
        refuse("nine-diagram topology drift")

    for kind, pattern, expected, _, _ in SURFACE_SPECS:
        source_occurrences = occurrence_lines(source_text, pattern)
        target_occurrences = occurrence_lines(target_text, pattern)
        if source_occurrences != target_occurrences or len(source_occurrences) != expected:
            refuse(f"{expected}-{kind} topology drift")

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    if len(source_inline) != 204 or len(target_inline) != 204:
        refuse("204-inline-formula topology drift")
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
    if len(inline_pairs) != 204:
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
        len(source_env) != 4
        or len(target_env) != 4
        or tuple(item[:4] for item in source_env) != tuple(item[:4] for item in target_env)
        or tuple(localized_math(item[4], repair_source=True) for item in source_env)
        != tuple(localized_math(item[4]) for item in target_env)
    ):
        refuse("four environment-display formula topology drift")

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
        r"\InputSourceLineRange{chapter3.tex}{512}{721}",
        r"\setstretch{1.16}",
        MODEL,
    ):
        if needle not in driver:
            refuse(f"driver lacks {needle!r}")
    if "unit-022-candidate" in driver or Path(CANDIDATE).name in driver:
        refuse("public reader driver still depends on the isolated build candidate")
    bibliography = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8", errors="replace")
    for bib_key in ("Ke05", "May99"):
        if not re.search(rf"@[A-Za-z]+\s*\{{\s*{bib_key}\s*,", bibliography):
            refuse(f"bibliography lacks {bib_key}")

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
    correction_review = (ROOT / CORRECTION_REVIEW).read_text(encoding="utf-8")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for needle in ("PASS", "lines 513", TARGET_SPAN[1], MODEL, *(item[0] for item in CORRECTIONS)):
        if needle not in review:
            refuse(f"source review lacks {needle!r}")
    for needle in (
        "PASS",
        "41 balanced environment pairs",
        "204 dollar-delimited inline formula",
        "three `tikzpicture`",
        "six `tikzcd`",
        *(item[0] for item in CORRECTIONS),
    ):
        if needle not in math_review:
            refuse(f"math review lacks {needle!r}")
    for needle in ("CANONICALLY INTEGRATED", MODEL, *(item[0] for item in CORRECTIONS)):
        if needle not in correction_review:
            refuse(f"correction review lacks {needle!r}")
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
    unit_key = "unit/bab-3-kategori-diperkaya-dan-aditif"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/kategori-diperkaya-dan-aditif"
    section_id = uid(section_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_absolute = lambda line: SOURCE_START + line - 1
    target_absolute = lambda line: TARGET_START + line - 1

    core_specs = (
        ("concept/monoidal-category", "幺半范畴", "kategori monoidal"),
        ("concept/enriched-category", "充实范畴", "kategori diperkaya"),
        ("concept/hom-object", "Hom-对象", "objek-Hom"),
        ("concept/enriched-composition", "充实复合", "komposisi diperkaya"),
        ("concept/enriched-identity", "充实恒等态射", "morfisme identitas diperkaya"),
        ("concept/enriched-functor", "充实函子", "fungtor diperkaya"),
        ("concept/underlying-ordinary-category", "底层通常范畴", "kategori biasa yang mendasari"),
        ("concept/enriched-natural-transformation", "充实自然变换", "transformasi natural diperkaya"),
        ("concept/enriched-category-equivalence", "充实范畴等价", "ekuivalensi kategori diperkaya"),
        ("concept/topological-category", "拓扑范畴", "kategori topologis"),
        ("concept/ab-enriched-category", "Ab-充实范畴", "kategori-Ab"),
        ("concept/bilinear-composition", "双线性复合", "komposisi bilinear"),
        ("concept/preadditive-category", "预加性范畴", "kategori praaditif"),
        ("concept/forgetful-functor", "遗忘函子", "fungtor pelupa"),
        ("concept/product", "积", "produk"),
        ("concept/coproduct", "余积", "koproduk"),
        ("concept/biproduct", "双积", "biproduk"),
        ("concept/zero-object", "零对象", "objek nol"),
        ("concept/zero-morphism", "零态射", "morfisme nol"),
        ("concept/biproduct-projection", "双积投影", "proyeksi biproduk"),
        ("concept/biproduct-injection", "双积嵌入", "injeksi biproduk"),
        ("concept/additive-category", "加性范畴", "kategori aditif"),
        ("concept/additive-functor", "加性函子", "fungtor aditif"),
        ("concept/finite-biproduct", "有限双积", "biproduk berhingga"),
        ("concept/unit-object", "幺对象", "objek satuan"),
        ("concept/associativity-constraint", "结合约束", "kendala asosiativitas"),
        ("concept/unit-constraint", "幺约束", "kendala satuan"),
        ("concept/naturality", "自然性", "naturalitas"),
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
                f"surface/unit-022/environment/{ordinal:03d}-{environment_slug}-{occurrence:02d}",
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
                f"surface/unit-022/label/{ordinal:03d}",
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
                f"surface/unit-022/reference/{kind}/{ordinal:03d}",
                f"引用 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}",
                f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_absolute(target_line)}",
            )
        )

    for ordinal, (locator, bib_key, line) in enumerate(CITATIONS, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-022/citation-occurrence/{ordinal:03d}",
                f"引文出现 {ordinal:03d}: {bib_key}; {locator or '无定位符'}; 源行 {source_absolute(line)}",
                f"kemunculan sitasi {ordinal:03d}: {bib_key}; {locator or 'tanpa lokator'}; baris target {target_absolute(line)}",
            )
        )

    for ordinal, line in enumerate(ITEM_LINES, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-022/item/{ordinal:03d}",
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
                f"surface/unit-022/formula/inline/{ordinal:03d}",
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
                f"surface/unit-022/formula/display-bracket/{ordinal:03d}",
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
                f"surface/unit-022/formula/display-environment/{ordinal:03d}",
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
                    f"surface/unit-022/diagram-{kind}/{ordinal:03d}",
                    f"{source_name} {ordinal:03d}; 源行 {source_absolute(source_line)}",
                    f"{target_name} {ordinal:03d}; baris target {target_absolute(target_line)}",
                )
            )

    for correction_id, source_line, target_line, issue in CORRECTIONS:
        concepts.append(
            surface_concept(
                uid,
                f"correction/{correction_id.casefold()}",
                f"声明的源文本更正 {correction_id}; 源行 {source_line}",
                f"koreksi sumber terdeklarasi {correction_id}; baris sumber {source_line}; "
                f"baris target {target_line}; {issue} Bukti: {CORRECTION_REVIEW}.",
            )
        )

    for ordinal, row in enumerate(terminology_rows, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-022/terminology-row/{ordinal:03d}",
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
        "prerequisite/representable-functors-and-yoneda",
        "prerequisite/limits-and-colimits",
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
        {"language": "zh-Hans", "text": "第三章：幺半范畴；充实范畴与加性范畴"},
        {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Kategori Diperkaya dan Aditif"},
    ]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter3.tex:513-722",
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
        key = f"citation/unit-022/{bib_key.casefold()}"
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
        key = f"index-entry/unit-022/{slug}"
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
        key = f"diagram/unit-022/{source_format}-{occurrence:02d}"
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
        "id": uid("build-surface/unit-022-pdf"),
        "stable_key": "build-surface/unit-022-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_022.ps1 -OutputDirectory build/unit-022-replay",
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
            "packages loaded by the Unit 022 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    formula_total = len(inline_pairs) + len(source_brackets) + len(source_env)
    qa_admission = {
        "id": uid("qa/unit-022/admission-gate"),
        "stable_key": "qa/unit-022/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and all-page admission of chapter3.tex authority lines "
            "513-722 to target lines 512-721: eleven labels, fifteen ordinary references, no equation "
            "references, two citation occurrences, seventeen list items, forty-one environment pairs, "
            "three tikzpicture and six tikzcd "
            "structures, twenty-one tikzcd arrows, fourteen TikZ nodes, eleven draws, thirteen edge "
            "tokens, 204 inline plus eleven bracket-display and four environment-display formula surfaces "
            f"({formula_total} total), and ten localized index entries. O013-LI-U022-COR-001 repairs the "
            "set-level product in the underlying-category composition map; O013-LI-U022-COR-002 repairs "
            "the biproduct injection domain. Exactly eleven applicable terminology rows are bound: eight "
            "new Unit 022 records and three previously admitted records, with evidentiary limits intact. "
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
        "id": uid("qa/unit-022/source-review"),
        "stable_key": "qa/unit-022/source-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent translation/source review of the exact authority and target spans, including terminology, formulas, citations, indexes, diagrams, and disclosed corrections.",
        "witness": REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(REVIEW),
    }
    qa_math = {
        "id": uid("qa/unit-022/math-structure-review"),
        "stable_key": "qa/unit-022/math-structure-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent mathematical/protected-topology audit of every formula, identifier, reference, citation, list item, index, diagram primitive, and the two declared source repairs.",
        "witness": MATH_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(MATH_REVIEW),
    }
    qa_correction = {
        "id": uid("qa/unit-022/source-corrections"),
        "stable_key": "qa/unit-022/source-corrections",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Separate provenance and deterministic adjudication for O013-LI-U022-COR-001 and O013-LI-U022-COR-002.",
        "witness": CORRECTION_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(CORRECTION_REVIEW),
    }
    qa_structure = {
        "id": uid("qa/unit-022/structure-check"),
        "stable_key": "qa/unit-022/structure-check",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Fail-closed machine structure check binds source/candidate/canonical identities, next-section closure, all protected surfaces, two declared repairs, and zero Han residue.",
        "witness": STRUCTURE_GATE,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(STRUCTURE_GATE),
    }
    qa_replay = {
        "id": uid("qa/unit-022/render-replay"),
        "stable_key": "qa/unit-022/render-replay",
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
        "id": uid("qa/unit-022/all-page-visual-review"),
        "stable_key": "qa/unit-022/all-page-visual-review",
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
        "id": uid("qa/unit-022/terminology-control"),
        "stable_key": "qa/unit-022/terminology-control",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live id-ID glossary binding for exactly eleven applicable admitted Unit 022 terminology rows: eight new records and three reused category-theory records.",
        "witness": TERMINOLOGY,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY),
    }
    qa_term_evidence = {
        "id": uid("qa/unit-022/terminology-evidence"),
        "stable_key": "qa/unit-022/terminology-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Bound terminology adjudication distinguishes directly attested Indonesian category-theory forms from transparent compositional choices for enriched-category, Hom-object, biproduct, and additive-functor terminology without overclaiming uniform usage.",
        "witness": TERMINOLOGY_AUDIT,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY_AUDIT),
    }

    data["dataset_stable_key"] = "dataset/unit-022/id-id"
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
        "order": 22,
        "source_local_id": "chapter3.tex:513-722",
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
            qa_correction["id"],
            qa_structure["id"],
            qa_replay["id"],
            qa_visual["id"],
            qa_terms["id"],
            qa_term_evidence["id"],
        ],
        "outcome_keys": [
            "outcome/define-categories-enriched-over-a-monoidal-category",
            "outcome/construct-enriched-functors-and-natural-transformations",
            "outcome/recover-the-underlying-ordinary-category",
            "outcome/analyze-topological-and-ab-enriched-categories",
            "outcome/characterize-biproducts-by-projections-and-injections",
            "outcome/relate-additive-categories-functors-products-and-coproducts",
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
        qa_correction,
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
                "environments": 41,
                "labels": 11,
                "ordinary_references": 15,
                "equation_references": 0,
                "citation_occurrences": 2,
                "native_bibliography_records": len(citations),
                "items": 17,
                "formula_entities": formula_total,
                "diagrams": len(diagrams),
                "arrows": 21,
                "nodes": 14,
                "coordinates": 0,
                "draws": 11,
                "paths": 0,
                "edges": 13,
                "braids": 0,
                "hlines": 0,
                "index_entries": 10,
                "corrections": 2,
                "terminology_rows": 11,
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
