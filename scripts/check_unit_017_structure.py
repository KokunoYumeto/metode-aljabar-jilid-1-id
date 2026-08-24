#!/usr/bin/env python3
"""Fail-closed structural check for Unit 017 (chapter 2, lines 1406--1602)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import sys


UNIT_START = 1406
UNIT_END = 1602
BOUNDARY_LINE = 1603
UNIT_LINE_COUNT = 197

SOURCE_BYTES = 15_810
SOURCE_SHA256 = "ccc5a17cbf856e59e7b8abbff8fd542c5deb399e58b6fc7a5a0f448c7c019e92"
TARGET_BYTES = 18_633
TARGET_SHA256 = "e27dba97355122446714b8e58f71f80edbb1d74e6160f99ba0b8160e7c3ec30b"
EXPECTED_BOUNDARY = r"\begin{Exercises}"
EXPECTED_COMMENT_LINES = tuple(range(1531, 1539))
TRANSLATABLE_TEXT_ORDINALS = frozenset({3, 7, 8})
EXPECTED_ACTIVE_COMMAND_REORDER_LINES = (
    1417,
    1423,
    1424,
    1428,
    1463,
    1464,
    1522,
    1529,
    1565,
    1598,
)
EXPECTED_RAW_COMMAND_REORDER_LINES = (
    *EXPECTED_ACTIVE_COMMAND_REORDER_LINES[:8],
    1531,
    1536,
    1538,
    *EXPECTED_ACTIVE_COMMAND_REORDER_LINES[8:],
)
EXPECTED_ACTIVE_MATH_REORDER_LINES = (
    1410,
    1417,
    1423,
    1424,
    1428,
    1430,
    1463,
    1464,
    1520,
    1522,
    1529,
    1547,
    1550,
    1560,
    1561,
    1565,
)
EXPECTED_COMMENT_MATH_REORDER_LINES = (1531, 1536, 1538)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = (
    PROJECT_ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter2.tex"
)
TARGET_PATH = PROJECT_ROOT / "repo" / "source" / "chapter2.tex"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\ref\{([^{}]+)\}")
EQREF_RE = re.compile(r"\\eqref\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[([^\]\r\n]*)\])?\{([^{}]+)\}")
INDEX_RE = re.compile(r"\\index(?:\[([^\]\r\n]*)\])?\{([^{}\r\n]*)\}")
ITEM_RE = re.compile(r"\\item\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 2,
        "array": 1,
        "compactenum": 1,
        "compactitem": 3,
        "convention": 1,
        "corollary": 1,
        "definition": 3,
        "enumerate": 1,
        "equation": 3,
        "example": 2,
        "inparaenum": 1,
        "itemize": 2,
        "proof": 4,
        "proposition": 2,
        "remark": 1,
        "theorem": 2,
        "tikzcd": 9,
    }
)

EXPECTED_LABELS = (
    "def:completeness",
    "prop:preorder-complete",
    "prop:limit-buildingblocks",
    "eqn:lim-as-ker",
    "prop:completeness-criterion",
    "eg:complete-cocomplete",
    "def:preservation-limit",
    "rem:preservation-limit",
    "eg:preservation-limit",
    "prop:Hom-exact",
    "prop:adjuncion-limit",
)
EXPECTED_ITEM_LINES = (
    1423,
    1424,
    1463,
    1464,
    1500,
    1501,
    1502,
    1504,
    1505,
    1506,
    1510,
    1512,
    1513,
    1514,
    1543,
    1544,
    1560,
    1561,
    1594,
    1595,
    1596,
)
EXPECTED_INDEX_LINES = (1409, 1409, 1463, 1463, 1464, 1464, 1483, 1483, 1569)

COR_001_SOURCE = r"F(\alpha(j) \to \varinjlim \alpha)"
COR_001_TARGET = r"F(\alpha(i) \to \varinjlim \alpha)"
COR_003_SOURCE = r"j \in \Obj(i)"
COR_003_TARGET = r"j \in \Obj(I)"
COR_004_SOURCE = r"\Hom_{\mathcal{C}_1}(F(\cdot), \beta(j))"
COR_004_TARGET = r"\Hom_{\mathcal{C}_2}(F(\cdot), \beta(j))"
COR_005_SOURCE = r"\arrow[twoheadrightarrow, r]"
COR_005_TARGET = r"\arrow[r]"
COR_006_SOURCE = r"\varprojlim \beta"
COR_006_TARGET = r"\varprojlim (F\beta)"


class CheckFailure(RuntimeError):
    """A deterministic admission check failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def lf_records(data: bytes) -> list[bytes]:
    """Split bytes into records while retaining each physical LF terminator."""
    records: list[bytes] = []
    start = 0
    for index, value in enumerate(data):
        if value == 0x0A:
            records.append(data[start : index + 1])
            start = index + 1
    if start < len(data):
        records.append(data[start:])
    return records


