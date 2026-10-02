# THEORY — APEX RBAC Security

## 1. Defense in depth, four layers

Authentication (who are you: LDAP → local PBKDF2 fallback) →
authorization (what may you do: role + permission + branch) →
auditing (what did you do: every decision logged with user/IP/time) →
session discipline (15-minute expiry, lockout, HTTPS). Each layer assumes
the previous one can fail — the audit log catches what authorization
misses, lockout catches what passwords don't.

## 2. Why hierarchy lives in data, not code

`app_roles.parent_role_id` plus explicit `app_role_permissions` rows per
role (ADMIN gets all 8, MANAGER 5, ANALYST 3, VIEWER 2) — permissions are
*granted*, never computed by walking the tree at request time. Role
changes take effect immediately precisely because checks query live
tables (`has_permission` counts current rows). Cached roles would be
faster and wrong after every grant/revoke.

## 3. The auth function's ordering is the security

Lockout-check *before* password-verify (locked accounts never burn CPU
on hashes, and never leak timing); LDAP-try inside its own
`BEGIN…EXCEPTION` so directory outages fall back instead of failing
closed for local users; `NO_DATA_FOUND` → logged FALSE (unknown users get
no oracle distinguishing them from bad passwords); success resets the
counter, failure increments with lock-at-5. Every branch commits its audit
row — uncommitted audit is unwritten audit.

## 4. Row security: VPD vs predicate

VPD (`branch_access_policy` on PORTFOLIOS for SELECT/UPDATE/DELETE with
`update_check`) enforces at the database — no query can forget it. The
`1=1 / branch_id= / 1=0` trichotomy (ADMIN / scoped / none) is the whole
policy in three lines. Application-level `AND (branch_id=:G OR
role='ADMIN')` is cheaper to build but must be repeated in *every* query —
one forgotten report leaks all branches. And UI hiding without
server-side schemes is decoration, not security (pitfall #5).
