# Flashcards: CompletableFuture

## Q/A pairs

**Q:** Where does a sync stage (`thenApply`) run?
**A:** In the thread that completes the upstream — attaching thread if already
complete, `complete()` caller / pool worker otherwise.

**Q:** Where does `thenApplyAsync(f)` run by default?
**A:** `ForkJoinPool.commonPool()` — when `USE_COMMON_POOL` holds
(parallelism > 1); else a fresh thread per task.

**Q:** `thenApply` vs `thenCompose`?
**A:** Map vs flatMap: `T → U` giving `CF<U>` vs `T → CF<U>` giving `CF<U>`.
Future-returning lambda needs `thenCompose`.

**Q:** What does `allOf(a, b)` return and carry?
**A:** `CF<Void>` carrying no values — extract via `join()` on each input
after the barrier.

**Q:** What does `anyOf(...)` return?
**A:** `CF<Object>` — first completion wins (value or exception); cast back
yourself; losers keep running.

**Q:** `exceptionally` vs `handle` vs `whenComplete`?
**A:** `exceptionally`: failure-only → fallback value. `handle`: always →
unified value. `whenComplete`: always → peek, outcome unchanged.

**Q:** What does `cancel(mayInterruptIfRunning)` do with the flag?
**A:** Ignores it — CASes `CancellationException` into `result` if incomplete;
running `supplyAsync` bodies finish regardless.

**Q:** `orTimeout` / `completeOnTimeout` return value?
**A:** `this` — in-place deadlines on the same future, not derived stages.

**Q:** `join()` vs `get()` failure wrapping?
**A:** `join` → unchecked `CompletionException`; `get` → checked
`ExecutionException` + `InterruptedException`.

**Q:** What does `getNow(d)` do?
**A:** Non-blocking peek: value if complete, else `d`. Never waits.

**Q:** First-completion-wins scope?
**A:** Value, exception, or cancellation — whichever lands first is permanent;
late completions return `false`.

**Q:** Blocking I/O stage executor?
**A:** Dedicated bounded pool — never the common pool (shared with parallel
streams).

**Q:** Self-deadlock shape?
**A:** Stage on a 1-thread pool `join()`ing an inner future needing the same
thread. Chain (`thenCompose`) instead.
