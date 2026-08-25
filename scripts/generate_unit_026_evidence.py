#!/usr/bin/env python3
"""Deterministic, bounded PDF evidence generator for O013 Unit 026."""
from __future__ import annotations

import hashlib, json, re, shutil, subprocess, tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pypdf import PdfReader
from pypdf.generic import IndirectObject

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "qa" / "unit-026-evidence"
REPORT = ROOT / "qa" / "UNIT_026_VISUAL_QA_20260825.md"
TMP = ROOT / "tmp" / "pdfs"
DPI, PAGES, SIZE, EDGE = 144, 9, (998, 1418), 3
DOCS = {
    "build-c": (ROOT / "build/unit-026-c-20260825/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.pdf", 115288, "de415fed2c9aceafc41d5e22d2dd6d73e81c37f3a3463af18d73f59409b09dbf"),
    "build-d": (ROOT / "build/unit-026-d-20260825/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi.pdf", 115284, "e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089"),
    "artifact": (ROOT / "artifacts/unit-026-bab-4-homomorfisme-dan-grup-hasil-bagi-id.pdf", 115284, "e3c0e0241901eb0f5f2477a1fe09f64eff34af325dc209b25aa8d71900deb089"),
}
LOG = (ROOT / "qa/UNIT_026_BUILD_FINAL.log", 86417, "f26903ed598b9191005e00dd8f2d55b2de09eb0464722ed5bef24e9f9f93f8fd")
OUTLINE = [("4.2 Homomorfisme dan grup hasil bagi", 3), ("Daftar Pustaka", 9), ("Indeks Istilah", 9), ("Indeks Simbol", 9)]
FINDINGS = [
    "Cover hierarchy, subtitle, scope box, metadata line, and footer are balanced and inside the trim box.",
    "Edition, attribution, licence, provenance, and repository statements wrap cleanly without collision.",
    "Section 4.2, Definition 4.2.1, Proposition 4.2.2, displayed algebra, and coloured rules are intact.",
    "Proof, automorphisms, kernel, quotient structure, and equation (4.1) are aligned and unclipped.",
    "Universal diagram, induced homomorphism, equation (4.2), and quotient-group definition are clean.",
    "Quotient homomorphism, Propositions 4.2.7–4.2.8, and correspondence diagram are intact.",
    "Proposition 4.2.9, cyclic groups, congruence, Proposition 4.2.11, and Grothendieck opening are clean.",
    "Grothendieck continuation/proof, categorical remark, and following paragraph remain within bounds.",
    "Conclusion, bibliography, and indexes are clean; white space is intentional. MuPDF renders 代数学引论; this Poppler installation omits it.",
]

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def bhash(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def rel(path: Path) -> str: return path.resolve().relative_to(ROOT).as_posix()
def obj(x: Any) -> Any: return x.get_object() if isinstance(x, IndirectObject) else x

def clean(text: str) -> str:
    for old, new in ((str(ROOT), "<REPO>"), (str(ROOT).replace("\\", "/"), "<REPO>"),
                     (str(Path.home()), "%USERPROFILE%"), (str(Path.home()).replace("\\", "/"), "%USERPROFILE%")):
        text = text.replace(old, new)
    return text

def run(args: list[str]) -> tuple[str, str]:
    p = subprocess.run(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode: raise RuntimeError(f"{Path(args[0]).name} exit {p.returncode}: {clean(p.stderr)}")
    return clean(p.stdout), clean(p.stderr)

def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

def identities() -> dict[str, Any]:
    result = {}
    for name, (path, size, digest) in DOCS.items():
        got = {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)}
        assert (got["bytes"], got["sha256"]) == (size, digest), (name, got)
        result[name] = got
    path, size, digest = LOG
    got = {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path)}
    assert (got["bytes"], got["sha256"]) == (size, digest), got
    result["build-log"] = got
    assert DOCS["build-d"][0].read_bytes() == DOCS["artifact"][0].read_bytes()
    result["build-d_artifact_byte_identical"] = True
    return result

