from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter6.tex"
COMPLETE = HERE / "chapter6-complete-id.tex"
AUTHORITY_SHA256 = "c825f51dc19c254c89a7ede05723b62d6cd2b18cc6ac8c78d9ea00c3b8434e49"
COMPLETE_SHA256 = "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14"
SEGMENTS = (
    HERE / "chapter6-lines-0001-0337-id.tex",
    HERE / "chapter6-lines-0338-0973-id.tex",
    HERE / "chapter6-lines-0974-1663-id.tex",
    HERE / "chapter6-lines-1664-1994-id.tex",
)
CHECKERS = (
    HERE / "check_candidate.py",
    HERE / "check_candidate_0338_0973.py",
    HERE / "check_candidate_0974_1663.py",
    HERE / "check_candidate_1664_1994.py",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise RuntimeError(f"noncanonical encoding/newlines: {path}")
    return data, data.decode("utf-8", errors="strict")


def sequence(pattern: str, text: str) -> list[tuple[str, ...]]:
    return [match.groups() for match in re.finditer(pattern, text)]


def main() -> int:
    failures: list[str] = []
    checker_summaries: list[str] = []
    for checker in CHECKERS:
        result = subprocess.run(
            [sys.executable, str(checker)], cwd=ROOT,
            text=True, encoding="utf-8", stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False,
        )
        checker_summaries.append(f"{checker.name}:{'PASS' if result.returncode == 0 else 'FAIL'}")
        if result.returncode:
            failures.append(f"segment checker failed: {checker.name}\n{result.stdout}")

    authority_bytes, authority_text = strict(AUTHORITY)
    complete_bytes, complete_text = strict(COMPLETE)
    if digest(authority_bytes) != AUTHORITY_SHA256:
        failures.append("authority hash mismatch")
    if digest(complete_bytes) != COMPLETE_SHA256:
        failures.append("complete candidate hash mismatch")
    expected = "\n".join(strict(path)[1].rstrip("\n") for path in SEGMENTS) + "\n"
    if complete_text != expected:
        failures.append("complete candidate is not the exact ordered segment concatenation")
    if len(authority_text.splitlines()) != 1994 or len(complete_text.splitlines()) != 1994:
        failures.append("record-count/whole-chapter closure mismatch")

    exact = {
        "environment starts": r"\\begin\{([^}]+)\}",
        "environment ends": r"\\end\{([^}]+)\}",
        "labels": r"\\label\{([^}]+)\}",
        "references": r"\\(ref|eqref|rref|cref)\{([^}]+)\}",
        "citations": r"\\(cite|parencite|textcite)(?:\[[^\]]*\])?\{([^}]+)\}",
    }
    for name, pattern in exact.items():
        if sequence(pattern, authority_text) != sequence(pattern, complete_text):
            failures.append(f"whole-chapter {name} sequence mismatch")
    for name, pattern in {
        "sections": r"\\section\{",
        "indexes": r"\\index(?:\[[^\]]+\])?\{",
        "items": r"\\item\b",
        "hints": r"\\begin\{hint\}|\\hint\{",
    }.items():
        if len(re.findall(pattern, authority_text)) != len(re.findall(pattern, complete_text)):
            failures.append(f"whole-chapter {name} count mismatch")
    cjk = len(re.findall(r"[\u3400-\u9fff]", complete_text))
    if cjk:
        failures.append(f"{cjk} CJK residue characters")
    if re.search(r"TODO|FIXME|TBD|@@|TRANSLATE", complete_text, re.I):
        failures.append("placeholder residue")

    print(f"authority_records={len(authority_text.splitlines())}")
    print(f"authority_bytes={len(authority_bytes)}")
    print(f"authority_sha256={digest(authority_bytes)}")
    print(f"candidate_records={len(complete_text.splitlines())}")
    print(f"candidate_bytes={len(complete_bytes)}")
    print(f"candidate_sha256={digest(complete_bytes)}")
    print(f"segment_checkers={','.join(checker_summaries)}")
    print(f"sections={len(re.findall(r'\\section\{', complete_text))}")
    print(f"labels={len(sequence(r'\\label\{([^}]+)\}', complete_text))}")
    print(f"references={len(sequence(r'\\(ref|eqref|rref|cref)\{([^}]+)\}', complete_text))}")
    print(f"citations={len(sequence(r'\\(cite|parencite|textcite)(?:\[[^\]]*\])?\{([^}]+)\}', complete_text))}")
    print(f"indexes={len(re.findall(r'\\index(?:\[[^\]]+\])?\{', complete_text))}")
    print(f"items={len(re.findall(r'\\item\b', complete_text))}")
    print("next_cursor=chapter7.tex:1")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
