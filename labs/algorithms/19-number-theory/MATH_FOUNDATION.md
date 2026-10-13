# Math Foundation: Euclid Halving, Sieve Double-Log, Modpow Bits
> Logarithmic gcd, O(n log log n) sieve, O(log e) powers, Fermat statements.

## Definitions
- gcd(a, b): largest d dividing both; Bezout: exists x, y with ax + by = gcd.
- Sieve crossing: multiples of prime p marked from p*p upward.
- Modular power: x^e mod m via binary exponentiation with per-step reduction.
- Fermat: a^(p-1) = 1 mod p for prime p and a not multiple of p.

## Counting argument
- Euclid: a mod b < a/2 every two steps, so O(log min(a, b)) divisions.
- Sieve: sum over primes of n/p operations; prime reciprocal sum grows like log log n.
- Total sieve O(n log log n) time, O(n) booleans; segments trade time for space.
- Modpow: one iteration per exponent bit: Theta(log e) multiplies, O(1) space.

## Recurrence
- gcd(a, b) = gcd(b, a mod b): argument sum shrinks geometrically, not linearly.
- Sieve has no recursion: outer primes to sqrt(n), inner arithmetic progressions.
- Modpow loop invariant: result x base^exp = x^e_original (mod m) throughout.
- Trial factoring to sqrt(n): O(sqrt n) worst case per number, fine for small inputs.

## Derivation of the bound
- Euclid halving: two consecutive steps more than halve the pair sum (standard lemma).
- log2(min) bounds the step count up to a constant factor.
- Sieve double log: sum_{p <= n} n/p = n log log n + lower terms (standard estimate).
- Fermat test cost = one modpow: Theta(log n) multiplies per base.

## Worked mini-proofs
- Proof 1: a mod b < a/2 every two Euclid steps. (4 lines)
- Proof 2: modpow invariant by induction on remaining bits. (4 lines)
- Proof 3: sieve p*p start valid since smaller multiples have smaller factors. (3 lines)

## Exercises with answers
- 1. gcd(30, 20) with coefficients. Answer: 10 = 30(1) + 20(-1).
- 2. Primes below 30. Answer: 2 3 5 7 11 13 17 19 23 29.
- 3. 2^16 mod 17 and 2^560 mod 561. Answer: 1 and 1 (second is Carmichael).

## Pitfalls
- Reading Fermat passes as primality proof (561 refutes the inference).
- Sieve from 2p with no awareness of the wasted work.
- modpow without per-step reduction overflowing.

## Checklist
- Prove Euclid logarithmic via the two-step halving lemma.
- Derive the sieve bound from the prime-reciprocal sum.
