# Lab 09: Security Engineering in Production — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the actual security model of a JWT, and what does that imply about logout?**
- A) JWTs are encrypted; revoking one is instant
- B) A JWT is a signed, self-contained assertion. Anyone who can verify the signature trusts it, so logout cannot be immediate without server-side state — you need a denylist, a short expiry, or introspection
- C) JWTs are server-side sessions in disguise
- D) JWT expiry cannot be set

**Answer: B** — Signed ≠ encrypted: anyone can read the claims. So minimize PII in the payload, use short access-token lifetimes (5–15 min) plus refresh tokens, and accept that revocation is bounded by TTL unless you add state.

---

**Q2. Why validate a JWT's `iss`, `aud`, `exp`, `nbf`, and algorithm — not just the signature?**
- A) They are optional metadata
- B) A signature from the trusted issuer proves nothing about *who* it was meant for: without `aud` check you accept a token minted for a different service (confused deputy), and without pinning the algorithm you enable `alg: none` / algorithm-confusion attacks
- C) It improves performance
- D) Only symmetric JWTs need them

**Answer: B** — Every claim is a security control, not documentation. And always pin the expected algorithm; never trust the `alg` header.

---

**Q3. Spring Security's default CSRF behaviour, and when is it safe to disable?**
- A) CSRF protection is on by default; disabling it is safe for any stateless API using bearer tokens in the `Authorization` header
- B) CSRF is off by default and should stay on
- C) CSRF only applies to cookie sessions
- D) Disabling CSRF is never safe

**Answer: A** — The classic CSRF attack relies on the browser *automatically* attaching an ambient credential (cookie). A bearer token read from a header cannot be forged cross-site, so `csrf.disable()` is correct for stateless APIs — and dangerous for anything cookie-authenticated.

---

**Q4. Why is `permitAll()` on a `/internal/**` path a serious finding?**
- A) It is a performance issue
- B) Internal endpoints must still be authenticated; "internal" is a network location, not an identity. Anyone who can reach the pod (a compromised pod, a flat network, a misrouted ingress) gets unauthenticated access
- C) `permitAll` requires a CSRF token
- D) It disables logging

**Answer: B** — Use mTLS or a service-account JWT for service-to-service identity, and enforce the rule in CI (`@PreAuthorize` presence check).

---

**Q5. The N+1 query and unbounded result set — what is the security angle beyond performance?**
- A) None; it is purely a performance issue
- B) It is both: a performance DoS vector (a single request can consume the DB) and a data-exfiltration vector (a client-controlled `pageSize` returning an entire table)
- C) It only affects logs
- D) It enables SQL injection

**Answer: B** — Every missing limit is an availability and confidentiality control, not just a tuning knob. Cap `pageSize` server-side and always allow-list sort fields.

---

**Q6. Why parameterised queries are the only reliable defence against SQL injection?**
- A) Input validation and escaping are enough
- B) Escaping depends on character set and context; parameterisation keeps data and code in separate channels so no input can change statement structure
- C) Prepared statements are faster only
- D) Stored procedures prevent it

**Answer: B** — Validation and escaping are defence-in-depth; the structural guarantee is parameterisation. Note also that ORDER BY, table names, and `IN` lists cannot be parameterised — those need allow-listing.

---

**Q7. What is the danger of `ORDER BY ${userInput}`?**
- A) None
- B) `${}` performs string substitution, so a sort field is concatenated into the statement and becomes injectable; `?` binding cannot be used for identifiers, so you must map a whitelist token → real column name
- C) It is slow
- D) It prevents indexing

**Answer: B** — Whitelist-map sort fields (`"createdAt" → "created_at"`), never concatenate. Same for table names, direction, and `IN` lists.

---

**Q8. Why must a Spring Boot actuator be restricted, and how?**
- A) Actuator is harmless
- B) `/actuator/env`, `/heapdump`, `/threaddump`, `/loggers` (POST) leak environment variables — including secrets — full heap contents (session tokens, PII), and allow runtime log-level changes and log-file writes
- C) Actuator needs HTTPS only
- D) Actuator exposes only health

