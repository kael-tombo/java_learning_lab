# Security: Set Theory in Practice

## RSA's Algebra Is Set Theory in Disguise

RSA works in the ring Z/nZ = {0, 1, …, n−1} with multiplication mod n, where n = pq. For primes p, q, Euler's theorem says a^φ(n) ≡ 1 (mod n) for gcd(a, n) = 1, with φ(n) = (p−1)(q−1). The units of Z/nZ — the elements with a multiplicative inverse — form a *set* of size φ(n), and key generation is: choose e with 1 < e < φ(n) and gcd(e, φ(n)) = 1, publish (n, e), keep d ≡ e⁻¹ (mod φ(n)).

Small worked example: p = 61, q = 53 → n = 3233, φ = 60·52 = 3120. Pick e = 17 (gcd(17, 3120) = 1). Then d = 2753 since 17·2753 = 46801 = 15·3120 + 1. Encrypt m = 65: c = 65^17 mod 3233 = 2790. Decrypt: 2790^2753 mod 3233 = 65. The security assumption is that the *set* of prime factors of n is unknowable from n alone.

A structural warning: Z/nZ is a ring but generally **not** a field — for n = 15, 3·5 ≡ 0 with neither factor zero (zero divisors). Code that divides by a residue without checking `gcd(x, n) == 1` silently computes garbage; when gcd(x, n) = k > 1 you have factored n (this is exactly how Pollard's p−1 and trial division exploits leak factors).

## Oracles as Sets

A cryptographic oracle is a set membership question posed to a system: "Is this padding valid?" (POODLE), "Is this guess a valid MAC?" (timing side channel). Defenses reduce the oracle's answers: constant-time comparison prevents the response from distinguishing elements from non-elements, and rate limits shrink how many queries an attacker can pose per unit time.

## Access Control Is Set Algebra

Permissions are sets: effective rights = (granted) − (revoked) − (denied ∪ ∩). A privilege-escalation bug is almost always a set error: applying the grant *after* the revoke (so the grant reintroduces the revoked element), forgetting that `deny` must win via set difference rather than last-write-wins, or computing the union of roles before subtracting bans. Model it as `effective = (⋃ roles) − ⋃ bans − ⋂ mandatoryDenies` and the ordering bugs vanish.

## Denial of Service via Set Growth

- Unbounded dedup sets (storing every visited session ID) let an attacker grow memory to O(requests) — bound it with an LRU or a time-windowed set.
- Collision attacks: a `HashSet` keyed on attacker-controlled strings degrades from O(1) to O(n) per lookup when the attacker can force hash collisions (as in HashDoS against language runtimes), turning a login-lookup endpoint into CPU exhaustion. Mitigation: keyed hashing (SipHash) or rejecting huge colliding keys.
- Power-set-style feature enumeration (subsets of user-selected flags) explodes as 2^n — cap n.

## Bloom Filters: Sets with False Positives

A Bloom filter answers "definitely not in the set" or "probably in the set," using k hash functions over a bit array of m bits. False-positive probability ≈ (1 − e^(−kn/m))^k. Because it never yields false negatives, it is safe as a pre-filter (skip expensive lookup when the filter says absent) and unsafe as an authorization decision — "probably a member" must never grant access.

## Secure-Coding Checklist for Set-Based Logic

- [ ] Universe declared wherever a complement or "everything else" filter is computed.
- [ ] Grant/revoke order written as an expression (difference after union), then implemented in that order.
- [ ] Dedup sets bounded (max size / TTL) so attacker-controlled inputs cannot grow them without limit.
- [ ] Hash-keyed hashing (SipHash) or input caps where keys are attacker-controlled (HashDoS).
- [ ] Bloom filters and other probabilistic sets used only as pre-filters, never as the final allow/deny.
- [ ] Set differences asserted in tests: |A − B| = |A| − |A ∩ B| (catches accidental union/XOR usage).
