# Diagrams — Lab 40: Advanced String Algorithms

Diagrams for the structural string algorithms in this lab: **suffix arrays**, **the Kasai LCP array**, **the suffix automaton**, **suffix trees**, **range-minimum queries over LCP**, and **runs/repetition structure**.

All diagrams are terminal-renderable ASCII so they survive a diff and an IDE preview. Each entry names the section of `../THEORY.md` it illustrates and gives a construction recipe for a rendered version.

---

## Diagram inventory

| # | File / construct | Purpose | Format |
|---|-----------------|---------|--------|
| S1 | `suffix-array-construction.md` | Sorted suffixes of `banana$` with ranks and LCPs | ASCII table |
| S2 | `doubling-rank-table.md` | The `(rank[i], rank[i+k])` doubling rounds | ASCII matrix |
| S3 | `kasai-lcp-proof.md` | Why `lcp[SA[i−1]]` only drops by one | ASCII annotated trace |
| S4 | `suffix-automaton-banana.md` | States, transitions, suffix links, end positions | ASCII graph |
| S5 | `suffix-tree-banana.md` | The compressed trie of suffixes with edge labels | ASCII tree |
| S6 | `rmq-lcp-interval.md` | The `[l..r]` interval and its `min(lcp)` value | ASCII |
| S7 | `substring-query-flow.md` | From a substring to a suffix-range to an LCP answer | ASCII flowchart |
| S8 | `runs-periodicity.md` | A run `(i, p)`, its period, and its minimality | ASCII diagram |
| S9 | `z-vs-sa-vs-sam.md` | The three tools side by side, with what each answers | ASCII comparison |
| S10 | `string-algorithms-in-systems.md` | Where these appear: indexes, compression, plagiarism, genomics | ASCII architecture |

---

## The picture that carries the whole lab (S1)

```
text:   b a n a n a $          ($ = unique sentinel, smaller than every symbol)

all suffixes, lexicographically sorted:

  rank  start  suffix             LCP with previous
  ----  -----  ----------------   -----------------
   6      6   $                        0     (previous = none; LCP with "" )
   5      5   a$                       1
   3      3   ana$                     1
   1      1   anana$                   3
   0      0   banana$                  0
   4      4   na$                      0
   2      2   nana$                    2

  SA  = [6, 5, 3, 1, 0, 4, 2]
  rank[0..5] = [4, 3, 6, 2, 5, 1, 0]        (inverse permutation)
  LCP = [-,  0, 1, 1, 3, 0, 0, 2]

WHY THE SENTINEL: without a unique smallest terminator, suffixes that are
prefixes of each other are ambiguous ("a" vs "ana"). The sentinel makes every
suffix a distinct string and makes "" the unique minimum.

THE CENTRAL THEOREM (LCP interval):
  LCP(suffixes sa[l] .. sa[r])  =  min( LCP[l+1], LCP[l+2], ..., LCP[r] )

i.e. the common prefix of ALL suffixes in a range is the MINIMUM LCP in
that range. Every substring query reduces to: find the suffix range, then
query min(LCP) over it with a sparse table -> O(1).
```

---

## Recommended diagram exercises

1. Draw S1 completely, then draw S2's doubling rounds for `banana$` and verify you reach the same `SA`.
2. Draw S3: annotate the Kasai proof for `banana$` — show that at each step the previous `lcp` value **decreases by at most 1**, which is what makes `Θ(n)` total possible. That one-line inequality is the whole algorithm.
3. Draw S4: build the suffix automaton of `banana$` by hand, marking which states are clones and why. Then answer: **how many states and transitions?** (`≤ 2n−1` states, `≤ 3n−4` transitions.)
4. Draw S5: the suffix **tree** of `banana$` (not the suffix *array*), with edge labels and the `w(c)` endpos sets on the leaves. Then draw the suffix **automaton** of the same string and explain why the tree has `Θ(n)` implicit suffixes while the automaton has `≤ 2n` states.
5. Draw S6: given the query `ana`, find its suffix range in `SA` (ranks 2 and 3 → indices 1 and 2) and show `min(LCP[2], LCP[3]) = 1`... **and notice the answer is wrong** (`ana` has length 3). Draw the corrected interval: suffixes `ana$` and `anana$` have LCP `ana`, length 3 — so the interval is `[2,3]` in *suffix* ranks and you must take `min(LCP[l+1..r]) = LCP[3] = 3`. **Get the indices right in your drawing**; this off-by-one is the single most common suffix-array bug.
6. Draw S8: find a run in `abababab` — period 2, exponents 4. Then find the *minimal* period and explain why `p` and the string length must satisfy `length ≥ 2p` for it to be a run.
7. Draw S9 and answer: which of Z / suffix array / suffix automaton would you use for (a) find all occurrences, (b) count distinct substrings, (c) longest common substring of two strings, (d) find the longest repeating substring, (e) answer substring-vs-substring equality in `O(1)`?

---

## Related files

- `../THEORY.md` — the doubling construction, Kasai's `Θ(n)` proof, the LCP interval theorem, suffix-automaton states and clones, `Σ(|sᵢ|)` bounds, and the `Σ(|sᵢ|)` distinct-substring count `n(n+1)/2`.
- `../MATH_FOUNDATION.md` — the doubling recurrence `T(n) = T(n/2) + Θ(n)` vs sorting suffixes directly `Θ(n² log n)`, Kasai's amortised argument, the `2n−1` state bound, and the `O(n log n)` / `O(n)` construction trade.
- `../BENCHMARK/` — where the ASCII renderers live; the ranks in S1 are reproducible there.