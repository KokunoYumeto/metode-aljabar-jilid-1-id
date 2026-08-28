#!/usr/bin/env python3
"""Fail-closed checker for isolated O013-LI-U041, monoid/polynomial rings."""

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
    / "unit-041-candidate"
    / "chapter5-monoid-polynomial-rings-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 783
SOURCE_END = 956
SLICE_RECORDS = 174
SLICE_BYTES = 16_536
SLICE_SHA256 = "00f6256684085d12651ccb4decc1c1c51a773c1a958b5e08da93a24aae3cc9bf"

CANDIDATE_RECORDS = 174
CANDIDATE_BYTES = 20_216
CANDIDATE_SHA256 = "128e12090cdca0030ee537d778838fd9daad941319fc63e112216c593454001a"

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
    r"\\begin\{(align\*?|aligned|array|cases|equation\*?|gather\*?|"
    r"gathered|multline\*?|pmatrix|smallmatrix|tikzcd|tikzpicture)\}"
    r"(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    786: (
        (
            r"\index{yaobanqunhuan@幺半群环}",
            r"\index{yaobanqunhuan@gelanggang monoid}",
        ),
    ),
    801: ((r"\text{幺半群}", r"\text{monoid}"),),
    805: ((r"\text{环}", r"\text{gelanggang}"),),
    819: (
        (
            r"\index{qunhuan@群环, 群代数 (group ring, group algebra)}",
            r"\index{qunhuan@gelanggang grup, aljabar grup (group ring, group algebra)}",
        ),
    ),
    824: (
        (
            r"\index{duoxiangshihuan@多项式环 (polynomial ring)}",
            r"\index{duoxiangshihuan@gelanggang polinomial (polynomial ring)}",
        ),
    ),
    845: (
        (
            r"\index{youlihanshuyu@有理函数域 (field of rational functions)}",
            r"\index{youlihanshuyu@medan fungsi rasional (field of rational functions)}",
        ),
    ),
    864: ((r"\text{有限和}", r"\text{jumlah berhingga}"),),
    867: (
        (
            r"\index{shouyiduoxiangshi@首一多项式 (monic polynomial)}",
            r"\index{shouyiduoxiangshi@polinomial monik (monic polynomial)}",
        ),
        (
            r"\index{daoshu@导数 (derivative)}",
            r"\index{daoshu@turunan (derivative)}",
        ),
    ),
    885: (
        (
            r"\index{xingshimijishuhuan@形式幂级数环 (ring of formal power series)}",
            r"\index{xingshimijishuhuan@gelanggang deret pangkat formal (ring of formal power series)}",
        ),
    ),
    891: ((r"\text{常数项}", r"\text{suku konstan}"),),
    906: ((r"\text{无穷和}", r"\text{jumlah tak hingga}"),),
    927: ((r"\text{(收敛级数)}", r"\text{(deret konvergen)}"),),
    933: ((r"\text{映射 }", r"\text{peta }"),),
    953: ((r"\text{其中}", r"\text{dengan}"),),
}

