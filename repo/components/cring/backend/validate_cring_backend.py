#!/usr/bin/env python3
"""Deterministically regenerate and validate the selected CRing backend."""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "interlanguage.cring-selected-component-backend.v1"
RECEIPT_SCHEMA = "interlanguage.cring-selected-backend-validation.v1"
COMPONENT_ID = "component.cring.selected_commutative_algebra"

AUTHORITY_ZIP_SHA256 = (
    "151cdf5498622251db9999b082c4b756a5a7e22b07ddd79538c0057472a4234d"
)
AUTHORITY_ZIP_BYTES = 442843
AUTHORITY_PDF_SHA256 = (
    "9d228183f549ab4a64dcacfa49884c0f7ef4d5d5f8c535f9066070bf909b580c"
)
AUTHORITY_PDF_BYTES = 2973918
AGGREGATE_RECEIPT_SHA256 = (
    "88d517bce56e50d090bce039c1786cd1dc75d0da5aa5644c87c8e585bcc344cb"
)
AGGREGATE_VALIDATOR_SHA256 = (
    "3c6a8a1a10197c58fd65694d0b2eb61916fec710862113864320f0dc3989964e"
)
AGGREGATE_PAIR_MANIFEST_SHA256 = (
    "05f6587857177c7bb92e5099b6bed5b6314679f9be2b7491747bcead4e7702a5"
)

BACKEND_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = BACKEND_DIR.parent
SUPPORT_DIR = COMPONENT_DIR / "support"
LANE_ROOT = COMPONENT_DIR.parents[2]
SOURCE_SEGMENT_DIR = COMPONENT_DIR / "source-en-segments"
REPAIRED_SOURCE_DIR = COMPONENT_DIR / "source-en-repaired"
TARGET_DIR = COMPONENT_DIR / "source-id"
SPAN_MANIFEST_PATH = SUPPORT_DIR / "CRING_SELECTED_SPANS.json"
REPAIR_GATE_PATH = SUPPORT_DIR / "CRING_REPAIR_GATE.json"
AUTHORITY_DIR = LANE_ROOT / "authority" / "cring-project-official-20260828"
AUTHORITY_SOURCE_DIR = AUTHORITY_DIR / "source" / "cring"
AUTHORITY_CHAPTER_DIR = AUTHORITY_SOURCE_DIR / "chapters"
AUTHORITY_ZIP_PATH = AUTHORITY_DIR / "CRing.zip"
AUTHORITY_PDF_PATH = AUTHORITY_DIR / "CRing.pdf"
AUTHORITY_BIB_PATH = AUTHORITY_SOURCE_DIR / "other" / "references.bib"
AUTHORITY_INTRO_PATH = AUTHORITY_SOURCE_DIR / "other" / "intro.tex"
AUTHORITY_LICENSE_PATH = AUTHORITY_CHAPTER_DIR / "license.tex"
AUTHORITY_CONTRIBUTORS_PATH = (
    AUTHORITY_SOURCE_DIR / "other" / "contributors.tex"
)
AGGREGATE_RECEIPT_PATH = (
    LANE_ROOT
    / "qa"
    / "cring-selected-evidence"
    / "cring-selected-aggregate-validation.json"
)
AGGREGATE_VALIDATOR_PATH = (
    LANE_ROOT
    / "qa"
    / "cring-selected-evidence"
    / "validate-cring-selected.ps1"
)

COMPONENT_PATH = BACKEND_DIR / "cring-component.json"
ROOTS_CSV_PATH = BACKEND_DIR / "cring-roots.csv"
ENTITIES_CSV_PATH = BACKEND_DIR / "cring-entities.csv"
LINKS_CSV_PATH = BACKEND_DIR / "cring-links.csv"
REPAIRS_CSV_PATH = BACKEND_DIR / "cring-repairs.csv"
PREREQUISITES_CSV_PATH = BACKEND_DIR / "cring-prerequisites.csv"
RECEIPT_PATH = BACKEND_DIR / "cring-backend-validation.json"

ROOT_ID_BY_FILE = {
    "01-nakayama.tex": "root.cring.nakayama",
    "02-spec-zariski.tex": "root.cring.spec_zariski",
    "03-associated-primary.tex": "root.cring.associated_primary",
    "04-lying-over-going-up.tex": "root.cring.lying_over_going_up",
    "05-nullstellensatz-normalization.tex": (
        "root.cring.nullstellensatz_normalization"
    ),
    "06-krull-dimension.tex": "root.cring.krull_dimension",
}
EXPECTED_FILES = tuple(ROOT_ID_BY_FILE)

THEOREM_ENVIRONMENTS = {
    "theorem",
    "lemma",
    "sublemma",
    "proposition",
    "corollary",
}
ENTITY_ENVIRONMENTS = (
    "definition",
    "theorem",
    "lemma",
    "sublemma",
    "proposition",
    "corollary",
    "example",
    "exercise",
    "remark",
    "question",
    "prediction",
)
MATH_ENVIRONMENTS = (
    "equation",
    "equation*",
    "align",
    "align*",
    "alignat",
    "alignat*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "eqnarray",
    "eqnarray*",
)
ENTITY_KINDS = (
    "section",
    "definition",
    "theorem",
    "example",
    "exercise",
    "remark",
    "question",
    "prediction",
    "formula",
    "hint",
)

REPAIR_ANCHORS = {
    "CRING-R01-empty-projective-reference": {
        "source": "projective-module discussion in Li, Chapter 6",
        "target": "pembahasan modul proyektif dalam Li, Bab 6",
    },
    "CRING-R02-empty-ufd-reference": {
        "source": "polynomial-ring UFD result developed in Li, Chapter 5",
        "target": (
            "hasil UFD bagi gelanggang polinomial yang dikembangkan "
            "dalam Li, Bab 5"
        ),
    },
    "CRING-R03-missing-semilocal-proof": {
        "source": r"surjective, so choose $x_1,\ldots,x_d\in M$",
        "target": r"surjektif, jadi pilih $x_1,\ldots,x_d\in M$",
    },
    "CRING-R03A-malformed-mu-max": {
        "source": (
            r"\mu_R(M) = \max_i \{\dim_{k_i} "
            r"M/\mathfrak{m}_i M\}"
        ),
        "target": (
            r"\mu_R(M) = \max_i \{\dim_{k_i} "
            r"M/\mathfrak{m}_i M\}"
        ),
    },
    "CRING-R04-undefined-annihilator-notation": {
        "source": r"\ann_R(x)=\{r\in R:rx=0\}",
        "target": r"\ann_R(x)=\{r\in R:rx=0\}",
    },
    "CRING-R05-irreducibility-definition": {
        "source": "A nonempty closed subset is irreducible",
        "target": (
            "Suatu himpunan bagian tertutup tak kosong disebut "
            "tak tereduksi"
        ),
    },
    "CRING-R06-embedded-prime-example": {
        "source": "ideal $(x,y)$ is embedded.",
        "target": "maksimal $(x,y)$ tertanam.",
    },
    "CRING-R07-constructibility-placeholder": {
        "source": (
            "Chevalley's constructibility theorem; its proof lies "
            "outside this selected supplement"
        ),
        "target": (
            "teorema konstruktibilitas Chevalley; buktinya berada "
            "di luar suplemen pilihan ini"
        ),
    },
    "CRING-R08-two-empty-dvr-references": {
        "source": (
            "DVR characterization proved in the full source's "
            "Dedekind-ring chapter"
        ),
        "target": (
            "karakterisasi DVR dibuktikan dalam bab mengenai gelanggang "
            "Dedekind pada sumber lengkap"
        ),
    },
}

