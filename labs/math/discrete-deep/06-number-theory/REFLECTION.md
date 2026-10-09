# Reflection: Number Theory

## The Inverse Confusion Was Worth the Exercise

"2⁻¹ mod 7 = 4" rewired something: division modulo m was never division — it is solving ax ≡ 1 in a world where only remainders exist. Watching the extended Euclid *construct* the answer (1 = 352 − 117·3 → inverse −117 ≡ 235) rather than invoke a theorem made the existence proof mechanical. The lesson generalizes: whenever an operation "should" exist, look for the algorithm that produces witnesses; if it halts without one, the operation doesn't exist (gcd(6, 9) = 3 → no inverse).

## Precondition Discipline Is the Meta-Skill

Fermat needs p prime *and* gcd(a, p) = 1; CRT needs pairwise-coprime moduli; Euler needs gcd(a, n) = 1. Every broken example in COMMON_MISTAKES is a violated hypothesis wearing the costume of a correct computation — 561 passing the Fermat test is the sharpest: the theorem is true, the input lied. I now read each theorem's statement for its "if" clauses before using it in code, and I write those clauses as `require` checks.

## The Hand Traces Pay Off Immediately

gcd(1071, 462) → 21, 3⁻¹ mod 352 → 235, 5¹²³ mod 7 → 6 (twice, by two methods), CRT → 23, sieve π(30) = 10 — five self-checking computations, each agreeing with its independent verification. That habit (two methods, one answer) is what makes the RSA toy example trustworthy: the encryption arithmetic was checkable with a calculator, and the decryption was justified by Euler's theorem rather than a 235-digit exponentiation.

## The Security File Changed How I Read Key Sizes

Working through keygen by hand — p, q, n, φ, e, d with the explicit check 3·235 = 705 = 2·352 + 1 — makes "2048-bit RSA" legible: the size is a statement about the *factoring* end of an O(√n)-vs-O(log³ n) asymmetry, and the Miller–Rabin round count is a 4^(−k) coin flip that I choose. Parameters that used to be folklore now read as arithmetic.

## History Worth Remembering

Euclid's product-plus-one proof is two lines and still current; Gauss's congruence notation is literally the syntax in this lab's code comments; Euler turned Fermat's one-prime statement into a φ(n) theorem that a 1978 paper turned into a key exchange. The line from *Elements* to TLS is short enough to recite — and Carmichael's 561 is the reminder that every one of these theorems fails honestly when its hypothesis does.

## Carry-Forward

- Use `BigInteger.modPow` as the oracle for every hand-rolled modular routine (the ARCHITECTURE test plan), and keep Miller–Rabin deterministic (fixed bases) in tests.
- For labs/protocols: the CRT-as-coordinates picture is the tool for multi-prime RSA and for reasoning mod n = pq without factoring in the proof.
- Open threads: quadratic reciprocity (I can state it; six proofs remain unread), primitive roots (existence proof via group theory), and the number field sieve's polynomial selection — the one part of PERFORMANCE only quoted rather than derived.

## What I Would Do Differently in Code

Normalize every residue into [0, m) at function boundaries (one helper, called twice), assert `a·a⁻¹ ≡ 1 (mod m)` in tests instead of trusting extgcd's internals, and never let a hot path build a sieve implicitly — prime generation gets its own explicit, parameterized function so the Miller–Rabin round count is visible in review.
