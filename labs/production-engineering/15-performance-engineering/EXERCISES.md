# EXERCISES: Mechanical Sympathy & High-Performance Java Engineering
## Lab 15 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Benchmark and Eliminate False Sharing Using JMH & VarHandle

### 1. Objective
Measure and eliminate the $80\% - 90\%$ throughput collapse caused by multi-threaded false sharing on contiguous memory addresses using JMH and cache line isolation.

### 2. Implementation Tasks
1. Create `UnpaddedCounters.java`:
   - 4 `volatile long` fields: `c0, c1, c2, c3`.
2. Create `PaddedCounters.java`:
   - 4 `volatile long` fields, but each field is separated by 7 dummy `long` fields (56 bytes of padding) so that each field sits alone on a distinct 64-byte cache line.
3. Write a JMH benchmark with `@Threads(4)`:
   - Thread 0 increments `c0`.
   - Thread 1 increments `c1`.
   - Thread 2 increments `c2`.
   - Thread 3 increments `c3`.
4. Run the benchmark across 3 JVM forks:
   ```bash
   mvn clean package
   java -jar target/benchmarks.jar FalseSharingBenchmark -t 4 -f 3 -wi 5 -i 10
   ```
5. Capture Linux hardware metrics during the test:
   ```bash
   perf c2c record -p $(pgrep -f "benchmarks.jar") -- sleep 10
   perf c2c report --stdio
   ```

### 3. Expected Benchmark Results
- `UnpaddedCounters`: $\approx 80{,}000 - 150{,}000\text{ ops/ms}$.
- `PaddedCounters`: $\ge 3{,}500{,}000\text{ ops/ms}$ ($> 20\times$ speedup).
- `perf c2c`: `UnpaddedCounters` will demonstrate thousands of `Remote HITM` events; `PaddedCounters` will show zero.

---

## Exercise 2: Contiguous Array vs. LinkedList Cache Miss Profiling with `perf stat`

### 1. Objective
Quantify the CPU cycle and cache miss penalties of pointer chasing (`LinkedList`) versus contiguous sequential memory (`int[]` and `ArrayList`) over 10,000,000 integers.

### 2. Implementation Tasks
1. Build a test fixture initializing:
   - `int[] primitiveArray` with $10^7$ sequentially incrementing values.
   - `ArrayList<Integer>` with $10^7$ boxed integers.
   - `LinkedList<Integer>` with $10^7$ boxed integers.
2. Write a JMH benchmark measuring average iteration time to compute the sum of each data structure.
3. Run under Linux `perf stat`:
   ```bash
   perf stat -e cycles,instructions,cache-references,cache-misses,L1-dcache-load-misses \
     java -cp target/benchmarks.jar com.learning.lab15.PointerChaseRunner
   ```

### 3. Expected Observations
- **Iteration Duration**:
  - `int[]`: $\approx 2.5\text{ ms}$
  - `ArrayList<Integer>`: $\approx 14.0\text{ ms}$ (object header dereference + unboxing)
  - `LinkedList<Integer>`: $\approx 280.0\text{ ms}$ ($> 100\times$ slower than primitive array!)
- **Cache Miss Ratios**:
  - `int[]`: Cache miss rate $< 1.2\%$ (L1/L2 streaming prefetcher operates at theoretical bus limit).
  - `LinkedList`: Cache miss rate $> 38.5\%$ (every pointer traverse triggers an L3 cache stall or DRAM access).

---

## Exercise 3: Zero-Allocation Lock-Free Ring Buffer Object Pool

### 1. Objective
Implement an allocation-free, GC-free object pool backed by a power-of-2 ring buffer capable of sustaining 20,000,000 borrow/release operations per second without triggering a single TLAB allocation.

### 2. Architecture Specifications
1. Pre-allocate an array of size $2^{16} = 65{,}536$ `OrderEvent` objects during startup.
2. Implement lock-free sequence management:
   - `claimSequence`: Atomic long tracking borrowed slots.
   - `releaseSequence`: Atomic long tracking returned slots.
3. Use bitwise index masking: `slot = seq & (capacity - 1)`.
4. Ensure sequence variables are padded to prevent False Sharing between publisher and consumer threads.
5. Verify zero GC allocations:
   ```bash
   asprof -e alloc -d 20 -f /tmp/pool_alloc.html $(pgrep -f "PoolRunner")
   ```
   The resulting flame graph must contain **zero** `[alloc]` frames originating from the hot borrow/release loop.

---

## Exercise 4: Simulating and Resolving JIT Megamorphic Deoptimization

### 1. Objective
Reproduce the exact HotSpot C2 compiler deoptimization cascade when a third implementation is dynamically introduced to a hot polymorphic interface.

### 2. Implementation Tasks
1. Define an interface `PricingStrategy` with method `double calculateDiscount(double price)`.
2. Create three implementations:
   - `StandardPricing`
   - `VolumePricing`
   - `TieredPricing`
3. Run a warmup loop of 1,000,000 iterations alternating strictly between `StandardPricing` and `VolumePricing` (Bimorphic call site).
4. Verify via `-XX:+PrintCompilation` that HotSpot C2 inlines both strategies into the caller method.
5. In iteration 1,000,001, inject a single instance of `TieredPricing` into the hot path.
6. Observe the immediate JIT output:
   - `made not entrant` deoptimization log.
   - Trap signature `reason=class_check`.
7. Refactor the call site to use an enum-driven direct dispatcher (`switch (strategy.getType())`) and re-verify that all calls are permanently inlined without megamorphic vtable degradation.
