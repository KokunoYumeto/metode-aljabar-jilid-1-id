#!/usr/bin/env python3
"""Fail-closed source/structure check for the isolated Unit 023 candidate."""

from __future__ import annotations

from collections import Counter
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
CANDIDATE = ROOT / "build/unit-023-candidate/chapter3-2-categories-id.tex"

SOURCE_START = 723
SOURCE_END = 872
SOURCE_FULL_LINES = 911
CANDIDATE_LINES = 150

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_PREFIX_BYTES = 58_181
SOURCE_PREFIX_SHA256 = "d140ee3d1cb53d03b8939223e412bfa974e10c0ab2b5b51a8a99400fd93353ad"
SOURCE_SPAN_BYTES = 12_436
SOURCE_SPAN_SHA256 = "2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856"
SOURCE_SUFFIX_BYTES = 4_954
SOURCE_SUFFIX_SHA256 = "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857"
SOURCE_START_LINE_BYTES = 64
SOURCE_START_LINE_SHA256 = "26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7"
SOURCE_NEXT_LINE_BYTES = 18
SOURCE_NEXT_LINE_SHA256 = "0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699"

CANDIDATE_BYTES = 14_894
CANDIDATE_SHA256 = "c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05"
CANDIDATE_START_LINE_BYTES = 76
CANDIDATE_START_LINE_SHA256 = "d383b0253bea36216351c071a8e8ba5a441658261e213bf2e03afb4bf7f0ecbe"
CANDIDATE_FINAL_RECORD = b"\t\n"

SOURCE_START_LINE = r"\section{\texorpdfstring{$2$}{2}-范畴一瞥}\label{sec:2-cat}"
SOURCE_NEXT_LINE = r"\begin{Exercises}"
CANDIDATE_START_LINE = (
    r"\section{Sekilas tentang \texorpdfstring{$2$}{2}-Kategori}\label{sec:2-cat}"
)

EDITORIAL_INDEX_ID = "O013-LI-U023-ED-001"
SOURCE_RAW_ADJUNCTION_INDEX = r"\index{bansuidui}"
TARGET_ADJUNCTION_INDEX = r"\index{bansuidui@pasangan adjoin}"

DISPLAY_LOCALIZATIONS = (
    (r"\text{dikomposisikan menjadi}", r"\text{合成为}"),
    (r"\text{komposisi horizontalnya adalah}", r"\text{横合成为}"),
    (r"\text{vertikal}", r"\text{纵}"),
    (r"\text{horizontal}", r"\text{横}"),
)

PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
CROSS_REF_RE = re.compile(r"\\(ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}")
ITEM_RE = re.compile(r"\\item\b")
INDEX_START_RE = re.compile(r"\\index(?:\[([^\]]*)\])?\{")
NODE_RE = re.compile(r"\\node\b")
PATH_RE = re.compile(r"\\path\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")
EDGE_RE = re.compile(r"\bedge\b")
DRAW_RE = re.compile(r"\\draw\b")
COORDINATE_RE = re.compile(r"\\coordinate\b")

EXPECTED_BEGIN_COUNTS = Counter(
    {
        "tikzcd": 14,
        "remark": 3,
        "definition": 2,
        "compactitem": 2,
        "itemize": 1,
        "enumerate": 1,
        "example": 1,
        "convention": 1,
    }
)

EXPECTED_LABELS = (
    (1, "sec:2-cat"),
    (88, "eg:Cat"),
)

EXPECTED_CROSS_REFS = (
    (4, "ref", "eg:Cat"),
    (85, "ref", "rem:strict-or-not"),
    (85, "ref", "prop:ML-coherence"),
    (89, "ref", "con:U-small"),
    (96, "ref", "prop:naturaltrans-associativity"),
    (99, "ref", "eg:categories"),
    (99, "ref", "eg:monoidal-cat"),
    (102, "ref", "sec:functor-category"),
    (116, "ref", "def:enriched-cat"),
    (120, "ref", "def:enriched-functor"),
    (120, "ref", "def:enriched-naturaltrans"),
    (125, "ref", "sec:functors"),
    (129, "ref", "rem:triangle-identity"),
    (144, "ref", "sec:adjoint-functor"),
    (148, "ref", "rem:triangle-identity"),
    (148, "ref", "prop:adjoint-equivalence"),
)

EXPECTED_ITEM_LINES = (
    9,
    10,
    11,
    15,
    17,
    32,
    45,
    53,
    54,
    67,
    91,
    92,
    93,
    94,
    106,
    107,
    108,
    110,
    112,
)

EXPECTED_BLANK_LINES = (
    3,
    5,
    83,
    87,
    98,
    100,
    103,
    115,
    118,
    123,
    142,
    150,
)

EXPECTED_TARGET_INDEXES = (
    (6, None, r"$2$-kategori"),
    (88, "sym1", r"Cat@$\cate{Cat}$"),
    (143, None, "bansuidui@pasangan adjoin"),
)

