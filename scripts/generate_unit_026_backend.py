#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 026.

Unit 026 is complete Section 4.2, homomorphisms and quotient groups.  The
shared schema has no native records for TeX environments, labels, reference
occurrences, list items, arrows, protected mathematical zones, terminology
rows, commented editorials, or source corrections, so those are represented
as deterministic UUIDv5 concept-compatible entities.  Citations, diagrams,
and index entries retain their native schema records.  Generation fails closed
unless every authority, candidate, canonical-target, terminology, build,
rights, QA, and final-reader binding has its reviewed identity.
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

import check_unit_026_candidate as candidate_check
import generate_unit_009_backend as base
import generate_unit_023_backend as common


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-025-bab-4-semigrup-monoid-dan-grup.json"
OUTPUT = ROOT / "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex"
TARGET = "repo/source/chapter4.tex"
DRIVER = "repo/source/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.tex"
COVER = "repo/source/coverpage-id-unit-026.tex"
CROSSREF = "repo/source/unit-026-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
BUILD_SCRIPT = "scripts/build_unit_026.ps1"
CANDIDATE_GATE = "scripts/check_unit_026_candidate.py"
STRUCTURE_GATE = "scripts/check_unit_026_structure.py"
REVIEW = "qa/UNIT_026_TRANSLATION_REVIEW_20260824.md"
TERMINOLOGY_RECOMMENDATION = "qa/UNIT_026_TERMINOLOGY_RECOMMENDATION_20260825.md"
TERMINOLOGY_AUDIT = "qa/UNIT_026_TERMINOLOGY_AUDIT_20260825.md"
PREPROMOTION_AUDIT = "qa/UNIT_026_PREPROMOTION_AUDIT_20260825.md"
TERMINOLOGY_DELTA = "build/unit-026-staging/terminology-delta.csv"
TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
FINAL_LOG = "qa/UNIT_026_BUILD_FINAL.log"
VISUAL_REVIEW = "qa/UNIT_026_VISUAL_QA_20260825.md"
STRUCTURE_PDF_QA = "qa/unit-026-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-026-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi-id.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"

# The frozen authority boundary includes its terminal blank line 364.  The
# record-aligned mathematical/content topology omits only that blank record.
SOURCE_START, SOURCE_END = 177, 364
SOURCE_CONTENT_END = 363
TARGET_START, TARGET_END = 179, 365

TEMPLATE_ID = (
    328_559,
    "478545e6f43f8557b3ea2da4dece92b9346886139cd3dea114336746aa9357a1",
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
    15_360,
    "4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8",
)
SOURCE_CONTENT_SPAN = (
    15_359,
    "6202107ace49fe5aae724b9ad5801bb1291c3211925618192bc65990dafba528",
)
CANDIDATE_FULL = (
    19_424,
    "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87",
)
TARGET_FULL = (
    163_745,
    "fc3fd6ef470d41f146456bfc889eb7c7ec84bb48890f1b23f18e51a195e7d463",
)
TARGET_SPAN = CANDIDATE_FULL
ARTIFACT_ID = (
    115_284,
    "e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089",
)
BIBLIOGRAPHY_ID = (
    29_580,
    "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e",
)
CANDIDATE_GATE_ID = (
    13_906,
    "42d3c8b669ac12ff5b29eb458c33123a04ad29e27f94acb2048d1cc72e0e92b5",
)
STRUCTURE_GATE_ID = (
    12_643,
    "ad0414a6d4f6358dfa3bdddc211b8ad48ff0f8cf02696263dd190c48f4147dc2",
)
REVIEW_ID = (
    10_415,
    "e0a0279f0db3e6ebbc65b3af979193591419b6bf21cdd374996e7967ed78d558",
)
TERMINOLOGY_RECOMMENDATION_ID = (
    12_339,
    "8b239bd3a07df12c09ac0b55922ffa262a37163ce3e23f1ea9434775cae468de",
)
TERMINOLOGY_AUDIT_ID = (
    5_363,
    "de621e7430079e7e2453f776763e6026043bb2103f01a842192463c661625d5f",
)
PREPROMOTION_AUDIT_ID = (
    3_683,
    "37fb01a88393c1773a9006dca038f2719e0ccfb2b75e9d90575860c9fd758be6",
)
TERMINOLOGY_DELTA_ID = (
    7_238,
    "29da42f631cb8290e54335142e589c71939040e6f874a0e7f026b9d70caad408",
)
TERMINOLOGY_ID = (
    58_658,
    "5ecccbbdbe99ce3dbe05baf42088c401e261663432d1116abcab66d2165abe17",
)
BUILD_SCRIPT_ID = (
    5_026,
    "54140175910974d488b43666a01ff0383e95387c62ab727aaa162af05d449632",
)
FINAL_LOG_ID = (
    86_417,
    "f26903ed598b9191005e00dd8f2d55b2de09eb0464722ed5bef24e9f9f93f8fd",
)
DRIVER_ID = (
    6_257,
    "01e707bfc20170ebf732b8df8619db6aa00040251ba426831ab5648a47bcb6c5",
)
COVER_ID = (
    3_664,
    "2f0a415d54b36cfe99f7ed6c04c3493ff633c6c483aa843a12ce02931063b999",
)
CROSSREF_ID = (
    445,
    "a5197d6e72d92b8c26749d924a545b3ced53f28648714b96c954d60a28cbe137",
)