def normalize_lf(record: bytes) -> bytes:
    if record.endswith(b"\r\n"):
        return record[:-2] + b"\n"
    return record


def record_text(record: bytes) -> str:
    if record.endswith(b"\n"):
        record = record[:-1]
    if record.endswith(b"\r"):
        record = record[:-1]
    return record.decode("utf-8", errors="strict")


@dataclass(frozen=True)
class UnitSpan:
    raw_lf: bytes
    lines: tuple[str, ...]
    boundary: str

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def active_lines(self) -> tuple[str, ...]:
        return tuple(strip_comment(line)[0] for line in self.lines)

    @property
    def active_text(self) -> str:
        return "\n".join(self.active_lines)

    def line(self, absolute_line: int) -> str:
        require(
            UNIT_START <= absolute_line <= UNIT_END,
            f"line {absolute_line} is outside Unit 017",
        )
        return self.lines[absolute_line - UNIT_START]


def read_unit(path: Path) -> UnitSpan:
    require(path.is_file(), f"missing input: {path}")
    records = lf_records(path.read_bytes())
    require(
        len(records) >= BOUNDARY_LINE,
        f"{path} has fewer than {BOUNDARY_LINE} physical lines",
    )
    selected = records[UNIT_START - 1 : UNIT_END]
    require(len(selected) == UNIT_LINE_COUNT, f"{path}: Unit 017 extraction failed")
    require(
        all(record.endswith(b"\n") for record in selected),
        f"{path}: every Unit 017 record must be LF-terminated",
    )
    normalized = tuple(normalize_lf(record) for record in selected)
    return UnitSpan(
        raw_lf=b"".join(normalized),
        lines=tuple(record_text(record) for record in normalized),
        boundary=record_text(normalize_lf(records[BOUNDARY_LINE - 1])),
    )


def is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def strip_comment(line: str) -> tuple[str, int | None, str | None]:
    for position, char in enumerate(line):
        if char == "%" and not is_escaped(line, position):
            return line[:position], position, line[position + 1 :]
    return line, None, None


def comment_records(span: UnitSpan) -> list[tuple[int, int, str]]:
    records: list[tuple[int, int, str]] = []
    for line_number, line in enumerate(span.lines, UNIT_START):
        _, column, body = strip_comment(line)
        if column is not None:
            records.append((line_number, column, body or ""))
    return records


def comment_text(span: UnitSpan) -> str:
    return "\n".join(body for _, _, body in comment_records(span))


def inline_math(text: str, first_line: int = UNIT_START) -> list[tuple[int, str]]:
    delimiters = [
        position
        for position, char in enumerate(text)
        if char == "$" and not is_escaped(text, position)
    ]
    require(len(delimiters) % 2 == 0, "unpaired inline-math dollar delimiter")
    results: list[tuple[int, str]] = []
    for offset in range(0, len(delimiters), 2):
        opening, closing = delimiters[offset : offset + 2]
        require(closing > opening, "invalid inline-math delimiter order")
        line_number = first_line + text.count("\n", 0, opening)
        results.append((line_number, text[opening + 1 : closing]))
    return results


