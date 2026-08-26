#!/usr/bin/env python3
"""Finalize fail-closed PDF and all-page visual evidence for Unit 032.

Run only after ``preflight_unit_032.py`` passes, every full-resolution page has
been inspected in both renderer outputs, and build J has been copied byte-for-
byte to the release artifact.  The findings file must be UTF-8 JSON of the
form ``{"status":"PASS","pages":{"1":"..."},"actionable_defects":[]}``
with one non-placeholder finding for every page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import generate_unit_030_evidence as render_base
import preflight_unit_032 as preflight


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFLIGHT = ROOT / "build/unit-032-preflight-final/preflight-observation.json"
DEFAULT_FINDINGS = ROOT / "build/unit-032-visual-findings.json"
DEFAULT_ARTIFACT = ROOT / "artifacts/unit-032-bab-4-grup-bebas-id.pdf"
DEFAULT_EVIDENCE = ROOT / "qa/unit-032-evidence"
DEFAULT_REPORT = ROOT / "qa/UNIT_032_VISUAL_QA_20260826.md"
DEFAULT_PREFLIGHT_REPORT = ROOT / "qa/UNIT_032_VISUAL_PREFLIGHT_20260826.md"
DEFAULT_FINAL_LOG = ROOT / "qa/UNIT_032_BUILD_FINAL.log"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def identity(path: Path) -> dict[str, Any]:
    return {"path": relative(path), "bytes": path.stat().st_size, "sha256": preflight.sha256(path)}


def bind_observation(path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    packet = load_json(path)
    assert packet["schema_version"] == 1 and packet["unit"] == "O013-LI-U032"
    assert packet["status"] == "PASS_PROVISIONAL_NOT_VISUAL_ADMISSION"
    assert (packet["candidate"]["bytes"], packet["candidate"]["sha256"]) == preflight.CANDIDATE_ID
    builds: dict[str, Path] = {}
    for name in ("build-i", "build-j"):
        record = packet["documents"][name]["identity"]
        pdf = (ROOT / record["path"]).resolve()
        assert pdf == preflight.DEFAULT_BUILDS[name].resolve() and pdf.is_file()
        assert identity(pdf) == record
        builds[name] = pdf
    return packet, builds


def validate_findings(path: Path, pages: int) -> dict[str, Any]:
    findings = load_json(path)
    assert findings.get("status") == "PASS"
    assert findings.get("actionable_defects") == []
    rows = findings.get("pages")
    assert isinstance(rows, dict) and set(rows) == {str(page) for page in range(1, pages + 1)}
    for page, text in rows.items():
        assert isinstance(text, str) and len(text.strip()) >= 24, (page, text)
        assert re.search(r"\b(?:TODO|TBD|PLACEHOLDER)\b", text, re.I) is None
    return findings


def sanitize_log(raw_path: Path) -> tuple[str, dict[str, int]]:
    raw = raw_path.read_text(encoding="utf-8")
    assert "\r" not in raw
    original_newlines = raw.count("\n")
    sanitized = raw
    miktex_root = str(Path.home() / "AppData/Local/Programs/MiKTeX")
    miktex_count = sanitized.count(miktex_root)
    assert miktex_count > 0
    sanitized = sanitized.replace(miktex_root, "<MIKTEX_ROOT>")
    lane_root = str(ROOT.resolve())
    lane_count = sanitized.count(lane_root)
    sanitized = sanitized.replace(lane_root, "<LANE_ROOT>")
    for split_at in range(1, len(lane_root)):
        wrapped = lane_root[:split_at] + "\n" + lane_root[split_at:]
        count = sanitized.count(wrapped)
        if count:
            sanitized = sanitized.replace(wrapped, "<LANE_ROOT>\n")
            lane_count += count
    assert sanitized.count("\n") == original_newlines
    assert re.search(r"[A-Za-z]:\\Users\\", sanitized, re.I) is None
    assert Path.home().name.lower() not in sanitized.lower()
    return sanitized, {
        "miktex_placeholder_occurrences": miktex_count,
        "lane_root_placeholder_occurrences": lane_count,
        "line_records_preserved": original_newlines + 1,
        "windows_user_path_occurrences": 0,
        "profile_name_occurrences": 0,
    }


def compare_renders(renderings: dict[str, Any], pages: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for engine in renderings:
        result[engine] = {}
        for left, right, key in (
            ("build-i", "build-j", "build-i_vs_build-j"),
            ("build-j", "artifact", "build-j_vs_artifact"),
        ):
            rows = [
                {
                    "page": left_page["page"],
                    "decoded_pixel_identical": left_page["decoded_rgb_sha256"]
                    == right_page["decoded_rgb_sha256"],
                    "png_byte_identical": left_page["png_sha256"] == right_page["png_sha256"],
                }
                for left_page, right_page in zip(
                    renderings[engine][left]["pages"],
                    renderings[engine][right]["pages"],
                    strict=True,
                )
            ]
            assert len(rows) == pages and all(row["decoded_pixel_identical"] for row in rows)
            result[engine][key] = {f"all_{pages}_decoded_pixel_identical": True, "pages": rows}
    all_pages = [page for engine in renderings.values() for doc in engine.values() for page in doc["pages"]]
    assert not any(page["outer_3px_ink_pixels"] for page in all_pages)
    return result


def write_reports(
    report: Path,
    preflight_report: Path,
    documents: dict[str, Any],
    renderings: dict[str, Any],
    comparisons: dict[str, Any],
    findings: dict[str, Any],
    log: dict[str, Any],
) -> None:
    pages = documents["artifact"]["pages"]
    identities = "\n".join(
        f"| `{row['identity']['path']}` | {row['identity']['bytes']:,} | `{row['identity']['sha256']}` |"
        for row in documents.values()
    )
    comparisons_text = "\n".join(
        f"- {engine} {name.replace('_', ' ')}: all {pages} decoded-RGB pages are identical."
        for engine, pairs in comparisons.items()
        for name in pairs
    )
    page_rows = "\n".join(
        f"| {page} | {findings['pages'][str(page)]} |" for page in range(1, pages + 1)
    )
    artifact_pages = {engine: renderings[engine]["artifact"]["pages"] for engine in renderings}
    pixel_rows = "\n".join(
        f"| {page} | `{artifact_pages['poppler'][page - 1]['decoded_rgb_sha256']}` | "
        f"`{artifact_pages['mupdf'][page - 1]['decoded_rgb_sha256']}` |"
        for page in range(1, pages + 1)
    )
    report.write_text(
        f"""# Unit 032 visual and PDF QA — 2026-08-26

