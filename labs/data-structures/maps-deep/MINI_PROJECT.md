# MINI_PROJECT — Maps Deep

2-week build: a small in-memory KV store that swaps HashMap/TreeMap/LinkedHashMap/CHM backends.

## 1. Objective
One KvStore interface, four backends, parity tests, benchmark matrix, ASCII view.

## 2. Requirements
1. Operations: put, get, remove, containsKey, iterate (typed order).
2. CLI scenario: mixed workload.
3. ASCII printout of a few entries.
4. Benchmark at several n.
5. README section: when each backend wins.

## 3. Two-week plan
Week 1: interface + HashMap/TreeMap + parity.
Week 2: LinkedHashMap/CHM + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. seeded puts  2. iterate  3. print view
        // 4. benchmark with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n | Op | HashMap | TreeMap | LinkedHashMap | CHM |
|---|---|---|---|---|---|
| 1k | put |  |  |  |  |
| 10k | put |  |  |  |  |
| 100k | put |  |  |  |  |

## 6. Visualization idea
Print iteration order and load-factor after each run.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Add a Bloom front-filter; JFR profile.
