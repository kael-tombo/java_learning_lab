# Thread Creation & Virtual Threads — Quiz

> **Instructions**: Answer each question before revealing the solution.

<details>
<summary><strong>1. What is the key difference between platform threads and virtual threads (Java 21+)?</strong></summary>
**Answer: Virtual threads are lightweight, user-mode threads managed by the JDK; platform threads are 1:1 mapped to OS threads.** Virtual threads have minimal memory footprint (~1KB vs ~1MB stack) and support millions of concurrent tasks.
</details>

<details>
<summary><strong>2. Which executor factory creates a virtual thread per task executor?</strong></summary>
**Answer: `Executors.newVirtualThreadPerTaskExecutor()`** — Returns an `ExecutorService` that creates a new virtual thread for each submitted task.
</details>

<details>
<summary><strong>3. What happens when a virtual thread blocks on I/O (e.g., socket read)?</strong></summary>
**Answer: The virtual thread is unmounted from its carrier platform thread; the carrier is freed to run other virtual threads.** This is the key scalability benefit — no OS thread is blocked.
</details>

<details>
<summary><strong>4. Which method creates a platform thread executor with a fixed pool size?</strong></summary>
**Answer: `Executors.newFixedThreadPool(n)`** — Creates a pool of n platform threads.
</details>

<details>
<summary><strong>5. What is `Thread.ofVirtual().start(runnable)` equivalent to?</strong></summary>
**Answer: `Thread.startVirtualThread(runnable)`** — Starts a new virtual thread running the given task.
</details>

<details>
<summary><strong>6. Can virtual threads be used with `synchronized` blocks?</strong></summary>
**Answer: Yes, but they pin the carrier thread** — While inside a `synchronized` block, the virtual thread cannot be unmounted. Avoid long-running synchronized sections in virtual threads.
</details>

<details>
<summary><strong>7. What is `ThreadLocal` behavior with virtual threads?</strong></summary>
**Answer: Each virtual thread has its own `ThreadLocal` values** — `ThreadLocal` is scoped to the virtual thread, not the carrier. `InheritableThreadLocal` works across virtual thread boundaries.
</details>

<details>
<summary><strong>8. How do you create a thread factory for virtual threads?</strong></summary>
**Answer: `Thread.ofVirtual().factory()` or `Thread.ofVirtual().name("worker-", 0).factory()`** — Returns a `ThreadFactory` that produces virtual threads.
</details>

<details>
<summary><strong>9. What is the default scheduler for virtual threads?</strong></summary>
**Answer: `ForkJoinPool` in LIFO mode** — Virtual threads are scheduled on a shared `ForkJoinPool` (common pool) using work-stealing.
</details>

<details>
<summary><strong>10. When should you prefer platform threads over virtual threads?</strong></summary>
**Answer: CPU-intensive work, native code via JNI, or when thread count is small (< 1000) and you need precise OS-thread control.** Virtual threads excel at high-concurrency I/O-bound workloads.
</details>

---
*Quiz complete. Review incorrect answers and re-read the THEORY.md for deeper understanding.*