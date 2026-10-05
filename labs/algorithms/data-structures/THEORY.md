# THEORY — Data Structures Track
> Mechanics + invariants + complexity proof. Track `data-structures`.

## 1. Problem statement (5)
- Input, output, constraints stated formally per structure.
- For this track: graphs (V,E) queries + trees (ordered/hierarchical) queries.
- Context: foundation for every graph/DP/search lab.
- Success = correct output on all edge cases + proven bounds.

## 2. Intuition in one paragraph (8)
- Data structures maintain a promise: adjacency reflects edges; BST order reflects keys; heap shape reflects priority; DSU sets partition vertices.
- Think of it as maintaining a promise while scanning/building the answer.
- If the promise ever breaks, the algorithm has a repair step (sift, rotate, path compress).
- Example domains: social graphs, routing tables, leaderboards, autocomplete.

## 3. Formal model (10)
- State: defines current partial solution.
- Decision: choice at each step derived from structural invariant.
- Transition: how state evolves (see recurrence below).
- Objective: support ops (insert/delete/query) within stated bounds.
- Model instances: `adj[u] neighbor lists`; `BST: left<k<right`; `heap: parent≤children`; `DSU parent/size`.

## 4. Mechanics step-by-step (15)
1. Initialize structures (arrays, heaps, hash maps as needed).
2. Establish base case / empty-structure invariant.
3. Iterate / recurse over input in defined order.
4. Apply local rule (greedy choice, DP transition, pointer move).
5. Maintain auxiliary data (prefix sums, pi table, residual graph).
6. Prune / skip provably useless branches.
7. Record best answer seen so far.
8. Terminate when input exhausted or target reached.
9. Reconstruct solution via parent pointers if needed.
10. Validate output with checker.
11. BFS: queue layers; record dist/parent on first visit.
12. DFS: color white/gray/black; timestamps for topo/cycles.
13. DSU: union by size + path compression.
14. Heap: sift-up on insert, sift-down on extract-min.
15. Segment tree: build O(n), query/update O(log n) over intervals.

## 5. Worked trace (12)
- Small input example: BFS on 5-node graph; BST insert 3,1,4.
- Table-driven trace (step | state | decision | invariant holds?).
- Step 1: init — invariant holds vacuously.
- Step 2: first decision — show why alternatives are dominated.
- Step 3: middle — show auxiliary structure update.
- Step 4: last — show answer extraction.
- Key lesson: trace exposes off-by-one and order bugs early.
- DSU trace: unions (1-2,3-4,2-3) with path compression.
- Heap trace: insert 5,3,8 then extract-min.
- Segment trace: range sum [1,4) over 8 leaves.

## 6. Invariants (precise) (10)
- I1: BFS queue holds frontier in nondecreasing distance.
- I2: DFS gray stack is exactly the current root path.
- I3: BST inorder yields sorted keys at all times.
- I4: heap array satisfies heap order after every public op.
- I5: DSU parent pointers always resolve to the set representative.
- Initialization: I holds before loop (empty prefix).
- Maintenance: each iteration re-establishes I (case split).
- Termination: I + exit condition => correctness.

## 7. Correctness proof sketch (10)
- Lemma 1 (safety): maintained invariant holds each iteration.
- Lemma 2 (progress): measure strictly decreases/increases toward goal.
- Theorem: on termination output is optimal/correct.
- Proof by induction on steps using I1–I5.
- Counterexample if invariant dropped: construct small failing input.
- BFS: first-visit distance is shortest (layer argument).
- Topo: DAG finish order reversed is valid (no back edge).

## 8. Complexity analysis with proof (12)
- Count primitive ops per step; sum over steps.
- Recurrence where applicable: T(n) = a·T(n/b) + f(n) (see MATH_FOUNDATION.md).
- Apply Master theorem / Akra-Bazzi / accounting method.
- Typical bounds: BFS/DFS O(V+E); BST O(h), O(log n) balanced; heap O(log n); DSU O(α(n)); segment O(log n); trie O(L).
- Space: adjacency O(V+E); trees O(n).
- Lower bound argument: comparison / information-theoretic where relevant.
- Tightness: exhibit worst-case family achieving the bound.

## 9. Variants and connections (8)
- Iterative vs recursive formulations.
- Adjacency list vs matrix; implicit vs explicit graphs.
- Randomized / parallel / streaming variants.
- Reduces to / from neighboring lab topics.
- When NOT to use: input too small, constraints violated, simpler method wins.

## 10. Common misconceptions (5)
- Confusing average with worst case.
- Forgetting reconstruction vs value-only DP.
- Off-by-one in indices / hash modulus.
- Assuming sorted input when it is not.
- Ignoring integer overflow in cost accumulation.

## 11. Interview signal (3)
- State invariant first, then code.
- Derive complexity without hand-waving.
- Name one pitfall and its test.

## 12. Checklist (2)
- [ ] Can replay trace without notes. [ ] Can prove bound. [ ] Can code in 20 min.
