# Real-World Project — Concurrency Deep & Virtual Threads (concurrency-deep)

Production-style build around JMM, Loom, structured concurrency, VarHandles: design, scale, operate.

## Problem statement
Design a service/demo where JMM happens-before, virtual threads & carriers, structured concurrency are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `JMM happens-before` → component + owner + SLO.
- `virtual threads & carriers` → component + owner + SLO.
- `structured concurrency` → component + owner + SLO.
- `scoped values` → component + owner + SLO.
- `ForkJoinPool` → component + owner + SLO.

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
Extension 0: scale JMM happens-before under load.
Extension 1: scale virtual threads & carriers under load.
Extension 2: scale structured concurrency under load.
Extension 3: scale scoped values under load.
Extension 4: scale ForkJoinPool under load.
Extension 5: scale StampedLock/LongAdder under load.
Extension 6: scale VarHandle under load.
Extension 7: scale reactive vs virtual under load.
Extension 8: scale JMM happens-before under load.
Extension 9: scale virtual threads & carriers under load.
Extension 10: scale structured concurrency under load.
Extension 11: scale scoped values under load.
Extension 12: scale ForkJoinPool under load.
Extension 13: scale StampedLock/LongAdder under load.
Extension 14: scale VarHandle under load.
Extension 15: scale reactive vs virtual under load.
Extension 16: scale JMM happens-before under load.
Extension 17: scale virtual threads & carriers under load.
Extension 18: scale structured concurrency under load.
Extension 19: scale scoped values under load.
Extension 20: scale ForkJoinPool under load.
Extension 21: scale StampedLock/LongAdder under load.
Extension 22: scale VarHandle under load.
Extension 23: scale reactive vs virtual under load.
Extension 24: scale JMM happens-before under load.
Extension 25: scale virtual threads & carriers under load.
Extension 26: scale structured concurrency under load.
Extension 27: scale scoped values under load.
Extension 28: scale ForkJoinPool under load.
Extension 29: scale StampedLock/LongAdder under load.
Extension 30: scale VarHandle under load.
Extension 31: scale reactive vs virtual under load.
Extension 32: scale JMM happens-before under load.
Extension 33: scale virtual threads & carriers under load.
Extension 34: scale structured concurrency under load.
Extension 35: scale scoped values under load.
Extension 36: scale ForkJoinPool under load.
Extension 37: scale StampedLock/LongAdder under load.
Extension 38: scale VarHandle under load.
Extension 39: scale reactive vs virtual under load.
Extension 40: scale JMM happens-before under load.
Extension 41: scale virtual threads & carriers under load.
Extension 42: scale structured concurrency under load.
Extension 43: scale scoped values under load.
Extension 44: scale ForkJoinPool under load.
Extension 45: scale StampedLock/LongAdder under load.
Extension 46: scale VarHandle under load.
Extension 47: scale reactive vs virtual under load.
Extension 48: scale JMM happens-before under load.
Extension 49: scale virtual threads & carriers under load.
Extension 50: scale structured concurrency under load.
Extension 51: scale scoped values under load.
Extension 52: scale ForkJoinPool under load.
Extension 53: scale StampedLock/LongAdder under load.
Extension 54: scale VarHandle under load.
Extension 55: scale reactive vs virtual under load.
Extension 56: scale JMM happens-before under load.
Extension 57: scale virtual threads & carriers under load.
Extension 58: scale structured concurrency under load.
Extension 59: scale scoped values under load.
Extension 60: scale ForkJoinPool under load.
Extension 61: scale StampedLock/LongAdder under load.
Extension 62: scale VarHandle under load.
Extension 63: scale reactive vs virtual under load.
Extension 64: scale JMM happens-before under load.
Extension 65: scale virtual threads & carriers under load.
Extension 66: scale structured concurrency under load.
Extension 67: scale scoped values under load.
Extension 68: scale ForkJoinPool under load.
Extension 69: scale StampedLock/LongAdder under load.
Extension 70: scale VarHandle under load.
Extension 71: scale reactive vs virtual under load.
Extension 72: scale JMM happens-before under load.
Extension 73: scale virtual threads & carriers under load.
Extension 74: scale structured concurrency under load.
