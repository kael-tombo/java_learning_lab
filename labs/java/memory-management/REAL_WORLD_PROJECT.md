# Real-World Project — Java Memory Management (memory-management)

Production-style build around allocation, GC tuning, leak detection, heap dumps: design, scale, operate.

## Problem statement
Design a service/demo where allocation paths (TLAB), young/old GC, G1/ZGC/Shenandoah are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `allocation paths (TLAB)` → component + owner + SLO.
- `young/old GC` → component + owner + SLO.
- `G1/ZGC/Shenandoah` → component + owner + SLO.
- `tuning flags` → component + owner + SLO.
- `leak detection` → component + owner + SLO.

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
Extension 0: scale allocation paths (TLAB) under load.
Extension 1: scale young/old GC under load.
Extension 2: scale G1/ZGC/Shenandoah under load.
Extension 3: scale tuning flags under load.
Extension 4: scale leak detection under load.
Extension 5: scale heap dump analysis under load.
Extension 6: scale OOM causes under load.
Extension 7: scale direct memory under load.
Extension 8: scale allocation paths (TLAB) under load.
Extension 9: scale young/old GC under load.
Extension 10: scale G1/ZGC/Shenandoah under load.
Extension 11: scale tuning flags under load.
Extension 12: scale leak detection under load.
Extension 13: scale heap dump analysis under load.
Extension 14: scale OOM causes under load.
Extension 15: scale direct memory under load.
Extension 16: scale allocation paths (TLAB) under load.
Extension 17: scale young/old GC under load.
Extension 18: scale G1/ZGC/Shenandoah under load.
Extension 19: scale tuning flags under load.
Extension 20: scale leak detection under load.
Extension 21: scale heap dump analysis under load.
Extension 22: scale OOM causes under load.
Extension 23: scale direct memory under load.
Extension 24: scale allocation paths (TLAB) under load.
Extension 25: scale young/old GC under load.
Extension 26: scale G1/ZGC/Shenandoah under load.
Extension 27: scale tuning flags under load.
Extension 28: scale leak detection under load.
Extension 29: scale heap dump analysis under load.
Extension 30: scale OOM causes under load.
Extension 31: scale direct memory under load.
Extension 32: scale allocation paths (TLAB) under load.
Extension 33: scale young/old GC under load.
Extension 34: scale G1/ZGC/Shenandoah under load.
Extension 35: scale tuning flags under load.
Extension 36: scale leak detection under load.
Extension 37: scale heap dump analysis under load.
Extension 38: scale OOM causes under load.
Extension 39: scale direct memory under load.
Extension 40: scale allocation paths (TLAB) under load.
Extension 41: scale young/old GC under load.
Extension 42: scale G1/ZGC/Shenandoah under load.
Extension 43: scale tuning flags under load.
Extension 44: scale leak detection under load.
Extension 45: scale heap dump analysis under load.
Extension 46: scale OOM causes under load.
Extension 47: scale direct memory under load.
Extension 48: scale allocation paths (TLAB) under load.
Extension 49: scale young/old GC under load.
Extension 50: scale G1/ZGC/Shenandoah under load.
Extension 51: scale tuning flags under load.
Extension 52: scale leak detection under load.
Extension 53: scale heap dump analysis under load.
Extension 54: scale OOM causes under load.
Extension 55: scale direct memory under load.
Extension 56: scale allocation paths (TLAB) under load.
Extension 57: scale young/old GC under load.
Extension 58: scale G1/ZGC/Shenandoah under load.
Extension 59: scale tuning flags under load.
Extension 60: scale leak detection under load.
Extension 61: scale heap dump analysis under load.
Extension 62: scale OOM causes under load.
Extension 63: scale direct memory under load.
Extension 64: scale allocation paths (TLAB) under load.
Extension 65: scale young/old GC under load.
Extension 66: scale G1/ZGC/Shenandoah under load.
Extension 67: scale tuning flags under load.
Extension 68: scale leak detection under load.
Extension 69: scale heap dump analysis under load.
Extension 70: scale OOM causes under load.
Extension 71: scale direct memory under load.
Extension 72: scale allocation paths (TLAB) under load.
Extension 73: scale young/old GC under load.
Extension 74: scale G1/ZGC/Shenandoah under load.
