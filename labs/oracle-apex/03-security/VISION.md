# Lab 03: Security (RBAC + Custom Auth + Audit) — Vision

## Where this lab takes you
From an open demo application to a financial-services APEX app under LDAP, with
a four-level role hierarchy, branch-scoped row security, feature-level
authorisation, full audit, 15-minute sessions, and OWASP-verified controls.

## The Arc
1. **Authentication** — how a user becomes a session.
2. **LDAP with fallback** — directory authentication and local break-glass.
3. **Role hierarchy** — ADMIN > MANAGER > ANALYST > VIEWER.
4. **Row security** — branch scoping so a user sees only their data.
5. **Feature authorisation** — capability checks, not just page access.
6. **Session discipline** — 15-minute timeout, secure cookies, session state.
7. **Password handling** — PBKDF2, lockout, no plaintext.
8. **Audit** — who did what, tamper-evident, retained.
9. **OWASP** — verify against the top 10 rather than assuming.

## Milestones (checkable)
- [ ] M1: Build a custom login with LDAP and a documented local fallback.
- [ ] M2: Define the four roles and prove each sees a different capability set.
- [ ] M3: Implement branch-scoped row security and test cross-branch denial.
- [ ] M4: Add feature-level authorisation beyond page access.
- [ ] M5: Enforce a 15-minute session timeout and verify it.
- [ ] M6: Implement PBKDF2 hashing and 5-strike lockout.
- [ ] M7: Build an audit trail capturing authentication and data access.
- [ ] M8: Walk the OWASP Top 10 and evidence the control for each.

## Anti-Goals
- Relying on page-level access where the risk is data-level.
- Leaving a local authentication path undocumented or unlimited in attempts.
- Storing passwords hashed with a fast algorithm such as plain SHA-256.
- Logging sensitive values into the audit trail.
- Assuming a session timeout setting is the same as an enforced timeout.

## The one-sentence thesis
APEX security is layered — authentication decides who you are, authorisation
decides what you can reach, row security decides what you can see, and audit
proves it; skipping any layer leaves the others undefended.