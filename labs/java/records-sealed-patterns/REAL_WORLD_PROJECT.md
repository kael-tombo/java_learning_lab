# Real-World Project — Records, Sealed Classes & Patterns (records-sealed-patterns)

Production-style build around data carriers, exhaustive switch, deconstruction: design, scale, operate.

## Problem statement
Design a service/demo where record canonical constructors, compact constructors, sealed permits are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `record canonical constructors` → component + owner + SLO.
- `compact constructors` → component + owner + SLO.
- `sealed permits` → component + owner + SLO.
- `pattern matching switch` → component + owner + SLO.
- `guarded patterns` → component + owner + SLO.

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
- https://docs.oracle.com/en/java/javase/17/language/records.html
- https://docs.oracle.com/en/java/javase/17/language/sealed-classes-and-interfaces.html
- https://openjdk.org/jeps/444 (virtual threads)

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale record canonical constructors under load.
Extension 1: scale compact constructors under load.
Extension 2: scale sealed permits under load.
Extension 3: scale pattern matching switch under load.
Extension 4: scale guarded patterns under load.
Extension 5: scale record patterns under load.
Extension 6: scale exhaustiveness under load.
Extension 7: scale serialization of records under load.
Extension 8: scale record canonical constructors under load.
Extension 9: scale compact constructors under load.
Extension 10: scale sealed permits under load.
Extension 11: scale pattern matching switch under load.
Extension 12: scale guarded patterns under load.
Extension 13: scale record patterns under load.
Extension 14: scale exhaustiveness under load.
Extension 15: scale serialization of records under load.
Extension 16: scale record canonical constructors under load.
Extension 17: scale compact constructors under load.
Extension 18: scale sealed permits under load.
Extension 19: scale pattern matching switch under load.
Extension 20: scale guarded patterns under load.
Extension 21: scale record patterns under load.
Extension 22: scale exhaustiveness under load.
Extension 23: scale serialization of records under load.
Extension 24: scale record canonical constructors under load.
Extension 25: scale compact constructors under load.
Extension 26: scale sealed permits under load.
Extension 27: scale pattern matching switch under load.
Extension 28: scale guarded patterns under load.
Extension 29: scale record patterns under load.
Extension 30: scale exhaustiveness under load.
Extension 31: scale serialization of records under load.
Extension 32: scale record canonical constructors under load.
Extension 33: scale compact constructors under load.
Extension 34: scale sealed permits under load.
Extension 35: scale pattern matching switch under load.
Extension 36: scale guarded patterns under load.
Extension 37: scale record patterns under load.
Extension 38: scale exhaustiveness under load.
Extension 39: scale serialization of records under load.
Extension 40: scale record canonical constructors under load.
Extension 41: scale compact constructors under load.
Extension 42: scale sealed permits under load.
Extension 43: scale pattern matching switch under load.
Extension 44: scale guarded patterns under load.
Extension 45: scale record patterns under load.
Extension 46: scale exhaustiveness under load.
Extension 47: scale serialization of records under load.
Extension 48: scale record canonical constructors under load.
Extension 49: scale compact constructors under load.
Extension 50: scale sealed permits under load.
Extension 51: scale pattern matching switch under load.
Extension 52: scale guarded patterns under load.
Extension 53: scale record patterns under load.
Extension 54: scale exhaustiveness under load.
Extension 55: scale serialization of records under load.
Extension 56: scale record canonical constructors under load.
Extension 57: scale compact constructors under load.
Extension 58: scale sealed permits under load.
Extension 59: scale pattern matching switch under load.
Extension 60: scale guarded patterns under load.
Extension 61: scale record patterns under load.
Extension 62: scale exhaustiveness under load.
Extension 63: scale serialization of records under load.
Extension 64: scale record canonical constructors under load.
Extension 65: scale compact constructors under load.
Extension 66: scale sealed permits under load.
Extension 67: scale pattern matching switch under load.
Extension 68: scale guarded patterns under load.
Extension 69: scale record patterns under load.
Extension 70: scale exhaustiveness under load.
Extension 71: scale serialization of records under load.
Extension 72: scale record canonical constructors under load.
Extension 73: scale compact constructors under load.
Extension 74: scale sealed permits under load.
