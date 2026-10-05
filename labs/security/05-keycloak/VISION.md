# VISION — Keycloak: Identity Provider as Infrastructure
> Where this lab takes you: from "run the container" to operating a realm whose misconfiguration is a company-wide outage.

## The Arc
1. **Model** — realms, clients, users, groups, roles, and the identity brokering tree.
2. **Protocols** — OIDC endpoints, OAuth 2 flows, SAML 2.0, and the token contents.
3. **Application wiring** — `spring-security-oauth2-resource-server` + JWKS, or the legacy adapter.
4. **Operations** — realms as config, token lifespans, key rotation, admin API automation.
5. **Federation & scale** — LDAP/social brokering, identity providers, HA, custom claims.

## Milestones (checkable)
- [ ] M1: model a company of 3 business units as 1 realm with groups vs 3 realms, and defend the choice.
- [ ] M2: obtain a token via authorization code + PKCE and decode every claim.
- [ ] M3: wire a Spring Boot resource server to Keycloak with zero hardcoded secrets.
- [ ] M4: script realm/client/role provisioning through the admin REST API in CI.
- [ ] M5: explain why an audience mapper is required when a non-Keycloak app verifies your tokens.

## Core Competencies
- Client configuration: public vs confidential, redirect URIs, service-account roles.
- Realm/client/role export-import as version-controlled infrastructure.
- Protocol bridging (OIDC ↔ SAML) and the trust consequences of brokering.
- Token customization via protocol mappers without forking Keycloak.

## Anti-Goals
- Hand-editing a realm in the admin UI and never exporting it.
- Putting application roles directly in the realm's `realm-management` client.
- Copying the `master` realm's patterns into production.

## Interview Lens
- "When do you add a realm versus a group?" "How do you rotate signing keys without downtime?"
- "Our app is a SAML app but everything else is OIDC — what breaks?"

## 30-Day Plan
- Wk1 THEORY + EXERCISES: run Keycloak via Testcontainers, get a token.
- Wk2 QUIZ/FLASHCARDS to 90%+; wire the resource server and read all claims.
- Wk3 MINI_PROJECT: automated realm provisioning.
- Wk4 REAL_WORLD_PROJECT: HA, federation, and an onboarding/offboarding drill.

## Done = You Can
- Stand up a Keycloak deployment, configure it entirely as code, and debug a
  token-rejection failure from the claim that is wrong.