def render(engine: str, name: str, pdf: Path, work: Path) -> dict[str, Any]:
    temp = work / f"{engine}-{name}"; temp.mkdir()
    target = OUT / "renders" / engine / name; target.mkdir(parents=True)
    if engine == "poppler":
        exe = shutil.which("pdftoppm"); prefix = temp / "p"
        stdout, stderr = run([exe, "-png", "-r", str(DPI), "-f", "1", "-l", str(PAGES), str(pdf), str(prefix)])
        pages = sorted(temp.glob("p-*.png"), key=lambda x: int(x.stem.split("-")[-1]))
    else:
        exe = shutil.which("mutool"); pattern = temp / "p-%02d.png"
        stdout, stderr = run([exe, "draw", "-q", "-r", str(DPI), "-o", str(pattern), str(pdf)])
        pages = sorted(temp.glob("p-*.png"))
    assert len(pages) == PAGES
    records = []
    for number, source in enumerate(pages, 1):
        path = target / f"page-{number:02d}.png"; shutil.copy2(source, path)
        with Image.open(path) as im:
            rgb = im.convert("RGB"); assert rgb.size == SIZE
            px, w, h = rgb.load(), *rgb.size
            coords = {(x, y) for x in range(EDGE) for y in range(h)} | {(w-1-x, y) for x in range(EDGE) for y in range(h)} | {(x, y) for y in range(EDGE) for x in range(w)} | {(x, h-1-y) for y in range(EDGE) for x in range(w)}
            edge_ink = sum(min(px[x, y]) < 250 for x, y in coords)
            dark = ImageChops.darker(ImageChops.darker(rgb.getchannel("R"), rgb.getchannel("G")), rgb.getchannel("B")).point(lambda p: 255 if p < 250 else 0)
            bbox = dark.getbbox()
            records.append({"page": number, "path": rel(path), "png_bytes": path.stat().st_size,
                            "png_sha256": sha(path), "decoded_rgb_sha256": bhash(rgb.tobytes()),
                            "size": list(rgb.size), "outer_3px_ink_pixels": edge_ink,
                            "nonwhite_bbox": list(bbox) if bbox else None})
    return {"engine": engine, "document": name, "dpi": DPI, "stdout": stdout.strip(), "stderr": stderr.strip(), "pages": records}

def contact(engine: str, name: str, pages: list[dict[str, Any]]) -> dict[str, Any]:
    tw, th, gap, cap = 399, 567, 12, 22
    sheet = Image.new("RGB", (gap + 3*(tw+gap), gap + 3*(th+cap+gap)), "white")
    draw, font = ImageDraw.Draw(sheet), ImageFont.load_default()
    for i, rec in enumerate(pages):
        with Image.open(ROOT / rec["path"]) as im:
            page = im.convert("RGB"); page.thumbnail((tw, th), Image.Resampling.LANCZOS)
        x, y = gap + (i%3)*(tw+gap), gap + (i//3)*(th+cap+gap)
        draw.text((x, y+3), f"{name} / {engine} / p.{i+1}", fill="black", font=font)
        sheet.paste(page, (x, y+cap))
    path = OUT / "contact-sheets" / f"{name}-{engine}.png"; path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha(path), "size": list(sheet.size)}

def render_gate(data: dict[str, Any]) -> dict[str, Any]:
    comparisons = {}
    for engine in ("poppler", "mupdf"):
        comparisons[engine] = {}
        for left, right, key in (("build-c", "build-d", "build-c_vs_build-d"), ("build-d", "artifact", "build-d_vs_artifact")):
            rows = [{"page": a["page"], "decoded_pixel_identical": a["decoded_rgb_sha256"] == b["decoded_rgb_sha256"],
                     "png_byte_identical": a["png_sha256"] == b["png_sha256"]}
                    for a, b in zip(data[engine][left]["pages"], data[engine][right]["pages"])]
            assert len(rows) == PAGES and all(x["decoded_pixel_identical"] for x in rows)
            comparisons[engine][key] = {"all_9_decoded_pixel_identical": True, "pages": rows}
    assert not any(p["outer_3px_ink_pixels"] for e in data.values() for d in e.values() for p in d["pages"])
    return comparisons

