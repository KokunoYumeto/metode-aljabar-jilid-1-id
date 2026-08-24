#!/usr/bin/env python3
"""Regenerate and byte-check the canonical Unit 023 backend round trip."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import generate_unit_023_backend as gen


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/generate_unit_023_backend.py"
VALIDATOR = ROOT / "scripts/validate_backend.py"
SCHEMA = ROOT / "backend/schema/open-math-corpus-unit.schema.v1.json"
DATA = ROOT / "backend/data/unit-023-bab-3-sekilas-tentang-2-kategori.json"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
STRUCTURE_QA = ROOT / "qa/unit-023-evidence/structure-and-pdf-qa.json"
VISUAL_REVIEW = ROOT / "qa/UNIT_023_VISUAL_QA_20260824.md"
MATH_REVIEW = ROOT / "qa/UNIT_023_MATH_STRUCTURE_AUDIT_20260824.md"
TERMINOLOGY_AUDIT = ROOT / "qa/UNIT_023_TERMINOLOGY_AUDIT_20260824.md"
EVIDENCE = ROOT / "qa/unit-023-evidence/backend-validation.json"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
CSV_FILES = tuple(
    ROOT / f"backend/csv/unit-023-{name}.csv"
    for name in ("bindings", "entities", "qa", "relations", "rights", "surfaces")
)
EXPECTED_PREFIX_COUNTS = {
    "surface/unit-023/environment/": 25,
    "surface/unit-023/label/": 2,
    "surface/unit-023/reference/ordinary/": 16,
    "surface/unit-023/reference/equation/": 0,
    "surface/unit-023/citation-occurrence/": 0,
    "surface/unit-023/item/": 19,
    "surface/unit-023/formula/inline/": 156,
    "surface/unit-023/formula/display-bracket/": 11,
    "surface/unit-023/formula/display-environment/": 0,
    "surface/unit-023/diagram-arrow/": 64,
    "surface/unit-023/diagram-node/": 0,
    "surface/unit-023/diagram-coordinate/": 0,
    "surface/unit-023/diagram-draw/": 0,
    "surface/unit-023/diagram-path/": 0,
    "surface/unit-023/diagram-edge/": 0,
    "surface/unit-023/diagram-braid/": 0,
    "surface/unit-023/diagram-hline/": 0,
    "surface/unit-023/terminology-row/": 20,
    "editorial/o013-li-u023-ed-001": 1,
}
EXPECTED_RIGHTS = {
    "rights/principal-cc-by-4.0": True,
    "rights/lanzhou-cc-by-sa-3.0": False,
    "rights/ajbook-fragment-cc-by-sa-3.0": True,
    "rights/noto-fonts-ofl-1.1": True,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identities(paths: tuple[Path, ...]) -> dict[str, tuple[int, str]]:
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(
            "Unit 023 round-trip validation refused: missing canonical outputs; "
            "run the admission-gated generator after final QA:\n  - "
            + "\n  - ".join(path.relative_to(ROOT).as_posix() for path in missing)
        )
    return {
        path.relative_to(ROOT).as_posix(): (path.stat().st_size, sha256(path))
        for path in paths
    }


def run(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode:
        raise SystemExit(
            "Unit 023 round-trip validation refused:\n"
            + completed.stdout
            + completed.stderr
        )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("Unit 023 round-trip validation refused: " + message)


def audit_bindings(value: object) -> dict[str, object]:
    """Validate every local full-file and optional line-span binding recursively."""

    bindings: list[dict[str, object]] = []

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if {"path", "bytes", "sha256"}.issubset(node):
                bindings.append(node)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    span_count = 0
    full_count = 0
    paths: set[str] = set()
    for binding in bindings:
        relative = str(binding["path"])
        path = ROOT / relative
        require(path.is_file(), f"bound file missing: {relative}")
        require(
            (int(binding["bytes"]), str(binding["sha256"]))
            == (path.stat().st_size, sha256(path)),
            f"full-file binding drift: {relative}",
        )
        paths.add(relative)
        has_span = any(
            key in binding
            for key in ("line_start", "line_end", "span_sha256", "span_hash_algorithm")
        )
        if has_span:
            require(
                {"line_start", "line_end", "span_sha256", "span_hash_algorithm"}.issubset(binding),
                f"incomplete line-span binding: {relative}",
            )
            first = int(binding["line_start"])
            last = int(binding["line_end"])
            require(1 <= first <= last, f"invalid line span: {relative}:{first}-{last}")
            require(
                binding["span_hash_algorithm"] == "sha256-utf8-lines-lf-v1",
                f"unexpected span algorithm: {relative}:{first}-{last}",
            )
            require(
                sha256_bytes(gen.normalized_span(relative, first, last))
                == binding["span_sha256"],
                f"line-span binding drift: {relative}:{first}-{last}",
            )
            span_count += 1
        else:
            full_count += 1
    require(bindings, "no bindings found")
    return {
        "occurrences": len(bindings),
        "full_file_occurrences": full_count,
        "line_span_occurrences": span_count,
        "unique_paths": len(paths),
        "paths": sorted(paths),
    }


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    canonical_paths = (DATA, *CSV_FILES)
    before = identities(canonical_paths)
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_one = identities(canonical_paths)
    require(
        before == after_generation_one,
        "first deterministic regeneration changed "
        + ", ".join(
            sorted(key for key in before if before[key] != after_generation_one[key])
        ),
    )
    run([sys.executable, "-B", str(GENERATOR)])
    after_generation_two = identities(canonical_paths)
    require(
        after_generation_one == after_generation_two,
        "second deterministic regeneration changed "
        + ", ".join(
            sorted(
                key
                for key in after_generation_one
                if after_generation_one[key] != after_generation_two[key]
            )
        ),
    )
    run(
        [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "--lane-root",
            str(ROOT),
            "--data",
            str(DATA),
            "--schema",
            str(SCHEMA),
            "--csv-dir",
            str(ROOT / "backend/csv"),
        ]
    )
    after_validation = identities(canonical_paths)
    require(after_generation_two == after_validation, "shared validation mutated outputs")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    require(data["dataset_stable_key"] == "dataset/unit-023/id-id", "dataset key drift")
    unit = data["unit"]
    require(
        unit["stable_key"] == "unit/bab-3-sekilas-tentang-2-kategori",
        "unit key drift",
    )
    require(unit["order"] == 23, "unit order drift")
    require(unit["source_local_id"] == "chapter3.tex:723-872", "authority range drift")
    require(
        unit["source_binding"]["line_start"] == 723
        and unit["source_binding"]["line_end"] == 872,
        "source binding drift",
    )
    require(
        unit["target_binding"]["line_start"] == 722
        and unit["target_binding"]["line_end"] == 871,
        "target binding drift",
    )
    require(unit["source_binding"]["span_sha256"] == gen.SOURCE_SPAN[1], "source span hash drift")
    require(unit["target_binding"]["span_sha256"] == gen.TARGET_SPAN[1], "target span hash drift")
    require(
        (unit["target_binding"]["bytes"], unit["target_binding"]["sha256"])
        == gen.TARGET_FULL,
        "target full-file admission identity drift",
    )
    require(unit["translation_state"] == "visually_checked", "translation state drift")
    require(unit["admission_state"] == "admitted", "admission state drift")

    require(len(data["sections"]) == 1, "expected one contiguous section")
    section = data["sections"][0]
    require(
        section["stable_key"]
        == "unit/bab-3-sekilas-tentang-2-kategori/section/sekilas-tentang-2-kategori",
        "section key drift",
    )
    require(
        section["source_binding"]["line_start"] == 723
        and section["source_binding"]["line_end"] == 872
        and section["target_binding"]["line_start"] == 722
        and section["target_binding"]["line_end"] == 871,
        "section boundary drift",
    )

    concepts = data["concepts"]
    concept_keys = tuple(item["stable_key"] for item in concepts)
    require(
        len(concept_keys) == 343,
        f"expected 343 concept-compatible entities, got {len(concept_keys)}",
    )
    require(len(concept_keys) == len(set(concept_keys)), "duplicate concept stable key")
    for prefix, expected in EXPECTED_PREFIX_COUNTS.items():
        actual = sum(key.startswith(prefix) for key in concept_keys)
        require(actual == expected, f"{prefix} expected {expected}, got {actual}")
    require(
        not any("/answer/" in key or "/solution/" in key or "/hint/" in key for key in concept_keys),
        "invented answer, solution, or hint entity",
    )
    editorial_expectations = {
        "editorial/o013-li-u023-ed-001": ("865", "864", "pasangan adjoin"),
    }
    concepts_by_key = {item["stable_key"]: item for item in concepts}
    for key, tokens in editorial_expectations.items():
        text = " ".join(label["text"] for label in concepts_by_key[key]["labels"])
        require(gen.REVIEW in text, f"{key} evidence path drift")
        for token in tokens:
            require(token in text, f"{key} lacks {token!r}")

    citations = data["citations"]
    require(citations == [], "Unit 023 must contain no native citation record")

    diagrams = data["diagrams"]
    require(len(diagrams) == 14, "expected fourteen diagrams")
    require(
        all(item["source_format"] == "tikzcd" for item in diagrams),
        "fourteen-tikzcd split drift",
    )
    require(
        tuple(
            (
                item["source_format"],
                item["source_occurrence_index"],
                item["source_binding"]["line_start"] - gen.SOURCE_START + 1,
                item["source_binding"]["line_end"] - gen.SOURCE_START + 1,
            )
            for item in diagrams
        )
        == gen.DIAGRAM_SPECS,
        "diagram occurrence bindings drift",
    )
    require(
        all(item["state"] == "audited_preserved" for item in diagrams),
        "diagram audit state drift",
    )

    indexes = data["index_entries"]
    require(len(indexes) == 3, "expected three localized index entries")
    require(
        tuple((item["target_binding"]["line_start"], item["target_key"]) for item in indexes)
        == tuple(
            (gen.TARGET_START + line - 1, target_key)
            for _, _, line, target_key in gen.INDEX_SPECS
        ),
        "localized index topology drift",
    )
    require(
        all(
            item["provenance_state"] == "source_key_preserved_target_key_localized"
            for item in indexes
        ),
        "index provenance drift",
    )

    require(
        unit["surface_counts"]
        == {
            "sections": 1,
            "exercises": 0,
            "hints": 0,
            "answers": 0,
            "solutions": 0,
            "citations": 0,
            "diagrams": 14,
            "index_entries": 3,
        },
        "native/compatibility surface-count drift",
    )

    rights = {item["stable_key"]: item for item in data["rights"]}
    require(set(rights) == set(EXPECTED_RIGHTS), "rights-component inventory drift")
    require(
        {key: rights[key]["applies_to_unit"] for key in rights} == EXPECTED_RIGHTS,
        "rights applicability drift",
    )
    principal_paths = {item["path"] for item in rights["rights/principal-cc-by-4.0"]["bindings"]}
    require(
        principal_paths == {gen.SOURCE, "repo/source/LICENSE", "repo/source/ccby.png"},
        "principal-rights source/license binding drift",
    )
    rights_id_to_key = {item["id"]: key for key, item in rights.items()}
    require(
        {rights_id_to_key[item] for item in unit["rights_component_ids"]}
        == {
            "rights/principal-cc-by-4.0",
            "rights/ajbook-fragment-cc-by-sa-3.0",
            "rights/noto-fonts-ofl-1.1",
        },
        "unit rights flattening or Lanzhou applicability drift",
    )

    require(len(data["build_surfaces"]) == 1, "build-surface count drift")
    build = data["build_surfaces"][0]
    require(build["artifact_path"] == gen.ARTIFACT and build["status"] == "pass", "artifact path/state drift")
    artifact_path = ROOT / gen.ARTIFACT
    require(
        build["artifact_binding"]["bytes"] == artifact_path.stat().st_size
        and build["artifact_binding"]["sha256"] == sha256(artifact_path),
        "live artifact identity drift",
    )
    require(
        isinstance(build["page_count"], int) and build["page_count"] >= 1,
        "final reader page count is invalid",
    )
    input_paths = {item["path"] for item in build["input_bindings"]}
    require(gen.TARGET in input_paths, "canonical integrated reader input is not bound")
    require(
        gen.CANDIDATE not in input_paths,
        "public reader build must not depend on the isolated review candidate",
    )

    qa_by_key = {item["stable_key"]: item for item in data["qa_events"]}
    require(
        set(qa_by_key)
        == {
            "qa/unit-023/admission-gate",
            "qa/unit-023/source-review",
            "qa/unit-023/math-structure-review",
            "qa/unit-023/editorial-normalization",
            "qa/unit-023/structure-check",
            "qa/unit-023/render-replay",
            "qa/unit-023/all-page-visual-review",
            "qa/unit-023/terminology-control",
            "qa/unit-023/terminology-evidence",
        },
        "QA event topology drift",
    )
    require(
        all(
            item["result"] == "pass"
            and item["translation_audit_state"] == "pass"
            and item["build_state"] == "pass"
            and item["visual_state"] == "pass"
            for item in qa_by_key.values()
        ),
        "QA pass-state drift",
    )
    admission_scope = qa_by_key["qa/unit-023/admission-gate"]["scope"]
    for token in (
        MODEL,
        "O013-LI-U023-ED-001",
        "twenty-five environment pairs",
        "sixty-four tikzcd arrows",
        "no TikZ nodes",
        "Exactly twenty applicable terminology rows",
    ):
        require(token in admission_scope, f"admission provenance/topology token missing: {token}")

    bound_witnesses = {
        "qa/unit-023/terminology-control": GLOSSARY,
        "qa/unit-023/math-structure-review": MATH_REVIEW,
        "qa/unit-023/editorial-normalization": ROOT / gen.REVIEW,
        "qa/unit-023/terminology-evidence": TERMINOLOGY_AUDIT,
    }
    for key, path in bound_witnesses.items():
        binding = qa_by_key[key]["witness_binding"]
        require(
            binding["path"] == path.relative_to(ROOT).as_posix()
            and binding["bytes"] == path.stat().st_size
            and binding["sha256"] == sha256(path),
            f"{key} witness binding drift",
        )

    binding_audit = audit_bindings(data)
    require(
        binding_audit["line_span_occurrences"] >= 1,
        "no source/target line-span bindings were audited",
    )
    require(
        gen.SOURCE in binding_audit["paths"] and gen.TARGET in binding_audit["paths"],
        "authority or canonical target absent from binding audit",
    )

    report = {
        "status": "PASS",
        "unit": "unit-023-bab-3-sekilas-tentang-2-kategori",
        "authority": "chapter3.tex:723-872",
        "target": "chapter3.tex:722-871",
        "data": DATA.relative_to(ROOT).as_posix(),
        "schema": SCHEMA.relative_to(ROOT).as_posix(),
        "provenance_model": MODEL,
        "artifact": {
            "path": gen.ARTIFACT,
            "pages": build["page_count"],
            "bytes": artifact_path.stat().st_size,
            "sha256": sha256(artifact_path),
        },
        "counts": {
            "concepts": len(concepts),
            "environments": 25,
            "labels": 2,
            "ordinary_references": 16,
            "equation_references": 0,
            "citation_occurrences": 0,
            "native_bibliography_records": 0,
            "items": 19,
            "inline_formulae": 156,
            "bracket_display_formulae": 11,
            "environment_display_formulae": 0,
            "tikzcd": 14,
            "tikzpicture": 0,
            "arrows": 64,
            "nodes": 0,
            "coordinates": 0,
            "draws": 0,
            "paths": 0,
            "edges": 0,
            "braids": 0,
            "hlines": 0,
            "index_entries": 3,
            "terminology_rows": 20,
            "editorial_normalizations": 1,
            "csv_projections": 6,
        },
        "checks": {
            "deterministic_regeneration_one": "PASS",
            "deterministic_regeneration_two": "PASS",
            "shared_schema_and_uuidv5": "PASS",
            "source_candidate_target_line_boundary": "PASS",
            "protected_surface_topology": "PASS",
            "editorial_normalization_provenance": "PASS",
            "component_rights": "PASS",
            "build_and_visual_bindings": "PASS",
            "terminology_binding": "PASS",
            "all_full_file_and_line_span_bindings": "PASS",
            "validation_mutated_outputs": False,
        },
        "binding_audit": binding_audit,
        "identities": {
            key: {"bytes": value[0], "sha256": value[1]}
            for key, value in after_validation.items()
        },
        "bound_inputs": {
            path.relative_to(ROOT).as_posix(): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in (
                GLOSSARY,
                STRUCTURE_QA,
                VISUAL_REVIEW,
                MATH_REVIEW,
                ROOT / gen.REVIEW,
                TERMINOLOGY_AUDIT,
            )
        },
        "tools": {
            GENERATOR.relative_to(ROOT).as_posix(): {
                "bytes": GENERATOR.stat().st_size,
                "sha256": sha256(GENERATOR),
            },
            Path(__file__).resolve().relative_to(ROOT).as_posix(): {
                "bytes": Path(__file__).resolve().stat().st_size,
                "sha256": sha256(Path(__file__).resolve()),
            },
        },
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
