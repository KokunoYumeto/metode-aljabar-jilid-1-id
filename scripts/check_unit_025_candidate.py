#!/usr/bin/env python3
"""Fail-closed structural admission check for the isolated Unit 025 candidate."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter4.tex"
)
CANDIDATE = ROOT / "build" / "unit-025-candidate" / "chapter4-group-basics-id.tex"

SOURCE_FILE_BYTES = 154_744
SOURCE_FILE_SHA256 = "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3"
SOURCE_RECORDS = 1_898
SOURCE_START_LINE = 1
SOURCE_END_LINE = 176
SOURCE_SLICE_BYTES = 15_528
SOURCE_SLICE_SHA256 = "d88ca03645fd4c781d16907e063b06cd072ad5fbe0e48ce2149d8fdecfb76a52"
SOURCE_NEXT_LINE_BYTES = 49
SOURCE_NEXT_LINE_SHA256 = "60ddf2971ef969510be8fa725a96b29d6d2dc7bfd1a62c9e45415368a627c46a"

CANDIDATE_BYTES = 20_464
CANDIDATE_SHA256 = "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a"
CANDIDATE_RECORDS = 178

MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
NON_ENDORSEMENT = (
    "Terjemahan independen ini tidak menyiratkan dukungan penulis "
    "atau sumber manusia mana pun."
)
CORRECTION_ID = "O013-LI-U025-COR-001"

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
BEGIN_RE = re.compile(r"\\begin\{([^{}]+)\}")
END_RE = re.compile(r"\\end\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref)\{([^{}]+)\}")
CITE_RE = re.compile(r"\\cite(?:\[[^\]]*\])?\{([^{}]+)\}")
INDEX_RE = re.compile(r"\\index(?P<option>\[[^\]]+\])?\{")
ITEM_RE = re.compile(r"\\item\b")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_utf8_strict(data: bytes, label: str, failures: list[str]) -> str:
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        failures.append(f"{label}: bukan UTF-8 ketat ({exc})")
        return ""


def strip_comments(text: str) -> str:
    cleaned: list[str] = []
    for line in text.splitlines():
        cut = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                cut = index
                break
        cleaned.append(line[:cut])
    return "\n".join(cleaned)


def balanced_braces(text: str) -> bool:
    depth = 0
    for index, char in enumerate(text):
        if char not in "{}":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and text[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2:
            continue
        depth += 1 if char == "{" else -1
        if depth < 0:
            return False
    return depth == 0


def environment_stack_ok(text: str) -> bool:
    token_re = re.compile(r"\\(?P<kind>begin|end)\{(?P<name>[^{}]+)\}")
    stack: list[str] = []
    for match in token_re.finditer(text):
        kind = match.group("kind")
        name = match.group("name")
        if kind == "begin":
            stack.append(name)
        elif not stack or stack.pop() != name:
            return False
    return not stack


def extract_math(text: str) -> list[str]:
    """Extract ordered inline/display math and align* bodies from comment-free TeX."""

    pattern = re.compile(
        r"\\\[(?P<bracket>.*?)\\\]"
        r"|\\begin\{align\*\}(?P<align>.*?)\\end\{align\*\}"
        r"|(?<!\\)\$(?P<inline>.*?)(?<!\\)\$",
        re.DOTALL,
    )
    result: list[str] = []
    for match in pattern.finditer(text):
        result.append(next(group for group in match.groups() if group is not None))
    return result


def canonical_math(math: str) -> str:
    math = re.sub(r"\\text\{[^{}]*\}", r"\\text{<TEXT>}", math)
    return re.sub(r"\s+", "", math)


def main() -> int:
    failures: list[str] = []

    if not SOURCE.is_file():
        failures.append(f"sumber tidak ditemukan: {SOURCE}")
        source_bytes = b""
    else:
        source_bytes = SOURCE.read_bytes()

    if not CANDIDATE.is_file():
        failures.append(f"kandidat tidak ditemukan: {CANDIDATE}")
        candidate_bytes = b""
    else:
        candidate_bytes = CANDIDATE.read_bytes()

    if len(source_bytes) != SOURCE_FILE_BYTES:
        failures.append(f"ukuran sumber berubah: {len(source_bytes)} != {SOURCE_FILE_BYTES}")
    if sha256(source_bytes) != SOURCE_FILE_SHA256:
        failures.append("SHA-256 sumber berubah")
    if source_bytes.startswith(b"\xef\xbb\xbf"):
        failures.append("sumber memiliki BOM UTF-8 yang tidak diharapkan")
    if b"\r" in source_bytes:
        failures.append("sumber tidak lagi memakai LF murni")

    source_records = source_bytes.splitlines(keepends=True)
    if len(source_records) != SOURCE_RECORDS:
        failures.append(f"jumlah rekaman sumber berubah: {len(source_records)} != {SOURCE_RECORDS}")
    source_slice = b"".join(source_records[SOURCE_START_LINE - 1 : SOURCE_END_LINE])
    if len(source_slice) != SOURCE_SLICE_BYTES:
        failures.append(f"ukuran irisan sumber berubah: {len(source_slice)} != {SOURCE_SLICE_BYTES}")
    if sha256(source_slice) != SOURCE_SLICE_SHA256:
        failures.append("SHA-256 irisan sumber berubah")
    if not source_slice.endswith(b"\n"):
        failures.append("irisan sumber tidak berakhir dengan LF")
    if len(source_records) > SOURCE_END_LINE:
        next_line = source_records[SOURCE_END_LINE].rstrip(b"\r\n")
        if len(next_line) != SOURCE_NEXT_LINE_BYTES or sha256(next_line) != SOURCE_NEXT_LINE_SHA256:
            failures.append("batas Unit 025 tidak lagi tepat sebelum Bagian 4.2")
    else:
        failures.append("sumber berakhir sebelum batas alami Unit 025")

    if len(candidate_bytes) != CANDIDATE_BYTES:
        failures.append(f"ukuran kandidat berubah: {len(candidate_bytes)} != {CANDIDATE_BYTES}")
    if sha256(candidate_bytes) != CANDIDATE_SHA256:
        failures.append("SHA-256 kandidat berubah")
    if candidate_bytes.startswith(b"\xef\xbb\xbf"):
        failures.append("kandidat memiliki BOM UTF-8")
    if b"\r" in candidate_bytes:
        failures.append("kandidat harus memakai LF murni")
    if candidate_bytes and not candidate_bytes.endswith(b"\n"):
        failures.append("kandidat tidak berakhir dengan LF")
    candidate_records = candidate_bytes.splitlines()
    if len(candidate_records) != CANDIDATE_RECORDS:
        failures.append(
            f"jumlah rekaman kandidat berubah: {len(candidate_records)} != {CANDIDATE_RECORDS}"
        )

    source_text = decode_utf8_strict(source_slice, "irisan sumber", failures)
    candidate_text = decode_utf8_strict(candidate_bytes, "kandidat", failures)
    source_clean = strip_comments(source_text)
    candidate_clean = strip_comments(candidate_text)

    han = HAN_RE.findall(candidate_text)
    if han:
        failures.append(f"kandidat memuat {len(han)} aksara Han yang tidak diizinkan")
    if candidate_text.count(MODEL_PROVENANCE) != 1:
        failures.append("provenans model harus muncul tepat sekali")
    if candidate_text.count(NON_ENDORSEMENT) != 1:
        failures.append("pernyataan non-dukungan harus muncul tepat sekali")
    if candidate_text.count("CC BY 4.0") != 1:
        failures.append("pemberitahuan CC BY 4.0 harus muncul tepat sekali")
    if candidate_text.count("Wen-Wei Li") != 1:
        failures.append("kredit Wen-Wei Li harus muncul tepat sekali")
    if candidate_text.count(CORRECTION_ID) != 1:
        failures.append("ID koreksi sumber harus muncul tepat sekali")

    for label, regex in (
        ("lingkungan awal", BEGIN_RE),
        ("lingkungan akhir", END_RE),
        ("label", LABEL_RE),
        ("referensi", REF_RE),
        ("sitasi", CITE_RE),
    ):
        source_values = regex.findall(source_clean)
        candidate_values = regex.findall(candidate_clean)
        if source_values != candidate_values:
            failures.append(f"urutan {label} berubah")

    source_index_options = [match.group("option") for match in INDEX_RE.finditer(source_clean)]
    candidate_index_options = [match.group("option") for match in INDEX_RE.finditer(candidate_clean)]
    if source_index_options != candidate_index_options:
        failures.append("jumlah/opsi entri indeks berubah")
    if len(source_index_options) != 25:
        failures.append(f"inventaris indeks sumber tak terduga: {len(source_index_options)} != 25")

    source_items = len(ITEM_RE.findall(source_clean))
    candidate_items = len(ITEM_RE.findall(candidate_clean))
    if source_items != candidate_items or source_items != 24:
        failures.append(f"jumlah item berubah: sumber={source_items}, kandidat={candidate_items}")

    for command, expected in (("chapter", 1), ("section", 1), ("subsection", 0)):
        command_re = re.compile(rf"\\{command}\{{")
        source_count = len(command_re.findall(source_clean))
        candidate_count = len(command_re.findall(candidate_clean))
        if source_count != expected or candidate_count != expected:
            failures.append(
                f"jumlah \\{command} berubah: sumber={source_count}, kandidat={candidate_count}, "
                f"harapan={expected}"
            )

    for label, text in (("sumber", source_clean), ("kandidat", candidate_clean)):
        if not balanced_braces(text):
            failures.append(f"kurung kurawal tidak seimbang pada {label}")
        if not environment_stack_ok(text):
            failures.append(f"tumpukan lingkungan tidak seimbang pada {label}")

    source_math = [canonical_math(item) for item in extract_math(source_clean)]
    candidate_math = [canonical_math(item) for item in extract_math(candidate_clean)]
    if len(source_math) != len(candidate_math):
        failures.append(
            f"jumlah ruas matematika berubah: sumber={len(source_math)}, kandidat={len(candidate_math)}"
        )
    else:
        source_math_inventory = Counter(source_math)
        expected_candidate_inventory = source_math_inventory.copy()
        if source_math_inventory[r"H\subsetG"] < 1:
            failures.append("ruas sumber H subset G untuk koreksi tidak ditemukan")
        else:
            expected_candidate_inventory[r"H\subsetG"] -= 1
            if expected_candidate_inventory[r"H\subsetG"] == 0:
                del expected_candidate_inventory[r"H\subsetG"]
            expected_candidate_inventory[r"H\subset\Z"] += 1
        candidate_math_inventory = Counter(candidate_math)
        if candidate_math_inventory != expected_candidate_inventory:
            missing = expected_candidate_inventory - candidate_math_inventory
            unexpected = candidate_math_inventory - expected_candidate_inventory
            failures.append(
                "inventaris ruas matematika berubah di luar koreksi yang diizinkan; "
                f"hilang={dict(missing)}, tak terduga={dict(unexpected)}"
            )
        if candidate_math_inventory[r"H\subsetG"] != source_math_inventory[r"H\subsetG"] - 1:
            failures.append("jumlah H subset G pada kandidat tidak mencerminkan tepat satu koreksi")
        if candidate_math_inventory[r"H\subset\Z"] != source_math_inventory[r"H\subset\Z"] + 1:
            failures.append("kandidat harus menambahkan tepat satu pembatas H subset Z")

    if failures:
        print("UNIT 025 CANDIDATE CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("UNIT 025 CANDIDATE CHECK: PASS")
    print(f"source_file_bytes={len(source_bytes)}")
    print(f"source_file_sha256={sha256(source_bytes)}")
    print(f"source_slice_lines={SOURCE_START_LINE}-{SOURCE_END_LINE}")
    print(f"source_slice_bytes={len(source_slice)}")
    print(f"source_slice_sha256={sha256(source_slice)}")
    print(f"candidate_records={len(candidate_records)}")
    print(f"candidate_bytes={len(candidate_bytes)}")
    print(f"candidate_sha256={sha256(candidate_bytes)}")
    print(f"math_spans={len(source_math)}")
    print(f"labels={len(LABEL_RE.findall(source_clean))}")
    print(f"refs={len(REF_RE.findall(source_clean))}")
    print(f"citations={len(CITE_RE.findall(source_clean))}")
    print(f"indexes={len(source_index_options)}")
    print(f"items={source_items}")
    print(f"source_corrections=1 ({CORRECTION_ID})")
    print("han_residue=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
