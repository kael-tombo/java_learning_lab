# INTERVIEW QUESTIONS: High-Performance Java & Mechanical Sympathy
## Lab 15 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What is False Sharing and how does it manifest in Java applications?
**Answer**:
Modern CPUs cache memory in 64-byte chunks called cache lines. If two independent threads on different CPU cores write to two different variables that happen to be located within the same 64-byte memory block (e.g. adjacent fields in an object or adjacent elements in an array), the CPU cores invalidate each other's cache lines via the hardware MESI cache coherency protocol. Even though the variables are logically independent, the cores spend massive cycles waiting for bus arbitration and cache line invalidation. This can degrade throughput by 80–90%.
**Remedy**: Add 56 bytes of padding or use `@Contended` to force the variables onto separate cache lines.

---

## Staff / Principal Level (8+ Years)

### Q2: Why is the LMAX Disruptor vastly faster than standard `BlockingQueue` implementations in Java?
**Answer**:
1. **Ring Buffer with Pre-allocated Objects**: Pre-allocates an array of event objects during startup. Producers overwrite existing objects rather than allocating new nodes on the heap, eliminating GC churn entirely.
2. **Lock-Free Concurrency**: Publishers coordinate via atomic sequence numbers using CAS and memory barriers rather than kernel mutexes or condition variables.
3. **Cache Line Padding**: Sequence numbers are heavily padded with dummy longs to guarantee they never share a 64-byte cache line with adjacent data.
4. **Batched Consumer Draining**: When a consumer wakes up, it can process an entire batch of sequences up to the publisher cursor with a single memory read, amortizing cross-core synchronization costs over thousands of events.
