# Information Theory — Math Foundation

Every figure below was printed by a captured run of the
CODE_DEEP_DIVE programs before being written; dyadic arithmetic runs
in exact fractions, the non-dyadic cases in floats with stated
precision.

## 1. Entropy of a Dyadic Distribution, Exactly

For p = (1/2, 1/4, 1/8, 1/8) each −log2 pᵢ is an integer (1, 2, 3, 3),
so the entropy sum stays in fractions:

  H = 1/2·1 + 1/4·2 + 1/8·3 + 1/8·3 = 1/2 + 1/2 + 3/8 + 3/8 = 7/4

The run printed each contribution pᵢ·(−log2 pᵢ) — [('1/2', '1/2'),
('1/4', '1/2'), ('1/8', '3/8'), ('1/8', '3/8')] — and cross-checked
the float loop against float(H): `equal: True`. Interpretation: the
rarest symbol's information is 3 bits, but it shows up rarely
enough that its weighted share is only 3/8.

## 2. Bounds Around 7/4

Any four-symbol distribution has H ≤ log2 4 = 2 (uniformity is the
maximizer) — the run asserted 2.0 > 1.75. The two-symbol benchmark
(2/3, 1/3) is NOT dyadic: its entropy is log2 3 − 2/3, an irrational
≈ 0.9182958340544896 bits, matching the float loop to the last
printed digit. Dyadic masses are exactly the case where H closes as
a rational; everything else must be quoted with a precision contract.

## 3. Huffman Coding on Two Alphabets

Builder run on (1/2, 1/4, 1/8, 1/8): the two 1/8 masses merge first
(→ 1/4), then 1/4 + 1/4 (→ 1/2), then 1/2 + 1/2 — printed code
lengths [1, 2, 3, 3], average Σpᵢℓᵢ = 7/4 = 1.75 bits, and gap
7/4 − 7/4 = 0.0: a dyadic alphabet makes Huffman EXACTLY equal to
entropy. Kraft's inequality audit printed Σ2^(−ℓ) = 1 (a full tree,
no wasted codewords). Second alphabet (2/5, 1/5, 1/5, 1/10, 1/10):
lengths [2, 2, 2, 3, 3], average 11/5 = 2.2 bits, H ≈ 2.121928,
gap 0.07807190511263773 — positive because no prefix code can beat
the entropy, and it can only touch it when every pᵢ is dyadic.
Kraft printed 1 again: optimal prefix code, tight tree.

## 4. KL Divergence: Exact Pairing, Then the Asymmetry Punchline

Exact bookkeeping on P = (1/2, 1/4, 1/8, 1/8) versus
Q = (1/4, 1/8, 1/2, 1/8): every ratio pᵢ/qᵢ is a power of two, so

  KL(P||Q) = 1/2·log2 2 + 1/4·log2 2 + 1/8·log2 (1/4) + 1/8·log2 1
           = 1/2 + 1/4 − 1/4 + 0 = 1/2,
  KL(Q||P) = 1/4·(−1) + 1/8·(−1) + 1/2·2 + 0 = 5/8

The run confirmed 1/2 ≠ 5/8 (`asymmetric: True`), both strictly
positive, and KL(P||P) = 0.0. Asymmetry is the fingerprint of
direction: KL(P||Q) charges the surprise of Q's leaner slot 1 twice
as heavily as the reverse journey does. The float pair
P = (1/2, 1/4, 1/4) against R = (3/4, 1/8, 1/8) printed 0.188722 for
one direction and 0.207519 for the other — unequal again, with no
dyadic shortcut available.

## 5. Mutual Information, Verified Two Ways

Joint table: p(0,0) = 1/2, p(0,1) = 0, p(1,0) = 1/4, p(1,1) = 1/4.
Marginals printed: pX = (1/2, 1/2), pY = (3/4, 1/4). The program
printed H(X) = 1.0 = 1 exactly, H(Y) = 0.811278 bits, H(X,Y) =
sorted exact fraction 3/2, then BOTH routes to MI:

  route A: H(X) + H(Y) − H(X,Y) = 1 + 0.811278 − 1.5 = 0.311278
  route B: direct double sum Σ p(x,y)·log2(p(x,y)/(p(x)p(y)))
           over the three nonzero cells = 0.311278

Agreement within 1e−12 (`equal: True`) is the audit. The chain-rule
decomposition also ran: H(Y|X) = H(X,Y) − H(X) = 3/2 − 1 = 1/2
exactly, and MI = H(Y) − H(Y|X). Reading check: X completely
determines Y only when it does not — a coin tossed between
"Y = X" and "fair", with the fair case arising half the time.

## 6. A Worthwhile Caution on Bases

Every logarithm above is base 2, quoted in "bits"; switching to ln
(nats) multiplies every number here by ln 2 ≈ 0.6931... and silently
breaks Kraft-sum comparisons (Σ2^(−ℓ) assumes bits). The runs used
log2 exclusively — the base is part of the definition, not a style
choice.
