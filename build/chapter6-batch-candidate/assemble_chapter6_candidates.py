from __future__ import annotations

import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
TAIL = HERE / "chapter6-lines-1664-1994-id.tex"
COMPLETE = HERE / "chapter6-complete-id.tex"
SEGMENTS = (
    HERE / "chapter6-lines-0001-0337-id.tex",
    HERE / "chapter6-lines-0338-0973-id.tex",
    HERE / "chapter6-lines-0974-1663-id.tex",
    TAIL,
)

INITIAL_TAIL_SHA256 = "4e763096d11eb1f2b8203d23f4f22fbdf835b1f06468ff5fdbc5ddbe467b5dfa"
INDECOMPOSABLE_MARKER = r"\section{Modul Tak Terurai}\label{sec:indecomposable-mod}"
SEMISIMPLE_REMAINDER_MARKER = r"\begin{lemma}\label{prop:existence-simple-subquotient}"

MISSING_PARAGRAPH = r"""Sebagai akibat, misalkan diberikan dekomposisi jumlah langsung hingga $M = \bigoplus_{i=1}^r M_i^{\oplus n_i}$, dengan $M_1, \ldots, M_r$ modul-modul sederhana yang saling tak isomorfik. Lemma \ref{prop:Hom-matrix} memberikan
\[ \End_R(M)^{\text{op}} \rightiso \prod_{i=1}^n M_{n_i}\left(D_i^{\text{op}}\right)^{\text{op}} \xrightarrow[\text{transpos}]{\sim} \prod_{i=1}^n M_{n_i}(D_i) \]
dengan $D_i := \End_R(M_i)^\text{op}$ suatu gelanggang pembagian, $M_i^{\oplus n_i}$ suatu modul kanan $M_{n_i}(D_i)$, dan $M$ suatu modul kanan $\End_R(M)^\text{op}$; isomorfisme di atas mempertahankan struktur-struktur modul tersebut."""

