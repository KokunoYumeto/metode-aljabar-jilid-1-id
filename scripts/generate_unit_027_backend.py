#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 027.

Unit 027 is complete Section 4.3: direct products, semidirect products, and
group extensions.  The shared schema has no native records for TeX
environments, labels, reference occurrences, list items, drawing commands,
protected mathematical zones, terminology rows, or correction provenance, so
those surfaces are represented as deterministic UUIDv5 concept-compatible
entities.  Diagrams and index entries retain their native schema records.
Generation fails closed unless every authority, candidate, canonical target,
terminology, build, rights, review, visual-preflight, and final-reader binding
has its reviewed identity.
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

import check_unit_027_candidate as candidate_check
import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
OUTPUT = ROOT / "backend/data/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.json"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-027-candidate/chapter4-products-group-extensions-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup.tex"
COVER = "repo/source/coverpage-id-unit-027.tex"
CROSSREF = "repo/source/unit-027-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_027.ps1"
CANDIDATE_GATE = "scripts/check_unit_027_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_027_structure.py"
REVIEW = "qa/UNIT_027_INDEPENDENT_REVIEW_20260825.md"
TERMINOLOGY_AUDIT = "qa/UNIT_027_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = "qa/UNIT_027_PREPROMOTION_AUDIT_20260825.md"
TERMINOLOGY_DELTA = "build/unit-027-staging/terminology-delta.csv"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
FINAL_LOG = "qa/UNIT_027_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_027_VISUAL_PREFLIGHT_20260825.md"
VISUAL_REVIEW = "qa/UNIT_027_VISUAL_QA_20260825.md"
STRUCTURE_PDF_QA = "qa/unit-027-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-027-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-027-bab-4-produk-langsung-semilangsung-dan-ekstensi-grup-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

# The frozen authority boundary includes blank separator line 517.  The
# record-aligned target mapping contains only substantive lines 365--516.
SOURCE_START, SOURCE_END = 365, 517
SOURCE_CONTENT_END = 516
TARGET_START, TARGET_END = 366, 517

TEMPLATE_ID = (
    352_612,
    "cceb010d8569c01e9fd7fb4149765da798a0c00409cadeb743a0326d192df29c",
)
SCHEMA_ID = (
    21_358,
    "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3",
)
SOURCE_FULL = (
    154_744,
    "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3",
)
SOURCE_SPAN = (
    10_209,
    "bb7cb2d385018971fe325c417bcafdccd9e92376c02e7cb72d3af038097f8db8",
)
SOURCE_CONTENT_SPAN = (
    10_208,
    "200bb833830f8d76849640ad3ced9a01b11e6b409fb7401c838f2aa7d936d2f3",
)
CANDIDATE_FULL = (
    12_675,
    "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563",
)
TARGET_FULL = (
    166_211,
    "5a4ec3ec5f420c694f7e1207f02a79c558da0f18c6c1f23969856c481f9a7420",
)
TARGET_SPAN = CANDIDATE_FULL
ARTIFACT_ID = (
    97_427,
    "8eeab2d34a745b0e5a12acc29c0c5474e9c84d1248686d743302c03859851dd7",
)
CANDIDATE_GATE_ID = (
    14_054,
    "a98d407c23ce2ae28f3fbe1776387c96b9d2cc4db6c987e089227fbc92fd556e",
)
STRUCTURE_GATE_ID = (
    7_778,
    "40fa1156223922b7581970458322d76fa78b94931a9748153ade58f026880510",
)
REVIEW_ID = (
    6_104,
    "28d0834da4d076a4926ccc10b956c32a3445453567abff9c449ee7eeeae843ef",
)
TERMINOLOGY_AUDIT_ID = (
    4_590,
    "21f794e503efc4c24924e48e0520bff601474c3d8b1e0f0c37fcf0a3d3cbd806",
)
PREPROMOTION_AUDIT_ID = (
    2_998,
    "6486e7cb387fb3a5e1d579bbffc079bb235919b5446f2f5b06ad7e7ce63f6b32",
)
TERMINOLOGY_DELTA_ID = (
    1_959,
    "5a661682e425f53ed0bd25a3f1badd6cdc83b396946901573bcb0c7d8e1a977e",
)
TERMINOLOGY_ID = (
    60_575,
    "61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97",
)
BUILD_SCRIPT_ID = (
    4_932,
    "5287ddeae06ace2c804b4fc24811cbd8318f96480a785b58ee737e6c02196c71",
)
FINAL_LOG_ID = (
    86_569,
    "b18386c3273612276813fa1c9fa00a606becc3d35e980e68351f258bfc893cb4",
)
DRIVER_ID = (
    5_206,
    "724ce2e32023fff81dc3f67cdf34e33557de506891d78eb2566abc4c31f8ce94",
)
COVER_ID = (
    3_689,
    "66e4499e39304e21fbca012bd0941c22a8af497257e7481aaa42b9c20b527b0e",
)
CROSSREF_ID = (
    49,
    "90d0014732a38f49fb82e4e9c1f446ff061ccc1dc6ce230f833e9126d1dfa49b",
)
VISUAL_PREFLIGHT_ID = (
    7_067,
    "a961a6fc301972826901103b7c3ba05baebbc23a5d6cf09291b14bbedb2b8d0d",
)
VISUAL_REVIEW_ID = (
    6_180,
    "370bf47ef7defb494ad3b227f1280f01bcfc081f1c92b0c5ef7986d4dddc95c9",
)
STRUCTURE_PDF_QA_ID = (
    57_622,
    "e43de32df9e1cef83da6fc1539a160de3d093afe6ebedcbf12b7bcd0264cb789",
)
RENDER_HASH_INVENTORY_ID = (
    34_438,
    "2f9e5b102f29b7a3480e80c1db413a547368f1638e9b669f4de7a4e9f685fd15",
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 3,
        "center": 1,
        "compactenum": 1,
        "compactitem": 3,
        "definition": 3,
        "enumerate": 1,
        "example": 1,
        "gather": 1,
        "inparaenum": 1,
        "lemma": 3,
        "proof": 3,
        "tikzcd": 4,
        "tikzpicture": 3,
    }
)

