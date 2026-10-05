# REAL-WORLD PROJECT — Functional Programming: Discount Bug Costs $40k

## Incident Scenario
Promo stacking applies twice on retry, and a "pure" tax helper secretly reads a mutable static rate — finance finds $40k over-discount in one weekend.

## Symptoms
- Reducer mutates input cart (`cart.lines.add(...)`) then parallel re-run double-counts; totals differ run-to-run.
- Static `TaxCache.rate` mutated by a background refresh mid-calculation → same cart prices differently within one request.
- `null` coupon means "no coupon" in one method, "error" in another → NPE on retry path.
- Retry re-applies `discount(cart)` on already-discounted cart (non-idempotent) → double dip.

## Investigation Tasks
1. Heap/JFR: `jcmd <pid> GC.heap_dump`; JFR `jdk.ObjectAllocationInNewTLAB` — shared `ArrayList` writes from multiple threads.
2. Logs: `grep "coupon=null\|discount applied" orders.log | head`; correlate duplicate application with retry ids.
3. Repro: single cart through `applyAll` twice — show total drops second time (non-idempotent); run 50x parallel, collect variance.
4. Threads: `jcmd <pid> Thread.print` — background refresher writing static rate during request threads.
5. Correctness: golden diff — legacy spreadsheet total vs engine total per order; list mismatches by rule.

## Root Cause
Impure "pure" core (input mutation + static mutable rate), null-as-signal ambiguity, non-idempotent rules re-applied on retry without guard.

## Resolution
- Immediate: defensive copies + unmodifiable lists, inject rate as parameter (no static read), `Optional<Coupon>` + `Result` errors, idempotency key per cart (skip if already applied).
- Short-term: purity code review checklist, property tests (apply-twice ≡ apply-once where required), retry-safe contract tests.
- Long-term: functional-core/imperative-shell split enforced by package boundary (ArchUnit), audit log of rule inputs/outputs.

## Runbook
```
1. Dump heap + JFR; freeze promo.
2. Deploy copy-on-write + injected-rate hotfix to canary.
3. Replay weekend orders; diff vs finance sheet to $0.
4. Backfill over-discount report; issue credits.
5. Land ArchUnit purity rule + idempotency tests.
```

## Metrics
- Replay determinism 50/50 identical; over-discount = $0 on replay; NPE rate = 0; retry double-apply = 0 over 10k simulated retries.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.util.function API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html
- Stream package (map/filter/reduce model): https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html
