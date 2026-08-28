#!/usr/bin/env python3
"""Generate the admission-gated modular backend for Li Volume 1 Unit 034.

Unit 034 is complete Section 4.10, group limits and completions.  The emitted
schema-compatible entities preserve every TeX environment, identifier,
reference, list item, protected mathematical zone, admitted terminology row,
declared correction/localization/reflow, citation, index, diagram, rights
component, build surface, and QA witness.  Generation fails closed unless the
authority, candidate, canonical target, glossary, reader, PDF, and all-page
evidence remain at their frozen production identities.
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

import check_unit_034_candidate as candidate_check
import generate_unit_009_backend as binding_contract
import generate_unit_023_backend as topology_contract


ROOT = Path(__file__).resolve().parents[1]
UNIT_NUMBER = 34
UNIT_SLUG = "bab-4-limit-dan-kompletisasi-grup"
UNIT_KEY = f"unit/{UNIT_SLUG}"
DATASET_KEY = "dataset/unit-034/id-id"
TASK_KEY = "task/o013-li-u034-backend"

TEMPLATE = "backend/data/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.json"
SCHEMA = "backend/schema/open-math-corpus-unit.schema.v1.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
CANDIDATE = "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
CANDIDATE_GATE = "scripts/check_unit_034_candidate.py"
REVIEW = "qa/UNIT_034_TRANSLATION_REVIEW_20260825.md"
TARGET = "repo/source/chapter4.tex"
OUTPUT = "backend/data/unit-034-bab-4-limit-dan-kompletisasi-grup.json"
EVIDENCE = "qa/unit-034-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_PAGE_COUNT = 9

TERMINOLOGY = "00_control/TERMINOLOGY.id-ID.csv"
TERMINOLOGY_DELTA = "build/unit-034-staging/terminology-delta.csv"
TERMINOLOGY_AUDIT = "qa/UNIT_034_TERMINOLOGY_AUDIT_20260827.md"
PREPROMOTION_AUDIT = "qa/UNIT_034_PREPROMOTION_AUDIT_20260827.md"
STRUCTURE_GATE = "scripts/check_unit_034_structure.py"
BUILD_SCRIPT = "scripts/build_unit_034.ps1"
DRIVER = "repo/source/unit-034-bab-4-limit-dan-kompletisasi-grup.tex"
COVER = "repo/source/coverpage-id-unit-034.tex"
CROSSREF = "repo/source/unit-034-crossrefs.aux"
BIBLIOGRAPHY = "repo/source/Al-jabr.bib"
FINAL_LOG = "qa/UNIT_034_BUILD_FINAL.log"
VISUAL_PREFLIGHT = "qa/UNIT_034_VISUAL_PREFLIGHT_20260827.md"
VISUAL_REVIEW = "qa/UNIT_034_VISUAL_QA_20260827.md"
STRUCTURE_PDF_QA = "qa/unit-034-evidence/structure-and-pdf-qa.json"
RENDER_HASH_INVENTORY = "qa/unit-034-evidence/render-hash-inventory.json"
ARTIFACT = "artifacts/unit-034-bab-4-limit-dan-kompletisasi-grup-id.pdf"
PREFLIGHT_SCRIPT = "scripts/preflight_unit_034.py"
EVIDENCE_SCRIPT = "scripts/generate_unit_034_evidence.py"
FANDOL_AUTHORITY = "repo/fonts/FANDOL-AUTHORITY.json"
FANDOL_LICENSE = "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt"
FANDOL_README = "repo/fonts/FANDOL-README.txt"

SOURCE_START, SOURCE_END = 1609, 1744
SOURCE_CONTENT_END = 1743
TARGET_START, TARGET_END = 1604, 1738
TARGET_BOUNDARY_BLANK = 1739
TARGET_NEXT_SENTINEL = 1740

KNOWN_IDENTITIES: dict[str, tuple[int, str]] = {
    TEMPLATE: (352_612, "cceb010d8569c01e9fd7fb4149765da798a0c00409cadeb743a0326d192df29c"),
    SCHEMA: (21_358, "bad45d310e429926f1c05283232e6f8ccc7a7461c0c99faea8509497054efbc3"),
    SOURCE: (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"),
    CANDIDATE: (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62"),
    CANDIDATE_GATE: (16_590, "7b444643a1ccc1705690c64d099722844a30f40f0d97f04200095f0aaa40caf7"),
    REVIEW: (12_856, "e849ba49aa9cc96e3c841dfe0b383ccf4eeed6793e3cd50af18b924e5735e909"),
    BIBLIOGRAPHY: (29_580, "4979570eb4e3a9edcddd2f975790e56c98dcb3201e03e0a1fbdd64ba60c8263e"),
    TERMINOLOGY_DELTA: (6_613, "077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659"),
    FANDOL_AUTHORITY: (2_557, "1b74145b289d1c87f79f2e633934f10404adf9a4c02349c7db523de63b892a1f"),
    FANDOL_LICENSE: (35_737, "853b586f0d520493390e571431afaf36a5fbb27dcfd239338a7ee9b0505cb004"),
    FANDOL_README: (645, "32537e063f4c7d4aebf016d5c8279cbce13f34fc8970f24b2578a3c04d0f8ca6"),
}
SOURCE_SPAN_ID = (15_005, "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab")
SOURCE_CONTENT_SPAN_ID = (15_004, "1c331cf956dac84f46e3bb156efd3f8a26fc91e04de067bf59618cd70514649f")
PREINTEGRATION_TARGET_ID = (185_920, "a462826136cced1b766a2807ca61e055539bd4427b5f5da89df4573bdbbeccde")

CSV_OUTPUTS = tuple(
    f"backend/csv/unit-034-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 1, "aligned": 1, "compactitem": 1, "definition": 4,
        "enumerate": 1, "equation": 1, "equation*": 1, "example": 2,
        "lemma": 3, "proof": 5, "remark": 2, "theorem": 2, "tikzcd": 1,
    }
)

EXPECTED_COUNTS = {
    "source_records_including_blank_boundary": 136,
    "candidate_records": 135,
    "environment_pairs": 25,
    "environment_markers": 50,
    "labels": 11,
    "ordinary_references": 16,
    "equation_references": 0,
    "citation_occurrences": 6,
    "citation_keys": 2,
    "list_items": 5,
    "protected_math_zones": 276,
    "diagrams": 1,
    "tikzcd_diagrams": 1,
    "tikzpicture_diagrams": 0,
    "diagram_arrows": 12,
    "drawing_commands": 0,
    "index_entries": 6,
    "source_corrections": 1,
    "protected_text_localizations": 9,
    "index_localizations": 6,
    "terminology_rows": 37,
    "terminology_normalizations": 0,
    "citation_locator_localizations": 3,
    "digital_reflows": 1,
    "exercises": 0,
    "hints": 0,
    "answers": 0,
    "solutions": 0,
    "csv_projections": 6,
}

CORE_STABLE_KEYS = (
    "concept/inverse-limit", "concept/direct-limit", "concept/filtered-poset",
    "concept/topological-group", "concept/neighborhood-basis",
    "concept/product-topology", "concept/hausdorff-space", "concept/compact-space",
    "concept/tychonoff-theorem", "concept/open-subgroup", "concept/closed-subgroup",
    "concept/profinite-group", "concept/totally-disconnected-space",
    "concept/group-completion", "concept/cauchy-sequence", "concept/discrete-topology",
    "concept/p-adic-integer", "concept/p-adic-additive-group", "concept/tate-module",
    "concept/rational-tate-module", "concept/elliptic-curve", "concept/homology",
)

# Exact admitted 37-row Unit 034 terminology delta, in delta-file order.
TERMINOLOGY_PLAN = (
    ("completion", "pelengkapan"), ("completeness", "kelengkapan"),
    ("point-set topology", "topologi himpunan titik"),
    ("topological group", "grup topologis"),
    ("topological group homomorphism", "homomorfisme grup topologis"),
    ("continuous map", "peta kontinu"), ("neighborhood", "lingkungan"),
    ("open neighborhood", "lingkungan terbuka"),
    ("neighborhood basis", "basis lingkungan"),
    ("closed neighborhood", "lingkungan tertutup"),
    ("homeomorphism", "homeomorfisme"), ("closure (topology)", "penutup"),
    ("open cover", "liput terbuka"), ("Hausdorff space", "ruang Hausdorff"),
    ("compact (topology)", "kompak"),
    ("compact Hausdorff space", "ruang Hausdorff kompak"),
    ("product topology", "topologi produk"), ("profinite group", "grup profinit"),
    ("totally disconnected", "tak terhubung total"),
    ("reverse inclusion", "inklusi terbalik"),
    ("group completion", "pelengkapan grup"),
    ("complete (topological group)", "lengkap"),
    ("Cauchy sequence", "barisan Cauchy"),
    ("countable neighborhood basis", "basis lingkungan terhitung"),
    ("dense (topology)", "rapat"),
    ("p-adic integer", "bilangan bulat p-adik"),
    ("rational Tate module", "modul Tate rasional"), ("Tate module", "modul Tate"),
    ("complex torus", "torus kompleks"), ("lattice (complex torus)", "kisi"),
    ("algebraic curve", "kurva aljabar"), ("elliptic curve", "kurva eliptik"),
    ("algebraically closed field", "medan tertutup secara aljabar"),
    ("topological invariant", "invarian topologis"),
    ("homology theory", "teori homologi"), ("net (topology)", "net"),
    ("filter (topology)", "filter"),
)

EXTERNAL_REFERENCE_LABELS = (
    "sec:free-group", "eg:complete-cocomplete", "prop:limit-buildingblocks",
    "eg:categories", "def:filtrant-poset", "def:filtrant-cat",
    "prop:coset-decomp", "prop:completion-ring-characterization",
    "sec:filters", "sec:ring-limits",
)
CITATION_KEYS_IN_ORDER = ("FL14", "Xiong", "Xiong", "Xiong", "FL14", "Xiong")
INDEX_TARGETS_IN_ORDER = (
    "poset terarah ke atas (filtered poset)",
    "grup topologis (topological group)",
    "grup profinit (pro-finite group)",
    "pelengkapan (completion)", r"Z_p@$\Z_p$", "modul Tate (Tate module)",
)

# Exact post-admission identities.  These values are independently rechecked by
# every normal invocation before any canonical backend output is written.
FREEZE_STATE = "frozen"
FROZEN_IDENTITIES: dict[str, tuple[int, str] | None] = {
    TARGET: (189_935, "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569"),
    TERMINOLOGY: (82_586, "59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955"),
    TERMINOLOGY_AUDIT: (8_808, "7b0cedcff9f1747cc56371b9b64a7529f357c426fbec0de55ed1e34c52e39b55"),
    PREPROMOTION_AUDIT: (8_238, "c27216096100c336b308e28115b6ffa3c9809cc0b7a20f6d04cc52443956f104"),
    STRUCTURE_GATE: (3_703, "c80e22ed46a8920c36b07ba5543c447bb851d9c0681429ebffafaf270057da0d"),
    BUILD_SCRIPT: (10_343, "2511bb4e0a936a96fb8519ff96977aa51400730e551083d354703d2e74e431f2"),
    PREFLIGHT_SCRIPT: (13_458, "dd811141f4ac88bba35400dffcebf7e1e58a7c00e3205227799887e08d12beec"),
    EVIDENCE_SCRIPT: (13_600, "3cf940b9ddc341052ed6f36c68431f2f6b125394f9a466d0013bd4d1f8c1d485"),
    DRIVER: (5_235, "3451d8581e0fa92a993c378bec019b991b9a07b2638973a67131226fed550b8e"),
    COVER: (3_859, "3ecd9e70ce5fc904026bfe3f2f3366405f7958809598c50f958d02e2b44335c5"),
    CROSSREF: (446, "809d5798727dd72c5b71b73f1631e576c5e836ebc17dbb8fb00570e301c486bd"),
    FINAL_LOG: (77_357, "bb4b9b6d7de341239eb137173b7dc774f4774298cccf534645cb2561ca9a779d"),
    VISUAL_PREFLIGHT: (658, "6e6e498cb775254bcf4b8ca5e6e3c2f98597afd1062342f4d0eab8373c612f1c"),
    VISUAL_REVIEW: (5_015, "ceefb6b40c21b99ca4a673e32223323dcdb19373dbcdcf6822a79c8e0111a2a6"),
    STRUCTURE_PDF_QA: (31_319, "4c37064eaa05cfcb0b70718b27c2213a36e1dfa0eda6bf098fd92c06fd641e2d"),
    RENDER_HASH_INVENTORY: (41_802, "c1e54d2d0d2527542b8b0f575614d8cc27d7c7238a3ea859074d271d9945c3ba"),
    ARTIFACT: (136_702, "e69eef970ade092dae4d0e8740092ae8611010bca83ab190e3331e145e852272"),
}
FROZEN_TARGET_SPAN_ID: tuple[int, str] | None = (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62")
FROZEN_TERMINOLOGY_PAIRS: tuple[tuple[str, str], ...] = TERMINOLOGY_PLAN
FROZEN_GLOSSARY_ROW_COUNT: int | None = 513
FROZEN_PAGE_COUNT: int | None = 9
DIGITAL_REFLOWS = (1661,)
TERMINOLOGY_NORMALIZATIONS: tuple[tuple[str, int, int, str, str], ...] = ()


def refuse(message: str) -> "NoReturn":
    raise SystemExit("Unit 034 backend refused: " + message)


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
    require(len(lines) == 135, "source substantive-record extraction drift")
    return "\n".join(
        candidate_check.normalize_authority_line(line, SOURCE_START + offset)
        for offset, line in enumerate(lines)
    ) + "\n"


def normalized_target_content(text: str | None = None) -> str:
    """Remove only the declared target-only display reflow for topology parity."""
    if text is None:
        text = span_text(TARGET, TARGET_START, TARGET_END)
    return candidate_check.remove_declared_digital_reflow(text)


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
    if first == r"\section{群的极限和完备化}\label{sec:group-limit}":
        return "preintegration-authority"
    if first == r"\section{Limit dan Pelengkapan Grup}\label{sec:group-limit}":
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
    require(source_span == source_content + b"\n", "authority line 1744 is not the single blank boundary")
    require(
        normalized_span(SOURCE, 1745, 1745).decode("utf-8").rstrip("\n")
        == r"\section{范畴中的群}\label{sec:group-in-cat}",
        "authority line 1745 next-section sentinel drift",
    )
    require(
        normalized_span(TARGET, TARGET_BOUNDARY_BLANK, TARGET_BOUNDARY_BLANK) == b"\n"
        and normalized_span(TARGET, TARGET_NEXT_SENTINEL, TARGET_NEXT_SENTINEL).decode("utf-8").rstrip("\n")
        == r"\section{范畴中的群}\label{sec:group-in-cat}",
        "canonical target blank boundary or next-section sentinel drift",
    )

    checked = subprocess.run(
        [sys.executable, "-B", str(ROOT / CANDIDATE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    require(checked.returncode == 0 and "PASS: O013-LI-U034" in checked.stdout,
            "isolated candidate checker failed\n" + checked.stdout + checked.stderr)

    source_text = source_content.decode("utf-8")
    normalized_source_text = normalized_source_content()
    candidate_text = (ROOT / CANDIDATE).read_text(encoding="utf-8")
    normalized_candidate_text = normalized_target_content(candidate_text)
    # Compare topology and mathematics after removing exactly the declared
    # target-only display reflow.  Raw source/target text remains authoritative
    # for identifiers, references, citations, diagrams, and indexes.
    source_env = topology_contract.environment_occurrences(normalized_source_text)
    candidate_env = topology_contract.environment_occurrences(normalized_candidate_text)
    require([(x[0], x[1]) for x in source_env] == [(x[0], x[1]) for x in candidate_env],
            "environment ordering drift")
    require(Counter(x[0] for x in source_env) == EXPECTED_ENVIRONMENTS, "environment census drift")

    source_labels = topology_contract.label_occurrences(source_text)
    candidate_labels = topology_contract.label_occurrences(candidate_text)
    require([x[0] for x in source_labels] == [x[0] for x in candidate_labels], "label drift")
    source_refs = topology_contract.reference_occurrences(source_text)
    candidate_refs = topology_contract.reference_occurrences(candidate_text)
    require([x[:2] for x in source_refs] == [x[:2] for x in candidate_refs], "reference drift")
    internal_labels = {item[0] for item in source_labels}
    external_labels = tuple(dict.fromkeys(item[1] for item in source_refs if item[1] not in internal_labels))
    require(external_labels == EXTERNAL_REFERENCE_LABELS, "external-reference order drift")
    source_cites = topology_contract.citation_occurrences(source_text)
    candidate_cites = topology_contract.citation_occurrences(candidate_text)
    require([x[1] for x in source_cites] == [x[1] for x in candidate_cites], "citation-key drift")
    require(tuple(x[1] for x in source_cites) == CITATION_KEYS_IN_ORDER, "citation occurrence order drift")
    source_items = topology_contract.occurrence_lines(source_text, r"\\item(?![A-Za-z])")
    candidate_items = topology_contract.occurrence_lines(candidate_text, r"\\item(?![A-Za-z])")
    require(len(source_items) == len(candidate_items) == 5, "list-item drift")

    source_math = protected_math_occurrences(normalized_source_content())
    candidate_math = protected_math_occurrences(normalized_candidate_text)
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
    require(len(source_arrows) == len(candidate_arrows) == 12, "diagram-arrow drift")
    require([x[0] for x in drawing_commands(source_text)] == [x[0] for x in drawing_commands(candidate_text)],
            "TikZ drawing-command drift")

    binding_contract.SPAN_START = SOURCE_START
    source_indexes = binding_contract.index_occurrences(source_text)
    binding_contract.SPAN_START = TARGET_START
    candidate_indexes = binding_contract.index_occurrences(candidate_text)
    require([x[0] for x in source_indexes] == [x[0] for x in candidate_indexes], "index-stream drift")
    require(tuple(x[1] for x in candidate_indexes) == INDEX_TARGETS_IN_ORDER, "localized index order/value drift")

    actual = {
        "source_records_including_blank_boundary": 136,
        "candidate_records": len(candidate_text.splitlines()),
        "environment_pairs": len(source_env), "environment_markers": 2 * len(source_env),
        "labels": len(source_labels),
        "ordinary_references": sum(x[0] == "ordinary" for x in source_refs),
        "equation_references": sum(x[0] == "equation" for x in source_refs),
        "citation_occurrences": len(source_cites),
        "citation_keys": len({x[1] for x in source_cites}), "list_items": len(source_items),
        "protected_math_zones": len(source_math), "diagrams": len(source_diagrams),
        "tikzcd_diagrams": sum(x[0] == "tikzcd" for x in source_diagrams),
        "tikzpicture_diagrams": sum(x[0] == "tikzpicture" for x in source_diagrams),
        "diagram_arrows": len(source_arrows),
        "drawing_commands": len(drawing_commands(source_text)),
        "index_entries": len(source_indexes), "source_corrections": 1,
        "protected_text_localizations": 9, "index_localizations": 6,
        "terminology_rows": len(TERMINOLOGY_PLAN),
        "terminology_normalizations": 0, "citation_locator_localizations": 3,
        "digital_reflows": 1,
        "exercises": 0, "hints": 0, "answers": 0, "solutions": 0,
        "csv_projections": len(CSV_OUTPUTS),
    }
    require(actual == EXPECTED_COUNTS, f"topology expectation drift: {actual!r}")

    ns = namespace()
    stable_keys = (DATASET_KEY, UNIT_KEY, f"{UNIT_KEY}/section/01", *CORE_STABLE_KEYS)
    ids = {key: "urn:uuid:" + str(uuid.uuid5(ns, key)) for key in stable_keys}
    return {
        "status": "PASS_SCAFFOLD_ONLY", "unit": "unit-034-bab-4-limit-dan-kompletisasi-grup",
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
    require(
        len(delta) == 37
        and tuple((row["source_term"], row["target_term"]) for row in delta) == TERMINOLOGY_PLAN,
        "thirty-seven-row Unit 034 glossary delta order/value drift",
    )
    require(tuple(rows[-35:]) == delta[2:], "thirty-five appended glossary rows drift")
    by_source = {row["source_term"]: row for row in rows}
    require(all(by_source.get(row["source_term"]) == row for row in delta),
            "replacement/appended delta rows differ from the live glossary")
    target_lines = span_text(TARGET, TARGET_START, TARGET_END).splitlines()
    target_evidence_lines = [re.sub(r"\\emph\{([^{}]+)\}", r"\1", line) for line in target_lines]
    evidence_aliases = {
        "closed neighborhood": "lingkungan-lingkungan tertutup",
        "p-adic integer": r"bilangan bulat $p$-adik",
    }
    selected = []
    for source_term, target_term in TERMINOLOGY_PLAN:
        row = by_source.get(source_term)
        require(
            row is not None and row.get("target_term") == target_term
            and row.get("status") == "admitted" and row.get("scope") and row.get("note"),
            f"terminology admission drift: {source_term!r}",
        )
        fragment = evidence_aliases.get(source_term, target_term)
        pattern = re.compile(rf"(?<![\w-]){re.escape(fragment)}(?![\w-])", re.IGNORECASE)
        occurrences = [i for i, line in enumerate(target_evidence_lines) if pattern.search(line)]
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
    require(candidate_run.returncode == 0 and "PASS: O013-LI-U034" in candidate_run.stdout,
            "candidate gate failed\n" + candidate_run.stdout + candidate_run.stderr)
    structure_run = subprocess.run(
        [sys.executable, "-B", str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    require(structure_run.returncode == 0 and "UNIT 034 STRUCTURE CHECK: PASS" in structure_run.stdout,
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
        and len(artifact_qa.get("outline", [])) == 4
        and artifact_qa.get("action_counts") == {"/GoTo": 20, "/URI": 5}
        and artifact_qa.get("fonts", {}).get("all_embedded") is True
        and final_log_qa.get("identity")
        == {"bytes": FROZEN_IDENTITIES[FINAL_LOG][0], "path": FINAL_LOG, "sha256": FROZEN_IDENTITIES[FINAL_LOG][1]}
        and final_log_qa.get("page_marker") == EXPECTED_PAGE_COUNT
        and final_log_qa.get("nonfatal_underfull_hboxes") == 0
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
            and len(document.get("outline", [])) == 4
            and len(document.get("named_destinations", {})) == 39
            and document.get("action_counts") == {"/GoTo": 20, "/URI": 5}
            and document.get("fonts", {}).get("all_embedded") is True
            and document.get("fonts", {}).get("unique") == 31
            for document in documents_qa.values()
        ),
        "three-document PDF structure/navigation/font contract drift",
    )
    render = json.loads((ROOT / RENDER_HASH_INVENTORY).read_text(encoding="utf-8"))
    comparisons = render.get("decoded_pixel_comparisons", {})
    require(
        render.get("status") == "PASS_WITH_WARNINGS"
        and render.get("actionable_defects") == []
        and render.get("edge_gate") == {"all_54_zero_ink": True, "outer_band_pixels": 3}
        and render.get("manual_visual_review", {}).get("status") == "PASS"
        and len(render.get("manual_visual_review", {}).get("pages", {})) == EXPECTED_PAGE_COUNT
        and all(
            comparisons.get(renderer, {}).get(pair, {}).get("all_9_decoded_pixel_identical") is True
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
        "54-render/contact-sheet/manual-page evidence contract drift",
    )
    driver_text = (ROOT / DRIVER).read_text(encoding="utf-8")
    require(driver_text.count(r"\newcommand{\UnitThirtyFourRef}") == 1,
            "reader external-reference wrapper drift")
    require(driver_text.count(r"\input{unit-034-canonical-span.tex}") == 1,
            "reader canonical-span input boundary drift")
    require(r"\input{../../build/unit-034-candidate/chapter4-group-limits-completions-id.tex}" not in driver_text,
            "reader must not input the isolated candidate directly")
    for label in EXTERNAL_REFERENCE_LABELS:
        require(driver_text.count(rf"\UnitThirtyFourMarkExternalRef{{{label}}}") == 1,
                f"reader external-reference declaration drift: {label}")
    raw_candidate = (ROOT / CANDIDATE).read_text(encoding="utf-8")
    normalized_candidate = normalized_target_content(raw_candidate)
    require(raw_candidate != normalized_candidate,
            "declared target-only digital reflow is absent")
    require(
        [(item[1], item[3]) for item in protected_math_occurrences(normalized_candidate)]
        == [(item[1], item[3]) for item in protected_math_occurrences(normalized_source_content())],
        "declared digital-reflow normalization does not recover protected mathematics",
    )
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
    normalized_target = normalized_target_content(target_text)

    supplemental_prerequisites = (
        ("prerequisite/group-homomorphisms-kernels-and-quotients", "群同态、核与商群", "homomorfisme grup, kernel, dan grup hasil bagi", 177, 364),
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
        "prerequisite/point-set-topology", "prerequisite/cauchy-sequences-and-completeness",
        "prerequisite/categories-and-morphisms", "prerequisite/functors-and-natural-transformations",
        "prerequisite/limits-and-colimits",
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
    target_env = topology_contract.environment_occurrences(normalized_target)
    for ordinal, (source_item, target_item) in enumerate(zip(source_env, target_env, strict=True), 1):
        environment, occurrence, source_first, source_last = source_item
        target_environment, target_occurrence, target_first, target_last = target_item
        require((environment, occurrence) == (target_environment, target_occurrence), f"environment pairing drift: {ordinal}")
        slug = re.sub(r"[^a-z0-9._/-]+", "-", environment.casefold()).strip("-")
        add_concept(
            f"surface/unit-034/environment/{ordinal:03d}-{slug}-{occurrence:02d}",
            f"TeX environment {ordinal:03d}: {environment}, occurrence {occurrence}; normalized authority {SOURCE_START + source_first - 1}-{SOURCE_START + source_last - 1}",
            f"lingkungan TeX {ordinal:03d}: {environment}, kemunculan {occurrence}; target {TARGET_START + target_first - 1}-{TARGET_START + target_last - 1}",
        )
    for ordinal, (source_item, target_item) in enumerate(zip(topology_contract.label_occurrences(raw_source), topology_contract.label_occurrences(target_text), strict=True), 1):
        label, source_line = source_item; target_label, target_line = target_item
        require(label == target_label, f"label pairing drift: {ordinal}")
        add_concept(f"surface/unit-034/label/{ordinal:03d}", f"label {label}; authority line {SOURCE_START + source_line - 1}", f"label {label}; baris target {TARGET_START + target_line - 1}")
    for ordinal, (source_item, target_item) in enumerate(zip(topology_contract.reference_occurrences(raw_source), topology_contract.reference_occurrences(target_text), strict=True), 1):
        kind, label, source_line = source_item; target_kind, target_label, target_line = target_item
        require((kind, label) == (target_kind, target_label), f"reference pairing drift: {ordinal}")
        add_concept(f"surface/unit-034/reference/{kind}/{ordinal:03d}", f"{kind} reference {label}; authority line {SOURCE_START + source_line - 1}", f"rujukan {kind} {label}; baris target {TARGET_START + target_line - 1}")
    source_items = topology_contract.occurrence_lines(raw_source, r"\\item(?![A-Za-z])")
    target_items = topology_contract.occurrence_lines(target_text, r"\\item(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_items, target_items, strict=True), 1):
        add_concept(f"surface/unit-034/item/{ordinal:03d}", f"list item; authority line {SOURCE_START + source_line - 1}", f"butir daftar; baris target {TARGET_START + target_line - 1}")
    source_arrows = topology_contract.occurrence_lines(raw_source, r"\\arrow(?![A-Za-z])")
    target_arrows = topology_contract.occurrence_lines(target_text, r"\\arrow(?![A-Za-z])")
    for ordinal, (source_line, target_line) in enumerate(zip(source_arrows, target_arrows, strict=True), 1):
        add_concept(f"surface/unit-034/diagram-arrow/{ordinal:03d}", f"tikzcd arrow; authority line {SOURCE_START + source_line - 1}", f"panah tikzcd; baris target {TARGET_START + target_line - 1}")
    for ordinal, (source_item, target_item) in enumerate(zip(drawing_commands(raw_source), drawing_commands(target_text), strict=True), 1):
        command, source_line = source_item; target_command, target_line = target_item
        require(command == target_command, f"drawing-command pairing drift: {ordinal}")
        add_concept(f"surface/unit-034/drawing-command/{ordinal:03d}-{command}", f"TikZ {command}; authority line {SOURCE_START + source_line - 1}", f"perintah TikZ {command}; baris target {TARGET_START + target_line - 1}")
    source_math = protected_math_occurrences(normalized_source)
    target_math = protected_math_occurrences(normalized_target)
    for source_item, target_item in zip(source_math, target_math, strict=True):
        ordinal, kind, source_line, formula = source_item
        _, target_kind, target_line, target_formula = target_item
        require((kind, formula) == (target_kind, target_formula), f"protected-math pairing drift: {ordinal}")
        formula_hash = digest(formula.encode("utf-8"))
        add_concept(f"surface/unit-034/protected-math-zone/{ordinal:03d}-{kind}", f"protected {kind} zone; normalized authority line {SOURCE_START + source_line - 1}; SHA-256 {formula_hash}", f"zona matematika terlindungi {kind}; baris target {TARGET_START + target_line - 1}; SHA-256 {formula_hash}")
    for ordinal, (row, source_line, target_line) in enumerate(terminology_rows, 1):
        source_term, target_term = TERMINOLOGY_PLAN[ordinal - 1]
        add_concept(f"surface/unit-034/terminology-row/{ordinal:03d}", f"terminology row: {source_term}; representative authority line {source_line}", f"baris terminologi: {source_term} -> {target_term}; status admitted; scope {row['scope']}; baris target {target_line}")

    corrections = (
        ("O013-LI-U034-COR-001", 1720, 1715,
         "p-adic compatible-family index i >= 1", "compatible-family index i >= 0"),
    )
    for correction_id, source_line, target_line, issue, repair in corrections:
        add_concept(f"correction/{correction_id.casefold()}", f"declared source correction {correction_id}; authority line {source_line}; {issue}; evidence {REVIEW}", f"koreksi sumber {correction_id}; baris target {target_line}; {repair}; bukti {REVIEW}")

    localization_ordinal = 0
    for source_line, replacements in candidate_check.PROTECTED_TEXT_REPLACEMENTS.items():
        for source_fragment, target_fragment in replacements:
            localization_ordinal += 1
            local_id = f"O013-LI-U034-LOC-{localization_ordinal:03d}"
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
            local_id = f"O013-LI-U034-CITELOC-{citation_localization_ordinal:03d}"
            add_concept(f"citation-locator-localization/{local_id.casefold()}", f"citation-locator localization {local_id}; key {source_key}; authority line {SOURCE_START + source_line - 1}; {source_note}; evidence {REVIEW}", f"lokalisasi penunjuk sitasi {local_id}; kunci {target_key}; baris target {TARGET_START + target_line - 1}; {target_note}; bukti {REVIEW}")
    for norm_id, source_line, target_line, issue, repair in TERMINOLOGY_NORMALIZATIONS:
        add_concept(
            f"terminology-normalization/{norm_id.casefold()}",
            f"target terminology normalization {norm_id}; aligned authority line {source_line}; older target synonym {issue}; evidence {TERMINOLOGY_AUDIT}",
            f"normalisasi terminologi target {norm_id}; baris target {target_line}; bentuk terkendali {repair}; bukti {TERMINOLOGY_AUDIT}",
        )
    for ordinal, source_line in enumerate(DIGITAL_REFLOWS, 1):
        reflow_id = f"O013-LI-U034-REFLOW-{ordinal:03d}"
        add_concept(f"digital-reflow/{reflow_id.casefold()}", f"declared target-only digital reflow {reflow_id}; authority line {source_line}; unchanged neighborhood-basis identity; evidence {PREPROMOTION_AUDIT}", f"reflow digital khusus target {reflow_id}; baris target {source_line - 5}; display tiga baris; bukti {PREPROMOTION_AUDIT}")
    add_concept("provenance/o013-li-u034-production", f"Production provenance: {MODEL}, acting on the user's instruction; source-author and source credits remain unchanged.", f"Provenans produksi: {MODEL}, bertindak atas instruksi pengguna; kredit penulis dan sumber tetap dipertahankan.")

    require(localization_ordinal == 9 and citation_localization_ordinal == 3, "localization census drift")
    require(len(concepts) == 419 and len({item["stable_key"] for item in concepts}) == 419,
            f"concept-compatible entity census drift: {len(concepts)}")

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    require(set(prerequisites).issubset(prerequisite_by_key), "required prerequisite absent")
    data["rights"].append({
        "id": uid("rights/fandol-gpl-3.0-with-font-exception"),
        "stable_key": "rights/fandol-gpl-3.0-with-font-exception",
        "entity_type": "rights",
        "component": "Fandol 0.3 fonts used by the XeLaTeX closure and embedded as subsets where needed",
        "holder_or_source": "Fandol team (Clerk Ma and Jie Su); official CTAN package https://ctan.org/pkg/fandol",
        "license": "GNU GPL version 3 with the Fandol document-embedding font exception",
        "required_treatment": "Retain Fandol attribution, the GPLv3 text, the font exception, and access to the official source package; keep this font component separate from the book's CC BY 4.0 content license and the Noto OFL 1.1 component.",
        "applies_to_unit": True,
        "bindings": [
            live_binding(FANDOL_AUTHORITY),
            live_binding(FANDOL_LICENSE),
            live_binding(FANDOL_README),
            live_binding("repo/source/font-setup-id.tex"),
            live_binding(ARTIFACT),
            live_binding(STRUCTURE_PDF_QA),
        ],
    })
    rights_by_key = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights_by_key) == {"rights/principal-cc-by-4.0", "rights/lanzhou-cc-by-sa-3.0", "rights/ajbook-fragment-cc-by-sa-3.0", "rights/noto-fonts-ofl-1.1", "rights/fandol-gpl-3.0-with-font-exception"}, "rights inventory drift")
    rights_by_key["rights/principal-cc-by-4.0"]["bindings"] = [live_binding(path) for path in (SOURCE, CANDIDATE, TARGET, BIBLIOGRAPHY, "repo/source/LICENSE", "repo/source/ccby.png")]
    rights_by_key["rights/principal-cc-by-4.0"]["applies_to_unit"] = True
    rights_by_key["rights/lanzhou-cc-by-sa-3.0"]["applies_to_unit"] = False
    rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["applies_to_unit"] = True
    rights_by_key["rights/noto-fonts-ofl-1.1"]["applies_to_unit"] = True
    rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["applies_to_unit"] = True
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    unit_rights = [principal, rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"], rights_by_key["rights/noto-fonts-ofl-1.1"]["id"], rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"]]

    section_key = f"{unit_key}/section/01"
    section_id = uid(section_key)
    prerequisite_ids = [prerequisite_by_key[key] for key in prerequisites]
    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section",
        "parent_id": unit_id, "order": 1,
        "source_local_id": "chapter4.tex:1609-1744 (line 1744 blank boundary omitted from target mapping)",
        "titles": [{"language": "zh-Hans", "text": "群的极限和完备化"}, {"language": "id-ID", "text": "Limit dan Pelengkapan Grup"}],
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
        key = f"citation/unit-034/{ordinal:02d}-{bib_key.casefold()}"
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
        key = f"index-entry/unit-034/{stream}/{ordinal:03d}"
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
        key = f"diagram/unit-034/{source_format}-{occurrence:02d}"
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
        "id": uid("build-surface/unit-034-pdf"), "stable_key": "build-surface/unit-034-pdf",
        "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_034.ps1 -OutputDirectory build/unit-034-replay",
        "artifact_path": ARTIFACT, "artifact_binding": live_binding(ARTIFACT), "log_binding": live_binding(FINAL_LOG),
        "build_script": live_binding(BUILD_SCRIPT), "page_count": page_count, "status": "pass",
        "driver": live_binding(DRIVER), "input_bindings": [live_binding(path) for path in inputs],
        "external_dependencies": ["XeLaTeX", "PowerShell 7", "Biber", "makeindex", "Poppler pdfinfo", "Noto CJK fonts", "Fandol 0.3 fonts", "packages loaded by the Unit 034 driver and AJbook.cls"],
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
        qa_event("qa/unit-034/admission-gate", "admission_gate", "Complete Section 4.10 admission: authority lines 1609-1744 with blank boundary excluded from the 135-record target mapping at 1604-1738; 25 environment pairs, 11 labels, 16 references, 6 citation occurrences / 2 bibliography keys, 6 localized indexes, 1 tikzcd diagram / 12 arrows, 276 protected mathematical zones, 37 admitted terminology rows, 1 declared source correction, 9 protected-text localizations, 3 citation-locator localizations, 1 declared target-only digital reflow, and no exercises, hints, answers, or solutions. CC BY 4.0 content, the AJbook fragment, Noto OFL 1.1 fonts, and Fandol GPLv3-with-font-exception rights remain separate; no endorsement is implied. Production provenance is " + MODEL + ", acting on the user's instruction.", VISUAL_REVIEW),
        qa_event("qa/unit-034/source-review", "backend_integrity", "Exact authority, translation, mathematical, identifier, correction, localization, terminology, and provenance review.", REVIEW),
        qa_event("qa/unit-034/candidate-artifact", "backend_integrity", "Exact isolated Indonesian candidate binding.", CANDIDATE),
        qa_event("qa/unit-034/candidate-check", "backend_integrity", "Fail-closed candidate topology and semantic check.", CANDIDATE_GATE),
        qa_event("qa/unit-034/canonical-integration", "backend_integrity", "Fail-closed target splice, glossary, and source-order check.", STRUCTURE_GATE),
        qa_event("qa/unit-034/source-correction", "backend_integrity", "One declared high-confidence p-adic compatible-family source correction at authority line 1720 / target line 1715.", REVIEW),
        qa_event("qa/unit-034/digital-reflow", "backend_integrity", "One declared target-only three-line neighborhood-basis display reflow with protected mathematical identity preserved.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-034/protected-text-localizations", "backend_integrity", "Nine protected mathematical-text localizations.", REVIEW),
        qa_event("qa/unit-034/citation-locator-localizations", "backend_integrity", "Three localized citation locators preserve bibliography keys and occurrence order.", REVIEW),
        qa_event("qa/unit-034/index-localizations", "backend_integrity", "Six index entries preserve stream/order and localize their target keys.", REVIEW),
        qa_event("qa/unit-034/terminology-control", "backend_integrity", "Live 513-row unique id-ID glossary.", TERMINOLOGY),
        qa_event("qa/unit-034/terminology-delta", "backend_integrity", "Exact 37-row admitted terminology delta: two replacements and 35 appended rows.", TERMINOLOGY_DELTA),
        qa_event("qa/unit-034/terminology-evidence", "backend_integrity", "Bound terminology audit and production-model provenance.", TERMINOLOGY_AUDIT),
        qa_event("qa/unit-034/prepromotion-evidence", "backend_integrity", "Exact splice, corrections, localizations, reflow, and source-order evidence.", PREPROMOTION_AUDIT),
        qa_event("qa/unit-034/build-log", "backend_integrity", "Final 9-page XeLaTeX/Biber/index build log without fatal, unresolved, citation, missing-character, empty-target, or overfull diagnostics.", FINAL_LOG),
        qa_event("qa/unit-034/driver-external-reference-isolation", "backend_integrity", "Reader-driver external-reference wrapper keeps ten cross-unit references non-clickable while retaining internal navigation and the exact hash-gated canonical target span.", DRIVER),
        qa_event("qa/unit-034/preflight-tool", "backend_integrity", "Frozen all-page dual-renderer/PDF preflight implementation.", PREFLIGHT_SCRIPT),
        qa_event("qa/unit-034/evidence-tool", "backend_integrity", "Frozen structure/PDF and render-evidence generator implementation.", EVIDENCE_SCRIPT),
        qa_event("qa/unit-034/visual-preflight", "backend_integrity", "All-page dual-renderer preflight and deterministic decoded-pixel comparison.", VISUAL_PREFLIGHT),
        qa_event("qa/unit-034/structure-and-pdf-qa", "backend_integrity", "Machine-readable PDF structure, metadata, safety, build-log, and exact artifact checks.", STRUCTURE_PDF_QA),
        qa_event("qa/unit-034/render-hash-inventory", "backend_integrity", "All 54 renders pass the edge gate and defined same-renderer deterministic comparisons.", RENDER_HASH_INVENTORY),
        qa_event("qa/unit-034/all-page-visual-review", "backend_integrity", "Independent full-resolution review of all 9 pages in Poppler and MuPDF with no actionable defect.", VISUAL_REVIEW),
    ]

    data["dataset_stable_key"] = DATASET_KEY
    data["dataset_id"] = uid(DATASET_KEY)
    data["workflow"] = {"responsible_task": str(uuid.uuid5(ns, TASK_KEY)), "updated": "2026-08-27", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_math_backend_build_visual_pass"}
    data["unit"] = {
        "id": unit_id, "stable_key": unit_key, "entity_type": "unit",
        "program_id": data["program"]["id"], "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"], "order": UNIT_NUMBER,
        "source_local_id": "chapter4.tex:1609-1744; substantive authority map 1609-1743 to target 1604-1738",
        "titles": [{"language": "zh-Hans", "text": "第四章：群的极限和完备化"}, {"language": "id-ID", "text": "Bab 4: Limit dan Pelengkapan Grup"}],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": live_binding(SOURCE, SOURCE_START, SOURCE_END),
        "target_binding": live_binding(TARGET, TARGET_START, TARGET_END),
        "section_ids": [section_id], "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations], "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries], "build_surface_ids": [build["id"]],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": ["outcome/construct-projective-limits-of-groups", "outcome/analyze-topological-and-profinite-groups", "outcome/construct-group-completions", "outcome/interpret-p-adic-and-tate-module-examples"],
        "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 2, "diagrams": 1, "index_entries": 6},
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
        "sections": 1, "concepts": len(concepts), "textual_environment_pairs": 25,
        "labels": 11, "references": 16, "citation_occurrences": 6, "citations": len(citations), "items": 5,
        "protected_math_zones": 276, "diagrams": len(diagrams), "diagram_arrows": 12,
        "drawing_commands": 0,
        "index_entries": len(index_entries), "index_localizations": 6, "terminology_rows": 37,
        "source_corrections": 1, "protected_text_localizations": 9,
        "terminology_normalizations": 0, "citation_locator_localizations": 3, "digital_reflows": 1,
        "reader_external_reference_isolations": 10,
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
