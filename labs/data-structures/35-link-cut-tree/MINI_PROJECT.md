# MINI_PROJECT — Link-Cut Trees (35)

2-week build: dynamic-connectivity forest with an access-path benchmark vs naive DFS.

## 1. Objective
Working link-cut tree demo with invariant checker, connected/link/cut/pathAggregate, and benchmark of connectivity queries on a growing forest.

## 2. Requirements
1. Ops: link, cut, connected, evert, pathAggregate.
2. CLI: seeded sequence of link/cut/query.
3. ASCII preferred-path printout.
4. Benchmark at n=1k/10k/100k ops.
5. README section: LCT vs DSU-with-rollback.

## 3. Two-week plan
Week 1: LCT node model + access + connected with tests.
Week 2: evert + pathAggregate + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded links/cuts  2. connected queries  3. print paths
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n ops | Op | LCT (ns/op) | DFS baseline (ns/op) | Notes |
|---|---|---|---|---|
| 1k | connected |  |  |  |
| 10k | connected |  |  |  |
| 100k | connected |  |  |  |

## 6. Visualization idea
Print preferred-path splays and lazy-reverse flags before/after an access.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; path-max aggregate variant; JFR profile.
