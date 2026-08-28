#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U037 translation.

The checker binds the frozen Li authority, the complete special-rings section,
the Indonesian candidate, record-level TeX and protected mathematics,
identifiers, the geometric diagram, attribution-bearing theorem/proof/example
records, localized protected text and indexes, and one proven source repair.
It writes nothing.
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
    / "chapter5.tex"
)
CANDIDATE = (
    ROOT
    / "build"
    / "unit-037-candidate"
    / "chapter5-special-rings-id.tex"
)

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 174
SOURCE_END = 290
SLICE_RECORDS = 117
SLICE_BYTES = 10_243
SLICE_SHA256 = "8309a8125f04a87ab5fd9b1c04b197769e4ddcfbebe07d19523fbac4b3be1b05"

CANDIDATE_BYTES = 13_369
CANDIDATE_SHA256 = "9f6ea7b368133027c1a12efef74db48eed36c6db6662fe746b894a938a0825f5"
CANDIDATE_RECORDS = 117

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
    r"\\begin\{(align\*?|aligned|array|cases|equation\*?|gather\*?|gathered|"
    r"multline\*?|pmatrix|smallmatrix|tikzcd|tikzpicture)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    183: ((r"\text{项}", r"\text{suku}"),),
    243: ((r"\text{(Euler 函数)}", r"\text{(fungsi Euler)}"),),
    247: (
        (r"\text{素数}", r"\text{prima}"),
        (r"\text{素数}", r"\text{prima}"),
    ),
    250: (
        (
            r"\text{初等数论, 或 \eqref{eqn:Euler-phi-sum}}",
            r"\text{teori bilangan elementer, atau \eqref{eqn:Euler-phi-sum}}",
        ),
    ),
    254: (
        (
            r"(-1)^{(d \;\text{的素因子个数})}",
            r"(-1)^{(\text{banyaknya faktor prima dari }\; d)}",
        ),
        (
            r"\text{无 $1$ 之外的平方因子}",
            r"\text{tidak mempunyai faktor kuadrat selain $1$}",
        ),
    ),
    255: (
        (r"\text{有平方因子}", r"\text{mempunyai faktor kuadrat}"),
    ),
}

