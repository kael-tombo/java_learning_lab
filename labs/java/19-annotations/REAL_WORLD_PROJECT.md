# REAL-WORLD PROJECT — Annotations: Silent Validation Bypass Bills Wrong Tier

## Incident Scenario
Enterprise customers are billed on the free tier for a week. `@Valid` cascade "works in tests" but nested `Plan.limits` objects skip validation in production.

## Symptoms
- `@Valid` placed on field but validator only checks top level (no cascade loop) → nested `@Min(1)` violations pass silently.
- Custom annotation uses `RetentionPolicy.CLASS` but runtime lookup via `getAnnotation` → always null, fallback permits everything.
- `@Target` missing `TYPE_USE` so `List<@NonNull String>` doesn't compile; dev drops nullness checks entirely.
- Processor logs duplicates with `System.out` instead of `Messager.error` → duplicate `@Route` ships, last-wins routing bills wrong handler.

## Investigation Tasks
1. Bytecode/reflect: `javap -v Dto.class | grep RuntimeVisibleAnnotations` — missing entry proves CLASS-retention bug.
2. JFR/heap: `jcmd <pid> GC.heap_dump` not central; instead `jcmd <pid> VM.system_properties` + config dump showing validator version.
3. Logs: `grep "violation\|billed tier" billing.log | head -50`; count free-tier bills for enterprise ids.
4. Repro: nested DTO with violating child — `validate()` returns empty (before fix); duplicate-route fixture compiles when it shouldn't.
5. Threads: `jcmd <pid> Thread.print` — router threads serving wrong handler (stack shows fallback method).

## Root Cause
Non-cascading validator, wrong retention (CLASS vs RUNTIME), over-broad/missing targets, processor failures downgraded to stdout warnings.

## Resolution
- Immediate: cascade loop for `@Valid` (fields + collections), fix retention to RUNTIME, add TYPE_USE target, `Messager error()` on duplicates + CI compile-fail test.
- Short-term: violation-metric + alert (validation-pass rate drop), annotation review checklist (retention/target table).
- Long-term: move route-conflict + nullness to compile-time (checker-style), contract tests per DTO graph depth.

## Runbook
```
1. Dump annotations (javap) + validator version; freeze billing run.
2. Deploy cascade+retention hotfix to canary.
3. Replay week's DTOs; assert violations caught, rebill diff.
4. Enable duplicate-route build gate; verify red fixture fails.
5. Land retention/target lint + dashboard.
```

## Metrics
- Nested violations caught 100% (fixture suite); wrong-tier bills = 0 over 7d; duplicate-route builds fail in < 1 min; validator p99 < 50µs/object.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.lang.annotation API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/annotation/package-summary.html
- Annotations tutorial: https://docs.oracle.com/javase/tutorial/java/annotations/