def bracket_displays(text: str) -> list[str]:
    opens = [match.start() for match in re.finditer(r"\\\[", text)]
    closes = [match.start() for match in re.finditer(r"\\\]", text)]
    require(len(opens) == len(closes), "unpaired bracket-display delimiter")
    results: list[str] = []
    cursor = 0
    while cursor < len(text):
        opening = text.find(r"\[", cursor)
        if opening < 0:
            break
        closing = text.find(r"\]", opening + 2)
        require(closing >= 0, "unterminated bracket display")
        results.append(text[opening + 2 : closing])
        cursor = closing + 2
    require(len(results) == len(opens), "overlapping bracket-display delimiters")
    return results


def mask_translatable_text_arguments(text: str) -> tuple[str, tuple[str, ...]]:
    """Mask only the three language-bearing active ``\\text`` arguments."""
    needle = r"\text{"
    output: list[str] = []
    arguments: list[str] = []
    cursor = 0
    ordinal = 0
    while True:
        start = text.find(needle, cursor)
        if start < 0:
            output.append(text[cursor:])
            return "".join(output), tuple(arguments)
        output.append(text[cursor:start])
        depth = 1
        position = start + len(needle)
        while position < len(text) and depth:
            char = text[position]
            if char == "{" and not is_escaped(text, position):
                depth += 1
            elif char == "}" and not is_escaped(text, position):
                depth -= 1
            position += 1
        require(depth == 0, "unterminated \\text argument")
        argument = text[start + len(needle) : position - 1]
        arguments.append(argument)
        if ordinal in TRANSLATABLE_TEXT_ORDINALS:
            output.append(r"\text{<PROSE>}")
        else:
            output.append(text[start:position])
        ordinal += 1
        cursor = position


def environment_events(text: str) -> list[tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in ENV_RE.finditer(text)]


def audit_environment_nesting(events: list[tuple[str, str]], side: str) -> None:
    stack: list[str] = []
    for kind, name in events:
        if kind == "begin":
            stack.append(name)
        else:
            require(bool(stack), f"{side}: unmatched \\end{{{name}}}")
            opened = stack.pop()
            require(opened == name, f"{side}: \\begin{{{opened}}} closed by \\end{{{name}}}")
    require(not stack, f"{side}: unclosed environments: {stack}")


def extract_environments(text: str, name: str) -> list[str]:
    escaped = re.escape(name)
    pattern = re.compile(
        rf"\\begin\{{{escaped}\}}.*?\\end\{{{escaped}\}}",
        flags=re.DOTALL,
    )
    return [match.group(0) for match in pattern.finditer(text)]


def brace_audit(text: str) -> tuple[int, int, int, int]:
    balance = 0
    minimum = 0
    opens = 0
    closes = 0
    for position, char in enumerate(text):
        if char not in "{}" or is_escaped(text, position):
            continue
        if char == "{":
            balance += 1
            opens += 1
        else:
            balance -= 1
            closes += 1
            minimum = min(minimum, balance)
    return balance, minimum, opens, closes


def han_count(text: str) -> int:
    ranges = (
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0xF900, 0xFAFF),
        (0x20000, 0x2EBEF),
        (0x30000, 0x323AF),
    )
    return sum(any(low <= ord(char) <= high for low, high in ranges) for char in text)


def without_emphasis(tokens: list[str]) -> list[str]:
    return [token for token in tokens if token != r"\emph"]


def gate_line_command_order(
    source_lines: tuple[str, ...],
    target_lines: tuple[str, ...],
    expected_reorder_lines: tuple[int, ...],
    side: str,
) -> None:
    """Allow only enumerated whole-expression relocations caused by Indonesian syntax."""
    reordered: list[int] = []
    for line_number, (source_line, target_line) in enumerate(
        zip(source_lines, target_lines, strict=True), UNIT_START
    ):
        source_tokens = without_emphasis(COMMAND_RE.findall(source_line))
        target_tokens = without_emphasis(COMMAND_RE.findall(target_line))
        if source_tokens == target_tokens:
            continue
        reordered.append(line_number)
        require(
            Counter(source_tokens) == Counter(target_tokens),
            f"{side} line {line_number}: command relocation changes the command multiset",
        )
    require(
        tuple(reordered) == expected_reorder_lines,
        f"{side} command-reorder lines differ: {reordered}",
    )


