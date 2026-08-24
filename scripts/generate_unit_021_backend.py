#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 021.

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
OUTPUT = ROOT / "backend/data/unit-021-bab-3-struktur-kepang.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
CANDIDATE = "build/unit-021-candidate/chapter3-braiding-id.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-021-bab-3-struktur-kepang.tex"
COVER = "repo/source/coverpage-id-unit-021.tex"
CROSSREF = "repo/source/unit-021-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_021.ps1"
STRUCTURE_GATE = "scripts/check_unit_021_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_021_evidence.py"
RENDER_INVENTORY = "qa/unit-021-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-021-evidence/structure-and-pdf-qa.json"
REVIEW = "qa/UNIT_021_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_021_MATH_STRUCTURE_AUDIT_20260824.md"
CORRECTION_REVIEW = "qa/UNIT_021_SOURCE_CORRECTIONS_20260824.md"
VISUAL_REVIEW = "qa/UNIT_021_VISUAL_QA_20260824.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_021_TERMINOLOGY_AUDIT_20260824.md"
FINAL_LOG = "qa/UNIT_021_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-021-bab-3-struktur-kepang.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_START, SOURCE_END = 307, 512
TARGET_START, TARGET_END = 306, 511
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    15_276,
    "cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8",
)
CANDIDATE_FULL = (
    17_968,
    "57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085",
)
TARGET_FULL = (
    83_581,
    "ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9",
)
TARGET_SPAN = CANDIDATE_FULL
NEXT_LINE_SHA256 = "c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541"
STRUCTURE_GATE_ID = (
    28_404,
    "f5ef89d6fcfa7196e54a43e1a13377df93d985bc7407f60b3f58ecef0aeb2cce",
)
REVIEW_ID = (
    9_460,
    "b22feafa193ed118bbe7c559a97e05817f720575bda8cfe190b8827c5f47fe4e",
)
MATH_REVIEW_ID = (
    7_530,
    "099d3d9e31111b79b8b1fac0490176a18bb2b773a7493e7b731e1241f71279d0",
)
CORRECTION_REVIEW_ID = (
    3_492,
    "53cdb481310e76a2b2025b9086b884f7c6a7b1071606ce1c545cf24ac559db55",
)
TERMINOLOGY_ID = (
    39_866,
    "45e7b1500533e4fa8a8a257efe2982261704bd00a27f056030112141e5ed0efe",
)
TERMINOLOGY_AUDIT_ID = (
    4_653,
    "baaf37af9e72cb487636b07369403432d6a02e8bd6b2960fda1ca7d9537c2ef2",
)

CORRECTIONS = (
    (
        "O013-LI-U021-COR-001",
        "487",
        "486",
        "The authority repeats the upper objects in the braiding naturality square; "
        "the target restores the primed codomains and component c(X',Y').",
    ),
    (
        "O013-LI-U021-COR-002",
        "450 and 452",
        "449 and 451",
        "After defining X=m and Y=n as objects, the authority misnames both as "
        "braids; the target correctly calls them objects without changing symbols.",
    ),
    (
        "O013-LI-U021-ED-001",
        "508",
        "507",
        "The authority contains a duplicated Chinese noun for group; the target states "
        "the intended infinite cyclic group once.",
    ),
)

LABELS = (
    "sec:braiding",
    "def:braiding",
    "eqn:hexagon-axiom-1",
    "eqn:hexagon-axiom-2",
    "rem:hexagon-axiom-strict",
    "def:symm-monoidal-cat",
    "prop:YBE-cat-strict",
    "rem:YBE-cat-strict",
    "eg:braid",
)
REFERENCES = (
    ("ordinary", "eg:braid", 2),
    ("equation", "eqn:hexagon-axiom-1", 29),
    ("equation", "eqn:hexagon-axiom-2", 29),
    ("ordinary", "def:strict-monoidal-cat", 31),
    ("ordinary", "eg:monoidal-cat", 51),
    ("ordinary", "prop:product-commutativity", 51),
    ("ordinary", "sec:module-tensor-prod", 56),
    ("ordinary", "eg:fundamental-groupoid", 128),
    ("ordinary", "sec:symmetric-group", 130),
    ("equation", "eqn:braid-presentation", 130),
    ("ordinary", "rem:hexagon-axiom-strict", 166),
    ("ordinary", "rem:YBE-cat-strict", 168),
    ("ordinary", "def:braiding", 205),
)
CITATIONS = (
    ("", "JS93", 2),
    ("Corollary 2.6", "JS93", 205),
)
ITEM_LINES: tuple[int, ...] = ()

