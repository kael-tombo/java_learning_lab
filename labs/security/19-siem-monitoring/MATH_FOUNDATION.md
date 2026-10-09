# Math Foundation: 19-siem-monitoring

## Mathematics of SIEM Monitoring

### Event Rate Calculation

**Events Per Second (EPS)**:
- EPS = total_events / time_period
- Peak EPS = max(events_per_second_sample)
- Sustained EPS = 75th percentile EPS

### Storage Requirements

- Daily storage: EPS × avg_event_size × 86400 × compression_ratio
- Compression ratio: typically 0.3-0.5 (Elasticsearch)
- Retention: daily_storage × retention_days × replication_factor

### Correlation Thresholds

- Threshold rules: P(event_count > threshold | baseline) < a
- a = significance level (typically 0.01-0.05)
- Baseline = moving average over sliding window

### Anomaly Detection Statistics

Z-score:
- z = (x - µ) / s
- |z| > 3: potential anomaly (99.7% confidence)
- |z| > 4: high-confidence anomaly

EWMA (Exponentially Weighted Moving Average):
- S_t = a × x_t + (1-a) × S_(t-1)
- a = smoothing factor (typically 0.1-0.3)

### Alert Fatigue

- True Positive Rate: TP / (TP + FP)
- Precision: TP / (TP + FP)
- Alert volume reduction = 1 - (alerts_after / alert_before)
- Target precision: > 0.5 (more confirmed alerts than false)

### Detection Latency

- Time to Detect (TTD): collection + processing + correlation time
- Time to Respond (TTR): detection + notification + human response
- Target TTD: < 1 minute for critical, < 15 minutes for high

### Machine Learning for SIEM

- Isolation Forest: anomaly detection for high-dimensional data
- LSTM: sequential pattern detection for time series
- Autoencoders: reconstruction error for unusual behavior

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
