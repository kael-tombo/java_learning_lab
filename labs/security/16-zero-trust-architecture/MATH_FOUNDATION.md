# Math Foundation: 16-zero-trust-architecture

## Mathematics of Zero Trust

### Risk Scoring

**Trust Score = S(signal? × weight?)**

Signal dimensions:
- Identity: User authentication strength (0-100)
- Device: Posture compliance (0-100)
- Location: Geographic risk score (0-100)
- Behavior: Deviation from baseline (0-100)
- Time: Access time appropriateness (0-100)

### Access Decision Function

P(grant) = s(S(w? × s?) - t)

Where:
- s(x) = 1/(1 + e??) (sigmoid)
- w? = signal weights
- s? = signal scores
- t = decision threshold

### Micro-Segmentation Scale

Number of possible segments:
- N_services = total microservices
- N_segments = 2^N_services (theoretical max)
- Practical segments ˜ N_services (per-service perimeters)

### Continuous Verification

Session risk reassessment:
- R(t) = R0 × e^(?t) + N(0, s²)
- R0 = initial risk score
- ? = risk decay rate
- s = noise/signal variation

### JIT Access Duration

- Access window: typically 1-4 hours
- Approval time: < 5 minutes (automated)
- Audit frequency: every access event logged

### Policy Evaluation Latency

- Cache hit: < 1ms
- Cache miss: 10-50ms (policy evaluation)
- External PDP: 50-200ms (network call)

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
