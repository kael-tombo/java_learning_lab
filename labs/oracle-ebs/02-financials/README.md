# 02 — Financials (GL ↔ Subledger with Reconciliation)

## Overview

Month-end close for 200,000+ monthly subledger transactions (AP/AR/FA):
SLA as the single accounting engine, `GL_INTERFACE` transfer, `GL_POST`,
and an automated reconciliation package (`xx_gl_reconciliation_pkg`) with
GL→subledger drill-down, multi-currency handling, and a close dashboard —
taking close from 8 days to 3.

## Learning Objectives

- [ ] Trace Subledger → SLA (`XLA`) → `GL_INTERFACE` → `GL_POST` → `GL_BALANCES`
- [ ] Configure SLA accounting methods + journal line types + attribute mappings
- [ ] Build pipelined reconciliation (`MATCHED`/`UNMATCHED`) with tolerance-aware FX handling
- [ ] Drill from a GL journal line back to its source document; monitor close via dashboard

## Topics Covered

### 1. SLA engine + journal rules (Steps 2–3)
`XLA_ACCOUNTING_METHODS` query; `CREATE_ACCOUNTING_METHOD`;
`CREATE_LINE_TYPE` (e.g. `AP_ACCRUAL` DR); attribute mapping
(`AP_INVOICES_ALL.INVOICE_NUM → SEGMENT1`). Files: walkthrough Steps 2–3.

### 2. AP invoice → event → SLA entries (Steps 4.1–4.2)
Header/line/distribution inserts; `CREATE_EVENT` (`INVOICE_VALIDATION`)
+ `PROCESS_EVENT`; `XLA_AE_HEADERS/LINES ⨝ GL_CODE_COMBINATIONS_KFV`
query. Files: walkthrough Steps 4.1–4.2.

### 3. Transfer + post (Steps 5–6)
`FND_REQUEST.SUBMIT_REQUEST` (`APXTRAMTHX`); batch/header creation
(`GL_JE_BATCHES_PKG`, `GL_JE_HEADERS_PKG`); `GL_JE_POSTING_PKG.POST`.
Files: walkthrough Steps 5–6.

### 4. Reconciliation + drill-down + FX + dashboard (Steps 7–10)
`xx_gl_reconciliation_pkg` (pipelined AP/AR comparators, `run_period_
reconciliation`, log table); `CASE`-based source-document drill-down;
`xx_reconcile_multi_currency` (0.01 tolerance); `xx_period_close_
dashboard` view. Files: walkthrough Steps 7–10, `WORKED_SQL_EXAMPLE.sql`.

## Prerequisites

- EBS Financials schemas (AP/AR/GL/XLA); PL/SQL packages, pipelined functions
- Concurrent programs (`FND_REQUEST`); period/ledger concepts (`GL_PERIODS`, `GL_BALANCES`)

## Further Reading

- Oracle SLA Implementation Guide (event model, accounting methods)
- `../02-system-administration/` for the `GL_POST` failure mode of this flow
