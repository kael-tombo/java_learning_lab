# INTERVIEW QUESTIONS: Production Security, Cryptography & Zero Trust
## Lab 09 | Senior / Staff / Principal / Distinguished Level

---

## Senior Level (5–7 Years)

### Q1: How does a native Java deserialization gadget chain achieve Remote Code Execution (RCE) without calling any application business logic?

**Answer:**
Native Java deserialization via `ObjectInputStream.readObject()` does not merely read data fields; it **dynamically reconstructs active object graphs by executing bytecode embedded in class definitions**:

1. **The Inherent Vulnerability**: When `readObject()` parses a serialized stream, it looks up class definitions on the application's classpath and invokes class-specific callback methods (e.g. `readObject()`, `readResolve()`, `hashCode()`, or `equals()`).
2. **Gadget Chains**: An attacker does not inject new classes into the JVM; they leverage classes that **already exist on the application's classpath** (e.g., Apache Commons Collections, Spring Core, Groovy, or Jackson).
3. **The Execution Flow**:
   - The attacker nests objects so that `readObject()` triggers `Map.get()`.
   - `LazyMap.get()` invokes a `Transformer`.
   - `ChainedTransformer` invokes `InvokerTransformer`.
   - `InvokerTransformer` uses Java reflection to invoke `Runtime.getRuntime().exec("malicious_shell_command")`.
4. **Execution Precedes Casting**: The arbitrary shell execution takes place **inside the call to `ois.readObject()`**. Even if the very next line of application code is `UserSession s = (UserSession) ois.readObject()`, the code never reaches the type-cast because the exploit has already compromised the host process!

**Defenses**:
- Eliminate `java.io.Serializable` for network payloads in favor of typed JSON or Protobuf.
- Enforce strict JVM serial filtering via **JEP 290** (`-Djdk.serialFilter="!*"`).

---

### Q2: Explain the JWT Algorithm Confusion attack (RS256 vs. HS256). How can an attacker forge an administrative token using the server's public RSA key?

**Answer:**

**The Asymmetric Baseline (RS256)**:
- In RS256, the Authorization Server signs tokens with a private RSA key ($K_{\text{priv}}$).
- Microservices verify tokens with the public RSA key ($K_{\text{pub}}$). The public key is not secret; it is widely distributed.

**The Exploit**:
1. An attacker obtains the server's public RSA key ($K_{\text{pub}}$) in PEM format.
2. The attacker crafts a forged JWT payload:
   ```json
   {"sub": "attacker", "roles": ["ADMIN", "SUPERUSER"], "exp": 1928400000}
   ```
3. The attacker sets the JWT header to specify **`{"alg": "HS256"}`** (symmetric HMAC-SHA256).
4. The attacker computes the HMAC signature using the **server's public RSA key as the symmetric secret key**:
   $$\text{Signature} = \text{HMAC-SHA256}(\text{Header} + "." + \text{Payload}, K_{\text{pub\_bytes}})$$
5. **The Verification Vulnerability**:
   When the receiving microservice verifies the token using a naive JWT library:
   - The library reads `alg: HS256` from the header.
   - It retrieves the configured verification key (the public key $K_{\text{pub}}$).
   - Because HS256 is symmetric, the library treats $K_{\text{pub}}$ as an HMAC secret!
   - It re-computes the HMAC using $K_{\text{pub}}$ and compares it to the incoming signature.
   - **The signatures match!** The forged admin token is accepted as authentic.

**The Defensive Invariant**:
Always enforce **Strict Algorithm Pinning** in the verification parser (`requireAlgorithm(SignatureAlgorithm.RS256)`). The parser must strictly reject any token that specifies symmetric algorithms when an asymmetric key is configured.

---

## Staff Level (8–12 Years)

### Q3: Explain the cryptographic mechanics and operational invariants of Envelope Encryption. Why must the plaintext Data Encryption Key (DEK) be explicitly zeroized in memory?

**Answer:**

**1. The Two-Key Hierarchy**:
- **Key Encryption Key (KEK / Master Key)**: Resides permanently inside a cloud Hardware Security Module (AWS KMS / GCP Cloud KMS / Vault HSM). The KEK is never exported and cannot be extracted into application memory.
- **Data Encryption Key (DEK)**: An ephemeral 256-bit AES symmetric key generated dynamically per record or session.

**2. The Encryption Protocol**:
1. Application calls KMS: `GenerateDataKey(KeyId=KEK, Spec=AES_256)`.
2. KMS generates the DEK inside its HSM and returns two artifacts:
   - `Plaintext DEK` (32 bytes)
   - `Encrypted DEK` (Ciphertext encrypted with the KEK inside the HSM)
