# Math Foundation — String Algorithms Advanced

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## KMP linearity

Let j be the matched length. Each comparison either increments i and j together, or decreases j via π. j can increase at most n times, so it can decrease at most n times; each step costs O(1). Total Θ(n+m).

The same potential argument applies to π-table construction, giving Θ(m) build.

## Rolling hash update

H(i) = Σ t[i+k]·B^(m-1-k) for k=0..m-1. Then H(i+1) = B·H(i) - t[i]·B^m + t[i+m].

Modulo a prime q, collisions occur only when the two window values differ by a multiple of q — with a uniform hash the expected number of collisions is small.

## Z window reuse

If i lies inside the current rightmost match [l,r], then t[i..] and t[i-l..] agree for r-i+1 characters, so Z[i] ≥ min(Z[i-l], r-i+1). Scanning only beyond r keeps total work Θ(n).

The bound is the same potential argument as KMP: the right edge r never retreats.

## Manacher mirror reuse

If i is inside the palindrome centred at c with radius R, then its mirror 2c-i has known radius ρ; the palindrome at i has radius at least min(ρ, R-i). Only the part beyond R needs fresh comparisons.

Summing the fresh comparisons over all centres is Θ(n) because the right edge moves only right.

## Period from border

If p has a border of length b, then p[i] = p[i+b] for all valid i, so p is periodic with period m-b.

Conversely a period q gives the border p[0..m-q-1]; the two notions are dual.
