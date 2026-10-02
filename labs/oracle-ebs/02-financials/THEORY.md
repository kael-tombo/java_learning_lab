# THEORY — GL ↔ Subledger Accounting Flow

## 1. The pipeline (memorize the five hops)

```
AP/AR/FA transaction → SLA/XLA (event → journal lines)
  → GL_INTERFACE → GL_POST (GL_JE_HEADERS/LINES)
  → GL_BALANCES → reconciliation (SLA ↔ GL)
```

Every hop has one owner table set and one failure signature. Close
failures are diagnosed by walking the pipeline forward from the last
good hop — never by staring at `GL_BALANCES` first.

## 2. SLA is the single accounting engine

Nothing posts directly to GL. A subledger transaction raises an
**event** (`INVOICE_VALIDATION`, …); the SLA event model (method +
line types + attribute mappings) derives journal lines into
`XLA_AE_HEADERS/LINES` with full audit columns (`created_by`,
`creation_date`, per-line updater). The attribute mapping
(`INVOICE_NUM → SEGMENT1` via `SUBSTR`) is where source data becomes
chart-of-accounts data — and where a bad transformation silently
mis-codes thousands of lines. Map early, transform minimally, keep the
trail.

## 3. Reconciliation is a three-way match

Subledger detail → SLA entries → GL balances. The package compares per
`code_combination_id`: subledger sum vs `GL_BALANCES(period_net_dr -
period_net_cr)`, difference → `MATCHED`/`UNMATCHED`. Two design points:

- **Pipelined functions** stream rows to the caller (`PIPE ROW`) instead
  of materializing — the AP comparator can feed millions of combinations
  without a giant collection in PGA.
- **Tolerance, not zero**: FX rounding creates 0.01–0.03 diffs; the
  multi-currency procedure flags only `fx_diff > 0.01`. Zero-tolerance
  reconciliation drowns in noise; tiered tolerances (general vs clearing
  accounts) are the production answer.

## 4. Drill-down and the dashboard close the loop

`reference_1 = TO_CHAR(ae_header_id)` on `GL_JE_LINES` is the physical
link enabling GL→SLA→source-document drill-down (the `CASE` on
`event_type_code` picks invoice/check/receipt). The dashboard view turns
close status into counters: posted vs unposted journals, unaccounted AP
invoices (approved but no `INVOICE_VALIDATION` event transferred), and
total unreconciled difference — the three numbers a close coordinator
watches. Target state from the walkthrough: 100% match, <72 h close,
<15 min SLA batches.
