#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 024.

Unit 024 is the complete Chapter 3 exercise tail. The shared schema has no
first-class exercise, nested-item, hint, formula, TeX-reference occurrence,
diagram primitive, terminology-row, or correction record. Those surfaces are
therefore represented by deterministic UUIDv5 concept-compatible entities,
while diagrams, index entries, rights, build surfaces, and QA events retain
their native records. Nothing is written until the integrated target and the
final reader/build/visual evidence all pass.
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
TEMPLATE = ROOT / "backend/data/unit-023-bab-3-sekilas-tentang-2-kategori.json"
OUTPUT = ROOT / "backend/data/unit-024-bab-3-latihan.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
CANDIDATE = "build/unit-024-candidate/chapter3-exercises-id.tex"
TARGET = "repo/source/chapter3.tex"
DRIVER = "repo/source/unit-024-bab-3-latihan-kategori-monoidal.tex"
COVER = "repo/source/coverpage-id-unit-024.tex"
CROSSREF = "repo/source/unit-024-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_024.ps1"
CANDIDATE_GATE = "scripts/check_unit_024_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_024_structure.py"
EVIDENCE_GENERATOR = "scripts/generate_unit_024_evidence.py"
RENDER_INVENTORY = "qa/unit-024-evidence/render-hash-inventory.json"
STRUCTURE_QA = "qa/unit-024-evidence/structure-and-pdf-qa.json"
REVIEW = "qa/UNIT_024_TRANSLATION_SOURCE_REVIEW_20260824.md"
MATH_REVIEW = "qa/UNIT_024_MATH_STRUCTURE_AUDIT_20260825.md"
VISUAL_REVIEW = "qa/UNIT_024_VISUAL_QA_20260825.md"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_024_TERMINOLOGY_AUDIT_20260824.md"
FINAL_LOG = "qa/UNIT_024_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-024-bab-3-latihan-kategori-monoidal.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

SOURCE_START, SOURCE_END = 873, 911
TARGET_START, TARGET_END = 872, 910
SOURCE_FULL = (
    75_571,
    "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0",
)
SOURCE_SPAN = (
    4_954,
    "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857",
)
CANDIDATE_FULL = (
    6_071,
    "576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a",
)
TARGET_FULL = (
    89_608,
    "443b71b515aef66c6ba8e259e65083604d227370c1ee7ca3ed49bdb5996f45fb",
)
TARGET_SPAN = CANDIDATE_FULL
CANDIDATE_GATE_ID = (
    19_505,
    "920b8b7d143027d29c50e69f63372b91892511bf9bbcaf3b61f3f86889552e02",
)
STRUCTURE_GATE_ID = (
    5_111,
    "4ff95709815806faf623a19841645870267a45094a1a5847fc9ef3adf8bd4868",
)
REVIEW_ID = (
    8_765,
    "901a502b939ab51adc59324a521d6e98d5c71c01d3732d3af05e6dc072fea430",
)
MATH_REVIEW_ID = (
    3_850,
    "c1ad911cc6597998582a99183d657a4524161b34c93027f8bdbc324e947e4efc",
)
TERMINOLOGY_ID = (
    46_585,
    "4fa4c6d2720dd7ab9c4ebe570a1124794bc8282af1b4491201fb61b7b973ce1b",
)
TERMINOLOGY_AUDIT_ID = (
    4_700,
    "bbf87b09d7941b8a9d5e7457725eba6f013e0a07d340082ce59a8345401ef27f",
)

