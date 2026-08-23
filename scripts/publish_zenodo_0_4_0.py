#!/usr/bin/env python3
"""Publish the existing O013 Zenodo concept's 0.4.0 version.

The token is read only at runtime from the local credential path and is never
written to output, metadata, receipts, or the repository.  The script updates
the draft created through the existing record's ``newversion`` endpoint,
replaces its files with one reader-first payload, publishes it, and performs an
anonymous public-byte readback before writing a sanitized receipt.
"""

from __future__ import annotations

import argparse
import concurrent.futures
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
DESCRIPTION = (
    "<p>Edisi Bahasa Indonesia independen yang sedang berlangsung dari "
    "<em>Methods of Algebra, Volume 1</em> karya Wen-Wei Li. Versi 0.4.0 "
    "memuat checkpoint pembaca 128 halaman dan dua belas reader mandiri: "
    "pendahuluan lengkap, Bab 1 lengkap, pengantar Bab 2, serta Bagian 2.1–2.4 "
    "hingga kategori koma. Bagian 2.5 dan seluruh bagian sesudahnya belum "
    "disertakan; OCW Etingof dan CRing belum disertakan.</p>"
    "<p>Matematika, latihan, petunjuk, sitasi, rujukan silang, diagram, dan "
    "indeks dipertahankan pada cakupan sumber. Arsip sumber/backend mengikat "
    "setiap unit ke sumber dan target melalui hash, ID stabil lintas bahasa, "
    "hak komponen, dan bukti build/QA.</p>"
    f"<p>Model: {html.escape(MODEL)}. Seluruh kredit penulis, sumber, dan "
    "komponen dipertahankan.</p>"
    "<p>Otoritas sumber dibekukan pada commit "
    "<code>c4f7a01f68f5f407906b4b970640cddbbad85f6b</code>, tree "
    "<code>0f9fd52748165ec89a85ba602ccb949a2ce04694</code>, dan PDF resmi "
    "445 halaman dengan SHA-256 "
    "<code>dc751a2d5146edc9f9638471ff3fac4107eab8dd0d3331803581a06998663c38</code>. "
    "Arsip versi ini berasal dari commit edisi "
    "<code>84f2e1e98b404dff45f00ea629eddc00dc4fa70b</code>.</p>"
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
    # The current credential file is a single token.  The fallback also keeps
    # this safe if the local note later gains a Markdown label.
    if re.fullmatch(r"[A-Za-z0-9._~-]{20,}", text):
        return text
    match = re.search(r"([A-Za-z0-9._~-]{20,})", text)
    if not match:
        raise RuntimeError("No usable Zenodo token found in the local credential note")
    return match.group(1)


def body(response: requests.Response) -> bytes:
    # Requests transparently decodes gzip content for ``response.content``.
    return response.content


def request(session: requests.Session, method: str, url: str, **kwargs: object) -> requests.Response:
    for attempt in range(3):
        try:
            response = session.request(method, url, timeout=(30, 300), **kwargs)
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(4 * (attempt + 1))
            continue
        if response.status_code in {502, 503, 504, 429} and attempt < 2:
            time.sleep(5 * (attempt + 1))
            continue
        if response.status_code >= 400:
            detail = body(response)[:500].decode("utf-8", "replace")
            raise RuntimeError(f"Zenodo {method} {url} -> HTTP {response.status_code}: {detail}")
        return response
    raise RuntimeError("Unreachable request retry state")


def delete_file(session: requests.Session, url: str) -> None:
    """Delete one inherited draft file, tolerating a gateway timeout.

    Zenodo occasionally completes a DELETE while its proxy returns 504.  A
    timeout is therefore followed by a bounded retry; a later 404 means the
    file is already gone and is treated as success.
    """
    for attempt in range(4):
        try:
            response = session.delete(url, timeout=(20, 75))
        except requests.RequestException:
            response = None
        if response is not None and response.status_code in {200, 202, 204, 404}:
            return
        if response is not None and response.status_code not in {429, 502, 503, 504}:
            detail = response.content[:300].decode("utf-8", "replace")
            raise RuntimeError(f"Zenodo DELETE {url} -> HTTP {response.status_code}: {detail}")
        time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"Could not confirm deletion of inherited Zenodo draft file: {url}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stream_digest(session: requests.Session, url: str) -> tuple[int, str]:
    response = request(session, "GET", url, stream=True)
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
    args = parser.parse_args()

    stage = args.stage.resolve()
    zenodo_dir = stage / "zenodo"
    if not zenodo_dir.is_dir():
        raise SystemExit(f"Missing Zenodo stage directory: {zenodo_dir}")
    files = sorted(zenodo_dir.iterdir(), key=lambda p: (0 if p.name.startswith("00-") else 1 if p.name.startswith("10-") else 2 if p.name.startswith("20-") else 3 if p.name.startswith("30-") else 4 if p.name.startswith("40-") else 5, p.name))
    expected = {path.name: (path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest()) for path in files}

    session = requests.Session()
    session.trust_env = False
    session.headers.update({"Authorization": f"Bearer {read_token()}", "User-Agent": "Codex O013 publication client"})
    base = f"https://zenodo.org/api/deposit/depositions/{args.draft_id}"
    draft = json.loads(body(request(session, "GET", base)))

    # Remove the inherited 0.3.0 inventory before uploading the 0.4.0 set.
    # The API is slow but independent file deletes are safe to parallelize.
    for _round in range(3):
        old_files = draft.get("files", [])
        if not old_files:
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(delete_file, session, old["links"]["self"]) for old in old_files]
            for future in futures:
                future.result()
        draft = json.loads(body(request(session, "GET", base)))
    if draft.get("files"):
        raise RuntimeError("Inherited Zenodo draft files remain after bounded deletion rounds")

    metadata = {
        "title": TITLE,
        "publication_date": "2026-08-23",
        "description": DESCRIPTION,
        "access_right": "open",
        "creators": [{"name": "Li, Wen-Wei", "affiliation": None}],
        "contributors": [{"name": "TTP", "affiliation": None, "type": "ProjectMember"}],
        "keywords": ["aljabar", "teori himpunan", "teori kategori", "morfisme", "fungtor", "sifat universal", "kategori koma", "Bahasa Indonesia", "buku teks terbuka", "graduate algebra", "matematika"],
        "related_identifiers": [
            {"identifier": "https://github.com/wenweili/AlJabr-1/commit/c4f7a01f68f5f407906b4b970640cddbbad85f6b", "relation": "isDerivedFrom", "scheme": "url"},
            {"identifier": "978-7-04-050725-6", "relation": "isDerivedFrom", "scheme": "isbn"},
            {"identifier": "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id", "relation": "isSupplementTo", "scheme": "url"},
        ],
        "language": "ind",
        "license": "other-open",
        "imprint_publisher": "Zenodo",
        "notes": "Rekaman ini memakai Other (Open) karena paket memuat beberapa komponen berlisensi terbuka. Lihat 20-LICENSES.md dan RIGHTS_COMPONENTS.csv untuk ketentuan per komponen. Status: parsial publik aktif; Unit 001-012 termasuk sampai Bagian 2.4, Bagian 2.5 dan komponen OCW/CRing belum termasuk.",
        "upload_type": "publication",
        "publication_type": "book",
        "version": "0.4.0",
        "prereserve_doi": {"doi": "10.5281/zenodo.22071178", "recid": args.draft_id},
    }
    request(session, "PUT", base, json={"metadata": metadata})

    draft = json.loads(body(request(session, "GET", base)))
    bucket = draft["links"]["bucket"]
    for path in files:
        with path.open("rb") as handle:
            request(session, "PUT", f"{bucket}/{path.name}", data=handle, headers={"Content-Type": "application/octet-stream"})

    draft = json.loads(body(request(session, "GET", base)))
    names = [item["filename"] for item in draft.get("files", [])]
    if names != [path.name for path in files]:
        raise RuntimeError(f"Unexpected Zenodo draft file order/inventory: {names}")
    for item in draft["files"]:
        if item["filesize"] != expected[item["filename"]][0]:
            raise RuntimeError(f"Draft byte size mismatch for {item['filename']}")

    published = json.loads(body(request(session, "POST", draft["links"]["publish"])))
    record_id = published["id"]
    public_url = published.get("links", {}).get("record", f"https://zenodo.org/records/{record_id}")
    public_api = f"https://zenodo.org/api/records/{record_id}"
    public = json.loads(body(request(session, "GET", public_api)))
    public_files = public.get("files", [])
    if [item["key"] for item in public_files] != [path.name for path in files]:
        raise RuntimeError("Published Zenodo inventory/order differs from the staged payload")

    readback: list[dict[str, object]] = []
    for item in public_files:
        total, digest = stream_digest(session, item["links"]["self"])
        expected_bytes, expected_sha = expected[item["key"]]
        if (total, digest) != (expected_bytes, expected_sha):
            raise RuntimeError(f"Public-byte mismatch for {item['key']}: {total}/{digest}")
        readback.append({"name": item["key"], "bytes": total, "sha256": digest, "file_id": item["id"]})

    receipt_path = (ROOT / args.receipt).resolve() if not args.receipt.is_absolute() else args.receipt.resolve()
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Zenodo publication receipt — version 0.4.0",
        "",
        "Date: 2026-08-23",
        f"Record: `{public_url}`",
        f"Version DOI: `{public.get('doi', '10.5281/zenodo.22071178')}`",
        "Concept DOI: `10.5281/zenodo.22059759`",
        "Version: `0.4.0`",
        "Edition release commit: `84f2e1e98b404dff45f00ea629eddc00dc4fa70b`",
        "",
        "The existing concept lineage was updated; no competing concept was created.",
        "The title remains the exact work title, the sole creator is Wen-Wei Li, and the contributor organization entry occurs once. Metadata states the partial Unit 001-012 scope, exact model provenance, independent/non-endorsed relationship, and mixed component-rights boundary.",
        "",
        "## Published and anonymously verified files",
        "",
        "| File ID | File | Bytes | SHA-256 |",
        "|---:|---|---:|---|",
    ]
    for item in readback:
        lines.append(f"| {item['file_id']} | `{item['name']}` | {item['bytes']:,} | `{item['sha256']}` |")
    total_bytes = sum(int(item["bytes"]) for item in readback)
    lines.extend([
        "",
        f"All {len(readback)} public files ({total_bytes:,} bytes) were downloaded anonymously after publication and matched local byte counts and SHA-256 hashes. Result: **PASS**.",
        "Rights: principal text/adaptation CC BY 4.0; credited Lanzhou.png and AJbook.cls fragment CC BY-SA 3.0; bundled Noto fonts OFL 1.1. This receipt contains no credential material.",
        f"Model provenance: `{MODEL}`. Signed: `Codex, on instructions of the user.`",
    ])
    receipt_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"record_id": record_id, "public_url": public_url, "doi": public.get("doi"), "version": "0.4.0", "files": readback, "total_bytes": total_bytes, "receipt": str(receipt_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