VISUAL_REVIEW_ID = (
    4_333,
    "b601c16c0a391484064f269998567ab8cb4919a0301433d8a4d0deacd287ebfe",
)
STRUCTURE_PDF_QA_ID = (
    48_059,
    "37e5aefb3bcea6fe78e17cb5dd881107590384f835a8f4cbc0b27258f91922e0",
)
RENDER_HASH_INVENTORY_ID = (
    41_318,
    "74fd7daa416595c6adc0d8c541db22756df655bdcd067c5d4985d5dc482f5731",
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 6,
        "compactenum": 2,
        "compactitem": 2,
        "definition-theorem": 1,
        "definition": 3,
        "example": 1,
        "gather": 2,
        "proof": 8,
        "proposition": 7,
        "remark": 1,
        "tikzcd": 3,
    }
)
DIAGRAM_SPECS = (
    ("tikzcd", 1, 235, 238, 237, 240),
    ("tikzcd", 2, 284, 289, 286, 291),
    ("tikzcd", 3, 337, 340, 339, 342),
)

CORE_SPECS = (
    ("concept/homomorphism", "同态", "homomorfisme", 178),
    ("concept/semigroup-homomorphism", "半群同态", "homomorfisme semigrup", 178),
    ("concept/monoid-homomorphism", "幺半群同态", "homomorfisme monoid", 181),
    ("concept/group-homomorphism", "群同态", "homomorfisme grup", 199),
    ("concept/isomorphism", "同构", "isomorfisme", 188),
    ("concept/endomorphism", "自同态", "endomorfisme", 186),
    ("concept/automorphism", "自同构", "automorfisme", 188),
    ("concept/inner-automorphism", "内自同构", "automorfisme dalam", 207),
    ("concept/homomorphism-image", "同态的像", "bayangan homomorfisme", 219),
    ("concept/kernel", "核", "kernel", 219),
    ("concept/quotient-structure", "商结构", "struktur hasil bagi", 224),
    ("concept/quotient-universal-property", "商的泛性质", "sifat universal hasil bagi", 233),
    ("concept/quotient-group", "商群", "grup hasil bagi", 263),
    ("concept/quotient-homomorphism", "商同态", "homomorfisme hasil bagi", 271),
    ("concept/first-isomorphism-theorem", "第一同构定理", "teorema isomorfisme pertama", 275),
    ("concept/subgroup-correspondence", "子群对应", "korespondensi subgrup", 282),
    ("concept/third-isomorphism-theorem", "第三同构定理", "teorema isomorfisme ketiga", 299),
    ("concept/cyclic-group", "循环群", "grup siklik", 315),
    ("concept/element-order", "元素的阶", "orde unsur", 318),
    ("concept/grothendieck-group", "Grothendieck 群", "grup Grothendieck", 333),
    ("concept/group-completion", "交换幺半群的群化", "pelengkapan grup dari monoid komutatif", 334),
    ("concept/forgetful-functor", "忘却函子", "fungtor pelupa", 358),
    ("concept/adjunction", "伴随对", "pasangan adjoin", 363),
)