REFERENCES = (
    ("ordinary", "prop:Kelly", 3),
    ("ordinary", "prop:YBE-cat-strict", 10),
    ("ordinary", "eg:Ab-cat", 32),
    ("ordinary", "def:comma-category", 33),
)
ITEM_LINES = (2, 3, 4, 5, 6, 20, 22, 27, 29, 32, 33)
TOP_LEVEL_ITEM_LINES = (2, 3, 4, 5, 6, 20, 32, 33)
NESTED_ITEM_LINES = (22, 27, 29)
HINT_LINES = (2, 3)
DIAGRAM_SPECS = (
    ("tikzcd", 1, 23, 26),
    ("tikzcd", 2, 34, 37),
)
INDEX_SPECS = (("ybe", "main", 18, "YBE"),)
SURFACE_SPECS = (
    ("arrow", r"\\arrow(?![A-Za-z])", 8, "图表箭头", "panah diagram"),
    ("node", r"\\node(?![A-Za-z])", 0, "图表节点", "simpul diagram"),
    ("coordinate", r"\\coordinate(?![A-Za-z])", 0, "图表坐标", "koordinat diagram"),
    ("draw", r"\\draw(?![A-Za-z])", 0, "绘图命令", "perintah gambar"),
    ("path", r"\\path(?![A-Za-z])", 0, "图表路径", "lintasan diagram"),
    ("edge", r"(?<![A-Za-z])edge(?![A-Za-z])", 0, "图表边", "sisi diagram"),
    ("braid", r"\\braid(?![A-Za-z])", 0, "辫图命令", "perintah diagram kepang"),
    ("hline", r"\\hline(?![A-Za-z])", 0, "表格横线", "garis mendatar tabel"),
)
TERMINOLOGY_SPECS = (
    ("Catalan number", "bilangan Catalan", 2),
    ("quantum integrable system", "sistem integrabel kuantum", 10),
    ("Drinfeld center", "pusat Drinfeld", 31),
    ("categorification", "kategorifikasi", 31),
    ("monoid center", "pusat monoid", 31),
    ("functor isomorphism", "isomorfisme natural antarfungtor", 22),
    ("morphism between functors", "transformasi natural", 33),
)
CORRECTIONS = (
    (
        "O013-LI-U024-COR-001",
        877,
        876,
        "The authority's unique objectwise ordinal-sum isomorphisms are not natural for arbitrary order-preserving maps; the target replaces the false symmetry proof demand with an explicit naturality test and counterexample task.",
    ),
)
EXERCISE_SPECS = (
    (1, 874, 874, 873, 873, "Catalan 括号计数", "Pencacahan Tanda Kurung Catalan"),
    (2, 875, 875, 874, 874, "幺元自同态的交换性", "Komutativitas Endomorfisme Objek Satuan"),
    (3, 876, 876, 875, 875, "有限全序集的序数和", "Jumlah Ordinal Himpunan Terurut Total Berhingga"),
    (4, 877, 877, 876, 876, "序数和同构的自然性", "Naturalitas Isomorfisme Jumlah Ordinal"),
    (5, 878, 890, 877, 889, "Yang--Baxter 方程", "Persamaan Yang--Baxter"),
    (6, 892, 903, 891, 902, "Drinfeld 中心", "Pusat Drinfeld"),
    (7, 904, 904, 903, 903, "Ab-充实范畴", "Kategori yang Diperkaya atas Ab"),
    (8, 905, 910, 904, 909, "逗号范畴与 2-胞腔", "Kategori Koma dan 2-Sel"),
)
CORE_SPECS = (
    ("concept/catalan-parenthesization-count", "Catalan 括号计数", "pencacahan tanda kurung Catalan", 1),
    ("concept/unit-endomorphism-commutativity", "幺元自同态的交换性", "komutativitas endomorfisme objek satuan", 2),
    ("concept/ordinal-sum-monoidal-structure", "序数和幺半结构", "struktur monoidal jumlah ordinal", 3),
    ("concept/objectwise-order-isomorphism", "逐对象序同构", "isomorfisme urutan objek demi objek", 4),
    ("concept/naturality-counterexample", "自然性反例", "contoh tandingan naturalitas", 4),
    ("concept/yang-baxter-equation", "Yang--Baxter 方程", "persamaan Yang--Baxter", 5),
    ("concept/yang-baxter-coefficient-equation", "Yang--Baxter 系数方程", "persamaan koefisien Yang--Baxter", 5),
    ("concept/hecke-type-yang-baxter-solution", "Hecke 型解", "solusi Yang--Baxter bertipe Hecke", 5),
    ("concept/drinfeld-center", "Drinfeld 中心", "pusat Drinfeld", 6),
    ("concept/half-braiding", "半辫结构", "struktur setengah kepang", 6),
    ("concept/ab-enrichment", "Ab-充实", "pengayaan atas Ab", 7),
    ("concept/comma-category", "逗号范畴", "kategori koma", 8),
    ("concept/natural-transformation-as-two-cell", "作为 2-胞腔的自然变换", "transformasi natural sebagai 2-sel", 8),
)
PREREQUISITES_BY_EXERCISE = {
    1: (
        "prerequisite/elementary-set-theory",
        "prerequisite/categories-and-morphisms",
    ),
    2: ("prerequisite/categories-and-morphisms",),
    3: (
        "prerequisite/elementary-set-theory",
        "prerequisite/categories-and-morphisms",
    ),
    4: (
        "prerequisite/elementary-set-theory",
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
    ),
    5: (
        "prerequisite/vector-spaces",
        "prerequisite/linear-transformations",
        "prerequisite/categories-and-morphisms",
    ),
    6: (
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
    ),
    7: (
        "prerequisite/elementary-set-theory",
        "prerequisite/categories-and-morphisms",
    ),
    8: (
        "prerequisite/categories-and-morphisms",
        "prerequisite/functors-and-natural-transformations",
        "prerequisite/functor-categories",
        "prerequisite/universal-properties-and-comma-categories",
    ),
}
CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-024-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 024 backend refused: " + message)


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


