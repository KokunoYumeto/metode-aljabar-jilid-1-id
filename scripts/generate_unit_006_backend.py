#!/usr/bin/env python3
"""Generate the canonical Unit 006 backend record from reviewed live inputs.

The generator deliberately refuses to emit an admitted record until the final
reader artifact, portable build summary, and admission witness all exist.  This
keeps build and visual-QA claims tied to live evidence rather than placeholders.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-005-bab-1-kardinal.json"
OUTPUT = ROOT / "backend" / "data" / "unit-006-bab-1-semesta-grothendieck.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter1.tex"
TARGET = "repo/source/chapter1.tex"
BUILD_SUMMARY = "qa/unit-006-evidence/build-log-summary.txt"
ADMISSION_WITNESS = "qa/UNIT_006_ADMISSION_20260822.md"
ARTIFACT = "artifacts/unit-006-bab-1-semesta-grothendieck.pdf"
CORRECTION_ID = "O013-LI-U006-COR-001"

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
            "Unit 006 backend generation is gated on final build/admission evidence. "
            "Create and verify these files first:\n  - " + formatted
        )


def require_text(relative: str, needle: str, purpose: str) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"Unit 006 backend generation refused: {purpose} is absent from {relative}: {needle!r}")


def admitted_page_count() -> int:
    text = (ROOT / BUILD_SUMMARY).read_text(encoding="utf-8")
    match = re.search(r"^PDF pages:\s*(\d+)\s*$", text, flags=re.MULTILINE)
    if match is None:
        raise SystemExit(
            f"Unit 006 backend generation refused: {BUILD_SUMMARY} has no 'PDF pages: N' evidence line"
        )
    count = int(match.group(1))
    if count < 1:
        raise SystemExit(f"Unit 006 backend generation refused: invalid admitted PDF page count {count}")
    return count


def main() -> None:
    require_final_inputs()
    require_text(
        SOURCE,
        r"\index{jihelun!层垒谱系 (cumulative hierachy)}",
        "the frozen upstream index-key typo corrected by O013-LI-U006-COR-001",
    )
    require_text(
        TARGET,
        r"\index{teori himpunan!hierarki kumulatif (cumulative hierarchy)}",
        "the corrected Indonesian index entry for O013-LI-U006-COR-001",
    )
    require_text(BUILD_SUMMARY, CORRECTION_ID, "the correction receipt")
    require_text(ADMISSION_WITNESS, CORRECTION_ID, "the correction adjudication")
    page_count = admitted_page_count()

    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-1-semesta-grothendieck"
    unit_id = identifier(unit_key)

    concept_specs = [
        ("concept/grothendieck-universe", "Grothendieck 宇宙", "semesta Grothendieck"),
        ("concept/transitive-set", "传递集", "himpunan transitif"),
        ("concept/universe-closure-properties", "宇宙的封闭性质", "sifat ketertutupan semesta"),
        ("concept/u-set", "\\mathcal{U}-集", "himpunan-$\\mathcal{U}$"),
        ("concept/u-small-set", "\\mathcal{U}-小集", "himpunan kecil relatif terhadap $\\mathcal{U}$"),
        ("concept/proper-class-firewall", "真类问题的防火墙", "sekat pelindung terhadap persoalan kelas sejati"),
        ("concept/grothendieck-universe-hypothesis", "Grothendieck 宇宙假设", "hipotesis semesta Grothendieck"),
        ("concept/cumulative-hierarchy", "层垒谱系", "hierarki kumulatif"),
        ("concept/membership-minimal-element", "关于属于关系的极小元", "elemen minimal terhadap relasi keanggotaan"),
        ("concept/hereditarily-finite-set", "遗传有限集", "himpunan yang berhingga secara herediter"),
        ("concept/strongly-inaccessible-cardinal", "强不可达基数", "kardinal tak terjangkau kuat"),
        ("concept/universe-characterization", "宇宙的层垒谱系刻画", "karakterisasi semesta dalam hierarki kumulatif"),
        ("concept/zfc-model", "ZFC 模型", "model ZFC"),
        ("concept/internal-set-class-viewpoint", "模型内部的集合与类", "sudut pandang internal tentang himpunan dan kelas"),
        ("concept/large-cardinal-strength", "大基数假设的强度", "kekuatan asumsi kardinal besar"),
        ("concept/single-universe-practice", "单个宇宙的数学实践", "praktik matematika dengan satu semesta"),
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
            "universe-definition-closure-and-hypothesis",
            436,
            463,
            "Grothendieck 宇宙、封闭性质与宇宙假设",
            "Definisi, Ketertutupan, dan Hipotesis Semesta Grothendieck",
            [
                "concept/grothendieck-universe",
                "concept/transitive-set",
                "concept/universe-closure-properties",
                "concept/u-set",
                "concept/u-small-set",
                "concept/proper-class-firewall",
                "concept/grothendieck-universe-hypothesis",
            ],
        ),
        (
            "cumulative-hierarchy-and-set-membership",
            465,
            483,
            "层垒谱系与集合的归属",
            "Hierarki Kumulatif dan Keanggotaan Setiap Himpunan",
            [
                "concept/cumulative-hierarchy",
                "concept/transitive-set",
                "concept/membership-minimal-element",
            ],
        ),
        (
            "hereditarily-finite-sets-and-universe-definition",
            485,
            485,
            "遗传有限集与宇宙定义",
            "Himpunan Berhingga secara Herediter dan Definisi Semesta",
            [
                "concept/hereditarily-finite-set",
                "concept/grothendieck-universe",
            ],
        ),
        (
            "strongly-inaccessible-cardinals-and-universe-characterization",
            487,
            498,
            "强不可达基数与宇宙刻画",
            "Kardinal Tak Terjangkau Kuat dan Karakterisasi Semesta",
            [
                "concept/strongly-inaccessible-cardinal",
                "concept/large-cardinal-strength",
                "concept/universe-characterization",
                "concept/cumulative-hierarchy",
            ],
        ),
        (
            "zfc-models-and-strength-of-the-universe-hypothesis",
            500,
            506,
            "ZFC 模型与宇宙假设的强度",
            "Model ZFC dan Kekuatan Hipotesis Semesta",
            [
                "concept/zfc-model",
                "concept/internal-set-class-viewpoint",
                "concept/grothendieck-universe-hypothesis",
                "concept/strongly-inaccessible-cardinal",
                "concept/large-cardinal-strength",
                "concept/single-universe-practice",
            ],
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

    bibliography = binding("repo/source/Al-jabr.bib")
    citation_specs = [
        ("SGA4-1", 437, "universe-definition-closure-and-hypothesis"),
        ("Je03", 495, "strongly-inaccessible-cardinals-and-universe-characterization"),
        ("Shu08", 506, "zfc-models-and-strength-of-the-universe-hypothesis"),
    ]
    citations = []
    for key, line, section_slug in citation_specs:
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
                "section_id": section_by_slug[section_slug]["id"],
            }
        )

    index_specs = [
        (
            "universe",
            439,
            "yuzhou@宇宙 (universe)",
            "semesta@semesta (universe)",
            "universe-definition-closure-and-hypothesis",
        ),
        (
            "u-set",
            448,
            r"U-ji@$\mathcal{U}$-集",
            r"himpunan-U@himpunan-$\mathcal{U}$",
            "universe-definition-closure-and-hypothesis",
        ),
        (
            "cumulative-hierarchy",
            465,
            "jihelun!层垒谱系 (cumulative hierachy)",
            "teori himpunan!hierarki kumulatif (cumulative hierarchy)",
            "cumulative-hierarchy-and-set-membership",
        ),
        (
            "strongly-inaccessible-cardinal",
            487,
            "jishu!强不可达 (strongly inaccessible)",
            "kardinal!tak terjangkau kuat (strongly inaccessible)",
            "strongly-inaccessible-cardinals-and-universe-characterization",
        ),
    ]
    index_entries = []
    for ordinal, (slug, line, source_key, target_key, section_slug) in enumerate(index_specs, start=1):
        stable_key = f"index-entry/unit-006/{slug}"
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

    build_key = "build-surface/unit-006-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_006.ps1 -OutputDirectory build/unit-006-replay-id",
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(BUILD_SUMMARY),
        "build_script": binding("scripts/build_unit_006.ps1"),
        "page_count": page_count,
        "status": "pass",
        "driver": binding("repo/source/unit-006-bab-1-semesta-grothendieck.tex"),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-006.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-006-crossrefs.aux"),
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
            "packages loaded by unit-006-bab-1-semesta-grothendieck.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-006/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": (
            "Complete source-order translation and independent audit for chapter1.tex lines 436-506; "
            "documented correction O013-LI-U006-COR-001 repairing the upstream English index typo "
            "'cumulative hierachy' to 'cumulative hierarchy' at line 465; schema and stable-ID "
            "integrity; live inclusive line-span hashes; three unique citation keys across six protected "
            "citation occurrences (SGA4-1 twice, Je03 three times, and Shu08 once); two labels and four "
            "protected reference occurrences over four unique keys, including three frozen cross-unit "
            "references; four brace-aware index entries; zero diagrams, exercises, hints, answers, or "
            "solutions; localized Indonesian reader interface; standalone digital reflow; two clean "
            "builds; structural PDF checks; and all-page MuPDF and Poppler visual inspection."
        ),
        "witness": ADMISSION_WITNESS,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding(ADMISSION_WITNESS),
    }

    dataset_key = "dataset/unit-006/id-id"
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
        "order": 6,
        "source_local_id": "chapter1.tex:436-506",
        "titles": [
            {"language": "zh-Hans", "text": "第一章：集合论；Grothendieck 宇宙"},
            {"language": "id-ID", "text": "Bab 1: Teori Himpunan; Semesta Grothendieck"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, 436, 506),
        "target_binding": binding(TARGET, 436, 506),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/define-grothendieck-universes-u-sets-and-u-small-sets",
            "outcome/derive-the-standard-closure-properties-of-a-grothendieck-universe",
            "outcome/explain-the-grothendieck-universe-hypothesis-and-its-purpose",
            "outcome/construct-the-cumulative-hierarchy-by-transfinite-recursion",
            "outcome/prove-that-every-set-belongs-to-some-cumulative-hierarchy-stage",
            "outcome/distinguish-hereditarily-finite-sets-and-the-books-universe-definition",
            "outcome/characterize-universes-by-strongly-inaccessible-cardinals",
            "outcome/interpret-v-kappa-as-a-zfc-model-and-assess-the-assumptions-strength",
        ],
        "surface_counts": {
            "sections": 5,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 3,
            "diagrams": 0,
            "index_entries": 4,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = []
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
