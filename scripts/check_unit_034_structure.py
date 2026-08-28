#!/usr/bin/env python3
"""Verify the promoted Unit 034 canonical splice and controlled glossary."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "repo/source/chapter4.tex"
CANDIDATE = ROOT / "build/unit-034-candidate/chapter4-group-limits-completions-id.tex"
GLOSSARY = ROOT / "00_control/TERMINOLOGY.id-ID.csv"
DELTA = ROOT / "build/unit-034-staging/terminology-delta.csv"
CHECKER = ROOT / "scripts/check_unit_034_candidate.py"


def ident(path: Path) -> tuple[int, str]:
    payload = path.read_bytes()
    return len(payload), hashlib.sha256(payload).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("UNIT 034 STRUCTURE CHECK REFUSED: " + message)


def main() -> None:
    need(ident(CANDIDATE) == (19_019, "8f5ffb27fcf5b8163dea021d6d075f091b15251b9c07efb7578ac16f1b428b62"), "candidate drift")
    need(ident(TARGET) == (189_935, "37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569"), "canonical target drift")
    need(ident(GLOSSARY) == (82_586, "59e66d5acf8f8e792327730c01a236d3bc7570b9f71a200b9a6d7b9a71fa3955"), "glossary drift")
    need(ident(DELTA) == (6_613, "077b2903a33cdcf2df893a9ef57926b3c5d5157fc4be670f5aad10bdfdccf659"), "delta drift")
    target = TARGET.read_bytes()
    candidate = CANDIDATE.read_bytes()
    need(b"\r" not in target + candidate + GLOSSARY.read_bytes() + DELTA.read_bytes(), "CR/CRLF detected")
    lines = target.splitlines(keepends=True)
    need(len(lines) == 1_893, "target record count drift")
    span = b"".join(lines[1_603:1_738])
    need(span == candidate, "canonical span is not candidate-identical")
    need(lines[1_738] == b"\n", "blank boundary line 1739 drift")
    need(lines[1_739] == "\\section{范畴中的群}\\label{sec:group-in-cat}\n".encode(), "Section 4.11 sentinel drift")
    rows = list(csv.DictReader(GLOSSARY.read_text(encoding="utf-8").splitlines()))
    delta = list(csv.DictReader(DELTA.read_text(encoding="utf-8").splitlines()))
    need(len(rows) == 513 and len({row["source_term"] for row in rows}) == 513, "glossary uniqueness/count drift")
    need(len(delta) == 37 and all(row["status"] == "admitted" for row in delta), "delta status/count drift")
    by_term = {row["source_term"]: row for row in rows}
    need(by_term["completion"]["target_term"] == "pelengkapan" and by_term["completion"]["status"] == "admitted", "completion replacement drift")
    need(by_term["completeness"]["target_term"] == "kelengkapan" and by_term["completeness"]["scope"] == "category theory and topology", "completeness replacement drift")
    need(all(by_term[row["source_term"]] == row for row in delta), "delta rows are not exactly admitted")
    need("kompletisasi" not in candidate.decode("utf-8") and "penutup terbuka" not in candidate.decode("utf-8"), "superseded terminology remains")
    checked = subprocess.run([sys.executable, str(CHECKER)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="strict")
    need(checked.returncode == 0 and "PASS: O013-LI-U034" in checked.stdout, "candidate checker replay failed")
    print("UNIT 034 STRUCTURE CHECK: PASS")
    print("canonical_target_bytes=189935")
    print("canonical_target_sha256=37ff3990850d81505ded1d1b71ca9318ea6dd3d1343a18e49495bf83d8367569")
    print("canonical_span_lines=1604-1738")
    print("preserved_blank_boundary_line=1739")
    print("next_section_sentinel_line=1740")
    print("authority_suffix_start=chapter4.tex:1745")
    print("glossary_rows=513")
    print("terminology_delta_rows=37")


if __name__ == "__main__":
    main()
