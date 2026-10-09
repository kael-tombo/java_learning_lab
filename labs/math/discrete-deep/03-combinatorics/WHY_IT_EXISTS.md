# Why Combinatorics Exists

## Born From an Unfinished Game

In 1654 Antoine Gombaud, Chevalier de Méré, challenged Pascal with two dice bets. He expected "at least one 6 in 4 rolls" and "at least one double-6 in 24 rolls of two dice" to be equally favorable, because 4/6 = 24/36 — but the first wins with probability 1 − (5/6)⁴ ≈ 51.7% while the second wins only 1 − (35/36)²⁴ ≈ 49.1%. His error was adding probabilities linearly instead of counting sequences: Pascal's exchange with Fermat on dividing stakes in an unfinished game ("the problem of points") settled it by listing equally likely futures and dividing. Combinatorics exists because someone had money on the line and the arithmetic of arrangements disagreed with intuition.

## Counting Must Come Before Expectation

Every probability statement is a ratio of two counts: P(E) = |E| / |Ω|. You cannot define the chance of two people sharing a birthday until you can count the birthday tuples with no collision (365·364·…·(365−n+1)) and the total (365ⁿ). Combinatorics is the arithmetic that makes probability well-defined on finite spaces; Laplace said as much in 1812 when he made counting the technical core of his *Théorie analytique*.

## It Is the Cost Model of Discrete Algorithms

Before analyzing any algorithm that manipulates subsets, permutations, or assignments, you must know how many such objects exist: 2ⁿ subsets, n! permutations, nⁿ functions, C(n,k) k-cliques. That count *is* the lower bound — any algorithm that must output every object runs in Ω(output size). Combinatorics was systematized in computer science precisely because complexity theory needed these lower bounds: you cannot prove a problem hard without first counting its search space.

## The Twofold Origin: Games and Nature

Probability began as a gambling question (Pascal–Fermat, 1654 — stakes divided by counting futures), and enumeration kept returning through chemistry: Cayley counted alkane isomers in the 1870s to organize the periodic table's predecessors, and Pólya's 1937 theorem counted molecules "up to rotation." Both origins show the pattern: a concrete practitioner needs an exact integer, no closed form is obvious, and a new counting device (bijection, GF, sieve) gets invented to produce it.

## Real Objects Need Enumerations

Chemistry counts molecular isomers (Cayley counted alkane isomers in the 1870s), biology counts k-mers and gene orderings, scheduling counts timetables, and testing counts combinations of parameters. In each case a scientist asked "how many possible X?" and needed a formula or a generator — the practical demand that has driven the field from Pascal through Euler to Stanley.

## The "How Many" Questions Are the Easiest to State, the Hardest to Settle

"Number of partitions of n," "number of Latin squares of order n," "number of graphs with n vertices" are one-sentence questions with no closed forms after centuries of effort — but excellent asymptotics (Hardy–Ramanujan: partitions p(n) ~ e^(π√(2n/3))/(4n√3)). Combinatorics exists as a discipline because exact counts resist algebraic tools and required new ones: bijections, generating functions (lab 05), the inclusion–exclusion sieve, and creative telescoping — and because each new counting tool (Pólya's cycle index, the transfer-matrix method, holonomic creative telescoping) immediately answered a backlog of previously stuck questions.

## It Connects Algebra to Counting

Vandermonde's identity Σ_k C(r,k)C(s, n−k) = C(r+s, n) is both a counting statement (split a committee by source) and an identity about polynomial coefficients. The bridge — counting coefficient extraction in products — is what makes generating functions work, and it is why combinatorics in a curriculum sits immediately before generating functions: the two are the same subject seen from the enumeration side and the algebraic side.

## The Short Answer

Combinatorics exists because someone had to answer "how many?" before anyone could ask "how fast?" — counting is the arithmetic that makes probability, complexity bounds, and enumeration well-defined, in that order of historical necessity.
