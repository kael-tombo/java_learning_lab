# REAL-WORLD PROJECT — Enums: Payment Status Deploy Breaks Checkout

## Incident Scenario
Payments team adds `REFUNDED_PARTIAL` to `PaymentStatus` and persists
`ordinal()`. After deploy, old rows decode to wrong statuses — `CAPTURED`
reads as `REFUNDED`, refunds fire on paid orders. Rollback debated mid-peak.

## Symptoms
- Refund rate spikes 40x; support queue floods with "charged then refunded".
- `valueOf` throws `IllegalArgumentException: No enum constant` on new code
  seen by old canary instances; error rate 12% during mixed-version window.
- DB column holds ints (0–5); new deploy shifts every ordinal after index 3.
- `switch` without default silently falls through on the new constant.

## Investigation Tasks
1. Heap/dump: `jcmd <pid> GC.heap_dump` not central — instead snapshot DB:
   `SELECT status, COUNT(*) GROUP BY status` before/after deploy diff.
2. JFR: `jcmd <pid> JFR.start duration=120s filename=pay.jfr`; check
   `jdk.JavaExceptionThrow` for `IllegalArgumentException` spike + stacks.
3. Logs: `grep "No enum constant\|IllegalTransition" app.log | sort | uniq -c`.
4. Threads: `jcmd <pid> Thread.print` to confirm refund workers active, not stuck.
5. Repro: load prod-code snapshot in staging; insert old ordinals, decode with
   new enum — show shift; replay new code on old binary — show `valueOf` crash.
6. Code audit: `grep -rn "ordinal()\|valueOf(" src/`; list every switch on
   `PaymentStatus` and check exhaustiveness/default.
7. Wire check: inspect API payloads — int vs string code on the wire.

## Root Cause
Persisting `ordinal()` couples storage to declaration order; adding a constant
mid-enum rewrites history. `valueOf` is strict (crashes on unknown), switches
non-exhaustive, and mixed-version rollout had no forward-compat `UNKNOWN`.

## Resolution
- Immediate: freeze deploys; backfill map ordinal->code with migration table;
  hotfix `fromCode` with `UNKNOWN` fallback; disable auto-refund on UNKNOWN.
- Short-term: migrate column to `code VARCHAR`; JPA converter + Jackson
  `@JsonValue/@JsonCreator`; exhaustive switch expressions; compat tests
  (old binary vs new codes, new binary vs old rows).
- Long-term: enum-governance rule (append-only + review, never reorder),
  ArchUnit ban on `ordinal()` persistence, contract tests on status codes.

## Runbook
```
1. Halt refund job; snapshot status counts + JFR + error logs.
2. Deploy hotfix: fromCode/UNKNOWN guard + refund-require-explicit-status.
3. Backfill ordinals -> codes via mapping table; verify counts reconcile.
4. Migrate column to VARCHAR code; enable exhaustive-switch lint.
5. Postmortem: append-only policy + mixed-version canary test.
```

## Metrics
- Refund anomaly = 0 (rate back to baseline ±0.1%); `valueOf` crashes = 0.
- 100% rows decode to pre-deploy meaning; mixed-version error rate < 0.01%.
- All switches exhaustive; `ordinal()` persistence grep = 0 hits.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Enum API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Enum.html
- Enum tutorial: https://docs.oracle.com/javase/tutorial/java/javaOO/enum.html
