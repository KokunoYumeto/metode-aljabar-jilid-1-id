#!/usr/bin/env python3
"""Fail-closed isolated checker for O013-LI-U043 (Chapter 5 tail)."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter5.tex"
)
CANDIDATE = Path(__file__).with_name("chapter5-symmetric-polynomials-exercises-id.tex")

AUTHORITY_BYTES = 122_998
AUTHORITY_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
AUTHORITY_RECORDS = 1_382
SOURCE_START = 1_184
SOURCE_END = 1_382
SLICE_RECORDS = 199
SLICE_BYTES = 18_389
SLICE_SHA256 = "755bb123580e5f50e0fff03175117190f1490e4e41ffaf2a6e0df2df9190565f"
CANDIDATE_BYTES = 22_558
CANDIDATE_SHA256 = "5318c2433ca4784d1fbf64a86989bd3a3a007a10ed00cb6e0ae7f46a37122a2d"

ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[([^\]]*)\])?\{([^{}]+)\}")
COMMAND_RE = re.compile(r"\\([A-Za-z@]+|.)")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CHINESE_PUNCT_RE = re.compile(r"[，。；：！？“”‘’]")
PLACEHOLDER_RE = re.compile(r"(?i)(?:TODO|FIXME|TBD|PLACEHOLDER|LOREM)")
MATH_ENVS = ("align", "align*", "gather", "gather*", "equation", "equation*", "cases", "ytableau")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        fail(f"UTF-8 BOM is forbidden: {path}")
    if b"\r" in data:
        fail(f"CR bytes are forbidden: {path}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"invalid UTF-8 in {path}: {exc}")
    return data, text


def records(text: str) -> list[str]:
    return text.splitlines()


def command_multisets_by_record(lines: list[str]) -> list[Counter[str]]:
    return [Counter(COMMAND_RE.findall(line)) for line in lines]


def index_commands(text: str) -> list[tuple[str | None, str]]:
    found: list[tuple[str | None, str]] = []
    pos = 0
    while True:
        start = text.find(r"\index", pos)
        if start < 0:
            return found
        cursor = start + len(r"\index")
        stream: str | None = None
        if cursor < len(text) and text[cursor] == "[":
            close = text.find("]", cursor + 1)
            if close < 0:
                fail("unterminated index stream option")
            stream = text[cursor + 1 : close]
            cursor = close + 1
        if cursor >= len(text) or text[cursor] != "{":
            fail("malformed index command")
        depth = 1
        body_start = cursor + 1
        cursor += 1
        while cursor < len(text) and depth:
            if text[cursor] == "{" and (cursor == 0 or text[cursor - 1] != "\\"):
                depth += 1
            elif text[cursor] == "}" and (cursor == 0 or text[cursor - 1] != "\\"):
                depth -= 1
            cursor += 1
        if depth:
            fail("unterminated index body")
        found.append((stream, text[body_start : cursor - 1]))
        pos = cursor


def index_skeleton(indexes: list[tuple[str | None, str]]) -> list[tuple[str | None, bool, str | None]]:
    result: list[tuple[str | None, bool, str | None]] = []
    for stream, body in indexes:
        has_sort = "@" in body
        sort_key = body.split("@", 1)[0] if has_sort else None
        result.append((stream, has_sort, sort_key))
    return result


def normalize_text_commands(zone: str) -> str:
    previous = None
    while previous != zone:
        previous = zone
        zone = re.sub(r"\\text\{[^{}]*\}", r"\\text{#}", zone)
    return re.sub(r"\s+", "", zone)


def dollar_math(text: str) -> list[str]:
    zones: list[str] = []
    cursor = 0
    while cursor < len(text):
        if text[cursor] != "$" or (cursor > 0 and text[cursor - 1] == "\\"):
            cursor += 1
            continue
        delimiter = "$$" if text.startswith("$$", cursor) else "$"
        start = cursor + len(delimiter)
        cursor = start
        while cursor < len(text):
            if text.startswith(delimiter, cursor) and (cursor == 0 or text[cursor - 1] != "\\"):
                zones.append(text[start:cursor])
                cursor += len(delimiter)
                break
            cursor += 1
        else:
            fail("unbalanced dollar mathematics")
    return zones


def display_math(text: str) -> list[str]:
    return re.findall(r"\\\[(.*?)\\\]", text, flags=re.DOTALL)


def environment_math(text: str) -> list[str]:
    zones: list[str] = []
    for env in MATH_ENVS:
        pattern = rf"\\begin\{{{re.escape(env)}\}}(.*?)\\end\{{{re.escape(env)}\}}"
        zones.extend(re.findall(pattern, text, flags=re.DOTALL))
    return zones


def normalized_math(text: str) -> list[str]:
    return [
        normalize_text_commands(zone)
        for zone in dollar_math(text) + display_math(text) + environment_math(text)
    ]


def inline_math_multisets_by_record(lines: list[str]) -> list[Counter[str]]:
    return [Counter(normalize_text_commands(zone) for zone in dollar_math(line)) for line in lines]


def normalized_block_math(text: str) -> list[str]:
    return [normalize_text_commands(zone) for zone in display_math(text) + environment_math(text)]


def apply_declared_source_corrections(text: str) -> str:
    corrections = (
        (r"1 \leq \lambda_i \leq n", r"1 \leq i \leq r"),
        (r"0 \leq i < k", r"1 \leq i < k"),
    )
    for old, new in corrections:
        if text.count(old) != 1:
            fail(f"declared source correction anchor drift: {old!r}")
        text = text.replace(old, new, 1)
    return text


def main() -> None:
    authority_data, authority_text = strict_text(AUTHORITY)
    candidate_data, candidate_text = strict_text(CANDIDATE)
    if len(authority_data) != AUTHORITY_BYTES or digest(authority_data) != AUTHORITY_SHA256:
        fail("frozen Chapter 5 authority identity drift")
    authority_lines = records(authority_text)
    if len(authority_lines) != AUTHORITY_RECORDS:
        fail("authority record-count drift")

    source_lines = authority_lines[SOURCE_START - 1 : SOURCE_END]
    source_text = "\n".join(source_lines) + "\n"
    source_data = source_text.encode("utf-8")
    if len(source_lines) != SLICE_RECORDS:
        fail("source-slice record-count drift")
    if len(source_data) != SLICE_BYTES or digest(source_data) != SLICE_SHA256:
        fail("source-slice identity drift")
    if authority_lines[SOURCE_START - 2] != "":
        fail("opening blank separator drift")
    if source_lines[0] != r"\section{对称多项式入门}\label{sec:symmetric-poly}":
        fail("source section opening drift")
    if source_lines[-1] != r"\end{Exercises}":
        fail("source exercise closure drift")

    if not candidate_text.endswith("\n") or candidate_text.endswith("\n\n"):
        fail("candidate must end in exactly one LF")
    candidate_lines = records(candidate_text)
    if len(candidate_lines) != SLICE_RECORDS:
        fail("candidate must preserve all 199 source records")
    if len(candidate_data) != CANDIDATE_BYTES or digest(candidate_data) != CANDIDATE_SHA256:
        fail("candidate byte identity drift")
    if candidate_lines[0] != r"\section{Pengantar Polinomial Simetris}\label{sec:symmetric-poly}":
        fail("localized section opening drift")
    if candidate_lines[-1] != r"\end{Exercises}":
        fail("candidate exercise closure drift")

    corrected_source = apply_declared_source_corrections(source_text)
    source_commands = command_multisets_by_record(records(corrected_source))
    candidate_commands = command_multisets_by_record(candidate_lines)
    if source_commands != candidate_commands:
        differences = [
            SOURCE_START + index
            for index, (source_row, candidate_row) in enumerate(zip(source_commands, candidate_commands))
            if source_row != candidate_row
        ]
        fail(f"per-record TeX command topology drift at authority records {differences[:12]}")
    if ENV_RE.findall(corrected_source) != ENV_RE.findall(candidate_text):
        fail("environment topology drift")
    if LABEL_RE.findall(corrected_source) != LABEL_RE.findall(candidate_text):
        fail("label identifiers drift")
    if REF_RE.findall(corrected_source) != REF_RE.findall(candidate_text):
        fail("reference identifiers drift")
    if CITE_RE.findall(corrected_source) != CITE_RE.findall(candidate_text):
        fail("citation locators or keys drift")

    source_indexes = index_commands(corrected_source)
    candidate_indexes = index_commands(candidate_text)
    if len(source_indexes) != 8 or len(candidate_indexes) != 8:
        fail("index-command census drift")
    expected_candidate_indexes = [
        (None, "duichengduoxiangshi@polinomial simetris (symmetric polynomial)"),
        (None, "Young-tu@diagram Young (Young diagram)"),
        (None, "fenchai@partisi (partition)"),
        (None, "duichengduoxiangshi!elementer (elementary)"),
        (None, "panbieshi@diskriminan (discriminant)"),
        (None, "duichengduoxiangshi!jumlah pangkat (power-sum)"),
        (None, "Rumus Newton"),
        (None, "jiaxingduoxiangshi@polinomial aditif (additive polynomial)"),
    ]
    if candidate_indexes != expected_candidate_indexes:
        fail("localized index stream drift")
    source_inline_math = inline_math_multisets_by_record(records(corrected_source))
    candidate_inline_math = inline_math_multisets_by_record(candidate_lines)
    if source_inline_math != candidate_inline_math:
        differences = [
            SOURCE_START + index
            for index, (source_row, candidate_row) in enumerate(zip(source_inline_math, candidate_inline_math))
            if source_row != candidate_row
        ]
        fail(f"per-record inline mathematical content drift at authority records {differences[:12]}")
    if normalized_block_math(corrected_source) != normalized_block_math(candidate_text):
        fail("display or mathematical-environment content drift")

    source_blank_mask = [not line.strip() for line in source_lines]
    candidate_blank_mask = [not line.strip() for line in candidate_lines]
    if source_blank_mask != candidate_blank_mask:
        fail("blank-record topology drift")
    source_comments = [line.lstrip().startswith("%") for line in source_lines]
    candidate_comments = [line.lstrip().startswith("%") for line in candidate_lines]
    if source_comments != candidate_comments:
        fail("comment-state topology drift")

    if candidate_text.count(r"\item") != 35:
        fail("item census drift")
    if candidate_text.count(r"\begin{Exercises}") != 1 or candidate_text.count(r"\end{Exercises}") != 1:
        fail("Exercises environment drift")
    if candidate_text.count(r"\begin{hint}") != 11 or candidate_text.count(r"\end{hint}") != 11:
        fail("hint topology drift")
    if any(token in candidate_text for token in (r"\begin{solution}", r"\begin{exercise}")):
        fail("unexpected solution or nested exercise environment")
    if HAN_RE.search(candidate_text) or CHINESE_PUNCT_RE.search(candidate_text):
        fail("Chinese-language residue remains")
    if PLACEHOLDER_RE.search(candidate_text):
        fail("placeholder residue remains")
    for forbidden in ("cincin", "lapangan", "kelompok", "variabel", "funktor", "kompletisasi"):
        if forbidden.casefold() in candidate_text.casefold():
            fail(f"uncontrolled or superseded terminology: {forbidden!r}")
    if r"1 \leq \lambda_i \leq n" in candidate_text or r"0 \leq i < k" in candidate_text:
        fail("declared source correction not applied")

    print("PASS: O013-LI-U043 complete Chapter 5 symmetric-polynomial section and exercises")
    print(f"source: {SLICE_RECORDS} records, {SLICE_BYTES} bytes, sha256={SLICE_SHA256}")
    print(f"candidate: {len(candidate_lines)} records, {len(candidate_data)} bytes, sha256={digest(candidate_data)}")
    print(
        "topology: "
        f"{len(ENV_RE.findall(candidate_text))} environment markers, "
        f"{len(LABEL_RE.findall(candidate_text))} labels, "
        f"{len(REF_RE.findall(candidate_text))} references, "
        f"{len(CITE_RE.findall(candidate_text))} citations, 8 indexes, 35 items, 11 hints"
    )
    print("corrections: 2; next source cursor: chapter6.tex line 1")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        fail(f"missing required file: {exc.filename}")
