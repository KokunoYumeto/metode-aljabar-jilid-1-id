#!/usr/bin/env python3
"""Build the reader-first Zenodo 0.8.0 payload through complete Chapter 6."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

from pypdf import PdfReader

import build_release_0_7_0 as base


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.8.0"
RELEASE_DATE = "2026-08-28"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
CONCEPT_DOI = "10.5281/zenodo.22059759"
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf"
READER_REL = f"output/pdf/{READER_NAME}"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.8.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
EXPECTED_NAMES = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
BUILD_EVIDENCE_REL = "qa/unit-044-evidence/checkpoint-through-bab-6-build.json"
BACKEND_EVIDENCE_REL = "qa/unit-044-evidence/backend-validation.json"
EXPECTED_PAGES = 460
EXPECTED_COMPONENTS = 37
EXPECTED_SOURCE_PAGES = 459


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(path: Path) -> dict[str, object]:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def pdf_facts(path: Path) -> dict[str, object]:
    reader = PdfReader(str(path), strict=True)
    root = reader.trailer["/Root"]
    annotations: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    widgets = 0
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            subtype = str(annotation.get("/Subtype", ""))
            annotations[subtype] += 1
            widgets += subtype == "/Widget"
            action_ref = annotation.get("/A")
            if action_ref:
                action = action_ref.get_object()
                actions[str(action.get("/S", ""))] += 1
            elif annotation.get("/Dest") is not None:
                actions["/GoTo"] += 1
    unsafe = sum(actions[item] for item in ("/JavaScript", "/Launch", "/GoToR"))
    return {
        "pages": len(reader.pages), "language": str(root.get("/Lang", "")),
        "tagged_pdf": "/StructTreeRoot" in root,
        "named_destinations": len(reader.named_destinations),
        "annotation_subtypes": dict(sorted(annotations.items())),
        "actions": dict(sorted(actions.items())), "widgets": widgets,
        "unsafe_actions": unsafe, "open_action": root.get("/OpenAction") is not None,
        "acroform": root.get("/AcroForm") is not None,
        "title": str((reader.metadata or {}).get("/Title", "")),
        "author": str((reader.metadata or {}).get("/Author", "")),
        "creator": str((reader.metadata or {}).get("/Creator", "")),
    }


def validate_reader_and_base_evidence() -> tuple[dict[str, object], list[dict[str, object]]]:
    reader_path = ROOT / READER_REL
    build_path = ROOT / BUILD_EVIDENCE_REL
    backend_path = ROOT / BACKEND_EVIDENCE_REL
    build = json.loads(build_path.read_text(encoding="utf-8"))
    backend = json.loads(backend_path.read_text(encoding="utf-8"))
    reader_identity = digest(reader_path)
    facts = pdf_facts(reader_path)
    require(build.get("schema") == "o013-checkpoint-through-chapter-6-build-v1", "unexpected Chapter 6 build schema")
    require(build.get("result") == "pass" and build.get("component_count") == EXPECTED_COMPONENTS, "Chapter 6 build did not pass")
    inputs = build.get("inputs")
    require(isinstance(inputs, list) and len(inputs) == EXPECTED_COMPONENTS, "Chapter 6 input inventory drifted")
    require(sum(int(item.get("pages", -1)) for item in inputs) == EXPECTED_SOURCE_PAGES, "source page total drifted")
    output = build.get("output", {})
    require(output.get("path") == READER_REL and output.get("pages") == EXPECTED_PAGES, "reader output identity drifted")
    require(output.get("bytes") == reader_identity["bytes"] and output.get("sha256") == reader_identity["sha256"], "reader bytes drifted")
    require(backend.get("schema") == "o013-unit-backend-validation-v1", "unexpected backend schema")
    require(backend.get("unit") == "O013-LI-U044" and backend.get("result") == "pass", "Unit 044 backend did not pass")
    require(backend.get("rights_components") == 5 and backend.get("build_surfaces") == 2, "Unit 044 rights/build surface closure drifted")
    require(facts["pages"] == EXPECTED_PAGES and facts["language"] == "id-ID", "strict reader facts drifted")
    require(facts["widgets"] == 0 and facts["unsafe_actions"] == 0 and not facts["acroform"], "reader contains unsafe or interactive actions")
    require(facts["author"] == "Wen-Wei Li" and facts["creator"] in {MODEL, MODEL + "."}, "reader credit/provenance drifted")
    reader_identity.update({"role": "primary_reader", **facts})
    return reader_identity, [
        base.evidence_entry(build_path, "checkpoint_build"),
        base.evidence_entry(backend_path, "unit_044_backend_validation"),
    ]


def validate_final_evidence(path: Path, reader_identity: dict[str, object], role: str) -> None:
    require(path.is_file(), f"missing {role}: {path}")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        require(data.get("result") in {"pass", "PASS"} or data.get("status") == "PASS" or data.get("all_match") is True,
                f"{role} does not record a pass")
        text = json.dumps(data, ensure_ascii=False)
    else:
        text = path.read_text(encoding="utf-8")
        require("PASS" in text.upper(), f"{role} does not record PASS")
    require(str(reader_identity["sha256"]) in text, f"{role} does not bind the Chapter 6 reader hash")


def checksum_map(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        checksum, name = line.split("  ", 1)
        require(len(checksum) == 64 and name not in result, f"bad checksum line: {line!r}")
        result[name] = checksum
    return result


def validate_stage(stage: Path, *, allow_preparation: bool) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    zenodo = stage / "zenodo"
    files = sorted(path for path in zenodo.iterdir() if path.is_file())
    require([path.name for path in files] == EXPECTED_NAMES, f"unexpected payload inventory: {[path.name for path in files]}")
    expected = {path.name: digest(path) for path in files}
    require(sum(int(item["bytes"]) for item in expected.values()) <= 500_000_000, "payload exceeds cap")
    manifest = json.loads((zenodo / MANIFEST_NAME).read_text(encoding="utf-8"))
    require(manifest.get("version") == VERSION and manifest.get("release_date") == RELEASE_DATE, "manifest version/date drifted")
    require(manifest.get("work", {}).get("title") == TITLE.replace("—", "-"), "manifest title drifted")
    require(manifest.get("work", {}).get("model") == MODEL, "model provenance drifted")
    require(manifest.get("preservation", {}).get("zenodo_concept_doi") == CONCEPT_DOI, "competing concept detected")
    require(manifest.get("rights") == base.RIGHTS, "component rights drifted")
    require("TTP" not in json.dumps(manifest.get("work", {}), ensure_ascii=False), "organization label leaked into work prose")
    ready = manifest.get("publication_ready") is True
    if not allow_preparation:
        require(ready, "stage is not publication-ready")
    if ready:
        doi = str(manifest.get("preservation", {}).get("zenodo_version_doi", ""))
        require(base.DOI.fullmatch(doi) is not None and doi != CONCEPT_DOI, "reserved version DOI is invalid")
    by_name = {item.get("name"): item for item in manifest.get("files", []) if isinstance(item, dict)}
    require(set(by_name) == {READER_NAME, ZIP_NAME, LICENSE_NAME}, "manifest file inventory drifted")
    for name, item in by_name.items():
        require(item.get("bytes") == expected[name]["bytes"] and item.get("sha256") == expected[name]["sha256"], f"manifest hash drifted: {name}")
    require(by_name[READER_NAME].get("role") == "primary_reader" and by_name[READER_NAME].get("pages") == EXPECTED_PAGES, "reader is not primary/exact")
    with zipfile.ZipFile(zenodo / ZIP_NAME) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        require(bool(members) and archive.testzip() is None, "source ZIP is empty or corrupt")
        for item in members:
            member = PurePosixPath(item.filename)
            require(not member.is_absolute() and ".." not in member.parts, f"unsafe ZIP member {item.filename}")
    sums = checksum_map(zenodo / SUMS_NAME)
    require(set(sums) == {READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME}, "checksum inventory drifted")
    for name, value in sums.items():
        require(value == expected[name]["sha256"], f"checksum drifted: {name}")
    return manifest, expected


def configure_base() -> None:
    for name, value in {
        "VERSION": VERSION, "RELEASE_DATE": RELEASE_DATE, "MODEL": MODEL,
        "TITLE": TITLE, "MANIFEST_TITLE": TITLE.replace("—", "-"),
        "CONCEPT_DOI": CONCEPT_DOI, "READER_NAME": READER_NAME,
        "READER_REL": READER_REL, "ZIP_NAME": ZIP_NAME,
        "LICENSE_NAME": LICENSE_NAME, "MANIFEST_NAME": MANIFEST_NAME,
        "SUMS_NAME": SUMS_NAME, "EXPECTED_NAMES": EXPECTED_NAMES,
        "BUILD_EVIDENCE_REL": BUILD_EVIDENCE_REL,
        "BACKEND_EVIDENCE_REL": BACKEND_EVIDENCE_REL,
        "EXPECTED_PAGES": EXPECTED_PAGES, "EXPECTED_COMPONENTS": EXPECTED_COMPONENTS,
        "EXPECTED_SOURCE_PAGES": EXPECTED_SOURCE_PAGES,
    }.items():
        setattr(base, name, value)
    base.validate_reader_and_base_evidence = validate_reader_and_base_evidence
    base.validate_final_evidence = validate_final_evidence
    base.validate_stage = validate_stage


def output_directory_from_argv() -> Path:
    marker = "--output-directory"
    require(marker in sys.argv and sys.argv.index(marker) + 1 < len(sys.argv), "--output-directory is required")
    return Path(sys.argv[sys.argv.index(marker) + 1]).resolve()


def finalize_stage(stage: Path) -> dict[str, Any]:
    zenodo = stage / "zenodo"
    manifest_path = zenodo / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["work"]["coverage"] = (
        "Pendahuluan dan Bab 1-6 lengkap dalam Unit 001-044 (37 komponen pembaca). "
        "Bab 7-10 Li, komponen teori representasi Duncan, enam span CRing, dan "
        "lapisan konektif/penguasaan belum disertakan."
    )
    qa = manifest["qa"]
    qa.pop("chapter_5_backend_validation", None)
    qa["chapter_6_backend_validation"] = "pass"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    checksum_paths = [zenodo / name for name in (READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME)]
    (zenodo / SUMS_NAME).write_text(
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in checksum_paths),
        encoding="utf-8", newline="\n",
    )
    inventory_path = stage / "inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["zenodo"] = [digest(zenodo / name) for name in EXPECTED_NAMES]
    inventory["zenodo_payload_bytes"] = sum(int(item["bytes"]) for item in inventory["zenodo"])
    inventory["under_cap"] = inventory["zenodo_payload_bytes"] <= 500_000_000
    inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest, _ = validate_stage(stage, allow_preparation=not bool(inventory.get("publication_ready")))
    coverage = manifest["work"]["coverage"]
    for phrase in ("Bab 1-6 lengkap", "Unit 001-044", "Bab 7-10", "Duncan", "CRing"):
        require(phrase in coverage, f"coverage lacks {phrase!r}")
    return inventory


def main() -> None:
    configure_base()
    stage = output_directory_from_argv()
    base.main()
    inventory = finalize_stage(stage)
    print(json.dumps({
        "result": "PASS", "version": VERSION,
        "publication_ready": inventory["publication_ready"],
        "zenodo_payload_bytes": inventory["zenodo_payload_bytes"],
        "zenodo_version_doi": inventory["zenodo_version_doi"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
