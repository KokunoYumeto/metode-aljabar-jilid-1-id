#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 028.

Unit 028 is complete Section 4.4: group actions and the counting principle.
The shared schema has no native records for TeX environments, labels,
reference/citation occurrences, list items, protected mathematical zones,
terminology rows, correction provenance, or protected-text localizations, so
those surfaces are represented as deterministic UUIDv5 concept-compatible
entities.  The one TikZ-cd diagram, bibliography citations, and index entries
retain their native schema records.
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

import check_unit_028_candidate as candidate_check
import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
OUTPUT = ROOT / "backend/data/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.json"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-028-candidate/chapter4-group-actions-counting-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan.tex"
COVER = "repo/source/coverpage-id-unit-028.tex"
CROSSREF = "repo/source/unit-028-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_028.ps1"
CANDIDATE_GATE = "scripts/check_unit_028_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_028_structure.py"
REVIEW = "qa/UNIT_028_INDEPENDENT_REVIEW_20260825.md"
TERMINOLOGY_AUDIT = "qa/UNIT_028_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = "qa/UNIT_028_PREPROMOTION_AUDIT_20260825.md"
TERMINOLOGY_DELTA = "build/unit-028-staging/terminology-delta.csv"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
FINAL_LOG = "qa/UNIT_028_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_028_VISUAL_PREFLIGHT_20260825.md"
VISUAL_REVIEW = "qa/UNIT_028_VISUAL_QA_20260825.md"
STRUCTURE_PDF_QA = "qa/unit-028-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-028-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-028-bab-4-aksi-grup-dan-prinsip-pencacahan-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

# The frozen authority boundary includes blank separator line 665.  The
# record-aligned target mapping contains only substantive lines 518--664.
SOURCE_START, SOURCE_END = 518, 665
SOURCE_CONTENT_END = 664
TARGET_START, TARGET_END = 518, 664

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
    10_550,
    "af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db",
)
SOURCE_CONTENT_SPAN = (
    10_549,
    "f28c472e1d40f0fcbc6c40262002f4bda50563040cdda0321f1169580039f399",
)
CANDIDATE_FULL = (
    13_017,
    "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd",
)
TARGET_FULL = (
    168_678,
    "33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3",
)
TARGET_SPAN = CANDIDATE_FULL
ARTIFACT_ID = (
    108_689,
    "50c40ddefa870866568f8d1621d5fc204a1fd0fd0a45bdfc74659197c585790a",
)
BIBLIOGRAPHY_ID = (
    29_580,
    "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e",
)
CANDIDATE_GATE_ID = (
    14_671,
    "be2674c75fb17bf8dd8de43d4dd0230fd049f2b5640c72aa372aecc1742d1527",
)
STRUCTURE_GATE_ID = (
    10_010,
    "b1b3812cfe250a3f4ba3bcfa216927ff43158cdab8a08c6a31f7b1942f6a90b4",
)
REVIEW_ID = (
    5_051,
    "2fc54f16ba0da2ca280772bd986c2c7c8e44561d71e80ac7ec6419ed10734b0d",
)
TERMINOLOGY_AUDIT_ID = (
    3_981,
    "d10146b85cb798ad78e8a0c153ade50ebe80cb1fdd60fc15128e92ebc54f722a",
)
PREPROMOTION_AUDIT_ID = (
    4_289,
    "590c4d404ad8d48d925484d55fe15e0ed75b6694a4c6b8effde61d9c3fe690fe",
)
TERMINOLOGY_DELTA_ID = (
    4_052,
    "601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7",
)
TERMINOLOGY_ID = (
    64_585,
    "fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7",
)
BUILD_SCRIPT_ID = (
    5_848,
    "eaa5b98bfd96690add2635aee6e180a1ec220a110d047a9b12536c6a6239f4a2",
)
FINAL_LOG_ID = (
    78_086,
    "e34377e726cef55c50ead5b7a5e056ca332d653b0603a3e214f7b56d44594120",
)
DRIVER_ID = (
    6_077,
    "883ae7140934727fbc6ae90b6d3195b9285a3f0de1d99f04d668bc23515eb3fe",
)
COVER_ID = (
    3_690,
    "0785896485fb7cc92dca4a42f4bdb651f3c4c1cdadc5c30a3b0860812c2ba7cd",
)
CROSSREF_ID = (
    200,
    "f8cf71f988d1027e344d3a13547149ba2b877c79c55d76fc16c393b703ba852b",
)
VISUAL_PREFLIGHT_ID = (
    4_962,
    "ba49035f77ee3b96b3f5cbe9cafb71eade735225f43018aab1f5edd87287fda1",
)
VISUAL_REVIEW_ID = (
    6_209,
    "5ef33e044cd6c4e0b7cde33432a238d00ad835804ec4edbd7fd2deb7623bde73",
)
STRUCTURE_PDF_QA_ID = (
    55_099,
    "e3907e0035f514b44180c6796ab44b5980ddd58c7110e1f7f6e4c4217d4d3426",
)
RENDER_HASH_INVENTORY_ID = (
    35_181,
    "c622cde057eff3a70e0301d60fc6b46d3b3924153d7c01c2d4b7a206427ac310",
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 2,
        "cases": 1,
        "compactenum": 2,
        "compactitem": 2,
        "definition": 3,
        "example": 6,
        "gather*": 1,
        "inparaenum": 1,
        "lemma": 2,
        "proof": 2,
        "remark": 1,
        "tikzcd": 1,
    }
)

