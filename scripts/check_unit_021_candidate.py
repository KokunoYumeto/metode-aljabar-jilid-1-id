#!/usr/bin/env python3
"""Fail-closed source/structure check for the isolated Unit 021 candidate."""

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
CANDIDATE = ROOT / "build/unit-021-candidate/chapter3-braiding-id.tex"

SOURCE_START = 307
SOURCE_END = 512
SOURCE_FULL_LINES = 911
CANDIDATE_LINES = 206

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_PREFIX_BYTES = 27_816
SOURCE_PREFIX_SHA256 = "ffce6a027b6d3ceacffd30548553b7539688ff552f075127dd769a9900bbfff5"
SOURCE_SPAN_BYTES = 15_276
SOURCE_SPAN_SHA256 = "cbbf8714c3e5a387e42e2653900a8f3911e41df530b39a86701261c89de64ff8"
SOURCE_SUFFIX_BYTES = 32_479
SOURCE_SUFFIX_SHA256 = "0184b127cecf8e973aa395e050385ed75280b898d5ea22293572d6513d7a6c83"
SOURCE_START_LINE_BYTES = 40
SOURCE_START_LINE_SHA256 = "0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8"
SOURCE_NEXT_LINE_BYTES = 47
SOURCE_NEXT_LINE_SHA256 = "c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541"

CANDIDATE_BYTES = 17_968
CANDIDATE_SHA256 = "57f5bc8a211b6a9b76a096742fbfc94989c890f11d5140ad449d0e76e2c67085"
CANDIDATE_START_LINE_BYTES = 46
CANDIDATE_START_LINE_SHA256 = "8acd960675d96dd70537f2cb73f61098075ac025b1b983fcc584dd66573605bd"

SOURCE_START_LINE = r"\section{辫结构}\label{sec:braiding}"
SOURCE_NEXT_LINE = r"\section{充实范畴}\label{sec:enriched-cat}"
CANDIDATE_START_LINE = r"\section{Struktur Kepang}\label{sec:braiding}"

CORRECTION_ID = "O013-LI-U021-COR-001"
SOURCE_NATURALITY_BOTTOM = (
    r'X \otimes Y \arrow[r, "{c(X, Y)}"'
    r"'] & Y \otimes X"
)
TARGET_NATURALITY_BOTTOM = (
    r'''X' \otimes Y' \arrow[r, "{c(X', Y')}"'''
    r"'] & Y' \otimes X'"
)
OBJECT_TYPE_CORRECTION_ID = "O013-LI-U021-COR-002"
SOURCE_OBJECT_X_MISNOMER = r"对应于辫子 $X$"
SOURCE_OBJECT_Y_MISNOMER = r"对应于辫子 $Y$"
TARGET_OBJECT_X_CLARIFICATION = r"bersesuaian dengan objek $X$"
TARGET_OBJECT_Y_CLARIFICATION = r"bersesuaian dengan objek $Y$"
EDITORIAL_ID = "O013-LI-U021-ED-001"
SOURCE_DUPLICATION = "无穷循环群群"
TARGET_NORMALIZATION = "grup siklik tak hingga"
PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"

COMMAND_RE = re.compile(r"\\(?:[A-Za-z@]+|.)")
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
CROSS_REF_RE = re.compile(r"\\(ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}")
ITEM_RE = re.compile(r"\\item\b")
INDEX_RE = re.compile(r"\\index(?:\[([^\]]*)\])?\{((?:[^{}]|\{[^{}]*\})*)\}")
NODE_RE = re.compile(r"\\node\b")
PATH_RE = re.compile(r"\\path\b")
ARROW_RE = re.compile(r"\\arrow\s*\[")
EDGE_RE = re.compile(r"\bedge\b")
DRAW_RE = re.compile(r"\\draw\b")
BRAID_RE = re.compile(r"\\braid\b")
COORDINATE_RE = re.compile(r"\\coordinate\b")

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

