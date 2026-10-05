# REAL-WORLD PROJECT — Java 21 Features: Half-Migrated Service Regresses

## Incident Scenario
Java 21 upgrade ships records + virtual threads but keeps old `visitor` + `synchronized` cache. Result: pinning stalls plus a JSON library that can't deserialize records in prod.

## Symptoms
- Jackson (old version) deserializes `record Order` as nulls (no canonical-ctor support in pinned version) → downstream NPE pricing $0.
- `synchronized` cache on virtual-thread path pins carriers → p99 doubles (JFR `jdk.VirtualThreadPinned` storm).
- Sealed `Payment` switch kept a `default: throw` from migration; new `Voucher` permit silently hits default in one service still on old switch → wrong decline.
- `--enable-preview` string-templates code merged to main → CI (no preview flag) fails, blocking hotfix.

## Investigation Tasks
1. JFR: `jdk.VirtualThreadPinned` + `jdk.Deserialization` (if mapped) or allocation of fallback maps; `jdk.JavaMonitorEnter` on cache lock.
2. Heap: `jcmd <pid> GC.heap_dump` — `LinkedHashMap` fallback objects where records expected null.
3. Logs: `grep "InvalidDefinitionException\|MismatchedInput\|pinned\|preview" app.log`; Jackson version dump.
4. Threads: `jcmd <pid> Thread.print` — carriers BLOCKED in synchronized cache.
5. Repro: record round-trip on prod Jackson version (fails) vs bumped version (passes); guarded-switch test with new permit.

## Root Cause
Partial modernization: outdated serialization lib, synchronized-on-virtual-thread pinning, stale default-branch switch, preview feature merged without build policy.

## Resolution
- Immediate: bump Jackson (record module), `synchronized` → `ReentrantLock`, add explicit `Voucher` case everywhere, revert preview-template code to text blocks.
- Short-term: version-compatibility matrix test (record round-trip), pinning alert, exhaustive-switch lint (no default on sealed).
- Long-term: modern-Java migration checklist (lib compat → types → patterns → Loom), preview-feature ban on main.

## Runbook
```
1. JFR + heap dump; pin Jackson version + flag carriers.
2. Patch Jackson + lock + switch cases to canary.
3. Replay failed orders; verify totals + p99.
4. Rebill $0-priced orders; confirm 0 recurrence 24h.
5. Land compat + pinning + no-preview gates.
```

## Metrics
- Record deser failures = 0; pinned events ≈ 0; p99 at pre-migration baseline; exhaustive-switch coverage 100% (mutation: new permit breaks build).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JDK 21 project page: https://openjdk.org/projects/jdk/21/
- Java SE 21 docs: https://docs.oracle.com/en/java/javase/21/
