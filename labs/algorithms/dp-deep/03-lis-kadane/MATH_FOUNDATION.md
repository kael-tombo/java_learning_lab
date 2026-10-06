# Math Foundation — LIS & Kadane

The dominance-query reformulation, the geometric decay behind Kadane's deque optimisation, and the comparison of the DP forms.

---

## 1. The LIS DP as a dominance query

```
dp[i] = 1 + max { dp[j] : j < i  and  a[j] < a[i] }
```

Rewrite: associate to each processed index `j` the point `(a[j], dp[j])` in the plane. The query for index `i` is

```
max y over all points with x < a[i]
```

— a **2-D dominance max query**. Three implementations:

| method | query | update | total |
|---|---|---|---|
| linear scan | `Θ(n)` | `Θ(1)` | `Θ(n²)` |
| sorted array + binary search (patience) | `Θ(log n)` | `Θ(log n)` (shift-free overwrite) | **`Θ(n log n)`** |
| Fenwick on compressed values | `Θ(log n)` | `Θ(log n)` | `Θ(n log n)` |
| segment tree | `Θ(log n)` | `Θ(log n)` | `Θ(n log n)` |

**Why patience sorting beats Fenwick despite the same bound:** the Fenwick tree is `Θ(log n)` *random* accesses into an array of size `σ`. Patience sorting is `Θ(log n)` accesses into the `tails` array, which is at most `L ≤ n` long and — crucially — the binary search touches only the *current* length prefix, which grows slowly. Cache behaviour dominates.

---

## 2. The patience invariant and its proof

> `tails[k]` = the minimum, over all strictly increasing subsequences of length `k+1` of `a[0..i-1]`, of the last element.

**Claim 1: `tails` is strictly increasing.**
If there is a subsequence of length `k+2` with last element `t`, its first `k+1` elements form a subsequence of length `k+1` with last element `< t`. Hence `tails[k] < tails[k+1]`. ∎

*(This is what makes the binary search valid — and it holds because the comparison is **strict**.)*

**Claim 2: `lowerBound(tails, x) = p` implies `x` can end a subsequence of length exactly `p+1`.**
`tails[p-1] < x` (by Claim 1 and the definition of `p`, since `p` is the *first* index with `tails[p] >= x`, so `tails[p-1] < x`). Take a length-`p` subsequence with tail `tails[p-1]` and append `x`. ✓

**Claim 3: `x` cannot end a subsequence longer than `p+1`.**
A length-`p+2` subsequence ending at `x` has a length-`p+1` prefix with tail `< x`, so `tails[p] < x`. But `p` is the first index with `tails[p] >= x`, so `tails[p] >= x` — contradiction. ∎

Claims 2 + 3: writing `x` at slot `p` is exactly right, and `p == length` (appending) means a new longest subsequence was found.

**Answer = `length`**, the number of occupied slots.

---

## 3. Why `tails` is not an LIS — a counting argument

**Claim.** For `a` of length `n`, the set of possible `tails` arrays is not the set of subsequences.

**Example:** `a = [3, 1, 2]`.
- Patience: `x=3` → slot 0, `tails=[3]`, length 1. `x=1` → `lowerBound([3],1)=0`, `tails=[1]`. `x=2` → `lowerBound([1],2)=1`, `tails=[1,2]`, length 2.
- `tails = [1, 2]`.
- LIS = `[1,2]` (length 2). Here they coincide.

**Better example:** `a = [5, 1, 4, 2, 3]`.
- `5` → `tails=[5]`
- `1` → `tails=[1]`
- `4` → `p=1` → `tails=[1,4]`, length 2
- `2` → `lowerBound([1,4],2)=1` → `tails=[1,2]`
- `3` → `p=2` → `tails=[1,2,3]`, length 3

LIS = `[1,2,3]` — again coincides. Try: `a = [10, 9, 2, 5, 3, 7, 101, 18]`.
- `10` → `[10]`
- `9`  → `[9]`
- `2`  → `[2]`
- `5`  → `[2,5]`
- `3`  → `[2,3]`
- `7`  → `[2,3,7]`
- `101`→ `[2,3,7,101]`, length 4
- `18` → `lowerBound([2,3,7,101],18)=3` → `[2,3,7,18]`, length 4

Final `tails = [2, 3, 7, 18]`. `[2,3,7,18]` **is** a subsequence here. Hmm.

**The classic counter-example:** `a = [3, 5, 1, 4, 2]`.
- `3` → `[3]`
- `5` → `[3,5]`, length 2
- `1` → `p=0` → `[1,5]`
- `4` → `p=1` → `[1,4]`
- `2` → `p=1` → `[1,2]`, length 2

Final `tails = [1, 2]`. And `[1,2]` **is** a subsequence (positions 2 and 4). Still coincides!

**The real demonstration that `tails` is not an LIS:** `a = [1, 4, 2, 3, 0]`.
- `1` → `[1]`
- `4` → `[1,4]`, len 2
- `2` → `p=1` → `[1,2]`
- `3` → `p=2` → `[1,2,3]`, len 3
- `0` → `p=0` → `[0,2,3]`, len 3