3. The application initializes local AES-256-GCM using the `Plaintext DEK` and encrypts the sensitive payload.
4. **Mandatory Memory Zeroization**:
   The application immediately overwrites the byte array containing the plaintext DEK with zeroes (`Arrays.fill(plaintextDek, (byte) 0)`).
   - *Why?* If the JVM generates a heap dump, crashes, or is inspected by an attacker via `/proc/$PID/mem`, lingering plaintext keys in garbage-collected memory can be recovered. Zeroizing removes the key material from physical DRAM immediately.
5. The application stores the persisted payload containing:
   $$\text{Stored Blob} = [\text{IV (12B)}] + [\text{Encrypted DEK}] + [\text{Ciphertext}] + [\text{GCM Tag}]$$

**3. Operational Invariant**:
When rotating the Master KEK, persisted database records do not need to be decrypted and re-encrypted. KMS simply re-encrypts the small Encrypted DEK headers without touching petabytes of ciphertext.

---

### Q4: How does SPIFFE/SPIRE Mutual TLS (mTLS) work in a Kubernetes service mesh, and how does it solve the "Secret Zero" authentication problem?

**Answer:**

**The "Secret Zero" Problem**:
To authenticate securely to a vault or database, an application needs a credential. But how does the container securely receive that initial credential without hardcoding a secret in the Docker image or environment variables?

**The SPIFFE/SPIRE Architecture**:
1. **Cryptographic Workload Attestation**:
   When a Java pod boots, the local node agent (SPIRE Agent) inspects the Linux kernel state of the new process:
   - Queries Linux cgroups, namespace PID, and Kubelet API to verify the pod's exact `namespace`, `ServiceAccount`, and container image hash.
2. **X.509 SVID Issuance**:
   Once attested, the SPIRE Server issues an ephemeral, short-lived X.509 certificate containing a **SPIFFE ID** in the SAN:
   ```text
   spiffe://prod.corp/ns/payments/sa/payment-service
   ```
   This certificate is projected into the pod via an in-memory secret volume, with a lifetime of **1 hour**, rotated automatically every 30 minutes.
3. **Mutual TLS (mTLS) Handshake**:
   When `payment-service` calls `ledger-service`:
   - Both services perform a full TLS handshake using their SPIFFE X.509 certificates.
   - Traffic over the VPC is encrypted with AES-256-GCM.
   - `ledger-service` inspects the client's certificate: *Is the caller `spiffe://.../sa/payment-service`?*
   - Authorization is enforced at the cryptographic layer without any static passwords or API keys!

---

### Q5: Can SQL injection occur in Hibernate or Spring Data JPA? Give concrete examples of vulnerable JPQL and `ORDER BY` clauses, and demonstrate their architectural mitigations.

**Answer:**
**Yes. Using an ORM does NOT protect against SQL injection if strings are concatenated!**

**Vulnerability 1: JPQL / HQL Concatenation**:
```java
// VULNERABLE:
String jpql = "SELECT u FROM User u WHERE u.email = '" + userEmail + "'";
return entityManager.createQuery(jpql, User.class).getResultList();
```
Passing `userEmail = "admin@corp.com' OR '1'='1"` returns all users in the database.

**Vulnerability 2: Dynamic `ORDER BY` Injection**:
Developers frequently parameterize the `WHERE` clause but dynamically concatenate sorting parameters:
```java
// VULNERABLE: Positional parameter (?1) cannot parameterize ORDER BY clauses!
@Query(value = "SELECT * FROM orders WHERE status = ?1 ORDER BY " + sortColumn, nativeQuery = true)
List<Order> findOrders(String status, String sortColumn);
```
Because SQL grammar does not permit column names or sorting directions to be parameterized via JDBC prepared statements, passing:
```text
sortColumn = "(CASE WHEN (SELECT 1 FROM users WHERE username='admin' AND substring(password,1,1)='a') THEN id ELSE created_at END)"
```
allows an attacker to execute **Blind Boolean SQL Injection**, extracting arbitrary database hashes character-by-character!

**Architectural Mitigations**:
1. **Mandatory Named Parameters**: Always use `:param` binding in queries.
2. **Strict Enum Sorting Whitelist**: Never pass raw HTTP sort strings into queries. Bind incoming sort requests to an internal Java `enum`:
   ```java
   public enum OrderSort {
       DATE("created_at"), AMOUNT("total_amount");
       // Whitelist guarantees only known, safe column identifiers can be injected!
   }
   ```