def font(ref: Any) -> dict[str, Any]:
    source, direct = obj(ref), ref
    subtype, base = str(source.get("/Subtype", "")), str(source.get("/BaseFont", ""))
    if subtype == "/Type0":
        descendants = obj(source.get("/DescendantFonts")) or []
        if descendants: source = obj(descendants[0])
    desc = obj(source.get("/FontDescriptor")) if source else None
    streams = [k for k in ("/FontFile", "/FontFile2", "/FontFile3") if desc and desc.get(k) is not None]
    oid = f"{direct.idnum} {direct.generation}" if isinstance(direct, IndirectObject) else None
    return {"object": oid, "basefont": base, "normalized": re.sub(r"^/[A-Z]{6}\+", "/", base),
            "subtype": subtype, "embedded": bool(streams), "streams": streams}

def inspect(name: str, path: Path, work: Path) -> dict[str, Any]:
    reader, fonts, links, texts = PdfReader(str(path)), {}, [], []
    root = obj(reader.trailer["/Root"]); assert len(reader.pages) == PAGES
    destinations = {str(k): reader.get_destination_page_number(v)+1 for k, v in reader.named_destinations.items()}
    outline = []
    def walk(items: list[Any], depth: int = 0) -> None:
        for item in items:
            if isinstance(item, list): walk(item, depth+1)
            elif hasattr(item, "title"): outline.append({"title": str(item.title), "page": reader.get_destination_page_number(item)+1, "depth": depth})
    walk(reader.outline)
    actions, uris, gotos, bad_rects, unsafe, broken = Counter(), [], [], [], [], []
    page_aa = annot_aa = 0
    for pn, page in enumerate(reader.pages, 1):
        texts.append(page.extract_text() or "")
        resources = obj(page.get("/Resources")) or {}; fdict = obj(resources.get("/Font")) or {}
        for ref in fdict.values():
            rec = font(ref); fonts[rec["object"] or rec["basefont"]] = rec
        page_aa += page.get("/AA") is not None
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        for aref in obj(page.get("/Annots")) or []:
            a = obj(aref); annot_aa += a.get("/AA") is not None
            if str(a.get("/Subtype")) != "/Link": continue
            rect = [float(x) for x in a.get("/Rect", [])]
            if len(rect) == 4 and (min(rect[::2]) < -.5 or min(rect[1::2]) < -.5 or max(rect[::2]) > w+.5 or max(rect[1::2]) > h+.5): bad_rects.append({"page": pn, "rect": rect})
            act = obj(a.get("/A"))
            if not act: continue
            kind = str(act.get("/S")); actions[kind] += 1
            if kind == "/URI": uris.append(str(act.get("/URI")))
            elif kind == "/GoTo":
                target = str(act.get("/D")); gotos.append(target)
                if target not in destinations: broken.append({"page": pn, "target": target})
            else: unsafe.append({"page": pn, "action": kind})
    ptext = "\f".join(texts)
    textfile = work / f"{name}.txt"; _, text_err = run([shutil.which("pdftotext"), "-enc", "UTF-8", str(path), str(textfile)])
    popbytes = textfile.read_bytes(); poptext = popbytes.decode("utf-8", "replace")
    ffout, fferr = run([shutil.which("pdffonts"), str(path)])
    infoout, infoerr = run([shutil.which("pdfinfo"), str(path)])
    mutout, muterr = run([shutil.which("mutool"), "info", "-M", str(path)])
    rows = [x for x in ffout.splitlines() if re.search(r"\s(?:yes|no)\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", x)]
    info = {k.strip(): v.strip() for line in infoout.splitlines() if ":" in line for k, v in [line.split(":", 1)]}
    fitz_blocks_bad, fitz_pages = [], []
    with fitz.open(path) as doc:
        for pn, page in enumerate(doc, 1):
            fitz_pages.append(page.get_text())
            for block in page.get_text("blocks"):
                x0,y0,x1,y1 = block[:4]; r = page.rect
                if x0<r.x0-1 or y0<r.y0-1 or x1>r.x1+1 or y1>r.y1+1: fitz_blocks_bad.append({"page":pn,"bbox":[x0,y0,x1,y1]})
    ftext = "\f".join(fitz_pages); names = obj(root.get("/Names")) or {}; marks = obj(root.get("/MarkInfo")) or {}
    recs = sorted(fonts.values(), key=lambda x:(x["normalized"], x["object"] or ""))
    record = {
        "identity":{"path":rel(path),"bytes":path.stat().st_size,"sha256":sha(path)}, "pages":len(reader.pages),
        "pdf_header":path.read_bytes()[:8].decode("ascii","replace"), "language":str(root.get("/Lang")), "tagged":bool(marks.get("/Marked",False)),
        "encrypted":reader.is_encrypted, "catalog_keys":sorted(map(str,root.keys())), "page_sizes_points":[[float(p.mediabox.width),float(p.mediabox.height)] for p in reader.pages],
        "metadata":{str(k):str(v) for k,v in (reader.metadata or {}).items()}, "outline":outline, "named_destinations":dict(sorted(destinations.items())),
        "actions":{"counts":dict(sorted(actions.items())),"uris":uris,"gotos":gotos,"broken_destinations":broken,"unsafe":unsafe,"out_of_bounds_rects":bad_rects,
                   "all_uris_https":all(x.startswith("https://") for x in uris),"catalog_AA":root.get("/AA") is not None,"page_AA":page_aa,"annotation_AA":annot_aa,
                   "open_action_present":root.get("/OpenAction") is not None},
        "payloads":{"forms":root.get("/AcroForm") is not None,"javascript":names.get("/JavaScript") is not None,"embedded_files":names.get("/EmbeddedFiles") is not None},
        "fonts":{"pypdf_unique":len(recs),"pypdf_all_embedded":all(x["embedded"] for x in recs),"records":recs,"pdffonts_rows":len(rows),
                 "pdffonts_all_embedded":all(re.search(r"\syes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$",x) for x in rows),"pdffonts_stderr":fferr.strip()},
        "text":{"pypdf_sha256":bhash(ptext.encode()),"pypdf_page_sha256":[bhash(x.encode()) for x in texts],"pypdf_nul":ptext.count("\0"),"pypdf_replacement":ptext.count("�"),
                "pdftotext_sha256":bhash(popbytes),"pdftotext_nul":poptext.count("\0"),"pdftotext_replacement":poptext.count("�"),"pdftotext_stderr":text_err.strip(),
                "mupdf_sha256":bhash(ftext.encode()),"mupdf_nul":ftext.count("\0"),"mupdf_replacement":ftext.count("�"),"mupdf_contains_代数学引论":"代数学引论" in ftext,
                "poppler_contains_代数学引论":"代数学引论" in poptext,"pypdf_contains_代数学引论":"代数学引论" in ptext},
        "geometry":{"fitz_text_blocks_out_of_bounds":fitz_blocks_bad}, "pdfinfo":info,
        "tool_diagnostics":{"pdfinfo_stderr":infoerr.strip(),"mutool_info_stdout":mutout.strip(),"mutool_info_stderr":muterr.strip()}}
    expected_outline = [{"title":t,"page":p,"depth":0} for t,p in OUTLINE]
    checks = {"nine_pages":record["pages"]==PAGES,"language_id_ID":record["language"]=="id-ID","untagged_disclosed":not record["tagged"],
              "outline_exact":outline==expected_outline,"44_destinations":len(destinations)==44,"action_counts":record["actions"]["counts"]=={"/GoTo":25,"/URI":3},
              "link_closure":not broken,"safe_actions":not unsafe and record["actions"]["all_uris_https"],"rects_in_bounds":not bad_rects,"text_blocks_in_bounds":not fitz_blocks_bad,
              "no_active_payloads":not any(record["payloads"].values()) and not record["actions"]["catalog_AA"] and not page_aa and not annot_aa,
              "fonts_embedded":record["fonts"]["pypdf_all_embedded"] and record["fonts"]["pdffonts_all_embedded"],
              "mupdf_recovers_CJK_title":record["text"]["mupdf_contains_代数学引论"],"no_replacement_chars":not record["text"]["pypdf_replacement"] and not record["text"]["pdftotext_replacement"] and not record["text"]["mupdf_replacement"]}
    failed=[k for k,v in checks.items() if not v]; assert not failed,(name,failed); record["checks"]=checks
    return record