TERMINOLOGY_PAIRS = (
    ("semigroup homomorphism", "homomorfisme semigrup"),
    ("identity map", "peta identitas"),
    ("trivial homomorphism", "homomorfisme trivial"),
    ("inverse", "invers"),
    ("isomorphic", "isomorfik"),
    ("automorphism group", "grup automorfisme"),
    ("group homomorphism", "homomorfisme grup"),
    ("group isomorphism", "isomorfisme grup"),
    ("group automorphism", "automorfisme grup"),
    ("inner automorphism", "automorfisme dalam"),
    ("adjoint automorphism", "automorfisme adjoin"),
    ("image of a homomorphism", "bayangan homomorfisme"),
    ("kernel", "kernel"),
    ("quotient map", "peta hasil bagi"),
    ("well-defined", "terdefinisi dengan baik"),
    ("quotient structure", "struktur hasil bagi"),
    ("quotient monoid", "monoid hasil bagi"),
    ("induced homomorphism", "homomorfisme terimbas"),
    ("surjective", "surjektif"),
    ("quotient group", "grup hasil bagi"),
    ("quotient homomorphism", "homomorfisme hasil bagi"),
    ("coset space", "ruang koset"),
    ("surjectivity", "surjektivitas"),
    ("inclusion relation", "relasi pencakupan"),
    ("generator", "pembangkit"),
    ("cyclic subgroup", "subgrup siklik"),
    ("congruence", "kongruensi"),
    ("commutative monoid", "monoid komutatif"),
    ("monoid homomorphism", "homomorfisme monoid"),
    ("Grothendieck group", "grup Grothendieck"),
    ("cancellation law", "hukum pembatalan"),
    ("additive inverse", "invers aditif"),
    ("U-category", "kategori-U"),
)

# Two admitted terminology rows are intentionally realized inflectionally or
# with TeX notation in the prose rather than as their uninflected CSV display
# form.  The locators bind those reviewed surfaces without weakening the
# requirement that every other admitted target term occur literally.
TERMINOLOGY_SURFACE_LOCATORS = {
    "image of a homomorphism": "Bayangannya ditulis",
    "U-category": r"kategori-$\mathcal{U}$",
}

CORRECTIONS = (
    (
        "O013-LI-U026-COR-001",
        (301, 308, 312),
        (303, 310, 314),
        "Parenthesize H/(N intersection H), the kernel quotient required by the restricted quotient homomorphism.",
        "Tambahkan tanda kurung pada H/(N irisan H), yaitu hasil bagi oleh kernel homomorfisme hasil bagi yang dibatasi.",
    ),
    (
        "O013-LI-U026-COR-002",
        (358,),
        (360,),
        "Use varphi consistently for the single monoid homomorphism introduced and reused in the composite.",
        "Gunakan varphi secara konsisten untuk satu homomorfisme monoid yang diperkenalkan dan dipakai kembali dalam komposisi.",
    ),
    (
        "O013-LI-U026-COR-003",
        (231,),
        (233,),
        "Restrict the inverse formula to quotient groups; arbitrary quotient-monoid elements need not be invertible.",
        "Batasi rumus invers pada grup hasil bagi; unsur monoid hasil bagi sebarang tidak harus invertibel.",
    ),
    (
        "O013-LI-U026-COR-004",
        (320,),
        (322,),
        "Make the cyclic-subgroup statement total: assume nonzero n in the finite case, use absolute order, and state the n=0 cases.",
        "Lengkapi pernyataan subgrup siklik: andaikan n tak nol dalam kasus hingga, gunakan nilai mutlak untuk orde, dan nyatakan kasus n=0.",
    ),
)

