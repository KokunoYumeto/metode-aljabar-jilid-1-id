#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 029."""

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
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-029-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_029_candidate.py"
PROMOTION_SCRIPT = ROOT / "scripts/promote_unit_029.py"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_025_ID = (20_464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a")
UNIT_026_ID = (19_424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87")
UNIT_027_ID = (12_675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563")
UNIT_028_ID = (13_017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd")
UNIT_029_ID = (10_028, "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d")
SOURCE_SLICE_ID = (8_043, "760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163")
SOURCE_SUFFIX_ID = (95_054, "79bffb7c169bc99af3e7b4354cba883ae036abb6287421099dc5d930f06895d1")
TARGET_ID = (170_663, "8cbd766360a3c7cd214876e297c45de3b8938daa9a3623192efdf1d6ebc766fc")
OLD_GLOSSARY_ID = (64_585, "fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7")
DELTA_ID = (1_030, "e0e00678dc46fd8c702c17614ea2d1e1e71ee6ff622f8986097dfd296e759ecc")
GLOSSARY_ID = (65_573, "adc2152dc08131e0098ac159137378aa50cd7b54cb282a8e713899662d335ca3")
CANDIDATE_CHECKER_ID = (14_830, "3a67accdd9cbcace31547b4284fe65b4f4ab29ebd0efd04be325d450fe6936d7")
PROMOTION_SCRIPT_ID = (8_634, "825c157ddae9503c387803ba7a5eef6e8ca8c5729ae7c9ef1e6f49afe6dbafa0")

SOURCE_START, SOURCE_END = 666, 795
TARGET_START, TARGET_END = 665, 793

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-029 candidate admission",
        "authority=chapter4.tex:666-795",
        "authority_slice_records=130",
        "authority_slice_bytes=8043",
        "authority_slice_sha256=760366ac81aff9bd6170c96996ae16c29a02a93034a77f7d4c7f01485bbf3163",
        "candidate_records=129",
        "candidate_bytes=10028",
        "candidate_sha256=234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d",
        "environment_markers=50",
        "labels=6",
        "refs_eqrefs=16",
        "citations=1",
        "indexes=2",
        "protected_math_zones=211",
        "diagrams=0",
        "exercises=0",
        "hints=0",
        "han_residue=0",
        "declared_source_corrections=0",
        "protected_text_localizations=1",
        "next_boundary=chapter4.tex:796",
        "",
    )
)

DELTA_SURFACES = {
    "p-group": "$p$-grup",
    "p-subgroup": "$p$-subgrup",
    "Sylow p-subgroup": "subgrup Sylow $p$",
    "binomial coefficient": "koefisien binomial",
    "coprime": "saling koprima",
}


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 029 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
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
    unit_025, _ = strict(UNIT_025)
    unit_026, _ = strict(UNIT_026)
    unit_027, _ = strict(UNIT_027)
    unit_028, _ = strict(UNIT_028)
    unit_029, unit_029_text = strict(UNIT_029)
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()
    promotion = PROMOTION_SCRIPT.read_bytes()

    for got, expected, label in (
        (identity(authority), AUTHORITY_ID, "authority"),
        (identity(unit_025), UNIT_025_ID, "Unit 025 prefix"),
        (identity(unit_026), UNIT_026_ID, "Unit 026 prefix"),
        (identity(unit_027), UNIT_027_ID, "Unit 027 prefix"),
        (identity(unit_028), UNIT_028_ID, "Unit 028 prefix"),
        (identity(unit_029), UNIT_029_ID, "Unit 029 candidate"),
        (identity(target), TARGET_ID, "canonical Chapter 4"),
        (identity(glossary), GLOSSARY_ID, "controlled glossary"),
        (identity(delta), DELTA_ID, "terminology delta"),
        (identity(checker), CANDIDATE_CHECKER_ID, "candidate checker"),
        (identity(promotion), PROMOTION_SCRIPT_ID, "promotion script"),
    ):
        require(got == expected, f"{label} identity drifted: {got}")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    target_lines = target_text.splitlines()
    candidate_lines = unit_029_text.splitlines()
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(target_lines) == 1_896, "target line topology drifted")
    require(len(candidate_lines) == 129, "candidate line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target lacks exactly one final LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_END:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 666-795 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 795 is not blank")
    require(
        authority_lines[SOURCE_END] == r"\section{群的合成列}\label{sec:composition-series-grp}",
        "authority line 796 is not the pinned Section 4.6 boundary",
    )
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 796 drifted")

    expected_target = unit_025 + unit_026 + unit_027 + unit_028 + unit_029 + source_suffix + b"\n"
    require(target == expected_target, "canonical target is not exact Unit 025-029 prefix plus authority suffix")
    require(
        target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines,
        "canonical target lines 665-793 differ from Unit 029",
    )
    require(
        target_lines[TARGET_END] == r"\section{群的合成列}\label{sec:composition-series-grp}",
        "target line 794 is not untranslated Section 4.6",
    )

    glossary_lines = glossary.splitlines(keepends=True)
    require(len(glossary_lines) == 414, "controlled glossary physical row topology drifted")
    require(
        identity(b"".join(glossary_lines[:409])) == OLD_GLOSSARY_ID,
        "pre-Unit-029 glossary prefix drifted",
    )
    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 413 and len(delta_rows) == 5, "glossary/delta row counts drifted")
    require(glossary_rows[-5:] == delta_rows, "controlled glossary tail differs from Unit 029 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    require(set(DELTA_SURFACES) == {row["source_term"] for row in delta_rows}, "terminology delta vocabulary drifted")
    for source_term, surface in DELTA_SURFACES.items():
        require(surface in unit_029_text, f"Unit 029 evidence surface absent for {source_term!r}")

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
    require(
        all(run.stdout == EXPECTED_CANDIDATE_OUTPUT for run in runs),
        "candidate checker output drifted or was nondeterministic",
    )

    print("UNIT 029 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={UNIT_029_ID[0]}")
    print(f"canonical_span_sha256={UNIT_029_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print("next_section_sentinel_line=794")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")


if __name__ == "__main__":
    main()
