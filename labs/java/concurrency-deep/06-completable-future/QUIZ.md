# Quiz: CompletableFuture

## Questions (answers at end)

1. `completedFuture(1).thenApply(f)` — which thread runs `f`, and does any
   pool get involved?
2. Gate `g` is incomplete; thread F calls `g.complete("go")`. A `thenApply`
   was attached earlier. Where does it run?
3. `u.thenApply(x -> fetchAsync(x))` compiles. What is the result type, why is
   it wrong, and what is the fix?
4. After `allOf(a, b, c)`, how do you get `a`'s value? Why can't it block?
5. `anyOf(primary, replica)` wins with the replica. What is the result type,
   and what must you still do about the primary?
6. A future fails. Contrast the three terminals: `exceptionally(ex -> fb)` vs
   `handle((v, ex) -> ...)` vs `whenComplete((v, ex) -> ...)`.
7. `f.cancel(true)` on a running `supplyAsync` body — does the body stop?
   What do dependents observe?
8. `CF<String> b = f.orTimeout(2, SECONDS)` — what is `b == f`? What completes
   on expiry, and does the upstream stop?
9. `join()` vs `get()` on a failed future — exception types?
10. A stage on a 1-thread pool calls `inner.join()`, where `inner` needs the
    same pool. What happens and what is the fix?
11. On a 1-CPU container, default `supplyAsync` behaves differently. How, and
    which source constant governs it?
12. `allOf(a, b).join()` throws. Where are `b`'s failures if `a` failed first?

## Answers

1. The calling thread, synchronously — no pool touched.
2. In F, the completing thread.
3. `CF<CF<U>>` nesting — the inner future becomes the *value*. Fix:
   `thenCompose` (flatMap).
4. `a.join()` inside a continuation of the barrier — all inputs complete, so
   no blocking; failure surfaces as `CompletionException`.
5. `CF<Object>` — cast back. Explicitly cancel the primary; `anyOf` never
   cancels stragglers.
6. `exceptionally` recovers to `fb`; `handle` unifies both paths into one
   value; `whenComplete` only observes — the failure still propagates.
7. No — the flag is ignored (no owned thread). Body finishes; dependents see
   `CancellationException` (if cancel won the race).
8. `true` — in-place. *This* future completes with `TimeoutException`; the
   upstream keeps running unless cancelled.
9. `join` → unchecked `CompletionException(cause)`; `get` → checked
   `ExecutionException(cause)` (+ `InterruptedException`).
10. Self-deadlock: the thread waits for work needing itself. Fix: chain with
    `thenCompose` instead of blocking-join.
11. Thread-per-task (`new Thread` per submission) — governed by
    `USE_COMMON_POOL = commonPoolParallelism > 1`.
12. Attached as suppressed throwables on the surfaced exception — log the full
    `CompletionException`, not just the message.
