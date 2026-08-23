#!/usr/bin/env python3
"""Generate the admitted O013 Unit 010 backend from frozen live evidence."""

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
TEMPLATE = ROOT / "backend/data/unit-009-bab-2-kategori-dan-morfisme.json"
OUTPUT = ROOT / "backend/data/unit-010-bab-2-fungtor-dan-transformasi-natural.json"
SOURCE = "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
TARGET = "repo/source/chapter2.tex"
DRIVER = "repo/source/unit-010-bab-2-fungtor-dan-transformasi-natural.tex"
COVER = "repo/source/coverpage-id-unit-010.tex"
CROSSREF = "repo/source/unit-010-crossrefs.aux"
BUILD_SCRIPT = "scripts/build_unit_010.ps1"
STRUCTURE_GATE = "scripts/check_unit_010_structure.py"
SUMMARY = "qa/unit-010-evidence/build-log-summary.txt"
ADMISSION = "qa/UNIT_010_ADMISSION_20260822.md"
ARTIFACT = "artifacts/unit-010-bab-2-fungtor-dan-transformasi-natural.pdf"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
START, END = 199, 467

EXPECTED = {
    SOURCE: (139983, "56496e557f6f05efdb825be000f688a904b1d1f44a752ebecac517d0a4ba1840"),
    DRIVER: (4456, "14b3b6be5cb1ed6121ea7c7ef1171f27b688d74e73a8d694df3d0f9be8398c02"),
    COVER: (4352, "79e81dce274ce479b0a8db1c4c86836e6e293db412efefa0e44b2ddc4e715565"),
    CROSSREF: (347, "93f7dd88c427169e550b858c24ebd9dee213eb062165a213019984612881336e"),
    BUILD_SCRIPT: (2864, "908515af22c5dec259e9038def8372eabfa3f7023c3fcddd834d5940d4e47c63"),
    STRUCTURE_GATE: (9693, "cb515f12c24bc38c4d8130af652e9b73be320ab51706654b7dd37a19429b6af2"),
    SUMMARY: (951, "c599fbecb824caa01744d6bc3c417ea3c55b40cc82885dbc3ed738bfa32889b0"),
    ADMISSION: (3270, "1e55671a6baf0b47fe26e029778d7cc1afdb3516d9201176d36d65aae84f960b"),
    ARTIFACT: (153352, "a06c4152e6233270cfa138b6c99ae9f307246fe2e1eac6b72a9533c9d74bfce4"),
}
SOURCE_SPAN = (23553, "316db06a11ca7b1caeb316a1285a7d506effb5d8c7c88459f33192a5ca94092a")
TARGET_SPAN = (28112, "84cd01f4bfb9b2dcf6720991b72d714335e3f977e2bee88d40b2b64733572053")
LABELS = (
    "sec:functors", "def:functor", "rem:op-functor", "eg:functors",
    "eqn:naturaltrans-def", "con:naturaltrans-morphism",
    "eqn:horizontal-comp", "prop:naturaltrans-associativity",
    "def:cat-equivalence", "rem:strict-or-not", "prop:skeletal-cat-isom",
    "prop:functor-equiv-criterion", "eg:vectf-duality",
)
EXTERNAL_REFS = (
    ("prop:abelianization", "4.7.{3}", "126"),
    ("sec:2-cat", "3.5", "92"),
    ("prop:adjoint-equivalence", "2.6.{12}", "56"),
)
INDEX_SLUGS = (
    "functor", "functor-full", "functor-essentially-surjective",
    "functor-faithful", "forgetful-functor", "vector-space-dual-symbol",
    "natural-transformation", "natural", "canonical",
    "natural-transformation-composition", "category-equivalence-definition",
    "functor-quasi-inverse", "adjoint-equivalence", "category-skeleton",
    "category-equivalence-criterion",
)
DIAGRAM_SLUGS = (
    "naturality-square", "natural-transformation-two-cell",
    "vertical-composition-input", "vertical-composition-result",
    "horizontal-composition-chain", "horizontal-composition-naturality-square",
    "horizontal-composition-input", "horizontal-composition-result",
    "whiskering", "interchange-law", "horizontal-composition-proof-square",
    "horizontal-associativity-input", "horizontal-associativity-diamond",
    "horizontal-associativity-upper-path", "horizontal-associativity-lower-path",
    "category-equivalence-pair", "gelfand-naimark-equivalence",
    "fully-faithful-hom-chain", "evaluation-naturality-square",
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def identity(relative: str) -> tuple[int, str]:
    payload = (ROOT / relative).read_bytes()
    return len(payload), digest(payload)


def span(relative: str) -> bytes:
    return base.normalized_span(relative, START, END)


def gate() -> int:
    base.SPAN_START, base.SPAN_END = START, END
    for relative, expected in EXPECTED.items():
        if not (ROOT / relative).is_file() or identity(relative) != expected:
            raise SystemExit(f"Unit 010 backend refused: identity drift for {relative}")
    if (len(span(SOURCE)), digest(span(SOURCE))) != SOURCE_SPAN:
        raise SystemExit("Unit 010 backend refused: source span drift")
    if (len(span(TARGET)), digest(span(TARGET))) != TARGET_SPAN:
        raise SystemExit("Unit 010 backend refused: target span drift")
    check = subprocess.run(
        [sys.executable, str(ROOT / STRUCTURE_GATE)], cwd=ROOT,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if check.returncode:
        raise SystemExit("Unit 010 backend refused: structure gate failed\n" + check.stdout)
    report = json.loads(check.stdout)
    required = {
        "status": "pass", "mathematics_source_count": 291,
        "mathematics_target_count": 291, "environment_sequence_exact": True,
        "han_residue_count": 0, "target_sha256": TARGET_SPAN[1],
    }
    if any(report.get(key) != value for key, value in required.items()):
        raise SystemExit("Unit 010 backend refused: structure evidence drift")
    source = span(SOURCE).decode("utf-8")
    target = span(TARGET).decode("utf-8")
    for label, text in (("source", source), ("target", target)):
        if tuple(re.findall(r"\\label\{([^}]+)\}", text)) != LABELS:
            raise SystemExit(f"Unit 010 backend refused: {label} label drift")
        if len(base.index_occurrences(text)) != 15:
            raise SystemExit(f"Unit 010 backend refused: {label} index drift")
        if len(base.diagram_occurrences(text)) != 19:
            raise SystemExit(f"Unit 010 backend refused: {label} diagram drift")
        if base.citation_occurrences(text) != (("Zh2", 388), ("Zh2", 388)):
            raise SystemExit(f"Unit 010 backend refused: {label} citation drift")
    aux = tuple(
        line.strip() for line in (ROOT / CROSSREF).read_text(encoding="utf-8").splitlines()
        if line.lstrip().startswith(r"\newlabel{")
    )
    wanted = tuple(
        r"\newlabel{" + key + "}{{" + number + "}{" + page + "}}"
        for key, number, page in EXTERNAL_REFS
    )
    if aux != wanted:
        raise SystemExit("Unit 010 backend refused: external-reference drift")
    summary = (ROOT / SUMMARY).read_text(encoding="utf-8")
    admission = (ROOT / ADMISSION).read_text(encoding="utf-8")
    for needle in (
        "Final pages: 15", "Functional replay: 15/15", "Final-log blockers: zero",
        "Visual QA: all 15 pages inspected",
    ):
        if needle not in summary:
            raise SystemExit(f"Unit 010 backend refused: summary lacks {needle!r}")
    for needle in (
        "Status: admitted locally", "chapter2.tex:199-467", TARGET_SPAN[1],
        EXPECTED[ARTIFACT][1], "291 normalized mathematics",
        MODEL, "Wen-Wei Li", "CC BY 4.0", "CC BY-SA 3.0", "OFL 1.1",
        "independent, non-endorsed derivative",
    ):
        if needle not in admission:
            raise SystemExit(f"Unit 010 backend refused: admission lacks {needle!r}")
    info = subprocess.run(
        ["pdfinfo", str(ROOT / ARTIFACT)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if info.returncode or re.search(r"^Pages:\s*15\s*$", info.stdout, re.MULTILINE) is None:
        raise SystemExit("Unit 010 backend refused: PDF page count drift")
    return 15


def main() -> None:
    pages = gate()
    base.SPAN_START, base.SPAN_END = START, END
    data = copy.deepcopy(json.loads(TEMPLATE.read_text(encoding="utf-8")))
    namespace = uuid.UUID(data["id_namespace"]["namespace_uuid"].removeprefix("urn:uuid:"))
    uid = lambda key: "urn:uuid:" + str(uuid.uuid5(namespace, key))
    binding = base.binding
    unit_key = "unit/bab-2-fungtor-dan-transformasi-natural"
    unit_id = uid(unit_key)
    section_key = unit_key + "/section/fungtor-dan-transformasi-natural"
    section_id = uid(section_key)

    concept_specs = [
        ("concept/functor", "函子", "fungtor"),
        ("concept/functor-composition", "合成函子", "komposisi fungtor"),
        ("concept/covariant-functor", "共变函子", "fungtor kovarian"),
        ("concept/contravariant-functor", "反变函子", "fungtor kontravarian"),
        ("concept/opposite-functor", "反范畴间的相应函子", "fungtor lawan"),
        ("concept/full-functor", "全函子", "fungtor penuh"),
        ("concept/faithful-functor", "忠实函子", "fungtor setia"),
        ("concept/essentially-surjective-functor", "本质满函子", "fungtor surjektif secara esensial"),
        ("concept/identity-functor", "恒等函子", "fungtor identitas"),
        ("concept/inclusion-functor", "包含函子", "fungtor inklusi"),
        ("concept/forgetful-functor", "忘却函子", "fungtor pelupa"),
        ("concept/dual-functor", "对偶函子", "fungtor dual"),
        ("concept/double-dual-functor", "双对偶函子", "fungtor dual ganda"),
        ("concept/natural-transformation", "自然变换", "transformasi natural"),
        ("concept/naturality-square", "自然性方块", "persegi naturalitas"),
        ("concept/two-cell", "2-胞腔", "2-sel"),
        ("concept/functoriality", "函子性", "fungtorialitas"),
        ("concept/vertical-composition-of-natural-transformations", "自然变换的纵合成", "komposisi vertikal transformasi natural"),
        ("concept/horizontal-composition-of-natural-transformations", "自然变换的横合成", "komposisi horizontal transformasi natural"),
        ("concept/whiskering", "横合成的特例", "whiskering"),
        ("concept/interchange-law", "互换律", "hukum pertukaran"),
        ("concept/natural-isomorphism", "自然同构", "isomorfisme natural"),
        ("concept/category-equivalence", "范畴等价", "ekuivalensi kategori"),
        ("concept/quasi-inverse-functor", "拟逆函子", "fungtor kuasi-invers"),
        ("concept/category-isomorphism", "范畴同构", "isomorfisme kategori"),
        ("concept/coherence", "融贯性", "koherensi"),
        ("concept/adjoint-equivalence", "伴随等价", "ekuivalensi adjoin"),
        ("concept/category-skeleton", "范畴骨架", "kerangka kategori"),
        ("concept/skeletal-category", "骨架范畴", "kategori berkerangka"),
        ("concept/equivalence-criterion", "等价判据", "kriteria ekuivalensi"),
        ("concept/gelfand-naimark-duality", "Gelfand--Naimark 定理", "dualitas Gelfand--Naimark"),
        ("concept/evaluation-natural-transformation", "求值自然变换", "transformasi natural evaluasi"),
        ("concept/matrix-category", "矩阵范畴", "kategori matriks"),
    ]
    for label in LABELS:
        slug = label.lower().replace(":", "-").replace("_", "-")
        concept_specs.append((f"surface/unit-010/label/{slug}", f"标签 {label}", f"label {label}"))
    for label, _number, _page in EXTERNAL_REFS:
        slug = label.lower().replace(":", "-").replace("_", "-")
        concept_specs.append((f"surface/unit-010/reference/{slug}", f"外部引用 {label}", f"rujukan eksternal {label}"))
    concept_specs += [
        ("surface/unit-010/citation-occurrence/zh2-line-388-occurrence-2", "重复引文 Zh2（第 388 行，第二次）", "kemunculan kedua sitasi Zh2 pada baris 388"),
        ("surface/unit-010/correction/index-equivalence-line-415", "第 415 行的范畴等价索引短项", "normalisasi entri indeks ekuivalensi kategori pada baris 415"),
    ]
    concepts = [
        {"id": uid(key), "stable_key": key, "entity_type": "concept",
         "labels": [{"language": "zh-Hans", "text": zh}, {"language": "id-ID", "text": id_text}]}
        for key, zh, id_text in concept_specs
    ]
    concept_ids = [item["id"] for item in concepts]

    prerequisite_key = "prerequisite/categories-and-morphisms"
    prerequisite = {
        "id": uid(prerequisite_key), "stable_key": prerequisite_key,
        "entity_type": "prerequisite",
        "labels": [{"language": "zh-Hans", "text": "范畴与态射"}, {"language": "id-ID", "text": "kategori dan morfisme"}],
        "requiredness": "expected",
        "source_evidence": {"path": SOURCE, "line_start": 39, "line_end": 198},
    }
    data["prerequisites"].append(prerequisite)
    pmap = {item["stable_key"]: item["id"] for item in data["prerequisites"]}
    prerequisites = [pmap[key] for key in (
        "prerequisite/basic-mathematical-literacy",
        "prerequisite/mathematical-logic",
        "prerequisite/elementary-set-theory",
        prerequisite_key,
    )]

    principal = next(x for x in data["rights"] if x["stable_key"] == "rights/principal-cc-by-4.0")
    principal["bindings"] = [binding(SOURCE), binding("repo/source/LICENSE"), binding("repo/source/ccby.png")]
    rmap = {item["stable_key"]: item["id"] for item in data["rights"]}
    unit_rights = [rmap["rights/principal-cc-by-4.0"], rmap["rights/ajbook-fragment-cc-by-sa-3.0"], rmap["rights/noto-fonts-ofl-1.1"]]

    section = {
        "id": section_id, "stable_key": section_key, "entity_type": "section",
        "parent_id": unit_id, "order": 1, "source_local_id": "chapter2.tex:199-467",
        "titles": [{"language": "zh-Hans", "text": "2.2 函子与自然变换"}, {"language": "id-ID", "text": "2.2 Fungtor dan Transformasi Natural"}],
        "source_binding": binding(SOURCE, START, END), "target_binding": binding(TARGET, START, END),
        "concept_ids": concept_ids, "prerequisite_ids": prerequisites,
        "rights_component_ids": [rmap["rights/principal-cc-by-4.0"]],
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    bib = binding("repo/source/Al-jabr.bib")
    citation_key = "citation/unit-010/zh2/line-388"
    citations = [{
        "id": uid(citation_key), "stable_key": citation_key, "entity_type": "citation",
        "bib_key": "Zh2", "bibliography_path": bib["path"], "bibliography_sha256": bib["sha256"],
        "source_line": 388, "target_line": 388, "section_id": section_id,
    }]

    source_indexes = base.index_occurrences(span(SOURCE).decode("utf-8"))
    target_indexes = base.index_occurrences(span(TARGET).decode("utf-8"))
    index_entries = []
    for ordinal, (slug, source_index, target_index) in enumerate(zip(INDEX_SLUGS, source_indexes, target_indexes, strict=True), 1):
        sname, skey, sline = source_index; tname, tkey, tline = target_index
        if (sname, sline) != (tname, tline):
            raise SystemExit("Unit 010 backend refused: index topology mismatch")
        key = f"index-entry/unit-010/{slug}"
        index_entries.append({
            "id": uid(key), "stable_key": key, "entity_type": "index_entry",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_key": skey, "target_key": tkey,
            "source_binding": binding(SOURCE, sline, sline), "target_binding": binding(TARGET, tline, tline),
            "provenance_state": "source_key_preserved_target_key_localized",
        })

    diagram_specs = base.diagram_occurrences(span(SOURCE).decode("utf-8"))
    diagrams = []
    for ordinal, (slug, spec) in enumerate(zip(DIAGRAM_SLUGS, diagram_specs, strict=True), 1):
        fmt, occurrence, first, last = spec; key = f"diagram/unit-010/{slug}"
        diagrams.append({
            "id": uid(key), "stable_key": key, "entity_type": "diagram",
            "section_id": section_id, "ordinal_in_unit": ordinal,
            "source_format": fmt, "source_occurrence_index": occurrence,
            "source_binding": binding(SOURCE, first, last), "target_binding": binding(TARGET, first, last),
            "rights_component_id": rmap["rights/principal-cc-by-4.0"], "state": "audited_preserved",
        })

    build_key = "build-surface/unit-010-pdf"
    build = {
        "id": uid(build_key), "stable_key": build_key, "entity_type": "build_surface",
        "unit_id": unit_id, "kind": "pdf", "working_directory": ".",
        "command": "pwsh -NoProfile -File scripts/build_unit_010.ps1 -OutputDirectory build/unit-010-replay-id",
        "artifact_path": ARTIFACT, "artifact_binding": binding(ARTIFACT),
        "log_binding": binding(SUMMARY), "build_script": binding(BUILD_SCRIPT),
        "page_count": pages, "status": "pass", "driver": binding(DRIVER),
        "input_bindings": [binding(x) for x in (
            COVER, "repo/source/font-setup-id.tex", "repo/source/AJbook.cls",
            "repo/source/titles-setup-id.tex", "repo/source/locale-ui-id.tex",
            "repo/source/titles-setup.tex", "repo/source/mycommand.sty",
            "repo/source/myarrows.sty", "repo/source/Al-jabr.bib",
            "repo/source/ccby.png", CROSSREF,
            "repo/fonts/NotoSansCJKsc-Black.otf", "repo/fonts/NotoSansCJKsc-Medium.otf",
            "repo/fonts/NotoSansCJKsc-Regular.otf", "repo/fonts/NotoSerifCJKsc-Bold.otf",
        )],
        "external_dependencies": ["XeLaTeX", "PowerShell 7", "biber", "makeindex (default and sym1 indexes)", "Fandol fonts from TeX distribution", "TeX Gyre Heros", "packages loaded by the Unit 010 driver and AJbook.cls"],
        "rights_component_ids": unit_rights,
    }
    qa_key = "qa/unit-010/admission-gate"
    qa = {
        "id": uid(qa_key), "stable_key": qa_key, "entity_type": "qa_event",
        "unit_id": unit_id, "check_type": "admission_gate", "result": "pass",
        "scope": (
            "Complete source-order translation and semantic review of chapter2.tex lines 199-467; "
            "291 exact normalized mathematics surfaces, 51 balanced environments, 13 labels, seven "
            "ordinary references, two equation references, two protected Zh2 occurrences represented "
            "by one unique-key citation plus one compatibility surface, 19 preserved diagrams, 15 index "
            "entries including the disclosed line-415 source-consistency repair, 17 list items, zero "
            "exercises/hints/answers/solutions, three frozen external references, separate component "
            "rights, two-build functional replay, PDF checks, and all-page visual QA. Production "
            f"provenance records {MODEL} separately from source authorship and human credit."
        ),
        "witness": ADMISSION, "translation_audit_state": "pass",
        "build_state": "pass", "visual_state": "pass", "witness_binding": binding(ADMISSION),
    }

    dataset_key = "dataset/unit-010/id-id"
    data["dataset_stable_key"] = dataset_key; data["dataset_id"] = uid(dataset_key)
    data["workflow"] = {
        "responsible_task": "01a02163-e2bf-7a93-950a-b9ab84d7e8b9",
        "updated": "2026-08-23", "status": "admitted",
        "admission_state": "admitted", "translation_state": "visually_checked",
        "qa_state": "translation_backend_build_visual_pass",
    }
    data["unit"] = {
        "id": unit_id, "stable_key": unit_key, "entity_type": "unit",
        "program_id": data["program"]["id"], "course_id": data["course"]["id"],
        "resource_id": data["resource"]["id"], "edition_id": data["edition"]["id"],
        "order": 10, "source_local_id": "chapter2.tex:199-467",
        "titles": [{"language": "zh-Hans", "text": "第二章：范畴论基础；函子与自然变换"}, {"language": "id-ID", "text": "Bab 2: Dasar-Dasar Teori Kategori; Fungtor dan Transformasi Natural"}],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": binding(SOURCE, START, END), "target_binding": binding(TARGET, START, END),
        "section_ids": [section_id], "concept_ids": concept_ids,
        "prerequisite_ids": prerequisites, "rights_component_ids": unit_rights,
        "citation_ids": [x["id"] for x in citations], "diagram_ids": [x["id"] for x in diagrams],
        "index_entry_ids": [x["id"] for x in index_entries], "build_surface_ids": [build["id"]],
        "qa_event_ids": [qa["id"]],
        "outcome_keys": [
            "outcome/define-and-compose-functors",
            "outcome/distinguish-full-faithful-and-essentially-surjective-functors",
            "outcome/construct-standard-and-contravariant-functors",
            "outcome/define-natural-transformations-and-check-naturality",
            "outcome/compose-natural-transformations-vertically-and-horizontally",
            "outcome/apply-the-interchange-law-and-whiskering",
            "outcome/construct-category-equivalences-and-quasi-inverses",
            "outcome/apply-the-full-faithful-essentially-surjective-criterion",
        ],
        "surface_counts": {"sections": 1, "exercises": 0, "hints": 0, "answers": 0, "solutions": 0, "citations": 1, "diagrams": 19, "index_entries": 15},
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    data["sections"] = [section]; data["concepts"] = concepts
    data["citations"] = citations; data["diagrams"] = diagrams
    data["index_entries"] = index_entries; data["build_surfaces"] = [build]
    data["qa_events"] = [qa]
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
