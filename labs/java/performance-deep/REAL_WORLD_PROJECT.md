# Real-World Project — Java Performance Engineering (performance-deep)

Production-style build around JMH, JIT, profiling, GC latency: design, scale, operate.

## Problem statement
Design a service/demo where JMH benchmarks, JIT C1/C2 & inlining, escape analysis are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `JMH benchmarks` → component + owner + SLO.
- `JIT C1/C2 & inlining` → component + owner + SLO.
- `escape analysis` → component + owner + SLO.
- `allocation profiling` → component + owner + SLO.
- `async-profiler/JFR` → component + owner + SLO.

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
- https://docs.oracle.com/en/java/javase/17/gctuning/
- https://openjdk.org/projects/jfr/
- https://docs.oracle.com/en/java/javase/17/docs/api/java.management/java/lang/management/package-summary.html

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale JMH benchmarks under load.
Extension 1: scale JIT C1/C2 & inlining under load.
Extension 2: scale escape analysis under load.
Extension 3: scale allocation profiling under load.
Extension 4: scale async-profiler/JFR under load.
Extension 5: scale GC pause tuning under load.
Extension 6: scale lock contention under load.
Extension 7: scale vector API under load.
Extension 8: scale JMH benchmarks under load.
Extension 9: scale JIT C1/C2 & inlining under load.
Extension 10: scale escape analysis under load.
Extension 11: scale allocation profiling under load.
Extension 12: scale async-profiler/JFR under load.
Extension 13: scale GC pause tuning under load.
Extension 14: scale lock contention under load.
Extension 15: scale vector API under load.
Extension 16: scale JMH benchmarks under load.
Extension 17: scale JIT C1/C2 & inlining under load.
Extension 18: scale escape analysis under load.
Extension 19: scale allocation profiling under load.
Extension 20: scale async-profiler/JFR under load.
Extension 21: scale GC pause tuning under load.
Extension 22: scale lock contention under load.
Extension 23: scale vector API under load.
Extension 24: scale JMH benchmarks under load.
Extension 25: scale JIT C1/C2 & inlining under load.
Extension 26: scale escape analysis under load.
Extension 27: scale allocation profiling under load.
Extension 28: scale async-profiler/JFR under load.
Extension 29: scale GC pause tuning under load.
Extension 30: scale lock contention under load.
Extension 31: scale vector API under load.
Extension 32: scale JMH benchmarks under load.
Extension 33: scale JIT C1/C2 & inlining under load.
Extension 34: scale escape analysis under load.
Extension 35: scale allocation profiling under load.
Extension 36: scale async-profiler/JFR under load.
Extension 37: scale GC pause tuning under load.
Extension 38: scale lock contention under load.
Extension 39: scale vector API under load.
Extension 40: scale JMH benchmarks under load.
Extension 41: scale JIT C1/C2 & inlining under load.
Extension 42: scale escape analysis under load.
Extension 43: scale allocation profiling under load.
Extension 44: scale async-profiler/JFR under load.
Extension 45: scale GC pause tuning under load.
Extension 46: scale lock contention under load.
Extension 47: scale vector API under load.
Extension 48: scale JMH benchmarks under load.
Extension 49: scale JIT C1/C2 & inlining under load.
Extension 50: scale escape analysis under load.
Extension 51: scale allocation profiling under load.
Extension 52: scale async-profiler/JFR under load.
Extension 53: scale GC pause tuning under load.
Extension 54: scale lock contention under load.
Extension 55: scale vector API under load.
Extension 56: scale JMH benchmarks under load.
Extension 57: scale JIT C1/C2 & inlining under load.
Extension 58: scale escape analysis under load.
Extension 59: scale allocation profiling under load.
Extension 60: scale async-profiler/JFR under load.
Extension 61: scale GC pause tuning under load.
Extension 62: scale lock contention under load.
Extension 63: scale vector API under load.
Extension 64: scale JMH benchmarks under load.
Extension 65: scale JIT C1/C2 & inlining under load.
Extension 66: scale escape analysis under load.
Extension 67: scale allocation profiling under load.
Extension 68: scale async-profiler/JFR under load.
Extension 69: scale GC pause tuning under load.
Extension 70: scale lock contention under load.
Extension 71: scale vector API under load.
Extension 72: scale JMH benchmarks under load.
Extension 73: scale JIT C1/C2 & inlining under load.
Extension 74: scale escape analysis under load.
