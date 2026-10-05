# MINI_PROJECT — Data Structures Advanced

2-week build: a "range analytics" harness with Fenwick + segment tree + Bloom, with parity tests.

## 1. Objective
One harness that ingests a stream of updates and answers prefix sums, range-add range-sum, and membership probes.

## 2. Requirements
1. Fenwick + segment tree parity checker (same outputs on random streams).
2. Bloom filter with measured FPR at planned capacity.
3. CLI driving a synthetic workload.
4. Benchmark ns/op at several n.
5. README decision: which backs which query.

## 3. Two-week plan
Week 1: Fenwick + segment tree + parity tests.
Week 2: Bloom + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded updates  2. parity check  3. print snapshots
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | Fenwick | SegTree | Bloom(insert) | Notes |
|---|---|---|---|---|---|
| 1k | add+query |  |  |  |  |
| 10k | add+query |  |  |  |  |
| 100k | add+query |  |  |  |  |

## 6. Visualization idea
Print Fenwick nonzero cells and segment-tree lazy pendings at a milestone.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add skip list; JFR allocation profile.
