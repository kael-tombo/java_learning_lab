# Lab 09: Security (SOD Remediation) — Real World Project

## Scenario
You are at PwC auditing the EBS implementation at a financial services client.
Internal audit found 45 users holding conflicting responsibilities that violate
SOX SOD rules — users in AP can create suppliers, approve invoices, and process
payments, all without secondary approval. No SOD enforcement exists in EBS. The
audit committee demands immediate remediation, and the business cannot stop.
Alongside this, 12 dormant accounts hold elevated access and a profile with
`FND_HIDE_DB_PASSWORD='N'` is leaking database credentials into diagnostics and
support logs. You have 30 days.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS security)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/rnbrdu/ (EBS Security Guide)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/admin/

## Architecture
```
Duty catalogue (xx_sod_duty) ──► Conflict matrix (xx_sod_conflict)
                                          │
                                          ▼
                       Detection at USER-ASSIGNMENT level
                          (self-join on fnd_user_responsibilities)
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
             Risk ranking        Remediation          Preventive control
        severity × value      revoke ONE duty     block at grant time
                    │                     │                     │
                    └─────────────────────┼─────────────────────┘
                                          ▼
                      Exceptions (time-bound, owned, compensating control)
                                          ▼
                      Certification (attestation + evidence retention)
                                          │
                                          ▼
                    Hardening: password visibility + dormancy sweep
```

## Implementation sketch
```sql
-- Detection must be at the ASSIGNMENT level — a violation is a property of a
-- user's set of duties, not of any single responsibility
WITH user_duties AS (
  SELECT DISTINCT fu.user_id, fu.user_name, t.duty_code, t.duty_name
    FROM fnd_users fu
    JOIN fnd_user_responsibilities ur ON ur.user_id = fu.user_id
    JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
    JOIN xx_sod_duty t ON t.function_name = r.responsibility_name
   WHERE fu.active = 'Y')
SELECT a.user_name, a.duty_code duty_a, b.duty_code duty_b, c.severity
  FROM user_duties a
  JOIN user_duties b ON a.user_id = b.user_id AND a.duty_code < b.duty_code
  JOIN xx_sod_conflict c
    ON (c.duty_a = a.duty_code AND c.duty_b = b.duty_code)
    OR (c.duty_a = b.duty_code AND c.duty_b = a.duty_code);

-- The finding that makes every other control moot
SELECT o.profile_option_name, v.level, v.profile_option_value
  FROM fnd_profile_options o
  JOIN fnd_profile_values v ON v.profile_option_id = o.profile_option_id
 WHERE o.profile_option_name = 'FND_HIDE_DB_PASSWORD'
   AND v.profile_option_value = 'N';
```

## Requirements
- F1: SOD risk matrix enumerating duties, conflicts, severity, and rationale.
- F2: Detection query at user-assignment level across all 2,400 active users.
- F3: Risk ranking by severity weighted by annual value at risk.
- F4: Remediation of all 45 violations, removing only conflicting duties.
- F5: Alternate path identified and staffed for every removed duty.
- F6: Preventive control blocking conflicting assignments at grant time.
- F7: Time-bound exception process with compensating controls and expiry.
- F8: Dormant account review; deactivation of all 12 elevated accounts.
- F9: Password visibility hardening across every profile level.
- F10: Monthly (then quarterly) certification with evidence retention.
- NF1: Zero open SOD violations at audit sign-off.
- NF2: Zero password exposure — the scan returns clean.
- NF3: Zero dormant elevated accounts.
- NF4: No business disruption — payment cycle time unchanged.
- NF5: Security baseline — least privilege evidenced, not asserted.
- NF6: Evidence pack produced without further queries at audit committee.
- NF7: 30-day window met with a verification phase reserved.

## Milestones
- Week 1 (days 1–7): Risk matrix, detection, quantification, risk ranking.
- Week 2 (days 8–14): Preventive control, scripts, exception form, sign-off.
- Week 3 (days 15–21): Pilot one business unit; validate no disruption.
- Week 4 (days 22–26): Execute all units; dormant accounts and password fix.
- Week 4 (days 27–30): Verification re-run, evidence pack, audit committee.

## Verification
- Re-run detection and confirm zero open high-severity violations.
- Attempt a conflicting assignment; confirm the preventive control blocks it.
- Attempt to connect to diagnostics and confirm no password is displayed.
- Confirm no shared logins or out-of-system approval workarounds emerged.
- Payment cycle timing compared before and after per business unit.

## Rollback
Every revocation is recorded with approver, reference, alternate path, and
effective date, and is reversible by re-granting the responsibility; preventive
control deploys in report mode before enforcement; exception records are
retained. Document rollback steps for every change.