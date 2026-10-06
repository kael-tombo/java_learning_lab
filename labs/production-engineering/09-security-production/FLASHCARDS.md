# Lab 09: Security Engineering in Production — Flashcards

~60 cards. Most answers are a control, a header, or a claim you must validate.

---

## Identity & JWT

Q: JWT = header.payload.signature. What is signed and what is visible?
A: Base64url header and payload are *signed* but readable by anyone; the signature is HMAC (shared secret) or asymmetric (private key signs, public key verifies). JWTs are not encrypted.

Q: Mandatory claims to validate?
A: `alg` (pinned by you, not trusted from the header), `iss`, `aud`, `exp`, `nbf`, and `iat` sanity. Plus `jti` if you need replay detection.

Q: Why pin the algorithm?
A: Trusting the `alg` header enables `alg: none` and RSA→HMAC key-confusion attacks where the public key is used as the HMAC secret.

Q: What does a missing `aud` check enable?
A: Confused deputy: a token legitimately issued for a *different* service is accepted by yours because you only verified the issuer's signature.

Q: Access token lifetime?
A: 5–15 minutes, so the revocation window equals the TTL. Refresh token: longer, rotated on every use, with reuse detection.

Q: Refresh-token rotation and reuse detection?
A: Each refresh mints a new refresh token and invalidates the old one. Presenting a used refresh token means it was stolen — revoke the whole family.

Q: Where to store tokens in a browser?
A: `HttpOnly; Secure; SameSite=Lax|Strict` cookies for the session cookie, or in-memory JS with BFF pattern. **Never** `localStorage` (XSS reads it).

Q: CSRF: when is protection required?
A: Whenever the browser attaches credentials automatically — i.e. cookie/session auth. Not needed for `Authorization: Bearer` header APIs.

Q: `SameSite` values?
A: `Strict` (never cross-site), `Lax` (top-level GET navigations), `None` (cross-site, requires `Secure`) — cross-site iframes need `None; Secure` plus CSRF tokens.

Q: Service-to-service identity in a mesh?
A: mTLS (SPIFFE/SPIRE identity) plus a short-lived service-account JWT for application authorization. "Internal" network location is not an identity.

Q: `WWW-Authenticate` vs 401 vs 403?
A: 401 = not authenticated (send `WWW-Authenticate`); 403 = authenticated but not authorized. Confusing them leaks policy information and breaks clients.

Q: Scope/role claims: least privilege shape?
A: Per-endpoint scopes (`invoices:read`), not a blanket `ROLE_USER`. Deny by default; enumerate authority at build time.

---

## Spring Security specifics

Q: Default `SecurityFilterChain` for HTTP Basic?
A: All requests authenticated, CSRF on, session created, H2 console if on classpath (disable it), no CORS configured (same-origin only), no CSP headers by default.

Q: Stateless API config?
A: `SessionCreationPolicy.STATELESS`, `csrf().disable()`, `oauth2ResourceServer().jwt()`, `SecurityContextRepository` not persisting sessions.

Q: `@PreAuthorize` vs `@Secured` vs web-security rules?
A: Method security for fine-grained logic (`@PreAuthorize("hasAuthority('invoices:write')")`); use `denyAll` for anything not explicitly granted. Web rules still apply first.

Q: `permitAll()` on `/internal/**`?
A: A finding. Authenticate with mTLS or a service JWT; enforce in CI that every `@RestController` path is covered by a security matcher or an authorization annotation.

Q: CSRF token endpoint / double-submit?
A: Spring Security's `CookieCsrfTokenRepository` with the header `X-XSRF-TOKEN` for SPAs; rotate the token after login (session fixation defence).

Q: Password hashing in Spring Security?
A: `BCryptPasswordEncoder`/`Argon2PasswordEncoder`/`SCrypt` — never MD5, SHA-1, or unsalted SHA-256. Verify current defaults; Argon2id is preferred where available.

Q: Login rate limiting?
A: Spring Security doesn't provide it out of the box; you need a bucket (Bucket4j/B Resilience4j `RateLimiter`) keyed by IP + account, plus MFA and lockout/backoff. Credential stuffing is a login-path problem.

Q: Spring Security 6 path matching change?
A: `requestMatchers("/api/**")` (the 6.x lambda form); `antMatchers`/`mvcMatchers` were removed. Verify the version in your app — this is a common upgrade compile failure and a source of accidentally-unmatched paths.

