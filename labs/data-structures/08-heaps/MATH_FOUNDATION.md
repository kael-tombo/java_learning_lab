# MATH_FOUNDATION — Heaps (Advanced Use) (`08-heaps`)
> Amortized analysis · load-factor math · height proofs. Proofs over hand-waving.

## 1. Amortized analysis: array doubling (aggregate method)
Append to empty array with doubling (1,2,4,8,…). Resizes at powers of 2 cost 1+2+4+…+n ≈ 2n.
n appends ⇒ total ≤ 3n (n writes + ≤2n copies) ⇒ amortized O(1) each.
- Potential method: Φ = 2·size − capacity; each cheap append pays $1 forward; resize spends savings.
- Contrast linear growth (+k): Σ n/k resizes × O(n) ⇒ O(n²) total ⇒ amortized O(n). Never grow by constant.
- Java: `ArrayList` grows ~1.5×; same geometric argument, different constant.

## 2. Load factor and hashing math (α = n/m)
- Uniform hashing: expected chain length = α; successful search ≈ 1 + α/2, unsuccessful ≈ 1 + α (chaining).
- Open addressing (linear probing): expected probes ≈ ½(1 + 1/(1−α)) (hit) and ½(1 + 1/(1−α)²) (miss) — blows up as α→1.
- Rule: resize at α ≈ 0.75 (Java `HashMap`); keeps chains short, probes bounded.
- Birthday intuition: collisions arrive long before m ≈ n; with m=365, n=23 ⇒ >50% collision — hence rehash + good avalanche.
- Sizing exercise: want ≤1% miss penalty with linear probing ⇒ solve ½(1+1/(1−α)²) ≤ 2 ⇒ α ≤ ~0.5. Show work.

## 3. Height proofs: trees / heaps / tries
- Perfect binary tree: n = 2^(h+1) − 1 ⇒ h = ⌊log₂ n⌋. Complete heap ⇒ same bound ⇒ sift O(log n).
- BST worst case (sorted insert, no balance): h = n−1 ⇒ O(n). Balanced (AVL): h ≤ 1.44·log₂(n+2) (Fibonacci-tree lower bound).
- AVL sketch: minimal nodes N(h) = N(h−1)+N(h−2)+1 ⇒ N(h) ≥ φ^h ⇒ h = O(log n), φ golden ratio.
- Trie: depth = key length L, independent of n; worst nodes ≤ Σ|words|; shared prefixes divide cost.
- Bloom: FPR p ≈ (1 − e^(−kn/m))^k; optimal k = (m/n)·ln2; m = −n·ln p / (ln2)². Example: n=1e6, p=1% ⇒ m≈9.6e6 bits (~1.2MB), k≈7.

## 4. Recurrences you should solve cold
- Binary search / BST step: T(n)=T(n/2)+O(1) ⇒ O(log n) (Master / iteration).
- Merge / heap-build naive: T(n)=2T(n/2)+O(n) ⇒ O(n log n); bottom-up heapify ⇒ O(n) (heights-weighted sum Σ h·n/2^h).
- DFS/BFS: each vertex+edge once ⇒ O(V+E); Dijkstra with binary heap ⇒ O((V+E) log V).

## 5. Probability quick-kit (hashing + bloom + skip/treap intuition)
- Linearity of expectation: expected chain = Σ Pr[collision_i] = α.
- Union bound for FPR reasoning; independence assumption for k hashes (use double-hashing in practice).
- Amortized expected O(1) hash op = hashing O(key) + O(1) probes + (1/n)·O(n) resize share.

## 6. Worked numeric examples
1. Doubling from 8, 100 appends: copies at 8,16,32,64 ⇒ 120 copies + 100 writes = 220 ops ⇒ 2.2/op.
2. HashMap n=10k, m=16k (α=0.625): expected chain 0.625; miss probes ~1.6 chaining.
3. Heap n=1e6: h=19 ⇒ ≤19 swaps per pop; 1e6 pops ≈ 19e6 swaps worst.
4. Bloom n=100k, p=0.1%: m = −1e5·ln(1e-3)/(ln2)² ≈ 1.44e6 bits (~180KB), k ≈ 10.

## 7. Exercises (do with pen)
- Prove Σ_{i=0}^{⌊log n⌋} 2^i < 2n and map each term to a resize copy.
- Derive optimal bloom k by minimizing (1−e^(−kn/m))^k over k (take logs, differentiate).
- Show linear-probing miss cost → ∞ as α→1 using the formula above.
- Prove AVL height bound via N(h) recurrence (induction to φ^h).

## 8. Queueing + caching math you will reuse- Ring buffer: `head/tail mod m`; full vs empty needs a wasted slot or a size counter — prove both work.
- Little's Law L = λW: with arrival rate λ and wait W, queue holds L items ⇒ size your buffer from (λ, W) SLOs.
- LRU locality: hit-rate curves are concave — doubling cache past the working set buys ~nothing; measure, don't guess.

## 9. Worked proof: bottom-up heapify is O(n)
Naive: n pushes × O(log n) = O(n log n). Bottom-up: at height h there are ≤ n/2^(h+1)
nodes, each sifted ≤ h steps. Total ≤ Σ h·n/2^(h+1) = n·Σ h/2^(h+1) = n·1 = O(n),
since Σ h·x^h = x/(1−x)² → 1 at x=1/2. Moral: count work per level, not per node.
Same technique bounds trie build (Σ shared-prefix savings) and rehash chains (Σ α^i).

## 10. Checklist
- [ ] Can reproduce doubling proof and α formulas without notes.
- [ ] Can size a hash table and a bloom filter from (n, p) targets.
- [ ] Can state when O(log n) holds vs collapses to O(n).
