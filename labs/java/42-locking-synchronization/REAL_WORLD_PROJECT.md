# REAL-WORLD PROJECT — Locking: Silent Deadlock Freezes Payouts

## Incident Scenario
Payout service freezes every 2–3 days: threads stop processing but CPU
is idle, health checks stay green (separate thread), and restart clears
it. APM shows "no errors" — because deadlocked threads throw nothing.
Finance notices first via missing settlement batch.

## Symptoms
- Throughput 0 for 40 min while CPU 8%, heap flat, GC normal — not a
  resource-exhaustion shape.
- `Thread.print` later reveals `Found one Java-level deadlock`:
  `Payout.transfer` locks accounts in opposite order on two paths.
- JFR `jdk.JavaMonitorEnter` duration p99 12s on `Account.class` lock;
  `jdk.ThreadPark` stacks converge on two methods.
- One code path holds a DB-row lock while calling a 3s fraud API with
  a synchronized block — lock held across I/O amplifies the window.
- Health endpoint uses its own executor, so k8s never restarts the pod.

## Investigation Tasks
1. Deadlock proof: `jcmd <pid> Thread.print > payout.txt`; find
   `Found one Java-level deadlock` section; map lock addresses to
   account ids; confirm circular wait pair.
2. JFR: `jcmd <pid> JFR.start name=lock settings=profile
   duration=120s filename=lock.jfr`; in JMC rank
   `jdk.JavaMonitorEnter` by stack + longest duration; correlate with
   `jdk.ThreadPark` on fraud-API path.
3. Heap: `jcmd <pid> GC.heap_dump payout.hprof`; inspect lock objects
   (who holds `Account` monitors) and the fraud-client future chain.
4. Logs: `grep "transfer start\|fraud call" app.log` — interleave shows
   A→B and B→A overlapping; code grep `synchronized.*account`
   reveals two opposite orderings.
5. Repro: 2-account opposite transfer loop × 16 threads on staging;
   old code deadlocks <60s, fixed code completes 200k ops.

## Root Cause
Inconsistent lock ordering (id order in one path, request order in
another) plus lock-held-across-I/O (fraud call inside synchronized).
Low-probability interleave → certain deadlock at volume.

## Resolution
- Immediate: restart frozen pods one by one; pause settlement; deploy
  global id-ordered `tryLock(500ms)` patch to canary.
- Short-term: move fraud check outside the lock (validate → lock →
  commit); add lock-hold-time histogram + deadlock-detector thread
  that logs + alerts (and fails health after 2 hits).
- Long-term: single `Ledger.transfer` choke point with ordering unit
  tests + ArchUnit "no synchronized in client-call packages"; JFR
  contention budget in CI.

## Runbook
```
1. jcmd Thread.print immediately (before restart) + JFR 120s + heap dump.
2. Confirm deadlock section; identify the two opposite-order stacks.
3. Canary the ordering + tryLock + move-I/O-out patch (10% traffic).
4. Verify: monitor-enter p99 12s -> <50ms; 200k-op storm clean.
5. Roll 100%; replay missing settlement batch idempotently; reconcile ledger sum.
6. Land detector + health-fail + contention alerts.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| Deadlocks/week | ~2 | 0 (90d) | Detector alert = page |
| Monitor-enter p99 | 12s | <50ms | Alert >200ms |
| Freeze MTTR | 40 min (manual) | <2 min (auto-fail) | Health probe |
| Storm repro | deadlock <60s | 200k ops clean | CI deadlock-soak |
| Settlement lag | 6h | <5 min | Batch SLA |

## Prevention Checklist
- [ ] Single ordered lock helper used everywhere
- [ ] No I/O inside synchronized (review gate)
- [ ] Deadlock detector + health integration
- [ ] Opposite-order soak in CI (100k ops)

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- java.util.concurrent + locks API docs: https://docs.oracle.com/en/java/javase/21/docs/api/
- OpenJDK Loom / synchronization notes: https://openjdk.org/projects/loom/
