# THEORY: Performance Engineering & Mechanical Sympathy
## Lab 15 | Production Engineering Academy

---

## 1. Hardware Architecture & Latency Numbers Every Architect Must Know

To write high-performance software, code must be aligned with physical hardware ("Mechanical Sympathy", coined by Martin Thompson):

| Operation | Latency | Scaled Comparison (1 CPU Cycle = 1 sec) |
|:---|:---:|:---:|
| L1 Cache Hit | 0.5 - 1.0 ns | 1 second |
| Branch Misprediction | 3.0 - 5.0 ns | 5 seconds |
| L2 Cache Hit | 3.0 - 4.0 ns | 4 seconds |
| L3 Cache Hit | 10 - 20 ns | 20 seconds |
| Main Memory (DRAM) Access | 50 - 100 ns | 1.5 minutes |
| NVMe SSD I/O Read | 10 - 50 μs | 12 hours |
| Same Data Center Network Round Trip | 0.5 ms | 6 days |
| Disk Seek (Spinning HDD) | 5 - 10 ms | 2.5 months |
| Cross-Continent Network (NYC to London) | 65 ms | 2 years |

---

## 2. CPU Cache Lines & False Sharing

CPUs do not read memory in single bytes or words; memory is loaded into L1/L2/L3 caches in fixed **64-byte chunks called Cache Lines**:
- **False Sharing**:
  Suppose Thread 1 on Core 0 modifies variable `A`, and Thread 2 on Core 1 modifies variable `B`.
  If `A` and `B` happen to reside in the **same 64-byte cache line**, whenever Core 0 writes to `A`, the MESI cache coherency protocol invalidates the entire cache line on Core 1!
  Even though Thread 1 and Thread 2 are modifying completely distinct variables, the CPU cores constantly invalidate and reload each other's L1 caches over the memory bus.
  This degrades multi-threaded throughput by up to **90%**!
- **Solution**:
  - Memory padding (inserting dummy `long` fields).
  - Or using Java's `@jdk.internal.vm.annotation.Contended` (requires `-XX:-RestrictContended`).

---

## 3. The LMAX Disruptor Architecture

Traditional Java concurrent queues (`ArrayBlockingQueue`, `LinkedBlockingQueue`) rely on lock contention and dynamic node allocation:
- Every `put()` and `take()` acquires a lock or increments an `AtomicInteger` CAS, bottlenecking cores.
- `LinkedBlockingQueue` allocates a `Node` object for every message, creating intense GC churn.

The **LMAX Disruptor** achieves 10+ million operations/sec with microsecond latency:
1. **Ring Buffer**: Pre-allocated array of events (Zero GC allocation at runtime).
2. **Lock-Free Sequence Numbers**: Publishers claim slots using atomic CAS on a single `Sequence` cursor.
3. **No False Sharing**: Sequences are heavily padded with 56 bytes of dummy data.
4. **Batch Consumption**: A consumer lagging behind the publisher can read 100 messages in a single memory access without locking.
