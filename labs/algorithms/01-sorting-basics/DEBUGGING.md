# Debugging — Sorting Basics

## 1. Diagnostic Invariant Assertions

Enable JVM assertions using the `-ea` flag when running tests or development builds:

```java
// Method postcondition check
assert isSorted(arr) : "Array invariant violated: collection must be monotonically non-decreasing";

public static boolean isSorted(int[] arr) {
    if (arr == null || arr.length <= 1) return true;
    for (int i = 1; i < arr.length; i++) {
        if (arr[i] < arr[i - 1]) {
            System.err.printf("Inversion detected at index %d: arr[%d]=%d > arr[%d]=%d%n",
                    i, i - 1, arr[i - 1], i, arr[i]);
            return false;
        }
    }
    return true;
}

public static <T extends Comparable<T>> boolean isSorted(T[] arr) {
    if (arr == null || arr.length <= 1) return true;
    for (int i = 1; i < arr.length; i++) {
        if (arr[i].compareTo(arr[i - 1]) < 0) return false;
    }
    return true;
}
```

## 2. Pass-by-Pass State Snapshotting

When tracking inner loop logic (e.g., insertion shifts, bubble swaps):

```java
public static void printStep(String label, int[] arr, int highlightIdx1, int highlightIdx2) {
    StringBuilder sb = new StringBuilder();
    sb.append(String.format("%-15s: [", label));
    for (int i = 0; i < arr.length; i++) {
        if (i == highlightIdx1 || i == highlightIdx2) {
            sb.append("*").append(arr[i]).append("*");
        } else {
            sb.append(arr[i]);
        }
        if (i < arr.length - 1) sb.append(", ");
    }
    sb.append("]");
    System.out.println(sb);
}
```

## 3. Systematic Edge Case Test Matrix

Always debug sorting routines against the standard anomaly suite:
1. `null` reference and empty array `[]`
2. Single-element array `[42]`
3. Two elements in sorted order `[1, 2]` vs reverse order `[2, 1]`
4. All identical elements `[5, 5, 5, 5, 5]` (detects infinite loops in unstable partitioning)
5. Already sorted sequence `[1, 2, 3, 4, 5]` (verifies early exit optimization)
6. Reverse-sorted sequence `[5, 4, 3, 2, 1]` (worst-case trigger)
7. Extreme values `[Integer.MIN_VALUE, -1, 0, 1, Integer.MAX_VALUE]` (checks subtraction-based comparator overflow bugs!)

> [!WARNING]
> Never write comparators as `(a, b) -> a - b` because `Integer.MIN_VALUE - 1` overflows to `Integer.MAX_VALUE`, inverting sort order. Always use `Integer.compare(a, b)`.

## 4. Profiling Tools & Verification

- **JMH (Java Microbenchmark Harness)**: Measures nanoseconds/op avoiding JVM JIT warm-up bias.
- **Async-profiler**: Captures flame graphs of CPU cache misses during partitioning.
- **JVisualVM / JMC**: Confirms zero heap allocations for in-place sorting routines.
