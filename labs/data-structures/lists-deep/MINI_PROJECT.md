# MINI_PROJECT — Lists Deep

2-week build: list-workload harness comparing ArrayList/LinkedList/ArrayDeque/Vector across access/insert/iterate.

## 1. Objective
One harness driving seeded workloads, invariant checkers, and a benchmark matrix.

## 2. Requirements
1. Parity vs Arrays.asList-backed model.
2. Implement your own ArrayList and LinkedList with invariants.
3. CLI workload: append-heavy, random-access-heavy, middle-insert-heavy.
4. Benchmark table.
5. README decision: when each wins.

## 3. Two-week plan
Week 1: own ArrayList + invariants.
Week 2: own LinkedList + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seed workload  2. run scenario  3. print states
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | ArrayList | LinkedList | ArrayDeque | Vector |
|---|---|---|---|---|---|
| 1k | add |  |  |  |  |
| 10k | add |  |  |  |  |
| 100k | add |  |  |  |  |

## 6. Visualization idea
Print capacities, node counts, and iterator state at milestones.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add CopyOnWriteArrayList variant; JFR profile.
