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
    r"|\\(?:begin|end)\{[^{}]+\}"
    r"|\\(?:label|ref|cref|rref|eqref|pageref|cite)(?:\[[^\]]*\])?\{[^{}]*\}"
    r"|\\\\"
    r"|\\(?:[A-Za-z@]+|.)"
    r"|[{}\[\]&~$%^#]",
    re.DOTALL,
)
HAS_WORD = re.compile(r"[A-Za-z]{2,}")


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


def split_protected(text: str) -> list[tuple[bool, str]]:
    pieces: list[tuple[bool, str]] = []
    position = 0
    for match in PROTECTED.finditer(text):
        if match.start() > position:
            pieces.append((False, text[position:match.start()]))
        pieces.append((True, match.group(0)))
        position = match.end()
    if position < len(text):
        pieces.append((False, text[position:]))
    return pieces


def reflow(text: str, originals: list[str]) -> list[str]:
    count = len(originals)
    if count == 1:
        return [text.strip()]
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
                token = tokens[cursor + take]
                width += len(token) + (1 if take else 0)
                take += 1
                if width >= target:
                    break
        content = " ".join(tokens[cursor:cursor + take])
        cursor += take
        indent = re.match(r"^[ \t]*", originals[index]).group(0)
        output.append(indent + content if content else "")
    return output


all_plans: dict[str, list[tuple[list[str], bool, list[tuple[bool, str | int]]]]] = {}
requests: list[str] = []
request_lookup: dict[str, int] = {}

for filename in FILES:
    source_lines = (SOURCE_DIR / filename).read_text(encoding="utf-8").splitlines()
    file_plan: list[tuple[list[str], bool, list[tuple[bool, str | int]]]] = []
    for original_lines, translatable in blocks(source_lines):
        if not translatable:
            file_plan.append((original_lines, False, [(True, original_lines[0])]))
            continue
        joined = " ".join(line.strip() for line in original_lines)
        plan: list[tuple[bool, str | int]] = []
        for protected, piece in split_protected(joined):
            if protected or not HAS_WORD.search(piece):
                plan.append((True, piece))
                continue
            leading = piece[: len(piece) - len(piece.lstrip())]
            trailing = piece[len(piece.rstrip()):]
            core = piece.strip()
            if not core:
                plan.append((True, piece))
                continue
            key = core
            if key not in request_lookup:
                request_lookup[key] = len(requests)
                requests.append(key)
            plan.append((True, leading))
            plan.append((False, request_lookup[key]))
            plan.append((True, trailing))
        file_plan.append((original_lines, True, plan))
    all_plans[filename] = file_plan

print(f"unique prose fragments: {len(requests)}", flush=True)
tokenizer = AutoTokenizer.from_pretrained(
    "facebook/nllb-200-distilled-600M",
    src_lang="eng_Latn",
    local_files_only=True,
)
model = AutoModelForSeq2SeqLM.from_pretrained(
    "facebook/nllb-200-distilled-600M",
    local_files_only=True,
    dtype=torch.float16,
).to("cuda")
target_id = tokenizer.convert_tokens_to_ids("ind_Latn")
translations: list[str] = [""] * len(requests)
for start in range(0, len(requests), 24):
    batch = requests[start:start + 24]
    encoded = tokenizer(
        batch,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    ).to("cuda")
    with torch.inference_mode():
        generated = model.generate(
            **encoded,
            forced_bos_token_id=target_id,
            max_new_tokens=512,
            num_beams=4,
        )
    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
    for offset, translated in enumerate(decoded):
        translations[start + offset] = translated.strip()
    if start % 240 == 0:
        print(f"translated {min(start + len(batch), len(requests))}/{len(requests)}", flush=True)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for filename in FILES:
    output_lines: list[str] = []
    for original_lines, translatable, plan in all_plans[filename]:
        if not translatable:
            output_lines.extend(original_lines)
            continue
        rebuilt = "".join(
            str(value) if literal else translations[int(value)]
            for literal, value in plan
        )
        output_lines.extend(reflow(rebuilt, original_lines))
    expected = len((SOURCE_DIR / filename).read_text(encoding="utf-8").splitlines())
    if len(output_lines) != expected:
        raise SystemExit(f"record mismatch for {filename}: {len(output_lines)} != {expected}")
    (OUTPUT_DIR / filename).write_text(
        "\n".join(output_lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {filename}: {len(output_lines)} records", flush=True)
