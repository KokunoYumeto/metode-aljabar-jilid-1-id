#!/usr/bin/env python3
"""Unit 043 / complete-Chapter-5 binding for the shared GitHub verifier."""

from pathlib import Path

import verify_unit_035_github_readback as verifier


verifier.UNIT = "043"
verifier.OUTPUTS = {
    boundary: Path(__file__).resolve().parents[1]
    / "qa"
    / f"PUBLICATION_GITHUB_UNIT_043_{boundary.upper()}_READBACK.json"
    for boundary in verifier.BOUNDARIES
}
verifier.USER_AGENT = "O013-unit-043-public-byte-verifier/2.0"

_shared_build_parser = verifier.build_parser


def _build_parser():
    parser = _shared_build_parser()
    parser.description = "Verify one Unit 043 / complete-Chapter-5 GitHub boundary byte-for-byte."
    parser.epilog = parser.epilog.replace('"unit": "035"', '"unit": "043"').replace(
        "verify_unit_035_github_readback.py", "verify_unit_043_github_readback.py"
    )
    return parser


verifier.build_parser = _build_parser


if __name__ == "__main__":
    raise SystemExit(verifier.main())
