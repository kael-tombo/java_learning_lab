# Flashcards: Spring Security / JWT Rotation

## Q: Short access token + long refresh token — why?
**A:** Stolen access tokens expire fast; the refresh token is server-tracked and revocable.

## Q: What is refresh-token rotation?
**A:** Every refresh returns a NEW refresh token and invalidates the previous one.

## Q: What is reuse detection?
**A:** Presenting an already-rotated token signals theft → revoke the whole token family.

## Q: How is an HMAC-SHA256 JWT verified?
**A:** Recompute signature over `header.payload` with the secret (constant-time compare) + validate `exp`/`nbf` with skew tolerance.

## Q: Where to store revocations?
**A:** Server-side (e.g. Redis) with TTL = token expiry; checked per request.

## Q: Bearer header vs HttpOnly cookie split?
**A:** Access token in `Authorization` header for API calls; refresh token in HttpOnly+Secure cookie so XSS JS cannot read it.

## Q: Clock-skew tolerance?
**A:** Allow ±60s drift when validating `exp`/`nbf`/`iat` across machines.

## Q: Where does JWT validation sit in Spring Security?
**A:** A `OncePerRequestFilter` that fills `SecurityContextHolder` before authorization.

## Q: Why constant-time comparison?
**A:** Prevents timing attacks on signatures/hashes.

## Q: What happens on logout?
**A:** Revoke the refresh family + blacklist the access token until `exp`.
