# EXERCISES: Mechanical Sympathy & Performance Engineering
## Lab 15 | Production Engineering Academy

---

## Exercise 1: Benchmark and Eliminate False Sharing

### Objective
Measure the dramatic throughput difference between false sharing unpadded counters and cache-line padded counters using JMH.

### Tasks
1. Create a class `UnpaddedCounters` with 4 contiguous `volatile long` fields.
2. Create a class `PaddedCounters` with 56 bytes of padding between each `volatile long` field.
3. Write a JMH benchmark where 4 threads concurrently increment their respective counter fields.
4. Run the benchmark:
   ```bash
   mvn clean package
   java -jar target/benchmarks.jar BenchmarkCounters -t 4
   ```
5. Verify that `PaddedCounters` demonstrates $4\times - 8\times$ higher throughput than `UnpaddedCounters`.

---

## Exercise 2: Contiguous Array vs LinkedList Cache Miss Benchmark

### Tasks
1. Create an `ArrayList<Integer>` with 10,000,000 integers and a `LinkedList<Integer>` with identical elements.
2. Write a JMH benchmark measuring total time to iterate and sum all elements.
3. Observe that `ArrayList` executes substantially faster due to CPU L1 prefetching.
4. Run under Linux `perf stat`: verify that `LinkedList` produces $10\times$ more cache misses.
