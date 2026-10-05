# REAL-WORLD PROJECT — Data Types: The $0.01 That Lost $48k

## Incident Scenario
Month-end reconciliation off by $48,231.17 across 2M invoices. Finance escalates; billing service (Java) suspected. No exceptions in logs — silent precision drift.

## Symptoms
- Totals differ between Java service (`double total`) and DB `DECIMAL(19,2)` by cents per invoice, compounding.
- Spot check: `0.1 + 0.2 = 0.30000000000000004` in service logs.
- Overflow side-quest: `int` invoice counter wrapped negative at 2.1B in staging.

## Investigation Tasks
1. Logs: grep billing calc path; confirm `double` in `Invoice.total()` signature.
2. Repro: JShell `double` vs `BigDecimal("19.99")` addition table; scale/rounding audit.
3. Heap/JFR: `jcmd <pid> GC.class_histogram`, JFR `jdk.ObjectAllocationInNewTLAB` to show autoboxed `Double` churn in loop.
4. DB compare: export 1k invoices, recompute both ways, diff histogram.
5. Range: check `int` counters near `Integer.MAX_VALUE`; `jcmd VM.flags` for nothing relevant — code bug confirmed.

## Root Cause
Money stored/computed in `double` (binary floating point) + `HALF_UP` missing; plus `int` counter near overflow. Classic type-choice defect.

## Resolution
- Immediate: hotfix `Money` to `BigDecimal` scale-2 `HALF_EVEN`; recompute + credit affected invoices; freeze payouts 4h.
- Short-term: forbid `double` in money path (ArchUnit rule + grep CI gate); migrate counters to `long`; add reconciliation job DB-vs-service nightly.
- Long-term: `Money` value type + currency; property-based tests (random cents); finance sign-off on rounding policy doc.

## Runbook
```
1. Freeze payouts; snapshot DB totals.
2. Recompute sample both ways; confirm drift pattern.
3. Patch Money→BigDecimal; add rounding tests.
4. Backfill + reconcile; publish credit report.
5. Add ArchUnit + nightly recon alert.
```

## Metrics
- Recon diff = $0.00 for 7 days; p99 calc latency delta < 2%; zero `double` in billing module; counter headroom > 100x.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- BigDecimal API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html
- Primitive data types: https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html
