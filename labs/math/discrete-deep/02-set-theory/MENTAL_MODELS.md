# Mental Models: Set Theory

## 1. A Set as a Membership Predicate

The most durable picture: a set is not a bag of things, it is a *test*. "Is x in S?" returns true or false. Two sets are equal exactly when their tests agree on every possible object (extensionality). This is why {x : x is prime and x < 10} equals {2, 3, 5, 7} — the definition doesn't matter, only the yes/no answers. In code, a `Predicate<T>` with structural equality behaves like a set.

## 2. Characteristic Functions (0/1 Vectors)

Fix a universe U = {u₁, …, uₙ}. A subset A ⊆ U is a string of n bits: bit i is 1 iff uᵢ ∈ A. Under this dictionary, ∪ is bitwise OR, ∩ is AND, complement is NOT, and difference A − B is `a & ~b`. |A| is the popcount. If two operations ever "feel" wrong, write the bits out — boolean algebra over {0,1} makes the answer mechanical. This is exactly how `BitSet` implements sets.

## 3. The Subset Lattice

Draw P(A) as layers: ∅ at the bottom, singletons above, pairs above that, …, A at the top, with an arrow X → Y when Y = X ∪ {y}. |P(A)| = 2^|A| counts the paths/levels; every element added to A doubles the lattice height-by-count. Complement is the reflection that swaps bottom and top; De Morgan is the statement that this reflection reverses ∪ and ∩.

## 4. Inclusion–Exclusion as an Overlap Audit

Counting |A ∪ B| by |A| + |B| double-counts A ∩ B exactly once, so subtract it. Three sets double-count pairwise intersections and subtract the triple intersection thrice, so add it back. Mental check: keep a Venn diagram in which each region is counted exactly once; the sign alternates by the number of sets covering the region.

## 5. Cardinality as "Can I List It?"

Two sets have the same size iff a bijection exists — even infinite ones. ℕ and the evens are the same size (n → 2n). Cantor's diagonal says no list of reals covers ℝ, so ℝ is strictly bigger than ℕ. When you need to prove two infinite sets "equal," your real work is exhibiting the pairing function.

## 6. Complement Relative to a Universe

"A's complement" is meaningless without a declared universe U; Aᶜ = U − A flips whenever U changes. This mirrors how `Set<String> universe` in a test fixture determines what "not selected" means. Bugs labeled "complement came out wrong" are usually an unstated or mismatched universe.

## 7. Set Builder as a Query

{f(x) : x ∈ D ∧ P(x)} is a SQL query: FROM D, WHERE P, SELECT f, with duplicates collapsed (DISTINCT) because a set holds elements, not occurrences. If you need occurrence counts, you want a multiset/bag — SQL's default — and the theory changes (|A ∪ B| formula needs max, not +).

## 8. Union Grows, Intersection Shrinks, Complement Flips

Track the *direction* of each operation as a sanity check: |A ∪ B| ≥ max(|A|, |B|), |A ∩ B| ≤ min(|A|, |B|), |Aᶜ| = |U| − |A|. If a computed union came back smaller than an input, or an intersection larger than both, the code (or the algebra) inverted the operation — this quick inequality test catches sign/operation mix-ups without constructing a single example.
