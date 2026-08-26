#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U033 translation.

The checker binds the frozen Li authority, the complete Section 4.9 boundary,
the Indonesian candidate, record-level TeX and protected mathematics,
identifiers, diagrams, localized protected text, localized index entries, and
two declared source corrections. It performs no writes.
"""

from __future__ import annotations

import collections
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter4.tex"
)
CANDIDATE = (
    ROOT
    / "build"
    / "unit-033-candidate"
    / "chapter4-symmetric-groups-id.tex"
)

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 1_389
SOURCE_END = 1_608
SLICE_RECORDS = 220
SLICE_BYTES = 19_076
SLICE_SHA256 = "c86fdd5bf99aec013ea42ca0042242066c12a8ed7133dd735a3f237446712b4a"

CANDIDATE_BYTES = 23_099
CANDIDATE_SHA256 = "1abae4c95d52e98c6c2375c5394bd4a7f5d4319ef018849ae10c4c0ac6598d76"
CANDIDATE_RECORDS = 219

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CHINESE_PUNCT_RE = re.compile(
    r"[\uFF0C\u3002\uFF1B\uFF1A\uFF1F\uFF01\u300A\u300B"
    r"\u300C\u300D\u300E\u300F\u3001]"
)
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(eqref|ref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
INDEX_STREAM_RE = re.compile(r"\\index(?:\[([^\]]+)\])?\{")
COMMAND_RE = re.compile(r"\\[A-Za-z@]+|\\.")
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
MATH_ENV_RE = re.compile(
    r"\\begin\{(array|cases|equation\*?|gather\*?|gathered|"
    r"multline\*?|pmatrix|tikzcd|tikzpicture)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    1454: (
        (r"\text{商同态}", r"\text{homomorfisme hasil bagi}"),
    ),
    1460: (
        (r"\text{$3$-循环}", r"\text{$3$-siklus}"),
        (r"\text{恰有一元素}", r"\text{tepat satu unsur}"),
    ),
    1510: (
        (r"\text{拉直}", r"\text{diluruskan}"),
    ),
    1580: (
        (r"\text{满足于}", r"\text{memenuhi}"),
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{duichengqun@grup simetris (symmetric group)}",
    r"\index{xunhuan@siklus (cycle)}",
    r"\index{duihuan@transposisi (transposition)}",
    r"\index[sym1]{S_n@$\mathfrak{S}_n$}",
    r"\index{fenchai@partisi (partition)}",
    r"\index[sym1]{sgn@$\sgn$}",
    r"\index[sym1]{A_n@$\mathfrak{A}_n$}",
    r"\index{kejiequn@grup solvabel (solvable group)}",
    r"\index{grup Coxeter (Coxeter group)}",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        fail(f"UTF-8 BOM is forbidden: {path}")
    if b"\r" in data:
        fail(f"CR/CRLF line endings are forbidden: {path}")
    try:
        return data, data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(f"strict UTF-8 decode failed for {path}: {exc}")


def records(text: str) -> list[str]:
    result = text.split("\n")
    if result and result[-1] == "":
        result.pop()
    return result


def ordered(regex: re.Pattern[str], text: str) -> list[tuple[str, ...] | str]:
    result: list[tuple[str, ...] | str] = []
    for match in regex.finditer(text):
        groups = match.groups()
        result.append(groups if len(groups) > 1 else groups[0])
    return result


def normalize_authority_line(text: str, absolute_line: int) -> str:
    """Apply only declared protected-text localizations and source repairs."""

    for source_fragment, target_fragment in PROTECTED_TEXT_REPLACEMENTS.get(
        absolute_line, ()
    ):
        if source_fragment not in text:
            fail(
                f"protected source fragment missing at authority line {absolute_line}: "
                f"{source_fragment!r}"
            )
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line == 1580:
        source_fragment = r"\tilde{\tau}_1, \ldots, \tilde{\tau}_n"
        target_fragment = r"\tilde{\tau}_1, \ldots, \tilde{\tau}_{n-1}"
        if source_fragment not in text:
            fail("generator-endpoint source defect drift at authority line 1580")
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line == 1591:
        source_fragment = r"$\mathfrak{S}'_n \leq n |\mathfrak{S}'_{n-1}|"
        target_fragment = r"$|\mathfrak{S}'_n| \leq n |\mathfrak{S}'_{n-1}|"
        if source_fragment not in text:
            fail("cardinality-bar source defect drift at authority line 1591")
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line == 1495:
        source_fragment = (
            r"$\mathscr{D}^1 \mathfrak{A}_4 = \left\{\identity, (1 2)(3 4), "
            r"(1 3) (2 4), (1 4)(2 3)\right\}$"
        )
        target_fragment = (
            r"\[ \mathscr{D}^1 \mathfrak{A}_4 = \left\{\identity, (1 2)(3 4), "
            r"(1 3) (2 4), (1 4)(2 3)\right\} , \]"
        )
        if source_fragment not in text:
            fail("digital-reflow source anchor drift at authority line 1495")
        text = text.replace(source_fragment, target_fragment, 1)

    return text


def structural_signature(line: str) -> tuple[object, ...]:
    return (
        tuple(ENV_RE.findall(line)),
        tuple(LABEL_RE.findall(line)),
        tuple(REF_RE.findall(line)),
        tuple(CITE_RE.findall(line)),
        tuple(stream or "main" for stream in INDEX_STREAM_RE.findall(line)),
        line.count(r"\["),
        line.count(r"\]"),
        len(re.findall(r"(?<!\\)\$", line)),
        line.count("&"),
        line.count(r"\\"),
    )


def normalize_math(text: str) -> str:
    return re.sub(r"\s+", "", text)


def math_zones(text: str) -> list[str]:
    spans: list[tuple[int, str]] = []
    for regex in (INLINE_MATH_RE, DISPLAY_MATH_RE, MATH_ENV_RE):
        for match in regex.finditer(text):
            content = match.group(2) if regex is MATH_ENV_RE else match.group(1)
            spans.append((match.start(), normalize_math(content)))
    return [content for _, content in sorted(spans)]


def main() -> int:
    source_data, source_text = strict_text(SOURCE)
    candidate_data, candidate_text = strict_text(CANDIDATE)

    if len(source_data) != SOURCE_BYTES or digest(source_data) != SOURCE_SHA256:
        fail("frozen chapter4.tex authority identity drift")
    source_lines = records(source_text)
    if len(source_lines) != SOURCE_RECORDS:
        fail(f"authority record count drift: {len(source_lines)}")

    source_slice_lines = source_lines[SOURCE_START - 1 : SOURCE_END]
    source_slice_text = "\n".join(source_slice_lines) + "\n"
    source_slice_data = source_slice_text.encode("utf-8")
    if len(source_slice_lines) != SLICE_RECORDS:
        fail("authority slice record count drift")
    if len(source_slice_data) != SLICE_BYTES or digest(source_slice_data) != SLICE_SHA256:
        fail("authority lines 1389-1608 identity drift")
    if source_slice_lines[-1] != "":
        fail("authority line 1608 must remain the blank section boundary")
    if source_lines[SOURCE_END] != r"\section{群的极限和完备化}\label{sec:group-limit}":
        fail("next boundary at authority line 1609 drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")
    if candidate_lines[0] != r"\section{Grup Simetris}\label{sec:symmetric-group}":
        fail("candidate opening boundary drift")
    if not candidate_lines[-1].endswith(r"\index{grup Coxeter (Coxeter group)}"):
        fail("candidate closing boundary drift")
    if r"\section{Limit dan Kelengkapan Grup}" in candidate_text:
        fail("Section 4.10 crossed into isolated candidate")

    if HAN_RE.search(candidate_text):
        fail("unauthorized Han residue in candidate")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("unauthorized Chinese punctuation residue in candidate")
    if "\u200b" in candidate_text or "\ufeff" in candidate_text:
        fail("invisible Unicode control residue in candidate")
    for character in candidate_text:
        if ord(character) < 32 and character not in "\n\t":
            fail(f"unauthorized control character U+{ord(character):04X}")
    if re.search(r"\b(?:TODO|TBD|FIXME|TRANSLATE)\b", candidate_text, re.IGNORECASE):
        fail("placeholder residue in candidate")
    if len(candidate_data) <= len(source_slice_data):
        fail("translation does not dominate the authority slice by byte extent")

    substantive_source_lines = source_slice_lines[:-1]
    substantive_source_text = "\n".join(substantive_source_lines) + "\n"
    if ordered(ENV_RE, substantive_source_text) != ordered(ENV_RE, candidate_text):
        fail("ordered begin/end environment topology drift")
    if ordered(LABEL_RE, substantive_source_text) != ordered(LABEL_RE, candidate_text):
        fail("ordered label identifiers drift")
    if ordered(REF_RE, substantive_source_text) != ordered(REF_RE, candidate_text):
        fail("ordered ref/eqref identifiers drift")
    if ordered(CITE_RE, substantive_source_text) != ordered(CITE_RE, candidate_text):
        fail("ordered citation keys drift")
    if ordered(INDEX_STREAM_RE, substantive_source_text) != ordered(
        INDEX_STREAM_RE, candidate_text
    ):
        fail("ordered index-stream topology drift")

    normalized_source_lines: list[str] = []
    for offset, (source_line, candidate_line) in enumerate(
        zip(substantive_source_lines, candidate_lines, strict=True)
    ):
        absolute_line = SOURCE_START + offset
        normalized_source_line = normalize_authority_line(source_line, absolute_line)
        normalized_source_lines.append(normalized_source_line)
        if structural_signature(normalized_source_line) != structural_signature(candidate_line):
            fail(f"per-record TeX topology drift at authority line {absolute_line}")
        if COMMAND_RE.findall(normalized_source_line) != COMMAND_RE.findall(candidate_line):
            fail(f"ordered TeX command drift at authority line {absolute_line}")

    normalized_source_text = "\n".join(normalized_source_lines) + "\n"
    source_math = math_zones(normalized_source_text)
    candidate_math = math_zones(candidate_text)
    if source_math != candidate_math:
        if len(source_math) != len(candidate_math):
            fail(
                "protected mathematical-zone count drift: "
                f"{len(source_math)} != {len(candidate_math)}"
            )
        mismatch = next(
            index
            for index, (source_zone, candidate_zone) in enumerate(
                zip(source_math, candidate_math, strict=True), start=1
            )
            if source_zone != candidate_zone
        )
        fail(f"protected mathematical zone {mismatch} drift")

    expected_begins = {
        "array": 1,
        "cases": 1,
        "center": 4,
        "compactitem": 1,
        "corollary": 1,
        "definition": 2,
        "equation": 3,
        "gather*": 2,
        "gathered": 1,
        "inparaenum": 1,
        "itemize": 1,
        "lemma": 3,
        "proof": 7,
        "proposition": 1,
        "theorem": 2,
        "tikzcd": 1,
        "tikzpicture": 11,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 86:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 10:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 20:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 0:
        fail("citation count drift")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 9:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")
    if candidate_text.count(r"\begin{tikzcd}") != 1:
        fail("tikzcd census drift")
    if candidate_text.count(r"\begin{tikzpicture}") != 11:
        fail("tikzpicture census drift")
    if len(re.findall(r"\\arrow", candidate_text)) != 4:
        fail("diagram-arrow census drift")
    if len(re.findall(r"\\braid", candidate_text)) != 9:
        fail("braid-command census drift")
    if len(re.findall(r"\\draw", candidate_text)) != 3:
        fail("draw-command census drift")
    if len(re.findall(r"\\node", candidate_text)) != 10:
        fail("node-command census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 554:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 476 or candidate_text.count("}") != 476:
        fail("raw brace census drift")
    if re.search(r"\\begin\{(?:exercise|hint|solution)\}", candidate_text):
        fail("out-of-scope exercise, hint or solution environment appeared")
    if any(line.lstrip().startswith("%") for line in candidate_lines):
        fail("source-disabled/comment topology appeared in candidate")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 5:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        for _, target_fragment in replacements:
            if candidate_line.count(target_fragment) != 1:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    line_1580 = candidate_lines[1580 - SOURCE_START]
    corrected_generators = r"\tilde{\tau}_1, \ldots, \tilde{\tau}_{n-1}"
    defective_generators = r"\tilde{\tau}_1, \ldots, \tilde{\tau}_n"
    if corrected_generators not in line_1580 or defective_generators in line_1580:
        fail("O013-LI-U033-COR-001 generator-endpoint repair drift")
    line_1591 = candidate_lines[1591 - SOURCE_START]
    corrected_bound = r"|\mathfrak{S}'_n| \leq n |\mathfrak{S}'_{n-1}|"
    defective_bound = r"$\mathfrak{S}'_n \leq n |\mathfrak{S}'_{n-1}|"
    if corrected_bound not in line_1591 or defective_bound in line_1591:
        fail("O013-LI-U033-COR-002 cardinality-bar repair drift")

    required_anchors = (
        "grup simetris",
        "Dekomposisi siklus",
        "tipe siklus",
        "kelipatan persekutuan terkecil",
        "grup selang-seling",
        "permutasi genap",
        "subgrup turunan",
        "homomorfisme hasil bagi",
        "grup sederhana nonabelian",
        "tidak solvabel",
        "grup kepang",
        "persamaan Yang--Baxter",
        "presentasi grup",
        "grup Coxeter",
        "teori representasi",
    )
    candidate_casefold = candidate_text.casefold()
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    if "antarkelompok" in candidate_text or "grup alternatif" in candidate_text:
        fail("uncontrolled Indonesian group terminology appeared")
    if "unsur satuan" in candidate_text:
        fail("pre-glossary identity-element synonym remains in candidate")
    if candidate_text.count("unsur identitas") != 2:
        fail("identity-element terminology census drift")
    if (
        "Karena setiap $1$-siklus merupakan unsur identitas, semua siklus "
        "panjang satu itu boleh dihilangkan dari hasil kali."
    ) not in candidate_text:
        fail("1-cycle identity clarification drift")
    if r"\allowbreak" in candidate_text:
        fail("superseded inline reflow command remains")
    if (
        r"\[ \mathscr{D}^1 \mathfrak{A}_4 = \left\{\identity, (1 2)(3 4), "
        r"(1 3) (2 4), (1 4)(2 3)\right\} , \]"
    ) not in candidate_lines[1495 - SOURCE_START]:
        fail("O013-LI-U033-REFLOW-001 drift")

    print("PASS: O013-LI-U033 isolated complete Section 4.9 candidate")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 86 environment markers, 10 labels, 20 references, "
        f"0 citations, 9 indexes, {len(source_math)} protected math zones, "
        f"12 diagrams / 4 arrows / 9 braid commands"
    )
    print(
        "content: 0 exercises, 0 hints, 0 solutions, 0 Han residue; "
        "5 protected-text localizations; 9 localized indexes; "
        "2 declared source corrections"
    )
    print("declared_digital_reflows=1")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
