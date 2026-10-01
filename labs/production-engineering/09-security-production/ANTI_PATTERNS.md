# ANTI-PATTERNS: Enterprise Java Security & Cryptographic Pitfalls
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Native Java Deserialization on Untrusted Input Streams

### The Mistake
```java
@PostMapping("/data")
public void handleIncomingPayload(HttpServletRequest request) throws Exception {
    // Reading untrusted network bytes directly into ObjectInputStream:
    try (ObjectInputStream ois = new ObjectInputStream(request.getInputStream())) {
        UserSession session = (UserSession) ois.readObject(); // FATAL VULNERABILITY!
        processSession(session);
    }
}
```

### Why It Fails (The Gadget Chain RCE)
- `ObjectInputStream.readObject()` reconstructs dynamic object graphs by invoking classloaders and constructors embedded in the serialized byte stream.
- An attacker uses automated tools (like `ysoserial`) to craft a serialized payload utilizing common utility libraries residing on the classpath (e.g. Apache Commons Collections, Spring Core, Groovy, AspectJ).
- These classes form a **Gadget Chain** that culminates in `Runtime.getRuntime().exec()` or reflective bytecode execution.
- **The Execution Occurs INSIDE `readObject()`**: The malicious shell command executes before the application even attempts to cast the object to `UserSession`!
- The attacker achieves immediate, unauthenticated **Remote Code Execution (RCE)** with the privileges of the JVM container process.

### The Correct Production Fix
1. **Ban Native Java Serialization Completely**: Use schema-driven, typed serialization formats (JSON, Protocol Buffers, or Apache Avro).
2. If legacy formats must be read, enforce strict **JEP 290 JVM Serial Filtering**:
   ```bash
   -Djdk.serialFilter="com.learning.production.safe.*;!*"
   ```
   Or configure programmatic filtering rejecting any class not explicitly in the safe package.

---

## Anti-Pattern 2: JWT Algorithm Confusion & Loose Verification

### The Mistake
```java
// Vulnerable JWT Verification:
public Claims parseToken(String token, PublicKey rsaPublicKey) {
    // BUG: Allows the token header to dictate the verification algorithm!
    return Jwts.parser()
        .setSigningKey(rsaPublicKey)
        .parseClaimsJws(token)
        .getBody();
}
```

### Why It Fails (The RSA-to-HMAC Key Confusion Exploit)
1. The service signs legitimate tokens using asymmetric **RS256** (RSA private key signs; public key verifies).
2. The RSA public key is distributed publicly or exposed via a JWKS endpoint (`/.well-known/jwks.json`).
3. An attacker crafts a forged administrative JWT (`"sub": "admin", "role": "SUPERUSER"`).
4. The attacker sets the JWT header to **`{"alg": "HS256"}`** (symmetric HMAC-SHA256).
5. The attacker computes the HMAC signature using the **server's public RSA key as the symmetric secret key**!
6. When the vulnerable library parses the token:
   - It reads `alg: HS256` from the header.
   - It takes the configured `rsaPublicKey` and treats its raw bytes as a symmetric HMAC secret.
   - The HMAC signature matches!
7. The forged admin token is accepted as valid, granting the attacker full administrative access!

### The Correct Production Fix
Enforce **Strict Algorithm Pinning**:
```java
public Claims parseToken(String token, PublicKey rsaPublicKey) {
    return Jwts.parser()
        .requireAlgorithm(SignatureAlgorithm.RS256) // HARD-CODED: Strictly reject any token that is not RS256!
        .setSigningKey(rsaPublicKey)
        .build()
        .parseSignedClaims(token)
        .getPayload();
}
```

---

## Anti-Pattern 3: Hardcoded Secrets & Long-Lived Static Database Credentials

### The Mistake
```yaml
# In application.yml or Dockerfile:
spring:
  datasource:
    url: jdbc:postgresql://db.corp.internal:5432/payments
    username: app_prod_user
    password: SuperSecretProductionPassword2026!  # Hardcoded static secret!
```

### Why It Fails
1. **Git Secret Leaks**: The static credential is committed to version control, mirrored across developer workstations, and backed up in third-party Git hosts.
2. **Blast Radius of Exfiltration**: If an attacker or disgruntled employee acquires the password, they possess perpetual read/write access to the production database from any compromised container.
3. **Impossibility of Rotation**: Rotating a hardcoded static password requires updating configuration files, rebuilding container images, and restarting hundreds of microservice pods simultaneously, causing customer downtime.

### The Correct Production Fix
Implement **Ephemeral Dynamic Credentials via Vault or Cloud IAM**:
- Microservices use **Kubernetes Workload Identity / AWS IRSA** to authenticate to Vault without passwords.
- Vault generates temporary, unique database credentials valid for **1 hour**:
  ```text
  username: v-token-app-4f2a9
  password: <ephemeral_hash>
  ttl: 3600s
  ```
