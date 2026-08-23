#!/usr/bin/env python3
"""Fail-closed structure and mathematics gate for O013 Unit 014."""

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
LINE_START = 766
LINE_END = 909
EXPECTED_SOURCE_BYTES = 10_365
EXPECTED_SOURCE_SHA256 = (
    "930232390be4aed3aea2155ae1779e95eae621bb7b23ea9c6899828b46ce2960"
)
EXPECTED_TARGET_BYTES = 11_655
EXPECTED_TARGET_SHA256 = (
    "5526e8eb99dba9dc3e0eebbd1ddd278eb6343fd50a1d18cf0f6715f09f6e1ed2"
)
EXPECTED_TARGET_SECTION = r"\section{Fungtor Adjoin}\label{sec:adjoint-functor}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_line_span(path: Path) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    if len(lines) < LINE_END:
        raise ValueError(f"{path} has only {len(lines)} physical lines")
    return b"".join(lines[LINE_START - 1 : LINE_END])


def balanced_command_arguments(text: str, command: str) -> list[str]:
    """Return the first mandatory brace argument after every exact command."""

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


def mask_localized_text(formula: str) -> str:
    """Mask translatable balanced \text payloads while preserving \text{op}."""

    output: list[str] = []
    cursor = 0
    marker = r"\text{"
    while True:
        start = formula.find(marker, cursor)
        if start < 0:
            output.append(formula[cursor:])
            return "".join(output)
        output.append(formula[cursor:start])
        pos = start + len(marker)
        depth = 1
        content_start = pos
        while pos < len(formula) and depth:
            escaped = pos > 0 and formula[pos - 1] == "\\"
            if formula[pos] == "{" and not escaped:
                depth += 1
            elif formula[pos] == "}" and not escaped:
                depth -= 1
            pos += 1
        if depth:
            raise ValueError("unbalanced \\text argument in mathematical surface")
        content = formula[content_start : pos - 1]
        if content.strip() == "op":
            output.append(r"\text{op}")
        else:
            output.append(r"\text{<localized>}")
        cursor = pos


def normalized_math(text: str) -> list[str]:
    formulas = INLINE_MATH_RE.findall(text) + DISPLAY_MATH_RE.findall(text)
    formulas += [match[1] for match in MATH_ENV_RE.findall(text)]
    return [re.sub(r"\s+", "", mask_localized_text(formula)) for formula in formulas]


