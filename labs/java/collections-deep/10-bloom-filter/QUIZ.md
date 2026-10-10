# Quiz: Bloom Filter

## Q1. State the FPR formula and derive it in three steps.

**A.** p = (1 − e^(−kn/m))^k. (1) P(bit still 0) = (1−1/m)^(kn) ≈
e^(−kn/m). (2) P(bit set) ≈ 1 − e^(−kn/m). (3) All k probes set → raise
to k.

## Q2. Derive optimal k and m.

**A.** Minimize p over k → e^(−kn/m) = 1/2 → k = (m/n)·ln 2 (half the bits
set, p = (1/2)^k). Invert with p = (1/2)^k → m = −n·ln p/(ln 2)².

## Q3. Canonical numbers for n=10000, p=0.01?

**A.** m ≈ 95 851 bits (~12 KB), k = 7. Measured FPR ladder: k=1: 9.9%,
3: 1.9%, 5: 1.1%, 7: 1.0%, 10: 1.3% (rises past optimum).

## Q4. How does double hashing produce k positions from 2?

**A.** g_i = h1 + i·h2 (mod m), Kirsch–Mitzenmacher 2006: same asymptotic
FPR without k hash evaluations. h2 forced odd so probes cover the array;
modulo in long arithmetic.

## Q5. Why no deletion or enumeration?

**A.** Bits are shared — clearing one can unset another element's evidence
(false negative). Elements aren't stored, so nothing to iterate or count
(size unknowable from bits).

## Q6. When is union valid, and how?

**A.** Bitwise OR, iff (m, k, hash functions) identical on both sides.
Result = filter of the set union. AND-intersection is not closable.

## Q7. What breaks if you skip the hash finalizer?

**A.** Raw `hashCode` low-bit weakness correlates probes; measured FPR
overshoots the formula. The uniform-hash assumption is the formula's
precondition.
