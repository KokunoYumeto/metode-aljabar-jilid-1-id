#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U032 translation.

The checker binds the frozen Li authority, the exact complete Section 4.8
boundary, the Indonesian candidate, record-level TeX and protected
mathematics, identifiers, diagrams, localized protected text, four localized
citation locators, and two declared source corrections.  It performs no
writes.
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
    / "unit-032-candidate"
    / "chapter4-free-groups-id.tex"
)

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 1_108
SOURCE_END = 1_388
SLICE_RECORDS = 281
SLICE_BYTES = 22_547
SLICE_SHA256 = "5a7083cd89d13e776bbf94189f7f96f5d976cd962cba7a8d4c6b2453bd59c8af"

CANDIDATE_BYTES = 27_910
CANDIDATE_SHA256 = "28e8fd2475a89b4617c26b21f0753aa95a81c7bc8524b7540881281159ab4cfc"
CANDIDATE_RECORDS = 280

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
INDEX_HEAD_RE = re.compile(r"\\index(?:\[([^\]]+)\])?\{([^@{}]*@)?")
COMMAND_RE = re.compile(r"\\[A-Za-z@]+|\\.")
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
MATH_ENV_RE = re.compile(
    r"\\begin\{(align\*?|cases|equation\*?|gather\*?|gathered|"
    r"multline\*?|pmatrix|tikzcd|tikzpicture)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    1187: (
        (r"\text{在 $M_i$ 中}", r"\text{di dalam $M_i$}"),
        (
            r"\text{在 $\mathbf{M}(S)$ 中}",
            r"\text{di dalam $\mathbf{M}(S)$}",
        ),
    ),
    1188: (
        (r"\text{$M_i$ 幺元}", r"\text{unsur identitas $M_i$}"),
        (
            r"\text{$\mathbf{M}(S)$ 幺元}",
            r"\text{unsur identitas $\mathbf{M}(S)$}",
        ),
    ),
    1221: (
        (r"\text{ 子集 }", r"\text{ subhimpunan }"),
        (r"\text{ 使得 }", r"\text{ sedemikian sehingga }"),
    ),
    1249: ((r"\text{其中}", r"\text{dengan}"),),
    1250: ((r"\text{其中}", r"\text{dengan}"),),
    1274: (
        (r"\text{ 容许重复 }", r"\text{ pengulangan diperbolehkan }"),
    ),
    1302: (
        (
            r"\text{除至多有限个 $i$ 外}",
            r"\text{untuk semua kecuali paling banyak berhingga banyak $i$}",
        ),
    ),
    1314: (
        (r"\text{形式和 }", r"\text{jumlah formal }"),
        (
            r"\text{仅有限项非零}",
            r"\text{hanya berhingga banyak suku yang tak nol}",
        ),
    ),
    1383: ((r"\text{是自由群}", r"\text{adalah grup bebas}"),),
}

DIGITAL_REFLOWS = {
    1302: (
        r"\[ \bigoplus_{i \in I} M_i := \left\{ (m_i)_{i \in I} \in \prod_{i \in I} M_i : \text{untuk semua kecuali paling banyak berhingga banyak $i$}, \; m_i = 0 \right\}. \]",
        r"\[ \begin{aligned} \bigoplus_{i \in I} M_i &:= \Bigl\{ (m_i)_{i \in I} \in \prod_{i \in I} M_i : {} \\ &\qquad \text{untuk semua kecuali paling banyak berhingga banyak $i$}, \; m_i = 0 \Bigr\}. \end{aligned} \]",
    ),
    1314: (
        r"\[ \Z_{\geq 0}^{\oplus X} := \left\{ \text{jumlah formal } \; \sum_{x \in X} a_x \cdot x : \forall x, \; a_x \in \Z_{\geq 0}, \; \text{hanya berhingga banyak suku yang tak nol} \right\}. \]",
        r"\[ \begin{aligned} \Z_{\geq 0}^{\oplus X} &:= \Bigl\{ \text{jumlah formal } \; \sum_{x \in X} a_x \cdot x : {} \\ &\qquad \forall x, \; a_x \in \Z_{\geq 0}, \; \text{hanya berhingga banyak suku yang tak nol} \Bigr\}. \end{aligned} \]",
    ),
}


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


def index_signature(text: str) -> list[tuple[str, str | None]]:
    return [
        (match.group(1) or "main", (match.group(2) or "").removesuffix("@") or None)
        for match in INDEX_HEAD_RE.finditer(text)
    ]


