# MINI PROJECT — Locking & Synchronization: Contended Ledger

## Goal (2 weeks, ~8–10h)
Build a ledger (`transfer(from, to, amount)`) that is deadlock-free,
linearizable, and fast under 32-thread contention — with JFR proof
that contention moved off the hot path.

## Requirements
### Functional
1. Correct transfer with global lock ordering (by account id) using
   `ReentrantLock.tryLock(500ms)`; deadlock test with opposite-order
   transfers passes 100k iterations.
2. Read path: balance snapshot via `StampedLock` optimistic read or
   `ConcurrentHashMap` + `LongAdder` balances; no `synchronized` on I/O.
3. High-contention fee counter using `LongAdder`; microbenchmark vs
   `AtomicLong` showing crossover (JMH, 1/4/16/32 threads).
4. `Condition`-based overdraft wait: `await(amountAvailable,
   1s)` with signal on deposit; spurious-wakeup-safe loop.
5. Lock-free audit ring: `AtomicReference`/`VarHandle` CAS ring or
   JCTools-style MPSC queue for transfer events (no locks).
6. Chaos: random 5% slow downstream inside transfer — timeouts still
   hold, no lock held across the sleep (verified by test).

### Non-functional
- 18+ tests incl. JCStress-style interleaving test (at least scripted
  10k-iteration race), deadlock soak, ordering invariant checker.
- JFR: `jdk.JavaMonitorEnter` + `jdk.ThreadPark` capture before/after
  striping; contention time reduced ≥ 50%.
- JMH numbers in README (ops/s + p99 park time per variant).
- README: lock-ordering diagram + "why this primitive" table.

## Starter Layout
```
src/main/java/com/lab42/ledger/{Ledger,Account,StripedCounter,AuditRing}.java
src/test/java/.../{DeadlockTest,OrderingTest,CounterBenchTest}.java
src/jmh/java/.../CounterBenchmark.java
```

## Phases
### Week 1 — Correctness (4–5h)
- Ordering, tryLock, conditions, audit ring; deadlock soak green.
- Deliverable: linearizability + ordering tests passing.
### Week 2 — Contention Tuning (4–5h)
- JMH + JFR, LongAdder/striping swap, stamped reads.
- Deliverable: before/after contention report with numbers.

## Test Plan
- Opposite-direction transfer storm (2 accounts, 32 threads, 100k ops)
  → balances conserved, zero deadlock.
- Invariant: sum(balances) constant after every 1k ops snapshot.
- Timeout: blocked transfer aborts <600ms, funds untouched.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Deadlock-free | Ordering + tryLock proven | Ordered | Ad-hoc locking |
| Read path | Optimistic/striped, measured | Concurrent map | Global lock reads |
| Counter | LongAdder + JMH crossover | Atomic correct | Single hot Atomic |
| JFR proof | ≥50% contention cut, attributed | Captured | No profile |
| Tests | 18+ incl. race soak | 12+ | No race coverage |

Pass ≥ 70. Stretch: custom AQS synchronizer (counted gate) with
JMM happens-before proof sketch; VarHandle fence experiment.

## Demo Checklist
- [ ] Live deadlock-storm run (old code deadlocks, new does not)
- [ ] JMH bar chart + JFR monitor-enter delta
- [ ] Dump reading: point at parking queue in 2 min
- [ ] Timeout path demo (blocked → clean abort)

## Common Traps
Locking on `String`/boxed `Integer`, holding locks across I/O,
`if` instead of `while` around await — all auto-fail.
