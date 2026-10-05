# VISION — Security (Crypto, TLS, Auth, OWASP)

## Vision Statement
**Security is defaults + verification** — encrypt with standard primitives,
validate every boundary, and manage secrets so the happy path is also the
safe path. Never roll your own crypto.

---

## Mental Models
### 1. Boundaries Are Attack Surface
Every parse (JSON, JWT, file, SQL) is untrusted. Validate, cap sizes,
parameterize queries, encode output — injection lives at concatenation.
### 2. Crypto Has One Right Way
AES-GCM (random 96-bit IV), bcrypt/argon2 for passwords, `SecureRandom`,
TLS 1.2+ with hostname verification. `ECB`, `MD5/SHA1`, static IVs = bugs.
### 3. AuthN ≠ AuthZ ≠ Secrets
OIDC/JWT for identity, scopes/roles for authorization, vault/KMS for keys.
JWTs verified (sig + exp + aud + iss), never trusted by shape; rotate keys.
### 4. Least Privilege Everywhere
File, DB, and network permissions minimal; dependency CVEs triaged (SBOM);
security headers + audit logs on auth events; `jcmd` only over secured attach.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Hash passwords? | bcrypt/argon2, never MD5/SHA-256 bare |
| Encrypt data? | AES-GCM + KMS envelope, random IV per message |
| Accept JWT? | Verify sig/exp/aud/iss; short TTL + refresh |
| Build query? | Prepared statements / bound params only |
| Add dependency? | CVE + provenance check first |

---

## Career Trajectory
- **L1:** Hashing, salting, JWT verify, OWASP Top-10 basics, headers.
- **L2:** TLS/mTLS setup, OAuth2 flows, vault integration, ZAP scans.
- **L3:** Threat modeling, key rotation, crypto agility, SAST/DAST gates.
- **L4:** Security architecture (zero-trust, incident response policy).

---

## 4-Week Path
```
W1: Hashing, SecureRandom, AES-GCM lab, password verify kata.
W2: JWT issue/verify/rotate, OAuth2 code flow with Keycloak.
W3: OWASP lab (SQLi, XSS, SSRF, path traversal) + fixes.
W4: Hardened notes-API capstone + ZAP scan report.
```
## Success Metrics
- [ ] ZAP high-findings = 0; secrets outside repo
- [ ] JWT forgeries/expired/replayed all rejected with tests
- [ ] Crypto choices cite standard-names doc