3. Use the **JPA CriteriaBuilder API** for dynamic query generation.

---

## Principal / Distinguished Level (12+ Years)

### Q6: Design an end-to-end zero-trust financial settlement platform where microservices communicate over untrusted networks, database columns are encrypted at rest, and all credentials rotate automatically with zero downtime.

**Answer — Architecture Blueprint**:

```
                       [Incoming Ingress: mTLS + JWT]
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│ Service A: Payment Gateway      │             │ Service B: Ledger Settlement    │
├─────────────────────────────────┤             ├─────────────────────────────────┤
│ • Projected SPIFFE X.509 Cert   │             │ • Projected SPIFFE X.509 Cert   │
│ • Validates RS256 JWT           │ ── mTLS ──► │ • Validates SPIFFE ID of A      │
│ • Zero static secrets in image  │   (Wire)    │ • Performs Envelope Encryption  │
└────────────────┬────────────────┘             └────────────────┬────────────────┘
                 │                                               │
                 │ Workload Identity Token                       │ Ephemeral DEK Request
                 ▼                                               ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│ HashiCorp Vault / Cloud IAM     │             │ AWS KMS / Hardware HSM          │
├─────────────────────────────────┤             ├─────────────────────────────────┤
│ • Generates 1-hour ephemeral    │             │ • Master KEK never leaves HSM   │
│   dynamic PostgreSQL creds      │             │ • Rotates automatically 365d    │
└────────────────┬────────────────┘             └────────────────┬────────────────┘
                 │ Dynamic Connection Lease                      │
                 ▼                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ High-Availability PostgreSQL Database Cluster                                   │
│ • Stored Columns: Encrypted via AES-256-GCM with Envelope Headers               │
│ • DB Users: Ephemeral Vault Users (`v-k8s-app-4f2a9`) auto-evicted after 1 hour│
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Security Guarantees**:
1. **Network Layer**: All East-West traffic enforced via SPIFFE mTLS with strict cryptographic SAN identity verification.
2. **Storage Layer**: Sensitive financial PII is encrypted with AES-256-GCM envelope encryption. Database dumps are useless to an attacker without HSM access.
3. **Identity Layer**: Zero static database credentials exist anywhere in Git, Helm, or Kubernetes Secrets. Vault generates temporary dynamic database users rotated every 60 minutes.
4. **Token Security**: Stateless RS256 JWTs with strict algorithm pinning, 10-minute access lifetimes, and Redis-backed refresh token revocation lists.

---

### Q7: How do you architect a Java Runtime Application Self-Protection (RASP) and eBPF kernel defense system capable of detecting and neutralizing zero-day memory corruption, supply-chain bytecode injection (Log4Shell-style), and SSRF attacks in real time?

**Answer — Multi-Layered RASP & eBPF Defense**:

**Layer 1: eBPF Linux Kernel Probe Defense (Tetragon / Cilium)**:
- eBPF programs hook directly into Linux kernel system call entrypoints (`sys_execve`, `sys_connect`, `sys_openat`).
- **Zero-Day RCE Block**: If a Java container (PID 1 = `java`) attempts to execute `execve("/bin/sh")` or `/bin/bash` (the standard payload of Log4Shell and deserialization gadget chains), eBPF intercepts the syscall in kernel space and **kills the process immediately with `SIGKILL` before the shell spawns**.
- **SSRF Block**: eBPF monitors outbound socket connects. Any Java process attempting to connect to the AWS metadata IP (`169.254.169.254`) or internal non-routable subnets from an unauthorized namespace is dropped at the Linux socket layer.

**Layer 2: In-JVM Bytecode Instrumentation (RASP Agent)**:
- A Java Bytecode Agent (`-javaagent:rasp-agent.jar`) uses ASM / ByteBuddy to dynamically intercept security-sensitive JDK methods:
  - Hooks `java.lang.ProcessBuilder.start()`: Blocks arbitrary sub-process spawning.
  - Hooks `java.net.Socket.connect()`: Enforces outbound URL domain whitelists to block SSRF and JNDI LDAP lookup callbacks.
  - Hooks JNDI `InitialContext.lookup()`: Strips LDAP and RMI protocols entirely to neutralize Log4j2-style remote classloading.
  - Hooks `ObjectInputStream.resolveClass()`: Validates classes against JEP 290 whitelist filters.

**Outcome**:
Even if an application imports an unpatched zero-day vulnerable third-party library, the attack payload is blocked at both the JVM bytecode boundary and the Linux kernel eBPF boundary.
