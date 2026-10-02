# Theory: 07-csrf-xss-protection

## Core Concepts

### CSRF tokens, XSS prevention, content security policy

Security in Java applications is built on foundational concepts that work together to protect resources and data.

### Key Principles

1. **Defense in Depth** - Multiple layers of security controls ensure that if one layer fails, others still provide protection.

2. **Least Privilege** - Every component should operate with the minimum set of permissions necessary to function.

3. **Fail Secure** - When a security control fails, it should default to a denied state rather than an allowed state.

4. **Separation of Concerns** - Security logic should be separated from business logic.

### Spring Security Integration

Spring Security provides a comprehensive framework that implements these principles through its filter chain architecture, authentication providers, and authorization managers.

### Java Platform Support

The Java platform provides:

- Java Cryptography Architecture (JCA) for cryptographic operations
- Java Authentication and Authorization Service (JAAS)
- Java Secure Socket Extension (JSSE) for TLS/SSL

## Detailed Analysis

### Authentication

Authentication verifies the identity of a user or system. Spring Security supports multiple authentication mechanisms including form login, HTTP Basic, OAuth2, and SAML.

### Authorization

Authorization determines what an authenticated user is allowed to do. This can be role-based, scope-based, or attribute-based.

### Cryptography

Cryptographic operations ensure data confidentiality, integrity, and authenticity. Java provides strong cryptographic support through the JCA framework.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- OWASP Cross-Site Request Forgery Prevention Cheat Sheet — living document (accessed Oct 2026) — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html — Takeaway tied to lab: implement synchronizer-token pattern (per-session/per-request CSPRNG token validated server-side) for state-changing POST/PUT/DELETE in the Spring Security filter-chain exercise; never put the token in a cookie or URL.
- OWASP Cross Site Scripting Prevention Cheat Sheet — living document (accessed Oct 2026) — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html — Takeaway tied to lab: any XSS defeats CSRF tokens, so pair CSRF-token exercises with context-sensitive output encoding/CSP from this sheet before testing bypasses.
- OWASP Cross-Site Request Forgery (CSRF) attack page — living document (accessed Oct 2026) — https://community.owasp.org/attacks/csrf — Takeaway tied to lab: use it to frame the login-form CSRF exercise (attacker forges an authenticated browser request via auto-sent session cookies) and to justify SameSite + Origin/Referer defense-in-depth checks alongside tokens.
