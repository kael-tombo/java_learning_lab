# Lab 03: Security (RBAC + Custom Auth + Audit) — Mini Project

## Goal
Build a secured APEX application with LDAP-plus-fallback authentication, a
four-role hierarchy, branch row security, and full audit in 90 minutes.

## Requirements
- R1: Custom login page with LDAP authentication and local break-glass.
- R2: Four roles: ADMIN, MANAGER, ANALYST, VIEWER, with distinct capabilities.
- R3: Branch-scoped row security using an APEX session context function.
- R4: Feature-level authorisation checks in the page processes.
- R5: 15-minute session timeout enforced and tested.
- R6: PBKDF2 password hashing with per-user salt and 5-strike lockout.
- R7: Audit table capturing login attempts, role, and data access.
- R8: An OWASP review checklist with evidence for each item.

## Steps
1. Create the branch and user tables with a branch identifier.
2. Build the login page and validate credentials against LDAP, then locally.
3. On success, set the session role and branch context.
4. Implement the context function that scopes queries to the user's branch.
5. Add feature authorisation checks to each page process.
6. Set the session timeout to 15 minutes and verify expiry.
7. Implement PBKDF2 hashing and account lockout after 5 failures.
8. Write audit triggers for login and for access to sensitive tables.
9. Walk the OWASP checklist and record evidence for each control.

## Acceptance criteria
- LDAP users authenticate; the local fallback works only for named break-glass
  accounts and is rate-limited.
- A VIEWER user cannot reach an ANALYST capability.
- A MANAGER sees only their branch's rows.
- Sessions expire at 15 minutes of inactivity.
- Passwords are PBKDF2 with unique salts; no plaintext exists anywhere.
- Five failed attempts lock the account and the audit trail records them.
- The audit trail records who accessed what, when, and from where.

## Stretch
- Demonstrate that audit records cannot be updated or deleted.
- Test the OWASP items you expect to be weakest and document the gap.