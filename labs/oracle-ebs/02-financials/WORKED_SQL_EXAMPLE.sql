-- WORKED_SQL_EXAMPLE — Financials (GL ↔ Subledger)
-- Companion to PROBLEM_WALKTHROUGH.md Steps 2–10. Sandbox only.

---------------------------------------------------------------
-- §1. Inspect the SLA setup (Steps 2–3)
---------------------------------------------------------------

-- 1a. Which accounting methods can AP use?
SELECT lam.accounting_method_code, lam.accounting_method_name,
       lam.accounting_method_type, laam.application_id
FROM   xla_accounting_methods_b lam,
       xla_applicable_accounting_methods laam
WHERE  lam.accounting_method_id = laam.accounting_method_id
AND    lam.enabled_flag = 'Y'
AND    laam.application_id = 200;  -- AP

-- 1b. SLA lines for one event (the Step 4.2 query, parameterized)
-- Bind :ev = accounting_event_id from CREATE_EVENT.
SELECT xah.event_type_code, xah.accounting_date, xal.je_line_num,
       gcck.segment1 AS company, gcck.segment2 AS department,
       gcck.segment3 AS account,
       xal.accounted_dr, xal.accounted_cr,
       xal.currency_code, xal.entered_dr, xal.entered_cr
FROM   xla_ae_headers xah,
       xla_ae_lines xal,
       gl_code_combinations_kfv gcck
WHERE  xah.ae_header_id = xal.ae_header_id
AND    xal.code_combination_id = gcck.code_combination_id
AND    xah.application_id = 200
AND    xah.accounting_event_id = :ev
ORDER  BY xal.je_line_num;

---------------------------------------------------------------
-- §2. One-invoice end-to-end smoke (Step 4.1, minimal)
---------------------------------------------------------------

-- Creates header + line + distribution, then raises the event.
-- Verify with §1b afterwards; accounted_dr must equal accounted_cr.
-- (Full block in walkthrough Step 4.1; run it, then continue here.)

-- 2a. Did the event transfer? (unaccounted-AP pattern from dashboard)
SELECT COUNT(*) AS unaccounted
FROM   ap_invoices_all ai
WHERE  ai.approval_status = 'APPROVED'
AND NOT EXISTS (
  SELECT 1 FROM xla_ae_headers xah
  WHERE  xah.entity_id = ai.invoice_id
  AND    xah.event_type_code = 'INVOICE_VALIDATION'
  AND    xah.gl_transfer_flag = 'Y'
);

---------------------------------------------------------------
-- §3. Reconciliation spot-checks (Step 7)
---------------------------------------------------------------

-- 3a. AP vs GL for one combination + period (bind :ccid, :period)
SELECT
  (SELECT NVL(SUM(NVL(amount,0)),0) FROM ap_invoice_distributions_all
   WHERE  dist_code_combination_id = :ccid) AS subledger_amt,
  (SELECT NVL(SUM(period_net_dr - period_net_cr),0) FROM gl_balances
   WHERE  code_combination_id = :ccid
   AND    period_name = :period AND actual_flag = 'A') AS gl_amt
FROM DUAL;

-- 3b. Run the package for a period, then read results + log
BEGIN
  xx_gl_reconciliation_pkg.run_period_reconciliation(:period, 101);
END;
/

SELECT recon_status, COUNT(*) AS n, SUM(ABS(difference)) AS total_abs_diff
FROM   xx_gl_recon_results
WHERE  period_name = :period
GROUP  BY recon_status;

SELECT status, match_count, unmatch_count, total_difference
FROM   xx_gl_recon_log
WHERE  period_name = :period;

---------------------------------------------------------------
-- §4. Drill-down + FX + dashboard (Steps 8–10)
---------------------------------------------------------------

-- 4a. GL journal line → source document (bind :je_header_id)
-- (Full CASE query in walkthrough Step 8; pattern below for AP leg.)
SELECT xah.event_type_code,
       (SELECT ai.invoice_num FROM ap_invoices_all ai
        WHERE  ai.invoice_id = xah.entity_id) AS source_doc,
       xal.accounted_dr, xal.accounted_cr
FROM   xla_ae_headers xah, xla_ae_lines xal
WHERE  xah.ae_header_id = xal.ae_header_id
AND    EXISTS (
  SELECT 1 FROM gl_je_lines gjl
  WHERE  gjl.reference_1 = TO_CHAR(xah.ae_header_id)
  AND    gjl.je_header_id = :je_header_id
);

-- 4b. FX suspects above tolerance (bind :period)
SELECT currency_code, entered_balance, accounted_balance, fx_difference
FROM   xx_fx_recon_results
WHERE  period_name = :period AND ABS(fx_difference) > 0.01;

-- 4c. Close dashboard snapshot (bind :period via set_of_books 101)
SELECT * FROM xx_period_close_dashboard
WHERE  period_name = :period;
