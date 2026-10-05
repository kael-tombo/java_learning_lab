# QUIZ — Sorting & Searching Deep Track
> 15 questions with answers. Track `sorting-searching-deep`.

1. Comparison lower bound? → Ω(n log n) via log₂(n!) decision tree.
2. When do linear sorts win? → Bounded integer keys: counting O(n+k), radix O(d(n+k)).
3. Quicksort vs mergesort? → QS cache-friendly in-place, unstable; merge stable, O(n) extra.
4. Heapsort niche? → In-place O(n log n) worst guarantee, poor locality.
5. 3-way partition wins? → Duplicate-heavy inputs, O(n) all-equal.
6. lowerBound contract? → First i with a[i] ≥ x in [0,n].
7. Rotated insight? → One half sorted; test membership there.
8. Answer-search needs? → Monotonic predicate; binary search first true.
9. Quickselect expected? → E[O(n)] discarding a fraction per round.
10. KMP bound? → O(n+m): pi build + single scan, no re-scan.
11. Rabin-Karp risk? → Spurious hits; verify + double hash/mod.
12. Aho-Corasick? → O(n+m+z) multi-pattern via goto/fail/output.
13. Suffix array query? → O(m log n) binary search over SA.
14. Stability definition? → Equal keys keep input order; matters for multi-key sorts.
15. Fuzz oracles? → Arrays.sort, linear scan, naive indexOf.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
