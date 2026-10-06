# Lab 04: APEX Security — Mini Project

## Goal
Configure OIDC SSO for an APEX application with fail-closed claim mapping,
break-glass fallback, and OWASP evidence, in 90 minutes.

## Requirements
- R1: The four-layer model with 10 controls placed.
- R2: A scheme comparison table on the four stated criteria.
- R3: An OIDC authentication scheme configured from IdP metadata.
- R4: A local user directory keyed on the IdP subject claim.
- R5: A mapping process that denies an unmapped subject and logs it.
- R6: Break-glass accounts, limited and rate-limited.
- R7: RP-initiated logout configured and tested.
- R8: An OWASP evidence pack with a per-item entry.

## Steps
1. Draw the four-layer model and place the controls.
2. Build the scheme comparison and justify the OIDC choice.
3. Register the APEX application with the test IdP; note the callback URL.
4. Copy the metadata endpoints and configure the scheme.
5. Create the directory table and provision three test users by `sub`.
6. Log in as each user; confirm the mapping works.
7. Attempt login with an unprovisioned subject; confirm denial and a log entry.
8. Test break-glass login, then lock it out and confirm rate limiting.
9. Log out and confirm you must re-authenticate at the IdP.
10. Produce the OWASP evidence pack.

## Acceptance criteria
- Every test user authenticates and maps correctly.
- An unmapped subject is denied, logged, and never receives a default account.
- No secret appears in the application export.
- Break-glass lockout triggers and is logged.
- Logout requires re-authentication at the IdP.
- All 10 OWASP items have a recorded evidence entry.

## Stretch
- Break the IdP deliberately and confirm break-glass still works and alerts.
- Demonstrate the difference between application logout and RP-initiated logout.