EXERCISES = r"""\begin{Exercises}
	\item Untuk suatu kategori kecil $I$ dan fungtor $\alpha: I \to R\dcate{Mod}$, yang pada tingkat objek ditulis $i \mapsto M_i$, buktikan bahwa $\varinjlim_i M_i := \varinjlim \alpha$ mempunyai konstruksi langsung berikut:
	\[ \varinjlim_i M_i := \left( \bigoplus_{i \in \Obj(I)} M_i \right) \bigg/N \]
	dengan submodul $N = \lrangle{ \alpha(f)(x_i) - x_i : i \xrightarrow{f} j, \;  x_i \in M_i }$.
	\item Ambil sebarang gelanggang $A$ dan modul kanan $A$, $V = A^{\oplus I}$, dengan $I$ himpunan tak hingga. Buktikan bahwa gelanggang $R := \End(V_A)$ memenuhi $(R_R)^{\oplus 2} \simeq R_R$, sehingga $R$ tidak mempunyai sifat bilangan basis invarian kanan. \begin{hint} Pilih suatu isomorfisme $V \rightiso V \oplus V$ dan terapkan fungtor $\Hom_A(V, -)$.\end{hint}
	\item Ingat kembali konsep pusat kategori (Definisi \ref{def:cat-center}). Untuk setiap gelanggang $R$, buktikan bahwa pusat $\cated{Mod}R$ dapat diidentifikasi dengan pusat gelanggang $Z_R$. \begin{hint} Amati terlebih dahulu bahwa gelanggang endomorfisme $R$ sebagai modul kanan $R$ dapat diidentifikasi dengan $R$.\end{hint}
	\item Buktikan secara lengkap pernyataan dalam Catatan \ref{rem:bimodule-balanced}.
	\item Untuk modul terbangkitkan hingga $N$ atas gelanggang ideal utama $R$, buktikan bahwa faktor-faktor elementer $\mathfrak{d}(N_0)_1 \supset \cdots$ dari suatu submodul $N_0$ dapat disisipkan sebagai ``faktor'' ke dalam faktor-faktor elementer $\mathfrak{d}(N)_1 \supset \cdots$ dari $N$; jelaskan secara tepat arti pernyataan ini, dan buktikan hasil yang sama untuk modul hasil bagi. \begin{hint} Reduksikan ke kasus $N=N[p^\infty]$ dan gunakan \eqref{eqn:PID-decomp-nu_j} untuk membuktikan bahwa diagram \eqref{eqn:PID-decomp-diagram} bagi $N_0$ dapat ditanamkan ke dalam diagram bagi $N$.\end{hint}
	\item Homomorfisme penghubung dalam Proposisi \ref{prop:snake-lemma-mod} bersifat fungtorial. Jelaskan pernyataan ini.
	\item (Lemma Schanuel) Diberikan barisan-barisan eksak pendek dalam $R\dcate{Mod}$
		\begin{gather*}
			0 \to K \to P \xrightarrow{\phi} M \to 0, \\
			0 \to L \to Q \xrightarrow{\psi} M \to 0,
		\end{gather*}
		dengan $P$ dan $Q$ modul kiri $R$ yang projektif.
		\begin{enumerate}
			\item Definisikan submodul $X := \left\{(p,q) \in P \oplus Q: \phi(p) = \psi(q) \right\}$. Tunjukkan bahwa terdapat barisan eksak pendek natural $0 \to L \to X \to P \to 0$ dan $0 \to K \to X \to Q \to 0$;
			\item buktikan bahwa $K \oplus Q \simeq L \oplus P$. \begin{hint} Terapkan Proposisi \ref{prop:proj-mod-characterization}. \end{hint}
		\end{enumerate}
	\item Tetapkan $\Z_{(p)} := \bigcup_{k \geq 0} p^{-k}\Z$. Buktikan bahwa $\Z_{(p)}/\Z$, sebagai modul $\Z$, merupakan modul Artinian tetapi bukan modul Noetherian.
	\item Misalkan $R$ suatu daerah integral dan $K$ medan pecahannya. Jika untuk setiap $x \in K^\times$ berlaku $x \in R$ atau $x^{-1} \in R$, maka $R$ disebut \emph{gelanggang valuasi}\index{gelanggang!valuasi (valuation)} (lihat juga Definisi \ref{def:valuation-ring}).
		\begin{compactenum}[(i)]
			\item Buktikan bahwa setiap ideal terbangkitkan hingga dalam gelanggang valuasi $R$ merupakan ideal utama;
			\item buktikan bahwa gelanggang valuasi $R$ Noetherian jika dan hanya jika $R$ merupakan gelanggang ideal utama;
			\item tunjukkan bahwa $\CC\llbracket t \rrbracket$ merupakan gelanggang valuasi Noetherian, sedangkan $\bigcup_{n \geq 1} \CC \llbracket t^{1/2^n} \rrbracket$ merupakan gelanggang valuasi non-Noetherian.
		\end{compactenum}
	\item Definisikan modul $\Z$, $D := \R \dotimes{\Z} (\R/\pi\Z)$, dengan $\pi$ menyatakan konstanta lingkaran. Buktikan bahwa dalam $D$ berlaku $a \otimes b = 0 \iff a = 0 \;\text{atau}\; b \in \Q\pi$.
		\begin{hint}
			Implikasi $\impliedby$ lebih mudah. Untuk $\implies$, salah satu caranya ialah menyatakan $\R$ sebagai kolimit terfilter $\varinjlim$ dari semua submodul $\Z$ terbangkitkan hingga $M$. Proposisi \ref{prop:tensor-mod-exact} kemudian memberikan $D \simeq \varinjlim_M \left( M \dotimes{\Z} \R/\pi\Z \right)$, dan ruas kanan tetap merupakan kolimit terfilter. Jadi, jika $a \in \R \smallsetminus \{0\}$ memenuhi $a \otimes b = 0$, terdapat submodul $\Z$ terbangkitkan hingga $M \subset \R$, $M \supset \Z a$, sehingga $a \otimes b \mapsto 0 \in M \dotimes{\Z} \R/\pi\Z$; gunakan Teorema Faktor Elementer \ref{prop:elementary-divisor-sub} untuk membuktikan bahwa dalam keadaan ini harus berlaku $b \in \Q\pi$.
		\end{hint}
	\item (Masalah ketiga Hilbert) Menurut definisi, suatu polihedron dalam ruang Euklides tiga dimensi $\mathbb{E}^3$ (yang menjadi $\simeq \R^3$ setelah titik asal dipilih) adalah subhimpunan terbatas $P$ yang diperoleh sebagai irisan berhingga setengah-ruang $H_\alpha = \{x \in \mathbb{E}^3: \alpha(x) \geq 0 \}$, dengan $\alpha: \mathbb{E}^3 \to \R$ suatu fungsi afin. Secara konkret, objek-objek ini tidak lain ialah polihedron ruang yang dikenal dari matematika sekolah menengah, misalnya
	\begin{center}\begin{tikzpicture}
		\coordinate (pic) at (0,0);
		\begin{scope}[shift=(pic), scale=0.8, rotate=-15]
			\coordinate (T) at (pic);
			\coordinate (A) at (-4.5em, -6em);
			\coordinate (B) at (4.5em, -6em);
			\coordinate (C) at (0, -9em);
		\end{scope}
		\draw[fill=gray!10, opacity=0.6] (A) -- (C) -- (B);	% Sisi bawah
		\draw[loosely dashed, opacity=0.6] (A) -- (B);
		\draw[fill=gray!10, opacity=0.6] (T) -- (A) -- (C);	% Sisi kiri
		\draw[fill=gray!25, opacity=0.6] (T) -- (B) -- (C) --cycle;	% Sisi kanan
	\end{tikzpicture} \qquad \begin{tikzpicture}
		\coordinate (pic) at (0,0);
		\begin{scope}[shift=(pic), scale=0.8]
			\coordinate (A1) at (pic);
			\coordinate (A2) at (6em, 2em);
			\coordinate (A3) at (10em, 0);
			\coordinate (A4) at (4em, -2em);
			\coordinate (B1) at (5em, 5em);
			\coordinate (B2) at (5em, -5em);
		\end{scope}
		
		\begin{scope}[loosely dashed, opacity=0.6]
			\draw (A1) -- (A2) -- (A3);
			\draw (B1) -- (A2) -- (B2);
		\end{scope}
		\draw[fill=gray!10,opacity=0.6] (A1) -- (A4) -- (B1);
		\draw[fill=gray!20,opacity=0.6] (A1) -- (A4) -- (B2);
		\draw[fill=gray!30,opacity=0.6] (A3) -- (A4) -- (B1);
		\draw[fill=gray!50,opacity=0.6] (A3) -- (A4) -- (B2);
		\draw (B1) -- (A1) -- (B2) -- (A3) --cycle;
	\end{tikzpicture}\end{center}
	dan sebagainya. Dua polihedron disebut kongruen jika keduanya dapat ditumpangtindihkan melalui serangkaian translasi, pencerminan, dan rotasi. Selanjutnya, kita meninjau polihedron hanya hingga kekongruenan. Definisi yang ketat termasuk dalam analisis konveks.
	
	Jika dua polihedron $P, P'$ masing-masing dapat dipotong menjadi banyaknya bagian polihedron kecil yang sama (misalnya dengan pemotongan oleh bidang)
	\[ P = P_1 \cup \ldots \cup P_r, \quad P' = P'_1 \cup \cdots \cup P'_r \]
	sehingga setiap $P_i$ kongruen dengan $P'_i$, maka $P$ dan $P'$ disebut \emph{kongruen-pembedahan}. Sewajarnya, setiap konsep volume polihedron yang masuk akal harus invarian terhadap kongruensi-pembedahan; definisi yang bersesuaian juga tersedia dalam ruang dua dimensi $\mathbb{E}^2$. Untuk mempelajari volume polihedron, Euklides menggunakan apa yang disebut metode penghabisan Eudoksos dalam Buku XI \emph{Unsur-unsur}, suatu pendahulu konsep limit modern. Banyak matematikawan, termasuk Gauss, tidak sepenuhnya puas dan bertanya apakah kesamaan volume dua polihedron dapat diputuskan melalui metode pembedahan elementer. Jawabannya afirmatif dalam dua dimensi (Teorema Bolyai--Gerwien; lihat \cite[Theorem 24.7]{Har00}), sedangkan kasus tiga dimensi merupakan salah satu masalah yang diajukan Hilbert pada Kongres Matematikawan Internasional tahun 1900. Berikut garis besar jawaban negatif M.\ Dehn.
		\begin{enumerate}[(i)]
			\item Untuk setiap rusuk $E$ dari polihedron $P$, tuliskan panjangnya sebagai $\ell(E) \in \R$. Sudut dihedralnya $\angle E \in \R/\pi\Z$ didefinisikan sebagai berikut: pilih suatu bidang $L$ yang melalui titik interior $x$ dari $E$ dan tegak lurus terhadap $E$; sudut dalam poligon $L \cap P$ pada verteks $x$ ialah $\angle E$. Definisikan invarian Dehn dari $P$ sebagai
				\[ \delta(P) := \sum_{E: \text{rusuk}} \ell(E) \otimes \angle E \quad \in A. \]
				% Gambar
				Buktikan bahwa $\delta$ untuk setiap kubus adalah $0$. Buktikan bahwa $\delta$ untuk suatu tetrahedron beraturan dengan panjang rusuk $\ell$ adalah $6\ell \otimes \arccos(\frac{1}{3})$.
			\item Buktikan bahwa jika suatu bidang $\alpha=0$ dalam ruang memotong polihedron $P$ menjadi dua bagian $P = P_+ \cup P_-$, dengan $P_{\pm} := P \cap \{\pm\alpha \geq 0 \}$, maka $\delta(P) = \delta(P_+) + \delta(P_-)$. Dengan demikian, invarian Dehn dipertahankan oleh kongruensi-pembedahan.
				\begin{hint}
					Tinjau rusuk-rusuk baru yang dihasilkan oleh irisan bidang $\alpha=0$; keadaan tipikal mencakup yang berikut.
					\begin{center}\begin{tikzpicture}[scale=0.7]
						\fill[gray!25] (0,0) rectangle (2.3, 1.7);
						\draw (0,0) -- (-1,2); \draw (0,0) -- (1,2); \draw[ultra thick] (0,0) -- (2.3, 0);
						\draw (0,0) -- (0,1.7);
					\end{tikzpicture} \qquad \begin{tikzpicture}[scale=0.7]
						\fill[gray!25] (0,0) rectangle (2.3, 1.7);
						\draw (0,0) -- (-1,2); \draw (0,0) -- (1,2); \draw (0,0) -- (2.3, 0);
						\draw[ultra thick] (0,0) -- (0,1.7);
					\end{tikzpicture} \\ \vspace{2em}
					\begin{tikzpicture}[scale=0.7, rotate=-20]
						\fill[gray!25] (0,0) -- (1,2) -- (-1,2) --cycle;
						\draw (-2.5, 0) -- (2, 0);
						\draw[ultra thick] (0,0) -- (1,2); \draw[dashed, ultra thick] (0,0) -- (-1,2);
						\draw (-2.5,0) -- (-3.5, 2); \draw (-2.5,0) -- (-1.5, 2);
					\end{tikzpicture} \qquad \begin{tikzpicture}[scale=0.7, rotate=-20]
						\fill[gray!25] (0,0) -- (1,2) -- (-1,2) --cycle;
						\draw (0,0) -- (1,2); \draw[dashed] (0,0) -- (-1,2);
						\draw[ultra thick] (0,0) -- (-2.5,0); \draw[ultra thick] (0,0) -- (2,0);
						\filldraw[fill=white] (0,0) circle[radius=3pt];
						\draw (-2.5,0) -- (-3.5, 2); \draw (-2.5,0) -- (-1.5, 2);
					\end{tikzpicture}\end{center}
					Garis tebal menyatakan rusuk baru yang sedang ditinjau, sedangkan daerah berarsir ialah bagian yang dipotong oleh bidang. Gunakan sifat hasil kali tensor untuk memperoleh $\delta(P) = \delta(P_+) + \delta(P_-)$.
				\end{hint}
			\item Buktikan bahwa suatu tetrahedron beraturan tidak mungkin kongruen-pembedahan dengan sebuah kubus, walaupun volumenya dapat sama. \hint{Masalah ini tereduksi menjadi $\arccos(\frac{1}{3}) \notin \Q\pi$. Pembaca dapat mencoba memberikan argumen langsung, atau menerima Proposisi \ref{prop:cos-rationality} yang akan dibuktikan kemudian.}
		\end{enumerate}
		Catatan: J.-P.\ Sydler (1965) membuktikan bahwa dua polihedron $P, P'$ dalam $\mathbb{E}^3$ kongruen-pembedahan jika dan hanya jika keduanya mempunyai volume dan invarian Dehn yang sama.
	\item Buktikan bahwa konstruksi $A \mapsto A^\vee$ dalam Korolari \ref{prop:finite-duality} memberikan suatu ekuivalensi dari kategori grup abelian berhingga $\cate{FinAb}$ ke $\cate{FinAb}^\text{op}$, dan tunjukkan bahwa konstruksi tersebut merupakan fungtor eksak.
	\item Untuk suatu grup abelian bereksponen $A$, buktikan bahwa homomorfisme $\iota_A$ dalam \eqref{eqn:ab-group-duality} bersifat injektif.
		\begin{hint} Kasus grup siklik mudah ditangani. Gunakan sifat bahwa $\Q/\Z$ merupakan modul $\Z$ yang dapat dibagi untuk beralih ke kasus umum. \end{hint}
	\item Lengkapi pembuktian Proposisi \ref{prop:5-lemma-mod} dengan pengejaran diagram.
\end{Exercises}"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_read(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
        raise RuntimeError(f"noncanonical encoding/newlines: {path}")
    return data.decode("utf-8", errors="strict")


def main() -> None:
    tail_bytes = TAIL.read_bytes()
    tail_text = strict_read(TAIL)
    if r"\begin{Exercises}" not in tail_text:
        if digest(tail_bytes) != INITIAL_TAIL_SHA256:
            raise RuntimeError("unrecognized unrepaired tail candidate")
        indecomposable_at = tail_text.index(INDECOMPOSABLE_MARKER)
        remainder_at = tail_text.index(SEMISIMPLE_REMAINDER_MARKER)
        if remainder_at <= indecomposable_at:
            raise RuntimeError("unexpected tail block order")
        prefix = tail_text[:indecomposable_at].rstrip()
        indecomposable = tail_text[indecomposable_at:remainder_at].strip()
        semisimple_remainder = tail_text[remainder_at:].strip()
        # The translated prefix already contains the Hom-matrix consequence in
        # source position.  Keep it there; do not duplicate it near Exercises.
        if r"\ref{prop:Hom-matrix}" not in prefix:
            prefix = "\n\n".join((prefix, MISSING_PARAGRAPH))
        repaired = "\n\n".join((prefix, semisimple_remainder, indecomposable, EXERCISES)) + "\n"
        TAIL.write_text(repaired, encoding="utf-8", newline="\n")

    segment_texts = [strict_read(path).rstrip("\n") for path in SEGMENTS]
    complete = "\n".join(segment_texts) + "\n"
    COMPLETE.write_text(complete, encoding="utf-8", newline="\n")

    print(f"tail_sha256={digest(TAIL.read_bytes())}")
    print(f"tail_bytes={TAIL.stat().st_size}")
    print(f"complete_sha256={digest(COMPLETE.read_bytes())}")
    print(f"complete_bytes={COMPLETE.stat().st_size}")


if __name__ == "__main__":
    main()
