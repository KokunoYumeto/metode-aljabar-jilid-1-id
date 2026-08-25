#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 029.

Unit 029 is complete Section 4.5: the Sylow theorems.
The shared schema has no native records for TeX environments, labels,
reference/citation occurrences, list items, protected mathematical zones,
terminology rows, correction provenance, or protected-text localizations, so
those surfaces are represented as deterministic UUIDv5 concept-compatible
entities.  The bibliography citation and index entries retain their native
schema records; this unit contains no diagram surface.
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

import check_unit_029_candidate as candidate_check
import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
OUTPUT = ROOT / "backend/data/unit-029-bab-4-teorema-sylow.json"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-029-candidate/chapter4-sylow-theorems-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-029-bab-4-teorema-sylow.tex"
COVER = "repo/source/coverpage-id-unit-029.tex"
CROSSREF = "repo/source/unit-029-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_029.ps1"
CANDIDATE_GATE = "scripts/check_unit_029_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_029_structure.py"
REVIEW = "qa/UNIT_029_TRANSLATION_REVIEW_20260824.md"
TERMINOLOGY_AUDIT = "qa/UNIT_029_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = "qa/UNIT_029_PREPROMOTION_AUDIT_20260825.md"
TERMINOLOGY_DELTA = "build/unit-029-staging/terminology-delta.csv"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
FINAL_LOG = "qa/UNIT_029_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_029_VISUAL_PREFLIGHT_20260825.md"
VISUAL_REVIEW = "qa/UNIT_029_VISUAL_QA_20260825.md"
STRUCTURE_PDF_QA = "qa/unit-029-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-029-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-029-bab-4-teorema-sylow-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_PAGE_COUNT = 6

# The frozen authority boundary includes blank separator line 795.  The
# record-aligned target mapping contains only substantive authority lines
# 666--794, integrated at canonical target lines 665--793 after the omitted
# Unit 028 boundary record.
SOURCE_START, SOURCE_END = 666, 795
SOURCE_CONTENT_END = 794
TARGET_START, TARGET_END = 665, 793

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
    8_043,
    "760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163",
)
SOURCE_CONTENT_SPAN = (
    8_042,
    "b18d7d61b446d2a884f34ad9c7761d935f34d438b031f63a87f885df9ed557a9",
)
CANDIDATE_FULL = (
    10_028,
    "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d",
)
TARGET_FULL = (
    170_663,
    "8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc",
)
TARGET_SPAN = CANDIDATE_FULL
ARTIFACT_ID = (
    99_689,
    "64fde52948525fc5b159f76fbed6571c150e4184a87e47e715164aec135e5012",
)
BIBLIOGRAPHY_ID = (
    29_580,
    "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e",
)
CANDIDATE_GATE_ID = (
    14_830,
    "3a67accdd9cbcace31547b4284fe65b4f4ab29ebd0efd04be325d450fe6936d7",
)
STRUCTURE_GATE_ID = (
    9_674,
    "64f422aafc03b4b2d8ab0c5995bb3e8ff420efdddc3f110c769c20ff827b44a7",
)
REVIEW_ID = (
    9_138,
    "9a88a668fc38471d7bbfbdb69df73133dcb6985ef6e5f1cd4a8d2696283a5fb0",
)
TERMINOLOGY_AUDIT_ID = (
    2_144,
    "a5b766779eac0726ccd0d5fae220932c9afba08953ca1eefd94785251db86627",
)
PREPROMOTION_AUDIT_ID = (
    4_003,
    "e92692dc2c59eed7f120d2c0fabaa78f8c24f4efc14479437398a7180fdccbf6",
)
TERMINOLOGY_DELTA_ID = (
    1_030,
    "e0e00678dc46fd8c702c17614ea2d1e1e71ee6ff622f8986097dfd296e759ecc",
)
TERMINOLOGY_ID = (
    65_573,
    "adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3",
)
BUILD_SCRIPT_ID = (
    5_007,
    "a8dca51981509d80a2902b5ef7ba52e9505008bf7cfd03866cd0a5d022d5d80c",
)
FINAL_LOG_ID = (
    77_013,
    "606a707d5aad534f58af25333f3fbffe964ab7c7f1a260b3ffe9c1f1bce8364e",
)
DRIVER_ID = (
    6_028,
    "7f2f677d9f5b54f0fe802d5367990bf3b62bf46c04f2087fbd4f91c5f265a08f",
)
COVER_ID = (
    3_590,
    "4a66895d41b7ad3c73f2f7ab244a93e042bb365ca706d38b1b62d3cf956f104b",
)
CROSSREF_ID = (
    355,
    "12856b4cc11ee6aabd903791ce89bc097ae0746473b6bb5ce3035a2896483ba6",
)
VISUAL_PREFLIGHT_ID = (
    1_842,
    "19f221c309040a07aef483bc3f90e28eda76cf74d5c43c49ce15b0d06483331d",
)
VISUAL_REVIEW_ID = (
    6_319,
    "adfbada7eb878fa23c49e66ffd9499c9297f38c596bdb3a2e1a3efd587637ae6",
)
STRUCTURE_PDF_QA_ID = (
    61_120,
    "23b61663269b592c232752b88409f48acd999eae20dd513eefa546d0a3835e1f",
)
RENDER_HASH_INVENTORY_ID = (
    30_170,
    "689ff5198ccc43b61ef755dbde902747f5cc70a8366dc68c520db086eebd8452",
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 1,
        "compactenum": 1,
        "convention": 1,
        "corollary": 3,
        "definition": 2,
        "lemma": 2,
        "proof": 10,
        "proposition": 2,
        "theorem": 3,
    }
)

