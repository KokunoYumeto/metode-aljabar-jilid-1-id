from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "authority" / "source" / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b" / "chapter6.tex"
CANDIDATE = Path(__file__).with_name("chapter6-lines-0974-1663-id.tex")
AUTHORITY_SHA256 = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
SOURCE_SLICE_SHA256 = "80ca8dce3687a47498c927d8621b4fd772ca299b374cee26c20e0a0a4c09555a"
CANDIDATE_SHA256 = "b6a02ff43f55dbe498cab34ff3f34ef4aaf581a8b37487c85a8ea24a0a8dd315"
SOURCE_START = 974
SOURCE_END = 1663
NEXT_CURSOR = r"\section{半单模}"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_strict(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM forbidden: {path}")
    if b"\r" in data:
        raise ValueError(f"CR bytes forbidden: {path}")
    return data, data.decode("utf-8", errors="strict")


def captures(pattern: str, text: str) -> list[tuple[str, ...]]:
    return [match.groups() for match in re.finditer(pattern, text)]


def scrub_balanced_command(fragment: str, command: str) -> str:
    marker = command + "{"
    output: list[str] = []
    cursor = 0
    while True:
        start = fragment.find(marker, cursor)
        if start < 0:
            output.append(fragment[cursor:])
            break
        output.append(fragment[cursor:start])
        depth = 1
        index = start + len(marker)
        while index < len(fragment) and depth:
            if fragment[index] == "{" and fragment[index - 1] != "\\":
                depth += 1
            elif fragment[index] == "}" and fragment[index - 1] != "\\":
                depth -= 1
            index += 1
        output.append(command + "{}")
        cursor = index
    return "".join(output)


def skeleton(fragment: str) -> str:
    value = scrub_balanced_command(fragment, r"\text")
    value = re.sub(r"\scriptsize\s+[^}\n]*", lambda _: r"\scriptsize", value)
    value = re.sub(r'"[^"\n]*"', '""', value)
    return re.sub(r"\s+", "", value)


def bracket_displays(text: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"\\\[(.*?)\\\]", text, re.S)]


def dollar_displays(text: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"(?<!\\)\$\$(.*?)(?<!\\)\$\$", text, re.S)]


def inline_math(text: str) -> list[str]:
    stripped = re.sub(r"\\\[.*?\\\]", "", text, flags=re.S)
    stripped = re.sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$", "", stripped, flags=re.S)
    return [match.group(1) for match in re.finditer(r"(?<!\\)\$(.*?)(?<!\\)\$", stripped, re.S)]


def substantive(fragment: str) -> bool:
    value = skeleton(fragment)
    alphanumeric = re.sub(r"\\[A-Za-z]+|[^A-Za-z0-9]", "", value)
    return len(alphanumeric) > 1 or any(char in value for char in "=<>:+-/()[]{}_^" )


def line_structure(line: str) -> list[str]:
    return re.findall(
        r"\\(chapter|section|subsection|subsubsection|begin|end|label|ref|eqref|rref|cref|cite|index|item)\b",
        line,
    )


