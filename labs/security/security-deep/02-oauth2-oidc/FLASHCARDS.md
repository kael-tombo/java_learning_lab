# OAuth2 & OIDC — Flashcards

---

## OAuth2 Fundamentals

**Q: What are the four OAuth2 roles?**
**A:** Resource Owner (user), Client (app), Authorization Server (issues tokens), Resource Server (API).

---

**Q: What are the main OAuth2 grant types and when to use each?**
**A:**
- Authorization Code (+ PKCE): Web apps, SPAs, mobile — user involved, most secure
- Client Credentials: Machine-to-machine, no user — service accounts
- Refresh Token: Long-lived token to obtain new access tokens
- Device Code: TVs, CLI, limited input devices
- Implicit (deprecated): Legacy SPA flow, replaced by Auth Code + PKCE
- Resource Owner Password Credentials (deprecated): Legacy, never use

---

**Q: What is PKCE and why is it required for public clients?**
**A:** Proof Key for Code Exchange. Client generates `code_verifier` (random), sends `code_challenge = SHA256(verifier)` in auth request. Token exchange requires `verifier`. Prevents code interception attacks. Required for SPAs/mobile (no client secret).

---

**Q: What is the difference between authorization code and access token?**
**A:** Auth code: short-lived (10 min), single-use, exchanged for tokens. Access token: used to call APIs, longer-lived (15-60 min), bearer token.

---

**Q: What is a confidential vs public client?**
**A:** Confidential: can store secret (backend server). Public: cannot store secret (SPA, mobile, desktop). Public clients MUST use PKCE.

---

## JWT & Token Validation

**Q: What are the three parts of a JWT?**
**A:** Header (alg, typ), Payload (claims: sub, exp, iss, aud, iat, nbf, jti, custom), Signature (alg(header.payload, secret/private_key)).

---

**Q: What claims MUST be validated on every JWT?**
**A:** 1) Signature (alg matches expected, key matches issuer) 2) exp (not expired) 3) iss (expected issuer) 4) aud (expected audience) 5) nbf (not before) 6) iat (not too far in future)

---

**Q: What is the "alg: none" attack?**
**A:** Attacker sets header `"alg":"none"`, omits signature. Vulnerable libraries accept unsigned tokens. Fix: reject `none` algorithm, require explicit alg allowlist.

---

**Q: What is the RSA/HMAC key confusion attack?**
**A:** Token header says `"alg":"HS256"` but server expects RS256. Server uses RSA public key as HMAC secret. Attacker signs with public key. Fix: configure expected alg per key, never read alg from token.

---

**Q: What is the `aud` claim and why is it critical?**
**A:** Audience — identifies intended recipient. Prevents confused deputy: token for Service A rejected by Service B. Every resource server must validate `aud` matches its identifier.

---

**Q: What is the `jti` claim used for?**
**A:** JWT ID — unique identifier for token. Enables replay detection (blocklist) and token revocation.

---

## OpenID Connect

**Q: What does OIDC add to OAuth2?**
**A:** ID Token (JWT with user identity claims), UserInfo endpoint, Discovery endpoint, standardized scopes (openid, profile, email), session management.

---

**Q: What is the difference between ID Token and Access Token?**
**A:** ID Token: proves authentication, audience=client_id, contains user claims (sub, name, email). Access Token: authorizes API access, audience=resource server, contains scopes/permissions.

---

**Q: What is the OIDC Discovery endpoint?**
**A:** `/.well-known/openid-configuration` — returns JSON with auth/token/JWKS endpoints, issuer, supported features. Enables dynamic configuration.

---

**Q: What are standard OIDC scopes?**
**A:** `openid` (required), `profile` (name, picture), `email` (email, email_verified), `address`, `phone`.

---

**Q: What is the UserInfo endpoint?**
**A:** Protected resource returning user claims (sub, name, email, etc.). Accessed with access token (scope `openid`). Alternative to putting all claims in ID Token.

---

## Token Security

**Q: Why use short-lived access tokens (15-60 min)?**
**A:** Limits damage window if token stolen. Combine with refresh tokens for long sessions.

---

**Q: What is refresh token rotation?**
**A:** Each refresh token use invalidates the old token and issues a new one. Detects theft: if stolen token used, legitimate client's next use fails → alert/revoke.

---

**Q: How to detect refresh token theft?**
**A:** Rotation + simultaneous use detection. If same refresh token used twice, both sessions revoked, user alerted.

---

**Q: Where to store tokens in browser?**
**A:** Access token: in memory (JS variable). Refresh token: HTTP-only, Secure, SameSite=Strict cookie. Never localStorage/sessionStorage (XSS accessible).

---

**Q: Where to store tokens in mobile apps?**
**A:** iOS Keychain / Android Keystore with biometric/device credential gating. Never SharedPreferences/Keychain without protection.

---

**Q: What is token introspection (RFC 7662)?**
**A:** Resource server calls auth server `/introspect` endpoint with token → returns active, scopes, exp, client_id. For opaque tokens. Adds latency, enables full revocation.

---

## Threat Modeling Flashcards

**Q: What threat does missing PKCE enable?**
**A:** Authorization code interception → token theft via custom URL scheme, XSS, or network sniffing.

---

**Q: What threat does missing `aud` validation enable?**
**A:** Confused deputy — token for Service A accepted by Service B → privilege escalation.

---

**Q: What threat does `alg: none` enable?**
**A:** Unsigned token forgery — attacker creates arbitrary claims, no signature needed.

---

**Q: What threat does RSA/HMAC confusion enable?**
**A:** Attacker signs with public key, server verifies with same public key as HMAC secret → valid signature.

---

**Q: What threat does long-lived access token enable?**
**A:** Extended damage window if stolen — attacker accesses API until expiry.

---

**Q: What threat does refresh token without rotation enable?**
**A:** Persistent access after theft — no detection, no revocation.

---

**Q: What threat does localStorage token storage enable?**
**A:** XSS → immediate token theft — any script on page reads tokens.

---

**Q: What threat does missing `iss` validation enable?**
**A:** Token substitution — token from rogue/compromised auth server accepted.

---

**Q: What threat does missing `exp` validation enable?**
**A:** Replay of expired tokens — indefinite access.

---

**Q: What threat does missing Discovery endpoint validation enable?**
**A:** Phishing via fake auth server — client redirects to attacker-controlled endpoints.