REQUIRED_TERMINOLOGY = (
    "$2$-kategori",
    "$2$-sel",
    "komposisi vertikal",
    "komposisi horizontal",
    "hukum pertukaran",
    "bikategori",
    "kategori vertikal",
    "kategori yang diperkaya atas",
    "$2$-fungtor",
    "$2$-transformasi natural",
    "pasangan adjoin",
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
    records: tuple[bytes, ...]
    lines: tuple[str, ...]

    @property
    def text(self) -> str:
        return self.raw.decode("utf-8", errors="strict")

    def line(self, line_number: int) -> str:
        return self.lines[line_number - 1]


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
    return Span(
        b"".join(records),
        tuple(records),
        tuple(record_text(record) for record in records),
    )


def hash_gate(name: str, data: bytes, expected_bytes: int, expected_hash: str) -> None:
    require(len(data) == expected_bytes, f"{name}: byte count changed")
    require(sha256(data).hexdigest() == expected_hash, f"{name}: SHA-256 changed")


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


def normalize_display(value: str) -> str:
    for target, source in DISPLAY_LOCALIZATIONS:
        value = value.replace(target, source)
    return value


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


def extract_environment(text: str, name: str) -> list[str]:
    pattern = re.compile(
        rf"\\begin\{{{re.escape(name)}\}}.*?\\end\{{{re.escape(name)}\}}",
        re.DOTALL,
    )
    return [match.group(0) for match in pattern.finditer(text)]


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


def index_entries(text: str) -> tuple[tuple[int, str | None, str], ...]:
    entries: list[tuple[int, str | None, str]] = []
    for match in INDEX_START_RE.finditer(text):
        opening = match.end() - 1
        depth = 1
        cursor = opening + 1
        while cursor < len(text) and depth:
            if not is_escaped(text, cursor):
                if text[cursor] == "{":
                    depth += 1
                elif text[cursor] == "}":
                    depth -= 1
            cursor += 1
        require(depth == 0, "unterminated index entry")
        entries.append(
            (
                1 + text.count("\n", 0, match.start()),
                match.group(1),
                text[opening + 1 : cursor - 1],
            )
        )
    return tuple(entries)


def gate_boundaries(source_view: FileView, source: Span, candidate: Span) -> None:
    prefix = b"".join(source_view.records[: SOURCE_START - 1])
    suffix = b"".join(source_view.records[SOURCE_END:])
    first_line = source_view.records[SOURCE_START - 1]
    next_line = source_view.records[SOURCE_END]

    hash_gate("source full file", source_view.raw, SOURCE_FULL_BYTES, SOURCE_FULL_SHA256)
    hash_gate("source prefix 1-722", prefix, SOURCE_PREFIX_BYTES, SOURCE_PREFIX_SHA256)
    hash_gate("source span 723-872", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix 873-911", suffix, SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256)
    hash_gate("source line 723", first_line, SOURCE_START_LINE_BYTES, SOURCE_START_LINE_SHA256)
    hash_gate("source line 873", next_line, SOURCE_NEXT_LINE_BYTES, SOURCE_NEXT_LINE_SHA256)
    hash_gate("candidate full file", candidate.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)
    hash_gate(
        "candidate line 1",
        candidate.records[0],
        CANDIDATE_START_LINE_BYTES,
        CANDIDATE_START_LINE_SHA256,
    )

    require(source.line(1) == SOURCE_START_LINE, "authority line 723 start signature changed")
    require(source.line(150) == "", "authority line 872 must be the included blank separator")
    require(source_view.lines[872] == SOURCE_NEXT_LINE, "authority line 873 exercise boundary changed")
    require(candidate.line(1) == CANDIDATE_START_LINE, "candidate opening signature changed")
    require(candidate.records[149] == CANDIDATE_FINAL_RECORD, "candidate final separator record changed")
    require(not candidate.line(150).strip(), "candidate line 150 must remain whitespace-only")
    require(r"\begin{Exercises}" not in candidate.text, "excluded exercise block leaked into candidate")


def gate_editorial_index(source: Span, candidate: Span) -> None:
    require(source.text.count(SOURCE_RAW_ADJUNCTION_INDEX) == 1, "source raw index key changed")
    require(SOURCE_RAW_ADJUNCTION_INDEX in source.line(143), "source raw index moved from line 865")
    require(SOURCE_RAW_ADJUNCTION_INDEX not in candidate.text, "raw pinyin-only index remains")
    require(candidate.text.count(TARGET_ADJUNCTION_INDEX) == 1, "localized adjunction index changed")
    require(TARGET_ADJUNCTION_INDEX in candidate.line(143), "localized index moved from line 143")


def gate_commands_and_math(source: Span, candidate: Span) -> None:
    for line_number, (source_line, target_line) in enumerate(
        zip(source.lines, candidate.lines, strict=True), 1
    ):
        require(
            Counter(COMMAND_RE.findall(source_line)) == Counter(COMMAND_RE.findall(target_line)),
            f"line {line_number}: TeX command multiset changed",
        )
    require(len(COMMAND_RE.findall(source.text)) == 446, "source command census changed")
    require(len(COMMAND_RE.findall(candidate.text)) == 446, "candidate command census changed")

    source_inline = inline_math(source.text)
    target_inline = inline_math(candidate.text)
    require(len(source_inline) == len(target_inline) == 156, "inline-math census changed")
    require(source_inline == target_inline, "inline mathematics or positions changed")

    source_displays = bracket_displays(source.text)
    target_displays = [normalize_display(value) for value in bracket_displays(candidate.text)]
    require(len(source_displays) == len(target_displays) == 11, "bracket-display census changed")
    require(source_displays == target_displays, "display mathematics changed beyond text localization")


def gate_document_topology(source: Span, candidate: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(candidate.text)
    audit_nesting(source_events, "source span")
    audit_nesting(target_events, "candidate")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == len(target_events) == 50, "environment event census changed")
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
            (1 + text.count("\n", 0, match.start()), match.group(1), match.group(2))
            for match in CROSS_REF_RE.finditer(text)
        )

    require(
        cross_refs(source.text) == cross_refs(candidate.text) == EXPECTED_CROSS_REFS,
        "reference topology changed",
    )
    require(not CITE_RE.search(source.text), "source citation census changed")
    require(not CITE_RE.search(candidate.text), "unexpected candidate citation")
    require(
        located_lines(ITEM_RE, source.text)
        == located_lines(ITEM_RE, candidate.text)
        == EXPECTED_ITEM_LINES,
        "item topology changed",
    )
    require(
        tuple(line for line, value in enumerate(source.lines, 1) if not value.strip())
        == tuple(line for line, value in enumerate(candidate.lines, 1) if not value.strip())
        == EXPECTED_BLANK_LINES,
        "blank-line topology changed",
    )
    source_comments = tuple(i for i, line in enumerate(source.lines, 1) if "%" in line)
    target_comments = tuple(i for i, line in enumerate(candidate.lines, 1) if "%" in line)
    require(source_comments == target_comments == (16,), "comment topology changed")


def gate_diagrams_indexes_and_language(source: Span, candidate: Span) -> None:
    source_tikzcd = extract_environment(source.text, "tikzcd")
    target_tikzcd = extract_environment(candidate.text, "tikzcd")
    require(len(source_tikzcd) == len(target_tikzcd) == 14, "tikzcd census changed")
    require(source_tikzcd == target_tikzcd, "tikzcd mathematics/topology changed")

    for pattern, expected, name in (
        (NODE_RE, 0, "node"),
        (PATH_RE, 0, "path"),
        (ARROW_RE, 64, "tikzcd arrow"),
        (EDGE_RE, 0, "TikZ edge"),
        (DRAW_RE, 0, "draw"),
        (COORDINATE_RE, 0, "coordinate"),
    ):
        require(
            located_lines(pattern, source.text) == located_lines(pattern, candidate.text),
            f"{name} positions changed",
        )
        require(
            len(pattern.findall(source.text))
            == len(pattern.findall(candidate.text))
            == expected,
            f"{name} census changed",
        )

    require(len(index_entries(source.text)) == 3, "source index census changed")
    require(index_entries(candidate.text) == EXPECTED_TARGET_INDEXES, "localized index topology changed")
    require(
        brace_audit(source.text) == brace_audit(candidate.text) == (0, 0, 186, 186),
        "brace topology changed",
    )
    require(han_count(source.text) == 1_519, "source Han census changed")
    require(han_count(candidate.text) == 0, "candidate contains untranslated Han")

    for term in REQUIRED_TERMINOLOGY:
        require(term in candidate.text, f"required controlled/corpus terminology missing: {term}")
    require("morfisma" not in candidate.text, "non-corpus morfisma spelling introduced")
    require("funktor" not in candidate.text, "non-corpus funktor spelling introduced")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source_view = read_file(SOURCE, SOURCE_FULL_LINES)
    candidate_view = read_file(CANDIDATE, CANDIDATE_LINES)
    source = make_span(source_view, SOURCE_START, SOURCE_END)
    candidate = make_span(candidate_view, 1, CANDIDATE_LINES)

    gate_boundaries(source_view, source, candidate)
    gate_editorial_index(source, candidate)
    gate_commands_and_math(source, candidate)
    gate_document_topology(source, candidate)
    gate_diagrams_indexes_and_language(source, candidate)

    print(
        "\n".join(
            (
                "PASS Unit 023 isolated candidate checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source prefix=1-722 bytes={SOURCE_PREFIX_BYTES} sha256={SOURCE_PREFIX_SHA256}",
                f"source span=723-872 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"source suffix=873-911 bytes={SOURCE_SUFFIX_BYTES} sha256={SOURCE_SUFFIX_SHA256}",
                f"candidate lines=150 bytes={len(candidate.raw)} sha256={sha256(candidate.raw).hexdigest()}",
                "boundary=start=2-categories included-blank=872 next=873-exercises-excluded",
                "environments=25-pairs labels=2 refs=16 eqrefs=0 cites=0 items=19 indexes=3",
                "inline_math=156 bracket_displays=11 commands=446 braces=186/186 han=0",
                "tikzcd=14 arrows=64 nodes=0 paths=0 edges=0 draws=0",
                f"editorial={EDITORIAL_INDEX_ID}-raw-pinyin-index-to-localized-display",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 023 isolated candidate checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
