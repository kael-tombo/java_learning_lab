# 05 — Matrix Chain & String DP

<div align="center">

**Matrix Chain Multiplication · Palindrome Partitioning · String Metrics & The Penney Game · Word Break · RNA Folding · Optimal Polygon Triangulation**

</div>

---

## Learning Objectives

- Derive the `Θ(n³)` matrix-chain recurrence and understand why the naive greedy fails
- Explain the four subproblems of a polygonal triangulation problem and how they relate
- Implement palindrome partitioning in `Θ(n²)` and optimise to `Θ(n²)` with `O(n)` space
- Implement the string-edit/alignment DP for **metrics** (`Θ(n²)`) and recognise the Penney-game consequence
- Implement word break (`Θ(n²)`) and explain its connection to the `Θ(nW)` knapsack
- Understand why many of these problems are `Θ(n³)` and what the best-known cubic-time algorithms do
- Recognise the shared structure: **interval DP on a path-like state graph**

## Prerequisites

- `01-dp-classics` — the framework
- `02-lcs-edit-distance` — the 2-D grid DP
- Interval/state-space thinking: the state is a *pair* of indices, not a single index

## Estimated Time

- **Theory**: 95 minutes
- **Practice**: 140 minutes
- **Exercises**: 75 minutes
- **Total**: 5–6 hours

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Interval DP** | the state is a *sub-interval* `[i, j]`, giving `Θ(n²)` states |
| **Split DP** | the transition picks a split point `k` between `i` and `j`, giving `Θ(n³)` |
| Matrix chain | optimise the parenthesisation of `A₁A₂…Aₙ` |
| Triangulation | identical recurrence — polygons and matrix chains are the same problem |
| Palindrome partitioning | minimise cuts so every piece is a palindrome |
| String metrics | longest common substring, prefix/suffix distance, `Θ(n²)` |
| Penney game | two-player string game; its equilibrium is found by a `Θ(n²)` DP over overlap |
| Word break | `dp[i]` = can `s[0..i-1]` be segmented into dictionary words |
| RNA folding | `Θ(n³)` Nussinov: max base pairs subject to no pseudoknots |
| `Θ(n³)` barrier | `n ≤ 500` practical; `n = 1000` ≈ 1 s; `n = 5000` ✗ |

## Complexity Snapshot

| Problem | Naive | DP | Notes |
|---------|-------|-----|-------|
| Matrix chain | `Θ(4ⁿ)` (all parenthesisations) | **`Θ(n³)`** | `n ≤ 500` |
| Matrix chain (Ostertree) | — | `Θ(n³)` fewer constants | |
| Palindrome partitioning (min cuts) | exponential | **`Θ(n²)`** | `n ≤ 10⁵`? no, `n ≤ 5000` |
| Palindrome partitioning, `O(n)` space | — | `Θ(n²)` | for length only |
| Longest common substring | `Θ(nm)` | `Θ(nm)` | see lab 02 |
| **String metrics DP** | `Θ(n²·m)` (triple loop) | **`Θ(n²)`** | the key one |
| Penney game equilibrium | exponential | **`Θ(n²)`** | the Penney/Conway result |
| Word break | `Θ(2ⁿ)` | **`Θ(n²)`** or `Θ(n·L)` | |
| Word break II (all segmentations) | exponential | `Θ(n²)` + output | |
| RNA folding (Nussinov) | exponential | **`Θ(n³)`** | `n ≤ 500` |
| Optimal triangulation | `Θ(4ⁿ)` | `Θ(n³)` | = matrix chain |
| Burst balloons | `Θ(n³)` | `Θ(n³)` | = matrix chain shape |
| Rod cutting | — | `Θ(n²)` | see lab 01 |
| Edit distance on strings | — | `Θ(nm)` | see lab 02 |

## Algorithms Covered

### Matrix chain multiplication
```
cost[i][j] = 0                                          if i == j
cost[i][j] = min over i < k < j of ( cost[i][k] + cost[k+1][j] + d[i]*d[k+1]*d[j] )
```
**Time:** `Θ(n³)`. **Space:** `Θ(n²)`, reducible to `Θ(n)` for the value (but not for reconstruction).

**Why greedy fails:** the cost `d[i]d[k+1]d[j]` depends on `k` in a way that interacts with every other split. **No local rule works** — this is the textbook counterexample to greedy.

### Palindrome partitioning
```
cut[0] = 0
cut[i] = min over 0 <= j < i with pal(j, i-1) of ( cut[j] + 1 )
pal(i,j) = s[i]==s[j] && (j-i < 2 || pal(i+1, j-1))          -- Θ(n²) precompute
```
`Θ(n²)`, `Θ(n)` space with `O(n²)` precomputation via the centre-expansion trick.

### String metrics (`Θ(n²)`)
For two strings `X`, `Y`, the **string edit distance** `δ(X, Y)` is the minimum total weight of a set of transposition-free edit operations. Define
```
d[0][j] = Σ_{k=1}^{j}  insertionCost(Y[k])
d[i][0] = Σ_{k=1}^{i}  deletionCost(X[k])
d[i][j] = min( d[i-1][j] + deletionCost(X[i]),
                d[i][j-1] + insertionCost(Y[j]),
                d[i-1][j-1] + substitutionCost(X[i], Y[j]) )
```
This is Levenshtein with **separable costs** (`d(X_i, Y_j) = s(x_i) + i(y_j) + s(x_i, y_j)`).

**The Penney game consequence:** the probability player B wins against A's string `A` is a **linear function of the transition matrix** `M(s, t)` built from `d` in `Θ(|s||t|)`, then a `Θ(n²)` linear solve. **The equilibrium "best response" string for A = `HRRRRRH…R` — the same for every alphabet.** That is a genuinely surprising theorem and it is derived from a `Θ(n²)` DP.

### Word break
```
can[0] = true
can[i] = OR over j < i with s[j..i-1] in dict of can[j]
```
`Θ(n²)` with a `HashSet` lookup, or `Θ(n·L)` with `L` the max word length. Reconstruction is `O(n)`.

### RNA folding (Nussinov)
```
N[i][j] = 0                                             if i >= j - 1
N[i][j] = max( N[i+1][j],
               max over i < k < j-1, pairable(i,k) of ( 3 + N[i+1][k-1] + N[k+1][j] ) )
```
`Θ(n³)` time, `Θ(n²)` space. This is the **first genuinely hard `Θ(n³)` biological DP**, and it is the same interval+split shape as matrix chain.

## Files

| File | Purpose |
|------|---------|
| `src/main/java/com/alglab/intervaldp/` | All six problems |
| `src/test/java/com/alglab/intervaldp/` | Cross-validation vs brute force |
| `SOLUTION/` | Worked solutions |
| `TESTS/` | Boundary cases (`n = 0,1,2`), empty dictionary, impossible word break |
| `BENCHMARK/` | The `Θ(n³)` wall demonstrated |
| `MINI_PROJECT/` | Parenthesisation visualiser, palindrome partition display |
| `REAL_WORLD_PROJECT/` | Paraphrase detection / document segmentation |
| `CHALLENGE/` | Hu–Shing `Θ(n log n)` polygon triangulation, Aho–Corasick-assisted word break |
| `DIAGRAMS/` | Split trees, interval grids |