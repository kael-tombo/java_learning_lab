# Lab 02: Financials (GL + Subledger) — Vision

## Where this lab takes you
From understanding the accounting engine to closing 200,000 monthly subledger
transactions on time, with a drill-down path from any GL line to its source.

## The Arc
1. **The model** — GL as the single accounting engine; subledgers as feeders.
2. **Transfer** — `GL_INTERFACE` as the only sanctioned bridge into GL.
3. **Summary** — SLA (Summary Ledger) defining what GL lines are created.
4. **Posting** — `GL_POST`, period close, and the transfer-to-GL concurrent flow.
5. **Reconciliation** — automated GL↔subledger matching with variance tracking.
6. **Currency** — multi-currency revaluation and translation.
7. **Visibility** — a close dashboard that shows variance, not just totals.

## Milestones (checkable)
- [ ] M1: Draw the GL→SLA→subledger data flow for AP, AR, and FA.
- [ ] M2: Populate `GL_INTERFACE` correctly with balanced debit/credit rows.
- [ ] M3: Define an SLA accounting template for one business event.
- [ ] M4: Run the transfer-to-GL and post journals for a closed period.
- [ ] M5: Build `xx_gl_reconciliation_pkg` comparing GL and subledger.
- [ ] M6: Explain a variance to its root cause using the drill-down.
- [ ] M7: Revalue a foreign-currency balance and reconcile the reval entry.
- [ ] M8: Produce a close dashboard with open-period and variance metrics.

## Anti-Goals
- Posting to GL via direct DML instead of the interface.
- Treating a balanced trial balance as proof the close is correct.
- Ignoring SLA and letting every subledger line create a GL line.
- Closing a period before the reconciliation reports zero unexplained variance.

## The one-sentence thesis
A close is finished when the drill-down reconciles — not when the trial balance
balances.