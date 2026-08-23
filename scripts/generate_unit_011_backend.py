#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 011."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

import generate_unit_009_backend as base

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "backend/data/unit-010-bab-2-fungtor-dan-transformasi-natural.json"
OUTPUT = ROOT / "backend/data/unit-011-bab-2-kategori-fungtor.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-011-bab-2-kategori-fungtor.tex"
COVER = "repo/source/coverpage-id-unit-011.tex"
CROSSREF = "repo/source/unit-011-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_011.ps1"
STRUCTURE_GATE = "scripts/check_unit_011_structure.py"
SUMMARY = "qa/unit-011-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_011_ADMISSION_20260823.md"
FINAL_LOG = "qa/UNIT_011_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-011-bab-2-kategori-fungtor.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 468, 563
SOURCE_FULL = (139983, "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840")
SOURCE_SPAN = (6733, "892e22da2db9e269a7bacf112e82e7795a4c4b3a7d38d34212e569470696b4ad")
TARGET_SPAN = (8004, "a848cb6d7dfdd7edc1f5b07be14f421ed075a8124723ab9b73a207f86216e105")
ARTIFACT_ID = (105391, "f18ea37d945b08961f14e49581dd13a5a3024307fe3d33a77c7d5bb5631859fe")
FINAL_LOG_ID = (85824, "873f96fdb5ac604e23ed5f1ab6955ba2d4deca869bd433c1bc6b9d11907ef78a")
LABELS = ("sec:functor-category", "eg:Hom-functor", "prop:op-functor-cat", "def:cat-center")
EXTERNAL_REFS = (
    ("con:U-small", "2.1.{4}", "3"),
    ("eg:categories", "2.1.{5}", "3"),
    ("rem:op-functor", "2.2.{2}", "1"),
    ("eqn:naturaltrans-def", "2.1", "3"),
    ("con:naturaltrans-morphism", "2.2.{6}", "3"),
    ("prop:naturaltrans-associativity", "2.2.{7}", "4"),
)
INDEX_SLUGS = (
    "product-coproduct", "pullback", "pushforward", "hom-symbol",
    "functor-category", "functor-category-symbol", "category-center", "center",
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def span(relative: str) -> bytes:
    return base.normalized_span(relative, START, END)


def require_identity(relative: str, expected: tuple[int, str]) -> None:
    if not (ROOT / relative).is_file() or identity(relative) != expected:
        raise SystemExit(f"Unit 011 backend refused: identity drift for {relative}")


def gate() -> None:
    require_identity(SOURCE, SOURCE_FULL)
    require_identity(FINAL_LOG, FINAL_LOG_ID)
    require_identity(ARTIFACT, ARTIFACT_ID)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 011 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 011 backend refused: target span drift")
    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 011 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass", "mathematics_source_count": 102,
        "mathematics_target_count": 102, "environment_sequence_exact": True,
        "han_residue_count": 0, "target_sha256": TARGET_SPAN[1],
    }
    if any(report.get(k) != v for k, v in required.items()):
        raise SystemExit("Unit 011 backend refused: structural evidence drift")
    source, target = span(SOURCE).decode(), span(TARGET).decode()
    for text in (source, target):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit("Unit 011 backend refused: label drift")
        if len(base.index_occurrences(text)) != 8:
            raise SystemExit("Unit 011 backend refused: index drift")
        if len(base.diagram_occurrences(text)) != 1:
            raise SystemExit("Unit 011 backend refused: diagram drift")
    aux = tuple(
        line.strip() for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.startswith(r"\newlabel{")
    )
    wanted = tuple(
        r"\newlabel{" + key + "}{{" + number + "}{" + page + "}}"
        for key, number, page in EXTERNAL_REFS
    )
    if aux != wanted:
        raise SystemExit("Unit 011 backend refused: external-reference drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    receipt = (ROOT / ADMISSION).read_text(encoding="utf-8")
    for needle in ("PDF pages: 7", "Functional replay: 7/7", "Final-log blockers: zero", "Visual QA: all 7 pages inspected"):
        if needle not in summary:
            raise SystemExit(f"Unit 011 backend refused: summary lacks {needle!r}")
    for needle in ("Status: admitted locally", "chapter2.tex:468-563", TARGET_SPAN[1], ARTIFACT_ID[1], FINAL_LOG_ID[1], MODEL, "Wen-Wei Li", "CC BY 4.0", "CC BY-SA 3.0", "OFL 1.1", "non-endorsed derivative"):
        if needle not in receipt:
            raise SystemExit(f"Unit 011 backend refused: admission lacks {needle!r}")


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-2-kategori-fungtor"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/kategori-fungtor"
    section_id = uid(section_key)
    bind = base.binding

    concept_specs = [
        ("concept/product-category", "积范畴", "kategori produk"),
        ("concept/coproduct-category", "余积范畴", "kategori koproduk"),
        ("concept/bifunctor", "二元函子", "fungtor biner"),
        ("concept/multivariable-functor", "多元函子", "fungtor banyak peubah"),
        ("concept/hom-bifunctor", "Hom 函子", "fungtor Hom"),
        ("concept/pullback", "拉回", "tarik balik"),
        ("concept/pushforward", "推出", "dorong maju"),
        ("concept/functor-category", "函子范畴", "kategori fungtor"),
        ("concept/opposite-functor-category", "反范畴函子范畴", "kategori fungtor lawan"),
        ("concept/category-center", "范畴中心", "pusat kategori"),
        ("concept/natural-transformation", "自然变换", "transformasi natural"),
        ("concept/endomorphism-monoid", "自同态幺半群", "monoid endomorfisme"),
        ("concept/automorphism-group", "自同构群", "grup automorfisme"),
        ("concept/center-invariant", "中心不变量", "invarian pusat"),
    ]
    for label in LABELS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-011/label/{slug}", f"标签 {label}", f"label {label}"))
    for label, _number, _page in EXTERNAL_REFS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-011/reference/{slug}", f"外部引用 {label}", f"rujukan eksternal {label}"))
    concepts = [{"id": uid(k), "stable_key": k, "entity_type": "concept", "labels": [{"language": "zh-Hans", "text": zh}, {"language": "id-ID", "text": idt}]} for k, zh, idt in concept_specs]
    concept_ids = [x["id"] for x in concepts]

    rights_map = {x["stable_key"]: x["id"] for x in data["rights"]}
    principal = rights_map["rights/principal-cc-by-4.0"]
    unit_rights = [principal, rights_map["rights/ajbook-fragment-cc-by-sa-3.0"], rights_map["rights/noto-fonts-ofl-1.1"]]
    prerequisite_ids = [x["id"] for x in data["prerequisites"]]
    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section", "parent_id": unit_id, "order": 1,
        "source_local_id": "chapter2.tex:468-563",
        "titles": [{"language": "zh-Hans", "text": "2.3 函子范畴"}, {"language": "id-ID", "text": "2.3 Kategori Fungtor"}],
        "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END),
        "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": [principal],
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    source_indexes = base.index_occurrences(span(SOURCE).decode())
    target_indexes = base.index_occurrences(span(TARGET).decode())
    index_entries = []
    for n, (slug, s, t) in enumerate(zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1):
        if (s[0], s[2]) != (t[0], t[2]):
            raise SystemExit("Unit 011 backend refused: index topology mismatch")
        key = f"index-entry/unit-011/{slug}"
        index_entries.append({"id": uid(key), "stable_key": key, "entity_type": "index_entry", "section_id": section_id, "ordinal_in_unit": n, "source_key": s[1], "target_key": t[1], "source_binding": bind(SOURCE, s[2], s[2]), "target_binding": bind(TARGET, t[2], t[2]), "provenance_state": "source_key_preserved_target_key_localized"})
    diagrams = []
    for n, (fmt, occ, first, last) in enumerate(base.diagram_occurrences(span(SOURCE).decode()), 1):
        key = "diagram/unit-011/center-naturality-square"
        diagrams.append({"id": uid(key), "stable_key": key, "entity_type": "diagram", "section_id": section_id, "ordinal_in_unit": n, "source_format": fmt, "source_occurrence_index": occ, "source_binding": bind(SOURCE, first, last), "target_binding": bind(TARGET, first, last), "rights_component_id": principal, "state": "audited_preserved"})
    build_key = "build-surface/unit-011-pdf"
    inputs = [COVER, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls", "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex", "repo/source/titles-setup.tex", "repo/source/mycommand.sty", "repo/source/myarrows.sty", "repo/source/Al-jabr.bib", "repo/source/ccby.png", CROSSREF, "repo/fonts/NotoSansCJKsc-Black.otf", "repo/fonts/NotoSansCJKsc-Medium.otf", "repo/fonts/NotoSansCJKsc-Regular.otf", "repo/fonts/NotoSerifCJKsc-Bold.otf"]
    build = {"id": uid(build_key), "stable_key": build_key, "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf", "working_directory": ".", "command": "pwsh -NoProfile -File scripts/build_unit_011.ps1 -OutputDirectory build/unit-011-replay-id", "artifact_path": ARTIFACT, "artifact_binding": bind(ARTIFACT), "log_binding": bind(FINAL_LOG), "build_script": bind(BUILD_SCRIPT), "page_count": 7, "status": "pass", "driver": bind(DRIVER), "input_bindings": [bind(x) for x in inputs], "external_dependencies": ["XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)", "Fandol fonts from TeX distribution", "TeX Gyre Heros", "packages loaded by the Unit 011 driver and AJbook.cls"], "rights_component_ids": unit_rights}
    qa_key = "qa/unit-011/admission-gate"
    qa = {"id": uid(qa_key), "stable_key": qa_key, "entity_type": "qa_event", "unit_id": unit_id, "check_type": "admission_gate", "result": "pass", "scope": "Complete source-order translation and semantic review of chapter2.tex lines 468-563; 102 exact normalized mathematics surfaces, 17 balanced environments, four labels, five ordinary references, one equation reference, eight index entries, four TikZ-CD arrows, no exercises/hints/answers/solutions, frozen external references, separate component rights, two-build functional replay, PDF checks, and all-page visual QA. Production provenance records " + MODEL + " separately from source authorship and human credit.", "witness": ADMISSION, "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass", "witness_binding": bind(ADMISSION)}
    dataset_key = "dataset/unit-011/id-id"
    data["dataset_stable_key"] = dataset_key; data["dataset_id"] = uid(dataset_key)
    data["workflow"] = {"responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9", "updated": "2026-08-23", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_backend_build_visual_pass"}
    unit = {"id": unit_id, "stable_key": unit_key, "entity_type": "unit", "program_id": data["program"]["id"], "course_id": data["course"]["id"], "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"], "order": 11, "source_local_id": "chapter2.tex:468-563", "titles": [{"language": "zh-Hans", "text": "第二章：范畴论基础；函子范畴"}, {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Kategori Fungtor"}], "source_language": "zh-Hans", "target_language": "id-ID", "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END), "section_ids": [section_id], "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights, "citation_ids": [], "diagram_ids": [x["id"] for x in diagrams], "index_entry_ids": [x["id"] for x in index_entries], "build_surface_ids": [build["id"]], "qa_event_ids": [qa["id"]], "outcome_keys": ["outcome/construct-product-and-coproduct-categories", "outcome/construct-bifunctors-and-hom-bifunctors", "outcome/define-functor-categories", "outcome/dualize-functor-categories", "outcome/identify-the-category-center"], "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 0, "diagrams": len(diagrams), "index_entries": len(index_entries)}, "translation_state": "visually_checked", "admission_state": "admitted"}
    data["unit"] = unit; data["sections"] = [section]; data["concepts"] = concepts; data["citations"] = []; data["diagrams"] = diagrams; data["index_entries"] = index_entries; data["build_surfaces"] = [build]; data["qa_events"] = [qa]
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_backend.py"), "--lane-root", str(ROOT), "--data", str(OUTPUT), "--schema", str(ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"), "--csv-dir", str(ROOT / "backend/csv"), "--write-csv"], cwd=ROOT, check=True)
    print(json.dumps({"path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"), "bytes": OUTPUT.stat().st_size, "sha256": digest(OUTPUT.read_bytes()), "entities": 1 + 1 + 1 + 1 + 1 + len(data["sections"]) + len(concepts) + len(data["prerequisites"]) + len(data["rights"]) + len(data["citations"]) + len(diagrams) + len(index_entries) + len(data["build_surfaces"]) + len(data["qa_events"]), "concepts": len(concepts), "diagrams": len(diagrams), "index_entries": len(index_entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