def braces_balanced(text: str) -> bool:
    depth = 0
    for index, char in enumerate(text):
        escaped = index > 0 and text[index - 1] == "\\"
        if char == "{" and not escaped:
            depth += 1
        elif char == "}" and not escaped:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def main() -> int:
    failures: list[str] = []
    authority_bytes, authority_text = read_strict(AUTHORITY)
    candidate_bytes, candidate_text = read_strict(CANDIDATE)
    authority_lines = authority_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    source_lines = authority_lines[SOURCE_START - 1 : SOURCE_END]
    source_text = "\n".join(source_lines) + "\n"
    source_bytes = source_text.encode("utf-8")

    if digest(authority_bytes) != AUTHORITY_SHA256:
        failures.append("frozen authority hash mismatch")
    if digest(source_bytes) != SOURCE_SLICE_SHA256:
        failures.append("authority slice hash mismatch")
    if digest(candidate_bytes) != CANDIDATE_SHA256:
        failures.append("candidate hash mismatch")
    if len(candidate_lines) != SOURCE_END - SOURCE_START + 1:
        failures.append("record count mismatch")
    if authority_lines[SOURCE_END] != NEXT_CURSOR:
        failures.append("next-cursor sentinel mismatch")

    exact = {
        "begin environments": r"\\begin\{([^}]+)\}",
        "end environments": r"\\end\{([^}]+)\}",
        "labels": r"\\label\{([^}]+)\}",
        "references": r"\\(ref|eqref|rref|cref)\{([^}]+)\}",
        "citations": r"\\(cite|parencite|textcite)(?:\[[^\]]*\])?\{([^}]+)\}",
    }
    for name, pattern in exact.items():
        if captures(pattern, source_text) != captures(pattern, candidate_text):
            failures.append(f"{name} sequence mismatch")

    source_indexes = len(re.findall(r"\\index(?:\[[^\]]+\])?\{", source_text))
    target_indexes = len(re.findall(r"\\index(?:\[[^\]]+\])?\{", candidate_text))
    if source_indexes != target_indexes:
        failures.append("index count mismatch")

    if len(candidate_lines) == len(source_lines):
        for offset, (source_line, target_line) in enumerate(zip(source_lines, candidate_lines)):
            if line_structure(source_line) != line_structure(target_line):
                failures.append(f"line-level TeX topology mismatch at authority line {SOURCE_START + offset}")
                break
        source_comments = [i for i, line in enumerate(source_lines) if line.lstrip().startswith("%")]
        target_comments = [i for i, line in enumerate(candidate_lines) if line.lstrip().startswith("%")]
        if source_comments != target_comments:
            failures.append("comment-line topology mismatch")

    source_bracket = [skeleton(item) for item in bracket_displays(source_text)]
    target_bracket = [skeleton(item) for item in bracket_displays(candidate_text)]
    if source_bracket != target_bracket:
        failures.append("bracket-display skeleton sequence mismatch")
    source_dollars = [skeleton(item) for item in dollar_displays(source_text)]
    target_dollars = [skeleton(item) for item in dollar_displays(candidate_text)]
    if source_dollars != target_dollars:
        failures.append("double-dollar display skeleton sequence mismatch")
    source_inline = Counter(skeleton(item) for item in inline_math(source_text) if substantive(item))
    target_inline = Counter(skeleton(item) for item in inline_math(candidate_text) if substantive(item))
    if source_inline != target_inline:
        failures.append("substantive inline-math multiset mismatch")

    if not braces_balanced(candidate_text):
        failures.append("unbalanced braces")
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", candidate_text))
    if cjk_count:
        failures.append(f"{cjk_count} CJK residue characters")
    if re.search(r"TODO|FIXME|TBD|@@|TRANSLATE", candidate_text, re.I):
        failures.append("placeholder residue")
    if "produk tensor" in candidate_text.lower():
        failures.append("superseded tensor terminology residue")

    environments = Counter(name for (name,) in captures(exact["begin environments"], candidate_text))
    print(f"authority={AUTHORITY}")
    print(f"authority_sha256={digest(authority_bytes)}")
    print(f"source_range={SOURCE_START}-{SOURCE_END}")
    print(f"source_records={len(source_lines)}")
    print(f"source_bytes_normalized={len(source_bytes)}")
    print(f"source_slice_sha256={digest(source_bytes)}")
    print(f"candidate={CANDIDATE}")
    print(f"candidate_records={len(candidate_lines)}")
    print(f"candidate_bytes={len(candidate_bytes)}")
    print(f"candidate_sha256={digest(candidate_bytes)}")
    print(f"labels={len(captures(exact['labels'], candidate_text))}")
    print(f"references={len(captures(exact['references'], candidate_text))}")
    print(f"citations={len(captures(exact['citations'], candidate_text))}")
    print(f"indexes={target_indexes}")
    print(f"bracket_displays={len(target_bracket)}")
    print(f"dollar_displays={len(target_dollars)}")
    print(f"substantive_inline_math={sum(target_inline.values())}")
    print(f"environments={dict(sorted(environments.items()))}")
    print(f"next_cursor=chapter6.tex:{SOURCE_END + 1}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