Status: **PASS WITH WARNINGS**. Exact identity, two-engine decoded-pixel,
metadata, navigation, font, extraction, action/link, geometry, diagnostics,
and all-page visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
{identities}

Build J and the artifact are byte-identical; all three PDFs contain {pages} pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at 144 dpi (998 x 1418 pixels per page).
Equality is based on decoded RGB pixels.

{comparisons_text}

All {2 * 3 * pages} renders have zero ink in the outer three-pixel band.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
{pixel_rows}

## PDF and diagnostic gate

- PDF `%PDF-1.7`; `/Lang id-ID`; unencrypted; exact metadata and outline.
- All {len(documents['artifact']['named_destinations'])} named destinations resolve; action inventory is {documents['artifact']['action_counts']}.
- All {documents['artifact']['fonts']['unique']} font objects are embedded; no active payload or unsafe action is present.
- Final diagnostics are zero for errors, unresolved references/citations, missing characters, empty targets, and overfull boxes. Exactly {log['nonfatal_underfull_hboxes']} nonfatal underfull hboxes remain at the three visually inspected source locations; none causes clipping, collision, or impaired reading.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
{page_rows}

The PDF is untagged, so no tagged-accessibility claim is made. Stable
mathematics-font extraction limitations, if any, are recorded in the JSON
evidence. Toolchain advisories are retained exactly as {log['warning_counts']}.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
""",
        encoding="utf-8",
        newline="\n",
    )
    preflight_report.write_text(
        f"""# Unit 032 visual preflight — 2026-08-26

Status: **PASS WITH WARNINGS**. Two independent clean builds and the release
artifact were structurally inspected and rendered across all {pages} pages.
All same-renderer decoded-pixel comparisons, edge checks, metadata, outline,
destinations, links, embedded-font, extraction, diagnostics, and per-page
visual checks pass. The artifact is byte-identical to build J.