INDEX_SPECS = (
    ("braiding", "main", 4, "bianjiegou@struktur kepang (braiding)"),
    ("hexagon-axiom", "main", 4, "liujiaoxinggongli@aksioma segienam (hexagon axiom)"),
    (
        "braided-monoidal-functor",
        "main",
        38,
        "yaobanhanzi@fungtor monoidal (monoidal functor)!berkepang (braided)",
    ),
    (
        "symmetric-monoidal-category",
        "main",
        46,
        "yaobanfanchou@kategori monoidal (monoidal category)!"
        "kategori monoidal simetris (symmetric monoidal category)",
    ),
    (
        "yang-baxter-equation",
        "main",
        59,
        "YBE@persamaan Yang--Baxter (Yang--Baxter equation)",
    ),
    ("braid-category-symbol", "sym1", 97, r"Braid@$\cate{Braid}$"),
    ("braid-group", "main", 130, "bianqun@grup kepang (braid group)"),
    ("braid-group-symbol", "sym1", 130, r"B_n@$\mathcal{B}_n$"),
)

DIAGRAM_SPECS = (
    ("tikzcd", 1, 8, 12),
    ("tikzcd", 2, 13, 17),
    ("tikzcd", 3, 19, 22),
    ("tikzcd", 4, 22, 25),
    ("tikzcd", 5, 40, 43),
    ("tikzpicture", 1, 61, 81),
    ("tikzpicture", 2, 103, 111),
    ("tikzpicture", 3, 111, 116),
    ("tikzpicture", 4, 121, 127),
    ("tikzpicture", 5, 133, 139),
    ("tikzpicture", 6, 143, 143),
    ("tikzpicture", 7, 145, 145),
    ("tikzpicture", 8, 147, 153),
    ("tikzpicture", 9, 154, 154),
    ("tikzpicture", 10, 154, 154),
    ("tikzpicture", 11, 155, 159),
    ("tikzpicture", 12, 161, 165),
    ("tikzpicture", 13, 169, 171),
    ("tikzpicture", 14, 173, 175),
    ("tikzcd", 6, 179, 182),
    ("tikzpicture", 15, 183, 194),
    ("tikzpicture", 16, 196, 198),
    ("tikzpicture", 17, 199, 201),
)

TERMINOLOGY_SPECS = (
    ("braiding (monoidal category)", "struktur kepang"),
    ("braided monoidal category", "kategori monoidal berkepang"),
    ("braided monoidal functor", "fungtor monoidal berkepang"),
    ("symmetric monoidal category", "kategori monoidal simetris"),
    ("hexagon axiom (monoidal category)", "aksioma segienam"),
    ("Yang-Baxter equation", "persamaan Yang--Baxter"),
    ("braid", "kepang"),
    ("braid group", "grup kepang"),
    ("Artin braid group", "grup kepang Artin"),
)

