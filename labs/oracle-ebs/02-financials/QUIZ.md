# QUIZ — Financials

## 1. Name the five hops from subledger transaction to reconciled balance.
<details><summary>Answer</summary>Transaction → SLA/XLA entries → GL_INTERFACE → GL_POST (JE headers/lines) → GL_BALANCES → reconciliation.</details>

## 2. Why must *everything* flow through SLA instead of posting straight to GL?
<details><summary>Answer</summary>Single engine = single audit trail, uniform rules, SOX-traceable event→line lineage. Direct GL writes bypass all of it.</details>

## 3. What does an attribute mapping do, and why is a bad one catastrophic?
<details><summary>Answer</summary>Derives GL segments from source columns (e.g. INVOICE_NUM→SEGMENT1). It's metadata applied to every line — one bad rule mis-codes thousands silently.</details>

## 4. `CREATE_EVENT` then `PROCESS_EVENT` — why two calls?
<details><summary>Answer</summary>Declare the accounting event first, then run the engine against it. Separation lets validation, dating, and period checks happen before any lines exist.</details>

## 5. `accounted_dr` vs `entered_dr`?
<details><summary>Answer</summary>Entered = source currency amount; accounted = ledger-currency amount after FX. Their gap is exactly what the FX procedure measures.</details>

## 6. Why pipelined functions for the comparators?
<details><summary>Answer</summary>`PIPE ROW` streams combinations to the caller without materializing millions of rows in PGA — constant-memory reconciliation.</details>

## 7. `NO_DATA_FOUND → gl_balance := 0`. Why not an error?
<details><summary>Answer</summary>A combination with subledger activity but no GL row yet is a legitimate timing state (transfer pending), not corruption — it reconciles as UNMATCHED with diff = full amount.</details>

## 8. What physically links a GL journal line to its SLA entry?
<details><summary>Answer</summary>`GL_JE_LINES.reference_1 = TO_CHAR(XLA_AE_HEADERS.ae_header_id)` — the drill-down join key.</details>

## 9. Why a 0.01 FX tolerance instead of exact zero?
<details><summary>Answer</summary>FX revaluation rounding creates 0.01–0.03 diffs on correct entries. Zero tolerance flags noise; 0.01 absorbs rounding while catching real errors.</details>

## 10. Daily lightweight recon vs month-end-only: why daily?
<details><summary>Answer</summary>Issues found on day 2 are fixable in minutes; the same issue found on close day blocks 5 accountants. Shift-left the detection.</details>
