#!/usr/bin/env python3
"""Fail-closed checker for the isolated O013-LI-U034 translation.

The checker binds Li's frozen Chapter 4 authority, the complete Section 4.10
boundary, the Indonesian candidate, record-level TeX topology and protected
mathematics, localized protected text and indexes, one declared source
correction, and one target-only digital reflow. It is read-only.
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
    / "unit-034-candidate"
    / "chapter4-group-limits-completions-id.tex"
)

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 1_609
SOURCE_END = 1_744
SLICE_RECORDS = 136
SLICE_BYTES = 15_005
SLICE_SHA256 = "9c677e157431515caf095783906a06ac143e2c25870c831a3853002f00a3e5ab"

CANDIDATE_BYTES = 19_019
CANDIDATE_SHA256 = "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62"
CANDIDATE_RECORDS = 135

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
    r"multline\*?|pmatrix|tikzcd|tikzpicture)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)

PROTECTED_TEXT_REPLACEMENTS = {
    1630: (
        (r"\text{子集}", r"\text{himpunan bagian}"),
        (r"\text{为开}", r"\text{terbuka}"),
    ),
    1636: (
        (r"\text{为闭子集}", r"\text{himpunan bagian tertutup}"),
        (r"\text{开邻域}", r"\text{lingkungan terbuka}"),
    ),
    1641: (
        (
            r"x \;\text{的所有邻域}",
            r"\text{semua lingkungan dari } x",
        ),
    ),
    1661: (
        (r"\text{ 有限子集}", r"\text{himpunan bagian berhingga}"),
        (r"\text{开子集}", r"\text{himpunan bagian terbuka}"),
    ),
    1736: (
        (r"\text{乘以}", r"\text{dikalikan dengan}"),
        (r"\text{商}", r"\text{hasil bagi}"),
    ),
}

INDEX_LOCALIZATIONS = (
    r"\index{poset terarah ke atas (filtered poset)}",
    r"\index{grup topologis (topological group)}",
    r"\index{grup profinit (pro-finite group)}",
    r"\index{pelengkapan (completion)}",
    r"\index[sym1]{Z_p@$\Z_p$}",
    r"\index{modul Tate (Tate module)}",
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

    if absolute_line == 1720:
        source_fragment = r")_{i \geq 1}$"
        target_fragment = r")_{i \geq 0}$"
        if source_fragment not in text:
            fail("p-adic family-index source defect drift at authority line 1720")
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
    text = text.replace(r"\begin{aligned}", "").replace(r"\end{aligned}", "")
    text = text.replace(r"\\", "").replace("&", "")
    return re.sub(r"\s+", "", text)


def remove_declared_digital_reflow(text: str) -> str:
    reflowed = r"\[ \begin{aligned} \mathcal{U}_{I_0} &= \bigcap_{i \in I_0} p_i^{-1}(U_i), \qquad\\ I_0 &\subset I: \; \text{himpunan bagian berhingga}, \quad\\ U_i &\ni 1: \; \text{himpunan bagian terbuka} \end{aligned} \]"
    normalized = r"\[ \mathcal{U}_{I_0} = \bigcap_{i \in I_0} p_i^{-1}(U_i), \qquad I_0 \subset I: \; \text{himpunan bagian berhingga}, \quad U_i \ni 1: \; \text{himpunan bagian terbuka} \]"
    if text.count(reflowed) != 1:
        fail("declared Unit 034 digital reflow count drift")
    return text.replace(reflowed, normalized)


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
        fail("authority lines 1609-1744 identity drift")
    if source_slice_lines[-1] != "":
        fail("authority line 1744 must remain the blank section boundary")
    if source_lines[SOURCE_END] != r"\section{范畴中的群}\label{sec:group-in-cat}":
        fail("next boundary at authority line 1745 drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")
    if candidate_lines[0] != r"\section{Limit dan Pelengkapan Grup}\label{sec:group-limit}":
        fail("candidate opening boundary drift")
    if candidate_lines[-1] != r"\end{example}":
        fail("candidate closing boundary drift")
    if r"\section{Grup dalam Kategori}" in candidate_text:
        fail("Section 4.11 crossed into isolated candidate")

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
    candidate_topology_text = remove_declared_digital_reflow(candidate_text)
    candidate_topology_lines = candidate_topology_text.splitlines()
    if ordered(ENV_RE, substantive_source_text) != ordered(ENV_RE, candidate_topology_text):
        fail("ordered begin/end environment topology drift")
    if ordered(LABEL_RE, substantive_source_text) != ordered(LABEL_RE, candidate_topology_text):
        fail("ordered label identifiers drift")
    if ordered(REF_RE, substantive_source_text) != ordered(REF_RE, candidate_topology_text):
        fail("ordered ref/eqref identifiers drift")
    if ordered(CITE_RE, substantive_source_text) != ordered(CITE_RE, candidate_topology_text):
        fail("ordered citation keys drift")
    if ordered(INDEX_STREAM_RE, substantive_source_text) != ordered(
        INDEX_STREAM_RE, candidate_topology_text
    ):
        fail("ordered index-stream topology drift")

    normalized_source_lines: list[str] = []
    for offset, (source_line, candidate_line) in enumerate(
        zip(substantive_source_lines, candidate_topology_lines, strict=True)
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
    candidate_math = math_zones(candidate_topology_text)
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
        "align*": 1,
        "aligned": 1,
        "compactitem": 1,
        "definition": 4,
        "enumerate": 1,
        "equation": 1,
        "equation*": 1,
        "example": 2,
        "lemma": 3,
        "proof": 5,
        "remark": 2,
        "theorem": 2,
        "tikzcd": 1,
    }
    actual_begins = collections.Counter(
        environment
        for marker, environment in ENV_RE.findall(candidate_topology_text)
        if marker == "begin"
    )
    if actual_begins != collections.Counter(expected_begins):
        fail(f"environment census drift: {dict(actual_begins)!r}")
    if len(ENV_RE.findall(candidate_topology_text)) != 50:
        fail("environment marker count drift")
    if len(LABEL_RE.findall(candidate_text)) != 11:
        fail("label count drift")
    if len(REF_RE.findall(candidate_text)) != 16:
        fail("reference count drift")
    if len(CITE_RE.findall(candidate_text)) != 6:
        fail("citation count drift")
    if len(INDEX_STREAM_RE.findall(candidate_text)) != 6:
        fail("index count drift")
    for localized_index in INDEX_LOCALIZATIONS:
        if candidate_text.count(localized_index) != 1:
            fail(f"localized index missing or duplicated: {localized_index}")
    if candidate_text.count(r"\begin{tikzcd}") != 1:
        fail("tikzcd census drift")
    if len(re.findall(r"\\arrow", candidate_text)) != 12:
        fail("diagram-arrow census drift")
    if len(re.findall(r"(?<!\\)\$", candidate_text)) != 534:
        fail("unescaped dollar-delimiter census drift")
    if candidate_topology_text.count("{") != 257 or candidate_topology_text.count("}") != 257:
        fail("raw brace census drift")
    if re.search(r"\\begin\{(?:exercise|hint|solution)\}", candidate_text):
        fail("out-of-scope exercise, hint or solution environment appeared")
    if any(line.lstrip().startswith("%") for line in candidate_lines):
        fail("source-disabled/comment topology appeared in candidate")

    localization_count = sum(
        len(replacements) for replacements in PROTECTED_TEXT_REPLACEMENTS.values()
    )
    if localization_count != 9:
        fail("declared protected-text localization census drift")
    for absolute_line, replacements in PROTECTED_TEXT_REPLACEMENTS.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        for _, target_fragment in replacements:
            if candidate_line.count(target_fragment) != 1:
                fail(
                    f"protected-text localization drift at authority line {absolute_line}: "
                    f"{target_fragment!r}"
                )

    line_1720 = candidate_lines[1720 - SOURCE_START]
    corrected_index = r")_{i \geq 0}$"
    defective_index = r")_{i \geq 1}$"
    if corrected_index not in line_1720 or defective_index in line_1720:
        fail("O013-LI-U034-COR-001 p-adic family-index repair drift")

    required_anchors = (
        "poset terarah ke atas",
        "limit proyektif",
        "grup topologis",
        "basis lingkungan",
        "topologi produk",
        "ruang Hausdorff kompak",
        "grup profinit",
        "inklusi terbalik",
        "tak terhubung total",
        "pelengkapan grup",
        "barisan Cauchy",
        "topologi diskret",
        "bilangan bulat $p$-adik",
        "modul Tate rasional",
        "kurva eliptik",
        "teori homologi",
    )
    candidate_casefold = candidate_text.casefold()
    for anchor in required_anchors:
        if anchor.casefold() not in candidate_casefold:
            fail(f"required semantic/terminological anchor missing: {anchor!r}")
    if "antarkelompok" in candidate_text or "kelompok topologis" in candidate_text:
        fail("uncontrolled Indonesian group terminology appeared")

    print("PASS: O013-LI-U034 isolated complete Section 4.10 candidate")
    print(
        f"source slice: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, "
        f"sha256={SLICE_SHA256}"
    )
    print(
        f"candidate: {CANDIDATE_RECORDS} records, {CANDIDATE_BYTES} bytes, "
        f"sha256={CANDIDATE_SHA256}"
    )
    print(
        f"topology: 50 environment markers, 11 labels, 16 references, "
        f"6 citations, 6 indexes, {len(source_math)} protected math zones, "
        "1 diagram / 12 arrows"
    )
    print(
        "content: 0 exercises, 0 hints, 0 solutions, 0 Han residue; "
        "9 protected-text localizations; 6 localized indexes; "
        "1 declared source correction; 1 target-only digital reflow"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