FORMULA_CORRECTIONS = [
    {
        "id": "O013-LI-U014-COR-001",
        "source_line": 785,
        "issue": "The subscript switches from varphi_{V,W} to varphi_{VW} without changing the indexed family.",
        "source": r"\varphi_{VW}:\Hom_{\cate{Vect}(\Bbbk)}(V,DW)\rightiso\Hom_{\cate{Vect}(\Bbbk)^\text{op}}(D^\text{op}V,W)",
        "target": r"\varphi_{V,W}:\Hom_{\cate{Vect}(\Bbbk)}(V,DW)\rightiso\Hom_{\cate{Vect}(\Bbbk)^\text{op}}(D^\text{op}V,W)",
    },
    {
        "id": "O013-LI-U014-COR-002",
        "source_line": 789,
        "issue": "The finite-dimensional restriction is a functor on the opposite finite-dimensional category.",
        "source": r"\cate{Vect}_f(\Bbbk)",
        "target": r"\cate{Vect}_f(\Bbbk)^\text{op}",
    },
    {
        "id": "O013-LI-U014-COR-003",
        "source_line": 789,
        "issue": "The displayed domain uses the inconsistent form Vect(k)_f instead of Vect_f(k).",
        "source": r"\cate{Vect}(\Bbbk)_f^\text{op}\to\cate{Vect}_f(\Bbbk)",
        "target": r"\cate{Vect}_f(\Bbbk)^\text{op}\to\cate{Vect}_f(\Bbbk)",
    },
    {
        "id": "O013-LI-U014-COR-004",
        "source_line": 799,
        "issue": "Counit components belong to objects Y of C_2, not the X-index convention for C_1.",
        "source": r"\varepsilon=(\varepsilon_X)_X:FG\to\identity_{\mathcal{C}_2}",
        "target": r"\varepsilon=(\varepsilon_Y)_{Y\in\Obj(\mathcal{C}_2)}:FG\to\identity_{\mathcal{C}_2}",
    },
]


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
    if len(target_bytes) != EXPECTED_TARGET_BYTES:
        failures.append("target byte count differs from reviewed boundary")
    if sha256(target_bytes) != EXPECTED_TARGET_SHA256:
        failures.append("target SHA-256 differs from reviewed boundary")

    source_math = normalized_math(source)
    target_math = normalized_math(target)
    # Indonesian requires a conjunction between the two independently natural
    # transformations.  The target therefore splits the source's single
    # ``$\eta, \varepsilon$`` surface into ``$\eta$ dan $\varepsilon$``.
    # Rejoin that one explicitly anchored language edit only for mathematical
    # topology comparison; retain the two reader-facing math surfaces.
    language_segmentation_source = r"naturalitas $\eta$ dan $\varepsilon$"
    language_segmentation_target = r"naturalitas $\eta, \varepsilon$"
    target_comparison_text = target.replace(
        language_segmentation_source,
        language_segmentation_target,
    )
    language_segmentation_applied = target_comparison_text != target
    if not language_segmentation_applied:
        failures.append("controlled Indonesian math segmentation is missing")
    target_for_comparison = normalized_math(target_comparison_text)
    correction_results: list[dict[str, object]] = []
    for correction in FORMULA_CORRECTIONS:
        source_formula = correction["source"]
        target_formula = correction["target"]
        applied = (
            source_math.count(source_formula) >= 1
            and target_math.count(target_formula) >= 1
            and target_formula in target_for_comparison
        )
        if applied:
            target_for_comparison[target_for_comparison.index(target_formula)] = source_formula
        else:
            failures.append(f"declared correction is missing: {correction['id']}")
        correction_results.append(
            {
                "id": correction["id"],
                "source_line": correction["source_line"],
                "issue": correction["issue"],
                "applied": applied,
            }
        )

    math_exact = Counter(source_math) == Counter(target_math)
    math_equivalent = Counter(source_math) == Counter(target_for_comparison)
    if len(source_math) != 99 or len(target_math) != 100:
        failures.append("mathematical surface count is not the frozen 99/100")
    if not math_equivalent:
        failures.append("normalized mathematics differs beyond declared corrections")

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

    source_cite_signatures = re.findall(r"\\cite(\[[^]]+\])?\{([^}]+)\}", source)
    target_cite_signatures = re.findall(r"\\cite(\[[^]]+\])?\{([^}]+)\}", target)
    if source_cite_signatures != target_cite_signatures:
        failures.append("citation options or keys differ")

    source_indexes = balanced_command_arguments(source, r"\index")
    target_indexes = balanced_command_arguments(target, r"\index")
    index_topology_exact = (
        len(source_indexes) == len(target_indexes)
        and [[c for c in entry if c in "@!"] for entry in source_indexes]
        == [[c for c in entry if c in "@!"] for entry in target_indexes]
    )
    if not index_topology_exact:
        failures.append("index cardinality or @/! topology differs")

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
    if "funktor" in target.lower():
        failures.append("target contains the rejected spelling funktor")
    for term in (
        "pasangan adjoin",
        "fungtor adjoin kanan",
        "fungtor adjoin kiri",
        "kounit",
        "2-sel",
        "identitas segitiga",
    ):
        if term not in target:
            failures.append(f"controlled terminology is missing: {term}")

    target_lines = TARGET.read_text(encoding="utf-8").splitlines()
    next_boundary_ok = (
        len(target_lines) > LINE_END
        and target_lines[LINE_END].startswith(r"\begin{example}\label{eg:top-adjunction}")
    )
    if not next_boundary_ok:
        failures.append("line 910 is no longer the frozen next example boundary")

    report = {
        "schema_version": "unit-014-structure-gate-v1",
        "unit_id": "unit-014-bab-2-fungtor-adjoin-dasar",
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
        "indonesian_math_segmentation_applied": language_segmentation_applied,
        "mathematics_multiset_exact_without_corrections": math_exact,
        "mathematics_multiset_equivalent_after_declared_corrections": math_equivalent,
        "environment_sequence_exact": environments_exact,
        "environment_begin_count": len(source_begin),
        "commands": command_results,
        "citation_signatures_exact": source_cite_signatures == target_cite_signatures,
        "index_source_count": len(source_indexes),
        "index_target_count": len(target_indexes),
        "index_topology_exact": index_topology_exact,
        "literals": literal_results,
        "han_residue_count": len(han_residue),
        "next_boundary_ok": next_boundary_ok,
        "declared_source_corrections": correction_results,
        "status": "pass" if not failures else "fail",
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
