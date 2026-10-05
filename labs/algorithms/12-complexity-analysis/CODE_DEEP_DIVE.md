# CODE_DEEP_DIVE — Complexity Analysis (Timing Harness)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
public final class Complexity { // measures T(n); validates O() claims empirically
    public interface Task { void run(int n); } // workload at size n
    public static long timeMs(Task t, int n, int warm, int reps) { // robust median-ish
        for (int i = 0; i < warm; i++) t.run(n); // O(warm×T) JIT warmup (load-bearing)
        long best = Long.MAX_VALUE;              // best-of avoids GC noise
        for (int r = 0; r < reps; r++) {         // O(reps×T) samples
            long s = System.nanoTime();          // ns precision
            t.run(n);                            // measured workload
            best = Math.min(best, System.nanoTime() - s); // min filter
        }
        return best / 1_000_000;                 // ms
    }
    public static void doubling(int[] sizes, Task t) { // ratio test: O(n)→2×, O(n log n)→2×+, O(n²)→4×
        long prev = -1;                          // O(1)
        for (int n : sizes) {                    // sizes ×2 each step
            long ms = timeMs(t, n, 3, 5);        // O(warm+reps) per size
            double ratio = prev < 0 ? Double.NaN : (double) ms / prev; // growth factor
            System.out.printf("n=%d ms=%d ratio=%.2f%n", n, ms, ratio); // read ratios
            prev = ms;                           // update
        }
    }
    public static long fibTab(int n) { // O(n) reference workload
        if (n <= 1) return n; long a = 0, b = 1;
        for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; }
        return b;
    }
}
```

## 2. Complexity Annotations
- Warmup removes JIT bias (cold `O(T + compile)` vs steady `O(T)`).
- Best-of-reps filters GC pauses (conservative under-estimate, stable ratios).
- Doubling ratios: linear→2, linearithmic→~2.1–2.3, quadratic→4, log→~1, exp→≫2.

## 3. Pitfalls (5 + fixes)
1. No warmup → JIT noise dominates small n. Fix: ≥3 warm runs.
2. Single sample → GC outlier. Fix: min/median of ≥5.
3. Dead-code elimination (empty run optimized away) → consume result (Blackhole/print).
4. Nano→ms truncation hides sub-ms → use ns for small n.
5. Background load skews → close apps, pin sizes ×2 exactly for ratio math.

## 4. Micro-Opts
- JMH for publication-grade; this harness for lab-grade (document limits).

## 5. Test Snippets
```java
Complexity.doubling(new int[]{1000,2000,4000,8000}, n -> Complexity.fibTab(n)); // ratios ≈2
```

## 6. Checklist
- [ ] Warmup + reps. [ ] Ratio interpretation. [ ] DCE guard.
