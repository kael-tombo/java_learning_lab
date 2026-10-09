# Interview: Set Theory

## Conceptual Questions

**Q: Difference between ∈ and ⊆? Give an example where both hold and one where they don't.**
A: `3 ∈ {1,2,3}` (element), `{1} ⊆ {1,2,3}` (subset: every member of the left is a member of the right). `{1} ∈ {1,2,3}` is false because the set's elements are 1, 2, 3 — not sets. For a case where both hold: ∅ ⊆ {∅} (vacuously) and ∅ ∈ {∅} (it is the sole element).

**Q: Is ∅ a subset of every set? Is it an element of every set?**
A: Subset yes — there is no x ∈ ∅ that could violate x ∈ A, so the implication holds vacuously. Element no — a set has an element only if someone put one there; ∅ has none. Hence ∅ ⊆ ∅ is true and ∅ ∈ ∅ is false.

**Q: Prove |P(A)| = 2^|A|.**
A: Each subset S ⊆ A corresponds to a unique function χ_S: A → {0,1} (characteristic function), and there are 2 choices per element giving 2^|A| functions; the correspondence S ↔ χ_S is a bijection. For n = 3 this is the eight masks 000…111.

**Q: What does De Morgan's law say, and what is its most common misapplication?**
A: (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ and dually. Misapplication: negating a difference instead of a complement, e.g. claiming (A − B)ᶜ = Aᶜ − Bᶜ, or flipping the operator in code without negating both operands.

**Q: Why can't A − B equal B − A in general?**
A: Symmetry would require x ∈ A ∧ x ∉ B ⇔ x ∈ B ∧ x ∉ A for every x; take A = {1}, B = ∅: A − B = {1} but B − A = ∅. The equality holds iff A = B; the genuinely commutative operation is the symmetric difference.

## Complexity Questions

**Q: Union of two sets — complexities for `HashSet`, `TreeSet`, and `BitSet`?**
A: `HashSet.addAll`: expected O(|B|) hashing plus possible resize, O(|A|+|B|) work total. `TreeSet.addAll`: O(|B|·log(|A|+|B|)). `BitSet.or`: Θ(⌈n/64⌉) word operations over the universe width, independent of density.

**Q: Why is `HashSet` average O(1)? What makes it degrade?**
A: A uniform hash distributes n keys over m buckets so each bucket holds n/m ≈ 1 entry; lookup is one hash plus one comparison. It degrades to O(n) when many keys collide (poor `hashCode`, or adversarial keys exploiting an unkeyed hash function) or when `equals` itself is expensive.

**Q: Deduplicate n log lines by timestamp+level. Choose structure and state complexity.**
A: `HashSet<Key>` with `record Key(long ts, Level lv)`: O(n) expected, or `TreeSet` if you also need sorted output: O(n log n). Identity choice (which fields make two lines "the same") must be written down first — that is the real design decision.

## Applied / Coding Questions

**Q: Implement set difference given two sorted arrays, O(|A|+|B|).**
A: Two pointers: walk a and b; copy a[i] when b[j] != a[i] or b exhausted; advance the smaller of the two. This is a merge, Θ(|A|+|B|) time, no hash structure — sorted input converts hashing into a linear scan.

**Q: Your `HashSet<MyObject>` won't deduplicate. Diagnose in three checks.**
A: (1) Print sizes after each add — growth means identity is broken. (2) Verify `a.equals(b)` and `b.equals(a)` and `a.hashCode() == b.hashCode()` for the pair. (3) Check whether the object's hash fields were mutated after insertion (stale bucket). Fix: write `equals`/`hashCode` together or use a `record`.

**Q: Given a universe of 10⁶ ids and frequent membership tests, what do you use and why?**
A: A `BitSet`: 1,000,000 bits ≈ 125 KB, O(1) test via word + bit shift, cache-friendly bulk union by word OR. A `HashSet<Integer>` would need boxing (≥16 MB for the same dense population) and a hash per lookup.

**Q: How would you test that your set library satisfies De Morgan's laws?**
A: Exhaustively: iterate all subset pairs of a fixed 6–8 element universe (2ⁿ subsets, so (2ⁿ)² pairs), compute both sides with characteristic vectors and with the `Set` API, assert equality for every pair. Exhaustive small-universe testing is a proof for that universe and catches implementation asymmetry immediately.
