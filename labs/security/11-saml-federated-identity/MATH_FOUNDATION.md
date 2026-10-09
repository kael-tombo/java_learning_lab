# Math Foundation: 11-saml-federated-identity

## Mathematics of SAML Security

### XML Digital Signature Mathematics

SAML uses XML Digital Signature (XML-DSig) for integrity and authentication:

**RSA Signature Algorithm**:
- Key generation: n = p × q (RSA modulus)
- Signature: s = m^d mod n (private key signing)
- Verification: m = s^e mod n (public key verification)

**SHA-256 Hash**:
- Input message M, output 256-bit digest
- Used in digesting SAML elements before signing

### X.509 Certificate Mathematics

- **RSA-2048**: n is 2048 bits (617 decimal digits)
- **Elliptic Curve P-256**: 256-bit keys with equivalent security to RSA-3072
- **Certificate Chain Verification**: Hash chain validation from leaf to root CA

### Clock Skew and Time Synchronization

SAML assertions are time-bound:
- NotBefore: t0
- NotOnOrAfter: t1 = t0 + ?t (where ?t is typically 5 minutes)
- Clock skew tolerance: ±d (typically 5 minutes)
- Valid window: [t0 - d, t1 + d]

### Base64 Encoding Overhead

- SAML XML is often Base64-encoded for HTTP POST binding
- Overhead: ~33% size increase
- Max SAML response size: ~80KB typical, up to 1MB

### Probability of Hash Collision

- SHA-256: 2^128 collision resistance (birthday bound)
- For n signed assertions, collision probability: n²/2^257
- Practical collision risk: negligible for enterprise SSO

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

