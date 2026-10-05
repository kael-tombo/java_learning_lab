# QUIZ — Searching Track
> 15 questions with answers. Track `searching`.

1. Binary search bound? → O(log n) time, O(1) space iterative.
2. Safe mid in Java? → (lo+hi)>>>1; avoids int overflow.
3. lowerBound vs upperBound? → First ≥ x vs first > x.
4. Exact hit from lb? → lb if lb<n and a[lb]==x, else absent.
5. Rotated key insight? → One half always sorted; test membership.
6. Duplicates in rotated? → Shrink hi on tie; worst O(n).
7. Peak invariant? → A peak exists in [lo,hi]; climb toward higher neighbor.
8. Answer-search needs? → Monotonic predicate; search first true.
9. Interpolation average? → O(log log n) uniform; O(n) worst skewed.
10. Exponential search? → O(log pos) for unbounded/infinite arrays.
11. Recurrence? → T(n)=T(n/2)+O(1) → Θ(log n) Master case 2 (a=1).
12. Why half-open [lo,hi)? → No ±1 bugs; empty = done; length = hi-lo.
13. Ternary search? → Still Θ(log n), worse constants; skip.
14. Binary vs hash lookup? → Hash O(1) avg but no order/bounds/neighbors.
15. Fuzz oracle? → Linear scan on small n; brute predicate check.

## Scoring
- 13-15: expert. 10-12: practitioner. < 10: revisit THEORY + flashcards.

## Follow-ups
- Prove one bound on paper; implement one variant from memory.
