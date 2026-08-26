#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 033.

Unit 033 is complete Section 4.9, symmetric groups. Schema-compatible concept
entities preserve every TeX environment, identifier, reference, list item,
diagram command, protected mathematical zone, admitted terminology row,
correction, localization, normalization, digital reflow, and production/reader
workaround surface. Generation fails closed unless authority, target, glossary,
build, PDF, rights, translation, and all-page visual evidence remain frozen.
"""

from __future__ import annotations

import argparse
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

import check_unit_033_candidate as candidate_check
import generate_unit_009_backend as binding_contract
import generate_unit_023_backend as topology_contract


ROOT = Path(__file__).resolve().parents[1]
UNIT_NUMBER = 33
UNIT_SLUG = "bab-4-grup-simetris"
UNIT_KEY = f"unit/{UNIT_SLUG}"
DATASET_KEY = "dataset/unit-033/id-id"
TASK_KEY = "task/o013-li-u033-backend"

TEMPLATE = "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
SCHEMA = "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-033-candidate/chapter4-symmetric-groups-id.tex"
CANDIDATE_GATE = "scripts/check_unit_033_candidate.py"
REVIEW = "qa/UNIT_033_TRANSLATION_REVIEW_20260825.md"
TARGET = "repo/source/chapter4.tex"
OUTPUT = "backend/data/unit-033-bab-4-grup-simetris.json"
EVIDENCE = "qa/unit-033-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_PAGE_COUNT = 10

TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_DELTA = "build/unit-033-staging/terminology-delta.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_033_TERMINOLOGY_AUDIT_20260826.md"
PREPROMOTION_AUDIT = "qa/UNIT_033_PREPROMOTION_AUDIT_20260826.md"
STRUCTURE_GATE = "scripts/check_unit_033_structure.py"
BUILD_SCRIPT = "scripts/build_unit_033.ps1"
DRIVER = "repo/source/unit-033-bab-4-grup-simetris.tex"
COVER = "repo/source/coverpage-id-unit-033.tex"
CROSSREF = "repo/source/unit-033-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
FINAL_LOG = "qa/UNIT_033_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_033_VISUAL_PREFLIGHT_20260826.md"
VISUAL_REVIEW = "qa/UNIT_033_VISUAL_QA_20260826.md"
STRUCTURE_PDF_QA = "qa/unit-033-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-033-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-033-bab-4-grup-simetris-id.pdf"
PREFLIGHT_SCRIPT = "scripts/preflight_unit_033.py"
EVIDENCE_SCRIPT = "scripts/generate_unit_033_evidence.py"

SOURCE_START, SOURCE_END = 1389, 1608
SOURCE_CONTENT_END = 1607
TARGET_START, TARGET_END = 1384, 1602

KNOWN_IDENTITIES: dict[str, tuple[int, str]] = {
    TEMPLATE: (352_612, "cceb010d8569c01e9fd7fb4149765da798a0c00409cadeb743a0326d192df29c"),
    SCHEMA: (21_358, "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3"),
    SOURCE: (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"),
    CANDIDATE: (23_099, "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76"),
    CANDIDATE_GATE: (18_099, "643b1ccc5fe1f47aa185cbb8d2813e971c1381cbcc032fac8cc01c2c941c2a1d"),
    REVIEW: (7_346, "1b17a513e690e6a90a071bf3af440870f2d11f135fb31b2f8cc32151135a6599"),
    BIBLIOGRAPHY: (29_580, "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e"),
    TERMINOLOGY_DELTA: (1_987, "783f39a1d80f93613f1d60c53ab77c7ce0a4c5c799c8ea25248f427e4049437b"),
}
SOURCE_SPAN_ID = (19_076, "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a")
SOURCE_CONTENT_SPAN_ID = (19_075, "0b9f86b7752ba26eeb6540c18e5ad62d3d498663fd29068e548630927142beb9")
PREINTEGRATION_TARGET_ID = (181_896, "4381ae10c0e44eca80c40c25d602af39ed9da2e3725a35968ad697d40cc7f680")

CSV_OUTPUTS = tuple(
    f"backend/csv/unit-033-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "array": 1, "cases": 1, "center": 4, "compactitem": 1,
        "corollary": 1, "definition": 2, "equation": 3, "gather*": 2,
        "gathered": 1, "inparaenum": 1, "itemize": 1, "lemma": 3,
        "proof": 7, "proposition": 1, "theorem": 2, "tikzcd": 1,
        "tikzpicture": 11,
    }
)

EXPECTED_COUNTS = {
    "source_records_including_blank_boundary": 220,
    "candidate_records": 219,
    "environment_pairs": 43,
    "environment_markers": 86,
    "labels": 10,
    "ordinary_references": 10,
    "equation_references": 10,
    "citations": 0,
    "list_items": 10,
    "protected_math_zones": 311,
    "diagrams": 12,
    "tikzcd_diagrams": 1,
    "tikzpicture_diagrams": 11,
    "diagram_arrows": 4,
    "braid_commands": 9,
    "draw_commands": 3,
    "node_commands": 10,
    "drawing_commands": 22,
    "index_entries": 9,
    "source_corrections": 2,
    "protected_text_localizations": 5,
    "index_localizations": 9,
    "terminology_normalizations": 2,
    "citation_locator_localizations": 0,
    "digital_reflows": 1,
    "exercises": 0,
    "hints": 0,
    "answers": 0,
    "solutions": 0,
    "csv_projections": 6,
}

CORE_STABLE_KEYS = (
    "concept/symmetric-group", "concept/permutation", "concept/permutation-support",
    "concept/fixed-point", "concept/cycle", "concept/cycle-length",
    "concept/transposition", "concept/disjoint-cycles",
    "concept/disjoint-cycle-decomposition", "concept/cycle-type",
    "concept/integer-partition", "concept/order-of-permutation",
    "concept/least-common-multiple", "concept/conjugacy-class",
    "concept/adjacent-transposition", "concept/sign-homomorphism",
    "concept/vandermonde-function", "concept/alternating-group",
    "concept/even-permutation", "concept/odd-permutation",
    "concept/index-two-subgroup", "concept/derived-subgroup",
    "concept/three-cycle", "concept/simple-group",
    "concept/nonabelian-simple-group", "concept/galois-simplicity-theorem",
    "concept/solvable-group", "concept/nonsolvability-of-symmetric-groups",
    "concept/braid", "concept/braid-diagram", "concept/braid-composition",
    "concept/braid-group", "concept/braid-relation",
    "concept/yang-baxter-equation", "concept/artin-braid-presentation",
    "concept/braid-to-symmetric-quotient", "concept/generators-and-relations",
    "concept/coxeter-presentation", "concept/coxeter-group",
    "concept/coxeter-matrix", "concept/dihedral-group",
)

# Exact admitted 13-row Unit 033 terminology delta, in live-glossary order.
TERMINOLOGY_PLAN = (
    ("permutation", "permutasi"), ("cycle", "siklus"),
    ("cyclic permutation", "permutasi siklik"),
    ("cycle length", "panjang siklus"), ("transposition", "transposisi"),
    ("disjoint cycles", "siklus-siklus yang saling lepas"),
    ("cycle decomposition", "dekomposisi siklus"),
    ("cycle type", "tipe siklus"),
    ("least common multiple", "kelipatan persekutuan terkecil"),
    ("even permutation", "permutasi genap"),
    ("odd permutation", "permutasi ganjil"),
    ("strand (braid)", "untai"), ("Coxeter group", "grup Coxeter"),
)

# Exact post-admission identities.  These values are independently rechecked by
# every normal invocation before any canonical backend output is written.
FREEZE_STATE = "frozen"
FROZEN_IDENTITIES: dict[str, tuple[int, str] | None] = {
    TARGET: (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde"),
    TERMINOLOGY: (76_280, "9a999be8091cfb9429975d6dcf98aca3d6d3b432ab909891651c9c32e0c79f4c"),
    TERMINOLOGY_AUDIT: (3_699, "efdb7d0cfd43484e2b6b36604e13c7bbcc4dcee188745c637703b164f8abae13"),
    PREPROMOTION_AUDIT: (4_828, "a6f22f8ef5f64cd499fffe3cb6a2ffb13ce9c019ca8ab468e5e6ccc3283dde43"),
    STRUCTURE_GATE: (12_660, "d018a2966e46fe44045c2159a420769fa2f1a0bd5992ecceb454ab98ebfc4e65"),
    BUILD_SCRIPT: (9_366, "640892442816eee59b93b5a2980236901d9caae5aeee4a503cdb204d73896fba"),
    PREFLIGHT_SCRIPT: (13_360, "b48f2ec4783c61cba8011c62e6fc887b61dc5549361a89b0bdbbb76d34805b93"),
    EVIDENCE_SCRIPT: (13_586, "22756db66cf9442613b97be542fd5c164e6ef6110c4c6062eab5e246ed2477e9"),
    DRIVER: (4_919, "0f95f282b9b49b5ef8df029b0b82d64842a9ae77a3fc9614f8bfb386c1fa5152"),
    COVER: (3_728, "628529893b6760bdc9e4b94771963d63e6e9d29c539a105e1bda0ca044079876"),
    CROSSREF: (330, "d565529f09777621e07513bdc82358e8b36bc953547482c52ee2ac4bf3698ff2"),
    FINAL_LOG: (75_964, "ecc90e94457ba8e47e08329ed38a342e58576546a0c2c1733756cf470be702e8"),
    VISUAL_PREFLIGHT: (659, "a1c355f432fa01d352c9b6e71c057c4f354edc32a15ff5285ca51d55956213ef"),
    VISUAL_REVIEW: (5_285, "c6380aa1402c7571242b21a08275e758ed7c189cf16b2e637e1220a01ec14e36"),
    STRUCTURE_PDF_QA: (27_516, "8edbcd847cedeb88f6f464d699e823864a77a8c4c077ec846228c51b177e707c"),
    RENDER_HASH_INVENTORY: (46_048, "7e0bc3fd33a0d1d8c44f6ec7bb43016eb9ea1b281139ae28b69ded144954b915"),
    ARTIFACT: (118_964, "0af07d45c9aee57e28a6f27fe6162afda253e15c44779ccf07ac591516bd1f1d"),
}
FROZEN_TARGET_SPAN_ID: tuple[int, str] | None = (23_099, "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76")
FROZEN_TERMINOLOGY_PAIRS: tuple[tuple[str, str], ...] = TERMINOLOGY_PLAN
FROZEN_GLOSSARY_ROW_COUNT: int | None = 478
FROZEN_PAGE_COUNT: int | None = 10
DIGITAL_REFLOWS = (1495,)
TERMINOLOGY_NORMALIZATIONS = (
    ("O013-LI-U033-TERMNORM-001", 1407, 1402, "unsur satuan", "unsur identitas"),
    ("O013-LI-U033-TERMNORM-002", 1516, 1511, "unsur satuan", "unsur identitas"),
)


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 033 backend refused: " + message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def require(condition: bool, message: str) -> None:
    if not condition:
        refuse(message)


def normalized_span(relative: str, first: int, last: int) -> bytes:
    return topology_contract.normalized_span(relative, first, last)


def live_binding(relative: str, first: int | None = None, last: int | None = None) -> dict[str, object]:
    """Use the same full-file plus normalized-line-span contract as Unit 031."""
    return binding_contract.binding(relative, first, last)


def namespace() -> uuid.UUID:
    data = json.loads((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    return uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))


def uuidv5(stable_key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(namespace(), stable_key))


def line_at(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def normalized_source_content() -> str:
    lines = normalized_span(SOURCE, SOURCE_START, SOURCE_CONTENT_END).decode("utf-8").splitlines()
    require(len(lines) == 219, "source substantive-record extraction drift")
    return "\n".join(
        candidate_check.normalize_authority_line(line, SOURCE_START + offset)
        for offset, line in enumerate(lines)
    ) + "\n"


def protected_math_occurrences(text: str) -> tuple[tuple[int, str, int, str], ...]:
    spans: list[tuple[int, str, str]] = []
    for kind, regex in (
        ("inline", candidate_check.INLINE_MATH_RE),
        ("display-bracket", candidate_check.DISPLAY_MATH_RE),
        ("display-environment", candidate_check.MATH_ENV_RE),
    ):
        for match in regex.finditer(text):
            value = match.group(2) if regex is candidate_check.MATH_ENV_RE else match.group(1)
            spans.append((match.start(), kind, candidate_check.normalize_math(value)))
    return tuple(
        (ordinal, kind, line_at(text, position), value)
        for ordinal, (position, kind, value) in enumerate(sorted(spans), 1)
    )


def drawing_commands(text: str) -> tuple[tuple[str, int], ...]:
    return tuple(
        (match.group(1), line_at(text, match.start()))
        for match in re.finditer(r"\\(braid|draw|node)(?![A-Za-z])", text)
    )


def target_state() -> str:
    target = ROOT / TARGET
    if not target.is_file():
        return "missing"
    target_payload = target.read_bytes()
    span = normalized_span(TARGET, TARGET_START, TARGET_END)
    if span == (ROOT / CANDIDATE).read_bytes():
        return "candidate-integrated"
    first = span.decode("utf-8").splitlines()[0]
    if first == r"\section{对称群}\label{sec:symmetric-group}":
        return "preintegration-authority"
    if first == r"\section{Grup Simetris}\label{sec:symmetric-group}":
        return "integrated-but-not-candidate-identical"
    return f"unexpected:{len(target_payload)}:{digest(target_payload)}"


def scaffold_check() -> dict[str, object]:
    for relative, expected in KNOWN_IDENTITIES.items():
        require((ROOT / relative).is_file(), f"missing required file: {relative}")
        require(identity(relative) == expected, f"identity drift: {relative}")

    source_span = normalized_span(SOURCE, SOURCE_START, SOURCE_END)
    source_content = normalized_span(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    require((len(source_span), digest(source_span)) == SOURCE_SPAN_ID, "authority boundary drift")
    require((len(source_content), digest(source_content)) == SOURCE_CONTENT_SPAN_ID, "authority content drift")
    require(source_span == source_content + b"\n", "authority line 1608 is not the single blank boundary")
    require(
        normalized_span(SOURCE, 1609, 1609).decode("utf-8").rstrip("\n")
        == r"\section{群的极限和完备化}\label{sec:group-limit}",
        "authority line 1609 next-section sentinel drift",
    )

    checked = subprocess.run(
        [sys.executable, "-B", str(ROOT / CANDIDATE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    require(checked.returncode == 0 and "PASS: O013-LI-U033" in checked.stdout,
            "isolated candidate checker failed\n" + checked.stdout + checked.stderr)

    source_text = source_content.decode("utf-8")
    normalized_source_text = normalized_source_content()
    candidate_text = (ROOT / CANDIDATE).read_text(encoding="utf-8")
    # The admitted source-target display reflow is normalized by the candidate
    # checker. Compare against that exact normalized authority projection while
    # candidate to the checker-normalized authority projection, while retaining
    # the raw authority text for immutable labels, references, citations,
    # diagrams, and indexes.
    source_env = topology_contract.environment_occurrences(normalized_source_text)
    candidate_env = topology_contract.environment_occurrences(candidate_text)
    require([(x[0], x[1]) for x in source_env] == [(x[0], x[1]) for x in candidate_env],
            "environment ordering drift")
    require(Counter(x[0] for x in source_env) == EXPECTED_ENVIRONMENTS, "environment census drift")

    source_labels = topology_contract.label_occurrences(source_text)
    candidate_labels = topology_contract.label_occurrences(candidate_text)
    require([x[0] for x in source_labels] == [x[0] for x in candidate_labels], "label drift")
    source_refs = topology_contract.reference_occurrences(source_text)
    candidate_refs = topology_contract.reference_occurrences(candidate_text)
    require([x[:2] for x in source_refs] == [x[:2] for x in candidate_refs], "reference drift")
    source_cites = topology_contract.citation_occurrences(source_text)
    candidate_cites = topology_contract.citation_occurrences(candidate_text)
    require([x[1] for x in source_cites] == [x[1] for x in candidate_cites], "citation-key drift")
    source_items = topology_contract.occurrence_lines(source_text, r"\\item(?![A-Za-z])")
    candidate_items = topology_contract.occurrence_lines(candidate_text, r"\\item(?![A-Za-z])")
    require(len(source_items) == len(candidate_items) == 10, "list-item drift")

    source_math = protected_math_occurrences(normalized_source_content())
    candidate_math = protected_math_occurrences(candidate_text)
    require([(x[1], x[3]) for x in source_math] == [(x[1], x[3]) for x in candidate_math],
            "protected mathematics drift")

    binding_contract.SPAN_START = SOURCE_START
    source_diagrams = binding_contract.diagram_occurrences(source_text)
    binding_contract.SPAN_START = TARGET_START
    candidate_diagrams = binding_contract.diagram_occurrences(candidate_text)
    require([(x[0], x[1]) for x in source_diagrams] == [(x[0], x[1]) for x in candidate_diagrams],
            "diagram order drift")
    source_arrows = topology_contract.occurrence_lines(source_text, r"\\arrow(?![A-Za-z])")
    candidate_arrows = topology_contract.occurrence_lines(candidate_text, r"\\arrow(?![A-Za-z])")
    require(len(source_arrows) == len(candidate_arrows) == 4, "diagram-arrow drift")
    require([x[0] for x in drawing_commands(source_text)] == [x[0] for x in drawing_commands(candidate_text)],
            "TikZ drawing-command drift")

    binding_contract.SPAN_START = SOURCE_START
    source_indexes = binding_contract.index_occurrences(source_text)
    binding_contract.SPAN_START = TARGET_START
    candidate_indexes = binding_contract.index_occurrences(candidate_text)
    require([x[0] for x in source_indexes] == [x[0] for x in candidate_indexes], "index-stream drift")

    actual = {
        "source_records_including_blank_boundary": 220,
        "candidate_records": len(candidate_text.splitlines()),
        "environment_pairs": len(source_env), "environment_markers": 2 * len(source_env),
        "labels": len(source_labels),
        "ordinary_references": sum(x[0] == "ordinary" for x in source_refs),
        "equation_references": sum(x[0] == "equation" for x in source_refs),
        "citations": len(source_cites), "list_items": len(source_items),
        "protected_math_zones": len(source_math), "diagrams": len(source_diagrams),
        "tikzcd_diagrams": sum(x[0] == "tikzcd" for x in source_diagrams),
        "tikzpicture_diagrams": sum(x[0] == "tikzpicture" for x in source_diagrams),
        "diagram_arrows": len(source_arrows),
        "braid_commands": sum(item[0] == "braid" for item in drawing_commands(source_text)),
        "draw_commands": sum(item[0] == "draw" for item in drawing_commands(source_text)),
        "node_commands": sum(item[0] == "node" for item in drawing_commands(source_text)),
        "drawing_commands": len(drawing_commands(source_text)),
        "index_entries": len(source_indexes), "source_corrections": 2,
        "protected_text_localizations": 5, "index_localizations": 9,
        "terminology_normalizations": 2, "citation_locator_localizations": 0,
        "digital_reflows": 1,
        "exercises": 0, "hints": 0, "answers": 0, "solutions": 0,
        "csv_projections": len(CSV_OUTPUTS),
    }
    require(actual == EXPECTED_COUNTS, f"topology expectation drift: {actual!r}")

    ns = namespace()
    stable_keys = (DATASET_KEY, UNIT_KEY, f"{UNIT_KEY}/section/01", *CORE_STABLE_KEYS)
    ids = {key: "urn:uuid:" + str(uuid.uuid5(ns, key)) for key in stable_keys}
    return {
        "status": "PASS_SCAFFOLD_ONLY", "unit": "unit-033-bab-4-grup-simetris",
        "authority": f"{SOURCE}:{SOURCE_START}-{SOURCE_END}",
        "authority_identity": {"bytes": SOURCE_SPAN_ID[0], "sha256": SOURCE_SPAN_ID[1]},
        "candidate": CANDIDATE,
        "candidate_identity": {"bytes": KNOWN_IDENTITIES[CANDIDATE][0], "sha256": KNOWN_IDENTITIES[CANDIDATE][1]},
        "projected_target": f"{TARGET}:{TARGET_START}-{TARGET_END}",
        "target_state": target_state(), "counts": actual,
        "namespace_uuid": str(ns), "stable_uuidv5_preview": ids,
        "core_concepts": len(CORE_STABLE_KEYS),
        "terminology_delta_rows_admitted": len(TERMINOLOGY_PLAN),
        "csv_outputs": list(CSV_OUTPUTS), "output_reserved": OUTPUT,
        "production_freeze_state": FREEZE_STATE,
    }


def require_identity(relative: str, expected: tuple[int, str] | None) -> None:
    require(expected is not None, f"unfrozen identity: {relative}")
    require((ROOT / relative).is_file(), f"missing frozen file: {relative}")
    require(identity(relative) == expected, f"identity drift: {relative}")


def span_text(relative: str, first: int, last: int) -> str:
    return normalized_span(relative, first, last).decode("utf-8")


def read_terminology_rows() -> tuple[tuple[dict[str, str], int, int], ...]:
    with (ROOT / TERMINOLOGY).open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(csv.DictReader(handle))
    require(
        len(rows) == FROZEN_GLOSSARY_ROW_COUNT
        and len({row.get("source_term") for row in rows}) == FROZEN_GLOSSARY_ROW_COUNT,
        "controlled glossary row/uniqueness drift",
    )
    with (ROOT / TERMINOLOGY_DELTA).open("r", encoding="utf-8", newline="") as handle:
        delta = tuple(csv.DictReader(handle))
    require(len(delta) == 13 and tuple(rows[-13:]) == delta, "thirteen-row Unit 033 glossary delta drift")
    by_source = {row["source_term"]: row for row in rows}
    target_lines = span_text(TARGET, TARGET_START, TARGET_END).splitlines()
    target_evidence_lines = [re.sub(r"\\emph\{([^{}]+)\}", r"\1", line) for line in target_lines]
    evidence_aliases: dict[str, str] = {}
    selected = []
    for source_term, target_term in TERMINOLOGY_PLAN:
        row = by_source.get(source_term)
        require(
            row is not None and row.get("target_term") == target_term
            and row.get("status") == "admitted" and row.get("scope") and row.get("note"),
            f"terminology admission drift: {source_term!r}",
        )
        fragment = evidence_aliases.get(source_term, target_term)
        occurrences = [i for i, line in enumerate(target_evidence_lines) if fragment.casefold() in line.casefold()]
        require(bool(occurrences), f"admitted term absent from target: {source_term!r}")
        relative = occurrences[0] + 1
        selected.append((row, SOURCE_START + relative - 1, TARGET_START + relative - 1))
    return tuple(selected)


def pdf_page_count() -> int:
    completed = subprocess.run(
        ["pdfinfo", str(ROOT / ARTIFACT)], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", check=False,
    )
    require(completed.returncode == 0, "pdfinfo failed\n" + completed.stderr)
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    require(match is not None, "pdfinfo returned no page count")
    return int(match.group(1))


def production_gate() -> tuple[int, tuple[tuple[dict[str, str], int, int], ...]]:
    require(FREEZE_STATE == "frozen", "production freeze state is not frozen")
    for relative, expected in (*KNOWN_IDENTITIES.items(), *FROZEN_IDENTITIES.items()):
        require_identity(relative, expected)
    require(FROZEN_TARGET_SPAN_ID is not None, "target span is not frozen")
    target_span = normalized_span(TARGET, TARGET_START, TARGET_END)
    require((len(target_span), digest(target_span)) == FROZEN_TARGET_SPAN_ID, "target span drift")
    require(target_span == (ROOT / CANDIDATE).read_bytes(), "target span differs from candidate")
    require(
        (len(normalized_span(SOURCE, SOURCE_START, SOURCE_END)), digest(normalized_span(SOURCE, SOURCE_START, SOURCE_END)))
        == SOURCE_SPAN_ID,
        "authority span drift",
    )

    candidate_run = subprocess.run(
        [sys.executable, "-B", str(ROOT / CANDIDATE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    require(candidate_run.returncode == 0 and "PASS: O013-LI-U033" in candidate_run.stdout,
            "candidate gate failed\n" + candidate_run.stdout + candidate_run.stderr)
    structure_run = subprocess.run(
        [sys.executable, "-B", str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    require(structure_run.returncode == 0 and "UNIT 033 STRUCTURE CHECK: PASS" in structure_run.stdout,
            "structure gate failed\n" + structure_run.stdout + structure_run.stderr)

    page_count = pdf_page_count()
    require(page_count == FROZEN_PAGE_COUNT == EXPECTED_PAGE_COUNT, "final reader page-count drift")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    for token in (
        "Undefined control sequence", "There were undefined references", "Citation `",
        "! LaTeX Error", "Emergency stop", "Fatal error", "Overfull \\hbox", "Overfull \\vbox",
    ):
        require(token not in final_log, f"final build log contains blocker {token!r}")
    # PTY capture may wrap both the path and the word ``pages``.
    page_hits = re.findall(r"Output written on .*?\((\d+)\s+p\s*a\s*g\s*e\s*s?", final_log, re.DOTALL)
    require(bool(page_hits) and int(page_hits[-1]) == page_count, "build-log page marker drift")

    structure_qa = json.loads((ROOT / STRUCTURE_PDF_QA).read_text(encoding="utf-8"))
    final_log_qa = structure_qa.get("final_build_log", {})
    documents_qa = structure_qa.get("documents", {})
    artifact_qa = documents_qa.get("artifact", {})
    require(
        structure_qa.get("status") == "PASS_WITH_WARNINGS"
        and structure_qa.get("actionable_defects") == []
        and structure_qa.get("cross_pdf_semantic_identity") is True
        and structure_qa.get("artifact_byte_identical_to_build_j") is True
        and artifact_qa.get("identity")
        == {"bytes": FROZEN_IDENTITIES[ARTIFACT][0], "path": ARTIFACT, "sha256": FROZEN_IDENTITIES[ARTIFACT][1]}
        and artifact_qa.get("pages") == EXPECTED_PAGE_COUNT
        and artifact_qa.get("safe") is True
        and artifact_qa.get("tagged") is False
        and len(artifact_qa.get("outline", [])) == 3
        and artifact_qa.get("action_counts") == {"/GoTo": 22, "/URI": 3}
        and artifact_qa.get("fonts", {}).get("all_embedded") is True
        and final_log_qa.get("identity")
        == {"bytes": FROZEN_IDENTITIES[FINAL_LOG][0], "path": FINAL_LOG, "sha256": FROZEN_IDENTITIES[FINAL_LOG][1]}
        and final_log_qa.get("page_marker") == EXPECTED_PAGE_COUNT
        and final_log_qa.get("nonfatal_underfull_hboxes") == 1
        and final_log_qa.get("sanitized_log_reproduced_from_build_j") is True
        and set(final_log_qa.get("forbidden_diagnostics", {}).values()) == {0},
        "structure/PDF evidence semantics drift",
    )
    require(
        set(documents_qa) == {"artifact", "build-i", "build-j"}
        and all(
            document.get("pages") == EXPECTED_PAGE_COUNT
            and document.get("safe") is True
            and document.get("tagged") is False
            and len(document.get("outline", [])) == 3
            and len(document.get("named_destinations", {})) == 35
            and document.get("action_counts") == {"/GoTo": 22, "/URI": 3}
            and document.get("fonts", {}).get("all_embedded") is True
            and document.get("fonts", {}).get("unique") == 27
            for document in documents_qa.values()
        ),
        "three-document PDF structure/navigation/font contract drift",
    )
    render = json.loads((ROOT / RENDER_HASH_INVENTORY).read_text(encoding="utf-8"))
    comparisons = render.get("decoded_pixel_comparisons", {})
    require(
        render.get("status") == "PASS_WITH_WARNINGS"
        and render.get("actionable_defects") == []
        and render.get("edge_gate") == {"all_60_zero_ink": True, "outer_band_pixels": 3}
        and render.get("manual_visual_review", {}).get("status") == "PASS"
        and len(render.get("manual_visual_review", {}).get("pages", {})) == EXPECTED_PAGE_COUNT
        and all(
            comparisons.get(renderer, {}).get(pair, {}).get("all_10_decoded_pixel_identical") is True
            for renderer in ("poppler", "mupdf")
            for pair in ("build-i_vs_build-j", "build-j_vs_artifact")
        ),
        "render inventory semantics drift",
    )
    renderers = render.get("renderers", {})
    require(
        len(render.get("contact_sheets", [])) == 6
        and set(renderers) == {"poppler", "mupdf"}
        and all(
            set(documents) == {"artifact", "build-i", "build-j"}
            and all(
                document.get("dpi") == 144
                and document.get("stdout") == ""
                and document.get("stderr") == ""
                and len(document.get("pages", [])) == EXPECTED_PAGE_COUNT
                for document in documents.values()
            )
            for documents in renderers.values()
        )
        and set(render.get("manual_visual_review", {}).get("pages", {}))
        == {str(page) for page in range(1, EXPECTED_PAGE_COUNT + 1)},
        "60-render/contact-sheet/manual-page evidence contract drift",
    )
    driver_text = (ROOT / DRIVER).read_text(encoding="utf-8")
    workaround = r"\renewcommand{\xlongequal}[2][]{\mathrel{\mathop{=}\limits^{\textstyle #2}}}"
    require(driver_text.count(workaround) == 1, "driver-only xlongequal workaround drift")
    require(workaround not in (ROOT / CANDIDATE).read_text(encoding="utf-8"),
            "reader workaround leaked into candidate mathematics")
    require(workaround not in target_span.decode("utf-8"),
            "reader workaround leaked into canonical source span")
    for witness in (DRIVER, COVER, TERMINOLOGY_AUDIT, VISUAL_PREFLIGHT, VISUAL_REVIEW):
        require(MODEL in re.sub(r"\s+", " ", (ROOT / witness).read_text(encoding="utf-8")),
                f"exact production-model provenance absent: {witness}")
    return page_count, read_terminology_rows()


def generate_backend() -> dict[str, object]:
    page_count, terminology_rows = production_gate()
    data = copy.deepcopy(json.loads((ROOT / TEMPLATE).read_text(encoding="utf-8")))
    ns = namespace()
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(ns, key))
    unit_key = UNIT_KEY
    unit_id = uid(unit_key)
    raw_source = span_text(SOURCE, SOURCE_START, SOURCE_CONTENT_END)
    normalized_source = normalized_source_content()
    target_text = span_text(TARGET, TARGET_START, TARGET_END)

    supplemental_prerequisites = (
        ("prerequisite/group-homomorphisms-kernels-and-quotients", "群同态、核与商群", "homomorfisme grup, kernel, dan grup hasil bagi", 177, 364),
        ("prerequisite/group-actions-orbits-and-stabilizers", "群作用、轨道与稳定化子", "aksi grup, orbit, dan stabilisator", 518, 665),
        ("prerequisite/commutators-derived-series-and-solvability", "换位子、导出列与可解性", "komutator, deret turunan, dan solvabilitas", 906, 1107),
    )
    existing = {item["stable_key"] for item in data["prerequisites"]}
    for key, zh, ind, first, last in supplemental_prerequisites:
        if key not in existing:
            data["prerequisites"].append({
                "id": uid(key), "stable_key": key, "entity_type": "prerequisite",
                "labels": [{"language": "zh-Hans", "text": zh}, {"language": "id-ID", "text": ind}],
                "requiredness": "expected",
                "source_evidence": {"path": SOURCE, "line_start": first, "line_end": last},
            })
    prerequisites = (
        "prerequisite/basic-mathematical-literacy", "prerequisite/elementary-set-theory",
        "prerequisite/basic-group-theory", "prerequisite/group-homomorphisms-kernels-and-quotients",
        "prerequisite/group-actions-orbits-and-stabilizers",
        "prerequisite/commutators-derived-series-and-solvability",
    )

    concepts: list[dict[str, object]] = []
    def add_concept(key: str, source_label: str, target_label: str, language: str = "en") -> None:
        concepts.append({
            "id": uid(key), "stable_key": key, "entity_type": "concept",
            "labels": [{"language": language, "text": source_label}, {"language": "id-ID", "text": target_label}],
        })

    for key in CORE_STABLE_KEYS:
        label = key.removeprefix("concept/").replace("-", " ")
        add_concept(key, label, label)

    source_env = topology_contract.environment_occurrences(normalized_source)
    target_env = topology_contract.environment_occurrences(target_text)
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        target_environment, target_occurrence, target_first, target_last = target_item
        require((environment, occurrence) == (target_environment, target_occurrence), f"environment pairing drift: {ordinal}")
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-033/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; normalized authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}",
        )
    for ordinal, (source_item, target_item) in enumerate(zip(topology_contract.label_occurrences(raw_source), topology_contract.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item; target_label, target_line = target_item
        require(label == target_label, f"label pairing drift: {ordinal}")
        add_concept(f"surface/unit-033/label/{ordinal:03d}", f"label {label}; authority line {SOURCE_START + source_line - 1}", f"label {label}; baris target {TARGET_START + target_line - 1}")
    for ordinal, (source_item, target_item) in enumerate(zip(topology_contract.reference_occurrences(raw_source), topology_contract.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item; target_kind, target_label, target_line = target_item
        require((kind, label) == (target_kind, target_label), f"reference pairing drift: {ordinal}")
        add_concept(f"surface/unit-033/reference/{kind}/{ordinal:03d}", f"{kind} reference {label}; authority line {SOURCE_START + source_line - 1}", f"rujukan {kind} {label}; baris target {TARGET_START + target_line - 1}")
    source_items = topology_contract.occurrence_lines(raw_source, r"\\item(?![A-Za-z])")
    target_items = topology_contract.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(f"surface/unit-033/item/{ordinal:03d}", f"list item; authority line {SOURCE_START + source_line - 1}", f"butir daftar; baris target {TARGET_START + target_line - 1}")
    source_arrows = topology_contract.occurrence_lines(raw_source, r"\\arrow(?![A-Za-z])")
    target_arrows = topology_contract.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(f"surface/unit-033/diagram-arrow/{ordinal:03d}", f"tikzcd arrow; authority line {SOURCE_START + source_line - 1}", f"panah tikzcd; baris target {TARGET_START + target_line - 1}")
    for ordinal, (source_item, target_item) in enumerate(zip(drawing_commands(raw_source), drawing_commands(target_text), strict=True), 1):
        command, source_line = source_item; target_command, target_line = target_item
        require(command == target_command, f"drawing-command pairing drift: {ordinal}")
        add_concept(f"surface/unit-033/drawing-command/{ordinal:03d}-{command}", f"TikZ {command}; authority line {SOURCE_START + source_line - 1}", f"perintah TikZ {command}; baris target {TARGET_START + target_line - 1}")
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(target_text)
    for source_item, target_item in zip(source_math, target_math, strict=True):
        ordinal, kind, source_line, formula = source_item
        _, target_kind, target_line, target_formula = target_item
        require((kind, formula) == (target_kind, target_formula), f"protected-math pairing drift: {ordinal}")
        formula_hash = digest(formula.encode("utf-8"))
        add_concept(f"surface/unit-033/protected-math-zone/{ordinal:03d}-{kind}", f"protected {kind} zone; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {formula_hash}", f"zona matematika terlindungi {kind}; baris target {TARGET_START + target_line - 1}; SHA-256 {formula_hash}")
    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PLAN[ordinal - 1]
        add_concept(f"surface/unit-033/terminology-row/{ordinal:03d}", f"terminology row: {source_term}; representative authority line {source_line}", f"baris terminologi: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}")

    corrections = (
        ("O013-LI-U033-COR-001", 1580, 1575, "generator-list endpoint tilde-tau_n", "endpoint tilde-tau_{n-1}"),
        ("O013-LI-U033-COR-002", 1591, 1586, "missing cardinality bars on S'_n", "cardinality |S'_n|"),
    )
    for correction_id, source_line, target_line, issue, repair in corrections:
        add_concept(f"correction/{correction_id.casefold()}", f"declared source correction {correction_id}; authority line {source_line}; {issue}; evidence {REVIEW}", f"koreksi sumber {correction_id}; baris target {target_line}; {repair}; bukti {REVIEW}")

    localization_ordinal = 0
    for source_line, replacements in candidate_check.PROTECTED_TEXT_REPLACEMENTS.items():
        for source_fragment, target_fragment in replacements:
            localization_ordinal += 1
            local_id = f"O013-LI-U033-LOC-{localization_ordinal:03d}"
            add_concept(f"protected-text-localization/{local_id.casefold()}", f"protected-text localization {local_id}; authority line {source_line}; {source_fragment}; evidence {REVIEW}", f"lokalisasi teks terlindungi {local_id}; baris target {source_line - 5}; {target_fragment}; bukti {REVIEW}")

    source_citation_occurrences = topology_contract.citation_occurrences(raw_source)
    target_citation_occurrences = topology_contract.citation_occurrences(target_text)
    citation_localization_ordinal = 0
    for source_item, target_item in zip(source_citation_occurrences, target_citation_occurrences, strict=True):
        source_note, source_key, source_line = source_item
        target_note, target_key, target_line = target_item
        require(source_key == target_key, "citation key drift")
        if source_note != target_note:
            citation_localization_ordinal += 1
            local_id = f"O013-LI-U033-CITELOC-{citation_localization_ordinal:03d}"
            add_concept(f"citation-locator-localization/{local_id.casefold()}", f"citation-locator localization {local_id}; key {source_key}; authority line {SOURCE_START + source_line - 1}; {source_note}; evidence {REVIEW}", f"lokalisasi penunjuk sitasi {local_id}; kunci {target_key}; baris target {TARGET_START + target_line - 1}; {target_note}; bukti {REVIEW}")
    for norm_id, source_line, target_line, issue, repair in TERMINOLOGY_NORMALIZATIONS:
        add_concept(
            f"terminology-normalization/{norm_id.casefold()}",
            f"target terminology normalization {norm_id}; aligned authority line {source_line}; older target synonym {issue}; evidence {TERMINOLOGY_AUDIT}",
            f"normalisasi terminologi target {norm_id}; baris target {target_line}; bentuk terkendali {repair}; bukti {TERMINOLOGY_AUDIT}",
        )
    for ordinal, source_line in enumerate(DIGITAL_REFLOWS, 1):
        reflow_id = f"O013-LI-U033-REFLOW-{ordinal:03d}"
        add_concept(f"digital-reflow/{reflow_id.casefold()}", f"source-target digital reflow {reflow_id}; authority line {source_line}; unchanged Klein-four equality; evidence {PREPROMOTION_AUDIT}", f"reflow digital sumber-target {reflow_id}; baris target {source_line - 5}; matematika display; bukti {PREPROMOTION_AUDIT}")
    add_concept("provenance/o013-li-u033-production", f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.", f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.")

    require(localization_ordinal == 5 and citation_localization_ordinal == 0, "localization census drift")
    require(len(concepts) == 485 and len({item["stable_key"] for item in concepts}) == 485,
            f"concept-compatible entity census drift: {len(concepts)}")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    require(set(prerequisites).issubset(prerequisite_by_key), "required prerequisite absent")
    rights_by_key = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights_by_key) == {"rights/principal-cc-by-4.0", "rights/lanzhou-cc-by-sa-3.0", "rights/ajbook-fragment-cc-by-sa-3.0", "rights/noto-fonts-ofl-1.1"}, "rights inventory drift")
    rights_by_key["rights/principal-cc-by-4.0"]["bindings"] = [live_binding(path) for path in (SOURCE, CANDIDATE, TARGET, BIBLIOGRAPHY, "repo/source/LICENSE", "repo/source/ccby.png")]
    rights_by_key["rights/principal-cc-by-4.0"]["applies_to_unit"] = True
    rights_by_key["rights/lanzhou-cc-by-sa-3.0"]["applies_to_unit"] = False
    rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["applies_to_unit"] = True
    rights_by_key["rights/noto-fonts-ofl-1.1"]["applies_to_unit"] = True
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    unit_rights = [principal, rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"], rights_by_key["rights/noto-fonts-ofl-1.1"]["id"]]

    section_key = f"{unit_key}/section/01"
    section_id = uid(section_key)
    prerequisite_ids = [prerequisite_by_key[key] for key in prerequisites]
    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section",
        "parent_id": unit_id, "order": 1,
        "source_local_id": "chapter4.tex:1389-1608 (line 1608 blank boundary omitted from target mapping)",
        "titles": [{"language": "zh-Hans", "text": "对称群"}, {"language": "id-ID", "text": "Grup Simetris"}],
        "source_binding": live_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": live_binding(TARGET, TARGET_START, TARGET_END),
        "concept_ids": [item["id"] for item in concepts], "prerequisite_ids": prerequisite_ids,
        "rights_component_ids": [principal], "translation_state": "visually_checked", "admission_state": "admitted",
    }

    citations = []
    seen_bib_keys: set[str] = set()
    for source_item, target_item in zip(source_citation_occurrences, target_citation_occurrences, strict=True):
        _, bib_key, source_line = source_item; _, target_key, target_line = target_item
        require(bib_key == target_key, "citation pairing drift")
        if bib_key in seen_bib_keys:
            continue
        seen_bib_keys.add(bib_key)
        ordinal = len(citations) + 1
        key = f"citation/unit-033/{ordinal:02d}-{bib_key.casefold()}"
        citations.append({
            "id": uid(key), "stable_key": key, "entity_type": "citation", "bib_key": bib_key,
            "bibliography_path": BIBLIOGRAPHY, "bibliography_sha256": KNOWN_IDENTITIES[BIBLIOGRAPHY][1],
            "source_line": SOURCE_START + source_line - 1, "target_line": TARGET_START + target_line - 1,
            "section_id": section_id,
        })
    binding_contract.SPAN_START = SOURCE_START
    source_indexes = binding_contract.index_occurrences(raw_source)
    binding_contract.SPAN_START = TARGET_START
    target_indexes = binding_contract.index_occurrences(target_text)
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes, strict=True), 1):
        stream, source_key, source_line = source_item; target_stream, target_key, target_line = target_item
        require(stream == target_stream, f"index-stream drift: {ordinal}")
        key = f"index-entry/unit-033/{stream}/{ordinal:03d}"
        index_entries.append({
            "id": uid(key), "stable_key": key, "entity_type": "index_entry", "section_id": section_id,
            "ordinal_in_unit": ordinal, "source_key": source_key, "target_key": target_key,
            "source_binding": live_binding(SOURCE, source_line, source_line),
            "target_binding": live_binding(TARGET, target_line, target_line),
            "provenance_state": "source_key_preserved_target_key_localized",
        })
    binding_contract.SPAN_START = SOURCE_START
    source_diagrams = binding_contract.diagram_occurrences(raw_source)
    binding_contract.SPAN_START = TARGET_START
    target_diagrams = binding_contract.diagram_occurrences(target_text)
    diagrams = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        source_format, occurrence, source_first, source_last = source_item
        target_format, target_occurrence, target_first, target_last = target_item
        require((source_format, occurrence) == (target_format, target_occurrence), f"diagram pairing drift: {ordinal}")
        key = f"diagram/unit-033/{source_format}-{occurrence:02d}"
        diagrams.append({
            "id": uid(key), "stable_key": key, "entity_type": "diagram", "section_id": section_id,
            "ordinal_in_unit": ordinal, "source_format": source_format, "source_occurrence_index": occurrence,
            "source_binding": live_binding(SOURCE, source_first, source_last),
            "target_binding": live_binding(TARGET, target_first, target_last),
            "rights_component_id": principal, "state": "audited_preserved",
        })

    inputs = [
        COVER, TARGET, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls",
        "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex", "repo/source/titles-setup.tex",
        "repo/source/mycommand.sty", "repo/source/myarrows.sty", BIBLIOGRAPHY,
        "repo/source/ccby.png", CROSSREF, "repo/fonts/NotoSansCJKsc-Black.otf",
        "repo/fonts/NotoSansCJKsc-Medium.otf", "repo/fonts/NotoSansCJKsc-Regular.otf",
        "repo/fonts/NotoSerifCJKsc-Bold.otf",
    ]
    build = {
        "id": uid("build-surface/unit-033-pdf"), "stable_key": "build-surface/unit-033-pdf",
        "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_033.ps1 -OutputDirectory build/unit-033-replay",
        "artifact_path": ARTIFACT, "artifact_binding": live_binding(ARTIFACT), "log_binding": live_binding(FINAL_LOG),
        "build_script": live_binding(BUILD_SCRIPT), "page_count": page_count, "status": "pass",
        "driver": live_binding(DRIVER), "input_bindings": [live_binding(path) for path in inputs],
        "external_dependencies": ["XeLaTeX", "PowerShell 7", "Biber", "makeindex", "Poppler pdfinfo", "Noto CJK fonts", "packages loaded by the Unit 033 driver and AJbook.cls"],
        "rights_component_ids": unit_rights,
    }
    def qa_event(key: str, check_type: str, scope: str, witness: str) -> dict[str, object]:
        return {
            "id": uid(key), "stable_key": key, "entity_type": "qa_event", "unit_id": unit_id,
            "check_type": check_type, "result": "pass", "scope": scope, "witness": witness,
            "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass",
            "witness_binding": live_binding(witness),
        }
    qa_events = [
        qa_event("qa/unit-033/admission-gate", "admission_gate", "Complete Section 4.9 admission: authority lines 1389-1608, 219 substantive target records at 1384-1602, 43 environment pairs, 10 labels, 20 references, no citations, 9 localized indexes, 12 diagrams, 4 arrows, 9 braid commands, 3 draw commands, 10 node commands, 311 protected mathematical zones, 13 admitted terminology rows, 2 source corrections, 5 protected-text localizations, 2 terminology normalizations, 1 source-target display reflow, and no exercises, hints, answers, or solutions. CC BY 4.0 content, AJbook fragment, and Noto font rights remain separate; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.", VISUAL_REVIEW),
        qa_event("qa/unit-033/source-review", "backend_integrity", "Exact authority, translation, mathematical, identifier, correction, localization, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-033/candidate-artifact", "backend_integrity", "Exact isolated Indonesian candidate binding.", CANDIDATE),
        qa_event("qa/unit-033/candidate-check", "backend_integrity", "Fail-closed candidate topology and semantic check.", CANDIDATE_GATE),
        qa_event("qa/unit-033/canonical-integration", "backend_integrity", "Fail-closed target splice, glossary, and source-order check.", STRUCTURE_GATE),
        qa_event("qa/unit-033/source-corrections", "backend_integrity", "Two declared high-confidence source corrections.", REVIEW),
        qa_event("qa/unit-033/terminology-normalizations", "backend_integrity", "Two target synonym normalizations from unsur satuan to corpus-controlled unsur identitas, distinct from source corrections.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-033/digital-reflow", "backend_integrity", "One source-target display reflow with protected mathematical identity preserved.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-033/protected-text-localizations", "backend_integrity", "Five protected mathematical-text localizations.", REVIEW),
        qa_event("qa/unit-033/index-localizations", "backend_integrity", "Nine index entries preserve stream/order and localize their target keys.", REVIEW),
        qa_event("qa/unit-033/terminology-control", "backend_integrity", "Live 478-row id-ID glossary.", TERMINOLOGY),
        qa_event("qa/unit-033/terminology-delta", "backend_integrity", "Exact 13-row admitted terminology delta.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-033/terminology-evidence", "backend_integrity", "Bound terminology audit and production-model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-033/prepromotion-evidence", "backend_integrity", "Exact splice, corrections, localizations, reflow, and source-order evidence.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-033/build-log", "backend_integrity", "Final 10-page XeLaTeX/Biber/index build log without fatal, unresolved, citation, missing-character, empty-target, or overfull diagnostics.", FINAL_LOG),
        qa_event("qa/unit-033/driver-poppler-xlongequal-workaround", "backend_integrity", "Reader-driver-only robust xlongequal rendering workaround preserves labelled equality semantics and changes no candidate or canonical-source mathematics.", DRIVER),
        qa_event("qa/unit-033/preflight-tool", "backend_integrity", "Frozen all-page dual-renderer/PDF preflight implementation.", PREFLIGHT_SCRIPT),
        qa_event("qa/unit-033/evidence-tool", "backend_integrity", "Frozen structure/PDF and render-evidence generator implementation.", EVIDENCE_SCRIPT),
        qa_event("qa/unit-033/visual-preflight", "backend_integrity", "All-page dual-renderer preflight and deterministic decoded-pixel comparison.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-033/structure-and-pdf-qa", "backend_integrity", "Machine-readable PDF structure, metadata, safety, build-log, and exact artifact checks.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-033/render-hash-inventory", "backend_integrity", "All 60 renders pass the edge gate and defined same-renderer deterministic comparisons.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-033/all-page-visual-review", "backend_integrity", "Independent full-resolution review of all 10 pages in Poppler and MuPDF with no actionable defect.", VISUAL_REVIEW),
    ]

    data["dataset_stable_key"] = DATASET_KEY
    data["dataset_id"] = uid(DATASET_KEY)
    data["workflow"] = {"responsible_task": str(uuid.uuid5(ns, TASK_KEY)), "updated": "2026-08-26", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_math_backend_build_visual_pass"}
    data["unit"] = {
        "id": unit_id, "stable_key": unit_key, "entity_type": "unit",
        "program_id": data["program"]["id"], "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"], "order": UNIT_NUMBER,
        "source_local_id": "chapter4.tex:1389-1608; substantive authority map 1389-1607 to target 1384-1602",
        "titles": [{"language": "zh-Hans", "text": "第四章：对称群"}, {"language": "id-ID", "text": "Bab 4: Grup Simetris"}],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": live_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": live_binding(TARGET, TARGET_START, TARGET_END),
        "section_ids": [section_id], "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations], "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries], "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": ["outcome/decompose-permutations-into-disjoint-cycles", "outcome/use-sign-and-alternating-groups", "outcome/prove-simplicity-and-nonsolvability-results", "outcome/read-braid-and-coxeter-presentations"],
        "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 0, "diagrams": 12, "index_entries": 9},
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build]
    data["qa_events"] = qa_events

    output = ROOT / OUTPUT
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    completed = subprocess.run([
        sys.executable, "-B", str(ROOT / "scripts/validate_backend.py"), "--lane-root", str(ROOT),
        "--data", str(output), "--schema", str(ROOT / SCHEMA), "--csv-dir", str(ROOT / "backend/csv"), "--write-csv",
    ], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    require(completed.returncode == 0, "shared validator/projection failed\n" + completed.stdout + completed.stderr)
    require(all((ROOT / path).is_file() for path in CSV_OUTPUTS), "missing CSV projection")
    return {
        "path": OUTPUT, "bytes": output.stat().st_size, "sha256": digest(output.read_bytes()),
        "sections": 1, "concepts": len(concepts), "textual_environment_pairs": 43,
        "labels": 10, "references": 20, "citation_occurrences": 0, "citations": len(citations), "items": 10,
        "protected_math_zones": 311, "diagrams": len(diagrams), "diagram_arrows": 4,
        "drawing_commands": 22, "braid_commands": 9, "draw_commands": 3, "node_commands": 10,
        "index_entries": len(index_entries), "index_localizations": 9, "terminology_rows": 13,
        "source_corrections": 2, "protected_text_localizations": 5,
        "terminology_normalizations": 2, "citation_locator_localizations": 0, "digital_reflows": 1,
        "driver_rendering_workarounds": 1,
        "qa_events": len(qa_events),
        "artifact": {"pages": page_count, "bytes": FROZEN_IDENTITIES[ARTIFACT][0], "sha256": FROZEN_IDENTITIES[ARTIFACT][1]},
        "csv_projections": list(CSV_OUTPUTS),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scaffold-check", action="store_true")
    args = parser.parse_args()
    if args.scaffold_check:
        print(json.dumps(scaffold_check(), ensure_ascii=False, sort_keys=True))
        return
    scaffold_check()
    print(json.dumps(generate_backend(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
