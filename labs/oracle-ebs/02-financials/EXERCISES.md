# EXERCISES — Financials

## 1. Trace one invoice end-to-end (beginner)
In a sandbox, create one AP invoice per Step 4.1, run `CREATE_EVENT` +
`PROCESS_EVENT`, then query the SLA lines (Step 4.2). Verify
`accounted_dr == accounted_cr` and the segment derivation matches the
mapping. *Reflection: which step would break first if the mapping used
`SUBSTR(INVOICE_NUM,5,3)` instead?*

## 2. Break the transfer, read the log (beginner)
Submit `APXTRAMTHX` for a period with no new events. Check request status
and output. Then submit for `JUL-26` after Step 4 and confirm GL rows
appear. Document the two log signatures (nothing-to-do vs transferred).

## 3. Seed an UNMATCHED case (intermediate)
Post an AP invoice but *skip* the SLA transfer for it. Run
`run_period_reconciliation` and confirm the combination shows UNMATCHED
with difference = invoice amount. Then transfer + re-run → MATCHED.
This is the daily-recon loop in miniature.

## 4. FX tolerance tuning (intermediate)
Insert SLA lines with entered/accounted diffs of 0.005, 0.01, and 0.05 in
a non-USD currency. Run `xx_reconcile_multi_currency`. Which rows flag?
Justify the 0.01 threshold against the walkthrough's rounding analysis.

## 5. Close-dashboard drill (advanced)
Populate a test period with: 3 posted + 2 unposted journals, 1 approved
but unaccounted AP invoice, and 1 UNMATCHED recon row. Query
`xx_period_close_dashboard` and verify all four counters. Then write the
coordinator runbook: thresholds per counter that page vs wait-till-morning.
