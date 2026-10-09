# Why Generating Functions Exist

## Because Unrolling Recurrences Doesn't Scale

The natural way to get a sequence from a recurrence is to compute term after term: Θ(n) work per term, Θ(n²) for the whole table, and no insight into growth. A GF converts the *rule* into an *equation* (rational function), and solving the equation yields aₙ directly — for Fibonacci-like recurrences, one term in O(log n) rather than O(n). The technique exists because "compute every term" and "understand the terms" are different tasks, and only the second one answers questions like "is aₙ ~ c·λⁿ?"

## It Turns Combinatorics Into Algebra

Counting by hand means writing case analyses: splits of n, choices of parts, first-return decompositions. Euler's insight (Basel problem, partition products) was that a sequence of counts can be *multiplied* — and that the algebra of products mirrors the combinatorics of building structures from parts:

- sequence of choices → product of series
- independent alternatives → sum of series
- "sets of things" → exp of an EGF

Once that dictionary exists, hard combinatorial identities become algebraic identities (multiply out, compare coefficients). Vandermonde's convolution, the hockey-stick identity, and the binomial theorem are all one-line coefficient comparisons in GF language.

## It Gives Exact Counting Where Formulas Don't Exist

Partition numbers p(n), graph counts, and restricted compositions have no closed forms — but they all have GFs, and GFs let you compute terms to any n by DP or extract asymptotics from singularities (Hardy–Ramanujan's p(n) formula comes from analyzing the infinite product's behavior near x = 1). The GF *is* the answer when no formula exists: a compact specification from which any coefficient is computable.

## It Unifies Linear Recurrences and Rational Functions

The theorem "a sequence satisfies a constant-coefficient linear recurrence ⟺ its GF is rational" makes GFs the *reason* the characteristic-equation method works: denominator roots are the eigenvalues. This equivalence is not just aesthetic — it powers real machinery: Berlekamp–Massey recovers the shortest recurrence from sequence terms (used in stream-cipher analysis and system identification), and linear-complexity measures are defined via the rational-GF representation.

## It Extends to Labels and Symmetry

Plain counting fails when objects have labels (labeled graphs: 2^(n(n−1)/2) on n vertices) or symmetry (necklaces equivalent under rotation). The exponential GF fixes the first (division by n! built into the coefficients), and Pólya's theorem (with cycle-index GFs) fixes the second by averaging over the symmetry group. Generating functions are the substrate both corrections are built on — they exist partly because unlabelled and labelled enumeration are *different arithmetic*.

## It Is the Bridge to Analysis

Coefficients and functions trade information: growth rates of aₙ ↔ singularity location of A(x), periodicity ↔ roots of unity poles, asymptotics ↔ Darboux/saddle-point methods. This is why analysis of algorithms (generating functions for tree sizes, recursive structures) and analytic number theory (circle method) both run on GFs: they exist to move questions between the discrete sequence and the continuous function, whichever side is easier.
