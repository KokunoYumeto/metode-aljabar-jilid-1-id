from __future__ import annotations

import re
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


BASE = Path(__file__).resolve().parent
SOURCE_DIR = BASE / "repaired-source-en"
OUTPUT_DIR = BASE / "translated-id"
FILES = [
    "01-nakayama.tex",
    "02-spec-zariski.tex",
    "03-associated-primary.tex",
    "04-lying-over-going-up.tex",
    "05-nullstellensatz-normalization.tex",
    "06-krull-dimension.tex",
]

MATH_ENV = r"align\*?|aligned|equation\*?|gather\*?|multline\*?|array|cases|matrix|pmatrix|bmatrix|smallmatrix|tikzcd|tikzpicture"
PROTECTED = re.compile(
    rf"\\begin\{{({MATH_ENV})\}}.*?\\end\{{\1\}}"
    r"|\\\[.*?\\\]"
    r"|\\\(.*?\\\)"
    r"|(?<!\\)\$(?!\$).*?(?<!\\)\$"
    r"|\\(?:emph|textbf|section|subsection|subsubsection|paragraph|caption|text|textrm|textnormal|mathrm)\s*\{[^{}]*\}"
    r"|\\index(?:\[[^\]]*\])?\{[^{}]*\}"
    r"|\\(?:begin|end)\{[^{}]+\}(?:\[[^\]]*\])?"
    r"|\\(?:label|ref|cref|rref|eqref|pageref|cite)(?:\[[^\]]*\])?\{[^{}]*\}"
    r"|\\\\"
    r"|\\(?:[A-Za-z@]+|.)"
    r"|[{}\[\]&~$%^#]",
    re.DOTALL,
)
PLACEHOLDER = re.compile(r"ZXQPH\d{4}QXZ")
HAS_WORD = re.compile(r"[A-Za-z]{2,}")

