# MINI_PROJECT — van Emde Boas Trees (29)

2-week build: vEB predecessor index over a small universe with a successor-query benchmark.

## 1. Objective
Working vEB tree demo answering pred/succ on u=2^16 with invariant checker and ns/op comparison vs TreeSet.

## 2. Requirements
1. Op set: insert, delete, member, pred, succ, min, max.
2. CLI driving seeded inserts + random pred queries.
3. ASCII cluster printout of one level.
4. Benchmark at n=1k/10k/100k (ns/op + memory).
5. README section: universe-size regimes where vEB wins.

## 3. Two-week plan
Week 1: recursion skeleton + min/max + member tests.
Week 2: pred/succ + delete repair + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded inserts  2. pred queries  3. print one cluster
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | vEB (ns/op) | TreeSet (ns/op) | Notes |
|---|---|---|---|---|
| 1k | pred |  |  |  |
| 10k | pred |  |  |  |
| 100k | pred |  |  |  |

## 6. Visualization idea
Print cluster[0..3] occupancy and summary before/after one delete.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add y-fast variant; JFR allocation profile.