ORIGINAL_BRIDGE_REPAIR_IDS = (
    "CRING-R04-undefined-annihilator-notation",
    "CRING-R05-irreducibility-definition",
    "CRING-R06-embedded-prime-example",
)

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
SECTION_RE = re.compile(
    r"\\(?P<subtype>chapter|section|subsection|subsubsection)"
    r"(?P<star>\*)?\s*\{"
)
ENVIRONMENT_START_RE = re.compile(
    r"\\begin\s*\{(?P<environment>"
    + "|".join(re.escape(value) for value in ENTITY_ENVIRONMENTS)
    + r")\}"
)
FORMULA_RE = re.compile(
    r"\\begin\s*\{(?P<mathenv>"
    + "|".join(re.escape(value) for value in MATH_ENVIRONMENTS)
    + r")\}.*?\\end\s*\{(?P=mathenv)\}"
    + r"|\\\[.*?\\\]"
    + r"|\\\(.*?\\\)"
    + r"|\$\$.*?\$\$"
    + r"|(?<!\\)\$(?!\$)(?:\\.|[^$])*?(?<!\\)\$",
    re.DOTALL,
)
LABEL_RE = re.compile(r"\\(?P<command>label)(?![A-Za-z@])\s*\{")
REF_RE = re.compile(
    r"\\(?P<command>rref|eqref|pageref|autoref|cref|Cref|ref)"
    r"(?![A-Za-z@])\s*\{"
)
CITATION_RE = re.compile(
    r"\\(?P<command>(?:[A-Za-z]*cite[A-Za-z]*))"
    r"(?![A-Za-z@])(?P<options>(?:\s*\[[^\]]*\])*)\s*\{"
)
BIB_ENTRY_RE = re.compile(r"(?m)^\s*@[A-Za-z]+\s*\{\s*([^,\s]+)")
SOURCE_HINT_RE = re.compile(r"\bHint\s*:")
TARGET_HINT_RE = re.compile(r"\bPetunjuk\s*:")
BRIDGE_SOURCE_MARKER = "Edition bridge (original)."
BRIDGE_TARGET_MARKER = "Jembatan edisi (asli)."


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def csv_bytes(fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: (
                    "true"
                    if value is True
                    else "false"
                    if value is False
                    else ""
                    if value is None
                    else value
                )
                for key, value in row.items()
            }
        )
    return buffer.getvalue().encode("utf-8")


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(LANE_ROOT.resolve()).as_posix()


