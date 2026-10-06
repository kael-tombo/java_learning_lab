# Theory — Randomized Algorithms

A randomised algorithm uses a random source internally. The two guarantees
are: **Las Vegas** — always correct, expected time bounded; and **Monte
Carlo** — time bounded, correctness holds with high probability. The trick is
that by moving the bad cases from the *input* to the *coins*, the adversary
can no longer construct a worst case on purpose.

## Randomised quicksort

Pick the pivot uniformly at random. The expected number of comparisons is
Θ(n log n). A clean way to see it: element xᵢ and xⱼ (in sorted order) are
compared at most once, and they are compared iff one of them is chosen as
pivot before any element between them is chosen. For elements at sorted
distance j-i, that probability is `2/(j-i+1)`. So the expected number of
comparisons is

```
E[comparisons] = Σ_{i<j} 2/(j-i+1) ≤ 2 Σ_{d=2}^{n} (n-d+1)/d ≤ 2n·H_n = Θ(n log n)
```

The worst case Θ(n²) still exists (one bad pivot-path), but its probability
is 2^(−Θ(n)) — an adversary cannot force it because the input no longer
determines the pivots.

## Randomised selection (quickselect)

To find the k-th smallest, pick a random pivot, partition, and recurse only
on the side containing the k-th. In expectation the retained side has at most
3n/4 elements, so `E[T(n)] ≤ E[T(3n/4)] + Θ(n)` = Θ(n). The deterministic
median-of-medians is an alternative but has a large constant; randomised
quickselect is what real systems use.

## Monte Carlo vs Las Vegas

- **Las Vegas**: the answer is always right; only the *time* varies. Example:
  randomised quicksort, quickselect — the sort is correct regardless of the
  pivots; the pivots only affect the time.
- **Monte Carlo**: the time is bounded, but the answer may be wrong with some
  probability. Example: Miller–Rabin (a composite can pass k rounds with
  probability ≤ 4⁻ᵏ), Freivalds' matrix-multiplication check.
A Monte Carlo algorithm is boosted by repetition: k independent rounds
multiply the success probabilities, so k rounds give error ≤ δᵏ.

## Randomised primality (Miller–Rabin)

For odd n = 2^s·d+1, pick a random base a. If a^d ≠ 1 and a^(2^r·d) ≠ -1 for
all r, composite is proven. A composite passes a random base with probability
≤ 1/4, so k rounds give error ≤ 4⁻ᵏ. This is Monte Carlo: the witness is
always a certificate of compositeness, but a non-witness is only evidence of
primality.

## Reservoir sampling

To draw a uniform k-sample from a stream of unknown length n: keep the first
k items, then for item i > k include it with probability k/i, evicting a
uniform random reservoir item if included. Induction on i shows every item is
in the reservoir with probability exactly k/n. Time Θ(n), space Θ(k), one
pass — the algorithm to reach for when you cannot store the stream.

## Randomised hash tables

A hash table maps keys through a hash function to buckets. With a uniform
hash, the expected chain length under n keys and m buckets is n/m (the load
factor), so expected lookup is Θ(1) when the load factor is Θ(1). Worst-case
chains (all keys in one bucket) are Θ(n), but making the hash function random
— e.g. universal hashing with a random parameter — makes any *fixed* input
have Θ(1) expected cost. This is the same adversary-defeating move as
randomised quicksort.

## When randomisation does NOT help

- If the input is already structured and an adversary knows your seed, the
  worst case returns.
- Randomisation is not needed when a deterministic algorithm already meets
  the bound (e.g. sorting via a deterministic O(n log n) sort if memory is
  free).
- The probabilistic guarantees are about the *coins*, not the input — a
  Monte Carlo algorithm can be unlucky on any input.

## Pitfalls

- Reporting E[T] but never bounding the worst case — the worst case is still
  Θ(n²) for randomised quicksort, just improbable.
- Using a predictable seed (e.g. time-based) for a security-sensitive hash —
  the adversary re-derives the worst case.
- Confusing "expected time" with "always fast": the distribution has a long
  tail.
