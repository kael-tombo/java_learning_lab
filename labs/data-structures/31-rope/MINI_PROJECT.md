# MINI_PROJECT — Ropes (31)

2-week build: rope-backed text buffer with concat/split/index benchmarks.

## 1. Objective
Working Rope demo with invariant checker, cursor iterator, and benchmark vs StringBuilder for middle-insert workloads.

## 2. Requirements
1. Ops: concat, split, insertAt, deleteRange, charAt(cursor), length, toString.
2. CLI driving seeded edit script.
3. ASCII tree printout (weights at internal nodes).
4. Benchmark at n=1k/10k/100k leaf chars (ns/op).
5. README section: rope vs StringBuilder vs piece table.

## 3. Two-week plan
Week 1: leaf/node model + concat/split + invariant tests.
Week 2: cursor + rebalance heuristic + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. build rope from parts  2. split/concat  3. print tree
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | Rope (ns/op) | StringBuilder (ns/op) | Notes |
|---|---|---|---|---|
| 1k | insertAt |  |  |  |
| 10k | insertAt |  |  |  |
| 100k | insertAt |  |  |  |

## 6. Visualization idea
Print weights and leaf sizes before/after a split.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add leaf-size cap tuning; JFR allocation profile.
