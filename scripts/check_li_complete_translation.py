#!/usr/bin/env python3
"""One bounded gate for the complete Li Volume 1 Indonesian source closure."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
TARGET = ROOT / "repo/source"
FREEZE = ROOT / "qa/LI_COMPLETE_TRANSLATION_FREEZE.json"
FILES = ["prelude.tex", *(f"chapter{number}.tex" for number in range(1, 11))]
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def identity(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    require(not payload.startswith(b"\xef\xbb\xbf") and b"\r" not in payload,
            f"noncanonical UTF-8/LF file: {path}")
    text = payload.decode("utf-8", errors="strict")
    return {
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "records": len(text.splitlines()),
    }


def active_text(text: str) -> str:
    rows: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for match in re.finditer(r"%", line):
            position = match.start()
            backslashes = 0
            cursor = position - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = position
                break
        rows.append(line[:cut])
    return "\n".join(rows)


def balanced_braces(text: str) -> bool:
    depth = 0
    for position, character in enumerate(text):
        escaped = position > 0 and text[position - 1] == "\\"
        if escaped:
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def topology(text: str) -> dict[str, int]:
    exercises = ""
    if r"\begin{Exercises}" in text and r"\end{Exercises}" in text:
        exercises = text.split(r"\begin{Exercises}", 1)[1].split(r"\end{Exercises}", 1)[0]
    return {
        "environment_starts": len(re.findall(r"\\begin\{[^{}]+\}", text)),
        "environment_ends": len(re.findall(r"\\end\{[^{}]+\}", text)),
        "labels": len(re.findall(r"\\label\{[^{}]+\}", text)),
        "references": len(re.findall(r"\\(?:ref|eqref|rref|cref)\{[^{}]+\}", text)),
        "citations": len(re.findall(r"\\cite(?:\[[^\]]*\])?\{[^{}]+\}", text)),
        "indexes": len(re.findall(r"\\index(?:\[[^\]]+\])?\{", text)),
        "items": len(re.findall(r"\\item\b", text)),
        "top_level_exercises": len(re.findall(r"(?m)^\t\\item\b", exercises)),
        "exercise_items": len(re.findall(r"\\item\b", exercises)),
        "hints": len(re.findall(r"\\begin\{hint\}", text)),
        "inline_math_delimiters": len(re.findall(r"(?<!\\)\$", text)),
    }


def main() -> int:
    require(FREEZE.is_file(), f"missing complete translation freeze: {FREEZE}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    require(freeze.get("schema") == "o013.li-complete-translation-freeze.v1", "freeze schema drift")
    require(freeze.get("result") == "pass", "freeze is not admitted")
    require(freeze.get("authority_commit") == "c4f7a01f68f5f407906b4b970640cddbbad85f6b", "authority commit drift")
    require(freeze.get("authority_tree") == "0f9fd52748165ec89a85ba602ccb949a2ce04694", "authority tree drift")
    records = {item["filename"]: item for item in freeze.get("files", [])}
    require(set(records) == set(FILES), "freeze file closure drift")

    aggregate = Counter()
    results: list[dict[str, object]] = []
    for filename in FILES:
        source_path = AUTHORITY / filename
        target_path = TARGET / filename
        require(source_path.is_file() and target_path.is_file(), f"missing source pair: {filename}")
        source_identity = identity(source_path)
        target_identity = identity(target_path)
        expected = records[filename]
        require(source_identity == expected.get("authority"), f"authority identity drift: {filename}")
        require(target_identity == expected.get("target"), f"target identity drift: {filename}")
        source_active = active_text(source_path.read_text(encoding="utf-8"))
        target_active = active_text(target_path.read_text(encoding="utf-8"))
        require(not HAN.search(target_active), f"active Han residue: {filename}")
        require(balanced_braces(target_active), f"unbalanced target braces: {filename}")
        for residue in ("ZXQ", "__MATH_", "⟦", "⟧"):
            require(residue not in target_active, f"translation residue {residue!r}: {filename}")
        target_topology = topology(target_active)
        source_topology = topology(source_active)
        require(target_topology == expected.get("target_topology"), f"target topology drift: {filename}")
        require(source_topology == expected.get("authority_topology"), f"authority topology drift: {filename}")
        require(target_topology["environment_starts"] == target_topology["environment_ends"],
                f"unbalanced environments: {filename}")
        aggregate.update(target_topology)
        results.append({"filename": filename, "target": target_identity, "topology": target_topology})

    expected_aggregate = freeze.get("target_aggregate_topology")
    require(dict(aggregate) == expected_aggregate, "aggregate topology drift")
    require(aggregate["top_level_exercises"] == 161, "active source exercise census drift")
    require(aggregate["hints"] == 51, "active source hint census drift")
    print(json.dumps({
        "result": "PASS",
        "files": len(results),
        "records": sum(item["target"]["records"] for item in results),
        "bytes": sum(item["target"]["bytes"] for item in results),
        "top_level_exercises": aggregate["top_level_exercises"],
        "hints": aggregate["hints"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
