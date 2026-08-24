#!/usr/bin/env python3
"""Fail-closed mathematics/protected-topology check for Unit 021 candidate/canonical span."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
)
CANDIDATE = ROOT / "build/unit-021-candidate/chapter3-braiding-id.tex"
TARGET = ROOT / "repo/source/chapter3.tex"

SOURCE_START = 307
SOURCE_END = 512
SOURCE_FULL_LINES = 911
CANDIDATE_LINES = 206
TARGET_START = 306
TARGET_END = 511
TARGET_FULL_LINES = 910

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_PREFIX_BYTES = 27_816
SOURCE_PREFIX_SHA256 = "ffce6a027b6d3ceacffd30548553b7539688ff552f075127dd769a9900bbfff5"
SOURCE_SPAN_BYTES = 15_276
SOURCE_SPAN_SHA256 = "cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8"
SOURCE_SUFFIX_BYTES = 32_479
SOURCE_SUFFIX_SHA256 = "0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83"
CANDIDATE_BYTES = 17_968
CANDIDATE_SHA256 = "57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085"
TARGET_FULL_BYTES = 83_581
TARGET_FULL_SHA256 = "ce310d940819f0fc51ee6459f73a8380b602edee42ef666720e225451adee9f9"
TARGET_PREFIX_BYTES = 33_134
TARGET_PREFIX_SHA256 = "db4b9e76f638eb4338f496664e58213102c1ccc6b8933e890bb5d00fa1702ae0"
TARGET_SPAN_BYTES = CANDIDATE_BYTES
TARGET_SPAN_SHA256 = CANDIDATE_SHA256
TARGET_SUFFIX_BYTES = SOURCE_SUFFIX_BYTES
TARGET_SUFFIX_SHA256 = SOURCE_SUFFIX_SHA256

SOURCE_START_LINE_BYTES = 40
SOURCE_START_LINE_SHA256 = "0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8"
CANDIDATE_START_LINE_BYTES = 46
CANDIDATE_START_LINE_SHA256 = "8acd960675d96dd70537f2cb73f61098075ac025b1b983fcc584dd66573605bd"
INCLUDED_BLANK_BYTES = 1
INCLUDED_BLANK_SHA256 = "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b"
NEXT_LINE_BYTES = 47
NEXT_LINE_SHA256 = "c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541"

SOURCE_START_LINE = r"\section{辫结构}\label{sec:braiding}"
CANDIDATE_START_LINE = r"\section{Struktur Kepang}\label{sec:braiding}"
NEXT_LINE = r"\section{充实范畴}\label{sec:enriched-cat}"

CORRECTION_NATURALITY = "O013-LI-U021-COR-001"
CORRECTION_OBJECTS = "O013-LI-U021-COR-002"
EDITORIAL_DUPLICATE = "O013-LI-U021-ED-001"
PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"

BAD_NATURALITY_ROW = "\t\t" + r'''X \otimes Y \arrow[r, "{c(X, Y)}"'] & Y \otimes X'''
GOOD_NATURALITY_ROW = "\t\t" + r"""X' \otimes Y' \arrow[r, "{c(X', Y')}"'] & Y' \otimes X'"""
BAD_OBJECT_X = "对应于辫子 $X$"
BAD_OBJECT_Y = "对应于辫子 $Y$"
GOOD_OBJECT_X = "bersesuaian dengan objek $X$"
GOOD_OBJECT_Y = "bersesuaian dengan objek $Y$"
BAD_DUPLICATE = "无穷循环群群"
GOOD_DUPLICATE = "grup siklik tak hingga"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
CROSS_REF_RE = re.compile(r"\\(ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}")
ITEM_RE = re.compile(r"\\item\b")
INDEX_OPEN_RE = re.compile(r"\\index(?:\[([^\]]*)\])?\{")
NODE_RE = re.compile(r"\\node\b")
COORDINATE_RE = re.compile(r"\\coordinate\b")
DRAW_RE = re.compile(r"\\draw\b")
PATH_RE = re.compile(r"\\path\b")
EDGE_RE = re.compile(r"\bedge\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")
BRAID_RE = re.compile(r"\\braid\b")
HLINE_RE = re.compile(r"\\hline\b")

EXPECTED_BEGIN_COUNTS = Counter(
    {
        "tikzpicture": 17,
        "tikzcd": 6,
        "center": 4,
        "definition": 3,
        "equation": 3,
        "remark": 2,
        "align*": 2,
        "example": 2,
        "proposition": 1,
        "proof": 1,
        "multline*": 1,
        "array": 1,
    }
)

EXPECTED_LABELS = (
    (1, "sec:braiding"),
    (4, "def:braiding"),
    (8, "eqn:hexagon-axiom-1"),
    (13, "eqn:hexagon-axiom-2"),
    (30, "rem:hexagon-axiom-strict"),
    (46, "def:symm-monoidal-cat"),
    (59, "prop:YBE-cat-strict"),
    (88, "rem:YBE-cat-strict"),
    (97, "eg:braid"),
)

EXPECTED_CROSS_REFS = (
    (2, "ref", "eg:braid"),
    (29, "eqref", "eqn:hexagon-axiom-1"),
    (29, "eqref", "eqn:hexagon-axiom-2"),
    (31, "ref", "def:strict-monoidal-cat"),
    (51, "ref", "eg:monoidal-cat"),
    (51, "ref", "prop:product-commutativity"),
    (56, "ref", "sec:module-tensor-prod"),
    (128, "ref", "eg:fundamental-groupoid"),
    (130, "ref", "sec:symmetric-group"),
    (130, "eqref", "eqn:braid-presentation"),
    (166, "ref", "rem:hexagon-axiom-strict"),
    (168, "ref", "rem:YBE-cat-strict"),
    (205, "ref", "def:braiding"),
)

EXPECTED_CITES = (
    (2, r"\cite{JS93}"),
    (205, r"\cite[Corollary 2.6]{JS93}"),
)

EXPECTED_TARGET_INDEXES = (
    (4, None, "bianjiegou@struktur kepang (braiding)"),
    (4, None, "liujiaoxinggongli@aksioma segienam (hexagon axiom)"),
    (
        38,
        None,
        "yaobanhanzi@fungtor monoidal (monoidal functor)!berkepang (braided)",
    ),
    (
        46,
        None,
        "yaobanfanchou@kategori monoidal (monoidal category)!"
        "kategori monoidal simetris (symmetric monoidal category)",
    ),
    (59, None, "YBE@persamaan Yang--Baxter (Yang--Baxter equation)"),
    (97, "sym1", r"Braid@$\cate{Braid}$"),
    (130, None, "bianqun@grup kepang (braid group)"),
    (130, "sym1", r"B_n@$\mathcal{B}_n$"),
)

EXPECTED_TIKZCD_SPANS = (
    (8, 12),
    (13, 17),
    (19, 22),
    (22, 25),
    (40, 43),
    (179, 182),
)

EXPECTED_TIKZPICTURE_SPANS = (
    (61, 81),
    (103, 111),
    (111, 116),
    (121, 127),
    (133, 139),
    (143, 143),
    (145, 145),
    (147, 153),
    (154, 154),
    (154, 154),
    (155, 159),
    (161, 165),
    (169, 171),
    (173, 175),
    (183, 194),
    (196, 198),
    (199, 201),
)


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
    require(not record.endswith(b"\r"), "CRLF record encountered; reviewed inputs are LF-only")
    return record.decode("utf-8", errors="strict")


@dataclass(frozen=True)
class FileView:
    raw: bytes
    records: tuple[bytes, ...]
    lines: tuple[str, ...]


@dataclass(frozen=True)
class Span:
    raw: bytes
    lines: tuple[str, ...]

    @property
    def text(self) -> str:
        return self.raw.decode("utf-8", errors="strict")

    def line(self, line_number: int) -> str:
        return self.lines[line_number - 1]


@dataclass(frozen=True)
class EnvironmentOccurrence:
    start_line: int
    end_line: int
    text: str


def read_file(path: Path, expected_lines: int) -> FileView:
    require(path.is_file(), f"missing input: {path}")
    data = path.read_bytes()
    records = lf_records(data)
    require(data.endswith(b"\n"), f"{path}: file must end with LF")
    require(len(records) == expected_lines, f"{path}: physical LF-record count changed")
    require(all(record.endswith(b"\n") for record in records), f"{path}: unterminated record")
    return FileView(data, tuple(records), tuple(record_text(record) for record in records))


def make_span(view: FileView, start: int, end: int) -> Span:
    records = view.records[start - 1 : end]
    require(len(records) == end - start + 1, f"could not extract lines {start}-{end}")
    return Span(b"".join(records), tuple(record_text(record) for record in records))


def hash_gate(name: str, data: bytes, expected_bytes: int, expected_hash: str) -> None:
    require(len(data) == expected_bytes, f"{name}: byte count changed")
    require(sha256(data).hexdigest() == expected_hash, f"{name}: SHA-256 changed")


def line_number(text: str, position: int) -> int:
    return 1 + text.count("\n", 0, position)


def is_escaped(text: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def inline_math(text: str) -> list[tuple[int, str]]:
    delimiters = [
        position
        for position, char in enumerate(text)
        if char == "$" and not is_escaped(text, position)
    ]
    require(len(delimiters) % 2 == 0, "unpaired inline-math delimiter")
    return [
        (line_number(text, opening), text[opening + 1 : closing])
        for opening, closing in zip(delimiters[::2], delimiters[1::2])
    ]


def bracket_displays(text: str) -> list[str]:
    displays: list[str] = []
    cursor = 0
    while True:
        opening = text.find(r"\[", cursor)
        if opening < 0:
            break
        closing = text.find(r"\]", opening + 2)
        require(closing >= 0, "unterminated bracket display")
        displays.append(text[opening + 2 : closing])
        cursor = closing + 2
    require(text.count(r"\[") == text.count(r"\]") == len(displays), "display delimiter mismatch")
    return displays


def localized_math(text: str, repair_naturality: bool = False) -> str:
    if repair_naturality:
        text = text.replace(BAD_NATURALITY_ROW, GOOD_NATURALITY_ROW)
    text = re.sub(r"\\text\{[^{}]*\}", r"\\text{<localized>}", text)
    return re.sub(r"\s+", "", text)


def located_values(pattern: re.Pattern[str], text: str) -> tuple[tuple[int, str], ...]:
    return tuple(
        (line_number(text, match.start()), match.group(1))
        for match in pattern.finditer(text)
    )


def located_lines(pattern: re.Pattern[str], text: str) -> tuple[int, ...]:
    return tuple(line_number(text, match.start()) for match in pattern.finditer(text))


def environment_events(text: str) -> tuple[tuple[int, str, str], ...]:
    return tuple(
        (line_number(text, match.start()), match.group(1), match.group(2))
        for match in ENV_RE.finditer(text)
    )


def audit_nesting(events: tuple[tuple[int, str, str], ...], name: str) -> None:
    stack: list[str] = []
    for line, kind, environment in events:
        if kind == "begin":
            stack.append(environment)
            continue
        require(bool(stack), f"{name}:{line}: unmatched end of {environment}")
        require(stack[-1] == environment, f"{name}:{line}: crossed environment {environment}")
        stack.pop()
    require(not stack, f"{name}: unclosed environments: {stack}")


def environment_occurrences(text: str, name: str) -> tuple[EnvironmentOccurrence, ...]:
    pattern = re.compile(
        rf"\\begin\{{{re.escape(name)}\}}.*?\\end\{{{re.escape(name)}\}}",
        re.DOTALL,
    )
    return tuple(
        EnvironmentOccurrence(
            line_number(text, match.start()),
            line_number(text, match.end() - 1),
            match.group(0),
        )
        for match in pattern.finditer(text)
    )


def balanced_argument(text: str, opening: int) -> tuple[str, int]:
    require(text[opening] == "{", "balanced parser did not start on an opening brace")
    depth = 0
    for position in range(opening, len(text)):
        if is_escaped(text, position):
            continue
        if text[position] == "{":
            depth += 1
        elif text[position] == "}":
            depth -= 1
            if depth == 0:
                return text[opening + 1 : position], position + 1
        require(depth >= 0, "balanced parser crossed below zero")
    raise CheckFailure("unterminated balanced argument")


def index_occurrences(text: str) -> tuple[tuple[int, str | None, str], ...]:
    occurrences: list[tuple[int, str | None, str]] = []
    for match in INDEX_OPEN_RE.finditer(text):
        value, _ = balanced_argument(text, match.end() - 1)
        occurrences.append((line_number(text, match.start()), match.group(1), value))
    return tuple(occurrences)


def brace_audit(text: str) -> tuple[int, int, int, int]:
    depth = 0
    minimum = 0
    opens = 0
    closes = 0
    for position, char in enumerate(text):
        if is_escaped(text, position):
            continue
        if char == "{":
            depth += 1
            opens += 1
        elif char == "}":
            depth -= 1
            closes += 1
            minimum = min(minimum, depth)
    return depth, minimum, opens, closes


def han_count(text: str) -> int:
    def is_han(char: str) -> bool:
        value = ord(char)
        return (
            0x3400 <= value <= 0x4DBF
            or 0x4E00 <= value <= 0x9FFF
            or 0xF900 <= value <= 0xFAFF
            or 0x20000 <= value <= 0x2EBEF
            or 0x30000 <= value <= 0x323AF
        )

    return sum(is_han(char) for char in text)


def gate_identities_and_boundaries(
    source_view: FileView,
    candidate_view: FileView,
    target_view: FileView,
    source: Span,
    target: Span,
) -> None:
    source_prefix = b"".join(source_view.records[: SOURCE_START - 1])
    source_suffix = b"".join(source_view.records[SOURCE_END:])
    target_prefix = b"".join(target_view.records[: TARGET_START - 1])
    target_suffix = b"".join(target_view.records[TARGET_END:])

    hash_gate("source full file", source_view.raw, SOURCE_FULL_BYTES, SOURCE_FULL_SHA256)
    hash_gate("source prefix 1-306", source_prefix, SOURCE_PREFIX_BYTES, SOURCE_PREFIX_SHA256)
    hash_gate("source span 307-512", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix 513-911", source_suffix, SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256)
    hash_gate("candidate full file", candidate_view.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)
    hash_gate("target full file", target_view.raw, TARGET_FULL_BYTES, TARGET_FULL_SHA256)
    hash_gate("target prefix 1-305", target_prefix, TARGET_PREFIX_BYTES, TARGET_PREFIX_SHA256)
    hash_gate("target span 306-511", target.raw, TARGET_SPAN_BYTES, TARGET_SPAN_SHA256)
    hash_gate("target suffix 512-910", target_suffix, TARGET_SUFFIX_BYTES, TARGET_SUFFIX_SHA256)
    hash_gate(
        "source opening line 307",
        source_view.records[SOURCE_START - 1],
        SOURCE_START_LINE_BYTES,
        SOURCE_START_LINE_SHA256,
    )
    hash_gate(
        "candidate opening line 1",
        candidate_view.records[0],
        CANDIDATE_START_LINE_BYTES,
        CANDIDATE_START_LINE_SHA256,
    )
    hash_gate(
        "source included blank line 512",
        source_view.records[SOURCE_END - 1],
        INCLUDED_BLANK_BYTES,
        INCLUDED_BLANK_SHA256,
    )
    hash_gate(
        "candidate included blank line 206",
        candidate_view.records[-1],
        INCLUDED_BLANK_BYTES,
        INCLUDED_BLANK_SHA256,
    )
    hash_gate(
        "source next line 513",
        source_view.records[SOURCE_END],
        NEXT_LINE_BYTES,
        NEXT_LINE_SHA256,
    )

    require(source.line(1) == SOURCE_START_LINE, "source Unit 021 opening changed")
    require(candidate_view.lines[0] == CANDIDATE_START_LINE, "candidate Unit 021 opening changed")
    require(source.line(CANDIDATE_LINES) == "", "source line 512 must be the included blank")
    require(candidate_view.lines[-1] == "", "candidate line 206 must be the included blank")
    require(source_view.lines[SOURCE_END] == NEXT_LINE, "source line 513 boundary changed")
    require(target.line(1) == CANDIDATE_START_LINE, "target Unit 021 opening changed")
    require(target.line(CANDIDATE_LINES) == "", "target line 511 must be the included blank")
    require(target_view.lines[TARGET_END] == NEXT_LINE, "target line 512 boundary changed")
    require("sec:enriched-cat" not in candidate_view.raw.decode("utf-8"), "next section leaked into candidate")
    require(target.raw == candidate_view.raw, "canonical Unit 021 span is not byte-identical to candidate")
    require(target_suffix == source_suffix, "post-Unit-021 canonical remainder differs from authority")


def gate_declared_corrections(source: Span, candidate: Span) -> None:
    require(source.line(181) == BAD_NATURALITY_ROW, "COR-001 authority row moved or changed")
    require(candidate.line(181) == GOOD_NATURALITY_ROW, "COR-001 candidate row moved or changed")
    require(source.text.count(BAD_NATURALITY_ROW) == 1, "COR-001 authority signature census changed")
    require(source.text.count(GOOD_NATURALITY_ROW) == 0, "authority unexpectedly contains corrected row")
    require(candidate.text.count(BAD_NATURALITY_ROW) == 0, "COR-001 defective row remains in candidate")
    require(candidate.text.count(GOOD_NATURALITY_ROW) == 1, "COR-001 candidate signature census changed")

    require(BAD_OBJECT_X in source.line(144), "COR-002 X authority signature moved or changed")
    require(BAD_OBJECT_Y in source.line(146), "COR-002 Y authority signature moved or changed")
    require(GOOD_OBJECT_X in candidate.line(144), "COR-002 X candidate repair moved or changed")
    require(GOOD_OBJECT_Y in candidate.line(146), "COR-002 Y candidate repair moved or changed")
    require(source.text.count(BAD_OBJECT_X) == source.text.count(BAD_OBJECT_Y) == 1, "COR-002 source census changed")
    require(candidate.text.count(GOOD_OBJECT_X) == candidate.text.count(GOOD_OBJECT_Y) == 1, "COR-002 target census changed")

    require(BAD_DUPLICATE in source.line(202), "ED-001 authority signature moved or changed")
    require(source.text.count(BAD_DUPLICATE) == 1, "ED-001 authority census changed")
    require(BAD_DUPLICATE not in candidate.text, "ED-001 duplicated noun remains in candidate")
    require(GOOD_DUPLICATE in candidate.line(202), "ED-001 candidate normalization moved or changed")


def gate_commands_and_math(source: Span, candidate: Span) -> None:
    for relative_line, (source_line, candidate_line) in enumerate(
        zip(source.lines, candidate.lines, strict=True), 1
    ):
        require(
            Counter(COMMAND_RE.findall(source_line)) == Counter(COMMAND_RE.findall(candidate_line)),
            f"relative line {relative_line}: TeX command multiset changed",
        )
    require(len(COMMAND_RE.findall(source.text)) == 527, "source command census changed")
    require(len(COMMAND_RE.findall(candidate.text)) == 527, "candidate command census changed")

    source_inline = inline_math(source.text)
    target_inline = inline_math(candidate.text)
    require(len(source_inline) == len(target_inline) == 144, "inline-math census changed")
    source_by_line: dict[int, list[str]] = defaultdict(list)
    target_by_line: dict[int, list[str]] = defaultdict(list)
    for line, value in source_inline:
        source_by_line[line].append(localized_math(value, repair_naturality=True))
    for line, value in target_inline:
        target_by_line[line].append(localized_math(value))
    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology changed")
    reorder_lines: list[int] = []
    for line in source_by_line:
        require(
            Counter(source_by_line[line]) == Counter(target_by_line[line]),
            f"relative line {line}: inline mathematics changed beyond localization/COR-001",
        )
        if source_by_line[line] != target_by_line[line]:
            reorder_lines.append(line)
    require(
        tuple(reorder_lines) == (100, 132, 144, 146),
        f"reviewed within-line formula reorder topology changed: {reorder_lines}",
    )

    source_displays = bracket_displays(source.text)
    candidate_displays = bracket_displays(candidate.text)
    require(len(source_displays) == len(candidate_displays) == 6, "bracket-display census changed")
    require(
        tuple(localized_math(value) for value in source_displays)
        == tuple(localized_math(value) for value in candidate_displays),
        "bracket-display mathematics changed",
    )

    for environment, expected_count in (("equation", 3), ("align*", 2), ("multline*", 1)):
        source_occurrences = environment_occurrences(source.text, environment)
        candidate_occurrences = environment_occurrences(candidate.text, environment)
        require(
            len(source_occurrences) == len(candidate_occurrences) == expected_count,
            f"{environment} display census changed",
        )
        require(
            tuple(item.text for item in source_occurrences)
            == tuple(item.text for item in candidate_occurrences),
            f"{environment} mathematics changed",
        )


def gate_document_topology(source: Span, candidate: Span) -> None:
    source_events = environment_events(source.text)
    candidate_events = environment_events(candidate.text)
    audit_nesting(source_events, "source span")
    audit_nesting(candidate_events, "candidate")
    require(source_events == candidate_events, "ordered environment topology changed")
    require(len(source_events) == len(candidate_events) == 86, "environment event census changed")
    begins = Counter(name for _, kind, name in source_events if kind == "begin")
    ends = Counter(name for _, kind, name in source_events if kind == "end")
    require(begins == ends == EXPECTED_BEGIN_COUNTS, "environment type census changed")

    require(
        located_values(LABEL_RE, source.text)
        == located_values(LABEL_RE, candidate.text)
        == EXPECTED_LABELS,
        "label topology changed",
    )

    def cross_refs(text: str) -> tuple[tuple[int, str, str], ...]:
        return tuple(
            (line_number(text, match.start()), match.group(1), match.group(2))
            for match in CROSS_REF_RE.finditer(text)
        )

    require(
        cross_refs(source.text) == cross_refs(candidate.text) == EXPECTED_CROSS_REFS,
        "reference topology changed",
    )

    def citations(text: str) -> tuple[tuple[int, str], ...]:
        return tuple(
            (line_number(text, match.start()), match.group(0))
            for match in CITE_RE.finditer(text)
        )

    require(
        citations(source.text) == citations(candidate.text) == EXPECTED_CITES,
        "citation topology changed",
    )
    require(not ITEM_RE.search(source.text) and not ITEM_RE.search(candidate.text), "unexpected item in Unit 021")
    require("%" not in source.text and "%" not in candidate.text, "unexpected TeX comment in Unit 021")


def gate_diagrams_indexes_and_residue(source: Span, candidate: Span) -> None:
    source_tikz = environment_occurrences(source.text, "tikzpicture")
    candidate_tikz = environment_occurrences(candidate.text, "tikzpicture")
    require(
        tuple((item.start_line, item.end_line) for item in source_tikz)
        == tuple((item.start_line, item.end_line) for item in candidate_tikz)
        == EXPECTED_TIKZPICTURE_SPANS,
        "TikZ-picture span topology changed",
    )
    require(
        tuple(item.text for item in source_tikz) == tuple(item.text for item in candidate_tikz),
        "TikZ-picture payload changed",
    )

    source_tikzcd = environment_occurrences(source.text, "tikzcd")
    candidate_tikzcd = environment_occurrences(candidate.text, "tikzcd")
    require(
        tuple((item.start_line, item.end_line) for item in source_tikzcd)
        == tuple((item.start_line, item.end_line) for item in candidate_tikzcd)
        == EXPECTED_TIKZCD_SPANS,
        "tikzcd span topology changed",
    )
    require(
        tuple(item.text for item in source_tikzcd[:5])
        == tuple(item.text for item in candidate_tikzcd[:5]),
        "one of the five unchanged tikzcd payloads changed",
    )
    require(
        source_tikzcd[5].text.replace(BAD_NATURALITY_ROW, GOOD_NATURALITY_ROW)
        == candidate_tikzcd[5].text,
        "sixth tikzcd differs beyond COR-001",
    )

    for pattern, expected_count, name in (
        (NODE_RE, 30, "node"),
        (COORDINATE_RE, 2, "coordinate"),
        (DRAW_RE, 32, "draw"),
        (PATH_RE, 0, "path"),
        (EDGE_RE, 15, "edge"),
        (ARROW_RE, 26, "arrow"),
        (BRAID_RE, 10, "braid"),
        (HLINE_RE, 3, "hline"),
    ):
        require(
            located_lines(pattern, source.text) == located_lines(pattern, candidate.text),
            f"{name} line topology changed",
        )
        require(len(pattern.findall(source.text)) == expected_count, f"source {name} census changed")
        require(len(pattern.findall(candidate.text)) == expected_count, f"candidate {name} census changed")

    source_indexes = index_occurrences(source.text)
    candidate_indexes = index_occurrences(candidate.text)
    require(len(source_indexes) == 8, "source index census changed")
    require(
        tuple(line for line, _, _ in source_indexes)
        == tuple(line for line, _, _ in candidate_indexes),
        "index line topology changed",
    )
    require(candidate_indexes == EXPECTED_TARGET_INDEXES, "localized index topology changed")

    require(brace_audit(source.text) == brace_audit(candidate.text) == (0, 0, 276, 276), "unescaped-brace topology changed")
    require(
        (source.text.count("{"), source.text.count("}"))
        == (candidate.text.count("{"), candidate.text.count("}"))
        == (282, 282),
        "raw-brace census changed",
    )
    require(han_count(source.text) == 1_446, "source Han census changed")
    require(han_count(candidate.text) == 0, "candidate contains untranslated Han")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source_view = read_file(SOURCE, SOURCE_FULL_LINES)
    candidate_view = read_file(CANDIDATE, CANDIDATE_LINES)
    target_view = read_file(TARGET, TARGET_FULL_LINES)
    source = make_span(source_view, SOURCE_START, SOURCE_END)
    candidate = make_span(candidate_view, 1, CANDIDATE_LINES)
    target = make_span(target_view, TARGET_START, TARGET_END)

    gate_identities_and_boundaries(source_view, candidate_view, target_view, source, target)
    gate_declared_corrections(source, candidate)
    gate_commands_and_math(source, candidate)
    gate_document_topology(source, candidate)
    gate_diagrams_indexes_and_residue(source, candidate)

    print(
        "\n".join(
            (
                "PASS Unit 021 candidate/canonical mathematics/protected-topology checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source prefix=1-306 bytes={SOURCE_PREFIX_BYTES} sha256={SOURCE_PREFIX_SHA256}",
                f"source span=307-512 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"source suffix=513-911 bytes={SOURCE_SUFFIX_BYTES} sha256={SOURCE_SUFFIX_SHA256}",
                f"candidate lines=1-206 bytes={len(candidate.raw)} sha256={sha256(candidate.raw).hexdigest()}",
                f"target full_lines=910 bytes={len(target_view.raw)} sha256={sha256(target_view.raw).hexdigest()}",
                f"target prefix=1-305 bytes={TARGET_PREFIX_BYTES} sha256={TARGET_PREFIX_SHA256}",
                f"target span=306-511 bytes={len(target.raw)} sha256={sha256(target.raw).hexdigest()}",
                f"target suffix=512-910 bytes={TARGET_SUFFIX_BYTES} sha256={TARGET_SUFFIX_SHA256}",
                "integration=candidate-byte-identical remainder=authority-513-911-byte-identical",
                "boundary=source-307-start included-blank=512 target-306-start included-blank=511 next-target-512-enriched-category-excluded",
                "environments=43-pairs labels=9 refs=10 eqrefs=3 cites=2 items=0 indexes=8",
                "commands=527/527 inline_math=144 bracket_displays=6 braces=276/276-unescaped raw_braces=282/282 han=0",
                "tikzpicture=17 tikzcd=6 nodes=30 coordinates=2 draws=32 paths=0 edges=15 arrows=26 braids=10 hlines=3",
                f"corrections={CORRECTION_NATURALITY},{CORRECTION_OBJECTS},{EDITORIAL_DUPLICATE}",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 021 candidate/canonical mathematics/protected-topology checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
