# Reflection: Generating Functions

## The One Move Worth Memorizing

Sum the recurrence against xⁿ and re-index. Everything else (solving for A(x), factoring, partial fractions, expanding) is algebra you already know. Seeing "lag by one → multiply by x, lag by two → multiply by x²" turn a difference equation into a polynomial equation is the moment the technique stops being magic; the verification step (a₀ = 1, a₁ = 3 reproduced exactly) confirmed the machinery end to end.

## What "Formal" Actually Buys

Before this lab I treated convergence as a precondition for series. The clarification that formal power series are a ring (with division legal iff the divisor's constant term ≠ 0) — and that counting never asks about x as a number — removed a persistent source of hesitation. It also made the coin-change product honest: Π 1/(1 − x^c) is a perfectly meaningful object even though it has poles everywhere on the unit circle; only *evaluation* would care, and we only ever extract coefficients.

## The Dictionary Is the Skill

Structural translation — sequence-of → product, set-of → exp, choice → sum — is the transferable part; the coefficient extraction is clerical. I now read enumeration problems first for structure ("is the construction a sequence, a set, or a choice?") and only then pick arithmetic. That ordering (structure first, algebra second) prevented me from blindly writing 1/(1−x)² for compositions, which the dictionary check immediately corrected: compositions need x/(1−2x), giving 2^{n−1}.

## Coin Change Showed the Boundary of Closed Forms

The 50¢ derivation was satisfying (1 → 11 → 36 → 49 → 50 by four folds), and the punchline mattered more: because the five-factor product is *not* rational, no linear recurrence exists for the full coin-change sequence and no partial-fraction miracle is coming. Rational GF ⇔ recurrence ⇔ possible closed form is a genuine classification, not a slogan — it tells you before you start whether to reach for algebra or DP.

## The Security Connection Was the Surprise

Learning that LFSR stream-cipher security *is* the degree of the keystream's rational GF (Berlekamp–Massey recovers Q from 2L bits) and that GHASH/CRC run on Galois-field polynomial arithmetic — while disambiguating "GF" — gave the lab a concrete payoff. Linearity making CRC cheap and forgeable is a nice reminder that the property enabling an optimization is often the property an attacker exploits.

## Carry-Forward

- Lab 06 (number theory) will use GFs implicitly: the geometric series 1/(1−x) mod p, generating functions for divisor sums, and the fact that Σ_{d|n} μ(d) = [n = 1] is a coefficient identity — worth recalling there.
- For algorithms coursework: Rémy/flajolet-style average-case analysis (expected cost of recursive routines) is now within reach; Flajolet–Sedgewick is the book.
- Practically: any recurrence I meet in code gets the same three-question treatment — is it linear? constant-coefficient? then its GF is rational; read Q off as the recurrence and use fast doubling for large n.

## The Sentence to Remember

"Write the object's structure as a product, sum, or exponential; solve for the series; extract the coefficient you need." That recipe — structure first, algebra second, number last — is the whole method, and every section of this lab was one application of it in a different structural costume.
