# REAL-WORLD PROJECT — Control Flow: Orders Stuck in LIMBO

## Incident Scenario
02:14 — 340 orders stuck in `PENDING` after promo deploy. Payments captured, fulfillment never triggered. Support queue exploding.

## Symptoms
- State column shows `PENDING` despite `paid=true`; logs show `if (status == "PAID")` never true for new events.
- Recent PR added `SHIPPED_PARTIAL` status; old `if-else` chain silently falls to `else { /* ignore */ }`.
- Loop over events uses `==` on Strings + missing `break` causing fall-through double-ship on 12 orders.

## Investigation Tasks
1. Logs: `grep "ignoring event" app.log | sort | uniq -c`; correlate with deploy timestamp.
2. Code: map every branch of `transition()`; list unhandled enum values.
3. Repro: feed prod event sample through state machine in JShell; assert expected states.
4. Runtime: `jcmd <pid> Thread.print` to confirm worker threads idle (not deadlock — logic skip); JFR `jdk.JavaMonitorWait` to rule out contention.
5. Data: `SELECT status, count(*) GROUP BY status` before/after; count double-ships.

## Root Cause
String `==` comparison + non-exhaustive `if-else` with silent `else-ignore`; new enum value unhandled; fall-through in legacy switch. Control-flow debt detonated by feature flag.

## Resolution
- Immediate: rollback promo flag; patch `equals`/exhaustive switch expression; replay 340 events from outbox; refund 12 double-ships.
- Short-term: enum + switch expression (compiler-enforced exhaustiveness); guard-clause refactor; mutation tests on transitions.
- Long-term: state-machine library (Spring StateMachine or explicit table) + transition audit log + alert on `ignored-event` counter.

## Runbook
```
1. Freeze fulfillment; snapshot order-state counts.
2. Ship exhaustive-switch fix; replay outbox in dry-run.
3. Replay live; verify zero PENDING-paid.
4. Refund double-ships; post-mortem branch-coverage gate.
```

## Metrics
- Ignored-event count = 0; branch coverage on transition ≥ 95%; stuck-order SLO < 0.01%; replay success 100%.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Switch expressions: https://docs.oracle.com/en/java/javase/21/docs/specs/switch-expressions.html
- Spring StateMachine: https://docs.spring.io/spring-statemachine/docs/current/reference/