def normalize_authority_line(text: str, absolute_line: int) -> str:
    """Apply only the declared language localizations and source repairs."""

    for source_fragment, target_fragment in PROTECTED_TEXT_REPLACEMENTS.get(
        absolute_line, ()
    ):
        if source_fragment not in text:
            fail(
                f"protected source fragment missing at authority line {absolute_line}: "
                f"{source_fragment!r}"
            )
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line == 1335:
        source_fragment = r"\lrangle{w_1, \ldots, w_n}_\text{nor}"
        target_fragment = r"\lrangle{w_1, \ldots, w_m}_\text{nor}"
        if source_fragment not in text:
            fail("declared relation-index source defect drift at authority line 1335")
        text = text.replace(source_fragment, target_fragment, 1)

    if absolute_line in DIGITAL_REFLOWS:
        source_fragment, target_fragment = DIGITAL_REFLOWS[absolute_line]
        if source_fragment not in text:
            fail(f"digital-reflow source fragment drift at authority line {absolute_line}")
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
        fail("authority lines 1108-1388 identity drift")
    if source_slice_lines[-1] != "":
        fail("authority line 1388 must remain the blank section boundary")
    if source_lines[SOURCE_END] != r"\section{对称群}\label{sec:symmetric-group}":
        fail("next boundary at authority line 1389 drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")
    if candidate_lines[0] != r"\section{Grup Bebas}\label{sec:free-group}":
        fail("candidate opening boundary drift")
    if candidate_lines[-1] != r"\end{proof}":
        fail("candidate closing boundary drift")
    if r"\section{Grup Simetris}" in candidate_text:
        fail("Section 4.9 crossed into isolated candidate")

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
    candidate_source_environments = [
        item for item in ordered(ENV_RE, candidate_text)
        if item[1] != "aligned"
    ]
    if ordered(ENV_RE, substantive_source_text) != candidate_source_environments:
        fail("ordered begin/end environment topology drift")
    if ordered(LABEL_RE, substantive_source_text) != ordered(LABEL_RE, candidate_text):
        fail("ordered label identifiers drift")
    if ordered(REF_RE, substantive_source_text) != ordered(REF_RE, candidate_text):
        fail("ordered ref/eqref identifiers drift")
    if ordered(CITE_RE, substantive_source_text) != ordered(CITE_RE, candidate_text):
        fail("ordered citation keys drift")
    if index_signature(substantive_source_text) != index_signature(candidate_text):
        fail("index stream or source sort-key topology drift")

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
        "align*": 3,
        "aligned": 2,
        "cases": 1,
        "center": 3,
        "compactenum": 1,
        "compactitem": 1,
        "definition": 6,
        "description": 1,
        "equation": 1,
        "example": 2,
        "gather": 1,
        "gather*": 1,
        "gathered": 1,
        "inparaenum": 1,
        "lemma": 3,
        "proof": 7,
        "proposition": 3,
        "remark": 1,
        "scope": 1,
        "theorem": 1,
        "tikzcd": 9,
        "tikzpicture": 2,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_text)) != 104:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 10:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 20:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 6:
        fail("citation count drift")
    if len(INDEX_RE.findall(candidate_text)) != 7:
        fail("index count drift")
    if candidate_text.count(r"\begin{tikzcd}") != 9:
        fail("tikzcd census drift")
    if candidate_text.count(r"\begin{tikzpicture}") != 2:
        fail("tikzpicture census drift")
    if len(re.findall(r"\\arrow", candidate_text)) != 28:
        fail("diagram-arrow census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 644:
        fail("unescaped dollar-delimiter census drift")
    if candidate_text.count("{") != 387 or candidate_text.count("}") != 387:
        fail("raw brace census drift")
    if re.search(r"\\begin\{(?:exercise|hint|solution)\}", candidate_text):
        fail("out-of-scope exercise, hint or solution environment appeared")
    if any(line.lstrip().startswith("%") for line in candidate_lines):
        fail("source-disabled/comment topology appeared in candidate")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 13:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        for _, target_fragment in replacements:
            if candidate_line.count(target_fragment) != 1:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    relation_source = r"\lrangle{w_1, \ldots, w_n}_\text{nor}"
    relation_target = r"\lrangle{w_1, \ldots, w_m}_\text{nor}"
    line_1335 = candidate_lines[1335 - SOURCE_START]
    if relation_target not in line_1335 or relation_source in line_1335:
        fail("O013-LI-U032-COR-001 relation-index repair drift")
    line_1345 = candidate_lines[1345 - SOURCE_START]
    if r"R.\ Guralnick" not in line_1345 or "Guranlnick" in line_1345:
        fail("O013-LI-U032-COR-002 author-name repair drift")

    citation_localizations = {
        r"\cite[Bab IV \S 3.1]{You}",
        r"\cite[Lampiran B]{You}",
        r"\cite[Bab IV \S 4.3]{You}",
        r"\cite[Bab V \S 4]{You}",
    }
    for citation in citation_localizations:
        if candidate_text.count(citation) != 1:
            fail(f"localized citation locator missing or duplicated: {citation}")

    required_anchors = (
        "fungtor adjoin kiri bagi fungtor pelupa",
        "konstruksi bebas = fungtor adjoin kiri dari fungtor pelupa",
        "produk teramalgamasi",
        "representasi tereduksi yang unik",
        "Monoid komutatif bebas dan grup komutatif bebas",
        "jumlah langsung",
        "presentasi = pembangkit + relasi",
        "Masalah kata",
        "Masalah konjugasi",
        "Masalah isomorfisme",
        "teori grup kombinatorial",
        "teori rekursi",
        "Setiap subgrup dari grup bebas juga merupakan grup bebas",
        "ruang penutup",
        "sifat pengangkatan lintasan",
    )
    for anchor in required_anchors:
        if anchor not in candidate_text:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    if "antarkelompok" in candidate_text:
        fail("uncontrolled group rendering 'kelompok' appeared")
    if "kuosien" in candidate_text:
        fail("candidate drifted from the admitted hasil bagi terminology family")
    if "bertitik pangkal" in candidate_text:
        fail("candidate drifted from the admitted bertitik dasar terminology family")
    if "unsur satuan" in candidate_text:
        fail("candidate drifted from the admitted unsur identitas terminology family")
    if "teramalgamasinya" in candidate_text:
        fail("malformed Indonesian amalgamation surface reappeared")

    print("PASS: O013-LI-U032 isolated complete Section 4.8 candidate")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 104 environment markers, 10 labels, 20 references, "
        f"6 citations, 7 indexes, {len(source_math)} protected math zones, "
        f"11 diagrams / 28 arrows"
    )
    print(
        "content: 0 exercises, 0 hints, 0 solutions, 0 Han residue; "
        "13 protected-text localizations; 4 citation-locator localizations; "
        "2 declared source corrections; 2 target-only digital reflows"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
