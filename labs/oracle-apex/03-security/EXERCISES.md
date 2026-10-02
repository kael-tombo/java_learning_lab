# EXERCISES — APEX Security

## 1. Same password, different hashes (beginner)
Create two users with password `Welcome1` via `sec_pwd` (fresh salts).
Show the stored hashes differ. Verify both log in. *Reflection: what
exactly does the salt defeat?*

## 2. Lockout drill (beginner)
Fail login 4× (no lock), 5th time (locked 15 min), correct password during
lock (still denied), after expiry (admitted, counter reset). Confirm each
transition in `app_audit_log`. Explain why the check precedes verification.

## 3. pesticide: injection battery (intermediate)
Fire `' OR '1'='1`, `'; DROP TABLE app_users; --`, and UNION probes at the
login + one report. All must fail (binds). Then deliberately build one
concatenated query in a scratch page, exploit it, and delete the page —
the exercise is feeling the difference.

## 4. Branch-escape test (intermediate)
Log in as ANALYST_LON (branch 102): confirm only 102 rows. Craft a report
URL with another branch's parameters; confirm VPD/predicate still scopes.
Remove the predicate from a copy of the query and show the leak — then
explain why UI-hiding alone would have passed a demo and failed an audit.

## 5. Stale-grant race (advanced)
Grant ANALYST a new permission, and within the same minute verify a live
session sees it immediately (no cache). Then implement the cache you were
told not to (10-min TTL) in a scratch function, demonstrate the stale
window, and write the incident note justifying live checks in production.
