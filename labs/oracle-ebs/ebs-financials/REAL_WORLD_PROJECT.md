# EBS Financials — Real World Project

## Scenario
A multi-entity manufacturer runs EBS Financials for 6 legal entities across 14
currencies. Month-end close takes 9 days and is reworked twice on average. Last
quarter an intercompany elimination was missed, producing a $6.2M misstatement
that reached the statutory accounts before it was caught. Finance has asked you
to make the close repeatable and the numbers traceable — not to add features.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS Financials)
- https://docs.oracle.com/en/cloud/saas/financials/25d/faipp/
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
AP / AR / FA / Cash  (subledgers record events)
        │  SLA accounting templates
        ▼
   GL_INTERFACE ──► balanced-batch validation gate
        │
        ▼
       GL  (accounting engine)
        │
        ├─► Intercompany elimination engine (6 entities)
        ├─► xx_gl_reconciliation_pkg ─► variance report
        └─► Close dashboard (open periods, batch status, variance)
```

## Implementation sketch
```sql
-- Intercompany mismatch detector between paired entities
SELECT ic.ledger_id,
       SUM(ic.debit_amount) - SUM(ic.credit_amount) AS imbalance,
       COUNT(*) AS line_count
  FROM gl_intercompany_accounts ic
 WHERE ic.period_name = 'FEB-26'
 GROUP BY ic.ledger_id
HAVING SUM(ic.debit_amount) <> SUM(ic.credit_amount);

-- GL vs subledger variance by entity and account
SELECT g.entity_id, g.account_segment1, SUM(g.debit_amount) gl_amt,
       SUM(s.subledger_amt) sub_amt
  FROM gl_balance_v g
  JOIN xx_subledger_balances s
    ON s.entity_id = g.entity_id AND s.account = g.account_segment1
 WHERE g.period_name = 'FEB-26'
   AND SUM(g.debit_amount) <> SUM(s.subledger_amt);
```

## Requirements
- F1: Chart of accounts governance with a documented segment logic per entity.
- F2: SLA accounting templates for AP, AR, FA, Cash, and intercompany.
- F3: Enforced balanced-batch validation before any transfer to GL.
- F4: Automated intercompany elimination for all 15 entity pairings.
- F5: `xx_gl_reconciliation_pkg` producing GL↔subledger variance reports.
- F6: Multi-currency revaluation and translation with rate sourcing documented.
- F7: Close dashboard: open periods, batch status, variance, elapsed days.
- F8: Idempotent re-run design so a failed close can be safely retried.
- F9: SOX control evidence for each close step (who, when, what, approval).
- F10: Period close checklist automation with electronic sign-off.
- NF1: Close completes in 5 business days.
- NF2: Zero unexplained reconciliation variance at sign-off.
- NF3: Zero missed intercompany eliminations.
- NF4: Security baseline — SOD on journal posting and period closing.
- NF5: Audit retention for reconciliation and approval evidence.
- NF6: Documented rollback for every accounting configuration change.

## Milestones
- Week 1: Baseline — close calendar, rework causes, variance history, CoA review.
- Week 2: SLA templates rebuilt and signed off by the controller.
- Week 3: Intercompany elimination engine implemented and back-tested.
- Week 4: Balanced-batch gate and reconciliation package live.
- Week 5: Dashboard and control evidence deployed to finance.
- Week 6: First full parallel close with zero unexplained variance.

## Verification
- Two consecutive parallel closes must produce identical GL balances.
- Fault injection: unbalanced batch, duplicate submission, mid-close failure.
- Restore drill verifying balances and SLA configuration survive recovery.
- Finance sign-off that every variance has a documented disposition.

## Rollback
SLA templates are versioned by effective date and reinstatable; the interface
gate is validation-only; elimination rules are rule-driven and reversible.
Document rollback steps for every accounting configuration change.