TERMS = {
    "krull dimension": "dimensi Krull",
    "krull's principal ideal theorem": "Hauptidealsatz Krull",
    "zariski topology": "topologi Zariski",
    "algebraically closed field": "medan tertutup secara aljabar",
    "associated primes": "prima terkait",
    "associated prime": "prima terkait",
    "primary decomposition": "dekomposisi primer",
    "minimal prime": "prima minimal",
    "embedded prime": "prima tertanam",
    "prime ideals": "ideal prima",
    "prime ideal": "ideal prima",
    "maximal ideals": "ideal maksimal",
    "maximal ideal": "ideal maksimal",
    "principal ideals": "ideal utama",
    "principal ideal": "ideal utama",
    "local rings": "gelanggang lokal",
    "local ring": "gelanggang lokal",
    "commutative rings": "gelanggang komutatif",
    "commutative ring": "gelanggang komutatif",
    "polynomial rings": "gelanggang polinomial",
    "polynomial ring": "gelanggang polinomial",
    "noetherian rings": "gelanggang Noetherian",
    "noetherian ring": "gelanggang Noetherian",
    "noetherian modules": "modul Noetherian",
    "noetherian module": "modul Noetherian",
    "integral domains": "daerah integral",
    "integral domain": "daerah integral",
    "fraction field": "medan pecahan",
    "residue field": "medan residu",
    "field extensions": "ekstensi medan",
    "field extension": "ekstensi medan",
    "integral extensions": "ekstensi integral",
    "integral extension": "ekstensi integral",
    "finitely generated": "dibangkitkan secara hingga",
    "tensor products": "hasil kali tensor",
    "tensor product": "hasil kali tensor",
    "direct sums": "jumlah langsung",
    "direct sum": "jumlah langsung",
    "vector spaces": "ruang vektor",
    "vector space": "ruang vektor",
    "jacobson radical": "radikal Jacobson",
    "associated graded ring": "gelanggang bergradasi terkait",
    "transcendence degree": "derajat transendensi",
    "chain of prime ideals": "rantai ideal prima",
    "algebraic geometry": "geometri aljabar",
    "irreducible decomposition": "dekomposisi taktereduksi",
    "reduced primary decomposition": "dekomposisi primer tereduksi",
    "multiplicative sets": "himpunan multiplikatif",
    "multiplicative set": "himpunan multiplikatif",
    "hilbert function": "fungsi Hilbert",
    "hilbert polynomial": "polinomial Hilbert",
    "embedding dimension": "dimensi embedding",
    "normalization lemma": "lema normalisasi",
    "integral closure": "penutupan integral",
    "integral elements": "unsur integral",
    "integral element": "unsur integral",
    "finite maps": "pemetaan hingga",
    "finite map": "pemetaan hingga",
    "affine rings": "gelanggang afin",
    "affine ring": "gelanggang afin",
    "exact sequences": "barisan eksak",
    "exact sequence": "barisan eksak",
    "homeomorphisms": "homeomorfisme",
    "homeomorphism": "homeomorfisme",
    "homomorphisms": "homomorfisme",
    "homomorphism": "homomorfisme",
    "isomorphisms": "isomorfisme",
    "isomorphism": "isomorfisme",
    "bijections": "bijeksi",
    "bijection": "bijeksi",
    "polynomials": "polinomial",
    "polynomial": "polinomial",
    "algebras": "aljabar",
    "algebra": "aljabar",
    "modules": "modul",
    "module": "modul",
    "fields": "medan",
    "field": "medan",
    "rings": "gelanggang",
    "ring": "gelanggang",
    "ideals": "ideal",
    "ideal": "ideal",
    "domains": "daerah integral",
    "domain": "daerah integral",
    "dimension": "dimensi",
    "codimension": "kodimensi",
    "normalization": "normalisasi",
    "constructible": "konstruktibel",
    "irreducible": "taktereduksi",
    "nilpotent": "nilpoten",
    "surjective": "surjektif",
    "injective": "injektif",
    "continuous": "kontinu",
    "functoriality": "funktorialitas",
    "nilradical": "nilradikal",
    "localization": "lokalisasi",
    "spectrum": "spektrum",
    "support": "dukungan",
}
TERM_RE = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in sorted(TERMS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def blocks(lines: list[str]) -> list[tuple[list[str], bool]]:
    result: list[tuple[list[str], bool]] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            result.append((current, True))
            current = []

    for line in lines:
        if not line.strip():
            flush()
            result.append(([line], False))
        elif re.search(r"(?<!\\)%", line):
            flush()
            result.append(([line], True))
        else:
            current.append(line)
            if len(current) >= 18:
                flush()
    flush()
    return result


def mask(text: str) -> tuple[str, list[str]]:
    mappings: list[str] = []

    def token(value: str) -> str:
        marker = f"ZXQPH{len(mappings):04d}QXZ"
        mappings.append(value)
        return f" {marker} "

    pieces: list[str] = []
    position = 0
    for match in PROTECTED.finditer(text):
        plain = text[position:match.start()]
        cursor = 0
        for term_match in TERM_RE.finditer(plain):
            pieces.append(plain[cursor:term_match.start()])
            pieces.append(token(TERMS[term_match.group(0).lower()]))
            cursor = term_match.end()
        pieces.append(plain[cursor:])
        pieces.append(token(match.group(0)))
        position = match.end()
    plain = text[position:]
    cursor = 0
    for term_match in TERM_RE.finditer(plain):
        pieces.append(plain[cursor:term_match.start()])
        pieces.append(token(TERMS[term_match.group(0).lower()]))
        cursor = term_match.end()
    pieces.append(plain[cursor:])
    return re.sub(r"\s+", " ", "".join(pieces)).strip(), mappings


def restore(translated: str, mappings: list[str]) -> str:
    expected = [f"ZXQPH{i:04d}QXZ" for i in range(len(mappings))]
    seen = PLACEHOLDER.findall(translated)
    if seen != expected:
        raise ValueError(f"placeholder topology changed: expected {expected}, got {seen}")
    for index, value in enumerate(mappings):
        translated = translated.replace(f"ZXQPH{index:04d}QXZ", value)
    return re.sub(r"[ \t]+", " ", translated).strip()


def reflow(text: str, originals: list[str]) -> list[str]:
    count = len(originals)
    if count == 1:
        return [text]
    tokens = text.split()
    if not tokens:
        return [""] * count
    output: list[str] = []
    cursor = 0
    for index in range(count):
        remaining_lines = count - index
        remaining_tokens = len(tokens) - cursor
        if remaining_lines == 1:
            take = remaining_tokens
        elif remaining_tokens <= remaining_lines:
            take = 1 if remaining_tokens else 0
        else:
            remaining_chars = sum(len(token) + 1 for token in tokens[cursor:])
            target = max(1, remaining_chars // remaining_lines)
            width = 0
            take = 0
            while cursor + take < len(tokens) - (remaining_lines - 1):
                item = tokens[cursor + take]
                width += len(item) + (1 if take else 0)
                take += 1
                if width >= target:
                    break
        content = " ".join(tokens[cursor:cursor + take])
        cursor += take
        indent = re.match(r"^[ \t]*", originals[index]).group(0)
        output.append(indent + content if content else "")
    return output


tokenizer = AutoTokenizer.from_pretrained(
    "facebook/nllb-200-distilled-600M", src_lang="eng_Latn", local_files_only=True
)
model = AutoModelForSeq2SeqLM.from_pretrained(
    "facebook/nllb-200-distilled-600M", local_files_only=True, dtype=torch.float16
).to("cuda")
target_id = tokenizer.convert_tokens_to_ids("ind_Latn")


def translate_batch(items: list[str]) -> list[str]:
    results: list[str] = []
    for start in range(0, len(items), 20):
        batch = items[start:start + 20]
        encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=768).to("cuda")
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                forced_bos_token_id=target_id,
                max_new_tokens=768,
                num_beams=1,
            )
        results.extend(text.strip() for text in tokenizer.batch_decode(generated, skip_special_tokens=True))
        if start % 200 == 0:
            print(f"translated {min(start + len(batch), len(items))}/{len(items)} contextual blocks", flush=True)
    return results