DIAGRAM_SPECS = (
    ("tikzcd", 1, 532, 534, 532, 534),
)

CITATION_SPECS = (
    ("例 7.2.4", "Contoh 7.2.4", "Zh2", 561),
    ("例 3.2.7", "Contoh 3.2.7", "Zh1", 561),
)

CORE_SPECS = (
    ("concept/monoid-action", "幺半群作用", "aksi monoid", 521),
    ("concept/action-map", "作用映射", "pemetaan aksi", 522),
    ("concept/m-set", "M-集", "himpunan-M", 530),
    ("concept/equivariant-map", "等变映射", "pemetaan ekuivarian", 530),
    ("concept/equivariant-isomorphism", "等变同构", "isomorfisme ekuivarian", 531),
    ("concept/left-and-right-action", "左作用与右作用", "aksi kiri dan aksi kanan", 550),
    ("concept/fixed-point", "不动点", "titik tetap", 575),
    ("concept/orbit", "轨道", "orbit", 576),
    ("concept/stabilizer", "稳定化子", "stabilisator", 577),
    ("concept/orbit-decomposition", "轨道分解", "dekomposisi orbit", 586),
    ("concept/orbit-stabilizer-cardinality", "轨道稳定化子基数公式", "rumus kardinal orbit-stabilisator", 593),
    ("concept/faithful-action", "忠实作用", "aksi setia", 607),
    ("concept/free-action", "自由作用", "aksi bebas", 608),
    ("concept/transitive-action", "传递作用", "aksi transitif", 609),
    ("concept/n-transitive-action", "n-传递作用", "aksi n-transitif", 610),
    ("concept/homogeneous-space", "齐性空间", "ruang homogen", 613),
    ("concept/torsor", "挠子", "torsor", 613),
    ("concept/translation-action", "平移作用", "aksi translasi", 619),
    ("concept/double-coset-action", "双陪集作用", "aksi koset ganda", 629),
    ("concept/conjugation-action", "共轭作用", "aksi konjugasi", 633),
    ("concept/conjugacy-class", "共轭类", "kelas konjugasi", 637),
    ("concept/centralizer-and-center", "中心化子与中心", "sentralisator dan pusat", 640),
    ("concept/bitorsor", "双挠子", "bitorsor", 644),
    ("concept/torsor-bijection-criterion", "挠子的双射判据", "kriteria bijektif torsor", 654),
)

