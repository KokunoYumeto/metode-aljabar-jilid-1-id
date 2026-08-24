#!/usr/bin/env python3
"""Fail-closed source/structure check for the isolated Unit 022 candidate."""

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
CANDIDATE = ROOT / "build/unit-022-candidate/chapter3-enriched-categories-id.tex"

SOURCE_START = 513
SOURCE_END = 722
SOURCE_FULL_LINES = 911
CANDIDATE_LINES = 210

SOURCE_FULL_BYTES = 75_571
SOURCE_FULL_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_PREFIX_BYTES = 43_092
SOURCE_PREFIX_SHA256 = "6726e64e5924c3ca06d5ce68aa654e3e8ec00c01799164e5f959f6b485be09c9"
SOURCE_SPAN_BYTES = 15_089
SOURCE_SPAN_SHA256 = "85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d"
SOURCE_SUFFIX_BYTES = 17_390
SOURCE_SUFFIX_SHA256 = "db85619a873a826c4a417252b5268b9c85d068f18f9467664599fb9b0575b6af"
SOURCE_START_LINE_BYTES = 47
SOURCE_START_LINE_SHA256 = "c4fb914defd51476a7a9721c86e92cedeef7c29344722a029cf2dc46825ac541"
SOURCE_NEXT_LINE_BYTES = 64
SOURCE_NEXT_LINE_SHA256 = "26cf19a66c488255e23a0fa8774aca285f48b9049a6111bf2c6fe8d746bdced7"

CANDIDATE_BYTES = 17_541
CANDIDATE_SHA256 = "e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255"
CANDIDATE_START_LINE_BYTES = 53
CANDIDATE_START_LINE_SHA256 = "b78c271f491390406a7a662c60840619c688f3e225674d18f549c88170b2384e"

SOURCE_START_LINE = r"\section{充实范畴}\label{sec:enriched-cat}"
SOURCE_NEXT_LINE = r"\section{\texorpdfstring{$2$}{2}-范畴一瞥}\label{sec:2-cat}"
CANDIDATE_START_LINE = r"\section{Kategori Diperkaya}\label{sec:enriched-cat}"

CORRECTION_SET_PRODUCT_ID = "O013-LI-U022-COR-001"
SOURCE_SET_LEVEL_PRODUCT = r"\right) \otimes \Hom_{\mathcal{V}}\left("
TARGET_SET_LEVEL_PRODUCT = r"\right) \times \Hom_{\mathcal{V}}\left("

CORRECTION_INJECTION_ID = "O013-LI-U022-COR-002"
SOURCE_INJECTION_DOMAIN = r"\iota_i: X_1 \to Z"
TARGET_INJECTION_DOMAIN = r"\iota_i: X_i \to Z"

SOURCE_FUNCTORIAL_LABEL = r"{\otimes \;\text{的函子性}}"
TARGET_FUNCTORIAL_LABEL = r"{\text{fungtorialitas }\;\otimes}"
SOURCE_PULLBACK_LABEL = (
    r"{\text{用 }\; \iota: \munit \otimes \munit "
    r"\rightiso \munit \text{ 拉回}}"
)
TARGET_PULLBACK_LABEL = (
    r"{\text{tarik balik melalui }\; \iota: \munit \otimes \munit "
    r"\rightiso \munit \text{ di atas}}"
)
SOURCE_HOM_SET_NODE = r"{$\Hom$-集}"
TARGET_HOM_SET_NODE = r"{himpunan-$\Hom$}"
SOURCE_HOM_OBJECT_NODE = r"{$\Hom$-对象}"
TARGET_HOM_OBJECT_NODE = r"{objek-$\Hom$}"
SOURCE_REPLACE_NODE = r"{\footnotesize 代换成}"
TARGET_REPLACE_NODE = r"{\footnotesize diganti dengan}"

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
        "tikzcd": 6,
        "definition": 5,
        "proof": 4,
        "tikzpicture": 3,
        "example": 3,
        "align*": 3,
        "cases": 3,
        "compactitem": 2,
        "center": 2,
        "remark": 2,
        "compactenum": 2,
        "proposition": 2,
        "enumerate": 1,
        "gather*": 1,
        "theorem": 1,
        "lemma": 1,
    }
)

