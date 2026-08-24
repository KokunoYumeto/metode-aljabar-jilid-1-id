#!/usr/bin/env python3
"""Fail-closed source/structure check for the isolated Unit 024 candidate."""

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
CANDIDATE = ROOT / "build/unit-024-candidate/chapter3-exercises-id.tex"

SOURCE_START = 873
SOURCE_END = 911
SOURCE_FULL_LINES = 911
CANDIDATE_LINES = 39

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_PREFIX_BYTES = 70_617
SOURCE_PREFIX_SHA256 = "8a0203bdb81b7384e7b84c9ccfbb37cdd57bc17f332061db707a9054fa7f58e9"
SOURCE_SPAN_BYTES = 4_954
SOURCE_SPAN_SHA256 = "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SOURCE_START_LINE_BYTES = 18
SOURCE_START_LINE_SHA256 = "0f80848f05d5d2ea79e191700984eea0aec0f85dfcf13ac2ad2c23cb282ae699"
SOURCE_END_LINE_BYTES = 16
SOURCE_END_LINE_SHA256 = "5737357e36540b3b9a76e967b17c118a49687b3fc513560a3231615ef0ef771a"

CANDIDATE_BYTES = 6_071
CANDIDATE_SHA256 = "576c39746534853cd5127298cf0c2ba7f6afb239e4d7b83f368b7a9969c5f43a"

START_LINE = r"\begin{Exercises}"
END_LINE = r"\end{Exercises}"

CORRECTION_NATURALITY_ID = "O013-LI-U024-COR-001"
SOURCE_FALSE_SYMMETRY_CLAIM = (
    r"证明 $(\cate{On}_f, \sqcup, c)$ 构成对称幺半范畴."
)
TARGET_NATURALITY_TEST = (
    r"Apakah keluarga isomorfisme ini membuat $(\cate{On}_f, \sqcup, c)$ "
    r"menjadi kategori monoidal simetris? Jika tidak, berikan contoh tandingan "
    r"terhadap naturalitasnya."
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
        "hint": 2,
        "tikzcd": 2,
        "Exercises": 1,
        "cases": 1,
        "itemize": 1,
    }
)

EXPECTED_CROSS_REFS = (
    (3, "ref", "prop:Kelly"),
    (10, "ref", "prop:YBE-cat-strict"),
    (32, "ref", "eg:Ab-cat"),
    (33, "ref", "def:comma-category"),
)

EXPECTED_ITEM_LINES = (
    2,
    3,
    4,
    5,
    6,
    20,
    22,
    27,
    29,
    32,
    33,
)

EXPECTED_BLANK_LINES = (11, 19)
EXPECTED_TARGET_INDEXES = ((18, None, "YBE"),)

