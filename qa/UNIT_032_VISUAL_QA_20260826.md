# Unit 032 visual and PDF QA — 2026-08-26

Status: **PASS WITH WARNINGS**. Exact identity, two-engine decoded-pixel,
metadata, navigation, font, extraction, action/link, geometry, diagnostics,
and all-page visual gates pass. No actionable defect remains.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `build/unit-032-final-k/unit-032-bab-4-grup-bebas.pdf` | 149,636 | `c7f06f1579bfd0abfc70a8af7a2fdf6b39fc10ef37bc2a951b8f38f47373151f` |
| `build/unit-032-final-l/unit-032-bab-4-grup-bebas.pdf` | 149,624 | `904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf` |
| `artifacts/unit-032-bab-4-grup-bebas-id.pdf` | 149,624 | `904330916e20f0782b6464cb85e07001851940f4adf153f6592cd34087dbadbf` |

Build J and the artifact are byte-identical; all three PDFs contain 13 pages.

## Rendering gate

Poppler and MuPDF rendered all PDFs at 144 dpi (998 x 1418 pixels per page).
Equality is based on decoded RGB pixels.

- poppler build-i vs build-j: all 13 decoded-RGB pages are identical.
- poppler build-j vs artifact: all 13 decoded-RGB pages are identical.
- mupdf build-i vs build-j: all 13 decoded-RGB pages are identical.
- mupdf build-j vs artifact: all 13 decoded-RGB pages are identical.

All 78 renders have zero ink in the outer three-pixel band.

| Page | Poppler decoded-RGB SHA-256 | MuPDF decoded-RGB SHA-256 |
|---:|---|---|
| 1 | `fd29311d9c36a6c6c13b1676858d4363ff74eff88470c692b24f04b1894966c6` | `7784a090d1bc4f5198df356bd6da317e35f07a56055805ba604b670c6a26d382` |
| 2 | `8af8dc5fdd628474721095624e4269b82275a8a09d7bb36462a69aec49588c8c` | `4849122d8ffc1142033d4b979ab02f346be0edd14160059b9db948eb7e49a43e` |
| 3 | `6ccbe7f065919e8f332422a9ca6f805769fe91f560abbbf52bb056a368420b62` | `c1fd92289411884d2ec42f89e7747d0522dff1d77974e9ca6058502b52f7032e` |
| 4 | `ad58c486f771654f28137506727e192b00d3ccaa591a806b0a69262a2037c92c` | `7e2c72c327b1ed080d7d0b92906d74300a6782279849f816fdaf2680b51f7fd1` |
| 5 | `28a4ad9704a3eca98ab0bb2176455945ccd83a8c6ff3468991c42e9e3e7a5404` | `c090e9a23fc6de22d457043ef03ab8871c8df09c3655db4921d2431d7be3af64` |
| 6 | `f39ba05a87340950f9651427234bd35e781e359d3d0facffb4d62be0b1e85d2b` | `fba21e95297d0fa0dcc65475692ac20ef52614295f2373d190a6efc896bc0490` |
| 7 | `08b5eefd10a5c19e9adccd1817d3d307c5a3aa95b1ba914c4d3e86d270b0fed4` | `d955c655fc3dec35825e7614c692d98faf18274834fa218a3e018c94cdde4169` |
| 8 | `a8ad43e4cc4812e05d85da4b3f3ae43a3217b275cbdd4a237249b3903b614f53` | `7d6d87e7fe009ef992b0e7136333221afb2caf8a5a4cf797aad39819e84b7f40` |
| 9 | `aca60508760d7577cbe2bf258566c91f41506321b386032cb568ecb92eaf7371` | `2e86b45402441c49d3b49f9b4a2f4e222752ac7d0e70e79528a3927db992c90d` |
| 10 | `db94e927552329d588c0759798b3a280c6d779a332bb43d81272098df3ca70e0` | `c9d19a0fa10e8baaff18acb63f11a5e3dbb51f6e86180db91ed2b883d5479e6b` |
| 11 | `fb7a2faac4507b0d6413d32e825436d3174e6c36c5b5e818d73b8d0361495efc` | `3338cb5b70c9ecd29c145b355ae581bfecb89a270d3f08d985d352386cc7cf62` |
| 12 | `ae7fcba651d06836a2801ec1aaf1bae7ccc0db8e8915e6df5cb64347457f6fd7` | `50e92a5fc9afc0cea7c5780601f02aaa7866edf33062577ac279a7a19e9e51d3` |
| 13 | `502370188c39b27a650a05f49edf10189faae117c9f5ac7016a74858f87f5c34` | `4c89c727226c5ba2fd20ef2c1813b1a2404da3338a8c43be06b5b3ab5e3d6cd6` |

