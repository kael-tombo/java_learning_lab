# EBS HRMS — Real World Project

## Scenario
A global financial services firm supports 25,000 employees across 18 countries
with 12 legislative data groups. Recruiting sits in an external ATS, payroll is
outsourced to ADP, HR lives in EBS HRMS, and offboarding is a spreadsheet. Each
lifecycle event takes 3–5 days of manual entry across four systems with no
reconciliation between them. The CHRO wants one automated lifecycle with an
audit trail — and a fixed go-live for the payroll integration.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- (link removed) (HCM / HRMS docs)
- (link removed) (Oracle HRMS concepts)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
ATS ──► Staging + validation ──► HRMS public APIs (PER_ALL_PEOPLE_F)
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
               HR / Payroll        Time & Labor          Benefits
                    │                   │                   │
                    └────────► ADP Global View ◄───────────┘
                                 (bidirectional)
                    │
                    ├──► Lifecycle event audit trail (7-year retention)
                    └──► Offboarding checklist automation
```

## Implementation sketch
```sql
-- Lifecycle event audit trail
CREATE TABLE xx_hr_lifecycle_audit (
  person_id     NUMBER,
  event_type    VARCHAR2(30),   -- HIRE / TRANSFER / PROMOTE / TERMINATE
  effective_from DATE,
  effective_to  DATE,
  actor         VARCHAR2(64),
  approval_ref  VARCHAR2(30),
  CONSTRAINT xx_hr_audit_ck CHECK (event_type IN
    ('HIRE','TRANSFER','PROMOTE','TERMINATE'))
);
-- Effective-dated headcount as at a past date
SELECT COUNT(DISTINCT person_id)
  FROM per_all_assignments_f
 WHERE assignment_type = 'E'
   AND effective_start_date <= DATE '2026-02-01'
   AND NVL(effective_end_date, DATE '9999-12-31') >= DATE '2026-02-01';
```

## Requirements
- F1: Single lifecycle model spanning hire → onboarding → payroll setup →
      benefits → development → termination.
- F2: Automated triggers fired on each lifecycle event, with retry and alerting.
- F3: Multi-pass validated load with a 99.9% first-pass acceptance rate.
- F4: ADP Global View integration for payroll input and result reconciliation.
- F5: Legislative compliance for 18 countries (notice periods, final pay).
- F6: Manager self-service for promotions, transfers, and terminations.
- F7: Offboarding checklist automation with evidence capture.
- F8: Lifecycle audit trail with 7-year retention.
- F9: Headcount and movement reporting as at any historical date.
- F10: Data quality dashboard with error counts by domain.
- NF1: Lifecycle event cycle time reduced from 3–5 days to under 4 hours.
- NF2: Payroll reconciliation with zero unexplained differences.
- NF3: P95 page load under 2 seconds on a 25,000-employee population.
- NF4: Security baseline — HR data access restricted by legislative need.
- NF5: Audit retention enforced and verified.
- NF6: RPO/RTO for the HR database with a documented restore drill.

## Milestones
- Week 1: Baseline — data quality audit, cycle-time measurement, gap list.
- Week 2: Validated load pipeline built; first pass measured.
- Week 3: Lifecycle triggers and workflow automation implemented.
- Week 4: ADP integration with reconciliation built and tested.
- Week 5: Self-service and offboarding automation deployed.
- Week 6: Audit trail, reporting, and data quality dashboard live.

## Verification
- Full population load achieving the stated first-pass acceptance rate.
- Payroll parallel run against a reference result for a sample population.
- Fault injection: duplicate records, missing supervisor, invalid identifier.
- Restore drill verifying effective-dated history survives recovery.

## Rollback
Lifecycle events are versioned by effective date; integration mappings are
configuration; self-service pages are flag-gated. Document rollback steps for
every change.