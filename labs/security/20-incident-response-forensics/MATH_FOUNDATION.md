# Math Foundation: 20-incident-response-forensics

## Mathematics of Incident Response

### Risk Calculation

**Annualized Loss Expectancy (ALE)**:
- SLE (Single Loss Expectancy) = AV (Asset Value) × EF (Exposure Factor)
- ARO (Annualized Rate of Occurrence)
- ALE = SLE × ARO

### Recovery Time Objectives

- RTO (Recovery Time Objective): maximum acceptable downtime
- RPO (Recovery Point Objective): maximum acceptable data loss
- MTD (Maximum Tolerable Downtime): business survival threshold

### Forensic Hashing

- SHA-256: 2^256 possible output values
- Collision probability: k²/2^257 (birthday attack)
- For 10¹5 hashes: P(collision) ˜ 10?²¹ (negligible)

### Incident Severity Matrix

Risk = P(occurrence) × I(impact)
- P: 1-5 (rare to almost certain)
- I: 1-5 (negligible to catastrophic)
- Risk Score: 1-25
- Critical: 20-25, High: 15-19, Medium: 10-14, Low: 5-9, Info: 1-4

### Timeline Analysis

- T0: First malicious action
- T1: Incident detection
- T2: Containment start
- T3: Containment complete
- T4: Eradication complete
- T5: Recovery complete
- Key metric: Dwell time = T1 - T0 (target: < 24 hours)

### Evidence Collection

- Volatile data decay: RAM (seconds), network connections (minutes)
- Disk imaging time: size / write_speed
- Example: 1TB SSD at 500MB/s ˜ 34 minutes

### Chain of Custody Probability

- P(evidence_admissible) = P(custody_complete) × P(integrity_verified)
- Integrity verification: SHA-256 hash match
- Documentation accuracy: timestamp, signature, witness verification

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
