# Common Mistakes — Number Theory

Each error below is stated with the exact wrong arithmetic that a
run exposed; the numbers are real, not constructed strawmen.

## 1. Sign Flip in the Bezout Back-Substitution

The true chain gives 2 = 2·6 − 10 then 2 = 2·46 − 9·10; expanding
10 = 240 − 5·46 must flip the inner sign: 2 = 2·46 − 9·240 + 45·46 =
47·46 − 9·240. Dropping the flip silently produces the false
identity 2 = 2·46 + 9·240, whose left side actually evaluates to
2252 — the run re-multiplied it. Any claim "checked" against 2252
is not a check.

## 2. Grabbing the Wrong Slot of the Bezout Pair

For ext_gcd(26, 7) the identity is 3·26 − 11·7 = 1: the coefficient
of 26 is 3, of 7 is −11. The inverse of 7 comes from the 7-slot
(−11 ≡ 15), but a careless reader (and a first draft of this lab's
program) took 3 mod 26 and "verified" 7·3 ≡ 21 — a number that
satisfies nothing. Slot discipline: the inverse of b mod m is the
coefficient standing next to b, not next to m.

## 3. Demanding an Inverse When gcd ≠ 1

pow(6, -1, 14) raises `base is not invertible for the given
modulus` because gcd(6, 14) = 2. Arguing "every nonzero residue has
an inverse" is true only in fields, i.e. prime moduli; mod 14 the
element 6 annihilates nothing — 6·7 = 42 = 0 mod 14, a nonzero pair
multiplying to zero, impossible when inverses exist.

## 4. Fermat Quoted at Composite Moduli

2¹⁴ mod 15 = 4, not 1: the (p−1)-form of Fermat needs p prime.
Euler's form survives — 2⁸ ≡ 1 (mod 15) with φ(15) = 8 — but only
for bases coprime to 15; a^φ(15) ≡ 1 fails for a sharing a factor
(a = 5: 5⁸ = 390625 ≡ 10 mod 15). Worse, Carmichael numbers like
561 pass the Fermat test for every coprime base while being
composite (3·11·17) — the primality screen has known liars.

## 5. CRT Applied Without the Coprimality Audit

Pairing x ≡ 1 (mod 4) with x ≡ 3 (mod 8) has no solution at all —
the brute sweep over 0..15 printed `[]` — because gcd(4, 8) = 4
does not divide 3 − 1 = 2. Meanwhile the consistent non-coprime
pair x ≡ 2 (mod 4), x ≡ 4 (mod 6) resolves not modulo 24 but modulo
lcm(4, 6) = 12 to x ≡ 10. The M = m₁m₂ formula and the existence
guarantee both assume pairwise coprime moduli.

## 6. Trusting Python divmod Signs Blindly

divmod(-17, -5) returns (3, -2): a remainder with the sign of the
divisor. The canonical answer is q = 4, r = 3 (both verified in the
run). Code that consumes raw divmod remainders as array indices,
hash keys, or "positions in 0..m−1" will index negatively or split
classes; normalize with `r %= m` (or add |b| when r < 0) before any
positional use.

## 7. Reducing a Division Instead of Dividing the Modulus

For 14x ≡ 7 (mod 21), "cancelling 7" naively yields 2x ≡ 1 (mod 21),
whose single solution x ≡ 11 (mod 21) was printed by the run — but
the true solution set is x ≡ 2 (mod 3), i.e. the seven classes
{2, 5, 8, 11, 14, 17, 20} mod 21. Cancellation is legal here (7
divides both 14 and 7) yet the modulus must shrink with it;
uncancelled-modulus answers lose six valid solutions. Cancellation
is licensed only when the factor is invertible or divides
everything in sight on both sides.
