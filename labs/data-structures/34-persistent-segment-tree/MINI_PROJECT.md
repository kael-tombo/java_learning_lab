# MINI_PROJECT — Persistent Segment Trees (34)

2-week build: persistent range-sum with version roots, plus kth-smallest-in-range demo.

## 1. Objective
Working persistent segment tree demo with invariant checker, version API, and benchmark vs copy-on-write full snapshots.

## 2. Requirements
1. Ops: versioned update, rangeSum(version,l,r), kthSmallest(l,r,k).
2. CLI: seeded updates + random versioned queries.
3. ASCII version-tree printout (root list with sizes).
4. Benchmark at n=1k/10k/100k updates.
5. README section: persistent vs copy-on-write.

## 3. Two-week plan
Week 1: path-copy nodes + update + rangeSum with tests.
Week 2: two-root kth + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded updates  2. versioned rangeSum  3. print roots
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | Persistent (ns/op) | Full-copy (ns/op) | Notes |
|---|---|---|---|---|
| 1k | update |  |  |  |
| 10k | update |  |  |  |
| 100k | update |  |  |  |

## 6. Visualization idea
Print which nodes are shared between the current and previous version.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; lazy propagation version; JFR profile.