SOURCE_CORRECTIONS = {
    860: (
        r"|c_{\bm{a}}|\neq 0",
        r"c_{\bm{a}}\neq 0",
        "O013-LI-U041-COR-001",
    ),
    892: (
        r"R\llbracket X\rrbracket",
        r"R\llbracket X_1, \ldots, X_n\rrbracket",
        "O013-LI-U041-COR-002",
    ),
    915: (
        r"容许在至多有限个项中 $a_1, \ldots, a_n$ 可取负整数值",
        r"eksponen $a_1, \ldots, a_n$ bernilai bilangan bulat yang secara serentak dibatasi dari bawah",
        "O013-LI-U041-COR-003",
    ),
    953: (
        r"X^{\bm{a}}",
        r"\bm{X}^{\bm{a}}",
        "O013-LI-U041-COR-004",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{yaobanqunhuan@gelanggang monoid}",
    r"\index[sym1]{$R[M]$}",
    r"\index{qunhuan@gelanggang grup, aljabar grup (group ring, group algebra)}",
    r"\index{duoxiangshihuan@gelanggang polinomial (polynomial ring)}",
    r"\index[sym1]{$R[X,\ldots]$}",
    r"\index{youlihanshuyu@medan fungsi rasional (field of rational functions)}",
    r"\index[sym1]{$F(X,\ldots)$}",
    r"\index{shouyiduoxiangshi@polinomial monik (monic polynomial)}",
    r"\index{daoshu@turunan (derivative)}",
    r"\index{xingshimijishuhuan@gelanggang deret pangkat formal (ring of formal power series)}",
    r"\index[sym1]{$R \llbracket X, \ldots \rrbracket, \; R(( X, \ldots ))$}",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        fail(f"UTF-8 BOM forbidden: {path}")
    if b"\r" in data:
        fail(f"CR/CRLF forbidden: {path}")
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
        source_fragment, target_fragment, correction_id = SOURCE_CORRECTIONS[
            absolute_line
        ]
        if source_fragment not in text:
            fail(f"{correction_id} source defect drift at line {absolute_line}")
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
        line.count("{"),
        line.count("}"),
        line.count("``"),
        line.count("''"),
        line.lstrip().startswith("%"),
    )


def math_zones(text: str) -> list[str]:
    spans: list[tuple[int, str]] = []
    for regex in (INLINE_MATH_RE, DISPLAY_MATH_RE, MATH_ENV_RE):
        for match in regex.finditer(text):
            content = match.group(2) if regex is MATH_ENV_RE else match.group(1)
            spans.append((match.start(), re.sub(r"\s+", "", content)))
    return [content for _, content in sorted(spans)]


def main() -> int:
    source_data, source_text = strict_text(SOURCE)
    candidate_data, candidate_text = strict_text(CANDIDATE)
    if len(source_data) != SOURCE_BYTES or digest(source_data) != SOURCE_SHA256:
        fail("frozen chapter5 authority identity drift")
    source_lines = records(source_text)
    if len(source_lines) != SOURCE_RECORDS:
        fail("authority record-count drift")

    expected_rights_header = (
        "% LaTeX source for book \x60\x60代数学方法'' in Chinese",
        "% Copyright 2018  李文威 (Wen-Wei Li).",
        "% Permission is granted to copy, distribute and/or modify this",
        "% document under the terms of the Creative Commons",
        "% Attribution 4.0 International (CC BY 4.0)",
        "% http://creativecommons.org/licenses/by/4.0/",
    )
    if tuple(source_lines[:6]) != expected_rights_header:
        fail("chapter rights header drift")

    source_slice_lines = source_lines[SOURCE_START - 1 : SOURCE_END]
    source_slice_text = "\n".join(source_slice_lines) + "\n"
    source_slice_data = source_slice_text.encode("utf-8")
    if len(source_slice_lines) != SLICE_RECORDS:
        fail("source slice record-count drift")
    if len(source_slice_data) != SLICE_BYTES or digest(source_slice_data) != SLICE_SHA256:
        fail("authority lines 783-956 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 782 opening separator drift")
    if source_slice_lines[0] != (
        r"\section{从幺半群环到多项式环}\label{sec:polynomial-ring}"
    ):
        fail("authority section opening drift")
    if source_slice_lines[-1] != r"\end{remark}":
        fail("authority section closing record drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 957 closing separator drift")
    if source_lines[SOURCE_END + 1] != (
        r"\section{唯一分解性}\label{sec:UFD}"
    ):
        fail("authority next-section cursor drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n") or candidate_text.endswith("\n\n"):
        fail("candidate must have exactly one final LF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail("candidate record-count drift")
    if candidate_lines[0] != (
        r"\section{Dari Gelanggang Monoid ke Gelanggang Polinomial}"
        r"\label{sec:polynomial-ring}"
    ):
        fail("candidate section opening drift")
    if candidate_lines[-1] != r"\end{remark}":
        fail("candidate section closing record drift")

    if HAN_RE.search(candidate_text):
        fail("unauthorized Han residue")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("unauthorized Chinese punctuation residue")
    if "\u00ad" in candidate_text or "\u200b" in candidate_text or "\ufeff" in candidate_text:
        fail("invisible Unicode residue")
    for character in candidate_text:
        if ord(character) < 32 and character not in "\n\t":
            fail(f"unauthorized control U+{ord(character):04X}")
    if re.search(r"\b(?:TODO|TBD|FIXME|TRANSLATE)\b", candidate_text, re.IGNORECASE):
        fail("placeholder residue")
    if len(candidate_data) <= len(source_slice_data):
        fail("candidate byte extent does not dominate source slice")

    for regex, name in (
        (ENV_RE, "environment topology"),
        (LABEL_RE, "label identifiers"),
        (REF_RE, "reference identifiers"),
        (CITE_RE, "citation keys"),
        (INDEX_STREAM_RE, "index streams"),
    ):
        if ordered(regex, source_slice_text) != ordered(regex, candidate_text):
            fail(f"ordered {name} drift")

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
    if len(source_math) != 277:
        fail(f"authority mathematical-zone census drift: {len(source_math)}")
    if source_math != candidate_math:
        if len(source_math) != len(candidate_math):
            fail(f"math-zone count drift: {len(source_math)} != {len(candidate_math)}")
        mismatch = next(
            index
            for index, (source_zone, candidate_zone) in enumerate(
                zip(source_math, candidate_math, strict=True), start=1
            )
            if source_zone != candidate_zone
        )
        fail(f"protected mathematical zone {mismatch} drift")

    expected_begins = {
        "align*": 4,
        "aligned": 1,
        "compactitem": 1,
        "definition": 5,
        "equation": 2,
        "gather*": 3,
        "itemize": 1,
        "proof": 5,
        "proposition": 5,
        "remark": 2,
        "tikzcd": 2,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 62:
        fail("environment marker census drift")
    if len(LABEL_RE.findall(candidate_text)) != 10:
        fail("label census drift")
    if len(REF_RE.findall(candidate_text)) != 10:
        fail("reference census drift")
    if CITE_RE.findall(candidate_text):
        fail("unexpected citation key")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 11:
        fail("index census drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized/preserved index missing or duplicated: {localized_index}")

    if candidate_text.count(r"\begin{tikzcd}") != 2:
        fail("tikzcd census drift")
    if len(re.findall(r"\\arrow\b", candidate_text)) != 8:
        fail("diagram arrow census drift")
    if candidate_text.count(r"\includegraphics") != 0:
        fail("unexpected raster asset pointer")
    if candidate_text.count(r"\href") != 0:
        fail("unexpected external asset link")
    if len(re.findall(r"\\item\b", candidate_text)) != 6:
        fail("item census drift")

    source_comments = [
        line_number
        for line_number, line in enumerate(source_slice_lines, start=SOURCE_START)
        if line.lstrip().startswith("%")
    ]
    candidate_comments = [
        line_number
        for line_number, line in enumerate(candidate_lines, start=1)
        if line.lstrip().startswith("%")
    ]
    if source_comments or candidate_comments:
        fail(
            f"comment-state drift: source={source_comments}, candidate={candidate_comments}"
        )
    for environment in ("Exercises", "exercise", "hint", "answer", "solution"):
        if candidate_text.count(rf"\begin{{{environment}}}") != 0:
            fail(f"unexpected {environment} environment")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 15:
        fail("protected substitution census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        targets = collections.Counter(target for _, target in replacements)
        for target_fragment, expected_count in targets.items():
            if candidate_line.count(target_fragment) != expected_count:
                fail(
                    f"protected substitution drift at authority line "
                    f"{absolute_line}: {target_fragment!r}"
                )

    correction_ids = {
        correction[2] for correction in SOURCE_CORRECTIONS.values()
    }
    if correction_ids != {
        "O013-LI-U041-COR-001",
        "O013-LI-U041-COR-002",
        "O013-LI-U041-COR-003",
        "O013-LI-U041-COR-004",
    }:
        fail("declared correction identity drift")
    for absolute_line, (source_fragment, target_fragment, correction_id) in (
        SOURCE_CORRECTIONS.items()
    ):
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if candidate_line.count(target_fragment) != 1 or source_fragment in candidate_line:
            fail(f"{correction_id} repair drift at authority line {absolute_line}")

    required_admitted_terminology = {
        "ring": "gelanggang",
        "field": "medan",
        "group": "grup",
        "monoid": "monoid",
        "commutative monoid": "monoid komutatif",
        "homomorphism": "homomorfisme",
        "isomorphism": "isomorfisme",
        "algebra": "aljabar",
        "polynomial ring": "gelanggang polinomial",
        "evaluation map": "peta evaluasi",
        "quotient map": "peta hasil bagi",
    }
    required_refined_terminology = {"completion": "pelengkapan"}
    with TERMINOLOGY.open("r", encoding="utf-8-sig", newline="") as handle:
        terminology_rows = {
            row["source_term"]: (row["target_term"], row["status"])
            for row in csv.DictReader(handle)
        }
    candidate_casefold = candidate_text.casefold()
    for source_term, target_term in required_admitted_terminology.items():
        if terminology_rows.get(source_term) != (target_term, "admitted"):
            fail(f"controlled admitted terminology drift: {source_term!r}")
        if target_term.casefold() not in candidate_casefold:
            fail(f"controlled target term absent: {target_term!r}")
    for source_term, target_term in required_refined_terminology.items():
        if target_term.casefold() not in candidate_casefold:
            fail(f"refined target term absent: {source_term!r}")

    required_anchors = (
        "gelanggang monoid",
        "aljabar monoid",
        "gelanggang grup",
        "aljabar grup",
        "monomial",
        "medan fungsi rasional",
        "multiindeks",
        "derajat total",
        "polinomial homogen",
        "polinomial monik",
        "aturan Leibniz",
        "turunan parsial",
        "gelanggang deret pangkat formal",
        "gelanggang deret Laurent formal",
        "secara serentak dibatasi dari bawah",
        "fungsi polinomial",
        "teorema kecil Fermat",
        "subgelanggang yang dibangkitkan",
    )
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"semantic anchor missing: {anchor!r}")
    for forbidden in ("cincin", "lapangan", "kelompok", "funktor", "kompletisasi"):
        if forbidden.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian term appeared: {forbidden!r}")

    print("PASS: O013-LI-U041 isolated complete monoid/polynomial-ring section")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 62 environment markers, 10 labels, 10 references, "
        f"0 citations, 11 indexes, {len(source_math)} protected math zones"
    )
    print(
        "diagrams/content: 2 tikzcd / 8 arrows / 0 external asset pointers; "
        "6 items; 0 exercises/hints/answers/solutions/comments"
    )
    print(
        "localizations/corrections: 15 protected substitutions "
        "(7 indexes + 8 math/diagram text fragments); "
        "4 proven source corrections"
    )
    print("rights: frozen Chapter 5 CC BY 4.0 authority header bound")
    print("next source cursor: chapter5.tex line 958")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