- The application automatically renews the lease via Spring Cloud Vault; credentials rotate continuously without downtime.

---

## Anti-Pattern 4: Hibernate / JPA Dynamic Query String Concatenation

### The Mistake
```java
// Concatenating untrusted input into JPQL:
public List<Account> searchAccounts(String ownerName, String sortColumn) {
    String jpql = "SELECT a FROM Account a WHERE a.owner = '" + ownerName + "' ORDER BY " + sortColumn;
    return entityManager.createQuery(jpql, Account.class).getResultList();
}
```

### Why It Fails
- Developers assume that because JPQL is an object-oriented query language, it is immune to SQL injection.
- Passing `ownerName = "John' OR '1'='1"` transforms the query into returning all accounts in the database.
- Furthermore, because `ORDER BY` clauses cannot be bound via positional JDBC parameters, an attacker injects subqueries into `sortColumn`:
  ```text
  sortColumn = "(CASE WHEN (SELECT ascii(substr(password,1,1)) FROM admin_users) > 100 THEN a.id ELSE a.balance END)"
  ```
  The attacker extracts database secrets character-by-character through blind boolean inference!

### The Correct Production Fix
Use **CriteriaBuilder** or strictly parameterized queries with an allowed whitelist for sorting:
```java
public List<Account> searchAccounts(String ownerName, AccountSortField sortField) {
    String jpql = "SELECT a FROM Account a WHERE a.owner = :owner ORDER BY a." + sortField.getColumnName();
    return entityManager.createQuery(jpql, Account.class)
        .setParameter("owner", ownerName)
        .getResultList();
}
```

---

## Anti-Pattern 5: Disabling TLS Certificate Verification in Internal Clients

### The Mistake
Disabling TLS certificate or hostname validation in internal HTTP or gRPC clients to "bypass self-signed certificate errors" in staging or production:
```java
// DANGEROUS SECURITY HOLE:
TrustManager[] trustAllCerts = new TrustManager[]{
    new X509TrustManager() {
        public void checkClientTrusted(X509Certificate[] certs, String authType) {}
        public void checkServerTrusted(X509Certificate[] certs, String authType) {}
        public X509Certificate[] getAcceptedIssuers() { return null; }
    }
};
SSLContext sc = SSLContext.getInstance("TLS");
sc.init(null, trustAllCerts, new SecureRandom());
HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
HttpsURLConnection.setDefaultHostnameVerifier((hostname, session) -> true); // Disables hostname checks!
```

### Why It Fails
- Trusting all certificates strips TLS down to an unauthenticated tunnel.
- Any compromised container, malicious node, or ARP spoofing inside the VPC can perform a **Man-In-The-Middle (MITM) attack**.
- The attacker intercepts, inspects, and modifies API traffic, session tokens, and passwords in plaintext without generating a single TLS handshake error!

### The Correct Production Fix
Always establish a private **Internal Certificate Authority (CA)** (e.g. via HashiCorp Vault, cert-manager, or AWS Private CA):
- Distribute the internal root CA bundle into the Java truststore (`cacerts`) of base container images:
  ```bash
  keytool -importcert -trustcacerts -file /certs/internal-ca.crt -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt
  ```
- Clients validate internal certificates normally with strict hostname verification.

---

## Anti-Pattern 6: Unrestricted Jackson Polymorphic Deserialization

### The Mistake
Enabling default polymorphic typing in Jackson to deserialize generic interface fields:
```java
ObjectMapper mapper = new ObjectMapper();
// CATASTROPHIC SECURITY FLAW:
mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
```

### Why It Fails
`enableDefaultTyping` instructs Jackson to deserialize JSON objects using the class name specified inside the JSON payload:
```json
{
  "item": ["com.sun.org.apache.bcel.internal.util.ClassLoader", "attack_payload"]
}
```
Attackers pass arbitrary Java class names present on the classpath. Jackson instantiates the specified class via reflection and populates its fields, allowing the attacker to trigger known **Jackson deserialization gadget chains** that execute arbitrary OS commands!

### The Correct Production Fix
1. Never use `enableDefaultTyping()`.
2. Use strict, bounded polymorphic deserialization with explicit permitted subtypes via **`@JsonSubTypes`**:
   ```java
   @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "type")
   @JsonSubTypes({
       @JsonSubTypes.Type(value = CreditCardPayment.class, name = "CREDIT_CARD"),
       @JsonSubTypes.Type(value = BankTransferPayment.class, name = "BANK_TRANSFER")
   })
   public sealed interface PaymentDetails permits CreditCardPayment, BankTransferPayment {}
   ```
Jackson will strictly reject any type not explicitly declared in `@JsonSubTypes`.
