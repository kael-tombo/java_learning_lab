# ANTI-PATTERNS: Security in Production Java
## Lab 09 | Production Engineering Academy

---

## Anti-Pattern 1: Baking Secrets into Container Images or Git Repositories

### The Mistake
Committing `application.yml` containing hardcoded database passwords, API keys, or private certificates, or embedding secrets into Dockerfile `ENV` directives.

### Why It Fails
1. Git history preserves secrets forever, even after subsequent deletion commits.
2. Container image layers are cached on public/private registries, allowing anyone with pull access to inspect `docker history --no-trunc` and extract credentials.

### The Correct Production Fix
Use Kubernetes External Secrets Operator or HashiCorp Vault Agent sidecar to inject secrets into ephemeral memory-backed volumes (`tmpfs`) or environment variables at container launch.

---

## Anti-Pattern 2: ECB Mode or Hardcoded Static Nonce in AES Encryption

### The Mistake
Using `AES/ECB/PKCS5Padding` or using a static IV in `AES/GCM/NoPadding`:
```java
// FATAL CRYPTOGRAPHIC FLAW: Static IV in GCM mode
byte[] staticIv = new byte[12]; // All zeroes
```

### Why It Fails
- AES-ECB mode encrypts identical plaintext blocks into identical ciphertext blocks (the infamous "Electronic Codebook Tux Penguin" leak), exposing patterns in structured data.
- In AES-GCM, reusing the same Initialization Vector (IV) with the same secret key completely destroys authentication security: an attacker can recover the authentication subkey and forge valid ciphertexts!

### The Correct Production Fix
Always use `AES/GCM/NoPadding` with a cryptographically secure random 96-bit IV generated freshly via `SecureRandom` for **every single encryption operation**.