REQUIRED_TERMINOLOGY = (
    "kategori monoidal",
    "bilangan Catalan",
    "himpunan terurut total",
    "peta-peta pelestari urutan",
    "persamaan Yang--Baxter",
    "struktur kepang",
    "kategori monoidal ketat",
    "pusat Drinfeld",
    "kategori diperkaya",
    "fungtor proyeksi",
    "isomorfisme natural antarfungtor",
    "transformasi natural",
    "$2$-kategori",
    "$2$-sel",
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

    hash_gate("source full file", source_view.raw, SOURCE_FULL_BYTES, SOURCE_FULL_SHA256)
    hash_gate("source prefix 1-872", prefix, SOURCE_PREFIX_BYTES, SOURCE_PREFIX_SHA256)
    hash_gate("source span 873-911", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix after 911", suffix, 0, EMPTY_SHA256)
    hash_gate(
        "source line 873",
        source_view.records[872],
        SOURCE_START_LINE_BYTES,
        SOURCE_START_LINE_SHA256,
    )
    hash_gate(
        "source line 911",
        source_view.records[910],
        SOURCE_END_LINE_BYTES,
        SOURCE_END_LINE_SHA256,
    )
    hash_gate("candidate full file", candidate.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)

    require(source.line(1) == candidate.line(1) == START_LINE, "exercise opening changed")
    require(source.line(39) == candidate.line(39) == END_LINE, "exercise closing changed")
    require(source_view.records[-1] == b"\\end{Exercises}\n", "authority EOF signature changed")
    require(candidate.records[-1] == b"\\end{Exercises}\n", "candidate EOF signature changed")
    require(source_view.raw == prefix + source.raw, "authority tail does not end at physical EOF")


def gate_naturality_correction(source: Span, candidate: Span) -> None:
    require(source.text.count(SOURCE_FALSE_SYMMETRY_CLAIM) == 1, "source false claim changed")
    require(SOURCE_FALSE_SYMMETRY_CLAIM in source.line(5), "false claim moved from line 877")
    require(SOURCE_FALSE_SYMMETRY_CLAIM not in candidate.text, "false symmetry demand remains")
    require(candidate.text.count(TARGET_NATURALITY_TEST) == 1, "naturality-test repair changed")
    require(TARGET_NATURALITY_TEST in candidate.line(5), "naturality repair moved from line 5")


def gate_prepromotion_language_refinements(candidate: Span) -> None:
    require(
        "suatu isomorfisme natural antarfungtor" in candidate.line(22),
        "functor-isomorphism refinement missing or moved",
    )
    require(
        "objek satuan dari $Z(\\mathcal{V})$" in candidate.line(29),
        "unit-object grammar refinement missing or moved",
    )
    require(
        candidate.line(33).count("transformasi natural") == 2,
        "natural-transformation refinement must occur twice on line 33",
    )
    require("isomorfisme fungtor" not in candidate.text, "compressed functor-isomorphism phrase remains")
    require("morfisme antarfungtor" not in candidate.text, "obsolete morphism-between-functors phrase remains")
    require("Definisikan morfisme $\\alpha" not in candidate.text, "generic alpha definition remains")


def gate_commands_and_math(source: Span, candidate: Span) -> None:
    for line_number, (source_line, target_line) in enumerate(
        zip(source.lines, candidate.lines, strict=True), 1
    ):
        require(
            Counter(COMMAND_RE.findall(source_line)) == Counter(COMMAND_RE.findall(target_line)),
            f"line {line_number}: TeX command multiset changed",
        )
    require(len(COMMAND_RE.findall(source.text)) == 248, "source command census changed")
    require(len(COMMAND_RE.findall(candidate.text)) == 248, "candidate command census changed")

    source_inline = inline_math(source.text)
    target_inline = inline_math(candidate.text)
    require(len(source_inline) == len(target_inline) == 69, "inline-math census changed")
    require(source_inline == target_inline, "inline mathematics or positions changed")

    source_displays = bracket_displays(source.text)
    target_displays = bracket_displays(candidate.text)
    require(len(source_displays) == len(target_displays) == 6, "bracket-display census changed")
    require(source_displays == target_displays, "display mathematics or diagram text changed")


def gate_document_topology(source: Span, candidate: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(candidate.text)
    audit_nesting(source_events, "source span")
    audit_nesting(target_events, "candidate")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == len(target_events) == 14, "environment event census changed")
    begins = Counter(name for _, kind, name in source_events if kind == "begin")
    ends = Counter(name for _, kind, name in source_events if kind == "end")
    require(begins == ends == EXPECTED_BEGIN_COUNTS, "environment type census changed")

    require(not LABEL_RE.search(source.text), "source label census changed")
    require(not LABEL_RE.search(candidate.text), "unexpected candidate label")

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
        "exercise/subitem topology changed",
    )
    require(
        tuple(line for line, value in enumerate(source.lines, 1) if not value.strip())
        == tuple(line for line, value in enumerate(candidate.lines, 1) if not value.strip())
        == EXPECTED_BLANK_LINES,
        "blank-line topology changed",
    )
    require("%" not in source.text and "%" not in candidate.text, "unexpected TeX comment")


def gate_diagrams_indexes_and_language(source: Span, candidate: Span) -> None:
    source_tikzcd = extract_environment(source.text, "tikzcd")
    target_tikzcd = extract_environment(candidate.text, "tikzcd")
    require(len(source_tikzcd) == len(target_tikzcd) == 2, "tikzcd census changed")
    require(source_tikzcd == target_tikzcd, "tikzcd mathematics/topology changed")

    for pattern, expected, name in (
        (NODE_RE, 0, "node"),
        (PATH_RE, 0, "path"),
        (ARROW_RE, 8, "tikzcd arrow"),
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

    require(index_entries(source.text) == EXPECTED_TARGET_INDEXES, "source index census changed")
    require(index_entries(candidate.text) == EXPECTED_TARGET_INDEXES, "candidate index topology changed")
    require(
        brace_audit(source.text) == brace_audit(candidate.text) == (0, 0, 83, 83),
        "brace topology changed",
    )
    require(han_count(source.text) == 575, "source Han census changed")
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
    gate_naturality_correction(source, candidate)
    gate_prepromotion_language_refinements(candidate)
    gate_commands_and_math(source, candidate)
    gate_document_topology(source, candidate)
    gate_diagrams_indexes_and_language(source, candidate)

    print(
        "\n".join(
            (
                "PASS Unit 024 isolated candidate checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source prefix=1-872 bytes={SOURCE_PREFIX_BYTES} sha256={SOURCE_PREFIX_SHA256}",
                f"source span=873-911 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                "source suffix=empty sha256=" + EMPTY_SHA256,
                f"candidate lines=39 bytes={len(candidate.raw)} sha256={sha256(candidate.raw).hexdigest()}",
                "boundary=start=Exercises line873 end=Exercises line911=authority-EOF",
                "environments=7-pairs exercises=8 subitems=3 hints=2 refs=4 cites=0 indexes=1",
                "inline_math=69 bracket_displays=6 commands=248 braces=83/83 han=0",
                "tikzcd=2 arrows=8 nodes=0 paths=0 edges=0 draws=0",
                f"correction={CORRECTION_NATURALITY_ID}-false-symmetry-demand-to-naturality-counterexample",
                "refinements=isomorfisme-natural-antarfungtor+objek-satuan-dari+2x-transformasi-natural",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 024 isolated candidate checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
