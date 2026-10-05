# MINI_PROJECT — Graphs (Intro) (`05-graphs`)
> Implement + benchmark + visualize `Graph`. ~4–6 hours. Deliverable: code + chart + 1-page memo.

## Goal
Prove you own graphs: a clean implementation, honest numbers, and a picture
that makes the tradeoff obvious (scaling curve / shape / distribution).

## Part A — Implement (2h)
1. Complete `Graph` per EXERCISES E1 (all of: addVertex, addEdge, BFS, DFS, hasCycle, connectedComponents, shortest-path-BFS, topo-sort).
2. Add `validate()` (invariant assert), `toString`/dump, and fail-fast iterator.
3. JUnit 5 suite ≥12 tests incl. empty/singleton/duplicates/null/resize-or-rebalance/fail-fast/oracle-1k-ops.
```bash
javac -d out $(find src -name "*.java")
java -cp out org.junit.runner.JUnitCore GraphTest  # or mvn/gradle test
```

## Part B — Benchmark (1.5h)
Measure insert / lookup / delete at n = 1_000 / 10_000 / 100_000 (warm up JIT: 3 untimed runs, then 5 timed, report median).
Template:
```java
long t0 = System.nanoTime();
for (int i = 0; i < n; i++) s.add(rnd.nextInt());
long dt = System.nanoTime() - t0;
System.out.printf("n=%d insert %.2f ms%n", n, dt/1e6);
```
Also record: memory (Runtime total/free or JOL), resize/rotation counts, max probe/chain or height or FPR (as applicable).
Fill:
| n | insert ms | lookup ms | delete ms | aux metric (resizes / height / max-chain / FPR) |
|---|---|---|---|---|
| 1k |  |  |  |  |
| 10k |  |  |  |  |
| 100k |  |  |  |  |

## Part C — Visualize (1h)
Pick one (ASCII ok, PNG better):
- Scaling line chart (n vs ms, log-x) with expected O-curve overlay.
- Structure dump: array occupancy / linked shape / tree levels / heap array / trie branches / bloom bit density.
- Distribution: chain-length or probe histogram (hash), height histogram (trees), FPR vs k sweep (bloom).
Tools: any (matplotlib, Sheets, even hand-drawn photo). Commit image to `DIAGRAMS/` or paste path here.

## Part D — 1-page memo (30–45 min)
1. What did you build + invariant in one sentence.
2. Table from Part B + one chart.
3. Interpretation: does data match THEORY §5? Where/why does it deviate (JIT, GC, hashing, skew)?
4. Recommendation: when to use graphs vs closest alternative for social networks, routing, dependency graphs, recommendations.
5. Honest limits: worst input, memory ceiling, what you'd change (compression, paging, concurrency).

## Stretch
- Adversarial input demo (E5) with before/after numbers.
- Compare vs stdlib counterpart (`ArrayList/HashMap/TreeMap/PriorityQueue`) — who wins where and why.
- Profile allocation (JFR / VisualVM) and attribute one hotspot to layout (contiguous vs pointer-chase).

## Rubric (10 pts)
- Correctness + edge tests (3) · Benchmark rigor: warmup+median (2) · Visualization clarity (2) · Memo honesty/depth (2) · Code quality + Javadoc Big-O (1).
- Pass ≥7; redo any red section before REAL_WORLD_PROJECT.
