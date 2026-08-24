#!/usr/bin/env python3
"""Fail-closed structure/math check for Unit 019 (chapter 3 opening)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import sys


SOURCE_END = 227
TARGET_END = 226
SOURCE_FULL_LINES = 911
TARGET_FULL_LINES = 910

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_SPAN_BYTES = 21_745
SOURCE_SPAN_SHA256 = "4aecde3d61fb173087ae3e7ab64cc84f7bd4f3fbc0dcbfa8a2c3d6bab1201a8a"
TARGET_FULL_BYTES = 79_694
TARGET_FULL_SHA256 = "bfe5d4745f9a3ac1062b79ee429356a17f3d5bff9be02ef0093eab6978f98e60"
TARGET_SPAN_BYTES = 25_868
TARGET_SPAN_SHA256 = "6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac"

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
)
TARGET = ROOT / "repo/source/chapter3.tex"

NEXT_BOUNDARY = r"\section{严格性与融贯定理}\label{sec:coherence}"
CORRECTION_ID = "O013-LI-U019-COR-001"
CORRECTION_SOURCE = r"Z \otimes ((1 \otimes X) \otimes Y)"
CORRECTION_TARGET = r"Z \otimes ((\munit \otimes X) \otimes Y)"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
CROSS_REF_RE = re.compile(r"\\(ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}")
ITEM_RE = re.compile(r"\\item\b")
INDEX_RE = re.compile(r"\\index(?:\[([^\]]*)\])?\{([^{}]+)\}")
NODE_RE = re.compile(r"\\node\b")
PATH_RE = re.compile(r"\\path\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")
EDGE_RE = re.compile(r"\bedge\b")

EXPECTED_BEGIN_COUNTS = Counter(
    {
        "enumerate": 3,
        "wenxintishi": 1,
        "definition": 4,
        "center": 3,
        "tikzpicture": 3,
        "compactitem": 1,
        "example": 3,
        "lemma": 1,
        "align": 1,
        "equation": 6,
        "tikzcd": 15,
        "proof": 1,
        "equation*": 1,
        "remark": 2,
    }
)

EXPECTED_LABELS = (
    (9, "sec:monoidal-cat"),
    (28, "sec:monoidal-cat-def"),
    (31, "def:monoidal-cat"),
    (62, "def:monoidal-constraints"),
    (76, "eg:monoidal-cat"),
    (86, "eg:cob-cat"),
    (108, "prop:Kelly"),
    (111, "eqn:unit-coherence-2a"),
    (112, "eqn:unit-coherence-2b"),
    (113, "eqn:unit-coherence-2c"),
    (116, "eqn:monoidal-cat-unit"),
    (121, "eqn:unit-coherence-1"),
    (130, "eqn:unit-coherence-3"),
    (144, "eqn:coherence-aux0"),
    (177, "def:monoidal-functor"),
    (199, "eqn:monoidal-functor-units"),
)

EXPECTED_CROSS_REFS = (
    (12, "ref", "sec:module-tensor-prod"),
    (13, "ref", "sec:braiding"),
    (16, "ref", "sec:enriched-cat"),
    (16, "ref", "sec:2-cat"),
    (21, "ref", "sec:enriched-cat"),
    (23, "ref", "sec:modules"),
    (60, "ref", "rem:strict-or-not"),
    (79, "ref", "prop:product-associativity"),
    (82, "ref", "prop:module-monoidal-cat"),
    (106, "ref", "def:monoidal-cat"),
    (106, "ref", "def:monoidal-constraints"),
    (106, "ref", "def:monoidal-cat"),
    (106, "ref", "sec:coherence"),
    (136, "eqref", "eqn:unit-coherence-2a"),
    (141, "eqref", "eqn:unit-coherence-2b"),
    (149, "eqref", "eqn:unit-coherence-2a"),
    (149, "eqref", "eqn:monoidal-cat-unit"),
    (149, "eqref", "eqn:monoidal-cat-unit"),
    (149, "eqref", "eqn:unit-coherence-2c"),
    (157, "eqref", "eqn:monoidal-cat-unit"),
    (162, "eqref", "eqn:unit-coherence-1"),
    (162, "eqref", "eqn:unit-coherence-1"),
    (164, "eqref", "eqn:unit-coherence-3"),
    (174, "eqref", "eqn:monoidal-cat-unit"),
    (210, "eqref", "eqn:monoidal-functor-units"),
    (210, "eqref", "eqn:monoidal-functor-units"),
    (214, "ref", "def:preservation-limit"),
    (226, "ref", "def:cat-equivalence"),
)

EXPECTED_CITES = (
    (18, r"\cite{EGNO15}"),
    (29, r"\cite[\S 2.1]{EGNO15}"),
    (174, r"\cite{ML98}"),
    (198, r"\cite[Proposition 2.4.3]{EGNO15}"),
)

EXPECTED_ITEMS = (12, 13, 34, 35, 36, 53, 54, 65, 67, 79, 80, 81, 82)
EXPECTED_COMMAND_MISMATCH_LINES = (13, 21, 74, 79, 81, 149, 155, 174, 178)
EXPECTED_INLINE_REORDER_LINES = (81, 109, 174)
EXPECTED_BLANK_LINES = (
    7, 15, 17, 19, 22, 24, 27, 30, 45, 57, 59, 61, 73, 75, 85, 88,
    94, 102, 105, 107, 142, 150, 163, 172, 176, 188, 208, 212, 216, 225,
)
EXPECTED_FULL_COMMENT_LINES = (1, 2, 3, 4, 5, 6, 8)
EXPECTED_ALL_COMMENT_LINES = (1, 2, 3, 4, 5, 6, 8, 91, 99)

EXPECTED_TARGET_INDEXES = (
    (25, None, "zhangliangfanchou@kategori tensor (tensor category)"),
    (31, None, "yaobanfanchou@kategori monoidal (monoidal category)"),
    (31, "sym1", r"1otimes@$\otimes$"),
    (53, None, "objek!objek satuan (unit object)"),
    (58, None, "jieheyueshu@kendala asosiativitas"),
    (58, None, "MacLane@aksioma segilima Mac Lane (pentagon axiom)"),
    (
        74,
        None,
        "yaobanfanchou@kategori monoidal (monoidal category)!"
        "subkategori monoidal (monoidal subcategory)",
    ),
    (177, None, "yaobanhanzi@fungtor monoidal (monoidal functor)"),
    (
        210,
        None,
        "yaobanhanzi@fungtor monoidal!"
        "longgar-kiri/longgar-kanan (left-lax/right-lax)",
    ),
    (217, None, "ziranbianhuan@transformasi natural!kasus monoidal"),
    (226, None, "fanchoudengjia@ekuivalensi kategori!kasus monoidal"),
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
    if record.endswith(b"\r"):
        record = record[:-1]
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
        return "\n".join(self.lines)

    def line(self, line_number: int) -> str:
        return self.lines[line_number - 1]


def read_file(path: Path, expected_lines: int) -> FileView:
    require(path.is_file(), f"missing input: {path}")
    data = path.read_bytes()
    records = lf_records(data)
    require(data.endswith(b"\n"), f"{path}: file must end with LF")
    require(len(records) == expected_lines, f"{path}: physical line count changed")
    require(all(record.endswith(b"\n") for record in records), f"{path}: non-LF record detected")
    return FileView(data, tuple(records), tuple(record_text(record) for record in records))


def make_span(view: FileView, end: int) -> Span:
    records = view.records[:end]
    require(len(records) == end, f"could not extract physical lines 1-{end}")
    return Span(b"".join(records), tuple(record_text(record) for record in records))


def is_escaped(text: str, position: int) -> bool:
    count = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        count += 1
        position -= 1
    return count % 2 == 1


def comment_positions(lines: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    found: list[tuple[int, int]] = []
    for line_number, line in enumerate(lines, 1):
        for position, char in enumerate(line):
            if char == "%" and not is_escaped(line, position):
                found.append((line_number, position))
                break
    return tuple(found)


def inline_math(text: str) -> list[tuple[int, str]]:
    delimiters = [
        position
        for position, char in enumerate(text)
        if char == "$" and not is_escaped(text, position)
    ]
    require(len(delimiters) % 2 == 0, "unpaired inline-math delimiter")
    return [
        (1 + text.count("\n", 0, opening), text[opening + 1 : closing])
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


def located_values(pattern: re.Pattern[str], text: str) -> tuple[tuple[int, str], ...]:
    return tuple(
        (1 + text.count("\n", 0, match.start()), match.group(1))
        for match in pattern.finditer(text)
    )


def located_lines(pattern: re.Pattern[str], text: str) -> tuple[int, ...]:
    return tuple(1 + text.count("\n", 0, match.start()) for match in pattern.finditer(text))


def environment_events(text: str) -> tuple[tuple[int, str, str], ...]:
    return tuple(
        (1 + text.count("\n", 0, match.start()), match.group(1), match.group(2))
        for match in ENV_RE.finditer(text)
    )


def audit_nesting(events: tuple[tuple[int, str, str], ...], side: str) -> None:
    stack: list[tuple[int, str]] = []
    for line, kind, name in events:
        if kind == "begin":
            stack.append((line, name))
        else:
            require(stack, f"{side}: unmatched end {name} at line {line}")
            opened_line, opened_name = stack.pop()
            require(
                opened_name == name,
                f"{side}: begin {opened_name} at line {opened_line} closed by {name}",
            )
    require(not stack, f"{side}: unclosed environments {stack}")


def extract_environment(text: str, name: str) -> list[str]:
    escaped = re.escape(name)
    return re.findall(
        rf"\\begin\{{{escaped}\}}.*?\\end\{{{escaped}\}}",
        text,
        flags=re.DOTALL,
    )


def normalize_diagram(text: str) -> str:
    text = text.replace(CORRECTION_SOURCE, CORRECTION_TARGET)
    return re.sub(r"\s+", "", text)


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


def gate_boundaries(source_view: FileView, target_view: FileView, source: Span, target: Span) -> None:
    require(source.line(9) == r"\chapter{幺半范畴}\label{sec:monoidal-cat}", "source chapter boundary changed")
    require(target.line(9) == r"\chapter{Kategori Monoidal}\label{sec:monoidal-cat}", "target chapter boundary changed")
    require(source.line(28) == r"\section{基本定义}\label{sec:monoidal-cat-def}", "source section boundary changed")
    require(target.line(28) == r"\section{Definisi Dasar}\label{sec:monoidal-cat-def}", "target section boundary changed")
    require(source.line(SOURCE_END) == "", "source Unit 019 must end at blank separator line 227")
    require(target.line(TARGET_END).startswith("Fungtor monoidal dan transformasi natural"), "target closing prose changed")
    require(source_view.lines[227] == NEXT_BOUNDARY, "source next boundary at line 228 changed")
    require(target_view.lines[226] == NEXT_BOUNDARY, "target next boundary at line 227 changed")
    require(
        b"".join(source_view.records[227:]) == b"".join(target_view.records[226:]),
        "target remainder no longer equals authority lines 228-911 byte-for-byte",
    )

    source_blanks = tuple(i for i, line in enumerate(source.lines, 1) if not line.strip())
    target_blanks = tuple(i for i, line in enumerate(target.lines, 1) if not line.strip())
    require(source_blanks == EXPECTED_BLANK_LINES + (227,), "source blank-line topology changed")
    require(target_blanks == EXPECTED_BLANK_LINES, "target blank-line topology changed")
    require(sum(bool(line.strip()) for line in source.lines) == 196, "source nonblank census changed")
    require(sum(bool(line.strip()) for line in target.lines) == 196, "target nonblank census changed")

    source_comments = comment_positions(source.lines)
    target_comments = comment_positions(target.lines)
    require(tuple(line for line, _ in source_comments) == EXPECTED_ALL_COMMENT_LINES, "source comment topology changed")
    require(tuple(line for line, _ in target_comments) == EXPECTED_ALL_COMMENT_LINES, "target comment topology changed")
    require(
        tuple(i for i, line in enumerate(source.lines, 1) if line.lstrip().startswith("%"))
        == EXPECTED_FULL_COMMENT_LINES,
        "source full-line comment topology changed",
    )
    require(
        tuple(i for i, line in enumerate(target.lines, 1) if line.lstrip().startswith("%"))
        == EXPECTED_FULL_COMMENT_LINES,
        "target full-line comment topology changed",
    )


def gate_command_topology(source: Span, target: Span) -> None:
    source_commands = COMMAND_RE.findall(source.text)
    target_commands = COMMAND_RE.findall(target.text)
    require(len(source_commands) == 1_034, "source command count changed")
    require(len(target_commands) == 1_035, "target command count changed")
    require(
        Counter(target_commands) - Counter(source_commands) == Counter({r"\munit": 1}),
        "target command additions differ from the declared unit-object correction",
    )
    require(
        not (Counter(source_commands) - Counter(target_commands)),
        "target omitted one or more source TeX commands",
    )

    mismatches: list[int] = []
    for line_number in range(1, TARGET_END + 1):
        source_line = COMMAND_RE.findall(source.line(line_number))
        target_line = COMMAND_RE.findall(target.line(line_number))
        if source_line == target_line:
            continue
        mismatches.append(line_number)
        if line_number == 155:
            require(
                Counter(target_line) - Counter(source_line) == Counter({r"\munit": 1})
                and not (Counter(source_line) - Counter(target_line)),
                "line 155 differs by more than the declared correction",
            )
        else:
            require(Counter(source_line) == Counter(target_line), f"line {line_number}: command multiset changed")
    require(tuple(mismatches) == EXPECTED_COMMAND_MISMATCH_LINES, f"command reorder lines changed: {mismatches}")


def gate_math(source: Span, target: Span) -> None:
    source_inline = inline_math(source.text)
    target_inline = inline_math(target.text)
    require(len(source_inline) == len(target_inline) == 167, "inline-math census changed")
    require(source.text.count(r"\text{终对象}") == 1, "source terminal-object localization signature changed")
    require(target.text.count(r"\text{objek terminal}") == 1, "target terminal-object localization missing")

    source_by_line: dict[int, list[str]] = {}
    target_by_line: dict[int, list[str]] = {}
    for line, value in source_inline:
        source_by_line.setdefault(line, []).append(value.replace(r"\text{终对象}", r"\text{objek terminal}"))
    for line, value in target_inline:
        target_by_line.setdefault(line, []).append(value)
    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology changed")

    reordered: list[int] = []
    for line in source_by_line:
        if source_by_line[line] == target_by_line[line]:
            continue
        reordered.append(line)
        require(
            Counter(source_by_line[line]) == Counter(target_by_line[line]),
            f"line {line}: inline-math multiset changed",
        )
    require(tuple(reordered) == EXPECTED_INLINE_REORDER_LINES, f"inline-math reorder lines changed: {reordered}")

    source_displays = bracket_displays(source.text)
    target_displays = bracket_displays(target.text)
    require(len(source_displays) == len(target_displays) == 9, "bracket-display census changed")
    require(source_displays == target_displays, "bracket-display mathematics changed")

    for name, expected in (("align", 1), ("equation", 6), ("equation*", 1)):
        source_blocks = extract_environment(source.text, name)
        target_blocks = extract_environment(target.text, name)
        require(len(source_blocks) == len(target_blocks) == expected, f"{name} environment census changed")
        require(
            [normalize_diagram(block) for block in source_blocks]
            == [normalize_diagram(block) for block in target_blocks],
            f"{name} mathematics changed beyond the declared correction/whitespace",
        )


def gate_documents_and_crossrefs(source: Span, target: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(target.text)
    audit_nesting(source_events, "source")
    audit_nesting(target_events, "target")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == target_events.__len__() == 90, "environment event census changed")
    begins = Counter(name for _, kind, name in source_events if kind == "begin")
    ends = Counter(name for _, kind, name in source_events if kind == "end")
    require(begins == ends == EXPECTED_BEGIN_COUNTS, "environment type census changed")

    source_labels = located_values(LABEL_RE, source.text)
    target_labels = located_values(LABEL_RE, target.text)
    require(source_labels == target_labels == EXPECTED_LABELS, "label topology changed")

    def cross_refs(text: str) -> tuple[tuple[int, str, str], ...]:
        return tuple(
            (1 + text.count("\n", 0, match.start()), match.group(1), match.group(2))
            for match in CROSS_REF_RE.finditer(text)
        )

    require(cross_refs(source.text) == cross_refs(target.text) == EXPECTED_CROSS_REFS, "reference topology changed")
    require(
        sum(kind == "ref" for _, kind, _ in EXPECTED_CROSS_REFS) == 15
        and sum(kind == "eqref" for _, kind, _ in EXPECTED_CROSS_REFS) == 13,
        "internal reference census constant is defective",
    )

    def cites(text: str) -> tuple[tuple[int, str], ...]:
        return tuple(
            (1 + text.count("\n", 0, match.start()), match.group(0))
            for match in CITE_RE.finditer(text)
        )

    require(cites(source.text) == cites(target.text) == EXPECTED_CITES, "citation topology changed")
    require(located_lines(ITEM_RE, source.text) == located_lines(ITEM_RE, target.text) == EXPECTED_ITEMS, "item topology changed")
    require(r"\begin{Exercises}" not in source.text and r"\begin{Exercises}" not in target.text, "unexpected formal exercise block")
    require(r"\hint{" not in source.text and r"\hint{" not in target.text, "unexpected formal hint")


def gate_diagrams_indexes_and_residue(source: Span, target: Span) -> None:
    require(source.text.count(CORRECTION_SOURCE) == 1, "source correction signature changed")
    require(target.text.count(CORRECTION_SOURCE) == 0, "undefined literal 1 remains in target Kelly diagram")
    require(target.text.count(CORRECTION_TARGET) == 1, "declared Kelly-diagram correction missing or duplicated")

    source_tikz = extract_environment(source.text, "tikzpicture")
    target_tikz = extract_environment(target.text, "tikzpicture")
    require(source_tikz == target_tikz and len(source_tikz) == 3, "tikzpicture topology changed")

    source_tikzcd = extract_environment(source.text, "tikzcd")
    target_tikzcd = extract_environment(target.text, "tikzcd")
    require(len(source_tikzcd) == len(target_tikzcd) == 15, "tikzcd census changed")
    require(
        [normalize_diagram(block) for block in source_tikzcd]
        == [normalize_diagram(block) for block in target_tikzcd],
        "tikzcd nodes/arrows/formulae changed beyond the declared correction/whitespace",
    )

    require(located_lines(NODE_RE, source.text) == located_lines(NODE_RE, target.text), "TikZ node positions changed")
    require(len(NODE_RE.findall(source.text)) == len(NODE_RE.findall(target.text)) == 11, "TikZ node census changed")
    require(located_lines(PATH_RE, source.text) == located_lines(PATH_RE, target.text) == (46,), "TikZ path topology changed")
    require(len(EDGE_RE.findall(source.text)) == len(EDGE_RE.findall(target.text)) == 5, "TikZ pentagon-edge census changed")
    require(located_lines(ARROW_RE, source.text) == located_lines(ARROW_RE, target.text), "tikzcd arrow positions changed")
    require(len(ARROW_RE.findall(source.text)) == len(ARROW_RE.findall(target.text)) == 75, "tikzcd arrow census changed")

    target_indexes = tuple(
        (1 + target.text.count("\n", 0, match.start()), match.group(1), match.group(2))
        for match in INDEX_RE.finditer(target.text)
    )
    require(len(INDEX_RE.findall(source.text)) == 11, "source index census changed")
    require(target_indexes == EXPECTED_TARGET_INDEXES, "localized index hierarchy/topology changed")

    require(brace_audit(source.text) == brace_audit(target.text) == (0, 0, 334, 334), "brace topology changed")
    require(han_count(source.text) == 2_381, "source Han census changed")
    require(han_count(target.text) == 0, "target contains untranslated Han/prose residue")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source_view = read_file(SOURCE, SOURCE_FULL_LINES)
    target_view = read_file(TARGET, TARGET_FULL_LINES)
    source = make_span(source_view, SOURCE_END)
    target = make_span(target_view, TARGET_END)

    require(len(source_view.raw) == SOURCE_FULL_BYTES, "source full-file byte count changed")
    require(sha256(source_view.raw).hexdigest() == SOURCE_FULL_SHA256, "source full-file hash changed")
    require(len(source.raw) == SOURCE_SPAN_BYTES, "source span byte count changed")
    require(sha256(source.raw).hexdigest() == SOURCE_SPAN_SHA256, "source span hash changed")
    require(len(target_view.raw) == TARGET_FULL_BYTES, "target full-file byte count changed")
    require(sha256(target_view.raw).hexdigest() == TARGET_FULL_SHA256, "target full-file hash changed")
    require(len(target.raw) == TARGET_SPAN_BYTES, "target span byte count changed")
    require(sha256(target.raw).hexdigest() == TARGET_SPAN_SHA256, "target span hash changed")

    gate_boundaries(source_view, target_view, source, target)
    gate_command_topology(source, target)
    gate_math(source, target)
    gate_documents_and_crossrefs(source, target)
    gate_diagrams_indexes_and_residue(source, target)

    print(
        "\n".join(
            (
                "PASS Unit 019 structural checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source span=1-227 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"target full_lines=910 bytes={len(target_view.raw)} sha256={sha256(target_view.raw).hexdigest()}",
                f"target span=1-226 bytes={len(target.raw)} sha256={sha256(target.raw).hexdigest()}",
                "boundary=chapter-opening+Definisi-Dasar source-next=228 target-next=227 remainder-exact",
                "environments=45-pairs labels=16 refs=15 eqrefs=13 cites=4 items=13",
                "inline_math=167 bracket_displays=9 align=1 equations=6 equation*=1 braces=334/334",
                "tikzpicture=3 tikzcd=15 nodes=11 paths=1 pentagon_edges=5 arrows=75 indexes=11 han=0",
                f"correction={CORRECTION_ID}-Kelly-diagram-1-to-munit",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 019 structural checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
