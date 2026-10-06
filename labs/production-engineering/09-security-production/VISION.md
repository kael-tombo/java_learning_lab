# VISION — Lab 09: Security Engineering in Production

> From "we use HTTPS and a login page" to "here is our threat model, and here is the evidence that each control works."

---

## The Arc

1. **Threat modelling** — what are we protecting, from whom, and which assets actually attract attackers (identity, secrets, money).
2. **Identity** — OAuth2/OIDC, JWT validation, scopes, session vs token, revocation reality.
3. **Spring Security in anger** — filter chains, method security, stateless config, the "silently ignored annotation" trap.
4. **Injection and untrusted input** — SQL, XSS, SSRF, deserialization, XXE, traversal, and resource-exhaustion limits.
5. **Transport, headers, and browser** — TLS/mTLS done right, HSTS/CSP/nosniff, cookie flags.
6. **Secrets and configuration** — where they leak, K8s Secret vs file vs dynamic credentials, actuator as an exfiltration surface.
7. **Supply chain** — SBOM, pinning, dependency confusion, build provenance, CI secret scoping.
8. **PII and compliance** — encryption layers, tokenisation, erasure propagation, audit logging.
9. **Proving it** — tests, fuzzing, dependency scanning, and a CI gate that blocks the regressions.

---

## Why this lab exists

Most production breaches of well-engineered Java services are not cryptanalysis. They are a missing authorization check, a secret in an env var that ended up in a log, an actuator endpoint on the public ingress, or a token valid for an hour after you revoked the session.

The specific goal here: **you can enumerate the security controls a Java service must have, explain the mechanism each one blocks, and demonstrate that its absence is exploitable.** And you can say, honestly, which risks you accept and why.

---

## Milestones (checkable)

- [ ] M1: Write a threat model (STRIDE) for one real service, naming the top 3 assets and the top 3 abuse cases.
- [ ] M2: Implement an OIDC resource-server config and demonstrate that a token with a wrong `aud`, wrong `iss`, expired `exp`, or `alg: none` is rejected — with a test for each case.
- [ ] M3: Find and fix one authorization gap (missing `@PreAuthorize`, `permitAll` on an internal path, or `@EnableMethodSecurity` absent) with an integration test proving the fix.
- [ ] M4: Produce a secret inventory for a real service and migrate every static secret to a mounted/dynamic credential, with rotation demonstrated.
- [ ] M5: Explain the difference between `readOnlyRootFilesystem`-era defence and the actuator exposure surface, and lock actuator down with a test.
- [ ] M6: Generate an SBOM for a real artifact and answer "are we affected by CVE-X?" for a real advisory in under 5 minutes.
- [ ] M7: Define and enforce the CI security gate list (dependency scan, secret scan, SAST, header check, authz coverage) and show it blocking a deliberately vulnerable PR.

---

## Anti-Goals

- Trusting the `alg` header or skipping `iss`/`aud` validation.
- Long-lived static tokens with no revocation path.
- `csrf().disable()` on a cookie-authenticated app.
- `@PreAuthorize` without `@EnableMethodSecurity`.
- Actuator exposed with `env`, `heapdump`, or `loggers` reachable from outside.
- Trust-all `TrustManager` / `NoopHostnameVerifier` in production code.
- PII or credentials in logs, spans, or error trackers.
- Client-supplied `pageSize`, `fields`, or sort columns without an allow-list.
- Secrets committed to git "just for local dev" without a documented rotation.

---

## Interview Lens

- "How do you revoke a JWT?"
- "Where do secrets live in your platform and how do they rotate?"
- "How do you prevent SQL injection when the user controls the sort column?"
- "What does your SBOM let you do in the first hour of a CVE advisory?"
- "How do you know your internal endpoints are actually authenticated?"

---

## 30-Day Plan

- **Week 1** — THEORY: threat modelling, identity/JWT, Spring Security filter chains; hands-on: build a resource server and attack it with wrong-audience and alg-none tokens. M1–M2.
- **Week 2** — EXERCISES: authorization matrix, secret handling, header config; QUIZ to 13/15; FLASHCARDS daily. M3–M5.
- **Week 3** — MINI_PROJECT: harden a deliberately vulnerable Spring app end to end, then prove each fix with a test. M6–M7.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a security posture review for a real service; teach-back: "our threat model and our accepted risks" in 10 minutes.

---

## Artifacts you should be able to show

1. A threat model with assets, trust boundaries, and abuse cases.
2. A JWT validation test suite covering `alg`, `iss`, `aud`, `exp`, `nbf`.
3. An authorization matrix mapping every endpoint to a required authority, with a CI check enforcing coverage.
4. A secret inventory with rotation evidence for each item.
5. An SBOM plus a measured "minutes to identify affected artifacts" for a real advisory.
6. A CI security gate report blocking a deliberately vulnerable PR.

---

## Done = You Can

- Explain the mechanism behind each control you enable, not just its name.
- Write a test that fails when an authorization check is removed.
- Say what risk you are accepting and what would change your mind.
- Take an advisory from publication to a fleet-wide fix with evidence.
