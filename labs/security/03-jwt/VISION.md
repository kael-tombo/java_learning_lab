# VISION — JWT: Compact, Verifiable, and Easy to Misuse
> Where this lab takes you: from "three base64 segments" to owning the full key/algorithm/claim lifecycle of stateless tokens.

## The Arc
1. **Anatomy** — JWS vs JWE, header/payload/signature, what is and is not encrypted.
2. **Algorithms** — HMAC vs RSA vs EC; why the `alg` header must never be trusted blindly.
3. **Verification discipline** — signature, then `exp`/`nbf`/`iss`/`aud`, then clock skew.
4. **Lifecycles** — expiry, refresh, rotation, and the revocation trade-off of statelessness.
5. **Attack surface** — `alg: none`, algorithm confusion, `kid` injection, claim over-granting.

## Milestones (checkable)
- [ ] M1: hand-decode a token and compute the signature over `header.payload` yourself.
- [ ] M2: reproduce `alg: none` and RSA→HMAC algorithm confusion against a naive verifier.
- [ ] M3: build a verifier that pins one algorithm and checks `iss` + `aud` before trusting claims.
- [ ] M4: implement key rotation via `kid` + JWKS with an overlap window.
- [ ] M5: explain the stateless revocation problem and implement a revocation-list workaround.

## Core Competencies
- JWT/JWS/JWE/JWT distinction and where a claim would be exposed in transit.
- Key-type selection: symmetric for single-service, asymmetric once a second party verifies.
- Clock skew, TTL budgeting, and refresh-token design that limits replay value.
- Reading a token in an incident and deciding whether it was signed, forged, or mis-scoped.

## Anti-Goals
- Putting sensitive data in a payload and calling it "encrypted".
- Accepting the token's declared algorithm as the algorithm to use.
- Long-lived access tokens to make revocation "unnecessary".

## Interview Lens
- "Your API accepts tokens signed with the public key as an HMAC secret — why is that fatal?"
- "How do you revoke a stateless JWT before it expires?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: sign, verify, and tamper with tokens by hand.
- Wk2 QUIZ/FLASHCARDS to 90%+; write the naive verifier, then attack it.
- Wk3 MINI_PROJECT: hardened verifier + JWKS rotation.
- Wk4 REAL_WORLD_PROJECT: rotation procedure under load + compromise playbook.

## Done = You Can
- Ship a JWT validator that an external auditor can trace line by line, and
  demonstrate the three classic JWT attacks failing against it.
