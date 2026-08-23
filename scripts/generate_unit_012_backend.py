#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 012."""

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
OUTPUT = ROOT / "backend/data/unit-012-bab-2-sifat-universal-dan-kategori-koma.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-012-bab-2-sifat-universal-dan-kategori-koma.tex"
COVER = "repo/source/coverpage-id-unit-012.tex"
CROSSREF = "repo/source/unit-012-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_012.ps1"
STRUCTURE_GATE = "scripts/check_unit_012_structure.py"
SUMMARY = "qa/unit-012-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_012_ADMISSION_20260823.md"
FINAL_LOG = "qa/UNIT_012_BUILD_FINAL.log"
ARTIFACT = "artifacts/unit-012-bab-2-sifat-universal-dan-kategori-koma.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 564, 677
SOURCE_FULL = (139983, "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840")
SOURCE_SPAN = (9095, "b9c84bf31468f78576a80b096871d72fd6d109742b2f816c36724cac467f1239")
TARGET_SPAN = (11056, "26a2e9a638fae91a1108c9a263a89b64b71ba5d351cae1bfae72eef6eba0649b")
ARTIFACT_ID = (121388, "1671beea4ab78c848d577f9b8428d5717de2ac55f309f4f075c455409fd878a9")
FINAL_LOG_ID = (85731, "1a0c18fa6efa5078e35c6bf9c42785888c57a209e0148b928773105f1ec55f7c")
LABELS = (
    "sec:cat-universals", "def:universal-objects", "prop:initial-obj-uniqueness",
    "def:zero-morphism", "eg:free-vectorspace", "eg:metric-completion",
    "def:comma-category",
)
EXTERNAL_REFS = (
    ("eg:functors", "2.2.{4}", "1"),
    ("eg:categories", "2.1.{5}", "3"),
    ("sec:free-group", "4.8", "130"),
)
INDEX_SLUGS = (
    "initial-terminal-zero-objects", "zero-morphism", "universal-property",
    "comma-category", "comma-category-symbol", "object-symbol",
)
EXPECTED_CITATIONS = (("Xiong", 624),)


