# Math Foundation: 14-container-security

## Mathematics of Container Security

### Image Size Optimization

Multi-stage builds reduce final image size:
- Final size = S(layers after last FROM)
- Layer caching: hit rate ~80% for well-structured Dockerfiles

### Vulnerability Scoring

CVSS v3.1 Base Score:
- Exploitability: AV × AC × PR × UI
- Impact: Conf × Integ × Avail
- Base Score function of Impact Sub-Score and Exploitability Sub-Score

### Resource Limits (cgroups)

CPU Quota Equations:
- cpu.cfs_period_us = 100000 (100ms default)
- cpu.cfs_quota_us = period × n_cores
- For 0.5 core: quota = 50000

Memory Limits:
- Hard limit: OOM killer triggered when exceeded
- Soft limit: Best-effort constraint
- Swappiness: 0-100 (page reclaim tendency)

### Network Policy Segmentation

Kubernetes Network Policy isolation:
- Ingress rules: allowed sources per pod
- Egress rules: allowed destinations per pod
- Default deny: explicit allow rules required

### Image Scanning Metrics

- True Positive Rate: TP / (TP + FN)
- False Positive Rate: FP / (FP + TN)
- Precision: TP / (TP + FP)
- F1 Score: 2 × Precision × Recall / (Precision + Recall)

### Layer Caching Efficiency

Cache hit probability:
- P(hit) = S(layer_size × cache_hit_rate) / total_size
- Effective build time = S(layer_build_time × (1 - P(hit)))

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
