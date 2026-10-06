# Lab 05: APEX Security — Vision

## Where this lab takes you
From APEX's default single-password model to a scheme with corporate SSO,
documented authorisation, protected session state, and OWASP-verified controls.

## The Arc
1. **The model** — authentication, authorisation, session state, as layers.
2. **Authentication schemes** — internal, LDAP, SAML, OIDC, custom.
3. **Choosing one** — SSO, compliance, and operational cost.
4. **Authorisation schemes** — access control at the right granularity.
5. **Session state protection** — what is in the session and who can read it.
6. **Workspace isolation** — schema boundaries as a security control.
7. **CSRF and XSS** — the two that APEX pages inherit by default.
8. **OWASP** — verify, do not assume.

## Milestones (checkable)
- [ ] M1: Draw the four-layer APEX security model and place controls in each.
- [ ] M2: Compare internal, LDAP, SAML, and OIDC schemes on stated criteria.
- [ ] M3: Configure an OIDC scheme with an identity provider.
- [ ] M4: Build an authorisation scheme granting a role to a page group.
- [ ] M5: Inspect session state and remove anything that should not be there.
- [ ] M6: Explain CSRF protection and verify it is active.
- [ ] M7: Walk the OWASP Top 10 with evidence per item.

## Anti-Goals
- Assuming authentication implies authorisation.
- Storing sensitive values in session state because it is convenient.
- Disabling CSRF protection to make a page work.
- Trusting an identity provider claim without validating it maps to a known user.

## The one-sentence thesis
APEX gives you four independent layers — authenticate the person, authorise the
action, scope the data, and protect the session — and most APEX breaches skip
straight from the first to the last.