SOURCE_CORRECTIONS = {
    219: (
        r"x' \in R",
        r"x' \in D",
        "O013-LI-U037-COR-001",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{zhongxin@pusat}",
    r"\index{lingyinzi@pembagi nol (zero divisor)}",
    r"\index{tezheng@karakteristik (characteristic)}",
    r"\index{zhenghuan@daerah integral (integral domain)}",
    r"\index{chuhuan@gelanggang pembagian (division ring)}",
    r"\index{yu@medan (field)}",
    r"\index{suziyu@submedan prima (prime subfield)}",
    r"\index{Wedderburn@Teorema Kecil Wedderburn}",
    r"\index{fenyuanduoxiangshi@polinomial siklotomik (cyclotomic polynomial)}",
    r"\index{siyuanshu@kuaternion (quaternion)}",
    r"\index{moxinglun@teori model}",
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
    """Apply only declared protected-text localizations and source repair."""

    for source_fragment, target_fragment in PROTECTED_TEXT_REPLACEMENTS.get(
        absolute_line, ()
    ):
        if source_fragment not in text:
            fail(
                f"protected source fragment missing at authority line {absolute_line}: "
                f"{source_fragment!r}"
            )
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line in SOURCE_CORRECTIONS:
        source_fragment, target_fragment, correction_id = SOURCE_CORRECTIONS[absolute_line]
        if source_fragment not in text:
            fail(f"{correction_id} source defect drift at authority line {absolute_line}")
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
        fail("frozen chapter5.tex authority identity drift")
    source_lines = records(source_text)
    if len(source_lines) != SOURCE_RECORDS:
        fail(f"authority record count drift: {len(source_lines)}")

    expected_rights_header = (
        r"% LaTeX source for book ``代数学方法'' in Chinese",
        "% Copyright 2018  李文威 (Wen-Wei Li).",
        "% Permission is granted to copy, distribute and/or modify this",
        "% document under the terms of the Creative Commons",
        "% Attribution 4.0 International (CC BY 4.0)",
        "% http://creativecommons.org/licenses/by/4.0/",
    )
    if tuple(source_lines[:6]) != expected_rights_header:
        fail("frozen chapter-level attribution or CC BY 4.0 notice drift")

    source_slice_lines = source_lines[SOURCE_START - 1 : SOURCE_END]
    source_slice_text = "\n".join(source_slice_lines) + "\n"
    source_slice_data = source_slice_text.encode("utf-8")
    if len(source_slice_lines) != SLICE_RECORDS:
        fail("authority slice record count drift")
    if len(source_slice_data) != SLICE_BYTES or digest(source_slice_data) != SLICE_SHA256:
        fail("authority lines 174-290 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 173 must remain the blank section boundary")
    if source_slice_lines[0] != r"\section{几类特殊的环}":
        fail("authority special-rings section opening boundary drift")
    if source_slice_lines[-1] != r"\end{example}":
        fail("authority special-rings section closing boundary drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 291 must remain the blank inter-section boundary")
    if source_lines[SOURCE_END + 1] != r"\section{交换环初探}\label{sec:comm-ring-intro}":
        fail("authority next-section cursor drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")
    if candidate_lines[0] != r"\section{Beberapa Kelas Gelanggang Khusus}":
        fail("candidate special-rings section opening boundary drift")
    if candidate_lines[-1] != r"\end{example}":
        fail("candidate special-rings section closing boundary drift")

    if HAN_RE.search(candidate_text):
        fail("unauthorized Han residue in candidate")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("unauthorized Chinese punctuation residue in candidate")
    if "\u00ad" in candidate_text or "\u200b" in candidate_text or "\ufeff" in candidate_text:
        fail("invisible Unicode control residue in candidate")
    for character in candidate_text:
        if ord(character) < 32 and character not in "\n\t":
            fail(f"unauthorized control character U+{ord(character):04X}")
    if re.search(r"\b(?:TODO|TBD|FIXME|TRANSLATE)\b", candidate_text, re.IGNORECASE):
        fail("placeholder residue in candidate")
    if len(candidate_data) <= len(source_slice_data):
        fail("translation does not dominate the authority slice by byte extent")

    if ordered(ENV_RE, source_slice_text) != ordered(ENV_RE, candidate_text):
        fail("ordered begin/end environment topology drift")
    if ordered(LABEL_RE, source_slice_text) != ordered(LABEL_RE, candidate_text):
        fail("ordered label identifiers drift")
    if ordered(REF_RE, source_slice_text) != ordered(REF_RE, candidate_text):
        fail("ordered ref/eqref identifiers drift")
    if ordered(CITE_RE, source_slice_text) != ordered(CITE_RE, candidate_text):
        fail("ordered citation keys drift")
    if ordered(INDEX_STREAM_RE, source_slice_text) != ordered(
        INDEX_STREAM_RE, candidate_text
    ):
        fail("ordered index-stream topology drift")

    normalized_source_lines: list[str] = []
    for offset, (source_line, candidate_line) in enumerate(
        zip(source_slice_lines, candidate_lines, strict=True)
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
    if len(source_math) != 186:
        fail(f"protected mathematical-zone census drift: {len(source_math)}")

    expected_begins = {
        "align*": 1,
        "aligned": 1,
        "cases": 1,
        "definition": 3,
        "equation": 3,
        "example": 2,
        "gather*": 1,
        "itemize": 1,
        "proof": 2,
        "proposition": 1,
        "theorem": 1,
        "tikzpicture": 1,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 36:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 7:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 14:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 1:
        fail("citation count drift")
    if CITE_RE.findall(candidate_text) != ["Feng17"]:
        fail("Feng17 citation identity drift")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 15:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")

    if candidate_text.count(r"\begin{tikzpicture}[baseline=(O)]") != 1:
        fail("geometric diagram census or baseline drift")
    if len(re.findall(r"\\draw\b", candidate_text)) != 5:
        fail("diagram draw-command census drift")
    if len(re.findall(r"\\coordinate\b", candidate_text)) != 3:
        fail("diagram coordinate census drift")
    if len(re.findall(r"\\node\b", candidate_text)) != 3:
        fail("diagram node census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 4:
        fail("quaternion item census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 340:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 184 or candidate_text.count("}") != 184:
        fail("raw brace census drift")
    comment_records = [
        index
        for index, line in enumerate(candidate_lines, start=1)
        if line.lstrip().startswith("%")
    ]
    if comment_records:
        fail(f"source comment-state topology drift: {comment_records!r}")
    for environment in ("Exercises", "exercise", "hint", "solution"):
        if candidate_text.count(rf"\begin{{{environment}}}") != 0:
            fail(f"unexpected {environment} environment appeared")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 8:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        seen_targets: collections.Counter[str] = collections.Counter()
        for _, target_fragment in replacements:
            seen_targets[target_fragment] += 1
        for target_fragment, expected_count in seen_targets.items():
            if candidate_line.count(target_fragment) != expected_count:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    for absolute_line, (source_fragment, target_fragment, correction_id) in (
        SOURCE_CORRECTIONS.items()
    ):
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if candidate_line.count(target_fragment) != 1 or source_fragment in candidate_line:
            fail(f"{correction_id} repair drift at authority line {absolute_line}")
    if candidate_text.count(r"x' \in D") != 1:
        fail("O013-LI-U037-COR-001 corrected ambient-ring census drift")

    required_anchors = (
        "Beberapa Kelas Gelanggang Khusus",
        "sentralisator",
        "pusat",
        "pembagi nol kiri",
        "pembagi nol kanan",
        "karakteristik",
        "daerah integral",
        "gelanggang pembagian",
        "submedan prima",
        "Teorema Kecil Wedderburn",
        "aksi konjugasi",
        "polinomial siklotomik",
        "fungsi Möbius",
        "prinsip inklusi-eksklusi",
        "aljabar kuaternion",
        "medan real formal",
        "teori model",
    )
    candidate_casefold = candidate_text.casefold()
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    forbidden_terms = (
        "cincin",
        "lapangan",
        "kelompok",
        "subring",
        "ring kuosien",
        "ideal bilateral",
    )
    for forbidden_term in forbidden_terms:
        if forbidden_term.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian terminology appeared: {forbidden_term!r}")

    if candidate_text.count("E.\\ Witt") != 1:
        fail("E. Witt proof attribution drift")
    if candidate_text.count("W.\\ Hamilton") != 1:
        fail("W. Hamilton attribution drift")

    print("PASS: O013-LI-U037 isolated complete Section 5.2 special rings")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 36 environment markers, 7 labels, 14 references, "
        f"1 citation, 15 indexes, {len(source_math)} protected math zones, "
        "1 tikzpicture / 5 draws / 3 coordinates / 3 nodes"
    )
    print(
        "content: 4 items, 0 exercises/hints/solutions, 0 comment records; "
        "8 protected-text localizations; 11 localized indexes; "
        "1 proven source correction"
    )
    print("rights: frozen Chapter 5 CC BY 4.0 notice and Wen-Wei Li attribution bound")
    print("next source cursor: chapter5.tex line 292")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
