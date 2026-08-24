#!/usr/bin/env python3
"""Publish checkpoint 0.5.0 through the existing O013 Zenodo version draft."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
TOKEN_PATH = Path(r"C:\Users\Floris\Documents\Obsidian notes\New zenodo token.md")
MODEL = "OpenAI Codex gpt-5.6-sol, Ultra"
TITLE = "Metode Aljabar, Jilid 1: Arsitektur Dasar — Edisi Bahasa Indonesia"
VERSION = "0.5.0"
PUBLICATION_DATE = "2026-08-24"


def make_description(edition_commit: str) -> str:
    return (
    "<p>Edisi Bahasa Indonesia independen yang sedang berlangsung dari "
    "<em>Methods of Algebra, Volume 1</em> karya Wen-Wei Li. Versi 0.5.0 "
    "memuat checkpoint pembaca 183 halaman dan delapan belas reader mandiri: "
    "pendahuluan lengkap, Bab 1 lengkap, serta Bab 2 lengkap termasuk "
    "latihannya. Bab 3–10, OCW Etingof, asesmennya, dan span CRing terpilih "
    "belum disertakan.</p>"
    "<p>Matematika, latihan, petunjuk, sitasi, rujukan silang, diagram, dan "
    "indeks dipertahankan pada cakupan sumber. Arsip sumber/backend mengikat "
    "setiap unit ke sumber dan target melalui hash, ID stabil lintas bahasa, "
    "hak komponen, dan bukti build/QA. Seluruh 182 halaman unit tetap identik "
    "secara visual setelah dirangkai menjadi checkpoint.</p>"
    f"<p>Provenance produksi: {html.escape(MODEL)}. Keterangan ini terpisah "
    "dari kepengarangan Wen-Wei Li dan tidak menggantikan kredit penulis, "
    "sumber, atau komponen manusia.</p>"
    "<p>Otoritas sumber dibekukan pada commit "
    "<code>c4f7a01f68f5f407906b4b970640cddbbad85f6b</code>, tree "
    "<code>0f9fd52748165ec89a85ba602ccb949a2ce04694</code>, dan PDF resmi "
    "445 halaman dengan SHA-256 "
    "<code>dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38</code>. "
    "Arsip versi ini berasal dari commit edisi "
    f"<code>{html.escape(edition_commit)}</code>.</p>"
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
        raise RuntimeError("No usable Zenodo token found in the local credential note")
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
        raise RuntimeError(
            f"Zenodo {method} {url} -> HTTP {response.status_code}: {detail}"
        )
    detail = last.content[:500].decode("utf-8", "replace") if last else "no response"
    raise RuntimeError(f"Zenodo request exhausted retries: {detail}")


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
            raise RuntimeError(f"Zenodo DELETE {url} -> HTTP {response.status_code}: {detail}")
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Could not confirm deletion of inherited draft file: {url}")


def stream_digest(session: requests.Session, url: str) -> tuple[int, str]:
    response = request(session, "GET", url, accepted={200}, stream=True)
    digest = hashlib.sha256()
    total = 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if chunk:
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--edition-commit", required=True)
    args = parser.parse_args()
    description = make_description(args.edition_commit)

    stage = args.stage.resolve()
    zenodo_dir = stage / "zenodo"
    if not zenodo_dir.is_dir():
        raise SystemExit(f"Missing Zenodo stage directory: {zenodo_dir}")
    files = sorted(zenodo_dir.iterdir())
    expected = {
        path.name: (path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())
        for path in files
    }
    expected_names = [path.name for path in files]
    if not expected_names or not expected_names[0].startswith("00-"):
        raise RuntimeError("Reader-first payload invariant failed")

    authenticated = requests.Session()
    authenticated.trust_env = False
    authenticated.headers.update(
        {
            "Authorization": f"Bearer {read_token()}",
            "User-Agent": "Codex O013 Zenodo publication client",
        }
    )
    base = f"https://zenodo.org/api/deposit/depositions/{args.draft_id}"
    draft = request(authenticated, "GET", base, accepted={200}).json()
    if draft.get("submitted") or draft.get("state") != "unsubmitted":
        raise RuntimeError(f"Expected existing unsubmitted draft, got {draft.get('state')}")
    reserved = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi")
    if reserved != "10.5281/zenodo.22071178":
        raise RuntimeError(f"Unexpected reserved DOI: {reserved}")

    current_sizes = {
        item["filename"]: item["filesize"] for item in draft.get("files", [])
    }
    payload_already_present = (
        set(current_sizes) == set(expected_names)
        and all(current_sizes[name] == expected[name][0] for name in expected_names)
    )
    if not payload_already_present:
        for _round in range(3):
            inherited = draft.get("files", [])
            if not inherited:
                break
            for old in inherited:
                delete_file(authenticated, old["links"]["self"])
            draft = request(authenticated, "GET", base, accepted={200}).json()
        if draft.get("files"):
            raise RuntimeError("Inherited draft inventory remains after bounded deletion")

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
            "fungtor",
            "adjoin",
            "limit",
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
                "identifier": f"https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id/commit/{args.edition_commit}",
                "relation": "isSupplementTo",
                "scheme": "url",
            },
        ],
        "language": "ind",
        "license": "other-open",
        "imprint_publisher": "Zenodo",
        "notes": (
            "Status: parsial publik aktif. Unit 001-018 mencakup pendahuluan, "
            "Bab 1 lengkap, dan Bab 2 lengkap termasuk latihan. Bab 3-10 serta "
            "komponen OCW/CRing belum termasuk. Paket memakai beberapa lisensi "
            "terbuka; 20-LICENSES.md dan RIGHTS_COMPONENTS.csv mengendalikan "
            "ketentuan per komponen."
        ),
        "upload_type": "publication",
        "publication_type": "book",
        "version": VERSION,
        "prereserve_doi": {"doi": "10.5281/zenodo.22071178", "recid": args.draft_id},
    }
    request(authenticated, "PUT", base, json={"metadata": metadata})

    draft = request(authenticated, "GET", base, accepted={200}).json()
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

    draft = request(authenticated, "GET", base, accepted={200}).json()
    draft_files = draft.get("files", [])
    draft_names = [item["filename"] for item in draft_files]
    if set(draft_names) != set(expected_names) or len(draft_names) != len(expected_names):
        raise RuntimeError(f"Unexpected draft inventory: {draft_names}")
    for item in draft_files:
        if item["filesize"] != expected[item["filename"]][0]:
            raise RuntimeError(f"Draft size mismatch for {item['filename']}")

    published = request(authenticated, "POST", draft["links"]["publish"]).json()
    record_id = published["id"]
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
    if public_response is None:
        raise RuntimeError("Published Zenodo record did not become anonymously readable")
    public = public_response.json()

    public_files = public.get("files", [])
    public_names = [item["key"] for item in public_files]
    if set(public_names) != set(expected_names) or len(public_names) != len(expected_names):
        raise RuntimeError(f"Published inventory differs: {public_names}")
    public_metadata = public.get("metadata", {})
    if public_metadata.get("title") != TITLE or public_metadata.get("version") != VERSION:
        raise RuntimeError("Published title/version metadata differs")
    combined_people = public_metadata.get("creators", []) + public_metadata.get("contributors", [])
    organization_count = sum(item.get("name") == "TTP" for item in combined_people)
    if organization_count != 1 or "TTP" in public_metadata.get("description", ""):
        raise RuntimeError("Organization metadata occurrence invariant failed")

    readback: list[dict[str, object]] = []
    for item in public_files:
        total, checksum = stream_digest(anonymous, item["links"]["self"])
        expected_bytes, expected_sha = expected[item["key"]]
        if (total, checksum) != (expected_bytes, expected_sha):
            raise RuntimeError(f"Public-byte mismatch for {item['key']}: {total}/{checksum}")
        readback.append(
            {
                "name": item["key"],
                "bytes": total,
                "sha256": checksum,
                "file_id": item["id"],
            }
        )

    receipt_path = (ROOT / args.receipt).resolve() if not args.receipt.is_absolute() else args.receipt.resolve()
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zenodo publication receipt — version 0.5.0",
        "",
        f"Date: {PUBLICATION_DATE}",
        f"Record: `{public_url}`",
        f"Version DOI: `{public.get('doi', '10.5281/zenodo.22071178')}`",
        "Concept DOI: `10.5281/zenodo.22059759`",
        f"Version: `{VERSION}`",
        f"Edition release commit: `{args.edition_commit}`",
        "",
        "The existing concept lineage was updated; no competing concept was created.",
        "The exact work title and Wen-Wei Li creator credit are preserved. The single organization contributor entry is separate from the title and description lead. Metadata states the partial Unit 001-018 scope, exact model provenance, independent/non-endorsed relationship, and mixed component-rights boundary.",
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
                "doi": public.get("doi"),
                "concept_doi": public.get("conceptdoi"),
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