DIAGRAM_SPECS = ()

CITATION_SPECS = (
    ("Theorem 6.2", "Theorem 6.2", "Lang02", 743),
)

CORE_SPECS = (
    ("concept/p-group", "$p$-群", "$p$-grup", 669),
    ("concept/p-group-orbit-counting-congruence", "$p$-群的轨道计数同余", "kongruensi pencacahan orbit untuk $p$-grup", 674),
    ("concept/nontrivial-center-of-p-group", "非平凡 $p$-群的中心非平凡", "pusat $p$-grup taktrivial bersifat taktrivial", 684),
    ("concept/proper-subgroup-proper-normalizer", "真子群严格包含于其正规化子", "subgrup sejati termuat secara ketat dalam normalisatornya", 694),
    ("concept/cauchy-theorem-for-finite-groups", "有限群的 Cauchy 定理", "Teorema Cauchy untuk grup berhingga", 704),
    ("concept/exact-prime-power-divisibility", "$p^a \\| n$ 记号", "notasi keterbagian tepat $p^a \\| n$", 721),
    ("concept/sylow-p-subgroup", "Sylow $p$-子群", "subgrup Sylow $p$", 725),
    ("concept/wielandt-binomial-congruence", "Wielandt 二项式同余", "kongruensi binomial Wielandt", 730),
    ("concept/first-sylow-theorem", "Sylow 第一定理", "Teorema Sylow Pertama", 740),
    ("concept/sylow-normalizer-lemma", "Sylow 子群的正规化子引理", "lema normalisator subgrup Sylow", 753),
    ("concept/second-sylow-theorem", "Sylow 第二定理", "Teorema Sylow Kedua", 760),
    ("concept/third-sylow-theorem", "Sylow 第三定理", "Teorema Sylow Ketiga", 780),
    ("concept/normal-sylow-direct-product-characterization", "正规 Sylow 子群的直积刻画", "karakterisasi produk langsung melalui subgrup Sylow normal", 787),
)

TERMINOLOGY_PAIRS = (
    ("p-group", "p-grup"),
    ("p-subgroup", "p-subgrup"),
    ("Sylow p-subgroup", "subgrup Sylow p"),
    ("binomial coefficient", "koefisien binomial"),
    ("coprime", "saling koprima"),
)

TERMINOLOGY_EVIDENCE = {
    "p-group": "$p$-grup",
    "p-subgroup": "$p$-subgrup",
    "Sylow p-subgroup": "subgrup Sylow $p$",
}

SOURCE_CORRECTIONS = ()

PROTECTED_TEXT_LOCALIZATIONS = (
    ("O013-LI-U029-LOC-001", 746, 745, "子集", "subhimpunan"),
)

