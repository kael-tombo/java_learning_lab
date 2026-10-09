# Architecture: Combinatorics in Code

## Separate the Four Concerns

A clean combinatorics module has distinct layers — mixing them is what makes counting code untestable:

1. **Model** — declare the objects: labeled/unlabeled, ordered/unordered, with/without repetition, with/without constraints. This layer produces the *formula*, not code: e.g., "5-letter words over 26 letters, no repeats, must start with a vowel" → 5 · P(25, 4).
2. **Counting** — a pure function returning the number: `binomial(n, k)`, `catalan(n)`, `countWithRecurrence(...)`. O(1)–O(n) per call, no enumeration.
3. **Enumeration** — an iterator producing objects one at a time (`nextCombination`, `nextPermutation`), used only when the count is small enough (guard with `if (count > LIMIT) throw`).
4. **Verification** — brute-force oracle for n ≤ 10 asserting `enumeratedCount == formulaCount`.

Keeping counting and enumeration apart is the architectural rule: you should be able to answer "how many" without ever constructing an object.

## A BinomialProvider Interface

```java
interface BinomialProvider {
    long chooseLong(int n, int k);        // throws if it overflows long
    BigInteger choose(int n, int k);      // exact
    default boolean fitsLong(int n, int k) { ... }
}
```

Two implementations: `PascalTableProvider` (Θ(n²) precompute up to configured n, then O(1) queries) and `MultiplicativeProvider` (O(k) per query, O(1) memory). Callers pick by access pattern; the interface prevents the classic bug of scattering `long` arithmetic everywhere until C(67,33) silently wraps.

## Recurrence Engines

Represent a linear recurrence as data, not code:

```java
record Recurrence(int order, long[] seeds, long[] coeffs) {}
```

with a generic `nthTerm(rec, n)` iterating Θ(n) in O(order) memory (or O(1) with a rolling window). The bitstring-without-"00" problem becomes `Recurrence(order=2, seeds={1,2}, coeffs={1,1})` — Fibonacci; "no 000" becomes order 3 with seeds {1, 2, 4}. Tests then check seeds only, and the loop is shared, audited once.

## Enumeration via Iterator/Stream

Expose combinations as a lazy `Iterator<List<Integer>>` so callers can `limit(k)` without materializing C(n,k) elements — the architecture that makes "enumerate the first 1,000 triples" O(3,000) instead of O(C(n,3)). Combine with a hard cap: the iterator itself throws after a configured maximum output count, so misuse becomes a loud failure instead of an OOM.

## Where Big Integers Live

Policy: counts that fit `long` stay primitive (fast paths in hot loops); anything crossing the boundary converts explicitly at a documented point (`chooseExact`). Overflow-checked arithmetic (`Math.multiplyExact`) sits inside the counting layer so the failure surfaces at the boundary, not as a wrong answer three layers up.

## Reuse Across Labs

This layer is infrastructure for later labs: the graph lab needs C(n, k) for subset-of-vertices subgraphs and for counting spanning trees (Cayley's nⁿ⁻² formula), the number-theory lab needs factorials mod p, and the generating-functions lab needs binomials for coefficient extraction (1−x)^(−k). One audited provider, four consumers.
