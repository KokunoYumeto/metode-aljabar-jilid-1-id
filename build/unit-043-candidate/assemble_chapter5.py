#!/usr/bin/env python3
"""Assemble the complete Indonesian Chapter 5 candidate from checked slices."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = (
    ROOT
    / "authority"
    / "source"
    / "AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b"
    / "chapter5.tex"
)
OUTPUT = ROOT / "build" / "unit-043-candidate" / "chapter5-complete-id.tex"

PARTS = (
    (1, 172, "build/unit-036-candidate/chapter5-ring-basics-id.tex", "d93ad6adeccae67ace0035286e9a41ab1350dca875acdb349d529c7f180b991a"),
    (174, 290, "build/unit-037-candidate/chapter5-special-rings-id.tex", "9f6ea7b368133027c1a12efef74db48eed36c6db6662fe746b894a938a0825f5"),
    (292, 461, "build/unit-038-candidate/chapter5-commutative-rings-localization-id.tex", "e48edae4d77c5be8206f8e18b0d4c71c307444830594295a338cbf8313d03607"),
    (463, 608, "build/unit-039-candidate/chapter5-mobius-inversion-id.tex", "5ed878a2ac0261b613cab8d050adc5130cf880e829736b80b24d696ba1a4c8a7"),
    (610, 781, "build/unit-040-candidate/chapter5-ring-limits-completion-id.tex", "b6131a25476422a43c51d844d1f75cbaf4a12da241b5db26e7f6f0435891e018"),
    (783, 956, "build/unit-041-candidate/chapter5-monoid-polynomial-rings-id.tex", "128e12090cdca0030ee537d778838fd9daad941319fc63e112216c593454001a"),
    (958, 1182, "build/unit-042-candidate/chapter5-unique-factorization-id.tex", "a76cf155134f6ae7a4a5e7a94cd9a5424ac83e277264f8d4228bdc5a2ed4b41a"),
    (1184, 1382, "build/unit-043-candidate/chapter5-symmetric-polynomials-exercises-id.tex", "5318c2433ca4784d1fbf64a86989bd3a3a007a10ed00cb6e0ae7f46a37122a2d"),
)
SEPARATORS = (173, 291, 462, 609, 782, 957, 1183)


def read_records(path: Path, *, require_final_lf: bool = True) -> tuple[bytes, list[str]]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise SystemExit(f"non-canonical UTF-8/LF input: {path}")
    text = data.decode("utf-8", errors="strict")
    if require_final_lf and (not text.endswith("\n") or text.endswith("\n\n")):
        raise SystemExit(f"input must end in exactly one LF: {path}")
    if text.endswith("\n"):
        text = text[:-1]
    return data, text.split("\n")


authority_data, authority_lines = read_records(AUTHORITY, require_final_lf=False)
if len(authority_data) != 122_998 or hashlib.sha256(authority_data).hexdigest() != (
    "e747d16b2ebacc95cf1c34da4bc8b7775a5ed8787b6d1edc2cc8e303535ac143"
):
    raise SystemExit("frozen Chapter 5 authority identity drift")
if len(authority_lines) != 1_382:
    raise SystemExit("authority record-count drift")

assembled: list[str | None] = [None] * len(authority_lines)
for start, end, relative_path, expected_sha in PARTS:
    data, lines = read_records(ROOT / relative_path)
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise SystemExit(f"checked fragment identity drift: {relative_path}")
    if len(lines) != end - start + 1:
        raise SystemExit(f"checked fragment record-count drift: {relative_path}")
    assembled[start - 1 : end] = lines

for record in SEPARATORS:
    if authority_lines[record - 1] != "":
        raise SystemExit(f"authority separator {record} is no longer blank")
    assembled[record - 1] = ""

if any(line is None for line in assembled):
    missing = [index for index, line in enumerate(assembled, start=1) if line is None]
    raise SystemExit(f"uncovered authority records: {missing}")

output_data = ("\n".join(line for line in assembled if line is not None) + "\n").encode("utf-8")
OUTPUT.write_bytes(output_data)
print(
    f"ASSEMBLED: {OUTPUT.relative_to(ROOT)}; 1382 records; "
    f"{len(output_data)} bytes; sha256={hashlib.sha256(output_data).hexdigest()}"
)
