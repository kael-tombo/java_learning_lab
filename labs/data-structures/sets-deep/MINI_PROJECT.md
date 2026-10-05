# MINI_PROJECT — Sets Deep

2-week build: a "tag index" harness with HashSet/TreeSet/LinkedHashSet/BitSet, parity tests, benchmark.

## 1. Objective
One TagIndex interface, four backends, parity tests, benchmark, ASCII view.

## 2. Requirements
1. add/contains/remove/iterate.
2. Custom comparator for TreeSet backend.
3. CLI scenario.
4. Benchmark.
5. README decision: when each wins.

## 3. Two-week plan
Week 1: interface + HashSet/TreeSet + parity.
Week 2: LinkedHashSet/BitSet + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seed tags  2. iterate  3. print view
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | HashSet | TreeSet | LinkedHashSet | BitSet |
|---|---|---|---|---|---|
| 1k | add |  |  |  |  |
| 10k | add |  |  |  |  |
| 100k | add |  |  |  |  |

## 6. Visualization idea
Print iteration orders for each backend side-by-side.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add EnumSet backend; JFR profile.