def log_record() -> dict[str, Any]:
    path,size,digest=LOG; text=path.read_text("utf-8",errors="replace")
    patterns={"fatal_error":r"fatal error","emergency_stop":r"emergency stop","undefined_control_sequence":r"undefined control sequence","undefined_references":r"undefined references","undefined_citations":r"undefined citations","missing_character":r"missing character","overfull":r"overfull \\[hv]box","empty_link_target":r"empty link target"}
    fatal={k:len(re.findall(v,text,re.I)) for k,v in patterns.items()}; assert not any(fatal.values())
    rec={"identity":{"path":rel(path),"bytes":size,"sha256":digest},"fatal_diagnostics":fatal,"latex_release_warnings":text.count("LaTeX Warning: You have requested release"),
         "xecjk_warnings":text.count("Package xeCJK Warning"),"braids_warnings":text.count("Package braids Warning"),"fontspec_CJK_advisories":text.count("Script 'CJK' not explicitly supported"),
         "underfull_badness":[int(x) for x in re.findall(r"Underfull \\hbox \(badness (\d+)\)",text)],"raw_log_has_profile_path":str(Path.home()).lower() in text.lower(),"evidence_sanitized":True}
    assert (rec["latex_release_warnings"],rec["xecjk_warnings"],rec["braids_warnings"],rec["fontspec_CJK_advisories"],len(rec["underfull_badness"]))==(3,1,1,6,4)
    return rec

