#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U035 translation.

The checker binds the frozen Li authority, the complete Section 4.11 and
Chapter 4 exercise boundary, the Indonesian candidate, record-level TeX and
protected mathematics, identifiers, diagrams, exercises/hints, localized
protected text and indexes, and one declared source correction. It writes
nothing.
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
    / "unit-035-candidate"
    / "chapter4-groups-in-categories-and-exercises-id.tex"
)

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 1_745
SOURCE_END = 1_898
SLICE_RECORDS = 154
SLICE_BYTES = 14_398
SLICE_SHA256 = "f841860520d4ab35dc82354f288bc295c4681f9faffc8f5a645c92a3af1dd287"

CANDIDATE_BYTES = 18_089
CANDIDATE_SHA256 = "5d9bf6e5c9c17c83821f1bba63078f4d28e3836428f4557e0727ee5b1046c2ca"
CANDIDATE_RECORDS = 154

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
    r"\\begin\{(align\*?|array|cases|equation\*?|gather\*?|gathered|"
    r"multline\*?|pmatrix|tikzcd|tikzpicture)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    1788: ((r"\text{置换}", r"\text{permutasi}"),),
    1805: ((r"\text{忘却函子}", r"\text{fungtor pelupa}"),),
    1810: (
        (r"\text{资料}", r"\text{data}"),
        (r"\text{自然}", r"\text{natural}"),
    ),
    1811: (
        (r"\text{资料}", r"\text{data}"),
        (r"\text{自然}", r"\text{natural}"),
    ),
    1812: ((r"\text{群同态}", r"\text{homomorfisme grup}"),),
    1813: ((r"\text{群对象}", r"\text{objek grup}"),),
    1822: (
        (r"\text{的群对象}", r"\text{: objek grup}"),
        (r"\text{中的群函子}", r"\text{: fungtor grup}"),
    ),
    1866: (
        (r"\text{有限子集}", r"\text{himpunan bagian berhingga}"),
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{duixiang!objek grup (group object)}",
    r"\index{zitonggou!automorfisme luar (outer automorphism)}",
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

    if absolute_line == 1858:
        source_fragment = r"\substack{1 \leq i \leq m \\ 1 \leq j \leq n}"
        target_fragment = r"\substack{1 \leq i \leq n \\ 1 \leq j \leq m}"
        if source_fragment not in text:
            fail("Neumann-lemma index-bound source defect drift at authority line 1858")
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
        fail("authority lines 1745-1898 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 1744 must remain the blank section boundary")
    if source_slice_lines[0] != r"\section{范畴中的群}\label{sec:group-in-cat}":
        fail("authority Section 4.11 opening boundary drift")
    if source_slice_lines[-1] != r"\end{Exercises}":
        fail("authority Chapter 4 closing boundary drift")
    if SOURCE_END != len(source_lines):
        fail("authority unexpectedly continues beyond the selected chapter boundary")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")
    if candidate_lines[0] != r"\section{Grup dalam Kategori}\label{sec:group-in-cat}":
        fail("candidate opening boundary drift")
    if candidate_lines[-1] != r"\end{Exercises}":
        fail("candidate closing boundary drift")

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

    expected_begins = {
        "Exercises": 1,
        "align*": 1,
        "array": 3,
        "compactenum": 3,
        "compactitem": 1,
        "definition": 2,
        "description": 1,
        "example": 1,
        "hint": 5,
        "inparaenum": 1,
        "lemma": 1,
        "proof": 1,
        "remark": 1,
        "tikzcd": 8,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 60:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 3:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 15:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 0:
        fail("citation count drift")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 2:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")
    if candidate_text.count(r"\begin{tikzcd}") != 8:
        fail("tikzcd census drift")
    if len(re.findall(r"\\arrow", candidate_text)) != 35:
        fail("diagram-arrow census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 41:
        fail("all-item census drift")

    exercise_body = candidate_text.split(r"\begin{Exercises}", 1)[1].split(
        r"\end{Exercises}", 1
    )[0]
    top_level_exercises = sum(
        1 for line in exercise_body.splitlines() if re.match(r"^\t\\item\b", line)
    )
    if top_level_exercises != 26:
        fail("top-level Chapter 4 exercise census drift")
    if len(re.findall(r"\\item\b", exercise_body)) != 36:
        fail("Chapter 4 exercise/subitem census drift")
    if exercise_body.count(r"\begin{hint}") != 5:
        fail("hint census drift")
    if re.search(r"\\begin\{solution\}", candidate_text):
        fail("source-absent solution environment appeared")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 452:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 246 or candidate_text.count("}") != 243:
        fail("raw brace census drift")
    commented_lines = [line for line in candidate_lines if "%" in line]
    if len(commented_lines) != 2 or not all("%" in line for line in commented_lines):
        fail("source comment topology drift")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 11:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        for _, target_fragment in replacements:
            if candidate_line.count(target_fragment) != 1:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    line_1858 = candidate_lines[1858 - SOURCE_START]
    corrected_bounds = r"\substack{1 \leq i \leq n \\ 1 \leq j \leq m}"
    defective_bounds = r"\substack{1 \leq i \leq m \\ 1 \leq j \leq n}"
    if corrected_bounds not in line_1858 or defective_bounds in line_1858:
        fail("O013-LI-U035-COR-001 Neumann-lemma index-bound repair drift")

    required_anchors = (
        "Grup dalam Kategori",
        "objek grup",
        "produk berhingga",
        "kendala asosiativitas produk",
        "fungtor grup",
        "pembenaman Yoneda",
        "fungtor penuh dan setia",
        "representabel",
        "torsor formal",
        "grup automorfisme luar",
        "Lema Neumann",
        "produk semilangsung",
        "ekstensi terpecah",
        "produk terbatas",
        "jumlah langsung",
        "$2$-transitif",
        "koset ganda",
        "Teorema Wilson",
        "Lema Ping-Pong",
        "homomorfisme kontinu",
    )
    candidate_casefold = candidate_text.casefold()
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    forbidden_terms = ("funktor", "obyek", "grup objek", "kelompok")
    for forbidden_term in forbidden_terms:
        if forbidden_term.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian terminology appeared: {forbidden_term!r}")

    print("PASS: O013-LI-U035 isolated Section 4.11 + complete Chapter 4 exercises")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 60 environment markers, 3 labels, 15 references, "
        f"0 citations, 2 indexes, {len(source_math)} protected math zones, "
        "8 diagrams / 35 arrows"
    )
    print(
        "content: 26 top-level exercises, 36 exercise/subitems, 5 hints, "
        "0 solutions, 0 Han residue; 11 protected-text localizations; "
        "2 localized indexes; 1 declared source correction"
    )
    print("next source cursor: chapter5.tex line 1")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
