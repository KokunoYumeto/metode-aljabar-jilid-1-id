#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 030."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter4.tex"
UNIT_025 = ROOT / "build/unit-025-candidate/chapter4-group-basics-id.tex"
UNIT_026 = ROOT / "build/unit-026-candidate/chapter4-homomorphisms-quotients-id.tex"
UNIT_027 = ROOT / "build/unit-027-candidate/chapter4-products-group-extensions-id.tex"
UNIT_028 = ROOT / "build/unit-028-candidate/chapter4-group-actions-counting-id.tex"
UNIT_029 = ROOT / "build/unit-029-candidate/chapter4-sylow-theorems-id.tex"
UNIT_030 = ROOT / "build/unit-030-candidate/chapter4-group-composition-series-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-030-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_030_candidate.py"
PROMOTION_SCRIPT = ROOT / "scripts/promote_unit_030.py"

AUTHORITY_ID = (154744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_025_ID = (20464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a")
UNIT_026_ID = (19424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87")
UNIT_027_ID = (12675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563")
UNIT_028_ID = (13017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd")
UNIT_029_ID = (10028, "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d")
UNIT_030_ID = (10044, "7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b")
SOURCE_SLICE_ID = (7981, "7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1")
SOURCE_SUFFIX_ID = (87073, "2507535ca192117452f9dd6b980842b8bdc1103b5b456be0a5a9d8d496448ed5")
TARGET_ID = (172726, "245a891930cefb1c18cbd1208386ba5131c56b8b5930510c329577eeeb96cddc")
OLD_GLOSSARY_ID = (65573, "adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3")
DELTA_ID = (1377, "fe0b91971953c8d14568fd1144f0799d8c36b6c6a7cc09be8dd11d688de3c7a4")
GLOSSARY_ID = (66908, "2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991")

SOURCE_START, SOURCE_END = 796, 935
TARGET_START, TARGET_END = 794, 932

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-030 candidate admission",
        "authority=chapter4.tex:796-935",
        "authority_slice_records=140",
        "authority_slice_bytes=7981",
        "authority_slice_sha256=7803452c4285c57e419a2cb2a288b3733975555fafd6b7a88c5732da369220c1",
        "candidate_records=139",
        "candidate_bytes=10044",
        "candidate_sha256=7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b",
        "environment_markers=52",
        "labels=10",
        "refs_eqrefs=9",
        "citations=0",
        "indexes=6",
        "protected_math_zones=88",
        "tikzcd_environments=6",
        "diagram_arrows=23",
        "exercises=0",
        "hints=0",
        "han_residue=0",
        "declared_source_corrections=1",
        "protected_text_localizations=2",
        "next_boundary=chapter4.tex:936",
        "",
    )
)

DELTA_SURFACES = {
    "normal series": "deret normal",
    "central series": "deret sentral",
    "composition series": "deret komposisi",
    "subquotient": "subkuosien",
    "refinement": "penghalusan",
    "proper refinement": "penghalusan sejati",
    "composition factor": "faktor komposisi",
    "multiplicity": "multiplikitas",
}

def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()

def fail(message: str) -> None:
    print(f"UNIT 030 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
    raise SystemExit(1)

def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def strict(path: Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    require(not data.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {path}")
    require(b"\r" not in data, f"CR/CRLF detected: {path}")
    try:
        return data, data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        fail(f"strict UTF-8 decode failed for {path}: {exc}")

def main() -> None:
    authority, authority_text = strict(AUTHORITY)
    prefix_paths = (UNIT_025, UNIT_026, UNIT_027, UNIT_028, UNIT_029)
    prefix_units = [strict(path)[0] for path in prefix_paths]
    unit_030, unit_030_text = strict(UNIT_030)
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()

    for got, expected, label in (
        (identity(authority), AUTHORITY_ID, "authority"),
        (identity(prefix_units[0]), UNIT_025_ID, "Unit 025 prefix"),
        (identity(prefix_units[1]), UNIT_026_ID, "Unit 026 prefix"),
        (identity(prefix_units[2]), UNIT_027_ID, "Unit 027 prefix"),
        (identity(prefix_units[3]), UNIT_028_ID, "Unit 028 prefix"),
        (identity(prefix_units[4]), UNIT_029_ID, "Unit 029 prefix"),
        (identity(unit_030), UNIT_030_ID, "Unit 030 candidate"),
        (identity(target), TARGET_ID, "canonical Chapter 4"),
        (identity(glossary), GLOSSARY_ID, "controlled glossary"),
        (identity(delta), DELTA_ID, "terminology delta"),
    ):
        require(got == expected, f"{label} identity drifted: {got}")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    target_lines = target_text.splitlines()
    candidate_lines = unit_030_text.splitlines()
    require(len(authority_lines) == 1898, "authority line topology drifted")
    require(len(target_lines) == 1895, "target line topology drifted")
    require(len(candidate_lines) == 139, "candidate line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target lacks exactly one final LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_END:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 796-935 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 935 is not blank")
    require(authority_lines[SOURCE_END] == r"\section{可解群与幂零群}\label{sec:solvable-groups}", "authority line 936 boundary drifted")
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 936 drifted")

    expected_target = b"".join(prefix_units) + unit_030 + source_suffix + b"\n"
    require(target == expected_target, "canonical target is not exact Unit 025-030 prefix plus authority suffix")
    require(target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines, "canonical target Unit 030 span differs from candidate")
    require(target_lines[TARGET_START - 1] == r"\section{Deret Komposisi Grup}\label{sec:composition-series-grp}", "target Unit 030 heading drifted")
    require(target_lines[TARGET_END] == r"\section{可解群与幂零群}\label{sec:solvable-groups}", "target line 933 suffix sentinel drifted")

    glossary_lines = glossary.splitlines(keepends=True)
    require(len(glossary_lines) == 422, "controlled glossary physical row topology drifted")
    require(identity(b"".join(glossary_lines[:414])) == OLD_GLOSSARY_ID, "pre-Unit-030 glossary prefix drifted")
    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 421 and len(delta_rows) == 8, "glossary/delta row counts drifted")
    require(glossary_rows[-8:] == delta_rows, "controlled glossary tail differs from Unit 030 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    require(set(DELTA_SURFACES) == {row["source_term"] for row in delta_rows}, "terminology delta vocabulary drifted")
    for source_term, surface in DELTA_SURFACES.items():
        require(surface in unit_030_text, f"Unit 030 evidence surface absent for {source_term!r}")

    runs = [
        subprocess.run(
            [sys.executable, str(CANDIDATE_CHECKER)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(2)
    ]
    require(all(run.returncode == 0 for run in runs), "candidate checker failed")
    require(all(run.stderr == "" for run in runs), "candidate checker emitted stderr")
    require(all(run.stdout == EXPECTED_CANDIDATE_OUTPUT for run in runs), "candidate checker output drifted or was nondeterministic")

    print("UNIT 030 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={UNIT_030_ID[0]}")
    print(f"canonical_span_sha256={UNIT_030_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print("next_section_sentinel_line=933")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")

if __name__ == "__main__":
    main()
