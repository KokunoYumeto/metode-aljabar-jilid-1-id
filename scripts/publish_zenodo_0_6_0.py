#!/usr/bin/env python3
"""Publish checkpoint 0.6.0 through an existing-concept Zenodo version draft."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATH = Path(r"C:\Users\Floris\Documents\Obsidian notes\New zenodo token.md")
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
VERSION = "0.6.0"
PUBLICATION_DATE = "2026-08-25"
CONCEPT_DOI = "10.5281/zenodo.22059759"
CONCEPT_RECORD_ID = 22059759
READER_NAME = "00-metode-aljabar-jilid-1-id-checkpoint-0.6.0-reader.pdf"
ZIP_NAME = "10-metode-aljabar-jilid-1-id-source-backend-0.6.0.zip"
LICENSE_NAME = "20-LICENSES.md"
MANIFEST_NAME = "30-MANIFEST.json"
SUMS_NAME = "40-SHA256SUMS.txt"
EXPECTED_NAMES = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME, SUMS_NAME]
EXPECTED_RIGHTS = [
    ("principal source text and Indonesian adaptation", "CC BY 4.0"),
    ("credited Lanzhou.png and credited AJbook.cls fragment", "CC BY-SA 3.0"),
    ("bundled Noto fonts", "SIL OFL 1.1"),
]
LICENSE_REQUIRED_PHRASES = [
    "Tidak ada satu label lisensi yang menggantikan hak setiap komponennya.",
    "Methods in Algebra, Volume 1",
    "Wen-Wei Li",
    "Creative Commons Attribution 4.0 International",
    "https://creativecommons.org/licenses/by/4.0/",
    "edisi ini independen serta tidak disahkan oleh penulis atau penerbit sumber",
    "repo/source/LICENSE",
    "repo/source/AJbook.cls",
    "Guido",
    "dpprdan",
    "CC BY-SA 3.0",
    "repo/source/Lanzhou.png",
    "Chk2011",
    "repo/fonts/",
    "SIL Open Font License 1.1",
    "repo/fonts/OFL-1.1-Noto-CJK.txt",
    "tidak mengubah atau memperluas izin komponen pihak ketiga",
]
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
ZENODO_DOI = re.compile(r"10\.5281/zenodo\.(\d+)\Z")


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(path: Path) -> dict[str, object]:
    return {
        "name": path.name,
        "bytes": path.stat().st_size,
        "sha256": hash_file(path, "sha256"),
        "md5": hash_file(path, "md5"),
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"Could not read valid JSON from {path}: {error}")
    require(isinstance(value, dict), f"Expected a JSON object in {path}")
    return value


def normalize_license_id(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("id")
    return str(value or "")


def people_names(value: object) -> list[str]:
    require(isinstance(value, list), "People metadata must be a list")
    require(all(isinstance(item, dict) for item in value), "People metadata contains a non-object")
    return [str(item.get("name", "")) for item in value]


def contributor_signatures(value: object) -> list[tuple[str, str]]:
    require(isinstance(value, list), "Contributor metadata must be a list")
    require(all(isinstance(item, dict) for item in value),
            "Contributor metadata contains a non-object")
    return [(str(item.get("name", "")), str(item.get("type", ""))) for item in value]


def related_identifier_signatures(value: object) -> list[tuple[str, str, str]]:
    require(isinstance(value, list), "Related-identifier metadata must be a list")
    require(all(isinstance(item, dict) for item in value),
            "Related-identifier metadata contains a non-object")
    signatures = [
        (
            str(item.get("identifier", "")),
            str(item.get("relation", "")),
            str(item.get("scheme", "")),
        )
        for item in value
    ]
    require(len(signatures) == len(set(signatures)), "Related identifiers contain duplicates")
    return signatures


def validate_metadata_semantics(
    actual: object,
    expected: dict[str, Any],
    *,
    context: str,
    public_record: bool = False,
) -> None:
    """Compare the publication-critical metadata while allowing API-added fields."""
    require(isinstance(actual, dict), f"{context} metadata is not an object")
    scalar_fields = [
        "title",
        "publication_date",
        "description",
        "access_right",
        "language",
        "notes",
        "version",
    ]
    if public_record:
        resource_type = actual.get("resource_type")
        require(isinstance(resource_type, dict),
                f"{context} lacks a public resource-type object")
        require(
            resource_type.get("type") == expected["upload_type"]
            and resource_type.get("subtype") == expected["publication_type"],
            f"{context} resource type drifted: {resource_type!r}",
        )
    else:
        scalar_fields.extend(("imprint_publisher", "upload_type", "publication_type"))
    for field in scalar_fields:
        require(actual.get(field) == expected[field],
                f"{context} {field} drifted: {actual.get(field)!r}")
    require(
        normalize_license_id(actual.get("license"))
        == normalize_license_id(expected.get("license")),
        f"{context} license drifted: {actual.get('license')!r}",
    )
    require(
        people_names(actual.get("creators")) == people_names(expected.get("creators")),
        f"{context} creators drifted: {actual.get('creators')!r}",
    )
    require(
        contributor_signatures(actual.get("contributors"))
        == contributor_signatures(expected.get("contributors")),
        f"{context} contributors drifted: {actual.get('contributors')!r}",
    )
    actual_keywords = actual.get("keywords")
    expected_keywords = expected.get("keywords")
    require(isinstance(actual_keywords, list) and isinstance(expected_keywords, list),
            f"{context} keywords are not lists")
    require(all(isinstance(item, str) for item in actual_keywords + expected_keywords),
            f"{context} keywords contain a non-string value")
    require(len(actual_keywords) == len(set(actual_keywords)),
            f"{context} keywords contain duplicates")
    require(len(expected_keywords) == len(set(expected_keywords)),
            f"{context} expected keywords contain duplicates")
    require(set(actual_keywords) == set(expected_keywords),
            f"{context} keywords drifted: {actual_keywords!r}")
    require(
        set(related_identifier_signatures(actual.get("related_identifiers")))
        == set(related_identifier_signatures(expected.get("related_identifiers"))),
        f"{context} related identifiers drifted: {actual.get('related_identifiers')!r}",
    )


def validate_draft_envelope(
    draft: object,
    *,
    draft_id: int,
    version_doi: str,
    context: str,
    expected_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(draft, dict), f"{context} draft response is not an object")
    require(draft.get("id") == draft_id, f"{context} returned a different draft ID")
    require(not draft.get("submitted") and draft.get("state") == "unsubmitted",
            f"{context} is not the expected unsubmitted draft: {draft.get('state')}")
    require(str(draft.get("conceptrecid", "")) == str(CONCEPT_RECORD_ID),
            f"{context} left concept record {CONCEPT_RECORD_ID}: {draft.get('conceptrecid')}")
    draft_metadata = draft.get("metadata")
    require(isinstance(draft_metadata, dict), f"{context} lacks metadata")
    reserved = draft_metadata.get("prereserve_doi", {})
    require(isinstance(reserved, dict), f"{context} lacks a reserved DOI object")
    require(reserved.get("doi") == version_doi,
            f"{context} reserved DOI drifted: {reserved.get('doi')}")
    require(str(reserved.get("recid", "")) == str(draft_id),
            f"{context} reserved record ID drifted: {reserved.get('recid')}")
    if expected_metadata is not None:
        validate_metadata_semantics(draft_metadata, expected_metadata, context=context)
    return draft


def validate_stage(stage: Path) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    zenodo_dir = stage / "zenodo"
    require(zenodo_dir.is_dir(), f"Missing Zenodo stage directory: {zenodo_dir}")
    files = sorted(path for path in zenodo_dir.iterdir() if path.is_file())
    require([path.name for path in files] == EXPECTED_NAMES,
            f"Unexpected Zenodo stage inventory: {[path.name for path in files]}")
    require(not any(path.is_dir() for path in zenodo_dir.iterdir()),
            "Zenodo stage contains an unexpected directory")

    expected = {path.name: digest(path) for path in files}
    require(sum(int(item["bytes"]) for item in expected.values()) <= 500_000_000,
            "Release payload exceeds the 500,000,000-byte work-level cap")

    manifest = load_json(zenodo_dir / MANIFEST_NAME)
    require(manifest.get("schema") == "metode-aljabar-checkpoint/v4", "Unexpected manifest schema")
    require(manifest.get("version") == VERSION, "Manifest version is not 0.6.0")
    require(manifest.get("release_date") == PUBLICATION_DATE, "Manifest release date drifted")
    work = manifest.get("work", {})
    require(work.get("title") == TITLE.replace("—", "-"), "Manifest title drifted")
    require(work.get("language") == "id-ID", "Manifest language is not id-ID")
    require(work.get("status") == "partial_public_active", "Manifest status drifted")
    require(work.get("model") == MODEL, "Manifest model provenance drifted")
    require(work.get("independent_nonendorsed") is True,
            "Manifest does not preserve the independent/non-endorsed relationship")
    coverage = str(work.get("coverage", ""))
    require("TTP" not in str(work), "Manifest work metadata contains a forbidden organization label")
    for phrase in ("Unit 001-024", "Bab 4-10 Li", "Duncan", "CRing", "belum disertakan"):
        require(phrase in coverage, f"Manifest coverage lacks required phrase: {phrase}")

    authority = manifest.get("authority", {})
    require(bool(HEX40.fullmatch(str(authority.get("edition_receipt_commit", "")))),
            "Manifest edition commit is not a full SHA-1")
    require(bool(HEX40.fullmatch(str(authority.get("checkpoint_content_commit", "")))),
            "Manifest checkpoint content commit is not a full SHA-1")
    preservation = manifest.get("preservation", {})
    require(preservation.get("zenodo_concept_doi") == CONCEPT_DOI,
            "Manifest points to a competing Zenodo concept")
    version_doi = str(preservation.get("zenodo_version_doi", ""))
    doi_match = ZENODO_DOI.fullmatch(version_doi)
    require(doi_match is not None and version_doi != CONCEPT_DOI,
            f"Manifest has an invalid reserved version DOI: {version_doi}")

    rights = manifest.get("rights")
    require(isinstance(rights, list), "Manifest rights must be a list")
    require(all(isinstance(item, dict) for item in rights),
            "Manifest rights contains a non-object")
    rights_pairs = [
        (str(item.get("component", "")), str(item.get("license", "")))
        for item in rights
    ]
    require(rights_pairs == EXPECTED_RIGHTS,
            f"Manifest component-rights boundary drifted: {rights_pairs!r}")

    manifest_files = manifest.get("files")
    require(isinstance(manifest_files, list) and len(manifest_files) == 3,
            "Manifest must describe exactly reader, source/backend ZIP, and license")
    manifest_by_name = {
        item.get("name"): item for item in manifest_files if isinstance(item, dict)
    }
    require(set(manifest_by_name) == {READER_NAME, ZIP_NAME, LICENSE_NAME},
            "Manifest file inventory drifted")
    for name in (READER_NAME, ZIP_NAME, LICENSE_NAME):
        item = manifest_by_name[name]
        require(item.get("bytes") == expected[name]["bytes"], f"Manifest bytes drifted for {name}")
        require(item.get("sha256") == expected[name]["sha256"], f"Manifest SHA-256 drifted for {name}")
    reader = manifest_by_name[READER_NAME]
    require(reader.get("role") == "primary_reader", "Reader is not the primary manifest file")
    require(reader.get("pages") == 229, "Reader page count drifted")
    require(reader.get("language") == "id-ID", "Reader /Lang evidence drifted")
    require(reader.get("widgets") == 0 and reader.get("unsafe_actions") == 0,
            "Reader contains unexpected interactive or unsafe actions")
    require(manifest_by_name[LICENSE_NAME].get("role") == "controlling_component_rights_notice",
            "License notice is not marked as the controlling component-rights file")

    license_text = (zenodo_dir / LICENSE_NAME).read_text(encoding="utf-8")
    require("\x00" not in license_text, "License notice contains a NUL byte")
    require("TTP" not in license_text,
            "License notice contains a forbidden organization-label occurrence")
    for phrase in LICENSE_REQUIRED_PHRASES:
        require(phrase in license_text,
                f"License notice lacks required rights/attribution phrase: {phrase}")

    qa = manifest.get("qa", {})
    require(qa.get("reader_pages") == 229 and qa.get("source_units") == 24,
            "Manifest checkpoint coverage drifted")
    require(qa.get("source_unit_pages") == 228, "Manifest source-page total drifted")
    require(qa.get("source_to_merged_pages_compared") == 228,
            "Manifest content comparison is incomplete")
    require(qa.get("source_to_merged_pages_pixel_identical") == 228,
            "Manifest pixel comparison is incomplete")
    require(qa.get("all_pages_visually_inspected") is True,
            "Manifest does not record all-page visual inspection")
    require(qa.get("github_public_byte_readback") is True,
            "Manifest does not record GitHub public-byte readback")

    evidence = manifest.get("evidence")
    require(isinstance(evidence, list) and len(evidence) == 3,
            "Manifest must bind machine QA, visual review, and GitHub readback evidence")
    evidence_by_role = {
        item.get("role"): item for item in evidence if isinstance(item, dict)
    }
    require(
        set(evidence_by_role)
        == {
            "checkpoint_machine_qa",
            "all_page_visual_review",
            "anonymous_github_public_byte_readback",
        },
        "Manifest evidence-role inventory drifted",
    )
    for role, item in evidence_by_role.items():
        evidence_path = (ROOT / str(item.get("path", ""))).resolve()
        try:
            evidence_path.relative_to(ROOT)
        except ValueError:
            fail(f"Manifest evidence escapes the repository: {item.get('path')}")
        require(evidence_path.is_file(), f"Missing bound evidence for {role}: {evidence_path}")
        require(item.get("bytes") == evidence_path.stat().st_size,
                f"Evidence bytes drifted for {role}")
        require(item.get("sha256") == hash_file(evidence_path, "sha256"),
                f"Evidence hash drifted for {role}")

    checksum_lines = (zenodo_dir / SUMS_NAME).read_text(encoding="utf-8").splitlines()
    checksum_map: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"Malformed SHA256SUMS line: {line!r}")
        checksum, name = match.groups()
        require(name not in checksum_map, f"Duplicate SHA256SUMS entry: {name}")
        checksum_map[name] = checksum
    summed_names = [READER_NAME, ZIP_NAME, LICENSE_NAME, MANIFEST_NAME]
    require(set(checksum_map) == set(summed_names), "SHA256SUMS inventory drifted")
    for name in summed_names:
        require(checksum_map[name] == expected[name]["sha256"],
                f"SHA256SUMS mismatch for {name}")

    inventory = load_json(stage / "inventory.json")
    require(inventory.get("version") == VERSION, "Release inventory version drifted")
    require(inventory.get("edition_commit") == authority["edition_receipt_commit"],
            "Inventory/manifest edition commit mismatch")
    require(inventory.get("checkpoint_content_commit") == authority["checkpoint_content_commit"],
            "Inventory/manifest checkpoint commit mismatch")
    recorded = inventory.get("zenodo")
    require(isinstance(recorded, list) and len(recorded) == len(EXPECTED_NAMES),
            "Release inventory lacks the exact Zenodo payload")
    recorded_by_name = {item.get("name"): item for item in recorded if isinstance(item, dict)}
    require(set(recorded_by_name) == set(EXPECTED_NAMES), "Release inventory names drifted")
    for name in EXPECTED_NAMES:
        require(recorded_by_name[name].get("bytes") == expected[name]["bytes"],
                f"Release inventory bytes drifted for {name}")
        require(recorded_by_name[name].get("sha256") == expected[name]["sha256"],
                f"Release inventory hash drifted for {name}")
    return manifest, expected


def make_description(manifest: dict[str, Any]) -> str:
    authority = manifest["authority"]
    qa = manifest["qa"]
    return (
        "<p>Edisi Bahasa Indonesia independen yang sedang berlangsung dari "
        "<em>Methods in Algebra, Volume 1</em> karya Wen-Wei Li. Versi 0.6.0 "
        f"memuat checkpoint pembaca {qa['reader_pages']} halaman dan dua puluh empat "
        "reader mandiri: pendahuluan lengkap, Bab 1 lengkap, Bab 2 lengkap, serta "
        "Bab 3 lengkap termasuk latihannya. Bab 4–10 Li, komponen teori representasi "
        "Duncan, enam span CRing, dan lapisan konektif/penguasaan belum disertakan.</p>"
        "<p>Matematika, latihan, petunjuk, sitasi, rujukan silang, diagram, dan "
        "indeks dipertahankan pada cakupan sumber. Arsip sumber/backend mengikat "
        "setiap unit ke sumber dan target melalui hash, ID stabil lintas bahasa, "
        "hak komponen, serta bukti build/QA. Seluruh 228 halaman unit tetap identik "
        "secara visual setelah dirangkai menjadi checkpoint.</p>"
        f"<p>Provenance produksi: {html.escape(MODEL)}. Keterangan ini terpisah "
        "dari kepengarangan Wen-Wei Li dan tidak menggantikan kredit penulis, "
        "sumber, atau komponen manusia.</p>"
        "<p>Otoritas sumber dibekukan pada commit "
        f"<code>{html.escape(authority['source_commit'])}</code>, tree "
        f"<code>{html.escape(authority['source_tree'])}</code>, dan PDF resmi "
        f"{authority['official_pdf_pages']} halaman dengan SHA-256 "
        f"<code>{html.escape(authority['official_pdf_sha256'])}</code>. Arsip versi "
        "ini berasal dari commit edisi "
        f"<code>{html.escape(authority['edition_receipt_commit'])}</code>.</p>"
        "<p>Hak tidak diratakan: teks utama dan adaptasi Indonesia menggunakan CC BY "
        "4.0; <code>Lanzhou.png</code> dan fragmen <code>AJbook.cls</code> yang "
        "dikreditkan menggunakan CC BY-SA 3.0; font Noto yang dibundel menggunakan "
        "OFL 1.1. Pemberitahuan per komponen di <code>20-LICENSES.md</code> "
        "mengendalikan.</p>"
        "<p>Ini adalah turunan independen, bukan edisi resmi, dan tidak disahkan "
        "oleh penulis atau pihak hulu.</p>"
    )


def read_token() -> str:
    text = TOKEN_PATH.read_text(encoding="utf-8").strip()
    match = re.search(r"([A-Za-z0-9._~-]{20,})", text)
    if not match:
        fail("No usable Zenodo token found in the local credential note")
    return match.group(1)


def request(
    session: requests.Session,
    method: str,
    url: str,
    *,
    accepted: set[int] | None = None,
    **kwargs: object,
) -> requests.Response:
    accepted = accepted or {200, 201, 202, 204}
    last: requests.Response | None = None
    for attempt in range(4):
        try:
            response = session.request(method, url, timeout=(30, 300), **kwargs)
        except requests.RequestException:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
            continue
        last = response
        if response.status_code in accepted:
            return response
        if response.status_code in {429, 502, 503, 504} and attempt < 3:
            time.sleep(4 * (attempt + 1))
            continue
        detail = response.content[:500].decode("utf-8", "replace")
        fail(f"Zenodo {method} {url} -> HTTP {response.status_code}: {detail}")
    detail = last.content[:500].decode("utf-8", "replace") if last else "no response"
    fail(f"Zenodo request exhausted retries: {detail}")


def delete_file(session: requests.Session, url: str) -> None:
    for attempt in range(4):
        try:
            response = session.delete(url, timeout=(20, 90))
        except requests.RequestException:
            response = None
        if response is not None and response.status_code in {200, 202, 204, 404}:
            return
        if response is not None and response.status_code not in {429, 502, 503, 504}:
            detail = response.content[:300].decode("utf-8", "replace")
            fail(f"Zenodo DELETE {url} -> HTTP {response.status_code}: {detail}")
        time.sleep(3 * (attempt + 1))
    fail(f"Could not confirm deletion of inherited draft file: {url}")


def normalize_md5(value: object) -> str:
    text = str(value or "").lower()
    return text.removeprefix("md5:")


def draft_inventory_matches(
    draft_files: list[dict[str, Any]], expected: dict[str, dict[str, object]]
) -> bool:
    if len(draft_files) != len(expected):
        return False
    by_name = {item.get("filename"): item for item in draft_files}
    if set(by_name) != set(expected):
        return False
    return all(
        item.get("filesize") == expected[name]["bytes"]
        and normalize_md5(item.get("checksum")) == expected[name]["md5"]
        for name, item in by_name.items()
    )


def stream_digest(session: requests.Session, url: str) -> tuple[int, str]:
    response = request(session, "GET", url, accepted={200}, stream=True)
    digest_value = hashlib.sha256()
    total = 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            total += len(chunk)
            digest_value.update(chunk)
    return total, digest_value.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, required=True,
                        help="existing unsubmitted 0.6.0 draft in concept 10.5281/zenodo.22059759")
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    stage = args.stage.resolve()
    manifest, expected = validate_stage(stage)
    authority = manifest["authority"]
    preservation = manifest["preservation"]
    version_doi = preservation["zenodo_version_doi"]
    version_record_id = int(ZENODO_DOI.fullmatch(version_doi).group(1))
    require(args.draft_id == version_record_id,
            f"Draft ID {args.draft_id} does not match reserved DOI {version_doi}")
    description = make_description(manifest)

    notes = (
        "Status: parsial publik aktif. Unit 001-024 mencakup pendahuluan, Bab 1, "
        "Bab 2, dan Bab 3 lengkap termasuk latihan. Bab 4-10 Li serta komponen "
        "Duncan/CRing/konektif-penguasaan belum termasuk. Paket memakai beberapa "
        "lisensi terbuka; 20-LICENSES.md dan RIGHTS_COMPONENTS.csv mengendalikan "
        "ketentuan per komponen."
    )
    require("TTP" not in TITLE and "TTP" not in description and "TTP" not in notes,
            "Organization label may occur only in its single contributor entry")

    authenticated = requests.Session()
    authenticated.trust_env = False
    authenticated.headers.update(
        {
            "Authorization": f"Bearer {read_token()}",
            "User-Agent": "Codex O013 Zenodo publication client",
        }
    )
    base = f"https://zenodo.org/api/deposit/depositions/{args.draft_id}"
    draft = validate_draft_envelope(
        request(authenticated, "GET", base, accepted={200}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
        context="Initial Zenodo response",
    )

    zenodo_dir = stage / "zenodo"
    files = [zenodo_dir / name for name in EXPECTED_NAMES]
    payload_already_present = draft_inventory_matches(draft.get("files", []), expected)
    if not payload_already_present:
        for _round in range(3):
            inherited = draft.get("files", [])
            if not inherited:
                break
            for old in inherited:
                delete_file(authenticated, old["links"]["self"])
            draft = request(authenticated, "GET", base, accepted={200}).json()
        require(not draft.get("files"), "Inherited draft inventory remains after bounded deletion")

    metadata = {
        "title": TITLE,
        "publication_date": PUBLICATION_DATE,
        "description": description,
        "access_right": "open",
        "creators": [{"name": "Li, Wen-Wei"}],
        "contributors": [{"name": "TTP", "type": "ProjectMember"}],
        "keywords": [
            "aljabar",
            "teori himpunan",
            "teori kategori",
            "kategori monoidal",
            "teori grup",
            "Bahasa Indonesia",
            "buku teks terbuka",
            "graduate algebra",
            "matematika",
        ],
        "related_identifiers": [
            {
                "identifier": "https://github.com/wenweili/AlJabr-1/commit/c4f7a01f68f5f407906b4b970640cddbbad85f6b",
                "relation": "isDerivedFrom",
                "scheme": "url",
            },
            {"identifier": "978-7-04-050725-6", "relation": "isDerivedFrom", "scheme": "isbn"},
            {
                "identifier": (
                    "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/"
                    f"{authority['edition_receipt_commit']}"
                ),
                "relation": "isSupplementTo",
                "scheme": "url",
            },
        ],
        "language": "ind",
        "license": "other-open",
        "imprint_publisher": "Zenodo",
        "notes": notes,
        "upload_type": "publication",
        "publication_type": "book",
        "version": VERSION,
        "prereserve_doi": {"doi": version_doi, "recid": args.draft_id},
    }
    combined_people = metadata["creators"] + metadata["contributors"]
    require(sum(person.get("name") == "TTP" for person in combined_people) == 1,
            "Metadata must contain exactly one organization contributor")
    nonpeople_metadata = {
        key: value for key, value in metadata.items() if key not in {"creators", "contributors"}
    }
    require("TTP" not in json.dumps(nonpeople_metadata, ensure_ascii=False),
            "Organization label leaked into prose or non-person metadata")
    draft = validate_draft_envelope(
        request(authenticated, "PUT", base, json={"metadata": metadata}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
        context="Zenodo PUT response",
        expected_metadata=metadata,
    )

    if not payload_already_present:
        bucket = draft["links"]["bucket"]
        for path in files:
            with path.open("rb") as handle:
                request(
                    authenticated,
                    "PUT",
                    f"{bucket}/{path.name}",
                    data=handle,
                    headers={"Content-Type": "application/octet-stream"},
                )

    draft = validate_draft_envelope(
        request(authenticated, "GET", base, accepted={200}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
        context="Final pre-publish Zenodo response",
        expected_metadata=metadata,
    )
    draft_files = draft.get("files", [])
    require(draft_inventory_matches(draft_files, expected),
            f"Draft byte inventory differs: {[item.get('filename') for item in draft_files]}")

    published = request(authenticated, "POST", draft["links"]["publish"]).json()
    record_id = published["id"]
    require(record_id == args.draft_id, f"Published record ID drifted: {record_id}")
    public_url = f"https://zenodo.org/records/{record_id}"

    anonymous = requests.Session()
    anonymous.trust_env = False
    anonymous.headers.update({"User-Agent": "Codex O013 anonymous readback client"})
    public_api = f"https://zenodo.org/api/records/{record_id}"
    public_response: requests.Response | None = None
    for attempt in range(8):
        candidate = anonymous.get(public_api, timeout=(30, 90))
        if candidate.status_code == 200:
            public_response = candidate
            break
        time.sleep(2 + attempt)
    require(public_response is not None,
            "Published Zenodo record did not become anonymously readable")
    public = public_response.json()

    require(public.get("doi") == version_doi, f"Published DOI drifted: {public.get('doi')}")
    require(public.get("conceptdoi") == CONCEPT_DOI,
            f"Published record left the intended concept: {public.get('conceptdoi')}")
    public_files = public.get("files", [])
    public_names = [item["key"] for item in public_files]
    require(len(public_names) == len(EXPECTED_NAMES) and set(public_names) == set(EXPECTED_NAMES),
            f"Published file inventory differs: {public_names}")
    require(public_names[0] == READER_NAME,
            f"Primary visible file is not the reader: {public_names}")
    public_metadata = public.get("metadata", {})
    validate_metadata_semantics(
        public_metadata,
        metadata,
        context="Anonymous postpublication record",
        public_record=True,
    )
    require(public_metadata.get("title") == TITLE and public_metadata.get("version") == VERSION,
            "Published title/version metadata differs")
    public_description = str(public_metadata.get("description", ""))
    public_notes = str(public_metadata.get("notes", ""))
    for phrase in ("Versi 0.6.0", "dua puluh empat", "Bab 3 lengkap", "Duncan", "CRing"):
        require(phrase in public_description,
                f"Published description lacks required coverage phrase: {phrase}")
    for phrase in ("Unit 001-024", "Bab 4-10 Li", "Duncan/CRing"):
        require(phrase in public_notes,
                f"Published notes lack required coverage phrase: {phrase}")
    combined_public = public_metadata.get("creators", []) + public_metadata.get("contributors", [])
    require(sum(item.get("name") == "TTP" for item in combined_public) == 1,
            "Published organization metadata occurrence invariant failed")
    require("TTP" not in public_metadata.get("title", "")
            and "TTP" not in public_description
            and "TTP" not in public_notes,
            "Published prose contains a forbidden organization-label occurrence")
    public_nonpeople = {
        key: value
        for key, value in public_metadata.items()
        if key not in {"creators", "contributors"}
    }
    require("TTP" not in json.dumps(public_nonpeople, ensure_ascii=False),
            "Published non-person metadata contains a forbidden organization-label occurrence")

    readback: list[dict[str, object]] = []
    for item in public_files:
        total, checksum = stream_digest(anonymous, item["links"]["self"])
        local = expected[item["key"]]
        require((total, checksum) == (local["bytes"], local["sha256"]),
                f"Public-byte mismatch for {item['key']}: {total}/{checksum}")
        readback.append(
            {
                "name": item["key"],
                "bytes": total,
                "sha256": checksum,
                "file_id": item["id"],
            }
        )

    receipt_path = args.receipt.resolve() if args.receipt.is_absolute() else (ROOT / args.receipt).resolve()
    try:
        receipt_path.relative_to(ROOT)
    except ValueError:
        fail(f"Receipt must remain inside the edition repository: {receipt_path}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zenodo publication receipt — version 0.6.0",
        "",
        f"Date: {PUBLICATION_DATE}",
        f"Record: `{public_url}`",
        f"Version DOI: `{version_doi}`",
        f"Concept DOI: `{CONCEPT_DOI}`",
        f"Version: `{VERSION}`",
        f"Edition release commit: `{authority['edition_receipt_commit']}`",
        f"Checkpoint content commit: `{authority['checkpoint_content_commit']}`",
        "",
        "The existing concept lineage was updated; no competing concept was created.",
        "The exact work title and Wen-Wei Li creator credit are preserved. The single organization contributor entry is separate from the title, description, and prose metadata. Metadata states the partial Unit 001-024 scope, exact model provenance, independent/non-endorsed relationship, current Li/Duncan/CRing architecture boundary, and mixed component-rights boundary.",
        "",
        "## Published and anonymously verified files",
        "",
        "| File ID | File | Bytes | SHA-256 |",
        "|---:|---|---:|---|",
    ]
    for item in readback:
        lines.append(
            f"| {item['file_id']} | `{item['name']}` | {item['bytes']:,} | `{item['sha256']}` |"
        )
    total_bytes = sum(int(item["bytes"]) for item in readback)
    lines.extend(
        [
            "",
            f"All {len(readback)} public files ({total_bytes:,} bytes) were downloaded without credentials after publication and matched local byte counts and SHA-256 hashes. Result: **PASS**.",
            "Rights: principal text/adaptation CC BY 4.0; credited Lanzhou.png and AJbook.cls fragment CC BY-SA 3.0; bundled Noto fonts OFL 1.1. This receipt contains no credential material.",
            f"Model provenance: `{MODEL}`. Signed: `Codex, on instructions of the user.`",
        ]
    )
    receipt_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "record_id": record_id,
                "public_url": public_url,
                "doi": version_doi,
                "concept_doi": CONCEPT_DOI,
                "version": VERSION,
                "files": readback,
                "total_bytes": total_bytes,
                "anonymous_public_api": True,
                "anonymous_file_readback": True,
                "receipt": str(receipt_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
