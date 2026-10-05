# Exercises: Union-Find / Disjoint Set Union (DSU)

Implement from scratch in Java (no AI-written core logic). Trace each exercise on paper before coding; commit the trace as a comment.

## Beginner

1. **DSU from scratch**: Implement parent/rank arrays with makeSet, find, union. Trace find(3) on 0..6 after unions (0,1),(2,3),(1,2).
```java
// Lab 11-union-find: DSU from scratch
DisjointSetUnion dsu = new DisjointSetUnion(7);
```

2. **Path compression**: Add halving vs full compression. Count pointer hops before/after on a chain of 8.
```java
// Lab 11-union-find: Path compression
dsu.find(7); // count hops, then find(7) again
```

3. **Union by rank/size**: Attach smaller under larger; prove height <= log2 n with ranks. Test worst-case order.
```java
// Lab 11-union-find: Union by rank/size
dsu.union(a, b); // assert height bound
```

## Intermediate

4. **Kruskal MST**: Sort edges, union endpoints, collect MST. Run on a 6-node graph; verify total weight.
```java
// Lab 11-union-find: Kruskal MST
List<Edge> mst = Kruskal.mst(n, edges);
```

5. **Percolation check**: Model grid percolation with virtual top/bottom; open sites until connected.
```java
// Lab 11-union-find: Percolation check
perc.open(r, c); assert perc.percolates() == ...;
```

6. **Offline connectivity**: Answer interleaved queries by replaying unions; compare naive BFS answers.
```java
// Lab 11-union-find: Offline connectivity
for (q : queries) ans.add(dsu.connected(q.a, q.b));
```

## Advanced

7. **Accounts merge**: Union emails sharing an account id; output merged groups sorted.
```java
// Lab 11-union-find: Accounts merge
Map<String,Integer> idOf = ...; // union per account
```

8. **Rollback spike**: Record union changes on a stack; snapshot + rollback to checkpoint k.
```java
// Lab 11-union-find: Rollback spike
int s = dsu.snapshot(); ...; dsu.rollback(s);
```

## Traces and checks
- Commit one ASCII hand-trace per exercise (state before/after the hot path).
- Invariant holds after every op; trace matches execution or the exercise fails.

## Grading rubric

- Correctness 40 / hand traces 20 / edge-case tests 20 / benchmark note 20.

## How to work this set

- Timebox: Beginner 25 min, Intermediate 40 min, Advanced 60 min.
- Write the trace first; code second; fuzz last.
- If stuck more than 20 min, shrink the input to n = 3 and re-trace.

## Common wrong turns

- Skipping the hand trace and debugging blind against failing tests.
- Testing only sorted/insertion-order input; adversarial order finds the real bugs.
- Forgetting the empty and singleton cases in every new operation.
- Measuring performance without warmup and reporting noise as signal.

## Stretch

- S1. Swap one core design choice (array vs map, iterative vs recursive) and re-benchmark.
- S2. Write the 5-line lesson-learned note: what broke, what fixed it, what to check first next time.

## Done when

- [ ] 8/8 exercises green with committed traces
- [ ] Fuzz run clean for 10k random ops against the naive model
- [ ] Benchmark table filled at n = 1k / 10k / 100k
