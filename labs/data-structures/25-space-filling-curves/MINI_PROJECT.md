# MINI_PROJECT — Space-Filling Curves (Z-order / Hilbert)

Build + benchmark + visualize: tile-server spatial index for map rendering. (4–6 hours)

## 1. Objective
Working `Space-Filling Curves (Z-order / Hilbert)` demo with seeded data, visualized state, and a benchmark table vs baseline.

## 2. Requirements
1. Full op set from THEORY with invariant checker.
2. CLI or tests driving a realistic scenario.
3. ASCII/Swing/JavaFX visualization of internal state.
4. Benchmark at n=1k/10k/100k (ns/op + memory).
5. README section: when this wins vs baseline.

## 3. Milestones
M1 skeleton + checker (1h). M2 ops + tests (2h). M3 visualize (1h). M4 benchmark + writeup (1h).

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. load seeded data  2. run scenario  3. print state
        // 4. benchmark hot path with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)

| n | Op | Yours (ns/op) | Baseline (ns/op) | Notes |
|---|---|---|---|---|
| 1k | encode(x,y) |  |  |  |
| 10k | encode(x,y) |  |  |  |
| 100k | encode(x,y) |  |  |  |

## 6. Visualization idea
Print the structure after each milestone op; snapshot before/after the maintenance path.

## 7. Grading
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate the trace; add a second baseline; profile allocations with JFR.
