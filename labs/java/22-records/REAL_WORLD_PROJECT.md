# REAL-WORLD PROJECT — Records: Shared List Mutates "Immutable" Orders

## Incident Scenario
"Immutable" `record Order(List<LineItem>)` leaks its list; a promo thread adds a freebie to one order and 300 unrelated orders change totals. Finance flags phantom revenue.

## Symptoms
- Compact ctor assigns `this.items = items` directly → caller retains alias; later `callerList.add(freebie)` mutates stored order.
- Jackson deserializes to unmodifiable? No — old config gives mutable `ArrayList` inside record → post-load mutation path open.
- `Money` as `record` with `double` amount → `0.1+0.2` rounding drifts totals by cents across 100k orders.
- Log shows `Order[...]` toString with huge lists (10k lines) → log volume 10x, disk fills.

## Investigation Tasks
1. Heap: `jcmd <pid> GC.heap_dump`; find shared `ArrayList` referenced by N `Order` records (dominator shows one list, many parents).
2. JFR: `jdk.ObjectAllocationInNewTLAB` — list growth; `jdk.FileWrite` for log spam volume.
3. Logs: `grep "Order\[" app.log | wc -l`; sample one giant toString; correlate promo-thread add with total drift.
4. Repro: construct order from mutable list, mutate list, show `order.items()` changed (alias proof); double-vs-cents drift script.
5. Threads: `jcmd <pid> Thread.print` — promo thread writing while pricing threads read (no lock, assumed immutable).

## Root Cause
Shallow immutability misunderstood (no defensive copy), mutable deserialization target, floating-point money, unbounded toString logging.

## Resolution
- Immediate: `List.copyOf` in compact ctor + null/empty guards, `Money(long cents)` migration with adapter, truncate custom `toString` for large orders.
- Short-term: alias-mutation regression test, money-type lint (ban double for currency), log-size budget.
- Long-term: immutable-domain policy (records + copyOf + with-methods), event-sourced order changes (no in-place adds).

## Runbook
```
1. Heap dump; identify shared lists + drift scope.
2. Deploy copyOf + cents-money hotfix to canary.
3. Replay affected orders; diff totals vs ledger to $0.
4. Purge oversized logs; verify volume back.
5. Land alias + money + log gates in CI.
```

## Metrics
- Alias-mutation test passes (0 shared); money drift = $0 over 100k replay; log volume −90%; phantom-revenue incidents = 0.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JEP 395 Records: https://openjdk.org/jeps/395
- Record API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Record.html
