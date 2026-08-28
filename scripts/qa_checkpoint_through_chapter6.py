from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-6-reader.pdf"
PRIOR = ROOT / "output/pdf/00-metode-aljabar-jilid-1-id-checkpoint-through-bab-5-reader.pdf"
CHAPTER6 = ROOT / "artifacts/unit-044-bab-6-modul-id.pdf"
RENDER_DIR = ROOT / "tmp/pdfs/checkpoint-through-chapter6-boundaries"
RECEIPT = ROOT / "qa/unit-044-evidence/checkpoint-through-bab-6-structural-qa.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def page_identity(page) -> tuple[str, tuple[float, float, float, float], int]:
    contents = page.get_contents()
    data = contents.get_data() if contents is not None else b""
    media = tuple(round(float(value), 4) for value in page.mediabox)
    text_length = len(page.extract_text() or "")
    return hashlib.sha256(data).hexdigest(), media, text_length


def main() -> int:
    current = PdfReader(CURRENT, strict=True)
    prior = PdfReader(PRIOR, strict=True)
    chapter6 = PdfReader(CHAPTER6, strict=True)
    failures: list[str] = []
    if len(current.pages) != 460:
        failures.append(f"current page count {len(current.pages)} != 460")
    if len(prior.pages) != 385:
        failures.append(f"prior page count {len(prior.pages)} != 385")
    if len(chapter6.pages) != 75:
        failures.append(f"Chapter 6 page count {len(chapter6.pages)} != 75")

    inherited_mismatches: list[int] = []
    if len(current.pages) >= 385 and len(prior.pages) == 385:
        for index in range(1, 385):
            if page_identity(current.pages[index]) != page_identity(prior.pages[index]):
                inherited_mismatches.append(index + 1)
    appended_mismatches: list[int] = []
    if len(current.pages) == 460 and len(chapter6.pages) == 75:
        for index in range(75):
            if page_identity(current.pages[385 + index]) != page_identity(chapter6.pages[index]):
                appended_mismatches.append(386 + index)
    if inherited_mismatches:
        failures.append(f"{len(inherited_mismatches)} inherited page identity mismatches")
    if appended_mismatches:
        failures.append(f"{len(appended_mismatches)} appended Chapter 6 page identity mismatches")

    boundary_text = {
        "page_1": current.pages[0].extract_text() or "",
        "page_385": current.pages[384].extract_text() or "",
        "page_386": current.pages[385].extract_text() or "",
        "page_460": current.pages[459].extract_text() or "",
    }
    expected_fragments = {
        "page_1": "MELALUI BAB 6",
        "page_385": "INDEKS SIMBOL",
        "page_386": "Metode Aljabar",
        "page_460": "INDEKS SIMBOL",
    }
    for key, fragment in expected_fragments.items():
        if fragment.casefold() not in boundary_text[key].casefold():
            failures.append(f"boundary text missing {fragment!r} on {key}")

    rendered = sorted(RENDER_DIR.glob("*.png"))
    if len(rendered) != 4:
        failures.append(f"boundary render count {len(rendered)} != 4")

    receipt = {
        "schema": "o013-checkpoint-through-chapter6-structural-qa-v1",
        "result": "pass" if not failures else "fail",
        "output": {
            "path": CURRENT.relative_to(ROOT).as_posix(),
            "pages": len(current.pages),
            "bytes": CURRENT.stat().st_size,
            "sha256": sha256(CURRENT),
        },
        "inherited_pages_compared": 384,
        "inherited_page_identity_mismatches": inherited_mismatches,
        "appended_chapter6_pages_compared": 75,
        "appended_page_identity_mismatches": appended_mismatches,
        "boundary_pages_rendered": [path.name for path in rendered],
        "boundary_text_lengths": {key: len(value) for key, value in boundary_text.items()},
        "visual_inspection": "PENDING_MODEL_INSPECTION",
        "failures": failures,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
