#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U036 translation.

The checker binds the frozen Li authority, the Chapter 5 opening and complete
first-section boundary, the Indonesian candidate, record-level TeX and
protected mathematics, identifiers, diagrams, comments, rights attribution,
localized protected text and indexes, and exactly two proven source repairs.
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
    / "unit-036-candidate"
    / "chapter5-ring-basics-id.tex"
)

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 1
SOURCE_END = 172
SLICE_RECORDS = 172
SLICE_BYTES = 13_758
SLICE_SHA256 = "84b70368ebdfa557fa76eb229166aa6851b3295f620b240cc080f419ef40c14f"

CANDIDATE_BYTES = 18_181
CANDIDATE_SHA256 = "d93ad6adeccae67ace0035286e9a41ab1350dca875acdb349d529c7f180b991a"
CANDIDATE_RECORDS = 172

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
    148: (
        (r"R_2 \text{的双边理想}", r"\text{ideal dua sisi di } R_2"),
        (r"R_1 \text{的双边理想}", r"\text{ideal dua sisi di } R_1"),
    ),
    158: (
        (r"\text{双边理想}", r"\text{ideal dua sisi}"),
        (r"\text{双边理想}", r"\text{ideal dua sisi}"),
    ),
}

SOURCE_CORRECTIONS = {
    143: (
        r"\bar{\varphi}: (R/I) \to \Image(\varphi)",
        r"\bar{\varphi}: R/\Ker(\varphi) \to \Image(\varphi)",
        "O013-LI-U036-COR-001",
    ),
    168: (
        r"\theta: S/I \cap S \to (S+I)/I",
        r"\theta: S/(I \cap S) \to (S+I)/I",
        "O013-LI-U036-COR-002",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{huan@gelanggang (ring)}",
    r"\index{yaoyuan@unsur satuan}",
    r"\index[sym1]{$R^\times$}",
    r"\index{xiangfanhuan@gelanggang lawan (opposite ring)}",
    r"\index{jiaohuan@gelanggang komutatif}",
    r"\index{tongtai@homomorfisme gelanggang}",
    r"\index{he@kernel}",
    r"\index[sym1]{$M_n(R)$}",
    r"\index{zitongtaihuan@gelanggang endomorfisme}",
    r"\index{lixiang@ideal (ideal)}",
    r"\index{shang@gelanggang hasil bagi}",
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

    source_slice_lines = source_lines[SOURCE_START - 1 : SOURCE_END]
    source_slice_text = "\n".join(source_slice_lines) + "\n"
    source_slice_data = source_slice_text.encode("utf-8")
    if len(source_slice_lines) != SLICE_RECORDS:
        fail("authority slice record count drift")
    if len(source_slice_data) != SLICE_BYTES or digest(source_slice_data) != SLICE_SHA256:
        fail("authority lines 1-172 identity drift")
    if source_slice_lines[0] != r"% LaTeX source for book ``代数学方法'' in Chinese":
        fail("authority Chapter 5 copyright-header opening boundary drift")
    if source_slice_lines[8] != r"\chapter{环论初步}\label{sec:ring}":
        fail("authority Chapter 5 opening boundary drift")
    if source_slice_lines[21] != r"\section{基本概念}\label{sec:ring-basics}":
        fail("authority first-section opening boundary drift")
    if source_slice_lines[-1] != r"和左理想或右理想相关的构造将在模论部分统一处理.":
        fail("authority first-section closing boundary drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 173 must remain the blank inter-section boundary")
    if source_lines[SOURCE_END + 1] != r"\section{几类特殊的环}":
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
    if candidate_lines[0] != r"% Indonesian LaTeX source for book ``Methods in Algebra''":
        fail("candidate rights-header opening drift")
    if candidate_lines[8] != r"\chapter{Pengantar Teori Gelanggang}\label{sec:ring}":
        fail("candidate Chapter 5 opening boundary drift")
    if candidate_lines[21] != r"\section{Konsep Dasar}\label{sec:ring-basics}":
        fail("candidate first-section opening boundary drift")
    if candidate_lines[-1] != (
        "Konstruksi-konstruksi yang berkaitan dengan ideal kiri atau ideal kanan "
        "akan ditangani secara terpadu dalam pembahasan teori modul."
    ):
        fail("candidate first-section closing boundary drift")

    required_rights_header = (
        r"% Indonesian LaTeX source for book ``Methods in Algebra''",
        "% Copyright 2018  李文威 (Wen-Wei Li).",
        "% Permission is granted to copy, distribute and/or modify this",
        "% document under the terms of the Creative Commons",
        "% Attribution 4.0 International (CC BY 4.0)",
        "% http://creativecommons.org/licenses/by/4.0/",
        "",
        "% To be included",
    )
    if tuple(candidate_lines[:8]) != required_rights_header:
        fail("CC BY 4.0 notice or Wen-Wei Li attribution drift")
    if candidate_text.count("李文威") != 1:
        fail("source-author Han attribution missing or duplicated")
    han_scan_text = candidate_text.replace("李文威", "", 1)
    if HAN_RE.search(han_scan_text):
        fail("unauthorized Han residue outside the preserved author attribution")
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
    if len(source_math) != 230:
        fail(f"protected mathematical-zone census drift: {len(source_math)}")

    expected_begins = {
        "align*": 1,
        "aligned": 1,
        "array": 1,
        "compactenum": 1,
        "compactitem": 1,
        "definition": 5,
        "enumerate": 1,
        "equation": 1,
        "example": 3,
        "gather*": 1,
        "itemize": 2,
        "pmatrix": 1,
        "proposition": 4,
        "smallmatrix": 1,
        "tikzcd": 2,
        "wenxintishi": 1,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 54:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 11:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 12:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 0:
        fail("citation count drift")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 11:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")
    if candidate_text.count(r"\begin{tikzcd}") != 2:
        fail("tikzcd census drift")
    if len(re.findall(r"\\arrow", candidate_text)) != 6:
        fail("diagram-arrow census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 16:
        fail("item census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 420:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 158 or candidate_text.count("}") != 158:
        fail("raw brace census drift")
    comment_records = [
        index
        for index, line in enumerate(candidate_lines, start=1)
        if line.lstrip().startswith("%")
    ]
    if comment_records != [1, 2, 3, 4, 5, 6, 8]:
        fail(f"source comment-state topology drift: {comment_records!r}")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 4:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        for _, target_fragment in replacements:
            if candidate_line.count(target_fragment) != 1 and not (
                absolute_line == 158
                and target_fragment == r"\text{ideal dua sisi}"
                and candidate_line.count(target_fragment) == 2
            ):
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
    if candidate_text.count(r"R/\Ker(\varphi)") != 1:
        fail("O013-LI-U036-COR-001 corrected quotient census drift")
    if candidate_text.count(r"S/(I \cap S)") != 1:
        fail("O013-LI-U036-COR-002 corrected quotient census drift")

    required_anchors = (
        "Pengantar Teori Gelanggang",
        "gelanggang komutatif",
        "gelanggang takkomutatif",
        "gelanggang tanpa unsur satuan",
        "subgelanggang",
        "gelanggang lawan",
        "homomorfisme gelanggang",
        "gelanggang matriks",
        "gelanggang endomorfisme",
        "ideal kiri",
        "ideal kanan",
        "ideal dua sisi",
        "ideal sejati",
        "gelanggang hasil bagi",
        "homomorfisme hasil bagi",
        "kernel",
        "isomorfisme gelanggang",
        "Teorema Kecil Wedderburn",
        "faktorisasi tunggal",
        "polinomial simetris",
        "diagram Young",
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

    print("PASS: O013-LI-U036 isolated Chapter 5 opening + complete Section 5.1")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 54 environment markers, 11 labels, 12 references, "
        f"0 citations, 11 indexes, {len(source_math)} protected math zones, "
        "2 diagrams / 6 arrows"
    )
    print(
        "content: 16 items, 7 preserved comment records, one exact Han author "
        "attribution, 0 other Han residue; 4 protected-text localizations; "
        "11 localized indexes; 2 proven source corrections"
    )
    print("next source cursor: chapter5.tex line 174")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
