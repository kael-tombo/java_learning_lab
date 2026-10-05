# THEORY — Binary Search
> Mechanics + invariants + complexity proof sketch for binary search.

## 1. Problem Statement
- Input: sorted ascending `a[0..n-1]`, key `k`.
- Output: any `i` with `a[i]==k`, or insertion point / -1 if absent.
- Precondition: sorted per same comparator used for probing.
- Success: `O(log n)` probes, correct on empty/duplicates/edges.
- Contrast: linear needs no order but costs `O(n)`.

## 2. Algorithm Mechanics
- Init `lo=0, hi=n` (half-open `[lo,hi)` — preferred, no `+1/-1` bugs).
- While `lo<hi`: `mid=(lo+hi)>>>1` (unsigned shift avoids overflow).
- If `a[mid]==k` return `mid`; if `a[mid]<k` → `lo=mid+1` else `hi=mid`.
- Exit → not found; `lo` is lower-bound insertion point.
- Recursive form: `search(lo,hi)` with same update; tail-recursive.
- Duplicate policy: any-hit vs first-hit (lowerBound loop without early return).
- Comparator consistency: sort order must match probe order.
- Overflow trap: `(lo+hi)/2` overflows for large int indices — use `>>>1`.

## 3. Invariants
- Invariant I: if `k` present, `k ∈ a[lo..hi)`; absent → insertion point ∈ `[lo,hi]`.
- Init: `[0,n)` whole array — holds trivially.
- Maintenance: `a[mid]<k` discards `[lo..mid]` (all < k by sortedness); else discards `[mid+1..hi)`.
- Shrink: `hi-lo` strictly decreases each iteration → terminates.
- Exit `lo==hi`: interval empty → absent; `lo` is lower bound.
- Sortedness is load-bearing: one inversion can discard the half holding `k`.

## 4. Worked Trace
- `a=[1,3,5,7,9], k=7`: [0,5) mid=2 (5<7) → [3,5) mid=4 (9>7) → [3,4) mid=3 hit.
- `k=6`: same path, exit lo=3 (insert between 5 and 7).
- Empty: `[0,0)` loop skipped → -1/insert 0.
- Duplicates `[2,2,2,2]`: any-hit returns 1 or 2; lowerBound returns 0.

## 5. Complexity Proof Sketch
- Recurrence `T(n)=T(⌈n/2⌉)+O(1)`, `T(1)=O(1)`.
- Unroll: `k` levels with `n/2^k ≤ 1` → `k=⌈log₂n⌉` → `Θ(log n)`.
- Iteration view: interval halves; ≤ `⌊log₂n⌋+1` probes worst.
- Best `Θ(1)` (first mid hit). Average `Θ(log n)`.
- Space: iterative `O(1)`; naive recursive `O(log n)` stack.
- Lower bound: comparison decision tree has `n+1` outcomes → height `Ω(log n)`.

## 6. Correctness Argument
- invariant I + shrinking + sortedness ⇒ returned index holds `k` or absence certified.
- Induction on interval size; base `hi-lo≤1` checked directly.
- Counter-example: unsorted `[3,1,2]`, `k=1` may probe mid=1 and discard wrong half.

## 7. When NOT to Use
- Unsorted + single query → linear (sorting costs more than it saves).
- Linked list → no random access; linear or skip structure instead.
- Floating keys with epsilon semantics → custom comparator needed.
- Heavy inserts → balanced BST / skip list over sorted array.

## 8. Java Notes
- `Arrays.binarySearch` returns `-(insertion+1)` on miss — mirror that contract.
- `Collections.binarySearch(List, key)` similar; needs `RandomAccess` for speed.
- Generics: `Comparator<? super T>` must match sort comparator.

## 9. Common Misconceptions
- "`mid=(lo+hi)/2` always fine" — overflows; use `lo+(hi-lo)/2` or `>>>1`.
- "`lo<=hi` closed intervals are simpler" — they add off-by-one risk; half-open wins.
- "Duplicates don't matter" — any-hit vs first-hit changes callers; specify.

## 10. Checklist
- [ ] Empty/singleton/two-element traces pass.
- [ ] Overflow-safe mid + half-open bounds.
- [ ] Miss returns documented insertion encoding.
- [ ] Sorted-precondition asserted/tested.