plans: dict[str, list[tuple[list[str], bool, str, list[str]]]] = {}
requests: list[str] = []
request_refs: list[tuple[str, int]] = []
for filename in FILES:
    source_lines = (SOURCE_DIR / filename).read_text(encoding="utf-8").splitlines()
    file_plan: list[tuple[list[str], bool, str, list[str]]] = []
    for original_lines, translatable in blocks(source_lines):
        if not translatable:
            file_plan.append((original_lines, False, original_lines[0], []))
            continue
        joined = " ".join(line.strip() for line in original_lines)
        masked, mappings = mask(joined)
        file_plan.append((original_lines, True, masked, mappings))
        if HAS_WORD.search(masked):
            request_refs.append((filename, len(file_plan) - 1))
            requests.append(masked)
    plans[filename] = file_plan

print(f"contextual blocks: {len(requests)}", flush=True)
translated_requests = translate_batch(requests)
translated_lookup = dict(zip(request_refs, translated_requests))

NORMALIZATIONS = (
    (r"\bKami\b", "Kita"),
    (r"\bBiarkan\b", "Misalkan"),
    (r"\bbiarkan\b", "misalkan"),
    (r"\bcincin\b", "gelanggang"),
    (r"\bCincin\b", "Gelanggang"),
    (r"ideal maksimum", "ideal maksimal"),
    (r"ideal-ideal maksimum", "ideal-ideal maksimal"),
    (r"produk tensor", "hasil kali tensor"),
    (r"fungsi kontravarian", "fungtor kontravarian"),
    (r"fungsi kovarian", "fungtor kovarian"),
    (r"\bkorollary\b", "korolari"),
    (r"\bpolynomial\b", "polinomial"),
    (r"\bPolinomi\b", "Polinomial"),
    (r"\bpolinomi\b", "polinomial"),
    (r"secara terbatas", "secara hingga"),
    (r"secara akhir", "secara hingga"),
    (r"\bSurjective\b", "surjektif"),
    (r"\bInjective\b", "injektif"),
    (r"\bmap\b", "pemetaan"),
    (r"\bmaps\b", "pemetaan"),
    (r"\bfield\b", "medan"),
    (r"\bfields\b", "medan"),
    (r"\bvariety\b", "varietas"),
    (r"\bvarieties\b", "varietas"),
)

