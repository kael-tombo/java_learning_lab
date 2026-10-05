# MINI_PROJECT — Queue & Stack Deep

2-week build: a "task dispatch" harness with ArrayDeque FIFO, PriorityQueue, and a bounded blocking queue; benchmark matrix.

## 1. Objective
One DispatchQueue interface, three backends, parity tests, benchmark, ASCII view.

## 2. Requirements
1. offer/poll/peek semantics.
2. Custom comparator for task priority.
3. CLI scenario.
4. Benchmark.
5. README when each wins.

## 3. Two-week plan
Week 1: interface + ArrayDeque + PriorityQueue + parity.
Week 2: blocking queue + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. enqueue tasks  2. drain  3. print peeks
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | ArrayDeque | PriorityQueue | ArrayBlockingQueue |
|---|---|---|---|---|
| 1k | offer+poll |  |  |  |
| 10k | offer+poll |  |  |  |
| 100k | offer+poll |  |  |  |

## 6. Visualization idea
Print head, peek, size after milestones.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add PriorityBlockingQueue; JFR profile.