def source_absolute(relative_line: int) -> int:
    return SOURCE_START + relative_line - 1


def target_absolute(relative_line: int) -> int:
    return TARGET_START + relative_line - 1


def exercise_for_source_line(line: int) -> int:
    for ordinal, first, last, _, _, _, _ in EXERCISE_SPECS:
        if first <= line <= last:
            return ordinal
    refuse(f"no exercise owns authority line {line}")


def read_terminology_rows() -> tuple[tuple[dict[str, str], int], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    selected = []
    for source_term, target_term, relative_line in TERMINOLOGY_SPECS:
        matches = [row for row in rows if row.get("source_term") == source_term]
        if len(matches) != 1:
            refuse(f"terminology row {source_term!r} is not unique")
        row = matches[0]
        if row.get("target_term") != target_term or row.get("status") != "admitted":
            refuse(f"terminology admission drift for {source_term!r}")
        selected.append((row, relative_line))
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
    if evidence.get("status") != "PASS" or evidence.get("unit_id") != "O013-LI-U024":
        refuse("structured QA status/unit drift")
    expected_target = {
        "path": TARGET,
        "bytes": TARGET_FULL[0],
        "sha256": TARGET_FULL[1],
        "line_records": 910,
        "span_lines": "872-910",
        "span_line_records": 39,
        "span_bytes": TARGET_SPAN[0],
        "span_sha256": TARGET_SPAN[1],
        "span_equals_isolated_candidate": True,
        "post_span_suffix_bytes": 0,
        "chapter_complete": True,
    }
    if evidence.get("canonical_target") != expected_target:
        refuse("structured canonical target drift")
    if evidence.get("candidate") != {
        "path": CANDIDATE,
        "bytes": CANDIDATE_FULL[0],
        "sha256": CANDIDATE_FULL[1],
    }:
        refuse("structured candidate identity drift")
    expected_structure = {
        "exercises": 8,
        "nested_items": 3,
        "hints": 2,
        "labels": [],
        "references": [label for _, label, _ in REFERENCES],
        "citations": [],
        "index_entries": 1,
        "environment_counts": {
            "Exercises": 1,
            "hint": 2,
            "cases": 1,
            "itemize": 1,
            "tikzcd": 2,
        },
        "inline_math": 69,
        "bracket_displays": 6,
        "tikzcd": 2,
        "arrows": 8,
        "declared_corrections": [item[0] for item in CORRECTIONS],
    }
    if evidence.get("structure") != expected_structure:
        refuse("structured source/target topology drift")
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
        renders.get("unit_id") != "O013-LI-U024"
        or renders.get("status") != "PASS"
        or renders.get("page_count") != page_count
        or renders.get("provenance_model") != MODEL
    ):
        refuse("render inventory unit/page drift")
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
    checks = evidence.get("checks", {})
    if not isinstance(checks, dict) or len(checks) < 12 or not all(checks.values()):
        refuse("structured PASS-check inventory drift")
    return page_count, artifact_id, log_id


