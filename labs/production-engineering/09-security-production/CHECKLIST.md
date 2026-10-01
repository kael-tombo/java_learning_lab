# CHECKLIST: Production Security & Zero Trust Architecture Readiness
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Zero Trust Network & Workload Identity Standards

- [ ] **Mutual TLS (mTLS) Mesh**:
  - [ ] All internal East-West microservice traffic encrypted via mTLS with short-lived X.509 certificates.
  - [ ] Services validate caller SPIFFE IDs against explicit Layer-7 authorization policies; anonymous calls rejected with `403 Forbidden`.
  - [ ] TLS certificate verification strictly enabled across all internal HTTP/gRPC clients; `TrustAllStrategy` and `NoopHostnameVerifier` prohibited.
- [ ] **Cloud Metadata & SSRF Hardening**:
  - [ ] AWS IMDSv2 enforced across all worker nodes (`HttpTokens=required`, `HttpPutResponseHopLimit=1`).
  - [ ] Kubernetes egress `NetworkPolicy` deployed to block access to `169.254.169.254` from application pods.

---

## 2. Cryptographic Storage & Envelope Encryption Standards

- [ ] **Envelope Encryption Architecture**:
  - [ ] Sensitive customer PII and financial records encrypted using **Envelope Encryption** before persistence.
  - [ ] Master Key (KEK) managed exclusively inside Hardware Security Modules (AWS KMS / Vault HSM).
  - [ ] Local encryption uses **AES-256-GCM** with a unique 96-bit Initialization Vector (IV) per record.
  - [ ] Plaintext Data Encryption Keys (DEKs) explicitly zeroized in memory immediately after encryption/decryption (`Arrays.fill(plaintextDek, (byte) 0)`).

---

## 3. Authentication & JWT Cryptographic Hardening

- [ ] **Strict Algorithm Pinning**:
  - [ ] JWT parsers explicitly configure `requireAlgorithm(RS256)` or `requireAlgorithm(ES256)`.
  - [ ] Tokens specifying `alg: none` or symmetric `HS256` are rejected immediately.
- [ ] **Dual-Token Lifecycle**:
  - [ ] Access tokens configured with short lifetimes ($\le 15\text{ minutes}$).
  - [ ] Refresh tokens stored as opaque strings in Redis, enabling immediate session revocation upon account compromise.
  - [ ] Clock skew tolerance capped at $\le 30\text{ seconds}$.

---

## 4. Serialization & Remote Code Execution (RCE) Defenses

- [ ] **Prohibition of Native Java Deserialization**:
  - [ ] `java.io.ObjectInputStream` strictly prohibited for network payloads and Redis session storage.
  - [ ] Production base Docker images start with the global JVM serialization filter:
    ```bash
    -Djdk.serialFilter="!*"
    ```
- [ ] **Jackson Polymorphic Deserialization Hardening**:
  - [ ] `ObjectMapper.enableDefaultTyping()` strictly banned in code reviews.
  - [ ] Polymorphic JSON payloads use explicit `@JsonTypeInfo` and `@JsonSubTypes` bound to Java 21 sealed interfaces.

---

## 5. Database & ORM Injection Defenses

- [ ] **Strict Parameterization**:
  - [ ] Zero dynamic string concatenation in SQL, JPQL, or HQL queries.
  - [ ] Dynamic sorting parameters bound strictly to internal Java `enum` whitelists rather than unvalidated user strings.
- [ ] **Dynamic Credential Leases**:
  - [ ] Static database passwords eliminated from Helm values and Kubernetes Secrets.
  - [ ] Application retrieves short-lived (1-hour) dynamic database credentials via HashiCorp Vault / IAM authentication.

---

## 6. Secret Management & PII Log Sanitization

- [ ] **Git Secret Scanners**:
  - [ ] Pre-commit hooks (`trufflehog` / `gitleaks`) active across all developer workstations to prevent committing API keys or tokens.
- [ ] **Structured Log Redaction**:
  - [ ] Logback configured with regex masking filters to sanitize credit card numbers (PAN), CVVs, and authorization bearer tokens before emission.
  - [ ] Domain DTOs explicitly exclude sensitive fields from Lombok `@ToString`.
