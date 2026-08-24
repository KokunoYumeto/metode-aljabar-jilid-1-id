#!/usr/bin/env python3
"""Admission-gated modular backend for Li Volume 1 Unit 013."""

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
OUTPUT = ROOT / "backend/data/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.tex"
COVER = "repo/source/coverpage-id-unit-013.tex"
CROSSREF = "repo/source/unit-013-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_013.ps1"
STRUCTURE_GATE = "scripts/check_unit_013_structure.py"
SUMMARY = "qa/unit-013-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_013_ADMISSION_20260823.md"
CORRECTION_RECEIPT = "qa/UNIT_013_EQUATION_NUMBER_CORRECTION_20260823.md"
FINAL_LOG = "qa/UNIT_013_BUILD_FINAL.log"
FINAL_AUX = "qa/unit-013-evidence/final-label-map.aux"
ARTIFACT = "artifacts/unit-013-bab-2-fungtor-representabel-dan-lema-yoneda.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 678, 765
SOURCE_FULL = (139983, "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840")
SOURCE_SPAN = (7413, "9b30201ad8df7822e2e6bb20080097bff6ef663c763653f859f6ab4e028b2928")
TARGET_SPAN = (8643, "eeb6bbb2aca0ea17277e7afea39492729996cd9d8648deccc94bcebe9111327d")
DRIVER_ID = (4776, "f3a7b9e2351288eaf273930572d564cb8d0011e44441cd22246e8f385985cdf2")
ARTIFACT_ID = (106162, "03ced2b80bf14814d01bc73cf378bfab820ec40ad0571eaa33cf514d79d760cf")
FINAL_LOG_ID = (86834, "605c9d68009fcfa0d9b746864ebad7e1618943932cd6d8cd1140e84fbd657039")
FINAL_AUX_ID = (2078, "1c95b7121342b9d73fa1915a3efe8eab0c4dc19d3a65f5d48903e3fbad301f4f")
CORRECTION_RECEIPT_ID = (3547, "d57a0a20abbf36124489357dd55784f0a169f423a17ad28a30b701d057ee2b22")
PAGE_COUNT = 7
LABELS = (
    "sec:representable-functors", "eqn:Yoneda-cat-duality", "prop:Yoneda-lemma",
    "eqn:Yoneda-map", "def:representable-functor",
    "rem:Yoneda-universal-family", "prop:representable-functor-uniqueness",
)
EXTERNAL_REFS = (
    ("con:U-small", "2.1.{4}", "3"),
    ("eg:Hom-functor", "2.2.{3}", "2"),
    ("prop:op-functor-cat", "2.2.{6}", "3"),
    ("sec:cat-universals", "2.4", "1"),
    ("prop:initial-obj-uniqueness", "2.4.{2}", "1"),
    ("eg:free-vectorspace", "2.4.{5}", "2"),
    ("def:comma-category", "2.4.{7}", "3"),
)
INDEX_SLUGS = (
    "category-wedge-vee-symbol", "presheaf", "yoneda-lemma",
    "representable-functor", "universal-family",
)
EXPECTED_CITATIONS = ()
EQUATION_MAP = (
    ("eqn:Yoneda-cat-duality", "2.3", "1", "equation.2.3"),
    ("eqn:Yoneda-map", "2.4", "1", "equation.2.4"),
)


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
        raise SystemExit(f"Unit 013 backend refused: identity drift for {relative}")