def gate() -> tuple[int, tuple[int, str], tuple[int, str], tuple[tuple[dict[str, str], int], ...]]:
    required = (
        TEMPLATE.relative_to(ROOT).as_posix(),
        CANDIDATE,
        DRIVER,
        COVER,
        CROSSREF,
        BUILD_SCRIPT,
        CANDIDATE_GATE,
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
        refuse("final inputs are missing:\n  - " + "\n  - ".join(missing))

    require_identity(SOURCE, SOURCE_FULL)
    require_identity(CANDIDATE, CANDIDATE_FULL)
    require_identity(TARGET, TARGET_FULL)
    require_identity(CANDIDATE_GATE, CANDIDATE_GATE_ID)
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
    source_lines = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_lines = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_lines) != 911 or len(target_lines) != 910:
        refuse("Chapter 3 line-record census drift")
    if b"".join(source_lines[SOURCE_END:]) != b"" or b"".join(target_lines[TARGET_END:]) != b"":
        refuse("Unit 024 is no longer the Chapter 3 physical EOF")

    for relative, expected_prefix in (
        (CANDIDATE_GATE, "PASS Unit 024 isolated candidate checker"),
        (STRUCTURE_GATE, "PASS Unit 024 canonical structure"),
    ):
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / relative)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if completed.returncode or expected_prefix not in completed.stdout:
            refuse(f"{relative} failed\n" + completed.stdout + completed.stderr)
        for token in (SOURCE_SPAN[1], TARGET_SPAN[1]):
            if token not in completed.stdout:
                refuse(f"{relative} output lacks {token}")

    source_text = source_span.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_env = common.environment_occurrences(source_text)
    target_env = common.environment_occurrences(target_text)
    expected_env_counts = Counter({"Exercises": 1, "hint": 2, "cases": 1, "itemize": 1, "tikzcd": 2})
    if source_env != target_env or Counter(item[0] for item in source_env) != expected_env_counts:
        refuse("seven-environment topology drift")
    if common.label_occurrences(source_text) or common.label_occurrences(target_text):
        refuse("unexpected Unit 024 label")
    if common.reference_occurrences(source_text) != REFERENCES or common.reference_occurrences(target_text) != REFERENCES:
        refuse("four-reference topology drift")
    if common.citation_occurrences(source_text) or common.citation_occurrences(target_text):
        refuse("unexpected Unit 024 citation")
    if common.occurrence_lines(source_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        refuse("source item topology drift")
    if common.occurrence_lines(target_text, r"\\item(?![A-Za-z])") != ITEM_LINES:
        refuse("target item topology drift")
    source_inline = common.inline_formula_occurrences(source_text)
    target_inline = common.inline_formula_occurrences(target_text)
    if source_inline != target_inline or len(source_inline) != 69:
        refuse("69-inline-formula topology drift")
    source_brackets = common.bracket_formula_occurrences(source_text)
    target_brackets = common.bracket_formula_occurrences(target_text)
    if source_brackets != target_brackets or len(source_brackets) != 6:
        refuse("six-display-formula topology drift")
    if common.environment_formula_occurrences(source_text) or common.environment_formula_occurrences(target_text):
        refuse("unexpected equation-like display environment")
    base.SPAN_START = 1
    if base.diagram_occurrences(source_text) != DIAGRAM_SPECS or base.diagram_occurrences(target_text) != DIAGRAM_SPECS:
        refuse("two-diagram topology drift")
    source_indexes = base.index_occurrences(source_text)
    target_indexes = base.index_occurrences(target_text)
    if source_indexes != (("main", "YBE", 18),) or target_indexes != source_indexes:
        refuse("single-index topology drift")
    for kind, pattern, expected, _, _ in SURFACE_SPECS:
        source_hits = common.occurrence_lines(source_text, pattern)
        target_hits = common.occurrence_lines(target_text, pattern)
        if source_hits != target_hits or len(source_hits) != expected:
            refuse(f"{expected}-{kind} topology drift")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", target_text):
        refuse("Han residue remains in Unit 024 target")

    terms = read_terminology_rows()
    for row, relative_line in terms:
        if row["target_term"] not in target_text.splitlines()[relative_line - 1]:
            refuse(f"candidate line does not use terminology row {row['source_term']!r}")
    review = (ROOT / REVIEW).read_text(encoding="utf-8")
    math_review = (ROOT / MATH_REVIEW).read_text(encoding="utf-8")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    for token in ("PASS", "873–911", MODEL, CORRECTIONS[0][0]):
        if token not in review:
            refuse(f"source review lacks {token!r}")
    for token in ("PASS", "eight top-level exercises", "69 position- and value-identical", "two byte-identical `tikzcd`", MODEL, CORRECTIONS[0][0]):
        if token not in math_review:
            refuse(f"mathematics review lacks {token!r}")
    for source_term, target_term, _ in TERMINOLOGY_SPECS:
        if source_term not in terminology_audit or target_term not in terminology_audit:
            refuse(f"terminology audit lacks {source_term!r} / {target_term!r}")

    page_count, artifact_id, log_id = gate_structured_evidence()
    if pdfinfo_page_count() != page_count:
        refuse("live PDF page count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+)\s+pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != page_count:
        refuse("final log page count drift")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS", str(page_count), "Poppler", "MuPDF", artifact_id[1]):
        if token not in visual_review:
            refuse(f"visual review lacks {token!r}")
    return page_count, artifact_id, log_id, terms


def main() -> None:
    page_count, artifact_id, log_id, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-3-latihan"
    unit_id = uid(unit_key)
    source_text = span_text(SOURCE, SOURCE_START, SOURCE_END)
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    concepts: list[dict[str, object]] = []
    concept_exercises: dict[str, set[int]] = {}
    concept_lines: dict[str, int] = {}

    def add_concept(
        stable_key: str,
        source_label: str,
        target_label: str,
        *,
        exercise: int | None = None,
        relative_line: int | None = None,
        source_language: str = "zh-Hans",
        target_language: str = "id-ID",
    ) -> None:
        concept = common.surface_concept(uid, stable_key, source_label, target_label)
        concept["labels"][0]["language"] = source_language
        concept["labels"][1]["language"] = target_language
        concepts.append(concept)
        if exercise is not None:
            concept_exercises.setdefault(stable_key, set()).add(exercise)
        if relative_line is not None:
            concept_lines[stable_key] = relative_line

    for stable_key, source_label, target_label, exercise in CORE_SPECS:
        add_concept(stable_key, source_label, target_label, exercise=exercise)

    for ordinal, (source_item, target_item) in enumerate(
        zip(common.environment_occurrences(source_text), common.environment_occurrences(target_text), strict=True), 1
    ):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-024/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"环境 {ordinal:03d}: {environment} 第 {occurrence} 次; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}",
            f"lingkungan {ordinal:03d}: {environment} kemunculan {occurrence}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}",
            relative_line=source_first,
        )

    for ordinal, (source_item, target_item) in enumerate(
        zip(common.reference_occurrences(source_text), common.reference_occurrences(target_text), strict=True), 1
    ):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-024/reference/{kind}/{ordinal:03d}",
            f"引用 {ordinal:03d}: {label}; 源行 {source_absolute(source_line)}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {target_absolute(target_line)}",
            relative_line=source_line,
        )

    for ordinal, relative_line in enumerate(ITEM_LINES, 1):
        add_concept(
            f"surface/unit-024/item/{ordinal:03d}",
            f"列表项 {ordinal:03d}; 源行 {source_absolute(relative_line)}",
            f"butir daftar {ordinal:03d}; baris target {target_absolute(relative_line)}",
            relative_line=relative_line,
        )
    for ordinal, relative_line in enumerate(TOP_LEVEL_ITEM_LINES, 1):
        add_concept(
            f"surface/unit-024/exercise/{ordinal:03d}",
            f"顶层习题 {ordinal}; 源行 {source_absolute(relative_line)}",
            f"latihan tingkat atas {ordinal}; baris target {target_absolute(relative_line)}",
            exercise=ordinal,
        )
    for ordinal, relative_line in enumerate(NESTED_ITEM_LINES, 1):
        add_concept(
            f"surface/unit-024/nested-item/{ordinal:03d}",
            f"嵌套项目 {ordinal}; 源行 {source_absolute(relative_line)}",
            f"butir bersarang {ordinal}; baris target {target_absolute(relative_line)}",
            relative_line=relative_line,
        )
    for ordinal, relative_line in enumerate(HINT_LINES, 1):
        add_concept(
            f"surface/unit-024/hint/{ordinal:03d}",
            f"提示 {ordinal}; 源行 {source_absolute(relative_line)}",
            f"petunjuk {ordinal}; baris target {target_absolute(relative_line)}",
            relative_line=relative_line,
        )

    inline_pairs = common.pair_inline_formula_occurrences(
        common.inline_formula_occurrences(source_text), common.inline_formula_occurrences(target_text)
    )
    for source_item, target_item in inline_pairs:
        ordinal, source_line, source_formula = source_item
        _, target_line, target_formula = target_item
        add_concept(
            f"surface/unit-024/formula/inline/{ordinal:03d}",
            f"行内公式 {ordinal:03d}; 源行 {source_absolute(source_line)}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"rumus sebaris {ordinal:03d}; baris target {target_absolute(target_line)}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            relative_line=source_line,
        )
    source_brackets = common.bracket_formula_occurrences(source_text)
    target_brackets = common.bracket_formula_occurrences(target_text)
    for source_item, target_item in zip(source_brackets, target_brackets, strict=True):
        ordinal, source_first, source_last, source_formula = source_item
        _, target_first, target_last, target_formula = target_item
        add_concept(
            f"surface/unit-024/formula/display-bracket/{ordinal:03d}",
            f"陈列公式 {ordinal:03d}; 源行 {source_absolute(source_first)}-{source_absolute(source_last)}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"rumus pajang {ordinal:03d}; baris target {target_absolute(target_first)}-{target_absolute(target_last)}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            relative_line=source_first,
        )
    for kind, pattern, _, source_name, target_name in SURFACE_SPECS:
        source_lines = common.occurrence_lines(source_text, pattern)
        target_lines = common.occurrence_lines(target_text, pattern)
        for ordinal, (source_line, target_line) in enumerate(zip(source_lines, target_lines, strict=True), 1):
            add_concept(
                f"surface/unit-024/diagram-{kind}/{ordinal:03d}",
                f"{source_name} {ordinal:03d}; 源行 {source_absolute(source_line)}",
                f"{target_name} {ordinal:03d}; baris target {target_absolute(target_line)}",
                relative_line=source_line,
            )
    for row, relative_line in terminology_rows:
        ordinal = next(index for index, spec in enumerate(TERMINOLOGY_SPECS, 1) if spec[0] == row["source_term"])
        add_concept(
            f"surface/unit-024/terminology-row/{ordinal:03d}",
            f"terminology row {ordinal:03d}: {row['source_term']}",
            f"baris terminologi {ordinal:03d}: {row['source_term']} -> {row['target_term']}; status admitted; scope {row['scope']}",
            relative_line=relative_line,
            source_language="en",
        )
    for correction_id, source_line, target_line, issue in CORRECTIONS:
        add_concept(
            f"correction/{correction_id.casefold()}",
            f"declared source correction {correction_id}; source line {source_line}; target line {target_line}; {issue} Evidence: {REVIEW}.",
            f"koreksi sumber terdeklarasi {correction_id}; baris sumber {source_line}; baris target {target_line}; isomorfisme jumlah ordinal tunggal pada setiap pasangan objek tidak natural terhadap semua pemetaan yang mempertahankan urutan; target mengganti tuntutan pembuktian simetri yang keliru dengan uji naturalitas dan tugas contoh tandingan eksplisit. Bukti: {REVIEW}.",
            exercise=4,
            source_language="en",
        )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")
    for key, relative_line in concept_lines.items():
        if relative_line not in (1, 39):
            concept_exercises.setdefault(key, set()).add(exercise_for_source_line(source_absolute(relative_line)))

    prerequisite_keys = {
        key for keys in PREREQUISITES_BY_EXERCISE.values() for key in keys
    }
    prerequisite_by_key = {
        item["stable_key"]: item["id"] for item in data["prerequisites"]
    }
    prerequisite_ids = [
        item["id"] for item in data["prerequisites"] if item["stable_key"] in prerequisite_keys
    ]
    if len(prerequisite_ids) != len(prerequisite_keys):
        refuse("prerequisite inventory drift")

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
    for ordinal, source_first, source_last, target_first, target_last, source_title, target_title in EXERCISE_SPECS:
        section_key = f"{unit_key}/exercise/{ordinal:02d}"
        local_keys = [key for key, exercises in concept_exercises.items() if ordinal in exercises]
        sections.append(
            {
                "id": uid(section_key),
                "stable_key": section_key,
                "entity_type": "section",
                "parent_id": unit_id,
                "order": ordinal,
                "source_local_id": f"chapter3.tex:{source_first}-{source_last}",
                "titles": [
                    {"language": "zh-Hans", "text": f"练习 {ordinal}：{source_title}"},
                    {"language": "id-ID", "text": f"Latihan {ordinal}: {target_title}"},
                ],
                "source_binding": source_binding(SOURCE, source_first, source_last),
                "target_binding": target_binding(target_first, target_last),
                "concept_ids": [concept_by_key[key] for key in local_keys],
                "prerequisite_ids": [
                    prerequisite_by_key[key]
                    for key in PREREQUISITES_BY_EXERCISE[ordinal]
                ],
                "rights_component_ids": [principal],
                "translation_state": "visually_checked",
                "admission_state": "admitted",
            }
        )
    section_by_exercise = {index: section["id"] for index, section in enumerate(sections, 1)}

    base.SPAN_START = 1
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(
        zip(base.diagram_occurrences(source_text), base.diagram_occurrences(target_text), strict=True), 1
    ):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-024/{source_format}-{occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_by_exercise[exercise_for_source_line(source_absolute(source_first))],
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": occurrence,
                "source_binding": source_binding(SOURCE, source_absolute(source_first), source_absolute(source_last)),
                "target_binding": target_binding(target_absolute(target_first), target_absolute(target_last)),
                "rights_component_id": principal,
                "state": "audited_preserved",
            }
        )
    index_entries = [
        {
            "id": uid("index-entry/unit-024/ybe"),
            "stable_key": "index-entry/unit-024/ybe",
            "entity_type": "index_entry",
            "section_id": section_by_exercise[5],
            "ordinal_in_unit": 1,
            "source_key": "YBE",
            "target_key": "YBE",
            "source_binding": source_binding(SOURCE, 890, 890),
            "target_binding": target_binding(889, 889),
            "provenance_state": "source_key_preserved_target_key_localized",
        }
    ]

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
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-024-pdf"),
        "stable_key": "build-surface/unit-024-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_024.ps1 -OutputDirectory build/unit-024-replay",
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
            "makeindex (default index)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "TikZ and tikz-cd",
            "packages loaded by the Unit 024 driver and AJbook.cls",
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
            "qa/unit-024/admission-gate",
            "admission_gate",
            "Complete source-order Chapter 3 exercise-tail admission: eight exercises, three nested items, two hints, four ordinary references, one index entry, 69 inline and six bracket-display formulas, two tikzcd diagrams and eight arrows, seven admitted terminology rows, and correction O013-LI-U024-COR-001. No labels, equation references, citations, answers, or solutions are invented. Component rights remain separate. Production provenance is " + MODEL + ", separate from Wen-Wei Li's authorship and human credits.",
            STRUCTURE_QA,
        ),
        qa_event(
            "qa/unit-024/source-review",
            "backend_integrity",
            "Independent continuous source and mathematical review of the complete Chapter 3 exercise tail, including every exercise, nested item, hint, formula, reference, index, diagram, and the disclosed correction.",
            REVIEW,
        ),
        qa_event(
            "qa/unit-024/math-structure-review",
            "backend_integrity",
            "Canonical mathematical-structure audit binding all exercises, nested items, hints, references, formulas, index and diagram topology, the integrated Chapter 3 EOF, and the disclosed correction.",
            MATH_REVIEW,
        ),
        qa_event(
            "qa/unit-024/source-correction",
            "backend_integrity",
            "Deterministic provenance for O013-LI-U024-COR-001: the false ordinal-sum symmetry demand is replaced by a naturality decision and counterexample task without changing the true objectwise-isomorphism statement.",
            REVIEW,
        ),
        qa_event(
            "qa/unit-024/structure-check",
            "backend_integrity",
            "Fail-closed candidate and canonical integration checks bind the authority EOF, exact integrated target, exercise/hint/item/formula/reference/index/diagram topology, correction, and zero Han residue.",
            STRUCTURE_GATE,
        ),
        qa_event(
            "qa/unit-024/render-replay",
            "backend_integrity",
            "Deterministic semantic and same-renderer Poppler/MuPDF replay with complete page inventories.",
            RENDER_INVENTORY,
        ),
        qa_event(
            "qa/unit-024/all-page-visual-review",
            "backend_integrity",
            "Independent all-page visual review of the final reader in Poppler and MuPDF after final reflow.",
            VISUAL_REVIEW,
        ),
        qa_event(
            "qa/unit-024/terminology-control",
            "backend_integrity",
            "Live id-ID glossary binding for exactly seven admitted Unit 024 terminology rows.",
            TERMINOLOGY,
        ),
        qa_event(
            "qa/unit-024/terminology-evidence",
            "backend_integrity",
            "Bound Unit 024 terminology promotion audit, including schema, uniqueness, semantic-alias, candidate-occurrence, and exact hash evidence.",
            TERMINOLOGY_AUDIT,
        ),
    ]

    titles = [
        {"language": "zh-Hans", "text": "第三章：习题"},
        {"language": "id-ID", "text": "Bab 3: Latihan"},
    ]
    data["dataset_stable_key"] = "dataset/unit-024/id-id"
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
        "order": 24,
        "source_local_id": "chapter3.tex:873-911",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": source_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": target_binding(TARGET_START, TARGET_END),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [
            "outcome/count-parenthesizations-by-catalan-numbers",
            "outcome/prove-unit-endomorphism-commutativity",
            "outcome/build-and-test-the-ordinal-sum-monoidal-structure",
            "outcome/derive-and-verify-yang-baxter-solutions",
            "outcome/construct-the-drinfeld-center-and-its-braiding",
            "outcome/verify-ab-enrichment",
            "outcome/construct-a-comma-category-natural-transformation-as-two-cell",
        ],
        "surface_counts": {
            "sections": 8,
            "exercises": 8,
            "hints": 2,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 2,
            "index_entries": 1,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = []
    data["diagrams"] = diagrams
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
                "entities": 5 + len(sections) + len(concepts) + len(data["prerequisites"]) + len(data["rights"]) + len(diagrams) + len(index_entries) + 1 + len(qa_events),
                "concepts": len(concepts),
                "exercises": 8,
                "nested_items": 3,
                "hints": 2,
                "references": 4,
                "formula_entities": len(inline_pairs) + len(source_brackets),
                "diagrams": len(diagrams),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "corrections": len(CORRECTIONS),
                "artifact": {"pages": page_count, "bytes": artifact_id[0], "sha256": artifact_id[1]},
                "final_log": {"bytes": log_id[0], "sha256": log_id[1]},
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
