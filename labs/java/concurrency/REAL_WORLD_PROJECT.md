# Real-World Project — Java Concurrency Basics (concurrency)

Production-style build around threads, locks, executors, atomics: design, scale, operate.

## Problem statement
Design a service/demo where Thread lifecycle, synchronized & volatile, Locks & conditions are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `Thread lifecycle` → component + owner + SLO.
- `synchronized & volatile` → component + owner + SLO.
- `Locks & conditions` → component + owner + SLO.
- `Executors & pools` → component + owner + SLO.
- `Futures & CompletableFuture` → component + owner + SLO.

## Milestones (4)
1. Slice: happy path + test.
2. Harden: timeouts, retries, validation.
3. Observe: logs/metrics/JFR + dashboard.
4. Scale: benchmark + tune one bottleneck.

## Ops checklist
- [ ] Dockerfile + health check
- [ ] Load test (k6/JMeter) with p99
- [ ] Runbook: top-3 failures + mitigations

## Interview story
Prepare STAR: problem → approach → metric → lesson.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html
- https://openjdk.org/jeps/444 (virtual threads)
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale Thread lifecycle under load.
Extension 1: scale synchronized & volatile under load.
Extension 2: scale Locks & conditions under load.
Extension 3: scale Executors & pools under load.
Extension 4: scale Futures & CompletableFuture under load.
Extension 5: scale atomics under load.
Extension 6: scale deadlock avoidance under load.
Extension 7: scale thread-safety patterns under load.
Extension 8: scale Thread lifecycle under load.
Extension 9: scale synchronized & volatile under load.
Extension 10: scale Locks & conditions under load.
Extension 11: scale Executors & pools under load.
Extension 12: scale Futures & CompletableFuture under load.
Extension 13: scale atomics under load.
Extension 14: scale deadlock avoidance under load.
Extension 15: scale thread-safety patterns under load.
Extension 16: scale Thread lifecycle under load.
Extension 17: scale synchronized & volatile under load.
Extension 18: scale Locks & conditions under load.
Extension 19: scale Executors & pools under load.
Extension 20: scale Futures & CompletableFuture under load.
Extension 21: scale atomics under load.
Extension 22: scale deadlock avoidance under load.
Extension 23: scale thread-safety patterns under load.
Extension 24: scale Thread lifecycle under load.
Extension 25: scale synchronized & volatile under load.
Extension 26: scale Locks & conditions under load.
Extension 27: scale Executors & pools under load.
Extension 28: scale Futures & CompletableFuture under load.
Extension 29: scale atomics under load.
Extension 30: scale deadlock avoidance under load.
Extension 31: scale thread-safety patterns under load.
Extension 32: scale Thread lifecycle under load.
Extension 33: scale synchronized & volatile under load.
Extension 34: scale Locks & conditions under load.
Extension 35: scale Executors & pools under load.
Extension 36: scale Futures & CompletableFuture under load.
Extension 37: scale atomics under load.
Extension 38: scale deadlock avoidance under load.
Extension 39: scale thread-safety patterns under load.
Extension 40: scale Thread lifecycle under load.
Extension 41: scale synchronized & volatile under load.
Extension 42: scale Locks & conditions under load.
Extension 43: scale Executors & pools under load.
Extension 44: scale Futures & CompletableFuture under load.
Extension 45: scale atomics under load.
Extension 46: scale deadlock avoidance under load.
Extension 47: scale thread-safety patterns under load.
Extension 48: scale Thread lifecycle under load.
Extension 49: scale synchronized & volatile under load.
Extension 50: scale Locks & conditions under load.
Extension 51: scale Executors & pools under load.
Extension 52: scale Futures & CompletableFuture under load.
Extension 53: scale atomics under load.
Extension 54: scale deadlock avoidance under load.
Extension 55: scale thread-safety patterns under load.
Extension 56: scale Thread lifecycle under load.
Extension 57: scale synchronized & volatile under load.
Extension 58: scale Locks & conditions under load.
Extension 59: scale Executors & pools under load.
Extension 60: scale Futures & CompletableFuture under load.
Extension 61: scale atomics under load.
Extension 62: scale deadlock avoidance under load.
Extension 63: scale thread-safety patterns under load.
Extension 64: scale Thread lifecycle under load.
Extension 65: scale synchronized & volatile under load.
Extension 66: scale Locks & conditions under load.
Extension 67: scale Executors & pools under load.
Extension 68: scale Futures & CompletableFuture under load.
Extension 69: scale atomics under load.
Extension 70: scale deadlock avoidance under load.
Extension 71: scale thread-safety patterns under load.
Extension 72: scale Thread lifecycle under load.
Extension 73: scale synchronized & volatile under load.
Extension 74: scale Locks & conditions under load.
