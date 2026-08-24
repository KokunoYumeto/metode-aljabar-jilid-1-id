#!/usr/bin/env python3
"""Fail-closed structure and mathematics gate for O013 Unit 015."""

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
LINE_START = 910
LINE_END = 1110
EXPECTED_SOURCE_BYTES = 16_925
EXPECTED_SOURCE_SHA256 = (
    "49c812f4cdb1929cf11e1bc3e5d916d21e82051d17a686f826c1b171a1f33062"
)
EXPECTED_TARGET_BYTES = 19_355
EXPECTED_TARGET_SHA256 = (
    "df3c65bfea7f7272a31809b96b5ae18fdf966afe22e9ab38a0d8f9d35680520f"
)
EXPECTED_FIRST_LINE = r"\begin{example}\label{eg:top-adjunction}"
EXPECTED_NEXT_BOUNDARY = r"\section{极限}\label{sec:limits}"
EXPECTED_CITATIONS = (("[Chapter 4]", "Co11"),)
EXPECTED_LABELS = (
    "eg:top-adjunction",
    "eg:forgetful-adjunction",
    "prop:adjunction-pointwise",
    "prop:adjunction-uniqueness",
    "prop:adjunction-composition",
    "prop:adjoint-equivalence",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
    "eqn:adj-equiv-two-expression",
)
EXPECTED_REFERENCES = (
    "def:free-group",
    "prop:adjunction-uniqueness",
    "eg:metric-completion",
    "prop:representable-functor-uniqueness",
    "prop:adjunction-pointwise",
    "def:cat-equivalence",
    "prop:naturaltrans-associativity",
    "sec:braiding",
)
EXPECTED_EQUATION_REFERENCES = (
    "eqn:unit-counit-relation",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-2",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-2",
    "eqn:adj-zigzag-1",
    "eqn:adj-equiv-two-expression",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
    "eqn:adj-zigzag-1",
    "eqn:adj-zigzag-2",
)

CORRECTIONS = (
    {
        "id": "O013-LI-U015-COR-001",
        "source_line": 962,
        "issue": "The prime is attached after the comma in the second adjunction tuple.",
        "source": "$(F', G,' \\eta', \\varepsilon')$",
        "target": "$(F', G', \\eta', \\varepsilon')$",
    },
    {
        "id": "O013-LI-U015-COR-002",
        "source_line": 997,
        "issue": "The baseline midpoint refers to A1 from a preceding picture instead of local node A2.",
        "source": r"\coordinate (X) at ($(A0)!.5!(A1)$);",
        "target": r"\coordinate (X) at ($(A0)!.5!(A2)$);",
    },
)


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
DIAGRAM_RE = re.compile(
    r"\\begin\{(tikzcd|tikzpicture)\}.*?\\end\{\1\}", re.DOTALL
)


def mask_localized_text(formula: str) -> str:
    """Mask translatable balanced text payloads while preserving text{op}."""

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


