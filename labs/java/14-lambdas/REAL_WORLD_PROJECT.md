# REAL-WORLD PROJECT — Lambdas: Callback Hell + Capture Bug in Checkout

## Incident Scenario
After a "cleanup" PR converted anonymous classes to lambdas, checkout webhooks fire twice and amounts intermittently show `$0`. Rollback is debated; the lambda diff looks innocent.

## Symptoms
- Captured loop variable pattern: `for (int i...) { on("pay", e -> fees[i].apply(e)); }` — after refactor `i` is no longer effectively final; dev "fixed" with `int[] box = {i}` → all handlers share the last index.
- `this` semantics changed: anonymous `new Handler(){... this ...}` meant the handler; lambda `this` means the enclosing service → audit logger now records service name instead of handler id.
- Checked-exception swallowing: `e -> { try { send(e); } catch (IOException ex) {} }` silently drops failures; retry queue starves.
- Serialization: a `Serializable` lambda stored in HTTP session breaks rolling deploy (different synthetic method) → `InvalidClassException`.

## Investigation Tasks
1. Heap/JFR: `jcmd <pid> GC.heap_dump dump.hprof`; JFR `jdk.ObjectAllocationInNewTLAB` — boxed `int[]`/captured holders dominate.
2. Repro: loop-register 5 handlers, fire events — show all 5 use last fee (capture bug); assert with unit test.
3. Logs: `grep "audit handler=" app.log | sort | uniq -c` — single id proves `this` shift.
4. Threads: `jcmd <pid> Thread.print` — webhook threads blocked on swallowed-exception retry spin (or idle starving).
5. Bytecode: `javap -c -p Router.class | grep invokedynamic` vs old `$1.class` count; confirm metafactory linkage.
6. Session: decode failing session bytes; `grep InvalidClassException` in deploy logs.

## Root Cause
Capture-by-value misunderstood (box-shared mutation), `this` rebinding, empty-catch inside lambda hiding `IOException`, non-stable serializable lambda persisted across deploys.

## Resolution
- Immediate: copy loop var to final local (`int idx = i;`), restore handler-id field explicitly, rethrow as `UncheckedIOException` via `ThrowingConsumer`, stop persisting lambdas (persist data DTO instead).
- Short-term: lint rule banning `int[]`/mutability capture and empty catch in lambdas; `this::` vs `Handler.this` review checklist.
- Long-term: handler registry with named method refs, contract tests per event type, serialization policy (data only).

## Runbook
```
1. jcmd heap dump + JFR 60s; freeze deploy.
2. Apply capture/this/exception hotfix; redeploy one canary.
3. Replay webhook fixtures; assert fee math + audit ids.
4. Purge poisoned sessions; verify InvalidClassException = 0.
5. Land lint rules; close rollback debate with diff memo.
```

## Metrics
- Fee correctness 100% on 1k fixture replays; audit-id cardinality = handler count; webhook DLQ = 0; session deser errors = 0 over 24h.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Lambda expressions tutorial: https://docs.oracle.com/javase/tutorial/java/javaOO/lambdaexpressions.html
- java.util.function API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/function/package-summary.html
