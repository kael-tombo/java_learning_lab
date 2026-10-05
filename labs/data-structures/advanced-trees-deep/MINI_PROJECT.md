# MINI_PROJECT — Advanced Trees (Deep)

2-week build: OrderMap lab harness comparing 4 implementations with a benchmark matrix.

## 1. Objective
One OrderedSet interface, four backends (AVL, RB-lite, treap, splay), JMH-style benchmark, ASCII visualization.

## 2. Requirements
1. Shared interface: add/remove/contains/inOrder/validation.
2. Each backend with an invariant checker.
3. CLI driving a mixed workload.
4. Benchmark table vs JDK TreeMap.
5. README section: when to pick which backend.

## 3. Two-week plan
Week 1: interface + two backends + invariants.
Week 2: two more backends + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. build each backend  2. run same workload  3. verify
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | AVL | RB | Treap | Splay | Notes |
|---|---|---|---|---|---|---|
| 1k | add |  |  |  |  |  |
| 10k | add |  |  |  |  |  |
| 100k | add |  |  |  |  |  |

## 6. Visualization idea
Print each tree's height and rotation counts after the workload.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add a B+ microbench; JFR allocation profile.