DIAGRAM_SPECS = (
    ("tikzcd", 1, 385, 388, 386, 389),
    ("tikzpicture", 1, 443, 449, 444, 450),
    ("tikzpicture", 2, 449, 455, 450, 456),
    ("tikzpicture", 3, 455, 461, 456, 462),
    ("tikzcd", 2, 497, 500, 498, 501),
    ("tikzcd", 3, 506, 508, 507, 509),
    ("tikzcd", 4, 511, 514, 512, 515),
)

CORE_SPECS = (
    ("concept/direct-product", "直积", "produk langsung", 368),
    ("concept/projection-homomorphism", "投影同态", "homomorfisme proyeksi", 375),
    ("concept/product-universal-property", "积的泛性质", "sifat universal produk", 383),
    ("concept/semidirect-product", "半直积", "produk semilangsung", 397),
    ("concept/conjugation-action", "共轭作用", "aksi konjugasi", 414),
    ("concept/normalizer", "正规化子", "normalisator", 423),
    ("concept/internal-semidirect-product-decomposition", "内半直积分解", "dekomposisi produk semilangsung internal", 465),
    ("concept/dihedral-group", "二面体群", "grup dihedral", 441),
    ("concept/internal-direct-product", "内直积", "produk langsung internal", 477),
    ("concept/exact-sequence", "正合列", "barisan eksak", 483),
    ("concept/exactness-image-kernel", "像与核的正合性", "keeksakan melalui bayangan dan kernel", 486),
    ("concept/group-extension", "群扩张", "ekstensi grup", 496),
    ("concept/equivalence-of-group-extensions", "群扩张的等价", "ekuivalensi ekstensi grup", 501),
    ("concept/splitting-of-extension", "扩张的分裂", "pemecahan ekstensi", 503),
    ("concept/split-extension", "可裂扩张", "ekstensi terpecah", 503),
    ("concept/semidirect-split-extension-correspondence", "半直积与可裂扩张的联系", "korespondensi produk semilangsung dan ekstensi terpecah", 503),
    ("concept/restricted-adjoint-automorphism", "伴随自同构的限制", "pembatasan automorfisme adjoin", 510),
)

TERMINOLOGY_PAIRS = (
    ("projection homomorphism", "homomorfisme proyeksi"),
    ("semidirect product", "produk semilangsung"),
    ("internal semidirect product decomposition", "dekomposisi produk semilangsung internal"),
    ("dihedral group", "grup dihedral"),
    ("internal direct product", "produk langsung internal"),
    ("group extension", "ekstensi grup"),
    ("equivalence of group extensions", "ekuivalensi ekstensi grup"),
    ("splitting (of an extension)", "pemecahan"),
    ("split extension", "ekstensi terpecah"),
)

