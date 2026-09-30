# EXERCISES: Production Security & Cryptography
## Lab 09 | Production Engineering Academy

---

## Exercise 1: Implement Production AES-256-GCM Envelope Encryption

### Objective
Build a cryptographic utility class that encrypts and decrypts sensitive customer PII using AES-256-GCM with unique cryptographic nonces and HMAC authentication tags.

### Tasks
1. Implement the `ProductionEnvelopeEncryptor` class from `CODE_DEEP_DIVE.md`.
2. Generate a 256-bit AES key using `KeyGenerator.getInstance("AES")`.
3. Encrypt 1,000 credit card numbers.
4. Verify that encrypting the identical credit card number twice produces two completely different ciphertexts (proving unique IV generation).
5. Tamper with a single byte of ciphertext and attempt decryption: verify that `AEADBadTagException` is thrown, proving authentication integrity.

---

## Exercise 2: Secure an Outbound HTTP Client Against SSRF

### Objective
Create a custom Java HTTP client interceptor that prevents Server-Side Request Forgery against cloud metadata and private network addresses.

### Tasks
1. Implement `SsrfSafetyValidator`.
2. Write unit tests attempting to connect to:
   - `http://169.254.169.254/latest/meta-data/` (AWS IMDS)
   - `http://127.0.0.1:8080/admin` (Loopback)
   - `http://10.0.1.50:5432/` (Internal VPC DB)
   - `http://localhost/`
   - `https://api.github.com/` (Valid public endpoint)
3. Ensure the validator throws `SecurityException` for all internal addresses while allowing public endpoints.
