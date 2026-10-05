# Real-World Project — Deep Collections Engineering (collections-deep)

Production-style build around hashing, trees, concurrent maps, custom structures: design, scale, operate.

## Problem statement
Design a service/demo where hash spreading & bins, red-black trees, ConcurrentHashMap are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `hash spreading & bins` → component + owner + SLO.
- `red-black trees` → component + owner + SLO.
- `ConcurrentHashMap` → component + owner + SLO.
- `CopyOnWriteArrayList` → component + owner + SLO.
- `immutable collections` → component + owner + SLO.

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
Extension 0: scale hash spreading & bins under load.
Extension 1: scale red-black trees under load.
Extension 2: scale ConcurrentHashMap under load.
Extension 3: scale CopyOnWriteArrayList under load.
Extension 4: scale immutable collections under load.
Extension 5: scale Deque & queues under load.
Extension 6: scale caching (LRU/LFU) under load.
Extension 7: scale memory footprint under load.
Extension 8: scale hash spreading & bins under load.
Extension 9: scale red-black trees under load.
Extension 10: scale ConcurrentHashMap under load.
Extension 11: scale CopyOnWriteArrayList under load.
Extension 12: scale immutable collections under load.
Extension 13: scale Deque & queues under load.
Extension 14: scale caching (LRU/LFU) under load.
Extension 15: scale memory footprint under load.
Extension 16: scale hash spreading & bins under load.
Extension 17: scale red-black trees under load.
Extension 18: scale ConcurrentHashMap under load.
Extension 19: scale CopyOnWriteArrayList under load.
Extension 20: scale immutable collections under load.
Extension 21: scale Deque & queues under load.
Extension 22: scale caching (LRU/LFU) under load.
Extension 23: scale memory footprint under load.
Extension 24: scale hash spreading & bins under load.
Extension 25: scale red-black trees under load.
Extension 26: scale ConcurrentHashMap under load.
Extension 27: scale CopyOnWriteArrayList under load.
Extension 28: scale immutable collections under load.
Extension 29: scale Deque & queues under load.
Extension 30: scale caching (LRU/LFU) under load.
Extension 31: scale memory footprint under load.
Extension 32: scale hash spreading & bins under load.
Extension 33: scale red-black trees under load.
Extension 34: scale ConcurrentHashMap under load.
Extension 35: scale CopyOnWriteArrayList under load.
Extension 36: scale immutable collections under load.
Extension 37: scale Deque & queues under load.
Extension 38: scale caching (LRU/LFU) under load.
Extension 39: scale memory footprint under load.
Extension 40: scale hash spreading & bins under load.
Extension 41: scale red-black trees under load.
Extension 42: scale ConcurrentHashMap under load.
Extension 43: scale CopyOnWriteArrayList under load.
Extension 44: scale immutable collections under load.
Extension 45: scale Deque & queues under load.
Extension 46: scale caching (LRU/LFU) under load.
Extension 47: scale memory footprint under load.
Extension 48: scale hash spreading & bins under load.
Extension 49: scale red-black trees under load.
Extension 50: scale ConcurrentHashMap under load.
Extension 51: scale CopyOnWriteArrayList under load.
Extension 52: scale immutable collections under load.
Extension 53: scale Deque & queues under load.
Extension 54: scale caching (LRU/LFU) under load.
Extension 55: scale memory footprint under load.
Extension 56: scale hash spreading & bins under load.
Extension 57: scale red-black trees under load.
Extension 58: scale ConcurrentHashMap under load.
Extension 59: scale CopyOnWriteArrayList under load.
Extension 60: scale immutable collections under load.
Extension 61: scale Deque & queues under load.
Extension 62: scale caching (LRU/LFU) under load.
Extension 63: scale memory footprint under load.
Extension 64: scale hash spreading & bins under load.
Extension 65: scale red-black trees under load.
Extension 66: scale ConcurrentHashMap under load.
Extension 67: scale CopyOnWriteArrayList under load.
Extension 68: scale immutable collections under load.
Extension 69: scale Deque & queues under load.
Extension 70: scale caching (LRU/LFU) under load.
Extension 71: scale memory footprint under load.
Extension 72: scale hash spreading & bins under load.
Extension 73: scale red-black trees under load.
Extension 74: scale ConcurrentHashMap under load.
