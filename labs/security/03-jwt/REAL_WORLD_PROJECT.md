# JWT - REAL WORLD PROJECT

## Project: MeshLink — JWT-secured service mesh for inter-service auth in a Java platform

A platform team owns 40+ Spring Boot services. They need zero-trust service-to-service auth,
human user sessions bridged from an external IdP, and key rotation that does not page anyone
at 3 a.m. Tokens are validated locally (no network hop), which makes the verifier's
correctness the entire security boundary.

### Architecture

```
                 ┌──────────────────────┐
 External IdP ──▶│ Identity Service     │
 (OIDC)          │ - bridges user sess  │
                 │ - mints service tok │
                 └───┬─────────────┬────┘
        JWKS (rotating) │             │ user JWT (aud=user-api)
                     ▼               ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ Orders Service   │   │ Reporting Svc    │
        │ resource server  │   │ resource server  │
        │ - local verify   │   │ - service-to-svc │
        │ - scope→authority│   │   mTLS + JWT     │
        └────────┬─────────┘   └──────────────────┘
                 │ Authorization header only; no cookies, no session store
                 ▼
   Revocation (Redis) + Denylist (Redis) consulted only on jti hit / high-risk routes
```

### Implementation

```java
@Component
class MeshLinkJwtDecoder implements JwtDecoder {   // custom, not the default one
    private final CachedJwks jwks;                   // 5 min TTL, refresh-on-unknown-kid
    private final Set<String> audienceAllowList;
    private final JtiDenylist denylist;

    @Override public Jwt decode(String token) {
        String[] parts = token.split("\\.");
        if (parts.length != 3) throw new BadJwtException("malformed");
        JsonNode header = readTree(decode64(parts[0]));

        String alg = header.path("alg").asText();
        if (!ALLOWED_ALGS.contains(alg)) throw new BadJwtException("alg not allowed: " + alg);

        JWK jwk = jwks.byKid(header.path("kid").asText())
                       .orElseThrow(() -> new BadJwtException("unknown kid"));
        keyRefCache.put(jwk.kid(), jwk.toPublicKey());   // JWK -> PublicKey memoized
        JWSVerifier verifier = JWSVerifier.withSignature(alg, keyRefCache.get(jwk.kid()))
                .build();
        if (!verifier.verify(parts[0] + "." + parts[1], decode64(parts[2])))
            throw new BadJwtException("signature invalid");

        Claims c = readTree(decode64(parts[1]));
        if (c.path("iss").asText().equals("https://idp.example.com") && denylist.contains(c.path("jti").asText())) {
            audit.warn("TOKEN_DENYLISTED", c.path("sub").asText(), c.path("jti").asText());
            throw new BadJwtException("token revoked");   // covers the stateless-revocation gap
        }
        String aud = c.path("aud").asText();
        if (!audienceAllowList.contains(aud)) throw new BadJwtException("aud not allowed");
        return Jwt.withTokenValue(token).header(h -> h.addAll((Map) header)).claim("scope", c.path("scope").asText()).build();
    }

    private static final Set<String> ALLOWED_ALGS = Set.of("RS256", "ES256");
    // NOTE: no "none", no HS* — asymmetric only, because multiple parties verify these tokens.
}
```

Key rotation without downtime, the operationally interesting part:

```java
@Service
class KeyRotationService {
    // 1. publish NEW public key to JWKS, keep OLD public key present
    // 2. wait = max token TTL + clock skew (e.g. 5 min access, 10 min overlap)
    // 3. switch signing to NEW private key
    // 4. wait one full access-token lifetime
    // 5. remove OLD public key from JWKS
    void rotate() {
        KeyPair next = generateEc("P-256");
        jwks.publish(next.publicKey(), kidOf(next));          // step 1
        sleep(Duration.ofMinutes(10));                          // step 2 - old tokens still valid
        active.set(next);                                       // step 3
        scheduledPublish(kidOf(next), ttlPlusSkew());           // step 4/5
    }

    @EventListener
    void onUnknownKid(UnknownKidEvent e) { jwks.invalidate(); } // any unknown kid = force refresh
}
```

### Non-functional requirements

- **Latency**: verification is pure CPU + a cached key map. p95 under 2 ms, zero network calls.
- **Rotation**: automated, zero downtime, quarterly + on-demand (compromise) path.
- **Revocation**: Redis denylist keyed by `jti`, 15 min TTL = access-token lifetime; trade
  statelessness for a bounded revocation window and document it.
- **Observability**: metrics on verification failure reason, unknown-`kid` rate (a probe
  signature for an attacker probing the verifier), algorithm-rejection counts.
- **Blast radius**: `aud` allow-list means a stolen token for another service is useless.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP JSON Web Token Cheat Sheet for Java documents the recommended key-selection and
  validation order, and explicitly warns against accepting the token's `alg` value.
  https://web.archive.org/web/20200125082857/(link removed)
- Spring Security's resource-server JWT reference describes JWKS-based validation and
  `JwtAuthenticationConverter` scope-to-authority mapping.
  https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html

## Deliverables

- [x] Custom `JwtDecoder` with pinned asymmetric algorithms and claim validation order
- [x] JWKS cache with refresh-on-unknown-kid and key-type memoization
- [x] Zero-downtime rotation runbook (5-phase, automated)
- [x] `jti` denylist for bounded revocation, documented as a statelessness trade-off
- [x] Audience allow-list to limit stolen-token blast radius
- [x] Metrics for verification failure reasons and unknown-`kid` probing
- [x] Runbook for token compromise: rotate, denylist, re-issue
