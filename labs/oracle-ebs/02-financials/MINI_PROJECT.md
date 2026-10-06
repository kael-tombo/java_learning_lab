# Lab 02: Financials (GL + Subledger) — Mini Project

## Goal
Build a working subledger-to-GL close for one month of AP and AR activity in
90 minutes, including an automated reconciliation.

## Requirements
- R1: DDL for a small subledger (invoices), `GL_INTERFACE`, and a custom
      reconciliation table `xx_gl_recon`.
- R2: Insert AP and AR activity and transfer it via the transfer-to-GL flow.
- R3: Balanced interface rows — every batch has equal debits and credits.
- R4: An SLA accounting template mapping one business event to GL accounts.
- R5: `xx_gl_reconciliation_pkg` comparing subledger totals to GL balances by
      account and period, writing variance rows.
- R6: A drill-down query from any GL line back to its source document.
- R7: A multi-currency revaluation step with the resulting entry.
- R8: A close dashboard query showing open periods, batch status, and variance.

## Steps
1. Create the subledger, `GL_INTERFACE`, and `xx_gl_recon` tables with keys.
2. Load 200 AP invoices and 200 AR invoices with at least three currencies.
3. Post the subledger activity into `GL_INTERFACE` using the SLA template.
4. Verify each batch balances before running the transfer to GL.
5. Execute the transfer, then post the resulting summary journals.
6. Run `xx_gl_reconciliation_pkg` and inspect the variance rows.
7. Investigate one variance via the drill-down query; record the root cause.
8. Run revaluation on a foreign-currency balance and post the entry.
9. Build the close dashboard and confirm every period is closed.

## Acceptance criteria
- Every `GL_INTERFACE` batch is balanced and carries a valid `GROUP_CODE`.
- Reconciliation reports zero unexplained variance for the period.
- At least one variance was traced, explained, and resolved in writing.
- Revaluation produces a balanced, reversible entry.

## Stretch
- Add a second SLA template for a different event and show the GL impact.
- Simulate a failed close and add a retry that is safe to run twice.