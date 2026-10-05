# VISION — SAML 2.0: Federated Identity the Enterprise Way
> Where this lab takes you: from "the enterprise uses SAML" to building an SP that survives real-world IdPs and metadata rotation.

## The Arc
1. **Model** — IdP vs SP, assertions vs SAML, the trust relationship, and why SAML still exists.
2. **Flows** — SP-initiated and IdP-initiated SSO, SLO, artifact vs POST binding.
3. **Assertions** — `AuthnStatement`, attribute statements, conditions (audience, time), and
   why signature validation must be all-or-nothing.
4. **Security** — signature wrapping, XML external entity attacks, assertion replay, clock skew.
5. **Operations** — metadata exchange, certificate rotation, multi-IdP federation, and
   testing against a real IdP.

## Milestones (checkable)
- [ ] M1: capture and read a full SAML response, identifying every signed element.
- [ ] M2: explain why an unsigned attribute assertion is a privilege escalation.
- [ ] M3: defend against signature wrapping and show the naive validator failing.
- [ ] M4: implement SP-initiated SSO plus SLO against Keycloak.
- [ ] M5: rotate signing certificates with zero downtime using metadata dual-publish.

## Core Competencies
- Binding types (POST, Redirect, Artifact) and what each requires of your endpoint.
- Signature trust: which XML elements must be signed, and validating the signature over the
  correct reference rather than any signature found in the document.
- IdP metadata as configuration: fetching, parsing, caching, and pinning.
- IdP-initiated SSO mapping: turning an unsolicited assertion into an authenticated session.

## Anti-Goals
- Trusting SAML attributes without verifying the assertion signature.
- Disabling signature validation "because our IdP does not sign the response".
- Hardcoding an IdP certificate instead of honouring metadata rotation.

## Interview Lens
- "What is a signature wrapping attack and how do you prevent it?"
- "When would you choose SAML over OIDC for a new integration?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: run Keycloak as an IdP, build a minimal SP.
- Wk2 QUIZ/FLASHCARDS to 90%+; dissect a captured response element by element.
- Wk3 MINI_PROJECT with SSO, SLO, and metadata-driven config.
- Wk4 REAL_WORLD_PROJECT: multi-IdP federation with rotation and a capture harness.

## Done = You Can
- Integrate with an enterprise IdP you do not control, and debug an assertion by
  reading the XML rather than by guessing at headers.
