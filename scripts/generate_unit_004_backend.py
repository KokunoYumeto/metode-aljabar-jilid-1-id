#!/usr/bin/env python3
"""Generate the canonical Unit 004 backend record from reviewed live inputs."""

from __future__ import annotations

import copy
import hashlib
import json
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-003-bab-1-struktur-urutan-dan-ordinal.json"
OUTPUT = ROOT / "backend" / "data" / "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter1.tex"
TARGET = "repo/source/chapter1.tex"


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


def main() -> None:
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-1-rekursi-transfinit-dan-penerapannya"
    unit_id = identifier(unit_key)

    concept_specs = [
        ("concept/transfinite-induction", "超穷归纳法", "induksi transfinit"),
        ("concept/theta-sequence", "θ-列", "barisan-θ"),
        ("concept/transfinite-recursion", "超穷递归", "rekursi transfinit"),
        ("concept/class-function", "类函数", "fungsi kelas"),
        ("concept/ordinal-addition", "序数加法", "penjumlahan ordinal"),
        ("concept/ordinal-multiplication", "序数乘法", "perkalian ordinal"),
        ("concept/ordinal-exponentiation", "序数指数", "perpangkatan ordinal"),
        ("concept/ordinal-representation-of-well-orders", "良序集的序数表示", "representasi ordinal bagi himpunan terurut baik"),
        ("concept/zermelo-well-ordering-theorem", "Zermelo 良序定理", "teorema pengurutan baik Zermelo"),
        ("concept/zorns-lemma", "Zorn 引理", "lema Zorn"),
        (
            "concept/choice-well-order-zorn-equivalence",
            "选择公理、良序定理与 Zorn 引理的等价性",
            "ekuivalensi aksioma pilihan, teorema pengurutan baik, dan lema Zorn",
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
    concept_by_key = {item["stable_key"]: item["id"] for item in concepts}
    concept_ids = [item["id"] for item in concepts]

    prerequisite_by_key = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    unit_prerequisites = [
        prerequisite_by_key["prerequisite/elementary-set-theory"],
        prerequisite_by_key["prerequisite/mathematical-logic"],
    ]
    rights_by_key = {item["stable_key"]: item["id"] for item in data["rights"]}
    unit_rights = [
        rights_by_key["rights/principal-cc-by-4.0"],
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"],
        rights_by_key["rights/noto-fonts-ofl-1.1"],
    ]

    section_specs = [
        (
            "transfinite-induction",
            205,
            221,
            "超穷归纳法",
            "Induksi transfinit",
            ["concept/transfinite-induction"],
        ),
        (
            "transfinite-recursion-principle",
            223,
            246,
            "超穷递归原理",
            "Prinsip rekursi transfinit",
            ["concept/theta-sequence", "concept/transfinite-recursion", "concept/class-function"],
        ),
        (
            "ordinal-arithmetic",
            248,
            254,
            "序数算术",
            "Aritmetika ordinal",
            ["concept/ordinal-addition", "concept/ordinal-multiplication", "concept/ordinal-exponentiation"],
        ),
        (
            "ordinal-representation-of-well-orders",
            256,
            266,
            "良序集的序数表示",
            "Representasi ordinal bagi himpunan terurut baik",
            ["concept/ordinal-representation-of-well-orders"],
        ),
        (
            "zermelo-well-ordering-theorem",
            268,
            279,
            "Zermelo 良序定理",
            "Teorema pengurutan baik Zermelo",
            ["concept/zermelo-well-ordering-theorem"],
        ),
        (
            "zorns-lemma-and-choice",
            281,
            287,
            "Zorn 引理与选择公理",
            "Lema Zorn dan aksioma pilihan",
            ["concept/zorns-lemma", "concept/choice-well-order-zorn-equivalence"],
        ),
    ]
    sections = []
    for order, (slug, line_start, line_end, source_title, target_title, keys) in enumerate(section_specs, start=1):
        stable_key = f"{unit_key}/section/{slug}"
        sections.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "section",
                "parent_id": unit_id,
                "order": order,
                "source_local_id": f"chapter1.tex:{line_start}-{line_end}",
                "titles": [
                    {"language": "zh-Hans", "text": source_title},
                    {"language": "id-ID", "text": target_title},
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
    section_by_slug = {item["stable_key"].rsplit("/", 1)[-1]: item for item in sections}

    index_specs = [
        (
            "transfinite-induction",
            207,
            "chaoqiongguinafa@超穷归纳法 (transfinite induction)",
            "induksi transfinit@induksi transfinit (transfinite induction)",
            "transfinite-induction",
        ),
        (
            "zermelo-well-ordering-theorem",
            269,
            "Zermelo 良序定理",
            "teorema pengurutan baik Zermelo@teorema pengurutan baik Zermelo",
            "zermelo-well-ordering-theorem",
        ),
        (
            "zorns-lemma",
            281,
            "Zorn 引理",
            "lema Zorn@lema Zorn",
            "zorns-lemma-and-choice",
        ),
    ]
    index_entries = []
    for ordinal, (slug, line, source_key, target_key, section_slug) in enumerate(index_specs, start=1):
        stable_key = f"index-entry/unit-004/{slug}"
        index_entries.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "index_entry",
                "section_id": section_by_slug[section_slug]["id"],
                "ordinal_in_unit": ordinal,
                "source_key": source_key,
                "target_key": target_key,
                "source_binding": binding(SOURCE, line, line),
                "target_binding": binding(TARGET, line, line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    bibliography = binding("repo/source/Al-jabr.bib")
    build_key = "build-surface/unit-004-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_unit_004.ps1 -OutputDirectory build/unit-004-replay",
        "artifact_path": "artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf",
        "artifact_binding": binding("artifacts/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.pdf"),
        "log_binding": binding("qa/unit-004-evidence/build-log-summary.txt"),
        "build_script": binding("scripts/build_unit_004.ps1"),
        "page_count": 8,
        "status": "pass",
        "driver": binding("repo/source/unit-004-bab-1-rekursi-transfinit-dan-penerapannya.tex"),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-004.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-004-crossrefs.aux"),
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
            "packages loaded by unit-004-bab-1-rekursi-transfinit-dan-penerapannya.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-004/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": "Complete source-order translation and independent audit for chapter1.tex lines 205-287; documented correction O013-LI-U004-COR-001 restoring the nonempty condition omitted from source line 206 but present in the cited theorem; schema and stable-ID integrity; live inclusive line-span hashes; four labels and nine protected reference occurrences over eight unique keys; three brace-aware index entries; zero citations, diagrams, exercises, hints, answers, or solutions; localized Indonesian reader interface; 8-page standalone digital reflow; two clean builds; structural PDF checks; and all-page MuPDF and Poppler visual inspection.",
        "witness": "qa/UNIT_004_ADMISSION_20260822.md",
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding("qa/UNIT_004_ADMISSION_20260822.md"),
    }

    dataset_key = "dataset/unit-004/id-id"
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
        "order": 4,
        "source_local_id": "chapter1.tex:205-287",
        "titles": [
            {"language": "zh-Hans", "text": "第一章：集合论；超穷递归及其应用"},
            {"language": "id-ID", "text": "Bab 1: Teori Himpunan; Rekursi Transfinit dan Penerapannya"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, 205, 287),
        "target_binding": binding(TARGET, 205, 287),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [],
        "diagram_ids": [],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/apply-transfinite-induction",
            "outcome/construct-class-functions-by-transfinite-recursion",
            "outcome/compute-basic-ordinal-arithmetic",
            "outcome/represent-well-orders-by-unique-ordinals",
            "outcome/use-the-well-ordering-theorem",
            "outcome/apply-zorns-lemma-and-relate-choice-principles",
        ],
        "surface_counts": {
            "sections": 6,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 0,
            "index_entries": 3,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = []
    data["diagrams"] = []
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
