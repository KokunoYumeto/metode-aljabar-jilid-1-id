#!/usr/bin/env python3
"""Validate or publish Zenodo checkpoint 0.7.0 in the existing concept lineage.

The default operation is local validation only and does not read credentials or
contact Zenodo.  Network mutation requires the explicit ``--publish`` flag plus
an already-created new-version draft whose concept and reserved DOI match the
final release manifest.  This prevents accidental duplicate concepts/drafts.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
from pathlib import Path
from typing import Any

from build_release_0_7_0 import (
    CONCEPT_DOI,
    EXPECTED_NAMES,
    LICENSE_NAME,
    MANIFEST_NAME,
    MODEL,
    READER_NAME,
    ROOT,
    SUMS_NAME,
    TITLE,
    VERSION,
    ZIP_NAME,
    validate_stage,
)


TOKEN_PATH = Path(r"C:\Users\Floris\Documents\Obsidian notes\New zenodo token.md")
CONCEPT_RECORD_ID = 22059759
PUBLICATION_DATE = "2026-08-28"
DOI = re.compile(r"10\.5281/zenodo\.(\d+)\Z")
requests: Any = None


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_token() -> str:
    text = TOKEN_PATH.read_text(encoding="utf-8").strip()
    match = re.search(r"([A-Za-z0-9._~-]{20,})", text)
    require(match is not None, "No usable Zenodo token found in the local credential note")
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


def normalize_license_id(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("id")
    return str(value or "")


def people(value: object) -> list[tuple[str, str]]:
    require(isinstance(value, list), "People metadata must be a list")
    require(all(isinstance(item, dict) for item in value),
            "People metadata contains a non-object")
    return [(str(item.get("name", "")), str(item.get("type", ""))) for item in value]


def related(value: object) -> set[tuple[str, str, str]]:
    require(isinstance(value, list), "Related identifiers must be a list")
    result = {
        (
            str(item.get("identifier", "")),
            str(item.get("relation", "")),
            str(item.get("scheme", "")),
        )
        for item in value
        if isinstance(item, dict)
    }
    require(len(result) == len(value), "Related identifiers are malformed or duplicated")
    return result


def validate_metadata(actual: object, expected: dict[str, Any], *, public: bool) -> None:
    require(isinstance(actual, dict), "Zenodo metadata is not an object")
    scalar = ["title", "publication_date", "description", "access_right", "language",
              "notes", "version"]
    if public:
        resource_type = actual.get("resource_type")
        require(isinstance(resource_type, dict), "Public metadata lacks resource_type")
        require(resource_type.get("type") == "publication"
                and resource_type.get("subtype") == "book",
                f"Public resource type drifted: {resource_type!r}")
    else:
        scalar.extend(("upload_type", "publication_type", "imprint_publisher"))
    for key in scalar:
        require(actual.get(key) == expected.get(key), f"Zenodo metadata {key} drifted")
    require(normalize_license_id(actual.get("license"))
            == normalize_license_id(expected.get("license")), "Zenodo license drifted")
    require(people(actual.get("creators")) == people(expected.get("creators")),
            "Zenodo creators drifted")
    require(people(actual.get("contributors")) == people(expected.get("contributors")),
            "Zenodo contributors drifted")
    require(set(actual.get("keywords", [])) == set(expected.get("keywords", [])),
            "Zenodo keywords drifted")
    require(related(actual.get("related_identifiers"))
            == related(expected.get("related_identifiers")),
            "Zenodo related identifiers drifted")


def validate_draft(
    draft: object,
    *,
    draft_id: int,
    version_doi: str,
    expected_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require(isinstance(draft, dict), "Zenodo draft response is not an object")
    require(draft.get("id") == draft_id, "Zenodo returned a different draft")
    require(not draft.get("submitted") and draft.get("state") == "unsubmitted",
            "Zenodo target is not an unsubmitted new-version draft")
    require(str(draft.get("conceptrecid", "")) == str(CONCEPT_RECORD_ID),
            "Zenodo draft left the existing work concept")
    metadata = draft.get("metadata")
    require(isinstance(metadata, dict), "Zenodo draft lacks metadata")
    reserved = metadata.get("prereserve_doi")
    require(isinstance(reserved, dict), "Zenodo draft lacks a reserved DOI")
    require(reserved.get("doi") == version_doi, "Zenodo reserved DOI differs from manifest")
    require(str(reserved.get("recid", "")) == str(draft_id),
            "Zenodo reserved DOI record differs from draft")
    if expected_metadata is not None:
        validate_metadata(metadata, expected_metadata, public=False)
    return draft


def md5_file(path: Path) -> str:
    value = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def normalize_md5(value: object) -> str:
    return str(value or "").lower().removeprefix("md5:")


def draft_matches(files: list[dict[str, Any]], expected: dict[str, dict[str, object]],
                  zenodo: Path) -> bool:
    if len(files) != len(EXPECTED_NAMES):
        return False
    by_name = {item.get("filename"): item for item in files}
    if set(by_name) != set(EXPECTED_NAMES):
        return False
    return all(
        item.get("filesize") == expected[name]["bytes"]
        and normalize_md5(item.get("checksum")) == md5_file(zenodo / name)
        for name, item in by_name.items()
    )


def stream_sha256(session: requests.Session, url: str) -> tuple[int, str]:
    response = request(session, "GET", url, accepted={200}, stream=True)
    value = hashlib.sha256()
    total = 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            total += len(chunk)
            value.update(chunk)
    return total, value.hexdigest()


def description(manifest: dict[str, Any]) -> str:
    authority = manifest["authority"]
    return (
        "<p>Edisi Bahasa Indonesia independen yang sedang berlangsung dari "
        "<em>Methods in Algebra, Volume 1</em> karya Wen-Wei Li. Versi 0.7.0 "
        "memuat pembaca 385 halaman: pendahuluan serta Bab 1 sampai Bab 5 "
        "lengkap dalam 36 komponen pembaca. Bab 6 sampai Bab 10, komponen teori "
        "representasi Duncan, enam span CRing, dan lapisan konektif/penguasaan "
        "belum disertakan.</p>"
        "<p>Paket pembaca dipimpin oleh PDF; arsip ringkas menyertakan sumber "
        "yang dapat dilanjutkan, backend ID stabil, proyeksi CSV, skrip build, "
        "hak komponen, dan bukti deterministik yang relevan.</p>"
        f"<p>Provenance produksi: {html.escape(MODEL)}. Keterangan ini terpisah "
        "dari kepengarangan Wen-Wei Li dan tidak menggantikan kredit penulis, "
        "sumber, atau kontributor manusia.</p>"
        "<p>Otoritas sumber dibekukan pada commit "
        f"<code>{html.escape(authority['source_commit'])}</code>, tree "
        f"<code>{html.escape(authority['source_tree'])}</code>, dan PDF resmi "
        f"{authority['official_pdf_pages']} halaman dengan SHA-256 "
        f"<code>{html.escape(authority['official_pdf_sha256'])}</code>. Arsip versi "
        "ini berasal dari commit edisi "
        f"<code>{html.escape(authority['edition_receipt_commit'])}</code>.</p>"
        "<p>Hak tidak diratakan: teks utama/adaptasi CC BY 4.0; Lanzhou.png dan "
        "fragmen AJbook.cls masing-masing CC BY-SA 3.0; font Noto OFL 1.1; "
        "font Fandol 0.3 GPLv3 dengan pengecualian font. 20-LICENSES.md "
        "mengendalikan hak per komponen.</p>"
        "<p>Ini adalah turunan independen, bukan edisi resmi, dan tidak disahkan "
        "oleh penulis atau pihak hulu.</p>"
    )


def metadata_for(manifest: dict[str, Any], version_doi: str, draft_id: int) -> dict[str, Any]:
    authority = manifest["authority"]
    text = description(manifest)
    notes = (
        "Status: parsial publik aktif. Unit 001-043 mencakup pendahuluan serta "
        "Bab 1-5 lengkap. Bab 6-10 Li dan komponen Duncan/CRing/konektif-penguasaan "
        "belum termasuk. Paket multi-lisensi; 20-LICENSES.md dan "
        "RIGHTS_COMPONENTS.csv mengendalikan hak setiap komponen."
    )
    result: dict[str, Any] = {
        "title": TITLE,
        "publication_date": PUBLICATION_DATE,
        "description": text,
        "access_right": "open",
        "creators": [{"name": "Li, Wen-Wei"}],
        "contributors": [{"name": "TTP", "type": "ProjectMember"}],
        "keywords": [
            "aljabar", "teori himpunan", "teori kategori", "kategori monoidal",
            "teori grup", "teori gelanggang", "Bahasa Indonesia",
            "buku teks terbuka", "graduate algebra", "matematika",
        ],
        "related_identifiers": [
            {
                "identifier": (
                    "https://github.com/wenweili/AlJabr-1/commit/"
                    "c4f7a01f68f5f407906b4b970640cddbbad85f6b"
                ),
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
        "prereserve_doi": {"doi": version_doi, "recid": draft_id},
    }
    combined = result["creators"] + result["contributors"]
    require(sum(item.get("name") == "TTP" for item in combined) == 1,
            "Metadata must contain exactly one organization contributor")
    require("TTP" not in result["title"] and "TTP" not in text and "TTP" not in notes,
            "Organization label leaked into title or prose metadata")
    return result


def main() -> None:
    global requests
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--draft-id", type=int)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--publish", action="store_true",
                        help="mutate/publish the matching existing-concept new-version draft")
    args = parser.parse_args()

    stage = args.stage.resolve()
    manifest, expected = validate_stage(stage, allow_preparation=not args.publish)
    local_summary = {
        "stage": str(stage),
        "version": VERSION,
        "publication_ready": manifest["publication_ready"],
        "concept_doi": CONCEPT_DOI,
        "files": [expected[name] for name in EXPECTED_NAMES],
        "total_bytes": sum(int(expected[name]["bytes"]) for name in EXPECTED_NAMES),
        "network_mutation": False,
    }
    if not args.publish:
        print(json.dumps(local_summary, ensure_ascii=False, indent=2))
        return

    require(args.draft_id is not None, "--publish requires --draft-id")
    require(args.receipt is not None, "--publish requires --receipt")
    try:
        import requests as requests_module
    except ImportError as error:
        fail(f"Publishing requires the requests package: {error}")
    requests = requests_module
    version_doi = str(manifest["preservation"]["zenodo_version_doi"])
    match = DOI.fullmatch(version_doi)
    require(match is not None and int(match.group(1)) == args.draft_id,
            "Draft ID does not match the manifest reserved DOI")

    # Credential access begins only after every local publication gate has passed.
    authenticated = requests.Session()
    authenticated.trust_env = False
    authenticated.headers.update({
        "Authorization": f"Bearer {read_token()}",
        "User-Agent": "Codex O013 Zenodo 0.7.0 publication client",
    })
    base = f"https://zenodo.org/api/deposit/depositions/{args.draft_id}"
    draft = validate_draft(
        request(authenticated, "GET", base, accepted={200}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
    )
    zenodo = stage / "zenodo"
    payload_already_present = draft_matches(draft.get("files", []), expected, zenodo)
    if not payload_already_present:
        for _round in range(3):
            inherited = draft.get("files", [])
            if not inherited:
                break
            for item in inherited:
                delete_file(authenticated, item["links"]["self"])
            draft = request(authenticated, "GET", base, accepted={200}).json()
        require(not draft.get("files"), "Inherited draft files remain after bounded deletion")

    metadata = metadata_for(manifest, version_doi, args.draft_id)
    draft = validate_draft(
        request(authenticated, "PUT", base, json={"metadata": metadata}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
        expected_metadata=metadata,
    )
    if not payload_already_present:
        bucket = draft["links"]["bucket"]
        for name in EXPECTED_NAMES:  # The 00-prefixed reader is deliberately uploaded first.
            with (zenodo / name).open("rb") as stream:
                request(
                    authenticated, "PUT", f"{bucket}/{name}", data=stream,
                    headers={"Content-Type": "application/octet-stream"},
                )
    draft = validate_draft(
        request(authenticated, "GET", base, accepted={200}).json(),
        draft_id=args.draft_id,
        version_doi=version_doi,
        expected_metadata=metadata,
    )
    require(draft_matches(draft.get("files", []), expected, zenodo),
            "Final Zenodo draft inventory differs from the validated local stage")

    published = request(authenticated, "POST", draft["links"]["publish"]).json()
    require(published.get("id") == args.draft_id, "Published record ID drifted")
    public_url = f"https://zenodo.org/records/{args.draft_id}"

    anonymous = requests.Session()
    anonymous.trust_env = False
    anonymous.headers.update({"User-Agent": "Codex O013 anonymous readback client"})
    public: dict[str, Any] | None = None
    for attempt in range(8):
        response = anonymous.get(
            f"https://zenodo.org/api/records/{args.draft_id}", timeout=(30, 90)
        )
        if response.status_code == 200:
            public = response.json()
            break
        time.sleep(2 + attempt)
    require(public is not None, "Published Zenodo record did not become anonymously readable")
    require(public.get("doi") == version_doi, "Published DOI drifted")
    require(public.get("conceptdoi") == CONCEPT_DOI,
            "Published record left the existing concept lineage")
    validate_metadata(public.get("metadata"), metadata, public=True)
    public_files = public.get("files")
    require(isinstance(public_files, list), "Published record lacks a file inventory")
    public_names = [item.get("key") for item in public_files]
    require(len(public_names) == len(EXPECTED_NAMES)
            and set(public_names) == set(EXPECTED_NAMES),
            f"Published file inventory drifted: {public_names}")
    # Zenodo's public API does not promise presentation order for its files
    # array.  The unique 00- prefix is the deterministic reader-first contract.
    require(sorted(public_names)[0] == READER_NAME,
            "Primary visible public filename is not the reader")

    readback: list[dict[str, object]] = []
    for item in public_files:
        name = item["key"]
        total, checksum = stream_sha256(anonymous, item["links"]["self"])
        require(total == expected[name]["bytes"] and checksum == expected[name]["sha256"],
                f"Anonymous public-byte mismatch for {name}")
        readback.append({
            "name": name,
            "bytes": total,
            "sha256": checksum,
            "file_id": item.get("id"),
        })

    receipt = args.receipt.resolve() if args.receipt.is_absolute() else (ROOT / args.receipt).resolve()
    try:
        receipt.relative_to(ROOT)
    except ValueError:
        fail(f"Receipt must remain inside the edition repository: {receipt}")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zenodo publication receipt — version 0.7.0",
        "",
        f"Date: {PUBLICATION_DATE}",
        f"Record: `{public_url}`",
        f"Version DOI: `{version_doi}`",
        f"Concept DOI: `{CONCEPT_DOI}`",
        f"Edition release commit: `{manifest['authority']['edition_receipt_commit']}`",
        f"Checkpoint content commit: `{manifest['authority']['checkpoint_content_commit']}`",
        "",
        "The existing concept lineage was updated; no competing concept was created.",
        "The unchanged work title and Wen-Wei Li creator credit were preserved. Metadata records the exact partial Unit 001-043 scope, independent/non-endorsed relationship, exact model provenance, and five-component rights boundary.",
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
    lines.extend([
        "",
        f"All {len(readback)} public files ({total_bytes:,} bytes) were downloaded without credentials and matched local byte counts and SHA-256 hashes. Result: **PASS**.",
        "Rights: principal text/adaptation CC BY 4.0; Lanzhou.png CC BY-SA 3.0; credited AJbook.cls fragment CC BY-SA 3.0; Noto fonts OFL 1.1; Fandol 0.3 fonts GPLv3 with the Fandol font exception.",
        f"Model provenance: `{MODEL}`. Signed: `Codex, on instructions of the user.`",
    ])
    receipt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "record_id": args.draft_id,
        "public_url": public_url,
        "doi": version_doi,
        "concept_doi": CONCEPT_DOI,
        "files": readback,
        "total_bytes": total_bytes,
        "anonymous_public_api": True,
        "anonymous_file_readback": True,
        "receipt": str(receipt),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
