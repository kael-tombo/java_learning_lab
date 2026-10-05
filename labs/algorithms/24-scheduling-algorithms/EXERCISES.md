# EXERCISES — Scheduling Algorithms
> Implement + trace + edge cases. Java templates. Lab `24-scheduling-algorithms`.

## Setup
- JDK 17, JUnit 5, no external deps. Create `src/main/java/lab/24_scheduling_algorithms/`.

## E1 — Warm-up trace (paper, 10 min)
- Given small instance of Scheduling Algorithms (EDF, SJF/SRPT, list scheduling; Graham bound 2-1/m), simulate 5 steps by hand.
- Fill table: step | data structure snapshot | decision | why safe.
- Deliverable: photo/scan of table + invariant sentence.

## E2 — Implement core (Java template)
```java
package lab.exercise;
import java.util.*;
public class Core {
    // TODO: implement Scheduling Algorithms core.
    // Contract: EDF, SJF/SRPT, list scheduling; Graham bound 2-1/m
    // Invariant to maintain: feasibility / priority invariants; exchange arguments.
    // Target complexity: SJF optimal avg wait; EDF optimal uniprocessor; multiprocessor NP-hard.
    public static int solve(int[] a) {
        // E2a: handle null/empty (throw IllegalArgumentException or return sentinel).
        // E2b: init auxiliary structures.
        // E2c: main loop with invariant comment each iteration.
        // E2d: return answer; add reconstruct() variant returning full solution.
        throw new UnsupportedOperationException("implement me");
    }
    public static void main(String[] args) {
        System.out.println(solve(new int[]{3,1,2,1,5}));
    }
}
```
- Tasks: complete TODOs; add `reconstruct()` returning actual solution, not just value.
- Tests: empty, singleton, sorted asc/desc, duplicates, max-size random vs brute force.

## E3 — Edge cases drill
- Null / empty / single element / all-equal / adversarial (e.g., reverse-sorted).
- Overflow: use long for accumulators; mod arithmetic where needed.
- Off-by-one: inclusive vs exclusive bounds; test both.
- Stability / tie-breaking: define and assert deterministic rule.
- Fuzz: 200 random small inputs vs O(2^n) brute force oracle.

## E4 — Complexity measurement
- Instrument op counts (comparisons, hash ops, allocations).
- Time n=1k/10k/100k/1M; plot; confirm SJF optimal avg wait; EDF optimal uniprocessor; multiprocessor NP-hard.
- Identify cache/GC effects; run with `-Xmx2g`, 5 warmups.

## E5 — Variant (stretch)
- Implement second variant (e.g., memoized vs tabulated; sequential vs parallel).
- Compare code size, speed, memory on same inputs.
- Write 5-line decision rule for when to prefer each.

## E6 — Debugging challenge
- Given buggy implementation (swapped loop order / missing base case / int overflow):
- (a) find failing test in <5 min, (b) fix with minimal diff, (c) add regression test.

## E7 — Trace table template
| Step | Input slice | Aux state | Choice | Invariant OK? |
|---|---|---|---|---|
| 0 | … | init | — | yes |
| 1 | … | … | … | yes |

## E8 — Self-check rubric
- [ ] Compiles clean, no warnings. [ ] All edge tests pass.
- [ ] Invariant comments present. [ ] Benchmark table filled.
- [ ] Can explain feasibility / priority invariants; exchange arguments aloud in 60 seconds.

## Hints
- Start from brute force, then add memo/pruning/order.
- Draw the state DAG / decision tree for n=4 before coding.
- Keep functions pure; isolate I/O in main().

## E9 - Additional edge sweep (extend coverage)
- MIN_VALUE and MAX_VALUE inputs; empty-string vs null distinctions.
- Single-row and single-column matrices; k=0 and k>n parameter extremes.
- Duplicate-heavy and already-optimal inputs (idempotence check).

## E10 - Property-based tests (manual loop, 500 seeds)
- For small n, assert solve(x) equals bruteForce(x).
- Assert determinism across runs and idempotence where applicable.

## E11 - Time-boxed interview simulation (25 min)
- 5 min: restate problem plus invariant. 12 min: code core. 5 min: edge tests.
- 3 min: complexity derivation aloud. Score with E8 rubric.
