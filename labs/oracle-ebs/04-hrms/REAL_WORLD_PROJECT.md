# Lab 04: Employee Lifecycle Management (HRMS) — Real World Project

## Scenario
A global financial services firm has 25,000 employees across 18 countries.
Recruiting is in an external ATS, HR is in EBS HRMS, payroll is outsourced to
ADP, and offboarding is a spreadsheet. Every lifecycle event costs 3–5 days of
manual entry across four systems with no reconciliation between them. At 32%
turnover that is roughly 19,250 events a year and a persistent error surface.
The CHRO wants one automated lifecycle with a complete audit trail — and a
regulator's retention expectations on the record.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/hcm/25d/faipp/ (HCM / HRMS)
- https://docs.oracle.com/database/121/HCMR/ (Oracle HRMS concepts)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
ATS ──► Staging + validation ──► HRMS public APIs
                                      │
                     ┌────────────────┼────────────────┐
                     ▼                ▼                ▼
              Person/Assignment   Time & Labor     Benefits
                     │                │                │
                     └──────────► Trigger engine ◄─────┘
                                      │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
   ADP payroll    Benefits       Equipment     Security       Offboarding
   out / in       enrollment     request       profile        checklist
        │              │              │              │              │
        └──► Reconciliation ◄──────  Lifecycle audit trail (7 yr) ◄──┘
```

## Implementation sketch
```sql
-- Idempotent cascade: MERGE + unique constraint means retry is safe
MERGE INTO xx_hr_lifecycle_action tgt
USING (SELECT l_event_id eid, p_person_id pid, t.action_type atype
         FROM dual,
       TABLE(SYS.ODCIVARCHAR2LIST('PAYROLL_SETUP','BENEFITS_ENROLLMENT',
                                   'EQUIPMENT','SECURITY_PROFILE')) t) src
   ON (tgt.event_id = src.eid AND tgt.person_id = src.pid
       AND tgt.action_type = src.atype)
WHEN NOT MATCHED THEN
  INSERT (event_id, person_id, action_type, status)
  VALUES (src.eid, src.pid, src.atype, 'PENDING');

-- Payroll reconciliation: every employee sent must appear in the response
SELECT s.national_identifier sent_emp, r.national_identifier recv_emp,
       CASE WHEN r.national_identifier IS NULL THEN 'MISSING_IN_ADP' END status
  FROM xx_adp_outbound s
  LEFT JOIN xx_adp_inbound r ON r.national_identifier = s.national_identifier
 WHERE s.direction = 'OUT' AND s.status = 'SENT'
   AND (r.national_identifier IS NULL);
```

## Requirements
- F1: Lifecycle state machine covering hire → active → terminated → alumni.
- F2: Effective-dated data model with `_F` history and `_V` current state.
- F3: Automated, idempotent trigger cascades for every lifecycle event.
- F4: Legislative compliance for 18 countries read from HRMS configuration.
- F5: ADP Global View integration with outbound payloads and inbound results.
- F6: Mandatory payroll reconciliation with exception reporting.
- F7: Manager self-service for promotion, transfer, and termination.
- F8: Offboarding checklist automation with owners, deadlines, and escalation.
- F9: Append-only lifecycle audit trail with 7-year retention.
- F10: Data quality dashboard with error counts by domain.
- NF1: Lifecycle event cycle time reduced from 3–5 days to under 4 hours.
- NF2: Payroll reconciliation rate ≥ 99.9% with zero unexplained variance.
- NF3: P95 lifecycle page load under 2 seconds on 25,000 employees.
- NF4: Security baseline — SSO revocation on the termination effective date.
- NF5: Audit retention enforced and independently verifiable.
- NF6: RPO/RTO for the HR database with a documented restore drill.

## Milestones
- Week 1: Current-state lifecycle map and cycle-time baseline measured.
- Week 2: State machine, schema, and audit trail implemented.
- Week 3: Trigger engine with idempotency proof and retry handling.
- Week 4: ADP integration with reconciliation built and tested.
- Week 5: Self-service and offboarding automation deployed.
- Week 6: Reporting, data quality dashboard, and knowledge transfer.

## Verification
- Replay 500 historical lifecycle events and compare resulting state.
- Fault injection: duplicate event fire, ADP timeout, missing ADP response.
- Idempotency test: fire each event type twice, assert zero duplication.
- Restore drill verifying effective-dated history survives recovery.

## Rollback
Lifecycle events are versioned by effective date; trigger actions are queued and
can be held; self-service is flag-gated; the audit trail is never rolled back by
design. Document rollback steps for every change.