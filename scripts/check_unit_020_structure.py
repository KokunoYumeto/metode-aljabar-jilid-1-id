#!/usr/bin/env python3
"""Fail-closed canonical structure/math check for Indonesian Unit 020."""

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
TARGET = ROOT / "repo/source/chapter3.tex"
CANDIDATE = ROOT / "build/unit-020-candidate/chapter3-strictness-coherence-id.tex"

SOURCE_START = 228
SOURCE_END = 306
TARGET_START = 227
TARGET_END = 305
SOURCE_FULL_LINES = 911
TARGET_FULL_LINES = 910
CANDIDATE_LINES = 79

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_SPAN_BYTES = 6_071
SOURCE_SPAN_SHA256 = "86f02abb667e1f03a99e89f34982527fbb715eb55496f9c76c576e041076d737"
SOURCE_SUFFIX_BYTES = 47_755
SOURCE_SUFFIX_SHA256 = "2efcd829501d06686667549395cb4680ebeccce48ecb981f9b144890fcf4a1f2"

TARGET_FULL_BYTES = 80_889
TARGET_FULL_SHA256 = "64d334af911539cbe844a250ab41c3e6d537e2c827919c21d41547e1f5782d7a"
TARGET_PREFIX_BYTES = 25_868
TARGET_PREFIX_SHA256 = "6b42291293a06d15b64034a26ed25aeac3cb41465bf9533e069bc9ac65d9b8ac"
TARGET_SPAN_BYTES = 7_266
TARGET_SPAN_SHA256 = "25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270"
TARGET_SUFFIX_BYTES = 47_755
TARGET_SUFFIX_SHA256 = "2efcd829501d06686667549395cb4680ebeccce48ecb981f9b144890fcf4a1f2"

CANDIDATE_BYTES = 7_266
CANDIDATE_SHA256 = "25f8aa41663253a28ac27c3cf635470ac2e20e69d48b168d98cb025a3a792270"

SOURCE_START_LINE_BYTES = 56
SOURCE_START_LINE_SHA256 = "de95d42ef774ec462cf17acb4bfc80ad71f202f4d9b5c6caeabb4e6b513f0ca7"
TARGET_START_LINE_BYTES = 63
TARGET_START_LINE_SHA256 = "e868d99e2c3d7dfdbf3ea4eacadf040bbffa0d17d8e2aa166ed4b0833ada1f26"
NEXT_LINE_BYTES = 40
NEXT_LINE_SHA256 = "0f3481f923513a19091dc664cd63849cbceb4b3097c192d9ea5b1780c4f750e8"

SOURCE_START_LINE = r"\section{严格性与融贯定理}\label{sec:coherence}"
TARGET_START_LINE = r"\section{Keketatan dan Teorema Koherensi}\label{sec:coherence}"
NEXT_LINE = r"\section{辫结构}\label{sec:braiding}"

CORRECTION_ID = "O013-LI-U020-COR-001"
CORRECTION_SOURCE = r"(F, m) \simeq L(F(\munit))"
CORRECTION_TARGET = r"(F, \rho) \simeq L(F(\munit))"
PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"

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
        "compactitem": 3,
        "lemma": 2,
        "proof": 2,
        "compactenum": 1,
        "definition": 1,
        "theorem": 1,
        "center": 1,
        "tikzpicture": 1,
        "tikzcd": 1,
    }
)

EXPECTED_LABELS = (
    (1, "sec:coherence"),
    (9, "def:strict-monoidal-cat"),
    (21, "prop:ML-coherence"),
)

EXPECTED_CROSS_REFS = (
    (5, "ref", "def:monoidal-cat"),
    (19, "ref", "sec:monoidal-cat-def"),
    (19, "ref", "eg:monoidal-cat"),
    (25, "ref", "prop:ML-coherence"),
    (78, "ref", "prop:ML-coherence"),
)

EXPECTED_CITES = (
    (19, r"\cite[VII.2]{ML98}"),
    (25, r"\cite[pp.26--27]{JS93}"),
    (25, r"\cite[\S 2.8]{EGNO15}"),
)

EXPECTED_ITEMS = (4, 5, 12, 13, 27, 44, 50, 51, 72, 73)