EXPECTED_LABELS = (
    (1, "sec:enriched-cat"),
    (15, "def:enriched-cat"),
    (59, "def:enriched-functor"),
    (71, "rem:enriched-to-ordinary"),
    (82, "def:enriched-naturaltrans"),
    (100, "eg:Ab-cat"),
    (120, "def:biproduct"),
    (133, "prop:biproduct-criterion"),
    (191, "def:additive-cat"),
    (197, "prop:biproduct-preservation"),
    (204, "prop:additive-prod-coprod"),
)

EXPECTED_CROSS_REFS = (
    (7, "ref", "eg:categories"),
    (57, "ref", "def:category"),
    (93, "ref", "eg:monoidal-cat"),
    (93, "ref", "con:U-small"),
    (97, "ref", "eg:categories"),
    (97, "ref", "eg:categories"),
    (115, "ref", "rem:enriched-to-ordinary"),
    (118, "ref", "sec:limits"),
    (142, "ref", "prop:product-associativity"),
    (185, "ref", "def:universal-objects"),
    (185, "ref", "def:zero-morphism"),
    (192, "ref", "def:enriched-functor"),
    (195, "ref", "prop:Mod-cat-additive"),
    (208, "ref", "prop:biproduct-criterion"),
    (208, "ref", "prop:product-associativity"),
)

EXPECTED_CITES = (
    (13, r"\cite{Ke05}"),
    (97, r"\cite[Chapter 5]{May99}"),
)

EXPECTED_ITEM_LINES = (
    4,
    5,
    18,
    19,
    20,
    23,
    103,
    104,
    105,
    106,
    136,
    137,
    138,
    180,
    181,
    182,
    183,
)

EXPECTED_BLANK_LINES = (
    14,
    33,
    47,
    56,
    58,
    70,
    81,
    91,
    95,
    99,
    109,
    117,
    119,
    132,
    152,
    176,
    190,
    194,
    196,
    203,
    210,
)

EXPECTED_TARGET_INDEXES = (
    (15, None, "chongshifanchou@kategori diperkaya (enriched category)"),
    (16, "sym1", r"HomCi@$\iHom_{\mathcal{C}}(X, Y)$"),
    (59, None, "hanzi@fungtor!kasus diperkaya"),
    (82, None, "ziranbianhuan@transformasi natural!kasus diperkaya"),
    (90, None, "fanchoudengjia@ekuivalensi kategori!kasus diperkaya"),
    (96, None, "tuopufanchou@kategori topologis (topological category)"),
    (100, None, r"Ab-fanchou@kategori-$\cate{Ab}$"),
    (120, None, "shuangji@biproduk (biproduct)"),
    (191, None, "jiaxingfanchou@kategori aditif (additive category)"),
    (191, None, "hanzi@fungtor!kasus aditif"),
)

