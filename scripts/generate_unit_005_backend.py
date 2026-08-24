#!/usr/bin/env python3
"""Generate the canonical Unit 005 backend record from reviewed live inputs."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend" / "data" / "unit-004-bab-1-rekursi-transfinit-dan-penerapannya.json"
OUTPUT = ROOT / "backend" / "data" / "unit-005-bab-1-kardinal.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter1.tex"
TARGET = "repo/source/chapter1.tex"
DRIVER = "repo/source/unit-005-bab-1-kardinal.tex"
SUMMARY = "qa/unit-005-evidence/build-log-summary.txt"
EQUATION_MAP = "qa/unit-005-evidence/equation-number-map.txt"
ADMISSION = "qa/UNIT_005_ADMISSION_20260822.md"
CORRECTION_RECEIPT = "qa/UNIT_005_EQUATION_NUMBER_REPAIR_20260823.md"
FINAL_LOG = "qa/UNIT_005_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-005-bab-1-kardinal.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
ARTIFACT_ID = (
    128554,
    "205359b6c3b406a4f6595908381147e2bb3dba6aab8fdc9057436b11bec252de",
)
FINAL_LOG_ID = (
    87110,
    "2de97988ca56557b50822f4fbaef60784fbc21b7c3b32d184eab87236c058748",
)
PAGE_COUNT = 12
EQUATION_LABEL_SEQUENCE = (
    "eqn:infinity-axiom",
    "eqn:cardinal-infinite-sum",
    "eqn:cardinal-infinite-prod",
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


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), sha256(payload)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 005 backend refused: identity drift for {relative}")


def equation_labels_through(relative: str, line_end: int) -> tuple[str, ...]:
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    return tuple(
        re.findall(r"\\label\{(eqn:[^}]+)\}", "\n".join(lines[:line_end]))
    )


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
        raise SystemExit(
            "Unit 005 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 005 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate() -> None:
    require_identity(ARTIFACT, ARTIFACT_ID)
    require_identity(FINAL_LOG, FINAL_LOG_ID)

    for relative in (SOURCE, TARGET):
        if equation_labels_through(relative, 434) != EQUATION_LABEL_SEQUENCE:
            raise SystemExit(
                f"Unit 005 backend refused: Chapter 1 equation-label order drift in {relative}"
            )

    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    counter_map = re.compile(
        r"\\setcounter\{section\}\{3\}\s*"
        r"\\setcounter\{equation\}\{1\}\s*"
        r"\\InputSourceLineRange\{chapter1\.tex\}\{289\}\{434\}"
    )
    if counter_map.search(driver) is None:
        raise SystemExit(
            "Unit 005 backend refused: standalone Chapter 1 equation offset drift"
        )

    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(
        r"Output written on .*?\(([\d\s]+) pages?\)\.", final_log, re.DOTALL
    )
    if not log_pages or int(re.sub(r"\s+", "", log_pages[-1])) != PAGE_COUNT:
        raise SystemExit("Unit 005 backend refused: final build-log page count drift")
    if pdfinfo_page_count() != PAGE_COUNT:
        raise SystemExit("Unit 005 backend refused: live PDF page count drift")

    extracted = subprocess.run(
        ["pdftotext", "-layout", str(ROOT / ARTIFACT), "-"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if extracted.returncode or "(1.2)" not in extracted.stdout or "(1.3)" not in extracted.stdout:
        raise SystemExit("Unit 005 backend refused: rendered equation-number map drift")

    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    equation_map = (ROOT / EQUATION_MAP).read_text(encoding="utf-8")
    admission = (ROOT / ADMISSION).read_text(encoding="utf-8")
    repair = (ROOT / CORRECTION_RECEIPT).read_text(encoding="utf-8")
    for needle in (
        f"PDF pages: {PAGE_COUNT}",
        f"Functional replay: {PAGE_COUNT}/{PAGE_COUNT} Poppler pages and {PAGE_COUNT}/{PAGE_COUNT} MuPDF pages pixel-identical",
        "Final-log blockers: zero",
        f"Visual QA: all {PAGE_COUNT} pages inspected in Poppler and MuPDF",
        "eqn:cardinal-infinite-sum` is (1.2)",
        "eqn:cardinal-infinite-prod` is (1.3)",
    ):
        if needle not in summary:
            raise SystemExit(f"Unit 005 backend refused: summary lacks {needle!r}")
    for needle in (
        r"\newlabel{eqn:cardinal-infinite-sum}{{1.2}{2}",
        r"\newlabel{eqn:cardinal-infinite-prod}{{1.3}{2}",
        "eqn:infinity-axiom = (1.1)",
    ):
        if needle not in equation_map:
            raise SystemExit(f"Unit 005 backend refused: equation map lacks {needle!r}")
    for needle in (
        "O013-LI-U005-READER-COR-001",
        "Status: admitted",
        ARTIFACT_ID[1],
        FINAL_LOG_ID[1],
        MODEL,
        "`eqn:cardinal-infinite-sum` prints as (1.2)",
        "`eqn:cardinal-infinite-prod` prints as (1.3)",
    ):
        if needle not in admission or needle not in repair:
            raise SystemExit(
                f"Unit 005 backend refused: admission/repair evidence lacks {needle!r}"
            )


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))

    def identifier(stable_key: str) -> str:
        return "urn:uuid:" + str(uuid.uuid5(namespace, stable_key))

    unit_key = "unit/bab-1-kardinal"
    unit_id = identifier(unit_key)

    concept_specs = [
        ("concept/equipollence", "等势", "ekuipotensi"),
        ("concept/schroeder-bernstein-theorem", "Schröder--Bernstein 定理", "teorema Schröder--Bernstein"),
        ("concept/cardinal-arithmetic", "基数算术", "aritmetika kardinal"),
        ("concept/infinite-cardinal-sum-and-product", "无穷基数和与积", "jumlah dan hasil kali kardinal tak hingga"),
        ("concept/cantor-theorem", "Cantor 定理", "teorema Cantor"),
        ("concept/cardinal-as-initial-ordinal", "作为初始序数的基数", "kardinal sebagai ordinal awal"),
        ("concept/countable-and-uncountable-sets", "可数集与不可数集", "himpunan terhitung dan tak terhitung"),
        ("concept/cardinal-supremum", "基数上确界", "supremum kardinal"),
        ("concept/aleph-hierarchy", "aleph 数层级", "hierarki bilangan alef"),
        ("concept/continuum", "连续统", "kontinuum"),
        ("concept/continuum-hypothesis", "连续统假设", "hipotesis kontinuum"),
        ("concept/continuum-hypothesis-independence", "连续统假设的独立性", "independensi hipotesis kontinuum"),
        ("concept/canonical-well-order-on-ordinal-pairs", "序数对上的典范良序", "urutan baik kanonik pada pasangan ordinal"),
        ("concept/infinite-cardinal-arithmetic", "无穷基数算术", "aritmetika kardinal tak hingga"),
        ("concept/regular-cardinal", "正则基数", "kardinal reguler"),
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
            "equipollence-and-schroeder-bernstein",
            289,
            317,
            "等势与 Schröder--Bernstein 定理",
            "Ekuipotensi dan Teorema Schröder--Bernstein",
            ["concept/equipollence", "concept/schroeder-bernstein-theorem"],
        ),
        (
            "cardinal-arithmetic-and-cantor",
            319,
            342,
            "基数运算与 Cantor 定理",
            "Aritmetika Kardinal dan Teorema Cantor",
            [
                "concept/cardinal-arithmetic",
                "concept/infinite-cardinal-sum-and-product",
                "concept/cantor-theorem",
            ],
        ),
        (
            "cardinal-representatives-and-alephs",
            344,
            371,
            "基数代表与 aleph 数",
            "Wakil Kardinal dan Bilangan Alef",
            [
                "concept/cardinal-as-initial-ordinal",
                "concept/countable-and-uncountable-sets",
                "concept/cardinal-supremum",
                "concept/aleph-hierarchy",
            ],
        ),
        (
            "continuum-and-continuum-hypothesis",
            373,
            379,
            "连续统与连续统假设",
            "Kontinuum dan Hipotesis Kontinuum",
            [
                "concept/continuum",
                "concept/continuum-hypothesis",
                "concept/continuum-hypothesis-independence",
            ],
        ),
        (
            "canonical-well-order-and-infinite-cardinal-arithmetic",
            381,
            427,
            "典范良序与无穷基数算术",
            "Urutan Baik Kanonik dan Aritmetika Kardinal Tak Hingga",
            [
                "concept/canonical-well-order-on-ordinal-pairs",
                "concept/infinite-cardinal-arithmetic",
            ],
        ),
        (
            "regular-cardinals",
            429,
            434,
            "正则基数",
            "Kardinal Reguler",
            ["concept/regular-cardinal"],
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
    citation_key = "citation/je03"
    citations = [
        {
            "id": identifier(citation_key),
            "stable_key": citation_key,
            "entity_type": "citation",
            "bib_key": "Je03",
            "bibliography_path": bibliography["path"],
            "bibliography_sha256": bibliography["sha256"],
            "source_line": 333,
            "target_line": 333,
            "section_id": section_by_slug["cardinal-arithmetic-and-cantor"]["id"],
        }
    ]

    index_specs = [
        (
            "equipollence",
            292,
            "dengshi@等势 (equipollence)",
            "ekuipotensi@ekuipotensi (equipollence)",
            "equipollence-and-schroeder-bernstein",
        ),
        (
            "cardinal",
            344,
            "jishu@基数 (cardinal)",
            "bilangan kardinal@bilangan kardinal (cardinal)",
            "cardinal-representatives-and-alephs",
        ),
        (
            "countable-set",
            356,
            "keshuji@可数集 (countable set)",
            "himpunan terhitung@himpunan terhitung (countable set)",
            "cardinal-representatives-and-alephs",
        ),
        (
            "aleph-symbol",
            365,
            "aleph@$\\aleph_\\alpha$",
            "aleph@$\\aleph_\\alpha$",
            "cardinal-representatives-and-alephs",
        ),
        (
            "regular-cardinal",
            429,
            "jishu!正则基数 (regular cardinal)",
            "kardinal!kardinal reguler (regular cardinal)",
            "regular-cardinals",
        ),
    ]
    index_entries = []
    for ordinal, (slug, line, source_key, target_key, section_slug) in enumerate(index_specs, start=1):
        stable_key = f"index-entry/unit-005/{slug}"
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

    diagram_specs = [
        ("aleph-zero-square-enumeration", 1, 395, 402),
        ("aleph-zero-square-axes", 2, 403, 406),
    ]
    diagrams = []
    diagram_section_id = section_by_slug["canonical-well-order-and-infinite-cardinal-arithmetic"]["id"]
    for ordinal, (slug, occurrence, line_start, line_end) in enumerate(diagram_specs, start=1):
        stable_key = f"diagram/{slug}"
        diagrams.append(
            {
                "id": identifier(stable_key),
                "stable_key": stable_key,
                "entity_type": "diagram",
                "section_id": diagram_section_id,
                "ordinal_in_unit": ordinal,
                "source_format": "tikzpicture",
                "source_occurrence_index": occurrence,
                "source_binding": binding(SOURCE, line_start, line_end),
                "target_binding": binding(TARGET, line_start, line_end),
                "rights_component_id": rights_by_key["rights/principal-cc-by-4.0"],
                "state": "audited_preserved",
            }
        )

    build_key = "build-surface/unit-005-pdf"
    build_surface = {
        "id": identifier(build_key),
        "stable_key": build_key,
        "entity_type": "build_surface",
        "unit_id": unit_id,
        "kind": "pdf",
        "working_directory": ".",
        "command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_unit_005.ps1 -OutputDirectory build/unit-005-replay",
        "artifact_path": ARTIFACT,
        "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(SUMMARY),
        "build_script": binding("scripts/build_unit_005.ps1"),
        "page_count": PAGE_COUNT,
        "status": "pass",
        "driver": binding(DRIVER),
        "input_bindings": [
            binding("repo/source/coverpage-id-unit-005.tex"),
            binding("repo/source/font-setup-id.tex"),
            binding("repo/source/AJbook.cls"),
            binding("repo/source/titles-setup-id.tex"),
            binding("repo/source/locale-ui-id.tex"),
            binding("repo/source/titles-setup.tex"),
            binding("repo/source/mycommand.sty"),
            binding("repo/source/myarrows.sty"),
            bibliography,
            binding("repo/source/ccby.png"),
            binding("repo/source/unit-005-crossrefs.aux"),
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
            "packages loaded by unit-005-bab-1-kardinal.tex and AJbook.cls",
        ],
        "rights_component_ids": unit_rights,
    }

    qa_key = "qa/unit-005/admission-gate"
    qa_event = {
        "id": identifier(qa_key),
        "stable_key": qa_key,
        "entity_type": "qa_event",
        "unit_id": unit_id,
        "check_type": "admission_gate",
        "result": "pass",
        "scope": "Complete source-order translation and independent audit for chapter1.tex lines 289-434; documented correction O013-LI-U005-COR-001 repairing the reversed Gödel/Cohen attribution at line 379; documented clarification O013-LI-U005-CLR-001 making the composed injection explicit at line 304; documented reader correction O013-LI-U005-READER-COR-001 restoring source-order equation numbers (1.2) and (1.3); schema and stable-ID integrity; live inclusive line-span hashes; one unique citation; ten preserved labels; six protected reference occurrences over five unique keys, comprising four internal occurrences over three keys and two frozen external references; five brace-aware index entries (four default and one sym1); two source-preserved TikZ pictures; zero exercises, hints, answers, or solutions; localized Indonesian reader interface; 12-page standalone digital reflow; two clean builds; structural PDF checks; and all-page MuPDF and Poppler visual inspection. Production provenance records " + MODEL + " separately from source authorship and human credit.",
        "witness": ADMISSION,
        "translation_audit_state": "pass",
        "build_state": "pass",
        "visual_state": "pass",
        "witness_binding": binding(ADMISSION),
    }

    dataset_key = "dataset/unit-005/id-id"
    data["dataset_stable_key"] = dataset_key
    data["dataset_id"] = identifier(dataset_key)
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-23",
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
        "order": 5,
        "source_local_id": "chapter1.tex:289-434",
        "titles": [
            {"language": "zh-Hans", "text": "第一章：集合论；基数"},
            {"language": "id-ID", "text": "Bab 1: Teori Himpunan; Bilangan Kardinal"},
        ],
        "source_language": "zh-Hans",
        "target_language": "id-ID",
        "source_binding": binding(SOURCE, 289, 434),
        "target_binding": binding(TARGET, 289, 434),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": concept_ids,
        "prerequisite_ids": unit_prerequisites,
        "rights_component_ids": unit_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [build_surface["id"]],
        "qa_event_ids": [qa_event["id"]],
        "outcome_keys": [
            "outcome/compare-cardinalities-with-injections-and-bijections",
            "outcome/apply-schroeder-bernstein-and-cantor-theorems",
            "outcome/compute-cardinal-sums-products-and-powers",
            "outcome/represent-cardinals-by-initial-ordinals-and-alephs",
            "outcome/explain-the-continuum-hypothesis-and-its-independence",
            "outcome/use-canonical-well-orders-in-infinite-cardinal-arithmetic",
            "outcome/recognize-regular-and-singular-cardinal-behavior",
        ],
        "surface_counts": {
            "sections": 6,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 1,
            "diagrams": 2,
            "index_entries": 5,
        },
        "translation_state": "visually_checked",
        "admission_state": "admitted",
    }
    data["sections"] = sections
    data["concepts"] = concepts
    data["citations"] = citations
    data["diagrams"] = diagrams
    data["index_entries"] = index_entries
    data["build_surfaces"] = [build_surface]
    data["qa_events"] = [qa_event]

    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
