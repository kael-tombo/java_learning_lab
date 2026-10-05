# Real-World Project — Java Generics Mastery (generics)

Production-style build around type params, wildcards, erasure, variance: design, scale, operate.

## Problem statement
Design a service/demo where type parameters & bounds, wildcards PECS, erasure & bridge methods are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `type parameters & bounds` → component + owner + SLO.
- `wildcards PECS` → component + owner + SLO.
- `erasure & bridge methods` → component + owner + SLO.
- `generic methods` → component + owner + SLO.
- `variance` → component + owner + SLO.

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
- https://docs.oracle.com/en/java/javase/17/docs/api/
- https://openjdk.org/jeps/401 (value classes discussion)
- https://openjdk.org/projects/jmh/

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale type parameters & bounds under load.
Extension 1: scale wildcards PECS under load.
Extension 2: scale erasure & bridge methods under load.
Extension 3: scale generic methods under load.
Extension 4: scale variance under load.
Extension 5: scale type tokens under load.
Extension 6: scale records + generics under load.
Extension 7: scale reflection on generics under load.
Extension 8: scale type parameters & bounds under load.
Extension 9: scale wildcards PECS under load.
Extension 10: scale erasure & bridge methods under load.
Extension 11: scale generic methods under load.
Extension 12: scale variance under load.
Extension 13: scale type tokens under load.
Extension 14: scale records + generics under load.
Extension 15: scale reflection on generics under load.
Extension 16: scale type parameters & bounds under load.
Extension 17: scale wildcards PECS under load.
Extension 18: scale erasure & bridge methods under load.
Extension 19: scale generic methods under load.
Extension 20: scale variance under load.
Extension 21: scale type tokens under load.
Extension 22: scale records + generics under load.
Extension 23: scale reflection on generics under load.
Extension 24: scale type parameters & bounds under load.
Extension 25: scale wildcards PECS under load.
Extension 26: scale erasure & bridge methods under load.
Extension 27: scale generic methods under load.
Extension 28: scale variance under load.
Extension 29: scale type tokens under load.
Extension 30: scale records + generics under load.
Extension 31: scale reflection on generics under load.
Extension 32: scale type parameters & bounds under load.
Extension 33: scale wildcards PECS under load.
Extension 34: scale erasure & bridge methods under load.
Extension 35: scale generic methods under load.
Extension 36: scale variance under load.
Extension 37: scale type tokens under load.
Extension 38: scale records + generics under load.
Extension 39: scale reflection on generics under load.
Extension 40: scale type parameters & bounds under load.
Extension 41: scale wildcards PECS under load.
Extension 42: scale erasure & bridge methods under load.
Extension 43: scale generic methods under load.
Extension 44: scale variance under load.
Extension 45: scale type tokens under load.
Extension 46: scale records + generics under load.
Extension 47: scale reflection on generics under load.
Extension 48: scale type parameters & bounds under load.
Extension 49: scale wildcards PECS under load.
Extension 50: scale erasure & bridge methods under load.
Extension 51: scale generic methods under load.
Extension 52: scale variance under load.
Extension 53: scale type tokens under load.
Extension 54: scale records + generics under load.
Extension 55: scale reflection on generics under load.
Extension 56: scale type parameters & bounds under load.
Extension 57: scale wildcards PECS under load.
Extension 58: scale erasure & bridge methods under load.
Extension 59: scale generic methods under load.
Extension 60: scale variance under load.
Extension 61: scale type tokens under load.
Extension 62: scale records + generics under load.
Extension 63: scale reflection on generics under load.
Extension 64: scale type parameters & bounds under load.
Extension 65: scale wildcards PECS under load.
Extension 66: scale erasure & bridge methods under load.
Extension 67: scale generic methods under load.
Extension 68: scale variance under load.
Extension 69: scale type tokens under load.
Extension 70: scale records + generics under load.
Extension 71: scale reflection on generics under load.
Extension 72: scale type parameters & bounds under load.
Extension 73: scale wildcards PECS under load.
Extension 74: scale erasure & bridge methods under load.
