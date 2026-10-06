# Lab 05: APEX Security — Mini Project

## Goal
Configure a multi-layer APEX security model — OIDC authentication, an
authorisation scheme, row-level scoping, and session protection — in 90 minutes.

## Requirements
- R1: The four-layer model drawn with each control placed.
- R2: A comparison of four authentication schemes on stated criteria.
- R3: An OIDC authentication scheme configured against a test IdP.
- R4: An authorisation scheme granting a role access to a defined page group.
- R5: Row-level scoping applied to all data regions.
- R6: Session state inventory with sensitive values removed.
- R7: CSRF protection verified active on every page.
- R8: An OWASP review with evidence recorded per item.

## Steps
1. Draw the four-layer model and label each control.
2. Build the scheme comparison table on the four criteria.
3. Configure the OIDC scheme: issuer, endpoints, and claim mapping.
4. Test the login flow and confirm the returned user is mapped correctly.
5. Build the authorisation scheme and grant a role to a page group.
6. Apply row-level scoping to every region.
7. Dump session state; identify and remove anything sensitive.
8. Attempt a cross-site request and confirm it is rejected.
9. Complete the OWASP review with evidence for each item.

## Acceptance criteria
- OIDC login completes and the session user is the expected identity.
- An unauthorised role cannot reach a page it is not granted.
- Regions are scoped; a user sees only their own data.
- Session state contains no credentials or sensitive values.
- CSRF is active and rejects a forged request.
- Every OWASP item has recorded evidence.

## Stretch
- Demonstrate what happens when a claim maps to no known user.
- Break the IdP deliberately and observe the application's failure mode.