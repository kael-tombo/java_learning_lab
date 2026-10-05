# Real-World Project — Modern Java 17-25 (modern-java)

Production-style build around records, sealed classes, pattern matching, virtual threads, switch expressions: design, scale, operate.

## Problem statement
Design a service/demo where records, sealed classes, pattern matching instanceof/switch are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `records` → component + owner + SLO.
- `sealed classes` → component + owner + SLO.
- `pattern matching instanceof/switch` → component + owner + SLO.
- `text blocks` → component + owner + SLO.
- `virtual threads` → component + owner + SLO.

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
Extension 0: scale records under load.
Extension 1: scale sealed classes under load.
Extension 2: scale pattern matching instanceof/switch under load.
Extension 3: scale text blocks under load.
Extension 4: scale virtual threads under load.
Extension 5: scale structured concurrency under load.
Extension 6: scale new HTTP client under load.
Extension 7: scale foreign memory API under load.
Extension 8: scale records under load.
Extension 9: scale sealed classes under load.
Extension 10: scale pattern matching instanceof/switch under load.
Extension 11: scale text blocks under load.
Extension 12: scale virtual threads under load.
Extension 13: scale structured concurrency under load.
Extension 14: scale new HTTP client under load.
Extension 15: scale foreign memory API under load.
Extension 16: scale records under load.
Extension 17: scale sealed classes under load.
Extension 18: scale pattern matching instanceof/switch under load.
Extension 19: scale text blocks under load.
Extension 20: scale virtual threads under load.
Extension 21: scale structured concurrency under load.
Extension 22: scale new HTTP client under load.
Extension 23: scale foreign memory API under load.
Extension 24: scale records under load.
Extension 25: scale sealed classes under load.
Extension 26: scale pattern matching instanceof/switch under load.
Extension 27: scale text blocks under load.
Extension 28: scale virtual threads under load.
Extension 29: scale structured concurrency under load.
Extension 30: scale new HTTP client under load.
Extension 31: scale foreign memory API under load.
Extension 32: scale records under load.
Extension 33: scale sealed classes under load.
Extension 34: scale pattern matching instanceof/switch under load.
Extension 35: scale text blocks under load.
Extension 36: scale virtual threads under load.
Extension 37: scale structured concurrency under load.
Extension 38: scale new HTTP client under load.
Extension 39: scale foreign memory API under load.
Extension 40: scale records under load.
Extension 41: scale sealed classes under load.
Extension 42: scale pattern matching instanceof/switch under load.
Extension 43: scale text blocks under load.
Extension 44: scale virtual threads under load.
Extension 45: scale structured concurrency under load.
Extension 46: scale new HTTP client under load.
Extension 47: scale foreign memory API under load.
Extension 48: scale records under load.
Extension 49: scale sealed classes under load.
Extension 50: scale pattern matching instanceof/switch under load.
Extension 51: scale text blocks under load.
Extension 52: scale virtual threads under load.
Extension 53: scale structured concurrency under load.
Extension 54: scale new HTTP client under load.
Extension 55: scale foreign memory API under load.
Extension 56: scale records under load.
Extension 57: scale sealed classes under load.
Extension 58: scale pattern matching instanceof/switch under load.
Extension 59: scale text blocks under load.
Extension 60: scale virtual threads under load.
Extension 61: scale structured concurrency under load.
Extension 62: scale new HTTP client under load.
Extension 63: scale foreign memory API under load.
Extension 64: scale records under load.
Extension 65: scale sealed classes under load.
Extension 66: scale pattern matching instanceof/switch under load.
Extension 67: scale text blocks under load.
Extension 68: scale virtual threads under load.
Extension 69: scale structured concurrency under load.
Extension 70: scale new HTTP client under load.
Extension 71: scale foreign memory API under load.
Extension 72: scale records under load.
Extension 73: scale sealed classes under load.
Extension 74: scale pattern matching instanceof/switch under load.