PREREQUISITES = (
    "prerequisite/basic-mathematical-literacy",
    "prerequisite/elementary-set-theory",
    "prerequisite/basic-group-theory",
    "prerequisite/categories-and-morphisms",
    "prerequisite/functors-and-natural-transformations",
    "prerequisite/universal-properties-and-comma-categories",
)

CSV_OUTPUTS = tuple(
    ROOT / f"backend/csv/unit-026-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 026 backend refused: " + message)


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


def target_line_for_source(source_line: int) -> int:
    if not SOURCE_START <= source_line <= SOURCE_CONTENT_END:
        refuse(f"authority line outside Unit 026 substantive mapping: {source_line}")
    return source_line + 2


def normalized_source_content() -> str:
    # Line 364 is the frozen boundary's deliberately omitted blank record.
    # Normalize only the 187 substantive records so the correction callback
    # receives the exact authority line numbers 177--363.
    lines = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END).splitlines()
    if len(lines) != 187:
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


def read_terminology_rows() -> tuple[tuple[dict[str, str], int, int], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    if len(rows) != 374 or len({row.get("source_term") for row in rows}) != 374:
        refuse("controlled glossary row/uniqueness drift")
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
        surface = TERMINOLOGY_SURFACE_LOCATORS.get(source_term, target_term)
        occurrences = [
            offset
            for offset, line in enumerate(target_lines)
            if surface.casefold() in line.casefold()
        ]
        if not occurrences:
            refuse(
                "admitted target terminology surface absent from Unit 026: "
                f"{source_term!r} -> {surface!r}"
            )
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
        (BIBLIOGRAPHY, BIBLIOGRAPHY_ID),
        (BUILD_SCRIPT, BUILD_SCRIPT_ID),
        (CANDIDATE_GATE, CANDIDATE_GATE_ID),
        (STRUCTURE_GATE, STRUCTURE_GATE_ID),
        (REVIEW, REVIEW_ID),
        (TERMINOLOGY_RECOMMENDATION, TERMINOLOGY_RECOMMENDATION_ID),
        (TERMINOLOGY_AUDIT, TERMINOLOGY_AUDIT_ID),
        (PREPROMOTION_AUDIT, PREPROMOTION_AUDIT_ID),
        (TERMINOLOGY_DELTA, TERMINOLOGY_DELTA_ID),
        (TERMINOLOGY, TERMINOLOGY_ID),
        (FINAL_LOG, FINAL_LOG_ID),
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
        refuse("authority line 364 is not exactly the omitted blank boundary record")
    if (len(target_span), digest(target_span)) != TARGET_SPAN:
        refuse("canonical target span drift")
    if target_span != (ROOT / CANDIDATE).read_bytes():
        refuse("canonical target span is not byte-identical to reviewed candidate")
    source_records = (ROOT / SOURCE).read_bytes().splitlines(keepends=True)
    target_records = (ROOT / TARGET).read_bytes().splitlines(keepends=True)
    if len(source_records) != 1_898 or (ROOT / SOURCE).read_bytes().endswith(b"\n"):
        refuse("authority Chapter 4 record/EOF census drift")
    if len(target_records) != 1_899 or not (ROOT / TARGET).read_bytes().endswith(b"\n"):
        refuse("canonical Chapter 4 record/EOF census drift")

    for relative, marker, tokens in (
        (
            CANDIDATE_GATE,
            "PASS unit-026 candidate admission",
            (SOURCE_SPAN[1], CANDIDATE_FULL[1], "declared_source_corrections=4"),
        ),
        (
            STRUCTURE_GATE,
            "UNIT 026 STRUCTURE CHECK: PASS",
            (TARGET_FULL[1], TERMINOLOGY_ID[1], "delta_terms_verified=33"),
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
        or len(source_env) != 36
    ):
        refuse("36-pair textual environment topology drift")
    source_lines = raw_source_text.splitlines()
    target_lines = target_text.splitlines()
    inactive = [
        item for item in source_env if source_lines[item[2] - 1].lstrip().startswith("%")
    ]
    target_inactive = [
        item for item in target_env if target_lines[item[2] - 1].lstrip().startswith("%")
    ]
    if inactive != [("align*", 5, 131, 134)] or target_inactive != inactive:
        refuse("commented alternative-proof align topology drift")
    if len(source_env) - len(inactive) != 35:
        refuse("active environment-pair census drift")

    source_labels = common.label_occurrences(raw_source_text)
    target_labels = common.label_occurrences(target_text)
    if [item[0] for item in source_labels] != [item[0] for item in target_labels] or len(source_labels) != 12:
        refuse("twelve-label topology drift")
    source_refs = common.reference_occurrences(raw_source_text)
    target_refs = common.reference_occurrences(target_text)
    if [item[:2] for item in source_refs] != [item[:2] for item in target_refs] or len(source_refs) != 24:
        refuse("24-reference topology drift")
    if Counter(item[0] for item in source_refs) != Counter({"ordinary": 18, "equation": 6}):
        refuse("ordinary/equation reference census drift")
    source_cites = common.citation_occurrences(raw_source_text)
    target_cites = common.citation_occurrences(target_text)
    if [item[1] for item in source_cites] != [item[1] for item in target_cites] or [item[1] for item in source_cites] != ["DN00"]:
        refuse("DN00 citation topology drift")
    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    if source_items != target_items or len(source_items) != 12:
        refuse("twelve-item topology drift")

    normalized_source = normalized_source_content()
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    if [item[1:] for item in source_math] != [item[1:] for item in target_math] or len(source_math) != 275:
        refuse("275-zone protected mathematics drift")

    base.SPAN_START = SOURCE_START
    source_diagrams = base.diagram_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_diagrams = base.diagram_occurrences(target_text)
    expected_source_diagrams = tuple(item[:4] for item in DIAGRAM_SPECS)
    expected_target_diagrams = tuple((item[0], item[1], item[4], item[5]) for item in DIAGRAM_SPECS)
    if source_diagrams != expected_source_diagrams or target_diagrams != expected_target_diagrams:
        refuse("three-diagram topology drift")
    if len(common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")) != 12 or len(common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")) != 12:
        refuse("twelve-arrow diagram topology drift")

    base.SPAN_START = SOURCE_START
    source_indexes = base.index_occurrences(raw_source_text)
    base.SPAN_START = TARGET_START
    target_indexes = base.index_occurrences(target_text)
    if len(source_indexes) != 10 or len(target_indexes) != 10 or [item[0] for item in source_indexes] != [item[0] for item in target_indexes]:
        refuse("ten-index topology or stream drift")
    if Counter(item[0] for item in source_indexes) != Counter({"main": 9, "sym1": 1}):
        refuse("main/sym1 index census drift")

    for environment in ("Exercises", "exercise", "hint", "answer", "solution"):
        if f"\\begin{{{environment}}}" in raw_source_text or f"\\begin{{{environment}}}" in target_text:
            refuse(f"invented or unexpected {environment} surface")
    if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", target_text):
        refuse("Han residue remains in Unit 026 target")

    terminology_rows = read_terminology_rows()
    page_count = pdfinfo_page_count()
    if page_count != 9:
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
    ):
        if token in final_log:
            refuse(f"final build log contains blocker {token!r}")
    visual = (ROOT / VISUAL_REVIEW).read_text(encoding="utf-8")
    for token in ("PASS", "9", "Poppler", "MuPDF", ARTIFACT_ID[1]):
        if token not in visual:
            refuse(f"visual review lacks {token!r}")
    terminology_audit = (ROOT / TERMINOLOGY_AUDIT).read_text(encoding="utf-8")
    if MODEL not in terminology_audit:
        refuse("terminology audit lacks exact production-model provenance")
    for relative in (STRUCTURE_PDF_QA, RENDER_HASH_INVENTORY):
        qa_payload = (ROOT / relative).read_text(encoding="utf-8")
        for token in ("PASS_WITH_WARNINGS", ARTIFACT_ID[1]):
            if token not in qa_payload:
                refuse(f"{relative} lacks exact final-reader QA token {token!r}")
    return page_count, terminology_rows


