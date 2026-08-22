#!/usr/bin/env python3
"""Generate the canonical Unit 009 backend from reviewed, admitted inputs.

This generator is deliberately admission-gated.  It refuses to write JSON until
the final reader, final XeLaTeX log, portable build summary, and admission
receipt agree on the artifact identity.  It also pins the exact authority and
Indonesian source spans and checks the labels, references, citations,
environments, mathematics, diagrams, index entries, list topology, frozen
cross-references, and standalone driver controls reviewed for Chapter 2,
Section 2.1.

Backend schema v1.1.0 has first-class citation, diagram, and index-entry
records, so those surfaces are represented natively.  TeX labels and frozen
external references still use deterministic concept-compatible records whose
stable keys explicitly mark them as compatibility surfaces.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import uuid
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-008-bab-2-pengantar-teori-kategori.json"
OUTPUT = ROOT / "backend" / "data" / "unit-009-bab-2-kategori-dan-morfisme.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-009-bab-2-kategori-dan-morfisme.tex"
COVER = "repo/source/coverpage-id-unit-009.tex"
CROSSREF_AUX = "repo/source/unit-009-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_009.ps1"
BUILD_SUMMARY = "qa/unit-009-evidence/build-log-summary.txt"
ADMISSION_WITNESS = "qa/UNIT_009_ADMISSION_20260822.md"
ARTIFACT = "artifacts/unit-009-bab-2-kategori-dan-morfisme.pdf"
FINAL_LOG = "qa/UNIT_009_BUILD_FINAL.log"

SPAN_START = 39
SPAN_END = 198
EXPECTED_SOURCE_FULL_BYTES = 139_983
EXPECTED_SOURCE_FULL_SHA256 = "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840"
EXPECTED_TARGET_FULL_BYTES = 145_511
EXPECTED_TARGET_FULL_SHA256 = "09231954639e6c12b1dd3107e9e4ff5af6113de1970010a49f23dc2ec8fb5f7b"
EXPECTED_SOURCE_SPAN_SHA256 = "1fa6ecc8f3ec477611f05ddd07297f9e115b7bb118e5fd5be4b7981cde7747ae"
EXPECTED_TARGET_SPAN_SHA256 = "b20dfbefb909ffe91c4857df6c183dffbdd7fd2c316156f5d7d9274efa3b41e2"

REQUIRED_FINAL_INPUTS = (
    ARTIFACT,
    FINAL_LOG,
    BUILD_SUMMARY,
    ADMISSION_WITNESS,
)

EXPECTED_LABELS = (
    "sec:cat-and-morphism",
    "def:category",
    "def:subcategory",
    "def:U-cat",
    "con:U-small",
    "eg:categories",
    "eg:fundamental-groupoid",
)
EXPECTED_REFERENCES = (
    "def:monoid",
    "def:group",
    "sec:Grot-universe",
    "hyp:universe",
    "def:partial-order",
    "sec:order",
    "eg:Ab-cat",
    "sec:enriched-cat",
    "con:U-small",
    "sec:Grot-universe",
)
EXPECTED_EXTERNAL_CROSSREFS = (
    ("def:monoid", "4.1.{1}", "101"),
    ("def:group", "4.1.{2}", "101"),
    ("sec:Grot-universe", "1.5", "24"),
    ("hyp:universe", "1.5.{2}", "24"),
    ("def:partial-order", "1.2.{1}", "15"),
    ("sec:order", "1.2", "15"),
    ("eg:Ab-cat", "3.4.{7}", "89"),
    ("sec:enriched-cat", "3.4", "87"),
)
EXPECTED_CITATIONS = (
    ("Xiong", 120),
    ("May99", 122),
    ("You", 153),
    ("Xiong", 153),
    ("May99", 184),
)
RECORDED_CITATIONS = (
    ("Xiong", 120),
    ("May99", 122),
    ("You", 153),
)
EXPECTED_ENVIRONMENTS = (
    "definition",
    "enumerate",
    "tikzcd",
    "align*",
    "compactenum",
    "itemize",
    "tikzcd",
    "tikzcd",
    "definition",
    "compactenum",
    "tikzcd",
    "definition",
    "convention",
    "example",
    "enumerate",
    "remark",
    "definition",
    "itemize",
    "definition",
    "example",
    "cases",
    "center",
    "tikzpicture",
    "definition",
    "compactitem",
)
EXPECTED_DIAGRAMS = (
    ("tikzcd", 1, 46, 46),
    ("tikzcd", 2, 67, 70),
    ("tikzcd", 3, 70, 73),
    ("tikzcd", 4, 86, 86),
    ("tikzpicture", 1, 160, 178),
)
DIAGRAM_SLUGS = (
    "category-source-target",
    "commutative-triangle",
    "commutative-square",
    "subcategory-source-target",
    "fundamental-groupoid-homotopy",
)
EXPECTED_INDEX_TOPOLOGY = (
    ("main", 42),
    ("sym1", 42),
    ("sym1", 42),
    ("main", 45),
    ("main", 46),
    ("sym1", 46),
    ("main", 47),
    ("sym1", 47),
    ("main", 65),
    ("main", 66),
    ("main", 76),
    ("sym1", 78),
    ("sym1", 78),
    ("main", 81),
    ("main", 81),
    ("main", 95),
    ("sym1", 113),
    ("sym1", 114),
    ("main", 115),
    ("sym1", 116),
    ("sym1", 119),
    ("sym1", 120),
    ("sym1", 123),
    ("main", 130),
    ("main", 134),
    ("main", 134),
    ("main", 134),
    ("main", 146),
    ("main", 152),
    ("main", 188),
    ("sym1", 188),
)
INDEX_SLUGS = (
    "category",
    "mor-symbol",
    "object-symbol",
    "category-object",
    "morphism",
    "hom-set-symbol",
    "identity-morphism",
    "identity-symbol",
    "empty-category",
    "commutative-diagram",
    "isomorphism",
    "endomorphism-symbol",
    "automorphism-symbol",
    "subcategory",
    "full-subcategory",
    "u-category",
    "finite-ordinal-category-symbols",
    "set-category-symbol",
    "basepoint",
    "group-category-symbol",
    "abelian-group-category-symbol",
    "topological-space-category-symbol",
    "vector-space-category-symbol",
    "nbg-set-theory",
    "monomorphism",
    "epimorphism",
    "inverse-morphism",
    "groupoid",
    "fundamental-groupoid",
    "opposite-category",
    "opposite-category-symbol",
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalized_span(relative: str, line_start: int, line_end: int) -> bytes:
    lines = (ROOT / relative).read_bytes().decode("utf-8").splitlines()
    if len(lines) < line_end:
        raise SystemExit(
            f"Unit 009 backend generation refused: {relative} has only {len(lines)} lines; "
            f"cannot bind {line_start}-{line_end}"
        )
    return ("\n".join(lines[line_start - 1 : line_end]) + "\n").encode("utf-8")


def binding(relative: str, line_start: int | None = None, line_end: int | None = None) -> dict[str, object]:
    payload = (ROOT / relative).read_bytes()
    result: dict[str, object] = {
        "path": relative,
        "bytes": len(payload),
        "sha256": sha256(payload),
    }
    if line_start is not None and line_end is not None:
        span = normalized_span(relative, line_start, line_end)
        result.update(
            {
                "line_start": line_start,
                "line_end": line_end,
                "span_sha256": sha256(span),
                "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
            }
        )
    return result


def require_final_inputs() -> None:
    missing = [relative for relative in REQUIRED_FINAL_INPUTS if not (ROOT / relative).is_file()]
    if missing:
        formatted = "\n  - ".join(missing)
        raise SystemExit(
            "Unit 009 backend generation is gated on final build/admission evidence. "
            "Create and verify these files first:\n  - " + formatted
        )


def require_text(relative: str, needle: str, purpose: str, *, ignore_case: bool = False) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    haystack = text.casefold() if ignore_case else text
    expected = needle.casefold() if ignore_case else needle
    if expected not in haystack:
        raise SystemExit(
            f"Unit 009 backend generation refused: {purpose} is absent from {relative}: {needle!r}"
        )


def summary_value(label: str) -> str:
    text = (ROOT / BUILD_SUMMARY).read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if match is None:
        raise SystemExit(
            f"Unit 009 backend generation refused: {BUILD_SUMMARY} has no {label!r} evidence line"
        )
    return match.group(1)


def decimal_value(value: str, label: str) -> int:
    normalized = value.replace(",", "").strip()
    if not normalized.isdecimal():
        raise SystemExit(f"Unit 009 backend generation refused: invalid {label}: {value!r}")
    return int(normalized)


def pdfinfo_page_count() -> int:
    try:
        completed = subprocess.run(
            ["pdfinfo", str(ROOT / ARTIFACT)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise SystemExit(
            "Unit 009 backend generation refused: pdfinfo is required to cross-check the live artifact"
        ) from exc
    if completed.returncode != 0:
        raise SystemExit(
            "Unit 009 backend generation refused: pdfinfo could not inspect the live artifact: "
            + completed.stderr.strip()
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 009 backend generation refused: pdfinfo returned no page count")
    return int(match.group(1))


def require_build_evidence() -> int:
    artifact_payload = (ROOT / ARTIFACT).read_bytes()
    log_payload = (ROOT / FINAL_LOG).read_bytes()
    if len(artifact_payload) < 5 or not artifact_payload.startswith(b"%PDF-"):
        raise SystemExit(f"Unit 009 backend generation refused: {ARTIFACT} is not a nonempty PDF")

    actual_artifact_bytes = len(artifact_payload)
    actual_artifact_sha = sha256(artifact_payload)
    actual_log_bytes = len(log_payload)
    actual_log_sha = sha256(log_payload)
    summary_pages = decimal_value(summary_value("PDF pages"), "PDF page count")
    summary_artifact_bytes = decimal_value(summary_value("PDF bytes"), "PDF byte count")
    summary_artifact_sha = summary_value("PDF SHA-256").lower()
    summary_log_bytes = decimal_value(summary_value("Build-log bytes"), "build-log byte count")
    summary_log_sha = summary_value("Build-log SHA-256").lower()

    expected_hash_pattern = re.compile(r"^[0-9a-f]{64}$")
    for label, value in (
        ("PDF SHA-256", summary_artifact_sha),
        ("Build-log SHA-256", summary_log_sha),
    ):
        if expected_hash_pattern.fullmatch(value) is None:
            raise SystemExit(f"Unit 009 backend generation refused: invalid {label}: {value!r}")

    if (actual_artifact_bytes, actual_artifact_sha) != (summary_artifact_bytes, summary_artifact_sha):
        raise SystemExit(
            "Unit 009 backend generation refused: live PDF bytes/hash do not match the build summary"
        )
    if (actual_log_bytes, actual_log_sha) != (summary_log_bytes, summary_log_sha):
        raise SystemExit(
            "Unit 009 backend generation refused: live final-log bytes/hash do not match the build summary"
        )

    live_pdf_pages = pdfinfo_page_count()
    log_text = log_payload.decode("utf-8", errors="replace")
    log_page_matches = re.findall(r"Output written on .*?\((\d+) pages?\)\.", log_text, flags=re.DOTALL)
    if not log_page_matches:
        raise SystemExit("Unit 009 backend generation refused: final log has no output page-count witness")
    live_log_pages = int(log_page_matches[-1])

    receipt = (ROOT / ADMISSION_WITNESS).read_text(encoding="utf-8")
    artifact_receipt = re.search(
        rf"- Reader: `{re.escape(ARTIFACT)}`,\s*(\d+) pages,\s*([\d,]+) bytes,\s*"
        r"SHA-256 `([0-9a-f]{64})`",
        receipt,
        flags=re.DOTALL,
    )
    log_receipt = re.search(
        rf"- Final log: `{re.escape(FINAL_LOG)}`,\s*([\d,]+) bytes,\s*SHA-256 `([0-9a-f]{{64}})`",
        receipt,
        flags=re.DOTALL,
    )
    if artifact_receipt is None or log_receipt is None:
        raise SystemExit(
            "Unit 009 backend generation refused: admission receipt lacks parseable live PDF/log evidence"
        )

    receipt_pages = int(artifact_receipt.group(1))
    receipt_artifact_bytes = decimal_value(artifact_receipt.group(2), "receipt PDF byte count")
    receipt_artifact_sha = artifact_receipt.group(3)
    receipt_log_bytes = decimal_value(log_receipt.group(1), "receipt final-log byte count")
    receipt_log_sha = log_receipt.group(2)
    page_counts = {summary_pages, live_pdf_pages, live_log_pages, receipt_pages}
    if len(page_counts) != 1 or summary_pages < 1:
        raise SystemExit(
            "Unit 009 backend generation refused: PDF page count disagrees across live PDF, log, summary, and receipt"
        )
    if (receipt_artifact_bytes, receipt_artifact_sha) != (actual_artifact_bytes, actual_artifact_sha):
        raise SystemExit("Unit 009 backend generation refused: admission receipt PDF identity is stale")
    if (receipt_log_bytes, receipt_log_sha) != (actual_log_bytes, actual_log_sha):
        raise SystemExit("Unit 009 backend generation refused: admission receipt final-log identity is stale")
    return summary_pages


def span_text(relative: str) -> str:
    return normalized_span(relative, SPAN_START, SPAN_END).decode("utf-8")


def citation_occurrences(text: str) -> tuple[tuple[str, int], ...]:
    result: list[tuple[str, int]] = []
    pattern = re.compile(r"\\cite(?:\[[^\]]*\])*\{([^}]+)\}")
    for match in pattern.finditer(text):
        line = SPAN_START + text.count("\n", 0, match.start())
        result.extend((key.strip(), line) for key in match.group(1).split(",") if key.strip())
    return tuple(result)


def index_occurrences(text: str) -> tuple[tuple[str, str, int], ...]:
    """Return index name, balanced key, and absolute source line in order."""

    pattern = re.compile(r"\\index(?:\[([^\]]+)\])?\{")
    result: list[tuple[str, str, int]] = []
    position = 0
    while True:
        match = pattern.search(text, position)
        if match is None:
            break
        depth = 1
        cursor = match.end()
        while cursor < len(text) and depth:
            escaped = cursor > 0 and text[cursor - 1] == "\\"
            if text[cursor] == "{" and not escaped:
                depth += 1
            elif text[cursor] == "}" and not escaped:
                depth -= 1
            cursor += 1
        if depth:
            raise SystemExit("Unit 009 backend generation refused: unbalanced index entry")
        line = SPAN_START + text.count("\n", 0, match.start())
        result.append((match.group(1) or "main", text[match.end() : cursor - 1], line))
        position = cursor
    return tuple(result)


def diagram_occurrences(text: str) -> tuple[tuple[str, int, int, int], ...]:
    pattern = re.compile(r"\\begin\{(tikzcd|tikzpicture)\}")
    counts: Counter[str] = Counter()
    result: list[tuple[str, int, int, int]] = []
    position = 0
    while True:
        match = pattern.search(text, position)
        if match is None:
            break
        environment = match.group(1)
        end_marker = f"\\end{{{environment}}}"
        end = text.find(end_marker, match.end())
        if end < 0:
            raise SystemExit(
                f"Unit 009 backend generation refused: unterminated {environment} diagram"
            )
        counts[environment] += 1
        start_line = SPAN_START + text.count("\n", 0, match.start())
        end_line = SPAN_START + text.count("\n", 0, end + len(end_marker) - 1)
        result.append((environment, counts[environment], start_line, end_line))
        position = end + len(end_marker)
    return tuple(result)


def canonical_math(value: str) -> str:
    # Only this reviewed diagram caption is language-bearing mathematics prose.
    # Other \text payloads remain protected byte-for-byte after whitespace removal.
    localized = value.replace(
        r"\text{(略去恒等态射)}",
        r"\text{<localized-finite-ordinal-caption>}",
    ).replace(
        r"\text{(morfisme identitas dan panah komposit tidak digambar)}",
        r"\text{<localized-finite-ordinal-caption>}",
    )
    return re.sub(r"\s+", "", localized)


def math_multiset(text: str) -> Counter[str]:
    displays = re.findall(r"\\\[(.*?)\\\]", text, flags=re.DOTALL)
    outside_displays = re.sub(r"\\\[.*?\\\]", "", text, flags=re.DOTALL)
    inlines: list[str] = []
    for line in outside_displays.splitlines():
        inlines.extend(re.findall(r"(?<!\\)\$(?!\$)(.*?)(?<!\\)\$", line))
    return Counter(
        ["display:" + canonical_math(value) for value in displays]
        + ["inline:" + canonical_math(value) for value in inlines]
    )


def require_frozen_crossrefs() -> None:
    text = (ROOT / CROSSREF_AUX).read_text(encoding="utf-8")
    found_lines = tuple(
        line.strip()
        for line in text.splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    expected_lines = tuple(
        r"\newlabel{" + label + "}{{" + printed_number + "}{" + page + "}}"
        for label, printed_number, page in EXPECTED_EXTERNAL_CROSSREFS
    )
    if found_lines != expected_lines:
        raise SystemExit(
            "Unit 009 backend generation refused: frozen AUX labels/numbers/pages differ: "
            f"{found_lines!r} != {expected_lines!r}"
        )


def require_driver_controls() -> None:
    required_driver_text = (
        "coverpage-id-unit-009.tex",
        "\\externaldocument{unit-009-crossrefs}[]",
        "\\setcounter{chapter}{2}",
        "\\setcounter{section}{0}",
        "\\InputSourceLineRange{chapter2.tex}{39}{198}",
        "pdflang = {id-ID}",
    )
    for needle in required_driver_text:
        require_text(DRIVER, needle, "a frozen standalone-driver control")
    require_text(COVER, "Unit 9: Kategori dan Morfisme", "the Unit 009 cover identity")
    require_text(BUILD_SCRIPT, "unit-009-bab-2-kategori-dan-morfisme", "the Unit 009 build job")
    require_text(BUILD_SCRIPT, "-no-shell-escape", "the shell-escape prohibition")


def require_protected_surfaces() -> None:
    source_payload = (ROOT / SOURCE).read_bytes()
    target_payload = (ROOT / TARGET).read_bytes()
    if (len(source_payload), sha256(source_payload)) != (
        EXPECTED_SOURCE_FULL_BYTES,
        EXPECTED_SOURCE_FULL_SHA256,
    ):
        raise SystemExit(
            "Unit 009 backend generation refused: complete frozen authority chapter identity drift"
        )
    if (len(target_payload), sha256(target_payload)) != (
        EXPECTED_TARGET_FULL_BYTES,
        EXPECTED_TARGET_FULL_SHA256,
    ):
        raise SystemExit(
            "Unit 009 backend generation refused: complete reviewed target chapter identity drift"
        )

    source = span_text(SOURCE)
    target = span_text(TARGET)
    actual_source_hash = sha256(source.encode("utf-8"))
    actual_target_hash = sha256(target.encode("utf-8"))
    if actual_source_hash != EXPECTED_SOURCE_SPAN_SHA256:
        raise SystemExit(
            "Unit 009 backend generation refused: frozen source span drift: "
            f"{actual_source_hash} != {EXPECTED_SOURCE_SPAN_SHA256}"
        )
    if actual_target_hash != EXPECTED_TARGET_SPAN_SHA256:
        raise SystemExit(
            "Unit 009 backend generation refused: reviewed target span drift: "
            f"{actual_target_hash} != {EXPECTED_TARGET_SPAN_SHA256}"
        )

    for label, text in (("source", source), ("target", target)):
        labels = tuple(re.findall(r"\\label\{([^}]+)\}", text))
        references = tuple(re.findall(r"\\ref\{([^}]+)\}", text))
        citations = citation_occurrences(text)
        environments = tuple(re.findall(r"\\begin\{([^}]+)\}", text))
        diagrams = diagram_occurrences(text)
        indexes = index_occurrences(text)
        index_topology = tuple((index_name, line) for index_name, _key, line in indexes)

        if labels != EXPECTED_LABELS:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} labels are {labels}, expected {EXPECTED_LABELS}"
            )
        if references != EXPECTED_REFERENCES:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} references are {references}, "
                f"expected {EXPECTED_REFERENCES}"
            )
        if citations != EXPECTED_CITATIONS:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} citations are {citations}, "
                f"expected {EXPECTED_CITATIONS}"
            )
        if environments != EXPECTED_ENVIRONMENTS:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} environments are {environments}, "
                f"expected {EXPECTED_ENVIRONMENTS}"
            )
        if diagrams != EXPECTED_DIAGRAMS:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} diagrams are {diagrams}, "
                f"expected {EXPECTED_DIAGRAMS}"
            )
        if index_topology != EXPECTED_INDEX_TOPOLOGY:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} index topology is {index_topology}, "
                f"expected {EXPECTED_INDEX_TOPOLOGY}"
            )
        item_count = len(re.findall(r"(?m)^\s*\\item\b", text))
        if item_count != 28:
            raise SystemExit(
                f"Unit 009 backend generation refused: {label} has {item_count} list items, expected 28"
            )
        for marker in (r"\begin{Exercises}", r"\begin{hint}", r"\begin{answer}", r"\begin{solution}"):
            if marker in text:
                raise SystemExit(
                    f"Unit 009 backend generation refused: unexpected learner surface {marker!r} in {label}"
                )

    source_math = math_multiset(source)
    target_math = math_multiset(target)
    if source_math != target_math:
        raise SystemExit(
            "Unit 009 backend generation refused: protected mathematical structures differ after "
            "whitespace and localized-text normalization"
        )
    if sum(source_math.values()) != 267:
        raise SystemExit(
            "Unit 009 backend generation refused: expected 267 protected inline/display mathematics surfaces"
        )
    if len(re.findall(r"\\\[", source)) != 8 or len(re.findall(r"\\\[", target)) != 8:
        raise SystemExit("Unit 009 backend generation refused: expected eight bracket displays")
    if len(INDEX_SLUGS) != len(EXPECTED_INDEX_TOPOLOGY):
        raise SystemExit("Unit 009 backend generator defect: index slug/topology lengths disagree")

    source_lines = (ROOT / SOURCE).read_text(encoding="utf-8").splitlines()
    target_lines = (ROOT / TARGET).read_text(encoding="utf-8").splitlines()
    if not source_lines[SPAN_END].startswith(r"\section{"):
        raise SystemExit("Unit 009 backend generation refused: source line 199 is no longer the next section")
    if not target_lines[SPAN_END].startswith(r"\section{"):
        raise SystemExit("Unit 009 backend generation refused: target line 199 is no longer the next section")
    expected_target_reflow = (
        r"{\small \[ 0 \to 1 \to \cdots \to (n-1) \qquad "
        r"\text{(morfisme identitas dan panah komposit tidak digambar)}. \] }"
    )
    if target_lines[111].strip() != expected_target_reflow:
        raise SystemExit(
            "Unit 009 backend generation refused: the reviewed target-only line-112 display reflow drifted"
        )
    if r"\small" in source_lines[111]:
        raise SystemExit(
            "Unit 009 backend generation refused: target-only line-112 display reflow appeared in authority source"
        )

    require_frozen_crossrefs()
    require_driver_controls()


def require_admission_evidence() -> int:
    require_final_inputs()
    page_count = require_build_evidence()
    require_protected_surfaces()
    require_text(BUILD_SUMMARY, "Unit 009 admitted build summary", "the admitted build identity")
    require_text(
        BUILD_SUMMARY,
        "Frozen source range: chapter2.tex lines 39-198",
        "the frozen source boundary",
    )
    require_text(BUILD_SUMMARY, "TeX errors: 0", "the zero-error build result")
    require_text(BUILD_SUMMARY, "Undefined references/citations: 0", "the resolved-reference result")
    require_text(BUILD_SUMMARY, "Visual review:", "the all-page visual-review result")
    require_text(ADMISSION_WITNESS, "Decision: admitted", "the admission decision", ignore_case=True)
    require_text(ADMISSION_WITNESS, "chapter2.tex", "the admitted source filename")
    require_text(ADMISSION_WITNESS, "39-198", "the admitted source line range")
    require_text(ADMISSION_WITNESS, "31", "the index-entry census")
    require_text(ADMISSION_WITNESS, "five", "the diagram census", ignore_case=True)
    for protected_key in (*EXPECTED_LABELS, *EXPECTED_REFERENCES):
        require_text(ADMISSION_WITNESS, protected_key, f"the protected surface {protected_key}")
    for citation_key in {key for key, _line in EXPECTED_CITATIONS}:
        require_text(ADMISSION_WITNESS, citation_key, f"the protected citation {citation_key}")
    return page_count


def main() -> None:
    page_count = require_admission_evidence()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-2-kategori-dan-morfisme"
    unit_id = identifier(unit_key)
    section_key = f"{unit_key}/section/kategori-dan-morfisme"
    section_id = identifier(section_key)

    concept_specs = [
        ("concept/category", "范畴", "kategori"),
        ("concept/category-object", "对象", "objek kategori"),
        ("concept/morphism", "态射", "morfisme"),
        ("concept/morphism-source", "态射的来源", "sumber morfisme"),
        ("concept/morphism-target", "态射的目标", "target morfisme"),
        ("concept/identity-morphism", "恒等态射", "morfisme identitas"),
        ("concept/morphism-composition", "态射合成", "komposisi morfisme"),
        ("concept/commutative-diagram", "交换图表", "diagram komutatif"),
        ("concept/isomorphism", "同构", "isomorfisme"),
        ("concept/endomorphism", "自同态", "endomorfisme"),
        ("concept/automorphism", "自同构", "automorfisme"),
        ("concept/subcategory", "子范畴", "subkategori"),
        ("concept/full-subcategory", "全子范畴", "subkategori penuh"),
        ("concept/u-category", "U-范畴", "kategori-U"),
        ("concept/u-small-category", "U-小范畴", "kategori kecil-U"),
        ("concept/preorder-as-category", "预序集范畴", "praterurut sebagai kategori"),
        ("concept/discrete-category", "离散范畴", "kategori diskret"),
        ("concept/pointed-set", "带基点集合", "himpunan bertitik dasar"),
        ("concept/monomorphism", "单态射", "monomorfisme"),
        ("concept/epimorphism", "满态射", "epimorfisme"),
        ("concept/left-inverse", "左逆", "invers kiri"),
        ("concept/right-inverse", "右逆", "invers kanan"),
        ("concept/groupoid", "广群", "grupoid"),
        ("concept/fundamental-groupoid", "基本广群", "grupoid fundamental"),
        ("concept/path-homotopy", "道路同伦", "homotopi lintasan"),
        ("concept/fundamental-group", "基本群", "grup fundamental"),
        ("concept/opposite-category", "反范畴", "kategori lawan"),
        ("concept/duality-principle", "对偶原理", "prinsip dualitas"),
        ("concept/category-size", "范畴的大小", "ukuran kategori"),
        ("concept/grothendieck-universe", "Grothendieck 宇宙", "semesta Grothendieck"),
        ("surface/unit-009/label/sec-cat-and-morphism", "标签 sec:cat-and-morphism", "label sec:cat-and-morphism"),
        ("surface/unit-009/label/def-category", "标签 def:category", "label def:category"),
        ("surface/unit-009/label/def-subcategory", "标签 def:subcategory", "label def:subcategory"),
        ("surface/unit-009/label/def-u-cat", "标签 def:U-cat", "label def:U-cat"),
        ("surface/unit-009/label/con-u-small", "标签 con:U-small", "label con:U-small"),
        ("surface/unit-009/label/eg-categories", "标签 eg:categories", "label eg:categories"),
        ("surface/unit-009/label/eg-fundamental-groupoid", "标签 eg:fundamental-groupoid", "label eg:fundamental-groupoid"),
        ("surface/unit-009/reference/def-monoid", "外部引用 def:monoid", "rujukan eksternal def:monoid"),
        ("surface/unit-009/reference/def-group", "外部引用 def:group", "rujukan eksternal def:group"),
        ("surface/unit-009/reference/sec-grot-universe", "外部引用 sec:Grot-universe", "rujukan eksternal sec:Grot-universe"),
        ("surface/unit-009/reference/hyp-universe", "外部引用 hyp:universe", "rujukan eksternal hyp:universe"),
        ("surface/unit-009/reference/def-partial-order", "外部引用 def:partial-order", "rujukan eksternal def:partial-order"),
        ("surface/unit-009/reference/sec-order", "外部引用 sec:order", "rujukan eksternal sec:order"),
        ("surface/unit-009/reference/eg-ab-cat", "外部引用 eg:Ab-cat", "rujukan eksternal eg:Ab-cat"),
        ("surface/unit-009/reference/sec-enriched-cat", "外部引用 sec:enriched-cat", "rujukan eksternal sec:enriched-cat"),
        (
            "surface/unit-009/reflow/finite-ordinal-category-display",
            "有限序数范畴显示（源排版）",
            "pembungkus tipografis target saja untuk tampilan kategori ordinal hingga",
        ),
        (
            "surface/unit-009/citation-occurrence/xiong-line-153",
            "重复引文 Xiong（第 153 行）",
            "kemunculan ulang sitasi Xiong pada baris 153",
        ),
        (
            "surface/unit-009/citation-occurrence/may99-line-184",
            "重复引文 May99（第 184 行）",
            "kemunculan ulang sitasi May99 pada baris 184",
        ),
    ]
    concepts = [
        {
            "id": identifier(key),
            "stable_key": key,
            "entity_type": "concept",
            "labels": [
                {"language": "zh-Hans", "text": source_label},
                {"language": "id-ID", "text": target_label},
            ],
        }
        for key, source_label, target_label in concept_specs
    ]
    concept_ids = [item["id"] for item in concepts]

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    unit_prerequisites = [
        prerequisite_by_key["prerequisite/basic-mathematical-literacy"],
        prerequisite_by_key["prerequisite/mathematical-logic"],
        prerequisite_by_key["prerequisite/elementary-set-theory"],
    ]

    principal_rights = next(
        item for item in data["rights"] if item["stable_key"] == "rights/principal-cc-by-4.0"
    )
    principal_rights["bindings"] = [
        binding(SOURCE),
        binding("repo/source/LICENSE"),
        binding("repo/source/ccby.png"),
    ]
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    unit_rights = [
        rights_by_key["rights/principal-cc-by-4.0"],
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_by_key["rights/noto-fonts-ofl-1.1"],
    ]

    section = {
        "id": section_id,
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter2.tex:39-198",
        "titles": [
            {"language": "zh-Hans", "text": "2.1 范畴与态射"},
            {"language": "id-ID", "text": "2.1 Kategori dan Morfisme"},
        ],
        "source_binding": binding(SOURCE, SPAN_START, SPAN_END),
        "target_binding": binding(TARGET, SPAN_START, SPAN_END),
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": [rights_by_key["rights/principal-cc-by-4.0"]],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    bibliography = binding("repo/source/Al-jabr.bib")
    citations = []
    # Backend v1.1.0 and its validator model citation closure by unique bib key.
    # The two repeated occurrences remain protected above and receive explicit
    # compatibility-surface identities in concept_specs.
    for key, line in RECORDED_CITATIONS:
        stable_key = f"citation/unit-009/{key.lower()}/line-{line}"
        citations.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "citation",
                "bib_key": key,
                "bibliography_path": bibliography["path"],
                "bibliography_sha256": bibliography["sha256"],
                "source_line": line,
                "target_line": line,
                "section_id": section_id,
            }
        )

    source_indexes = index_occurrences(span_text(SOURCE))
    target_indexes = index_occurrences(span_text(TARGET))
    index_entries = []
    for ordinal, (slug, source_index, target_index) in enumerate(
        zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True),
        start=1,
    ):
        source_name, source_key, source_line = source_index
        target_name, target_key, target_line = target_index
        if (source_name, source_line) != (target_name, target_line):
            raise SystemExit(
                f"Unit 009 backend generation refused: index occurrence {ordinal} source/target topology differs"
            )
        stable_key = f"index-entry/unit-009/{slug}"
        index_entries.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
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

    diagrams = []
    for ordinal, (slug, spec) in enumerate(zip(DIAGRAM_SLUGS, EXPECTED_DIAGRAMS, strict=True), start=1):
        source_format, occurrence, line_start, line_end = spec
        stable_key = f"diagram/unit-009/{slug}"
        diagrams.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "diagram",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_format": source_format,
                "source_occurrence_index": occurrence,
                "source_binding": binding(SOURCE, line_start, line_end),
                "target_binding": binding(TARGET, line_start, line_end),
                "rights_component_id": rights_by_key["rights/principal-cc-by-4.0"],
                "state": "audited_preserved",
            }
        )

    build_key = "build-surface/unit-009-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": (
            "pwsh -NoProfile -File scripts/build_unit_009.ps1 "
            "-OutputDirectory build/unit-009-replay-id"
        ),
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(BUILD_SUMMARY),
        "build_script": binding(BUILD_SCRIPT),
        "page_count": page_count,
        "status": "pass",
        "driver": binding(DRIVER),
        "input_bindings": [
            binding(COVER),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding(CROSSREF_AUX),
            binding("repo/fonts/NotoSansCJKsc-Black.otf"),
            binding("repo/fonts/NotoSansCJKsc-Medium.otf"),
            binding("repo/fonts/NotoSansCJKsc-Regular.otf"),
            binding("repo/fonts/NotoSerifCJKsc-Bold.otf"),
        ],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "biber",
            "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by unit-009-bab-2-kategori-dan-morfisme.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-009/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and independent audit for chapter2.tex lines 39-198; "
            "schema and stable-ID integrity; exact reviewed source and target span hashes; Section 2.1 "
            "with seven labels; ten reference occurrences over nine unique keys, including eight frozen "
            "external destinations and one internally resolved convention; five protected citation "
            "occurrences represented by three first-class unique-key records plus two explicit repeat-"
            "occurrence compatibility surfaces; 267 protected inline/display mathematical structures after "
            "explicit localized-text normalization; the target-only same-line small-display wrapper at "
            "line 112 recorded as digital reflow rather than upstream content; five source-preserved "
            "TikZ diagrams; 31 brace-aware "
            "localized index entries across the default and symbol indexes; 28 ordinary list items and "
            "zero exercises, hints, answers, or solutions; component-rights preservation; localized "
            "Indonesian reader interface; standalone digital reflow; clean replay build; structural PDF "
            "checks; and all-page MuPDF and Poppler visual inspection. Backend v1.1.0 has no first-class "
            "label or external-reference entity, so those protected surfaces receive deterministic "
            "concept-compatible IDs whose stable keys explicitly identify their compatibility role."
        ),
        "witness": ADMISSION_WITNESS,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding(ADMISSION_WITNESS),
    }

    dataset_key = "dataset/unit-009/id-id"
    data["dataset_stable_key"] = dataset_key
    data["dataset_id"] = identifier(dataset_key)
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-22",
        "status": "admitted",
        "admission_state": "admitted",
        "translation_state": "visually_checked",
        "qa_state": "translation_backend_build_visual_pass",
    }
    data["unit"] = {
        "id": unit_id,
        "stable_key": unit_key,
        "entity_type": "unit",
        "program_id": data["program"]["id"],
        "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"],
        "edition_id": data["edition"]["id"],
        "order": 9,
        "source_local_id": "chapter2.tex:39-198",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；范畴与态射"},
            {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Kategori dan Morfisme"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, SPAN_START, SPAN_END),
        "target_binding": binding(TARGET, SPAN_START, SPAN_END),
        "section_ids": [section_id],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/state-the-data-and-axioms-of-a-category",
            "outcome/read-and-compose-morphisms-in-commutative-diagrams",
            "outcome/distinguish-isomorphisms-endomorphisms-and-automorphisms",
            "outcome/distinguish-subcategories-full-subcategories-and-size-conditions",
            "outcome/recognize-standard-algebraic-topological-and-discrete-categories",
            "outcome/distinguish-monomorphisms-epimorphisms-and-one-sided-inverses",
            "outcome/construct-the-fundamental-groupoid-from-path-homotopy",
            "outcome/use-opposite-categories-and-the-duality-principle",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 3,
            "diagrams": 5,
            "index_entries": 31,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
