#!/usr/bin/env python3
"""Deterministically regenerate and validate the Duncan modular backend."""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "interlanguage.duncan-modular-backend.v1"
RECEIPT_SCHEMA = "interlanguage.duncan-modular-backend-validation.v1"
COMPONENT_ID = "component.duncan.representation_theory_notes"
AUTHORITY_COMMIT = "c62d36f41189da4bd3da4671668f68720df54ff7"
AUTHORITY_TREE = "e83ee440666133b14dec440158a108069a13e9e4"
AUTHORITY_ARCHIVE_SHA256 = "60dd9679c9ebe0c28f31794a7b2cb8552f4b7d68038061024972257280a1852c"
AUTHORITY_ARCHIVE_BYTES = 92763
AUTHORITY_DIRNAME = f"duncan-representation-theory-notes-{AUTHORITY_COMMIT}"
AUTHORITY_SOURCE_DIRNAME = f"representation-theory-notes-{AUTHORITY_COMMIT}"
ARCHIVE_FILENAME = f"representation-theory-notes-{AUTHORITY_COMMIT}.zip"

BACKEND_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = BACKEND_DIR.parent
SOURCE_DIR = COMPONENT_DIR / "source"
SUPPORT_DIR = COMPONENT_DIR / "support"
LANE_ROOT = COMPONENT_DIR.parents[2]
AUTHORITY_DIR = LANE_ROOT / "authority" / AUTHORITY_DIRNAME
AUTHORITY_SOURCE_DIR = AUTHORITY_DIR / "source" / AUTHORITY_SOURCE_DIRNAME
FREEZE_PATH = AUTHORITY_DIR / "DUNCAN_SOURCE_FREEZE.json"

COMPONENT_PATH = BACKEND_DIR / "duncan-component.json"
ROOTS_CSV_PATH = BACKEND_DIR / "duncan-roots.csv"
ENTITIES_CSV_PATH = BACKEND_DIR / "duncan-entities.csv"
LINKS_CSV_PATH = BACKEND_DIR / "duncan-links.csv"
SURFACES_CSV_PATH = BACKEND_DIR / "duncan-build-surfaces.csv"
RECEIPT_PATH = BACKEND_DIR / "duncan-backend-validation.json"

ROOT_SPECS = (
    {
        "stem": "rep_intro",
        "target_title": "Pengantar Teori Representasi",
        "prerequisites": (),
    },
    {
        "stem": "lin_alg",
        "target_title": "Aljabar Multilinear",
        "prerequisites": (),
    },
    {
        "stem": "modules",
        "target_title": "Modul dan Teori Wedderburn",
        "prerequisites": ("rep_intro", "lin_alg"),
    },
    {
        "stem": "characters",
        "target_title": "Teori Karakter",
        "prerequisites": ("rep_intro", "lin_alg", "modules"),
    },
    {
        "stem": "induction",
        "target_title": "Representasi Terinduksi",
        "prerequisites": ("rep_intro", "modules", "characters"),
    },
    {
        "stem": "symmetric",
        "target_title": "Grup Simetrik dan Grup Linear Umum",
        "prerequisites": ("lin_alg", "characters"),
    },
    {
        "stem": "nonclosed",
        "target_title": "Representasi atas Medan yang Tidak Tertutup",
        "prerequisites": ("modules", "characters"),
    },
)

