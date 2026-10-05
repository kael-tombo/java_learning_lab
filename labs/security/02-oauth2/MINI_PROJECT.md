# OAuth 2.0 - MINI PROJECT

## Project: AuthForge — a minimal authorization server with two grants and real token hygiene

Implement a self-contained authorization server in Java 21 using Spring Boot. No external IdP.
It must support **authorization code + PKCE** and **client credentials**, issue scoped tokens,
and rotate refresh tokens with replay detection.

### Architecture

```
Browser/App ──GET /authorize?client_id&redirect_uri&scope&state&code_challenge──> AuthForge
AuthForge: authenticate user, CONSENT screen, store one-time code (hashed) + PKCE challenge
        └──302 redirect_uri?code=...&state=...──> Client
Client ──POST /token  code + code_verifier──> AuthForge
        └─> verify PKCE (S256) ──> access_token (JWT, 5 min) + refresh_token (opaque, rotated)
Client ──GET /resource with Bearer──> ResourceServer ──> scope check ──> 200/403
```

### Implementation

```java
@Service
public class TokenService {
    private final Map<String, RefreshRecord> refreshStore = new ConcurrentHashMap<>();
    record RefreshRecord(String clientId, String scope, String familyId,
                         Instant issuedAt, boolean used) {}

    public TokenResponse issueFromCode(AuthCode code, String codeVerifier) {
        // PKCE S256: BASE64URL(SHA256(verifier)) must equal the stored challenge
        String derived = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(sha256(codeVerifier.getBytes(US_ASCII)));
        if (!MessageDigest.isEqual(derived.getBytes(US_ASCII),
                                   code.codeChallenge().getBytes(US_ASCII))) {
            audit.warn("PKCE_MISMATCH", code.clientId());
            throw new InvalidGrantException("code_verifier mismatch"); // consume the code anyway
        }
        codeStore.remove(code.value());   // single use
        String refresh = opaque(48);
        refreshStore.put(refresh, new RefreshRecord(code.clientId(), code.scope(),
                code.familyId(), Instant.now(), false));
        return new TokenResponse(signAccessToken(code.clientId(), code.scope(), Duration.ofMinutes(5)), refresh);
    }

    public TokenResponse rotate(String presentedRefresh) {
        RefreshRecord rec = refreshStore.get(presentedRefresh);
        if (rec == null) throw new InvalidGrantException("unknown refresh token");
        if (rec.used()) {
            // Replay of an already-rotated token => assume theft, nuke the whole family.
            refreshStore.values().removeIf(r -> r.familyId().equals(rec.familyId()));
            audit.warn("REFRESH_REPLAY", rec.clientId(), rec.familyId());
            throw new InvalidGrantException("refresh token reuse detected");
        }
        refreshStore.put(presentedRefresh, new RefreshRecord(rec.clientId(), rec.scope(),
                rec.familyId(), rec.issuedAt(), true));   // mark used, keep for replay detection
        String next = opaque(48);
        refreshStore.put(next, new RefreshRecord(rec.clientId(), rec.scope(),
                rec.familyId(), Instant.now(), false));
        return new TokenResponse(signAccessToken(rec.clientId(), rec.scope(), Duration.ofMinutes(5)), next);
    }
}
```

The authorization endpoint is where most real breaches live, so keep the guard rails explicit:

```java
@GetMapping("/authorize")
public ResponseEntity<Void> authorize(HttpServletRequest req, @RequestParam String client_id,
        @RequestParam String redirect_uri, @RequestParam String response_type,
        @RequestParam String scope, @RequestParam(required = false) String state,
        @RequestParam(required = false) String code_challenge,
        @RequestParam(required = false) String code_challenge_method) {
    Client client = clients.requireRegistered(client_id);
    if (!client.registeredRedirectUris().contains(redirect_uri)) {   // EXACT match
        throw new BadRequest("unregistered redirect_uri");           // do NOT redirect the error
    }
    if (!"code".equals(response_type)) throw new BadRequest("unsupported response_type");
    if (code_challenge == null) throw new BadRequest("PKCE required"); // public clients must
    if (!"S256".equals(code_challenge_method)) throw new BadRequest("plain PKCE not allowed");
    String code = oneTimeCode(client, redirect_uri, scope, code_challenge);
    audit.info("AUTHORIZE_GRANT", client_id, scope);
    return redirect(successUri(redirect_uri, Map.of("code", code, "state", state)));
}
```

### Test It

```java
@Test void pkcePlainMethodIsRejected() { assertThrows(BadRequest.class, () -> auth.authorize(p("plain"))); }

@Test void codeIsSingleUse() {
    String c = newCode();
    token.issueFromCode(codeStore.get(c), "verifier");
    assertThrows(InvalidGrantException.class, () -> token.issueFromCode(codeStore.get(c), "verifier"));
}

@Test void refreshReuseKillsFamily() {
    var t1 = token.rotate(firstRefresh);
    assertThrows(InvalidGrantException.class, () -> token.rotate(firstRefresh));
    assertThrows(InvalidGrantException.class, () -> token.rotate(t1.refreshToken())); // collateral
}

@Test void insufficientScopeIs403() {
    assertEquals(403, resource.call(token("read:orders"), "/orders").status());
}
```

## Deliverables

- [ ] `/authorize` with exact redirect_uri match, mandatory `state`, mandatory PKCE S256
- [ ] `/token` implementing `authorization_code` and `client_credentials`
- [ ] Scoped access tokens (JWT, ~5 min TTL) and opaque refresh tokens
- [ ] Refresh rotation with reuse detection and family revocation
- [ ] Consent screen logging grant + scope + client to the audit log
- [ ] 403 + `insufficient_scope` handling in the resource server
- [ ] JUnit 5 tests: PKCE mismatch, code replay, refresh replay, scope enforcement