INLINE_PROSE = re.compile(
    r"\\(?P<cmd>emph|textbf|section|subsection|subsubsection|paragraph|caption|text|textrm|textnormal|mathrm)"
    r"(?P<space>\s*)\{(?P<body>[^{}]*)\}"
)
INLINE_INVARIANTS = {"Spec", "Funct", "op"}
INLINE_EXACT = {
    "Nakayama's lemma": "Lema Nakayama",
    "The spectrum of a ring": "Spektrum gelanggang",
    "Definition and examples": "Definisi dan contoh",
    "The radical ideal-closed subset correspondence": "Korespondensi antara ideal radikal dan himpunan bagian tertutup",
    "A meta-observation about prime ideals": "Sebuah pengamatan meta tentang ideal prima",
    "Functoriality of $\\spec$": "Funktorialitas $\\spec$",
    "A basis for the Zariski topology": "Suatu basis untuk topologi Zariski",
    "Associated primes": "Prima terkait",
    "The support": "Dukungan",
    "Localization and $\\ass(M)$": "Lokalisasi dan $\\ass(M)$",
    "Associated primes determine the support": "Prima terkait menentukan dukungan",
    "Primary modules": "Modul primer",
    "Primary decomposition": "Dekomposisi primer",
    "Irreducible and coprimary modules": "Modul taktereduksi dan koprimer",
    "Irreducible and primary decompositions": "Dekomposisi taktereduksi dan primer",
    "Uniqueness questions": "Pertanyaan ketunggalan",
    "Lying over and going up": "Lying over dan going up",
    "Lying over": "Lying over",
    "Going up": "Going up",
    "The Hilbert Nullstellensatz": "Nullstellensatz Hilbert",
    "Statement and initial proof of the Nullstellensatz": "Pernyataan dan bukti awal Nullstellensatz",
    "The normalization lemma": "Lema normalisasi",
    "Back to the Nullstellensatz": "Kembali ke Nullstellensatz",
    "A little affine algebraic geometry": "Sedikit geometri aljabar afin",
    "The Hilbert function and the dimension of a local ring": "Fungsi Hilbert dan dimensi gelanggang lokal",
    "Integer-valued polynomials": "Polinomial bernilai bilangan bulat",
    "The Hilbert function is a polynomial": "Fungsi Hilbert adalah suatu polinomial",
    "The dimension of a module": "Dimensi modul",
    "Dimension depends only on the support": "Dimensi hanya bergantung pada dukungan",
    "The dimension of an affine ring": "Dimensi gelanggang afin",
    "Other definitions and characterizations of dimension": "Definisi dan karakterisasi lain dari dimensi",
    "The topological characterization of dimension": "Karakterisasi topologis dimensi",
    "Recap": "Ikhtisar",
    "Krull dimension": "Dimensi Krull",
    "Yet another definition": "Satu lagi definisi",
    "Krull's Hauptidealsatz": "Hauptidealsatz Krull",
    "Further remarks": "Catatan lebih lanjut",
    "Edition bridge (original).": "Jembatan edisi (orisinal).",
    "where": "dengan",
    "such that": "sedemikian sehingga",
    "fr.  \\ field \\": "medan pecahan",
    "other \\ factors": "faktor-faktor lain",
    "a \\ minimal \\ prime": "prima minimal",
    "local \\ noetherian \\ rings": "gelanggang Noetherian lokal",
    "for \\ some \\": "untuk suatu",
}


def normalize_id(text: str) -> str:
    for pattern, replacement in NORMALIZATIONS:
        text = re.sub(pattern, replacement, text)
    return text


def translate_inline_bodies(drafts: dict[str, list[str]]) -> dict[str, str]:
    bodies: list[str] = []
    masked_by_body: dict[str, tuple[str, list[str]]] = {}
    for output_lines in drafts.values():
        for match in INLINE_PROSE.finditer("\n".join(output_lines)):
            body = match.group("body")
            if body in INLINE_EXACT or body in INLINE_INVARIANTS or body in masked_by_body:
                continue
            if not HAS_WORD.search(body):
                continue
            masked_body, mappings = mask(body)
            masked_by_body[body] = (masked_body, mappings)
            if HAS_WORD.search(masked_body):
                bodies.append(body)

    translated: dict[str, str] = dict(INLINE_EXACT)
    requests = [masked_by_body[body][0] for body in bodies]
    if requests:
        print(f"inline prose fragments: {len(requests)}", flush=True)
        rendered = translate_batch(requests)
        for body, value in zip(bodies, rendered):
            translated[body] = normalize_id(restore(value, masked_by_body[body][1]))
    for body, (masked_body, mappings) in masked_by_body.items():
        if body not in translated:
            translated[body] = normalize_id(restore(masked_body, mappings))
    return translated


drafts: dict[str, list[str]] = {}
for filename in FILES:
    output_lines: list[str] = []
    for index, (original_lines, translatable, masked, mappings) in enumerate(plans[filename]):
        if not translatable:
            output_lines.extend(original_lines)
            continue
        if (filename, index) in translated_lookup:
            rebuilt = restore(translated_lookup[(filename, index)], mappings)
        else:
            rebuilt = restore(masked, mappings)
        rebuilt = normalize_id(rebuilt)
        output_lines.extend(reflow(rebuilt, original_lines))
    expected = len((SOURCE_DIR / filename).read_text(encoding="utf-8").splitlines())
    if len(output_lines) != expected:
        raise SystemExit(f"record mismatch for {filename}: {len(output_lines)} != {expected}")
    drafts[filename] = output_lines

inline_translations = translate_inline_bodies(drafts)
for filename in FILES:
    text = "\n".join(drafts[filename])

    def replace_inline(match: re.Match[str]) -> str:
        body = match.group("body")
        replacement = inline_translations.get(body, body)
        return f"\\{match.group('cmd')}{match.group('space')}{{{replacement}}}"

    text = INLINE_PROSE.sub(replace_inline, text)
    output_lines = text.splitlines()
    expected = len((SOURCE_DIR / filename).read_text(encoding="utf-8").splitlines())
    if len(output_lines) != expected:
        raise SystemExit(f"post-translation record mismatch for {filename}: {len(output_lines)} != {expected}")
    (OUTPUT_DIR / filename).write_text(text + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {filename}: {len(output_lines)} records", flush=True)