SOURCE_CORRECTIONS = (
    (
        "O013-LI-U027-COR-001",
        (384,),
        (385,),
        "Replace the undefined codomain M by the direct product required by the component maps and the displayed diagram.",
        "Ganti kodomain M yang tak terdefinisi dengan produk langsung yang ditentukan oleh peta komponen dan diagram.",
    ),
    (
        "O013-LI-U027-COR-002",
        (442,),
        (443,),
        "Restrict only the regular-polygon geometric model to n at least 3 while preserving the wider algebraic definition.",
        "Batasi hanya model geometris poligon beraturan pada n sekurang-kurangnya 3 tanpa mempersempit definisi aljabarnya.",
    ),
)

TRANSLATION_PRECISION = (
    (
        "O013-LI-U027-TR-001",
        (510,),
        (511,),
        "Describe the action as restriction of the adjoint automorphism of G; its restriction to N need not be inner on N.",
        "Nyatakan aksi sebagai pembatasan automorfisme adjoin pada G; pembatasannya pada N tidak harus merupakan automorfisme dalam pada N.",
    ),
)

STYLE_NORMALIZATIONS = (
    ("O013-LI-U027-STYLE-001", 372, 373, "unsur satuan", "unsur identitas"),
    ("O013-LI-U027-STYLE-002", 405, 406, "unsur satuan", "unsur identitas"),
)

