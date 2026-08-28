#!/usr/bin/env python3
"""Entry point for the complete O013-LI-U043 section-and-exercises checker."""

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
    / "unit-043-candidate"
    / "chapter5-symmetric-polynomials-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 122_998
SOURCE_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
SOURCE_RECORDS = 1_382
SOURCE_START = 1_184
SOURCE_END = 1_318
SLICE_RECORDS = 135
SLICE_BYTES = 11_304
SLICE_SHA256 = "2596fa0de36082ae7bc6800f25ad95d7bda419f84e2ab9aace686933227cbaf8"

CANDIDATE_RECORDS = 135
CANDIDATE_BYTES = 13_664
CANDIDATE_SHA256 = "c2a2b1a1d86a22bf1474ecb82c021d746104502d5cf6f4cf25eecad992c20668"

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
    1191: (
        (
            r"\index{duichengduoxiangshi@对称多项式 (symmetric polynomial)}",
            r"\index{duichengduoxiangshi@polinomial simetris (symmetric polynomial)}",
        ),
    ),
    1204: (
        (
            r"\index{Young-tu@Young 图 (Young diagram)}",
            r"\index{Young-tu@diagram Young (Young diagram)}",
        ),
        (r"\index{fenchai}", r"\index{fenchai@partisi (partition)}"),
    ),
    1235: (
        (
            r"\index{duichengduoxiangshi!初等 (elementary)}",
            r"\index{duichengduoxiangshi!elementer (elementary)}",
        ),
    ),
    1242: ((r"\text{或者}", r"\text{atau}"),),
    1286: (
        (
            r"\index{panbieshi@判别式 (discriminant)}",
            r"\index{panbieshi@diskriminan (discriminant)}",
        ),
    ),
    1288: ((r"\text{有重根}", r"\text{memiliki akar ganda}"),),
    1292: (
        (
            r"\index{duichengduoxiangshi!幂和 (power-sum)}",
            r"\index{duichengduoxiangshi!jumlah pangkat (power-sum)}",
        ),
    ),
    1295: ((r"\index{Newton 公式}", r"\index{Rumus Newton}"),),
}