REQUIRED_TERMINOLOGY = (
    "kategori diperkaya",
    "himpunan-$\\Hom$",
    "objek-$\\Hom$",
    "kategori topologis",
    "kategori-$\\cate{Ab}$",
    "kategori praaditif",
    "biproduk",
    "fungtor aditif",
    "kategori aditif",
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


def normalize_target(value: str) -> str:
    return (
        value.replace(TARGET_SET_LEVEL_PRODUCT, SOURCE_SET_LEVEL_PRODUCT)
        .replace(TARGET_INJECTION_DOMAIN, SOURCE_INJECTION_DOMAIN)
        .replace(TARGET_FUNCTORIAL_LABEL, SOURCE_FUNCTORIAL_LABEL)
        .replace(TARGET_PULLBACK_LABEL, SOURCE_PULLBACK_LABEL)
        .replace(TARGET_HOM_SET_NODE, SOURCE_HOM_SET_NODE)
        .replace(TARGET_HOM_OBJECT_NODE, SOURCE_HOM_OBJECT_NODE)
        .replace(TARGET_REPLACE_NODE, SOURCE_REPLACE_NODE)
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
    hash_gate("source prefix 1-512", prefix, SOURCE_PREFIX_BYTES, SOURCE_PREFIX_SHA256)
    hash_gate("source span 513-722", source.raw, SOURCE_SPAN_BYTES, SOURCE_SPAN_SHA256)
    hash_gate("source suffix 723-911", suffix, SOURCE_SUFFIX_BYTES, SOURCE_SUFFIX_SHA256)
    hash_gate("source line 513", first_line, SOURCE_START_LINE_BYTES, SOURCE_START_LINE_SHA256)
    hash_gate("source line 723", next_line, SOURCE_NEXT_LINE_BYTES, SOURCE_NEXT_LINE_SHA256)
    hash_gate("candidate full file", candidate.raw, CANDIDATE_BYTES, CANDIDATE_SHA256)
    hash_gate(
        "candidate line 1",
        candidate.records[0],
        CANDIDATE_START_LINE_BYTES,
        CANDIDATE_START_LINE_SHA256,
    )

    require(source.line(1) == SOURCE_START_LINE, "authority line 513 start signature changed")
    require(source.line(210) == "", "authority line 722 must be the included blank separator")
    require(source_view.lines[722] == SOURCE_NEXT_LINE, "authority line 723 2-category boundary changed")
    require(candidate.line(1) == CANDIDATE_START_LINE, "candidate opening signature changed")
    require(candidate.records[209] == b"\n", "candidate closing blank record changed")
    require(not candidate.line(210).strip(), "candidate must preserve authority line 722's blank record")
    require("sec:2-cat" not in candidate.text, "excluded 2-category section leaked into candidate")


def gate_corrections(source: Span, candidate: Span) -> None:
    require(source.text.count(SOURCE_SET_LEVEL_PRODUCT) == 1, "source set-product defect changed")
    require(candidate.text.count(SOURCE_SET_LEVEL_PRODUCT) == 0, "ill-typed set-level tensor remains")
    require(candidate.text.count(TARGET_SET_LEVEL_PRODUCT) == 1, "Cartesian-product correction changed")
    require(SOURCE_SET_LEVEL_PRODUCT in source.line(76), "set-product defect moved from authority line 588")
    require(TARGET_SET_LEVEL_PRODUCT in candidate.line(76), "set-product correction moved from line 76")

    require(source.text.count(SOURCE_INJECTION_DOMAIN) == 1, "source injection-domain defect changed")
    require(SOURCE_INJECTION_DOMAIN not in candidate.text, "incorrect X_1 injection domain remains")
    require(candidate.text.count(TARGET_INJECTION_DOMAIN) == 1, "X_i injection correction changed")
    require(SOURCE_INJECTION_DOMAIN in source.line(153), "injection defect moved from authority line 665")
    require(TARGET_INJECTION_DOMAIN in candidate.line(153), "injection correction moved from line 153")


def gate_commands_and_math(source: Span, candidate: Span) -> None:
    for line_number, (source_line, target_line) in enumerate(
        zip(source.lines, candidate.lines, strict=True), 1
    ):
        require(
            Counter(COMMAND_RE.findall(source_line))
            == Counter(COMMAND_RE.findall(normalize_target(target_line))),
            f"line {line_number}: TeX command multiset changed",
        )
    require(len(COMMAND_RE.findall(source.text)) == 668, "source command census changed")
    require(len(COMMAND_RE.findall(candidate.text)) == 668, "candidate command census changed")

    source_inline = inline_math(source.text)
    target_inline = [
        (line, normalize_target(value)) for line, value in inline_math(candidate.text)
    ]
    require(len(source_inline) == len(target_inline) == 204, "inline-math census changed")
    require(source_inline == target_inline, "inline mathematics changed beyond declared correction")

    source_displays = bracket_displays(source.text)
    target_displays = [normalize_target(value) for value in bracket_displays(candidate.text)]
    require(len(source_displays) == len(target_displays) == 11, "bracket-display census changed")
    require(source_displays == target_displays, "display mathematics changed beyond localization/correction")


def gate_document_topology(source: Span, candidate: Span) -> None:
    source_events = environment_events(source.text)
    target_events = environment_events(candidate.text)
    audit_nesting(source_events, "source span")
    audit_nesting(target_events, "candidate")
    require(source_events == target_events, "ordered environment topology changed")
    require(len(source_events) == len(target_events) == 82, "environment event census changed")
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
    require("%" not in source.text and "%" not in candidate.text, "unexpected TeX comment")


def gate_diagrams_indexes_and_language(source: Span, candidate: Span) -> None:
    source_tikz = extract_environment(source.text, "tikzpicture")
    target_tikz = [normalize_target(value) for value in extract_environment(candidate.text, "tikzpicture")]
    require(len(source_tikz) == len(target_tikz) == 3, "tikzpicture census changed")
    require(source_tikz == target_tikz, "tikzpicture changed beyond localized node text")

    source_tikzcd = extract_environment(source.text, "tikzcd")
    target_tikzcd = [normalize_target(value) for value in extract_environment(candidate.text, "tikzcd")]
    require(len(source_tikzcd) == len(target_tikzcd) == 6, "tikzcd census changed")
    require(source_tikzcd == target_tikzcd, "tikzcd changed beyond localization/correction")

    for name, expected in (("align*", 3), ("gather*", 1), ("cases", 3)):
        source_blocks = extract_environment(source.text, name)
        target_blocks = [normalize_target(value) for value in extract_environment(candidate.text, name)]
        require(len(source_blocks) == len(target_blocks) == expected, f"{name} census changed")
        require(source_blocks == target_blocks, f"{name} mathematics changed")

    for pattern, expected, name in (
        (NODE_RE, 14, "node"),
        (PATH_RE, 0, "path"),
        (ARROW_RE, 21, "tikzcd arrow"),
        (EDGE_RE, 13, "TikZ edge"),
        (DRAW_RE, 11, "draw"),
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

    require(len(index_entries(source.text)) == 10, "source index census changed")
    require(index_entries(candidate.text) == EXPECTED_TARGET_INDEXES, "localized index topology changed")
    require(
        brace_audit(source.text) == brace_audit(candidate.text) == (0, 0, 288, 288),
        "brace topology changed",
    )
    require(han_count(source.text) == 1_655, "source Han census changed")
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
    gate_corrections(source, candidate)
    gate_commands_and_math(source, candidate)
    gate_document_topology(source, candidate)
    gate_diagrams_indexes_and_language(source, candidate)

    print(
        "\n".join(
            (
                "PASS Unit 022 isolated candidate checker",
                f"source full_lines=911 bytes={len(source_view.raw)} sha256={sha256(source_view.raw).hexdigest()}",
                f"source prefix=1-512 bytes={SOURCE_PREFIX_BYTES} sha256={SOURCE_PREFIX_SHA256}",
                f"source span=513-722 bytes={len(source.raw)} sha256={sha256(source.raw).hexdigest()}",
                f"source suffix=723-911 bytes={SOURCE_SUFFIX_BYTES} sha256={SOURCE_SUFFIX_SHA256}",
                f"candidate lines=210 bytes={len(candidate.raw)} sha256={sha256(candidate.raw).hexdigest()}",
                "boundary=start=enriched-categories included-blank=722 next=723-2-categories-excluded",
                "environments=41-pairs labels=11 refs=15 eqrefs=0 cites=2 items=17 indexes=10",
                "inline_math=204 bracket_displays=11 commands=668 braces=288/288 han=0",
                "tikzpicture=3 tikzcd=6 nodes=14 arrows=21 edges=13 draws=11",
                f"correction={CORRECTION_SET_PRODUCT_ID}-Hom-set-input-tensor-to-Cartesian-product",
                f"correction={CORRECTION_INJECTION_ID}-biproduct-injection-domain-X_1-to-X_i",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 022 isolated candidate checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
