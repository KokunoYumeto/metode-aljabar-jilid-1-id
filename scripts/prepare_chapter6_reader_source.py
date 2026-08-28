from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "repo/source/chapter6.tex"
OUTPUT = ROOT / "build/chapter6-reader-source/chapter6-reader-reflow.tex"
SOURCE_SHA256 = "15c09af18eeab6ce1a4c5a4cb69b1b3a42bc2422b015f21f77ccfbb3c94f7e14"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    if source_bytes.startswith(b"\xef\xbb\xbf") or b"\r" in source_bytes:
        raise RuntimeError("canonical Chapter 6 has noncanonical encoding/newlines")
    if digest(source_bytes) != SOURCE_SHA256:
        raise RuntimeError("canonical Chapter 6 identity mismatch")
    text = source_bytes.decode("utf-8", errors="strict")

    text = replace_once(
        text,
        r"$\Hom_{(Q,S)\dcate{Mod}} \left( M \dotimes{R} N, A \right)$ dapat diidentifikasi",
        r"$\Hom_{(Q,S)\dcate{Mod}} \allowbreak \left( M \dotimes{R} N, A \right)$ dapat diidentifikasi",
        "Hom-tensor inline break",
    )
    text = replace_once(
        text,
        r"Kita hanya memberikan isomorfisme fungtor $P_{R \to S}(-) \dotimes{S} P_{R \to S}(-) \xrightarrow[\xi]{\sim} P_{R \to S}\left( - \dotimes{R} - \right)$ yang diperlukan bagi fungtor monoidal.",
        r"Kita hanya memberikan isomorfisme fungtor berikut, yang diperlukan bagi fungtor monoidal: \[P_{R \to S}(-) \dotimes{S} P_{R \to S}(-) \xrightarrow[\xi]{\sim} P_{R \to S}\left( - \dotimes{R} - \right).\]",
        "monoidal-functor display reflow",
    )
    text = replace_once(
        text,
        r"\end{cases} \quad \because\text{diperiksa setelah mengomposisikan kedua ruas dengan monomorfisme $\iota_i$ dari kiri}, \\",
        r"\end{cases} \quad \because\substack{\text{diperiksa setelah mengomposisikan kedua ruas} \\ \text{dengan monomorfisme }\iota_i\text{ dari kiri}}, \\",
        "idempotent proof display reflow",
    )

    output_bytes = text.encode("utf-8")
    if len(text.splitlines()) != 1994:
        raise RuntimeError("reader reflow changed Chapter 6 record count")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(output_bytes)
    print(f"source={SOURCE}")
    print(f"source_bytes={len(source_bytes)}")
    print(f"source_sha256={digest(source_bytes)}")
    print(f"output={OUTPUT}")
    print(f"output_records={len(text.splitlines())}")
    print(f"output_bytes={len(output_bytes)}")
    print(f"output_sha256={digest(output_bytes)}")
    print("reflows=3")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
