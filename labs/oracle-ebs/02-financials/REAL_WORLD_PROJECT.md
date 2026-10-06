# Lab 02: Financials (GL + Subledger) — Real World Project

## Scenario
A multi-entity manufacturer closes 200,000+ AP/AR/FA transactions per month
across 6 legal entities and 14 currencies. The close currently takes 9 days, is
reworked an average of twice, and last quarter shipped a $4.1M misposting that
was traced to an unbalanced interface batch nobody validated. You must rebuild
the accounting pipeline so the close is repeatable, reconciled, and auditable.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/financials/25d/faipp/ (Financials)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/erprug/
- https://docs.oracle.com/technologies/ebs/ (EBS Financials documentation)

## Architecture
```
AP / AR / FA / Cash
        │  subledger transactions
        ▼
   SLA (accounting templates)
        │  summary lines
        ▼
   GL_INTERFACE  ──► balance validation gate
        │  transfer_to_gl
        ▼
      GL  ──►  xx_gl_reconciliation_pkg  ──►  variance report
        │
        ├──►  Drill-down (GL_IMPORT_KEY → source document)
        └──►  Close dashboard (open periods, batch status, variance)
```

## Implementation sketch
```sql
-- Balanced-batch gate before transfer
SELECT gl_group_id, entity_id,
       SUM(CASE WHEN debit_amount  IS NOT NULL THEN debit_amount  ELSE 0 END) d,
       SUM(CASE WHEN credit_amount IS NOT NULL THEN credit_amount ELSE 0 END) c
  FROM gl_interface
 WHERE status_flag = 'N' AND period_name = 'FEB-26'
 GROUP BY gl_group_id, entity_id
HAVING SUM(debit_amount) <> SUM(credit_amount);
```

## Requirements
- F1: SLA accounting templates covering AP, AR, FA, and intercompany.
- F2: Enforced balanced-batch validation before any transfer to GL.
- F3: Multi-currency revaluation and translation with rate sourcing documented.
- F4: `xx_gl_reconciliation_pkg` producing GL↔subledger variance by entity,
      account, and period.
- F5: Full drill-down from GL line to source document via `GL_IMPORT_KEY`.
- F6: Intercompany elimination runbook for the 6 legal entities.
- F7: Close dashboard with open-period, batch, and variance metrics.
- F8: SOX-style control evidence for each close step (who, when, what).
- F9: Idempotent re-run design so a failed close can be retried safely.
- F10: Period-close checklist automation with sign-off capture.
- NF1: Close completes in 5 business days.
- NF2: Zero unexplained reconciliation variance at sign-off.
- NF3: RPO/RTO for the GL database and a documented restore drill.
- NF4: Security baseline — SOD on journal posting, restricted GL periods.
- NF5: Audit retention for reconciliation evidence.
- NF6: Every accounting change versioned with a rollback note.

## Milestones
- Week 1: Baseline — close calendar, rework causes, variance history.
- Week 2: SLA templates rebuilt and signed off by the controller.
- Week 3: Balanced-batch gate and reconciliation package implemented.
- Week 4: Multi-currency and intercompany processing validated.
- Week 5: Dashboard and control evidence deployed to finance.
- Week 6: First full parallel close and sign-off against target.

## Verification
- Parallel run of two consecutive closes must produce identical GL balances.
- Fault injection: unbalanced batch, duplicate submission, mid-close failure.
- Restore drill from backup with the close state verified after recovery.
- Finance sign-off that every variance has a documented disposition.

## Rollback
SLA templates are versioned and can be reinstated by date range; the interface
gate is a validation-only change and can be disabled without affecting posting.
Document rollback steps for every accounting configuration change.