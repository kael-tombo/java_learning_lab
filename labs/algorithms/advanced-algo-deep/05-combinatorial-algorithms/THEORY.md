# Theory — Combinatorial Algorithms

Combinatorics asks "how many?". The algorithms below compute those counts
without enumerating, using recurrences, closed forms, and symmetry. The
recurring theme: a count is answerable exactly when a recurrence or a
symmetry principle reduces it to smaller counts.

## Binomial coefficients

`C(n,k)` counts k-subsets of an n-set. Pascal's recurrence
`C(n,k) = C(n-1,k-1) + C(n-1,k)` has a one-line proof: fix a distinguished
element; a k-subset either contains it (choose the other k-1 from n-1) or
not (choose all k from n-1). Computing via the recurrence is Θ(n·k) time and
Θ(k) space with a rolling row. Watch for overflow: C(60,30) ≈ 1.18·10¹⁷, so
use long or BigInteger; Pascal's recurrence also avoids the division of the
`n!/(k!(n-k)!)` formula, which can lose exactness in integer division if
applied naively in another order.

## Catalan numbers

`C_n = (1/(n+1))·C(2n,n)` counts many things at once: valid parenthesis
strings of 2n symbols, binary trees with n internal nodes, non-crossing
matchings of 2n points, paths that never go below the x-axis. The recurrence
`C_{n+1} = Σ_{i=0}^{n} C_i · C_{n-i}` with C_0 = 1 is the defining relation;
it says a valid string splits at the position where the first paren closes,
with independent valid substrings inside and after. Use the closed form for a
Θ(n) computation; use the recurrence only when you need all values up to n.

## Inclusion–exclusion

Counting objects that satisfy *none* of the "bad" properties uses
inclusion–exclusion: `|∩ Aᵢᶜ| = Σ (-1)^|S| |∩_{i∈S} Aᵢ|`. It is exact, but
the sum has 2^k terms for k properties — it is only practical when the
intersection terms simplify. The classic example: counting derangements (no
fixed point) gives `D_n = n!·Σ_{k=0}^{n} (-1)^k / k!`, which converges to
`n!/e`. A useful derived fact: the number of onto maps from an n-set to a
k-set is `k!·S(n,k)` where S(n,k) is a Stirling number of the second kind.

## Stirling numbers

`S(n,k)` counts partitions of an n-set into k non-empty blocks. Recurrence:
`S(n,k) = k·S(n-1,k) + S(n-1,k-1)` — the nth element either joins an
existing block (k choices) or starts a new one. Time Θ(n·k). First-kind
numbers `c(n,k)` count permutations of n with k cycles, with recurrence
`c(n,k) = (n-1)·c(n-1,k) + c(n-1,k-1)`. Both are computed by Pascal-like
tabulations.

## Meet in the middle

When a brute-force search is Θ(2^n), split the input in half, enumerate each
half (Θ(2^{n/2})), and combine the results (Θ(2^{n/2}·log)) — usually by
sorting one half and binary-searching the other. This reduces Θ(2^n) time
and Θ(1) space to Θ(2^{n/2}) time and space. It is the workhorse when n ≈ 40
in problems like subset-sum and multi-constraint assignment.

## Subset and submask enumeration

For a k-bit mask M, the loop `for (s = M; ; s = (s-1) & M)` visits every
submask. The total number of (mask, submask) pairs summed over all masks of
size k is `Σ C(k,j)·2^(k-j)·... ` — the well-known result is that the sum of
the number of submasks over all masks is Θ(3^k). This is the complexity
bound that makes bitmask DP over subsets of size k practical up to k ≈ 20.

## Pitfalls

- `n!/(k!(n-k)!)` in integer arithmetic must divide in an order that keeps
  intermediate values integral — safer to use Pascal or multiply-then-divide
  stepwise by gcd.
- Inclusion–exclusion blows up as 2^k; do not use it when k > ~20.
- Catalan indices are a frequent off-by-one: C_n counts n pairs of
  parentheses, not n+1.
- Meet-in-the-middle uses Θ(2^{n/2}) *memory* — the time win is paid in
  space.
