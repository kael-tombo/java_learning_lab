# EXERCISES: Production Security, Cryptography & Zero Trust
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Exploiting and Neutralizing Native Java Deserialization via JEP 290

### 1. Objective
Simulate a native Java deserialization gadget attack in a controlled test environment, observe arbitrary code execution, and neutralize the attack using JEP 290 JVM serialization filtering.

### 2. Implementation Tasks
1. Build a simple Java application that deserializes incoming bytes using `ObjectInputStream.readObject()`.
2. Generate a simulated gadget payload using a dummy class hierarchy that executes a marker command (e.g. creating a file `/tmp/pwned.txt`) inside its custom `readObject()` method:
   ```java
   public class VulnerableReceiver {
       public static void main(String[] args) throws Exception {
           byte[] attackPayload = createExploitPayload();
           try (ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(attackPayload))) {
               ois.readObject(); // Triggers exploit!
           }
       }
   }
   ```
3. Run the application: verify `/tmp/pwned.txt` was created, proving arbitrary execution occurred before any application logic executed!
4. Remove `/tmp/pwned.txt`. Re-run the application with JEP 290 filtering:
   ```bash
   java -Djdk.serialFilter="com.learning.production.safe.*;!*" VulnerableReceiver
   ```
5. Observe the result:
   - The JVM throws `java.io.InvalidClassException: filter status: REJECTED`.
   - Verify `/tmp/pwned.txt` was **not** created, proving the gadget chain was neutralized before instantiation!

---

## Exercise 2: Simulating and Mitigating the JWT Algorithm Confusion Attack

### 1. Objective
Execute an RSA-to-HMAC algorithm confusion attack by crafting a forged administrative token signed with a public RSA key, verify that a naive parser accepts it, and eliminate the vulnerability using strict algorithm pinning.

### 2. Implementation Tasks
1. Generate an RSA-2048 keypair (`KeyPairGenerator.getInstance("RSA")`).
2. Export the public key in X.509 format.
3. Build a forged token:
   - Header: `{"alg":"HS256","typ":"JWT"}`
   - Claims: `{"sub":"attacker","role":"ADMIN"}`
   - Sign using HMAC-SHA256 with the **raw bytes of the RSA public key** as the secret.
4. Test against a naive parser:
   ```java
   // VULNERABLE:
   Jwts.parser().setSigningKey(publicKey).parseClaimsJws(forgedToken);
   ```
   - Verify that the naive parser accepts the forged token!
5. Refactor using strict algorithm pinning:
   ```java
   Jwts.parser()
       .requireAlgorithm(SignatureAlgorithm.RS256) // PIN ALGORITHM
       .setSigningKey(publicKey)
       .build()
       .parseSignedClaims(forgedToken);
   ```
6. Re-run: verify the parser throws an immediate `UnsupportedJwtException` or `SignatureException`, rejecting the forged token with HTTP 401.

---

## Exercise 3: Implementing AES-256-GCM Envelope Encryption with Key Zeroization

### 1. Objective
Implement a local mock of the Envelope Encryption Service from Pattern 1 of CODE DEEP DIVE, encrypt a 10MB sensitive dataset, verify ciphertext integrity, and prove that plaintext keys are zeroized in physical memory.

### 2. Implementation Tasks
1. Implement `EnvelopeEncryptionService`:
   - Simulates KMS `GenerateDataKey` returning an encrypted DEK and plaintext DEK.
   - Encrypts payload with `AES/GCM/NoPadding` using a random 96-bit IV.
2. In a unit test, encrypt a sample financial record:
   ```java
   byte[] plaintext = "CARD_NUMBER: 4111-2222-3333-4444".getBytes(StandardCharsets.UTF_8);
   byte[] encryptedBlob = service.encrypt(plaintext);
   ```
3. Verify that the encrypted blob does NOT contain the plaintext string in any substring:
   ```java
   assertFalse(new String(encryptedBlob).contains("4111"));
   ```
4. Verify key zeroization: verify that after `encrypt()` completes, the internal buffer holding the plaintext DEK has all bytes set to `(byte) 0`.
5. Decrypt the blob and verify that the original plaintext is restored with 100% fidelity.
6. Tamper with 1 byte of the ciphertext: verify that `AES/GCM` throws an `AEADBadTagException`, detecting the tampering attempt immediately!

---

## Exercise 4: Exploiting Blind SQL Injection in an ORM Query and Securing via CriteriaBuilder

### 1. Objective
Demonstrate how string concatenation in a dynamic JPA `ORDER BY` clause allows blind SQL injection even when using prepared statements for the `WHERE` clause, and rewrite the query using safe CriteriaBuilder with enum whitelisting.

### 2. Implementation Tasks
1. Start an in-memory H2 or PostgreSQL database with table `accounts(id INT, owner VARCHAR, balance DECIMAL)`.
2. Write a vulnerable repository method:
   ```java
   public List<Account> search(String owner, String sortColumn) {
       String sql = "SELECT * FROM accounts WHERE owner = ?1 ORDER BY " + sortColumn;
       return em.createNativeQuery(sql, Account.class).setParameter(1, owner).getResultList();
   }
   ```
3. Craft an exploit payload in `sortColumn`:
   ```sql
   sortColumn = "(CASE WHEN (SELECT count(*) FROM accounts WHERE balance > 10000) > 0 THEN id ELSE balance END)"
   ```
   - Prove that the database evaluates the subquery successfully, allowing blind data extraction.
4. Refactor the repository using `SecureAccountRepository` with `CriteriaBuilder` and a strict Java `AccountSortField` enum.
5. Re-run the attack string: verify that the application throws an `IllegalArgumentException: Disallowed sort column` at the boundary without touching the database!
