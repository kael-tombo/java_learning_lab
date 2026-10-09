# History: Set Theory

## Before Sets Had a Name

**Euclid (c. 300 BC)** reasoned about magnitudes and numbers in the *Elements*, using an implicit notion of "the whole is greater than the part." He had no notion of a set as an object; "collection" was never axiomatized in antiquity.

**Bernard Bolzano (1817)** and **Richard Dedekind (1872)** probed the foundations of the real numbers. Dedekind's *Stetigkeit und irrationale Zahlen* defined real numbers as cuts in the rationals — a construction that only makes sense if you can treat "the set of rationals less than r" as a single mathematical object.

## Cantor and the Crisis of Infinity

**Georg Cantor (1845–1918)** proved in 1874, in *Über eine Eigenschaft des Inbegriffs aller reellen algebraischen Zahlen*, that the real numbers cannot be listed: the algebraic numbers are countable, the reals are not, so most reals are transcendental. This was the first uncountability proof and the birth of transfinite cardinal arithmetic.

Cantor introduced the continuum hypothesis (1878) — that no set has cardinality strictly between ℕ and ℝ — and the diagonal argument (1891) showing |P(A)| > |A| for every set A. His *Beiträge zur Begründung der transfiniten Mengenlehre* (1895–1897) systematized ordinals and cardinals.

**Kronecker's** public hostility ("God made the integers, all else is the work of man") and **Poincaré's** skeptical editorials turned the topic into a controversy; the reaction later hardened into the formalist program.

## Paradoxes Force Axioms

**Gottlob Frege (1848–1925)** built arithmetic on extensions of concepts in *Grundgesetze der Arithmetik* (Vol. 1, 1893; Vol. 2, 1903). In June 1901 **Bertrand Russell** wrote to Frege pointing out that the extension of "is not a member of itself" yields a set both in and not in itself — the completion of Volume 2 carries Frege's famous apology admitting the basic law of his system was inconsistent.

**Ernst Zermelo (1871–1953)** answered in 1908 with the first axiomatization of set theory: extensionality, pairing, power set, union, separation (a restricted replacement of Frege's unrestricted comprehension), infinity, and a choice principle. The axioms were chosen to prove exactly what mathematics needed while blocking Russell's paradox — separation only forms {x ∈ A : φ(x)} from an already-given A.

**Abraham Fraenkel (1891–1965)** and **Thoralf Skolem (1887–1963)** added the axiom of replacement in 1922, and the resulting system became **ZFC** — Zermelo–Fraenkel with Choice — the default foundation of modern mathematics.

## Consistency and Independence

**Kurt Gödel (1906–1978)** showed in 1938–1940 that if ZFC is consistent then ZFC + constructible universe L (hence the continuum hypothesis) is consistent: CH cannot be refuted. **Paul Cohen (1934–2007)** invented forcing in 1963 and proved CH cannot be proved from ZFC — the independence result that earned him the Fields Medal.

**John von Neumann (1903–1957)** proposed the von Neumann ordinal construction (1923) still used in textbooks and programming models, and the NBG class theory that lets you talk about "the class of all sets" without contradiction. **Kazimierz Kuratowski (1891–1983)** gave the 1921 ordered-pair definition (a, b) = {{a}, {a, b}} that lets relations and functions be built from sets alone.

## Sets Become a Programming Primitive

**Edsger Dijkstra** argued in 1972 (*Notes on Structured Programming*) that programming variables should carry set-theoretic specifications. Java shipped `java.util.HashSet` in 1998, relying on the `hashCode`/`equals` contract — an engineering compromise Cantor would have recognized as treating each object as an element identified by a membership test.
