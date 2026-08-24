#!/usr/bin/env python3
"""Fail-closed structural check for Unit 016 (chapter 2, lines 1111--1405)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import sys


UNIT_START = 1111
UNIT_END = 1405
BOUNDARY_LINE = 1406
UNIT_LINE_COUNT = 295

SOURCE_BYTES = 24_790
SOURCE_SHA256 = "48abd6c33ecdc32591a05ecfbdc7381637027963a61cb3015016909a8faacf82"
TARGET_BYTES = 28_854
TARGET_SHA256 = "fe5e54d56824e8f1a76f93e1732220813c654ab16eb2d7c8daa8dcdde17f5c81"
EXPECTED_BOUNDARY = r"\section{完备性}"

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
INDEX_RE = re.compile(r"\\index(?:\[([^\]\r\n]*)\])?\{([^@{}\r\n]+)@([^{}\r\n]*)\}")
ITEM_RE = re.compile(r"\\item\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")

EXPECTED_ENVIRONMENTS = Counter(
    {
        "align*": 5,
        "array": 3,
        "asparaenum": 1,
        "cases": 1,
        "center": 1,
        "compactenum": 1,
        "compactitem": 1,
        "definition": 3,
        "enumerate": 1,
        "equation": 4,
        "equation*": 3,
        "example": 2,
        "gather*": 2,
        "gathered": 1,
        "lemma": 5,
        "proof": 5,
        "proposition": 2,
        "remark": 1,
        "tabular": 1,
        "tikzcd": 23,
    }
)

COR_001_SOURCE = r"(\varprojlim \beta, p_i: \varprojlim \beta \xrightarrow{p_i} \beta(i))"
COR_001_TARGET = r"(\varprojlim \beta, \varprojlim \beta \xrightarrow{p_i} \beta(i))"
COR_003_SOURCE_COLIMIT = r"\varinjlim \alpha(i)"
COR_003_TARGET_COLIMIT = r"\varinjlim_{i \in I} \alpha(i)"
COR_003_SOURCE_LIMIT = r"\prod_{i \in I} Y_i := \varprojlim \beta(i)"
COR_003_TARGET_LIMIT = r"\prod_{i \in I} Y_i := \varprojlim_{i \in I} \beta(i)"


class CheckFailure(RuntimeError):
    """A deterministic admission check failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def lf_records(data: bytes) -> list[bytes]:
    """Split bytes into one record per LF-terminated physical line."""
    records: list[bytes] = []
    start = 0
    for index, value in enumerate(data):
        if value == 0x0A:
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
class UnitSpan:
    raw: bytes
    lines: tuple[str, ...]
    boundary: str

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def line(self, absolute_line: int) -> str:
        require(
            UNIT_START <= absolute_line <= UNIT_END,
            f"line {absolute_line} is outside Unit 016",
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
    require(len(selected) == UNIT_LINE_COUNT, f"{path}: Unit 016 line-count extraction failed")
    require(
        all(record.endswith(b"\n") for record in selected),
        f"{path}: every Unit 016 record must remain LF-terminated",
    )
    return UnitSpan(
        raw=b"".join(selected),
        lines=tuple(record_text(record) for record in selected),
        boundary=record_text(records[BOUNDARY_LINE - 1]),
    )


def is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


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


def mask_text_arguments(text: str) -> str:
    """Replace every balanced \text{...} argument without touching other TeX."""
    needle = r"\text{"
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
            char = text[position]
            if char == "{" and not is_escaped(text, position):
                depth += 1
            elif char == "}" and not is_escaped(text, position):
                depth -= 1
            position += 1
        require(depth == 0, "unterminated \\text argument")
        output.append(r"\text{<PROSE>}")
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


def command_insertions(source: list[str], target: list[str]) -> list[str]:
    source_cursor = 0
    inserted: list[str] = []
    for token in target:
        if source_cursor < len(source) and token == source[source_cursor]:
            source_cursor += 1
        else:
            inserted.append(token)
    require(source_cursor == len(source), "target command sequence deletes, substitutes, or reorders source commands")
    return inserted


def without_emphasis(tokens: list[str]) -> list[str]:
    """Remove prose emphasis commands while retaining all mathematical commands."""
    return [token for token in tokens if token != r"\emph"]


def gate_exact_corrections(source: UnitSpan, target: UnitSpan) -> None:
    source_1177 = source.line(1177)
    target_1177 = target.line(1177)
    require(COR_001_SOURCE in source_1177, "COR-001 source signature missing at line 1177")
    require(COR_001_TARGET in target_1177, "COR-001 target repair missing at line 1177")
    require("p_i: \\varprojlim" not in target_1177, "COR-001 duplicate p_i remains in target")

    source_1343 = source.line(1343)
    target_1343 = target.line(1343)
    require(
        "因此断言中左项的极限有意义, 右项亦同." in source_1343,
        "COR-002 source left/right signature missing at line 1343",
    )
    target_right = target_1343.find("ruas kanan")
    target_left = target_1343.find("ruas kiri")
    require(
        0 <= target_right < target_left,
        "COR-002 target must establish the right term before the left term",
    )
    require(
        inline_math(source_1343, 1343) == inline_math(target_1343, 1343),
        "COR-002 must change prose only, not line-1343 mathematics",
    )

    source_1348 = source.line(1348)
    target_1348 = target.line(1348)
    require(COR_003_SOURCE_COLIMIT in source_1348, "COR-003 source colimit signature missing")
    require(COR_003_TARGET_COLIMIT in target_1348, "COR-003 target colimit binder missing")
    require(COR_003_SOURCE_LIMIT in source_1348, "COR-003 source limit signature missing")
    require(COR_003_TARGET_LIMIT in target_1348, "COR-003 target limit binder missing")

    source_inline = inline_math(source.text)
    target_inline = inline_math(target.text)
    require(len(source_inline) == 287, f"source inline math: expected 287, got {len(source_inline)}")
    require(len(target_inline) == 287, f"target inline math: expected 287, got {len(target_inline)}")
    mismatches = [
        (source_item, target_item)
        for source_item, target_item in zip(source_inline, target_inline, strict=True)
        if source_item != target_item
    ]
    expected_mismatches = [
        ((1177, COR_001_SOURCE), (1177, COR_001_TARGET)),
        ((1348, COR_003_SOURCE_COLIMIT), (1348, COR_003_TARGET_COLIMIT)),
        ((1348, COR_003_SOURCE_LIMIT), (1348, COR_003_TARGET_LIMIT)),
    ]
    require(
        mismatches == expected_mismatches,
        f"undeclared inline-math differences: {mismatches!r}",
    )
    repairs = {
        COR_001_SOURCE: COR_001_TARGET,
        COR_003_SOURCE_COLIMIT: COR_003_TARGET_COLIMIT,
        COR_003_SOURCE_LIMIT: COR_003_TARGET_LIMIT,
    }
    normalized_source = [repairs.get(content, content) for _, content in source_inline]
    normalized_target = [content for _, content in target_inline]
    require(normalized_source == normalized_target, "declared inline-math normalization failed")


def gate_official_errata(source: UnitSpan, target: UnitSpan) -> None:
    source_cones = source.line(1175)
    target_cones = target.line(1175)
    require(
        source_cones.find(r"$(\alpha/\Delta)$")
        < source_cones.find(r"$(\Delta/\beta)$")
        < source_cones.find("锥")
        < source_cones.find("余锥"),
        "authority cone/cocone order is not the admitted order",
    )
    require(
        target_cones.find(r"$(\alpha/\Delta)$")
        < target_cones.find(r"$(\Delta/\beta)$")
        < target_cones.find("kerucut")
        < target_cones.find("kokerucut"),
        "target cone/cocone order is not preserved",
    )

    source_mapsto = source.lines[1249 - UNIT_START : 1257 - UNIT_START + 1]
    target_mapsto = target.lines[1249 - UNIT_START : 1257 - UNIT_START + 1]
    require(source_mapsto == target_mapsto, "post-Equation-(2.11) diagram differs from authority")
    require(
        target.line(1254).count(r"\arrow[mapsto") == 4
        and r"\arrow[dashed, mapsto, ld]" in target.line(1255),
        "admitted post-Equation-(2.11) mapsto topology is missing",
    )


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source = read_unit(SOURCE_PATH)
    target = read_unit(TARGET_PATH)

    require(len(source.lines) == UNIT_LINE_COUNT, "source must contain 295 Unit 016 records")
    require(len(target.lines) == UNIT_LINE_COUNT, "target must contain 295 Unit 016 records")
    require(len(source.raw) == SOURCE_BYTES, f"source span byte count changed: {len(source.raw)}")
    require(sha256(source.raw).hexdigest() == SOURCE_SHA256, "source span SHA-256 changed")
    require(len(target.raw) == TARGET_BYTES, f"target span byte count changed: {len(target.raw)}")
    require(sha256(target.raw).hexdigest() == TARGET_SHA256, "target span SHA-256 changed")
    require(source.boundary == EXPECTED_BOUNDARY, "authority line 1406 boundary changed")
    require(target.boundary == EXPECTED_BOUNDARY, "target line 1406 is not the Chinese completeness section")
    require(source.line(1405).strip() == "", "authority Unit 016 must end on a blank record")
    require(target.line(1405).strip() == "", "target Unit 016 must end on a blank record")

    source_blank = tuple(not line.strip() for line in source.lines)
    target_blank = tuple(not line.strip() for line in target.lines)
    require(source_blank == target_blank, "blank-line topology differs")
    require(sum(source_blank) == 25, f"expected 25 blank lines, got {sum(source_blank)}")

    source_commands = COMMAND_RE.findall(source.text)
    target_commands = COMMAND_RE.findall(target.text)
    require(len(source_commands) == 1_382, f"source commands: expected 1382, got {len(source_commands)}")
    require(len(target_commands) == 1_384, f"target commands: expected 1384, got {len(target_commands)}")
    require(
        Counter(target_commands) - Counter(source_commands) == Counter({r"\in": 2})
        and not (Counter(source_commands) - Counter(target_commands)),
        "the command multiset may gain only the two COR-003 \\in binders",
    )
    require(
        command_insertions(without_emphasis(source_commands), without_emphasis(target_commands))
        == [r"\in", r"\in"],
        "after the two declared emphasis relocations, only the COR-003 \\in insertions are allowed",
    )
    ordered_command_diff_lines: list[int] = []
    multiset_command_diff_lines: list[int] = []
    for line_number in range(UNIT_START, UNIT_END + 1):
        source_line_commands = COMMAND_RE.findall(source.line(line_number))
        target_line_commands = COMMAND_RE.findall(target.line(line_number))
        if source_line_commands != target_line_commands:
            ordered_command_diff_lines.append(line_number)
        if Counter(source_line_commands) != Counter(target_line_commands):
            multiset_command_diff_lines.append(line_number)
    require(
        ordered_command_diff_lines == [1134, 1135, 1348],
        f"unexpected ordered command-difference lines: {ordered_command_diff_lines}",
    )
    require(
        multiset_command_diff_lines == [1348],
        f"unexpected command-multiset difference lines: {multiset_command_diff_lines}",
    )
    expected_emphasis_relocations = {
        1134: (
            [r"\item", r"\alpha", r"\Delta", r"\varinjlim", r"\alpha", r"\alpha", r"\emph"],
            [r"\item", r"\alpha", r"\Delta", r"\varinjlim", r"\alpha", r"\emph", r"\alpha"],
        ),
        1135: (
            [r"\item", r"\Delta", r"\beta", r"\varprojlim", r"\beta", r"\beta", r"\emph"],
            [r"\item", r"\Delta", r"\beta", r"\varprojlim", r"\beta", r"\emph", r"\beta"],
        ),
    }
    for line_number, (expected_source, expected_target) in expected_emphasis_relocations.items():
        require(
            COMMAND_RE.findall(source.line(line_number)) == expected_source
            and COMMAND_RE.findall(target.line(line_number)) == expected_target,
            f"line {line_number} is not the exact admitted Indonesian emphasis relocation",
        )
        require(
            inline_math(source.line(line_number), line_number)
            == inline_math(target.line(line_number), line_number),
            f"line {line_number} emphasis relocation changed mathematics",
        )
    require(
        command_insertions(COMMAND_RE.findall(source.line(1348)), COMMAND_RE.findall(target.line(1348)))
        == [r"\in", r"\in"],
        "line 1348 has command differences beyond the two explicit binders",
    )

    gate_exact_corrections(source, target)

    source_displays = bracket_displays(source.text)
    target_displays = bracket_displays(target.text)
    require(len(source_displays) == 12, f"source bracket displays: expected 12, got {len(source_displays)}")
    require(len(target_displays) == 12, f"target bracket displays: expected 12, got {len(target_displays)}")
    require(
        [mask_text_arguments(item) for item in source_displays]
        == [mask_text_arguments(item) for item in target_displays],
        "bracket-display mathematics differs after masking translated \\text prose",
    )

    source_events = environment_events(source.text)
    target_events = environment_events(target.text)
    audit_environment_nesting(source_events, "source")
    audit_environment_nesting(target_events, "target")
    source_begins = [name for kind, name in source_events if kind == "begin"]
    source_ends = [name for kind, name in source_events if kind == "end"]
    target_begins = [name for kind, name in target_events if kind == "begin"]
    target_ends = [name for kind, name in target_events if kind == "end"]
    require(len(source_begins) == len(source_ends) == 66, "source must have 66 begins and 66 ends")
    require(len(target_begins) == len(target_ends) == 66, "target must have 66 begins and 66 ends")
    require(source_begins == target_begins, "environment begin-name sequence differs")
    require(source_ends == target_ends, "environment end-name sequence differs")
    require(Counter(source_begins) == EXPECTED_ENVIRONMENTS, "source environment inventory changed")
    require(Counter(target_begins) == EXPECTED_ENVIRONMENTS, "target environment inventory changed")

    for environment, expected_count in (("gather*", 2), ("align*", 5), ("equation", 4), ("equation*", 3)):
        source_math = extract_environments(source.text, environment)
        target_math = extract_environments(target.text, environment)
        require(len(source_math) == expected_count, f"source {environment} count changed")
        require(len(target_math) == expected_count, f"target {environment} count changed")
        require(
            [mask_text_arguments(item) for item in source_math]
            == [mask_text_arguments(item) for item in target_math],
            f"{environment} mathematics differs after masking translated \\text prose",
        )

    source_labels = LABEL_RE.findall(source.text)
    target_labels = LABEL_RE.findall(target.text)
    source_refs = REF_RE.findall(source.text)
    target_refs = REF_RE.findall(target.text)
    source_eqrefs = EQREF_RE.findall(source.text)
    target_eqrefs = EQREF_RE.findall(target.text)
    source_cites = CITE_RE.findall(source.text)
    target_cites = CITE_RE.findall(target.text)
    source_indexes = INDEX_RE.findall(source.text)
    target_indexes = INDEX_RE.findall(target.text)
    require(len(source_labels) == len(target_labels) == 17 and source_labels == target_labels, "label targets differ")
    require(len(source_refs) == len(target_refs) == 21 and source_refs == target_refs, "ref targets differ")
    require(len(source_eqrefs) == len(target_eqrefs) == 7 and source_eqrefs == target_eqrefs, "eqref targets differ")
    require(len(source_cites) == len(target_cites) == 1 and source_cites == target_cites, "citation differs")
    require(len(source_indexes) == len(target_indexes) == 13, "index count differs from 13")
    require(
        [(namespace, sort_key) for namespace, sort_key, _ in source_indexes]
        == [(namespace, sort_key) for namespace, sort_key, _ in target_indexes],
        "index namespace or sort-key sequence differs",
    )
    require(
        sum(source_item == target_item for source_item, target_item in zip(source_indexes, target_indexes, strict=True)) == 4,
        "expected four unchanged symbolic index entries",
    )

    require(len(ITEM_RE.findall(source.text)) == 9, "source item count differs from 9")
    require(len(ITEM_RE.findall(target.text)) == 9, "target item count differs from 9")
    source_tikz = extract_environments(source.text, "tikzcd")
    target_tikz = extract_environments(target.text, "tikzcd")
    require(len(source_tikz) == len(target_tikz) == 23, "tikzcd count differs from 23")
    require(source_tikz == target_tikz, "diagram topology is not byte-text identical after EOL normalization")
    require(len(ARROW_RE.findall(source.text)) == 98, "source arrow count differs from 98")
    require(len(ARROW_RE.findall(target.text)) == 98, "target arrow count differs from 98")

    source_braces = brace_audit(source.text)
    target_braces = brace_audit(target.text)
    require(source_braces == (0, 0, 438, 438), f"source brace audit changed: {source_braces}")
    require(target_braces == (0, 0, 440, 440), f"target brace audit changed: {target_braces}")
    require(han_count(target.text) == 0, "target Unit 016 contains Han residue")

    gate_official_errata(source, target)

    report = "\n".join(
        (
            "PASS Unit 016 structural checker",
            f"source lines=295 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
            f"target lines=295 bytes={len(target.raw)} sha256={sha256(target.raw).hexdigest()}",
            "boundary line=1406 value=verified-Chinese-completeness-section",
            "commands=1382/1384 inserted=\\in,\\in emph_relocations=1134,1135 inline_math=287/287 bracket_displays=12/12",
            "begin=66/66 end=66/66 labels=17 refs=21 eqrefs=7 cite=1 indexes=13 items=9",
            "tikzcd=23 arrows=98 han=0 braces=438/438:440/440 diagrams=exact",
            "corrections=O013-LI-U016-COR-001,002,003 official_errata=preserved",
        )
    )
    print(report)


def main() -> int:
    try:
        run_checks()
    except Exception as error:  # Fail closed for expected and unexpected checker errors.
        print(f"FAIL Unit 016 structural checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