`tails = [0, 2, 3]`. Is `[0,2,3]` a subsequence of `[1,4,2,3,0]`? `0` is at index 4; `2` at index 2; `3` at index 3. Reading positions `4, 2, 3` is **not increasing** ⇒ **`[0,2,3]` is NOT a subsequence.** ✓ And the true LIS is `[1,2,3]`.

**This is the definitive counter-example.** `tails` is sorted (by Claim 1) but its elements come from positions that are not in increasing order.

---

## 4. Comparison of DP forms

### LIS

| form | recurrence | time | space |
|---|---|---|---|
| `Θ(n²)` DP | `dp[i] = 1 + max{dp[j] : j<i, a[j]<a[i]}` | `Θ(n²)` | `Θ(n)` |
| patience | sorted-array binary search | `Θ(n log n)` | `Θ(n)` |
| Fenwick on compressed ranks | prefix max over ranks `< rank(a[i])` | `Θ(n log n)` | `Θ(n)` |
| `n ≤ 20`, count all | bitmask | `Θ(n 2ⁿ)` | `Θ(2ⁿ)` |
| **`n = 10⁶`** | — | `Θ(n²) = 10¹²` ✗ | `Θ(n log n) = 2·10⁷` ✓ |

### Kadane

| form | recurrence | time | space |
|---|---|---|---|
| brute force | all `Θ(n²)` subarrays | `Θ(n²)` | `O(1)` |
| prefix sums + double loop | `max(P[j+1]-P[i])` | `Θ(n²)` | `Θ(n)` |
| **Kadane** | `cur = max(a[i], cur+a[i])` | **`Θ(n)`** | **`O(1)`** |
| prefix sums + running min | `best = max(best, P[i]-minP)` | `Θ(n)` | `O(1)` |
| constrained `≤ k` | sliding window min of `P` | `Θ(n)` deque | `O(k)` |

**Kadane beats the brute force by `Θ(n)`, not by `log n`.** That is unusual for this course and worth noting: for max-subarray, the "DP" is genuinely a linear-time discovery, not a log-factor win.

---

## 5. The constrained-subarray deque optimisation

Let `P[i] = a[0] + … + a[i-1]`. A subarray of **exactly** `k` ending at `i-1` has sum `P[i] - P[i-k]`. So

```
answer = max over i of ( P[i] − P[i-k] )
```

which is `Θ(n)` with a single loop and no data structure.

For **at most** `k`:

```
answer = max over i, j in [max(0,i-k), i-1] of ( P[i] − P[j] )
       = max over i of ( P[i] − min{ P[j] : j ∈ [max(0,i-k), i-1] } )
```

The inner `min` is a **sliding-window minimum of width `k`**. The monotonic-deque algorithm:

```
deque (increasing P values), each step i:
    while deque not empty and P[back] >= P[i]:  pop_back()   // dominated: smaller AND later
    push_back(i)
    while deque.front() < i - k:               pop_front()  // outside the window
    answer = max(answer, P[i] - P[front])
```

**Amortised proof:** every index is pushed once and popped at most once ⇒ `Θ(n)` total.

**Why the popping is correct:** if `j₁ < j₂` and `P[j₁] >= P[j₂]`, then `j₂` is at least as good as `j₁` for every future query (smaller value, later expiry). So `j₁` can be discarded permanently.

| `k` | brute `O(nk)` | deque `Θ(n)` |
|-----|---------------|--------------|
| 1 | `Θ(n)` | `Θ(n)` |
| 10 | `10n` | `n` |
| 1 000 | `1000n` | `n` |
| `n/2` | `Θ(n²)` ✗ | `Θ(n)` ✓ |

---

## 6. Circular subarray analysis

```
maxCircular = max( maxNormal(a),  total − minNormal(a) )
```

**`maxNormal ≤ maxCircular ≤ max(|total|, maxNormal)`.**

**The degenerate case:** if `minNormal == total`, the wrapping candidate is `0`, which corresponds to the empty complement. That is invalid for the non-empty convention. Fix:

```
if (maxCircular == 0 && allElementsNegative) maxCircular = max(a);
```

**Proof that the two cases are exhaustive.** A contiguous arc of a circular array either does not cross the array boundary (a normal subarray) or does (its complement in the circle is a normal subarray). ✓

| input | `maxNormal` | `total` | `minNormal` | `total − min` | answer (strict) |
|-------|-------------|---------|-------------|---------------|------------------|
| `[1, -2, 3, -2]` | 3 | 0 | -2 | **2** | **3** |
| `[-1, -2, -3]` | -1 | -6 | -6 | 0 | **-1** (edge case) |
| `[5]` | 5 | 5 | 5 | 0 | **5** |
| `[-1, 5, -2, 5, -3]` | 8 | 4 | -3 | **7** | **8** |

---

## 7. LIS variants complexity

### Max-sum increasing subsequence
```
best[i] = a[i] + max { best[j] : j < i, a[j] < a[i] }
```
Same dominance query, but the query returns `best[j]` (a sum) rather than `dp[j]` (a length), and the update adds `a[i]`. Fenwick on compressed ranks: `Θ(n log n)`.