EXPECTED_BLANK_LINES = (
    3,
    28,
    37,
    45,
    49,
    58,
    74,
    76,
    87,
    96,
    101,
    117,
    129,
    131,
    141,
    167,
    176,
    204,
    206,
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

REQUIRED_TERMINOLOGY = (
    "struktur kepang",
    "kendala komutativitas",
    "kategori monoidal berkepang",
    "fungtor monoidal berkepang",
    "kategori monoidal simetris",
    "aksioma segienam",
    "persamaan Yang--Baxter",
    "kategori kepang",
    "grup kepang Artin",
    "grup kepang",
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


def normalize_math(value: str) -> str:
    return (
        value.strip()
        .replace(r"\text{子集}", r"\text{subhimpunan}")
        .replace(r"\text{相异元}", r"\text{unsur-unsurnya berbeda}")
        .replace(r"\text{条}", r"\text{untai}")
        .replace(SOURCE_NATURALITY_BOTTOM, TARGET_NATURALITY_BOTTOM)
    )


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


def gate_boundaries(source_view: FileView, source: Span, candidate: Span) -> None:
    prefix = b"".join(source_view.records[: SOURCE_START - 1])
    suffix = b"".join(source_view.records[SOURCE_END:])
    first_line = source_view.records[SOURCE_START - 1]
    next_line = source_view.records[SOURCE_END]

    hash_gate("source full file", source_view.raw, SOURCE_FULL_BYTES, SOURCE_FULL_SHA256)
    hash_gate("source prefix 1-306", prefix, SOURCE_PREFIX_BYTES, SOURCE_PREFIX_SHA256)
    hash_gate("source span 307-512", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix 513-911", suffix, SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256)
    hash_gate(
        "source line 307",
        first_line,
        SOURCE_START_LINE_BYTES,
        SOURCE_START_LINE_SHA256,
    )
    hash_gate(
        "source line 513",
        next_line,
        SOURCE_NEXT_LINE_BYTES,
        SOURCE_NEXT_LINE_SHA256,
    )
    hash_gate("candidate full file", candidate.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)
    hash_gate(
        "candidate line 1",
        candidate.raw[: candidate.raw.find(b"\n") + 1],
        CANDIDATE_START_LINE_BYTES,
        CANDIDATE_START_LINE_SHA256,
    )

    require(source.line(1) == SOURCE_START_LINE, "authority line 307 start signature changed")
    require(source.line(206) == "", "authority line 512 must be the included blank separator")
    require(source_view.lines[512] == SOURCE_NEXT_LINE, "authority line 513 enriched boundary changed")
    require(candidate.line(1) == CANDIDATE_START_LINE, "candidate opening signature changed")
    require(candidate.line(206) == "", "candidate must preserve authority line 512's blank record")
    require("sec:enriched-cat" not in candidate.text, "excluded enriched-category section leaked into candidate")


def gate_commands_and_math(source: Span, candidate: Span) -> None:
    for line_number, (source_line, target_line) in enumerate(
        zip(source.lines, candidate.lines, strict=True), 1
    ):
        require(
            Counter(COMMAND_RE.findall(source_line))
            == Counter(COMMAND_RE.findall(target_line)),
            f"line {line_number}: TeX command multiset changed",
        )
    require(len(COMMAND_RE.findall(source.text)) == 527, "source command census changed")
    require(len(COMMAND_RE.findall(candidate.text)) == 527, "candidate command census changed")

    require(source.text.count(SOURCE_NATURALITY_BOTTOM) == 1, "source naturality defect changed")
    require(candidate.text.count(SOURCE_NATURALITY_BOTTOM) == 0, "untyped naturality bottom remains")
    require(candidate.text.count(TARGET_NATURALITY_BOTTOM) == 1, "corrected naturality bottom missing")
    require(SOURCE_NATURALITY_BOTTOM in source.line(181), "source defect moved from authority line 487")
    require(TARGET_NATURALITY_BOTTOM in candidate.line(181), "candidate correction moved from line 181")
    require(
        source.text.count(SOURCE_OBJECT_X_MISNOMER)
        == source.text.count(SOURCE_OBJECT_Y_MISNOMER)
        == 1,
        "source object/braid misnomer signatures changed",
    )
    require(
        candidate.text.count(TARGET_OBJECT_X_CLARIFICATION)
        == candidate.text.count(TARGET_OBJECT_Y_CLARIFICATION)
        == 1,
        "object-type clarifications changed",
    )
    require(
        SOURCE_OBJECT_X_MISNOMER in source.line(144)
        and TARGET_OBJECT_X_CLARIFICATION in candidate.line(144)
        and SOURCE_OBJECT_Y_MISNOMER in source.line(146)
        and TARGET_OBJECT_Y_CLARIFICATION in candidate.line(146),
        "object-type correction moved from source lines 450/452",
    )
    require(source.text.count(SOURCE_DUPLICATION) == 1, "source duplicated-word signature changed")
    require(SOURCE_DUPLICATION not in candidate.text, "source duplicated-word residue remains")
    require(candidate.text.count(TARGET_NORMALIZATION) == 1, "editorial normalization changed")

    source_inline = inline_math(source.text)
    target_inline = inline_math(candidate.text)
    require(len(source_inline) == len(target_inline) == 144, "inline-math census changed")
    source_by_line: dict[int, list[str]] = {}
    target_by_line: dict[int, list[str]] = {}
    for line, value in source_inline:
        source_by_line.setdefault(line, []).append(normalize_math(value))
    for line, value in target_inline:
        target_by_line.setdefault(line, []).append(normalize_math(value))
    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology changed")
    reorder_lines: list[int] = []
    for line in source_by_line:
        if source_by_line[line] == target_by_line[line]:
            continue
        reorder_lines.append(line)
        require(
            Counter(source_by_line[line]) == Counter(target_by_line[line]),
            f"line {line}: inline mathematics changed beyond localization/correction/reordering",
        )
    require(
        tuple(reorder_lines) == (100, 132, 144, 146),
        f"inline-math reorder lines changed: {reorder_lines}",
    )

    source_displays = [normalize_math(value) for value in bracket_displays(source.text)]
    target_displays = [normalize_math(value) for value in bracket_displays(candidate.text)]
    require(len(source_displays) == len(target_displays) == 6, "bracket-display census changed")
    require(source_displays == target_displays, "display mathematics changed beyond localization")


def gate_document_topology(source: Span, candidate: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(candidate.text)
    audit_nesting(source_events, "source span")
    audit_nesting(target_events, "candidate")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == len(target_events) == 86, "environment event census changed")
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

    def citations(text: str) -> tuple[tuple[int, str], ...]:
        return tuple(
            (1 + text.count("\n", 0, match.start()), match.group(0))
            for match in CITE_RE.finditer(text)
        )

    require(
        citations(source.text) == citations(candidate.text) == EXPECTED_CITES,
        "citation topology changed",
    )
    require(not ITEM_RE.search(source.text) and not ITEM_RE.search(candidate.text), "unexpected item")
    require("%" not in source.text and "%" not in candidate.text, "unexpected TeX comment")
    require(
        tuple(line for line, value in enumerate(source.lines, 1) if value == "")
        == tuple(line for line, value in enumerate(candidate.lines, 1) if value == "")
        == EXPECTED_BLANK_LINES,
        "blank-line topology changed",
    )


def gate_diagrams_indexes_and_language(source: Span, candidate: Span) -> None:
    source_tikz = extract_environment(source.text, "tikzpicture")
    target_tikz = extract_environment(candidate.text, "tikzpicture")
    require(source_tikz == target_tikz and len(source_tikz) == 17, "tikzpicture blocks changed")

    source_tikzcd = [normalize_math(value) for value in extract_environment(source.text, "tikzcd")]
    target_tikzcd = [normalize_math(value) for value in extract_environment(candidate.text, "tikzcd")]
    require(len(source_tikzcd) == len(target_tikzcd) == 6, "tikzcd census changed")
    require(source_tikzcd == target_tikzcd, "tikzcd changed beyond naturality correction")

    for name, expected in (("equation", 3), ("align*", 2), ("multline*", 1), ("array", 1)):
        source_blocks = [normalize_math(value) for value in extract_environment(source.text, name)]
        target_blocks = [normalize_math(value) for value in extract_environment(candidate.text, name)]
        require(len(source_blocks) == len(target_blocks) == expected, f"{name} census changed")
        require(source_blocks == target_blocks, f"{name} mathematics changed")

    for pattern, expected, name in (
        (NODE_RE, 30, "node"),
        (PATH_RE, 0, "path"),
        (ARROW_RE, 26, "tikzcd arrow"),
        (EDGE_RE, 15, "TikZ edge"),
        (DRAW_RE, 32, "draw"),
        (BRAID_RE, 10, "braid"),
        (COORDINATE_RE, 2, "coordinate"),
    ):
        require(located_lines(pattern, source.text) == located_lines(pattern, candidate.text), f"{name} positions changed")
        require(len(pattern.findall(source.text)) == len(pattern.findall(candidate.text)) == expected, f"{name} census changed")

    target_indexes = tuple(
        (1 + candidate.text.count("\n", 0, match.start()), match.group(1), match.group(2))
        for match in INDEX_RE.finditer(candidate.text)
    )
    require(len(INDEX_RE.findall(source.text)) == 8, "source index census changed")
    require(target_indexes == EXPECTED_TARGET_INDEXES, "localized index topology changed")

    require(brace_audit(source.text) == brace_audit(candidate.text) == (0, 0, 276, 276), "brace topology changed")
    require(han_count(source.text) == 1_446, "source Han census changed")
    require(han_count(candidate.text) == 0, "candidate contains untranslated Han")

    for term in REQUIRED_TERMINOLOGY:
        require(term in candidate.text, f"required controlled/corpus terminology missing: {term}")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source_view = read_file(SOURCE, SOURCE_FULL_LINES)
    candidate_view = read_file(CANDIDATE, CANDIDATE_LINES)
    source = make_span(source_view, SOURCE_START, SOURCE_END)
    candidate = make_span(candidate_view, 1, CANDIDATE_LINES)

    gate_boundaries(source_view, source, candidate)
    gate_commands_and_math(source, candidate)
    gate_document_topology(source, candidate)
    gate_diagrams_indexes_and_language(source, candidate)

    print(
        "\n".join(
            (
                "PASS Unit 021 isolated candidate checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source prefix=1-306 bytes={SOURCE_PREFIX_BYTES} sha256={SOURCE_PREFIX_SHA256}",
                f"source span=307-512 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"source suffix=513-911 bytes={SOURCE_SUFFIX_BYTES} sha256={SOURCE_SUFFIX_SHA256}",
                f"candidate lines=206 bytes={len(candidate.raw)} sha256={sha256(candidate.raw).hexdigest()}",
                "boundary=start=braiding included-blank=512 next=513-enriched-category-excluded",
                "environments=43-pairs labels=9 refs=10 eqrefs=3 cites=2 items=0 indexes=8",
                "inline_math=144 bracket_displays=6 commands=527 braces=276/276 han=0",
                "tikzpicture=17 tikzcd=6 nodes=30 arrows=26 draws=32 braids=10",
                f"correction={CORRECTION_ID}-naturality-bottom-X,Y-to-X-prime,Y-prime",
                f"correction={OBJECT_TYPE_CORRECTION_ID}-braid-X,Y-to-object-X,Y",
                f"editorial={EDITORIAL_ID}-duplicated-group-word-normalized",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 021 isolated candidate checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
