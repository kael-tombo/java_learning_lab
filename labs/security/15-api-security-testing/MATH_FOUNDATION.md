# Math Foundation: 15-api-security-testing

## Mathematics of Security Testing

### Vulnerability Risk Assessment

**Risk = Likelihood × Impact**

OWASP Risk Rating:
- Likelihood: Threat Agent × Vulnerability Factors
- Impact: Technical Impact × Business Impact
- Overall Score: Likelihood + Impact / 2

### False Positive Rate

- FP Rate: FP / (FP + TN)
- FPR for SAST tools: typically 5-30%
- FPR for DAST tools: typically 10-40%

### Fuzzing Coverage

Branch coverage = executed branches / total branches × 100%
- Random fuzzing: ~30-50% coverage
- Mutation fuzzing: ~40-60% coverage
- Feedback-guided: ~60-80% coverage
- Grammar-based: ~70-90% coverage

### Static Analysis Metrics

- Lines of Code (LOC) processed per second
- Rules matched per KLOC
- Mean Time to Detect (MTTD)
- Mean Time to Remediate (MTTR)

### Probability of Exploitation

- CVSS v3 exploitability sub-score:
  ES = 8.22 × AV × AC × PR × UI
- Range: 0.0 - 10.0
- Base Score classification:
  - None: 0.0
  - Low: 0.1-3.9
  - Medium: 4.0-6.9
  - High: 7.0-8.9
  - Critical: 9.0-10.0

### Sample Size for Penetration Testing

Confidence interval for vulnerability discovery:
- n = Z² × p × (1-p) / E²
- Z = 1.96 (95% confidence)
- p = expected prevalence
- E = margin of error

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