def diagram_blocks(text: str) -> tuple[tuple[str, int, str], ...]:
    return tuple(
        (match.group(1), ordinal, re.sub(r"\s+", "", match.group(0)))
        for ordinal, match in enumerate(DIAGRAM_RE.finditer(text), 1)
    )


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

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    target_lines = TARGET.read_text(encoding="utf-8").splitlines()
    source_for_comparison = source
    correction_results: list[dict[str, object]] = []
    for correction in CORRECTIONS:
        line_index = int(correction["source_line"]) - 1
        source_fragment = str(correction["source"])
        target_fragment = str(correction["target"])
        applied = (
            source_fragment in source_lines[line_index]
            and target_fragment in target_lines[line_index]
            and source.count(source_fragment) == 1
            and target.count(target_fragment) == 1
            and source_fragment not in target
        )
        if not applied:
            failures.append(f"declared correction is missing: {correction['id']}")
        else:
            source_for_comparison = source_for_comparison.replace(
                source_fragment, target_fragment, 1
            )
        correction_results.append(
            {
                "id": correction["id"],
                "source_line": correction["source_line"],
                "issue": correction["issue"],
                "applied": applied,
            }
        )

    source_math = normalized_math(source_for_comparison)
    target_math = normalized_math(target)
    math_equivalent = Counter(source_math) == Counter(target_math)
    if len(source_math) != 232 or len(target_math) != 232:
        failures.append("mathematical surface count is not the frozen 232/232")
    if not math_equivalent:
        failures.append("normalized mathematics differs beyond declared corrections")

    source_begin = environment_sequence(source, "begin")
    target_begin = environment_sequence(target, "begin")
    source_end = environment_sequence(source, "end")
    target_end = environment_sequence(target, "end")
    environments_exact = source_begin == target_begin and source_end == target_end
    if not environments_exact:
        failures.append("environment sequence differs")
    if len(source_begin) != 35 or len(target_begin) != 35:
        failures.append("environment count is not the frozen 35/35")
    if Counter(source_begin) != Counter(source_end):
        failures.append("source environment multiset is unbalanced")
    if Counter(target_begin) != Counter(target_end):
        failures.append("target environment multiset is unbalanced")

    command_specs = {
        "labels": (r"\label", EXPECTED_LABELS),
        "references": (r"\ref", EXPECTED_REFERENCES),
        "equation_references": (r"\eqref", EXPECTED_EQUATION_REFERENCES),
    }
    command_results: dict[str, dict[str, object]] = {}
    for name, (command, expected) in command_specs.items():
        source_args = balanced_command_arguments(source, command)
        target_args = balanced_command_arguments(target, command)
        exact = tuple(source_args) == expected and tuple(target_args) == expected
        command_results[name] = {
            "source_count": len(source_args),
            "target_count": len(target_args),
            "exact_argument_sequence": exact,
        }
        if not exact:
            failures.append(f"{name} argument sequence differs from frozen topology")

    source_citations = tuple(re.findall(r"\\cite(\[[^]]+\])?\{([^}]+)\}", source))
    target_citations = tuple(re.findall(r"\\cite(\[[^]]+\])?\{([^}]+)\}", target))
    citations_exact = (
        source_citations == EXPECTED_CITATIONS
        and target_citations == EXPECTED_CITATIONS
    )
    if not citations_exact:
        failures.append("citation option or key differs from [Chapter 4]{Co11}")

    source_indexes = balanced_command_arguments(source, r"\index")
    target_indexes = balanced_command_arguments(target, r"\index")
    source_index_options = re.findall(r"\\index(\[[^]]*\])?\{", source)
    target_index_options = re.findall(r"\\index(\[[^]]*\])?\{", target)
    index_topology_exact = (
        len(source_indexes) == 3
        and len(target_indexes) == 3
        and all(not option for option in source_index_options + target_index_options)
        and [[c for c in entry if c in "@!"] for entry in source_indexes]
        == [[c for c in entry if c in "@!"] for entry in target_indexes]
    )
    if not index_topology_exact:
        failures.append("ordinary index count/options or @/! topology differs")

    source_diagrams = diagram_blocks(source_for_comparison)
    target_diagrams = diagram_blocks(target)
    diagrams_exact = source_diagrams == target_diagrams
    diagram_kinds = Counter(kind for kind, _ordinal, _payload in source_diagrams)
    if not diagrams_exact:
        failures.append("TikZ blocks differ beyond declared correction")
    if diagram_kinds != Counter({"tikzpicture": 16, "tikzcd": 4}):
        failures.append("diagram block count is not frozen at 16 tikzpicture / 4 tikzcd")

    expected_literals = {
        "tikz_nodes": (r"\node", 75),
        "tikz_coordinates": (r"\coordinate", 32),
        "tikz_draws": (r"\draw", 4),
        "tikzcd_arrows": (r"\arrow", 13),
        "items": (r"\item", 4),
    }
    literal_results: dict[str, dict[str, int]] = {}
    for name, (token, expected_count) in expected_literals.items():
        source_count = source.count(token)
        target_count = target.count(token)
        literal_results[name] = {
            "source_count": source_count,
            "target_count": target_count,
        }
        if source_count != expected_count or target_count != expected_count:
            failures.append(f"{name} count is not the frozen {expected_count}/{expected_count}")

    han_residue = re.findall(r"[\u3400-\u9fff\uf900-\ufaff]", target)
    if han_residue:
        failures.append(f"target contains {len(han_residue)} Han characters")
    if brace_balance(target) != 0:
        failures.append("target brace balance is nonzero")
    if re.search(r"\$`|`\$", target):
        failures.append("target contains a suspicious backtick adjacent to mathematics")
    if "funktor" in target.lower():
        failures.append("target contains the rejected spelling funktor")
    if not target.splitlines() or target.splitlines()[0] != EXPECTED_FIRST_LINE:
        failures.append("line 910 is no longer the frozen opening example boundary")
    next_boundary_ok = (
        len(target_lines) > LINE_END
        and target_lines[LINE_END] == EXPECTED_NEXT_BOUNDARY
    )
    if not next_boundary_ok:
        failures.append("line 1111 is no longer the frozen limits-section boundary")

    report = {
        "schema_version": "unit-015-structure-gate-v1",
        "unit_id": "unit-015-bab-2-contoh-keunikan-dan-ekuivalensi-adjoin",
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
        "mathematics_multiset_equivalent_after_declared_corrections": math_equivalent,
        "environment_sequence_exact": environments_exact,
        "environment_begin_count": len(source_begin),
        "commands": command_results,
        "citation_signatures_exact": citations_exact,
        "index_source_count": len(source_indexes),
        "index_target_count": len(target_indexes),
        "index_topology_exact": index_topology_exact,
        "diagram_blocks_exact_after_declared_corrections": diagrams_exact,
        "diagram_counts": dict(sorted(diagram_kinds.items())),
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
