# Lab 02: System Administration — Real World Project

## Scenario
A distributor with 6,000 users and a warehouse operation of 4,000 staff has
three problems: onboarding a seasonal cohort of 500 users takes two weeks of
manual admin work, the nightly `GL_POST` has failed on `ORA-00001` three times
this month with no clear owner, and an audit found 45 users holding conflicting
responsibilities. You are the incoming EBS administrator.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS admin guidance)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/admin/
- https://docs.oracle.com/technologies/ebs/ (EBS Security guide)

## Architecture
```
HR feed ─► Staging + Validation ─► FND_USER_PKG ─► FND_USERS
                                            └──► Responsibility assignment
Nightly jobs ─► FND_CONCURRENT_REQUESTS ─► Log diagnostics ─► Fix
Audit ─► SOD conflict report ─► Remediation workflow ─► Monthly certification
Security baseline ─► Profile option scan (incl. FND_HIDE_DB_PASSWORD)
```

## Implementation sketch
```sql
-- SOD conflict detection: same user, mutually exclusive duties
SELECT fu.user_name, r1.responsibility_name ap_create,
       r2.responsibility_name ap_approve, r3.responsibility_name ap_pay
  FROM fnd_user_responsibilities ur1
  JOIN fnd_user_responsibilities ur2 ON ur1.user_id = ur2.user_id
  JOIN fnd_user_responsibilities ur3 ON ur1.user_id = ur3.user_id
  JOIN fnd_responsibilities r1 ON r1.responsibility_id = ur1.responsibility_id
  JOIN fnd_responsibilities r2 ON r2.responsibility_id = ur2.responsibility_id
  JOIN fnd_responsibilities r3 ON r3.responsibility_id = ur3.responsibility_id
 WHERE r1.responsibility_name LIKE 'AP%' AND r2.responsibility_name LIKE 'AP%APPROVE%'
   AND r3.responsibility_name LIKE 'AP%PAY%'
 GROUP BY fu.user_name, r1.responsibility_name, r2.responsibility_name,
          r3.responsibility_name;
```

## Requirements
- F1: Automated onboarding pipeline from the HR feed with validation gates.
- F2: Reconciliation report proving file rows match users created.
- F3: Root-cause fix for the `GL_POST` duplicate-key failure with a guard.
- F4: Preventive monitoring that alerts on job failure the same night.
- F5: Full SOD analysis with a risk-ranked conflict matrix.
- F6: Remediation of all 45 violations plus approved exceptions.
- F7: Monthly SOD certification workflow with evidence capture.
- F8: Security posture scan covering password visibility, default passwords,
      and dormant accounts.
- F9: Documented admin runbooks for the ten most common tasks.
- F10: Change log recording who changed what, when, and how to reverse it.
- NF1: Onboarding lead time reduced from 2 weeks to 2 days.
- NF2: Zero unowned job failures — every failure has an alert and an owner.
- NF3: SOD exceptions approved and dated; no unreviewed violations.
- NF4: Security baseline verified by a scan, not by assertion.
- NF5: RPO/RTO for the admin database with a restore drill performed.
- NF6: Audit-ready evidence for every remediation.

## Milestones
- Week 1: Baseline — user inventory, job failure history, SOD extract.
- Week 2: Onboarding pipeline built and dry-run against last year's file.
- Week 3: `GL_POST` root cause fixed; monitoring and alerting live.
- Week 4: SOD remediation executed; exceptions routed for approval.
- Week 5: Security posture scan and hardening applied.
- Week 6: Runbooks, change log, and audit handover complete.

## Verification
- Replay the seasonal cohort file and confirm an exact count reconciliation.
- Fault injection: duplicate interface rows and a deliberately failing job.
- Restore drill verifying user data and responsibility assignments survive.
- Auditor review of the change log and certification evidence.

## Rollback
User creation is reversible by end-dating; responsibility revocations are
recorded with a restore script; profile option changes capture the prior value.
Document rollback steps for every administrative change.