Q: Method security requires?
A: `@EnableMethodSecurity` (or `@EnableGlobalMethodSecurity` pre-6). Without it, `@PreAuthorize` is silently ignored — a very common false sense of security.

---

## Injection & input handling

Q: Defence against SQL injection?
A: Parameterised queries (`?` binding) via JPA/JDBC prepared statements. Structure and data never mix.

Q: What can NOT be parameterised?
A: Identifiers (table/column names), `ORDER BY` clauses, and `IN` lists. Whitelist-map them in code.

Q: `${}` vs `#{}` in MyBatis?
A: `#{}` = prepared-statement binding (safe). `${}` = string substitution (injection risk). Audit every `${}`.

Q: JPA and dynamic sort/filter?
A: Spring Data `Sort`/`Specification`/`Criteria` build bound parameters. Never concatenate a request-supplied field name into JPQL.

Q: XSS: output encoding vs input sanitising?
A: Encode at the sink, for the actual context (HTML body, attribute, JS string, URL). Input filtering is a false comfort — use a template engine with auto-escaping and a CSP as defence in depth.

Q: CSP that actually helps?
A: `default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'` — and avoid `unsafe-inline`. Report-only mode first to measure breakage.

Q: SSRF: what is the control?
A: Never fetch a client-supplied URL. If unavoidable, resolve DNS, reject private/link-local/metadata ranges (`169.254.169.254`), re-check after redirects, and use an egress proxy.

Q: Deserialization risk?
A: Java serialization on untrusted input (`ObjectInputStream`) is remote code execution by design. Use Jackson with explicit `PolymorphicTypeValidator` or a fixed-type DTO; disable `enableDefaultTyping`.

Q: XXE in XML parsing?
A: Disable DTDs and external entities (`DocumentBuilderFactory.setFeature("disallow-doctype-decl", true)`, `XMLConstants.FEATURE_SECURE_PROCESSING`). Prefer JSON where you have the choice.

Q: Path traversal?
A: Canonicalise and confine: `Paths.get(base).resolve(rel).normalize().startsWith(base)` — plus an allow-list of resource ids. Never build paths from raw request data.

Q: Unbounded input: `pageSize`, `ids`, `fields`?
A: Cap `pageSize` server-side (e.g. 100 max), cap the length of `ids`/`fields` lists, and allow-list `fields` against a known projection set.

---

## Transport & headers

