# Theory: Security Basics

## Spring Security Architecture

### Security Filter Chain
Spring Security uses a chain of servlet filters:
1. SecurityContextPersistenceFilter
2. LogoutFilter
3. UsernamePasswordAuthenticationFilter
4. ExceptionTranslationFilter
5. FilterSecurityInterceptor

### Authentication
- **AuthenticationManager**: Core authentication strategy
- **ProviderManager**: Delegates to AuthenticationProvider(s)
- **AuthenticationProvider**: Validates credentials
- **UserDetailsService**: Loads user details from database
- **PasswordEncoder**: Encodes and verifies passwords

### Authorization
- **FilterSecurityInterceptor**: Authorizes HTTP requests
- **@PreAuthorize**: Method-level access control
- **@Secured**: Simple role-based access
- **GrantedAuthority**: Represents permission/role

### Core Annotations
- @EnableWebSecurity
- @EnableGlobalMethodSecurity
- @PreFilter / @PostFilter
- @PreAuthorize("hasRole('ADMIN')")

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Password Storage Cheat Sheet" — OWASP Cheat Sheet Series (living document, recommendations current as of fetch Oct 2026) — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html — Takeaway tied to PasswordEncoder in this lab: never store plaintext; use slow memory-hard hashes — Argon2id (min 19 MiB, 2 iterations, parallelism 1), scrypt or bcrypt (work factor ≥ 10) for legacy, PBKDF2-HMAC-SHA256 600k iterations for FIPS-140 — fast hashes like SHA-256 alone are unsuitable.
- "Password Storage Cheat Sheet" (same page, Salting section; fetched Oct 2026) — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html — Takeaway tied to UserDetailsService-backed authentication in this lab: per-user unique salts (auto-managed by Argon2id/bcrypt/PBKDF2 libraries) defeat rainbow tables and ensure identical passwords hash differently, so the user store must persist the salt/hash pair per account.
- "Password Storage Cheat Sheet" (same page, Peppering + Work Factors sections; fetched Oct 2026) — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html — Takeaway tied to hardening the AuthenticationManager/Provider chain in this lab: add defense-in-depth with a secret pepper kept outside the DB (HSM/secrets vault, rotation forces password resets) and tune the work factor so verification takes < 1s, re-hashing on login when the factor is raised.
