#!/usr/bin/env python3
"""Fail-closed checker for isolated O013-LI-U042, unique factorization."""

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
    / "unit-042-candidate"
    / "chapter5-unique-factorization-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 958
SOURCE_END = 1_182
SLICE_RECORDS = 225
SLICE_BYTES = 22_981
SLICE_SHA256 = "2e3758fa4b4175eeba5969159a89ccb40895c173c12699a8c2211e68a1e94b2a"

CANDIDATE_RECORDS = 225
CANDIDATE_BYTES = 29_674
CANDIDATE_SHA256 = "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a"

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CHINESE_PUNCT_RE = re.compile(
    r"[\uFF0C\u3002\uFF1B\uFF1A\uFF1F\uFF01\u300A\u300B"
    r"\u300C\u300D\u300E\u300F\u3001]"
)
ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(eqref|ref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
INDEX_RE = re.compile(r"\\index(?:\[([^\]]+)\])?\{")
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
    967: (
        (
            r"\index{bukeyue@不可约 (irreducible)}",
            r"\index{bukeyue@tak tereduksi (irreducible)}",
        ),
        (
            r"\index{weiyifenjiehuan@唯一分解环 (unique factorization domain)}",
            r"\index{weiyifenjiehuan@daerah faktorisasi unik (unique factorization domain)}",
        ),
    ),
    974: (
        (
            r"\index{suyuan@素元 (prime element)}",
            r"\index{suyuan@unsur prima (prime element)}",
        ),
    ),
    1030: ((r"\index{Euclid 环}", r"\index{daerah Euklides (Euclidean domain)}"),),
    1032: (
        (r"\text{或者}", r"\text{atau}"),
        (r"\text{而}", r"\text{dan}"),
    ),
    1045: (
        (
            r"\text{(作为 $\CC$ 的子环)}",
            r"\text{(sebagai subgelanggang dari $\CC$)}",
        ),
    ),
    1070: (
        (
            r"\text{相异不可约元}",
            r"\text{unsur tak tereduksi yang berbeda}",
        ),
    ),
    1085: (
        (r"\text{分歧}", r"\text{teramifikasi}"),
        (r"\text{分裂}", r"\text{terbelah}"),
        (r"\text{惯性}", r"\text{iners}"),
    ),
    1096: (
        (
            r"\index{zhengbi@整闭 (integrally closed)}",
            r"\index{zhengbi@tertutup integral (integrally closed)}",
        ),
    ),
    1106: (
        (
            r"\index{rongdu@容度 (content)}",
            r"\index{rongdu@konten (content)}",
        ),
    ),
    1113: ((r"\index{Gauss 引理}", r"\index{Lema Gauss}"),),
    1162: ((r"\index{Eisenstein 判准}", r"\index{Kriteria Eisenstein}"),),
    1178: (
        (
            r"\text{高次项}",
            r"\text{suku-suku berderajat lebih tinggi}",
        ),
    ),
    1180: (
        (
            r"\text{高次项}",
            r"\text{suku-suku berderajat lebih tinggi}",
        ),
    ),
}

