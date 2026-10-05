# REAL-WORLD PROJECT — Pattern Matching: Guard Swallows VIP Refunds

## Incident Scenario
VIP refunds silently route to standard queue for two weeks; SLA breaches surface in a QBR, not in alerts. The switch "looks right."

## Symptoms
- Guard order bug: `case Paid p when p.amount() > 0 -> standard` placed before `case VipPaid v -> vip` → VIP (subtype of Paid) always matches first (dominance avoided only because guard, but logic shadows).
- `case null` missing → NPE on tombstone events; catch-all logs as "unknown" hiding the null source.
- Guard with side effect (`case E e when audit(e)`) runs audit twice (pattern evaluation) → double-charge audit ledger.
- One service on JDK 17 (no record patterns) silently skips new branch via `default` → divergent behavior across fleet.

## Investigation Tasks
1. Source: list switch order; write truth table (VipPaid × guard) proving shadowing.
2. JFR/logs: `grep "standard-queue.*vip\|NullPointer.*handle" events.log`; queue mixes counted.
3. Heap: `jcmd <pid> GC.heap_dump` — audit-ledger duplicate entries for same event id.
4. Repro: 4-case fixture (vip, paid, null, unknown) — show misroute + NPE before fix, correct after.
5. Fleet: `java -version` per node; diff behavior matrix JDK17 vs 21.

## Root Cause
Over-broad guarded supertype case shadowing subtype, missing `case null`, side-effecting guard evaluated multiple times, fleet JDK skew with default-masked divergence.

## Resolution
- Immediate: subtype-first ordering (VipPaid before Paid), explicit `case null -> rejected`, pure guards (audit moved to arm), align fleet JDK + remove masking default.
- Short-term: ordering unit tests per variant, guard-purity lint, JDK-version gate in deploy.
- Long-term: sealed-event router library shared across services, variant-matrix contract tests.

## Runbook
```
1. Dump switch source + versions fleet-wide; pause VIP auto-route.
2. Reorder + null-case + pure-guard hotfix to canary.
3. Replay 2 weeks VIP events; verify vip-queue 100%.
4. Reconcile audit ledger duplicates.
5. Land ordering + version gates in CI.
```

## Metrics
- VIP misroute = 0 over 5k replay; NPE = 0 on tombstones; audit duplicates = 0; fleet JDK uniform 21+.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JEP 441 Pattern Matching for switch: https://openjdk.org/jeps/441
- Switch tutorial (expressions/patterns): https://docs.oracle.com/javase/tutorial/java/nutsandbolts/switch.html