THEOREM_ENVIRONMENTS = {
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "conjecture",
}
ENTITY_ENVIRONMENTS = (
    "definition",
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "conjecture",
    "example",
    "exercise",
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

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
SECTION_RE = re.compile(
    r"\\(?P<subtype>section|subsection|subsubsection)(?P<star>\*)?\s*\{"
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
    r"\\(?P<command>eqref|pageref|autoref|cref|Cref|ref)"
    r"(?![A-Za-z@])\s*\{"
)
CITATION_RE = re.compile(
    r"\\(?P<command>(?:[A-Za-z]*cite[A-Za-z]*))"
    r"(?![A-Za-z@])(?P<options>(?:\s*\[[^\]]*\])*)\s*\{"
)
INDEX_RE = re.compile(r"\\(?P<command>index)(?![A-Za-z@])\s*\{")
BIB_ENTRY_RE = re.compile(r"(?m)^\s*@[A-Za-z]+\s*\{\s*([^,\s]+)")


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
    assert_true(end > start, f"empty source span in {data.path}")
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


def parse_single_command_argument(data: TextData, command: str) -> str:
    pattern = re.compile(r"\\" + re.escape(command) + r"(?![A-Za-z@])\s*\{")
    values = parse_braced_matches(data, pattern)
    assert_equal(len(values), 1, f"single \\{command} command in {data.path.name}")
    return collapse_space(values[0]["argument"])


def parse_sections(data: TextData) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in SECTION_RE.finditer(data.masked):
        open_index = match.end() - 1
        close_index = find_balanced_end(data.masked, open_index, "{", "}")
        subtype = match.group("subtype")
        values.append(
            {
                "start": match.start(),
                "end": close_index + 1,
                "subtype": subtype,
                "starred": bool(match.group("star")),
                "level": {
                    "section": 1,
                    "subsection": 2,
                    "subsubsection": 3,
                }[subtype],
                "title": collapse_space(data.text[open_index + 1 : close_index]),
                **{
                    key: value
                    for key, value in text_span(data, match.start(), close_index + 1).items()
                    if key.startswith("record_") or key == "sha256"
                },
            }
        )
    return values


def find_environment_end(data: TextData, match: re.Match[str], environment: str) -> int:
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
        if environment == "definition":
            kind = "definition"
        elif environment in THEOREM_ENVIRONMENTS:
            kind = "theorem"
        elif environment == "example":
            kind = "example"
        elif environment == "exercise":
            kind = "exercise"
        else:
            raise AssertionError(environment)
        span = text_span(data, match.start(), end)
        values.append(
            {
                "start": match.start(),
                "end": end,
                "kind": kind,
                "subtype": environment,
                "title": title,
                "record_start": span["record_start"],
                "record_end": span["record_end"],
                "sha256": span["sha256"],
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
        r"\\(?:text|textrm|textnormal|mbox|intertext)(?![A-Za-z@])\s*\{"
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
                "structural_sha256": sha256_bytes(normalized.encode("utf-8")),
            }
        )
    return values


def parse_links(data: TextData) -> dict[str, list[dict[str, Any]]]:
    return {
        "label": parse_braced_matches(data, LABEL_RE),
        "ref": parse_braced_matches(data, REF_RE),
        "citation": parse_braced_matches(data, CITATION_RE),
        "index_term": parse_braced_matches(data, INDEX_RE),
    }


def make_id_token(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return token or "value"


def entity_prefix(kind: str) -> str:
    return {
        "section": "section",
        "definition": "definition",
        "theorem": "theorem",
        "example": "example",
        "exercise": "exercise",
        "formula": "formula",
    }[kind]


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
        if entity["kind"] == "section" and entity["_source_start"] <= position
    ]
    return preceding_sections[-1]["entity_id"] if preceding_sections else None


def bind_root(
    spec: dict[str, Any],
    order: int,
    source: TextData,
    target: TextData,
    bibliography_keys: set[str],
) -> dict[str, Any]:
    stem = spec["stem"]
    root_id = f"root.{stem}"

    source_sections = parse_sections(source)
    target_sections = parse_sections(target)
    assert_equal(
        [(item["subtype"], item["starred"]) for item in target_sections],
        [(item["subtype"], item["starred"]) for item in source_sections],
        f"section topology for {stem}",
    )

    source_environments = parse_environments(source)
    target_environments = parse_environments(target)
    assert_equal(
        [(item["kind"], item["subtype"]) for item in target_environments],
        [(item["kind"], item["subtype"]) for item in source_environments],
        f"semantic environment topology for {stem}",
    )

    source_formulas = parse_formulas(source)
    target_formulas = parse_formulas(target)
    assert_equal(
        [item["subtype"] for item in target_formulas],
        [item["subtype"] for item in source_formulas],
        f"formula delimiter topology for {stem}",
    )
    formula_mismatch_indexes = [
        index + 1
        for index, (source_formula, target_formula) in enumerate(
            zip(source_formulas, target_formulas)
        )
        if source_formula["structural_sha256"]
        != target_formula["structural_sha256"]
    ]
    assert_equal(
        formula_mismatch_indexes,
        [],
        f"normalized formula structure for {stem}",
    )

    source_links = parse_links(source)
    target_links = parse_links(target)
    for kind in ("label", "ref", "citation", "index_term"):
        assert_equal(
            len(target_links[kind]),
            len(source_links[kind]),
            f"{kind} count for {stem}",
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
        f"label topology for {stem}",
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
        f"reference topology for {stem}",
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
        f"citation topology for {stem}",
    )
    assert_equal(
        [item["command"] for item in target_links["index_term"]],
        [item["command"] for item in source_links["index_term"]],
        f"index topology for {stem}",
    )

    source_title = parse_single_command_argument(source, "title")
    target_title = parse_single_command_argument(target, "title")
    assert_equal(
        target_title.casefold(),
        spec["target_title"].casefold(),
        f"target title for {stem}",
    )

    entity_pairs: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
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
        for source_item, target_item in zip(source_formulas, target_formulas)
    )
    entity_pairs.sort(key=lambda item: (item[1]["start"], item[1]["end"], item[0]))

    counters = {
        "section": 0,
        "definition": 0,
        "theorem": 0,
        "example": 0,
        "exercise": 0,
        "formula": 0,
    }
    entities: list[dict[str, Any]] = []
    for order_in_root, (kind, source_item, target_item) in enumerate(
        entity_pairs, start=1
    ):
        counters[kind] += 1
        entity_id = (
            f"{entity_prefix(kind)}.{stem}.{counters[kind]:04d}"
        )
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
                source_item["structural_sha256"] if kind == "formula" else ""
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
    for kind in ("label", "ref", "citation", "index_term"):
        link_pairs.extend(
            (kind, source_item, target_item)
            for source_item, target_item in zip(
                source_links[kind], target_links[kind]
            )
        )
    link_pairs.sort(key=lambda item: (item[1]["start"], item[1]["end"], item[0]))

    link_counters = {"label": 0, "ref": 0, "citation": 0, "index_term": 0}
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
            "owner_entity_id": owner_entity_id(entities, source_item["start"]),
            "resolved_ids": [],
            "resolution": "",
        }
        if kind == "citation":
            missing = [key for key in keys if key not in bibliography_keys and key != "*"]
            assert_equal(missing, [], f"bibliography resolution for {link_id}")
            link["resolved_ids"] = [
                f"bibliography.{make_id_token(key)}" for key in keys if key != "*"
            ]
            link["resolution"] = "shared-bibliography"
        elif kind == "index_term":
            link["resolution"] = "paired-index-term"
        links.append(link)

    entity_by_id = {entity["entity_id"]: entity for entity in entities}
    for link in links:
        if link["kind"] == "label" and link["owner_entity_id"]:
            entity_by_id[link["owner_entity_id"]]["label_ids"].append(
                link["link_id"]
            )

    for entity in entities:
        entity.pop("_section_level")

    root = {
        "root_id": root_id,
        "order": order,
        "source_title": source_title,
        "target_title": target_title,
        "source_path": relative_path(source.path),
        "target_path": relative_path(target.path),
        "source_records": source.records,
        "target_records": target.records,
        "source_bytes": source.bytes_count,
        "target_bytes": target.bytes_count,
        "source_sha256": source.sha256,
        "target_sha256": target.sha256,
        "prerequisite_root_ids": [
            f"root.{value}" for value in spec["prerequisites"]
        ],
        "prerequisite_kind": "pedagogical",
        "counts": {
            "sections": counters["section"],
            "definitions": counters["definition"],
            "theorems": counters["theorem"],
            "examples": counters["example"],
            "exercises": counters["exercise"],
            "formulas": counters["formula"],
            "labels": link_counters["label"],
            "refs": link_counters["ref"],
            "citations": link_counters["citation"],
            "index_terms": link_counters["index_term"],
        },
    }
    return {
        "root": root,
        "entities": entities,
        "links": links,
        "source_links": source_links,
    }


