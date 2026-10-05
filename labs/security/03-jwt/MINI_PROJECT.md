# JWT - MINI PROJECT

## Project: TokenLab — sign, verify, and deliberately break a JWT implementation

Build a small library that issues tokens, verifies them correctly, and includes an
attacker harness proving `alg: none` and algorithm confusion are dead against it.

### Architecture

```
issue(claims)  ──> header{alg,typ,kid} + payload{iss,aud,sub,exp,iat,jti,scope}
                     └─> base64url(header) + "." + base64url(payload)
                          └─> RSA-SHA256 sign with PRIVATE key ──> token

verify(token)  ──> 1) parse header  2) PIN alg = RS256 (ignore token's claim)
                     3) reject "none"  4) fetch public key by kid (JWKS, cached)
                     5) verify signature  6) check exp/nbf/iss/aud with skew
                     7) return typed claims
```

### Implementation

```java
public final class JwtService {
    private static final String PINNED_ALG = "RS256";
    private final PrivateKey privateKey;
    private final PublicKey publicKey;
    private final Map<String, JWK> jwks = new ConcurrentHashMap<>();
    private final Duration skew = Duration.ofSeconds(30);

    public String issue(String subject, String audience, List<String> scopes, Duration ttl) {
        Instant now = Instant.now();
        String header = b64(objectMapper.writeValueAsBytes(
                Map.of("alg", PINNED_ALG, "typ", "JWT", "kid", currentKid())));
        String payload = b64(objectMapper.writeValueAsBytes(Map.of(
                "iss", "https://tokenlab.local", "aud", audience, "sub", subject,
                "iat", now.getEpochSecond(), "nbf", now.getEpochSecond(),
                "exp", now.plus(ttl).getEpochSecond(),
                "jti", UUID.randomUUID().toString(),
                "scope", String.join(" ", scopes))));
        SignatureSigner signer = Signature.getInstance("SHA256withRSA");
        signer.initSign(privateKey);
        signer.update((header + "." + payload).getBytes(US_ASCII));
        return header + "." + payload + "." + b64(signer.sign());
    }

    public Claims verify(String token, String expectedAudience) {
        String[] parts = token.split("\\.");
        if (parts.length != 3) throw new JwtException("malformed token");

        JsonNode header = parse(parts[0]);
        String alg = header.path("alg").asText();
        // 1) Never trust the token's alg. If it is not what we pinned, it is an attack.
        if (!PINNED_ALG.equals(alg)) throw new JwtException("unexpected alg: " + alg);
        if ("none".equalsIgnoreCase(alg)) throw new JwtException("alg=none rejected");

        // 2) Key comes from OUR JWKS by kid, never from the token body.
        PublicKey key = jwks.get(header.path("kid").asText());
        if (key == null) throw new JwtException("unknown kid -> refresh JWKS and retry once");

        SignatureVerifier v = Signature.getInstance("SHA256withRSA");
        v.initVerify(key);
        v.update((parts[0] + "." + parts[1]).getBytes(US_ASCII));
        if (!v.verify(decode(parts[2]))) throw new JwtException("bad signature");

        Claims c = read(parse(parts[1]));
        Instant now = Instant.now();
        if (c.exp().isBefore(now.minus(skew))) throw new JwtException("expired");
        if (c.nbf().isAfter(now.plus(skew)))   throw new JwtException("not yet valid");
        if (!"https://tokenlab.local".equals(c.iss())) throw new JwtException("bad iss");
        if (!c.aud().contains(expectedAudience)) throw new JwtException("bad aud");
        return c;
    }
}
```

The attacker harness is a deliverable, not a joke — it is your regression suite:

```java
class JwtAttacker {
    /** alg=none: strip the signature, hope the server skips verification. */
    static String algNone(String token) {
        String[] p = token.split("\\.");
        Map<String, Object> h = new LinkedHashMap<>();
        h.put("alg", "none"); h.put("typ", "JWT");
        return b64(toJson(h)) + "." + p[1] + ".";
    }

    /** Algorithm confusion: sign HS256 using the RSA *public* key bytes as the HMAC secret. */
    static String algConfusion(String token, PublicKey victimPublicKey) {
        String[] p = token.split("\\.");
        Map<String, Object> h = Map.of("alg", "HS256", "typ", "JWT");
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(victimPublicKey.getEncoded(), "HmacSHA256"));
        return b64(toJson(h)) + "." + p[1] + "." + b64(mac.doFinal((p[0] + "." + p[1]).getBytes(US_ASCII)));
    }
}
```

### Test It

```java
@Test void algNoneIsRejected()  { assertThrows(JwtException.class, () -> svc.verify(JwtAttacker.algNone(t), "api")); }
@Test void algConfusionIsRejected() { assertThrows(JwtException.class, () -> svc.verify(JwtAttacker.algConfusion(t, pub), "api")); }
@Test void tamperedPayloadIsRejected() {
    String[] p = t.split("\\.");
    String evil = p[0] + "." + b64("{\"sub\":\"admin\"}".getBytes()) + "." + p[2];
    assertThrows(JwtException.class, () -> svc.verify(evil, "api"));
}
@Test void wrongAudienceIsRejected() { assertThrows(JwtException.class, () -> svc.verify(t, "other-api")); }
@Test void expiredTokenIsRejected()   { /* issue ttl=1s, sleep 1.5s, assert thrown */ }
```

## Deliverables

- [ ] Issue tokens with `iss`, `aud`, `sub`, `iat`, `nbf`, `exp`, `jti`, `scope`, `kid`
- [ ] Verifier that pins the algorithm and validates every registered claim
- [ ] JWKS endpoint + cache with refresh-on-unknown-kid
- [ ] Attacker harness: `alg=none`, algorithm confusion, payload tampering, claim over-grant
- [ ] Clock-skew tolerance configured explicitly (not accidental)
- [ ] JUnit 5 tests asserting every attack is rejected
- [ ] README documenting what is signed, what is encrypted, and what is only base64
