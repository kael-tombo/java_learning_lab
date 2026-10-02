# OAuth2 & OIDC — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: Why is the OAuth2 Implicit Flow deprecated, and what threat does it enable?

**Answer**: Implicit flow returns access token directly in the URL fragment (#access_token=...). Tokens leak via browser history, Referer headers, and logs. No client authentication possible (public clients can't store secrets).

**Threat-Model Reasoning**: In the browser threat model, URL fragments are accessible to any JavaScript on the page (XSS), logged by analytics, and sent in Referer headers to third parties. An attacker who compromises a third-party script or reads logs obtains valid access tokens. Authorization Code + PKCE replaces it: code is exchanged via backend (token never in browser), PKCE prevents code interception.

---

### Q2: How does PKCE (Proof Key for Code Exchange) prevent authorization code interception attacks?

**Answer**: Client generates random `code_verifier`, sends `code_challenge = SHA256(code_verifier)` in auth request. Token exchange requires `code_verifier`. Attacker who intercepts `code` cannot exchange it without `code_verifier`.

**Threat-Model Reasoning**: Threat model: attacker intercepts authorization code via malicious app registration (custom scheme), XSS stealing redirect URL, or network sniffing (if redirect URI uses HTTP). Without PKCE, intercepted code → token. With PKCE, code alone is useless; verifier never leaves client. PKCE binds the code to the specific client instance that initiated the flow.

---

### Q3: What JWT validation steps are mandatory, and what attack does skipping each enable?

**Answer**: 
1. **Signature verification** — prevents forgery (algorithm confusion, none alg, key confusion)
2. **exp (expiration)** — prevents replay of expired tokens
3. **iss (issuer)** — prevents token substitution from different auth server
4. **aud (audience)** — prevents token reuse across services (confused deputy)
5. **nbf (not before)** — prevents early use
6. **jti (JWT ID) + replay cache** — prevents replay within validity window

**Threat-Model Reasoning**: Each claim addresses a specific threat. Missing `aud` allows token minted for Service A to access Service B (confused deputy). Missing `iss` allows tokens from compromised/rogue auth server. Missing signature verification allows `alg: none` or key confusion (RSA vs HS256) attacks. All claims must be validated *before* trusting any token content.

---

### Q4: Explain the "algorithm confusion" attack (RSA vs HS256) and how to prevent it.

**Answer**: Attacker changes JWT header from `"alg":"RS256"` to `"alg":"HS256"`. If server uses RSA public key as HMAC secret (treating public key bytes as symmetric key), attacker signs with the known public key. Server verifies using same public key as HMAC key → validation passes.

**Threat-Model Reasoning**: The attack exploits type confusion: the verification algorithm is chosen by the *token*, not the *application*. Prevention: 1) Explicitly configure expected algorithm(s) per key, never read `alg` from token. 2) Use separate key objects for RSA vs HMAC. 3) Reject tokens with unexpected `alg`. 4) Use libraries that enforce this (e.g., `jose4j`, `nimbus-jose-jwt` with strict config).

---

### Q5: Why must refresh tokens be rotated, and what threat does rotation mitigate?

**Answer**: Refresh tokens are long-lived (days/weeks). If stolen (XSS, log leak, DB breach), attacker gets persistent access. Rotation: each use invalidates old token, issues new one. Stolen token becomes useless after legitimate client uses it.

**Threat-Model Reasoning**: Threat: attacker steals refresh token (via XSS, compromised client, backup). Without rotation, attacker maintains access indefinitely. With rotation, legitimate client's next use revokes attacker's token (detecting compromise). Rotation + theft detection (simultaneous use of same token) enables revocation alerts. Store refresh tokens in HTTP-only cookies or secure enclaves, never localStorage.

---

### Q6: What is the difference between OIDC ID Token and Access Token, and why must you not use ID Token for API authorization?

**Answer**: 
- **ID Token**: JWT for *authentication* (proves user identity). Contains `sub`, `name`, `email`. Audience = client_id. Short-lived.
- **Access Token**: Opaque or JWT for *authorization* (grants API access). Audience = resource server (API). Contains scopes/permissions.

**Threat-Model Reasoning**: Using ID Token for API auth breaks audience validation: API would accept tokens issued for *any* client of the same auth server. ID Tokens lack scopes/permissions. An attacker who obtains an ID Token for a low-privilege client could access high-privilege APIs if the API incorrectly validates ID Tokens. Always validate `aud` matches your API identifier.

---

### Q7: How does the OIDC Discovery endpoint (`/.well-known/openid-configuration`) enable secure integration, and what threat does it mitigate?

**Answer**: Discovery returns JSON with `authorization_endpoint`, `token_endpoint`, `jwks_uri`, `issuer`, supported scopes/claims. Clients fetch this at startup instead of hardcoding endpoints.

**Threat-Model Reasoning**: Mitigates: 1) Hardcoded endpoint drift (auth server changes, client breaks). 2) Phishing via fake auth server (client validates `issuer` matches discovered config). 3) JWKS rotation (client auto-fetches new keys). Threat: if discovery is poisoned (DNS hijack, compromised auth server), client trusts attacker's endpoints. Mitigation: pin `issuer` and/or `jwks_uri` at deploy time, validate TLS.

---

### Q8: What is the "confused deputy" problem in OAuth2, and how does the `aud` claim solve it?

**Answer**: Service A (deputy) accepts token intended for Service B, performs privileged action on behalf of attacker. Example: attacker gets token for `aud:calendar`, sends to `aud:email` service; email service accepts it and reads emails.

**Threat-Model Reasoning**: Threat model: attacker obtains valid token for Service A (legitimately or via compromise), presents it to Service B. Without `aud` validation, Service B cannot distinguish "token for me" vs "token for someone else". Solution: every resource server validates `aud` equals its own identifier. Use distinct audiences per service, not a shared wildcard.

---

### Q9: Why is storing tokens in `localStorage` dangerous, and what is the secure alternative?

**Answer**: `localStorage` is accessible to any JavaScript on the origin (XSS). Any third-party script, compromised dependency, or reflected XSS steals tokens. Secure alternative: HTTP-only, Secure, SameSite=Strict cookies (for browser apps) or platform secure storage (Keychain/Keystore for mobile).

**Threat-Model Reasoning**: Browser threat model assumes XSS is inevitable (supply chain, dependencies, human error). `localStorage` has no XSS protection. HTTP-only cookies are inaccessible to JavaScript. SameSite=Strict prevents CSRF. For SPAs: use short-lived access tokens in memory (JavaScript variable), refresh token in HTTP-only cookie. For mobile: use OS keychain with biometric gating.

---

### Q10: Explain the token revocation problem in stateless JWT systems and solutions.

**Answer**: JWTs are self-contained; no server-side state to revoke. Once issued, valid until `exp`. Solutions: 1) Short `exp` (5-15 min) + refresh token rotation (revoke refresh token). 2) Token blocklist (denylist) checked at validation — adds state. 3) Push-based revocation (events to resource servers). 4) Opaque tokens with introspection endpoint (RFC 7662) — server-side state.

**Threat-Model Reasoning**: Threat: user logs out, token stolen, privilege change, or account compromise. Without revocation, token remains valid. Short expiry limits window but hurts UX. Refresh token rotation is best balance: access token short (stateless), refresh token stateful (revocable). Blocklist scales poorly. Introspection adds latency but full control. Choose based on risk profile.