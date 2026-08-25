#!/usr/bin/env python3
"""Fail-closed canonical-integration check for O013 Li Unit 028."""

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
TARGET = ROOT / "repo/source/chapter4.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-028-staging/terminology-delta.csv"
CANDIDATE_CHECKER = ROOT / "scripts/check_unit_028_candidate.py"
PROMOTION_SCRIPT = ROOT / "scripts/promote_unit_028.py"

AUTHORITY_ID = (154_744, "63dbb81492f02f00a2d1d42b0ad382a26db92da08e8ed8d523b92bcacab870a3")
UNIT_025_ID = (20_464, "5da737ae9f32b4c4b75bb34d615eacd2acb2e68d8e69bdf2a25db590aad8281a")
UNIT_026_ID = (19_424, "a3745af3387afbee36e1c39a91ab531efc0f97d10b1fb6bc95d4505143c9de87")
UNIT_027_ID = (12_675, "aa7fa71a2cf748b29b9ca6ddfc6297d6af8d8ffcc6943ec061c1235d44f5f563")
UNIT_028_ID = (13_017, "027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd")
SOURCE_SLICE_ID = (10_550, "af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db")
SOURCE_SUFFIX_ID = (103_097, "e7c66981deb8f755ea97539b25d4b71742e5137f76238d8dfe5e3b351d18a4e7")
TARGET_ID = (168_678, "33ab68b169fad0f45815cbfa528e03eaa12efbb2add9a4599049a9823c86b0b3")
OLD_GLOSSARY_ID = (60_575, "61e45adc844d8fd6beccf1cbb2216340913d6eb3b55cdd487817820171899f97")
DELTA_ID = (4_052, "601944b6058b9506655eca969d4d85506e59c24d9779d38567c19cb84bde41d7")
GLOSSARY_ID = (64_585, "fdd00a574f7f93837688e2d9bc9707677c889eab1174b8f0121a119498557fe7")
CANDIDATE_CHECKER_ID = (14_671, "be2674c75fb17bf8dd8de43d4dd0230fd049f2b5640c72aa372aecc1742d1527")
PROMOTION_SCRIPT_ID = (7_522, "38a82ea5e45251c53acba661373a808aa54eaa8ec648f4873b95a06bfb2a9193")

SOURCE_START, SOURCE_END = 518, 665
TARGET_START, TARGET_END = 518, 664

EXPECTED_CANDIDATE_OUTPUT = "\n".join(
    (
        "PASS unit-028 candidate admission",
        "authority=chapter4.tex:518-665",
        "authority_slice_records=148",
        "authority_slice_bytes=10550",
        "authority_slice_sha256=af7b91d4650e637505555cc188056656cd02f400bc6e1dd1ded0f619040a80db",
        "candidate_records=147",
        "candidate_bytes=13017",
        "candidate_sha256=027201c4462b29d13552bd347e65b5d250942b7cc2f8ae9a34782eeeed85dcdd",
        "environment_markers=48",
        "labels=5",
        "refs_eqrefs=8",
        "citations=2",
        "indexes=9",
        "protected_math_zones=213",
        "tikzcd_arrows=2",
        "exercises=0",
        "hints=0",
        "han_residue=0",
        "declared_source_corrections=1",
        "protected_text_localizations=3",
        "next_boundary=chapter4.tex:666",
        "",
    )
)

DELTA_SURFACES = {
    "group action": "aksi grup",
    "monoid action": "aksi monoid",
    "action map": "pemetaan aksi",
    "M-set": "himpunan-$M$",
    "trivial action": "aksi trivial",
    "equivariant map": "ekuivarian",
    "left action": "aksi kiri",
    "right action": "aksi kanan",
    "fixed point": "titik tetap",
    "orbit": "orbit",
    "stabilizer": "stabilisator",
    "orbit decomposition": "dekomposisi orbit",
    "orbit space": "ruang orbit",
    "faithful action": r"\item setia",
    "free action": r"\item bebas",
    "semiregular action": "semireguler",
    "transitive action": r"\item transitif",
    "n-transitive action": "$n$-transitif",
    "homogeneous space": "ruang homogen",
    "principal homogeneous space": "ruang homogen utama",
    "torsor": "torsor",
    "translation action": "aksi translasi",
    "conjugation action": "aksi konjugasi",
    "conjugacy class": "kelas konjugasi",
    "bitorsor": "bitorsor",
}


