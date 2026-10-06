# Math Foundation — Cycle Detection

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Floyd correctness

Write the state at slow-step k as position p(k). Once both pointers are in the cycle, p_fast(k) ≡ 2k (mod L) and p_slow(k) ≡ k (mod L), so p_fast ≡ p_slow when k ≡ 0 (mod L). The first such k ≥ t is at most t+L.

Hence they meet within one full loop of the cycle after both enter it.

## Floyd entry-point proof

Let the entry be at distance t from the start, the meeting point at distance k from the start with k ≡ 0 (mod L) and k ≥ t. Starting one pointer at the start and advancing both by 1: after t steps the first pointer is at position t ≡ k + t - k. Since k ≡ 0 (mod L), position t is the same as position k inside the cycle offset by t — the two pointers coincide at the entry.

So the second pass finds the entry in exactly t steps.

## Three-colour DFS and cycles

A directed cycle v₁ → v₂ → … → vₖ → v₁ means that when DFS first reaches v₁, the path v₁ → … → vⱼ is still on the stack (grey). The eventual edge vₖ → v₁ is an edge to a grey vertex — a back edge — so DFS flags the cycle.

Conversely a back edge u → g where g is grey means g is an ancestor of u, and the tree path g ⇝ u plus u → g is a cycle.

## Union-Find cycle test

Adding edge (u,v) where find(u)=find(v): u and v already lie in one component, so there is a path u ⇝ v; adding (u,v) closes a cycle. If find(u)≠find(v), no u–v path exists yet, so the edge cannot close a cycle.

This is exactly the cut/cycle property that Kruskal's algorithm relies on.

## Floyd on a functional graph

The sequence x₀, x₁, …, x_{n} on n+1 states must repeat: x_a = x_b for some a < b. The first repeat is the cycle entry if a = t, and the cycle length is b - a. Advance slow by 1 and fast by 2; the meeting condition is p_slow ≡ p_fast (mod L), i.e. k ≡ 2k - t (mod L) — which holds for k = t mod L.

Hence the method finds t and L in one pass.