## PDF and diagnostic gate

- PDF `%PDF-1.7`; `/Lang id-ID`; unencrypted; exact metadata and outline.
- All 50 named destinations resolve; action inventory is {'/URI': 6, '/GoTo': 30}.
- All 28 font objects are embedded; no active payload or unsafe action is present.
- Final diagnostics are zero for errors, unresolved references/citations, missing characters, empty targets, and overfull boxes. Exactly 3 nonfatal underfull hboxes remain at the three visually inspected source locations; none causes clipping, collision, or impaired reading.

## Full-resolution visual review

Every page was inspected at full readability in both renderer outputs.

| Page | Finding |
|---:|---|
| 1 | Sampul terpusat, utuh, dan terbaca; judul, identitas Unit 32, kotak cakupan, serta tanggal tidak terpotong. |
| 2 | Halaman edisi dan hak utuh; atribusi, lisensi komponen, nonpengesahan, URL, dan provenans model terbaca tanpa tumpang tindih. |
| 3 | Pembuka Bagian 4.8, dua definisi universal, rumus, dan dua diagram komutatif tersusun rapi tanpa kliping atau glif hilang. |
| 4 | Naturalisasi, sifat adjoin, konstruksi kata, dan persamaan tampil dalam bidang halaman yang seimbang dan mudah diikuti. |
| 5 | Lema monoid bebas serta Definisi 4.8.5 dan daftar tiga butir terbaca utuh; underfull pertama hanya ruang daftar nonfatal. |
| 6 | Relasi produk teramalgamasi, Lema 4.8.6, bukti bernomor, dan diagram tampil utuh; underfull kedua tidak menimbulkan tabrakan. |
| 7 | Bentuk tereduksi, persamaan bernomor, Lema 4.8.7, dan awal buktinya terletak dalam margin serta tetap jelas. |
| 8 | Dua aksi pada Sigma, penutup bukti, Proposisi 4.8.8, dan rumus homomorfisme terbaca tanpa luapan atau kehilangan simbol. |
| 9 | Kata tereduksi, produk bebas, dan Definisi 4.8.10 tersusun stabil; diagram kecil dan semua rujukan silang terbaca. |
| 10 | Dua rumus himpunan dukungan hingga telah direflow dengan benar; proposisi, bukti, dan awal presentasi grup tidak melampaui margin. |
| 11 | Presentasi grup, dua contoh, tiga masalah Dehn, dan koreksi nama Guralnick tampil jelas; daftar tetap terjajar dan utuh. |
| 12 | Teorema Nielsen–Schreier, bukti topologis, diagram bouquet, dan paragraf graf terbaca penuh tanpa kliping atau glif rusak. |
| 13 | Penutup bukti, diagram graf, daftar pustaka, dan indeks istilah lengkap; underfull ketiga nonfatal dan ruang akhir halaman wajar. |

The PDF is untagged, so no tagged-accessibility claim is made. Stable
mathematics-font extraction limitations, if any, are recorded in the JSON
evidence. Toolchain advisories are retained exactly as {'latex_release': 3, 'xecjk': 1, 'braids': 1, 'fontspec_cjk': 7}.

Production/review provenance: **OpenAI Codex gpt-5.6-sol, Ultra**. Verdict:
**PASS WITH WARNINGS; zero actionable defects.**