The PDF is untagged, so no tagged-accessibility claim is made. Exactly
{log['nonfatal_underfull_hboxes']} visually non-actionable underfull hboxes and
the fixed toolchain advisories remain disclosed in the evidence packet.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**.
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args()
    observation_path = args.preflight.resolve()
    findings_path = args.findings.resolve()
    artifact = args.artifact.resolve()
    assert observation_path == DEFAULT_PREFLIGHT.resolve()
    assert findings_path == DEFAULT_FINDINGS.resolve()
    assert artifact == DEFAULT_ARTIFACT.resolve() and artifact.is_file()
    for output in (DEFAULT_EVIDENCE, DEFAULT_REPORT, DEFAULT_PREFLIGHT_REPORT, DEFAULT_FINAL_LOG):
        assert not output.exists(), f"final evidence output must be absent: {output}"

    observation, builds = bind_observation(observation_path)
    assert artifact.read_bytes() == builds["build-j"].read_bytes()
    pages = observation["documents"]["build-j"]["pages"]
    findings = validate_findings(findings_path, pages)
    documents = {name: preflight.inspect_pdf(path) for name, path in builds.items()}
    documents["artifact"] = preflight.inspect_pdf(artifact)
    for key in ("pages", "metadata", "outline", "named_destinations", "action_counts", "fonts", "text"):
        assert documents["build-i"][key] == documents["build-j"][key] == documents["artifact"][key], key

    raw_log = builds["build-j"].with_suffix(".log")
    sanitized, sanitization = sanitize_log(raw_log)
    DEFAULT_FINAL_LOG.write_text(sanitized, encoding="utf-8", newline="\n")
    log = preflight.inspect_log(DEFAULT_FINAL_LOG, pages)
    log["sanitization"] = sanitization
    log["sanitized_log_reproduced_from_build_j"] = True

    DEFAULT_EVIDENCE.mkdir(parents=True)
    render_base.ROOT = ROOT
    render_base.OUT = DEFAULT_EVIDENCE
    render_base.DPI = 144
    render_base.PAGES = pages
    render_base.PIXEL_SIZE = (998, 1418)
    pdfs = {**builds, "artifact": artifact}
    renderings: dict[str, dict[str, Any]] = {"poppler": {}, "mupdf": {}}
    contact_sheets = []
    with tempfile.TemporaryDirectory(prefix="unit032-evidence-") as temporary:
        work = Path(temporary)
        for engine in renderings:
            for name, pdf in pdfs.items():
                rendered = render_base.render(engine, name, pdf, work)
                renderings[engine][name] = rendered
                contact_sheets.append(render_base.contact_sheet(engine, name, rendered["pages"]))
    comparisons = compare_renders(renderings, pages)
    render_inventory = {
        "status": "PASS_WITH_WARNINGS",
        "preflight_observation": identity(observation_path),
        "renderer_versions": observation["renderer_versions"],
        "renderers": renderings,
        "contact_sheets": contact_sheets,
        "decoded_pixel_comparisons": comparisons,
        "edge_gate": {"outer_band_pixels": 3, f"all_{2 * 3 * pages}_zero_ink": True},
        "manual_visual_review": findings,
        "actionable_defects": [],
    }
    structure = {
        "status": "PASS_WITH_WARNINGS",
        "documents": documents,
        "final_build_log": log,
        "cross_pdf_semantic_identity": True,
        "artifact_byte_identical_to_build_j": True,
        "actionable_defects": [],
    }
    dump(DEFAULT_EVIDENCE / "render-hash-inventory.json", render_inventory)
    dump(DEFAULT_EVIDENCE / "structure-and-pdf-qa.json", structure)
    write_reports(
        DEFAULT_REPORT,
        DEFAULT_PREFLIGHT_REPORT,
        documents,
        renderings,
        comparisons,
        findings,
        log,
    )
    print("PASS_WITH_WARNINGS")
    print(relative(DEFAULT_EVIDENCE / "render-hash-inventory.json"))
    print(relative(DEFAULT_EVIDENCE / "structure-and-pdf-qa.json"))
    print(relative(DEFAULT_PREFLIGHT_REPORT))
    print(relative(DEFAULT_REPORT))


if __name__ == "__main__":
    main()
