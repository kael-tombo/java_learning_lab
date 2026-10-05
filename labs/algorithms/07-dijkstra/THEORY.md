# THEORY — Dijkstra's Algorithm
> Mechanics + invariants + complexity proof sketch for Dijkstra.

## 1. Problem Statement
- Input: graph with `w(e) ≥ 0`, source `s`.
- Output: `dist[]` least-weight distances, `prev[]` paths.
- Precondition: NO negative weights (even one breaks finality).
- Success: `O((V+E) log V)` binary-heap, paths reconstructable.
- Contrast: BFS = unit weights; Bellman-Ford = negatives allowed, slower.

## 2. Algorithm Mechanics
- Init `dist[s]=0`, others `∞`, PQ `{(0,s)}`, `settled=set()`.
- Pop min `(d,u)`; if stale (`d>dist[u]`) skip; mark settled; relax: `if dist[u]+w<dist[v]` update + push.
- Stale-entry skipping is required (Java PQ has no decrease-key).
- Early exit: stop when target popped (its distance final).
- Undirected: insert both directions. Dense: naive `O(V²)` array scan may win.
- Path: follow `prev[]` back from target; unreachable stays `∞`.

## 3. Invariants
- I1 (settled final): popped/settled `u` has `dist[u]=δ(s,u)` (true shortest).
- I2 (frontier bound): unsettled `dist[v]` = best path using only settled intermediates.
- Init: settled=∅, `dist[s]=0` — holds.
- Maintenance: min-frontier `u` cannot be improved — any alt path must exit settled set via edge ≥ `dist[u]` (non-negativity).
- Termination: PQ empty → all reachable settled; unreachable `∞` correct.
- Negative edge breaks I1: `s→a=5, s→b=6, b→a=-4` — `a` settles at 5, true is 2.

## 4. Worked Trace
- `s→A=4, s→B=2, B→A=1, A→T=1`: pop s(0), push A4 B2 → pop B2 relax A→3 → pop A3 → pop T4. `dist[T]=4` via B.
- Stale: old `(4,A)` skipped after `(3,A)` settles A.
- Unreachable `X`: stays `∞`, `prev=-1`.

## 5. Complexity Proof Sketch
- Each vertex settled once → ≤ `V` pops; each edge relaxes ≤ once → ≤ `E` pushes.
- Binary heap ops `O(log V)` → `O((V+E) log V)`; naive scan `O(V²+E)`.
- Space `O(V+E)` graph + `O(V)` dist/prev + `O(V)` PQ.
- Correctness induction on settle order using non-negativity (I1 proof above).
- Early-exit sound: target settle = final by I1; no need to drain PQ.
- Fibonacci-heap `O(E+V log V)` — theory; binary heap is the Java practice.

## 6. Correctness Argument
- Greedy-choice: min-frontier extraction safe iff weights ≥ 0.
- Counter-example (above) must be traceable by learner to feel the breakage.

## 7. When NOT to Use
- Any negative weight → Bellman-Ford.
- All-pairs dense → Floyd-Warshall / Johnson.
- Unit weights → BFS (simpler, faster constants).
- Goal-directed + heuristic → A* (Dijkstra with guidance).

## 8. Java Notes
- `PriorityQueue<long[]{d,v}>` with `Comparator.comparingLong`; use `long` distances.
- No decrease-key: push duplicates + stale check `if (d!=dist[u]) continue`.
- `dist` as `long[]` filled with `Long.MAX_VALUE/4` (avoid overflow on `+w`).

## 9. Common Misconceptions
- "Dijkstra handles negatives if no cycle" — false; single negative edge suffices to break.
- "Visited-on-push is fine" — must settle on pop, not push.
- "PQ size stays V" — with lazy pushes it can reach E; stale check required.

## 10. Checklist
- [ ] Non-negative precondition asserted.
- [ ] Stale-entry skip present + tested.
- [ ] Negative-edge counter-example traced.
- [ ] `long` distances + early-exit for target.
