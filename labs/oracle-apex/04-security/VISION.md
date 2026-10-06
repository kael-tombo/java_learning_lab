# Lab 04: APEX Security — VISION

## Where this lab takes you
From local passwords with no audit to corporate SSO with fail-closed claim
mapping, secure secret storage, RP-initiated logout, and OWASP evidence.

## The Arc
1. **Four layers** — authentication, authorisation, session, data scope.
2. **Scheme choice** — driven by IdP availability and compliance, not fashion.
3. **OIDC flow** — what an `id_token` proves versus an `access_token`.
4. **Claim mapping** — fail closed; provisioning is explicit.
5. **Secrets** — scheme configuration, never application source.
6. **Logout** — RP-initiated, so the IdP session also ends.
7. **Session state** — minimal, no credentials, CSRF retained.
8. **OWASP** — evidence per item, defaults separated from your work.

## Milestones (checkable)
- [ ] M1: Draw the four layers and place 10 controls in the correct layer.
- [ ] M2: Build the scheme comparison on the four stated criteria.
- [ ] M3: Register the app and configure the scheme from IdP metadata.
- [ ] M4: Map claims and test with an unmapped subject; confirm denial.
- [ ] M5: Search the application export and confirm no secret is present.
- [ ] M6: Configure RP-initiated logout and confirm re-authentication is required.
- [ ] M7: Audit session state and remove anything sensitive.
- [ ] M8: Produce the OWASP evidence pack with a per-item entry.

## Anti-Goals
- Treating authentication as the whole security model.
- Defaulting an unmapped subject to a privileged account.
- Using the wrong issuer or JWKS endpoint.
- Pasting a client secret into a page process.
- Application logout only.
- Disabling CSRF to make a form work.
- Bulk PII in session state.
- Claiming OWASP compliance with no evidence.

## The one-sentence thesis
SSO removes the password problem but adds new ones — fail closed on an unmapped
subject, keep the secret in scheme configuration, and end the session at the IdP
or "single sign-on" becomes an unattended-access weakness.