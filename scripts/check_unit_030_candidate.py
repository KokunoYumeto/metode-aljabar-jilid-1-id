#!/usr/bin/env python3
"""Fail-closed admission checker for isolated Unit 030.

The checker binds the complete frozen authority file, the exact Section 4.6
slice, the isolated Indonesian candidate, record-level TeX topology, protected
mathematics and diagrams, identifiers, references, indexes, controlled terms,
two protected-text localizations, and one declared relation repair.
"""

from __future__ import annotations

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
    / "chapter4.tex"
)
CANDIDATE = (
    ROOT
    / "build"
    / "unit-030-candidate"
    / "chapter4-group-composition-series-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 796
SOURCE_END = 935
SLICE_RECORDS = 140
SLICE_BYTES = 7_981
SLICE_SHA256 = "7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1"

CANDIDATE_BYTES = 10_044
CANDIDATE_SHA256 = "7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b"
CANDIDATE_RECORDS = 139

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
    r"\\begin\{(align\*?|gather\*?|gather|equation\*?|tikzcd)\}"
    r"(.*?)\\end\{\1\}",
    re.DOTALL,
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
    found: list[tuple[str, ...] | str] = []
    for match in regex.finditer(text):
        groups = match.groups()
        found.append(groups if len(groups) > 1 else groups[0])
    return found


def index_signature(text: str) -> list[tuple[str, str | None]]:
    return [
        (match.group(1) or "main", (match.group(2) or "").removesuffix("@") or None)
        for match in INDEX_HEAD_RE.finditer(text)
    ]


def normalize_authority_line(text: str, absolute_line: int) -> str:
    """Normalize only two localizations and the declared line-895 repair."""

    if absolute_line == 836:
        text = text.replace(r"\text{子群}", r"\text{subgrup}")
    if absolute_line == 839:
        text = text.replace(r"\text{正规子群}", r"\text{subgrup normal}")
    if absolute_line == 895:
        text = text.replace(
            r"\supset \cdots G_{i, s}",
            r"\supset \cdots \supset G_{i, s}",
        )
    return text


def structural_signature(line: str) -> tuple[object, ...]:
    return (
        tuple(ENV_RE.findall(line)),
        tuple(LABEL_RE.findall(line)),
        tuple(REF_RE.findall(line)),
        tuple(CITE_RE.findall(line)),
        tuple(stream or "main" for stream in INDEX_RE.findall(line)),
        line.count("\\["),
        line.count("\\]"),
        len(re.findall(r"(?<!\\)\$", line)),
        line.count("&"),
        line.count("\\\\"),
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
        fail("authority lines 796-935 identity drift")
    if source_slice_lines[-1] != "":
        fail("authority line 935 must remain the blank section boundary")
    if source_lines[SOURCE_END] != (
        r"\section{可解群与幂零群}\label{sec:solvable-groups}"
    ):
        fail("next boundary at authority line 936 drift")

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
        r"\section{Deret Komposisi Grup}\label{sec:composition-series-grp}"
    ):
        fail("candidate opening boundary drift")
    if candidate_lines[-1] != (
        "Kita akan mendeskripsikan struktur grup abelian berhingga secara "
        "terperinci dalam Korolari \\ref{prop:finite-abelian-structure}."
    ):
        fail("candidate closing boundary drift")
    if r"\section{Grup Terpecahkan dan Grup Nilpoten}" in candidate_text:
        fail("Section 4.7 crossed into isolated candidate")

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
    if candidate_text.count("{") != candidate_text.count("}"):
        fail("candidate brace balance failure")

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
    if index_signature(substantive_source_text) != index_signature(candidate_text):
        fail("index stream or sort-key topology drift")

    normalized_source_lines: list[str] = []
    for offset, (source_line, candidate_line) in enumerate(
        zip(substantive_source_lines, candidate_lines, strict=True)
    ):
        absolute_line = SOURCE_START + offset
        normalized_source_line = normalize_authority_line(source_line, absolute_line)
        normalized_source_lines.append(normalized_source_line)
        if structural_signature(normalized_source_line) != structural_signature(candidate_line):
            fail(f"per-record TeX topology drift at authority line {absolute_line}")
        source_commands = COMMAND_RE.findall(normalized_source_line)
        candidate_commands = COMMAND_RE.findall(candidate_line)
        if source_commands != candidate_commands:
            fail(
                f"ordered TeX command drift at authority line {absolute_line}: "
                f"{source_commands!r} != {candidate_commands!r}"
            )

    normalized_source_text = "\n".join(normalized_source_lines) + "\n"
    source_math_zones = math_zones(normalized_source_text)
    candidate_math_zones = math_zones(candidate_text)
    if source_math_zones != candidate_math_zones:
        if len(source_math_zones) != len(candidate_math_zones):
            fail(
                "protected mathematical-zone count drift: "
                f"{len(source_math_zones)} != {len(candidate_math_zones)}"
            )
        for zone_number, (source_zone, candidate_zone) in enumerate(
            zip(source_math_zones, candidate_math_zones, strict=True), start=1
        ):
            if source_zone != candidate_zone:
                fail(
                    f"protected mathematical zone {zone_number} drift: "
                    f"{source_zone!r} != {candidate_zone!r}"
                )
        fail("protected mathematical zones drift")

    localized_fragments = {
        836: r"\text{subgrup}",
        839: r"\text{subgrup normal}",
    }
    for absolute_line, fragment in localized_fragments.items():
        if fragment not in candidate_lines[absolute_line - SOURCE_START]:
            fail(f"protected-text localization drift at authority line {absolute_line}")
    if r"\text{子群}" in candidate_text or r"\text{正规子群}" in candidate_text:
        fail("unlocalized protected diagram text remains")

    correction_line = candidate_lines[895 - SOURCE_START]
    corrected_fragment = r"\supset \cdots \supset G_{i, s}"
    defective_fragment = r"\supset \cdots G_{i, s}"
    if corrected_fragment not in correction_line:
        fail("declared relation repair missing at authority line 895")
    if defective_fragment in correction_line:
        fail("uncorrected relation omission remains at authority line 895")

    required_terminology = {
        "group": "grup",
        "exact sequence": "barisan eksak",
        "abelian group": "grup abelian",
    }
    with TERMINOLOGY.open("r", encoding="utf-8-sig", newline="") as handle:
        admitted = {
            row["source_term"]: row["target_term"]
            for row in csv.DictReader(handle)
            if row.get("status") == "admitted"
        }
    for source_term, target_term in required_terminology.items():
        if admitted.get(source_term) != target_term:
            fail(f"controlled terminology drift: {source_term!r}")
        if target_term not in candidate_text:
            fail(f"controlled target term absent from candidate: {target_term!r}")

    required_semantic_anchors = (
        "deret normal",
        "deret sentral",
        "deret komposisi",
        "subkuosien",
        "penghalusan sejati",
        "Lema Zassenhaus",
        "Teorema Penghalusan Schreier",
        "Teorema Jordan--Hölder",
        "faktor komposisi",
        "multiplikitas",
        "barisan eksak",
        "grup abelian berhingga",
    )
    for anchor in required_semantic_anchors:
        if anchor not in candidate_text:
            fail(f"semantic anchor absent: {anchor!r}")

    for absent_environment in ("exercise", "hint", "solution"):
        if f"\\begin{{{absent_environment}}}" in candidate_text:
            fail(f"unexpected {absent_environment} environment in source-bounded unit")
    if candidate_text.count(r"\begin{tikzcd}") != 6:
        fail("tikzcd environment count drift")
    if candidate_text.count(r"\arrow") != 23:
        fail("diagram arrow count drift")

    print("PASS unit-030 candidate admission")
    print(f"authority={SOURCE.name}:{SOURCE_START}-{SOURCE_END}")
    print(f"authority_slice_records={SLICE_RECORDS}")
    print(f"authority_slice_bytes={SLICE_BYTES}")
    print(f"authority_slice_sha256={SLICE_SHA256}")
    print(f"candidate_records={CANDIDATE_RECORDS}")
    print(f"candidate_bytes={CANDIDATE_BYTES}")
    print(f"candidate_sha256={CANDIDATE_SHA256}")
    print(f"environment_markers={len(ordered(ENV_RE, candidate_text))}")
    print(f"labels={len(ordered(LABEL_RE, candidate_text))}")
    print(f"refs_eqrefs={len(ordered(REF_RE, candidate_text))}")
    print(f"citations={len(ordered(CITE_RE, candidate_text))}")
    print(f"indexes={len(ordered(INDEX_RE, candidate_text))}")
    print(f"protected_math_zones={len(candidate_math_zones)}")
    print(f"tikzcd_environments={candidate_text.count(r'\begin{tikzcd}')}")
    print(f"diagram_arrows={candidate_text.count(r'\arrow')}")
    print("exercises=0")
    print("hints=0")
    print("han_residue=0")
    print("declared_source_corrections=1")
    print("protected_text_localizations=2")
    print("next_boundary=chapter4.tex:936")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, OSError) as exc:
        print(f"FAIL unit-030 candidate admission: {exc}", file=sys.stderr)
        raise SystemExit(1)
