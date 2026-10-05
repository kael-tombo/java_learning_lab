# MINI_PROJECT — Cache-Oblivious Structures (30)

2-week build: cache-oblivious array layout + binary-search benchmark vs row-major.

## 1. Objective
Working demo of a static vEB-laid-out array supporting search, with invariant checker and ns/op comparison vs sorted array + classic binary search at several n.

## 2. Requirements
1. Op set: build(layout), search (iterative), height print.
2. CLI: seeded build + random searches.
3. ASCII layout printout for n=15.
4. Benchmark at n=1k/10k/100k (ns/op).
5. README section: when the layout wins.

## 3. Two-week plan
Week 1: layout construction (BFS/vEB order) + search tests.
Week 2: benchmark sweep + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. build vEB layout  2. search  3. print layout
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | vEB-layout (ns/op) | Row-major (ns/op) | Notes |
|---|---|---|---|---|
| 1k | search |  |  |  |
| 10k | search |  |  |  |
| 100k | search |  |  |  |

## 6. Visualization idea
Print the recursive cut at depth √h and which nodes share a cache line.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add funnelsort micro-benchmark; JFR cache-miss proxy.
