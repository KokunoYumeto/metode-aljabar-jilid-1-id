#!/usr/bin/env python3
"""Publish and verify Zenodo checkpoint 0.8.0 in the existing concept."""

from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any

import build_release_0_8_0 as release
import publish_zenodo_0_7_0 as base


PUBLICATION_DATE = "2026-08-28"


def description(manifest: dict[str, Any]) -> str:
    authority = manifest["authority"]
    return (
        "<p>Edisi Bahasa Indonesia independen yang sedang berlangsung dari "
        "<em>Methods in Algebra, Volume 1</em> karya Wen-Wei Li. Versi 0.8.0 "
        "memuat pembaca 460 halaman: pendahuluan serta Bab 1 sampai Bab 6 "
        "lengkap dalam 37 komponen pembaca. Bab 7 sampai Bab 10, komponen teori "
        "representasi Duncan, enam span CRing, dan lapisan konektif/penguasaan "
        "belum disertakan.</p>"
        "<p>Paket pembaca dipimpin oleh PDF; arsip ringkas menyertakan sumber "
        "yang dapat dilanjutkan, backend ID stabil, proyeksi CSV, skrip build, "
        "hak komponen, dan bukti deterministik yang relevan.</p>"
        f"<p>Provenance produksi: {html.escape(release.MODEL)}. Keterangan ini "
        "terpisah dari kepengarangan Wen-Wei Li dan tidak menggantikan kredit "
        "penulis, sumber, atau kontributor manusia.</p>"
        "<p>Otoritas sumber dibekukan pada commit "
        f"<code>{html.escape(authority['source_commit'])}</code>, tree "
        f"<code>{html.escape(authority['source_tree'])}</code>, dan PDF resmi "
        f"{authority['official_pdf_pages']} halaman dengan SHA-256 "
        f"<code>{html.escape(authority['official_pdf_sha256'])}</code>. Arsip "
        "versi ini berasal dari commit edisi "
        f"<code>{html.escape(authority['edition_receipt_commit'])}</code>.</p>"
        "<p>Hak tidak diratakan: teks utama/adaptasi CC BY 4.0; Lanzhou.png dan "
        "fragmen AJbook.cls masing-masing CC BY-SA 3.0; font Noto OFL 1.1; "
        "font Fandol 0.3 GPLv3 dengan pengecualian font. 20-LICENSES.md "
        "mengendalikan hak per komponen.</p>"
        "<p>Ini adalah turunan independen, bukan edisi resmi, dan tidak "
        "disahkan oleh penulis atau pihak hulu.</p>"
    )


ORIGINAL_METADATA_FOR = base.metadata_for


def metadata_for(manifest: dict[str, Any], version_doi: str, draft_id: int) -> dict[str, Any]:
    result = ORIGINAL_METADATA_FOR(manifest, version_doi, draft_id)
    result["notes"] = (
        "Status: parsial publik aktif. Unit 001-044 mencakup pendahuluan serta "
        "Bab 1-6 lengkap. Bab 7-10 Li dan komponen Duncan/CRing/konektif-penguasaan "
        "belum termasuk. Paket multi-lisensi; 20-LICENSES.md dan "
        "RIGHTS_COMPONENTS.csv mengendalikan hak setiap komponen."
    )
    if "teori modul" not in result["keywords"]:
        result["keywords"].append("teori modul")
    combined = result["creators"] + result["contributors"]
    release.require(sum(item.get("name") == "TTP" for item in combined) == 1,
                    "metadata must contain exactly one organization contributor")
    release.require("TTP" not in result["title"] and "TTP" not in result["description"] and "TTP" not in result["notes"],
                    "organization label leaked into title or prose")
    return result


def configure() -> None:
    for name, value in {
        "CONCEPT_DOI": release.CONCEPT_DOI,
        "EXPECTED_NAMES": release.EXPECTED_NAMES,
        "LICENSE_NAME": release.LICENSE_NAME,
        "MANIFEST_NAME": release.MANIFEST_NAME,
        "MODEL": release.MODEL,
        "READER_NAME": release.READER_NAME,
        "ROOT": release.ROOT,
        "SUMS_NAME": release.SUMS_NAME,
        "TITLE": release.TITLE,
        "VERSION": release.VERSION,
        "ZIP_NAME": release.ZIP_NAME,
        "PUBLICATION_DATE": PUBLICATION_DATE,
    }.items():
        setattr(base, name, value)
    base.validate_stage = release.validate_stage
    base.description = description
    base.metadata_for = metadata_for


def receipt_from_argv() -> Path | None:
    if "--receipt" not in sys.argv:
        return None
    index = sys.argv.index("--receipt")
    if index + 1 >= len(sys.argv):
        return None
    path = Path(sys.argv[index + 1])
    return path if path.is_absolute() else release.ROOT / path


def normalize_receipt(path: Path | None) -> None:
    if path is None or not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace("version 0.7.0", "version 0.8.0")
    text = text.replace("Unit 001-043 scope", "Unit 001-044 scope")
    text = text.replace("partial Unit 001-043", "partial Unit 001-044")
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    configure()
    receipt = receipt_from_argv()
    base.main()
    normalize_receipt(receipt)


if __name__ == "__main__":
    main()
