# MINI_PROJECT — Dancing Links (32)

2-week build: Algorithm X solver for Sudoku-mini and exact-cover count, with a search-node benchmark.

## 1. Objective
Working DLX solver with invariant checker (cover/uncover round-trip), a Sudoku encoder, and node-count comparison vs naive backtracking.

## 2. Requirements
1. Op set: addColumn, addRow, cover(c), uncover(c), search.
2. CLI: seeded Sudoku (4x4 or 9x9 mini).
3. ASCII column-header state printout.
4. Benchmark: node count and ms at problem sizes.
5. README section: when DLX beats naive backtracking.

## 3. Two-week plan
Week 1: node model + cover/uncover + round-trip invariant tests.
Week 2: MRV search + Sudoku encoder + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. build matrix  2. search  3. print headers
        // 4. benchmark nodes with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| size | Op | DLX (ms, nodes) | Naive BT (ms, nodes) | Notes |
|---|---|---|---|---|
| 4x4 | solve |  |  |  |
| 9x9 | solve |  |  |  |

## 6. Visualization idea
Print removed/restored column counts after each cover/uncover.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add polyomino tiling; JFR allocation profile.