SOURCE_CORRECTIONS = {
    1199: (
        r"1 \leq \lambda_i \leq n",
        r"1 \leq i \leq r",
        "O013-LI-U043-COR-001",
    ),
    1222: (
        r"0 \leq i < k",
        r"1 \leq i < k",
        "O013-LI-U043-COR-002",
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{duichengduoxiangshi@polinomial simetris (symmetric polynomial)}",
    r"\index{Young-tu@diagram Young (Young diagram)}",
    r"\index{fenchai@partisi (partition)}",
    r"\index{duichengduoxiangshi!elementer (elementary)}",
    r"\index{panbieshi@diskriminan (discriminant)}",
    r"\index{duichengduoxiangshi!jumlah pangkat (power-sum)}",
    r"\index{Rumus Newton}",
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
        "% LaTeX source for book ``代数学方法'' in Chinese",
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
        fail("authority lines 1184-1318 identity drift")
    if source_lines[SOURCE_START - 2] != "":
        fail("authority line 1183 opening separator drift")
    if source_slice_lines[0] != (
        r"\section{对称多项式入门}\label{sec:symmetric-poly}"
    ):
        fail("authority section opening drift")
    if source_slice_lines[-1] != (
        r"以上获得的结论与方法同等重要, 这还仅只是敲开了对称多项式理论的大门, 有心一窥堂奥的读者可参阅 \cite{Mac95}."
    ):
        fail("authority section closing record drift")
    if source_lines[SOURCE_END] != "":
        fail("authority line 1319 closing separator drift")
    if source_lines[SOURCE_END + 1] != "% % % % % % % % % % % % % % % % % % % % %":
        fail("authority line 1320 separator comment drift")
    if source_lines[SOURCE_END + 2] != "":
        fail("authority line 1321 separator drift")
    if source_lines[SOURCE_END + 3] != r"\begin{Exercises}":
        fail("authority next-unit cursor drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n") or candidate_text.endswith("\n\n"):
        fail("candidate must have exactly one final LF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail("candidate record-count drift")
    if candidate_lines[0] != (
        r"\section{Pengantar Polinomial Simetris}\label{sec:symmetric-poly}"
    ):
        fail("candidate section opening drift")
    if candidate_lines[-1] != (
        r"Hasil dan metode yang diperoleh di atas sama pentingnya; pembahasan ini baru sekadar membuka pintu menuju teori polinomial simetris. Pembaca yang ingin melihat lebih jauh dapat merujuk pada \cite{Mac95}."
    ):
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
    if len(source_math) != 190:
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
        "align*": 2,
        "equation*": 1,
        "definition": 2,
        "compactdesc": 1,
        "gather": 1,
        "proposition": 1,
        "proof": 4,
        "gather*": 1,
        "lemma": 1,
        "ytableau": 1,
        "theorem": 2,
        "example": 1,
        "cases": 1,
        "compactitem": 1,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 40:
        fail("environment marker census drift")
    if len(LABEL_RE.findall(candidate_text)) != 7:
        fail("label census drift")
    if len(REF_RE.findall(candidate_text)) != 5:
        fail("reference census drift")
    if len(CITE_RE.findall(candidate_text)) != 1:
        fail("citation census drift")
    if CITE_RE.findall(candidate_text) != ["Mac95"]:
        fail("citation identity/order drift")
    if len(INDEX_RE.findall(candidate_text)) != 7:
        fail("raw index census drift")
    if len(INDEX_RE.findall(strip_comments(candidate_text))) != 7:
        fail("live index census drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")

    if candidate_text.count(r"\[") != 14 or candidate_text.count(r"\]") != 14:
        fail("display-math delimiter census drift")
    if len(re.findall(r"\\item\b", candidate_text)) != 4:
        fail("item census drift")
    if candidate_text.count(r"\ydiagram") != 4:
        fail("Young-diagram command census drift")
    if candidate_text.count(r"\none") != 12:
        fail("Young-tableau placeholder census drift")
    if re.search(r"\\(?:begin\{tikzcd|begin\{tikzpicture|arrow)\b", candidate_text):
        fail("unexpected TikZ diagram topology")
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
        for line_number, line in enumerate(candidate_lines, start=SOURCE_START)
        if "%" in line
    ]
    if source_comments != [1270, 1307] or candidate_comments != [1270, 1307]:
        fail(
            f"inline comment topology drift: source={source_comments}, "
            f"candidate={candidate_comments}"
        )
    if candidate_lines[1270 - SOURCE_START] != (
        r"% Koefisien tak negatif $a_{\lambda,\mu}$ ini memiliki kandungan kombinatorial dan geometris yang halus."
    ):
        fail("disabled combinatorial comment drift")
    if candidate_lines[1307 - SOURCE_START] != (
        "\t\t"
        + r"% & = \sum_{r=1}^n \frac{\dd}{\dd Y} \left( \log \frac{1}{1 - X_r Y} \right), \\"
    ):
        fail("disabled logarithmic-derivative line drift")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 9:
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
        "O013-LI-U043-COR-001",
        "O013-LI-U043-COR-002",
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
        "polynomial ring": "gelanggang polinomial",
        "symmetric group": "grup simetris",
        "field": "medan",
        "free module": "modul bebas",
        "universal property": "sifat universal",
        "isomorphism": "isomorfisme",
        "partition": "partisi",
        "lexicographic order": "urutan leksikografis",
        "partially ordered set": "himpunan terurut parsial (poset)",
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
        "gelanggang komutatif",
        "subgelanggang",
        "fungsi rasional",
        "notasi multiindeks",
        "diagram Young",
        "konjugat",
        "urutan dominasi",
        "urutan leksikografis",
        "polinomial simetris elementer",
        "matriks segitiga unipoten",
        "Teorema dasar polinomial simetris",
        "diskriminan",
        "akar ganda",
        "jumlah pangkat",
        "Rumus Newton",
        "deret pembangkit",
    )
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"semantic anchor missing: {anchor!r}")
    for forbidden in ("cincin", "lapangan", "kelompok", "variabel", "funktor"):
        if forbidden.casefold() in candidate_casefold:
            fail(f"uncontrolled Indonesian term appeared: {forbidden!r}")

    print("PASS: O013-LI-U043 isolated complete symmetric-polynomials section")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 40 environment markers, 7 labels, 5 references, "
        f"1 citation, 7 live index commands, {len(source_math)} protected math zones"
    )
    print(
        "content: 4 items / 14 display pairs / 2 inline comments / "
        "4 ydiagram commands / 1 ytableau; 0 external assets or "
        "exercise/hint/answer/solution environments"
    )
    print(
        "localizations/corrections: 9 protected substitutions "
        "(7 indexes + 2 math-text fragments); 2 proven source corrections"
    )
    print("rights: frozen Chapter 5 CC BY 4.0 authority header bound")
    print("next isolated source cursor: chapter5.tex line 1322 (Exercises)")
    return 0


if __name__ == "__main__":
    import runpy

    runpy.run_path(
        str(ROOT / "build" / "unit-043-candidate" / "check_unit_043_candidate.py"),
        run_name="__main__",
    )
