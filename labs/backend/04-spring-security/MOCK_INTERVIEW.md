# Mock Interview: JWT with Refresh Token Rotation (Lab 04)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy JWT Basics (5 min)

**Interviewer:** What is a JWT and why is it used for authentication?

**Candidate:** JWT (JSON Web Token) is a compact URL-safe token format defined by RFC 7519. It consists of three Base64-url-encoded parts: header (algorithm and token type), payload (claims like subject issuer expiration), and signature. The signature cryptographically binds the header and payload so tampering is detectable. For authentication the server issues a JWT on login and the client sends it in the Authorization Bearer header on subsequent requests. The server verifies the signature without querying a database, making JWTs stateless.

**Interviewer:** What is the difference between access tokens and refresh tokens?

**Candidate:** Access tokens are short-lived (15 minutes) and carry the user identity and permissions. They are sent with every API request. Refresh tokens are long-lived (7 days) and used only to obtain new access tokens. The separation serves two purposes: (1) If the access token is stolen, the damage window is limited to 15 minutes. (2) The refresh token can be stored more securely (HttpOnly cookie or secure client-side store) since it is used infrequently.

**Interviewer:** What goes in the JWT payload? Give a concrete example.

**Candidate:** The payload contains registered claims: sub (subject/user ID), iss (issuer), iat (issued-at timestamp), exp (expiration timestamp), and jti (JWT ID). Custom claims include roles and type (access or refresh). Example: {"sub": "user-42", "iss": "backend-academy", "iat": 1700000000, "exp": 1700000900, "roles": ["admin", "user"], "type": "access"}.

---

## Round 2: Medium Refresh Token Rotation (10 min)

**Interviewer:** What is refresh token rotation and why is it important?

**Candidate:** Refresh token rotation means that every time a refresh token is used the server issues a new refresh token and invalidates the old one. This limits the window of compromise. Without rotation a stolen refresh token is valid for its entire lifetime (e.g., 7 days). With rotation the token is valid for only one use. If an attacker steals and uses the token before the legitimate user, the user next refresh will fail alerting them to the compromise. Rotation is an OAuth 2.0 BCP (RFC 9700) recommendation.

**Interviewer:** Explain the reuse detection mechanism in detail.

**Candidate:** The server maintains a set of used refresh token hashes. On refresh, the server checks if the hash is in the used set. If not, the token is valid and the server rotates it then adds the old hash to the used set. If the hash is in the used set, the token has been reused meaning someone has a copy. The server then revokes ALL tokens for that user forcing re-authentication. The detection relies on a race condition: the legitimate user and the attacker race to use the refresh token first. The loser request triggers the alarm.

**Interviewer:** What happens when the legitimate user loses the race?

**Candidate:** They get a 401 response with error code TOKEN_REUSE_DETECTED. Their client redirects to login and they re-authenticate. This is a minor inconvenience compared to persistent attacker access. To reduce false positives, I add a grace period: on first reuse detection issue a warning but do not revoke only revoke if reuse happens again within the grace period. This handles network retries that might cause the same valid token to be sent twice.

---

## Round 3: Medium-Hard Token Signing and Verification (10 min)

**Interviewer:** HMAC-SHA256 vs RSA/ECDSA which signing algorithm would you choose?

**Candidate:** HMAC-SHA256 is symmetric the same secret signs and verifies tokens. Simpler but any service that verifies could also sign if the secret is shared. RSA/ECDSA are asymmetric a private key signs and a public key verifies. For microservice architecture RSA/ECDSA is better because only the Auth Service holds the private key. I would choose ECDSA (ES256) over RSA (RS256) because keys are smaller and verification is faster.

**Interviewer:** How do you handle JWK (JSON Web Key) rotation?

**Candidate:** The signing key rotates periodically (e.g., every 90 days). The Auth Service exposes a /.well-known/jwks.json endpoint listing current and recent public keys. Each key has a kid (key ID) in the JWT header. Verifying services cache the JWK set and refresh periodically. Old keys remain valid until the maximum token lifetime expires (e.g., 7 days for refresh tokens). This allows graceful rotation without invalidating existing sessions.

**Interviewer:** Why use constant-time comparison in signature verification?

**Candidate:** Java MessageDigest.isEqual() is constant-time it compares all bytes regardless of when the first mismatch is found. Naive Arrays.equals() short-circuits on the first different byte leaking timing information. An attacker can exploit this to forge signatures byte by byte measuring response times. Constant-time comparison prevents this side-channel attack.

**Interviewer:** How do you handle clock skew?

**Candidate:** I add a configurable clockSkewMs (default 5000ms) to the expiration check: now > (exp * 1000) + clockSkewMs. This allows tokens to be accepted up to 5 seconds after nominal expiration. The same skew applies to iat and nbf claims. The skew should be small large skews defeat the purpose of expiration.

---

## Round 4: Hard Production Hardening (15 min)

**Interviewer:** How would you scale JWT verification across 100 microservices without duplicating the secret everywhere?

**Candidate:** API Gateway pattern. The gateway handles all authentication verifies access tokens extracts user context and forwards requests with user info in headers like X-User-Id and X-User-Roles. Downstream services trust the gateway (private network) and do not need to verify JWTs themselves. This keeps the JWT secret in one place and simplifies the architecture. For service-to-service communication within the network I use mTLS instead of JWTs.

**Interviewer:** Your active refresh tokens store is in-memory. How does it survive restart?

**Candidate:** It does not all sessions would be invalidated. For production I persist refresh token metadata to Redis with TTL storing userId, familyId, expiryTime, and revoked flag. Redis persistence (AOF + RDB) provides recovery across restarts. The in-memory ConcurrentHashMap is for demonstration production systems should never rely on ephemeral storage for session data.

**Interviewer:** How would you implement token blacklisting for immediate logout?

**Candidate:** I store the token hash in Redis with TTL equal to the remaining token lifetime. The verify method checks this blacklist before verifying the signature. The Redis key is blacklist:{tokenHash} with EXPIRE remainingTtl. This list is self-cleaning. Each verify request now requires a Redis round trip adding latency. A compromise: use a Bloom filter for a fast probabilistic blacklist check with Redis as the authoritative source.

**Interviewer:** What are the security implications of storing the signing secret in source code?

**Candidate:** The signing secret must never be in source code. It should be injected via environment variables or a secrets manager (HashiCorp Vault, AWS Secrets Manager). If the secret leaks an attacker can forge arbitrary tokens. Regular rotation mitigates the impact. I would also set up monitoring for unusual token issuance patterns and alert on anomalies.

---

## Round 5: Summary (5 min)

**Interviewer:** Summarize the critical design decisions.

**Candidate:** (1) Two-tier token architecture (access + refresh) balances security with user experience. (2) Refresh token rotation with reuse detection detects token theft. (3) HMAC simplicity vs RSA/ECDSA flexibility choose based on architecture. (4) Constant-time comparison prevents timing attacks. (5) Clock skew tolerance avoids false rejections. (6) Redis-backed persistence for session state survives restarts. The most important principle is defense in depth: even if one layer fails the rotation and reuse detection provide additional protection.
