# Theory: 02-oauth2

## Core Concepts

### OAuth2 flows, authorization code, client credentials, PKCE

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

- RFC 6749: The OAuth 2.0 Authorization Framework — October 2012 (Standards Track, obsoletes RFC 5849) — https://www.rfc-editor.org/info/rfc6749/ — Takeaway tied to lab: implement the §1.2 abstract protocol flow (A–F) and §4.1 authorization-code grant in the Spring OAuth2-client exercise; note §1.3.1 security benefits of passing the access token directly to the client instead of through the user-agent.
- RFC 9700: Best Current Practice for OAuth 2.0 Security — January 2025 (updates RFCs 6749/6750) — https://datatracker.ietf.org/doc/rfc9700/ — Takeaway tied to lab: apply to the PKCE/grant-type exercise — avoid implicit and resource-owner-password-credentials grants, use short-lived sender-constrained tokens, refresh-token rotation, exact redirect-URI matching, and `state` for CSRF protection.
- OAuth 2.0 (oauth.net) — living overview (accessed Oct 2026) — https://oauth.net/2/ — Takeaway tied to lab: use as index into current profiles/extensions when wiring authorization-code vs client-credentials (§1.3.4, machine-to-machine) flows in Java, and to confirm when to reach for OpenID Connect on top.
