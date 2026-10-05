# REAL-WORLD PROJECT — Structured Concurrency: Orphaned Futures Bill the Customer Twice

## Incident Scenario
Booking fans out with `CompletableFuture` + `orTimeout` + a shared
pool: on timeout the parent returns 504 but children keep running —
one books the flight anyway. Retries then double-book; orphans pile up
until the pool saturates and everything 503s.

## Symptoms
- Double bookings 12/day after timeouts; logs show `BOOKED` after
  `504 returned` — child outlived caller.
- Thread count grows 300 → 2,400/day; `Thread.print` shows stale
  `booking-*` tasks hours old; pool queue unbounded.
- `orTimeout` cancels the CF, not the underlying task (non-interruptible
  blocking call) — cancellation is decorative.
- Tenant context via ThreadLocal leaks across pooled threads: user A
  sees user B's pricing (P0 privacy near-miss).
- JFR `VirtualThreadPinned` on the payment lock + `SocketRead` stacks
  that never got interrupted.

## Investigation Tasks
1. Orphan proof: `jcmd <pid> Thread.print` histogram by age/name;
   correlate `booking-*` start times with already-returned request ids
   in access log (`grep 504`).
2. JFR: `jcmd <pid> JFR.start name=scope settings=profile duration=180s
   filename=scope.jfr`; inspect `jdk.ThreadStart/End` imbalance,
   `jdk.SocketRead` unbounded durations, `jdk.VirtualThreadPinned`.
3. Context leak: heap dump → ThreadLocalMap entries on pooled threads
   holding prior `Tenant` objects; reproduce cross-tenant read in test.
4. Code forensics: grep `orTimeout\|getNow\|supplyAsync` without
   scope/boundary; confirm no `cancel(true)` path reaches blocking I/O.
5. Repro: chaos timeout on staging — old CF path double-books 3/20;
   scope path 0/20 with zero thread growth.

## Root Cause
Unstructured fan-out: no lifetime binding, no real cancellation, and
mutable thread-scoped context on a shared pool. Timeouts hide work
instead of stopping it.

## Resolution
- Immediate: idempotency keys on book calls + orphan reaper (cancel
  aged tasks) + ThreadLocal clearing filter; cap retries.
- Short-term: migrate fan-out to `StructuredTaskScope` with
  `ShutdownOnFailure` + 2s deadline; `ScopedValue` for tenant/trace;
  interruptible I/O (timeouts on client, `ReentrantLock`).
- Long-term: scope-only fan-out rule (ArchUnit ban on raw
  `supplyAsync` in booking), idempotency everywhere, orphan dashboard.

## Runbook
```
1. Capture Thread.print + JFR 180s + heap dump (ThreadLocal evidence).
2. Enable idempotency keys + reaper to canary; verify doubles 12/d -> 0.
3. Migrate one endpoint to StructuredTaskScope + ScopedValue (10% traffic).
4. Verify: thread growth 0, deadline overshoot <100ms, pinned ~0.
5. Roll 100%; reconcile double-booked orders (refund + apology flow).
6. Land scope-only gate + orphan + context-leak alerts.
```

## Metrics
| Signal | Before | After | Gate |
|--------|--------|-------|------|
| Double books/day | 12 | 0 (60d) | Idempotency test |
| Orphan threads/day | +2,100 | 0 | Thread-delta alert |
| Timeout overshoot | unbounded | <100ms | Deadline test |
| Cross-tenant reads | 3 near-miss | 0 | ScopedValue test |
| 503 rate at peak | 8% | 0.1% | SLO |

## Prevention Checklist
- [ ] All fan-out inside a scope (lint-enforced)
- [ ] Idempotency keys on every booking call
- [ ] ScopedValue only (no request ThreadLocal)
- [ ] Orphan/thread-growth dashboard + alert

## Failure-Injection Drill
- Reproduce on staging with fault injection (latency + error 5%).
- Capture JFR + `jcmd Thread.print` + heap dump during the drill.
- Verify alerts fire in <2 min and runbook step 1–3 completes <15 min.

## Interview Debrief
- Explain the signal that distinguished this root cause in 2 minutes.
- Whiteboard the before/after data path with the bounding fix circled.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Structured concurrency (JEP 453) / ScopedValues: https://openjdk.org/projects/loom/
- Java SE 21 concurrency docs: https://docs.oracle.com/en/java/javase/21/
