#!/usr/bin/env python3
"""Publish and anonymously verify the complete O013 aggregate on Zenodo.

The default mode validates the deterministic local staging directory only.
Network mutation and credential access require ``--publish``.  The publisher
deduplicates both public records and authenticated drafts before creating a
single new aggregate concept; it never extends the Li-only concept.
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

import requests


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "publication" / "o013-aggregate-1.0.0"
TOKEN_PATH = Path(r"C:\Users\Floris\Documents\Obsidian notes\New zenodo token.md")
TITLE = "Aljabar Pascasarjana: Paket Pembelajaran Bahasa Indonesia (O013)"
VERSION = "1.0.0"
PUBLICATION_DATE = "2026-08-29"
LI_VERSION_DOI = "10.5281/zenodo.22151447"
LI_CONCEPT_DOI = "10.5281/zenodo.22059759"
CONTENT_COMMIT = "91b76d0381aa0d4c6614ad6556fe779fe8039f93"
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
EXPECTED_NAMES = (
    "01_metode-aljabar-jilid-1-id-lengkap.pdf",
    "02_catatan-teori-representasi-duncan-id.pdf",
    "03_pilihan-aljabar-komutatif-cring-id.pdf",
    "04_o013-rute-pembelajar-dan-penguasaan-id.pdf",
    "05_o013-sumber-backend-1.0.0.zip",
    "LICENSES.md",
    "o013-aggregate-manifest.schema.json",
    "o013-aggregate-manifest.json",
    "SHA256SUMS.txt",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def md5_file(path: Path) -> str:
    value = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def normalize_md5(value: object) -> str:
    return str(value or "").lower().removeprefix("md5:")


def read_sums(stage: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in (stage / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        digest, name = raw.split("  ", 1)
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                f"Malformed checksum for {name}")
        require(name not in result, f"Duplicate checksum entry: {name}")
        result[name] = digest
    return result


def validate_stage(stage: Path) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    require(stage == STAGE.resolve(), f"Unexpected staging directory: {stage}")
    require(stage.is_dir(), f"Missing staging directory: {stage}")
    names = tuple(sorted(item.name for item in stage.iterdir() if item.is_file()))
    require(set(names) == set(EXPECTED_NAMES),
            f"Staging inventory drifted: {names}")
    require(not any(item.is_dir() for item in stage.iterdir()),
            "Staging directory contains a nested directory")
    sums = read_sums(stage)
    require(set(sums) == set(EXPECTED_NAMES) - {"SHA256SUMS.txt"},
            "SHA256SUMS inventory drifted")
    expected: dict[str, dict[str, object]] = {}
    for name in EXPECTED_NAMES:
        path = stage / name
        digest = sha256_file(path)
        if name != "SHA256SUMS.txt":
            require(digest == sums[name], f"SHA-256 mismatch for {name}")
        expected[name] = {
            "name": name,
            "bytes": path.stat().st_size,
            "sha256": digest,
            "md5": md5_file(path),
        }
    require(sum(int(row["bytes"]) for row in expected.values()) <= 500_000_000,
            "Release exceeds the 500,000,000-byte cap")
    manifest = json.loads((stage / "o013-aggregate-manifest.json").read_text(encoding="utf-8"))
    require(manifest["release"]["title"] == TITLE, "Manifest title drifted")
    require(manifest["release"]["version"] == VERSION, "Manifest version drifted")
    require(manifest["release"]["status"] == "complete", "Manifest is not complete")
    require(manifest["release"]["total_reader_pages"] == 716,
            "Manifest reader-page total drifted")
    require(manifest["production_provenance"]["model"] == MODEL,
            "Manifest model provenance drifted")
    require(manifest["aggregate_rights"]["spdx_expression"] == "NOASSERTION",
            "Manifest flattened the component rights")
    return manifest, expected


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
    for attempt in range(5):
        try:
            response = session.request(method, url, timeout=(30, 300), **kwargs)
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))
            continue
        last = response
        if response.status_code in accepted:
            return response
        if response.status_code in {429, 502, 503, 504} and attempt < 4:
            time.sleep(3 * (attempt + 1))
            continue
        detail = response.content[:500].decode("utf-8", "replace")
        raise RuntimeError(f"Zenodo {method} {url} -> HTTP {response.status_code}: {detail}")
    detail = last.content[:500].decode("utf-8", "replace") if last else "no response"
    raise RuntimeError(f"Zenodo request exhausted retries: {detail}")


def description() -> str:
    return (
        "<p>Paket pembelajaran aljabar pascasarjana Bahasa Indonesia yang lengkap "
        "untuk peran kurikulum O013. Paket ini memuat empat pembaca, total 716 halaman: "
        "edisi lengkap <em>Methods in Algebra, Volume 1</em> karya Wen-Wei Li; edisi "
        "lengkap tujuh akar TeX catatan teori representasi berlisensi karya Alexander "
        "Duncan; enam pilihan tepat dari <em>CRing Project</em>; serta lapisan rute, "
        "diagnostik, dan penguasaan yang diprovenanskan terpisah.</p>"
        "<p>Berkas ditata dengan pembaca PDF utama lebih dahulu. Arsip ringkas "
        "menyertakan sumber, skrip build, backend ID stabil dan proyeksi mesin yang "
        "diperlukan untuk melanjutkan komponen Duncan, CRing, dan lapisan orisinal. "
        "Sumber serta backend Li lengkap dipertahankan pada DOI komponen yang ditautkan.</p>"
        f"<p>Provenance produksi: {html.escape(MODEL)}. Keterangan ini terpisah dari "
        "kepengarangan sumber dan tidak menggantikan kredit penulis atau kontributor "
        "manusia.</p>"
        "<p>Hak tidak diratakan. Edisi Li lengkap dan adaptasinya menggunakan CC BY "
        "4.0, dengan komponen terpisah CC BY-SA 3.0, OFL 1.1, dan GPLv3 dengan "
        "pengecualian font sebagaimana dirinci dalam LICENSES.md. Tujuh akar TeX "
        "Duncan dan terjemahannya menggunakan CC BY 4.0; enam lembar tugas situs "
        "penulis, 49 soal, dan solusi parsial tidak disertakan. Hanya enam pilihan "
        "CRing yang disertakan sebagai komponen termodifikasi menurut GFDL 1.2-or-"
        "later, tanpa Bagian Invarian atau Teks Sampul; ini bukan terjemahan seluruh "
        "CRing Project. Lapisan rute dan penguasaan orisinal menggunakan CC BY 4.0 "
        "dan diprovenanskan terpisah.</p>"
        "<p>Paket ini merupakan turunan dan integrasi independen. Nama para penulis, "
        "kontributor, institusi, dan proyek sumber dipakai untuk atribusi; tidak ada "
        "afiliasi, persetujuan, dukungan, atau pengesahan yang dinyatakan maupun "
        "disiratkan.</p>"
    )


def metadata(draft_id: int, version_doi: str) -> dict[str, Any]:
    prose = description()
    notes = (
        "Status: lengkap untuk paket empat komponen O013, total 716 halaman pembaca. "
        "Li Volume 1 lengkap; tujuh akar TeX Duncan lengkap dalam batas repositori "
        "berlisensi; tepat enam pilihan CRing; dan lapisan rute/penguasaan orisinal. "
        "LICENSES.md dan manifest mengendalikan batas hak, cakupan, atribusi, dan "
        "provenance setiap komponen."
    )
    contributors = [{"name": "TTP", "type": "ProjectMember"}]
    result: dict[str, Any] = {
        "title": TITLE,
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": PUBLICATION_DATE,
        "version": VERSION,
        "language": "ind",
        "access_right": "open",
        "license": "other-open",
        "imprint_publisher": "Zenodo",
        "description": prose,
        "notes": notes,
        "creators": [
            {"name": "Li, Wen-Wei"},
            {"name": "Duncan, Alexander"},
            {"name": "CRing Project"},
        ],
        "contributors": contributors,
        "keywords": [
            "aljabar pascasarjana", "teori representasi", "aljabar komutatif",
            "teori Galois", "teori kategori", "Bahasa Indonesia",
            "buku teks terbuka", "graduate algebra", "matematika", "O013",
        ],
        "related_identifiers": [
            {
                "identifier": "https://github.com/wenweili/AlJabr-1/commit/"
                "c4f7a01f68f5f407906b4b970640cddbbad85f6b",
                "relation": "isDerivedFrom", "scheme": "url",
            },
            {"identifier": "978-7-04-050725-6", "relation": "isDerivedFrom", "scheme": "isbn"},
            {
                "identifier": "https://github.com/vtorsor/representation-theory-notes/commit/"
                "c62d36f41189da4bd3da4671668f68720df54ff7",
                "relation": "isDerivedFrom", "scheme": "url",
            },
            {
                "identifier": "https://math.uchicago.edu/~amathew/CRing.zip",
                "relation": "isDerivedFrom", "scheme": "url",
            },
            {"identifier": LI_VERSION_DOI, "relation": "hasPart", "scheme": "doi"},
            {
                "identifier": "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/"
                f"{CONTENT_COMMIT}",
                "relation": "isSupplementTo", "scheme": "url",
            },
        ],
        "prereserve_doi": {"doi": version_doi, "recid": draft_id},
    }
    org = contributors[0]["name"]
    require(org not in TITLE and org not in prose and org not in notes,
            "Organization label leaked into title or prose metadata")
    require(sum(item.get("name") == org for item in result["creators"] + contributors) == 1,
            "Organization contributor must occur exactly once")
    return result


def exact_public_hits(session: requests.Session) -> list[dict[str, Any]]:
    response = request(
        session,
        "GET",
        "https://zenodo.org/api/records/",
        accepted={200},
        params={"q": f'metadata.title:"{TITLE}"', "all_versions": "true", "size": 25},
    )
    hits = response.json().get("hits", {}).get("hits", [])
    return [item for item in hits if item.get("metadata", {}).get("title") == TITLE]


def exact_drafts(session: requests.Session) -> list[dict[str, Any]]:
    response = request(
        session,
        "GET",
        "https://zenodo.org/api/deposit/depositions",
        accepted={200},
        params={
            "q": f'metadata.title:"{TITLE}"',
            "status": "draft", "all_versions": "true", "size": 100,
        },
    )
    data = response.json()
    require(isinstance(data, list), "Authenticated draft search did not return a list")
    return [item for item in data if item.get("metadata", {}).get("title") == TITLE]


def validate_draft(draft: dict[str, Any]) -> tuple[int, str]:
    require(not draft.get("submitted") and draft.get("state") == "unsubmitted",
            "Target is not an unsubmitted draft")
    draft_id = int(draft["id"])
    reserved = draft.get("metadata", {}).get("prereserve_doi")
    require(isinstance(reserved, dict), "Draft lacks a reserved DOI")
    version_doi = str(reserved.get("doi", ""))
    require(version_doi == f"10.5281/zenodo.{draft_id}", "Reserved DOI drifted")
    return draft_id, version_doi


def draft_inventory_matches(
    draft: dict[str, Any], expected: dict[str, dict[str, object]]
) -> bool:
    files = draft.get("files", [])
    if not isinstance(files, list) or len(files) != len(EXPECTED_NAMES):
        return False
    by_name = {item.get("filename"): item for item in files}
    if set(by_name) != set(EXPECTED_NAMES):
        return False
    return all(
        int(by_name[name].get("filesize", -1)) == int(expected[name]["bytes"])
        and normalize_md5(by_name[name].get("checksum")) == expected[name]["md5"]
        for name in EXPECTED_NAMES
    )


def delete_draft_files(session: requests.Session, draft: dict[str, Any]) -> None:
    for item in draft.get("files", []):
        response = session.delete(item["links"]["self"], timeout=(30, 120))
        require(response.status_code in {200, 202, 204, 404},
                f"Could not delete inherited draft file {item.get('filename')}: HTTP {response.status_code}")


def stream_sha256(session: requests.Session, url: str) -> tuple[int, str]:
    response = request(session, "GET", url, accepted={200}, stream=True)
    total = 0
    digest = hashlib.sha256()
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def people(value: object) -> list[tuple[str, str]]:
    require(isinstance(value, list), "People metadata must be a list")
    require(all(isinstance(item, dict) for item in value),
            "People metadata contains a non-object")
    return [(str(item.get("name", "")), str(item.get("type", ""))) for item in value]


def write_receipts(
    public: dict[str, Any], readback: list[dict[str, object]], concept_doi: str
) -> tuple[Path, Path]:
    version_doi = str(public["doi"])
    record_id = int(public["id"])
    receipt = ROOT / "qa" / "PUBLICATION_ZENODO_O013_AGGREGATE_1.0.0_20260829.md"
    metadata_path = ROOT / "qa" / "ZENODO_O013_AGGREGATE_1.0.0_METADATA_READBACK_20260829.json"
    lines = [
        "# Zenodo publication receipt — O013 aggregate 1.0.0",
        "",
        f"Date: {PUBLICATION_DATE}",
        f"Record: `https://zenodo.org/records/{record_id}`",
        f"Version DOI: `{version_doi}`",
        f"Concept DOI: `{concept_doi}`",
        f"GitHub content commit: `{CONTENT_COMMIT}`",
        "",
        "One new aggregate concept was published after exact-title public and authenticated-draft deduplication. The existing Li-only concept was not renamed or extended.",
        "",
        "## Published and anonymously verified files",
        "",
        "| File ID | File | Bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for row in readback:
        lines.append(
            f"| {row['file_id']} | `{row['name']}` | {int(row['bytes']):,} | `{row['sha256']}` |"
        )
    total = sum(int(row["bytes"]) for row in readback)
    lines.extend([
        "",
        f"All {len(readback)} public files ({total:,} bytes) were downloaded without credentials and matched local byte counts and SHA-256 hashes. Result: **PASS**.",
        "Record-level license: `other-open`; `LICENSES.md` and the manifest preserve the separate Li, Duncan, CRing, original-material, embedded-source, image, and font rights.",
        f"Model provenance: `{MODEL}`. Signed: `Codex, on instructions of the user.`",
    ])
    receipt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    sanitized = {
        "schema": "o013.zenodo-aggregate-public-readback.v1",
        "result": "PASS",
        "record_id": record_id,
        "public_url": f"https://zenodo.org/records/{record_id}",
        "doi": version_doi,
        "concept_doi": concept_doi,
        "li_component_doi": LI_VERSION_DOI,
        "github_content_commit": CONTENT_COMMIT,
        "public_access": True,
        "anonymous_api_readback": True,
        "anonymous_full_file_readback": True,
        "file_count": len(readback),
        "total_bytes": total,
        "files": readback,
        "metadata": public.get("metadata", {}),
    }
    metadata_path.write_text(
        json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    return receipt, metadata_path


def verify_public_record(
    public: dict[str, Any],
    anonymous: requests.Session,
    expected: dict[str, dict[str, object]],
) -> dict[str, Any]:
    draft_id = int(public["id"])
    version_doi = str(public.get("doi", ""))
    require(version_doi == f"10.5281/zenodo.{draft_id}", "Public DOI drifted")
    concept_doi = str(public.get("conceptdoi", ""))
    require(concept_doi and concept_doi != LI_CONCEPT_DOI,
            "Aggregate public record collided with the Li-only concept")
    expected_metadata = metadata(draft_id, version_doi)
    public_metadata = public.get("metadata", {})
    require(public_metadata.get("title") == TITLE, "Public title drifted")
    require(public_metadata.get("access_right") == "open", "Public access is not open")
    require(public_metadata.get("version") == VERSION, "Public version drifted")
    require(public_metadata.get("language") == "ind", "Public language drifted")
    require(public_metadata.get("license", {}).get("id") == "other-open",
            "Public record-level license drifted")
    require(people(public_metadata.get("creators")) == people(expected_metadata["creators"]),
            "Public creator metadata drifted")
    require(people(public_metadata.get("contributors")) == people(expected_metadata["contributors"]),
            "Public contributor metadata drifted")

    public_files = public.get("files", [])
    require(isinstance(public_files, list), "Public record lacks a file inventory")
    by_name = {item.get("key"): item for item in public_files}
    require(set(by_name) == set(EXPECTED_NAMES), "Public file inventory drifted")
    require(sorted(by_name)[0] == EXPECTED_NAMES[0],
            "Primary visible filename is not the Li reader")
    readback: list[dict[str, object]] = []
    for name in EXPECTED_NAMES:
        item = by_name[name]
        total, digest = stream_sha256(anonymous, item["links"]["self"])
        require(total == expected[name]["bytes"] and digest == expected[name]["sha256"],
                f"Anonymous public-byte mismatch for {name}")
        readback.append({
            "name": name,
            "bytes": total,
            "sha256": digest,
            "file_id": item.get("id"),
        })
    receipt, metadata_path = write_receipts(public, readback, concept_doi)
    return {
        "record_id": draft_id,
        "public_url": f"https://zenodo.org/records/{draft_id}",
        "doi": version_doi,
        "concept_doi": concept_doi,
        "files": len(readback),
        "total_bytes": sum(int(row["bytes"]) for row in readback),
        "anonymous_api_readback": True,
        "anonymous_full_file_readback": True,
        "receipt": str(receipt),
        "metadata_readback": str(metadata_path),
    }


def publish(stage: Path, expected: dict[str, dict[str, object]]) -> dict[str, Any]:
    anonymous = requests.Session()
    anonymous.trust_env = False
    anonymous.headers.update({"User-Agent": "Codex O013 aggregate anonymous client"})
    public_hits = exact_public_hits(anonymous)
    require(len(public_hits) <= 1,
            f"Multiple public records with the exact aggregate title exist: {[x.get('id') for x in public_hits]}")
    if public_hits:
        return verify_public_record(public_hits[0], anonymous, expected)

    authenticated = requests.Session()
    authenticated.trust_env = False
    authenticated.headers.update({
        "Authorization": f"Bearer {read_token()}",
        "User-Agent": "Codex O013 aggregate publication client",
    })
    drafts = exact_drafts(authenticated)
    require(len(drafts) <= 1,
            f"Multiple exact-title drafts exist; refusing to create another: {[x.get('id') for x in drafts]}")
    if drafts:
        draft = drafts[0]
    else:
        draft = request(
            authenticated, "POST", "https://zenodo.org/api/deposit/depositions",
            accepted={201}, json={},
        ).json()
    draft_id, version_doi = validate_draft(draft)
    require(str(draft.get("conceptrecid", draft_id)) != LI_CONCEPT_DOI.rsplit(".", 1)[-1],
            "Aggregate draft collided with the Li-only concept")
    base = f"https://zenodo.org/api/deposit/depositions/{draft_id}"

    if not draft_inventory_matches(draft, expected):
        if draft.get("files"):
            delete_draft_files(authenticated, draft)
            draft = request(authenticated, "GET", base, accepted={200}).json()
            require(not draft.get("files"), "Inherited draft files remain after bounded deletion")

    expected_metadata = metadata(draft_id, version_doi)
    draft = request(
        authenticated, "PUT", base, accepted={200}, json={"metadata": expected_metadata},
    ).json()
    validate_draft(draft)
    if not draft_inventory_matches(draft, expected):
        bucket = draft["links"]["bucket"]
        for name in EXPECTED_NAMES:
            with (stage / name).open("rb") as stream:
                request(
                    authenticated, "PUT", f"{bucket}/{name}",
                    data=stream, headers={"Content-Type": "application/octet-stream"},
                )
        draft = request(authenticated, "GET", base, accepted={200}).json()
    require(draft_inventory_matches(draft, expected),
            "Final Zenodo draft inventory differs from the validated local stage")

    published = request(authenticated, "POST", draft["links"]["publish"], accepted={201, 202}).json()
    require(int(published.get("id", -1)) == draft_id, "Published record ID drifted")

    public: dict[str, Any] | None = None
    for attempt in range(10):
        response = anonymous.get(f"https://zenodo.org/api/records/{draft_id}", timeout=(30, 90))
        if response.status_code == 200:
            public = response.json()
            break
        time.sleep(2 + attempt)
    require(public is not None, "Published record did not become anonymously readable")
    require(public.get("doi") == version_doi, "Public DOI drifted")
    return verify_public_record(public, anonymous, expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=Path, default=STAGE)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    stage = args.stage.resolve()
    _manifest, expected = validate_stage(stage)
    summary = {
        "stage": str(stage),
        "title": TITLE,
        "version": VERSION,
        "file_count": len(expected),
        "total_bytes": sum(int(row["bytes"]) for row in expected.values()),
        "local_validation": "PASS",
        "network_mutation": False,
    }
    if args.publish:
        summary.update(publish(stage, expected))
        summary["network_mutation"] = True
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