SOURCE_CORRECTIONS = {
    1053: (
        r"D \in \Z_{\neq 0}",
        r"D \in \Z \smallsetminus \{0,1\}",
        "O013-LI-U042-COR-001",
    ),
    1074: (
        r"u \in \Z[\sqrt{-1}]^\times = \{\pm 1, \pm\sqrt{-1}\}",
        r"\bar{\mathfrak{p}}=u\mathfrak{p}, \; u \in \Z[\sqrt{-1}]^\times = \{\pm 1, \pm\sqrt{-1}\}",
        "O013-LI-U042-COR-002",
    ),
    1114: (
        r"对每个不可约元 $p$, 函数 $c$ 皆满足乘性",
        r"Fungsi $c$ bersifat multiplikatif, yaitu",
        "O013-LI-U042-COR-003",
    ),
    1117: (
        r"置 ",
        r"Pilih wakil bagi kedua kelas konten tersebut, lalu tetapkan ",
        "O013-LI-U042-COR-004",
    ),
    1127: (
        r"对任意 $n \geq 0$",
        r"Dengan memperluas definisi konten ke polinomial banyak peubah melalui nilai minimum valuasi pada seluruh koefisien, untuk setiap $n \geq 0$",
        "O013-LI-U042-COR-005",
    ),
    1151: (
        r"今将往证 $X^{(a,b)} - 1$ 是 $X^a - 1$ 和 $X^b - 1$ 的最大公因子",
        r"Akan dibuktikan bahwa $X^{(a,b)} - 1$ merupakan pembagi persekutuan terbesar dari $X^a - 1$ dan $X^b - 1$ apabila kedua unsur terakhir tak nol",
        "O013-LI-U042-COR-006",
    ),
    1165: (
        r"k \leq n",
        r"1 \leq k \leq n",
        "O013-LI-U042-COR-007",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{bukeyue@tak tereduksi (irreducible)}",
    r"\index{weiyifenjiehuan@daerah faktorisasi unik (unique factorization domain)}",
    r"\index{suyuan@unsur prima (prime element)}",
    r"\index{daerah Euklides (Euclidean domain)}",
    r"\index{zhengbi@tertutup integral (integrally closed)}",
    r"\index{rongdu@konten (content)}",
    r"\index{Lema Gauss}",
    r"\index{Kriteria Eisenstein}",
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
        tuple(stream or "main" for stream in INDEX_RE.findall(line)),
        line.count(r"\["),
        line.count(r"\]"),
        len(re.findall(r"(?<!\\)\$", line)),
        line.count("&"),
        line.count(r"\\"),
        line.count("{"),
        line.count("}"),
        line.count("``"),
        line.count("''"),
        line.count("%"),
    )


def math_zones(text: str) -> list[str]:
    spans: list[tuple[int, str]] = []
    for regex in (INLINE_MATH_RE, DISPLAY_MATH_RE, MATH_ENV_RE):
        for match in regex.finditer(text):
            content = match.group(2) if regex is MATH_ENV_RE else match.group(1)
            spans.append((match.start(), re.sub(r"\s+", "", content)))
    return [content for _, content in sorted(spans)]


def strip_comments(text: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in text.split("\n"))


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
        fail("authority lines 958-1182 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 957 opening separator drift")
    if source_slice_lines[0] != r"\section{唯一分解性}\label{sec:UFD}":
        fail("authority section opening drift")
    if source_slice_lines[-1] != r"\end{proof}":
        fail("authority section closing record drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 1183 closing separator drift")
    if source_lines[SOURCE_END + 1] != (
        r"\section{对称多项式入门}\label{sec:symmetric-poly}"
    ):
        fail("authority next-section cursor drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n") or candidate_text.endswith("\n\n"):
        fail("candidate must have exactly one final LF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail("candidate record-count drift")
    if candidate_lines[0] != r"\section{Faktorisasi Unik}\label{sec:UFD}":
        fail("candidate section opening drift")
    if candidate_lines[-1] != r"\end{proof}":
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
        (INDEX_RE, "index streams"),
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
    if len(source_math) != 464:
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
        "definition": 2,
        "itemize": 1,
        "proposition": 3,
        "compactitem": 3,
        "proof": 10,
        "inparaenum": 2,
        "lemma": 3,
        "theorem": 4,
        "example": 4,
        "equation": 1,
        "cases": 1,
        "compactdesc": 1,
        "remark": 1,
        "compactenum": 2,
        "gather*": 1,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 78:
        fail("environment marker census drift")
    if len(LABEL_RE.findall(candidate_text)) != 15:
        fail("label census drift")
    if len(REF_RE.findall(candidate_text)) != 16:
        fail("reference census drift")
    if len(CITE_RE.findall(candidate_text)) != 2:
        fail("citation census drift")
    if CITE_RE.findall(candidate_text) != ["Go85", "Wil73"]:
        fail("citation identity/order drift")
    if len(INDEX_RE.findall(candidate_text)) != 8:
        fail("raw index census drift")
    if len(INDEX_RE.findall(strip_comments(candidate_text))) != 7:
        fail("live index census drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")

    if candidate_text.count(r"\[") != 18 or candidate_text.count(r"\]") != 18:
        fail("display-math delimiter census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 25:
        fail("item census drift")
    if re.search(r"\\(?:begin\{tikzcd|begin\{tikzpicture|arrow)\b", candidate_text):
        fail("unexpected diagram topology")
    if re.search(r"\\(?:includegraphics|input|include|href|url)\b", candidate_text):
        fail("unexpected source asset pointer")
    for environment in ("Exercises", "exercise", "problem", "hint", "answer", "solution"):
        if candidate_text.count(rf"\begin{{{environment}}}") != 0:
            fail(f"unexpected {environment} environment")

    source_comments = [
        line_number
        for line_number, line in enumerate(source_slice_lines, start=SOURCE_START)
        if "%" in line
    ]
    candidate_comments = [
        line_number
        for line_number, line in enumerate(candidate_lines, start=1)
        if "%" in line
    ]
    if source_comments != [1106] or candidate_comments != [149]:
        fail(
            f"inline comment topology drift: source={source_comments}, "
            f"candidate={candidate_comments}"
        )
    if candidate_lines[148] != r"\begin{definition} %\index{rongdu@konten (content)}":
        fail("disabled content-index comment drift")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 17:
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

    correction_ids = {correction[2] for correction in SOURCE_CORRECTIONS.values()}
    if correction_ids != {
        "O013-LI-U042-COR-001",
        "O013-LI-U042-COR-002",
        "O013-LI-U042-COR-003",
        "O013-LI-U042-COR-004",
        "O013-LI-U042-COR-005",
        "O013-LI-U042-COR-006",
        "O013-LI-U042-COR-007",
    }:
        fail("declared correction identity drift")
    for absolute_line, (source_fragment, target_fragment, correction_id) in (
        SOURCE_CORRECTIONS.items()
    ):
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if candidate_line.count(target_fragment) != 1:
            fail(f"{correction_id} repair drift at authority line {absolute_line}")
        if source_fragment not in target_fragment and source_fragment in candidate_line:
            fail(f"{correction_id} repair drift at authority line {absolute_line}")

    required_admitted_terminology = {
        "ring": "gelanggang",
        "field": "medan",
        "group": "grup",
        "monoid": "monoid",
        "algebra": "aljabar",
        "homomorphism": "homomorfisme",
        "isomorphism": "isomorfisme",
        "polynomial ring": "gelanggang polinomial",
        "quotient monoid": "monoid hasil bagi",
        "partially ordered set": "himpunan terurut parsial (poset)",
        "supremum": "supremum",
        "well-ordered set": "himpunan terurut baik",
        "cyclic group": "grup siklik",
    }
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

    required_anchors = (
        "daerah integral",
        "daerah faktorisasi unik",
        "unsur tak tereduksi",
        "unsur prima",
        "pembagi persekutuan terbesar",
        "relatif prima",
        "syarat rantai menaik",
        "daerah ideal utama",
        "daerah Euklides",
        "gelanggang bilangan bulat Gauss",
        "medan bilangan kuadrat",
        "bilangan bulat aljabar",
        "teorema dasar aritmetika",
        "terbelah",
        "teramifikasi",
        "iners",
        "akar primitif",
        "tertutup integral",
        "konten",
        "Lema Gauss",
        "Kriteria Eisenstein",
        "pembagian bersisa",
        "algoritma Euklides",
    )
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"semantic anchor missing: {anchor!r}")
    for forbidden in ("cincin", "lapangan", "kelompok", "funktor"):
        if forbidden.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian term appeared: {forbidden!r}")

    print("PASS: O013-LI-U042 isolated complete unique-factorization section")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 78 environment markers, 15 labels, 16 references, "
        f"2 citations, 8 index commands (7 live + 1 commented), "
        f"{len(source_math)} protected math zones"
    )
    print(
        "content: 25 items / 18 display pairs / 1 inline comment; "
        "0 diagrams, assets, or exercise/hint/answer/solution environments"
    )
    print(
        "localizations/corrections: 17 protected substitutions "
        "(8 indexes + 9 math-text fragments); 7 proven source corrections"
    )
    print("rights: frozen Chapter 5 CC BY 4.0 authority header bound")
    print("next source cursor: chapter5.tex line 1184")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
