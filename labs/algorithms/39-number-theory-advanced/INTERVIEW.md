# Interview Questions: Advanced Number Theory

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 952 Largest Component Size by Common Factor | Hard | Google | Union-Find + factorization |
| LC 1627 Graph Connectivity With Threshold | Hard | Google | Union-Find + sieve |
| LC 1998 GCD Sort of an Array | Hard | Google | Union-Find + factorization |
| LC 1201 Ugly Number III | Medium | Google | Binary search + inclusion-exclusion |

## NeetCode Reference
Not covered in NeetCode 150. Advanced number theory problems are Google-specific hard questions.

## Company-Specific Questions
### Google
- Design an algorithm to factor large numbers using Pollard's Rho
- How would you find the GCD of an array efficiently after multiple updates?
- Implement the Miller-Rabin primality test for 64-bit integers
- Explain the relationship between Euler's totient function and RSA encryption
- Design a system for generating large primes for cryptographic applications

### Microsoft
- How does Windows cryptography use advanced number theory?
- Design an algorithm for computing discrete logarithms
- Explain the Diffie-Hellman key exchange using modular exponentiation
- How would you implement a cryptographically secure random number generator?

### Meta
- Rare; appears in security-focused roles
- How would you implement a hash function using number theory?
- GCD-based problems for content deduplication
- Prime factorization for feature flag distribution

### Amazon
- Number theory for DynamoDB partition key distribution
- How would you implement consistent hashing using prime modulo?
- GCD-based inventory batching and grouping
- Prime factorization for AWS KMS key generation

### Apple
- Advanced number theory for Secure Enclave cryptography
- How does Apple implement hardware-backed key generation?
- Elliptic curve cryptography (ECC) on mobile devices
- Number theory for iMessage end-to-end encryption

### Oracle
- How does Oracle's Advanced Security option use cryptography?
- Design a database encryption scheme with number theory primitives
- Oracle's implementation of TLS for database connections
- How does Oracle Wallet manage cryptographic keys?

## Real Production Scenarios
- Scenario 1: Cryptographic key generation - using Miller-Rabin with Lucas test for generating 4096-bit RSA prime candidates in a certificate authority processing 100K CSR/day
- Scenario 2: Distributed system partitioning - applying consistent hashing with prime modulo to distribute data across 1024 shards while minimizing data movement when scaling from 128 to 256 shards
- Scenario 3: Security audit - debugging an RSA key generation that occasionally produces weak keys due to insufficient Miller-Rabin iterations, requiring FIPS 186-4 compliance fixes

## Interview Tips
- Pollard's Rho: O(sqrt(p)) where p is the smallest prime factor; Floyd's cycle detection
- Miller-Rabin: deterministic for n < 2^64 with specific witnesses (2, 3, 5, 7, 11, 13)
- Chinese Remainder Theorem: solve x ≡ a_i (mod n_i) where n_i are pairwise coprime
- Legendre/Jacobi symbols for quadratic residue determination and primality testing
- Common edge cases: prime powers, Carmichael numbers, numbers near overflow boundary

## Java-Specific Considerations
- `BigInteger` for arbitrary precision: `BigInteger.valueOf(n).isProbablePrime(certainty)` with Miller-Rabin
- `BigInteger.modPow()` for modular exponentiation (uses Montgomery reduction internally)
- Pollard's Rho: use `BigInteger` for gcd and iteration; `BigInteger.valueOf(2).gcd(diff)` for cycle detection
- Sieve of Eratosthenes: `BitSet` for memory-efficient storage; only odd numbers to halve memory
- Factor via trial division up to sqrt(n) after Pollard's Rho splits n into primes
- Pitfall: deterministic Miller-Rabin witness selection for n > 2^64 requires more careful implementation
- Pitfall: recursion depth in Pollard's Rho; use iterative approach or increase stack size