def located_matches(pattern: re.Pattern[str], text: str) -> list[tuple[int, tuple[str, ...]]]:
    return [
        (UNIT_START + text.count("\n", 0, match.start()), match.groups())
        for match in pattern.finditer(text)
    ]


def source_math_repairs(text: str) -> str:
    """Normalize only corrections 001, 003, 004 and 005 in math blocks."""
    text = text.replace(COR_001_SOURCE, COR_001_TARGET, 1)
    text = text.replace(COR_003_SOURCE, COR_003_TARGET)
    text = text.replace(COR_004_SOURCE, COR_004_TARGET)
    text = text.replace(COR_005_SOURCE, COR_005_TARGET)
    return text


def normalize_source_inline(items: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Apply line-aware math corrections, including the second limit on line 1547."""
    normalized: list[tuple[int, str]] = []
    line_1547_seen = 0
    for line_number, content in items:
        repaired = source_math_repairs(content)
        if line_number == 1547 and content == COR_006_SOURCE:
            line_1547_seen += 1
            if line_1547_seen == 2:
                repaired = COR_006_TARGET
        normalized.append((line_number, repaired))
    require(line_1547_seen == 2, "COR-006 source must contain two line-1547 limit spans")
    return normalized


def gate_inline_math_order(
    source_items: list[tuple[int, str]],
    target_items: list[tuple[int, str]],
) -> None:
    """Compare inline math exactly except for enumerated whole-span prose relocations."""
    normalized_source = normalize_source_inline(source_items)
    source_by_line: dict[int, list[str]] = {}
    target_by_line: dict[int, list[str]] = {}
    for line_number, content in normalized_source:
        source_by_line.setdefault(line_number, []).append(content)
    for line_number, content in target_items:
        target_by_line.setdefault(line_number, []).append(content)
    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology differs")
    reordered: list[int] = []
    for line_number in source_by_line:
        source_line = source_by_line[line_number]
        target_line = target_by_line[line_number]
        if source_line == target_line:
            continue
        reordered.append(line_number)
        require(
            Counter(source_line) == Counter(target_line),
            f"line {line_number}: inline-math relocation changes mathematical spans",
        )
    require(
        tuple(reordered) == EXPECTED_ACTIVE_MATH_REORDER_LINES,
        f"active inline-math reorder lines differ: {reordered}",
    )


def gate_commented_math(source: UnitSpan, target: UnitSpan) -> None:
    """Preserve every commented math span, allowing only enumerated prose-order moves."""
    source_records = comment_records(source)
    target_records = comment_records(target)
    reordered: list[int] = []
    for (line_number, _, source_body), (target_line, _, target_body) in zip(
        source_records, target_records, strict=True
    ):
        require(line_number == target_line, "commented-math line topology differs")
        source_math = [content for _, content in inline_math(source_body, line_number)]
        target_math = [content for _, content in inline_math(target_body, line_number)]
        if source_math == target_math:
            continue
        reordered.append(line_number)
        require(
            Counter(source_math) == Counter(target_math),
            f"comment line {line_number}: math relocation changes mathematical spans",
        )
    require(
        tuple(reordered) == EXPECTED_COMMENT_MATH_REORDER_LINES,
        f"commented inline-math reorder lines differ: {reordered}",
    )


def gate_exact_corrections(source: UnitSpan, target: UnitSpan) -> None:
    source_1410 = source.line(1410)
    target_1410 = target.line(1410)
    require("若对有所有小范畴" in source_1410, "line-1410 authority grammar signature missing")
    require(
        Counter(content for _, content in inline_math(source_1410, 1410))
        == Counter(content for _, content in inline_math(target_1410, 1410)),
        "line-1410 prose translation changed the mathematical-span multiset",
    )

    source_1525 = source.line(1525)
    target_1525 = target.line(1525)
    require(source_1525.count(COR_001_SOURCE) == 2, "COR-001 source signatures missing")
    require(
        target_1525 == source_1525.replace(COR_001_SOURCE, COR_001_TARGET, 1),
        "COR-001 must change only the left-leg alpha(j) label to alpha(i)",
    )

    source_1547_math = inline_math(source.line(1547), 1547)
    target_1547_math = inline_math(target.line(1547), 1547)
    expected_1547 = list(source_1547_math)
    positions = [index for index, (_, content) in enumerate(expected_1547) if content == COR_006_SOURCE]
    require(len(positions) == 2, "COR-006 source signatures missing")
    expected_1547[positions[1]] = (1547, COR_006_TARGET)
    require(
        Counter(content for _, content in target_1547_math)
        == Counter(content for _, content in expected_1547),
        "COR-006 must repair only the second line-1547 limit",
    )

    source_1554 = source.line(1554)
    target_1554 = target.line(1554)
    require("余积是交换群的直积" in source_1554, "COR-002 source direct-product prose missing")
    require(
        re.search(r"\b(?:jumlah|penjumlahan)\s+langsung\b", target_1554, re.IGNORECASE)
        is not None,
        "COR-002 target must identify the Ab coproduct as a direct sum",
    )
    require(
        inline_math(source_1554, 1554) == inline_math(target_1554, 1554),
        "COR-002 is prose-only and must not change line-1554 mathematics",
    )

    source_1585_math = inline_math(source.line(1585), 1585)
    target_1585_math = inline_math(target.line(1585), 1585)
    require(
        [(line, content.replace(COR_003_SOURCE, COR_003_TARGET)) for line, content in source_1585_math]
        == target_1585_math,
        "COR-003 must change Obj(i) to Obj(I) and nothing else",
    )

    require(COR_004_SOURCE in source.line(1588), "COR-004 line-1588 source signature missing")
    require(COR_004_SOURCE in source.line(1589), "COR-004 line-1589 source signature missing")
    require(
        target.line(1588) == source.line(1588).replace(COR_004_SOURCE, COR_004_TARGET),
        "COR-004 line 1588 must change only C_1 to C_2",
    )
    expected_1589 = source.line(1589).replace(COR_004_SOURCE, COR_004_TARGET)
    expected_1589 = expected_1589.replace(COR_005_SOURCE, COR_005_TARGET)
    require(target.line(1589) == expected_1589, "COR-004/005 line-1589 repair differs")
    require(
        target.line(1590) == source.line(1590).replace(COR_005_SOURCE, COR_005_TARGET),
        "COR-005 line 1590 must replace only the epimorphism arrow option",
    )


def gate_index_topology(source_text: str, target_text: str) -> None:
    source = located_matches(INDEX_RE, source_text)
    target = located_matches(INDEX_RE, target_text)
    require(len(source) == len(target) == 9, "active index-call count must remain 9")
    require(tuple(line for line, _ in source) == EXPECTED_INDEX_LINES, "source index lines changed")
    require(
        tuple(line for line, _ in target) == EXPECTED_INDEX_LINES,
        "target index-call line topology changed",
    )
    source_options = tuple(groups[0] for _, groups in source)
    target_options = tuple(groups[0] for _, groups in target)
    require(source_options == target_options, "index namespaces/options differ")
    source_args = tuple(groups[1] for _, groups in source)
    target_args = tuple(groups[1] for _, groups in target)
    require(all(argument.strip() for argument in target_args), "empty target index argument")
    require(
        tuple(argument.count("!") for argument in source_args)
        == tuple(argument.count("!") for argument in target_args),
        "index hierarchy depth/order differs",
    )
    require(target_args[2] == target_args[6], "the two pullback index entries must map identically")
    require(target_args[4] == target_args[7], "the two pushout index entries must map identically")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source = read_unit(SOURCE_PATH)
    target = read_unit(TARGET_PATH)

    require(len(source.lines) == len(target.lines) == UNIT_LINE_COUNT, "Unit 017 must have 197 lines")
    require(len(source.raw_lf) == SOURCE_BYTES, f"source span byte count changed: {len(source.raw_lf)}")
    require(sha256(source.raw_lf).hexdigest() == SOURCE_SHA256, "source span SHA-256 changed")
    require(len(target.raw_lf) == TARGET_BYTES, f"target span byte count changed: {len(target.raw_lf)}")
    require(sha256(target.raw_lf).hexdigest() == TARGET_SHA256, "target span SHA-256 changed")
    require(source.boundary == EXPECTED_BOUNDARY, "authority line-1603 boundary changed")
    require(target.boundary == EXPECTED_BOUNDARY, "target line 1603 is not the Exercises boundary")
    require(source.line(1602).strip() == target.line(1602).strip() == "", "line 1602 must remain blank")

    source_blank = tuple(not line.strip() for line in source.lines)
    target_blank = tuple(not line.strip() for line in target.lines)
    require(source_blank == target_blank, "physical blank-line topology differs")
    require(sum(source_blank) == 20, f"expected 20 physical blank lines, got {sum(source_blank)}")

    source_comments = comment_records(source)
    target_comments = comment_records(target)
    require(
        tuple((line, column) for line, column, _ in source_comments)
        == tuple((line, column) for line, column, _ in target_comments),
        "comment line/column topology differs",
    )
    require(
        tuple(line for line, _, _ in source_comments) == EXPECTED_COMMENT_LINES,
        "authority must have exactly the eight lines 1531--1538 commented",
    )
    require(all(column == 0 for _, column, _ in target_comments), "Unit 017 comments must stay at column zero")

    source_active_commands = COMMAND_RE.findall(source.active_text)
    target_active_commands = COMMAND_RE.findall(target.active_text)
    source_raw_commands = COMMAND_RE.findall(source.text)
    target_raw_commands = COMMAND_RE.findall(target.text)
    require(len(source_active_commands) == 749, "source active-command census changed")
    require(len(source_raw_commands) == 806, "source raw-command census changed")
    require(Counter(source_active_commands) == Counter(target_active_commands), "active command multiset differs")
    require(Counter(source_raw_commands) == Counter(target_raw_commands), "raw command multiset differs")
    gate_line_command_order(
        source.active_lines,
        target.active_lines,
        EXPECTED_ACTIVE_COMMAND_REORDER_LINES,
        "active",
    )
    gate_line_command_order(
        source.lines,
        target.lines,
        EXPECTED_RAW_COMMAND_REORDER_LINES,
        "raw",
    )
    require(source_active_commands.count(r"\emph") == target_active_commands.count(r"\emph") == 7, "emphasis count differs")

    source_events = environment_events(source.active_text)
    target_events = environment_events(target.active_text)
    audit_environment_nesting(source_events, "source active")
    audit_environment_nesting(target_events, "target active")
    require(source_events == target_events, "active environment event sequence differs")
    source_begins = [name for kind, name in source_events if kind == "begin"]
    source_ends = [name for kind, name in source_events if kind == "end"]
    require(len(source_begins) == len(source_ends) == 39, "source must have 39 active environment pairs")
    require(Counter(source_begins) == EXPECTED_ENVIRONMENTS, "active environment inventory changed")

    source_raw_events = environment_events(source.text)
    target_raw_events = environment_events(target.text)
    require(source_raw_events == target_raw_events, "raw/commented environment sequence differs")
    require(len([1 for kind, _ in source_raw_events if kind == "begin"]) == 40, "raw begin census changed")
    require(len([1 for kind, _ in source_raw_events if kind == "end"]) == 40, "raw end census changed")

    source_labels = LABEL_RE.findall(source.active_text)
    target_labels = LABEL_RE.findall(target.active_text)
    source_refs = REF_RE.findall(source.active_text)
    target_refs = REF_RE.findall(target.active_text)
    source_eqrefs = EQREF_RE.findall(source.active_text)
    target_eqrefs = EQREF_RE.findall(target.active_text)
    source_cites = CITE_RE.findall(source.active_text)
    target_cites = CITE_RE.findall(target.active_text)
    require(tuple(source_labels) == EXPECTED_LABELS, "source label sequence changed")
    require(source_labels == target_labels, "label targets differ")
    require(len(source_refs) == len(target_refs) == 32 and source_refs == target_refs, "active ref targets differ")
    require(len(REF_RE.findall(source.text)) == len(REF_RE.findall(target.text)) == 35, "raw ref census differs")
    require(REF_RE.findall(source.text) == REF_RE.findall(target.text), "raw/commented ref targets differ")
    require(len(source_eqrefs) == len(target_eqrefs) == 5 and source_eqrefs == target_eqrefs, "eqref targets differ")
    require(source_cites == target_cites == [], "Unit 017 must contain no active citations")

    gate_index_topology(source.active_text, target.active_text)
    source_items = tuple(line for line, _ in located_matches(ITEM_RE, source.active_text))
    target_items = tuple(line for line, _ in located_matches(ITEM_RE, target.active_text))
    require(source_items == target_items == EXPECTED_ITEM_LINES, "item line topology differs")

    source_masked, source_text_args = mask_translatable_text_arguments(source.active_text)
    target_masked, target_text_args = mask_translatable_text_arguments(target.active_text)
    require(len(source_text_args) == len(target_text_args) == 11, "active \\text argument count differs")
    require(
        tuple(value for index, value in enumerate(source_text_args) if index not in TRANSLATABLE_TEXT_ORDINALS)
        == tuple(value for index, value in enumerate(target_text_args) if index not in TRANSLATABLE_TEXT_ORDINALS),
        "mathematical \\text{op}/\\text{der} arguments differ",
    )

    source_inline = inline_math(source_masked)
    target_inline = inline_math(target_masked)
    require(len(source_inline) == len(target_inline) == 185, "active inline-math count differs from 185")
    gate_inline_math_order(source_inline, target_inline)
    require(len(inline_math(source.text)) == len(inline_math(target.text)) == 199, "raw inline-math census differs")
    gate_commented_math(source, target)

    source_displays = bracket_displays(source_masked)
    target_displays = bracket_displays(target_masked)
    require(len(source_displays) == len(target_displays) == 4, "bracket-display count differs from 4")
    require(
        [source_math_repairs(item) for item in source_displays] == target_displays,
        "bracket-display mathematics differs beyond declared repairs",
    )

    for environment, expected_count in (("equation", 3), ("align*", 2)):
        source_math = extract_environments(source_masked, environment)
        target_math = extract_environments(target_masked, environment)
        require(len(source_math) == len(target_math) == expected_count, f"active {environment} count changed")
        require(
            [source_math_repairs(item) for item in source_math] == target_math,
            f"{environment} mathematics differs beyond declared repairs",
        )

    source_tikz = extract_environments(source.active_text, "tikzcd")
    target_tikz = extract_environments(target.active_text, "tikzcd")
    require(len(source_tikz) == len(target_tikz) == 9, "tikzcd count differs from 9")
    require(
        [source_math_repairs(item) for item in source_tikz] == target_tikz,
        "diagram topology differs beyond declared repairs",
    )
    require(len(ARROW_RE.findall(source.active_text)) == 47, "source arrow count differs from 47")
    require(len(ARROW_RE.findall(target.active_text)) == 47, "target arrow count differs from 47")

    require(brace_audit(source.active_text) == (0, 0, 299, 299), "source active brace audit changed")
    require(brace_audit(target.active_text) == (0, 0, 299, 299), "target active brace topology differs")
    require(brace_audit(source.text) == (0, 0, 313, 313), "source raw brace audit changed")
    require(brace_audit(target.text) == (0, 0, 313, 313), "target raw brace topology differs")
    require(han_count(target.text) == 0, "target Unit 017 contains Han residue, including comments")

    gate_exact_corrections(source, target)

    print(
        "\n".join(
            (
                "PASS Unit 017 structural checker",
                f"source lines=197 bytes={len(source.raw_lf)} sha256={sha256(source.raw_lf).hexdigest()}",
                f"target lines=197 bytes={len(target.raw_lf)} sha256={sha256(target.raw_lf).hexdigest()}",
                "boundary line=1603 value=Exercises active_commands=749 raw_commands=806 comments=1531-1538",
                "active_begin=39 active_end=39 labels=11 refs=32 raw_refs=35 eqrefs=5 cites=0 indexes=9 items=21",
                "inline_math=185 raw_inline_math=199 bracket_displays=4 equations=3 align*=2 tikzcd=9 arrows=47 han=0",
                "corrections=O013-LI-U017-COR-001..006 prose_grammar_line=1410",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:  # Fail closed for expected and unexpected checker errors.
        print(f"FAIL Unit 017 structural checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
