#!/usr/bin/env python3
"""Fail-closed candidate/canonical structure check for admitted Unit 023."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from check_unit_023_candidate import run_checks as run_candidate_checks


ROOT = Path(__file__).resolve().parent.parent
AUTHORITY = (
    ROOT
    / "authority/source/AlJabr-1-c4f7a01f68f5f407906b4b970640cddbbad85f6b/chapter3.tex"
)
CANDIDATE = ROOT / "build/unit-023-candidate/chapter3-2-categories-id.tex"
TARGET = ROOT / "repo/source/chapter3.tex"

AUTHORITY_SHA256 = "7198f2c477890b333237156aba30b79db587e23dde7a878ed99f527e98a558d0"
SOURCE_SPAN_SHA256 = "2cb843048ffcb6378c3995e5b80c341000098187638e32af6aa918b87f5e5856"
SOURCE_SUFFIX_SHA256 = "2c8841f289261d68cde3e40141b2da7ce4ca6a76074fc5cb9163a508dfed5857"
CANDIDATE_SHA256 = "c15e079bc551b30ad7cc6daf72bee58a90108dc7fa5f101f768275e99d1dad05"
TARGET_SHA256 = "8ade04d16a5b71d4d1ffdf3bcee6736bb199c631a8851336d692e7ebdced5e7f"
TARGET_PREFIX_SHA256 = "e00bbceda9eec46bcef0b8ed63ba1c490145f0caa9209d43b28ccb904c3e5968"

SOURCE_START = 723
SOURCE_END = 872
TARGET_START = 722
TARGET_END = 871

EDITORIAL_INDEX_ID = "O013-LI-U023-ED-001"
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
    require(b"\r" not in data, f"{path}: unexpected CR byte")
    records = data.splitlines(keepends=True)
    require(len(records) == expected_lines, f"{path}: LF-record count changed")
    require(all(record.endswith(b"\n") for record in records), f"{path}: incomplete LF record")
    return data, records


def run_checks() -> None:
    require(len(sys.argv) == 1, "this checker accepts no path overrides or arguments")

    # The isolated checker pins the authority/candidate identities and all
    # mathematics, environments, labels, refs, diagrams, indexes, and language.
    run_candidate_checks()

    authority, authority_lines = read_records(AUTHORITY, 911)
    candidate, candidate_lines = read_records(CANDIDATE, 150)
    target, target_lines = read_records(TARGET, 910)

    target_prefix = b"".join(target_lines[: TARGET_START - 1])
    target_span = b"".join(target_lines[TARGET_START - 1 : TARGET_END])
    target_suffix = b"".join(target_lines[TARGET_END:])
    source_span = b"".join(authority_lines[SOURCE_START - 1 : SOURCE_END])
    source_suffix = b"".join(authority_lines[SOURCE_END:])

    require(
        len(authority) == 75_571 and sha256(authority).hexdigest() == AUTHORITY_SHA256,
        "authority drift",
    )
    require(
        len(source_span) == 12_436 and sha256(source_span).hexdigest() == SOURCE_SPAN_SHA256,
        "authority Unit 023 span drift",
    )
    require(
        len(source_suffix) == 4_954 and sha256(source_suffix).hexdigest() == SOURCE_SUFFIX_SHA256,
        "authority post-Unit-023 suffix drift",
    )
    require(
        len(candidate) == 14_894 and sha256(candidate).hexdigest() == CANDIDATE_SHA256,
        "candidate drift",
    )
    require(
        len(target) == 88_491 and sha256(target).hexdigest() == TARGET_SHA256,
        "canonical target drift",
    )
    require(len(target_prefix) == 68_643, "canonical admitted prefix byte count changed")
    require(
        sha256(target_prefix).hexdigest() == TARGET_PREFIX_SHA256,
        "pre-Unit-023 canonical prefix changed",
    )
    require(target_span == candidate, "canonical Unit 023 span is not byte-identical to candidate")
    require(
        target_suffix == source_suffix,
        "canonical remainder differs from authority lines 873-911",
    )

    require(
        target_lines[TARGET_START - 1] == candidate_lines[0],
        "canonical Unit 023 opening changed",
    )
    require(
        target_lines[TARGET_END - 1] == candidate_lines[-1] == b"\t\n",
        "included terminal separator changed",
    )
    require(
        target_lines[TARGET_END] == authority_lines[SOURCE_END] == b"\\begin{Exercises}\n",
        "next exercise boundary changed",
    )
    require(b"\\begin{Exercises}" not in target_span, "exercise block leaked into Unit 023")

    print(
        "\n".join(
            (
                "PASS Unit 023 candidate/canonical mathematics/protected-topology checker",
                f"authority full_lines=911 bytes={len(authority)} sha256={sha256(authority).hexdigest()}",
                f"source span=723-872 bytes={len(source_span)} sha256={sha256(source_span).hexdigest()}",
                f"candidate lines=1-150 bytes={len(candidate)} sha256={sha256(candidate).hexdigest()}",
                f"target full_lines=910 bytes={len(target)} sha256={sha256(target).hexdigest()}",
                f"target prefix=1-721 bytes={len(target_prefix)} sha256={sha256(target_prefix).hexdigest()}",
                f"target span=722-871 bytes={len(target_span)} sha256={sha256(target_span).hexdigest()}",
                f"target suffix=872-910 bytes={len(target_suffix)} sha256={sha256(target_suffix).hexdigest()}",
                "integration=candidate-byte-identical remainder=authority-873-911-byte-identical",
                "boundary=source-723-start included-blank=872 target-722-start included-tab-blank=871 next-target-872-Exercises-excluded",
                "environments=25-pairs labels=2 refs=16 eqrefs=0 cites=0 items=19 indexes=3",
                "inline_math=156 bracket_displays=11 commands=446 braces=186/186 han=0",
                "tikzcd=14 arrows=64 nodes=0 paths=0 edges=0 draws=0",
                f"editorial={EDITORIAL_INDEX_ID}-raw-pinyin-index-to-localized-display",
                f"provenance={PROVENANCE}",
            )
        )
    )


def main() -> int:
    try:
        run_checks()
    except Exception as error:
        print(
            f"FAIL Unit 023 candidate/canonical mathematics/protected-topology checker: {error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
