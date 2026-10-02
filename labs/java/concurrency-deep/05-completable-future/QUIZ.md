# CompletableFuture & Work-Stealing — Quiz

> **Instructions**: Answer each question before revealing the solution.

<details>
<summary><strong>1. What is the key difference between `ExecutorService.submit()` and `CompletableFuture.supplyAsync()`?</strong></summary>
**Answer: `submit()` returns a `Future` (blocking `get()`); `supplyAsync()` returns a `CompletableFuture` (non-blocking composition via `thenApply`, `thenCompose`, etc.).** CompletableFuture enables async pipelines.
</details>

<details>
<summary><strong>2. What does `thenApply(Function)` do?</strong></summary>
**Answer: Transforms the result of the previous stage** — runs synchronously on the same thread by default (unless `thenApplyAsync`).
</details>

<details>
<summary><strong>3. What does `thenCompose(Function)` do?</strong></summary>
**Answer: Chains a dependent CompletableFuture** — flattens nested futures. Use when the transformation returns another `CompletableFuture`.
</details>

<details>
<summary><strong>4. What is the difference between `thenApply` and `thenApplyAsync`?</strong></summary>
**Answer: `thenApply` runs on the completing thread; `thenApplyAsync` submits to the default async executor (ForkJoinPool.commonPool).**
</details>

<details>
<summary><strong>5. How do you combine two independent CompletableFutures?</strong></summary>
**Answer: `thenCombine(other, BiFunction)` or `thenAcceptBoth(other, BiConsumer)`** — waits for both, then combines results.
</details>

<details>
<summary><strong>6. What does `allOf(CompletableFuture<?>...)` return?</strong></summary>
**Answer: A `CompletableFuture<Void>` that completes when ALL given futures complete.** Use `.join()` to wait.
</details>

<details>
<summary><strong>7. What does `anyOf(CompletableFuture<?>...)` return?</strong></summary>
**Answer: A `CompletableFuture<Object>` that completes when ANY given future completes.** Result is the completed future's value.
</details>

<details>
<summary><strong>8. What is work-stealing in ForkJoinPool?</strong></summary>
**Answer: Idle workers steal tasks from the tail of busy workers' deques.** Each worker has a local deque (LIFO for own tasks, FIFO for steals) — reduces contention.
</details>

<details>
<summary><strong>9. When does ForkJoinPool create new threads?</strong></summary>
**Answer: When all workers are busy/blocked and there are pending tasks** — up to parallelism level. Compensates for blocked threads (managed blocker).
</details>

<details>
<summary><strong>10. How do you run a blocking operation safely in ForkJoinPool?</strong></summary>
**Answer: Use `ManagedBlocker` or `ForkJoinPool.managedBlock()`** — signals the pool to add a compensating thread to maintain parallelism.
</details>

---
*Quiz complete. Review incorrect answers and re-read the THEORY.md for deeper understanding.*