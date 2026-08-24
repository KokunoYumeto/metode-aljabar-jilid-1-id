#!/usr/bin/env python3
"""Fail-closed candidate/canonical structure check for Unit 022."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from check_unit_022_candidate import run_checks as run_candidate_checks


ROOT = Path(__file__).resolve().parent.parent
AUTHORITY = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
)
CANDIDATE = ROOT / "build/unit-022-candidate/chapter3-enriched-categories-id.tex"
TARGET = ROOT / "repo/source/chapter3.tex"

AUTHORITY_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_SPAN_SHA256 = "85332852a2b9808a5a9e7ec240adffdd5b286d44d724be38833aed53e65bd53d"
SOURCE_SUFFIX_SHA256 = "db85619a873a826c4a417252b5268b9c85d068f18f9467664599fb9b0575b6af"
CANDIDATE_SHA256 = "e1fa8da94c0c2431660f690aa9b2193e3c966e2d71b9d5a029da12a76bc0e255"
TARGET_SHA256 = "b395e1014becb462dae95eda5fde37da9b4edd0b477df8f0b5cefef43edbefa2"
TARGET_PREFIX_SHA256 = "5ea3a7c7b0c71bb69d1ed25b846fa7e859b5f0161644993eac8c38efac157d0c"

SOURCE_START = 513
SOURCE_END = 722
TARGET_START = 512
TARGET_END = 721

CORRECTIONS = ("O013-LI-U022-COR-001", "O013-LI-U022-COR-002")
PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"


class CheckFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def read_records(path: Path, expected_lines: int) -> tuple[bytes, list[bytes]]:
    require(path.is_file(), f"missing input: {path}")
    data = path.read_bytes()
    require(data.endswith(b"\n"), f"{path}: missing terminal LF")
    require(b"\r\n" not in data, f"{path}: unexpected CRLF")
    records = data.splitlines(keepends=True)
    require(len(records) == expected_lines, f"{path}: LF-record count changed")
    require(all(record.endswith(b"\n") for record in records), f"{path}: incomplete LF record")
    return data, records


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")

    # The isolated checker pins all mathematics, environments, labels, refs,
    # citations, indexes, diagrams, language residue, and both corrections.
    run_candidate_checks()

    authority, authority_lines = read_records(AUTHORITY, 911)
    candidate, candidate_lines = read_records(CANDIDATE, 210)
    target, target_lines = read_records(TARGET, 910)

    target_prefix = b"".join(target_lines[: TARGET_START - 1])
    target_span = b"".join(target_lines[TARGET_START - 1 : TARGET_END])
    target_suffix = b"".join(target_lines[TARGET_END:])
    source_span = b"".join(authority_lines[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines[SOURCE_END:])

    require(len(authority) == 75_571 and sha256(authority).hexdigest() == AUTHORITY_SHA256, "authority drift")
    require(len(source_span) == 15_089 and sha256(source_span).hexdigest() == SOURCE_SPAN_SHA256, "authority span drift")
    require(len(source_suffix) == 17_390 and sha256(source_suffix).hexdigest() == SOURCE_SUFFIX_SHA256, "authority suffix drift")
    require(len(candidate) == 17_541 and sha256(candidate).hexdigest() == CANDIDATE_SHA256, "candidate drift")
    require(len(target) == 86_033 and sha256(target).hexdigest() == TARGET_SHA256, "canonical target drift")
    require(len(target_prefix) == 51_102, "canonical admitted prefix byte count changed")
    require(sha256(target_prefix).hexdigest() == TARGET_PREFIX_SHA256, "pre-Unit-022 canonical prefix changed")
    require(target_span == candidate, "canonical Unit 022 span is not byte-identical to candidate")
    require(target_suffix == source_suffix, "canonical remainder differs from authority lines 723-911")

    require(target_lines[TARGET_START - 1] == candidate_lines[0], "canonical Unit 022 opening changed")
    require(target_lines[TARGET_END - 1] == candidate_lines[-1] == b"\n", "included terminal blank changed")
    require(target_lines[TARGET_END] == authority_lines[SOURCE_END], "next Section 3.5 boundary changed")
    require(b"sec:2-cat" not in target_span, "Section 3.5 leaked into Unit 022")
    require(
        b"".join(target_lines[: TARGET_START - 1]) == target_prefix,
        "prior target lines 1-511 were not preserved",
    )

    print(
        "\n".join(
            (
                "PASS Unit 022 candidate/canonical mathematics/protected-topology checker",
                f"authority full_lines=911 bytes={len(authority)} sha256={sha256(authority).hexdigest()}",
                f"source span=513-722 bytes={len(source_span)} sha256={sha256(source_span).hexdigest()}",
                f"candidate lines=1-210 bytes={len(candidate)} sha256={sha256(candidate).hexdigest()}",
                f"target full_lines=910 bytes={len(target)} sha256={sha256(target).hexdigest()}",
                f"target prefix=1-511 bytes={len(target_prefix)} sha256={sha256(target_prefix).hexdigest()}",
                f"target span=512-721 bytes={len(target_span)} sha256={sha256(target_span).hexdigest()}",
                f"target suffix=722-910 bytes={len(target_suffix)} sha256={sha256(target_suffix).hexdigest()}",
                "integration=candidate-byte-identical remainder=authority-723-911-byte-identical",
                "boundary=source-513-start included-blank=722 target-512-start included-blank=721 next-target-722-Section-3.5-excluded",
                "environments=41-pairs labels=11 refs=15 eqrefs=0 cites=2 items=17 indexes=10",
                "inline_math=204 bracket_displays=11 commands=668 braces=288/288 han=0",
                "tikzpicture=3 tikzcd=6 nodes=14 arrows=21 edges=13 draws=11",
                f"corrections={','.join(CORRECTIONS)}",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(f"FAIL Unit 022 candidate/canonical mathematics/protected-topology checker: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
