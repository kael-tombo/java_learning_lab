# History: Generating Functions

## Euler and Infinite Products

**Leonhard Euler** effectively invented generating-function reasoning in *De fractionibus continuis* (1737) and *Methodus generalis* (1744). His solution of the **Basel problem** (1735): start from sin x / x = Π_{n≥1} (1 − x²/n²π²), take logs, differentiate, and compare the coefficient of x² to get Σ 1/n² = π²/6. The move — treating an infinite sequence as coefficients of a formal product — is the entire idea. Euler also used the product Π (1 + xⁿ) = Σ p(n)xⁿ to study partition counts (1748, *Introductio in analysin infinitorum*), and solved the partition recurrence p(n) = Σ (±) p(n − k(3k−1)/2) that Euler himself called his "pentagonal number theorem" (1751).

**Nicolas Bernoulli (1687–1759)** and **Daniel Bernoulli (1700–1782)** used power-series arguments on probability and the St. Petersburg paradox (1738) — among the first sequences handled by summing their generating series. **Jakob Bernoulli's** *Ars Conjectandi* (1713) had already used Bernoulli numbers from sum-of-powers formulas, a pre-history of coefficient manipulation.

## Formalization: Euler to Laplace to Lagrange

Euler's letters to **Christian Goldbach** (1740s–1750s) repeatedly use what we now call ordinary generating functions, but the *formal* treatment — treating the series as an algebraic object with no convergence questions — came later. **Pierre-Simon Laplace (1749–1827)** used probability-generating functions in his 1812 *Théorie analytique des probabilités* (where the moment-generating / characteristic function tradition begins).

**Lagrange inversion** (1770s, in *Théorie des fonctions analytiques*) gives the coefficients of the inverse of a power series — the tool for counting trees and mappings by their functional equations; the full combinatorial interpretation was completed by **Laguerre (1880s)** and **Bôcher (1910)**.

## The Combinatorial Explosion of the 20th Century

**George Pólya (1887–1985)** merged generating functions with symmetry in his enumeration theorem (1937), enabling counts of objects "up to rotation/reflection" (polygons, molecules, necklaces).

**Srinivasa Ramanujan (1887–1920)** used generating functions at full strength: his 1913 letter to Hardy contains the partial theta function identities, the Rogers–Ramanujan identities, and the discriminant Δ = qΠ(1−qⁿ)²⁴ manipulations; his work on the partition function p(n) (with Hardy's circle method, 1918) derived the asymptotic p(n) ~ e^(π√(2n/3))/(4n√3) from the generating function's singular behavior. The circle method *is* generating-function analysis: expand about the rationals where the series is largest.

**Percy MacMahon (1854–1929)**, in *Combinatory Analysis* (1915–1916), systematized multivariate generating functions for partitions and partitions of grids.

## Ordinary vs Exponential: The Distinction Hardens

The need to distinguish *labeled* from *unlabeled* enumeration forced two species of series: ordinary GFs count sequences with unlabeled positions (partitions, binary strings), while **exponential GFs** (EGFs) a(x) = Σ aₙ xⁿ/n! count structures on labeled objects (permutations, set partitions, labeled trees) — where dividing by n! corrects the overcount from ordering labels. **Edward Wright (1907–1975)** and **John Riordan (1910–1991)** codified the combinatorial use: Riordan's *An Introduction to Combinatorial Analysis* (1958) and *Combinatorial Identities* (1968) standardize the bookkeeping, and **Euler's theorem for labeled structures** (the EGF of a set of connected components is exp of the component EGF) became the standard pattern: exp for "sets of," ordinary product for "sequences of."

## Modern Reference Points

**Herbert Wilf's** *generatingfunctionology* (1st ed. 1990, 2nd ed. 1994, free from the author) made the subject teachable and is the standard first text. **Richard Stanley's** *Enumerative Combinatorics* Vol. 1 (1986/2011) treats ordinary, exponential, and multivariate GFs with the twelvefold way as the organizing table. The **kernel method** (used for lattice-path counts by Deloche and Viennot, and earlier by Ramanujan himself for the Rogers–Ramanujan identities) extracts coefficients of equations like f = x + zf² without solving for f explicitly. **Flajolet and Sedgewick's** *Analytic Combinatorics* (2009) completed the analytic side: combinatorial classes map to GFs, and singularities of the resulting functions yield asymptotics for the coefficients.

## The Short Answer

Generating functions exist because Euler compared coefficients of two expansions of the same function and got pi squared over six — after which treating sequences as coefficients stopped being a trick and became a method.
