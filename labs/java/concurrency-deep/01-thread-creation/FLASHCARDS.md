# Thread Creation & Virtual Threads — Flashcards

| # | Question | Answer |
|---|----------|--------|
| 1 | **Virtual thread vs platform thread memory?** | Virtual ~1KB stack; Platform ~1MB stack |
| 2 | **Executor for virtual thread per task?** | `Executors.newVirtualThreadPerTaskExecutor()` |
| 3 | **Virtual thread blocks on I/O → what happens?** | Unmounts from carrier; carrier runs other virtual threads |
| 4 | **Fixed platform thread pool factory?** | `Executors.newFixedThreadPool(n)` |
| 5 | **Start virtual thread (factory method)?** | `Thread.ofVirtual().start(runnable)` |
| 6 | **Start virtual thread (static method)?** | `Thread.startVirtualThread(runnable)` |
| 7 | **Virtual thread in synchronized block?** | Pins carrier thread — cannot unmount |
| 8 | **ThreadLocal with virtual threads?** | Each virtual thread has its own copy |
| 9 | **Virtual thread factory?** | `Thread.ofVirtual().factory()` |
| 10 | **Virtual thread default scheduler?** | ForkJoinPool (common pool, LIFO/work-stealing) |
| 11 | **When to use platform threads?** | CPU-intensive, JNI, small thread counts, precise OS control |
| 12 | **When to use virtual threads?** | High-concurrency I/O (web servers, crawlers, DB clients) |
| 13 | **Can virtual threads be daemon?** | Yes — `Thread.ofVirtual().daemon().start(runnable)` |
| 14 | **Virtual thread name pattern?** | `Thread.ofVirtual().name("worker-", 0).start(runnable)` |
| 15 | **Carrier thread = ?** | Platform thread that runs virtual threads |
| 16 | **Unmount = ?** | Virtual thread yields carrier (e.g., on I/O, sleep, park) |
| 17 | **Pinning = ?** | Virtual thread stuck to carrier (synchronized, native call) |
| 18 | **How to avoid pinning?** | Use `ReentrantLock` instead of `synchronized` |
| 19 | **Virtual thread stack trace includes?** | Virtual thread frames + carrier frames (for debugging) |
| 20 | **Structured concurrency with virtual threads?** | `StructuredTaskScope` (JEP 453) — treats multiple subtasks as single unit |

---

**Study tip**: Cover the Answer column and quiz yourself. Shuffle by picking random numbers.