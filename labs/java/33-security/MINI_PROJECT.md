# MINI PROJECT — Security: Hardened Notes API

## Goal (2 weeks, ~8–10h)
Ship a `notes-api` (Spring Boot) that survives an OWASP-style assault: real
auth, encrypted secrets, injection-proof persistence, and a clean ZAP scan.

## Requirements
### Functional
1. Auth: OIDC/JWT resource server (Keycloak or test issuer); scopes
   `notes:read/write`; verify `sig+exp+aud+iss`; `401/403` shapes tested.
2. Crypto: AES-GCM note-body encryption (KMS-fake local key, 96-bit random
   IV per note); bcrypt password hash for local users; `SecureRandom` only.
3. Injection-proof: JPA bound params exclusively; filename/path traversal
   guard (`normalize + startsWith(base)`); upload size cap + type allowlist.
4. SSRF guard: URL-fetch feature allowlists hosts, blocks metadata IP
   (`169.254.169.254`) and private ranges; connect+read timeout 2s.
5. Headers + logs: `Content-Security-Policy`, `HSTS`, `X-Content-Type-Options`;
   audit log auth failures (no passwords/tokens logged); rate-limit login.

### Non-functional
- ZAP baseline scan: 0 High findings (attach report); `mvn dependency-check`
  with 0 critical un-triaged.
- 20+ tests: JWT forged/expired/wrong-aud, SQLi strings inert, traversal
  blocked, SSRF metadata blocked, AES tamper (tag-mismatch) rejected.
- Secrets via env/vault only (`grep` gate: no `password=` in repo).
- README: threat model (STRIDE-lite table) + key-rotation runbook.

## Phases
### Week 1 — Auth + Crypto (4–5h)
- Steps: JWT verifier, scopes, AES-GCM envelope, bcrypt login, audit log.
- Deliverable: auth-matrix tests green.

### Week 2 — Assault + Harden (4–5h)
- Steps: injection/SSRF/traversal attacks, ZAP scan, fix loop, headers.
- Deliverable: ZAP report + threat-model doc.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| JWT/OAuth | Full verify + scopes tested | Works | Trusted shape |
| Crypto | GCM+random IV, bcrypt, rotation doc | Correct use | ECB/MD5/static IV |
| Injection | All vectors blocked + tested | Basics | Concatenated SQL |
| SSRF/files | Allowlist + traversal guard | Partial | Open fetch |
| Scan+hygiene | ZAP clean + no secrets | Scanned | Skipped |

Pass >= 70. Stretch: mTLS between services; JFR `jdk.TLSHandshake` audit;
Sigstore-signed image + SBOM.