**Why patience sorting does not work here:** the invariant that makes patience work is "keep the smallest tail, since smaller is easier to extend". For max-sum you would want the largest `best[j]` among tails `< a[i]` — but "tail" and "best" are different quantities, and there is no array keeping both ordered. **Fenwick it is.**

### All LIS of maximum length
Let `r` be the number of distinct longest subsequences.

1. Patience sorting → `dpLen[i]` and the `prev` chain, `Θ(n log n)`.
2. Count nodes on all max-length chains via DFS/BFS on the `prev` DAG, `Θ(n + r)`.

**The output can be exponential in `n`** (e.g. `a = [1,2,3,…,n]` in a scrambled order with all values equal-ish gives `C(n, n/2)` subsequences), so `Θ(n + r)` is optimal — you cannot do better than writing the output.

### LIS with a difference bound `|a[i] − a[j]| ≤ d`
```
dp[i] = 1 + max { dp[j] : j < i, a[i] − d ≤ a[j] < a[i] }
```
A **range max over a sliding value window** ⇒ segment tree `Θ(log n)` per query, or a `TreeMap<Integer,Integer>` keyed by value, `Θ(log n)` per query. Total `Θ(n log n)`. Patience sorting cannot represent a *window* of valid predecessors.

---

## 8. Complexity summary table

| Problem | Time | Space | Notes |
|---------|------|-------|-------|
| LIS length | `Θ(n log n)` | `Θ(n)` | patience, `lowerBound` |
| LIS length + sequence | `Θ(n log n)` | `Θ(n)` | needs `prev[]` |
| LIS `n²` DP | `Θ(n²)` | `Θ(n)` | the oracle |
| LNDS (non-decreasing) | `Θ(n log n)` | `Θ(n)` | patience with `upperBound` |
| LDS | `Θ(n log n)` | `Θ(n)` | patience with `upperBound` |
| All LIS | `Θ(n log n + r)` | `Θ(n + r)` | `r` = output size |
| Count LIS | `Θ(n log n)` | `Θ(n)` | Fenwick counts |
| Max-sum increasing subseq | `Θ(n log n)` | `Θ(n)` | Fenwick |
| LIS with gap bound | `Θ(n log n)` | `Θ(n)` | segment tree |
| Max subarray | **`Θ(n)`** | **`O(1)`** | Kadane |
| Max subarray, circular | `Θ(n)` | `O(1)` | `total − min` |
| Max subarray, `≤ k` | `Θ(n)` | `O(k)` | monotonic deque |
| Max subarray, exactly `k` | `Θ(n)` | `O(k)` | `P[i] − P[i-k]` |
| Grid increasing path | `Θ(mn log n)` | `Θ(n)` | patience per row |
| Largest rectangle in a matrix | `Θ(nm)` | `Θ(m)` | histogram stack |

---

## 9. Quick reference

| Quantity | Value |
|----------|-------|
| `Θ(n²)` LIS DP recurrence | `dp[i] = 1 + max{dp[j] : j<i, a[j]<a[i]}` |
| LIS `Θ(n log n)` | `p = lowerBound(tails, x); tails[p] = x` |
| `tails` invariant | strictly increasing ⇒ **sorted ⇒ binary search valid** |
| `tails` is not | a subsequence — counter-example `a = [1,4,2,3,0]` ⇒ `tails = [0,2,3]` |
| `lowerBound` vs `upperBound` | strictly increasing vs **non-decreasing** |
| LIS speedup | `Θ(n²)` → `Θ(n log n)`; at `n = 10⁶` that is `10¹²` → `2·10⁷` |
| Patience vs Fenwick | same bound; patience wins on cache behaviour |
| Kadane recurrence | `cur = max(a[i], cur + a[i]); best = max(best, cur)` |
| Kadane speedup over brute force | **`Θ(n)` — a linear, not logarithmic, discovery** |
| Kadane prefix-sum form | `max P[i] − min P[j] (j < i)` |
| Kadane `best` initialiser | `Long.MIN_VALUE` for the non-empty convention |
| Circular subarray | `max( maxNormal, total − minNormal )` + the all-negative edge case |
| `≤ k` subarray | sliding min of prefix sums ⇒ monotonic deque, `Θ(n)` |
| exactly `k` subarray | `Θ(n)`, no data structure: `P[i] − P[i-k]` |
| Max-sum increasing subseq | `Θ(n log n)` Fenwick; patience does **not** generalise |
| All LIS | `Θ(n log n + r)` — output-bound |
| Grid LIS | `Θ(mn log n)` |
| Largest rectangle in a matrix | `Θ(nm)` histogram stack — **not** Kadane |

## Sources

- Schensted (1961) / Knuth — patience sorting, originally as a permutation-sorting construction.
- Ulm (1979) — the tails-array formulation.
- Kadane (1956) — maximum sum of consecutive elements.
- O(n²) LIS DP: standard, from the LCS special case with a sorted array.