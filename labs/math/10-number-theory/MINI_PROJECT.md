# MINI_PROJECT — Number Theory: Prime Toolkit & Modular Arithmetic Lab
> Implement + sieve + verify. ~3 hours.

## Goal
Build a CLI with sieve, Euclid gcd, extended gcd, modular inverse, modexp, Euler φ
sieve, and a Miller–Rabin probabilistic primality test, all cross-checked.

## Build Steps
1. `Sieve.java`: Eratosthenes to N; also Euler φ by multiplicative sieve.
2. `Gcd.java`: naive and Euclid + extended version returning (g,x,y).
3. `Mod.java`: modexp (binary), modInverse via extended gcd.
4. `MillerRabin.java`: k bases; deterministic for <2^32 with fixed bases {2,7,61}.
5. Driver: primality of 50 numbers < 2^32, timing sieve vs Miller–Rabin.

## Sample Output
```
gcd(1071,462)=21, 1071x+462y=21 with x=9,y=-20
3^-1 mod 11 = 4 (3*4=12≡1)
φ(36)=12, sieve agrees
MillerRabin vs sieve disagreements: 0/50
```

## Benchmark Table (fill)
| N or bits | sieve ms | modexp ms | MillerRabin ms |
|-----------|----------|-----------|----------------|
| 1e6 | | | |
| 1e7 | | | |
| 2048-bit prime test | — | — | |

## Acceptance
- [ ] φ sieve matches direct factorization for 1..100.
- [ ] Modular inverse raises when gcd>1.
- [ ] Miller–Rabin with fixed bases matches sieve on all <2^16 sample.

## Extensions
- CRT solver for a system of congruences.
- Hashing demo: polynomial rolling hash collisions counted.
