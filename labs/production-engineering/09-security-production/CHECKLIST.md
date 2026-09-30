# CHECKLIST: Production Security Readiness
## Lab 09 | Production Engineering Academy

---

## 1. Secrets & Credentials Hygiene
- [ ] Zero static credentials in Git repositories or Docker images (enforced via Git pre-commit hooks and TruffleHog / GitGuardian CI scans).
- [ ] Database credentials dynamically leased or rotated automatically.
- [ ] Vault / KMS auth tokens use short-lived projection tokens.
- [ ] Actuator `/actuator/env` and `/actuator/configprops` sanitize all keys containing `password`, `secret`, `key`, `token`.

## 2. Cryptographic Standards
- [ ] Symmetric encryption uses `AES/GCM/NoPadding` with fresh 96-bit IV generated per operation.
- [ ] Insecure algorithms banned: MD5, SHA-1, DES, 3DES, RC4, ECB mode.
- [ ] Password hashing uses Argon2id or BCrypt with minimum work factor 12.
- [ ] TLS 1.3 enforced for all ingress and inter-service communication.

## 3. Application Security Controls
- [ ] Native Java serialization disabled (`java.io.ObjectInputStream`).
- [ ] Jackson polymorphic typing disabled globally.
- [ ] SSRF validation applied on all outbound HTTP calls with private/metadata IP address filtering.
- [ ] Dependencies scanned for CVEs in CI pipeline via OWASP Dependency-Check or Snyk.
