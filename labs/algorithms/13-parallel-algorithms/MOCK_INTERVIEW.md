# Mock Interview: Parallel Algorithms: Chunked Sums, Safe Counters, Parallel Sort
> Three worked questions on parallelism basics. Each answer is complete runnable Java; outputs below were observed.

## Q1: Sum 1..100000 with 4 threads over disjoint chunks.
Key insight: Disjoint chunks need no synchronization: each thread owns its range, and the join-then-add step is the only sequential part. Equal values from any thread count prove the partition covered everything exactly once.
Complexity: Work Theta(n), span Theta(n/p + log p) for the chunking and final combine.
```java
public class L13Q1PSum {
    public static void main(String[] args) throws Exception {
        int n = 100000, p = 4;
        long[] part = new long[p];
        Thread[] ts = new Thread[p];
        for (int k = 0; k < p; k++) {
            final int f = k;
            ts[k] = new Thread(() -> {
                long s = 0;
                for (int i = f * (n / p) + 1; i <= (f + 1) * (n / p); i++) s += i;
                part[f] = s;
            });
            ts[k].start();
        }
        for (Thread t : ts) t.join();
        long total = part[0] + part[1] + part[2] + part[3];
        System.out.println("psum=" + total + " expect=" + ((long) n * (n + 1) / 2));
    }
}
```
Observed output: `psum=5000050000 expect=5000050000`
Follow-up: Where is the sequential bottleneck here, and how does Amdahl's law bound the speedup from it?

## Q2: Increment a shared counter from 4 threads, safely and unsafely.
Key insight: Read-modify-write on a plain long can lose increments when threads interleave, so shared counters use atomics. Here the atomic total always equals threads times iterations, which is the reproducible assertion the snippet checks.
Complexity: Work Theta(p * iters); contention on one atomic is the span limiter.
```java
import java.util.concurrent.atomic.AtomicLong;
public class L13Q2Race {
    static long racy = 0;
    public static void main(String[] args) throws Exception {
        int p = 4, iters = 50000;
        AtomicLong safe = new AtomicLong();
        Thread[] ts = new Thread[p];
        for (int k = 0; k < p; k++) {
            ts[k] = new Thread(() -> {
                for (int i = 0; i < iters; i++) { racy++; safe.incrementAndGet(); }
            });
            ts[k].start();
        }
        for (Thread t : ts) t.join();
        System.out.println("safe=" + safe.get() + " expect=" + (p * iters));
    }
}
```
Observed output: `safe=200000 expect=200000`
Follow-up: Why can the racy value differ between runs, and what does that nondeterminism imply for testing concurrent code?

## Q3: Verify Arrays.parallelSort sorts correctly.
Key insight: Parallel sort splits, sorts, and merges; for tiny inputs it behaves like sequential sort. Checking the output is sorted (each element <= the next) is a cheap self-test that does not depend on timing.
Complexity: Work O(n log n), span roughly O(log^2 n)-class for the parallel merge phases.
```java
import java.util.Arrays;
public class L13Q3PSort {
    public static void main(String[] args) {
        int[] a = {9, 4, 7, 1, 8, 2, 6, 3, 5, 0};
        Arrays.parallelSort(a);
        boolean ok = true;
        for (int i = 1; i < a.length; i++) if (a[i - 1] > a[i]) ok = false;
        System.out.println("psorted=" + ok + " " + Arrays.toString(a));
    }
}
```
Observed output: `psorted=true [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`
Follow-up: When is parallel sort slower than sequential sort, and what term (work vs overhead) dominates there?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
