# CompletableFuture & Work-Stealing — Flashcards

| # | Question | Answer |
|---|----------|--------|
| 1 | **Future vs CompletableFuture?** | Future: blocking get(); CompletableFuture: async composition (thenApply, thenCompose) |
| 2 | **thenApply(Function) does?** | Transforms result, runs on completing thread |
| 3 | **thenApplyAsync(Function) does?** | Transforms result, submits to ForkJoinPool.commonPool |
| 4 | **thenCompose(Function) does?** | Chains dependent CompletableFuture (flattens) |
| 5 | **thenCombine(other, BiFunction) does?** | Waits for both, combines results |
| 6 | **allOf(futures...) returns?** | CompletableFuture<Void> — completes when ALL done |
| 7 | **anyOf(futures...) returns?** | CompletableFuture<Object> — completes when ANY done |
| 8 | **exceptionally(Function) does?** | Recovers from exception, returns fallback value |
| 9 | **handle(BiFunction) does?** | Handles both result and exception |
| 10 | **Work-stealing deque: local ops use which end?** | Front (LIFO) — push/pop own tasks |
| 11 | **Work-stealing deque: steal from which end?** | Tail (FIFO) — steal from victim's tail |
| 12 | **Why LIFO for local, FIFO for steal?** | LIFO: cache locality (recent tasks hot); FIFO: steal larger/older tasks, reduce contention |
| 13 | **ForkJoinPool common pool parallelism?** | `Runtime.getRuntime().availableProcessors() - 1` (default) |
| 14 | **How to set custom parallelism?** | `-Djava.util.concurrent.ForkJoinPool.common.parallelism=N` or custom ForkJoinPool |
| 15 | **Compensating thread = ?** | Extra thread added when worker blocks in managed blocker |
| 16 | **ManagedBlocker interface methods?** | `block()` — do blocking work; `isReleasable()` — can unblock? |
| 17 | **RecursiveTask vs RecursiveAction?** | RecursiveTask<V> returns value; RecursiveAction returns void |
| 18 | **fork() vs compute()?** | fork() — async submit to pool; compute() — synchronous execution |
| 19 | **join() in ForkJoinTask?** | Waits for result, helps steal other tasks while waiting (work-stealing) |
| 20 | **When to use CompletableFuture vs ForkJoinTask?** | CompletableFuture: async pipelines, I/O; ForkJoinTask: CPU-intensive divide-and-conquer |

---

**Study tip**: Cover the Answer column and quiz yourself. Shuffle by picking random numbers.