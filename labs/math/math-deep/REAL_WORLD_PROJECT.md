# Real-World Project: Cryptography with Abstract Algebra

## Overview
Build a working public-key cryptography system using abstract algebra: RSA (based on modular arithmetic in ℤ/nℤ) and elliptic curve cryptography (based on group structure of elliptic curves). This demonstrates how pure mathematics secures the internet.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- NIST Cryptographic Standards: https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines
- IACR ePrint Archive (Cryptology): https://eprint.iacr.org/

## Project Goals
1. Implement RSA encryption/decryption from scratch
2. Implement elliptic curve point arithmetic
3. Build Diffie-Hellman key exchange
4. Analyze security parameters
5. Benchmark against standard libraries

## Mathematical Background

### RSA Cryptosystem
Based on the difficulty of factoring large semiprimes n = pq.

**Key generation:**
1. Choose large primes p, q
2. Compute n = pq and φ(n) = (p-1)(q-1)
3. Choose e with gcd(e, φ(n)) = 1 (typically 65537)
4. Compute d ≡ e⁻¹ (mod φ(n))
5. Public key: (n, e); Private key: (n, d)

**Encryption:** c ≡ m^e (mod n)
**Decryption:** m ≡ c^d (mod n)

**Security:** Recovering d from (n, e) requires factoring n.

### Elliptic Curve Cryptography (ECC)
Based on the discrete logarithm problem on elliptic curves.

**Curve equation:** y² = x³ + ax + b (over a field)

**Point addition:** Given points P and Q, draw line through them; third intersection with curve, reflected over x-axis, is P + Q.

**Scalar multiplication:** kP = P + P + ... + P (k times). Easy to compute; hard to reverse (discrete log).

**ECC advantages:** Smaller key sizes than RSA for equivalent security (256-bit ECC ≈ 3072-bit RSA).

### Diffie-Hellman Key Exchange
Allows two parties to establish a shared secret over a public channel:
1. Agree on public parameters (g, p)
2. Alice sends g^a (mod p); Bob sends g^b (mod p)
3. Both compute g^(ab) (mod p)

## Implementation Plan

### Phase 1: RSA Core
```python
import random

def is_prime(n, k=40):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    while True:
        n = random.getrandbits(bits) | 1 | (1 << (bits - 1))
        if is_prime(n):
            return n

def rsa_keygen(bits=2048):
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)
    return (n, e), (n, d)
```

### Phase 2: RSA Encryption
```python
def rsa_encrypt(message, public_key):
    n, e = public_key
    m = int.from_bytes(message, 'big')
    c = pow(m, e, n)
    return c.to_bytes((n.bit_length() + 7) // 8, 'big')

def rsa_decrypt(ciphertext, private_key):
    n, d = private_key
    c = int.from_bytes(ciphertext, 'big')
    m = pow(c, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, 'big')
```

### Phase 3: Elliptic Curve Arithmetic
```python
class EllipticCurve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

    def add(self, P, Q):
        """Add two points on the curve."""
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None  # Point at infinity
        if P == Q:
            lam = (3 * x1**2 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p
        x3 = (lam**2 - x1 - x2) % self.p
        y3 = (lam * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def multiply(self, k, P):
        """Scalar multiplication kP via double-and-add."""
        result = None
        addend = P
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result
```

### Phase 4: Diffie-Hellman
```python
def diffie_hellman(private_key, g, p):
    """Compute public value g^private mod p."""
    return pow(g, private_key, p)

def shared_secret(public_value, private_key, p):
    """Compute shared secret public^private mod p."""
    return pow(public_value, private_key, p)
```

### Phase 5: Security Analysis
- Benchmark key generation time
- Compare key sizes for equivalent security
- Implement timing attack countermeasures
- Test against known test vectors

## Validation
- Verify RSA round-trip: decrypt(encrypt(m)) == m
- Verify ECC point addition on known curves
- Test Diffie-Hellman shared secret agreement
- Compare with OpenSSL for correctness

## Extensions
- Digital signatures (ECDSA)
- Padding schemes (OAEP for RSA)
- Curve25519 implementation
- Post-quantum cryptography (lattice-based)
- Certificate authority simulation

## Deliverables
- `rsa.py` — RSA implementation
- `ecc.py` — Elliptic curve cryptography
- `diffie_hellman.py` — Key exchange
- `benchmark.py` — Performance analysis
- `README.md` — theory, usage, and security notes
