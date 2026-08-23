
#!/usr/bin/env python3
"""Fail-closed structural and mathematics-topology gate for O013 Unit 013.

The gate is safe to run while translation is in progress: it never writes and
reports every unmet condition in JSON.  Passing means only that the frozen
source/target span is structurally faithful and free of untranslated Han text;
build, visual, language, rights, backend, and admission gates remain separate.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


LANE = Path(__file__).resolve().parents[1]
SOURCE = (
    LANE
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter2.tex"
)
TARGET = LANE / "repo" / "source" / "chapter2.tex"
LINE_START = 678
LINE_END = 765
EXPECTED_SOURCE_BYTES = 7_413
EXPECTED_SOURCE_SHA256 = (
    "9b30201ad8df7822e2e6bb20080097bff6ef663c763653f859f6ab4e028b2928"
)
EXPECTED_TARGET_SECTION = (
    r"\section{Fungtor Representabel}\label{sec:representable-functors}"
)
SOURCE_FORMULA_CORRECTION = r"\phi:\Hom_{\mathcal{C}}(\cdot,\Omega)\rightisoP"
TARGET_FORMULA_CORRECTION = r"\phi:\Hom_{\cate{Set}}(\cdot,\Omega)\rightisoP"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_line_span(path: Path) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    if len(lines) < LINE_END:
        raise ValueError(f"{path} has only {len(lines)} physical lines")
    return b"".join(lines[LINE_START - 1 : LINE_END])


def balanced_command_arguments(text: str, command: str) -> list[str]:
    """Return the first mandatory brace argument after each exact command."""

    results: list[str] = []
    cursor = 0
    while True:
        start = text.find(command, cursor)
        if start < 0:
            return results
        pos = start + len(command)
        if pos < len(text) and text[pos].isalpha():
            cursor = pos
            continue
        while pos < len(text) and text[pos].isspace():
            pos += 1
        while pos < len(text) and text[pos] == "[":
            depth = 1
            pos += 1
            while pos < len(text) and depth:
                escaped = pos > 0 and text[pos - 1] == "\\"
                if text[pos] == "[" and not escaped:
                    depth += 1
                elif text[pos] == "]" and not escaped:
                    depth -= 1
                pos += 1
            while pos < len(text) and text[pos].isspace():
                pos += 1
        if pos >= len(text) or text[pos] != "{":
            cursor = max(pos, start + 1)
            continue
        depth = 1
        arg_start = pos + 1
        pos += 1
        while pos < len(text) and depth:
            escaped = pos > 0 and text[pos - 1] == "\\"
            if text[pos] == "{" and not escaped:
                depth += 1
            elif text[pos] == "}" and not escaped:
                depth -= 1
            pos += 1
        if depth:
            raise ValueError(f"unbalanced argument for {command} at offset {start}")
        results.append(text[arg_start : pos - 1])
        cursor = pos


INLINE_MATH_RE = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
MATH_ENV_RE = re.compile(
    r"\\begin\{(align\*?|gather\*?|equation\*?)\}(.*?)"
    r"\\end\{\1\}",
    re.DOTALL,
)
TEXT_COMMAND_RE = re.compile(r"\\text\{[^{}]*\}")


def normalized_math(text: str) -> list[str]:
    formulas = INLINE_MATH_RE.findall(text) + DISPLAY_MATH_RE.findall(text)
    formulas += [match[1] for match in MATH_ENV_RE.findall(text)]
    normalized: list[str] = []
    for formula in formulas:
        previous = None
        while previous != formula:
            previous = formula
            formula = TEXT_COMMAND_RE.sub(r"\\text{<localized>}", formula)
        normalized.append(re.sub(r"\s+", "", formula))
    return normalized


def environment_sequence(text: str, kind: str) -> list[str]:
    return re.findall(rf"\\{kind}\{{([^}}]+)\}}", text)


def brace_balance(text: str) -> int:
    balance = 0
    for index, char in enumerate(text):
        if index and text[index - 1] == "\\":
            continue
        if char == "{":
            balance += 1
        elif char == "}":
            balance -= 1
            if balance < 0:
                return balance
    return balance


def main() -> None:
    source_bytes = exact_line_span(SOURCE)
    target_bytes = exact_line_span(TARGET)
    source = source_bytes.decode("utf-8")
    target = target_bytes.decode("utf-8")
    failures: list[str] = []

    if len(source_bytes) != EXPECTED_SOURCE_BYTES:
        failures.append("source byte count differs from frozen boundary")
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        failures.append("source SHA-256 differs from frozen boundary")

    source_math = normalized_math(source)
    target_math = normalized_math(target)
    math_exact_without_corrections = Counter(source_math) == Counter(target_math)
    formula_correction_applied = (
        source_math.count(SOURCE_FORMULA_CORRECTION) == 1
        and target_math.count(TARGET_FORMULA_CORRECTION) == 1
        and target_math.count(SOURCE_FORMULA_CORRECTION) == 0
    )
    target_math_for_comparison = list(target_math)
    if formula_correction_applied:
        target_math_for_comparison[
            target_math_for_comparison.index(TARGET_FORMULA_CORRECTION)
        ] = SOURCE_FORMULA_CORRECTION
    else:
        failures.append("declared Hom category correction is missing or duplicated")
    math_equivalent = Counter(source_math) == Counter(target_math_for_comparison)
    if not math_equivalent:
        failures.append("normalized mathematics differs beyond declared correction")

    cohomology_correction_applied = (
        "同调函子" in source
        and "fungtor kohomologi" in target
        and "fungtor homologi" not in target
    )
    if not cohomology_correction_applied:
        failures.append("declared Eilenberg-MacLane cohomology correction is missing")

    source_begin = environment_sequence(source, "begin")
    target_begin = environment_sequence(target, "begin")
    source_end = environment_sequence(source, "end")
    target_end = environment_sequence(target, "end")
    environments_exact = source_begin == target_begin and source_end == target_end
    if not environments_exact:
        failures.append("environment sequence differs")
    if Counter(source_begin) != Counter(source_end):
        failures.append("source environment multiset is unbalanced")
    if Counter(target_begin) != Counter(target_end):
        failures.append("target environment multiset is unbalanced")

    command_results: dict[str, dict[str, object]] = {}
    for name, command in {
        "labels": r"\label",
        "references": r"\ref",
        "equation_references": r"\eqref",
        "citations": r"\cite",
    }.items():
        source_args = balanced_command_arguments(source, command)
        target_args = balanced_command_arguments(target, command)
        exact = source_args == target_args
        command_results[name] = {
            "source_count": len(source_args),
            "target_count": len(target_args),
            "exact_argument_sequence": exact,
        }
        if not exact:
            failures.append(f"{name} argument sequence differs")

    source_indexes = balanced_command_arguments(source, r"\index")
    target_indexes = balanced_command_arguments(target, r"\index")
    if len(source_indexes) != len(target_indexes):
        failures.append("index command cardinality differs")
    source_index_math = [
        formula for entry in source_indexes for formula in normalized_math(entry)
    ]
    target_index_math = [
        formula for entry in target_indexes for formula in normalized_math(entry)
    ]
    index_math_exact = Counter(source_index_math) == Counter(target_index_math)
    if not index_math_exact:
        failures.append("symbol-index mathematics differs")

    literal_results: dict[str, dict[str, int]] = {}
    for name, token in {
        "items": r"\item",
        "emphasis": r"\emph{",
        "tikzcd_arrows": r"\arrow",
        "tikz_draws": r"\draw",
        "tikz_coordinates": r"\coordinate",
        "tikz_nodes": r"\node",
    }.items():
        source_count = source.count(token)
        target_count = target.count(token)
        literal_results[name] = {
            "source_count": source_count,
            "target_count": target_count,
        }
        if source_count != target_count:
            failures.append(f"{name} cardinality differs")

    han_residue = re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", target)
    if han_residue:
        failures.append(f"target contains {len(han_residue)} Han characters")
    if brace_balance(target) != 0:
        failures.append("target brace balance is nonzero")
    if re.search(r"\$`|`\$", target):
        failures.append("target contains a suspicious backtick adjacent to mathematics")
    if not target.startswith(EXPECTED_TARGET_SECTION):
        failures.append("target section heading is not the controlled Indonesian heading")

    target_lines = TARGET.read_text(encoding="utf-8").splitlines()
    next_boundary_ok = (
        len(target_lines) > LINE_END
        and target_lines[LINE_END].startswith(r"\section{")
    )
    if not next_boundary_ok:
        failures.append("line 766 is no longer the next section boundary")

    report = {
        "schema_version": "unit-013-structure-gate-v1",
        "unit_id": "unit-013-bab-2-fungtor-representabel-dan-lema-yoneda",
        "source_path": str(SOURCE.relative_to(LANE)).replace("\\", "/"),
        "target_path": str(TARGET.relative_to(LANE)).replace("\\", "/"),
        "line_start": LINE_START,
        "line_end": LINE_END,
        "line_count": LINE_END - LINE_START + 1,
        "source_bytes": len(source_bytes),
        "source_sha256": sha256(source_bytes),
        "target_bytes": len(target_bytes),
        "target_sha256": sha256(target_bytes),
        "mathematics_source_count": len(source_math),
        "mathematics_target_count": len(target_math),
        "mathematics_multiset_exact_without_corrections": math_exact_without_corrections,
        "mathematics_multiset_equivalent_after_declared_correction": math_equivalent,
        "environment_sequence_exact": environments_exact,
        "commands": command_results,
        "index_source_count": len(source_indexes),
        "index_target_count": len(target_indexes),
        "index_symbol_math_exact": index_math_exact,
        "literals": literal_results,
        "han_residue_count": len(han_residue),
        "next_boundary_ok": next_boundary_ok,
        "declared_source_corrections": [
            {
                "id": "O013-LI-U013-COR-001",
                "source_line": 753,
                "issue": "The power-set example writes Hom_C although its domain category is Set.",
                "target": "Hom_Set",
                "applied": formula_correction_applied,
            },
            {
                "id": "O013-LI-U013-COR-002",
                "source_line": 762,
                "issue": "Eilenberg-MacLane spaces represent cohomology, not homology.",
                "target": "fungtor kohomologi",
                "applied": cohomology_correction_applied,
            },
        ],
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