Q: Minimum response headers?
A: `Strict-Transport-Security` (max-age ≥ 1 year, includeSubDomains), `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `frame-ancestors`/`X-Frame-Options` for non-embedding.

Q: TLS 1.2 vs 1.3?
A: Require 1.2 minimum, prefer 1.3. Disable weak cipher suites and legacy renegotiation.

Q: Trust-all `TrustManager` / `NoopHostnameVerifier`?
A: A permanent MITM backdoor that still logs "TLS enabled". Forbidden in production; detect with a CI grep and a security scanner rule.

Q: mTLS for service-to-service: what does it give and cost?
A: Workload identity + encryption. Cost: handshake CPU (reuse connections, enable session resumption), certificate rotation (SPIFFE/SPIRE or mesh CA), and per-hop latency.

Q: Certificate pinning?
A: Pin SPKI for high-value first-party connections; pin *keys*, not certs, so rotation is survivable. Avoid pinning to a private CA you don't control.

---

## Secrets & configuration

Q: Why not put secrets in `application.yml` or a container image?
A: They are baked into the image layer, visible in the registry, and in git history forever. Never commit a real secret; use placeholders and secret injection.

Q: Env var vs mounted file for a secret?
A: Files: not in `kubectl describe pod`, not in `/proc/<pid>/environ`, not inherited by children, permission-controllable, and `emptyDir { medium: Memory }` keeps them off disk. Rotate by atomically swapping the projected volume (Spring Cloud Config / Reloader).

Q: Kubernetes `Secret`: is it secure by default?
A: No — base64, not encryption. Enable `etcd` encryption at rest (`EncryptionConfiguration`), restrict RBAC on secret reads in that namespace, and prefer an external secrets operator syncing from Vault/AWS Secrets Manager.

Q: Dynamic credentials vs static secrets?
A: Prefer short-lived dynamic credentials (DB IAM auth, IRSA/Workload Identity, Vault leases) so a leak has a small blast radius.

Q: `management.endpoint.env.show-values` default?
A: `NEVER`-ish behaviour with key-name heuristics (`*password*`, `*secret*`, `*key*`, `*token*`, `*credentials*`). Unmatched key names leak in clear text — do not rely on it.

Q: Actuator: which endpoints to expose publicly?
A: None. Expose `health,info,prometheus,metrics` on a separate management port, authenticated, bound to an internal interface.

Q: Dangerous actuator endpoints?
A: `env`, `configprops`, `heapdump`, `threaddump`, `loggers` (POST changes levels), `mappings` (full route map), `shutdown` (POST kills the app), `jolokia`/`jmx` if present.

Q: Spring Cloud Config `refresh` scope?
A: Allows remote config change. If you don't need hot refresh, disable it and remove the dependency — it is a runtime mutation vector.

---

## Secrets in code & supply chain

Q: Hardcoded credential: why is it worse than no auth?
A: It is in git history, in every clone, in every CI log, and it looks intentional, so it survives for years. Rotate first, then remove.

Q: SBOM format?
A: CycloneDX or SPDX. Its purpose is answering "which of our artifacts contain CVE-X?" in minutes during an advisory.

Q: Dependency pinning?
A: Pin versions and verify checksums/signatures. Lock files plus an internal registry mirror prevent a transitive resolution from changing what you build.

Q: Dependency confusion?
A: Attacker publishes a higher-version package with your internal artifact's name in a public registry and wins unscoped resolution. Defend: scope internal coordinates to a private registry, restrict allowed repos, verify signatures, review transitive POM repository declarations.

Q: Maven mirror configuration risk?
A: `settings.xml` `<mirrors>` should be authoritative; a transitive POM declaring another repository can otherwise pull from anywhere.

Q: Build reproducibility & provenance?
A: Build once, promote the same digest through environments (no rebuild per stage); emit SLSA-style provenance; sign the image and verify at admission.

Q: CI secret scoping?
A: Per-job, per-environment, short-lived (OIDC federation instead of long-lived tokens), never echoed, masked in logs, and rotated on offboarding.

---

## PII & compliance

Q: Encryption at rest vs in transit vs in use?
A: At rest (disk/database encryption), in transit (TLS/mTLS), and in use (application-level field encryption or tokenisation for the most sensitive columns). You usually need all three for the sensitive subset.

Q: Tokenisation vs field encryption?
A: Tokenisation replaces the value with a reversible reference stored in a separate, more controlled store; field encryption keeps it in place. Tokenisation is easier to revoke/erase; encryption needs key rotation.

Q: GDPR erasure and backups?
A: Erasure must propagate to replicas, caches, search indexes, and analytics. Backups may retain data under legitimate-interest/legal-retention grounds — document the position rather than pretending.

Q: What must be in an audit log?
A: Who, what, when, from where, with outcome — for authentication, authorization decisions, data export, and configuration change. Append-only, tamper-evident, separate from app logs.

Q: Secrets/PII in logs is a compliance event or a hygiene issue?
A: Compliance. Logs are replicated, retained longer, and accessible to a broader audience than your database. Use a scrubbing filter and CI checks.

---

## Numbers and defaults to memorize

Q: Access token TTL?
A: 5–15 min. Refresh token: hours–days, rotated, with reuse detection.

Q: Password hashing default?
A: Argon2id preferred; BCrypt acceptable. Never MD5/SHA-1/unsalted SHA.

Q: Default actuator base path?
A: `/actuator`. Management port default is the app port unless configured — set a separate port.

Q: HSTS `max-age` minimum?
A: 31,536,000 s (1 year), with `includeSubDomains`; consider `preload` only if you own every subdomain.

Q: `frame-ancestors` / `X-Frame-Options`?
A: `'none'`/`DENY` unless the app must be embedded.

Q: Max page size?
A: Cap it (e.g. 100). Uncapped pagination is a data-exfiltration and DoS vector.

Q: bcrypt cost default?
A: 10. Raise it as hardware improves; Argon2 parameters (m=64MB, t=3, p=4) are a better default in modern stacks.

Q: Slack/incident-channel secret handling rule?
A: Never paste tokens, JWTs, or full request bodies into chat. Log a reference (request id) instead.

Q: How often to rotate static secrets?
A: Frequently enough to matter — and on every offboarding. Dynamic credentials make rotation automatic.
