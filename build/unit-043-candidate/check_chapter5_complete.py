#!/usr/bin/env python3
"""Single bounded checker for the assembled complete Indonesian Chapter 5."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter5.tex"
CANDIDATE = ROOT / "build/unit-043-candidate/chapter5-complete-id.tex"
DELTA = ROOT / "build/unit-043-candidate/CHAPTER5_TERMINOLOGY_DELTA.id-ID.csv"

AUTHORITY_BYTES = 122_998
AUTHORITY_SHA256 = "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
CANDIDATE_BYTES = 156_081
CANDIDATE_SHA256 = "33a1c65ce1ddea061e02d32a9a250d6db4444eb2251d5b721c8501f95a7f0e3c"

PARTS = (
    (1, 172, "build/unit-036-candidate/chapter5-ring-basics-id.tex", "d93ad6adeccae67ace0035286e9a41ab1350dca875acdb349d529c7f180b991a"),
    (174, 290, "build/unit-037-candidate/chapter5-special-rings-id.tex", "9f6ea7b368133027c1a12efef74db48eed36c6db6662fe746b894a938a0825f5"),
    (292, 461, "build/unit-038-candidate/chapter5-commutative-rings-localization-id.tex", "e48edae4d77c5be8206f8e18b0d4c71c307444830594295a338cbf8313d03607"),
    (463, 608, "build/unit-039-candidate/chapter5-mobius-inversion-id.tex", "5ed878a2ac0261b613cab8d050adc5130cf880e829736b80b24d696ba1a4c8a7"),
    (610, 781, "build/unit-040-candidate/chapter5-ring-limits-completion-id.tex", "b6131a25476422a43c51d844d1f75cbaf4a12da241b5db26e7f6f0435891e018"),
    (783, 956, "build/unit-041-candidate/chapter5-monoid-polynomial-rings-id.tex", "128e12090cdca0030ee537d778838fd9daad941319fc63e112216c593454001a"),
    (958, 1182, "build/unit-042-candidate/chapter5-unique-factorization-id.tex", "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a"),
    (1184, 1382, "build/unit-043-candidate/chapter5-symmetric-polynomials-exercises-id.tex", "5318c2433ca4784d1fbf64a86989bd3a3a007a10ed00cb6e0ae7f46a37122a2d"),
)
SEPARATORS = (173, 291, 462, 609, 782, 957, 1183)
UNIT_CHECKERS = tuple(
    f"scripts/check_unit_{unit:03d}_candidate.py" for unit in range(36, 44)
)

ENV_RE = re.compile(r"\\(begin|end)\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(?:eqref|ref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
INDEX_STREAM_RE = re.compile(r"\\index(?:\[([^\]]+)\])?\{")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
CHINESE_PUNCT_RE = re.compile(r"[，。；：？！《》「」『』、]")


def fail(message: str) -> None:
    raise AssertionError(message)


def strict(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        fail(f"non-canonical UTF-8/LF file: {path}")
    return data, data.decode("utf-8", errors="strict")


def records(text: str) -> list[str]:
    if text.endswith("\n"):
        text = text[:-1]
    return text.split("\n")


def main() -> None:
    authority_data, authority_text = strict(AUTHORITY)
    candidate_data, candidate_text = strict(CANDIDATE)
    if (len(authority_data), hashlib.sha256(authority_data).hexdigest()) != (
        AUTHORITY_BYTES,
        AUTHORITY_SHA256,
    ):
        fail("frozen Chapter 5 authority identity drift")
    if (len(candidate_data), hashlib.sha256(candidate_data).hexdigest()) != (
        CANDIDATE_BYTES,
        CANDIDATE_SHA256,
    ):
        fail("assembled Chapter 5 candidate identity drift")
    if not candidate_text.endswith("\n") or candidate_text.endswith("\n\n"):
        fail("candidate must end in exactly one LF")

    authority_lines = records(authority_text)
    candidate_lines = records(candidate_text)
    if len(authority_lines) != 1_382 or len(candidate_lines) != 1_382:
        fail("complete Chapter 5 record-count drift")

    expected: list[str | None] = [None] * 1_382
    for start, end, relative_path, expected_sha in PARTS:
        part_data, part_text = strict(ROOT / relative_path)
        if hashlib.sha256(part_data).hexdigest() != expected_sha:
            fail(f"checked fragment identity drift: {relative_path}")
        part_lines = records(part_text)
        if len(part_lines) != end - start + 1:
            fail(f"checked fragment record-count drift: {relative_path}")
        expected[start - 1 : end] = part_lines
    for record in SEPARATORS:
        if authority_lines[record - 1] != "":
            fail(f"authority blank separator drift at record {record}")
        expected[record - 1] = ""
    if any(line is None for line in expected) or candidate_lines != expected:
        fail("candidate is not the exact ordered checked-slice assembly")

    for checker in UNIT_CHECKERS:
        result = subprocess.run(
            [sys.executable, str(ROOT / checker)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode:
            detail = (result.stderr or result.stdout).strip().splitlines()[-1]
            fail(f"component checker failed ({checker}): {detail}")

    if [not line.strip() for line in authority_lines] != [
        not line.strip() for line in candidate_lines
    ]:
        fail("whole-chapter blank-record topology drift")
    if [line.lstrip().startswith("%") for line in authority_lines] != [
        line.lstrip().startswith("%") for line in candidate_lines
    ]:
        fail("whole-chapter comment-state topology drift")
    for regex, name in (
        (ENV_RE, "environment"),
        (LABEL_RE, "label"),
        (REF_RE, "reference"),
        (CITE_RE, "citation"),
        (INDEX_STREAM_RE, "index-stream"),
    ):
        if regex.findall(authority_text) != regex.findall(candidate_text):
            fail(f"ordered whole-chapter {name} topology drift")

    if candidate_text.count("李文威") != 1 or HAN_RE.search(candidate_text.replace("李文威", "", 1)):
        fail("unauthorized Han residue outside the exact author credit")
    if CHINESE_PUNCT_RE.search(candidate_text):
        fail("Chinese punctuation residue")
    if re.search(r"\b(?:TODO|TBD|FIXME|TRANSLATE)\b", candidate_text, re.IGNORECASE):
        fail("placeholder residue")
    candidate_fold = candidate_text.casefold()
    for forbidden in ("kompletisasi", "cincin", "lapangan", "kelompok", "variabel", "funktor"):
        if forbidden in candidate_fold:
            fail(f"uncontrolled or superseded terminology: {forbidden!r}")
    if candidate_fold.count("pelengkapan") != 16:
        fail("pelengkapan terminology census drift")

    topology = (
        len(ENV_RE.findall(candidate_text)),
        len(LABEL_RE.findall(candidate_text)),
        len(REF_RE.findall(candidate_text)),
        len(CITE_RE.findall(candidate_text)),
        len(INDEX_STREAM_RE.findall(candidate_text)),
        len(re.findall(r"\\item\b", candidate_text)),
    )
    if topology != (480, 80, 112, 7, 74, 112):
        fail(f"aggregate topology census drift: {topology!r}")
    if candidate_text.count(r"\begin{Exercises}") != 1 or candidate_text.count(r"\end{Exercises}") != 1:
        fail("whole-chapter Exercises topology drift")
    exercise_text = candidate_text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    exercise_census = (
        len(re.findall(r"(?m)^\t\\item\b", exercise_text)),
        len(re.findall(r"\\item\b", exercise_text)),
        exercise_text.count(r"\begin{hint}"),
        exercise_text.count(r"\begin{solution}"),
    )
    if exercise_census != (22, 31, 11, 0):
        fail(f"exercise topology drift: {exercise_census!r}")

    with DELTA.open("r", encoding="utf-8", newline="") as handle:
        delta_rows = list(csv.DictReader(handle))
    if len(delta_rows) != 22 or delta_rows[0]["source_term"] != "completion" or delta_rows[0]["target_term"] != "pelengkapan":
        fail("Chapter 5 terminology delta drift")
    if len({row["source_term"] for row in delta_rows}) != len(delta_rows):
        fail("duplicate source term in Chapter 5 terminology delta")

    print("PASS: complete Indonesian Chapter 5 candidate (authority records 1-1382)")
    print(f"candidate: {CANDIDATE_BYTES} bytes; sha256={CANDIDATE_SHA256}")
    print("topology: 480 environment markers; 80 labels; 112 references; 7 citations; 74 indexes; 112 items")
    print("exercises: 22 top-level / 31 including subitems; 11 hints; 0 solutions")
    print("terminology delta: 22 rows; completion -> pelengkapan; zero kompletisasi residue")
    print("next source cursor: chapter6.tex line 1")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