def main() -> None:
    page_count, terminology_rows = gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-4-homomorfisme-dan-grup-hasil-bagi"
    unit_id = uid(unit_key)
    raw_source_text = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    normalized_source = normalized_source_content()
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    concepts: list[dict[str, object]] = []

    def add_concept(
        stable_key: str,
        source_label: str,
        target_label: str,
        *,
        source_language: str = "zh-Hans",
    ) -> None:
        concept = common.surface_concept(uid, stable_key, source_label, target_label)
        concept["labels"][0]["language"] = source_language
        concepts.append(concept)

    for stable_key, source_label, target_label, _ in CORE_SPECS:
        add_concept(stable_key, source_label, target_label)

    source_env = common.environment_occurrences(raw_source_text)
    target_env = common.environment_occurrences(target_text)
    source_lines = raw_source_text.splitlines()
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        _, _, target_first, target_last = target_item
        state = "source-disabled comment" if source_lines[source_first - 1].lstrip().startswith("%") else "active"
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-026/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}; state {state}",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}; keadaan {state}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.label_occurrences(raw_source_text), common.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item
        _, target_line = target_item
        add_concept(
            f"surface/unit-026/label/{ordinal:03d}",
            f"label {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"label {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    for ordinal, (source_item, target_item) in enumerate(zip(common.reference_occurrences(raw_source_text), common.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item
        _, _, target_line = target_item
        add_concept(
            f"surface/unit-026/reference/{kind}/{ordinal:03d}",
            f"{kind} reference {ordinal:03d}: {label}; authority line {SOURCE_START + source_line - 1}",
            f"rujukan {kind} {ordinal:03d}: {label}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_items = common.occurrence_lines(raw_source_text, r"\\item(?![A-Za-z])")
    target_items = common.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(
            f"surface/unit-026/item/{ordinal:03d}",
            f"list item {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"butir daftar {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
            source_language="en",
        )

    source_arrows = common.occurrence_lines(raw_source_text, r"\\arrow(?![A-Za-z])")
    target_arrows = common.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(
            f"surface/unit-026/diagram-arrow/{ordinal:03d}",
            f"tikzcd arrow {ordinal:03d}; authority line {SOURCE_START + source_line - 1}",
            f"panah tikzcd {ordinal:03d}; baris target {TARGET_START + target_line - 1}",
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
            f"surface/unit-026/protected-math-zone/{ordinal:03d}-{kind}",
            f"protected {kind} mathematical zone {ordinal:03d}; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {digest(source_formula.encode('utf-8'))}",
            f"zona matematika terlindungi {kind} {ordinal:03d}; baris target {TARGET_START + target_line - 1}; SHA-256 {digest(target_formula.encode('utf-8'))}",
            source_language="en",
        )

    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PAIRS[ordinal - 1]
        add_concept(
            f"surface/unit-026/terminology-row/{ordinal:03d}",
            f"terminology row {ordinal:03d}: {source_term}; representative authority line {source_line}",
            f"baris terminologi {ordinal:03d}: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}",
            source_language="en",
        )

    add_concept(
        "editorial/o013-li-u026-commented-alternative-proof",
        "Source-disabled alternative proof preserved at authority lines 306-311, including one commented align environment; no commented mathematics was activated.",
        "Bukti alternatif nonaktif dipertahankan pada baris target 308-313, termasuk satu lingkungan align yang dikomentari; tidak ada matematika komentar yang diaktifkan.",
        source_language="en",
    )

    for correction_id, source_lines_abs, target_lines_abs, source_issue, target_issue in CORRECTIONS:
        add_concept(
            f"correction/{correction_id.casefold()}",
            f"declared source correction {correction_id}; authority lines {','.join(map(str, source_lines_abs))}; {source_issue} Evidence: {REVIEW}.",
            f"koreksi sumber terdeklarasi {correction_id}; baris target {','.join(map(str, target_lines_abs))}; {target_issue} Bukti: {REVIEW}.",
            source_language="en",
        )

    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    if len(concept_by_key) != len(concepts):
        refuse("duplicate concept stable key")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    if not set(PREREQUISITES).issubset(prerequisite_by_key):
        refuse("required Unit 026 prerequisite absent from template")

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
        "source_local_id": "chapter4.tex:177-364 (line 364 blank boundary omitted from target mapping)",
        "titles": [
            {"language": "zh-Hans", "text": "同态和商群"},
            {"language": "id-ID", "text": "Homomorfisme dan Grup Hasil Bagi"},
        ],
        "source_binding": binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": binding(TARGET, TARGET_START, TARGET_END),
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [prerequisite_by_key[key] for key in PREREQUISITES],
        "rights_component_ids": [principal],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    source_cites = common.citation_occurrences(raw_source_text)
    target_cites = common.citation_occurrences(target_text)
    citations = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_cites, target_cites, strict=True), 1):
        _, bib_key, source_line = source_item
        _, _, target_line = target_item
        key = f"citation/unit-026/{ordinal:02d}-{bib_key.casefold()}"
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
        key = f"index-entry/unit-026/{stream}/{ordinal:03d}"
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
        key = f"diagram/unit-026/{source_format}-{occurrence:02d}"
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
        BIBLIOGRAPHY,
        "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf",
        "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-026-pdf"),
        "stable_key": "build-surface/unit-026-pdf",
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_026.ps1 -OutputDirectory build/unit-026-replay",
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
            "Biber",
            "PowerShell 7",
            "makeindex (main and sym1 streams)",
            "Poppler pdfinfo",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by the Unit 026 driver and AJbook.cls",
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
            "qa/unit-026/admission-gate",
            "admission_gate",
            "Complete source-order Section 4.2 admission: authority lines 177-364 with blank boundary line 364 omitted from the 187-record target mapping; 36 textual environment pairs including one commented align pair (35 active pairs), 12 labels, 18 ordinary and six equation references, one DN00 citation, 12 list items, 275 protected mathematical zones, ten indexes, three tikzcd diagrams with 12 arrows, 33 admitted terminology rows, four declared corrections O013-LI-U026-COR-001 through COR-004, and no exercises, hints, answers, or solutions. Component rights and independent production provenance remain distinct. Production provenance is " + MODEL + ".",
            VISUAL_REVIEW,
        ),
        qa_event("qa/unit-026/source-review", "backend_integrity", "Exact authority, translation, mathematics, identifier, diagram, citation, index, comment, and four-correction review.", REVIEW),
        qa_event("qa/unit-026/candidate-artifact", "backend_integrity", "Exact isolated 187-record Indonesian candidate binding; this candidate is evidence and is not a public-reader build input.", CANDIDATE),
        qa_event("qa/unit-026/candidate-check", "backend_integrity", "Fail-closed candidate checker binding the 188-record authority boundary, 187 mapped records, all protected mathematical zones, terminology, comments, and four corrections.", CANDIDATE_GATE),
        qa_event("qa/unit-026/canonical-integration", "backend_integrity", "Fail-closed canonical integration binding Unit 025 prefix, Unit 026 candidate, omitted blank boundary, untouched authority suffix, 374-row glossary, and 33-row delta.", STRUCTURE_GATE),
        qa_event("qa/unit-026/source-corrections", "backend_integrity", "Separate deterministic provenance for O013-LI-U026-COR-001, COR-002, COR-003, and COR-004; no other source correction is claimed.", REVIEW),
        qa_event("qa/unit-026/terminology-control", "backend_integrity", "Live id-ID glossary binding for exactly 374 unique rows including the 33 admitted Unit 026 rows.", TERMINOLOGY),
        qa_event("qa/unit-026/terminology-delta", "backend_integrity", "Exact reviewed 33-row terminology delta reproduced in the controlled glossary without rewriting baseline rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-026/terminology-evidence", "backend_integrity", "Bound Unit 026 terminology audit with exact row inventory, surface refinements, evidence limits, and model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-026/terminology-recommendation", "backend_integrity", "Bound candidate-locus and terminology evidence recommendation supporting the admitted Unit 026 forms.", TERMINOLOGY_RECOMMENDATION),
        qa_event("qa/unit-026/prepromotion-evidence", "backend_integrity", "Exact splice arithmetic for target lines 179-365, omission of boundary-only authority line 364, suffix continuity, and terminology append.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-026/build-log", "backend_integrity", "Final deterministic XeLaTeX, Biber, and dual-index build log with nine-page output and no fatal build markers.", FINAL_LOG),
        qa_event("qa/unit-026/structure-and-pdf-qa", "backend_integrity", "Machine-readable structure, PDF, renderer, page, and rights QA evidence for the exact final reader artifact.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-026/render-hash-inventory", "backend_integrity", "Exact all-page Poppler and MuPDF render identities, decoded-pixel comparisons, contact-sheet identities, and edge-contact gate for the final reader artifact.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-026/all-page-visual-review", "backend_integrity", "All-page Poppler and MuPDF visual review of the exact final nine-page Unit 026 reader.", VISUAL_REVIEW),
    ]

    prerequisite_ids = [prerequisite_by_key[key] for key in PREREQUISITES]
    titles = [
        {"language": "zh-Hans", "text": "第四章：同态和商群"},
        {"language": "id-ID", "text": "Bab 4: Homomorfisme dan Grup Hasil Bagi"},
    ]
    data["dataset_stable_key"] = "dataset/unit-026/id-id"
    data["dataset_id"] = uid(data["dataset_stable_key"])
    data["workflow"] = {
        "responsible_task": str(uuid.uuid5(namespace, "task/o013-li-u026-backend")),
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
        "order": 26,
        "source_local_id": "chapter4.tex:177-364; substantive record map 177-363",
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
            "outcome/construct-and-recognize-group-homomorphisms",
            "outcome/compute-images-kernels-and-quotient-groups",
            "outcome/apply-the-isomorphism-theorems",
            "outcome/classify-cyclic-groups-and-element-orders",
            "outcome/construct-grothendieck-group-completions",
            "outcome/interpret-group-completion-as-an-adjunction",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 1,
            "diagrams": 3,
            "index_entries": 10,
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
                "active_environment_pairs": 35,
                "labels": len(common.label_occurrences(raw_source_text)),
                "references": len(common.reference_occurrences(raw_source_text)),
                "citations": len(citations),
                "items": len(source_items),
                "protected_math_zones": len(source_math),
                "diagrams": len(diagrams),
                "diagram_arrows": len(source_arrows),
                "index_entries": len(index_entries),
                "terminology_rows": len(terminology_rows),
                "corrections": len(CORRECTIONS),
                "artifact": {"pages": page_count, "bytes": ARTIFACT_ID[0], "sha256": ARTIFACT_ID[1]},
                "csv_projections": [path.relative_to(ROOT).as_posix() for path in CSV_OUTPUTS],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
