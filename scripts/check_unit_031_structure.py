#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 031."""

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
UNIT_031 = ROOT / "build/unit-031-candidate/chapter4-solvable-nilpotent-groups-id.tex"
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-031-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_031_candidate.py"

AUTHORITY_ID = (154744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_025_ID = (20464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a")
UNIT_026_ID = (19424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87")
UNIT_027_ID = (12675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563")
UNIT_028_ID = (13017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd")
UNIT_029_ID = (10028, "234c3a4d827a1e5810bffedf588daa2bc7d20778ad7b708d8fa1f7547a4c561d")
UNIT_030_ID = (10044, "7e39460c871f38145772d66c95160214d3bf33f18c15f858b4ee874e65474b4b")
UNIT_031_ID = (19855, "6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81")
CANDIDATE_CHECKER_ID = (16303, "64bb71b1ca1a301ab341dbf5ac6a25601663507df2c93a5028bc63cb1d64beb1")
SOURCE_SLICE_ID = (16048, "647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b")
SOURCE_SUFFIX_ID = (71025, "689476021d6233cc21a35f84081244e083f6f673ad9b91ee0077b5e8480aca16")
TARGET_ID = (176533, "440ed304a808c687d2e431eff1dbdbe0fe01458d7f8c82b47f515659307cf28f")
OLD_GLOSSARY_ID = (66908, "2fdad27f02b31ea2f29f9aecd8ef2e015a456b02636c402c3e985e5e0a5d7991")
DELTA_ID = (2766, "9939372a066946a23b644e6ed3a78abb9bbbc44d1a33879d3c63c9ef97147116")
GLOSSARY_ID = (69632, "6bc960138192243f9fd6e52a8dc60536362bc377946b49de06b49ee1d6e8298f")

SOURCE_START, SOURCE_END = 936, 1107
TARGET_START, TARGET_END = 933, 1103

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-031 candidate admission",
        "authority=chapter4.tex:936-1107",
        "authority_slice_records=172",
        "authority_slice_bytes=16048",
        "authority_slice_sha256=647d22446e75cde39b7b9f53d6658f39de78c5d773d51d6f446d651e1734967b",
        "candidate_records=171",
        "candidate_bytes=19855",
        "candidate_sha256=6bc4b1f7dd6cde6673915eba75cdf96cca6e8312d060d1fda0da25cb7073ee81",
        "environment_markers=62",
        "labels=6",
        "refs_eqrefs=7",
        "citations=1",
        "indexes=9",
        "protected_math_zones=326",
        "tikzpicture_environments=2",
        "tikzcd_environments=1",
        "diagram_arrows=3",
        "exercises=0",
        "hints=0",
        "han_residue=0",
        "declared_proof_repairs=1",
        "declared_digital_reflows=1",
        "protected_text_localizations=8",
        "next_boundary=chapter4.tex:1108",
        "",
    )
)

DELTA_SURFACES = {
    "solvable group": "grup solvabel",
    "supersolvable group": "grup supersolvabel",
    "nilpotent group": "grup nilpoten",
    "commutator": "komutator",
    "derived series": "deret turunan",
    "lower central series": "deret sentral menurun",
    "derived subgroup": "subgrup turunan",
    "upper central series": "deret sentral menaik",
    "symplectic form": "bentuk simplektik",
    "directional derivative": "turunan berarah",
    "canonical commutation relation": "relasi komutasi kanonik",
    "Heisenberg group": "grup Heisenberg",
    "upper triangular matrix group": "grup matriks segitiga atas",
    "Fourier transform": "transformasi Fourier",
}


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 031 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
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
    prefix_paths = (UNIT_025, UNIT_026, UNIT_027, UNIT_028, UNIT_029, UNIT_030)
    prefix_units = [strict(path)[0] for path in prefix_paths]
    unit_031, unit_031_text = strict(UNIT_031)
    target, target_text = strict(TARGET)
    glossary, glossary_text = strict(GLOSSARY)
    delta, delta_text = strict(DELTA)
    checker = CANDIDATE_CHECKER.read_bytes()

    expected_prefix_ids = (
        UNIT_025_ID,
        UNIT_026_ID,
        UNIT_027_ID,
        UNIT_028_ID,
        UNIT_029_ID,
        UNIT_030_ID,
    )
    for got, expected, label in (
        (identity(authority), AUTHORITY_ID, "authority"),
        *((identity(data), expected, f"Unit {number:03d} prefix") for data, expected, number in zip(prefix_units, expected_prefix_ids, range(25, 31))),
        (identity(unit_031), UNIT_031_ID, "Unit 031 candidate"),
        (identity(checker), CANDIDATE_CHECKER_ID, "Unit 031 candidate checker"),
        (identity(target), TARGET_ID, "canonical Chapter 4"),
        (identity(glossary), GLOSSARY_ID, "controlled glossary"),
        (identity(delta), DELTA_ID, "terminology delta"),
    ):
        require(got == expected, f"{label} identity drifted: {got}")

    authority_lines_bytes = authority.splitlines(keepends=True)
    authority_lines = authority_text.splitlines()
    target_lines = target_text.splitlines()
    candidate_lines = unit_031_text.splitlines()
    require(len(authority_lines) == 1898, "authority line topology drifted")
    require(len(target_lines) == 1894, "target line topology drifted")
    require(len(candidate_lines) == 171, "candidate line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target lacks exactly one final LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_END:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 936-1107 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 1107 is not blank")
    require(
        authority_lines[SOURCE_END] == r"\section{自由群}\label{sec:free-group}",
        "authority line 1108 boundary drifted",
    )
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 1108 drifted")

    expected_target = b"".join(prefix_units) + unit_031 + source_suffix + b"\n"
    require(target == expected_target, "canonical target is not exact Unit 025-031 prefix plus authority suffix")
    require(target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines, "canonical target Unit 031 span differs from candidate")
    require(
        target_lines[TARGET_START - 1] == r"\section{Grup Solvabel dan Grup Nilpoten}\label{sec:solvable-groups}",
        "target Unit 031 heading drifted",
    )
    require(target_lines[TARGET_END - 1] == r"\end{example}", "target Unit 031 closing record drifted")
    require(
        target_lines[TARGET_END] == r"\section{自由群}\label{sec:free-group}",
        "target line 1104 suffix sentinel drifted",
    )

    glossary_lines = glossary.splitlines(keepends=True)
    require(len(glossary_lines) == 436, "controlled glossary physical row topology drifted")
    require(identity(b"".join(glossary_lines[:422])) == OLD_GLOSSARY_ID, "pre-Unit-031 glossary prefix drifted")
    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 435 and len(delta_rows) == 14, "glossary/delta row counts drifted")
    require(glossary_rows[-14:] == delta_rows, "controlled glossary tail differs from Unit 031 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    require(set(DELTA_SURFACES) == {row["source_term"] for row in delta_rows}, "terminology delta vocabulary drifted")
    for source_term, surface in DELTA_SURFACES.items():
        require(surface in unit_031_text, f"Unit 031 evidence surface absent for {source_term!r}")

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

    print("UNIT 031 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={UNIT_031_ID[0]}")
    print(f"canonical_span_sha256={UNIT_031_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print("next_section_sentinel_line=1104")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")


if __name__ == "__main__":
    main()