SURFACE_SPECS = (
    ("arrow", r"\\arrow(?![A-Za-z])", 26, "图表箭头", "panah diagram"),
    ("node", r"\\node(?![A-Za-z])", 30, "图表节点", "simpul diagram"),
    ("coordinate", r"\\coordinate(?![A-Za-z])", 2, "图表坐标", "koordinat diagram"),
    ("draw", r"\\draw(?![A-Za-z])", 32, "绘图命令", "perintah gambar"),
    ("path", r"\\path(?![A-Za-z])", 0, "图表路径", "lintasan diagram"),
    ("edge", r"(?<![A-Za-z])edge(?![A-Za-z])", 15, "图表边", "sisi diagram"),
    ("braid", r"\\braid(?![A-Za-z])", 10, "辫图命令", "perintah diagram kepang"),
    ("hline", r"\\hline(?![A-Za-z])", 3, "表格横线", "garis mendatar tabel"),
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-021-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 021 backend refused: " + message)


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


def localized_math(text: str, repair_naturality: bool = False) -> str:
    if repair_naturality:
        text = text.replace(
            "\t\t" + r'''X \otimes Y \arrow[r, "{c(X, Y)}"'] & Y \otimes X''',
            "\t\t" + r"""X' \otimes Y' \arrow[r, "{c(X', Y')}"'] & Y' \otimes X'""",
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
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U021":
        refuse("structured QA status/unit drift")

    required_target = {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
        "span_lines": "306-511",
        "span_line_records": 206,
        "span_bytes": TARGET_SPAN[0],
        "span_sha256": TARGET_SPAN[1],
        "span_equals_isolated_candidate": True,
        "next_target_line": 512,
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
        "citations": [
            {"locator": locator, "key": bib_key}
            for locator, bib_key, _ in CITATIONS
        ],
        "index_entries": 8,
        "ordinary_index_entries": 6,
        "symbol_index_entries": 2,
        "environment_counts": {
            "definition": 3,
            "equation": 3,
            "tikzcd": 6,
            "remark": 2,
            "align*": 2,
            "example": 2,
            "proposition": 1,
            "center": 4,
            "tikzpicture": 17,
            "proof": 1,
            "multline*": 1,
            "array": 1,
        },
        "tikzpicture": 17,
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
        or visual.get("renderers_inspected") != ["Poppler", "PyMuPDF"]
    ):
        refuse("all-page visual evidence drift")
    if (
        renders.get("unit_id") != "O013-LI-U021"
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
        "nine_pages",
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
        or source_lines[511] != ""
        or target_lines[510] != ""
        or source_lines[512] != target_lines[511]
        or digest((source_lines[512] + "\n").encode("utf-8")) != NEXT_LINE_SHA256
    ):
        refuse("next-section boundary is not preserved")
    source_suffix = ("\n".join(source_lines[512:]) + "\n").encode("utf-8")
    target_suffix = ("\n".join(target_lines[511:]) + "\n").encode("utf-8")
    if source_suffix != target_suffix:
        refuse("post-Unit-021 canonical remainder differs from authority")

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
        "PASS Unit 021",
        SOURCE_SPAN[1],
        TARGET_SPAN[1],
        TARGET_FULL[1],
        *(item[0] for item in CORRECTIONS),
    ):
        if needle not in check.stdout:
            refuse(f"structure-check output lacks {needle!r}")

    source_text = source_span.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_labels = label_occurrences(source_text)
    target_labels = label_occurrences(target_text)
    if tuple(label for label, _ in source_labels) != LABELS or source_labels != target_labels:
        refuse("nine-label topology drift")
    if reference_occurrences(source_text) != REFERENCES or reference_occurrences(target_text) != REFERENCES:
        refuse("thirteen-reference topology drift")
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
        refuse("twenty-three-diagram topology drift")

    for kind, pattern, expected, _, _ in SURFACE_SPECS:
        source_occurrences = occurrence_lines(source_text, pattern)
        target_occurrences = occurrence_lines(target_text, pattern)
        if source_occurrences != target_occurrences or len(source_occurrences) != expected:
            refuse(f"{expected}-{kind} topology drift")

    source_inline = inline_formula_occurrences(source_text)
    target_inline = inline_formula_occurrences(target_text)
    if len(source_inline) != 144 or len(target_inline) != 144:
        refuse("144-inline-formula topology drift")
    source_by_line: dict[int, list[str]] = defaultdict(list)
    target_by_line: dict[int, list[str]] = defaultdict(list)
    for _, line, formula in source_inline:
        source_by_line[line].append(localized_math(formula, repair_naturality=True))
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
    if tuple(reorder_lines) != (100, 132, 144, 146):
        refuse(f"reviewed formula reorder topology drift: {reorder_lines}")
    inline_pairs = pair_inline_formula_occurrences(source_inline, target_inline)
    if len(inline_pairs) != 144:
        refuse("inline pairing census drift")

    source_brackets = bracket_formula_occurrences(source_text)
    target_brackets = bracket_formula_occurrences(target_text)
    if (
        len(source_brackets) != 6
        or len(target_brackets) != 6
        or tuple(item[:3] for item in source_brackets)
        != tuple(item[:3] for item in target_brackets)
        or tuple(localized_math(item[3]) for item in source_brackets)
        != tuple(localized_math(item[3]) for item in target_brackets)
    ):
        refuse("six bracket-display formula topology drift")
    source_env = environment_formula_occurrences(source_text)
    target_env = environment_formula_occurrences(target_text)
    if (
        len(source_env) != 6
        or len(target_env) != 6
        or tuple(item[:4] for item in source_env) != tuple(item[:4] for item in target_env)
        or tuple(localized_math(item[4]) for item in source_env)
        != tuple(localized_math(item[4]) for item in target_env)
    ):
        refuse("six environment-display formula topology drift")

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
        r"\InputSourceLineRange{chapter3.tex}{306}{511}",
        r"\setstretch{1.16}",
        MODEL,
    ):
        if needle not in driver:
            refuse(f"driver lacks {needle!r}")
    if r"../../build/unit-021-candidate" in driver:
        refuse("public reader driver still depends on the isolated build candidate")
    bibliography = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8", errors="replace")
    if not re.search(r"@[A-Za-z]+\s*\{\s*JS93\s*,", bibliography):
        refuse("bibliography lacks JS93")

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
    for needle in ("PASS", "lines 307", TARGET_SPAN[1], MODEL, *(item[0] for item in CORRECTIONS)):
        if needle not in review:
            refuse(f"source review lacks {needle!r}")
    for needle in (
        "PASS",
        "43 balanced environment pairs",
        "144 dollar-delimited math surfaces",
        "17 `tikzpicture`",
        "6 `tikzcd`",
        *(item[0] for item in CORRECTIONS),
    ):
        if needle not in math_review:
            refuse(f"math review lacks {needle!r}")
    for needle in ("APPLIED TO THE CANONICAL TARGET", MODEL, *(item[0] for item in CORRECTIONS)):
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
    unit_key = "unit/bab-3-struktur-kepang"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/struktur-kepang"
    section_id = uid(section_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)
    source_absolute = lambda line: SOURCE_START + line - 1
    target_absolute = lambda line: TARGET_START + line - 1

    core_specs = (
        ("concept/monoidal-category", "幺半范畴", "kategori monoidal"),
        ("concept/strict-monoidal-category", "严格幺半范畴", "kategori monoidal ketat"),
        ("concept/tensor-product", "张量积", "hasil kali tensor"),
        ("concept/unit-object", "幺对象", "objek satuan"),
        ("concept/associativity-constraint", "结合约束", "kendala asosiativitas"),
        ("concept/unit-constraint", "幺约束", "kendala satuan"),
        ("concept/commutativity-constraint", "交换约束", "kendala komutativitas"),
        ("concept/naturality", "自然性", "naturalitas"),
        ("concept/braiding-monoidal-category", "辫结构", "struktur kepang"),
        ("concept/braided-monoidal-category", "辫幺半范畴", "kategori monoidal berkepang"),
        ("concept/braided-monoidal-functor", "辫幺半函子", "fungtor monoidal berkepang"),
        ("concept/symmetric-monoidal-category", "对称幺半范畴", "kategori monoidal simetris"),
        ("concept/hexagon-axiom", "六角形公理", "aksioma segienam"),
        ("concept/yang-baxter-equation", "杨--Baxter 方程", "persamaan Yang--Baxter"),
        ("concept/module-tensor-product", "模的张量积", "hasil kali tensor modul"),
        ("concept/braid", "辫子", "kepang"),
        ("concept/braid-equivalence", "辫子等价", "ekuivalensi kepang"),
        ("concept/configuration-space", "配置空间 C_n", "ruang konfigurasi C_n"),
        ("concept/artin-braid-group", "Artin 辫群", "grup kepang Artin"),
        ("concept/braid-group", "辫群", "grup kepang"),
        ("concept/braid-category", "辫范畴 Braid", "kategori kepang Braid"),
        ("concept/fundamental-group", "基本群", "grup fundamental"),
        ("concept/symmetric-group", "对称群", "grup simetris"),
        ("concept/braid-juxtaposition", "辫子的并置", "penempatan kepang berdampingan"),
    )
    concepts = [surface_concept(uid, *spec) for spec in core_specs]

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
                f"surface/unit-021/label/{ordinal:03d}",
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
                f"surface/unit-021/reference/{kind}/{ordinal:03d}",
                f"引用 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}",
                f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_absolute(target_line)}",
            )
        )

    for ordinal, (locator, bib_key, line) in enumerate(CITATIONS, 1):
        concepts.append(
            surface_concept(
                uid,
                f"surface/unit-021/citation-occurrence/{ordinal:03d}",
                f"引文出现 {ordinal:03d}: {bib_key}; {locator or '无定位符'}; 源行 {source_absolute(line)}",
                f"kemunculan sitasi {ordinal:03d}: {bib_key}; {locator or 'tanpa lokator'}; baris target {target_absolute(line)}",
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
                f"surface/unit-021/formula/inline/{ordinal:03d}",
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
                f"surface/unit-021/formula/display-bracket/{ordinal:03d}",
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
                f"surface/unit-021/formula/display-environment/{ordinal:03d}",
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
                    f"surface/unit-021/diagram-{kind}/{ordinal:03d}",
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
                f"surface/unit-021/terminology-row/{ordinal:03d}",
                f"术语记录 {ordinal:03d}: {row['source_term']}",
                f"baris terminologi {ordinal:03d}: {row['source_term']} -> {row['target_term']}; "
                f"status admitted; scope {row['scope']}",
            )
        )

    concept_ids = [item["id"] for item in concepts]
    selected_prerequisite_keys = {
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
        "prerequisite/permutations-and-symmetric-groups",
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
        {"language": "zh-Hans", "text": "第三章：幺半范畴；辫结构"},
        {"language": "id-ID", "text": "Bab 3: Kategori Monoidal; Struktur Kepang"},
    ]
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter3.tex:307-512",
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
        key = f"citation/unit-021/{bib_key.casefold()}"
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
        key = f"index-entry/unit-021/{slug}"
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
        key = f"diagram/unit-021/{source_format}-{occurrence:02d}"
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
        "id": uid("build-surface/unit-021-pdf"),
        "stable_key": "build-surface/unit-021-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_021.ps1 -OutputDirectory build/unit-021-replay",
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
            "TikZ braids and tqft libraries",
            "packages loaded by the Unit 021 driver and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    formula_total = len(inline_pairs) + len(source_brackets) + len(source_env)
    qa_admission = {
        "id": uid("qa/unit-021/admission-gate"),
        "stable_key": "qa/unit-021/admission-gate",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and all-page admission of chapter3.tex authority lines "
            "307-512 to target lines 306-511: nine labels, ten ordinary references, three equation "
            "references, two citation occurrences, no list items, seventeen tikzpicture and six tikzcd "
            "structures, twenty-six tikzcd arrows, thirty TikZ nodes, two coordinates, thirty-two draws, "
            "fifteen edge tokens, ten braid commands, three hlines, 144 inline plus six bracket-display "
            f"and six environment-display formula surfaces ({formula_total} total), and eight localized "
            "index entries. O013-LI-U021-COR-001 repairs the naturality-square codomains; "
            "O013-LI-U021-COR-002 corrects the object/braid noun; O013-LI-U021-ED-001 removes a duplicated "
            "source noun. Exactly nine terminology rows are bound with direct-attestation limits intact. "
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
        "id": uid("qa/unit-021/source-review"),
        "stable_key": "qa/unit-021/source-review",
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
        "id": uid("qa/unit-021/math-structure-review"),
        "stable_key": "qa/unit-021/math-structure-review",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Independent mathematical/protected-topology audit of every formula, identifier, reference, citation, index, diagram primitive, and the three declared source repairs.",
        "witness": MATH_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(MATH_REVIEW),
    }
    qa_correction = {
        "id": uid("qa/unit-021/source-corrections"),
        "stable_key": "qa/unit-021/source-corrections",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Separate provenance and deterministic adjudication for O013-LI-U021-COR-001, O013-LI-U021-COR-002, and O013-LI-U021-ED-001.",
        "witness": CORRECTION_REVIEW,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(CORRECTION_REVIEW),
    }
    qa_structure = {
        "id": uid("qa/unit-021/structure-check"),
        "stable_key": "qa/unit-021/structure-check",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Fail-closed machine structure check binds source/candidate/canonical identities, next-section closure, all protected surfaces, three declared repairs, and zero Han residue.",
        "witness": STRUCTURE_GATE,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(STRUCTURE_GATE),
    }
    qa_replay = {
        "id": uid("qa/unit-021/render-replay"),
        "stable_key": "qa/unit-021/render-replay",
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
        "id": uid("qa/unit-021/all-page-visual-review"),
        "stable_key": "qa/unit-021/all-page-visual-review",
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
        "id": uid("qa/unit-021/terminology-control"),
        "stable_key": "qa/unit-021/terminology-control",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Live id-ID glossary binding for exactly nine admitted Unit 021 terminology rows; previously admitted category-theory terms are reused without duplication.",
        "witness": TERMINOLOGY,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY),
    }
    qa_term_evidence = {
        "id": uid("qa/unit-021/terminology-evidence"),
        "stable_key": "qa/unit-021/terminology-evidence",
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "backend_integrity",
        "result": "pass",
        "scope": "Bound terminology adjudication distinguishes direct Indonesian attestation for persamaan Yang--Baxter from transparent corpus choices for kepang-family and category-theory terms; the English loan alternative grup Braid remains recorded without overclaim.",
        "witness": TERMINOLOGY_AUDIT,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": source_binding(TERMINOLOGY_AUDIT),
    }

    data["dataset_stable_key"] = "dataset/unit-021/id-id"
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
        "order": 21,
        "source_local_id": "chapter3.tex:307-512",
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
            "outcome/define-braiding-and-hexagon-axioms",
            "outcome/distinguish-braided-and-symmetric-monoidal-categories",
            "outcome/verify-braided-monoidal-functor-naturality",
            "outcome/derive-the-yang-baxter-equation",
            "outcome/construct-artin-braid-groups-topologically",
            "outcome/construct-the-strict-braided-monoidal-category-braid",
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
                "labels": 9,
                "ordinary_references": 10,
                "equation_references": 3,
                "citation_occurrences": 2,
                "native_bibliography_records": len(citations),
                "items": 0,
                "formula_entities": formula_total,
                "diagrams": len(diagrams),
                "arrows": 26,
                "nodes": 30,
                "coordinates": 2,
                "draws": 32,
                "paths": 0,
                "edges": 15,
                "braids": 10,
                "hlines": 3,
                "index_entries": 8,
                "corrections": 3,
                "terminology_rows": 9,
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
