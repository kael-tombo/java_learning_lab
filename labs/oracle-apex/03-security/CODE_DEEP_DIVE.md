# CODE_DEEP_DIVE — Security walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. Schema (Step 1, lines 32–161)

- `UNIQUE(user_id, role_id)` and `UNIQUE(role_id, permission_id)` make
  double-grants structurally impossible; `ON DELETE CASCADE` on user_roles
  prevents orphan grants when users are purged.
- `app_audit_log` is interval-partitioned daily (`PARTITION BY RANGE …
  INTERVAL 1 DAY`) with username + date indexes — audit tables grow
  unboundedly, and unpartitioned audit is a future full-table-scan outage.
- Seed data encodes the hierarchy numerically (ADMIN 1 → VIEWER 4, parent
  pointers upward) and the permission gradient explicitly (8/5/3/2 rows).
  `get_user_role` defaults unknown users to VIEWER (fail-closed to
  least privilege, never to error or — worse — ADMIN).

## 2. `sec_pwd` (Step 2, lines 165–199)

- `PBKDF2(password, salt, 10000, dklen 32, HMAC_SH256)` → hex. Salt from
  `RANDOMBYTES(16)` per user — identical passwords hash differently, so
  rainbow tables die at the salt column.
- `verify_password` recomputes and compares strings. No plaintext
  anywhere: the seed `'HASH_VALUE'` placeholders mark where real hashes go
  (generated in app code, never pasted from logs).

## 3. Auth function (Step 3, lines 209–290)

- LDAP attempt wrapped so *any* directory failure → `FALSE` (fallback),
  not propagation. Local lookup is `LOWER(username)` + `is_active='Y'` —
  case-insensitive, deactivated users rejected before hashing.
- Failure path: `failed_logins+1`, lock when `>= 5` for 15 minutes; audit
  includes attempt number. Success path: reset counter, clear lock, stamp
  `last_login`, audit LOGIN. All three exits `COMMIT` their audit rows.
- Post-auth computations populate `G_USER_*` from `sec_rbac` — downstream
  authorization reads session items, never re-queries per page render…
  except permission checks themselves, which stay live (immediacy rule).

## 4. `sec_rbac` + enforcement (Steps 4–8, lines 312–509)

- `get_user_permissions` uses `BULK COLLECT INTO ODCIVARCHAR2LIST` — one
  round trip for the full set; `has_permission` counts matches in the
  collection (small-N, in-memory, no per-check query storm).
- `INSTR(','||list||',', ',PORTFOLIO_EDIT,')` — comma-wrapped matching
  avoids substring false positives (`EDIT` matching `RE_EDIT_X`).
- VPD function returns predicate *strings*; `update_check=>TRUE` extends
  the policy to writes (read-only VPD with writable holes is a classic
  bypass). Trigger `trg_audit_dml` logs `INSERTING/UPDATING/DELETING`
  with `:NEW`/`:OLD` ids + `:APP_USER`/`:APP_SESSION` context.
