#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U038 translation.

The checker is read-only. It binds the frozen Chapter 5 authority and rights
header, the complete commutative-rings/localization section, the Indonesian
candidate, record-level TeX topology, protected mathematics, identifiers,
diagram primitives, controlled terminology, six localized mathematical-text
fragments, localized indexes, and two separately proven source corrections.
"""

from __future__ import annotations

import collections
import csv
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
    / "unit-038-candidate"
    / "chapter5-commutative-rings-localization-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 292
SOURCE_END = 461
SLICE_RECORDS = 170
SLICE_BYTES = 13_040
SLICE_SHA256 = "742556293c463c59fc9dfd06b328e70f337a367e5cd739fb3ccd940793565955"

CANDIDATE_BYTES = 16_799
CANDIDATE_SHA256 = "e48edae4d77c5be8206f8e18b0d4c71c307444830594295a338cbf8313d03607"
CANDIDATE_RECORDS = 170

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
    333: (
        (r"\text{理想}", r"\text{ideal}"),
        (r"\text{理想}", r"\text{ideal}"),
    ),
    427: (
        (r"I: R \text{ 的理想}", r"I: \text{ideal dari } R"),
        (
            r"J: R[S^{-1}] \text{ 的理想}",
            r"J: \text{ideal dari } R[S^{-1}]",
        ),
    ),
    449: ((r"\text{或}", r"\text{atau}"),),
    451: (
        (
            r"\text{引理 \ref{prop:Spec-pullback}}",
            r"\text{Lema \ref{prop:Spec-pullback}}",
        ),
    ),
}

SOURCE_MATH_CORRECTIONS = {
    416: (
        r"\text{Frac}(R)",
        r"\text{Frac}(\Z)",
        "O013-LI-U038-COR-002",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{lixiang!ideal prima (prime ideal)}",
    r"\index{lixiang!ideal maksimal (maximal ideal)}",
    r"\index[sym1]{Spec@$\Spec$}",
    r"\index[sym1]{MaxSpec@$\MaxSpec$}",
    r"\index{zhulixianghuan@daerah ideal utama (principal ideal domain)}",
    r"\index{chengxingziji@himpunan bagian multiplikatif (multiplicative subset)}",
    r"\index{jubuhua@lokalisasi (localization)}",
    r"\index[sym1]{$R[S^{-1}]$}",
    r"\index{fenshiyu@medan pecahan (field of fractions)}",
    r"\index[sym1]{Frac(R)@$\text{Frac}(R)$}",
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
    """Apply only enumerated protected-text localizations and math correction."""

    for source_fragment, target_fragment in PROTECTED_TEXT_REPLACEMENTS.get(
        absolute_line, ()
    ):
        if source_fragment not in text:
            fail(
                f"protected source fragment missing at authority line {absolute_line}: "
                f"{source_fragment!r}"
            )
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line in SOURCE_MATH_CORRECTIONS:
        source_fragment, target_fragment, correction_id = SOURCE_MATH_CORRECTIONS[
            absolute_line
        ]
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
        line.lstrip().startswith("%"),
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
        "% LaTeX source for book \x60\x60代数学方法'' in Chinese",
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
        fail("authority lines 292-461 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 291 must remain the blank opening boundary")
    if source_slice_lines[0] != (
        r"\section{交换环初探}\label{sec:comm-ring-intro}"
    ):
        fail("authority commutative-rings section opening drift")
    if source_slice_lines[-1] != r"\end{example}":
        fail("authority commutative-rings section closing drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 462 must remain the blank closing boundary")
    if source_lines[SOURCE_END + 1] != (
        r"\section{间奏: Möbius 反演}\label{sec:Mobius}"
    ):
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
    if candidate_lines[0] != (
        r"\section{Tinjauan Awal tentang Gelanggang Komutatif}"
        r"\label{sec:comm-ring-intro}"
    ):
        fail("candidate section opening boundary drift")
    if candidate_lines[-1] != r"\end{example}":
        fail("candidate section closing boundary drift")

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
        if structural_signature(normalized_source_line) != structural_signature(
            candidate_line
        ):
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
    if len(source_math) != 247:
        fail(f"protected mathematical-zone census drift: {len(source_math)}")

    expected_begins = {
        "align*": 3,
        "compactitem": 1,
        "corollary": 1,
        "definition": 3,
        "enumerate": 2,
        "example": 2,
        "gather": 2,
        "gather*": 1,
        "lemma": 3,
        "proof": 6,
        "proposition": 4,
        "remark": 1,
        "tikzcd": 2,
        "tikzpicture": 2,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 66:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 12:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 15:
        fail("reference count drift")
    if CITE_RE.findall(candidate_text):
        fail("unexpected citation appeared")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 10:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")

    if candidate_text.count(r"\begin{tikzcd}") != 2:
        fail("tikzcd census drift")
    if candidate_text.count(r"\begin{tikzpicture}") != 2:
        fail("tikzpicture census drift")
    if len(re.findall(r"\\arrow\b", candidate_text)) != 5:
        fail("diagram arrow-command census drift")
    if len(re.findall(r"\\draw\b", candidate_text)) != 2:
        fail("diagram draw-command census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 8:
        fail("item census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 452:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 246 or candidate_text.count("}") != 246:
        fail("raw brace census drift")

    source_comments = [
        index
        for index, line in enumerate(source_slice_lines, start=SOURCE_START)
        if line.lstrip().startswith("%")
    ]
    candidate_comments = [
        index
        for index, line in enumerate(candidate_lines, start=1)
        if line.lstrip().startswith("%")
    ]
    if source_comments or candidate_comments:
        fail(
            "comment-state topology drift: "
            f"source={source_comments!r}, candidate={candidate_comments!r}"
        )
    for environment in ("Exercises", "exercise", "hint", "solution"):
        if candidate_text.count(rf"\begin{{{environment}}}") != 0:
            fail(f"unexpected {environment} environment appeared")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 6:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        targets = collections.Counter(target for _, target in replacements)
        for target_fragment, expected_count in targets.items():
            if candidate_line.count(target_fragment) != expected_count:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    if (
        "asalkan gelanggang ini bukan gelanggang nol"
        not in candidate_lines[355 - SOURCE_START]
    ):
        fail("O013-LI-U038-COR-001 zero-ring qualification missing")
    for absolute_line, (source_fragment, target_fragment, correction_id) in (
        SOURCE_MATH_CORRECTIONS.items()
    ):
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if candidate_line.count(target_fragment) != 1 or source_fragment in candidate_line:
            fail(f"{correction_id} repair drift at authority line {absolute_line}")

    required_terminology = {
        "ring": "gelanggang",
        "field": "medan",
        "quotient set": "himpunan hasil bagi",
        "partially ordered set": "himpunan terurut parsial (poset)",
        "chain": "rantai",
        "Zorn's lemma": "lema Zorn",
        "bijection": "bijeksi",
        "functor": "fungtor",
        "unital ring": "gelanggang dengan unsur satuan",
        "surjective": "surjektif",
        "identity element": "unsur identitas",
    }
    with TERMINOLOGY.open("r", encoding="utf-8-sig", newline="") as handle:
        admitted = {
            row["source_term"]: row["target_term"]
            for row in csv.DictReader(handle)
            if row.get("status") == "admitted"
        }
    candidate_casefold = candidate_text.casefold()
    for source_term, target_term in required_terminology.items():
        if admitted.get(source_term) != target_term:
            fail(f"controlled terminology drift: {source_term!r}")
        if target_term.casefold() not in candidate_casefold:
            fail(f"controlled target term absent: {target_term!r}")

    required_anchors = (
        "Tinjauan Awal tentang Gelanggang Komutatif",
        "ideal sejati",
        "ideal prima",
        "ideal maksimal",
        "spektrum prima",
        "spektrum ideal maksimal",
        "ideal dua sisi",
        "daerah integral",
        "daerah ideal utama",
        "himpunan bagian multiplikatif",
        "lokalisasi",
        "sifat universal",
        "pembagi nol",
        "gelanggang pecahan total",
        "medan pecahan",
        "prabayangan",
    )
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    forbidden_terms = (
        "cincin",
        "lapangan",
        "kelompok",
        "funktor",
        "ideal bilateral",
        "ring kuosien",
    )
    for forbidden_term in forbidden_terms:
        if forbidden_term.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian terminology appeared: {forbidden_term!r}")

    print("PASS: O013-LI-U038 isolated complete Section 5.3 commutative rings")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 66 environment markers, 12 labels, 15 references, "
        f"0 citations, 10 indexes, {len(source_math)} protected math zones"
    )
    print(
        "diagrams/content: 2 tikzcd / 5 arrows; 2 tikzpicture / 2 draws; "
        "8 items; 0 exercises/hints/solutions/comments"
    )
    print(
        "localization/corrections: 6 protected-text localizations; "
        "6 localized index displays plus 4 preserved symbol indexes; "
        "2 proven source corrections"
    )
    print("rights: frozen Chapter 5 CC BY 4.0 notice and author attribution bound")
    print("next source cursor: chapter5.tex line 463")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
