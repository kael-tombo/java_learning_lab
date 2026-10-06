# EBS Security Controls — Real World Project

## Scenario
A financial services client is undergoing SOX testing on EBS R12.2. Internal audit
found 45 users with conflicting responsibilities, 12 dormant accounts with
elevated access, and a profile with `FND_HIDE_DB_PASSWORD='N'` exposing database
credentials in the diagnostics. The remediation window is 30 days and the
business cannot stop. You own the control environment through the audit.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS security)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/admin/
- https://docs.oracle.com/database/121/EBSMG/ (EBS Security Guide)

## Architecture
```
Identity ─► Authentication scheme (sign-on) ─► Responsibility context
                                                     │
        ┌────────────────────┬───────────────────────┼──────────────┐
        ▼                    ▼                       ▼              ▼
  Function security   Form security          Data security    Row-level VPD
                                                            (FND_MOBS)
        └────────────────────┴───────────────────────┴──────────────┘
                                     │
                        SOD conflict engine ─► approval workflow
                                     │
                        Audit trail ─► SIEM ─► monthly certification
```

## Implementation sketch
```sql
-- SOD conflict detection across mutually exclusive duties
SELECT fu.user_name,
       MAX(CASE WHEN r.responsibility_name LIKE '%SUPPLIER%' THEN r.responsibility_name END) d1,
       MAX(CASE WHEN r.responsibility_name LIKE '%APPROVE%'    THEN r.responsibility_name END) d2,
       MAX(CASE WHEN r.responsibility_name LIKE '%PAYMENT%'   THEN r.responsibility_name END) d3
  FROM fnd_users fu
  JOIN fnd_user_responsibilities ur ON ur.user_id = fu.user_id
  JOIN fnd_responsibilities r ON r.responsibility_id = ur.responsibility_id
 GROUP BY fu.user_name
HAVING COUNT(DISTINCT CASE WHEN r.responsibility_name LIKE '%SUPPLIER%'
                          THEN 1 END) = 1
   AND COUNT(DISTINCT CASE WHEN r.responsibility_name LIKE '%APPROVE%'
                          THEN 1 END) = 1
   AND COUNT(DISTINCT CASE WHEN r.responsibility_name LIKE '%PAYMENT%'
                          THEN 1 END) = 1;

-- Dormant account detection
SELECT user_name, TO_CHAR(last_signin_date,'YYYY-MM-DD') last_seen
  FROM fnd_users
 WHERE active = 'Y'
   AND NVL(last_signin_date, DATE '2000-01-01') < SYSDATE - 90;
```

## Requirements
- F1: SOD risk matrix mapping functions to conflict categories.
- F2: Remediation of all 45 violations plus documented, approved exceptions.
- F3: Preventive SOD control blocking conflicting assignments at grant time.
- F4: Monthly certification workflow with evidence capture and sign-off.
- F5: Dormant account review and deactivation of all 12 elevated accounts.
- F6: Password policy enforcement with complexity, ageing, and lockout.
- F7: Row-level data security where business requires branch or entity scoping.
- F8: TLS everywhere with re-encryption to the application tier.
- F9: Transparent Data Encryption for sensitive tablespaces.
- F10: Hardening check covering `FND_HIDE_DB_PASSWORD` and default passwords.
- NF1: Zero unreviewed SOD violations at audit sign-off.
- NF2: SOD grant-time enforcement active for all new assignments.
- NF3: Zero dormant elevated accounts.
- NF4: Security baseline verified by scan, not by assertion.
- NF5: Audit trail retention aligned to SOX requirements.
- NF6: RPO/RTO with a documented restore drill, including key material.

## Milestones
- Week 1: Baseline — SOD extract, dormant accounts, hardening scan.
- Week 2: SOD remediation executed; exceptions routed and approved.
- Week 3: Preventive SOD control and approval workflow implemented.
- Week 4: Dormant accounts and password policy remediated.
- Week 5: TLS, TDE, and row-level scoping implemented where required.
- Week 6: Certification workflow live; audit handover package complete.

## Verification
- Re-run the SOD scan and confirm only approved exceptions remain.
- Attempt a conflicting assignment and confirm it is blocked.
- Restore drill verifying encrypted data is readable after recovery.
- Security review sign-off on the hardening scan results.

## Rollback
Responsibility revocations ship with a restore script and an approval record;
profile and password policy changes capture prior values; TDE can be disabled
by configuration. Document rollback steps for every security change.