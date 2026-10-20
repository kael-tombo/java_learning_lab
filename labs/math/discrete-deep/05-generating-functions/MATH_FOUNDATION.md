# Generating Functions — Math Foundation

Figures below are pasted from the captured runs of CODE_DEEP_DIVE.md
or follow by one exact step on a printed value. All arithmetic integer.

## 1. Binomial and Trinomial Expansions, Coefficient by Coefficient

(1+x)⁴ printed as the array 1, 4, 6, 4, 1 with sum 16 — the C(4,k)
row, total weight-checked at 2⁴. (1+x+x²)³ printed 1, 3, 6, 7, 6, 3, 1
with the per-index line [x³] = 7 among them; sum of coefficients
27 = 3³ printed against the literal power. Coefficient-sum equality is
the product rule read at x = 1: sums multiply when polynomials do.

## 2. The x = 1 Ledger

Σ coefficients of (1+x)(1+x+x²) = 6, printed against 2·3 = 6. The dot
that "all weights at once" makes the evaluation homomorphism explicit:
setting x = 1 in a product multiplies the totals. This identity line
is the cheapest sanity check any generating-function program can carry.

## 3. Two Dice, One Product

D(x) = x + x² + ⋯ + x⁶ has coefficients c₁..c₆ = 1. D(x)² printed
per total: 2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:5, 9:4, 10:3, 11:2, 12:1 —
sum 36, certified on the run. [x⁷] = 6 is the six ordered pairs
(1,6),(2,5),(3,4),(4,3),(5,2),(6,1); the extremes 2 and 12 hold one
pair each, and [x¹] printed 0 as a constraint outlier.

## 4. Partitions by Coefficient Extraction

1/∏_{k≥1}(1−xᵏ) truncated to degree 12 printed: p(0..12) =
1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77. Independent brute count:
p(10) = 42 = 42 and p(12) = 77 = 77 (run equal via paired prints). At
n = 10 the census alternative would scan every multiset of parts; the
GF recurrence instead costs 10 · (10/k) additions per k — exact
integers throughout, no closed form needed.

## 5. Euler Distinct = Odd, on Five Rows

Distinct-part counts and odd-part counts printed side-by-side:
n = 6: 4 = 4; n = 7: 5 = 5; n = 8: 6 = 6; n = 9: 8 = 8; n = 10: 10 =
10. The identity ∏(1+xᵏ) = ∏(1−x^{2k})/(1−xᵏ) telescopes even factors
and is the reason one DP with an inner sign flip converts between the
two, observed at all five n.

## 6. Change-Making, Verified by Triples

Coin set {1, 2, 5}: ways table printed for amounts 0..10 as
1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 10. The brute triple scan printed the
10 witnesses (x₁, x₂, x₅): (0,0,2), (0,5,0), (1,2,1), (2,4,0),
(3,1,1), (4,3,0), (5,0,1), (6,2,0), (8,1,0), (10,0,0) — count 10,
matching [x¹⁰] of (1+x+⋯+x¹⁰)(1+x²+x⁴+⋯)(1+x⁵+x¹⁰) at the same degree.
