# MINI_PROJECT — Count-Min Sketch (27)

2-week build: streaming top-k word-frequency reporter with sketch vs HashMap benchmark.

## 1. Objective
Working Count-Min Sketch demo over a synthetic word stream, with invariant checker, top-k reporting via heap, and ns/op benchmark table vs exact HashMap baseline.

## 2. Requirements
1. Full op set (add, estimate, merge) with one-sided error checker.
2. CLI driving a seeded scenario (zipfian stream).
3. ASCII dump of one row of counters after each milestone.
4. Benchmark at n=1k/10k/100k (ns/op + memory estimate).
5. README section: when the sketch beats the HashMap.

## 3. Two-week plan
Week 1: skeleton + hash family (Murmur-style seeds) + invariant tests.
Week 2: top-k + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded stream  2. add/estimate loop  3. print min-row state
        // 4. benchmark add() with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | Sketch (ns/op) | HashMap (ns/op) | Notes |
|---|---|---|---|---|
| 1k | add(w) |  |  |  |
| 10k | add(w) |  |  |  |
| 100k | add(w) |  |  |  |

## 6. Visualization idea
Print each row's first 8 counters before/after a milestone; highlight the min-cell of the queried word.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add Count-Sketch median variant; profile allocations with JFR.
