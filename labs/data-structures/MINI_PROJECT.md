# Data Structures Track — Mini Project

## Goal
Build one small system combining at least three structures from different
lab groups (e.g. trie + heap + Bloom filter, or segment tree + DSU + LRU).

## Suggested builds (pick one)
1. **Search box service**: trie autocomplete, LRU for hot suggestions,
   Bloom pre-filter over the document id set. Measure suggest p99.
2. **Leaderboard service**: skip list or balanced tree for ranking, Fenwick
   tree for score distribution, HyperLogLog for unique-player counts.
3. **Network lab**: union-find for connectivity, graph BFS for routes,
   Merkle tree over snapshots for tamper-evident history.
4. **Editor backend**: rope or unrolled-list buffer, persistent versions for
   undo, rolling hash (Rabin-Karp style) for search.

## Requirements
- Narrow interfaces per structure; swap one implementation without
  touching callers (e.g. segment tree vs Fenwick for prefix sums).
- Seeded workload generator plus an oracle cross-check (TreeMap/HashMap/
  sorted brute force) with zero mismatches on 10k operations.
- Metrics log (CSV: op, nanos, size) and a one-page report: target vs
  actual, bottleneck, next scaling step.

## Constraints
- Single module, no frameworks; `com.sun.net.httpserver` or CLI is fine.
- Pure-Java, deterministic seeds, reproducible runs.
- 30-80 line discipline applies to docs; code stays readable over clever.

## Milestones (~8 hours)
1. Slice 1 (2h): domain model + two structures wired, CLI works on fixture.
2. Slice 2 (3h): third structure + persistence + config flags.
3. Slice 3 (2h): metrics + benchmark + chart.
4. Hardening (1h): oracle test, edge/chaos pass, ops note.

## Grading
- Works end-to-end from cold start (3 pts) - Metrics honest + reproducible
  (3) - Edge/chaos handled (2) - Report depth (2). Ship >= 7/10.
