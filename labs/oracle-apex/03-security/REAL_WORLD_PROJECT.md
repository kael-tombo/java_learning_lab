# Lab 03: Security (RBAC + Custom Auth + Audit) — Real World Project

## Scenario
A financial services client has an APEX portfolio-data application that has
grown organically and now sits in scope for SOX testing. Authentication is a
custom login with no lockout, passwords are stored as plain SHA-256 hashes,
sessions last 8 hours, and every user sees every branch's data. Access is
role-based at page level only — a VIEWER can reach the same page as an ANALYST
and simply avoids the buttons. Compliance requires evidence that data access is
restricted, so the current design fails on four counts.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/database/oracle/apex/24.2/ (APEX security)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/
- https://docs.oracle.com/en/database/oracle/oracle-database/21/admin/ (security)

## Architecture
```
Authentication
  APEX custom login
    ├─ Primary:  LDAP bind (corporate directory)
    └─ Fallback: local accounts, break-glass only, rate-limited, audited
         │
         ▼
Session context: role (ADMIN/MANAGER/ANALYST/VIEWER) + branch_id
         │
         ▼
Authorisation (layered)
  ├─ Page access        — which pages a role may open
  ├─ Feature access     — which actions a role may perform (process-level)
  └─ Row security       — APEX_DATA_PROFILE or VPD scoped to branch_id
         │
         ▼
Audit (tamper-evident)
  login_attempt · data_access · privileged_action
  retention per SOX requirement, no UPDATE/DELETE
```

## Implementation sketch
```sql
-- Row security via an APEX session-context function
CREATE OR REPLACE FUNCTION branch_scope(p_col VARCHAR2) RETURN VARCHAR2 IS
  l_branch NUMBER := TO_NUMBER(APEX_UTIL.SESSION_STATE('MY_BRANCH_ID'));
BEGIN
  -- NULL session context = no data access, not full data access
  IF l_branch IS NULL THEN RETURN '1=0'; END IF;
  RETURN p_col || ' = ' || l_branch;
END;
/
-- Apply as a computed predicate on every branch-scoped region

-- PBKDF2 with per-user salt, never plain SHA-256
CREATE OR REPLACE PACKAGE xx_pwd_pkg AS
  FUNCTION hash(p_pwd VARCHAR2, p_salt RAW) RETURN RAW;
  FUNCTION verify(p_pwd VARCHAR2, p_salt RAW, p_hash RAW) RETURN BOOLEAN;
  PROCEDURE record_failure(p_user VARCHAR2);
END;
/
```

## Requirements
- F1: LDAP authentication with a documented, rate-limited local fallback.
- F2: Four-role hierarchy with explicit capability definitions.
- F3: Page-level authorisation per role.
- F4: Feature-level authorisation enforced in page processes.
- F5: Branch-scoped row security on every data region.
- F6: Session timeout of 15 minutes with idle-expiry enforcement.
- F7: PBKDF2 password hashing with per-user salts and migration from SHA-256.
- F8: Account lockout after 5 failed attempts with automatic unlock window.
- F9: Tamper-evident audit trail with SOX retention.
- F10: OWASP Top 10 review with documented evidence per item.
- NF1: Zero cross-branch data access in penetration testing.
- NF2: Zero privilege escalation paths from VIEWER to write capability.
- NF3: 100% of authentication and data access events audited.
- NF4: Session timeout enforced and independently verified.
- NF5: Security baseline — no fast hashing, no plaintext, no unbounded sessions.
- NF6: Documented rollback for every authorisation change.

## Milestones
- Week 1: Baseline — penetration test, capability inventory, gap register.
- Week 2: LDAP integration and local fallback with rate limiting.
- Week 3: Role hierarchy, page and feature authorisation.
- Week 4: Branch row security applied to all data regions.
- Week 5: PBKDF2 migration, lockout, session timeout.
- Week 6: Audit trail, OWASP evidence pack, penetration retest.

## Verification
- Attempt cross-branch access from a MANAGER account; confirm denial.
- Attempt privilege escalation from VIEWER to an ADMIN action.
- Verify session expiry at exactly 15 minutes.
- Confirm audit records cannot be updated or deleted.
- OWASP retest against the original findings.

## Rollback
Role definitions and page/feature grants are configuration and reversible per
responsibility; the authentication scheme reverts by changing the scheme in use;
password migration keeps the original hash until first successful login.
Document rollback steps for every change.