# MATH_FOUNDATION — Searching (Linear/Binary/Hash)
> Recurrences, Master theorem, amortized analysis for searching.

## 1. Recurrences (tailored)
- Binary: `T(n)=T(n/2)+Θ(1)` (one probe + half).
- Linear: `T(n)=T(n-1)+Θ(1)` → `Θ(n)` (peel one per step).
- Interpolation (uniform): expected `O(log log n)` — non-Master, distribution-dependent.
- BST search: avg `Θ(log n)` (random), worst `Θ(n)` (degenerate = linear recurrence).
- Hash lookup: `Θ(1)` expected via load-factor chain length.

## 2. Master Theorem
- Binary: `a=1,b=2,f=1` → `n^{0}=1`, case 2 → `Θ(log n)`.
- Linear-form `T(n)=T(n-1)+1` not Master (b=1) — unroll directly.
- Merge-sort contrast `2T(n/2)+n` → `Θ(n log n)` (why sorting dominates searching).
- Case-1 example: `T(n)=T(n/2)+1/n` still `Θ(log n)` (summable tail).
- Regularity reminder for case 3 (not needed here, but state it).

## 3. Counting / Expectation
- Linear avg (present uniform): `(n+1)/2` probes; absent: `n`.
- Binary worst: `⌊log₂n⌋+1` probes (decision-tree depth).
- Decision-tree lower bound: `n+1` outcomes → height `≥ ⌈log₂(n+1)⌉`.
- Hash expected chain: `α=n/m`; successful `1+α/2`, unsuccessful `1+α` (uniform hashing).

## 4. Amortized Analysis
- Resizing hash table: doubling aggregate `O(1)` amortized insert → keeps `α` bounded.
- Potential `Φ=2n−m` (elements vs buckets) mirrors array doubling.
- Splay/move-to-front: static-optimality amortized (brief note, extras).
- Sorted-array inserts `Ω(n)` worst each — no amortization saves it; use balanced BST.

## 5. Probabilistic Notes
- Uniform hashing assumption load-bearing; adversarial keys → worst `Θ(n)` chain.
- Universal hashing derandomizes; Bloom prefilter trades FPs for probes.
- Interpolation needs uniform gap distribution else degrades to `O(n)`.

## 6. Worked Numbers
- `n=10⁶`: linear avg 500k probes vs binary 20 vs hash ~1–2.
- `log₂10⁶≈20`; `log₂10⁹≈30` — binary scales to billions cheaply.
- Load `α=0.75`: miss cost `1.75` probes expected.

## 7. Exercises
- [ ] Unroll binary recurrence to `log n`.
- [ ] Derive `(n+1)/2` linear expectation.
- [ ] Decision-tree lower-bound proof sketch.
- [ ] Aggregate proof for table doubling in hash resize.
