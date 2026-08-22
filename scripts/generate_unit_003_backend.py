#!/usr/bin/env python3
"""Generate the canonical Unit 003 backend record from reviewed live inputs."""

from __future__ import annotations

import copy
import hashlib
import json
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-002-bab-1-zfc.json"
OUTPUT = ROOT / "backend" / "data" / "unit-003-bab-1-struktur-urutan-dan-ordinal.json"
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

    unit_key = "unit/bab-1-struktur-urutan-dan-ordinal"
    unit_id = identifier(unit_key)
    section_key = unit_key + "/section/order-and-ordinals"
    section_id = identifier(section_key)

    concept_specs = [
        ("concept/partial-order", "偏序", "urutan parsial"),
        ("concept/preorder", "预序", "praurutan"),
        ("concept/order-preserving-map", "保序映射", "peta pelestari urutan"),
        ("concept/order-type", "序型", "tipe urutan"),
        ("concept/order-bounds-and-extrema", "上下界与极值元", "batas dan elemen ekstrem"),
        ("concept/filtered-poset", "滤过偏序集", "poset terarah ke atas"),
        ("concept/total-order", "全序", "urutan total"),
        ("concept/well-order", "良序", "urutan baik"),
        ("concept/initial-segment", "前段", "segmen awal"),
        ("concept/transitive-set", "传递集", "himpunan transitif"),
        ("concept/ordinal", "序数", "ordinal"),
        ("concept/successor-and-limit-ordinal", "后继与极限序数", "ordinal penerus dan ordinal limit"),
        ("concept/proper-class", "真类", "kelas sejati"),
        ("concept/burali-forti-paradox", "Burali-Forti 佯谬", "paradoks Burali-Forti"),
        ("concept/omega-and-peano-induction", "序数 omega 与 Peano 归纳", "ordinal omega dan induksi Peano"),
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
        prerequisite_by_key["prerequisite/elementary-set-theory"],
        prerequisite_by_key["prerequisite/mathematical-logic"],
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
        "source_local_id": "chapter1.tex:87-203",
        "titles": [
            {"language": "zh-Hans", "text": "序结构与序数"},
            {"language": "id-ID", "text": "Struktur Urutan dan Ordinal"},
        ],
        "source_binding": binding(SOURCE, 87, 203),
        "target_binding": binding(TARGET, 87, 203),
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": [rights_by_key["rights/principal-cc-by-4.0"]],
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }

    citation_specs = [("Je03", 152), ("HY14", 152), ("DN00", 202)]
    bibliography = binding("repo/source/Al-jabr.bib")
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
                "section_id": section_id,
            }
        )

    index_specs = [
        ("partial-order-poset", 90, "pianxuji@偏序集 (partially ordered set/poset)", "himpunan terurut parsial@himpunan terurut parsial (partially ordered set/poset)"),
        ("preorder", 90, "yuxuji@预序集 (pre-ordered set)", "himpunan praterurut@himpunan praterurut (pre-ordered set)"),
        ("maximal-element", 104, "jidayuan@极大元 (maximal element)", "elemen maksimal@elemen maksimal (maximal element)"),
        ("upper-bound-supremum", 104, "shangjie@上界 (upper bound), 上确界 (supremum)", "batas atas@batas atas (upper bound), supremum"),
        ("lower-bound-infimum", 104, "xiajie@下界 (lower bound), 下确界 (infimum)", "batas bawah@batas bawah (lower bound), infimum"),
        ("supremum-symbol", 111, "sup@$\\sup$", "sup@$\\sup$"),
        ("infimum-symbol", 111, "inf@$\\inf$", "inf@$\\inf$"),
        ("filtered-poset", 114, "luguoxuji@滤过偏序集 (filtered poset)", "poset terarah ke atas@poset terarah ke atas (filtered poset)"),
        ("total-order", 118, "quanxuji@全序集 (totally ordered set)", "himpunan terurut total@himpunan terurut total (totally ordered set)"),
        ("chain", 118, "lian@链 (chain)", "rantai@rantai (chain)"),
        ("well-order", 125, "liangxuji@良序集 (well-ordered set)", "himpunan terurut baik@himpunan terurut baik (well-ordered set)"),
        ("ordinal", 148, "xushu@序数 (ordinal)", "ordinal@ordinal"),
        ("on-symbol", 172, "$\\textbf{On}$", "$\\textbf{On}$"),
        ("limit-ordinal", 181, "xushu!极限序数 (limit ordinal)", "ordinal!ordinal limit (limit ordinal)"),
        ("burali-forti-paradox", 189, "Burali-Forti 佯谬", "paradoks Burali--Forti@paradoks Burali--Forti"),
        ("omega-symbol", 191, "omega@$\\omega$", "omega@$\\omega$"),
    ]
    index_entries = []
    for ordinal, (slug, line, source_key, target_key) in enumerate(index_specs, start=1):
        stable_key = f"index-entry/unit-003/{slug}"
        index_entries.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "index_entry",
                "section_id": section_id,
                "ordinal_in_unit": ordinal,
                "source_key": source_key,
                "target_key": target_key,
                "source_binding": binding(SOURCE, line, line),
                "target_binding": binding(TARGET, line, line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    build_key = "build-surface/unit-003-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_unit_003.ps1 -OutputDirectory build/unit-003-replay",
        "artifact_path": "artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf",
        "artifact_binding": binding("artifacts/unit-003-bab-1-struktur-urutan-dan-ordinal.pdf"),
        "log_binding": binding("qa/unit-003-evidence/build-log-summary.txt"),
        "build_script": binding("scripts/build_unit_003.ps1"),
        "page_count": 11,
        "status": "pass",
        "driver": binding("repo/source/unit-003-bab-1-struktur-urutan-dan-ordinal.tex"),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-003.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-003-crossrefs.aux"),
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
            "packages loaded by unit-003-bab-1-struktur-urutan-dan-ordinal.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-003/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": "Complete source-order translation and semantic audit for chapter1.tex lines 87-203; schema and stable-ID integrity; live inclusive line-span hashes; three unique citations; ten labels and two protected forward references; sixteen brace-aware index entries (twelve default and four sym1); zero diagrams/exercises/hints/answers/solutions; localized Indonesian theorem interface; 11-page standalone digital reflow; two clean builds; structural PDF checks; and all-page visual inspection.",
        "witness": "qa/UNIT_003_ADMISSION_20260822.md",
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding("qa/UNIT_003_ADMISSION_20260822.md"),
    }

    dataset_key = "dataset/unit-003/id-id"
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
        "order": 3,
        "source_local_id": "chapter1.tex:87-203",
        "titles": [
            {"language": "zh-Hans", "text": "第一章：集合论；序结构与序数"},
            {"language": "id-ID", "text": "Bab 1: Teori Himpunan; Struktur Urutan dan Ordinal"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, 87, 203),
        "target_binding": binding(TARGET, 87, 203),
        "section_ids": [section_id],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/use-partial-total-and-well-orders",
            "outcome/compute-bounds-and-order-types",
            "outcome/characterize-ordinals-as-transitive-well-orders",
            "outcome/use-successor-limit-and-omega-ordinals",
            "outcome/explain-the-burali-forti-obstruction",
        ],
        "surface_counts": {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 3,
            "diagrams": 0,
            "index_entries": 16,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = [section]
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = []
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
