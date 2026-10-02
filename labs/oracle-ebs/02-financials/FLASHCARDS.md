# FLASHCARDS — Financials

| # | Front | Back |
|---|-------|------|
| 1 | Five hops? | Txn → SLA/XLA → GL_INTERFACE → GL_POST → GL_BALANCES → recon. |
| 2 | SLA role? | Single accounting engine: events → journal lines, full audit. |
| 3 | Attribute mapping? | Source column → GL segment (e.g. INVOICE_NUM→SEGMENT1). |
| 4 | Line type fixes? | DR/CR direction per entry type (e.g. AP_ACCRUAL = DR). |
| 5 | Event before lines? | CREATE_EVENT declares; PROCESS_EVENT derives lines. |
| 6 | entered vs accounted? | Source-currency vs ledger-currency amounts. |
| 7 | Transfer program? | `APXTRAMTHX` via FND_REQUEST; returns request_id. |
| 8 | Post package returns? | Status + message — capture both, always. |
| 9 | Pipelined comparator why? | Streams rows (PIPE ROW), constant memory over millions. |
| 10 | MATCHED condition? | `NVL(subledger − gl, 0) = 0` per code combination. |
| 11 | Missing GL row = ? | Balance 0 (timing state), UNMATCHED, not an error. |
| 12 | Drill-down key? | `GL_JE_LINES.reference_1 = TO_CHAR(ae_header_id)`. |
| 13 | FX tolerance? | Flag only `ABS diff > 0.01` (rounding noise below). |
| 14 | Dashboard's 4 counters? | Posted, unposted, unaccounted AP, unreconciled diff. |
| 15 | Close targets? | 100% match, <72 h, <15 min SLA batches, 0 unposted. |
