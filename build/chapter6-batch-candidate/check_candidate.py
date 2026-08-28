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
    / "chapter6.tex"
)
CANDIDATE = Path(__file__).with_name("chapter6-lines-0001-0337-id.tex")

AUTHORITY_SHA256 = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
SOURCE_SLICE_SHA256 = "02459418fdfcff285fc75f93c7847268214ccae5e2564a4c0b91cfcd8fa6a566"
CANDIDATE_SHA256 = "55d99163b73efef90d6a28ebe6a96faff4b68018e7ec5f04212d530cb80fee34"
SOURCE_START = 1
SOURCE_END = 337
NEXT_CURSOR = r"\section{自由模}\label{sec:free-modules}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_text(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is forbidden: {path}")
    if b"\r" in data:
        raise ValueError(f"CR bytes are forbidden: {path}")
    return data, data.decode("utf-8", errors="strict")


def captures(pattern: str, text: str) -> list[tuple[str, ...]]:
    return [match.groups() for match in re.finditer(pattern, text)]


def math_fragments(text: str) -> list[str]:
    display = [match.group(1) for match in re.finditer(r"\\\[(.*?)\\\]", text, re.S)]
    stripped = re.sub(r"\\\[.*?\\\]", "", text, flags=re.S)
    inline = [match.group(1) for match in re.finditer(r"(?<!\\)\$(.*?)(?<!\\)\$", stripped, re.S)]
    return display + inline


def display_math(text: str) -> list[str]:
    return [match.group(1) for match in re.finditer(r"\\\[(.*?)\\\]", text, re.S)]


def inline_math(text: str) -> list[str]:
    stripped = re.sub(r"\\\[.*?\\\]", "", text, flags=re.S)
    return [match.group(1) for match in re.finditer(r"(?<!\\)\$(.*?)(?<!\\)\$", stripped, re.S)]


def math_skeleton(fragment: str) -> str:
    value = re.sub(r"\\text\{[^{}]*\}", r"\\text{}", fragment)
    value = re.sub(r'"[^"\n]*"', '""', value)
    value = re.sub(r"\s+", "", value)
    return value


def substantive_math(fragment: str) -> bool:
    value = math_skeleton(fragment)
    alphanumeric = re.sub(r"\\[A-Za-z]+|[^A-Za-z0-9]", "", value)
    return len(alphanumeric) > 1 or any(char in value for char in "=<>:+-/()[]{}_^" )


def balanced_braces(text: str) -> bool:
    depth = 0
    for index, char in enumerate(text):
        if char == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def main() -> int:
    failures: list[str] = []
    authority_bytes, authority_text = strict_text(AUTHORITY)
    candidate_bytes, candidate_text = strict_text(CANDIDATE)

    if sha256(authority_bytes) != AUTHORITY_SHA256:
        failures.append("frozen authority hash mismatch")

    authority_lines = authority_text.splitlines()
    candidate_lines = candidate_text.splitlines()
    source_text = "\n".join(authority_lines[SOURCE_START - 1 : SOURCE_END]) + "\n"
    source_bytes = source_text.encode("utf-8")
    if sha256(source_bytes) != SOURCE_SLICE_SHA256:
        failures.append("normalized authority slice hash mismatch")
    if sha256(candidate_bytes) != CANDIDATE_SHA256:
        failures.append("candidate hash mismatch")
    if len(candidate_lines) != SOURCE_END - SOURCE_START + 1:
        failures.append("candidate record count differs from source slice")
    if authority_lines[SOURCE_END] != NEXT_CURSOR:
        failures.append("next-cursor sentinel mismatch")

    exact_sequences = {
        "begin environments": r"\\begin\{([^}]+)\}",
        "end environments": r"\\end\{([^}]+)\}",
        "labels": r"\\label\{([^}]+)\}",
        "references": r"\\(ref|eqref|rref|cref)\{([^}]+)\}",
        "citations": r"\\(cite|parencite|textcite)(?:\[[^\]]*\])?\{([^}]+)\}",
    }
    for name, pattern in exact_sequences.items():
        if captures(pattern, source_text) != captures(pattern, candidate_text):
            failures.append(f"{name} sequence mismatch")

    source_indexes = len(re.findall(r"\\index(?:\[[^\]]+\])?\{", source_text))
    target_indexes = len(re.findall(r"\\index(?:\[[^\]]+\])?\{", candidate_text))
    if source_indexes != target_indexes:
        failures.append("index-command count mismatch")

    for token in (r"\begin{align", r"\begin{tikzcd", r"\item", r"\\"):
        if source_text.count(token) != candidate_text.count(token):
            failures.append(f"structural token count mismatch: {token}")

    source_display = [math_skeleton(item) for item in display_math(source_text)]
    target_display = [math_skeleton(item) for item in display_math(candidate_text)]
    if source_display != target_display:
        failures.append("display-math skeleton sequence mismatch")
    source_math = [math_skeleton(item) for item in math_fragments(source_text)]
    target_math = [math_skeleton(item) for item in math_fragments(candidate_text)]
    source_inline = Counter(
        math_skeleton(item) for item in inline_math(source_text) if substantive_math(item)
    )
    target_inline = Counter(
        math_skeleton(item) for item in inline_math(candidate_text) if substantive_math(item)
    )
    if source_inline != target_inline:
        failures.append("substantive inline-math multiset mismatch")

    if not balanced_braces(candidate_text):
        failures.append("candidate has unbalanced braces")
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", candidate_text))
    if cjk_count:
        failures.append(f"candidate contains {cjk_count} CJK residue characters")
    if re.search(r"TODO|FIXME|TBD|@@|TRANSLATE", candidate_text, re.I):
        failures.append("candidate contains placeholder residue")
    if candidate_text == source_text:
        failures.append("candidate is unchanged authority text")

    environment_counts = Counter(name for (name,) in captures(r"\\begin\{([^}]+)\}", candidate_text))
    print(f"authority={AUTHORITY}")
    print(f"authority_sha256={sha256(authority_bytes)}")
    print(f"source_range={SOURCE_START}-{SOURCE_END}")
    print(f"source_records={SOURCE_END - SOURCE_START + 1}")
    print(f"source_bytes_normalized={len(source_bytes)}")
    print(f"source_slice_sha256={sha256(source_bytes)}")
    print(f"candidate={CANDIDATE}")
    print(f"candidate_records={len(candidate_lines)}")
    print(f"candidate_bytes={len(candidate_bytes)}")
    print(f"candidate_sha256={sha256(candidate_bytes)}")
    print(f"labels={len(captures(exact_sequences['labels'], candidate_text))}")
    print(f"references={len(captures(exact_sequences['references'], candidate_text))}")
    print(f"citations={len(captures(exact_sequences['citations'], candidate_text))}")
    print(f"indexes={target_indexes}")
    print(f"math_fragments={len(target_math)}")
    print(f"environments={dict(sorted(environment_counts.items()))}")
    print(f"next_cursor=chapter6.tex:{SOURCE_END + 1}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
