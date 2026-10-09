# Math Foundation: 13-secrets-management

## Mathematics of Secrets Management

### Entropy and Key Strength

**Secret Entropy Calculation**:
- H = log2(N) bits, where N = number of possible values
- Alphanumeric (62 chars), length L: H = L × log2(62)
- 16-char alphanumeric: H = 95.3 bits
- 32-char alphanumeric: H = 190.5 bits

**Recommendation**: = 128 bits of entropy for API keys

### Shamir's Secret Sharing (Vault Unseal)

Splits a secret S into n shares where k shares are required for reconstruction:

- Polynomial: f(x) = S + a1x + a2x² + ... + a??1x^(k-1)
- Shares: (i, f(i)) for i = 1, 2, ..., n
- Lagrange interpolation: S = f(0) = S(f(x?) × L?(0))

### AES-256 Encryption

- Block size: 128 bits
- Key size: 256 bits
- Rounds: 14
- Modes: GCM (recommended), CBC, CTR

### Secret Rotation Frequency

- Annualized Loss Expectancy: ALE = SLE × ARO
- Single Loss Expectancy: SLE = AV × EF
- Optimal rotation interval trades off security vs operational cost

### Hashing for Integrity

- SHA-256: 256-bit output
- HMAC-SHA256: Keyed hash for message authentication
- PBKDF2: Key stretching with configurable iterations

### Lease Duration Mathematics

- TTL (Time-To-Live): Max lease duration
- Renew window: Before TTL/2 expiry
- Grace period: Extended validity after TTL expiry

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