def report(ids:dict[str,Any], comps:dict[str,Any], docs:dict[str,Any], log:dict[str,Any]) -> None:
    d=docs["artifact"]; page_rows="\n".join(f"| {i} | {FINDINGS[i-1]} |" for i in range(1,10))
    identity_rows="\n".join(f"| `{v['path']}` | {v['bytes']:,} | `{v['sha256']}` |" for k,v in ids.items() if isinstance(v,dict))
    matrix="\n".join(f"- {engine} {pair.replace('_',' ')}: all 9 decoded RGB pages identical." for engine in comps for pair in comps[engine])
    text=f"""# Unit 026 visual and PDF QA — 2026-08-25

Status: **PASS WITH WARNINGS**. Required identity, replay, same-renderer decoded-pixel, structure, navigation, font, text, action/link, and clipping gates pass.

## Bound inputs

| Path | Bytes | SHA-256 |
|---|---:|---|
{identity_rows}

Build D and the artifact are byte-identical. All PDFs have 9 pages.

## Rendering gate

Poppler and MuPDF rendered every PDF at 144 dpi ({SIZE[0]} × {SIZE[1]} pixels per page). Equality uses decoded RGB pixels, not PNG compression.

{matrix}

All 54 renders have zero ink pixels in their outer 3-pixel band. Per-page PNG/decoded-pixel hashes and six contact sheets are recorded in `qa/unit-026-evidence/render-hash-inventory.json`.

## PDF gate

- PDF `{d['pdf_header']}`; `/Lang id-ID`; 9 pages; unencrypted; no form, JavaScript, additional action, or embedded file.
- Exact four-entry outline passes; all 44 named destinations are inventoried. All 25 `/GoTo` links close over them; three `/URI` links are HTTPS; no unsafe action occurs.
- Link rectangles and MuPDF text blocks are in bounds. All {d['fonts']['pypdf_unique']} pypdf font objects and {d['fonts']['pdffonts_rows']} `pdffonts` rows are embedded.
- pypdf, Poppler, and MuPDF text hashes match separately across C, D, and artifact. MuPDF recovers `代数学引论`; this Poppler installation and pypdf do not.

## Independent full-resolution review

All pages were reviewed independently in both renderers.

| Page | Finding |
|---:|---|
{page_rows}

No overlap, clipping, broken math/diagram stroke, tofu box, or unintended edge contact was found.

## Warnings

1. Poppler reports a missing `Adobe-GB1` language pack and omits the five bibliography-title glyphs `代数学引论` on page 9; its extractor also reports the mapping/font limitation. MuPDF renders and extracts the title correctly. Same-renderer C↔D and D↔artifact pixel identity still passes.
2. `/Lang id-ID` is correct, but the PDF is untagged; no tagged-accessibility claim is made.
3. The log has 3 LaTeX release warnings, 1 xeCJK warning, 1 frozen/deprecated `braids` warning, 6 fontspec CJK advisories, and 4 visually benign underfull hboxes (badness {', '.join(map(str,log['underfull_badness']))}). Fatal/error diagnostics and overfull boxes are zero.
4. The raw log contains an absolute profile path; generated evidence is sanitized and does not reproduce it.

Evidence: `structure-and-pdf-qa.json` holds exact structures, destinations, actions, fonts, text hashes, tool output, and checks; `render-hash-inventory.json` holds all image identities/comparisons. Verdict: **PASS WITH WARNINGS**.
"""
    REPORT.write_text(text, encoding="utf-8", newline="\n")

