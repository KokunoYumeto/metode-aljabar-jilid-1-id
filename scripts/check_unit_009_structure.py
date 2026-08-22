#!/usr/bin/env python3
"""Exact structural and mathematics-topology gate for O013 Unit 009."""

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
LINE_START = 39
LINE_END = 198
EXPECTED_SOURCE_BYTES = 16_442
EXPECTED_SOURCE_SHA256 = (
    "1fa6ecc8f3ec477611f05ddd07297f9e115b7bb118e5fd5be4b7981cde7747ae"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_line_span(path: Path) -> bytes:
    lines = path.read_bytes().splitlines(keepends=True)
    if len(lines) < LINE_END:
        raise ValueError(f"{path} has only {len(lines)} physical lines")
    return b"".join(lines[LINE_START - 1 : LINE_END])


def balanced_command_arguments(text: str, command: str) -> list[str]:
    """Return the first mandatory brace argument after each command token."""

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
        if pos < len(text) and text[pos] == "[":
            depth = 1
            pos += 1
            while pos < len(text) and depth:
                if text[pos] == "[" and text[pos - 1] != "\\":
                    depth += 1
                elif text[pos] == "]" and text[pos - 1] != "\\":
                    depth -= 1
                pos += 1
            while pos < len(text) and text[pos].isspace():
                pos += 1
        if pos >= len(text) or text[pos] != "{":
            cursor = pos
            continue
        depth = 1
        arg_start = pos + 1
        pos += 1
        while pos < len(text) and depth:
            char = text[pos]
            escaped = pos > 0 and text[pos - 1] == "\\"
            if char == "{" and not escaped:
                depth += 1
            elif char == "}" and not escaped:
                depth -= 1
            pos += 1
        if depth:
            raise ValueError(f"unbalanced argument for {command} at offset {start}")
        results.append(text[arg_start : pos - 1])
        cursor = pos


INLINE_MATH_RE = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
ALIGN_MATH_RE = re.compile(r"\\begin\{align\*\}(.*?)\\end\{align\*\}", re.DOTALL)
TEXT_COMMAND_RE = re.compile(r"\\text\{[^{}]*\}")


def normalized_math(text: str) -> list[str]:
    formulas = (
        INLINE_MATH_RE.findall(text)
        + DISPLAY_MATH_RE.findall(text)
        + ALIGN_MATH_RE.findall(text)
    )
    normalized: list[str] = []
    for formula in formulas:
        formula = TEXT_COMMAND_RE.sub(r"\\text{<localized>}", formula)
        formula = re.sub(r"\s+", "", formula)
        normalized.append(formula)
    return normalized


def environment_sequence(text: str, kind: str) -> list[str]:
    return re.findall(rf"\\{kind}\{{([^}}]+)\}}", text)


def literal_count(text: str, token: str) -> int:
    return text.count(token)


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
    math_multiset_exact = Counter(source_math) == Counter(target_math)
    if not math_multiset_exact:
        failures.append("normalized mathematics multiset differs")

    source_begin = environment_sequence(source, "begin")
    target_begin = environment_sequence(target, "begin")
    source_end = environment_sequence(source, "end")
    target_end = environment_sequence(target, "end")
    if source_begin != target_begin or source_end != target_end:
        failures.append("environment sequence differs")
    if source_begin != list(reversed(source_end)) and Counter(source_begin) != Counter(
        source_end
    ):
        failures.append("source environment multiset is unbalanced")
    if Counter(target_begin) != Counter(target_end):
        failures.append("target environment multiset is unbalanced")

    command_checks = {
        "labels": r"\label",
        "references": r"\ref",
        "citations": r"\cite",
    }
    command_results: dict[str, dict[str, object]] = {}
    for name, command in command_checks.items():
        source_args = balanced_command_arguments(source, command)
        target_args = balanced_command_arguments(target, command)
        command_results[name] = {
            "source_count": len(source_args),
            "target_count": len(target_args),
            "exact_argument_sequence": source_args == target_args,
        }
        if source_args != target_args:
            failures.append(f"{name} argument sequence differs")

    source_indexes = balanced_command_arguments(source, r"\index")
    target_indexes = balanced_command_arguments(target, r"\index")
    if len(source_indexes) != len(target_indexes):
        failures.append("index command cardinality differs")
    source_symbol_math = [
        formula for entry in source_indexes for formula in normalized_math(entry)
    ]
    target_symbol_math = [
        formula for entry in target_indexes for formula in normalized_math(entry)
    ]
    symbol_index_math_exact = Counter(source_symbol_math) == Counter(
        target_symbol_math
    )
    if not symbol_index_math_exact:
        failures.append("symbol-index mathematics differs")

    literal_tokens = {
        "items": r"\item",
        "emphasis": r"\emph{",
        "tikzcd_arrows": r"\arrow",
        "tikz_draws": r"\draw",
        "tikz_coordinates": r"\coordinate",
        "tikz_nodes": r"\node",
    }
    literal_results: dict[str, dict[str, int]] = {}
    for name, token in literal_tokens.items():
        source_count = literal_count(source, token)
        target_count = literal_count(target, token)
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

    clarification_text = "morfisme identitas dan panah komposit tidak digambar"
    clarification_applied = clarification_text in target
    if not clarification_applied:
        failures.append("required disclosed line-112 clarification is absent")

    expected_cardinality = {
        "labels": 7,
        "references": 10,
        "citations": 5,
        "indexes": 31,
        "items": 28,
        "emphasis": 18,
        "tikzcd_arrows": 11,
    }
    observed = {
        "labels": command_results["labels"]["target_count"],
        "references": command_results["references"]["target_count"],
        "citations": command_results["citations"]["target_count"],
        "indexes": len(target_indexes),
        "items": literal_results["items"]["target_count"],
        "emphasis": literal_results["emphasis"]["target_count"],
        "tikzcd_arrows": literal_results["tikzcd_arrows"]["target_count"],
    }
    if observed != expected_cardinality:
        failures.append("target cardinality differs from frozen source census")

    result = {
        "gate": "unit-009-structure-v1",
        "source": {
            "path": str(SOURCE.relative_to(LANE)),
            "line_start": LINE_START,
            "line_end": LINE_END,
            "bytes": len(source_bytes),
            "sha256": sha256(source_bytes),
        },
        "target": {
            "path": str(TARGET.relative_to(LANE)),
            "line_start": LINE_START,
            "line_end": LINE_END,
            "bytes": len(target_bytes),
            "sha256": sha256(target_bytes),
            "han_residue": len(han_residue),
            "brace_balance": brace_balance(target),
        },
        "mathematics": {
            "source_surfaces": len(source_math),
            "target_surfaces": len(target_math),
            "exact_normalized_multiset": math_multiset_exact,
            "sequence_equal_after_prose_reordering": source_math == target_math,
        },
        "environments": {
            "source": dict(sorted(Counter(source_begin).items())),
            "target": dict(sorted(Counter(target_begin).items())),
            "exact_sequence": source_begin == target_begin,
        },
        "commands": command_results,
        "indexes": {
            "source_count": len(source_indexes),
            "target_count": len(target_indexes),
            "symbol_math_surfaces": len(target_symbol_math),
            "symbol_mathematics_exact": symbol_index_math_exact,
        },
        "literal_counts": literal_results,
        "expected_cardinality": expected_cardinality,
        "observed_cardinality": observed,
        "known_source_clarification": {
            "line": 112,
            "issue": "The chain omits identity arrows and non-adjacent composite arrows, while the source parenthetical names only identities.",
            "correction_id": "O013-LI-U009-CLR-001",
            "status": "applied_and_disclosure_required" if clarification_applied else "missing",
        },
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