def pdfinfo_page_count() -> int:
    completed = subprocess.run(
        ["pdfinfo", str(ROOT / ARTIFACT)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if completed.returncode:
        raise SystemExit(
            "Unit 013 backend refused: pdfinfo could not inspect the live artifact\n"
            + completed.stderr
        )
    match = re.search(r"^Pages:\s*(\d+)\s*$", completed.stdout, re.MULTILINE)
    if match is None:
        raise SystemExit("Unit 013 backend refused: pdfinfo returned no page count")
    return int(match.group(1))


def gate() -> None:
    # Pin the shared occurrence parser to this unit before checking any
    # line-bearing labels, citations, indexes, or diagrams.
    base.SPAN_START = START
    base.SPAN_END = END
    require_identity(SOURCE, SOURCE_FULL)
    if ARTIFACT_ID is None or FINAL_LOG_ID is None or PAGE_COUNT is None:
        raise SystemExit(
            "Unit 013 backend scaffold is ready but admission is intentionally gated: "
            "record the final PDF/log byte identities and page count after visual QA, "
            "then fill ARTIFACT_ID, FINAL_LOG_ID, and PAGE_COUNT."
        )
    require_identity(DRIVER, DRIVER_ID)
    require_identity(FINAL_LOG, FINAL_LOG_ID)
    require_identity(FINAL_AUX, FINAL_AUX_ID)
    require_identity(ARTIFACT, ARTIFACT_ID)
    require_identity(CORRECTION_RECEIPT, CORRECTION_RECEIPT_ID)
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 013 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 013 backend refused: target span drift")
    driver = (ROOT / DRIVER).read_text(encoding="utf-8")
    equation_counter_gate = re.compile(
        r"\\setcounter\{equation\}\{2\}\s*"
        r"\\InputSourceLineRange\{chapter2\.tex\}\{678\}\{765\}"
    )
    if len(equation_counter_gate.findall(driver)) != 1:
        raise SystemExit("Unit 013 backend refused: standalone equation-counter gate failed")
    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 013 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass", "mathematics_source_count": 98,
        "mathematics_target_count": 98, "environment_sequence_exact": True,
        "mathematics_multiset_equivalent_after_declared_correction": True,
        "han_residue_count": 0, "target_sha256": TARGET_SPAN[1],
    }
    if any(report.get(k) != v for k, v in required.items()):
        raise SystemExit("Unit 013 backend refused: structural evidence drift")
    source, target = span(SOURCE).decode(), span(TARGET).decode()
    source_diagrams = base.diagram_occurrences(source)
    target_diagrams = base.diagram_occurrences(target)
    if [(x[0], x[1]) for x in source_diagrams] != [(x[0], x[1]) for x in target_diagrams]:
        raise SystemExit("Unit 013 backend refused: diagram order/format drift")
    if diagram_blocks(source) != diagram_blocks(target):
        raise SystemExit("Unit 013 backend refused: normalized diagram content drift")
    for text in (source, target):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit("Unit 013 backend refused: label drift")
        if len(base.index_occurrences(text)) != 5:
            raise SystemExit("Unit 013 backend refused: index drift")
        if len(base.diagram_occurrences(text)) != 2:
            raise SystemExit("Unit 013 backend refused: diagram drift")
        if base.citation_occurrences(text) != EXPECTED_CITATIONS:
            raise SystemExit("Unit 013 backend refused: citation topology drift")
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
        raise SystemExit("Unit 013 backend refused: external-reference drift")
    final_aux_lines = {
        match.group(1): line.strip()
        for line in (ROOT / FINAL_AUX).read_text(encoding="utf-8").splitlines()
        if (match := re.match(r"\\newlabel\{([^}]+)\}", line))
    }
    wanted_equations = {
        key: (
            r"\newlabel{" + key + "}{{" + number + "}{" + page
            + "}{Fungtor Representabel}{" + anchor + "}{}}"
        )
        for key, number, page, anchor in EQUATION_MAP
    }
    if any(final_aux_lines.get(key) != line for key, line in wanted_equations.items()):
        raise SystemExit("Unit 013 backend refused: equation-label map drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    receipt = (ROOT / ADMISSION).read_text(encoding="utf-8")
    correction_receipt = (ROOT / CORRECTION_RECEIPT).read_text(encoding="utf-8")
    final_log = (ROOT / FINAL_LOG).read_text(encoding="utf-8", errors="replace")
    log_pages = re.findall(r"Output written on .*?\((\d+) pages?\)\.", final_log, re.DOTALL)
    if not log_pages or int(log_pages[-1]) != PAGE_COUNT:
        raise SystemExit("Unit 013 backend refused: final build-log page count drift")
    if pdfinfo_page_count() != PAGE_COUNT:
        raise SystemExit("Unit 013 backend refused: live PDF page count drift")
    for needle in (f"PDF pages: {PAGE_COUNT}", f"Functional replay: {PAGE_COUNT}/{PAGE_COUNT}", "Final-log blockers: zero", f"Visual QA: all {PAGE_COUNT} pages inspected", "eqn:Yoneda-cat-duality = (2.3)", "eqn:Yoneda-map = (2.4)"):
        if needle not in summary:
            raise SystemExit(f"Unit 013 backend refused: summary lacks {needle!r}")
    for needle in ("Status: admitted locally", "chapter2.tex:678-765", f"{PAGE_COUNT} pages", TARGET_SPAN[1], ARTIFACT_ID[1], FINAL_LOG_ID[1], "equation.2.3", "equation.2.4", MODEL, "Wen-Wei Li", "CC BY 4.0", "CC BY-SA 3.0", "OFL 1.1", "non-endorsed derivative"):
        if needle not in receipt:
            raise SystemExit(f"Unit 013 backend refused: admission lacks {needle!r}")
    for needle in (DRIVER_ID[1], ARTIFACT_ID[1], FINAL_LOG_ID[1], FINAL_AUX_ID[1], "eqn:Yoneda-cat-duality -> 2.3", "eqn:Yoneda-map -> 2.4", MODEL, "Wen-Wei Li", "CC BY 4.0", "CC BY-SA 3.0", "OFL", "non-endorsed derivative"):
        if needle not in correction_receipt:
            raise SystemExit(f"Unit 013 backend refused: correction receipt lacks {needle!r}")


def main() -> None:
    gate()
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    unit_key = "unit/bab-2-fungtor-representabel-dan-lema-yoneda"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/fungtor-representabel-dan-lema-yoneda"
    section_id = uid(section_key)
    bind = base.binding

    source_citation_occurrences = base.citation_occurrences(span(SOURCE).decode())
    target_citation_occurrences = base.citation_occurrences(span(TARGET).decode())
    if source_citation_occurrences != EXPECTED_CITATIONS:
        raise SystemExit("Unit 013 backend refused: source citation identity drift")
    if target_citation_occurrences != EXPECTED_CITATIONS:
        raise SystemExit("Unit 013 backend refused: target citation identity drift")

    concept_specs = [
        ("concept/functor-category", "函子范畴", "kategori fungtor"),
        ("concept/presheaf", "预层", "pragemal"),
        ("concept/hom-functor", "Hom 函子", "fungtor Hom"),
        ("concept/evaluation-functor", "求值函子", "fungtor evaluasi"),
        ("concept/yoneda-lemma", "米田引理", "Lema Yoneda"),
        ("concept/yoneda-embedding", "米田嵌入", "pembenaman Yoneda"),
        ("concept/full-functor", "满函子", "fungtor penuh"),
        ("concept/faithful-functor", "忠实函子", "fungtor setia"),
        ("concept/representable-functor", "可表函子", "fungtor representabel"),
        ("concept/functor-representation", "代表元", "representasi fungtor"),
        ("concept/universal-family", "泛族", "keluarga universal"),
        ("concept/comma-category", "逗号范畴", "kategori koma"),
        ("concept/terminal-object", "终对象", "objek terminal"),
        ("concept/free-vector-space", "自由向量空间", "ruang vektor bebas"),
        ("concept/power-set", "幂集", "himpunan kuasa"),
        ("concept/characteristic-function", "示性函数", "fungsi karakteristik"),
        ("concept/moduli-space", "模空间", "ruang moduli"),
        ("concept/eilenberg-maclane-space", "Eilenberg-MacLane 空间", "ruang Eilenberg-MacLane"),
        ("concept/cohomology-functor", "上同调函子", "fungtor kohomologi"),
        ("concept/generalized-function", "广义函数", "fungsi rampat"),
    ]
    for label in LABELS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-013/label/{slug}", f"标签 {label}", f"label {label}"))
    for label, _number, _page in EXTERNAL_REFS:
        slug = label.replace(":", "-").lower()
        concept_specs.append((f"surface/unit-013/reference/{slug}", f"外部引用 {label}", f"rujukan eksternal {label}"))
    concepts = [{"id": uid(k), "stable_key": k, "entity_type": "concept", "labels": [{"language": "zh-Hans", "text": zh}, {"language": "id-ID", "text": idt}]} for k, zh, idt in concept_specs]
    concept_ids = [x["id"] for x in concepts]

    rights_map = {x["stable_key"]: x["id"] for x in data["rights"]}
    principal = rights_map["rights/principal-cc-by-4.0"]
    unit_rights = [principal, rights_map["rights/ajbook-fragment-cc-by-sa-3.0"], rights_map["rights/noto-fonts-ofl-1.1"]]
    prerequisite_ids = [x["id"] for x in data["prerequisites"]]
    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section", "parent_id": unit_id, "order": 1,
        "source_local_id": "chapter2.tex:678-765",
        "titles": [{"language": "zh-Hans", "text": "2.5 可表函子"}, {"language": "id-ID", "text": "2.5 Fungtor Representabel"}],
        "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END),
        "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": [principal],
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    citations = []
    source_indexes = base.index_occurrences(span(SOURCE).decode())
    target_indexes = base.index_occurrences(span(TARGET).decode())
    index_entries = []
    for n, (slug, s, t) in enumerate(zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1):
        if (s[0], s[2]) != (t[0], t[2]):
            raise SystemExit("Unit 013 backend refused: index topology mismatch")
        key = f"index-entry/unit-013/{slug}"
        index_entries.append({"id": uid(key), "stable_key": key, "entity_type": "index_entry", "section_id": section_id, "ordinal_in_unit": n, "source_key": s[1], "target_key": t[1], "source_binding": bind(SOURCE, s[2], s[2]), "target_binding": bind(TARGET, t[2], t[2]), "provenance_state": "source_key_preserved_target_key_localized"})
    diagrams = []
    source_diagrams = base.diagram_occurrences(span(SOURCE).decode())
    target_diagrams = base.diagram_occurrences(span(TARGET).decode())
    for n, (source_diagram, target_diagram) in enumerate(zip(source_diagrams, target_diagrams, strict=True), 1):
        fmt, occ, source_first, source_last = source_diagram
        target_fmt, target_occ, target_first, target_last = target_diagram
        if (fmt, occ) != (target_fmt, target_occ):
            raise SystemExit("Unit 013 backend refused: diagram binding drift")
        key = f"diagram/unit-013/{fmt}-{occ}"
        diagrams.append({"id": uid(key), "stable_key": key, "entity_type": "diagram", "section_id": section_id, "ordinal_in_unit": n, "source_format": fmt, "source_occurrence_index": occ, "source_binding": bind(SOURCE, source_first, source_last), "target_binding": bind(TARGET, target_first, target_last), "rights_component_id": principal, "state": "audited_preserved"})
    build_key = "build-surface/unit-013-pdf"
    inputs = [COVER, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls", "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex", "repo/source/titles-setup.tex", "repo/source/mycommand.sty", "repo/source/myarrows.sty", "repo/source/Al-jabr.bib", "repo/source/ccby.png", CROSSREF, "repo/fonts/NotoSansCJKsc-Black.otf", "repo/fonts/NotoSansCJKsc-Medium.otf", "repo/fonts/NotoSansCJKsc-Regular.otf", "repo/fonts/NotoSerifCJKsc-Bold.otf"]
    build = {"id": uid(build_key), "stable_key": build_key, "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf", "working_directory": ".", "command": "pwsh -NoProfile -File scripts/build_unit_013.ps1 -OutputDirectory build/unit-013-replay", "artifact_path": ARTIFACT, "artifact_binding": bind(ARTIFACT), "log_binding": bind(FINAL_LOG), "build_script": bind(BUILD_SCRIPT), "page_count": PAGE_COUNT, "status": "pass", "driver": bind(DRIVER), "input_bindings": [bind(x) for x in inputs], "external_dependencies": ["XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)", "Fandol fonts from TeX distribution", "TeX Gyre Heros", "packages loaded by the Unit 013 driver and AJbook.cls"], "rights_component_ids": unit_rights}
    qa_key = "qa/unit-013/admission-gate"
    qa = {"id": uid(qa_key), "stable_key": qa_key, "entity_type": "qa_event", "unit_id": unit_id, "check_type": "admission_gate", "result": "pass", "scope": "Complete source-order translation and semantic review of chapter2.tex lines 678-765; 98 normalized mathematics surfaces equivalent after two disclosed source corrections, 17 balanced environments, seven labels, ten ordinary references, three equation references, zero citations, five index entries, two TikZ-CD diagrams, no exercises/hints/answers/solutions, frozen external references, separate component rights, corrected Chapter 2 equation continuity, four-pass functional replay, PDF checks, and all-page visual QA. Production provenance records " + MODEL + " separately from source authorship and human credit.", "witness": ADMISSION, "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass", "witness_binding": bind(ADMISSION)}
    equation_qa_key = "qa/unit-013/equation-number-continuity"
    equation_qa = {"id": uid(equation_qa_key), "stable_key": equation_qa_key, "entity_type": "qa_event", "unit_id": unit_id, "check_type": "backend_integrity", "result": "pass", "scope": "Equation-number continuity: the complete Chapter 2 source has equations (2.1) and (2.2) before Unit 013. The standalone driver seeds equation=2 immediately before chapter2.tex lines 678-765, and the verified final AUX binds eqn:Yoneda-cat-duality to 2.3/equation.2.3 and eqn:Yoneda-map to 2.4/equation.2.4. Two clean builds replay identically in Poppler and MuPDF and all seven pages pass visual inspection. Translation content was unchanged and its prior audit remains valid.", "witness": CORRECTION_RECEIPT, "translation_audit_state": "pass", "build_state": "pass", "visual_state": "pass", "witness_binding": bind(CORRECTION_RECEIPT)}
    dataset_key = "dataset/unit-013/id-id"
    data["dataset_stable_key"] = dataset_key; data["dataset_id"] = uid(dataset_key)
    data["workflow"] = {"responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9", "updated": "2026-08-23", "status": "admitted", "admission_state": "admitted", "translation_state": "visually_checked", "qa_state": "translation_backend_build_visual_equation_continuity_pass"}
    unit = {"id": unit_id, "stable_key": unit_key, "entity_type": "unit", "program_id": data["program"]["id"], "course_id": data["course"]["id"], "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"], "order": 13, "source_local_id": "chapter2.tex:678-765", "titles": [{"language": "zh-Hans", "text": "第二章：范畴论基础；可表函子"}, {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Fungtor Representabel dan Lema Yoneda"}], "source_language": "zh-Hans", "target_language": "id-ID", "source_binding": bind(SOURCE, START, END), "target_binding": bind(TARGET, START, END), "section_ids": [section_id], "concept_ids": concept_ids, "prerequisite_ids": prerequisite_ids, "rights_component_ids": unit_rights, "citation_ids": [x["id"] for x in citations], "diagram_ids": [x["id"] for x in diagrams], "index_entry_ids": [x["id"] for x in index_entries], "build_surface_ids": [build["id"]], "qa_event_ids": [qa["id"], equation_qa["id"]], "outcome_keys": ["outcome/define-presheaf-categories", "outcome/apply-the-yoneda-lemma", "outcome/recognize-yoneda-embeddings", "outcome/characterize-representable-functors", "outcome/prove-uniqueness-of-functor-representations", "outcome/use-universal-families", "outcome/identify-power-set-representability"], "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 0, "diagrams": len(diagrams), "index_entries": len(index_entries)}, "translation_state": "visually_checked", "admission_state": "admitted"}
    data["unit"] = unit; data["sections"] = [section]; data["concepts"] = concepts; data["citations"] = citations; data["diagrams"] = diagrams; data["index_entries"] = index_entries; data["build_surfaces"] = [build]; data["qa_events"] = [qa, equation_qa]
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_backend.py"), "--lane-root", str(ROOT), "--data", str(OUTPUT), "--schema", str(ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"), "--csv-dir", str(ROOT / "backend/csv"), "--write-csv"], cwd=ROOT, check=True)
    print(json.dumps({"path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"), "bytes": OUTPUT.stat().st_size, "sha256": digest(OUTPUT.read_bytes()), "entities": 1 + 1 + 1 + 1 + 1 + len(data["sections"]) + len(concepts) + len(data["prerequisites"]) + len(data["rights"]) + len(data["citations"]) + len(diagrams) + len(index_entries) + len(data["build_surfaces"]) + len(data["qa_events"]), "concepts": len(concepts), "diagrams": len(diagrams), "index_entries": len(index_entries)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