EXPECTED_TARGET_INDEXES = (
    (
        9,
        None,
        "yaobanfanchou@kategori monoidal (monoidal category)!"
        "kategori monoidal ketat (strict monoidal category)",
    ),
    (
        21,
        None,
        "MacLane@Teorema koherensi Mac Lane (Mac Lane's Coherence Theorem)",
    ),
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
    target_view: FileView,
    candidate_view: FileView,
    source: Span,
    target: Span,
) -> None:
    source_suffix = b"".join(source_view.records[SOURCE_END:])
    target_prefix = b"".join(target_view.records[: TARGET_START - 1])
    target_suffix = b"".join(target_view.records[TARGET_END:])

    hash_gate("source full file", source_view.raw, SOURCE_FULL_BYTES, SOURCE_FULL_SHA256)
    hash_gate("source span 228-306", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix 307-911", source_suffix, SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256)
    hash_gate("target full file", target_view.raw, TARGET_FULL_BYTES, TARGET_FULL_SHA256)
    hash_gate("target prefix 1-226", target_prefix, TARGET_PREFIX_BYTES, TARGET_PREFIX_SHA256)
    hash_gate("target span 227-305", target.raw, TARGET_SPAN_BYTES, TARGET_SPAN_SHA256)
    hash_gate("target suffix 306-910", target_suffix, TARGET_SUFFIX_BYTES, TARGET_SUFFIX_SHA256)
    hash_gate("candidate full file", candidate_view.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)
    hash_gate(
        "source start line 228",
        source_view.records[SOURCE_START - 1],
        SOURCE_START_LINE_BYTES,
        SOURCE_START_LINE_SHA256,
    )
    hash_gate(
        "target start line 227",
        target_view.records[TARGET_START - 1],
        TARGET_START_LINE_BYTES,
        TARGET_START_LINE_SHA256,
    )
    hash_gate(
        "source next line 307",
        source_view.records[SOURCE_END],
        NEXT_LINE_BYTES,
        NEXT_LINE_SHA256,
    )
    hash_gate(
        "target next line 306",
        target_view.records[TARGET_END],
        NEXT_LINE_BYTES,
        NEXT_LINE_SHA256,
    )

    require(source.line(1) == SOURCE_START_LINE, "source Unit 020 opening changed")
    require(source.line(79) == "", "source line 306 must be the included blank separator")
    require(target.line(1) == TARGET_START_LINE, "canonical Unit 020 opening changed")
    require(target.line(79) == "", "target line 305 must preserve the included blank separator")
    require(source_view.lines[306] == target_view.lines[305] == NEXT_LINE, "braiding boundary changed")
    require(target.raw == candidate_view.raw, "canonical Unit 020 span is not byte-identical to candidate")
    require(target_suffix == source_suffix, "post-Unit-020 canonical remainder differs from frozen authority")
    require("sec:braiding" not in target.text, "braiding section leaked into Unit 020 span")


def gate_commands_and_math(source: Span, target: Span) -> None:
    mismatch_lines: list[int] = []
    for line_number, (source_line, target_line) in enumerate(
        zip(source.lines, target.lines, strict=True), 1
    ):
        source_commands = Counter(COMMAND_RE.findall(source_line))
        target_commands = Counter(COMMAND_RE.findall(target_line))
        if source_commands == target_commands:
            continue
        mismatch_lines.append(line_number)
        require(line_number == 72, f"relative line {line_number}: TeX command multiset changed")
        require(
            target_commands - source_commands == Counter({r"\rho": 1})
            and not (source_commands - target_commands),
            "relative line 72 differs beyond the declared (F,m)-to-(F,rho) correction",
        )
    require(tuple(mismatch_lines) == (72,), f"command mismatch lines changed: {mismatch_lines}")
    require(len(COMMAND_RE.findall(source.text)) == 228, "source command census changed")
    require(len(COMMAND_RE.findall(target.text)) == 229, "target command census changed")

    require(source.text.count(CORRECTION_SOURCE) == 1, "source correction signature changed")
    require(source.text.count(r"(F, \rho)") == 1, "source defining (F,rho) signature changed")
    require(target.text.count(CORRECTION_SOURCE) == 0, "source (F,m) defect remains in target")
    require(target.text.count(CORRECTION_TARGET) == 1, "target correction signature changed")
    require(target.text.count(r"(F, \rho)") == 2, "target (F,rho) census changed")
    require(CORRECTION_SOURCE in source.line(72), "correction moved from authority line 299")
    require(CORRECTION_TARGET in target.line(72), "correction moved from canonical line 298")

    source_inline = inline_math(source.text)
    target_inline = inline_math(target.text)
    require(len(source_inline) == len(target_inline) == 64, "inline-math census changed")
    source_by_line: dict[int, list[str]] = {}
    target_by_line: dict[int, list[str]] = {}
    for line, value in source_inline:
        source_by_line.setdefault(line, []).append(
            value.strip().replace("(F, m)", r"(F, \rho)")
        )
    for line, value in target_inline:
        target_by_line.setdefault(line, []).append(value.strip())
    require(source_by_line.keys() == target_by_line.keys(), "inline-math line topology changed")
    reorder_lines: list[int] = []
    for line in source_by_line:
        if source_by_line[line] == target_by_line[line]:
            continue
        reorder_lines.append(line)
        require(
            Counter(source_by_line[line]) == Counter(target_by_line[line]),
            f"relative line {line}: inline mathematics changed beyond correction/reordering",
        )
    require(tuple(reorder_lines) == (44,), f"inline-math reorder lines changed: {reorder_lines}")

    source_displays = bracket_displays(source.text)
    target_displays = bracket_displays(target.text)
    require(len(source_displays) == len(target_displays) == 5, "bracket-display census changed")
    require(source_displays == target_displays, "display mathematics or diagram changed")


def gate_document_topology(source: Span, target: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(target.text)
    audit_nesting(source_events, "source span")
    audit_nesting(target_events, "canonical span")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == len(target_events) == 26, "environment event census changed")
    begins = Counter(name for _, kind, name in source_events if kind == "begin")
    ends = Counter(name for _, kind, name in source_events if kind == "end")
    require(begins == ends == EXPECTED_BEGIN_COUNTS, "environment type census changed")

    require(
        located_values(LABEL_RE, source.text)
        == located_values(LABEL_RE, target.text)
        == EXPECTED_LABELS,
        "label topology changed",
    )

    def cross_refs(text: str) -> tuple[tuple[int, str, str], ...]:
        return tuple(
            (1 + text.count("\n", 0, match.start()), match.group(1), match.group(2))
            for match in CROSS_REF_RE.finditer(text)
        )

    require(
        cross_refs(source.text) == cross_refs(target.text) == EXPECTED_CROSS_REFS,
        "reference topology changed",
    )

    def citations(text: str) -> tuple[tuple[int, str], ...]:
        return tuple(
            (1 + text.count("\n", 0, match.start()), match.group(0))
            for match in CITE_RE.finditer(text)
        )

    require(
        citations(source.text) == citations(target.text) == EXPECTED_CITES,
        "citation topology changed",
    )
    require(
        located_lines(ITEM_RE, source.text)
        == located_lines(ITEM_RE, target.text)
        == EXPECTED_ITEMS,
        "item topology changed",
    )
    require("%" not in source.text and "%" not in target.text, "unexpected TeX comment in Unit 020")


def gate_diagrams_indexes_and_residue(source: Span, target: Span) -> None:
    source_tikz = extract_environment(source.text, "tikzpicture")
    target_tikz = extract_environment(target.text, "tikzpicture")
    require(source_tikz == target_tikz and len(source_tikz) == 1, "TikZ pentagon changed")

    source_tikzcd = extract_environment(source.text, "tikzcd")
    target_tikzcd = extract_environment(target.text, "tikzcd")
    require(source_tikzcd == target_tikzcd and len(source_tikzcd) == 1, "tikzcd square changed")

    require(located_lines(NODE_RE, source.text) == located_lines(NODE_RE, target.text), "node positions changed")
    require(len(NODE_RE.findall(source.text)) == len(NODE_RE.findall(target.text)) == 5, "node census changed")
    require(located_lines(PATH_RE, source.text) == located_lines(PATH_RE, target.text) == (37,), "path topology changed")
    require(len(EDGE_RE.findall(source.text)) == len(EDGE_RE.findall(target.text)) == 5, "edge census changed")
    require(located_lines(ARROW_RE, source.text) == located_lines(ARROW_RE, target.text), "arrow positions changed")
    require(len(ARROW_RE.findall(source.text)) == len(ARROW_RE.findall(target.text)) == 4, "arrow census changed")

    target_indexes = tuple(
        (1 + target.text.count("\n", 0, match.start()), match.group(1), match.group(2))
        for match in INDEX_RE.finditer(target.text)
    )
    require(len(INDEX_RE.findall(source.text)) == 2, "source index census changed")
    require(target_indexes == EXPECTED_TARGET_INDEXES, "localized index topology changed")

    require(brace_audit(source.text) == brace_audit(target.text) == (0, 0, 95, 95), "brace topology changed")
    require(han_count(source.text) == 811, "source Han census changed")
    require(han_count(target.text) == 0, "canonical Unit 020 contains untranslated Han")


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")
    source_view = read_file(SOURCE, SOURCE_FULL_LINES)
    target_view = read_file(TARGET, TARGET_FULL_LINES)
    candidate_view = read_file(CANDIDATE, CANDIDATE_LINES)
    source = make_span(source_view, SOURCE_START, SOURCE_END)
    target = make_span(target_view, TARGET_START, TARGET_END)

    gate_identities_and_boundaries(source_view, target_view, candidate_view, source, target)
    gate_commands_and_math(source, target)
    gate_document_topology(source, target)
    gate_diagrams_indexes_and_residue(source, target)

    print(
        "\n".join(
            (
                "PASS Unit 020 canonical structure checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source span=228-306 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"target full_lines=910 bytes={len(target_view.raw)} sha256={sha256(target_view.raw).hexdigest()}",
                f"target prefix=1-226 bytes={TARGET_PREFIX_BYTES} sha256={TARGET_PREFIX_SHA256}",
                f"target span=227-305 bytes={len(target.raw)} sha256={sha256(target.raw).hexdigest()}",
                f"target suffix=306-910 bytes={TARGET_SUFFIX_BYTES} sha256={TARGET_SUFFIX_SHA256}",
                "integration=candidate-byte-identical remainder=authority-307-911-byte-identical",
                "boundary=target-227-start included-blank=305 target-306-braiding-excluded",
                "environments=13-pairs labels=3 refs=5 eqrefs=0 cites=3 items=10 indexes=2",
                "inline_math=64 bracket_displays=5 braces=95/95 han=0",
                "tikzpicture=1 tikzcd=1 nodes=5 paths=1 edges=5 arrows=4",
                f"correction={CORRECTION_ID}-source-299-target-298-(F,m)-to-(F,rho)",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 020 canonical structure checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
