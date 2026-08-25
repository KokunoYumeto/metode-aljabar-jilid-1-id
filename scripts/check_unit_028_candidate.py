#!/usr/bin/env python3
"""Fail-closed admission checker for isolated Unit 028.

This read-only checker binds the complete frozen authority file, the exact
Section 4.4 slice, the candidate bytes, record-by-record TeX topology,
protected mathematical zones, identifiers, citations, index streams/sort
keys, controlled terminology, and the one declared source correction.  The
three explicitly normalized ``\\text{...}`` changes are language localization,
not mathematical corrections.
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
    / "unit-028-candidate"
    / "chapter4-group-actions-counting-id.tex"
)
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 518
SOURCE_END = 665
SLICE_RECORDS = 148
SLICE_BYTES = 10_550
SLICE_SHA256 = "af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db"

CANDIDATE_BYTES = 13_017
CANDIDATE_SHA256 = "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd"
CANDIDATE_RECORDS = 147

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
    r"\\begin\{(align\*?|gather\*?|tikzcd)\}(.*?)\\end\{\1\}", re.DOTALL
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
    """Normalize only one correction and three protected-text localizations."""

    if absolute_line == 533:
        text = text.replace(
            r'M_1 \arrow[yshift=0.5ex, r, "f"] & M_2',
            r'X \arrow[yshift=0.5ex, r, "f"] & Y',
        )
    if absolute_line == 535:
        text = text.replace(r"\identity_{M_2}", r"\identity_Y")
        text = text.replace(r"\identity_{M_1}", r"\identity_X")
    if absolute_line == 557:
        text = text.replace(r"\text{映射}", r"\text{pemetaan}")
    if absolute_line == 610:
        text = text.replace(r"\text{相异元}", r"\text{unsur-unsur berbeda}")
    if absolute_line == 646:
        text = text.replace(r"\text{ 同构 }", r"\text{ isomorfisme }")
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
        fail("authority lines 518-665 identity drift")
    if source_slice_lines[-1] != "":
        fail("authority line 665 must remain the blank section boundary")
    if source_lines[SOURCE_END] != r"\section{Sylow 定理}\label{sec:Sylow}":
        fail("next boundary at authority line 666 drift")

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
        r"\section{Aksi Grup dan Prinsip Pencacahan}\label{sec:group-action}"
    ):
        fail("candidate opening boundary drift")
    if candidate_lines[-1] != r"\end{proof}":
        fail("candidate closing boundary drift")
    if r"\section{Teorema Sylow}\label{sec:Sylow}" in candidate_text:
        fail("Section 4.5 crossed into isolated candidate")

    if HAN_RE.search(candidate_text):
        fail("unauthorized Han residue in candidate")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("unauthorized Chinese punctuation residue in candidate")
    if "\u200b" in candidate_text or "\ufeff" in candidate_text:
        fail("invisible Unicode control residue in candidate")
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

    correction_fragments = {
        533: r'X \arrow[yshift=0.5ex, r, "f"] & Y',
        535: r"$fg = \identity_Y$, $gf = \identity_X$",
    }
    forbidden_source_fragments = {
        533: r'M_1 \arrow[yshift=0.5ex, r, "f"] & M_2',
        535: r"$fg = \identity_{M_2}$, $gf = \identity_{M_1}$",
    }
    for absolute_line, fragment in correction_fragments.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if fragment not in candidate_line:
            fail(f"declared correction fragment missing at authority line {absolute_line}")
        if forbidden_source_fragments[absolute_line] in candidate_line:
            fail(f"uncorrected source defect remains at authority line {absolute_line}")

    localized_math_fragments = {
        557: r"\text{pemetaan}",
        610: r"\text{unsur-unsur berbeda}",
        646: r"\text{ isomorfisme }",
    }
    for absolute_line, fragment in localized_math_fragments.items():
        if fragment not in candidate_lines[absolute_line - SOURCE_START]:
            fail(f"protected-text localization drift at authority line {absolute_line}")

    required_terminology = {
        "group": "grup",
        "category": "kategori",
        "homomorphism": "homomorfisme",
        "isomorphism": "isomorfisme",
        "cardinal": "kardinal",
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
        "aksi monoid",
        "pemetaan aksi",
        "aksi trivial",
        "ekuivarian",
        "aksi kiri",
        "aksi kanan",
        "titik tetap",
        "orbit",
        "stabilisator",
        "dekomposisi orbit",
        "setia",
        "bebas atau semireguler",
        "transitif",
        "ruang homogen",
        "torsor",
        "aksi translasi",
        "aksi konjugasi",
        "kelas konjugasi",
        "sentralisator",
        "pusat",
        "bitorsor",
    )
    for anchor in required_semantic_anchors:
        if anchor not in candidate_text:
            fail(f"semantic anchor absent: {anchor!r}")

    for absent_environment in ("exercise", "hint", "solution"):
        if f"\\begin{{{absent_environment}}}" in candidate_text:
            fail(f"unexpected {absent_environment} environment in source-bounded unit")
    if candidate_text.count(r"\arrow") != 2:
        fail("tikzcd arrow count drift")

    print("PASS unit-028 candidate admission")
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
    print(f"tikzcd_arrows={candidate_text.count(r'\arrow')}")
    print("exercises=0")
    print("hints=0")
    print("han_residue=0")
    print("declared_source_corrections=1")
    print("protected_text_localizations=3")
    print("next_boundary=chapter4.tex:666")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, OSError) as exc:
        print(f"FAIL unit-028 candidate admission: {exc}", file=sys.stderr)
        raise SystemExit(1)
