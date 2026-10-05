# VISION — OAuth 2.0: Delegation, Not Login
> Where this lab takes you: from "grant a token" vocabulary to designing a delegation model that survives a security review.

## The Arc
1. **Problem** — why third-party password sharing is a liability, and what OAuth actually replaces.
2. **Actors & Grants** — resource owner, client, authorization server, resource server; the four grant types.
3. **Flow selection** — auth code + PKCE for user-facing apps, client credentials for machine-to-machine.
4. **Tokens & scopes** — access vs refresh, scope narrowing, opaque vs self-contained, TTL budgets.
5. **Hardening** — state/nonce, redirect URI exactness, refresh rotation, revocation, RFC 9700 guidance.

## Milestones (checkable)
- [ ] M1: draw the authorization code flow with PKCE end-to-end, including the verifier derivation.
- [ ] M2: name the grant type for a native mobile app and justify rejecting the implicit flow.
- [ ] M3: issue a scoped access token and reject an out-of-scope call with 403 + `insufficient_scope`.
- [ ] M4: implement refresh-token rotation and detect replay of a rotated token.
- [ ] M5: explain why `redirect_uri` must be an exact match and what open-redirect enables.

## Core Competencies
- Grant-type selection from client type (browser, SPA, mobile, daemon, service mesh).
- Scope design as a least-privilege vocabulary, not a marketing string.
- Token lifecycle budgeting: access TTL, refresh rotation, revocation propagation.
- Threat modelling the flow: CSRF via missing state, code interception, mix-up attacks.

## Anti-Goals
- Treating OAuth 2.0 as a login protocol (that is OIDC's job) or using it as one.
- Shipping the implicit/`password` grant to anything you did not fully own and control.
- Accepting a prefix or wildcard `redirect_uri` match.

## Interview Lens
- "Why PKCE if we already have a client secret?" "What breaks without a nonce?"
- "How do you revoke an access token you already issued as a self-contained JWT?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: build a working auth code + PKCE flow by hand.
- Wk2 QUIZ/FLASHCARDS to 90%+; add client credentials and scope enforcement.
- Wk3 MINI_PROJECT with refresh rotation and replay detection.
- Wk4 REAL_WORLD_PROJECT: threat-model it against RFC 9700 / OAuth 2.0 Security BCP.

## Done = You Can
- Design, implement, and attack-test an authorization server flow, and defend each
  decision with a spec citation rather than intuition.
