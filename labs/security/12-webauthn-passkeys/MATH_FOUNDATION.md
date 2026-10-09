# Math Foundation: 12-webauthn-passkeys

## Mathematics of WebAuthn

### Elliptic Curve Cryptography

WebAuthn primarily uses ECDSA with P-256 (secp256r1) curves:

**Elliptic Curve Equation** (Weierstrass form):
y² = x³ + ax + b (mod p)

For P-256: p = 2²56 - 2²²4 + 2¹?² + 2?6 - 1

**Key Generation**:
- Private key: random 256-bit integer d
- Public key: Q = d × G (scalar multiplication on curve)

**ECDSA Signature**:
- Random k, compute R = k × G
- Compute r = R.x mod n
- Compute s = k?¹ × (z + r × d) mod n
- Signature: (r, s)

### Challenge Entropy

WebAuthn challenges should be cryptographically random:
- Minimum 16 bytes (128 bits)
- Recommended 32 bytes (256 bits)
- Generated using SecureRandom (not Random)

### User Verification Statistics

- False Acceptance Rate (FAR): Biometric tolerance threshold
- False Rejection Rate (FRR): Legitimate user denied
- FAR target: < 1:50,000 for high security
- FRR target: < 3% for usability

### Credential ID Size

- RP ID hash: 32 bytes (SHA-256)
- Credential ID: 16-128 bytes typical
- Encoded credential ID: ~22-172 bytes (Base64url)

### Cryptographic Hash Functions

Hash functions are fundamental to security protocols:
- **SHA-256**: 256-bit output, 64-bit blocks, 64 rounds
- **SHA-3**: Sponge construction, arbitrary output length
- **BLAKE2**: Faster alternative to SHA-3 with comparable security

### Random Number Generation

Secure random numbers require:
- Entropy source: OS-provided (SecureRandom in Java)
- Minimum 128 bits for challenge values
- 256 bits recommended for key material
- Never use java.util.Random for security

### Key Derivation Functions

KDFs stretch passwords into cryptographic keys:
- PBKDF2: Iterated HMAC, configurable work factor
- bcrypt: Blowfish-based, adaptive cost
- scrypt: Memory-hard, resists ASIC attacks
- Argon2: Modern, winner of PHC competition

### Timing Attacks Prevention

Constant-time operations prevent side-channel attacks:
- XOR operations instead of branching
- Fixed-time memory access patterns
- MessageDigest.isEqual() for hash comparison
- Avoid short-circuit boolean evaluation

### Encoding Overhead

Base64 encoding increases size by exactly 33%:
- 3 bytes ? 4 characters
- Padding: 0-2 '=' characters
- Used in: SAML assertions, JWT tokens, certificates

### Use Case: This Lab

For this specific lab's mathematical requirements:
- [Specific math topic 1]: Applied in [context]
- [Specific math topic 2]: Applied in [context]
- [Specific math topic 3]: Applied in [context]
- [Specific math topic 4]: Applied in [context]
- [Specific math topic 5]: Applied in [context]

### Further Reading

- Handbook of Applied Cryptography (Menezes, van Oorschot, Vanstone)
- Cryptography Engineering (Ferguson, Schneier, Kohno)
- NIST SP 800-57: Recommendations for Key Management
- NIST SP 800-107: Recommendation for Applications Using Hash Functions
- RFC 8017: PKCS #1 v2.2 RSA Cryptography Standard

### Encryption Modes

Common block cipher modes of operation:
- ECB: Electronic Codebook (insecure, reveals patterns)
- CBC: Cipher Block Chaining (needs IV, sequential)
- GCM: Galois/Counter Mode (authenticated encryption, recommended)
- CTR: Counter (parallelizable, no padding)

### Key Exchange Mathematics

Diffie-Hellman key exchange:
- Public parameters: p (prime), g (generator)
- Alice: a (private), A = g^a mod p (public)
- Bob: b (private), B = g^b mod p (public)
- Shared secret: s = B^a mod p = A^b mod p = g^ab mod p

