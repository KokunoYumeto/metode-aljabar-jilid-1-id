#!/usr/bin/env python3
"""Fail-closed structural check for Unit 018 (chapter 2, lines 1603--1645)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import sys


UNIT_START = 1603
UNIT_END = 1645
UNIT_LINE_COUNT = 43
SOURCE_BYTES = 5_197
SOURCE_SHA256 = "24417872734a2dc72c1d52d0df30246a427c5bbb714faf5238679e19c8dd7cce"
TARGET_BYTES = 6_523
TARGET_SHA256 = "d69667baae061a5d06a57dcc25033b6a971986ea704c72a0f53d687707837b55"
FULL_TARGET_BYTES = 166_465
FULL_TARGET_SHA256 = "3ef0e0dd3a8a30f4e44d7f87d94a4a4343ac7097a1862180c8becaf3631cda16"

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter2.tex"
)
TARGET = ROOT / "repo/source/chapter2.tex"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
REF_RE = re.compile(r"\\ref\{([^{}]+)\}")
EQREF_RE = re.compile(r"\\eqref\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
INDEX_RE = re.compile(r"\\index(?:\[[^\]]*\])?\{([^{}]+)\}")
ITEM_RE = re.compile(r"\\item\b")
HINT_RE = re.compile(r"\\hint\{")
ARROW_RE = re.compile(r"\\arrow\s*\[")

EXPECTED_ENV_EVENTS = (
    ("begin", "Exercises"),
    ("begin", "align*"),
    ("begin", "cases"),
    ("end", "cases"),
    ("end", "align*"),
    ("begin", "compactitem"),
    ("end", "compactitem"),
    ("begin", "inparaenum"),
    ("end", "inparaenum"),
    ("begin", "tikzcd"),
    ("end", "tikzcd"),
    ("end", "Exercises"),
)
EXPECTED_ITEM_LINES = (
    1604, 1605, 1616, 1617, 1619, 1620, 1621, 1624, 1625,
    1626, 1627, 1629, 1630, 1639, 1640, 1641, 1643, 1644,
)
EXPECTED_TOP_LEVEL_ITEMS = (
    1604, 1605, 1616, 1617, 1624, 1625, 1626, 1627, 1639, 1640, 1641, 1643, 1644,
)
EXPECTED_NESTED_ITEMS = (1619, 1620, 1621, 1629, 1630)
EXPECTED_REFS = (
    "eg:forgetful-adjunction",
    "prop:Yoneda-lemma",
    "def:diagonal-functor",
)
EXPECTED_COMMAND_REORDER_LINES = (1617, 1632, 1639)
EXPECTED_MATH_REORDER_LINES = (1617, 1619, 1632, 1639)

COR_002_SOURCE = r"\cate{Set}_\bullet \to \cate{Set}"
COR_002_TARGET = r"U: \cate{Set}_\bullet \to \cate{Set}"


class CheckFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def lf_records(data: bytes) -> list[bytes]:
    records: list[bytes] = []
    start = 0
    for index, byte in enumerate(data):
        if byte == 0x0A:
            records.append(data[start : index + 1])
            start = index + 1
    if start < len(data):
        records.append(data[start:])
    return records


def record_text(record: bytes) -> str:
    if record.endswith(b"\n"):
        record = record[:-1]
    if record.endswith(b"\r"):
        record = record[:-1]
    return record.decode("utf-8", errors="strict")


@dataclass(frozen=True)
class Span:
    raw: bytes
    lines: tuple[str, ...]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def line(self, absolute_line: int) -> str:
        return self.lines[absolute_line - UNIT_START]


def read_span(path: Path) -> Span:
    require(path.is_file(), f"missing input: {path}")
    data = path.read_bytes()
    records = lf_records(data)
    require(len(records) == UNIT_END, f"{path}: chapter2.tex must end at physical line 1645")
    require(data.endswith(b"\n"), f"{path}: chapter2.tex must end with LF")
    require(all(record.endswith(b"\n") for record in records), f"{path}: non-LF record detected")
    selected = records[UNIT_START - 1 : UNIT_END]
    require(len(selected) == UNIT_LINE_COUNT, f"{path}: Unit 018 extraction failed")
    return Span(b"".join(selected), tuple(record_text(record) for record in selected))


def is_escaped(text: str, position: int) -> bool:
    count = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        count += 1
        position -= 1
    return count % 2 == 1


def comment_positions(lines: tuple[str, ...]) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for line_number, line in enumerate(lines, UNIT_START):
        for position, char in enumerate(line):
            if char == "%" and not is_escaped(line, position):
                found.append((line_number, position))
                break
    return found


def inline_math(text: str, first_line: int = UNIT_START) -> list[tuple[int, str]]:
    delimiters = [
        position for position, char in enumerate(text)
        if char == "$" and not is_escaped(text, position)
    ]
    require(len(delimiters) % 2 == 0, "unpaired inline-math delimiter")
    result: list[tuple[int, str]] = []
    for offset in range(0, len(delimiters), 2):
        opening, closing = delimiters[offset : offset + 2]
        result.append((first_line + text.count("\n", 0, opening), text[opening + 1 : closing]))
    return result


def bracket_displays(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    cursor = 0
    while True:
        opening = text.find(r"\[", cursor)
        if opening < 0:
            break
        closing = text.find(r"\]", opening + 2)
        require(closing >= 0, "unterminated bracket display")
        result.append((UNIT_START + text.count("\n", 0, opening), text[opening + 2 : closing]))
        cursor = closing + 2
    require(text.count(r"\[") == text.count(r"\]") == len(result), "display delimiters differ")
    return result


def environment_events(text: str) -> list[tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in ENV_RE.finditer(text)]


def audit_nesting(events: list[tuple[str, str]], side: str) -> None:
    stack: list[str] = []
    for kind, name in events:
        if kind == "begin":
            stack.append(name)
        else:
            require(stack, f"{side}: unmatched end {name}")
            opened = stack.pop()
            require(opened == name, f"{side}: begin {opened} closed by end {name}")
    require(not stack, f"{side}: unclosed environments {stack}")


def extract_environment(text: str, name: str) -> list[str]:
    escaped = re.escape(name)
    return re.findall(
        rf"\\begin\{{{escaped}\}}.*?\\end\{{{escaped}\}}",
        text,
        flags=re.DOTALL,
    )


def mask_balanced_argument(text: str, command: str) -> str:
    needle = rf"\{command}{{"
    output: list[str] = []
    cursor = 0
    while True:
        start = text.find(needle, cursor)
        if start < 0:
            output.append(text[cursor:])
            return "".join(output)
        output.append(text[cursor:start])
        depth = 1
        position = start + len(needle)
        while position < len(text) and depth:
            if text[position] == "{" and not is_escaped(text, position):
                depth += 1
            elif text[position] == "}" and not is_escaped(text, position):
                depth -= 1
            position += 1
        require(depth == 0, f"unterminated {needle} argument")
        output.append(rf"\{command}{{<PROSE>}}")
        cursor = position


def brace_audit(text: str) -> tuple[int, int, int, int]:
    balance = minimum = opens = closes = 0
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
    ranges = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF))
    return sum(any(low <= ord(char) <= high for low, high in ranges) for char in text)


def located_lines(pattern: re.Pattern[str], text: str) -> tuple[int, ...]:
    return tuple(UNIT_START + text.count("\n", 0, match.start()) for match in pattern.finditer(text))


def gate_command_topology(source: Span, target: Span) -> None:
    source_all = COMMAND_RE.findall(source.text)
    target_all = COMMAND_RE.findall(target.text)
    require(len(source_all) == len(target_all) == 250, "command count differs from 250")
    require(Counter(source_all) == Counter(target_all), "command multiset differs")
    reordered: list[int] = []
    for line_number in range(UNIT_START, UNIT_END + 1):
        source_line = COMMAND_RE.findall(source.line(line_number))
        target_line = COMMAND_RE.findall(target.line(line_number))
        if source_line == target_line:
            continue
        reordered.append(line_number)
        require(Counter(source_line) == Counter(target_line), f"line {line_number}: command multiset differs")
    require(tuple(reordered) == EXPECTED_COMMAND_REORDER_LINES, f"command reorder lines differ: {reordered}")


def gate_inline_math(source: Span, target: Span) -> None:
    source_items = inline_math(source.text)
    target_items = inline_math(target.text)
    require(len(source_items) == len(target_items) == 80, "inline-math count differs from 80")
    source_by_line: dict[int, list[str]] = {}
    target_by_line: dict[int, list[str]] = {}
    for line, content in source_items:
        source_by_line.setdefault(line, []).append(content)
    for line, content in target_items:
        target_by_line.setdefault(line, []).append(content)

    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology differs")
    # The target explicitly names the forgetful functor U in Exercise 13,
    # removing an otherwise free U in the following prose.
    line_1644 = source_by_line[1644]
    require(line_1644[0] == COR_002_SOURCE, "line-1644 source correction signature missing")
    line_1644[0] = COR_002_TARGET

    reordered: list[int] = []
    for line in source_by_line:
        if source_by_line[line] == target_by_line[line]:
            continue
        reordered.append(line)
        require(
            Counter(source_by_line[line]) == Counter(target_by_line[line]),
            f"line {line}: mathematical-span multiset differs",
        )
    require(tuple(reordered) == EXPECTED_MATH_REORDER_LINES, f"math reorder lines differ: {reordered}")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source = read_span(SOURCE)
    target = read_span(TARGET)

    require(len(source.raw) == SOURCE_BYTES, "source span byte count changed")
    require(sha256(source.raw).hexdigest() == SOURCE_SHA256, "source span hash changed")
    require(len(target.raw) == TARGET_BYTES, "target span byte count changed")
    require(sha256(target.raw).hexdigest() == TARGET_SHA256, "target span hash changed")
    target_full = TARGET.read_bytes()
    require(len(target_full) == FULL_TARGET_BYTES, "full target byte count changed")
    require(sha256(target_full).hexdigest() == FULL_TARGET_SHA256, "full target hash changed")
    require(source.lines[0] == target.lines[0] == r"\begin{Exercises}", "opening boundary changed")
    require(source.lines[-1] == target.lines[-1] == r"\end{Exercises}", "closing/EOF boundary changed")
    require(comment_positions(source.lines) == comment_positions(target.lines) == [], "comments are not permitted in Unit 018")
    require(
        tuple(not line.strip() for line in source.lines) == tuple(not line.strip() for line in target.lines),
        "blank-line topology differs",
    )
    require(tuple(index for index, line in enumerate(source.lines, UNIT_START) if not line.strip()) == (1638,), "blank-line census changed")

    gate_command_topology(source, target)

    source_events = environment_events(source.text)
    target_events = environment_events(target.text)
    audit_nesting(source_events, "source")
    audit_nesting(target_events, "target")
    require(tuple(source_events) == tuple(target_events) == EXPECTED_ENV_EVENTS, "environment topology differs")

    require(located_lines(ITEM_RE, source.text) == located_lines(ITEM_RE, target.text) == EXPECTED_ITEM_LINES, "item topology differs")
    require(tuple(line for line in EXPECTED_ITEM_LINES if line not in EXPECTED_NESTED_ITEMS) == EXPECTED_TOP_LEVEL_ITEMS, "top-level item census defect")
    require(located_lines(HINT_RE, source.text) == located_lines(HINT_RE, target.text) == (1632,), "hint topology differs")
    require(REF_RE.findall(source.text) == REF_RE.findall(target.text) == list(EXPECTED_REFS), "reference topology differs")
    require(EQREF_RE.findall(source.text) == EQREF_RE.findall(target.text) == [], "unexpected eqref")
    require(LABEL_RE.findall(source.text) == LABEL_RE.findall(target.text) == [], "unexpected label")
    require(CITE_RE.findall(source.text) == CITE_RE.findall(target.text) == [], "unexpected citation")
    require(INDEX_RE.findall(source.text) == INDEX_RE.findall(target.text) == [], "unexpected index entry")

    gate_inline_math(source, target)

    source_displays = bracket_displays(source.text)
    target_displays = bracket_displays(target.text)
    require(len(source_displays) == len(target_displays) == 2, "bracket-display count differs from 2")
    require(source_displays == target_displays, "display mathematics/diagram differs")

    source_align = extract_environment(source.text, "align*")
    target_align = extract_environment(target.text, "align*")
    require(len(source_align) == len(target_align) == 1, "align* count differs from 1")
    require(
        mask_balanced_argument(source_align[0], "text") == mask_balanced_argument(target_align[0], "text"),
        "align/cases mathematics differs after masking translated text",
    )
    source_tikz = extract_environment(source.text, "tikzcd")
    target_tikz = extract_environment(target.text, "tikzcd")
    require(source_tikz == target_tikz and len(source_tikz) == 1, "tikzcd topology differs")
    require(len(ARROW_RE.findall(source.text)) == len(ARROW_RE.findall(target.text)) == 10, "arrow count differs from 10")

    require(brace_audit(source.text) == brace_audit(target.text) == (0, 0, 124, 124), "brace topology differs")
    require(han_count(target.text) == 0, "target Unit 018 contains Han residue")

    print(
        "\n".join(
            (
                "PASS Unit 018 structural checker",
                f"source lines=43 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"target lines=43 bytes={len(target.raw)} sha256={sha256(target.raw).hexdigest()}",
                "boundary=Exercises-at-1603..1645-EOF commands=250 environments=6-pairs comments=0 han=0",
                "top_level_exercises=13 nested_items=5 items=18 hints=1 refs=3 labels=0 eqrefs=0 cites=0 indexes=0",
                "inline_math=80 bracket_displays=2 align*=1 tikzcd=1 arrows=10 braces=124/124",
                "correction=O013-LI-U018-COR-002-explicit-U-domain",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 018 structural checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
