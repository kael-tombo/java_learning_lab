# Real-World Project — Algorithmic Patterns in Java (LEETCODE_SOLUTIONS)

Production-style build around arrays/strings/DP/graphs/two-pointers/sliding-window: design, scale, operate.

## Problem statement
Design a service/demo where two pointers, sliding window, hashing are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `two pointers` → component + owner + SLO.
- `sliding window` → component + owner + SLO.
- `hashing` → component + owner + SLO.
- `binary search` → component + owner + SLO.
- `DP knapsack/LIS` → component + owner + SLO.

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
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Arrays.html
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Collections.html
- https://openjdk.org/projects/jmh/

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale two pointers under load.
Extension 1: scale sliding window under load.
Extension 2: scale hashing under load.
Extension 3: scale binary search under load.
Extension 4: scale DP knapsack/LIS under load.
Extension 5: scale graphs BFS/DFS under load.
Extension 6: scale heaps & top-K under load.
Extension 7: scale intervals & greedy under load.
Extension 8: scale two pointers under load.
Extension 9: scale sliding window under load.
Extension 10: scale hashing under load.
Extension 11: scale binary search under load.
Extension 12: scale DP knapsack/LIS under load.
Extension 13: scale graphs BFS/DFS under load.
Extension 14: scale heaps & top-K under load.
Extension 15: scale intervals & greedy under load.
Extension 16: scale two pointers under load.
Extension 17: scale sliding window under load.
Extension 18: scale hashing under load.
Extension 19: scale binary search under load.
Extension 20: scale DP knapsack/LIS under load.
Extension 21: scale graphs BFS/DFS under load.
Extension 22: scale heaps & top-K under load.
Extension 23: scale intervals & greedy under load.
Extension 24: scale two pointers under load.
Extension 25: scale sliding window under load.
Extension 26: scale hashing under load.
Extension 27: scale binary search under load.
Extension 28: scale DP knapsack/LIS under load.
Extension 29: scale graphs BFS/DFS under load.
Extension 30: scale heaps & top-K under load.
Extension 31: scale intervals & greedy under load.
Extension 32: scale two pointers under load.
Extension 33: scale sliding window under load.
Extension 34: scale hashing under load.
Extension 35: scale binary search under load.
Extension 36: scale DP knapsack/LIS under load.
Extension 37: scale graphs BFS/DFS under load.
Extension 38: scale heaps & top-K under load.
Extension 39: scale intervals & greedy under load.
Extension 40: scale two pointers under load.
Extension 41: scale sliding window under load.
Extension 42: scale hashing under load.
Extension 43: scale binary search under load.
Extension 44: scale DP knapsack/LIS under load.
Extension 45: scale graphs BFS/DFS under load.
Extension 46: scale heaps & top-K under load.
Extension 47: scale intervals & greedy under load.
Extension 48: scale two pointers under load.
Extension 49: scale sliding window under load.
Extension 50: scale hashing under load.
Extension 51: scale binary search under load.
Extension 52: scale DP knapsack/LIS under load.
Extension 53: scale graphs BFS/DFS under load.
Extension 54: scale heaps & top-K under load.
Extension 55: scale intervals & greedy under load.
Extension 56: scale two pointers under load.
Extension 57: scale sliding window under load.
Extension 58: scale hashing under load.
Extension 59: scale binary search under load.
Extension 60: scale DP knapsack/LIS under load.
Extension 61: scale graphs BFS/DFS under load.
Extension 62: scale heaps & top-K under load.
Extension 63: scale intervals & greedy under load.
Extension 64: scale two pointers under load.
Extension 65: scale sliding window under load.
Extension 66: scale hashing under load.
Extension 67: scale binary search under load.
Extension 68: scale DP knapsack/LIS under load.
Extension 69: scale graphs BFS/DFS under load.
Extension 70: scale heaps & top-K under load.
Extension 71: scale intervals & greedy under load.
Extension 72: scale two pointers under load.
Extension 73: scale sliding window under load.
Extension 74: scale hashing under load.