def file_surface(
    surface_id: str,
    order: int,
    kind: str,
    path: Path,
    role: str,
    required: bool = True,
) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "surface_id": surface_id,
        "order": order,
        "kind": kind,
        "path": relative_path(path),
        "role": role,
        "required": required,
        "generated": False,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
    }


def generated_surface(
    surface_id: str, order: int, kind: str, path: str, role: str
) -> dict[str, Any]:
    return {
        "surface_id": surface_id,
        "order": order,
        "kind": kind,
        "path": path,
        "role": role,
        "required": True,
        "generated": True,
        "bytes": None,
        "sha256": None,
    }


def validate_driver_root_order(driver: TextData) -> None:
    include_re = re.compile(
        r"(?m)^\\DuncanIncludeRoot\{(?P<filename>[^{}]+)\}"
        r"\{(?P<title>[^{}]+)\}\s*$"
    )
    actual = [
        (match.group("filename"), match.group("title"))
        for match in include_re.finditer(driver.masked)
    ]
    expected = [
        (f"../source/{spec['stem']}.tex", spec["target_title"])
        for spec in ROOT_SPECS
    ]
    assert_equal(actual, expected, "driver root order")


def build_backend() -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    authority = freeze["authority"]
    assert_equal(authority["commit"], AUTHORITY_COMMIT, "authority commit")
    assert_equal(authority["tree"], AUTHORITY_TREE, "authority tree")
    assert_equal(
        authority["archive_sha256"],
        AUTHORITY_ARCHIVE_SHA256,
        "authority archive SHA-256",
    )
    assert_equal(
        authority["archive_bytes"],
        AUTHORITY_ARCHIVE_BYTES,
        "authority archive bytes",
    )

    archive_path = AUTHORITY_DIR / ARCHIVE_FILENAME
    archive_raw = archive_path.read_bytes()
    assert_equal(len(archive_raw), AUTHORITY_ARCHIVE_BYTES, "physical archive bytes")
    assert_equal(
        sha256_bytes(archive_raw),
        AUTHORITY_ARCHIVE_SHA256,
        "physical archive SHA-256",
    )

    driver = read_text(SUPPORT_DIR / "duncan-complete-id.tex")
    preamble = read_text(SUPPORT_DIR / "duncan-id-preamble.tex")
    validate_driver_root_order(driver)

    required_driver_fragments = (
        "tidak ada dukungan, persetujuan, atau pengesahan",
        "Enam lembar tugas",
        "49 soal",
        "satu solusi parsial",
        "dikecualikan, tidak diunduh, tidak dimasukkan, tidak diadaptasi",
    )
    collapsed_driver = collapse_space(driver.text)
    for fragment in required_driver_fragments:
        assert_true(
            fragment in collapsed_driver,
            f"missing driver provenance fragment: {fragment}",
        )
    required_preamble_fragments = (
        r"\newcommand{\DuncanSourceAuthor}{Alexander Duncan}",
        rf"\newcommand{{\DuncanSourceCommit}}{{{AUTHORITY_COMMIT}}}",
        rf"\newcommand{{\DuncanSourceTree}}{{{AUTHORITY_TREE}}}",
        r"\newcommand{\DuncanLicenseSPDX}{CC-BY-4.0}",
        r"\newcommand{\DuncanModelProvenance}{OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna}",
    )
    for fragment in required_preamble_fragments:
        assert_true(fragment in preamble.text, f"missing preamble provenance fragment: {fragment}")

    bib_path = SOURCE_DIR / "rep_theory.bib"
    bib = read_text(bib_path)
    authority_bib = read_text(AUTHORITY_SOURCE_DIR / "rep_theory.bib")
    assert_equal(bib.sha256, authority_bib.sha256, "shared bibliography identity")
    bibliography_keys = set(BIB_ENTRY_RE.findall(bib.masked))
    assert_true(bool(bibliography_keys), "bibliography has no entries")

    freeze_sources = {
        item["filename"]: item for item in freeze["source_files"]
    }
    roots: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    source_link_sets: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for order, spec in enumerate(ROOT_SPECS, start=1):
        filename = f"{spec['stem']}.tex"
        source = read_text(AUTHORITY_SOURCE_DIR / filename)
        target = read_text(SOURCE_DIR / filename)
        assert_equal(
            source.sha256,
            freeze_sources[filename]["sha256"],
            f"frozen source hash for {filename}",
        )
        assert_equal(
            source.bytes_count,
            freeze_sources[filename]["bytes"],
            f"frozen source bytes for {filename}",
        )
        bound = bind_root(
            spec,
            order,
            source,
            target,
            bibliography_keys,
        )
        roots.append(bound["root"])
        entities.extend(bound["entities"])
        links.extend(bound["links"])
        source_link_sets[bound["root"]["root_id"]] = bound["source_links"]

    label_by_key: dict[str, str] = {}
    for link in links:
        if link["kind"] == "label":
            key = link["source_value"]
            assert_true(key not in label_by_key, f"duplicate component label: {key}")
            label_by_key[key] = link["link_id"]
            link["resolved_ids"] = [link["link_id"]]
            link["resolution"] = "component-label"

    for link in links:
        if link["kind"] != "ref":
            continue
        resolved: list[str] = []
        resolution_types: set[str] = set()
        for key in link["keys"]:
            if key in label_by_key:
                resolved.append(label_by_key[key])
                resolution_types.add("component-label")
            elif key == "LastPage":
                resolved.append("package.lastpage.label.LastPage")
                resolution_types.add("tex-package")
            else:
                raise ValueError(f"unresolved reference {key!r} in {link['link_id']}")
        link["resolved_ids"] = resolved
        link["resolution"] = (
            next(iter(resolution_types))
            if len(resolution_types) == 1
            else "mixed"
        )

    entity_ids = [entity["entity_id"] for entity in entities]
    link_ids = [link["link_id"] for link in links]
    all_ids = [COMPONENT_ID]
    all_ids.extend(root["root_id"] for root in roots)
    all_ids.extend(entity_ids)
    all_ids.extend(link_ids)
    assert_equal(len(all_ids), len(set(all_ids)), "unique backend IDs")
    invalid_ids = [value for value in all_ids if not ID_RE.fullmatch(value)]
    assert_equal(invalid_ids, [], "locale-neutral backend IDs")

    root_ids = {root["root_id"] for root in roots}
    root_order = {root["root_id"]: root["order"] for root in roots}
    for root in roots:
        for prerequisite in root["prerequisite_root_ids"]:
            assert_true(prerequisite in root_ids, f"unknown prerequisite {prerequisite}")
            assert_true(
                root_order[prerequisite] < root["order"],
                f"non-preceding prerequisite {prerequisite} for {root['root_id']}",
            )

    entity_id_set = set(entity_ids)
    link_id_set = set(link_ids)
    for entity in entities:
        if entity["parent_section_id"]:
            assert_true(
                entity["parent_section_id"] in entity_id_set,
                f"unknown parent section for {entity['entity_id']}",
            )
        for label_id in entity["label_ids"]:
            assert_true(label_id in link_id_set, f"unknown label ID {label_id}")
    for link in links:
        if link["owner_entity_id"]:
            assert_true(
                link["owner_entity_id"] in entity_id_set,
                f"unknown owner for {link['link_id']}",
            )

    surfaces: list[dict[str, Any]] = [
        file_surface(
            "surface.driver",
            1,
            "tex-driver",
            SUPPORT_DIR / "duncan-complete-id.tex",
            "integrated document entry point",
        ),
        file_surface(
            "surface.preamble",
            2,
            "tex-preamble",
            SUPPORT_DIR / "duncan-id-preamble.tex",
            "shared locale, theorem, provenance, and bibliography configuration",
        ),
        file_surface(
            "surface.bibliography",
            3,
            "bib-database",
            bib_path,
            "shared bibliography resolved by Biber",
        ),
        file_surface(
            "surface.license",
            4,
            "license",
            SUPPORT_DIR / "DUNCAN-LICENSE-CC-BY-4.0.txt",
            "CC BY 4.0 license text",
        ),
        file_surface(
            "surface.readme",
            5,
            "provenance-readme",
            SUPPORT_DIR / "DUNCAN-SOURCE-README.md",
            "source attribution and component notes",
        ),
        file_surface(
            "surface.builder",
            6,
            "build-script",
            SUPPORT_DIR / "build-duncan-id.ps1",
            "deterministic XeLaTeX and Biber build orchestration",
        ),
    ]
    for root in roots:
        surfaces.append(
            file_surface(
                f"surface.{root['root_id']}",
                10 + root["order"],
                "translated-tex-root",
                LANE_ROOT / root["target_path"],
                f"ordered root {root['order']} input",
            )
        )
    surfaces.append(
        generated_surface(
            "surface.output.pdf",
            100,
            "pdf",
            "artifacts/catatan-teori-representasi-duncan-id.pdf",
            "promoted integrated reader artifact",
        )
    )

    surface_ids = [surface["surface_id"] for surface in surfaces]
    assert_equal(len(surface_ids), len(set(surface_ids)), "unique build surface IDs")
    assert_equal(
        [surface["order"] for surface in surfaces],
        sorted(surface["order"] for surface in surfaces),
        "build surface order",
    )

    root_manifest_lines = [
        "|".join(
            (
                root["root_id"],
                str(root["order"]),
                root["source_sha256"],
                root["target_sha256"],
                str(root["source_records"]),
                str(root["target_records"]),
            )
        )
        for root in roots
    ]
    input_manifest_sha256 = sha256_bytes(
        ("\n".join(root_manifest_lines) + "\n").encode("utf-8")
    )

    counts = {
        "roots": len(roots),
        "sections": sum(root["counts"]["sections"] for root in roots),
        "definitions": sum(root["counts"]["definitions"] for root in roots),
        "theorems": sum(root["counts"]["theorems"] for root in roots),
        "examples": sum(root["counts"]["examples"] for root in roots),
        "exercises": sum(root["counts"]["exercises"] for root in roots),
        "formulas": sum(root["counts"]["formulas"] for root in roots),
        "labels": sum(root["counts"]["labels"] for root in roots),
        "refs": sum(root["counts"]["refs"] for root in roots),
        "citations": sum(root["counts"]["citations"] for root in roots),
        "index_terms": sum(root["counts"]["index_terms"] for root in roots),
        "entities": len(entities),
        "links": len(links),
        "bibliography_entries": len(bibliography_keys),
        "unique_citation_keys": len(
            {
                key
                for link in links
                if link["kind"] == "citation"
                for key in link["keys"]
                if key != "*"
            }
        ),
        "build_surfaces": len(surfaces),
        "source_records": sum(root["source_records"] for root in roots),
        "target_records": sum(root["target_records"] for root in roots),
        "source_bytes": sum(root["source_bytes"] for root in roots),
        "target_bytes": sum(root["target_bytes"] for root in roots),
    }

    public_entities = [
        {key: value for key, value in entity.items() if not key.startswith("_")}
        for entity in entities
    ]

    component = {
        "schema": SCHEMA,
        "component": {
            "component_id": COMPONENT_ID,
            "title": {
                "source": "Representation Theory Notes",
                "target": "Catatan Teori Representasi",
            },
            "locales": {"source": "en", "target": "id-ID"},
            "source_author": "Alexander Duncan",
            "course": {
                "code": "MATH 742",
                "institution": "University of South Carolina",
                "edition": "Spring 2023",
            },
            "authority": {
                "repository": "https://github.com/vtorsor/representation-theory-notes",
                "commit_sha1": AUTHORITY_COMMIT,
                "tree_sha1": AUTHORITY_TREE,
                "commit_date_utc": authority["commit_date_utc"],
                "archive": {
                    "filename": ARCHIVE_FILENAME,
                    "bytes": AUTHORITY_ARCHIVE_BYTES,
                    "sha256": AUTHORITY_ARCHIVE_SHA256,
                },
                "freeze_path": relative_path(FREEZE_PATH),
                "license": {
                    "name": "Creative Commons Attribution 4.0 International",
                    "spdx_expression": "CC-BY-4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0/",
                    "authority_file": relative_path(
                        AUTHORITY_SOURCE_DIR / "LICENSE"
                    ),
                    "authority_file_sha256": freeze["rights"]["license_sha256"],
                },
            },
            "adaptation_provenance": {
                "independent_adaptation": True,
                "endorsement_claimed": False,
                "non_endorsement_scope": [
                    "Alexander Duncan",
                    "University of South Carolina",
                    "Creative Commons",
                    "reference publishers",
                ],
                "model": {
                    "model_id": "model.openai_codex.gpt-5.6-sol.ultra",
                    "provider": "OpenAI",
                    "product": "Codex",
                    "model": "gpt-5.6-sol",
                    "reasoning_effort": "Ultra",
                    "full_identification": "OpenAI Codex gpt-5.6-sol, Ultra",
                    "instruction_context": "on instructions of the user",
                    "role": "Indonesian language adaptation and mathematical editing assistance",
                    "source_author": False,
                },
            },
            "component_boundary": {
                "included": {
                    "translated_root_count": 7,
                    "shared_bibliography": "rep_theory.bib",
                    "support_files": [
                        "README.md",
                        "LICENSE",
                    ],
                    "authority_tree_closed": True,
                },
                "excluded_external_assignment_sheets": {
                    "boundary_id": "boundary.external_assignments",
                    "status": "excluded",
                    "assignment_sheet_count": 6,
                    "reported_problem_count": 49,
                    "partial_solution_count": 1,
                    "within_pinned_cc_by_tree": False,
                    "downloaded": False,
                    "incorporated": False,
                    "adapted": False,
                    "relicensed": False,
                    "reason": "outside the pinned CC BY 4.0 repository tree",
                },
            },
            "prerequisite_policy": {
                "kind": "pedagogical",
                "description": (
                    "Conservative root-level reading dependencies; these are "
                    "distinct from TeX file dependencies."
                ),
            },
            "build": {
                "driver_surface_id": "surface.driver",
                "root_order": [root["root_id"] for root in roots],
                "engine_sequence": [
                    "xelatex",
                    "biber",
                    "xelatex",
                    "xelatex",
                ],
                "bibliography_backend": "biber",
                "output_surface_id": "surface.output.pdf",
                "external_tex_packages": [
                    "amsmath",
                    "amssymb",
                    "amsthm",
                    "babel",
                    "biblatex",
                    "csquotes",
                    "docmute",
                    "fancyhdr",
                    "fontspec",
                    "geometry",
                    "hyperref",
                    "lastpage",
                    "microtype",
                    "xurl",
                    "ytableau",
                ],
            },
            "input_manifest_sha256": input_manifest_sha256,
        },
        "roots": roots,
        "entities": public_entities,
        "links": links,
        "build_surfaces": surfaces,
        "counts": counts,
    }

    root_rows = [
        {
            "component_id": COMPONENT_ID,
            "root_id": root["root_id"],
            "order": root["order"],
            "source_path": root["source_path"],
            "target_path": root["target_path"],
            "source_records": root["source_records"],
            "target_records": root["target_records"],
            "source_bytes": root["source_bytes"],
            "target_bytes": root["target_bytes"],
            "source_sha256": root["source_sha256"],
            "target_sha256": root["target_sha256"],
            "source_title": root["source_title"],
            "target_title": root["target_title"],
            "prerequisite_root_ids": "|".join(root["prerequisite_root_ids"]),
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
    return component, root_rows, entity_rows, link_rows, surfaces, roots


def expected_artifacts() -> tuple[
    dict[Path, bytes], dict[str, Any], list[dict[str, Any]]
]:
    component, root_rows, entity_rows, link_rows, surfaces, _roots = build_backend()
    artifacts = {
        COMPONENT_PATH: json_bytes(component),
        ROOTS_CSV_PATH: csv_bytes(
            [
                "component_id",
                "root_id",
                "order",
                "source_path",
                "target_path",
                "source_records",
                "target_records",
                "source_bytes",
                "target_bytes",
                "source_sha256",
                "target_sha256",
                "source_title",
                "target_title",
                "prerequisite_root_ids",
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
        SURFACES_CSV_PATH: csv_bytes(
            [
                "surface_id",
                "order",
                "kind",
                "path",
                "role",
                "required",
                "generated",
                "bytes",
                "sha256",
            ],
            surfaces,
        ),
    }
    return artifacts, component, surfaces


def write_and_verify(regenerate: bool) -> dict[str, Any]:
    artifacts, component, _surfaces = expected_artifacts()
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
        row_count = (
            actual.count(b"\n") - 1 if path.suffix == ".csv" else None
        )
        artifact_receipt.append(
            {
                "path": relative_path(path),
                "bytes": len(actual),
                "sha256": sha256_bytes(actual),
                "rows": row_count,
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
            "authority_commit_exact": True,
            "authority_tree_exact": True,
            "authority_archive_bytes_and_sha256_exact": True,
            "seven_root_driver_order_exact": True,
            "source_target_section_topology_exact": True,
            "source_target_semantic_environment_topology_exact": True,
            "source_target_formula_topology_and_normalized_structure_exact": True,
            "source_target_label_ref_citation_index_topology_exact": True,
            "all_nonpackage_refs_resolved": True,
            "all_citations_resolved": True,
            "locale_neutral_ids_unique": True,
            "prerequisites_resolved_and_acyclic_by_order": True,
            "utf8_lf_inputs_and_outputs": True,
            "independent_nonendorsement_provenance_present": True,
            "external_assignment_boundary_present": True,
            "model_provenance_present": True,
            "artifact_regeneration_byte_identical": True,
        },
        "authority": {
            "commit_sha1": AUTHORITY_COMMIT,
            "tree_sha1": AUTHORITY_TREE,
            "archive_bytes": AUTHORITY_ARCHIVE_BYTES,
            "archive_sha256": AUTHORITY_ARCHIVE_SHA256,
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
    reread = RECEIPT_PATH.read_bytes()
    assert_equal(reread, receipt_raw, "receipt write")
    return {
        "result": "PASS",
        "counts": component["counts"],
        "artifacts": artifact_receipt,
        "receipt": {
            "path": relative_path(RECEIPT_PATH),
            "bytes": len(reread),
            "sha256": sha256_bytes(reread),
        },
        "validator": receipt["validator"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate and validate the Duncan modular backend."
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