def diagram_blocks(text: str) -> tuple[tuple[str, int, str], ...]:
    """Return whitespace-normalized diagram blocks in source order."""
    pattern = re.compile(r"\\begin\{(tikzcd|tikzpicture)\}.*?\\end\{\1\}", re.DOTALL)
    return tuple(
        (match.group(1), ordinal, re.sub(r"\s+", "", match.group(0)))
        for ordinal, match in enumerate(pattern.finditer(text), 1)
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
        raise SystemExit(f"Unit 012 backend refused: identity drift for {relative}")


def gate() -> None:
    # Pin the shared occurrence parser to this unit before checking any
    # line-bearing labels, citations, indexes, or diagrams.
    base.SPAN_START = START
    base.SPAN_END = END
    require_identity(SOURCE, SOURCE_FULL)
    if ARTIFACT_ID is None or FINAL_LOG_ID is None:
        raise SystemExit(
            "Unit 012 backend scaffold is ready but admission is intentionally gated: "
            "record the final PDF/log byte identities after visual QA, then fill ARTIFACT_ID and FINAL_LOG_ID."
        )
    require_identity(FINAL_LOG, FINAL_LOG_ID)
    require_identity(ARTIFACT, ARTIFACT_ID)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 012 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 012 backend refused: target span drift")
    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 012 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass", "mathematics_source_count": 159,
        "mathematics_target_count": 159, "environment_sequence_exact": True,
        "han_residue_count": 0, "target_sha256": TARGET_SPAN[1],
    }
    if any(report.get(k) != v for k, v in required.items()):
        raise SystemExit("Unit 012 backend refused: structural evidence drift")
    source, target = span(SOURCE).decode(), span(TARGET).decode()
    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if [(x[0], x[1]) for x in source_diagrams] != [(x[0], x[1]) for x in target_diagrams]:
        raise SystemExit("Unit 012 backend refused: diagram order/format drift")
    if diagram_blocks(source) != diagram_blocks(target):
        raise SystemExit("Unit 012 backend refused: normalized diagram content drift")
    for text in (source, target):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit("Unit 012 backend refused: label drift")
        if len(base.index_occurrences(text)) != 6:
            raise SystemExit("Unit 012 backend refused: index drift")
        if len(base.diagram_occurrences(text)) != 8:
            raise SystemExit("Unit 012 backend refused: diagram drift")
        if base.citation_occurrences(text) != EXPECTED_CITATIONS:
            raise SystemExit("Unit 012 backend refused: citation topology drift")
    aux_lines = {
        match.group(1): line.strip()
        for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if (match := re.match(r"\\newlabel\{([^}]+)\}", line))
    }
    wanted = {
        key: r"\newlabel{" + key + "}{{" + number + "}{" + page + "}}"
        for key, number, page in EXTERNAL_REFS
    }
    if any(aux_lines.get(key) != line for key, line in wanted.items()):
        raise SystemExit("Unit 012 backend refused: external-reference drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    receipt = (ROOT / ADMISSION).read_text(encoding="utf-8")
    for needle in ("PDF pages: 10", "Functional replay: 10/10", "Final-log blockers: zero", "Visual QA: all 10 pages inspected"):
        if needle not in summary:
            raise SystemExit(f"Unit 012 backend refused: summary lacks {needle!r}")
    for needle in ("Status: admitted locally", "chapter2.tex:564-677", TARGET_SPAN[1], ARTIFACT_ID[1], FINAL_LOG_ID[1], MODEL, "Wen-Wei Li", "CC BY 4.0", "CC BY-SA 3.0", "OFL 1.1", "non-endorsed derivative"):
        if needle not in receipt:
            raise SystemExit(f"Unit 012 backend refused: admission lacks {needle!r}")


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-2-sifat-universal-dan-kategori-koma"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/sifat-universal-dan-kategori-koma"
    section_id = uid(section_key)
    bind = base.binding

    source_citation_occurrences = base.citation_occurrences(span(SOURCE).decode())
    target_citation_occurrences = base.citation_occurrences(span(TARGET).decode())
    if source_citation_occurrences != EXPECTED_CITATIONS:
        raise SystemExit("Unit 012 backend refused: source citation identity drift")
    if tuple(name for name, _line in target_citation_occurrences) != tuple(name for name, _line in source_citation_occurrences):
        raise SystemExit("Unit 012 backend refused: target citation identity drift")

    concept_specs = [
        ("concept/initial-object", "始对象", "objek awal"),
        ("concept/terminal-object", "终对象", "objek terminal"),
        ("concept/zero-object", "零对象", "objek nol"),
        ("concept/zero-morphism", "零态射", "morfisme nol"),
        ("concept/universal-property", "泛性质", "sifat universal"),
        ("concept/free-vector-space", "自由向量空间", "ruang vektor bebas"),
        ("concept/metric-space", "度量空间", "ruang metrik"),
        ("concept/isometry", "保距映射", "pemetaan pelestari jarak"),
        ("concept/metric-completion", "完备化", "pelengkapan"),
        ("concept/comma-category", "逗号范畴", "kategori koma"),
        ("concept/projection-functor", "投影函子", "fungtor proyeksi"),
        ("concept/fiber", "纤维", "serat"),
        ("concept/slice-category", "切片范畴", "kategori slice"),
        ("concept/coslice-category", "余切片范畴", "kategori koslice"),
        ("concept/arrow-category", "箭头范畴", "kategori panah"),
        ("concept/representable-functor", "可表函子", "fungtor representabel"),
        ("concept/adjoint-functor", "伴随函子", "fungtor adjoin"),
    ]
    for label in LABELS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-012/label/{slug}", f"标签 {label}", f"label {label}"))
    for label, _number, _page in EXTERNAL_REFS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-012/reference/{slug}", f"外部引用 {label}", f"rujukan eksternal {label}"))
    concepts = [{"id": uid(k), "stable_key": k, "entity_type": "concept", "labels": [{"language": "zh-Hans", "text": zh}, {"language": "id-ID", "text": idt}]} for k, zh, idt in concept_specs]
    concept_ids = [x["id"] for x in concepts]

    rights_map = {x["stable_key"]: x["id"] for x in data["rights"]}
    principal = rights_map["rights/principal-cc-by-4.0"]
    unit_rights = [principal, rights_map["rights/ajbook-fragment-cc-by-sa-3.0"], rights_map["rights/noto-fonts-ofl-1.1"]]
    prerequisite_ids = [x["id"] for x in data["prerequisites"]]
    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section", "parent_id": unit_id, "order": 1,
        "source_local_id": "chapter2.tex:564-677",
        "titles": [{"language": "zh-Hans", "text": "2.4 泛性质"}, {"language": "id-ID", "text": "2.4 Sifat Universal"}],
        "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END),
        "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": [principal],
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    bib = bind("repo/source/Al-jabr.bib")
    citation_key = f"citation/unit-012/xiong/line-{source_citation_occurrences[0][1]}"
    citations = [{
        "id": uid(citation_key), "stable_key": citation_key, "entity_type": "citation",
        "bib_key": "Xiong", "bibliography_path": bib["path"], "bibliography_sha256": bib["sha256"],
        "source_line": source_citation_occurrences[0][1], "target_line": target_citation_occurrences[0][1], "section_id": section_id,
    }]
    source_indexes = base.index_occurrences(span(SOURCE).decode())
    target_indexes = base.index_occurrences(span(TARGET).decode())
    index_entries = []
    for n, (slug, s, t) in enumerate(zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1):
        if (s[0], s[2]) != (t[0], t[2]):
            raise SystemExit("Unit 012 backend refused: index topology mismatch")
        key = f"index-entry/unit-012/{slug}"
        index_entries.append({"id": uid(key), "stable_key": key, "entity_type": "index_entry", "section_id": section_id, "ordinal_in_unit": n, "source_key": s[1], "target_key": t[1], "source_binding": bind(SOURCE, s[2], s[2]), "target_binding": bind(TARGET, t[2], t[2]), "provenance_state": "source_key_preserved_target_key_localized"})
    diagrams = []
    source_diagrams = base.diagram_occurrences(span(SOURCE).decode())
    target_diagrams = base.diagram_occurrences(span(TARGET).decode())
    for n, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        fmt, occ, source_first, source_last = source_diagram
        target_fmt, target_occ, target_first, target_last = target_diagram
        if (fmt, occ) != (target_fmt, target_occ):
            raise SystemExit("Unit 012 backend refused: diagram binding drift")
        key = f"diagram/unit-012/{fmt}-{occ}"
        diagrams.append({"id": uid(key), "stable_key": key, "entity_type": "diagram", "section_id": section_id, "ordinal_in_unit": n, "source_format": fmt, "source_occurrence_index": occ, "source_binding": bind(SOURCE, source_first, source_last), "target_binding": bind(TARGET, target_first, target_last), "rights_component_id": principal, "state": "audited_preserved"})
    build_key = "build-surface/unit-012-pdf"
    inputs = [COVER, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls", "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex", "repo/source/titles-setup.tex", "repo/source/mycommand.sty", "repo/source/myarrows.sty", "repo/source/Al-jabr.bib", "repo/source/ccby.png", CROSSREF, "repo/fonts/NotoSansCJKsc-Black.otf", "repo/fonts/NotoSansCJKsc-Medium.otf", "repo/fonts/NotoSansCJKsc-Regular.otf", "repo/fonts/NotoSerifCJKsc-Bold.otf"]
    build = {"id": uid(build_key), "stable_key": build_key, "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf", "working_directory": ".", "command": "pwsh -NoProfile -File scripts/build_unit_012.ps1 -OutputDirectory build/unit-012-replay", "artifact_path": ARTIFACT, "artifact_binding": bind(ARTIFACT), "log_binding": bind(FINAL_LOG), "build_script": bind(BUILD_SCRIPT), "page_count": 10, "status": "pass", "driver": bind(DRIVER), "input_bindings": [bind(x) for x in inputs], "external_dependencies": ["XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)", "Fandol fonts from TeX distribution", "TeX Gyre Heros", "packages loaded by the Unit 012 driver and AJbook.cls"], "rights_component_ids": unit_rights}
    qa_key = "qa/unit-012/admission-gate"
    qa = {"id": uid(qa_key), "stable_key": qa_key, "entity_type": "qa_event", "unit_id": unit_id, "check_type": "admission_gate", "result": "pass", "scope": "Complete source-order translation and semantic review of chapter2.tex lines 564-677; 159 exact normalized mathematics surfaces, 20 balanced environments, seven labels, six references, one citation, six index entries, eight TikZ-CD diagrams, no exercises/hints/answers/solutions, frozen external references, separate component rights, four-pass functional replay, PDF checks, and all-page visual QA. Production provenance records " + MODEL + " separately from source authorship and human credit.", "witness": ADMISSION, "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass", "witness_binding": bind(ADMISSION)}
    dataset_key = "dataset/unit-012/id-id"
    data["dataset_stable_key"] = dataset_key; data["dataset_id"] = uid(dataset_key)
    data["workflow"] = {"responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9", "updated": "2026-08-23", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_backend_build_visual_pass"}
    unit = {"id": unit_id, "stable_key": unit_key, "entity_type": "unit", "program_id": data["program"]["id"], "course_id": data["course"]["id"], "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"], "order": 12, "source_local_id": "chapter2.tex:564-677", "titles": [{"language": "zh-Hans", "text": "第二章：范畴论基础；泛性质与逗号范畴"}, {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Sifat Universal dan Kategori Koma"}], "source_language": "zh-Hans", "target_language": "id-ID", "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END), "section_ids": [section_id], "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights, "citation_ids": [x["id"] for x in citations], "diagram_ids": [x["id"] for x in diagrams], "index_entry_ids": [x["id"] for x in index_entries], "build_surface_ids": [build["id"]], "qa_event_ids": [qa["id"]], "outcome_keys": ["outcome/identify-initial-terminal-zero-objects", "outcome/prove-universal-object-uniqueness", "outcome/define-zero-morphisms", "outcome/recognize-universal-properties", "outcome/construct-comma-categories", "outcome/identify-slice-coslice-and-arrow-categories"], "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 1, "diagrams": len(diagrams), "index_entries": len(index_entries)}, "translation_state": "visually_checked", "admission_state": "admitted"}
    data["unit"] = unit; data["sections"] = [section]; data["concepts"] = concepts; data["citations"] = citations; data["diagrams"] = diagrams; data["index_entries"] = index_entries; data["build_surfaces"] = [build]; data["qa_events"] = [qa]
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_backend.py"), "--lane-root", str(ROOT), "--data", str(OUTPUT), "--schema", str(ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"), "--csv-dir", str(ROOT / "backend/csv"), "--write-csv"], cwd=ROOT, check=True)
    print(json.dumps({"path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"), "bytes": OUTPUT.stat().st_size, "sha256": digest(OUTPUT.read_bytes()), "entities": 1 + 1 + 1 + 1 + 1 + len(data["sections"]) + len(concepts) + len(data["prerequisites"]) + len(data["rights"]) + len(data["citations"]) + len(diagrams) + len(index_entries) + len(data["build_surfaces"]) + len(data["qa_events"]), "concepts": len(concepts), "diagrams": len(diagrams), "index_entries": len(index_entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
