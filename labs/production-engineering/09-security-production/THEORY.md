# THEORY: Production Security Architecture for Java Systems
## Lab 09 | Production Engineering Academy

---

## 1. Zero Trust Architecture & Defense in Depth

In modern production environments, the network perimeter is assumed to be compromised. Every internal request must be authenticated, authorized, and encrypted:

1. **Mutual TLS (mTLS)**:
   - Both client and server validate cryptographic X.509 certificates.
   - Prevents eavesdropping and man-in-the-middle attacks on East-West microservice traffic.
   - Cryptographic identity bound to SPIFFE/SPIRE or Kubernetes ServiceAccount tokens.
2. **Envelope Encryption & Key Management (KMS)**:
   - Never encrypt sensitive data directly with a master key.
   - *Master Key (KEK - Key Encryption Key)* remains protected inside HSM/KMS (AWS KMS, GCP Cloud KMS, HashiCorp Vault).
   - Generate an ephemeral *Data Encryption Key (DEK)* to encrypt the payload with AES-256-GCM.
   - Store the ciphertext alongside the encrypted DEK.
3. **Secret Zero Problem**:
   - How does a newly spawned container authenticate to Vault to fetch secrets without hardcoding a password?
   - Solution: Leverage cloud identity federation (AWS IAM Roles for Service Accounts - IRSA, GCP Workload Identity, or Kubernetes ServiceAccount token projection).

---

## 2. Insecure Java Deserialization & Gadget Chains

Native Java Serialization (`ObjectInputStream.readObject()`) reconstructs objects by dynamically invoking class constructors, readObject methods, and classloaders.
- If an application deserializes untrusted bytes, an attacker can craft a payload leveraging existing classes on the classpath (e.g. Apache Commons Collections, Spring, Groovy) known as **Gadget Chains**.
- These gadget chains invoke arbitrary methods during object graph reconstruction, leading to immediate **Remote Code Execution (RCE)** before the application even casts the object!
- Defense: Prohibit native Java serialization. Enforce `java.io.ObjectInputFilter` (JEP 290) or use strict schema-based JSON/Protobuf parsing with polymorphic deserialization disabled.

---

## 3. JWT Security & Cryptographic Pitfalls

1. **The `alg: "none"` Attack**:
   - Attackers alter the JWT header to `{"alg": "none"}`, strip the signature, and forge arbitrary admin roles. Vulnerable libraries accept unsigned tokens.
2. **Algorithm Confusion (HMAC vs RSA/ECDSA)**:
   - Public key ($K_{\text{pub}}$) of an asymmetric key pair (RS256) is public.
   - If the server accepts HS256 (symmetric HMAC) using the public key as the HMAC secret key, an attacker signs forged tokens using the publicly known RSA public key!
3. **Replay Attacks & Revocation**:
   - JWTs are stateless and cannot be revoked without a centralized distributed blocklist or token introspection.
   - Standard: Short-lived access tokens (5–15 minutes) paired with rotating refresh tokens stored securely in Redis.
