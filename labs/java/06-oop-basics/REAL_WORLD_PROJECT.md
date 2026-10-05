# REAL-WORLD PROJECT — OOP Basics: Negative Balances After Midnight Batch

## Incident Scenario
00:30 — batch posts 47 accounts negative beyond overdraft limit. No exception; invariant "balance ≥ -500" violated silently.

## Symptoms
- `Account.balance` public mutable; batch job sets it directly, skipping validation in `withdraw()`.
- Constructor allows `new Account(null, -999999)`; `static` `interestRate` mutated per-instance confusion.
- Logs show `toString` useless (`Account@7a3f`) — triage slow.

## Investigation Tasks
1. Logs/DB: `SELECT * WHERE balance < -500`; correlate with batch window.
2. Code: find all direct field writes `grep -rn "\.balance ="`; confirm bypass path.
3. Heap: `jcmd GC.class_histogram` + heap dump to count invalid `Account` instances.
4. JFR: `jdk.ExceptionThrown` shows zero validation exceptions during batch (proof validation skipped).
5. Repro: construct invalid accounts in JShell; show invariant breach.

## Root Cause
Broken encapsulation — public mutable state + validation only in one method, not constructor; static/instance confusion; missing domain invariant enforcement.

## Resolution
- Immediate: freeze batch; private fields + validating ctors/factories; backfill balances from ledger (source of truth); useful `toString`/audit log.
- Short-term: `record` for receipts, `final` fields, ArchUnit "no public fields" gate; invariant tests.
- Long-term: aggregate-root discipline (all mutations via methods), event-sourced ledger, nightly invariant-check job + alert.

## Runbook
```
1. Halt batch; snapshot balances.
2. Deploy encapsulated model; dry-run batch on staging clone.
3. Recompute from ledger; reconcile + notify.
4. Enable invariant-check alert.
```

## Metrics
- Invariant violations = 0 for 30d; public mutable fields = 0; batch recon pass 100%; triage time < 15 min (readable toString/logs).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Classes/objects & encapsulation: https://docs.oracle.com/javase/tutorial/java/javaOO/classes.html
- Records: https://docs.oracle.com/en/java/javase/21/docs/specs/records.html
