# REAL-WORLD PROJECT — Optional: get() Roulette Takes Down Search

## Incident Scenario
Search p99 spikes and occasional 500s after an "Optional migration" that wrapped everything — including fields — in Optional. Heap grows, NPEs persist.

## Symptoms
- `Optional<User>` **field** in entity → Jackson serializes as `{"present":true}`; frontend breaks; DB mapper stores wrapper `toString` garbage.
- `opt.get()` without check in 14 places → `NoSuchElementException` replaces old NPE, same 500 rate with new name.
- `orElse(expensiveFallback())` evaluates fallback on every hit (cache rebuild, 40ms) → p99 +40ms even when Optional present.
- `Optional.of(legacyNullable)` instead of `ofNullable` → immediate NPE on legacy null rows during backfill.

## Investigation Tasks
1. Heap/JFR: `jcmd <pid> GC.heap_dump`; histogram `Optional` count (millions = field/collection abuse); JFR `jdk.ExecutionSample` on fallback method (always-on proof).
2. Logs: `grep "NoSuchElement\|MismatchedInput.*present" app.log | wc -l`; 500-rate by endpoint before/after migration.
3. Threads: `jcmd <pid> Thread.print` — search threads in fallback rebuild (stack evidence of eager eval).
4. Repro: present-Optional through `orElse(expensive)` with counter — counter increments (eager); `of(null)` throws vs `ofNullable` empty.
5. API: `curl` entity JSON showing `present` wrapper leak.

## Root Cause
Optional used as field/param type, unchecked `get()`, eager `orElse` on hot path, `of` vs `ofNullable` confusion on legacy data.

## Resolution
- Immediate: unwrap fields (nullable + documented or NullObject), replace `get()` with `orElseThrow/match`, `orElse` → `orElseGet` on hot path, `of` → `ofNullable` at legacy boundary.
- Short-term: ban-test (no Optional fields/params/get) in CI, 500-dashboard by exception type, JSON contract tests.
- Long-term: absence policy (Optional returns only + empty-collection rule), Either for error reasons where "why absent" matters.

## Runbook
```
1. Heap dump + 500/log census; freeze backfill.
2. Unwrap fields + fix terminals + lazy defaults to canary.
3. Replay search mix; verify p99 back + 500s = 0.
4. Rebuild corrupted rows from source; verify JSON shape.
5. Land ban-test + contract tests.
```

## Metrics
- NoSuchElement 500s = 0; p99 −40ms to baseline; Optional instances −90% in heap; contract tests green on all entities.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Optional API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html
- Optional tutorial (null-handling): https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html
