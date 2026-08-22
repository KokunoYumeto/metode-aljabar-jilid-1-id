#!/usr/bin/env python3
"""Generate the canonical Unit 007 backend record from reviewed live inputs.

The generator refuses to emit an admitted record until the final reader PDF,
portable build summary, and admission witness exist and contain the expected
admission markers.  All hashes are computed from the live files at generation
time.

Backend schema v1.1.0 has no first-class exercise, subpart, or hint arrays and
the corresponding validator currently requires their scalar surface counts to
remain zero.  To preserve the learner surfaces without changing the shared
schema in this unit, the six top-level exercises are represented as ordered
section entities.  Six subparts and six hints receive deterministic UUIDv5 IDs
as concept entities and are linked to their parent exercise through that
section's ``concept_ids`` (exported as ``covers`` relations).  The true 6/6/6
topology is also asserted against source and target and disclosed in the QA
event.  This is a compatibility encoding, not a claim that the surfaces are
ordinary exposition concepts.  Canonical CSV projection remains the shared
validator's responsibility; refusing the JSON write also prevents downstream
CSV emission from incomplete evidence.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-006-bab-1-semesta-grothendieck.json"
OUTPUT = ROOT / "backend" / "data" / "unit-007-bab-1-latihan.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter1.tex"
TARGET = "repo/source/chapter1.tex"
BUILD_SUMMARY = "qa/unit-007-evidence/build-log-summary.txt"
ADMISSION_WITNESS = "qa/UNIT_007_ADMISSION_20260822.md"
ARTIFACT = "artifacts/unit-007-bab-1-latihan.pdf"

REQUIRED_FINAL_INPUTS = (
    ARTIFACT,
    BUILD_SUMMARY,
    ADMISSION_WITNESS,
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def binding(relative: str, line_start: int | None = None, line_end: int | None = None) -> dict[str, object]:
    payload = (ROOT / relative).read_bytes()
    result: dict[str, object] = {
        "path": relative,
        "bytes": len(payload),
        "sha256": sha256(payload),
    }
    if line_start is not None and line_end is not None:
        lines = payload.decode("utf-8").splitlines()
        normalized = ("\n".join(lines[line_start - 1 : line_end]) + "\n").encode("utf-8")
        result.update(
            {
                "line_start": line_start,
                "line_end": line_end,
                "span_sha256": sha256(normalized),
                "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
            }
        )
    return result


def require_final_inputs() -> None:
    missing = [relative for relative in REQUIRED_FINAL_INPUTS if not (ROOT / relative).is_file()]
    if missing:
        formatted = "\n  - ".join(missing)
        raise SystemExit(
            "Unit 007 backend generation is gated on final build/admission evidence. "
            "Create and verify these files first:\n  - " + formatted
        )


def require_text(relative: str, needle: str, purpose: str, *, ignore_case: bool = False) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    haystack = text.casefold() if ignore_case else text
    expected = needle.casefold() if ignore_case else needle
    if expected not in haystack:
        raise SystemExit(
            f"Unit 007 backend generation refused: {purpose} is absent from {relative}: {needle!r}"
        )


def require_pattern(relative: str, pattern: str, purpose: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if re.search(pattern, text, flags=re.IGNORECASE) is None:
        raise SystemExit(
            f"Unit 007 backend generation refused: {purpose} is absent from {relative}: /{pattern}/i"
        )


def admitted_page_count() -> int:
    text = (ROOT / BUILD_SUMMARY).read_text(encoding="utf-8")
    match = re.search(r"^PDF pages:\s*(\d+)\s*$", text, flags=re.MULTILINE)
    if match is None:
        raise SystemExit(
            f"Unit 007 backend generation refused: {BUILD_SUMMARY} has no 'PDF pages: N' evidence line"
        )
    count = int(match.group(1))
    if count < 1:
        raise SystemExit(f"Unit 007 backend generation refused: invalid admitted PDF page count {count}")
    return count


def require_pdf_artifact() -> None:
    payload = (ROOT / ARTIFACT).read_bytes()
    if len(payload) < 5 or not payload.startswith(b"%PDF-"):
        raise SystemExit(f"Unit 007 backend generation refused: {ARTIFACT} is not a nonempty PDF")


TOPOLOGY_TOKEN_RE = re.compile(
    r"\\begin\{Exercises\}|\\end\{Exercises\}|"
    r"\\begin\{compactenum\}(?:\[[^\]]*\])?|\\end\{compactenum\}|"
    r"\\begin\{hint\}|\\end\{hint\}|\\item\b"
)


def exercise_topology(relative: str) -> tuple[int, int, int]:
    """Count top-level exercises, compactenum subparts, and hints in 508--536."""

    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[507:536]) + "\n"
    in_exercises = False
    compactenum_depth = 0
    exercises = 0
    subparts = 0
    hints = 0

    for match in TOPOLOGY_TOKEN_RE.finditer(text):
        token = match.group(0)
        if token == r"\begin{Exercises}":
            if in_exercises:
                raise SystemExit(f"Unit 007 backend generation refused: nested Exercises in {relative}")
            in_exercises = True
        elif token == r"\end{Exercises}":
            if not in_exercises or compactenum_depth != 0:
                raise SystemExit(f"Unit 007 backend generation refused: unbalanced Exercises in {relative}")
            in_exercises = False
        elif token.startswith(r"\begin{compactenum}"):
            compactenum_depth += 1
        elif token == r"\end{compactenum}":
            compactenum_depth -= 1
            if compactenum_depth < 0:
                raise SystemExit(f"Unit 007 backend generation refused: unbalanced compactenum in {relative}")
        elif token == r"\begin{hint}":
            hints += 1
        elif token == r"\item":
            if not in_exercises:
                raise SystemExit(f"Unit 007 backend generation refused: item outside Exercises in {relative}")
            if compactenum_depth == 0:
                exercises += 1
            else:
                subparts += 1

    if in_exercises or compactenum_depth != 0:
        raise SystemExit(f"Unit 007 backend generation refused: unterminated exercise topology in {relative}")
    return exercises, subparts, hints


def require_admission_evidence() -> int:
    require_final_inputs()
    require_pdf_artifact()
    require_text(BUILD_SUMMARY, "Unit 007 admitted build summary", "the admitted build identity")
    require_text(
        BUILD_SUMMARY,
        "Frozen source range: chapter1.tex lines 508-536",
        "the frozen source boundary",
    )
    require_text(BUILD_SUMMARY, "TeX errors: 0", "the zero-error build result")
    require_text(BUILD_SUMMARY, "Visual review:", "the all-page visual-review result")
    require_text(ADMISSION_WITNESS, "Decision: admitted", "the admission decision", ignore_case=True)
    require_text(ADMISSION_WITNESS, "chapter1.tex", "the admitted source filename")
    require_text(ADMISSION_WITNESS, "508-536", "the admitted source line range")
    require_text(ADMISSION_WITNESS, "six top-level exercises", "the exercise census", ignore_case=True)
    require_text(ADMISSION_WITNESS, "six enumerated subparts", "the subpart census", ignore_case=True)
    require_pattern(ADMISSION_WITNESS, r"six(?:\s+source)?\s+hints", "the hint census")
    return admitted_page_count()


def main() -> None:
    page_count = require_admission_evidence()
    expected_topology = (6, 6, 6)
    source_topology = exercise_topology(SOURCE)
    target_topology = exercise_topology(TARGET)
    if source_topology != expected_topology:
        raise SystemExit(
            f"Unit 007 backend generation refused: source exercise topology is {source_topology}, "
            f"expected {expected_topology}"
        )
    if target_topology != expected_topology:
        raise SystemExit(
            f"Unit 007 backend generation refused: target exercise topology is {target_topology}, "
            f"expected {expected_topology}"
        )

    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-1-latihan"
    unit_id = identifier(unit_key)

    # Ordinary mathematical concepts plus compatibility entities for the six
    # subparts and six hints.  The nested stable keys retain each learner
    # surface's parent exercise independently of wording, pagination, or locale.
    concept_specs = [
        ("concept/ordered-sum", "有序和", "jumlah terurut"),
        ("concept/reverse-lexicographic-order", "反字典序", "urutan leksikografis terbalik"),
        ("concept/ordinal-addition", "序数加法", "penjumlahan ordinal"),
        ("concept/ordinal-multiplication", "序数乘法", "perkalian ordinal"),
        ("concept/transfinite-induction", "超穷归纳", "induksi transfinit"),
        ("concept/ordinal-division-with-remainder", "序数带余除法", "pembagian ordinal dengan sisa"),
        ("concept/ordinal-exponentiation", "序数幂", "perpangkatan ordinal"),
        ("concept/noncommutative-ordinal-multiplication", "序数乘法的非交换性", "ketidakkomutatifan perkalian ordinal"),
        ("concept/cantor-normal-form", "Cantor 标准形", "bentuk normal Cantor"),
        ("concept/natural-number-pairing-bijection", "自然数对的双射编码", "pengodean bijektif pasangan bilangan cacah"),
        ("concept/konig-lemma-cardinals", "König 引理", "lema König untuk kardinal"),
        ("concept/cardinal-sum", "基数和", "jumlah kardinal"),
        ("concept/cardinal-product", "基数积", "hasil kali kardinal"),
        ("concept/cantor-theorem", "Cantor 定理", "teorema Cantor"),
        ("concept/diagonal-argument", "对角线论证", "argumen diagonal"),
        (f"{unit_key}/exercise/01/subpart/i", "练习 1(i)", "Latihan 1(i)"),
        (f"{unit_key}/exercise/01/subpart/ii", "练习 1(ii)", "Latihan 1(ii)"),
        (f"{unit_key}/exercise/02/subpart/i", "练习 2(i)", "Latihan 2(i)"),
        (f"{unit_key}/exercise/02/subpart/ii", "练习 2(ii)", "Latihan 2(ii)"),
        (f"{unit_key}/exercise/02/subpart/iii", "练习 2(iii)", "Latihan 2(iii)"),
        (f"{unit_key}/exercise/02/subpart/iv", "练习 2(iv)", "Latihan 2(iv)"),
        (f"{unit_key}/exercise/01/hint/01", "练习 1 的提示", "Petunjuk Latihan 1"),
        (f"{unit_key}/exercise/02/subpart/ii/hint/01", "练习 2(ii) 的提示", "Petunjuk Latihan 2(ii)"),
        (f"{unit_key}/exercise/02/subpart/iii/hint/01", "练习 2(iii) 的提示", "Petunjuk Latihan 2(iii)"),
        (f"{unit_key}/exercise/03/hint/01", "练习 3 的提示", "Petunjuk Latihan 3"),
        (f"{unit_key}/exercise/04/hint/01", "练习 4 的提示", "Petunjuk Latihan 4"),
        (f"{unit_key}/exercise/06/hint/01", "练习 6 的提示", "Petunjuk Latihan 6"),
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
    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    concept_ids = [item["id"] for item in concepts]

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    unit_prerequisites = [
        prerequisite_by_key["prerequisite/basic-mathematical-literacy"],
        prerequisite_by_key["prerequisite/mathematical-logic"],
        prerequisite_by_key["prerequisite/elementary-set-theory"],
    ]
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    unit_rights = [
        rights_by_key["rights/principal-cc-by-4.0"],
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_by_key["rights/noto-fonts-ofl-1.1"],
    ]

    exercise_specs = [
        (
            1,
            509,
            515,
            "序数加法与乘法的序型",
            "Tipe Urutan Penjumlahan dan Perkalian Ordinal",
            [
                "concept/ordered-sum",
                "concept/reverse-lexicographic-order",
                "concept/ordinal-addition",
                "concept/ordinal-multiplication",
                "concept/transfinite-induction",
                f"{unit_key}/exercise/01/subpart/i",
                f"{unit_key}/exercise/01/subpart/ii",
                f"{unit_key}/exercise/01/hint/01",
            ],
        ),
        (
            2,
            516,
            522,
            "序数运算的性质",
            "Sifat-Sifat Operasi Ordinal",
            [
                "concept/ordinal-addition",
                "concept/ordinal-division-with-remainder",
                "concept/ordinal-exponentiation",
                f"{unit_key}/exercise/02/subpart/i",
                f"{unit_key}/exercise/02/subpart/ii",
                f"{unit_key}/exercise/02/subpart/iii",
                f"{unit_key}/exercise/02/subpart/iv",
                f"{unit_key}/exercise/02/subpart/ii/hint/01",
                f"{unit_key}/exercise/02/subpart/iii/hint/01",
            ],
        ),
        (
            3,
            523,
            523,
            "序数乘法的非交换性",
            "Ketidakkomutatifan Perkalian Ordinal",
            [
                "concept/noncommutative-ordinal-multiplication",
                f"{unit_key}/exercise/03/hint/01",
            ],
        ),
        (
            4,
            524,
            526,
            "Cantor 标准形",
            "Bentuk Normal Cantor",
            [
                "concept/cantor-normal-form",
                "concept/ordinal-division-with-remainder",
                "concept/transfinite-induction",
                f"{unit_key}/exercise/04/hint/01",
            ],
        ),
        (
            5,
            527,
            527,
            "自然数对的双射编码",
            "Pengodean Bijektif Pasangan Bilangan Cacah",
            ["concept/natural-number-pairing-bijection"],
        ),
        (
            6,
            528,
            535,
            "König 引理与 Cantor 定理",
            "Lema König dan Teorema Cantor",
            [
                "concept/konig-lemma-cardinals",
                "concept/cardinal-sum",
                "concept/cardinal-product",
                "concept/cantor-theorem",
                "concept/diagonal-argument",
                f"{unit_key}/exercise/06/hint/01",
            ],
        ),
    ]
    sections = []
    for ordinal, line_start, line_end, source_title, target_title, keys in exercise_specs:
        stable_key = f"{unit_key}/exercise/{ordinal:02d}"
        sections.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "section",
                "parent_id": unit_id,
                "order": ordinal,
                "source_local_id": f"chapter1.tex:{line_start}-{line_end}",
                "titles": [
                    {"language": "zh-Hans", "text": f"练习 {ordinal}：{source_title}"},
                    {"language": "id-ID", "text": f"Latihan {ordinal}: {target_title}"},
                ],
                "source_binding": binding(SOURCE, line_start, line_end),
                "target_binding": binding(TARGET, line_start, line_end),
                "concept_ids": [concept_by_key[key] for key in keys],
                "prerequisite_ids": unit_prerequisites,
                "rights_component_ids": [rights_by_key["rights/principal-cc-by-4.0"]],
                "translation_state": "visually_checked",
                "admission_state": "admitted",
            }
        )

    build_key = "build-surface/unit-007-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_007.ps1 -OutputDirectory build/unit-007-replay-id",
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(BUILD_SUMMARY),
        "build_script": binding("scripts/build_unit_007.ps1"),
        "page_count": page_count,
        "status": "pass",
        "driver": binding("repo/source/unit-007-bab-1-latihan.tex"),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-007.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-007-crossrefs.aux"),
            binding("repo/fonts/NotoSansCJKsc-Black.otf"),
            binding("repo/fonts/NotoSansCJKsc-Medium.otf"),
            binding("repo/fonts/NotoSansCJKsc-Regular.otf"),
            binding("repo/fonts/NotoSerifCJKsc-Bold.otf"),
        ],
        "external_dependencies": [
            "XeLaTeX",
            "PowerShell 7",
            "makeindex (default and sym1 indexes)",
            "Fandol fonts from TeX distribution",
            "TeX Gyre Heros",
            "packages loaded by unit-007-bab-1-latihan.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-007/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and independent audit for chapter1.tex lines 508-536; "
            "documented correction O013-LI-U007-COR-001 repairing the source's type error at line 519 "
            "by taking delta to be the order type of the displayed well-ordered tail; "
            "schema and stable-ID integrity; live inclusive line-span hashes; six top-level exercises, "
            "six enumerated subparts, six source hints, and twelve total item tokens preserved in the "
            "target; deterministic compatibility IDs for every exercise, subpart, and hint with each "
            "subpart and hint linked to its parent exercise; zero citations, diagrams, index entries, "
            "answers, or solutions; component-rights preservation; localized Indonesian reader "
            "interface; standalone digital reflow; two clean builds; structural PDF checks; and "
            "all-page MuPDF and Poppler visual inspection. Backend v1.1.0 lacks first-class exercise "
            "and hint arrays, so the six exercises are encoded as ordered section entities and the "
            "six subparts plus six hints as stable concept entities; scalar exercise and hint surface "
            "counts remain zero solely for current validator compatibility."
        ),
        "witness": ADMISSION_WITNESS,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding(ADMISSION_WITNESS),
    }

    dataset_key = "dataset/unit-007/id-id"
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
        "order": 7,
        "source_local_id": "chapter1.tex:508-536",
        "titles": [
            {"language": "zh-Hans", "text": "第一章：习题"},
            {"language": "id-ID", "text": "Bab 1: Latihan"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, 508, 536),
        "target_binding": binding(TARGET, 508, 536),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [],
        "diagram_ids": [],
        "index_entry_ids": [],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/model-ordinal-addition-and-multiplication-by-ordered-constructions",
            "outcome/prove-monotonicity-and-division-properties-of-ordinal-operations",
            "outcome/exhibit-noncommutativity-of-ordinal-multiplication",
            "outcome/prove-existence-and-uniqueness-of-cantor-normal-form",
            "outcome/construct-a-bijection-between-pairs-and-natural-numbers",
            "outcome/prove-konigs-lemma-and-deduce-cantors-theorem",
        ],
        # Compatibility values required by the current validator.  The true
        # topology is 6 exercises / 6 subparts / 6 hints and is carried by the
        # stable entities, relations, live topology gate, and QA scope above.
        "surface_counts": {
            "sections": 6,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 0,
            "index_entries": 0,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = []
    data["diagrams"] = []
    data["index_entries"] = []
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
