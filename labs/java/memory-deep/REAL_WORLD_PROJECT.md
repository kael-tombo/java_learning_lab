# Real-World Project — JVM Memory Internals (memory-deep)

Production-style build around heap regions, metaspace, stack, GC internals, JOL, NMT: design, scale, operate.

## Problem statement
Design a service/demo where heap vs stack, eden/survivor/old gen, metaspace vs permgen are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `heap vs stack` → component + owner + SLO.
- `eden/survivor/old gen` → component + owner + SLO.
- `metaspace vs permgen` → component + owner + SLO.
- `object header & alignment` → component + owner + SLO.
- `GC roots & reachability` → component + owner + SLO.

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
Extension 0: scale heap vs stack under load.
Extension 1: scale eden/survivor/old gen under load.
Extension 2: scale metaspace vs permgen under load.
Extension 3: scale object header & alignment under load.
Extension 4: scale GC roots & reachability under load.
Extension 5: scale NMT & JOL under load.
Extension 6: scale reference types under load.
Extension 7: scale safepoints under load.
Extension 8: scale heap vs stack under load.
Extension 9: scale eden/survivor/old gen under load.
Extension 10: scale metaspace vs permgen under load.
Extension 11: scale object header & alignment under load.
Extension 12: scale GC roots & reachability under load.
Extension 13: scale NMT & JOL under load.
Extension 14: scale reference types under load.
Extension 15: scale safepoints under load.
Extension 16: scale heap vs stack under load.
Extension 17: scale eden/survivor/old gen under load.
Extension 18: scale metaspace vs permgen under load.
Extension 19: scale object header & alignment under load.
Extension 20: scale GC roots & reachability under load.
Extension 21: scale NMT & JOL under load.
Extension 22: scale reference types under load.
Extension 23: scale safepoints under load.
Extension 24: scale heap vs stack under load.
Extension 25: scale eden/survivor/old gen under load.
Extension 26: scale metaspace vs permgen under load.
Extension 27: scale object header & alignment under load.
Extension 28: scale GC roots & reachability under load.
Extension 29: scale NMT & JOL under load.
Extension 30: scale reference types under load.
Extension 31: scale safepoints under load.
Extension 32: scale heap vs stack under load.
Extension 33: scale eden/survivor/old gen under load.
Extension 34: scale metaspace vs permgen under load.
Extension 35: scale object header & alignment under load.
Extension 36: scale GC roots & reachability under load.
Extension 37: scale NMT & JOL under load.
Extension 38: scale reference types under load.
Extension 39: scale safepoints under load.
Extension 40: scale heap vs stack under load.
Extension 41: scale eden/survivor/old gen under load.
Extension 42: scale metaspace vs permgen under load.
Extension 43: scale object header & alignment under load.
Extension 44: scale GC roots & reachability under load.
Extension 45: scale NMT & JOL under load.
Extension 46: scale reference types under load.
Extension 47: scale safepoints under load.
Extension 48: scale heap vs stack under load.
Extension 49: scale eden/survivor/old gen under load.
Extension 50: scale metaspace vs permgen under load.
Extension 51: scale object header & alignment under load.
Extension 52: scale GC roots & reachability under load.
Extension 53: scale NMT & JOL under load.
Extension 54: scale reference types under load.
Extension 55: scale safepoints under load.
Extension 56: scale heap vs stack under load.
Extension 57: scale eden/survivor/old gen under load.
Extension 58: scale metaspace vs permgen under load.
Extension 59: scale object header & alignment under load.
Extension 60: scale GC roots & reachability under load.
Extension 61: scale NMT & JOL under load.
Extension 62: scale reference types under load.
Extension 63: scale safepoints under load.
Extension 64: scale heap vs stack under load.
Extension 65: scale eden/survivor/old gen under load.
Extension 66: scale metaspace vs permgen under load.
Extension 67: scale object header & alignment under load.
Extension 68: scale GC roots & reachability under load.
Extension 69: scale NMT & JOL under load.
Extension 70: scale reference types under load.
Extension 71: scale safepoints under load.
Extension 72: scale heap vs stack under load.
Extension 73: scale eden/survivor/old gen under load.
Extension 74: scale metaspace vs permgen under load.
