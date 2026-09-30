# ANTI-PATTERNS: High-Performance Java Engineering
## Lab 15 | Production Engineering Academy

---

## Anti-Pattern 1: Naive Microbenchmarking with `System.currentTimeMillis()`

### The Mistake
```java
long start = System.currentTimeMillis();
for (int i = 0; i < 1_000_000; i++) {
    myMethod();
}
long elapsed = System.currentTimeMillis() - start;
System.out.println("Time: " + elapsed + "ms");
```

### Why It Fails
1. **Dead Code Elimination (DCE)**: The JIT compiler realizes the return value of `myMethod()` is never used, and optimizes the entire loop down to zero instructions!
2. **No Warmup**: Fails to account for C1/C2 JIT tiering and on-stack replacement (OSR).
3. **Timer Precision**: `currentTimeMillis()` has granularity of 1–15ms on Windows/Linux; completely useless for nanosecond operations.

### The Correct Production Fix
Always use **JMH (Java Microbenchmark Harness)**:
- Uses `@Benchmark` and `Blackhole.consume()` to prevent Dead Code Elimination.
- Automated multi-round warmups and forked JVM processes.

---

## Anti-Pattern 2: Pointer Chasing (`LinkedList` vs Contiguous Memory)

### The Mistake
Using `LinkedList<T>` or deep graph pointer trees for high-throughput collections.

### Why It Fails
- A `LinkedList` node is an independent object allocated scattered randomly across heap memory.
- Walking the list causes a CPU L1/L2 cache miss on **every single node reference**.
- `ArrayList<T>` stores references in contiguous memory, allowing the CPU hardware prefetcher to load subsequent elements into L1 cache before the CPU even requests them.
- In modern computing, sequential arrays are up to $50\times$ faster than pointer-linked lists.