def identity(data: bytes) -> tuple[int, str]:
    return len(data), hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"UNIT 028 STRUCTURE CHECK: FAIL\n- {message}", file=sys.stderr)
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
    unit_028, unit_028_text = strict(UNIT_028)
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
        (identity(unit_028), UNIT_028_ID, "Unit 028 candidate"),
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
    candidate_lines = unit_028_text.splitlines()
    require(len(authority_lines) == 1_898, "authority line topology drifted")
    require(len(target_lines) == 1_897, "target line topology drifted")
    require(len(candidate_lines) == 147, "candidate line topology drifted")
    require(target.endswith(b"\n") and not target.endswith(b"\n\n"), "target lacks exactly one final LF")

    source_slice = b"".join(authority_lines_bytes[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines_bytes[SOURCE_END:])
    require(identity(source_slice) == SOURCE_SLICE_ID, "authority lines 518-665 drifted")
    require(authority_lines[SOURCE_END - 1] == "", "authority line 665 is not blank")
    require(
        authority_lines[SOURCE_END] == r"\section{Sylow 定理}\label{sec:Sylow}",
        "authority line 666 is not the pinned Section 4.5 boundary",
    )
    require(identity(source_suffix) == SOURCE_SUFFIX_ID, "authority suffix from line 666 drifted")

    expected_target = unit_025 + unit_026 + unit_027 + unit_028 + source_suffix + b"\n"
    require(target == expected_target, "canonical target is not exact Unit 025-028 prefix plus authority suffix")
    require(
        target_lines[TARGET_START - 1 : TARGET_END] == candidate_lines,
        "canonical target lines 518-664 differ from Unit 028",
    )
    require(
        target_lines[TARGET_END] == r"\section{Sylow 定理}\label{sec:Sylow}",
        "target line 665 is not untranslated Section 4.5",
    )

    glossary_lines = glossary.splitlines(keepends=True)
    require(len(glossary_lines) == 409, "controlled glossary physical row topology drifted")
    require(identity(b"".join(glossary_lines[:384])) == OLD_GLOSSARY_ID,
            "pre-Unit-028 glossary prefix drifted")
    glossary_rows = list(csv.DictReader(glossary_text.splitlines()))
    delta_rows = list(csv.DictReader(delta_text.splitlines()))
    require(len(glossary_rows) == 408 and len(delta_rows) == 25, "glossary/delta row counts drifted")
    require(glossary_rows[-25:] == delta_rows, "controlled glossary tail differs from Unit 028 delta")
    require(all(row["status"] == "admitted" for row in delta_rows), "delta has non-admitted row")
    terms = [row["source_term"] for row in glossary_rows]
    require(len(terms) == len(set(terms)), "controlled glossary has duplicate source terms")
    require(set(DELTA_SURFACES) == {row["source_term"] for row in delta_rows},
            "terminology delta vocabulary drifted")
    for source_term, surface in DELTA_SURFACES.items():
        require(surface in unit_028_text, f"Unit 028 evidence surface absent for {source_term!r}")

    runs = [
        subprocess.run(
            [sys.executable, str(CANDIDATE_CHECKER)], cwd=ROOT,
            text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        for _ in range(2)
    ]
    require(all(run.returncode == 0 for run in runs), "candidate checker failed")
    require(all(run.stderr == "" for run in runs), "candidate checker emitted stderr")
    require(all(run.stdout == EXPECTED_CANDIDATE_OUTPUT for run in runs),
            "candidate checker output drifted or was nondeterministic")

    print("UNIT 028 STRUCTURE CHECK: PASS")
    print(f"canonical_target_bytes={TARGET_ID[0]}")
    print(f"canonical_target_sha256={TARGET_ID[1]}")
    print(f"canonical_target_records={len(target_lines)}")
    print(f"canonical_span_lines={TARGET_START}-{TARGET_END}")
    print(f"canonical_span_bytes={UNIT_028_ID[0]}")
    print(f"canonical_span_sha256={UNIT_028_ID[1]}")
    print(f"authority_suffix_start=chapter4.tex:{SOURCE_END + 1}")
    print(f"glossary_rows={len(glossary_rows)}")
    print(f"glossary_sha256={GLOSSARY_ID[1]}")
    print(f"terminology_delta_rows={len(delta_rows)}")
    print(f"terminology_delta_sha256={DELTA_ID[1]}")


if __name__ == "__main__":
    main()
