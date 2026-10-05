# Real-World Project — Java Collections Fundamentals (collections)

Production-style build around List/Set/Map, equals/hashCode, sorting: design, scale, operate.

## Problem statement
Design a service/demo where ArrayList vs LinkedList, HashSet/TreeSet, HashMap internals are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `ArrayList vs LinkedList` → component + owner + SLO.
- `HashSet/TreeSet` → component + owner + SLO.
- `HashMap internals` → component + owner + SLO.
- `equals/hashCode contract` → component + owner + SLO.
- `comparators` → component + owner + SLO.

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
Extension 0: scale ArrayList vs LinkedList under load.
Extension 1: scale HashSet/TreeSet under load.
Extension 2: scale HashMap internals under load.
Extension 3: scale equals/hashCode contract under load.
Extension 4: scale comparators under load.
Extension 5: scale streams basics under load.
Extension 6: scale unmodifiable views under load.
Extension 7: scale fail-fast iterators under load.
Extension 8: scale ArrayList vs LinkedList under load.
Extension 9: scale HashSet/TreeSet under load.
Extension 10: scale HashMap internals under load.
Extension 11: scale equals/hashCode contract under load.
Extension 12: scale comparators under load.
Extension 13: scale streams basics under load.
Extension 14: scale unmodifiable views under load.
Extension 15: scale fail-fast iterators under load.
Extension 16: scale ArrayList vs LinkedList under load.
Extension 17: scale HashSet/TreeSet under load.
Extension 18: scale HashMap internals under load.
Extension 19: scale equals/hashCode contract under load.
Extension 20: scale comparators under load.
Extension 21: scale streams basics under load.
Extension 22: scale unmodifiable views under load.
Extension 23: scale fail-fast iterators under load.
Extension 24: scale ArrayList vs LinkedList under load.
Extension 25: scale HashSet/TreeSet under load.
Extension 26: scale HashMap internals under load.
Extension 27: scale equals/hashCode contract under load.
Extension 28: scale comparators under load.
Extension 29: scale streams basics under load.
Extension 30: scale unmodifiable views under load.
Extension 31: scale fail-fast iterators under load.
Extension 32: scale ArrayList vs LinkedList under load.
Extension 33: scale HashSet/TreeSet under load.
Extension 34: scale HashMap internals under load.
Extension 35: scale equals/hashCode contract under load.
Extension 36: scale comparators under load.
Extension 37: scale streams basics under load.
Extension 38: scale unmodifiable views under load.
Extension 39: scale fail-fast iterators under load.
Extension 40: scale ArrayList vs LinkedList under load.
Extension 41: scale HashSet/TreeSet under load.
Extension 42: scale HashMap internals under load.
Extension 43: scale equals/hashCode contract under load.
Extension 44: scale comparators under load.
Extension 45: scale streams basics under load.
Extension 46: scale unmodifiable views under load.
Extension 47: scale fail-fast iterators under load.
Extension 48: scale ArrayList vs LinkedList under load.
Extension 49: scale HashSet/TreeSet under load.
Extension 50: scale HashMap internals under load.
Extension 51: scale equals/hashCode contract under load.
Extension 52: scale comparators under load.
Extension 53: scale streams basics under load.
Extension 54: scale unmodifiable views under load.
Extension 55: scale fail-fast iterators under load.
Extension 56: scale ArrayList vs LinkedList under load.
Extension 57: scale HashSet/TreeSet under load.
Extension 58: scale HashMap internals under load.
Extension 59: scale equals/hashCode contract under load.
Extension 60: scale comparators under load.
Extension 61: scale streams basics under load.
Extension 62: scale unmodifiable views under load.
Extension 63: scale fail-fast iterators under load.
Extension 64: scale ArrayList vs LinkedList under load.
Extension 65: scale HashSet/TreeSet under load.
Extension 66: scale HashMap internals under load.
Extension 67: scale equals/hashCode contract under load.
Extension 68: scale comparators under load.
Extension 69: scale streams basics under load.
Extension 70: scale unmodifiable views under load.
Extension 71: scale fail-fast iterators under load.
Extension 72: scale ArrayList vs LinkedList under load.
Extension 73: scale HashSet/TreeSet under load.
Extension 74: scale HashMap internals under load.
