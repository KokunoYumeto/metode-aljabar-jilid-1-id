#!/usr/bin/env python3
"""Generate the complete-Chapter-5 modular backend for O013 Li Unit 043."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
import sys
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
TEMPLATE = ROOT / "backend/data/unit-035-bab-4-grup-dalam-kategori-dan-latihan.json"
SOURCE = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex"
CANDIDATE = ROOT / "build/unit-043-candidate/chapter5-complete-id.tex"
TARGET = ROOT / "repo/source/chapter5.tex"
DELTA = ROOT / "build/unit-043-candidate/CHAPTER5_TERMINOLOGY_DELTA.id-ID.csv"
CHECKER = ROOT / "build/unit-043-candidate/check_chapter5_complete.py"
CHAPTER_PDF = ROOT / "artifacts/unit-043-bab-5-pengantar-teori-gelanggang-id.pdf"
CHAPTER_LOG = ROOT / "qa/UNIT_043_BUILD_FINAL.log"
DRIVER = ROOT / "repo/source/unit-043-bab-5-pengantar-teori-gelanggang.tex"
COVER = ROOT / "repo/source/coverpage-id-unit-043.tex"
CROSSREF = ROOT / "repo/source/unit-043-crossrefs.aux"
BUILD_SCRIPT = ROOT / "scripts/build_unit_043.ps1"
COMBINED_PDF = ROOT / "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-5-reader.pdf"
COMBINED_SCRIPT = ROOT / "scripts/build_checkpoint_reader_through_chapter_5.py"
COMBINED_RECEIPT = ROOT / "qa/unit-043-evidence/checkpoint-through-bab-5-build.json"
VISUAL = ROOT / "qa/UNIT_043_COMBINED_READER_VISUAL_QA_20260828.md"
OUTPUT = ROOT / "backend/data/unit-043-bab-5-pengantar-teori-gelanggang.json"
VALIDATION = ROOT / "qa/unit-043-evidence/backend-validation.json"
CSV_PATHS = {
    name: ROOT / f"backend/csv/unit-043-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
}

NAMESPACE = uuid.UUID("5d74a443-839a-5a09-b2c6-0bc48a097f2b")
UNIT_KEY = "unit/bab-5-pengantar-teori-gelanggang"
SECTION_SPECS = [
    (1, 1, 21, "第五章导言", "Pengantar Bab 5"),
    (2, 22, 173, "基本概念", "Konsep Dasar"),
    (3, 174, 291, "若干特殊的环类", "Beberapa Kelas Gelanggang Khusus"),
    (4, 292, 462, "交换环初步", "Tinjauan Awal tentang Gelanggang Komutatif"),
    (5, 463, 609, "插曲：Möbius 反演", "Selingan: Inversi Möbius"),
    (6, 610, 782, "环的极限和完备化", "Limit dan Pelengkapan Gelanggang"),
    (7, 783, 957, "从幺半群环到多项式环", "Dari Gelanggang Monoid ke Gelanggang Polinomial"),
    (8, 958, 1183, "唯一分解", "Faktorisasi Unik"),
    (9, 1184, 1320, "对称多项式入门", "Pengantar Polinomial Simetris"),
    (10, 1321, 1382, "第五章习题", "Latihan Bab 5"),
]
CORRECTION_SPECS = [
    ("O013-LI-U036-COR-001", "qa/UNIT_036_TRANSLATION_REVIEW_20260825.md", 1, 172, 143,
     "Replace the undefined quotient R/I by R/Ker(varphi) in the first isomorphism theorem."),
    ("O013-LI-U036-COR-002", "qa/UNIT_036_TRANSLATION_REVIEW_20260825.md", 1, 172, 168,
     "Parenthesize the quotient as S/(I intersection S) in the subring-plus-ideal isomorphism."),
    ("O013-LI-U037-COR-001", "qa/UNIT_037_TRANSLATION_REVIEW_20260825.md", 174, 290, 219,
     "Place the inverse witness x-prime in the finite ring D rather than the undefined ring R."),
    ("O013-LI-U038-COR-001", "qa/UNIT_038_TRANSLATION_REVIEW_20260825.md", 292, 461, 355,
     "Qualify existence of a maximal proper ideal by excluding the zero ring."),
    ("O013-LI-U038-COR-002", "qa/UNIT_038_TRANSLATION_REVIEW_20260825.md", 292, 461, 416,
     "Use Frac(Z) rather than Frac(R) in the integer-ring example."),
    ("O013-LI-U039-COR-001", "qa/UNIT_039_TRANSLATION_REVIEW_20260825.md", 463, 608, 566,
     "Use the pairwise non-basepoint condition in the restricted-product multiplication."),
    ("O013-LI-U039-COR-002", "qa/UNIT_039_TRANSLATION_REVIEW_20260825.md", 463, 608, 598,
     "Describe Q(X)-times as nonzero rational functions rather than rational polynomials."),
    ("O013-LI-U040-COR-001", "qa/UNIT_040_TRANSLATION_REVIEW_20260825.md", 610, 781, 643,
     "Take the inverse limit of beta, the functor introduced locally, rather than alpha."),
    ("O013-LI-U041-COR-001", "qa/UNIT_041_TRANSLATION_REVIEW_20260825.md", 783, 956, 860,
     "Replace the undefined absolute-value test on a ring coefficient by nonvanishing."),
    ("O013-LI-U041-COR-002", "qa/UNIT_041_TRANSLATION_REVIEW_20260825.md", 783, 956, 892,
     "Restore all n variables in the formal power-series ring notation."),
    ("O013-LI-U041-COR-003", "qa/UNIT_041_TRANSLATION_REVIEW_20260825.md", 783, 956, 915,
     "State the exact coordinatewise lower-bound condition for Laurent-series exponent support."),
    ("O013-LI-U041-COR-004", "qa/UNIT_041_TRANSLATION_REVIEW_20260825.md", 783, 956, 953,
     "Restore bold multivariable X in the multiindex monomial."),
    ("O013-LI-U042-COR-001", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1053,
     "Exclude D=1 from the squarefree quadratic-field parameter."),
    ("O013-LI-U042-COR-002", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1074,
     "Complete the Gaussian-prime associate relation with conjugate(p)=u*p."),
    ("O013-LI-U042-COR-003", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1114,
     "Remove the unused irreducible-p quantifier from multiplicativity of global content."),
    ("O013-LI-U042-COR-004", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1117,
     "Choose representatives of content classes before multiplying them into polynomials."),
    ("O013-LI-U042-COR-005", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1127,
     "Define multivariable polynomial content by the minimum coefficient valuation."),
    ("O013-LI-U042-COR-006", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1151,
     "Restrict the gcd assertion to nonzero cyclotomic-binomial inputs while retaining the ideal identity."),
    ("O013-LI-U042-COR-007", "qa/UNIT_042_TRANSLATION_REVIEW_20260825.md", 958, 1182, 1165,
     "Strengthen k<=n to 1<=k<=n in Eisenstein's criterion."),
    ("O013-LI-U043-COR-001", "qa/UNIT_043_TRANSLATION_REVIEW_20260825.md", 1184, 1318, 1199,
     "Replace the false bound on partition parts by the intended index range 1<=i<=r."),
    ("O013-LI-U043-COR-002", "qa/UNIT_043_TRANSLATION_REVIEW_20260825.md", 1184, 1318, 1222,
     "Start the preceding-coordinate range at i=1 in the lexicographic-order definition."),
]


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def identity(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), sha(payload)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def uid(key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(NAMESPACE, key))


def label(language: str, text: str) -> dict[str, str]:
    return {"language": language, "text": text}


def entity(key: str, kind: str, english: str, Indonesian: str) -> dict[str, object]:
    return {
        "id": uid(key), "stable_key": key, "entity_type": kind,
        "labels": [label("en", english), label("id-ID", Indonesian)],
    }


def file_binding(path: Path) -> dict[str, object]:
    size, digest = identity(path)
    return {"path": rel(path), "bytes": size, "sha256": digest}


def span_payload(path: Path, first: int, last: int) -> bytes:
    text = path.read_text(encoding="utf-8")
    require("\r" not in text, f"CR forbidden: {rel(path)}")
    lines = text.splitlines()
    require(1 <= first <= last <= len(lines), f"invalid span: {rel(path)}:{first}-{last}")
    return ("\n".join(lines[first - 1:last]) + "\n").encode("utf-8")


def line_binding(path: Path, first: int, last: int) -> dict[str, object]:
    binding = file_binding(path)
    binding.update(
        {
            "line_start": first, "line_end": last,
            "span_sha256": sha(span_payload(path, first, last)),
            "span_hash_algorithm": "sha256-utf8-lines-lf-v1",
        }
    )
    return binding


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def section_index(line: int) -> int:
    for index, (_, first, last, _, _) in enumerate(SECTION_SPECS):
        if first <= line <= last:
            return index
    raise RuntimeError(f"line outside Chapter 5 section closure: {line}")


def diagram_spans(text: str) -> list[tuple[int, str, int, int]]:
    found: list[tuple[int, str, int, int]] = []
    for fmt in ("tikzcd", "tikzpicture"):
        pattern = re.compile(
            rf"\\begin\{{{fmt}\}}.*?\\end\{{{fmt}\}}", re.DOTALL
        )
        occurrence = 0
        for match in pattern.finditer(text):
            occurrence += 1
            found.append(
                (
                    match.start(), fmt, occurrence,
                    line_of(text, match.start()), line_of(text, match.end() - 1),
                )
            )
    found.sort()
    return [(position, fmt, occurrence, first, last) for position, fmt, occurrence, first, last in found]


def topology(text: str) -> dict[str, int]:
    env_markers = len(re.findall(r"\\(?:begin|end)\{[^{}]+\}", text))
    labels = len(re.findall(r"\\label\{[^{}]+\}", text))
    refs = len(re.findall(r"\\(?:eqref|ref)\{[^{}]+\}", text))
    citations = len(re.findall(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}", text))
    indexes = len(parse_indexes_with_lines(text))
    items = len(re.findall(r"\\item\b", text))
    exercises = text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    top_exercises = len(re.findall(r"(?m)^\t\\item\b", exercises))
    exercise_items = len(re.findall(r"\\item\b", exercises))
    hints = exercises.count(r"\begin{hint}")
    diagrams = diagram_spans(text)
    values = {
        "environment_markers": env_markers, "environment_pairs": env_markers // 2,
        "labels": labels, "references": refs, "citations": citations,
        "indexes": indexes, "list_items": items, "top_level_exercises": top_exercises,
        "exercise_items": exercise_items, "hints": hints,
        "diagrams": len(diagrams),
        "tikzcd": sum(1 for item in diagrams if item[1] == "tikzcd"),
        "tikzpicture": sum(1 for item in diagrams if item[1] == "tikzpicture"),
    }
    require(
        values == {
            "environment_markers": 480, "environment_pairs": 240,
            "labels": 80, "references": 112, "citations": 7,
            "indexes": 74, "list_items": 112, "top_level_exercises": 22,
            "exercise_items": 31, "hints": 11, "diagrams": 16,
            "tikzcd": 12, "tikzpicture": 4,
        },
        f"whole-chapter topology drift: {values}",
    )
    return values


def parse_indexes_with_lines(text: str) -> list[tuple[str, str, int]]:
    found: list[tuple[str, str, int]] = []
    cursor = 0
    while True:
        start = text.find(r"\index", cursor)
        if start < 0:
            return found
        pos = start + len(r"\index")
        stream = ""
        if pos < len(text) and text[pos] == "[":
            close = text.find("]", pos + 1)
            require(close >= 0, "unterminated index stream")
            stream = text[pos + 1:close]
            pos = close + 1
        require(pos < len(text) and text[pos] == "{", "malformed index")
        depth, body_start = 1, pos + 1
        pos += 1
        while pos < len(text) and depth:
            if text[pos] == "{" and text[pos - 1] != "\\":
                depth += 1
            elif text[pos] == "}" and text[pos - 1] != "\\":
                depth -= 1
            pos += 1
        require(depth == 0, "unterminated index body")
        found.append((stream, text[body_start:pos - 1], line_of(text, start)))
        cursor = pos


def make_backend() -> tuple[dict[str, object], dict[str, bytes], dict[str, object]]:
    require(identity(SOURCE) == (122998, "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"), "authority drift")
    require(identity(CANDIDATE) == (156081, "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c"), "candidate drift")
    require(TARGET.read_bytes() == CANDIDATE.read_bytes(), "canonical Chapter 5 is not the checked candidate")
    source_text = SOURCE.read_text(encoding="utf-8")
    target_text = TARGET.read_text(encoding="utf-8")
    counts = topology(target_text)
    require(topology(source_text) == counts, "source/target topology mismatch")
    with DELTA.open(encoding="utf-8", newline="") as handle:
        terms = list(csv.DictReader(handle))
    require(len(terms) == 22, "terminology delta drift")

    base = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    program, course, resource, edition = [
        copy.deepcopy(base[key]) for key in ("program", "course", "resource", "edition")
    ]
    prerequisites = copy.deepcopy(base["prerequisites"])
    rights = copy.deepcopy(base["rights"])
    unit_id = uid(UNIT_KEY)
    sections = []
    for order, first, last, source_title, target_title in SECTION_SPECS:
        key = f"{UNIT_KEY}/section/{order:02d}"
        sections.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "section",
                "parent_id": unit_id, "order": order,
                "source_local_id": f"chapter5.tex:{first}-{last}",
                "titles": [label("zh-Hans", source_title), label("id-ID", target_title)],
                "source_binding": line_binding(SOURCE, first, last),
                "target_binding": line_binding(TARGET, first, last),
                "concept_ids": [], "prerequisite_ids": [],
                "rights_component_ids": [uid("rights/principal-cc-by-4.0")],
                "translation_state": "visually_checked", "admission_state": "admitted",
            }
        )

    concepts: list[dict[str, object]] = []
    concept_section: dict[str, int] = {}
    for row in terms:
        slug = re.sub(r"[^a-z0-9]+", "-", row["source_term"].lower()).strip("-")
        key = f"concept/term/{slug}"
        record = entity(key, "concept", row["source_term"], row["target_term"])
        concepts.append(record)
        pos = target_text.casefold().find(row["target_term"].casefold())
        concept_section[record["id"]] = section_index(line_of(target_text, max(pos, 0)))
    outcomes = [
        ("ring-basics", "ring fundamentals", "dasar teori gelanggang", 1),
        ("special-rings", "special classes of rings", "kelas gelanggang khusus", 2),
        ("commutative-localization", "commutative rings and localization", "gelanggang komutatif dan lokalisasi", 3),
        ("mobius-inversion", "Möbius inversion", "inversi Möbius", 4),
        ("ring-completion", "limits and completion of rings", "limit dan pelengkapan gelanggang", 5),
        ("polynomial-rings", "monoid and polynomial rings", "gelanggang monoid dan polinomial", 6),
        ("unique-factorization", "unique factorization", "faktorisasi unik", 7),
        ("symmetric-polynomials", "symmetric polynomials", "polinomial simetris", 8),
        ("chapter-5-exercises", "Chapter 5 exercises", "latihan Bab 5", 9),
    ]
    for slug, en, indonesian, section_no in outcomes:
        record = entity(f"concept/o013-li-chapter5/{slug}", "concept", en, indonesian)
        concepts.append(record)
        concept_section[record["id"]] = section_no
    for kind, count, en, indonesian in (
        ("exercise", 22, "exercise", "latihan"),
        ("hint", 11, "hint", "petunjuk"),
    ):
        for number in range(1, count + 1):
            record = entity(
                f"surface/unit-043/{kind}/{number:03d}",
                "concept",
                f"Unit 043 {en} occurrence {number:03d}",
                f"Unit 043 kemunculan {indonesian} {number:03d}",
            )
            concepts.append(record)
            concept_section[record["id"]] = 9
    for concept in concepts:
        sections[concept_section[concept["id"]]]["concept_ids"].append(concept["id"])

    source_diagrams = diagram_spans(source_text)
    target_diagrams = diagram_spans(target_text)
    require([(x[1], x[2]) for x in source_diagrams] == [(x[1], x[2]) for x in target_diagrams], "diagram sequence drift")
    diagrams = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_diagrams, target_diagrams), 1):
        _, fmt, occurrence, source_first, source_last = source_item
        _, _, _, target_first, target_last = target_item
        key = f"diagram/unit-043/{fmt}-{occurrence:02d}"
        diagrams.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "diagram",
                "section_id": sections[section_index(target_first)]["id"],
                "ordinal_in_unit": ordinal, "source_format": fmt,
                "source_occurrence_index": occurrence,
                "source_binding": line_binding(SOURCE, source_first, source_last),
                "target_binding": line_binding(TARGET, target_first, target_last),
                "rights_component_id": uid("rights/principal-cc-by-4.0"),
                "state": "audited_preserved",
            }
        )

    source_indexes = parse_indexes_with_lines(source_text)
    target_indexes = parse_indexes_with_lines(target_text)
    require([x[0] for x in source_indexes] == [x[0] for x in target_indexes], "index-stream sequence drift")
    index_entries = []
    for ordinal, (source_item, target_item) in enumerate(zip(source_indexes, target_indexes), 1):
        stream, source_key, source_line = source_item
        _, target_key, target_line = target_item
        key = f"index-entry/unit-043/{stream or 'main'}/{ordinal:03d}"
        index_entries.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "index_entry",
                "section_id": sections[section_index(target_line)]["id"],
                "ordinal_in_unit": ordinal, "source_key": source_key,
                "target_key": target_key,
                "source_binding": line_binding(SOURCE, source_line, source_line),
                "target_binding": line_binding(TARGET, target_line, target_line),
                "provenance_state": "source_key_preserved_target_key_localized",
            }
        )

    bib = ROOT / "repo/source/Al-jabr.bib"
    bib_hash = identity(bib)[1]
    source_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", source_text))
    target_cites = list(re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}", target_text))
    require([x.group(1) for x in source_cites] == [x.group(1) for x in target_cites], "citation sequence drift")
    unique_cite_pairs = []
    seen_bib_keys = set()
    for source_match, target_match in zip(source_cites, target_cites):
        bib_key = target_match.group(1)
        if bib_key not in seen_bib_keys:
            unique_cite_pairs.append((source_match, target_match))
            seen_bib_keys.add(bib_key)
    citations = []
    for ordinal, (source_match, target_match) in enumerate(unique_cite_pairs, 1):
        bib_key = target_match.group(1)
        source_line, target_line = line_of(source_text, source_match.start()), line_of(target_text, target_match.start())
        key = f"citation/unit-043/{ordinal:02d}-{re.sub(r'[^a-z0-9]+', '-', bib_key.lower())}"
        citations.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "citation",
                "bib_key": bib_key, "bibliography_path": rel(bib),
                "bibliography_sha256": bib_hash, "source_line": source_line,
                "target_line": target_line,
                "section_id": sections[section_index(target_line)]["id"],
            }
        )

    rights_by_key = {item["stable_key"]: item for item in rights}
    for record in rights:
        if record["stable_key"] == "rights/principal-cc-by-4.0":
            record["bindings"] = [file_binding(SOURCE), file_binding(CANDIDATE), file_binding(TARGET), file_binding(ROOT / "repo/source/LICENSE")]
        elif record["stable_key"] == "rights/ajbook-fragment-cc-by-sa-3.0":
            record["bindings"] = [file_binding(ROOT / "repo/source/AJbook.cls")]
        elif record["stable_key"] == "rights/noto-fonts-ofl-1.1":
            record["bindings"] = [file_binding(ROOT / "repo/fonts/OFL-1.1-Noto-CJK.txt")]
        elif record["stable_key"] == "rights/fandol-gpl-3.0-with-font-exception":
            record["bindings"] = [file_binding(ROOT / "repo/fonts/FANDOL-AUTHORITY.json"), file_binding(ROOT / "repo/fonts/GPL-3.0-with-Fandol-font-exception.txt"), file_binding(CHAPTER_PDF), file_binding(COMBINED_PDF)]
        elif record["stable_key"] == "rights/lanzhou-cc-by-sa-3.0":
            record["bindings"] = [file_binding(ROOT / "repo/source/Lanzhou.png")]
            record["applies_to_unit"] = False
    principal = rights_by_key["rights/principal-cc-by-4.0"]["id"]
    common_rights = [
        principal,
        rights_by_key["rights/ajbook-fragment-cc-by-sa-3.0"]["id"],
        rights_by_key["rights/noto-fonts-ofl-1.1"]["id"],
        rights_by_key["rights/fandol-gpl-3.0-with-font-exception"]["id"],
    ]
    aggregate_rights = common_rights + [rights_by_key["rights/lanzhou-cc-by-sa-3.0"]["id"]]

    surfaces = [
        {
            "id": uid("build-surface/unit-043-chapter-pdf"),
            "stable_key": "build-surface/unit-043-chapter-pdf",
            "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf",
            "working_directory": ".",
            "command": "pwsh -NoProfile -File scripts/build_unit_043.ps1",
            "artifact_path": rel(CHAPTER_PDF), "artifact_binding": file_binding(CHAPTER_PDF),
            "log_binding": file_binding(CHAPTER_LOG), "build_script": file_binding(BUILD_SCRIPT),
            "page_count": 60, "status": "pass", "driver": file_binding(DRIVER),
            "input_bindings": [file_binding(COVER), file_binding(CROSSREF), file_binding(TARGET), file_binding(bib)],
            "external_dependencies": ["XeLaTeX", "Biber", "makeindex", "Noto CJK fonts", "Fandol 0.3 toolchain fonts"],
            "rights_component_ids": common_rights,
        },
        {
            "id": uid("build-surface/unit-043-combined-checkpoint-pdf"),
            "stable_key": "build-surface/unit-043-combined-checkpoint-pdf",
            "entity_type": "build_surface", "unit_id": unit_id, "kind": "pdf",
            "working_directory": ".",
            "command": "python scripts/build_checkpoint_reader_through_chapter_5.py",
            "artifact_path": rel(COMBINED_PDF), "artifact_binding": file_binding(COMBINED_PDF),
            "log_binding": file_binding(COMBINED_RECEIPT), "build_script": file_binding(COMBINED_SCRIPT),
            "page_count": 385, "status": "pass", "driver": file_binding(COMBINED_SCRIPT),
            "input_bindings": [file_binding(CHAPTER_PDF), file_binding(COMBINED_RECEIPT)],
            "external_dependencies": ["Python", "pypdf", "ReportLab", "Noto Sans fonts"],
            "rights_component_ids": aggregate_rights,
        },
    ]

    qa_specs = [
        ("structure", CHECKER, "Complete Chapter 5 structure, identifiers, mathematics, exercises, hints, and terminology passed."),
        ("chapter-build", CHAPTER_LOG, "Hash-gated 60-page Chapter 5 XeLaTeX/Biber/makeindex build passed."),
        ("combined-build", COMBINED_RECEIPT, "Reader-first 385-page checkpoint through complete Chapter 5 passed 36-component byte validation."),
        ("combined-visual", VISUAL, "All 385 pages were rendered once and inspected through eleven ordered contact sheets."),
        ("rights", COVER, "Attribution, changes, non-endorsement, model provenance, and separate component rights are explicit."),
    ]
    qa_events = []
    for order, (slug, witness, scope) in enumerate(qa_specs, 1):
        key = f"qa/unit-043/{order:02d}-{slug}"
        qa_events.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "qa_event",
                "unit_id": unit_id, "check_type": "admission_gate" if order == 1 else "backend_integrity",
                "result": "pass", "scope": scope, "witness": rel(witness),
                "translation_audit_state": "pass", "build_state": "pass",
                "visual_state": "pass", "witness_binding": file_binding(witness),
            }
        )
    require(len(CORRECTION_SPECS) == 21, "Chapter 5 correction-record census drift")
    require(len({item[0] for item in CORRECTION_SPECS}) == 21, "duplicate Chapter 5 correction ID")
    for order, (correction_id, review_rel, first, last, line, disposition) in enumerate(CORRECTION_SPECS, 1):
        witness = ROOT / review_rel
        key = f"qa/unit-043/correction/{order:02d}-{correction_id.lower()}"
        qa_events.append(
            {
                "id": uid(key), "stable_key": key, "entity_type": "qa_event",
                "unit_id": unit_id, "check_type": "backend_integrity", "result": "pass",
                "scope": (
                    f"{correction_id}: {disposition} "
                    f"Source range {rel(SOURCE)}:{first}-{last}; "
                    f"target range {rel(TARGET)}:{first}-{last}; "
                    f"corrected source line {line} corresponds to target line {line}."
                ),
                "witness": review_rel,
                "translation_audit_state": "pass", "build_state": "pass",
                "visual_state": "pass", "witness_binding": file_binding(witness),
            }
        )

    unit = {
        "id": unit_id, "stable_key": UNIT_KEY, "entity_type": "unit",
        "program_id": program["id"], "course_id": course["id"],
        "resource_id": resource["id"], "edition_id": edition["id"], "order": 43,
        "source_local_id": "chapter5.tex:1-1382; complete Chapter 5",
        "titles": [label("zh-Hans", "第五章 环论初步"), label("id-ID", "Bab 5: Pengantar Teori Gelanggang")],
        "source_language": "zh-Hans", "target_language": "id-ID",
        "source_binding": line_binding(SOURCE, 1, 1382),
        "target_binding": line_binding(TARGET, 1, 1382),
        "section_ids": [item["id"] for item in sections],
        "concept_ids": [item["id"] for item in concepts],
        "prerequisite_ids": [item["id"] for item in prerequisites],
        "rights_component_ids": common_rights,
        "citation_ids": [item["id"] for item in citations],
        "diagram_ids": [item["id"] for item in diagrams],
        "index_entry_ids": [item["id"] for item in index_entries],
        "build_surface_ids": [item["id"] for item in surfaces],
        "qa_event_ids": [item["id"] for item in qa_events],
        "outcome_keys": [item[0] for item in outcomes],
        "surface_counts": {
            "sections": 10, "exercises": 22, "hints": 11,
            "answers": 0, "solutions": 0, "citations": 6,
            "diagrams": 16, "index_entries": 74,
        },
        "translation_state": "visually_checked", "admission_state": "admitted",
    }
    document = {
        "$schema": "../schema/open-math-corpus-unit.schema.v1.json",
        "schema_name": "open-math-corpus-unit", "schema_version": "1.1.0",
        "profile": "curriculum-modular-backend-v0",
        "dataset_id": uid("dataset/unit-043/id-id"),
        "dataset_stable_key": "dataset/unit-043/id-id",
        "id_namespace": copy.deepcopy(base["id_namespace"]),
        "workflow": {
            "responsible_task": uid("task/o013-li-u043-backend"),
            "updated": "2026-08-28", "status": "admitted",
            "admission_state": "admitted", "translation_state": "visually_checked",
            "qa_state": "translation_math_backend_build_combined_visual_pass",
        },
        "program": program, "course": course, "resource": resource, "edition": edition,
        "unit": unit, "sections": sections, "concepts": concepts,
        "prerequisites": prerequisites, "rights": rights, "citations": citations,
        "diagrams": diagrams, "index_entries": index_entries,
        "build_surfaces": surfaces, "qa_events": qa_events,
    }

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(document)
    sys.path.insert(0, str(ROOT / "scripts"))
    import validate_backend as backend_validator
    result = backend_validator.Validation()
    backend_validator.semantic_validation(document, ROOT, result)
    require(not result.errors, "semantic backend validation failed: " + "; ".join(result.errors))
    rendered = backend_validator.render_csvs(document)
    csv_outputs = {
        name: rendered[f"unit-043-{name}.csv"]
        for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
    }
    validation = {
        "schema": "o013-unit-backend-validation-v1", "unit": "O013-LI-U043",
        "result": "pass", "generated": "2026-08-28",
        "authority": {"range": "chapter5.tex:1-1382", "bytes": identity(SOURCE)[0], "sha256": identity(SOURCE)[1]},
        "target": {"range": "chapter5.tex:1-1382", "bytes": identity(TARGET)[0], "sha256": identity(TARGET)[1], "candidate_identical": True},
        "topology": counts, "terminology_rows": 22, "sections": 10,
        "rights_components": 5, "build_surfaces": 2, "qa_events": len(qa_events),
        "correction_records": len(CORRECTION_SPECS),
        "correction_ids": [item[0] for item in CORRECTION_SPECS],
        "translation_review_witnesses": len({item[1] for item in CORRECTION_SPECS}),
        "schema_validation": "pass", "semantic_validation": "pass",
        "csv_projections": 6,
    }
    return document, csv_outputs, validation


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document, csv_outputs, validation = make_backend()
    json_bytes = encode(document)
    validation["backend"] = {"path": rel(OUTPUT), "bytes": len(json_bytes), "sha256": sha(json_bytes)}
    validation["csv"] = {
        name: {"path": rel(CSV_PATHS[name]), "bytes": len(payload), "sha256": sha(payload)}
        for name, payload in csv_outputs.items()
    }
    validation["generator"] = file_binding(Path(__file__))
    validation_bytes = encode(validation)
    expected = {
        OUTPUT: json_bytes, VALIDATION: validation_bytes,
        **{CSV_PATHS[name]: payload for name, payload in csv_outputs.items()},
    }
    if args.check:
        for path, payload in expected.items():
            require(path.is_file() and path.read_bytes() == payload, f"generated output drift: {rel(path)}")
        print(json.dumps({"result": "PASS", "backend": validation["backend"], "csv_projections": 6}, indent=2))
        return 0
    for path, payload in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    print(json.dumps({"result": "PASS_WRITTEN", "backend": validation["backend"], "csv_projections": 6}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
