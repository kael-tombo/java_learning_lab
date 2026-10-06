# Distributed Transactions - Vision

## Why This Lab Exists
The single ACID database was the last great simplification in computing. Once
your transaction crosses a service boundary, it is gone, and the choices that
replace it have real costs that are rarely written down. This lab exists so
those costs are explicit before an incident, not after.

## The Mental Model
Every distributed transaction mechanism trades **atomicity** against
**blocking** and **latency**:

```
  2PC      : atomic  + BLOCKING  + 2 RTTs    -> the coordinator can hang
  3PC      : atomic  + less blocking, + extra RTT + still assumes no partition
  Saga     : no global atomicity, NO blocking, but partial states are visible
  Outbox   : local atomicity + at-least-once delivery (no 2PC at all)
  Calvin   : atomic + non-blocking, but requires deterministic execution
```

## The Decision You Are Actually Making
There is no "distributed transaction" — there is only a choice about **which
failure mode you prefer**:

- 2PC → prefer *availability loss* (a coordinator or participant stalls).
- Saga → prefer *intermediate visibility* (an order exists without its payment).
- Outbox → prefer *duplicate delivery* (consumers must be idempotent).

You cannot avoid all three. Pick one deliberately.

## What You Should Be able To Do
- Explain 2PC's blocking window and why a coordinator recovery log is mandatory.
- Design a saga and its compensations, and name which compensations are
  *impossible* (an emailed invoice cannot be unsent).
- Implement the transactional outbox, including the CDC/poller that drains it.
- Make any handler idempotent using a key plus a result cache, with a TTL you
  can defend.
- Decide saga choreography vs. orchestration and state the failure-visibility
  trade-off for your case.
- State what "exactly-once" you can actually achieve, and where the illusion
  comes from.

## The Anti-Goals
- Not "use 2PC everywhere". Its cost is paid on every write, always.
- Not "make the saga look atomic". It is not; write down the visible
  intermediate states.
- Not exactly-once without a deduplication mechanism. Duplicates will happen.

## Success Criteria
Given a cross-service operation, you can produce: the saga steps, each
compensation, the compensating action for each non-compensatable step, the
idempotency key derivation, and the timeout/retry policy per step.

## How To Use This Lab
1. `THEORY.md` for 2PC/3PC, sagas, outbox, Calvin/Spanner.
2. `MATH_FOUNDATION.md` for 2PC cost, saga failure combinatorics, FLP.
3. `CODE_DEEP_DIVE.md` for outbox, idempotency store, saga orchestrator.
4. `MINI_PROJECT.md` to run a saga with real failures injected.
5. `REAL_WORLD_PROJECT.md` for a payment saga with reconciliation.