def collapse_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def split_keys(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def make_id_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return token or "value"


def assert_equal(actual: Any, expected: Any, message: str) -> None:
    if actual != expected:
        raise ValueError(f"{message}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def is_escaped(text: str, index: int) -> bool:
    slash_count = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return slash_count % 2 == 1


def mask_comments(text: str) -> str:
    chars = list(text)
    index = 0
    while index < len(chars):
        if chars[index] == "%" and not is_escaped(text, index):
            cursor = index
            while cursor < len(chars) and chars[cursor] != "\n":
                chars[cursor] = " "
                cursor += 1
            index = cursor
        else:
            index += 1
    return "".join(chars)


def find_balanced_end(
    text: str, open_index: int, open_character: str, close_character: str
) -> int:
    assert_equal(text[open_index], open_character, "balanced opener")
    depth = 0
    for index in range(open_index, len(text)):
        character = text[index]
        if is_escaped(text, index):
            continue
        if character == open_character:
            depth += 1
        elif character == close_character:
            depth -= 1
            if depth == 0:
                return index
    raise ValueError(
        f"unclosed balanced argument at character {open_index}: {open_character}"
    )


@dataclass(frozen=True)
class TextData:
    path: Path
    raw: bytes
    text: str
    masked: str
    line_starts: tuple[int, ...]

    @property
    def bytes_count(self) -> int:
        return len(self.raw)

    @property
    def records(self) -> int:
        return self.text.count("\n")

    @property
    def blank_records(self) -> int:
        return sum(
            1
            for record in self.text.splitlines()
            if not record.strip()
        )

    @property
    def blank_map(self) -> tuple[int, ...]:
        return tuple(
            index
            for index, record in enumerate(self.text.splitlines(), start=1)
            if not record.strip()
        )

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.raw)

    def record(self, index: int) -> int:
        return bisect.bisect_right(self.line_starts, index)


def read_text(path: Path, require_lf: bool = True) -> TextData:
    raw = path.read_bytes()
    assert_true(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM is disallowed: {path}")
    text = raw.decode("utf-8", errors="strict")
    if require_lf:
        assert_true("\r" not in text, f"non-LF line ending: {path}")
        assert_true(text.endswith("\n"), f"missing final LF: {path}")
    starts = [0]
    starts.extend(match.end() for match in re.finditer("\n", text))
    return TextData(path, raw, text, mask_comments(text), tuple(starts))


def text_span(data: TextData, start: int, end: int) -> dict[str, Any]:
    assert_true(end > start, f"empty text span in {data.path}")
    raw = data.text[start:end]
    return {
        "start": start,
        "end": end,
        "record_start": data.record(start),
        "record_end": data.record(end - 1),
        "sha256": sha256_bytes(raw.encode("utf-8")),
    }


def parse_braced_matches(
    data: TextData, pattern: re.Pattern[str]
) -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    for match in pattern.finditer(data.masked):
        open_index = match.end() - 1
        close_index = find_balanced_end(data.masked, open_index, "{", "}")
        occurrence = {
            "start": match.start(),
            "end": close_index + 1,
            "command": match.groupdict().get("command", ""),
            "argument": data.text[open_index + 1 : close_index],
            "record_start": data.record(match.start()),
            "record_end": data.record(close_index),
        }
        if "options" in match.groupdict():
            occurrence["options"] = collapse_space(match.group("options") or "")
        occurrences.append(occurrence)
    return occurrences


def parse_sections(data: TextData) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in SECTION_RE.finditer(data.masked):
        open_index = match.end() - 1
        close_index = find_balanced_end(data.masked, open_index, "{", "}")
        subtype = match.group("subtype")
        span = text_span(data, match.start(), close_index + 1)
        values.append(
            {
                "start": match.start(),
                "end": close_index + 1,
                "subtype": subtype,
                "starred": bool(match.group("star")),
                "level": {
                    "chapter": 0,
                    "section": 1,
                    "subsection": 2,
                    "subsubsection": 3,
                }[subtype],
                "title": collapse_space(
                    data.text[open_index + 1 : close_index]
                ),
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
            }
        )
    return values


def find_environment_end(
    data: TextData, match: re.Match[str], environment: str
) -> int:
    token_re = re.compile(
        r"\\(?P<kind>begin|end)\s*\{" + re.escape(environment) + r"\}"
    )
    depth = 1
    cursor = match.end()
    while True:
        token = token_re.search(data.masked, cursor)
        if token is None:
            raise ValueError(f"unclosed {environment} environment in {data.path}")
        depth += 1 if token.group("kind") == "begin" else -1
        cursor = token.end()
        if depth == 0:
            return token.end()


def environment_kind(environment: str) -> str:
    if environment == "definition":
        return "definition"
    if environment in THEOREM_ENVIRONMENTS:
        return "theorem"
    if environment in {
        "example",
        "exercise",
        "remark",
        "question",
        "prediction",
    }:
        return environment
    raise AssertionError(environment)


def parse_environments(data: TextData) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in ENVIRONMENT_START_RE.finditer(data.masked):
        environment = match.group("environment")
        end = find_environment_end(data, match, environment)
        cursor = match.end()
        while cursor < len(data.masked) and data.masked[cursor].isspace():
            cursor += 1
        title = ""
        if cursor < len(data.masked) and data.masked[cursor] == "[":
            close = find_balanced_end(data.masked, cursor, "[", "]")
            title = collapse_space(data.text[cursor + 1 : close])
        span = text_span(data, match.start(), end)
        values.append(
            {
                "start": match.start(),
                "end": end,
                "kind": environment_kind(environment),
                "subtype": environment,
                "title": title,
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
            }
        )
    return values


def parse_named_environment(
    data: TextData, environment: str
) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"\\begin\s*\{" + re.escape(environment) + r"\}"
    )
    values: list[dict[str, Any]] = []
    for match in pattern.finditer(data.masked):
        end = find_environment_end(data, match, environment)
        span = text_span(data, match.start(), end)
        values.append(
            {
                "start": match.start(),
                "end": end,
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
                "raw": data.text[match.start() : end],
            }
        )
    return values


def formula_subtype(raw: str, match: re.Match[str]) -> str:
    if match.groupdict().get("mathenv"):
        return f"environment:{match.group('mathenv')}"
    if raw.startswith(r"\["):
        return "display-bracket"
    if raw.startswith(r"\("):
        return "inline-parenthesis"
    if raw.startswith("$$"):
        return "display-dollar"
    return "inline-dollar"


def neutralize_text_commands(value: str) -> str:
    command_re = re.compile(
        r"\\(?:text|textrm|textnormal|mathrm|mbox|intertext)"
        r"(?![A-Za-z@])\s*\{"
    )
    result: list[str] = []
    cursor = 0
    while True:
        match = command_re.search(value, cursor)
        if match is None:
            result.append(value[cursor:])
            break
        open_index = match.end() - 1
        close_index = find_balanced_end(value, open_index, "{", "}")
        result.append(value[cursor : open_index + 1])
        result.append("#")
        result.append("}")
        cursor = close_index + 1
    return "".join(result)


def normalize_formula(value: str) -> str:
    return re.sub(r"\s+", "", neutralize_text_commands(value))


def parse_formulas(data: TextData) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in FORMULA_RE.finditer(data.masked):
        start, end = match.span()
        raw = data.text[start:end]
        normalized = normalize_formula(data.masked[start:end])
        span = text_span(data, start, end)
        values.append(
            {
                "start": start,
                "end": end,
                "subtype": formula_subtype(raw, match),
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
                "structural_sha256": sha256_bytes(
                    normalized.encode("utf-8")
                ),
            }
        )
    return values


def parse_hints(
    data: TextData, pattern: re.Pattern[str]
) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in pattern.finditer(data.masked):
        open_index = data.masked.rfind("(", max(0, match.start() - 4), match.start())
        assert_true(open_index >= 0, f"hint lacks parenthetical opener: {data.path}")
        close_index = find_balanced_end(data.masked, open_index, "(", ")")
        span = text_span(data, open_index, close_index + 1)
        values.append(
            {
                "start": open_index,
                "end": close_index + 1,
                "subtype": "parenthetical-hint",
                "title": "",
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
            }
        )
    return values


def parse_links(data: TextData) -> dict[str, list[dict[str, Any]]]:
    return {
        "label": parse_braced_matches(data, LABEL_RE),
        "ref": parse_braced_matches(data, REF_RE),
        "citation": parse_braced_matches(data, CITATION_RE),
    }


def owner_entity_id(
    entities: list[dict[str, Any]], position: int
) -> str | None:
    containing = [
        entity
        for entity in entities
        if entity["_source_start"] <= position < entity["_source_end"]
    ]
    if containing:
        containing.sort(
            key=lambda item: (
                item["_source_end"] - item["_source_start"],
                item["order_in_root"],
            )
        )
        return containing[0]["entity_id"]
    preceding_sections = [
        entity
        for entity in entities
        if entity["kind"] == "section"
        and entity["_source_start"] <= position
    ]
    return preceding_sections[-1]["entity_id"] if preceding_sections else None


def find_anchor_records(data: TextData, anchor: str) -> list[int]:
    records: list[int] = []
    cursor = 0
    while True:
        index = data.text.find(anchor, cursor)
        if index < 0:
            break
        records.append(data.record(index))
        cursor = index + len(anchor)
    return records


def bind_root(
    filename: str,
    root_id: str,
    order: int,
    source: TextData,
    target: TextData,
    bibliography_keys: set[str],
) -> dict[str, Any]:
    stem = root_id.removeprefix("root.cring.")

    assert_equal(source.records, target.records, f"record count for {filename}")
    assert_equal(source.blank_map, target.blank_map, f"blank map for {filename}")

    source_sections = parse_sections(source)
    target_sections = parse_sections(target)
    assert_equal(
        [(item["subtype"], item["starred"]) for item in target_sections],
        [(item["subtype"], item["starred"]) for item in source_sections],
        f"section topology for {filename}",
    )

    source_environments = parse_environments(source)
    target_environments = parse_environments(target)
    assert_equal(
        [(item["kind"], item["subtype"]) for item in target_environments],
        [(item["kind"], item["subtype"]) for item in source_environments],
        f"semantic environment topology for {filename}",
    )

    source_formulas = parse_formulas(source)
    target_formulas = parse_formulas(target)
    assert_equal(
        Counter(
            (item["subtype"], item["structural_sha256"])
            for item in target_formulas
        ),
        Counter(
            (item["subtype"], item["structural_sha256"])
            for item in source_formulas
        ),
        f"normalized formula multiset for {filename}",
    )
    target_formula_queues: defaultdict[
        tuple[str, str], deque[dict[str, Any]]
    ] = defaultdict(deque)
    for target_formula in target_formulas:
        target_formula_queues[
            (
                target_formula["subtype"],
                target_formula["structural_sha256"],
            )
        ].append(target_formula)
    formula_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for source_formula in source_formulas:
        key = (
            source_formula["subtype"],
            source_formula["structural_sha256"],
        )
        formula_pairs.append(
            (source_formula, target_formula_queues[key].popleft())
        )

    source_hints = parse_hints(source, SOURCE_HINT_RE)
    target_hints = parse_hints(target, TARGET_HINT_RE)
    assert_equal(
        len(target_hints),
        len(source_hints),
        f"hint topology for {filename}",
    )

    source_links = parse_links(source)
    target_links = parse_links(target)
    for kind in ("label", "ref", "citation"):
        assert_equal(
            len(target_links[kind]),
            len(source_links[kind]),
            f"{kind} count for {filename}",
        )
    assert_equal(
        [
            (item["command"], collapse_space(item["argument"]))
            for item in target_links["label"]
        ],
        [
            (item["command"], collapse_space(item["argument"]))
            for item in source_links["label"]
        ],
        f"label topology for {filename}",
    )
    assert_equal(
        [
            (item["command"], collapse_space(item["argument"]))
            for item in target_links["ref"]
        ],
        [
            (item["command"], collapse_space(item["argument"]))
            for item in source_links["ref"]
        ],
        f"reference topology for {filename}",
    )
    assert_equal(
        [
            (item["command"], split_keys(item["argument"]))
            for item in target_links["citation"]
        ],
        [
            (item["command"], split_keys(item["argument"]))
            for item in source_links["citation"]
        ],
        f"citation topology for {filename}",
    )

    entity_pairs: list[
        tuple[str, dict[str, Any], dict[str, Any]]
    ] = []
    entity_pairs.extend(
        ("section", source_item, target_item)
        for source_item, target_item in zip(source_sections, target_sections)
    )
    entity_pairs.extend(
        (source_item["kind"], source_item, target_item)
        for source_item, target_item in zip(
            source_environments, target_environments
        )
    )
    entity_pairs.extend(
        ("formula", source_item, target_item)
        for source_item, target_item in formula_pairs
    )
    entity_pairs.extend(
        ("hint", source_item, target_item)
        for source_item, target_item in zip(source_hints, target_hints)
    )
    entity_pairs.sort(
        key=lambda item: (item[1]["start"], item[1]["end"], item[0])
    )

    counters = {kind: 0 for kind in ENTITY_KINDS}
    entities: list[dict[str, Any]] = []
    for order_in_root, (kind, source_item, target_item) in enumerate(
        entity_pairs, start=1
    ):
        counters[kind] += 1
        entity_id = f"{kind}.{stem}.{counters[kind]:04d}"
        entity = {
            "entity_id": entity_id,
            "root_id": root_id,
            "order_in_root": order_in_root,
            "kind": kind,
            "subtype": source_item["subtype"],
            "source_record_start": source_item["record_start"],
            "source_record_end": source_item["record_end"],
            "target_record_start": target_item["record_start"],
            "target_record_end": target_item["record_end"],
            "source_title": source_item.get("title", ""),
            "target_title": target_item.get("title", ""),
            "source_sha256": source_item["sha256"],
            "target_sha256": target_item["sha256"],
            "structural_sha256": (
                source_item["structural_sha256"]
                if kind == "formula"
                else ""
            ),
            "parent_section_id": None,
            "label_ids": [],
            "_source_start": source_item["start"],
            "_source_end": source_item["end"],
            "_section_level": source_item.get("level"),
        }
        entities.append(entity)

    section_stack: dict[int, str] = {}
    latest_section_id: str | None = None
    for entity in entities:
        if entity["kind"] == "section":
            level = int(entity["_section_level"])
            entity["parent_section_id"] = section_stack.get(level - 1)
            section_stack[level] = entity["entity_id"]
            for stale_level in tuple(section_stack):
                if stale_level > level:
                    del section_stack[stale_level]
            latest_section_id = entity["entity_id"]
        else:
            entity["parent_section_id"] = latest_section_id

    link_pairs: list[
        tuple[str, dict[str, Any], dict[str, Any]]
    ] = []
    for kind in ("label", "ref", "citation"):
        link_pairs.extend(
            (kind, source_item, target_item)
            for source_item, target_item in zip(
                source_links[kind], target_links[kind]
            )
        )
    link_pairs.sort(
        key=lambda item: (item[1]["start"], item[1]["end"], item[0])
    )
    link_counters = {"label": 0, "ref": 0, "citation": 0}
    links: list[dict[str, Any]] = []
    for order_in_root, (kind, source_item, target_item) in enumerate(
        link_pairs, start=1
    ):
        link_counters[kind] += 1
        link_id = f"{kind}.{stem}.{link_counters[kind]:04d}"
        source_value = collapse_space(source_item["argument"])
        target_value = collapse_space(target_item["argument"])
        keys = (
            split_keys(source_value)
            if kind in {"ref", "citation"}
            else [source_value]
        )
        link = {
            "link_id": link_id,
            "root_id": root_id,
            "order_in_root": order_in_root,
            "kind": kind,
            "command": source_item["command"],
            "source_record": source_item["record_start"],
            "target_record": target_item["record_start"],
            "source_value": source_value,
            "target_value": target_value,
            "keys": keys,
            "owner_entity_id": owner_entity_id(
                entities, source_item["start"]
            ),
            "resolved_ids": [],
            "resolution": "",
        }
        if kind == "citation":
            missing = [
                key
                for key in keys
                if key not in bibliography_keys and key != "*"
            ]
            assert_equal(missing, [], f"citation resolution for {link_id}")
            link["resolved_ids"] = [
                f"bibliography.cring.{make_id_token(key)}"
                for key in keys
                if key != "*"
            ]
            link["resolution"] = "authority-bibliography"
        links.append(link)

    entity_by_id = {entity["entity_id"]: entity for entity in entities}
    for link in links:
        if link["kind"] == "label" and link["owner_entity_id"]:
            entity_by_id[link["owner_entity_id"]]["label_ids"].append(
                link["link_id"]
            )

    for entity in entities:
        entity.pop("_section_level")

    first_source_title = source_sections[0]["title"] if source_sections else ""
    first_target_title = target_sections[0]["title"] if target_sections else ""
    root = {
        "root_id": root_id,
        "order": order,
        "filename": filename,
        "source_title": first_source_title,
        "target_title": first_target_title,
        "repaired_source_path": relative_path(source.path),
        "target_path": relative_path(target.path),
        "repaired_source_records": source.records,
        "target_records": target.records,
        "blank_records": source.blank_records,
        "repaired_source_bytes": source.bytes_count,
        "target_bytes": target.bytes_count,
        "repaired_source_sha256": source.sha256,
        "target_sha256": target.sha256,
        "counts": {
            "sections": counters["section"],
            "definitions": counters["definition"],
            "theorems": counters["theorem"],
            "examples": counters["example"],
            "exercises": counters["exercise"],
            "remarks": counters["remark"],
            "questions": counters["question"],
            "predictions": counters["prediction"],
            "formulas": counters["formula"],
            "hints": counters["hint"],
            "labels": link_counters["label"],
            "refs": link_counters["ref"],
            "citations": link_counters["citation"],
        },
    }
    return {
        "root": root,
        "entities": entities,
        "links": links,
        "source": source,
        "target": target,
    }


def validate_authority_span(
    segment: dict[str, Any],
    original_segment: TextData,
) -> dict[str, Any]:
    authority_path = AUTHORITY_CHAPTER_DIR / segment["source_file"]
    authority = read_text(authority_path)
    lines = authority.text.splitlines(keepends=True)
    first_line = int(segment["first_line"])
    last_line = int(segment["last_line"])
    assert_true(
        1 <= first_line <= last_line <= len(lines),
        f"invalid authority line span for {segment['segment']}",
    )
    extracted = "".join(lines[first_line - 1 : last_line]).encode("utf-8")
    assert_equal(
        extracted,
        original_segment.raw,
        f"physical authority extraction for {segment['segment']}",
    )
    assert_equal(
        original_segment.records,
        segment["records"],
        f"original segment records for {segment['segment']}",
    )
    assert_equal(
        original_segment.bytes_count,
        segment["bytes"],
        f"original segment bytes for {segment['segment']}",
    )
    assert_equal(
        original_segment.sha256,
        segment["sha256"],
        f"original segment SHA-256 for {segment['segment']}",
    )
    return {
        "authority_file": relative_path(authority_path),
        "authority_file_bytes": authority.bytes_count,
        "authority_file_sha256": authority.sha256,
        "first_line": first_line,
        "last_line": last_line,
        "records": original_segment.records,
        "bytes": original_segment.bytes_count,
        "sha256": original_segment.sha256,
        "segment_path": relative_path(original_segment.path),
    }


def build_bridge_records(
    bound_by_file: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    bridge_file = "03-associated-primary.tex"
    bound = bound_by_file[bridge_file]
    source_quotes = [
        item
        for item in parse_named_environment(bound["source"], "quote")
        if BRIDGE_SOURCE_MARKER in item["raw"]
    ]
    target_quotes = [
        item
        for item in parse_named_environment(bound["target"], "quote")
        if BRIDGE_TARGET_MARKER in item["raw"]
    ]
    assert_equal(len(source_quotes), 3, "designated original source bridge records")
    assert_equal(len(target_quotes), 3, "designated original target bridge records")

    bridge_records: list[dict[str, Any]] = []
    bridge_by_repair: dict[str, str] = {}
    for index, (repair_id, source_quote, target_quote) in enumerate(
        zip(
            ORIGINAL_BRIDGE_REPAIR_IDS,
            source_quotes,
            target_quotes,
        ),
        start=1,
    ):
        bridge_id = f"bridge.cring.associated_primary.{index:04d}"
        bridge_by_repair[repair_id] = bridge_id
        bridge_records.append(
            {
                "bridge_id": bridge_id,
                "repair_id": repair_id,
                "root_id": ROOT_ID_BY_FILE[bridge_file],
                "provenance": "edition-original",
                "source_record_start": source_quote["record_start"],
                "source_record_end": source_quote["record_end"],
                "target_record_start": target_quote["record_start"],
                "target_record_end": target_quote["record_end"],
                "source_sha256": source_quote["sha256"],
                "target_sha256": target_quote["sha256"],
            }
        )
    return bridge_records, bridge_by_repair


def build_repairs(
    repair_gate: dict[str, Any],
    bound_by_file: dict[str, dict[str, Any]],
    bridge_by_repair: dict[str, str],
) -> list[dict[str, Any]]:
    assert_equal(repair_gate["repair_count"], 9, "repair gate count")
    repair_ids = [repair["id"] for repair in repair_gate["repairs"]]
    assert_equal(
        repair_ids,
        list(REPAIR_ANCHORS),
        "repair gate order and identities",
    )
    repairs: list[dict[str, Any]] = []
    for repair in repair_gate["repairs"]:
        repair_id = repair["id"]
        filename = repair["file"]
        anchors = REPAIR_ANCHORS[repair_id]
        source_records = find_anchor_records(
            bound_by_file[filename]["source"], anchors["source"]
        )
        target_records = find_anchor_records(
            bound_by_file[filename]["target"], anchors["target"]
        )
        assert_true(source_records, f"missing source repair anchor {repair_id}")
        assert_true(target_records, f"missing target repair anchor {repair_id}")
        assert_equal(
            len(source_records),
            len(target_records),
            f"repair anchor multiplicity for {repair_id}",
        )
        repairs.append(
            {
                "repair_id": repair_id,
                "root_id": ROOT_ID_BY_FILE[filename],
                "file": filename,
                "kind": repair["kind"],
                "provenance": repair["provenance"],
                "source_records": source_records,
                "target_records": target_records,
                "anchor_occurrences": len(source_records),
                "original_bridge_record": (
                    repair_id in ORIGINAL_BRIDGE_REPAIR_IDS
                ),
                "bridge_id": bridge_by_repair.get(repair_id),
                "record_class": (
                    "edition-original-bridge"
                    if repair_id in ORIGINAL_BRIDGE_REPAIR_IDS
                    else "edition-original-proof"
                    if repair_id == "CRING-R03-missing-semilocal-proof"
                    else "edition-correction"
                    if repair["provenance"] == "edition-correction"
                    else "edition-original-inline"
                ),
            }
        )
    assert_equal(
        sum(1 for repair in repairs if repair["original_bridge_record"]),
        3,
        "original bridge repair count",
    )
    return repairs


def build_prerequisites(
    repairs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    repair_by_id = {repair["repair_id"]: repair for repair in repairs}
    specifications = (
        {
            "prerequisite_id": (
                "prerequisite.li.chapter_6.projective_modules"
                ".to.cring.nakayama"
            ),
            "from_external_id": "external.li.chapter_6.projective_modules",
            "from_author": "Li",
            "from_chapter": 6,
            "topic": "projective modules",
            "to_root_id": "root.cring.nakayama",
            "repair_id": "CRING-R01-empty-projective-reference",
        },
        {
            "prerequisite_id": (
                "prerequisite.li.chapter_5.polynomial_ufd"
                ".to.cring.spec_zariski"
            ),
            "from_external_id": "external.li.chapter_5.polynomial_ufd",
            "from_author": "Li",
            "from_chapter": 5,
            "topic": "polynomial-ring unique factorization",
            "to_root_id": "root.cring.spec_zariski",
            "repair_id": "CRING-R02-empty-ufd-reference",
        },
    )
    prerequisites: list[dict[str, Any]] = []
    for order, specification in enumerate(specifications, start=1):
        repair = repair_by_id[specification["repair_id"]]
        assert_equal(
            repair["root_id"],
            specification["to_root_id"],
            f"Li prerequisite target for {specification['repair_id']}",
        )
        prerequisites.append(
            {
                "order": order,
                **specification,
                "relationship": "required-background",
                "source_records": repair["source_records"],
                "target_records": repair["target_records"],
                "evidence": "explicit repaired prerequisite bridge",
            }
        )
    return prerequisites


def build_backend() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    span_manifest = json.loads(
        SPAN_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    repair_gate = json.loads(REPAIR_GATE_PATH.read_text(encoding="utf-8"))
    aggregate_receipt_raw = AGGREGATE_RECEIPT_PATH.read_bytes()
    aggregate_validator_raw = AGGREGATE_VALIDATOR_PATH.read_bytes()
    assert_equal(
        sha256_bytes(aggregate_receipt_raw),
        AGGREGATE_RECEIPT_SHA256,
        "aggregate receipt SHA-256",
    )
    assert_equal(
        sha256_bytes(aggregate_validator_raw),
        AGGREGATE_VALIDATOR_SHA256,
        "aggregate validator SHA-256",
    )
    aggregate_receipt = json.loads(aggregate_receipt_raw.decode("utf-8"))
    assert_equal(aggregate_receipt["result"], "PASS", "aggregate receipt result")
    assert_equal(aggregate_receipt["pair_count"], 6, "aggregate pair count")
    assert_equal(aggregate_receipt["repair_count"], 9, "aggregate repair count")
    assert_equal(
        aggregate_receipt["pair_manifest_sha256"],
        AGGREGATE_PAIR_MANIFEST_SHA256,
        "aggregate pair manifest SHA-256",
    )

    assert_equal(
        span_manifest["authority_zip_sha256"],
        AUTHORITY_ZIP_SHA256,
        "span manifest authority ZIP SHA-256",
    )
    assert_equal(
        span_manifest["license"],
        "GFDL-1.2-or-later",
        "span manifest license",
    )
    assert_equal(
        span_manifest["invariant_sections"],
        [],
        "invariant sections",
    )
    assert_equal(span_manifest["cover_texts"], [], "cover texts")
    assert_equal(
        tuple(segment["segment"] for segment in span_manifest["segments"]),
        EXPECTED_FILES,
        "selected segment order",
    )
    assert_equal(
        span_manifest["total_records"],
        3570,
        "original selected records",
    )

    zip_raw = AUTHORITY_ZIP_PATH.read_bytes()
    pdf_raw = AUTHORITY_PDF_PATH.read_bytes()
    assert_equal(len(zip_raw), AUTHORITY_ZIP_BYTES, "authority ZIP bytes")
    assert_equal(
        sha256_bytes(zip_raw),
        AUTHORITY_ZIP_SHA256,
        "authority ZIP SHA-256",
    )
    assert_equal(len(pdf_raw), AUTHORITY_PDF_BYTES, "authority PDF bytes")
    assert_equal(
        sha256_bytes(pdf_raw),
        AUTHORITY_PDF_SHA256,
        "authority PDF SHA-256",
    )

    authority_intro = read_text(AUTHORITY_INTRO_PATH)
    authority_license = read_text(AUTHORITY_LICENSE_PATH)
    authority_contributors = read_text(AUTHORITY_CONTRIBUTORS_PATH)
    license_notice = collapse_space(authority_intro.text)
    for fragment in (
        "Copyright (C) 2010 CRing Project.",
        "GNU Free Documentation License, Version 1.2 or any later version",
        "with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts",
    ):
        assert_true(fragment in license_notice, f"missing rights fragment: {fragment}")
    assert_true(
        "GNU Free Documentation License" in authority_license.text
        and "Version 1.2, November 2002" in authority_license.text,
        "embedded GFDL 1.2 license text",
    )

    initial_translation_script = read_text(
        SUPPORT_DIR / "translate_cring_segments.py"
    )
    contextual_translation_script = read_text(
        SUPPORT_DIR / "retranslate_cring_context.py"
    )
    for script in (initial_translation_script, contextual_translation_script):
        assert_true(
            '"facebook/nllb-200-distilled-600M"' in script.text,
            f"missing exact NLLB model ID in {script.path.name}",
        )
        assert_true(
            '"eng_Latn"' in script.text and '"ind_Latn"' in script.text,
            f"missing exact NLLB language IDs in {script.path.name}",
        )

    bibliography = read_text(AUTHORITY_BIB_PATH)
    bibliography_keys = set(BIB_ENTRY_RE.findall(bibliography.masked))
    assert_true(bool(bibliography_keys), "authority bibliography is empty")

    aggregate_pair_by_file = {
        pair["file"]: pair for pair in aggregate_receipt["pairs"]
    }
    repair_output_by_file = {
        item["file"]: item for item in repair_gate["outputs"]
    }

    roots: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    bound_by_file: dict[str, dict[str, Any]] = {}
    for order, segment in enumerate(span_manifest["segments"], start=1):
        filename = segment["segment"]
        root_id = ROOT_ID_BY_FILE[filename]
        original_segment = read_text(SOURCE_SEGMENT_DIR / filename)
        authority_span = validate_authority_span(
            segment, original_segment
        )
        repaired_source = read_text(REPAIRED_SOURCE_DIR / filename)
        target = read_text(TARGET_DIR / filename)

        repair_output = repair_output_by_file[filename]
        aggregate_pair = aggregate_pair_by_file[filename]
        assert_equal(
            repaired_source.sha256,
            repair_output["sha256"],
            f"repair gate source SHA-256 for {filename}",
        )
        assert_equal(
            repaired_source.bytes_count,
            repair_output["bytes"],
            f"repair gate source bytes for {filename}",
        )
        assert_equal(
            repaired_source.records,
            repair_output["records"],
            f"repair gate source records for {filename}",
        )
        assert_equal(
            repaired_source.sha256,
            aggregate_pair["source_sha256"],
            f"aggregate source SHA-256 for {filename}",
        )
        assert_equal(
            target.sha256,
            aggregate_pair["target_sha256"],
            f"aggregate target SHA-256 for {filename}",
        )
        assert_equal(
            target.bytes_count,
            aggregate_pair["target_bytes"],
            f"aggregate target bytes for {filename}",
        )
        assert_equal(
            target.records,
            aggregate_pair["records"],
            f"aggregate target records for {filename}",
        )
        assert_equal(
            aggregate_pair["result"],
            "PASS",
            f"aggregate pair result for {filename}",
        )

        bound = bind_root(
            filename,
            root_id,
            order,
            repaired_source,
            target,
            bibliography_keys,
        )
        bound["root"]["selection_title_id"] = segment["title_id"]
        bound["root"]["authority_span"] = authority_span
        bound["root"]["repair_ids"] = [
            repair["id"]
            for repair in repair_gate["repairs"]
            if repair["file"] == filename
        ]
        bound["root"]["repair_count"] = aggregate_pair["repairs"]
        roots.append(bound["root"])
        entities.extend(bound["entities"])
        links.extend(bound["links"])
        bound_by_file[filename] = bound

    bridge_records, bridge_by_repair = build_bridge_records(bound_by_file)
    repairs = build_repairs(
        repair_gate, bound_by_file, bridge_by_repair
    )
    prerequisites = build_prerequisites(repairs)

    all_source_markers = sum(
        bound["source"].text.count(BRIDGE_SOURCE_MARKER)
        for bound in bound_by_file.values()
    )
    all_target_markers = sum(
        bound["target"].text.count(BRIDGE_TARGET_MARKER)
        for bound in bound_by_file.values()
    )
    assert_equal(all_source_markers, 4, "all source edition bridge markers")
    assert_equal(all_target_markers, 4, "all target edition bridge markers")

    label_by_key: dict[str, str] = {}
    for link in links:
        if link["kind"] == "label":
            key = link["source_value"]
            assert_true(key not in label_by_key, f"duplicate selected label: {key}")
            label_by_key[key] = link["link_id"]
            link["resolved_ids"] = [link["link_id"]]
            link["resolution"] = "selected-component-label"

    external_ref_keys: set[str] = set()
    selected_ref_count = 0
    external_ref_count = 0
    for link in links:
        if link["kind"] != "ref":
            continue
        resolved_ids: list[str] = []
        resolution_types: set[str] = set()
        for key in link["keys"]:
            if key in label_by_key:
                resolved_ids.append(label_by_key[key])
                resolution_types.add("selected-component-label")
                selected_ref_count += 1
            else:
                external_id = (
                    f"external.cring.label.{make_id_token(key)}"
                )
                resolved_ids.append(external_id)
                external_ref_keys.add(key)
                resolution_types.add("authority-external-label")
                external_ref_count += 1
        link["resolved_ids"] = resolved_ids
        link["resolution"] = (
            next(iter(resolution_types))
            if len(resolution_types) == 1
            else "mixed"
        )

    public_entities = [
        {key: value for key, value in entity.items() if not key.startswith("_")}
        for entity in entities
    ]
    entity_ids = [entity["entity_id"] for entity in public_entities]
    link_ids = [link["link_id"] for link in links]
    bridge_ids = [bridge["bridge_id"] for bridge in bridge_records]
    prerequisite_ids = [
        item["prerequisite_id"] for item in prerequisites
    ]
    locale_neutral_ids = [COMPONENT_ID]
    locale_neutral_ids.extend(root["root_id"] for root in roots)
    locale_neutral_ids.extend(entity_ids)
    locale_neutral_ids.extend(link_ids)
    locale_neutral_ids.extend(bridge_ids)
    locale_neutral_ids.extend(prerequisite_ids)
    assert_equal(
        len(locale_neutral_ids),
        len(set(locale_neutral_ids)),
        "unique locale-neutral IDs",
    )
    assert_equal(
        [
            value
            for value in locale_neutral_ids
            if not ID_RE.fullmatch(value)
        ],
        [],
        "locale-neutral ID syntax",
    )

    entity_id_set = set(entity_ids)
    link_id_set = set(link_ids)
    for entity in public_entities:
        if entity["parent_section_id"]:
            assert_true(
                entity["parent_section_id"] in entity_id_set,
                f"unknown parent section for {entity['entity_id']}",
            )
        for label_id in entity["label_ids"]:
            assert_true(label_id in link_id_set, f"unknown label {label_id}")
    for link in links:
        if link["owner_entity_id"]:
            assert_true(
                link["owner_entity_id"] in entity_id_set,
                f"unknown owner for {link['link_id']}",
            )

    root_manifest_lines = [
        "|".join(
            (
                root["root_id"],
                str(root["order"]),
                root["authority_span"]["sha256"],
                root["repaired_source_sha256"],
                root["target_sha256"],
                str(root["authority_span"]["first_line"]),
                str(root["authority_span"]["last_line"]),
            )
        )
        for root in roots
    ]
    input_manifest_sha256 = sha256_bytes(
        ("\n".join(root_manifest_lines) + "\n").encode("utf-8")
    )

    counts = {
        "roots": len(roots),
        "authority_span_records": sum(
            root["authority_span"]["records"] for root in roots
        ),
        "repaired_source_records": sum(
            root["repaired_source_records"] for root in roots
        ),
        "target_records": sum(root["target_records"] for root in roots),
        "blank_records_each_repaired_side": sum(
            root["blank_records"] for root in roots
        ),
        "authority_span_bytes": sum(
            root["authority_span"]["bytes"] for root in roots
        ),
        "repaired_source_bytes": sum(
            root["repaired_source_bytes"] for root in roots
        ),
        "target_bytes": sum(root["target_bytes"] for root in roots),
        "repairs": len(repairs),
        "edition_original_repairs": sum(
            repair["provenance"] == "edition-original"
            for repair in repairs
        ),
        "edition_corrections": sum(
            repair["provenance"] == "edition-correction"
            for repair in repairs
        ),
        "original_bridge_records": len(bridge_records),
        "edition_bridge_marker_occurrences": all_source_markers,
        "li_prerequisites": len(prerequisites),
        "sections": sum(root["counts"]["sections"] for root in roots),
        "definitions": sum(root["counts"]["definitions"] for root in roots),
        "theorems": sum(root["counts"]["theorems"] for root in roots),
        "examples": sum(root["counts"]["examples"] for root in roots),
        "exercises": sum(root["counts"]["exercises"] for root in roots),
        "remarks": sum(root["counts"]["remarks"] for root in roots),
        "questions": sum(root["counts"]["questions"] for root in roots),
        "predictions": sum(root["counts"]["predictions"] for root in roots),
        "formulas": sum(root["counts"]["formulas"] for root in roots),
        "hints": sum(root["counts"]["hints"] for root in roots),
        "labels": sum(root["counts"]["labels"] for root in roots),
        "refs": sum(root["counts"]["refs"] for root in roots),
        "refs_to_selected_labels": selected_ref_count,
        "refs_to_external_authority_labels": external_ref_count,
        "external_authority_label_keys": len(external_ref_keys),
        "citations": sum(root["counts"]["citations"] for root in roots),
        "unique_citation_keys": len(
            {
                key
                for link in links
                if link["kind"] == "citation"
                for key in link["keys"]
                if key != "*"
            }
        ),
        "bibliography_entries": len(bibliography_keys),
        "entities": len(public_entities),
        "links": len(links),
    }

    component = {
        "schema": SCHEMA,
        "component": {
            "component_id": COMPONENT_ID,
            "title": {
                "source": "CRing Project selected commutative algebra supplement",
                "target": "Suplemen pilihan aljabar komutatif CRing",
            },
            "locales": {"source": "en", "target": "id-ID"},
            "source_creator": "CRing Project",
            "authority": {
                "official_source_url": "https://math.uchicago.edu/~amathew/CRing.zip",
                "official_pdf_url": "https://math.uchicago.edu/~amathew/CRing.pdf",
                "zip": {
                    "path": relative_path(AUTHORITY_ZIP_PATH),
                    "bytes": AUTHORITY_ZIP_BYTES,
                    "sha256": AUTHORITY_ZIP_SHA256,
                },
                "pdf": {
                    "path": relative_path(AUTHORITY_PDF_PATH),
                    "bytes": AUTHORITY_PDF_BYTES,
                    "sha256": AUTHORITY_PDF_SHA256,
                    "pages": 493,
                },
                "selection_manifest": {
                    "path": relative_path(SPAN_MANIFEST_PATH),
                    "sha256": sha256_bytes(
                        SPAN_MANIFEST_PATH.read_bytes()
                    ),
                    "semantic_boundary": span_manifest["semantic_boundary"],
                },
                "bibliography": {
                    "path": relative_path(AUTHORITY_BIB_PATH),
                    "bytes": bibliography.bytes_count,
                    "sha256": bibliography.sha256,
                },
            },
            "rights": {
                "copyright_notice": "Copyright (C) 2010 CRing Project.",
                "license_name": "GNU Free Documentation License",
                "license_expression": "GFDL-1.2-or-later",
                "version": "1.2 or any later version",
                "invariant_sections": [],
                "front_cover_texts": [],
                "back_cover_texts": [],
                "notice_path": relative_path(AUTHORITY_INTRO_PATH),
                "notice_sha256": authority_intro.sha256,
                "license_text_path": relative_path(AUTHORITY_LICENSE_PATH),
                "license_text_sha256": authority_license.sha256,
                "contributors_path": relative_path(
                    AUTHORITY_CONTRIBUTORS_PATH
                ),
                "contributors_sha256": authority_contributors.sha256,
            },
            "adaptation_provenance": {
                "independent_adaptation": True,
                "endorsement_claimed": False,
                "non_endorsement_scope": [
                    "CRing Project",
                    "listed source contributors",
                    "source hosts and affiliated institutions",
                ],
                "models": [
                    {
                        "stage": "rough-machine-translation",
                        "model_id": "facebook/nllb-200-distilled-600M",
                        "source_language_id": "eng_Latn",
                        "target_language_id": "ind_Latn",
                        "role": "rough candidate aid only",
                        "script_paths": [
                            relative_path(initial_translation_script.path),
                            relative_path(contextual_translation_script.path),
                        ],
                    },
                    {
                        "stage": "editorial-completion",
                        "model_id": "openai.codex.gpt-5-family",
                        "display_name": "OpenAI Codex (GPT-5 family)",
                        "role": (
                            "Indonesian mathematical editing, repair preservation, "
                            "and deterministic QA"
                        ),
                        "source_creator": False,
                    },
                ],
            },
            "upstream_validation": {
                "receipt_path": relative_path(AGGREGATE_RECEIPT_PATH),
                "receipt_bytes": len(aggregate_receipt_raw),
                "receipt_sha256": AGGREGATE_RECEIPT_SHA256,
                "validator_path": relative_path(AGGREGATE_VALIDATOR_PATH),
                "validator_bytes": len(aggregate_validator_raw),
                "validator_sha256": AGGREGATE_VALIDATOR_SHA256,
                "pair_manifest_sha256": AGGREGATE_PAIR_MANIFEST_SHA256,
                "result": "PASS",
            },
            "repair_provenance": {
                "repair_gate_path": relative_path(REPAIR_GATE_PATH),
                "repair_gate_sha256": sha256_bytes(
                    REPAIR_GATE_PATH.read_bytes()
                ),
                "repair_count": 9,
                "original_bridge_record_count": 3,
                "semilocal_original_proof_record_count": 1,
                "edition_bridge_marker_occurrence_count": 4,
                "classification_note": (
                    "The three requested original bridge records are R04-R06; "
                    "the separately tracked R03 marker supplies the omitted "
                    "semilocal proof."
                ),
            },
            "input_manifest_sha256": input_manifest_sha256,
        },
        "roots": roots,
        "entities": public_entities,
        "links": links,
        "repairs": repairs,
        "original_bridge_records": bridge_records,
        "prerequisites": prerequisites,
        "external_authority_labels": [
            {
                "external_label_id": (
                    f"external.cring.label.{make_id_token(key)}"
                ),
                "key": key,
                "scope": "full CRing authority outside selected spans",
            }
            for key in sorted(external_ref_keys)
        ],
        "counts": counts,
    }

    root_rows = [
        {
            "component_id": COMPONENT_ID,
            "root_id": root["root_id"],
            "order": root["order"],
            "filename": root["filename"],
            "authority_file": root["authority_span"]["authority_file"],
            "authority_first_line": root["authority_span"]["first_line"],
            "authority_last_line": root["authority_span"]["last_line"],
            "authority_span_records": root["authority_span"]["records"],
            "authority_span_bytes": root["authority_span"]["bytes"],
            "authority_span_sha256": root["authority_span"]["sha256"],
            "repaired_source_path": root["repaired_source_path"],
            "target_path": root["target_path"],
            "repaired_source_records": root["repaired_source_records"],
            "target_records": root["target_records"],
            "repaired_source_bytes": root["repaired_source_bytes"],
            "target_bytes": root["target_bytes"],
            "repaired_source_sha256": root["repaired_source_sha256"],
            "target_sha256": root["target_sha256"],
            "source_title": root["source_title"],
            "target_title": root["target_title"],
            "repair_ids": "|".join(root["repair_ids"]),
        }
        for root in roots
    ]
    entity_rows = [
        {
            **entity,
            "label_ids": "|".join(entity["label_ids"]),
        }
        for entity in public_entities
    ]
    link_rows = [
        {
            **link,
            "keys": "|".join(link["keys"]),
            "resolved_ids": "|".join(link["resolved_ids"]),
        }
        for link in links
    ]
    repair_rows = [
        {
            **repair,
            "source_records": "|".join(
                str(value) for value in repair["source_records"]
            ),
            "target_records": "|".join(
                str(value) for value in repair["target_records"]
            ),
        }
        for repair in repairs
    ]
    prerequisite_rows = [
        {
            **item,
            "source_records": "|".join(
                str(value) for value in item["source_records"]
            ),
            "target_records": "|".join(
                str(value) for value in item["target_records"]
            ),
        }
        for item in prerequisites
    ]
    return (
        component,
        root_rows,
        entity_rows,
        link_rows,
        repair_rows,
        prerequisite_rows,
    )


def expected_artifacts() -> tuple[dict[Path, bytes], dict[str, Any]]:
    (
        component,
        root_rows,
        entity_rows,
        link_rows,
        repair_rows,
        prerequisite_rows,
    ) = build_backend()
    artifacts = {
        COMPONENT_PATH: json_bytes(component),
        ROOTS_CSV_PATH: csv_bytes(
            [
                "component_id",
                "root_id",
                "order",
                "filename",
                "authority_file",
                "authority_first_line",
                "authority_last_line",
                "authority_span_records",
                "authority_span_bytes",
                "authority_span_sha256",
                "repaired_source_path",
                "target_path",
                "repaired_source_records",
                "target_records",
                "repaired_source_bytes",
                "target_bytes",
                "repaired_source_sha256",
                "target_sha256",
                "source_title",
                "target_title",
                "repair_ids",
            ],
            root_rows,
        ),
        ENTITIES_CSV_PATH: csv_bytes(
            [
                "entity_id",
                "root_id",
                "order_in_root",
                "kind",
                "subtype",
                "source_record_start",
                "source_record_end",
                "target_record_start",
                "target_record_end",
                "source_title",
                "target_title",
                "source_sha256",
                "target_sha256",
                "structural_sha256",
                "parent_section_id",
                "label_ids",
            ],
            entity_rows,
        ),
        LINKS_CSV_PATH: csv_bytes(
            [
                "link_id",
                "root_id",
                "order_in_root",
                "kind",
                "command",
                "source_record",
                "target_record",
                "source_value",
                "target_value",
                "keys",
                "owner_entity_id",
                "resolved_ids",
                "resolution",
            ],
            link_rows,
        ),
        REPAIRS_CSV_PATH: csv_bytes(
            [
                "repair_id",
                "root_id",
                "file",
                "kind",
                "provenance",
                "source_records",
                "target_records",
                "anchor_occurrences",
                "original_bridge_record",
                "bridge_id",
                "record_class",
            ],
            repair_rows,
        ),
        PREREQUISITES_CSV_PATH: csv_bytes(
            [
                "order",
                "prerequisite_id",
                "from_external_id",
                "from_author",
                "from_chapter",
                "topic",
                "to_root_id",
                "repair_id",
                "relationship",
                "source_records",
                "target_records",
                "evidence",
            ],
            prerequisite_rows,
        ),
    }
    return artifacts, component


def write_and_verify(regenerate: bool) -> dict[str, Any]:
    artifacts, component = expected_artifacts()
    if regenerate:
        for path, expected in artifacts.items():
            path.write_bytes(expected)

    artifact_receipt: list[dict[str, Any]] = []
    for path, expected in artifacts.items():
        assert_true(path.is_file(), f"missing generated artifact: {path}")
        actual = path.read_bytes()
        assert_equal(actual, expected, f"regeneration bytes for {path.name}")
        assert_true(b"\r" not in actual, f"non-LF generated artifact: {path.name}")
        actual.decode("utf-8", errors="strict")
        artifact_receipt.append(
            {
                "path": relative_path(path),
                "bytes": len(actual),
                "sha256": sha256_bytes(actual),
                "rows": (
                    actual.count(b"\n") - 1
                    if path.suffix == ".csv"
                    else None
                ),
            }
        )

    validator_raw = Path(__file__).read_bytes()
    assert_true(b"\r" not in validator_raw, "validator must use LF")
    validator_raw.decode("utf-8", errors="strict")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "result": "PASS",
        "mode": "regenerate-and-validate" if regenerate else "validate-existing",
        "checks": {
            "six_authority_line_spans_exact": True,
            "authority_zip_bytes_and_sha256_exact": True,
            "authority_pdf_bytes_and_sha256_exact": True,
            "aggregate_translation_receipt_exact_and_pass": True,
            "nine_repairs_exact": True,
            "three_original_bridge_records_exact": True,
            "semilocal_original_proof_record_separate": True,
            "source_target_record_and_blank_maps_exact": True,
            "section_and_semantic_environment_topology_exact": True,
            "formula_normalized_multiset_and_bindings_exact": True,
            "label_ref_citation_topology_exact": True,
            "exercise_and_hint_topology_exact": True,
            "citations_resolved_to_authority_bibliography": True,
            "selected_and_external_authority_refs_classified": True,
            "li_prerequisite_links_resolved": True,
            "gfdl_1_2_or_later_rights_exact": True,
            "independent_nonendorsement_present": True,
            "exact_model_provenance_present": True,
            "locale_neutral_ids_unique": True,
            "utf8_lf_inputs_and_outputs": True,
            "artifact_regeneration_byte_identical": True,
        },
        "authority": {
            "zip_bytes": AUTHORITY_ZIP_BYTES,
            "zip_sha256": AUTHORITY_ZIP_SHA256,
            "pdf_bytes": AUTHORITY_PDF_BYTES,
            "pdf_sha256": AUTHORITY_PDF_SHA256,
            "license_expression": "GFDL-1.2-or-later",
        },
        "upstream_aggregate": {
            "receipt_sha256": AGGREGATE_RECEIPT_SHA256,
            "validator_sha256": AGGREGATE_VALIDATOR_SHA256,
            "pair_manifest_sha256": AGGREGATE_PAIR_MANIFEST_SHA256,
            "result": "PASS",
        },
        "counts": component["counts"],
        "input_manifest_sha256": component["component"]["input_manifest_sha256"],
        "validator": {
            "path": relative_path(Path(__file__)),
            "bytes": len(validator_raw),
            "sha256": sha256_bytes(validator_raw),
        },
        "artifacts": artifact_receipt,
    }
    receipt_raw = json_bytes(receipt)
    RECEIPT_PATH.write_bytes(receipt_raw)
    assert_equal(RECEIPT_PATH.read_bytes(), receipt_raw, "receipt write")
    return {
        "result": "PASS",
        "counts": component["counts"],
        "artifacts": artifact_receipt,
        "receipt": {
            "path": relative_path(RECEIPT_PATH),
            "bytes": len(receipt_raw),
            "sha256": sha256_bytes(receipt_raw),
        },
        "validator": receipt["validator"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate and validate the selected CRing backend."
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="write deterministic JSON/CSV artifacts before validation",
    )
    arguments = parser.parse_args()
    try:
        summary = write_and_verify(arguments.regenerate)
    except Exception as error:
        print(
            json.dumps(
                {
                    "result": "FAIL",
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
