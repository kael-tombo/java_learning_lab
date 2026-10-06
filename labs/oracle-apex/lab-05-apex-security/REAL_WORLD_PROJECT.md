# Lab 05: APEX Security — Real World Project

## Scenario
A client wants their APEX application to authenticate against the corporate
identity provider rather than maintaining a second set of passwords. The
identity team has an OIDC provider in place for other applications. Today the
APEX app uses APEX accounts with the default password policy, one shared
administrator account is used by three people, and an audit flagged that a
session cookie value contains an email address and a role name in clear text.
The application must move to SSO without an outage.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX security)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (authentication schemes)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/admin/

## Architecture
```
Identity Provider (OIDC)
   │  Authorization Code flow
   ▼
APEX Authentication Scheme (OIDC)
   ├─ issuer / authorization / token / JWKS endpoints from IdP metadata
   ├─ claim mapping: sub → username, email → email, roles → APEX role
   └─ RP-initiated logout

Session (post-authentication)
   ├─ APEX session state: minimal, no credentials or PII
   ├─ CSRF protection: active on every page
   └─ idle timeout enforced

Authorisation
   ├─ Authorisation scheme → page group per role
   └─ Row-level scoping per tenant/region

Shadow account (eliminated)
   └─ 3 shared admins → individual IdP identities
```

## Implementation sketch
```sql
-- Claim mapping must fail closed: an unmapped subject gets NO access
IF l_claim_sub IS NULL OR NOT EXISTS (
     SELECT 1 FROM app_user_directory u
      WHERE u.identity_subject = l_claim_sub AND u.active_flag = 'Y') THEN
  RAISE_APPLICATION_ERROR(-20050,
    'Identity not provisioned. Contact the application owner.');
END IF;
-- Do NOT default to "the first user" — that is how a provider misconfiguration
-- becomes a full-access account for a stranger.
```

## Requirements
- F1: OIDC authentication scheme configured from IdP metadata.
- F2: RP-initiated logout so sessions end at the provider.
- F3: Claim-to-user mapping that fails closed on an unknown subject.
- F4: Shared administrator accounts eliminated; individual identities only.
- F5: Authorisation scheme granting roles to defined page groups.
- F6: Session state minimised — no credentials, no unnecessary PII.
- F7: CSRF protection verified active on every page.
- F8: Idle timeout enforced and tested.
- F9: Row-level scoping per tenant.
- F10: OWASP Top 10 review with evidence per item.
- NF1: All users authenticate via corporate SSO; zero APEX passwords.
- NF2: Shared accounts reduced to zero.
- NF3: Unknown identity subject denied, with no default account.
- NF4: Session contains no credentials or unnecessary personal data.
- NF5: Security baseline — no layer skipped; OWASP evidence complete.
- NF6: Documented rollback — the previous scheme is retained until sign-off.

## Milestones
- Week 1: Scheme comparison and SSO design with the identity team.
- Week 2: OIDC scheme configured and tested against a test tenant.
- Week 3: Claim mapping, authorisations, and session state cleanup.
- Week 4: Eliminate shared accounts; row-level scoping; OWASP review.
- Week 4: Pilot with one team, then cutover.

## Verification
- Full login and logout flow through the IdP, including session end.
- Attempt login with an unprovisioned subject; confirm denial.
- Audit session state for credentials and unnecessary PII.
- CSRF test with a forged cross-site request.
- Break the IdP; confirm the failure mode is a clear error, not a bypass.

## Rollback
The APEX internal scheme is retained and can be reinstated as the current scheme
without redeploying the application; shared accounts are re-enabled only under
break-glass with audit. Document rollback steps for every change.