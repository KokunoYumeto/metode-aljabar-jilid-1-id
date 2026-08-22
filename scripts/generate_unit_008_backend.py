#!/usr/bin/env python3
"""Generate the canonical Unit 008 backend record from reviewed live inputs.

The generator is deliberately admission-gated: it will not write Unit 008 JSON
until the final PDF, portable build summary, and admission witness exist and
contain the expected evidence markers.  Source and target line-span hashes are
also pinned to the reviewed Chapter 2 introduction, so later edits require a
deliberate review and generator update rather than silently changing the unit.

Backend schema v1.1.0 has no first-class entities for TeX labels, external
cross-references, native tables, or accessibility semantics.  This generator
therefore gives those protected surfaces deterministic UUIDv5 IDs using
concept-compatible records and links them to the sole introduction section.
Their stable keys identify them as surfaces rather than mathematical concepts,
and the QA event discloses this compatibility encoding.  The native four-row,
five-column table remains TeX text (not a diagram or image), and a paired
accessibility entity records its linear reading semantics.  Canonical CSV
projection remains the shared validator's responsibility.
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
TEMPLATE = ROOT / "backend" / "data" / "unit-007-bab-1-latihan.json"
OUTPUT = ROOT / "backend" / "data" / "unit-008-bab-2-pengantar-teori-kategori.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
BUILD_SUMMARY = "qa/unit-008-evidence/build-log-summary.txt"
ADMISSION_WITNESS = "qa/UNIT_008_ADMISSION_20260822.md"
ARTIFACT = "artifacts/unit-008-bab-2-pengantar-teori-kategori.pdf"
FINAL_LOG = "qa/UNIT_008_BUILD_FINAL.log"

SPAN_START = 1
SPAN_END = 37
EXPECTED_SOURCE_SPAN_SHA256 = "30e31fc7ba682acb3291cfa37cc29ad0567b5f8b7955b974713fc565d62a9874"
EXPECTED_TARGET_SPAN_SHA256 = "5a9bf7812b024dbed7b5b2fb69df14a98a417e5db8a633573fecf9f43733c9a1"

REQUIRED_FINAL_INPUTS = (
    ARTIFACT,
    FINAL_LOG,
    BUILD_SUMMARY,
    ADMISSION_WITNESS,
)

EXPECTED_LABELS = ("sec:category",)
EXPECTED_REFERENCES = ("sec:limits", "sec:Grot-universe", "prop:preorder-complete")
EXPECTED_CITATIONS = ("EM45", "Co11", "ML98", "sep-category-theory")
EXPECTED_SOURCE_ENVIRONMENTS = ("center", "tabular", "wenxintishi")
EXPECTED_TARGET_ENVIRONMENTS = ("center", "tabularx", "wenxintishi")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalized_span(relative: str, line_start: int, line_end: int) -> bytes:
    lines = (ROOT / relative).read_bytes().decode("utf-8").splitlines()
    if len(lines) < line_end:
        raise SystemExit(
            f"Unit 008 backend generation refused: {relative} has only {len(lines)} lines; "
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
            "Unit 008 backend generation is gated on final build/admission evidence. "
            "Create and verify these files first:\n  - " + formatted
        )


def require_text(relative: str, needle: str, purpose: str, *, ignore_case: bool = False) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    haystack = text.casefold() if ignore_case else text
    expected = needle.casefold() if ignore_case else needle
    if expected not in haystack:
        raise SystemExit(
            f"Unit 008 backend generation refused: {purpose} is absent from {relative}: {needle!r}"
        )


def summary_value(label: str) -> str:
    text = (ROOT / BUILD_SUMMARY).read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    if match is None:
        raise SystemExit(
            f"Unit 008 backend generation refused: {BUILD_SUMMARY} has no {label!r} evidence line"
        )
    return match.group(1)


def decimal_value(value: str, label: str) -> int:
    normalized = value.replace(",", "").strip()
    if not normalized.isdecimal():
        raise SystemExit(f"Unit 008 backend generation refused: invalid {label}: {value!r}")
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
            "Unit 008 backend generation refused: pdfinfo is required to cross-check the live artifact"
        ) from exc
    if completed.returncode != 0:
        raise SystemExit(
            "Unit 008 backend generation refused: pdfinfo could not inspect the live artifact: "
            + completed.stderr.strip()
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 008 backend generation refused: pdfinfo returned no page count")
    return int(match.group(1))


def require_build_evidence() -> int:
    artifact_payload = (ROOT / ARTIFACT).read_bytes()
    log_payload = (ROOT / FINAL_LOG).read_bytes()
    if len(artifact_payload) < 5 or not artifact_payload.startswith(b"%PDF-"):
        raise SystemExit(f"Unit 008 backend generation refused: {ARTIFACT} is not a nonempty PDF")

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
            raise SystemExit(f"Unit 008 backend generation refused: invalid {label}: {value!r}")

    if (actual_artifact_bytes, actual_artifact_sha) != (summary_artifact_bytes, summary_artifact_sha):
        raise SystemExit(
            "Unit 008 backend generation refused: live PDF bytes/hash do not match the build summary"
        )
    if (actual_log_bytes, actual_log_sha) != (summary_log_bytes, summary_log_sha):
        raise SystemExit(
            "Unit 008 backend generation refused: live final-log bytes/hash do not match the build summary"
        )

    live_pdf_pages = pdfinfo_page_count()
    log_text = log_payload.decode("utf-8", errors="replace")
    log_page_matches = re.findall(r"Output written on .*?\((\d+) pages?\)\.", log_text, flags=re.DOTALL)
    if not log_page_matches:
        raise SystemExit("Unit 008 backend generation refused: final log has no output page-count witness")
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
            "Unit 008 backend generation refused: admission receipt lacks parseable live PDF/log evidence"
        )
    receipt_pages = int(artifact_receipt.group(1))
    receipt_artifact_bytes = decimal_value(artifact_receipt.group(2), "receipt PDF byte count")
    receipt_artifact_sha = artifact_receipt.group(3)
    receipt_log_bytes = decimal_value(log_receipt.group(1), "receipt final-log byte count")
    receipt_log_sha = log_receipt.group(2)

    page_counts = {summary_pages, live_pdf_pages, live_log_pages, receipt_pages}
    if len(page_counts) != 1 or summary_pages < 1:
        raise SystemExit(
            "Unit 008 backend generation refused: PDF page count disagrees across live PDF, log, summary, and receipt"
        )
    if (receipt_artifact_bytes, receipt_artifact_sha) != (actual_artifact_bytes, actual_artifact_sha):
        raise SystemExit("Unit 008 backend generation refused: admission receipt PDF identity is stale")
    if (receipt_log_bytes, receipt_log_sha) != (actual_log_bytes, actual_log_sha):
        raise SystemExit("Unit 008 backend generation refused: admission receipt final-log identity is stale")
    return summary_pages


def span_text(relative: str) -> str:
    return normalized_span(relative, SPAN_START, SPAN_END).decode("utf-8")


def tex_sequence(pattern: str, text: str) -> tuple[str, ...]:
    return tuple(re.findall(pattern, text))


def citation_sequence(text: str) -> tuple[str, ...]:
    result: list[str] = []
    for group in re.findall(r"\\cite(?:\[[^\]]*\])*\{([^}]+)\}", text):
        result.extend(key.strip() for key in group.split(",") if key.strip())
    return tuple(result)


def math_multiset(text: str) -> Counter[str]:
    displays = re.findall(r"\\\[(.*?)\\\]", text, flags=re.DOTALL)
    without_displays = re.sub(r"\\\[.*?\\\]", "", text, flags=re.DOTALL)
    inlines = re.findall(r"(?<!\\)\$(?!\$)(.*?)(?<!\\)\$", without_displays, flags=re.DOTALL)

    def normalized(value: str) -> str:
        return re.sub(r"\s+", "", value)

    return Counter(["display:" + normalized(value) for value in displays] + ["inline:" + normalized(value) for value in inlines])


def table_topology(text: str) -> tuple[str, int, int, int, bool]:
    """Return environment, rows, cell separators, rules, and full-width state."""

    environments = [name for name in ("tabular", "tabularx") if f"\\begin{{{name}}}" in text]
    if len(environments) != 1:
        raise SystemExit(
            "Unit 008 backend generation refused: expected exactly one native tabular or tabularx surface"
        )
    environment = environments[0]
    begin = text.index(f"\\begin{{{environment}}}")
    end_marker = f"\\end{{{environment}}}"
    end = text.find(end_marker, begin)
    if end < 0:
        raise SystemExit(f"Unit 008 backend generation refused: unterminated {environment} surface")
    segment = text[begin : end + len(end_marker)]
    first_line = segment.splitlines()[0]
    return (
        environment,
        segment.count(r"\\"),
        segment.count("&"),
        segment.count(r"\hline"),
        r"\textwidth" in first_line,
    )


def require_protected_surfaces() -> None:
    source = span_text(SOURCE)
    target = span_text(TARGET)

    actual_source_hash = sha256(source.encode("utf-8"))
    actual_target_hash = sha256(target.encode("utf-8"))
    if actual_source_hash != EXPECTED_SOURCE_SPAN_SHA256:
        raise SystemExit(
            "Unit 008 backend generation refused: frozen source span drift: "
            f"{actual_source_hash} != {EXPECTED_SOURCE_SPAN_SHA256}"
        )
    if actual_target_hash != EXPECTED_TARGET_SPAN_SHA256:
        raise SystemExit(
            "Unit 008 backend generation refused: reviewed target span drift: "
            f"{actual_target_hash} != {EXPECTED_TARGET_SPAN_SHA256}"
        )

    for label, text, expected_environments, expected_table in (
        ("source", source, EXPECTED_SOURCE_ENVIRONMENTS, ("tabular", 4, 16, 4, False)),
        ("target", target, EXPECTED_TARGET_ENVIRONMENTS, ("tabularx", 4, 16, 4, True)),
    ):
        labels = tex_sequence(r"\\label\{([^}]+)\}", text)
        references = tex_sequence(r"\\ref\{([^}]+)\}", text)
        citations = citation_sequence(text)
        environments = tex_sequence(r"\\begin\{([^}]+)\}", text)
        topology = table_topology(text)

        if labels != EXPECTED_LABELS:
            raise SystemExit(f"Unit 008 backend generation refused: {label} labels are {labels}, expected {EXPECTED_LABELS}")
        if references != EXPECTED_REFERENCES:
            raise SystemExit(
                f"Unit 008 backend generation refused: {label} references are {references}, "
                f"expected {EXPECTED_REFERENCES}"
            )
        if citations != EXPECTED_CITATIONS:
            raise SystemExit(
                f"Unit 008 backend generation refused: {label} citations are {citations}, "
                f"expected {EXPECTED_CITATIONS}"
            )
        if environments != expected_environments:
            raise SystemExit(
                f"Unit 008 backend generation refused: {label} environments are {environments}, "
                f"expected {expected_environments}"
            )
        if topology != expected_table:
            raise SystemExit(
                f"Unit 008 backend generation refused: {label} table topology is {topology}, "
                f"expected {expected_table}"
            )

    if math_multiset(source) != math_multiset(target):
        raise SystemExit("Unit 008 backend generation refused: protected mathematics differs between source and target")
    if sum(math_multiset(source).values()) != 9:
        raise SystemExit("Unit 008 backend generation refused: expected eight inline and one display math surfaces")
    for marker in (r"\begin{Exercises}", r"\begin{hint}", r"\item", r"\index{"):
        if marker in source or marker in target:
            raise SystemExit(f"Unit 008 backend generation refused: unexpected learner/index surface {marker!r}")


def require_admission_evidence() -> int:
    require_final_inputs()
    page_count = require_build_evidence()
    require_protected_surfaces()
    require_text(BUILD_SUMMARY, "Unit 008 admitted build summary", "the admitted build identity")
    require_text(
        BUILD_SUMMARY,
        "Frozen source range: chapter2.tex lines 1-37",
        "the frozen source boundary",
    )
    require_text(BUILD_SUMMARY, "TeX errors: 0", "the zero-error build result")
    require_text(BUILD_SUMMARY, "Visual review:", "the all-page visual-review result")
    require_text(ADMISSION_WITNESS, "Decision: admitted", "the admission decision", ignore_case=True)
    require_text(ADMISSION_WITNESS, "chapter2.tex", "the admitted source filename")
    require_text(ADMISSION_WITNESS, "1-37", "the admitted source line range")
    for protected_key in (*EXPECTED_LABELS, *EXPECTED_REFERENCES, *EXPECTED_CITATIONS):
        require_text(ADMISSION_WITNESS, protected_key, f"the protected surface {protected_key}")
    return page_count


def main() -> None:
    page_count = require_admission_evidence()

    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-2-pengantar-teori-kategori"
    unit_id = identifier(unit_key)

    concept_specs = [
        ("concept/category", "范畴", "kategori"),
        ("concept/category-object", "对象", "objek kategori"),
        ("concept/morphism", "态射", "morfisme"),
        ("concept/arrow-notation", "箭头记号", "notasi panah"),
        ("concept/functor", "函子", "fungtor"),
        ("concept/natural-transformation", "自然变换", "transformasi natural"),
        ("concept/category-equivalence", "范畴等价", "ekuivalensi kategori"),
        ("concept/structure-preserving-map", "保结构映射", "peta pelestari struktur"),
        ("concept/homology-functor", "同调群函子", "fungtor grup homologi"),
        ("concept/commutative-diagram", "交换图表", "diagram komutatif"),
        ("concept/universal-property", "泛性质", "sifat universal"),
        ("concept/natural-map", "自然映射", "peta natural"),
        ("concept/canonical-map", "典范映射", "peta kanonik"),
        ("concept/monoidal-category", "幺半范畴", "kategori monoidal"),
        ("concept/product", "积", "produk"),
        ("concept/coproduct", "余积", "koproduk"),
        ("concept/adjoint-functor", "伴随函子", "fungtor adjoin"),
        ("concept/limit-category-theory", "极限", "limit dalam teori kategori"),
        ("concept/grothendieck-universe", "Grothendieck 宇宙", "semesta Grothendieck"),
        ("concept/category-size", "范畴与集合的大小", "ukuran himpunan dalam teori kategori"),
        ("concept/cobordism", "配边关系", "kobordisme"),
        ("concept/typed-lambda-calculus", "带类型的 lambda-演算", "kalkulus-lambda bertipe"),
        ("surface/unit-008/label/sec-category", "标签 sec:category", "label sec:category"),
        ("surface/unit-008/reference/sec-limits", "外部引用 sec:limits", "rujukan eksternal sec:limits"),
        (
            "surface/unit-008/reference/sec-grot-universe",
            "外部引用 sec:Grot-universe",
            "rujukan eksternal sec:Grot-universe",
        ),
        (
            "surface/unit-008/reference/prop-preorder-complete",
            "外部引用 prop:preorder-complete",
            "rujukan eksternal prop:preorder-complete",
        ),
        (
            "surface/unit-008/table/comparative-domain-analogies",
            "跨领域对象与态射对照表",
            "tabel perbandingan objek dan morfisme lintas bidang",
        ),
        (
            "surface/unit-008/accessibility/comparative-domain-analogies",
            "对照表的线性文字语义",
            "semantik teks linear tabel perbandingan lintas bidang",
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

    section_key = f"{unit_key}/section/chapter-introduction"
    section = {
        "id": identifier(section_key),
        "stable_key": section_key,
        "entity_type": "section",
        "parent_id": unit_id,
        "order": 1,
        "source_local_id": "chapter2.tex:1-37",
        "titles": [
            {"language": "zh-Hans", "text": "第二章导言：范畴论基础"},
            {"language": "id-ID", "text": "Pengantar Bab 2: Dasar-Dasar Teori Kategori"},
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
    citation_specs = [
        ("EM45", 12),
        ("Co11", 18),
        ("ML98", 31),
        ("sep-category-theory", 31),
    ]
    citations = []
    for key, line in citation_specs:
        stable_key = "citation/" + key.lower()
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
                "section_id": section["id"],
            }
        )

    build_key = "build-surface/unit-008-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": (
            "pwsh -NoProfile -File scripts/build_unit_008.ps1 "
            "-OutputDirectory build/unit-008-replay-id"
        ),
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(BUILD_SUMMARY),
        "build_script": binding("scripts/build_unit_008.ps1"),
        "page_count": page_count,
        "status": "pass",
        "driver": binding("repo/source/unit-008-bab-2-pengantar-teori-kategori.tex"),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-008.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-008-crossrefs.aux"),
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
            "packages loaded by unit-008-bab-2-pengantar-teori-kategori.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-008/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and independent audit for chapter2.tex lines 1-37; "
            "schema and stable-ID integrity; exact reviewed source and target span hashes; one chapter-"
            "introduction semantic section; four unique citation keys and occurrences; label "
            "sec:category; three standalone-external references sec:limits, sec:Grot-universe, and "
            "prop:preorder-complete; eight inline and one display mathematics surfaces with identical "
            "normalized TeX; and the native four-row, five-column comparative table retained as text, "
            "reflowed to a full-width tabularx target, and paired with a linear-reading accessibility "
            "surface. Backend v1.1.0 has no first-class "
            "label, external-reference, native-table, or accessibility entities, so those six protected "
            "surfaces receive deterministic concept-compatible IDs whose stable keys explicitly mark "
            "them as surfaces. Zero exercises, hints, answers, solutions, diagrams, or index entries; "
            "component-rights preservation; localized Indonesian reader interface; standalone digital "
            "reflow; clean build; structural PDF checks; and all-page MuPDF and Poppler visual inspection."
        ),
        "witness": ADMISSION_WITNESS,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding(ADMISSION_WITNESS),
    }

    dataset_key = "dataset/unit-008/id-id"
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
        "order": 8,
        "source_local_id": "chapter2.tex:1-37",
        "titles": [
            {"language": "zh-Hans", "text": "第二章：范畴论基础；导言"},
            {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Pengantar"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, SPAN_START, SPAN_END),
        "target_binding": binding(TARGET, SPAN_START, SPAN_END),
        "section_ids": [section["id"]],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [],
        "index_entry_ids": [],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/identify-categories-objects-morphisms-functors-and-natural-transformations",
            "outcome/interpret-structure-preserving-maps-and-homology-as-categorical-bridges",
            "outcome/explain-the-relational-and-universal-property-viewpoint",
            "outcome/compare-object-and-morphism-analogies-across-four-disciplines",
            "outcome/follow-the-chapters-example-first-learning-route",
            "outcome/recognize-category-size-issues-and-the-grothendieck-universe-firewall",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 4,
            "diagrams": 0,
            "index_entries": 0,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = []
    data["index_entries"] = []
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
