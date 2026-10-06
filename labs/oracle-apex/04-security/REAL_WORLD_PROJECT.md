# Lab 04: APEX Security — Real World Project

## Scenario
A financial services client must move their APEX application to corporate SSO.
The identity team runs an Oracle Identity Cloud Service tenant already used by
other applications. Today the APEX app uses internal accounts with the default
password policy; three people share one administrator account, so every admin
action is unattributable; support handles roughly 160 password resets a month;
and an audit found that a session cookie value contains an email address and a
role name in clear text. The move must complete without an application outage,
and the internal scheme must remain available in case the IdP has an incident.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX security)
- https://docs.oracle.com/en/database/oracle/identity/docs/ (IDCS)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/admin/

## Architecture
```
IDCS (Identity Cloud Service)
   │  Authorization Code + PKCE
   │  Claims: sub, email, name, groups
   ▼
APEX OIDC Authentication Scheme
   ├─ issuer / authorization / token / userinfo / jwks from IdP metadata
   ├─ client secret in SCHEME CONFIG (never in a page process)
   ├─ claim mapping: sub → username, email → email
   └─ RP-initiated logout → post_logout_redirect_uri
         │
         ▼
app_user_directory (provisioned BEFORE first login — never on login)
   │  unknown subject → DENY + log
   ▼
APEX session (15 min idle timeout, CSRF token, no secrets)
   │
   ├─ Roles: ADMIN / MANAGER / ANALYST / VIEWER
   ├─ Row scoping: current_department()
   └─ auth_event_log (append-only, every login and denial)
         │
         ▼
Break-glass fallback: max 3 local accounts, rate-limited, every use alerted
```

## Implementation sketch
```sql
-- Fail closed: an unknown subject is denied, never defaulted
SELECT user_id, username, apex_workspace_id, role_code, department_id
  INTO l_user_id, l_username, l_workspace, l_role, l_dept
  FROM app_user_directory
 WHERE identity_subject = :P_IDENTITY_SUBJECT
   AND active_flag = 'Y';

EXCEPTION WHEN NO_DATA_FOUND THEN
  INSERT INTO auth_event_log (username, event_type, outcome, detail)
  VALUES (SUBSTR(l_subject,1,120), 'SSO_LOGIN', 'DENIED',
          'Identity not provisioned in app_user_directory', SYSTIMESTAMP);
  COMMIT;
  RAISE_APPLICATION_ERROR(-20051,
    'Your account is not provisioned for this application.');
END;
```

## Requirements
- F1: OIDC authentication scheme configured from IdP discovery metadata.
- F2: Correct issuer and JWKS; signature validation verified.
- F3: Claim-to-user mapping keyed on `sub`, failing closed.
- F4: Directory provisioned ahead of login; no create-on-first-login.
- F5: Shared administrator account eliminated; individual IdP identities.
- F6: Client secret in scheme configuration; absent from the export.
- F7: RP-initiated logout so sessions end at the IdP.
- F8: 15-minute session timeout with idle expiry verified.
- F9: Session state minimised; no credentials or unnecessary PII.
- F10: CSRF protection verified active on every page.
- F11: Break-glass fallback, limited to named accounts and rate-limited.
- F12: Append-only authentication log with break-glass usage alerting.
- F13: Row-level scoping from the directory for every data region.
- F14: OWASP Top 10 evidence pack with a per-item entry.
- NF1: Zero APEX-managed passwords for SSO users.
- NF2: Shared accounts reduced to zero.
- NF3: Unknown subject denied with no default account.
- NF4: Session timeout independently verified at 15 minutes.
- NF5: Stale leaver accounts eliminated (revocation at the IdP).
- NF6: Authentication audit coverage at 100%.
- NF7: Security baseline — no layer skipped; OWASP evidence complete.
- NF8: Documented rollback — previous scheme retained as break-glass.

## Milestones
- Week 1: Scheme comparison, SSO design, and IdP app registration.
- Week 2: Scheme configuration, claim mapping, and directory provisioning.
- Week 3: Authorisation roles, row scoping, and session-state cleanup.
- Week 4: Break-glass, RP-initiated logout, and OWASP evidence.
- Week 4: Pilot with one team, then phased cutover.

## Verification
- Full login and logout flow through the IdP, including session termination.
- Login with an unprovisioned subject; confirm denial and a log entry.
- Admin action audit confirms the individual identity, not a shared account.
- Session expiry at 15 minutes, verified with a timed test.
- Application export search: no secret present.
- CSRF test with a forged cross-site request.
- Break the IdP; confirm fallback works and generates an alert.
- OWASP retest against the original findings.

## Rollback
The internal authentication scheme is retained and can be reinstated as the
current scheme without redeploying the application; directory rows persist, so
re-provisioning is unnecessary; shared accounts are re-enabled only under
break-glass with audit. Document rollback steps for every change.