PREREQUISITES = (
    "prerequisite/basic-mathematical-literacy",
    "prerequisite/elementary-set-theory",
    "prerequisite/basic-group-theory",
    "prerequisite/group-homomorphisms-kernels-and-quotients",
    "prerequisite/group-actions-orbits-and-stabilizers",
    "prerequisite/elementary-number-theory",
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-029-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 029 backend refused: " + message)


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
    if len(lines) != 129:
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
    if len(rows) != 413 or len({row.get("source_term") for row in rows}) != 413:
        refuse("controlled glossary row/uniqueness drift")
    with (ROOT / TERMINOLOGY_DELTA).open("r", encoding="utf-8", newline="") as handle:
        delta = tuple(csv.DictReader(handle))
    if len(delta) != 5 or tuple(rows[-5:]) != delta:
        refuse("five-row Unit 029 glossary delta drift")
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
            refuse(f"admitted Unit 029 term absent: {source_term!r} -> {target_term!r}")
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
        refuse("authority line 795 is not exactly the omitted blank boundary record")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("canonical target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    source_records = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_records = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_records) != 1_898 or (ROOT / SOURCE).read_bytes().endswith(b"\n"):
        refuse("authority Chapter 4 record/EOF census drift")
    if len(target_records) != 1_896 or not (ROOT / TARGET).read_bytes().endswith(b"\n"):
        refuse("canonical Chapter 4 record/EOF census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "PASS unit-029 candidate admission",
            (SOURCE_SPAN[1], CANDIDATE_FULL[1], "declared_source_corrections=0", "protected_text_localizations=1"),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 029 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1], TERMINOLOGY_ID[1], "glossary_rows=413", "terminology_delta_rows=5"),
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
        or len(source_env) != 25
    ):
        refuse("25-pair textual environment topology drift")

    source_labels = common.label_occurrences(raw_source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 6:
        refuse("six-label topology drift")
    source_refs = common.reference_occurrences(raw_source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 16:
        refuse("16-reference topology drift")
    if Counter(item[0] for item in source_refs) != Counter({"ordinary": 16}):
        refuse("ordinary-reference census drift")
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
        refuse("one-citation topology or Lang02 key closure drift")
    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if source_items != target_items or len(source_items) != 2:
        refuse("two-item topology drift")

    normalized_source = normalized_source_content()
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    if [item[1:] for item in source_math] != [item[1:] for item in target_math] or len(source_math) != 211:
        refuse("211-zone protected mathematics drift")

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    expected_source_diagrams = tuple(item[:4] for item in DIAGRAM_SPECS)
    expected_target_diagrams = tuple((item[0], item[1], item[4], item[5]) for item in DIAGRAM_SPECS)
    if source_diagrams != expected_source_diagrams or target_diagrams != expected_target_diagrams:
        refuse("zero-diagram topology drift")
    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    if source_arrows != target_arrows or source_arrows:
        refuse("unexpected diagram-arrow surface")
    source_drawing = drawing_command_occurrences(raw_source_text)
    target_drawing = drawing_command_occurrences(target_text)
    if source_drawing != target_drawing or source_drawing:
        refuse("unexpected drawing-command surface")

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    if len(source_indexes) != 2 or len(target_indexes) != 2 or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]:
        refuse("two-index topology or stream drift")
    if Counter(item[0] for item in source_indexes) != Counter({"main": 2}):
        refuse("main index census drift")

    for environment in ("Exercises", "exercise", "problem", "hint", "answer", "solution"):
        if f"\\begin{{{environment}}}" in raw_source_text or f"\\begin{{{environment}}}" in target_text:
            refuse(f"invented or unexpected {environment} surface")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 029 target")

    terminology_rows = read_terminology_rows()
    bibliography_text = (ROOT / BIBLIOGRAPHY).read_text(encoding="utf-8")
    for bib_key in ("Lang02",):
        if re.search(r"@\w+\s*\{\s*" + re.escape(bib_key) + r"\s*,", bibliography_text) is None:
            refuse(f"bibliography lacks cited key {bib_key}")
    page_count = pdfinfo_page_count()
    if page_count != EXPECTED_PAGE_COUNT:
        refuse(f"final reader page count drift: {page_count}")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    # PTY capture can wrap the word ``pages`` between ``p`` and ``ages``.
    page_hits = re.findall(r"Output written on .*?\((\d+)\s+p\s*ages?", final_log, re.DOTALL)
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
    for token in ("PASS WITH WARNINGS", MODEL, "six pages", "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual:
            refuse(f"visual preflight lacks {token!r}")
    visual_review = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS WITH WARNINGS", MODEL, "All three PDFs have six pages", "Poppler", "MuPDF", ARTIFACT_ID[1]):
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
        or structure_qa.get("final_build_log", {}).get("page_marker") != EXPECTED_PAGE_COUNT
    ):
        refuse("canonical structure-and-PDF QA semantics drift")

    render_inventory = json.loads((ROOT / RENDER_HASH_INVENTORY).read_text(encoding="utf-8"))
    comparisons = render_inventory.get("decoded_pixel_comparisons", {})
    comparison_results = [
        comparisons.get(renderer, {}).get(pair, {}).get(f"all_{EXPECTED_PAGE_COUNT}_decoded_pixel_identical")
        for renderer in ("poppler", "mupdf")
        for pair in ("build-i_vs_build-j", "build-j_vs_artifact")
    ]
    manual = render_inventory.get("manual_visual_review", {})
    if (
        render_inventory.get("status") != "PASS_WITH_WARNINGS"
        or render_inventory.get("identities", {}).get("artifact")
        != {"bytes": ARTIFACT_ID[0], "path": ARTIFACT, "sha256": ARTIFACT_ID[1]}
        or render_inventory.get("identities", {}).get("final-build-log")
        != {"bytes": FINAL_LOG_ID[0], "path": FINAL_LOG, "sha256": FINAL_LOG_ID[1]}
        or render_inventory.get("identities", {}).get("build-j_artifact_byte_identical") is not True
        or comparison_results != [True, True, True, True]
        or render_inventory.get("edge_gate") != {"all_36_zero_ink": True, "outer_band_pixels": 3}
        or manual.get("status") != "PASS"
        or manual.get("pages_per_document") != EXPECTED_PAGE_COUNT
        or manual.get("actionable_defects") != []
        or set(manual.get("renderers", [])) != {"Poppler", "MuPDF"}
        or len(manual.get("findings", {})) != EXPECTED_PAGE_COUNT
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
    unit_key = "unit/bab-4-teorema-sylow"
    unit_id = uid(unit_key)
    raw_source_text = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    normalized_source = normalized_source_content()
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    supplemental_prerequisites = (
        (
            "prerequisite/group-homomorphisms-kernels-and-quotients",
            "群同态、核与商群",
            "homomorfisme grup, kernel, dan grup hasil bagi",
            177,
            364,
        ),
        (
            "prerequisite/group-actions-orbits-and-stabilizers",
            "群作用、轨道与稳定化子",
            "aksi grup, orbit, dan stabilisator",
            518,
            665,
        ),
    )
    existing_prerequisites = {item["stable_key"] for item in data["prerequisites"]}
    for prerequisite_key, source_label, target_label, first, last in supplemental_prerequisites:
        if prerequisite_key in existing_prerequisites:
            continue
        data["prerequisites"].append(
            {
                "id": uid(prerequisite_key),
                "stable_key": prerequisite_key,
                "entity_type": "prerequisite",
                "labels": [
                    {"language": "zh-Hans", "text": source_label},
                    {"language": "id-ID", "text": target_label},
                ],
                "requiredness": "expected",
                "source_evidence": {"path": SOURCE, "line_start": first, "line_end": last},
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
            f"surface/unit-029/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}; state active",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}; keadaan aktif",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.label_occurrences(raw_source_text), common.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-029/label/{ordinal:03d}",
            f"label {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"label {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.reference_occurrences(raw_source_text), common.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-029/reference/{kind}/{ordinal:03d}",
            f"{kind} reference {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-029/item/{ordinal:03d}",
            f"list item {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"butir daftar {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(
            f"surface/unit-029/diagram-arrow/{ordinal:03d}",
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
            f"surface/unit-029/polygon-drawing-command/{ordinal:03d}-{command}",
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
            f"surface/unit-029/protected-math-zone/{ordinal:03d}-{kind}",
            f"protected {kind} mathematical zone {ordinal:03d}; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"zona matematika terlindungi {kind} {ordinal:03d}; baris target {TARGET_START + target_line - 1}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_language="en",
        )

    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PAIRS[ordinal - 1]
        add_concept(
            f"surface/unit-029/terminology-row/{ordinal:03d}",
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
        "provenance/o013-li-u029-production",
        f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.",
        f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.",
        source_language="en",
    )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    if not set(PREREQUISITES).issubset(prerequisite_by_key):
        refuse("required Unit 029 prerequisite absent")

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
        "source_local_id": "chapter4.tex:666-795 (line 795 blank boundary omitted from target mapping)",
        "titles": [
            {"language": "zh-Hans", "text": "Sylow 定理"},
            {"language": "id-ID", "text": "Teorema Sylow"},
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
        key = f"citation/unit-029/{ordinal:02d}-{bib_key.casefold()}"
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
        key = f"index-entry/unit-029/{stream}/{ordinal:03d}"
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
        key = f"diagram/unit-029/{source_format}-{occurrence:02d}"
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
        "id": uid("build-surface/unit-029-pdf"),
        "stable_key": "build-surface/unit-029-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_029.ps1 -OutputDirectory build/unit-029-replay",
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
            "packages loaded by the Unit 029 driver and AJbook.cls",
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
            "qa/unit-029/admission-gate",
            "admission_gate",
            "Complete source-order Section 4.5 admission: authority lines 666-795 with blank boundary line 795 omitted from the 129-record target mapping at canonical lines 665-793; 25 active environment pairs, six labels, 16 ordinary references, one citation closed to bibliography key Lang02, two list items, 211 protected mathematical zones, two main indexes, five admitted terminology rows, zero source corrections, one protected-text localization, zero diagrams, and no exercises, hints, answers, or solutions. Principal CC BY 4.0 content rights remain separate from AJbook and Noto build-closure licenses; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.",
            VISUAL_REVIEW,
        ),
        qa_event("qa/unit-029/source-review", "backend_integrity", "Exact authority, translation, mathematics, identifiers, diagrams, indexes, corrections, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-029/candidate-artifact", "backend_integrity", "Exact isolated 129-record Indonesian candidate binding; evidence only, not a public-reader build input.", CANDIDATE),
        qa_event("qa/unit-029/candidate-check", "backend_integrity", "Fail-closed candidate checker binding 130 authority records, 129 target records, protected mathematics, the Lang02 citation, two index entries, zero diagrams, five terminology rows, zero corrections, and one protected-text localization.", CANDIDATE_GATE),
        qa_event("qa/unit-029/canonical-integration", "backend_integrity", "Fail-closed canonical integration binding the prior admitted prefix, Unit 029 candidate at lines 665-793, omitted authority blank boundary, untouched Section 4.6 suffix, 413-row glossary, and five-row delta.", STRUCTURE_GATE),
        qa_event("qa/unit-029/source-corrections", "backend_integrity", "Deterministic source adjudication records zero mathematical source corrections for this exact unit.", REVIEW),
        qa_event("qa/unit-029/protected-text-localizations", "backend_integrity", "One exact protected-text localization at authority line 746 and target line 745 preserves all surrounding mathematical topology.", REVIEW),
        qa_event("qa/unit-029/terminology-control", "backend_integrity", "Live id-ID glossary binding for exactly 413 unique rows including the five admitted Unit 029 rows.", TERMINOLOGY),
        qa_event("qa/unit-029/terminology-delta", "backend_integrity", "Exact reviewed five-row terminology delta reproduced as the controlled glossary tail without rewriting baseline rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-029/terminology-evidence", "backend_integrity", "Bound Unit 029 terminology audit, evidence limits, international-term decisions, and exact model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-029/prepromotion-evidence", "backend_integrity", "Exact splice arithmetic for target lines 665-793, omission of authority blank line 795, suffix continuity from Section 4.6, and additive terminology append.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-029/citation-closure", "backend_integrity", "The sole citation preserves locator Theorem 6.2 and key Lang02 and resolves against the exact bound Al-jabr.bib identity.", BIBLIOGRAPHY),
        qa_event("qa/unit-029/build-log", "backend_integrity", "Final deterministic XeLaTeX, Biber, and dual-index build log with six-page output and no fatal, unresolved, citation, or overfull markers.", FINAL_LOG),
        qa_event("qa/unit-029/visual-preflight", "backend_integrity", "Preserved independent all-page Poppler and MuPDF preflight for both clean builds; decoded-pixel, PDF-structure, font, navigation, safety, and exact final-reader identity pass with only documented non-blocking warnings.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-029/structure-and-pdf-qa", "backend_integrity", "Canonical machine-readable PDF structure, metadata, language, destinations, actions, fonts, text geometry, build-log, active-payload, and six-page checks for the exact final artifact.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-029/render-hash-inventory", "backend_integrity", "Canonical all-page Poppler and MuPDF render identities: 36 renders, four six-page decoded-pixel comparisons, six contact sheets, and the zero-ink outer-edge gate.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-029/all-page-visual-review", "backend_integrity", "Canonical independent full-resolution review of all six pages in Poppler and MuPDF; zero actionable defects with documented accessibility and font-subset warnings.", VISUAL_REVIEW),
    ]

    prerequisite_ids = [prerequisite_by_key[key] for key in PREREQUISITES]
    titles = [
        {"language": "zh-Hans", "text": "第四章：Sylow 定理"},
        {"language": "id-ID", "text": "Bab 4: Teorema Sylow"},
    ]
    data["dataset_stable_key"] = "dataset/unit-029/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u029-backend")),
        "updated": "2026-08-26",
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
        "order": 29,
        "source_local_id": "chapter4.tex:666-795; substantive authority map 666-794 to target 665-793",
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
            "outcome/define-p-groups-and-sylow-p-subgroups",
            "outcome/apply-p-group-orbit-counting-congruences",
            "outcome/prove-cauchy-theorem-by-cyclic-action",
            "outcome/apply-wielandt-binomial-congruence",
            "outcome/prove-and-use-the-three-sylow-theorems",
            "outcome/characterize-direct-products-by-normal-sylow-subgroups",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 1,
            "diagrams": 0,
            "index_entries": 2,
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
