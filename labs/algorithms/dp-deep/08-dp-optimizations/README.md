# 08 — DP Optimizations

<div align="center">

**Sliding Window · Monotone Queue · Divide & Conquer · Knuth · SMAWK · Sparse/Linear Space**

</div>

---

## Learning Objectives

- Recognise the three *structural* DP speedups: windowed, monotone, and sub-problem-decomposable
- Turn `O(n·W)` transitions into `O(n)` with a sliding window in `D[i][j] = min(D[i][j-1], f(i,j-k..j))`
- Prove convexity ⇒ monotone optima ⇒ divide & conquer optimisation (`O(n log n)` instead of `O(n²)`)
- State and apply Knuth's `O(n)` quadrangle condition for interval costs
- Explain monotone-deque mechanics: amortised `O(1)` push/pop despite `O(W)` window
- Use `SMAWK` / the totally-monotone matrix idea to go from `O(n log n)` to `O(n)`
- Convert `O(n·K)` space to `O(K)` by noticing which layers are read after they're written
- Recognise when a "DP optimisation" cannot apply and the naive bound stands

## Prerequisites

- `01-dp-classics` — the DAG recurrence framework
- `02-lcs-edit-distance` — a `Θ(nm)` baseline to optimise
- `04-knapsack-variants` — unbounded/0-1 windowing
- `05-matrix-chain-string-dp` — interval DP with quadrangle structure

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 150 minutes
- **Exercises**: 75 minutes
- **Total**: 5 hours

## Key Concepts

| Concept | Trigger | Saves |
|---------|---------|-------|
| **Sliding window** | transition looks at a *contiguous window* of the previous row | `O(nW)` → `O(n)` |
| **Monotone deque** | window with a *monotone* comparison (`min`/`max`) | same, with amortised proof |
| **Knuth optimisation** | interval cost `w(i,j)` is monotone + quadrangle inequality | `O(n³)` → `O(n²)` |
| **Divide & conquer opt** | `opt[i][j] ≤ opt[i][j+1]` (convex/Monge cost) | `O(n²)` → `O(n log n)` |
| **Monotone opt** | same conclusion, computed by pointer-walking | `O(n²)` → `O(n)` |
| **SMAWK** | the `DP` matrix is totally monotone | `O(n²)` → `O(n)` |
| **Aliens trick** | penalty `λ` makes a `k`-track problem solvable in `O(n log V)` | `O(nk)` → `O(n log V)` |
| **Linear memory** | layer `i` depends only on `i−1` (or `i−1..i−c`) | `O(nK)` → `O(K)` |
| **In-place DP** | transitions read the cell before overwriting | halves memory, trickier bugs |
| **Bitset DP** | boolean state over a small alphabet | `O(nm/64)` |

## Complexity Snapshot

| Problem | Naive | Optimised | Technique |
|---------|-------|-----------|-----------|
| Edit distance, min over window | `Θ(nm)` | `Θ(nm)` | baseline |
| Constrained edit distance (windowed) | `Θ(nmW)` | **`Θ(nm)`** | sliding window |
| Max sum of two non-overlapping subarrays | `Θ(n²)` | **`Θ(n)`** | sliding window / prefix-best |
| RNA folding (Nussinov) | `Θ(n³)` | **`Θ(n²)`** | Knuth |
| Optimal BST | `Θ(n³)` | **`Θ(n²)`** | Knuth |
| Matrix chain (already `Θ(n³)`) | `Θ(n³)` | **`Θ(n²)`** | Knuth |
| 1D/1D DP with convex cost | `Θ(n²)` | **`Θ(n log n)`** | D&C optim |
| Same, monotone cost | `Θ(n²)` | **`Θ(n)`** | SMAWK / monotone |
| `k`-segment partition (`O(nk)`) | `Θ(nk)` | `Θ(n log V)` | aliens trick |
| Knapsack by value `Σw` | `Θ(nW)` | `Θ(S)` where `S = Σw` | index by weight |
| Held-Karp TSP | `Θ(n²2^n)` | `Θ(n²2^n)` (memory halved) | linear-space meet-in-middle |
| Small-alphabet boolean DP | `Θ(n·2^k)` | `Θ(n·2^k/64)` | bitset |

**The headline:** most `O(n²)` DP tables in practice are `O(n)` or `O(n log n)` work wearing a
`O(n²)` costume. The table is rarely the problem — the *transition* is.

## Algorithms Covered

### Sliding window — the canonical form
```
D[i][j] = min over t in [j-W, j-1] of ( D[i-1][t] + cost(i, t+1, j) )
```
When `cost` factorises as `A[i] + B[j]` (no `t`-dependence) the window is a straight
`min` over a sliding range → monotone deque. When `cost` depends on `t`, the queue is not
monotone in general and you must fall back to a sparse table or segment tree (`O(n log n)`).

### Knuth's condition
For interval cost `w(l, r)` (1-indexed, inclusive), Knuth applies iff

1. `w(b, c) ≤ w(a, d)` for `a ≤ b ≤ c ≤ d`  (**monotonicity** / "quadrangle inequality" I)
2. `w(a, c) + w(b, d) ≤ w(a, d) + w(b, c)`  (**quadrangle inequality** II)

Then `opt[i][j−1] ≤ opt[i][j] ≤ opt[i+1][j]`, and by walking `k` from `opt[i][j−1]` upward to
`opt[i+1][j]` you get `O(n)` splits per cell → `Θ(n²)` total instead of `Θ(n³)`.
**Intuition:** the convexity makes the optimal split point non-decreasing in both endpoints, so
you never rescan the whole range.

### Divide & conquer optimisation
Assumption: `opt[i][j] ≤ opt[i][j+1]`. Then for each `i` the optimal `k` is monotone in `j`, so
solve rows with recursion, restricting each row's search to `[opt[i][mid−1], opt[i][mid+1]]`.
Cost: `O(n log n)`.

### Monotone / SMAWK
If additionally the optima move *strictly* (strong convexity), you can walk `k` directly instead
of bisecting: `O(n)` per row, `O(n)` total. SMAWK generalises this to totally monotone matrices
(`A[i][j] ≤ A[i'][j']` whenever `i<i'` and `j≤j'`, after row reduction), computing every row
minimum in `O(n)` even though the matrix has `Θ(n²)` entries — the entries are *generated*, not
stored.

## Files

| File | Purpose |
|------|---------|
| `THEORY.md` | Mechanism, conditions, correctness arguments per technique |
| `EXERCISES.md` | Implement each optimisation, prove the `O(n)` amortisation by hand |
| `QUIZ.md` | 15 questions on conditions, invariants, counter-examples |
| `FLASHCARDS.md` | ~60 rapid-recall rows |
| `MATH_FOUNDATION.md` | Recurrences, Knuth's amortised split count, deque potentials |
| `CODE_DEEP_DIVE.md` | Annotated Java for every optimisation + pitfalls |
| `DIAGRAMS/` | Deque evolution, `opt` monotone staircase |