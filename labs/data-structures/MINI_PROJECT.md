# Data Structures Track - Mini Project

## Aim
Combine at least three structures from separate lab families into one
small working system (examples: trie + heap + Bloom filter, or segment
tree + DSU + LRU).

## Build options (choose one)
1. **Suggest box**: trie completions, LRU over hot prefixes, Bloom
   membership over document ids. Quote suggestion latency at p99.
2. **Rankings**: skip list or balanced tree for order, Fenwick tree for
   score histograms, HyperLogLog for distinct-player estimates.
3. **Net lab**: union-find for connectivity, BFS for paths, Merkle tree
   over snapshots for tamper-evident state.
4. **Text backend**: rope or unrolled-list buffer, versioned roots for
   undo, Rabin-Karp-style rolling search.

## Build rules
- One narrow interface per structure; swapping an implementation (say
  Fenwick for segment tree on prefix sums) must not touch callers.
- Seeded workload plus oracle comparison (HashMap / TreeMap / brute
  force): zero divergences across 10k operations.
- CSV operation log (op, nanos, size) feeding a one-page outcome note:
  goal vs measured, bottleneck, next scale move.

## Limits
- One module, zero frameworks; plain CLI or the JDK built-in HTTP
  server covers serving needs.
- Pure Java with fixed seeds so reruns reproduce exactly.
- Docs stay within 30-80 content lines; clarity beats cleverness.

## Hour plan (~8 hours)
1. First slice (2h): domain model plus two structures, CLI on fixture.
2. Second slice (3h): third structure, file persistence, config flags.
3. Third slice (2h): operation log, benchmark run, result chart.
4. Hardening (1h): oracle pass, hostile-input pass, short ops note.

## Scoring
- Cold-start end-to-end run (3 pts) - honest reproducible numbers (3)
  - hostile inputs covered (2) - report quality (2). Pass at 7 or more.
