# Code Deep Dive — Randomized Algorithms

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.Random;

public final class Randomized {
    private static final Random RND = new Random(42);

    /** Randomised quicksort — always sorts, expected Θ(n log n). */
    public static void quicksort(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        int pivot = a[lo + RND.nextInt(hi - lo + 1)];
        int i = lo, j = hi;
        while (i <= j) {
            while (a[i] < pivot) i++;
            while (a[j] > pivot) j--;
            if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
        }
        quicksort(a, lo, j); quicksort(a, i, hi);
    }

    /** Randomised selection: k-th smallest (0-based) in expected Θ(n). */
    public static int quickselect(int[] a, int lo, int hi, int k) {
        while (lo < hi) {
            int pivot = a[lo + RND.nextInt(hi - lo + 1)];
            int i = lo, j = hi;
            while (i <= j) {
                while (a[i] < pivot) i++;
                while (a[j] > pivot) j--;
                if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
            }
            if (k <= j) hi = j; else if (k >= i) lo = i; else return a[k];
        }
        return a[lo];
    }
}
```

## Pitfalls

- Reporting only E[T] — the Θ(n²) worst case is still possible, just improbable.
- Using a time-based seed for a hash-randomised structure — the adversary reproduces it.
- Confusing "expected time" with "always fast" — the distribution has a tail.
- Treating a Monte Carlo pass as a proof — it is evidence; boost with more rounds.
- Assuming repetition with the same witness amplifies a Monte Carlo test — it does not.
- Reporting quickselect as worst-case O(n) — it is expected O(n); the worst case needs median-of-medians.

## Why the bounds hold

- **Randomised quicksort**: Θ(n log n) expected time, Θ(n log n) span — Θ(n²) worst, improbable.
- **Quickselect**: Θ(n) expected time, Θ(1) — recursive on one side.
- **Miller–Rabin**: Θ(k·log³ n) time, Θ(1) — error ≤ 4⁻ᵏ.
- **Reservoir sampling**: Θ(n) time, Θ(k) — one pass, unknown n.
- **Randomised hash ops**: Θ(1) expected time, Θ(n) worst — universal hashing.
- **Freivalds' verify**: Θ(n²) time, Θ(1) — Monte Carlo matrix check.

## Takeaway

# Theory — Randomized Algorithms
