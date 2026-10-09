# How It Works: Core Set Mechanics

## 1. HashSet Add/Contains, Step by Step

Inserting x into a `HashSet`:

1. `hash = x.hashCode()`; spread it: `hash ^= (hash >>> 16)` — mixes high bits down so a table of 16 buckets doesn't ignore them.
2. `i = (table.length − 1) & hash` picks the bucket (length is a power of two).
3. If the bucket is empty, create a node there. If occupied, walk the list (or the red-black tree when the bin has ≥ 8 entries and the table has ≥ 64 buckets) comparing `hash` then `equals()`.
4. If an equal element exists, do nothing (set semantics) and return false.
5. If not, append the node; increment size; if size > 0.75 × capacity, double the table and rehash every node into its new bucket.

Contains is steps 1–3 with an early true on match. Average O(1) because a good hash spreads elements uniformly; O(n) if every key lands in one bucket.

## 2. Union of Two HashSets

`a.addAll(b)` iterates each element of b, computes its bucket, and inserts if absent. Cost: Θ(|b|) hash computations plus Θ(|a|) on any resize — expected O(|a| + |b|). Elements already in a fail their `equals` check and are skipped, which is where the idempotence of ∪ comes from mechanically.

## 3. Power Set by Integer Mask

For A = {x₀, x₁, …, xₙ₋₁}, loop `mask` from 0 to 2ⁿ − 1; include xᵢ iff `(mask >>> i) & 1 == 1`. Every subset corresponds to exactly one binary vector, so no duplicates and none missing — the bijection between P(A) and {0,1}ⁿ. Total work O(n·2ⁿ).

## 4. Subset Lattice Generation

An alternative: start with [∅] and repeatedly, for each subset in the list, add each element not yet present, deduplicating. This builds level k from level k−1 and is exactly how Pascal's row sums arise: the number of ways to reach a k-subset is Σ over its (k−1)-subsets.

## 5. Complement Needs a Universe

`Aᶜ` is not computable from A alone: a loop over A can only tell you what is *in* A; "everything else" requires U. In code: `Set<T> comp = new HashSet<>(universe); comp.removeAll(A);` — Θ(|U|). With a `BitSet` you additionally need `universeSize`, because trailing zero words are indistinguishable from "not yet allocated."

## 6. Characteristic-Vector Evaluation

To evaluate A ∩ B on vector a, b (n bits): `for (w = 0; w < words; w++) c[w] = a[w] & b[w];` — Θ(⌈n/64⌉) word ops regardless of density. This is why dense set algebra runs at memory-bandwidth speed: one AND per 64 elements, no per-element branching or hashing.

## 7. Cantor's Argument as an Algorithmic Contradiction

Given any supposed list r₁, r₂, … of [0,1), the diagonal procedure *computes* a real not on the list in O(k) per digit k. The contradiction is effective: no program can output a complete list of all reals — uncountability is, constructively, "you cannot write the loop that enumerates them."