TERMINOLOGY_PAIRS = (
    ("group action", "aksi grup"),
    ("monoid action", "aksi monoid"),
    ("action map", "pemetaan aksi"),
    ("M-set", "himpunan-M"),
    ("trivial action", "aksi trivial"),
    ("equivariant map", "pemetaan ekuivarian"),
    ("left action", "aksi kiri"),
    ("right action", "aksi kanan"),
    ("fixed point", "titik tetap"),
    ("orbit", "orbit"),
    ("stabilizer", "stabilisator"),
    ("orbit decomposition", "dekomposisi orbit"),
    ("orbit space", "ruang orbit"),
    ("faithful action", "aksi setia"),
    ("free action", "aksi bebas"),
    ("semiregular action", "aksi semireguler"),
    ("transitive action", "aksi transitif"),
    ("n-transitive action", "aksi n-transitif"),
    ("homogeneous space", "ruang homogen"),
    ("principal homogeneous space", "ruang homogen utama"),
    ("torsor", "torsor"),
    ("translation action", "aksi translasi"),
    ("conjugation action", "aksi konjugasi"),
    ("conjugacy class", "kelas konjugasi"),
    ("bitorsor", "bitorsor"),
)

TERMINOLOGY_EVIDENCE = {
    "M-set": "himpunan-$M$",
    "faithful action": "setia",
    "free action": "bebas",
    "semiregular action": "semireguler",
    "transitive action": "transitif",
    "n-transitive action": "$n$-transitif",
}

SOURCE_CORRECTIONS = (
    (
        "O013-LI-U028-COR-001",
        (533, 535),
        (533, 535),
        "Restore the declared objects X and Y in the inverse-map diagram and identity subscripts, replacing undefined M_1 and M_2.",
        "Pulihkan objek X dan Y yang telah dideklarasikan pada diagram pemetaan invers dan subskrip identitas, menggantikan M_1 dan M_2 yang tak terdefinisi.",
    ),
)

PROTECTED_TEXT_LOCALIZATIONS = (
    ("O013-LI-U028-LOC-001", 557, 557, "映射", "pemetaan"),
    ("O013-LI-U028-LOC-002", 610, 610, "相异元", "unsur-unsur berbeda"),
    ("O013-LI-U028-LOC-003", 646, 646, "同构", "isomorfisme"),
)

