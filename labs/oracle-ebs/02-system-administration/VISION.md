# Lab 02: System Administration — Vision

## Where this lab takes you
From `FND_USER_PKG` bulk provisioning to holding the administrative line for
nightly jobs, audit findings, and password-leak remediation.

## The Arc
1. **Users** — creating accounts in bulk with correct profiles and defaults.
2. **Jobs** — diagnosing a nightly `GL_POST` failing on duplicate keys.
3. **Access** — SOD violations found by audit, and how to remediate them.
4. **Hygiene** — recognising settings that leak data (`FND_HIDE_DB_PASSWORD=N`).
5. **Responsibility** — knowing when an admin fix needs a business decision.
6. **Change control** — every admin change documented, reversible, and audited.

## Milestones (checkable)
- [ ] M1: Provision 500 warehouse users from a flat file via `FND_USER_PKG`.
- [ ] M2: Validate the load — no duplicate logins, no orphaned profiles.
- [ ] M3: Diagnose the `ORA-00001` duplicate in nightly `GL_POST` by reading
      the request log and the offending table.
- [ ] M4: Produce an SOD conflict report from responsibility assignments.
- [ ] M5: Remediate violations without breaking business operations.
- [ ] M6: Demonstrate the impact of `FND_HIDE_DB_PASSWORD=N` and fix it.
- [ ] M7: Write a runbook for adding a profile option change safely.
- [ ] M8: Hand over an admin change log an auditor would accept.

## Anti-Goals
- Creating users by hand when the volume is in the hundreds.
- Deleting a user record instead of end-dating it.
- Fixing SOD violations by granting more access rather than less.
- Applying a profile option globally when it was meant for one responsibility.

## The one-sentence thesis
Administration changes are code — they need review, a rollback, and an audit
trail exactly like any other change.