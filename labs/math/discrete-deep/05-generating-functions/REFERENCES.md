# References: Generating Functions

## Primary Sources

- **Leonhard Euler, "De fractionibus continuis" (1737)** and **"Methodus generalis summandi series" (1744)** — Euler's earliest systematic use of infinite products and series manipulation; the Basel-problem derivation (sin x)/x = Π(1 − x²/n²π²) appears in this line of work (1735 announcement).
- **Leonhard Euler, *Introductio in analysin infinitorum*, Vol. 1 (1748)** — Chapters 10–14 on power series, the partition product Π(1 − xⁿ)⁻¹, and the pentagonal number theorem.
- **Pierre-Simon Laplace, *Théorie analytique des probabilités* (1812)** — probability-generating functions and the analytic treatment of combinatorial sums.
- **Srinivasa Ramanujan, "On certain arithmetical functions" (Trans. Camb. Phil. Soc. 22, 1916)** — the Hardy–Ramanujan asymptotic for p(n) and the Rogers–Ramanujan identities, developed from generating-function/saddle-point analysis.
- **George Pólya, "Kombinatorische Anzahlbestimmungen für Gruppen, Graphen und chemische Verbindungen" (Acta Math. 68, 1937)** — cycle-index generating functions for counting up to symmetry.

## Textbooks

- **Herbert Wilf, *generatingfunctionology*, 2nd ed. (Academic Press, 1994)** — free from the author's website; the standard first book. Chapter 1 states the golden rule: "the coefficient of xⁿ in a GF is the answer to the counting question."
- **Richard Stanley, *Enumerative Combinatorics*, Vol. 1, 2nd ed. (Cambridge, 2011)** — Ch. 1 (the twelvefold way: ordinary vs exponential GFs by structure type), Ch. 2 (generating functions), Ch. 3 (the sieve).
- **Ronald Graham, Donald Knuth, Oren Patashnik, *Concrete Mathematics*, 2nd ed. (Addison-Wesley, 1994)** — Ch. 7 (generating functions): sums, products, partial fractions, and the generating-function proofs of binomial identities.
- **John Riordan, *An Introduction to Combinatorial Analysis* (Princeton, 1958)** and ***Combinatorial Identities* (Wiley, 1968)** — the mid-century codification of GF techniques and coefficient tables.
- **Eli Goodman, *Applied Combinatorics*, Ch. 5** or **Alan Tucker, *Applied Combinatorics*, 6th ed. (Wiley, 2012)** — undergraduate treatment with worked recurrence solutions.
- **Jonathan Cutler & Alexander Root, *Partitions, Motifs, and Graphs* (CMS, 2015)** — modern exercises in GF-based enumeration.

## Analysis of Algorithms

- **Philippe Flajolet & Robert Sedgewick, *Analytic Combinatorics* (Cambridge, 2009)** — free from the authors; the definitive symbolic-method treatment: combinatorial classes → GFs → asymptotics via singularity analysis (Ch. I–IV).
- **Donald Knuth, *The Art of Computer Programming*, Vol. 1, 3rd ed. (1997), §1.2.5.6 and §1.2.9** (generating functions and power series methods) and **Vol. 4A (2011), §7.2.1.4** (generating functions for combinatorial generation).
- **Rémy's analysis of random binary trees / Knuth TAOCP Vol. 3, §5.1.4–5.1.5** — tree enumeration and expected costs via generating functions.

## Related Techniques

- **Herbert Wilf, *discrete mathematics* and the "kernel method" surveys**, plus **Bousquet-Mélou's and Delest's papers on the kernel method (1990s)** — extracting coefficients from functional equations like F = x + zF² without solving for F.
- **E. M. Wright et al., *An Introduction to the Theory of Numbers*, 5th ed. (Hardy, Wright, Aigner, 5th ed. 1979), Ch. 10** — partitions and Euler's theorems in context.
- **Berlekamp's algorithm / Berlekamp–Massey**: E. R. Berlekamp, *Algebraic Coding Theory* (McGraw-Hill, 1968); J. L. Massey, "Shift-register synthesis and BCH decoding" (IEEE Trans. IT, 1969) — the rational-GF ↔ shortest-recurrence algorithm used in cryptanalysis.
