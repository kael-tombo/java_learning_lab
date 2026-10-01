# ARCHITECTURE DECISIONS: Enterprise Security & Zero Trust Standards
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Zero Trust Microservice Architecture & Mutual TLS (mTLS) Standard

### Status: ACCEPTED

### Context
Internal East-West microservice traffic inside our VPC was unencrypted and unauthenticated, relying on Kubernetes network boundaries for protection. A compromised container on a shared node could snoop unencrypted HTTP traffic or spoof requests to internal backend databases.

### Decision
1. **Mandatory mTLS Mesh**:
   - All inter-service network communication (HTTP, gRPC) must be encrypted and mutually authenticated using Mutual TLS (mTLS) with short-lived X.509 certificates rotated every 24 hours.
2. **Cryptographic Workload Identity (SPIFFE/SPIRE)**:
   - Every service is assigned a unique cryptographic SPIFFE ID embedded in the X.509 certificate SAN:
     ```text
     spiffe://cluster.local/ns/production/sa/<service-name>
     ```
3. **Explicit Layer-7 Authorization Policies**:
   - Every receiving service must validate the caller's SPIFFE ID against an explicit authorization matrix. Anonymous or unlisted identities are rejected with `403 Forbidden`.

### Consequences
- Eliminates Man-In-The-Middle (MITM) and network eavesdropping risks within the VPC.
- Protects services even in the event of pod or node compromise.

---

## ADR-02: Envelope Encryption & Key Management System (KMS) Policy

### Status: ACCEPTED

### Context
Sensitive customer data (Personal Identifiable Information - PII, bank account numbers) was stored in PostgreSQL using database-level column encryption with a static key loaded from application config, creating severe key-exposure risks and making periodic key rotation impossible.

### Decision
1. **Mandatory Envelope Encryption**:
   - Sensitive fields must be encrypted using **Envelope Encryption** before persistence.
   - Master Key (Key Encryption Key - KEK) resides permanently in hardware HSMs (AWS KMS / GCP Cloud KMS / HashiCorp Vault).
   - The application requests an ephemeral **Data Encryption Key (DEK)** from KMS, encrypts the payload using **AES-256-GCM**, wipes the plaintext DEK from memory, and persists the encrypted DEK alongside the ciphertext blob.
2. **Authenticated Encryption (AES-GCM)**:
   - All cryptographic operations must use **AES-256-GCM** with a unique 96-bit Initialization Vector (IV) per record to prevent replay attacks and ciphertext tampering.
3. **Automated KEK Rotation**:
   - Master KEKs are rotated automatically every 365 days in KMS without requiring re-encryption of persisted database records.

### Consequences
- Compromise of application memory or database storage does not compromise the master key.
- Guarantees compliance with PCI-DSS and GDPR cryptographic storage requirements.

---

## ADR-03: Strict Prohibition of Native Java Serialization & JEP 290 Enforcement

### Status: ACCEPTED

### Context
A legacy caching service used `java.io.ObjectInputStream` to deserialize cached session objects from Redis, creating an open Remote Code Execution (RCE) vector through deserialization gadget chains.

### Decision
1. **Total Ban on Native Java Serialization**:
   - `java.io.Serializable` is prohibited for inter-process communication, caching, and network protocols.
   - All network serialization must use typed, schema-driven protocols (JSON, Protocol Buffers, or Apache Avro).
2. **Mandatory JVM Serial Filtering (JEP 290)**:
   - All production JVM instances must configure the global serialization filter flag at startup:
     ```bash
     -Djdk.serialFilter="!*"
     ```
   - This completely blocks `ObjectInputStream.readObject()` from instantiating any class by default.
3. **Jackson Polymorphic Typing Restrictions**:
   - `ObjectMapper.enableDefaultTyping()` is strictly banned in code reviews. Polymorphic deserialization must use explicit `@JsonSubTypes` declarations on sealed classes.

### Consequences
- Completely eliminates Java deserialization gadget chain RCE vulnerabilities.
- Modernizes caching layers to use structured JSON/Protobuf formats.

---

## ADR-04: Stateless Dual-Token JWT Architecture with Algorithm Pinning

### Status: ACCEPTED

### Context
User authentication used long-lived (24-hour) JWTs signed with symmetric HMAC keys. When a user's password was changed or account compromised, the token could not be revoked until it expired 24 hours later.

### Decision
1. **Dual-Token Lifetime Hierarchy**:
   - **Access Tokens**: Short-lived (10 minutes), stateless JWTs signed via asymmetric **RS256** (RSA-2048) or **ES256** (ECDSA). Verified locally by downstream microservices using the public key.
   - **Refresh Tokens**: Long-lived (14 days), opaque random strings stored in Redis alongside user session metadata and device fingerprints.
2. **Strict Algorithm Pinning**:
   - JWT validation libraries must explicitly enforce the expected algorithm (`requireAlgorithm(RS256)`), eliminating `alg: none` and RSA-to-HMAC algorithm confusion attacks.
3. **Immediate Revocation**:
   - Account security events (password reset, suspicious login) immediately delete the refresh token from Redis. The user is locked out within a maximum of 10 minutes (when the access token expires).

### Consequences
- Eliminates the security risk of stolen long-lived JWTs.
- Enables local, fast public-key token verification without central auth server round-trips for routine API requests.

---

## ADR-05: Ephemeral Dynamic Secrets & Workload Identity Federation

### Status: ACCEPTED

### Context
Database passwords and cloud credentials were hardcoded in Helm values or stored in static Kubernetes Secrets, leaving permanent secrets accessible to cluster administrators and vulnerable to leakages.

### Decision
1. **Workload Identity Federation**:
   - Static cloud API keys are strictly banned. Pods authenticate to cloud resources using **AWS IAM Roles for Service Accounts (IRSA)** or **GCP Workload Identity** via projected OIDC ServiceAccount tokens.
2. **Dynamic Database Credential Generation**:
   - Applications authenticate to HashiCorp Vault using their projected Kubernetes ServiceAccount token.
   - Vault generates dynamic, ephemeral database credentials valid for **1 hour**:
     ```text
     username: v-k8s-app-3f920
     password: <temporary_hash>
     ```
   - The application automatically leases and rotates credentials dynamically without service restarts.

### Consequences
- Zero permanent database credentials exist to be leaked or stolen.
- Provides complete forensic audit trails of which container instance executed specific database queries.
