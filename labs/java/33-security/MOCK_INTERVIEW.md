# Mock Interview Transcript: Security

## Interviewer: Staff Engineer, Meta
## Candidate: Senior Java developer
## Time: 40 minutes
## Focus: Cryptographic APIs, secure coding, deserialization, authentication

---

**Q1: What security vulnerabilities are unique to Java?**

**Candidate**: (1) Deserialization attacks — Java serialization can be exploited via gadget chains (like the infamous Apache Commons Collection exploit). (2) Reflection-based access bypass. (3) JNDI injection (Log4Shell — CVE-2021-44228). (4) Thread safety issues leading to data corruption. (5) Insecure random number generation (using `Random` instead of `SecureRandom`).

**Interviewer**: How does the JVM's Security Manager work? What about its deprecation?

**Candidate**: `SecurityManager` (Java 1.0) uses a sandbox model — code is granted permissions based on where it's loaded from. It was deprecated for removal in Java 17 (JEP 411), disabled by default in 18, and permanently disabled in Java 24 (JEP 486). Reasons: (1) It gives a false sense of security — many escapes known. (2) Rarely used correctly. (3) Container-level security (Docker, cgroups) provides better isolation. (4) Project Loom virtual threads don't support it.

**Interviewer**: How would you securely hash a password in Java?

**Candidate**: 
```java
byte[] hashPassword(char[] password, byte[] salt) {
    var factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
    var spec = new PBEKeySpec(password, salt, 100000, 256);
    return factory.generateSecret(spec).getEncoded();
}
```
Never use SHA-256 directly for passwords — it's too fast. PBKDF2 with 100K+ iterations, bcrypt, or scrypt are appropriate. Argon2 is the current best practice. Use `char[]` instead of `String` for passwords so you can clear it after use.

**Interviewer**: How does `SecureRandom` differ from `Random`?

**Candidate**: `Random` uses a LCG (Linear Congruential Generator) — fast but predictable. If you know two consecutive outputs, you can predict all future values. `SecureRandom` uses system entropy sources (like `/dev/random` on Linux) — cryptographically strong but slower. Use `SecureRandom` for security-sensitive contexts (tokens, session IDs, keys, passwords).

**Interviewer**: Explain deserialization attacks and how to defend against them.

**Candidate**: Java deserialization reconstructs objects from byte streams. Attackers craft payloads that, when deserialized, trigger chains of method calls (gadgets) that execute arbitrary code. Defenses: (1) Never deserialize untrusted data. (2) Use `ObjectInputFilter` to blacklist/whitelist classes. (3) Use JSON/protobuf instead of Java serialization for external data. (4) Validate objects after deserialization.

**Interviewer**: How do you implement a safe deserialization filter?

**Candidate**: 
```java
// JVM-wide filter
ObjectInputFilter.Config.setSerialFilter(
    ObjectInputFilter.Config.createFilter(
        "com.example.whitelist.*;java.base.*;!*"
    )
);
// Per-stream filter
ObjectInputStream ois = new ObjectInputStream(input);
ois.setObjectInputFilter(filterInfo -> {
    if (filterInfo.serialClass() == null) return ObjectInputFilter.Status.UNDECIDED;
    if (filterInfo.serialClass().getName().startsWith("java.lang."))
        return ObjectInputFilter.Status.ALLOWED;
    return ObjectInputFilter.Status.REJECTED;
});
```

**Interviewer**: Write secure code for a JWT token validation.

**Candidate**: 
```java
SecretKey key = getSigningKey();  // From secure store, not hardcoded

boolean validateToken(String token) {
    try {
        var parser = Jwts.parser()
            .verifyWith(key)
            .requireIssuer("my-app")
            .requireExpiration(new Date())
            .build();
        Jws<Claims> jws = parser.parseSignedClaims(token);
        return true;
    } catch (JwtException e) {
        return false;  // Invalid signature, expired, etc.
    }
}
```

**Interviewer**: What are common Java crypto mistakes?

**Candidate**: (1) ECB mode — leaks patterns (same plaintext = same ciphertext). (2) Static IV/nonce. (3) Hard-coded keys in source code. (4) Using `String` for sensitive data (String is immutable, can't be cleared from memory). (5) PBE without salt. (6) Weak algorithms: DES, MD5, SHA-1, RC4. (7) Not authenticating ciphertext (need GCM mode, not CBC). (8) Exposing stack traces with sensitive information.

**Interviewer**: Final: How does the Java security library handle certificate validation?

**Candidate**: Java's `TrustManager` validates X.509 certificates against a truststore (cacerts file, default location `$JAVA_HOME/lib/security/cacerts`). The truststore contains root CA certificates. `HostnameVerifier` validates that the certificate's CN/SAN matches the hostname. Custom `TrustManager` should chain to the default for proper validation. Never trust all certificates (`return true` in checkServerTrusted).

---

## Feedback

**Strengths**:
- Comprehensive Java-specific vulnerability knowledge
- Correct password hashing with PBKDF2
- Understands deserialization attack vectors and filters
- Secure JWT and crypto practices

**Areas for Improvement**:
- Could mention JCE unlimited strength policy (needed for AES-256 in older Java)
- Discuss `KeyStore` types (PKCS12 vs JKS)

**Score**: 4.5/5 — Strong security awareness