PREREQUISITES = (
    "prerequisite/basic-mathematical-literacy",
    "prerequisite/elementary-set-theory",
    "prerequisite/basic-group-theory",
    "prerequisite/group-homomorphisms-kernels-and-quotients",
    "prerequisite/categories-and-morphisms",
    "prerequisite/permutations-and-symmetric-groups",
    "prerequisite/real-analysis-basics",
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-028-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 028 backend refused: " + message)


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
    if len(lines) != 147:
        refuse("source substantive-record extraction drift")
    return "\n".join(
        candidate_check.normalize_authority_line(line, SOURCE_START + offset)
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
    if len(rows) != 408 or len({row.get("source_term") for row in rows}) != 408:
        refuse("controlled glossary row/uniqueness drift")
    with (ROOT / TERMINOLOGY_DELTA).open("r", encoding="utf-8", newline="") as handle:
        delta = tuple(csv.DictReader(handle))
    if len(delta) != 25 or tuple(rows[-25:]) != delta:
        refuse("25-row Unit 028 glossary delta drift")
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
        evidence_fragment = TERMINOLOGY_EVIDENCE.get(source_term, target_term)
        occurrences = [
            offset
            for offset, line in enumerate(target_lines)
            if evidence_fragment.casefold() in line.casefold()
        ]
        if not occurrences:
            refuse(f"admitted Unit 028 term absent: {source_term!r} -> {target_term!r}")
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
        (BIBLIOGRAPHY, BIBLIOGRAPHY_ID),
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
        refuse("authority line 665 is not exactly the omitted blank boundary record")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("canonical target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    source_records = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_records = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_records) != 1_898 or (ROOT / SOURCE).read_bytes().endswith(b"\n"):
        refuse("authority Chapter 4 record/EOF census drift")
    if len(target_records) != 1_897 or not (ROOT / TARGET).read_bytes().endswith(b"\n"):
        refuse("canonical Chapter 4 record/EOF census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "PASS unit-028 candidate admission",
            (SOURCE_SPAN[1], CANDIDATE_FULL[1], "declared_source_corrections=1", "protected_text_localizations=3"),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 028 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1], TERMINOLOGY_ID[1], "glossary_rows=408", "delta_rows=25"),
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
        or len(source_env) != 24
    ):
        refuse("24-pair textual environment topology drift")

    source_labels = common.label_occurrences(raw_source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 5:
        refuse("five-label topology drift")
    source_refs = common.reference_occurrences(raw_source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 8:
        refuse("eight-reference topology drift")
    if Counter(item[0] for item in source_refs) != Counter({"ordinary": 7, "equation": 1}):
        refuse("ordinary/equation reference census drift")
    source_citations = common.citation_occurrences(raw_source_text)
    target_citations = common.citation_occurrences(target_text)
    if (
        tuple(
            (source_note, target_note, source_key, SOURCE_START + source_line - 1)
            for (source_note, source_key, source_line), (target_note, target_key, target_line)
            in zip(source_citations, target_citations, strict=True)
            if source_key == target_key and source_line == target_line
        )
        != CITATION_SPECS
    ):
        refuse("two-citation topology or Zh2/Zh1 key closure drift")
    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if source_items != target_items or len(source_items) != 16:
        refuse("16-item topology drift")

    normalized_source = normalized_source_content()
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    if [item[1:] for item in source_math] != [item[1:] for item in target_math] or len(source_math) != 213:
        refuse("213-zone protected mathematics drift")

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    expected_source_diagrams = tuple(item[:4] for item in DIAGRAM_SPECS)
    expected_target_diagrams = tuple((item[0], item[1], item[4], item[5]) for item in DIAGRAM_SPECS)
    if source_diagrams != expected_source_diagrams or target_diagrams != expected_target_diagrams:
        refuse("one-diagram topology drift")
    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    if source_arrows != target_arrows or len(source_arrows) != 2:
        refuse("two-arrow tikzcd topology drift")
    source_drawing = drawing_command_occurrences(raw_source_text)
    target_drawing = drawing_command_occurrences(target_text)
    if source_drawing != target_drawing or source_drawing:
        refuse("unexpected drawing-command surface")

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    if len(source_indexes) != 9 or len(target_indexes) != 9 or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]:
        refuse("nine-index topology or stream drift")
    if Counter(item[0] for item in source_indexes) != Counter({"main": 8, "sym1": 1}):
        refuse("main/sym1 index census drift")

    for environment in ("Exercises", "exercise", "problem", "hint", "answer", "solution"):
        if f"\\begin{{{environment}}}" in raw_source_text or f"\\begin{{{environment}}}" in target_text:
            refuse(f"invented or unexpected {environment} surface")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 028 target")

    terminology_rows = read_terminology_rows()
    bibliography_text = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8")
    for bib_key in ("Zh2", "Zh1"):
        if re.search(r"@\w+\s*\{\s*" + re.escape(bib_key) + r"\s*,", bibliography_text) is None:
            refuse(f"bibliography lacks cited key {bib_key}")
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
    unit_key = "unit/bab-4-aksi-grup-dan-prinsip-pencacahan"
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
            f"surface/unit-028/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}; state active",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}; keadaan aktif",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.label_occurrences(raw_source_text), common.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-028/label/{ordinal:03d}",
            f"label {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"label {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.reference_occurrences(raw_source_text), common.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-028/reference/{kind}/{ordinal:03d}",
            f"{kind} reference {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-028/item/{ordinal:03d}",
            f"list item {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"butir daftar {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(
            f"surface/unit-028/diagram-arrow/{ordinal:03d}",
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
            f"surface/unit-028/polygon-drawing-command/{ordinal:03d}-{command}",
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
            f"surface/unit-028/protected-math-zone/{ordinal:03d}-{kind}",
            f"protected {kind} mathematical zone {ordinal:03d}; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"zona matematika terlindungi {kind} {ordinal:03d}; baris target {TARGET_START + target_line - 1}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_language="en",
        )

    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PAIRS[ordinal - 1]
        add_concept(
            f"surface/unit-028/terminology-row/{ordinal:03d}",
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

    for localization_id, source_line, target_line, source_text, target_text_fragment in PROTECTED_TEXT_LOCALIZATIONS:
        add_concept(
            f"protected-text-localization/{localization_id.casefold()}",
            f"protected-text localization {localization_id}; authority line {source_line}; {source_text} localized without changing mathematical topology; evidence {REVIEW}",
            f"lokalisasi teks terlindungi {localization_id}; baris target {target_line}; {source_text} menjadi {target_text_fragment} tanpa mengubah topologi matematika; bukti {REVIEW}",
            source_language="en",
        )

    add_concept(
        "provenance/o013-li-u028-production",
        f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.",
        f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.",
        source_language="en",
    )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    if not set(PREREQUISITES).issubset(prerequisite_by_key):
        refuse("required Unit 028 prerequisite absent")

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
        binding(BIBLIOGRAPHY),
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
        "source_local_id": "chapter4.tex:518-665 (line 665 blank boundary omitted from target mapping)",
        "titles": [
            {"language": "zh-Hans", "text": "群作用和计数原理"},
            {"language": "id-ID", "text": "Aksi Grup dan Prinsip Pencacahan"},
        ],
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [prerequisite_by_key[key] for key in PREREQUISITES],
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    citations = []
    for ordinal, (source_item, target_item) in enumerate(
        zip(
            common.citation_occurrences(raw_source_text),
            common.citation_occurrences(target_text),
            strict=True,
        ),
        1,
    ):
        note, bib_key, source_line = source_item
        target_note, target_bib_key, target_line = target_item
        if bib_key != target_bib_key or source_line != target_line:
            refuse(f"citation {ordinal} pairing drift")
        key = f"citation/unit-028/{ordinal:02d}-{bib_key.casefold()}"
        citations.append(
            {
                "id": uid(key),
                "stable_key": key,
                "entity_type": "citation",
                "bib_key": bib_key,
                "bibliography_path": BIBLIOGRAPHY,
                "bibliography_sha256": BIBLIOGRAPHY_ID[1],
                "source_line": SOURCE_START + source_line - 1,
                "target_line": TARGET_START + target_line - 1,
                "section_id": section_id,
            }
        )

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
        key = f"index-entry/unit-028/{stream}/{ordinal:03d}"
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
        key = f"diagram/unit-028/{source_format}-{occurrence:02d}"
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
        BIBLIOGRAPHY,
        "repo/source/ccby.png",
        CROSSREF,
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-028-pdf"),
        "stable_key": "build-surface/unit-028-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_028.ps1 -OutputDirectory build/unit-028-replay",
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
            "Biber",
            "makeindex (main and sym1 streams)",
            "Poppler pdfinfo",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 028 driver and AJbook.cls",
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
            "qa/unit-028/admission-gate",
            "admission_gate",
            "Complete source-order Section 4.4 admission: authority lines 518-665 with blank boundary line 665 omitted from the 147-record target mapping; 24 active environment pairs, five labels, seven ordinary and one equation reference, two citations closed to bibliography keys Zh2 and Zh1, 16 list items, 213 protected mathematical zones, nine indexes, one TikZ-cd diagram with two arrows, 25 admitted terminology rows, one declared source correction, three protected-text localizations, and no exercises, hints, answers, or solutions. Principal CC BY 4.0 content rights remain separate from AJbook and Noto build-closure licenses; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.",
            VISUAL_REVIEW,
        ),
        qa_event("qa/unit-028/source-review", "backend_integrity", "Exact authority, translation, mathematics, identifiers, diagrams, indexes, corrections, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-028/candidate-artifact", "backend_integrity", "Exact isolated 147-record Indonesian candidate binding; evidence only, not a public-reader build input.", CANDIDATE),
        qa_event("qa/unit-028/candidate-check", "backend_integrity", "Fail-closed candidate checker binding 148 authority records, 147 target records, protected mathematics, citations, diagram topology, 25 terminology rows, one correction, and three protected-text localizations.", CANDIDATE_GATE),
        qa_event("qa/unit-028/canonical-integration", "backend_integrity", "Fail-closed canonical integration binding the prior admitted prefix, Unit 028 candidate, omitted blank boundary, untouched authority suffix, 408-row glossary, and 25-row delta.", STRUCTURE_GATE),
        qa_event("qa/unit-028/source-corrections", "backend_integrity", "Separate deterministic provenance for the sole source correction O013-LI-U028-COR-001; no second source correction is claimed.", REVIEW),
        qa_event("qa/unit-028/protected-text-localizations", "backend_integrity", "Three exact protected-text localizations at authority/target lines 557, 610, and 646 preserve all surrounding mathematical topology.", REVIEW),
        qa_event("qa/unit-028/terminology-control", "backend_integrity", "Live id-ID glossary binding for exactly 408 unique rows including the 25 admitted Unit 028 rows.", TERMINOLOGY),
        qa_event("qa/unit-028/terminology-delta", "backend_integrity", "Exact reviewed 25-row terminology delta reproduced as the controlled glossary tail without rewriting baseline rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-028/terminology-evidence", "backend_integrity", "Bound Unit 028 terminology audit, evidence limits, international-term decisions, and exact model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-028/prepromotion-evidence", "backend_integrity", "Exact splice arithmetic for target lines 518-664, omission of authority blank line 665, suffix continuity from Section 4.5, and additive terminology append.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-028/citation-closure", "backend_integrity", "Two citation occurrences preserve notes and keys Zh2 then Zh1 and resolve against the exact bound Al-jabr.bib identity.", BIBLIOGRAPHY),
        qa_event("qa/unit-028/build-log", "backend_integrity", "Final deterministic XeLaTeX, Biber, and dual-index build log with seven-page output and no fatal, unresolved, citation, or overfull markers.", FINAL_LOG),
        qa_event("qa/unit-028/visual-preflight", "backend_integrity", "Preserved independent all-page Poppler and MuPDF preflight for both clean builds; decoded-pixel, PDF-structure, font, navigation, safety, and exact final-reader identity pass with only documented non-blocking warnings.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-028/structure-and-pdf-qa", "backend_integrity", "Canonical machine-readable PDF structure, metadata, language, destinations, actions, fonts, text geometry, build-log, active-payload, and seven-page checks for the exact final artifact.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-028/render-hash-inventory", "backend_integrity", "Canonical all-page Poppler and MuPDF render identities: 42 renders, four seven-page decoded-pixel comparisons, six contact sheets, and the zero-ink outer-edge gate.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-028/all-page-visual-review", "backend_integrity", "Canonical independent full-resolution review of all seven pages in Poppler and MuPDF; zero actionable defects with documented accessibility and font-subset warnings.", VISUAL_REVIEW),
    ]

    prerequisite_ids = [prerequisite_by_key[key] for key in PREREQUISITES]
    titles = [
        {"language": "zh-Hans", "text": "第四章：群作用和计数原理"},
        {"language": "id-ID", "text": "Bab 4: Aksi Grup dan Prinsip Pencacahan"},
    ]
    data["dataset_stable_key"] = "dataset/unit-028/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u028-backend")),
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
        "order": 28,
        "source_local_id": "chapter4.tex:518-665; substantive record map 518-664",
        "titles": titles,
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "section_ids": [section_id],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [
            "outcome/define-monoid-and-group-actions-and-equivariant-maps",
            "outcome/compute-fixed-points-orbits-and-stabilizers",
            "outcome/apply-orbit-decomposition-and-orbit-stabilizer-counting",
            "outcome/distinguish-faithful-free-and-transitive-actions",
            "outcome/analyze-translation-double-coset-and-conjugation-actions",
            "outcome/recognize-torsors-bitorsors-and-the-bijection-criterion",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 2,
            "diagrams": 1,
            "index_entries": 9,
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
                "citations": len(citations),
                "items": len(source_items),
                "protected_math_zones": len(source_math),
                "diagrams": len(diagrams),
                "diagram_arrows": len(source_arrows),
                "drawing_commands": len(drawing_command_occurrences(raw_source_text)),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "source_corrections": len(SOURCE_CORRECTIONS),
                "protected_text_localizations": len(PROTECTED_TEXT_LOCALIZATIONS),
                "artifact": {"pages": page_count, "bytes": ARTIFACT_ID[0], "sha256": ARTIFACT_ID[1]},
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