def main() -> None:
    ids=identities(); resolved=OUT.resolve(); assert resolved.parent==(ROOT/"qa").resolve() and resolved.name=="unit-026-evidence"
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True); TMP.mkdir(parents=True,exist_ok=True)
    renders={e:{} for e in ("poppler","mupdf")}; sheets=[]
    with tempfile.TemporaryDirectory(prefix="unit026-",dir=TMP) as td:
        work=Path(td)
        for engine in renders:
            for name,(path,_,__) in DOCS.items():
                renders[engine][name]=render(engine,name,path,work); sheets.append(contact(engine,name,renders[engine][name]["pages"]))
        comps=render_gate(renders); docs={name:inspect(name,spec[0],work) for name,spec in DOCS.items()}
    for field in ("outline","named_destinations","page_sizes_points"):
        assert docs["build-c"][field]==docs["build-d"][field]==docs["artifact"][field]
    for field in ("pypdf_sha256","pypdf_page_sha256","pdftotext_sha256","mupdf_sha256"):
        assert docs["build-c"]["text"][field]==docs["build-d"]["text"][field]==docs["artifact"]["text"][field]
    log=log_record()
    dump(OUT/"render-hash-inventory.json",{"status":"PASS_WITH_WARNINGS","identities":ids,"renderers":renders,"contact_sheets":sheets,"decoded_pixel_comparisons":comps,"edge_gate":{"outer_band_pixels":EDGE,"all_54_zero_ink":True},"warning":"Poppler Adobe-GB1 mapping absent; page 9 CJK title omitted by Poppler but rendered by MuPDF."})
    dump(OUT/"structure-and-pdf-qa.json",{"status":"PASS_WITH_WARNINGS","documents":docs,"build_log":log,"cross_pdf_semantic_identity":True})
    report(ids,comps,docs,log)
    print("PASS_WITH_WARNINGS"); print(rel(OUT/"render-hash-inventory.json")); print(rel(OUT/"structure-and-pdf-qa.json")); print(rel(REPORT))

if __name__=="__main__": main()
