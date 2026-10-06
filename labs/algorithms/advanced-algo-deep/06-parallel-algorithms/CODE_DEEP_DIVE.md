# Code Deep Dive — Parallel Algorithms

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

public final class ParallelSum {
    /** Fork/join tree-reduce with Θ(n) work, Θ(log n) span. */
    static final class Sum extends RecursiveTask<Long> {
        final long[] a; final int lo, hi;
        Sum(long[] a, int lo, int hi) { this.a = a; this.lo = lo; this.hi = hi; }
        protected Long compute() {
            if (hi - lo <= 1024) {
                long s = 0; for (int i = lo; i < hi; i++) s += a[i];
                return s;
            }
            int mid = (lo + hi) >>> 1;
            Sum l = new Sum(a, lo, mid); l.fork();
            Sum r = new Sum(a, mid, hi);
            return r.compute() + l.join();
        }
    }

    public static long sum(long[] a) {
        return new ForkJoinPool().invoke(new Sum(a, 0, a.length));
    }
}
```

## Pitfalls

- Counting speedup on a single machine — the span is the answer.
- Races on a shared counter — use atomics, locks, or a reduction.
- Over-splitting into tasks smaller than the fork overhead.
- Blocking I/O inside fork/join workers.
- Assuming T₁/T∞ is unreachable — it is the ceiling on useful processors.
- Locking a hot counter — it serialises; prefer a reduction.

## Why the bounds hold

- **Work T₁**: — time, — — total operations on one processor.
- **Span T∞**: — time, — — longest dependency chain.
- **Brent T_p**: T₁/p + T∞ time, Θ(T₁) — ≤ that bound.
- **Parallel scan**: Θ(n) time, Θ(log n) span — up-sweep + down-sweep.
- **Parallel merge sort**: Θ(n log n) time, Θ(n) / Θ(log³ n) span — merge dominates.
- **Amdahl speedup**: 1/(f+(1-f)/p) time, — — ceilings at 1/f.

## Takeaway

# Theory — Parallel Algorithms
