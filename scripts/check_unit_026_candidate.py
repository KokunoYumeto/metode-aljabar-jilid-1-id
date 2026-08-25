#!/usr/bin/env python3
"""Fail-closed admission checker for the isolated Unit 026 translation candidate.

The checker is deliberately read-only.  It binds the frozen authority slice,
the candidate bytes, structural TeX topology, protected mathematical zones,
cross-reference identifiers, and the controlled terminology snapshot used by
the translator.  The mathematical-token corrections are normalized only at
their exact source records; the prose-level correction is pinned by an exact
candidate fragment.  Every other protected mathematical fragment must remain
identical.
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
CANDIDATE = ROOT / "build" / "unit-026-candidate" / "chapter4-homomorphisms-quotients-id.tex"
TERMINOLOGY = ROOT / "00_control" / "TERMINOLOGY.id-ID.csv"

SOURCE_BYTES = 154_744
SOURCE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START = 177
SOURCE_END = 364
SLICE_RECORDS = 188
SLICE_BYTES = 15_360
SLICE_SHA256 = "4377d6a31512cf3e2a56f4e8e1c3417b62ff1a6468eb85629c8d9867a4f975f8"

CANDIDATE_BYTES = 19_424
CANDIDATE_SHA256 = "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87"
CANDIDATE_RECORDS = 187

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


def apply_declared_source_corrections(text: str, absolute_line: int) -> str:
    """Normalize only the separately documented high-confidence defects."""

    if absolute_line in {301, 308, 312}:
        text = text.replace("H/N \\cap H", "H/(N \\cap H)")
    if absolute_line == 358:
        text = text.replace("\\phi: M \\to N", "\\varphi: M \\to N")
    if absolute_line == 320:
        text = text.replace(
            "设 $m \\mid n$.",
            "设 $n \\ne 0$ dan $m \\mid n$.",
        )
        text = text.replace(
            "$\\frac{n}{m}$ 阶",
            "$\\left|\\frac{n}{m}\\right|$ 阶",
        )
        text += (
            " Jika $n=0$, subgrup $m\\Z/0\\Z=m\\Z$ merupakan grup siklik tak hingga "
            "untuk $m\\ne0$, sedangkan $0\\Z/0\\Z$ merupakan grup trivial."
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
    # Indonesian prose inside \text{...} is the only deliberately translated
    # material inside the protected diagram/math zones in this slice.
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\\text\{[^{}]*\}", r"\\text{<TEXT>}", text)
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
        fail("authority lines 177-364 identity drift")

    candidate_lines = records(candidate_text)
    if not candidate_text.endswith("\n"):
        fail("candidate must end with exactly one LF record terminator")
    # Authority record 364 is a boundary-only blank record and is omitted from
    # the isolated candidate; all 187 substantive source records remain 1:1.
    if candidate_text.endswith("\n\n"):
        fail("candidate has an unauthorized extra blank record at EOF")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if len(candidate_lines) != CANDIDATE_RECORDS:
        fail(f"candidate record count drift: {len(candidate_lines)}")

    if HAN_RE.search(candidate_text):
        fail("unauthorized Han residue in candidate")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("unauthorized Chinese punctuation residue in candidate")
    if re.search(r"\b(?:TODO|TBD|FIXME|TRANSLATE)\b", candidate_text, re.IGNORECASE):
        fail("placeholder residue in candidate")

    if ordered(ENV_RE, source_slice_text) != ordered(ENV_RE, candidate_text):
        fail("ordered begin/end environment topology drift")
    if ordered(LABEL_RE, source_slice_text) != ordered(LABEL_RE, candidate_text):
        fail("ordered label identifiers drift")
    if ordered(REF_RE, source_slice_text) != ordered(REF_RE, candidate_text):
        fail("ordered ref/eqref identifiers drift")
    if ordered(CITE_RE, source_slice_text) != ordered(CITE_RE, candidate_text):
        fail("ordered citation keys drift")
    if ordered(INDEX_RE, source_slice_text) != ordered(INDEX_RE, candidate_text):
        fail("index stream/count topology drift")

    for offset, (source_line, candidate_line) in enumerate(
        zip(source_slice_lines[:-1], candidate_lines, strict=True)
    ):
        absolute_line = SOURCE_START + offset
        normalized_source_line = apply_declared_source_corrections(source_line, absolute_line)
        if structural_signature(normalized_source_line) != structural_signature(candidate_line):
            fail(f"per-record TeX topology drift at authority line {absolute_line}")
        source_commands = COMMAND_RE.findall(normalized_source_line)
        candidate_commands = COMMAND_RE.findall(candidate_line)
        if source_commands != candidate_commands:
            fail(
                f"ordered TeX command drift at authority line {absolute_line}: "
                f"{source_commands!r} != {candidate_commands!r}"
            )

    normalized_source_lines = [
        apply_declared_source_corrections(line, SOURCE_START + offset)
        for offset, line in enumerate(source_slice_lines[:-1])
    ]
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
        fail("protected inline/display/environment mathematical zones drift")

    # normalize_math deliberately permits translated prose in \text{...} but
    # must not erase the four mathematical order operators in this slice.
    expected_ord_by_line = {318: 1, 326: 1, 329: 2}
    for absolute_line, expected_count in expected_ord_by_line.items():
        source_line = source_slice_lines[absolute_line - SOURCE_START]
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if source_line.count(r"\text{ord}") != expected_count:
            fail(f"authority order-operator count drift at line {absolute_line}")
        if candidate_line.count(r"\text{ord}") != expected_count:
            fail(f"candidate order-operator count drift at authority line {absolute_line}")
    if r"\ord" in candidate_text:
        fail("undeclared order macro introduced in candidate")

    # Pin the corrections at their exact records; these assertions prevent the
    # broad normalization above from licensing an unrelated mathematical edit.
    exact_corrections = {
        231: "khusus dalam kasus grup, invers setiap unsur diberikan oleh",
        301: r"\[ \theta: H/(N \cap H) \to HN/N \]",
        308: r"\psi: HN/N & \longrightarrow H/(N \cap H) \\",
        312: r"$H/(N \cap H) \rightiso HN/N$",
        320: r"misalkan $n \ne 0$ dan $m \mid n$",
        358: r"$\varphi: M \to N$",
    }
    for absolute_line, fragment in exact_corrections.items():
        candidate_line = candidate_lines[absolute_line - SOURCE_START]
        if fragment not in candidate_line:
            fail(f"declared correction missing at authority line {absolute_line}")

    required_terminology = {
        "group": "grup",
        "homomorphism": "homomorfisme",
        "isomorphism": "isomorfisme",
        "endomorphism": "endomorfisme",
        "automorphism": "automorfisme",
        "quotient set": "himpunan hasil bagi",
        "equivalence class": "kelas ekuivalensi",
        "universal property": "sifat universal",
        "functor": "fungtor",
        "forgetful functor": "fungtor pelupa",
        "adjunction pair": "pasangan adjoin",
        "abelian group": "grup abelian",
        "full subcategory": "subkategori penuh",
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
        "homomorfisme trivial",
        "automorfisme dalam",
        "grup automorfisme",
        "homomorfisme hasil bagi",
        "grup hasil bagi",
        "subgrup normal",
        "grup siklik",
        "grup Grothendieck",
        "hukum pembatalan",
        "kategori monoid komutatif",
    )
    for anchor in required_semantic_anchors:
        if anchor not in candidate_text:
            fail(f"semantic anchor absent: {anchor!r}")

    print("PASS unit-026 candidate admission")
    print(f"authority={SOURCE.name}:{SOURCE_START}-{SOURCE_END}")
    print(f"authority_slice_records={SLICE_RECORDS}")
    print(f"authority_slice_bytes={SLICE_BYTES}")
    print(f"authority_slice_sha256={SLICE_SHA256}")
    print(f"candidate_records={CANDIDATE_RECORDS}")
    print(f"candidate_bytes={CANDIDATE_BYTES}")
    print(f"candidate_sha256={CANDIDATE_SHA256}")
    print(f"environments={len(ordered(ENV_RE, candidate_text))}")
    print(f"labels={len(ordered(LABEL_RE, candidate_text))}")
    print(f"refs_eqrefs={len(ordered(REF_RE, candidate_text))}")
    print(f"citations={len(ordered(CITE_RE, candidate_text))}")
    print(f"indexes={len(ordered(INDEX_RE, candidate_text))}")
    print("han_residue=0")
    print("declared_source_corrections=4")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL unit-026 candidate admission: {exc}", file=sys.stderr)
        raise SystemExit(1)
