# Flashcards — Number Theory Advanced

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | gcd(a,b) identity | gcd(a,b) = gcd(b, a mod b) |
| 2 | Euclid step count | Θ(log min(a,b)) |
| 3 | Bézout | s·a + t·b = gcd(a,b) |
| 4 | Inverse from Bézout | when gcd(a,m)=1, a⁻¹ ≡ s (mod m) |
| 5 | modPow multiplications | Θ(log e) |
| 6 | Euler theorem | a^φ(m) ≡ 1 (mod m) when gcd(a,m)=1 |
| 7 | Fermat as special case | m prime ⇒ φ(m) = m-1 |
| 8 | Exponent reduction | a^e ≡ a^(e mod φ(m)) only if gcd(a,m)=1 |
| 9 | Sieve start per prime | p² |
| 10 | Sieve total work | Θ(n log log n) |
| 11 | Miller–Rabin error per round | ≤ 1/4 |
| 12 | Miller–Rabin k rounds error | ≤ 4⁻ᵏ |
| 13 | n-1 decomposition for MR | n-1 = 2^s·d, d odd |
| 14 | MR witness condition | a^d ≡ 1, or a^(2^r d) ≡ -1 for some r |
| 15 | CRT solution formula | x = Σ bᵢ Mᵢ yᵢ, yᵢ = Mᵢ⁻¹ mod mᵢ |
| 16 | CRT requirement | pairwise-coprime moduli |
| 17 | Java negative % | result keeps the sign of the dividend |
| 18 | Fix for Java % | (x % m + m) % m |
| 19 | φ(n) meaning | count of integers in [1,n] coprime to n |
| 20 | φ(p) for prime p | p-1 |
| 21 | φ(p^k) | p^k - p^(k-1) |
| 22 | φ multiplicative | φ(mn) = φ(m)φ(n) when gcd(m,n)=1 |
| 23 | a^φ(m) mod m when gcd≠1 | no simple reduction — compute directly |
| 24 | Long overflow risk | a*b % m with a,b near 10⁹.⁵ overflows long |
| 25 | Fix for overflowing multiply-mod | BigInteger.modPow, or split the multiplication |
| 26 | Deterministic MR small bound | a fixed small witness set suffices below ~3.3·10⁹⁴ |
| 27 | Carmichael number | composite n with a^(n-1)≡1 for all coprime a — Fermat fails, MR does not |
| 28 | Strong probable prime | passes MR base a for that a |
| 29 | xgcd recursion invariant | maintain (old_r, r) and (old_s, s), update via quotients |
| 30 | Worst case Euclid | consecutive Fibonacci numbers |
| 31 | Every other Fibonacci in Euclid | ratio ≈ φ² per two steps |
| 32 | Modular inverse existence | exactly when gcd(a,m)=1 |
| 33 | CRT uniqueness | unique mod Πmᵢ |
| 34 | Garner's / mixed-radix CRT | combines congruences one modulus at a time |
| 35 | Sieve memory | Θ(n) — bitset to halve it |
| 36 | φ(2^k) | 2^(k-1) |
| 37 | Euler generalises Fermat | prime p ⟹ φ(p)=p-1 recovers FLT |
| 38 | MR cost per round | Θ(log³ n) naive, Θ(log² n) with fast mul |
| 39 | Sieve smallest prime factor variant | store spf for factorisation in O(log n) |
| 40 | Extended Euclid used in RSA | to compute d = e⁻¹ mod φ(n) |
| 41 | Why MR needs odd n>2 | the 2-adic decomposition is undefined for even n |
| 42 | Base −1 mod n is always −1 | n-1 ≡ -1; MR checks a^(2^r d) ≡ -1 to catch it |
| 43 | φ(mn) for shared factors | NOT multiplicative — use n·Π(1-1/p) |
| 44 | Euler's theorem corollary | a^(kφ(m)+r) ≡ a^r (mod m) for gcd=1 |
| 45 | Inverse via pow for prime p | a⁻¹ ≡ a^(p-2) (mod p) |
| 46 | Negative exponent in modPow | compute inverse first, then exponentiate |
| 47 | Number of residues coprime to p^k | p^k - p^(k-1) |
| 48 | CRT count of solutions | one mod M when consistent |
| 49 | Totient chain | n·Π_{p|n}(1 - 1/p) |
| 50 | Euler criterion | a^((p-1)/2) ≡ ±1 decides quadratic residuosity |
| 51 | gcd(0,n) | n — Euclid base case |
| 52 | a^0 mod m | 1 even for gcd(a,m)>1 — 1 ≡ 1 |
| 53 | Euler's theorem failure example | 2^φ(6) = 2² = 4 ≢ 1 (mod 6) |
| 54 | Strong liar fraction | ≤ 1/4 of bases |
| 55 | MR rounds for crypto sizes | 40+ for large n |
| 56 | Witness set for n < 3,317,444,400,000,000,000 | use bases 2,3,5,7,11,13,17,19,23,29,31,37 |
| 57 | Fermat liar for 561 | 561 = 3·11·17; for coprime a, a^560≡1 |
| 58 | CFR April: multiplicative order | ord_m(a) divides φ(m) |
| 59 | Repeated squaring ladder example | 3^13: 3,9,81,6561 by squaring, pick 8+4+1 |
| 60 | Euler totient of 12 | 4 (1,5,7,11) |
| 61 | CRT with non-coprime moduli | solution exists iff bᵢ≡bⱼ (mod gcd(mᵢ,mⱼ)) |
| 62 | φ(n) parity | φ(n) is even for n ≥ 3 |