PREREQUISITES = (
    "prerequisite/basic-mathematical-literacy",
    "prerequisite/elementary-set-theory",
    "prerequisite/basic-group-theory",
    "prerequisite/group-homomorphisms-kernels-and-quotients",
    "prerequisite/categories-and-morphisms",
    "prerequisite/functors-and-natural-transformations",
    "prerequisite/universal-properties-and-comma-categories",
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-027-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 027 backend refused: " + message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str | Path) -> tuple[int, str]:
    path = relative if isinstance(relative, Path) else ROOT / relative
    payload = path.read_bytes()
    return len(payload), digest(payload)


def require_identity(relative: str | Path, expected: tuple[int, str]) -> None:
    path = relative if isinstance(relative, Path) else ROOT / relative
    if not path.is_file() or identity(path) != expected:
        refuse(f"identity drift for {path.relative_to(ROOT).as_posix()}")


def normalized_span(relative: str, first: int, last: int) -> bytes:
    return common.normalized_span(relative, first, last)


def binding(relative: str, first: int | None = None, last: int | None = None):
    return base.binding(relative, first, last)


def span_text(relative: str, first: int, last: int) -> str:
    return normalized_span(relative, first, last).decode("utf-8")


def line_at(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def normalized_source_content() -> str:
    lines = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END).splitlines()
    if len(lines) != 152:
        refuse("source substantive-record extraction drift")
    return "\n".join(
        candidate_check.apply_declared_source_corrections(line, SOURCE_START + offset)
        for offset, line in enumerate(lines)
    ) + "\n"


def protected_math_occurrences(text: str):
    spans: list[tuple[int, str, str]] = []
    for kind, regex in (
        ("inline", candidate_check.INLINE_MATH_RE),
        ("display-bracket", candidate_check.DISPLAY_MATH_RE),
        ("display-environment", candidate_check.MATH_ENV_RE),
    ):
        for match in regex.finditer(text):
            content = match.group(2) if regex is candidate_check.MATH_ENV_RE else match.group(1)
            spans.append((match.start(), kind, candidate_check.normalize_math(content)))
    return tuple(
        (ordinal, kind, line_at(text, position), value)
        for ordinal, (position, kind, value) in enumerate(sorted(spans), 1)
    )


def drawing_command_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    return tuple(
        (match.group(1), line_at(text, match.start()))
        for match in re.finditer(r"\\(foreach|draw|node)(?![A-Za-z])", text)
    )


def read_terminology_rows() -> tuple[tuple[dict[str, str], int, int], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 383 or len({row.get("source_term") for row in rows}) != 383:
        refuse("controlled glossary row/uniqueness drift")
    with (ROOT / TERMINOLOGY_DELTA).open("r", encoding="utf-8", newline="") as handle:
        delta = tuple(csv.DictReader(handle))
    if len(delta) != 9 or tuple(rows[-9:]) != delta:
        refuse("nine-row Unit 027 glossary delta drift")
    by_source = {row["source_term"]: row for row in rows}
    target_lines = span_text(TARGET, TARGET_START, TARGET_END).splitlines()
    selected = []
    for source_term, target_term in TERMINOLOGY_PAIRS:
        row = by_source.get(source_term)
        if row is None:
            refuse(f"terminology row missing: {source_term!r}")
        if (
            row.get("target_term") != target_term
            or row.get("status") != "admitted"
            or not row.get("scope")
            or not row.get("note")
        ):
            refuse(f"terminology admission drift for {source_term!r}")
        occurrences = [
            offset
            for offset, line in enumerate(target_lines)
            if target_term.casefold() in line.casefold()
        ]
        if not occurrences:
            refuse(f"admitted Unit 027 term absent: {source_term!r} -> {target_term!r}")
        relative = occurrences[0] + 1
        selected.append((row, SOURCE_START + relative - 1, TARGET_START + relative - 1))
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


def gate() -> tuple[int, tuple[tuple[dict[str, str], int, int], ...]]:
    pinned = (
        (TEMPLATE, TEMPLATE_ID),
        (SCHEMA, SCHEMA_ID),
        (SOURCE, SOURCE_FULL),
        (CANDIDATE, CANDIDATE_FULL),
        (TARGET, TARGET_FULL),
        (DRIVER, DRIVER_ID),
        (COVER, COVER_ID),
        (CROSSREF, CROSSREF_ID),
        (BUILD_SCRIPT, BUILD_SCRIPT_ID),
        (CANDIDATE_GATE, CANDIDATE_GATE_ID),
        (STRUCTURE_GATE, STRUCTURE_GATE_ID),
        (REVIEW, REVIEW_ID),
        (TERMINOLOGY_AUDIT, TERMINOLOGY_AUDIT_ID),
        (PREPROMOTION_AUDIT, PREPROMOTION_AUDIT_ID),
        (TERMINOLOGY_DELTA, TERMINOLOGY_DELTA_ID),
        (TERMINOLOGY, TERMINOLOGY_ID),
        (FINAL_LOG, FINAL_LOG_ID),
        (VISUAL_PREFLIGHT, VISUAL_PREFLIGHT_ID),
        (VISUAL_REVIEW, VISUAL_REVIEW_ID),
        (STRUCTURE_PDF_QA, STRUCTURE_PDF_QA_ID),
        (RENDER_HASH_INVENTORY, RENDER_HASH_INVENTORY_ID),
        (ARTIFACT, ARTIFACT_ID),
    )
    for relative, expected in pinned:
        require_identity(relative, expected)

    source_span = normalized_span(SOURCE, SOURCE_START, SOURCE_END)
    source_content = normalized_span(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    target_span = normalized_span(TARGET, TARGET_START, TARGET_END)
    if (len(source_span), digest(source_span)) != SOURCE_SPAN:
        refuse("source boundary span drift")
    if (len(source_content), digest(source_content)) != SOURCE_CONTENT_SPAN:
        refuse("source substantive span drift")
    if source_span != source_content + b"\n":
        refuse("authority line 517 is not exactly the omitted blank boundary record")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("canonical target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    source_records = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_records = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_records) != 1_898 or (ROOT / SOURCE).read_bytes().endswith(b"\n"):
        refuse("authority Chapter 4 record/EOF census drift")
    if len(target_records) != 1_898 or not (ROOT / TARGET).read_bytes().endswith(b"\n"):
        refuse("canonical Chapter 4 record/EOF census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "PASS unit-027 candidate admission",
            (SOURCE_SPAN[1], CANDIDATE_FULL[1], "declared_source_corrections=2", "translation_precision_repairs=1"),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 027 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1], TERMINOLOGY_ID[1], "glossary_rows=383"),
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

    raw_source_text = source_content.decode("utf-8")
    target_text = target_span.decode("utf-8")
    source_env = common.environment_occurrences(raw_source_text)
    target_env = common.environment_occurrences(target_text)
    if (
        [(item[0], item[1], item[2], item[3]) for item in source_env]
        != [(item[0], item[1], item[2], item[3]) for item in target_env]
        or Counter(item[0] for item in source_env) != EXPECTED_ENVIRONMENTS
        or len(source_env) != 28
    ):
        refuse("28-pair textual environment topology drift")

    source_labels = common.label_occurrences(raw_source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 8:
        refuse("eight-label topology drift")
    source_refs = common.reference_occurrences(raw_source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 5:
        refuse("five-reference topology drift")
    if Counter(item[0] for item in source_refs) != Counter({"ordinary": 4, "equation": 1}):
        refuse("ordinary/equation reference census drift")
    if common.citation_occurrences(raw_source_text) or common.citation_occurrences(target_text):
        refuse("unexpected citation surface")
    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if source_items != target_items or len(source_items) != 15:
        refuse("fifteen-item topology drift")

    normalized_source = normalized_source_content()
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    if [item[1:] for item in source_math] != [item[1:] for item in target_math] or len(source_math) != 171:
        refuse("171-zone protected mathematics drift")

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    expected_source_diagrams = tuple(item[:4] for item in DIAGRAM_SPECS)
    expected_target_diagrams = tuple((item[0], item[1], item[4], item[5]) for item in DIAGRAM_SPECS)
    if source_diagrams != expected_source_diagrams or target_diagrams != expected_target_diagrams:
        refuse("seven-diagram topology drift")
    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    if source_arrows != target_arrows or len(source_arrows) != 30:
        refuse("30-arrow tikzcd topology drift")
    source_drawing = drawing_command_occurrences(raw_source_text)
    target_drawing = drawing_command_occurrences(target_text)
    if source_drawing != target_drawing or Counter(item[0] for item in source_drawing) != Counter({"foreach": 6, "draw": 6, "node": 3}):
        refuse("polygon drawing-command topology drift")

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    if len(source_indexes) != 6 or len(target_indexes) != 6 or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]:
        refuse("six-index topology or stream drift")
    if Counter(item[0] for item in source_indexes) != Counter({"main": 5, "sym1": 1}):
        refuse("main/sym1 index census drift")

    for environment in ("Exercises", "exercise", "problem", "hint", "answer", "solution"):
        if f"\\begin{{{environment}}}" in raw_source_text or f"\\begin{{{environment}}}" in target_text:
            refuse(f"invented or unexpected {environment} surface")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 027 target")

    terminology_rows = read_terminology_rows()
    page_count = pdfinfo_page_count()
    if page_count != 7:
        refuse(f"final reader page count drift: {page_count}")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    page_hits = re.findall(r"Output written on .*?\((\d+)\s+pages?", final_log, re.DOTALL)
    if not page_hits or int(page_hits[-1]) != page_count:
        refuse("final build-log page count drift")
    for token in (
        "Undefined control sequence",
        "There were undefined references",
        "Citation `",
        "! LaTeX Error",
        "Emergency stop",
        "Fatal error",
        "Overfull \\hbox",
        "Overfull \\vbox",
    ):
        if token in final_log:
            refuse(f"final build log contains blocker {token!r}")
    visual = (ROOT / VISUAL_PREFLIGHT).read_text(encoding="utf-8")
    for token in ("PASS WITH WARNINGS", MODEL, "seven pages", "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual:
            refuse(f"visual preflight lacks {token!r}")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS WITH WARNINGS", MODEL, "All three PDFs have seven pages", "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual_review:
            refuse(f"canonical visual review lacks {token!r}")

    structure_qa = json.loads((ROOT / STRUCTURE_PDF_QA).read_text(encoding="utf-8"))
    if (
        structure_qa.get("status") != "PASS_WITH_WARNINGS"
        or structure_qa.get("actionable_defects") != []
        or structure_qa.get("cross_pdf_semantic_identity") is not True
        or structure_qa.get("documents", {}).get("artifact", {}).get("identity")
        != {"bytes": ARTIFACT_ID[0], "path": ARTIFACT, "sha256": ARTIFACT_ID[1]}
        or not all(structure_qa.get("documents", {}).get("artifact", {}).get("checks", {}).values())
        or structure_qa.get("final_build_log", {}).get("identity")
        != {"bytes": FINAL_LOG_ID[0], "path": FINAL_LOG, "sha256": FINAL_LOG_ID[1]}
        or any(structure_qa.get("final_build_log", {}).get("fatal_diagnostics", {}).values())
        or structure_qa.get("final_build_log", {}).get("page_marker") != 7
    ):
        refuse("canonical structure-and-PDF QA semantics drift")

    render_inventory = json.loads((ROOT / RENDER_HASH_INVENTORY).read_text(encoding="utf-8"))
    comparisons = render_inventory.get("decoded_pixel_comparisons", {})
    comparison_results = [
        comparisons.get(renderer, {}).get(pair, {}).get("all_7_decoded_pixel_identical")
        for renderer in ("poppler", "mupdf")
        for pair in ("build-c_vs_build-d", "build-d_vs_artifact")
    ]
    manual = render_inventory.get("manual_visual_review", {})
    if (
        render_inventory.get("status") != "PASS_WITH_WARNINGS"
        or render_inventory.get("identities", {}).get("artifact")
        != {"bytes": ARTIFACT_ID[0], "path": ARTIFACT, "sha256": ARTIFACT_ID[1]}
        or render_inventory.get("identities", {}).get("final-build-log")
        != {"bytes": FINAL_LOG_ID[0], "path": FINAL_LOG, "sha256": FINAL_LOG_ID[1]}
        or render_inventory.get("identities", {}).get("build-d_artifact_byte_identical") is not True
        or comparison_results != [True, True, True, True]
        or render_inventory.get("edge_gate") != {"all_42_zero_ink": True, "outer_band_pixels": 3}
        or manual.get("status") != "PASS"
        or manual.get("pages_per_document") != 7
        or manual.get("actionable_defects") != []
        or set(manual.get("renderers", [])) != {"Poppler", "MuPDF"}
        or len(manual.get("findings", {})) != 7
        or len(render_inventory.get("contact_sheets", [])) != 6
    ):
        refuse("canonical render-hash inventory semantics drift")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    if MODEL not in re.sub(r"\s+", " ", terminology_audit):
        refuse("terminology audit lacks exact production-model provenance")
    return page_count, terminology_rows


def main() -> None:
    page_count, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-4-produk-langsung-semilangsung-dan-ekstensi-grup"
    unit_id = uid(unit_key)
    raw_source_text = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    normalized_source = normalized_source_content()
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    prerequisite_key = "prerequisite/group-homomorphisms-kernels-and-quotients"
    if not any(item["stable_key"] == prerequisite_key for item in data["prerequisites"]):
        data["prerequisites"].append(
            {
                "id": uid(prerequisite_key),
                "stable_key": prerequisite_key,
                "entity_type": "prerequisite",
                "labels": [
                    {"language": "zh-Hans", "text": "群同态、核与商群"},
                    {"language": "id-ID", "text": "homomorfisme grup, kernel, dan grup hasil bagi"},
                ],
                "requiredness": "expected",
                "source_evidence": {"path": SOURCE, "line_start": 177, "line_end": 364},
            }
        )

    concepts: list[dict[str, object]] = []

    def add_concept(stable_key: str, source_label: str, target_label: str, *, source_language: str = "zh-Hans") -> None:
        concept = common.surface_concept(uid, stable_key, source_label, target_label)
        concept["labels"][0]["language"] = source_language
        concepts.append(concept)

    for stable_key, source_label, target_label, _ in CORE_SPECS:
        add_concept(stable_key, source_label, target_label)

    source_env = common.environment_occurrences(raw_source_text)
    target_env = common.environment_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-027/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}; state active",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}; keadaan aktif",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.label_occurrences(raw_source_text), common.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-027/label/{ordinal:03d}",
            f"label {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"label {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.reference_occurrences(raw_source_text), common.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-027/reference/{kind}/{ordinal:03d}",
            f"{kind} reference {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-027/item/{ordinal:03d}",
            f"list item {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"butir daftar {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(
            f"surface/unit-027/diagram-arrow/{ordinal:03d}",
            f"tikzcd arrow {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"panah tikzcd {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(drawing_command_occurrences(raw_source_text), drawing_command_occurrences(target_text), strict=True), 1):
        command, source_line = source_item
        target_command, target_line = target_item
        if command != target_command:
            refuse(f"drawing command {ordinal} pairing drift")
        add_concept(
            f"surface/unit-027/polygon-drawing-command/{ordinal:03d}-{command}",
            f"TikZ polygon command {ordinal:03d}: {command}; authority line {SOURCE_START + source_line - 1}",
            f"perintah poligon TikZ {ordinal:03d}: {command}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    for source_item, target_item in zip(source_math, target_math, strict=True):
        ordinal, kind, source_line, source_formula = source_item
        _, target_kind, target_line, target_formula = target_item
        if kind != target_kind or source_formula != target_formula:
            refuse(f"protected math zone {ordinal} pairing drift")
        add_concept(
            f"surface/unit-027/protected-math-zone/{ordinal:03d}-{kind}",
            f"protected {kind} mathematical zone {ordinal:03d}; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"zona matematika terlindungi {kind} {ordinal:03d}; baris target {TARGET_START + target_line - 1}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_language="en",
        )

    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PAIRS[ordinal - 1]
        add_concept(
            f"surface/unit-027/terminology-row/{ordinal:03d}",
            f"terminology row {ordinal:03d}: {source_term}; representative authority line {source_line}",
            f"baris terminologi {ordinal:03d}: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}",
            source_language="en",
        )

    for correction_id, source_lines_abs, target_lines_abs, source_issue, target_issue in SOURCE_CORRECTIONS:
        add_concept(
            f"correction/{correction_id.casefold()}",
            f"declared source correction {correction_id}; authority lines {','.join(map(str, source_lines_abs))}; {source_issue} Evidence: {REVIEW}.",
            f"koreksi sumber terdeklarasi {correction_id}; baris target {','.join(map(str, target_lines_abs))}; {target_issue} Bukti: {REVIEW}.",
            source_language="en",
        )

    for repair_id, source_lines_abs, target_lines_abs, source_issue, target_issue in TRANSLATION_PRECISION:
        add_concept(
            f"translation-precision/{repair_id.casefold()}",
            f"translation-precision repair {repair_id}; authority lines {','.join(map(str, source_lines_abs))}; {source_issue} Evidence: {REVIEW}.",
            f"perbaikan presisi terjemahan {repair_id}; baris target {','.join(map(str, target_lines_abs))}; {target_issue} Bukti: {REVIEW}.",
            source_language="en",
        )

    for style_id, source_line, target_line, prior, admitted in STYLE_NORMALIZATIONS:
        add_concept(
            f"style-normalization/{style_id.casefold()}",
            f"controlled-style normalization {style_id}; authority line {source_line}; accepted synonym {prior} normalized to corpus term {admitted}; evidence {TERMINOLOGY_AUDIT}",
            f"normalisasi gaya terkendali {style_id}; baris target {target_line}; sinonim {prior} dinormalisasi menjadi istilah korpus {admitted}; bukti {TERMINOLOGY_AUDIT}",
            source_language="en",
        )

    add_concept(
        "provenance/o013-li-u027-production",
        f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.",
        f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.",
        source_language="en",
    )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    if not set(PREREQUISITES).issubset(prerequisite_by_key):
        refuse("required Unit 027 prerequisite absent")

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
        binding(SOURCE),
        binding(CANDIDATE),
        binding(TARGET),
        binding("repo/source/LICENSE"),
        binding("repo/source/ccby.png"),
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

    section_key = f"{unit_key}/section/01"
    section_id = uid(section_key)
    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter4.tex:365-517 (line 517 blank boundary omitted from target mapping)",
        "titles": [
            {"language": "zh-Hans", "text": "直积、半直积与群扩张"},
            {"language": "id-ID", "text": "Produk Langsung, Produk Semilangsung, dan Ekstensi Grup"},
        ],
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [prerequisite_by_key[key] for key in PREREQUISITES],
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        stream, source_key, source_line = source_item
        target_stream, target_key, target_line = target_item
        if stream != target_stream:
            refuse(f"index stream drift at ordinal {ordinal}")
        key = f"index-entry/unit-027/{stream}/{ordinal:03d}"
        index_entries.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "index_entry",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_key": source_key,
                "target_key": target_key,
                "source_binding": binding(SOURCE, source_line, source_line),
                "target_binding": binding(TARGET, target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        source_format, occurrence, source_first, source_last = source_diagram
        _, _, target_first, target_last = target_diagram
        key = f"diagram/unit-027/{source_format}-{occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "diagram",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": occurrence,
                "source_binding": binding(SOURCE, source_first, source_last),
                "target_binding": binding(TARGET, target_first, target_last),
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
        "repo/source/ccby.png",
        CROSSREF,
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-027-pdf"),
        "stable_key": "build-surface/unit-027-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_027.ps1 -OutputDirectory build/unit-027-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(FINAL_LOG),
        "build_script": binding(BUILD_SCRIPT),
        "page_count": page_count,
        "status": "pass",
        "driver": binding(DRIVER),
        "input_bindings": [binding(path) for path in inputs],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "makeindex (main and sym1 streams)",
            "Poppler pdfinfo",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 027 driver and AJbook.cls",
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
            "witness_binding": binding(witness),
        }

    qa_events = [
        qa_event(
            "qa/unit-027/admission-gate",
            "admission_gate",
            "Complete source-order Section 4.3 admission: authority lines 365-517 with blank boundary line 517 omitted from the 152-record target mapping; 28 active environment pairs, eight labels, four ordinary and one equation reference, 15 list items, 171 protected mathematical zones, six indexes, four tikzcd diagrams with 30 arrows, three polygon drawings with 15 drawing commands, nine admitted terminology rows, two declared source corrections, one translation-precision repair, two controlled-style normalizations, and no citations, exercises, hints, answers, or solutions. Principal CC BY 4.0 content rights remain separate from AJbook and Noto build-closure licenses; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.",
            VISUAL_REVIEW,
        ),
        qa_event("qa/unit-027/source-review", "backend_integrity", "Exact authority, translation, mathematics, identifiers, diagrams, indexes, corrections, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-027/candidate-artifact", "backend_integrity", "Exact isolated 152-record Indonesian candidate binding; evidence only, not a public-reader build input.", CANDIDATE),
        qa_event("qa/unit-027/candidate-check", "backend_integrity", "Fail-closed candidate checker binding 153 authority records, 152 target records, protected mathematics, diagrams, terminology, two corrections, and one translation-precision repair.", CANDIDATE_GATE),
        qa_event("qa/unit-027/canonical-integration", "backend_integrity", "Fail-closed canonical integration binding prior admitted prefix, Unit 027 candidate, omitted blank boundary, untouched authority suffix, 383-row glossary, and nine-row delta.", STRUCTURE_GATE),
        qa_event("qa/unit-027/source-corrections", "backend_integrity", "Separate deterministic provenance for O013-LI-U027-COR-001 and COR-002; no third source correction is claimed.", REVIEW),
        qa_event("qa/unit-027/translation-precision", "backend_integrity", "O013-LI-U027-TR-001 records that restriction of an adjoint automorphism of G need not be inner on N.", REVIEW),
        qa_event("qa/unit-027/terminology-control", "backend_integrity", "Live id-ID glossary binding for exactly 383 unique rows including the nine admitted Unit 027 rows.", TERMINOLOGY),
        qa_event("qa/unit-027/terminology-delta", "backend_integrity", "Exact reviewed nine-row terminology delta reproduced as the controlled glossary tail without rewriting baseline rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-027/terminology-evidence", "backend_integrity", "Bound Unit 027 terminology audit, two controlled-style normalizations, evidence limits, and exact model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-027/prepromotion-evidence", "backend_integrity", "Exact splice arithmetic for target lines 366-517, omission of authority blank line 517, suffix continuity, and terminology append.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-027/build-log", "backend_integrity", "Final deterministic XeLaTeX and dual-index build log with seven-page output and no fatal, unresolved, or overfull markers.", FINAL_LOG),
        qa_event("qa/unit-027/visual-preflight", "backend_integrity", "Preserved independent all-page Poppler and MuPDF preflight for both clean builds; decoded-pixel, PDF-structure, font, navigation, safety, and exact final-reader identity pass with only documented non-blocking warnings.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-027/structure-and-pdf-qa", "backend_integrity", "Canonical machine-readable PDF structure, metadata, language, destinations, actions, fonts, text geometry, build-log, active-payload, and seven-page checks for the exact final artifact.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-027/render-hash-inventory", "backend_integrity", "Canonical all-page Poppler and MuPDF render identities: 42 renders, four seven-page decoded-pixel comparisons, six contact sheets, and the zero-ink outer-edge gate.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-027/all-page-visual-review", "backend_integrity", "Canonical independent full-resolution review of all seven pages in Poppler and MuPDF; zero actionable defects with documented accessibility and font-subset warnings.", VISUAL_REVIEW),
    ]

    prerequisite_ids = [prerequisite_by_key[key] for key in PREREQUISITES]
    titles = [
        {"language": "zh-Hans", "text": "第四章：直积、半直积与群扩张"},
        {"language": "id-ID", "text": "Bab 4: Produk Langsung, Produk Semilangsung, dan Ekstensi Grup"},
    ]
    data["dataset_stable_key"] = "dataset/unit-027/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u027-backend")),
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
        "order": 27,
        "source_local_id": "chapter4.tex:365-517; substantive record map 365-516",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "section_ids": [section_id],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [
            "outcome/construct-direct-products-and-use-projections",
            "outcome/apply-the-product-universal-property",
            "outcome/construct-and-recognize-semidirect-products",
            "outcome/analyze-dihedral-and-internal-product-decompositions",
            "outcome/test-exactness-and-compare-group-extensions",
            "outcome/relate-split-extensions-to-semidirect-products",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 7,
            "index_entries": 6,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = []
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = qa_events

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
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
            str(SCHEMA),
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
                "sections": 1,
                "concepts": len(concepts),
                "textual_environment_pairs": len(source_env),
                "active_environment_pairs": len(source_env),
                "labels": len(common.label_occurrences(raw_source_text)),
                "references": len(common.reference_occurrences(raw_source_text)),
                "citations": 0,
                "items": len(source_items),
                "protected_math_zones": len(source_math),
                "diagrams": len(diagrams),
                "diagram_arrows": len(source_arrows),
                "drawing_commands": len(drawing_command_occurrences(raw_source_text)),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "source_corrections": len(SOURCE_CORRECTIONS),
                "translation_precision_repairs": len(TRANSLATION_PRECISION),
                "style_normalizations": len(STYLE_NORMALIZATIONS),
                "artifact": {"pages": page_count, "bytes": ARTIFACT_ID[0], "sha256": ARTIFACT_ID[1]},
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
