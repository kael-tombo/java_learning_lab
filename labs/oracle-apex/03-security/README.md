# 03 — Security (RBAC + Custom Auth + Audit)

## Overview

Portfolio-data APEX app under financial-services constraints: LDAP-with-
local-fallback auth, ADMIN>MANAGER>ANALYST>VIEWER hierarchy, branch-scoped
row security, feature-level authorization, full audit, 15-minute sessions,
PBKDF2 passwords, 5-strike lockout — verified against OWASP Top 10.

## Learning Objectives

- [ ] Model RBAC schema (users/roles/permissions + mappings, hierarchical roles, interval-partitioned audit)
- [ ] Implement PBKDF2 hashing (`DBMS_CRYPTO`, 10k iterations) + LDAP-then-local auth with lockout
- [ ] Centralize decisions in `sec_rbac` (role, permissions, branch, Y/N wrapper) + VPD or predicate filtering
- [ ] Harden the app (binds, session protection, HTTPS, error handler) and test all three attack classes

## Topics Covered

### 1. Schema + crypto (Steps 1–2)
Six tables (unique user_role/role_perm pairs; daily audit partitions);
`sec_pwd` (salt → PBKDF2 → hex; verify by recompute). Walkthrough Steps 1–2.

### 2. Auth + RBAC core (Steps 3–4)
LDAP-try/except-fallback; lockout check-before-verify; counter reset vs
`failed_logins+1` with 15-min lock at 5; `NO_DATA_FOUND` → logged FALSE;
`sec_rbac` six functions + `BULK COLLECT` permission lists. Walkthrough
Steps 3–4.

### 3. Enforcement layers (Steps 5–8)
G_* items via computations; four authorization-scheme shapes
(role-equality, role-set, `INSTR`-on-list permission); page/region/menu
binding; VPD (`1=1`/`branch_id=`/`1=0`) vs `AND (branch=:G OR role=ADMIN)`.
Walkthrough Steps 5–8.

### 4. Audit/session/hardening/tests (Steps 9–12)
DML trigger audit; 15-min timeout + JS warning + KEEP_ALIVE; six-item
hardening checklist; three test classes (auth flow, authorization, injection).
Walkthrough Steps 9–12, `WORKED_SQL_EXAMPLE.sql`.

## Prerequisites

- APEX auth schemes, computations, authorization schemes, session state
- PL/SQL packages/triggers; PBKDF2 concept; OWASP Top 10 basics

## Further Reading

- APEX Security Guide (session protection, checksums, HTTPS)
- `../05-restful-services/` for the OAuth2/API side of the same discipline
