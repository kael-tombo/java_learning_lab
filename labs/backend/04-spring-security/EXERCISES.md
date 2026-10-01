# Exercises: Spring Security / JWT Rotation

## Exercise 1: Issue + Verify
Implement `createAccessToken` / `verify` with HMAC-SHA256, `exp`/`iat` claims,
and ±60s clock-skew tolerance. Test: valid, expired, tampered-signature, and
future-`nbf` tokens.

## Exercise 2: Rotation
Implement refresh rotation: each `/refresh` returns a new access + refresh pair
and invalidates the old refresh token. Test that the old token no longer works.

## Exercise 3: Reuse Detection
Simulate theft: refresh twice with the SAME refresh token concurrently. Assert
the second attempt triggers family-wide revocation (all tokens for the user die).

## Exercise 4: Revocation Store
Back revocation with an in-memory/Redis blacklist keyed by `jti` with TTL =
token expiry. Write a test: logout → access token rejected, then accepted again
only after TTL passes (use short TTLs in tests).

## Exercise 5: Spring Security Wiring
Wire a `OncePerRequestFilter` that validates the Bearer token, populates
`SecurityContextHolder`, and protects `/api/**` while leaving `/auth/**` open.
Test with MockMvc: no token → 401, valid token → 200, revoked → 401.
