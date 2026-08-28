from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "authority" / "source" / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b" / "chapter6.tex"
CANDIDATE = Path(__file__).with_name("chapter6-lines-1664-1994-id.tex")
AUTHORITY_SHA256 = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
SOURCE_SLICE_SHA256 = "e5f925fff526a56459c1315ffa980cca67576ee4227dd5b9548e887a51253539"
CANDIDATE_SHA256 = "50091364e1692e8286ca5b8f87011e0f5c2e2a2958b4f9b21ca3a8d514927108"
SOURCE_START = 1664
SOURCE_END = 1994


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
    value = scrub_balanced_command(value, r"\mbox")
    value = re.sub(r"%[^\n]*", "", value)
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


def topology_failures(source_text: str, candidate_text: str) -> list[str]:
    failures: list[str] = []
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

    for name, pattern in {
        "sections": r"\\section\{",
        "indexes": r"\\index(?:\[[^\]]+\])?\{",
        "items": r"\\item\b",
        "inline hints": r"\\hint\{",
    }.items():
        if len(re.findall(pattern, source_text)) != len(re.findall(pattern, candidate_text)):
            failures.append(f"{name} count mismatch")

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

    source_tikz = [skeleton(item) for item in re.findall(r"\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}", source_text, re.S)]
    target_tikz = [skeleton(item) for item in re.findall(r"\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}", candidate_text, re.S)]
    if source_tikz != target_tikz:
        failures.append("TikZ skeleton sequence mismatch")
    return failures


def main() -> int:
    failures: list[str] = []
    authority_bytes, authority_text = read_strict(AUTHORITY)
    candidate_bytes, candidate_text = read_strict(CANDIDATE)
    authority_lines = authority_text.splitlines()
    source_lines = authority_lines[SOURCE_START - 1 : SOURCE_END]
    source_text = "\n".join(source_lines) + "\n"
    source_bytes = source_text.encode("utf-8")

    if digest(authority_bytes) != AUTHORITY_SHA256:
        failures.append("frozen authority hash mismatch")
    if digest(source_bytes) != SOURCE_SLICE_SHA256:
        failures.append("authority slice hash mismatch")
    if digest(candidate_bytes) != CANDIDATE_SHA256:
        failures.append("candidate hash mismatch")
    if len(authority_lines) != SOURCE_END:
        failures.append("chapter-end sentinel mismatch")
    failures.extend(topology_failures(source_text, candidate_text))
    if not braces_balanced(candidate_text):
        failures.append("unbalanced braces")
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", candidate_text))
    if cjk_count:
        failures.append(f"{cjk_count} CJK residue characters")
    if re.search(r"TODO|FIXME|TBD|@@|TRANSLATE", candidate_text, re.I):
        failures.append("placeholder residue")
    if "produk tensor" in candidate_text.lower():
        failures.append("superseded tensor terminology residue")

    environments = Counter(name for (name,) in captures(r"\\begin\{([^}]+)\}", candidate_text))
    print(f"authority={AUTHORITY}")
    print(f"authority_sha256={digest(authority_bytes)}")
    print(f"source_range={SOURCE_START}-{SOURCE_END}")
    print(f"source_records={len(source_lines)}")
    print(f"source_bytes_normalized={len(source_bytes)}")
    print(f"source_slice_sha256={digest(source_bytes)}")
    print(f"candidate={CANDIDATE}")
    print(f"candidate_records={len(candidate_text.splitlines())}")
    print(f"candidate_bytes={len(candidate_bytes)}")
    print(f"candidate_sha256={digest(candidate_bytes)}")
    print(f"labels={len(captures(r'\\label\{([^}]+)\}', candidate_text))}")
    print(f"references={len(captures(r'\\(ref|eqref|rref|cref)\{([^}]+)\}', candidate_text))}")
    print(f"citations={len(captures(r'\\(cite|parencite|textcite)(?:\[[^\]]*\])?\{([^}]+)\}', candidate_text))}")
    print(f"indexes={len(re.findall(r'\\index(?:\[[^\]]+\])?\{', candidate_text))}")
    print(f"items={len(re.findall(r'\\item\b', candidate_text))}")
    print(f"bracket_displays={len(bracket_displays(candidate_text))}")
    print(f"substantive_inline_math={sum(Counter(skeleton(item) for item in inline_math(candidate_text) if substantive(item)).values())}")
    print(f"environments={dict(sorted(environments.items()))}")
    print("next_cursor=chapter7.tex:1")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