**Answer: B** — Expose only `health,info,prometheus,metrics`; separate the management port; require authentication; block `env`, `heapdump`, `loggers`, `mappings` from the internet.

---

**Q9. Spring Boot Actuator `/env` redaction: what does `management.endpoint.env.show-values: NEVER` actually do and not do?**
- A) It encrypts the values
- B) It masks values for keys matching `*password*`, `*secret*`, `*key*`, `*token*`, `*credentials*`, `*vcap_services*` — but any secret stored under an unmatching key name is still printed in clear text
- C) It removes all values
- D) It only affects the `/env` sub-path

**Answer: B** — Redaction is a heuristic on key names. Never rely on it; keep secrets out of `SPRING_APPLICATION_JSON` and env vars visible to actuator in the first place.

---

**Q10. Secret management: why is a Kubernetes Secret mounted as an env var worse than as a file?**
- A) Files are always more secure
- B) Env vars appear in `kubectl describe pod`, `/proc/<pid>/environ`, crash dumps, and are inherited by child processes; file mounts can be memory-backed (`emptyDir` with `medium: Memory`) and file-permission controlled
- C) Env vars are not encrypted at rest either way
- D) Files cannot be rotated

**Answer: B** — Combine with `Secret` objects managed by an external secrets operator, `etcd` encryption at rest, RBAC so not every namespace can read the secret, and short-lived dynamic credentials where possible.

---

**Q11. TLS is configured but the app also trusts all certificates (`TrustAllCerts`). Why is this worse than no TLS?**
- A) It is slower
- B) You have encrypted a channel to an unauthenticated peer; an active MITM can intercept everything while the logs show "TLS enabled". TLS without certificate validation provides no protection against the threat it exists for
- C) It disables OCSP
- D) It only affects outbound calls

**Answer: B** — Trust-all in code is a permanent backdoor. Use the platform trust store and rotate it; add a CI check for `TrustManager`/`NoopHostnameVerifier` implementations.

---

**Q12. Supply-chain security: what do an SBOM and dependency pinning actually protect against?**
- A) Runtime attacks only
- B) SBOM (CycloneDX/SPDX) makes you able to answer "are we affected by CVE-X?" in minutes across your whole estate; pinning digests prevents a mutable tag from silently changing what you run; signature verification blocks a substituted artifact
- C) They speed up builds
- D) They scan for malware in runtime code

**Answer: B** — Assume breach: the question is not "can a CVE reach us?" but "can we identify every affected artifact in minutes?"

---

**Q13. PII handling: what must a log statement never do?**
- A) Log a hashed user id
- B) Log raw PII (email, card, name, address, full request/response bodies, authorization headers, cookies, session ids) — because logs are replicated to aggregators with different access control and much longer retention than your database
- C) Log a request id
- D) Log latency

**Answer: B** — Log an internal surrogate id and resolve it via an audited lookup. Add a log-scrubbing filter and a CI grep for `log.*password|token|Authorization`.

---

**Q14. Dependency-confusion: what is the attack and the defence?**
- A) A vulnerable transitive dependency; upgrade it
- B) An attacker publishes a higher-version package with the same name in a public registry so unscoped resolutions pick it up; defend by scoping internal artifacts to a private registry, requiring lockfiles, verifying signatures/checksums, and pinning versions
- C) A type-confusion bug in generics
- D) An outdated Maven mirror

**Answer: B** — Also verify that your Maven `settings.xml` mirror config cannot be overridden by repository declarations in transitive POMs.

---

**Q15. The single most common way a well-engineered Java service is actually breached in production is?**
- A) A novel zero-day in the JVM
- B) Credentials: a hardcoded or over-scoped secret, an unauthenticated internal endpoint, an actuator exposed publicly, or a leaked token in a log — all of which are configuration mistakes, not cryptography failures
- C) A SQL injection in a new endpoint
- D) A missing security header

**Answer: B** — Most breaches are authorization and secret-handling failures. That is why identity, scope, and secret hygiene dominate the hardening checklist.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and audit a real service.
- 12–10: revisit JWT validation, CSRF model, and secret handling; redo EXERCISES 2–5.
- <10: re-read THEORY + ANTI_PATTERNS cold, then re-run the hardening checklist against a sample app.
