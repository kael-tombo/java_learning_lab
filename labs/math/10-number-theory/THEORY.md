# Number Theory: A Comprehensive Treatment

## 1. Divisibility and Prime Numbers

### 1.1 Fundamental Theorem of Arithmetic
Every integer n > 1 can be written uniquely as a product of primes: n = p₁^a₁ · p₂^a₂ · ... · pₖ^aₖ.

### 1.2 Prime Number Theorem
The prime counting function π(x) ∼ x / ln(x) as x → ∞. This means primes become sparse but never cease.

### 1.3 Distribution of Primes
- There are infinitely many primes (Euclid's proof)
- The gap between consecutive primes grows slowly on average
- Dirichlet's theorem: arithmetic progressions contain infinitely many primes

## 2. Greatest Common Divisor

### 2.1 Euclidean Algorithm
gcd(a, b) = gcd(b, a mod b) for b ≠ 0.

### 2.2 Extended Euclidean Algorithm
Finds integers x, y such that ax + by = gcd(a, b). This is fundamental for computing modular inverses.

### 2.3 Applications
- Computing modular inverses
- Solving linear Diophantine equations
- Simplifying fractions

## 3. Modular Arithmetic

### 3.1 Congruences
a ≡ b (mod m) means m | (a - b).

### 3.2 Properties
- Reflexive: a ≡ a (mod m)
- Symmetric: a ≡ b ⇒ b ≡ a
- Transitive: a ≡ b, b ≡ c ⇒ a ≡ c
- Compatible with +, −, ×

### 3.3 Modular Inverses
a has an inverse modulo m iff gcd(a, m) = 1. The inverse satisfies a · a⁻¹ ≡ 1 (mod m).

## 4. Chinese Remainder Theorem

If moduli m₁, m₂, ..., mₖ are pairwise coprime, the system of congruences:
x ≡ a₁ (mod m₁), x ≡ a₂ (mod m₂), ..., x ≡ aₖ (mod mₖ)
has a unique solution modulo M = m₁m₂···mₖ.

### 4.1 Construction
x = Σ aᵢ · Mᵢ · yᵢ (mod M), where Mᵢ = M/mᵢ and yᵢ = Mᵢ⁻¹ (mod mᵢ).

### 4.2 Applications
- RSA acceleration (using Garner's algorithm)
- Secret sharing (Shamir's scheme uses CRT)
- Large integer arithmetic

## 5. Euler's Theorem and Fermat's Little Theorem

### 5.1 Fermat's Little Theorem
For prime p and integer a not divisible by p: a^(p-1) ≡ 1 (mod p).

### 5.2 Euler's Theorem
For gcd(a, n) = 1: a^φ(n) ≡ 1 (mod n), where φ(n) is Euler's totient function.

### 5.3 Euler's Totient Function
φ(n) = n · Π_{p|n} (1 − 1/p), counting numbers ≤ n that are coprime to n.

## 6. RSA Cryptosystem

### 6.1 Key Generation
1. Choose large primes p, q
2. Compute n = p · q
3. Compute φ(n) = (p−1)(q−1)
4. Choose e such that gcd(e, φ(n)) = 1 (typically 65537)
5. Compute d = e⁻¹ mod φ(n)
6. Public key: (n, e); Private key: (n, d)

### 6.2 Encryption/Decryption
- Encrypt: c = m^e mod n
- Decrypt: m = c^d mod n

### 6.3 Security
Security relies on the computational difficulty of factoring large integers. Breaking RSA requires factoring n, which is believed to be hard for sufficiently large n (2048+ bits).

## 7. Primality Testing

### 7.1 Trial Division
Check divisibility by all primes up to √n. Deterministic but slow for large numbers.

### 7.2 Miller-Rabin Test
Probabilistic test based on the property: if n is prime, then for any a, either a^d ≡ 1 (mod n) or a^(2^r d) ≡ −1 (mod n) for some r.

### 7.3 Deterministic Tests
- AKS primality test (polynomial time, but slow in practice)
- Deterministic Miller-Rabin for n < 3,317,044,064,679,887,385,961,981

## 8. Advanced Topics

### 8.1 Quadratic Reciprocity
Gauss's law relating solvability of quadratic congruences.

### 8.2 Elliptic Curves
Used in ECC (Elliptic Curve Cryptography) and ECDSA.

### 8.3 Lattice Cryptography
Post-quantum cryptographic systems based on lattice problems (SVP, LWE).

## 9. Computational Complexity

- GCD: O(log min(a,b)) using Euclidean algorithm
- Modular exponentiation: O(log exp) using binary exponentiation
- Miller-Rabin: O(k log³ n) where k is iterations
- Trial division: O(√n)
- RSA key generation: O(log³ n) for prime generation

## 10. Historical Notes

- Euclid (300 BCE): Euclidean algorithm, proof of infinite primes
- Fermat (1640): Little theorem, many number theory conjectures
- Euler (1763): Totient function, generalization of Fermat's theorem
- Gauss (1801): Disquisitiones Arithmeticae, quadratic reciprocity
- Rivest, Shamir, Adleman (1977): RSA cryptosystem
- Agrawal, Kayal, Saxena (2002): AKS primality test (polynomial time)
