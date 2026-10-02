# CODE_DEEP_DIVE — Financials walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. SLA setup (Steps 2–3, lines 70–129)

- **Method query** joins `XLA_ACCOUNTING_METHODS_B` to
  `XLA_APPLICABLE_ACCOUNTING_METHODS` on `accounting_method_id`,
  filtered `enabled_flag='Y'` — the "what may this app use" list.
- **`CREATE_ACCOUNTING_METHOD('GLOBAL_IC_ACCT', …, app 200)`**: custom
  method, type `E` (user-defined), scoped to AP. One method per module
  is the norm; custom methods only for intercompany/legal edge cases.
- **`CREATE_LINE_TYPE('AP_ACCRUAL', …, DR)`** + **`CREATE_MAPPING
  ('AP_SEG1_COMPANY', AP_INVOICES_ALL.INVOICE_NUM → SEGMENT1 via
  SUBSTR(...,1,3))`**: the line-type fixes debit/credit direction; the
  mapping fixes segment derivation. Both are metadata — wrong here means
  wrong everywhere downstream, silently.

## 2. Invoice → event → entries (Step 4, lines 135–225)

- Header/line/distribution inserts use `ap_invoices_all_s.NEXTVAL` for the
  id and a derived `INV-<id>` number; note `accounting_event_id=NULL`
  until validation creates the event.
- `CREATE_EVENT(INVOICE_VALIDATION, SYSDATE, 'JUL-26')` then
  `PROCESS_EVENT` — two-phase: declare, then run the SLA engine.
- The SLA query joins `XLA_AE_HEADERS ⨝ XLA_AE_LINES ⨝
  GL_CODE_COMBINATIONS_KFV` on `ae_header_id` + `code_combination_id`,
  filtered `application_id=200` + the event id, ordered by `je_line_num`.
  `accounted_dr/cr` (ledger currency) vs `entered_dr/cr` (source currency)
  is the pair the FX procedure later compares.

## 3. Transfer + post (Steps 5–6, lines 230–306)

- `FND_REQUEST.SUBMIT_REQUEST('SQLAP','APXTRAMTHX', period, 'BOTH','Y')`
  — transfer program with post-to-GL flag; returns `request_id` for
  monitoring. `COMMIT` after submit (request row must persist).
- Batch/header creation via `GL_JE_BATCHES_PKG`/`GL_JE_HEADERS_PKG` with
  balanced `running_total_dr/cr = 15000`; `GL_JE_POSTING_PKG.POST`
  returns status + message — always capture both (the walkthrough prints
  both for exactly this reason).

## 4. Reconciliation package (Step 7, lines 315–531)

- `compare_ap_gl_balances`: cursor aggregates AP distributions joined to
  invoices within the period's date range (`gl_periods` bounds),
  `approval_status='APPROVED'`; per combination, selects the GL balance
  with `NO_DATA_FOUND → 0` (missing GL row = zero, not error);
  `difference = subledger − gl`; `NVL(difference,0)=0 → MATCHED`.
- `run_period_reconciliation`: writes `IN_PROGRESS` log row, loops both
  TABLE() functions inserting into `xx_gl_recon_results`, counts
  matches/unmatches + total diff, updates log to
  `COMPLETE`/`COMPLETE_WITH_EXCEPTIONS`, single `COMMIT`.
- **Drill-down** (Step 8): `reference_1 = TO_CHAR(ae_header_id)` join +
  `event_type_code CASE` to invoice/check/receipt numbers.
- **FX** (Step 9): groups non-USD currencies, `HAVING ABS(…)>0.01`.
- **Dashboard** (Step 10): one view, four correlated subqueries
  (posted/unposted journals, unaccounted AP, unreconciled diff).
