# MINI_PROJECT — Advanced Trees (AVL / Red-Black / B-Tree) (`09-advanced-trees`)
> Implement + benchmark + visualize `AVLTree`. ~4–6 hours. Deliverable: code + chart + 1-page memo.

## Goal
Prove you own balanced trees: a clean implementation, honest numbers, and a picture
that makes the tradeoff obvious (scaling curve / shape / distribution).

## Part A — Implement (2h)
1. Complete `AVLTree` per EXERCISES E1 (all of: rotate-left/right, insert-balance, delete-balance, split-join, bulk-load, range-scan, order-statistics, B-tree-split).
2. Add `validate()` (invariant assert), `toString`/dump, and fail-fast iterator.
3. JUnit 5 suite ≥12 tests incl. empty/singleton/duplicates/null/resize-or-rebalance/fail-fast/oracle-1k-ops.
```bash
javac -d out $(find src -name "*.java")
java -cp out org.junit.runner.JUnitCore AVLTreeTest  # or mvn/gradle test
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
4. Recommendation: when to use balanced trees vs closest alternative for DB indexes, filesystems, ordered stores, in-memory engines.
5. Honest limits: worst input, memory ceiling, what you'd change (compression, paging, concurrency).

## Stretch
- Adversarial input demo (E5) with before/after numbers.
- Compare vs stdlib counterpart (`ArrayList/HashMap/TreeMap/PriorityQueue`) — who wins where and why.
- Profile allocation (JFR / VisualVM) and attribute one hotspot to layout (contiguous vs pointer-chase).

## Schedule (evenings)
| Block | Time | Output |
|---|---|---|
| A implement | 2h | `AVLTree` + 12 tests green |
| B benchmark | 1.5h | metrics table filled, median of 5 |
| C visualize | 1h | 1 chart committed |
| D memo | 45min | 1-page decision memo |

## FAQ / traps (read before asking for help)
- "My benchmark is noisy" → warm up JIT, pin n, close other apps, report median not mean.
- "HashMap beats my hash table" → expected; stdlib has treeified bins + tuned spread. Match, then find one workload where yours wins (e.g., pre-sized bulk load).
- "Tree degenerates on sorted input" → that IS the lesson; shuffle or balance, then show the height before/after.
- "Bloom FPR higher than formula" → check k independence (use double hashing), bit-array sizing in BITS not bytes, hash quality.

## Submission checklist
- [ ] `src/` + tests + run commands documented (JDK version recorded).
- [ ] Metrics table + chart + memo in one page (no orphan numbers).
- [ ] One honest limitation + next scaling step named.

## Rubric (10 pts)
- Correctness + edge tests (3) · Benchmark rigor: warmup+median (2) · Visualization clarity (2) · Memo honesty/depth (2) · Code quality + Javadoc Big-O (1).
- Pass ≥7; redo any red section before REAL_WORLD_PROJECT.
