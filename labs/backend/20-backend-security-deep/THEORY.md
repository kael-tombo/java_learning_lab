# Theory: Backend Security Deep Dive

## The Trust Boundary Rule

Everything crossing from outside — HTTP parameters, path variables, headers,
JWT claims, uploaded files, deserialized JSON — is untrusted until validated
against a schema and an authorization decision. In Spring, validation lives in
`@Valid`/`@Validated` on controllers (Jakarta Bean Validation), schema shape
in records with `@NotNull`/`@Size`/`@Pattern`, and authorization in Spring
Security's filter chain plus method security. Most real vulnerabilities are
the same handful of ways this rule is violated.

## Authentication vs Authorization

Authentication proves identity; authorization decides what identity may do.
Mixing them — e.g. "this filter checks the token, so this service method is
safe" — fails the moment a new internal caller bypasses the filter (message
consumers, scheduled jobs, GraphQL data fetchers). Prefer defense in depth:
filter chain gates the edge, `@PreAuthorize`/`@PostAuthorize` enforce per
method `(id == #ownerId)` ownership checks.

## Injection

SQL injection survives any framework that lets user input reach query strings.
`JdbcTemplate` with `String.format`, Spring Data JPA `@Query` built by
concatenation, and `EntityManager.createNativeQuery` with `+` all have the
same bug. The fix is always parameter binding (`?` placeholders, `:named`,
JPA criteria). Second-order injection — stored user input re-used later in a
query — is the variant that slips code review because the dangerous value
isn't in the request anymore.

## Session, CSRF, CORS

- **CSRF** matters whenever auth rides in cookies: a malicious site can
  trigger authenticated requests. Spring Security's default protection applies
  to state-changing verbs for browser clients; disabling it "for the API"
  re-opens the hole if any browser-facing endpoint accepts cookies.
- **CORS** is often misread: `allowedOrigins: ["*"]` with
  `allowCredentials: true` is rejected by browsers, but equally dangerous
  variants (reflecting the Origin header) silently grant cross-origin reads.
- **Session fixation**: rotate the session id on login — Spring Security's
  default `sessionFixationStrategy` does this; custom auth filters often don't.

## Password Handling and Token Pitfalls

Passwords go through a slow, salted hash: `BCryptPasswordEncoder` (work factor
10–13) or Argon2id. Issues seen in production: logging the raw password during
debug, encoding instead of hashing (`Base64`), reusing the hash as the auth
token in custom headers, and timing oracles that reveal whether a username
exists. JWTs inherit a different list: accepting `alg: none`, skipping audience
and issuer validation, never checking expiry, and storing long-lived JWTs in
localStorage where any XSS payload steals them. RS256 with JWKS rotation plus
short expiry and refresh-token rotation via an HttpOnly cookie is the
defensible baseline.

## Headers, Transport, Dependencies

`SecurityHeadersFilter` (CSP, HSTS, X-Content-Type-Options, frame options) is
on by default but frequently weakened during "it breaks my app" debugging and
never restored. `DependencyCheck`/OWASP dependency-check in CI catches CVEs in
transitives; `Content-Type` confusion (accepting `text/plain` bodies and
parsing them as JSON, or allowing file uploads without type sniffing checks)
remains a steady source of stored XSS.

## Failure Modes in Production

- BOLA/IDOR: `GET /orders/{id}` returns any order when the lookup ignores the
  caller's ownership — the single most common API breach pattern.
- Verbose error leakage: stack traces in 500 bodies expose versions and
  internals that reconnaissance feeds on.
- JWT algorithm confusion (`RS256` vs `HS256` key reuse) enabling forged
  tokens.
- Rate-limit absence: credential stuffing against `/login` goes unnoticed
  until the SIEM flags it.
- Multi-tenant filter scoping a Hibernate query but not the native SQL
  dashboard query — leaking across tenants in the "reporting" path.

## References

- OWASP Top 10 (2021) and OWASP Cheat Sheets
- Spring Security Reference: Architecture, CSRF, CORS
