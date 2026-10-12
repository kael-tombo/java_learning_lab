# CompletableFuture — Theoretical Foundation

## Core Concept

`CompletableFuture<T>` is a *writable* future plus a *monadic* pipeline:
stages (`thenApply`/`thenCompose`/`thenCombine`/`allOf`...) attached to a
future fire when it completes, in *whatever thread completes it* — unless
you pick the `*Async` variant with an explicit executor. Two ideas compose
everything here: **completion triggers dependents**, and **the completing
thread runs them** (the async variants only change *where* they run).

## Who Runs Your Stage: The Thread Rule

| Method shape | Runs in... |
|---|---|
| `thenApply(f)` (no executor) | the thread that completed the upstream stage — could be main, a pool thread, or the `complete()` caller |
| `thenApplyAsync(f)` | `ForkJoinPool.commonPool()` (default) |
| `thenApplyAsync(f, exec)` | your executor |
| `supplyAsync(s)` | common pool (default) or given executor |

Consequences:

- Non-async stages on an already-complete future run **synchronously in the
  calling thread** — `completedFuture(1).thenApply(f)` never touches a pool.
  Attaching chains to completed futures is free.
- `*Async` without executor means the **common pool** — a CPU-count-sized
  `ForkJoinPool` shared with parallel streams. Blocking I/O stages there
  starve every other user (the classic "my parallel stream hung" incident is
  usually a CF chain squatting the common pool). I/O-bound pipelines get a
  dedicated executor, always.
- Edge case from the source: `USE_COMMON_POOL = commonPoolParallelism > 1`
  — on a single-CPU container the default silently becomes a
  **thread-per-task executor**. Same code, unbounded threads, different
  machine. Size your own pool if the deployment target varies.

## thenApply (map) vs thenCompose (flatMap)

- `thenApply(x -> f(x))`: `T → U`, result `CF<U>`. Pure transformation.
- `thenCompose(x -> cf(x))`: `T → CF<U>`, result `CF<U>` — flattened.
  Using `thenApply` with a future-returning function gives the classic
  `CF<CF<U>>` nesting bug (compiles, never the value you wanted).

Mnemonic from streams: `map` vs `flatMap`, identical distinction.

## Combining: thenCombine / allOf / anyOf

- `a.thenCombine(b, (x, y) -> ...)`: waits for *both*, merges with a
  function. `thenAcceptBoth`/`runAfterBoth` are the side-effect shapes.
- `allOf(cf1, cf2, ...)`: `CF<Void>` — completes when **all** complete; it
  carries **no values** (source signature: `allOf(CF<?>...) → CF<Void>`).
  Extract results afterwards via `join()` on each input (all complete, so
  `join` can't block). If any input failed, `allOf` completes exceptionally
  — but a *different* input's exception may be the one surfaced.
- `anyOf(...)`: `CF<Object>` — first completion wins (value *or* exception).
  Cast the `Object` back yourself.
- Neither allOf nor anyOf *cancels* the losers/leftovers — stray stages keep
  running (and holding resources) unless you cancel them explicitly.

## Exceptions: Three Handlers, Three Contracts

| Handler | Input | Fires on... | Use |
|---|---|---|---|
| `exceptionally(f)` | `Throwable → T` | failure only | fallback value; result stays exceptional if f throws |
| `handle((v, ex) -> ...)` | `(T, Throwable) → U` | always (value or null + ex or null) | unify success/failure into one type |
| `whenComplete((v, ex) -> ...)` | peek, returns original | always | logging/metrics; cannot change the outcome |

Plus: `completeExceptionally(ex)` forces failure from the outside (the
producer-side dual of `complete(v)`); `orTimeout(t)` /
`completeOnTimeout(v, t)` (Java 9+) bound waiting in place — both return
`this` and complete the future itself, not a derived stage.

`join()` vs `get()`: `join` throws *unchecked* `CompletionException`
(wrapping the cause) — pipeline-friendly; `get` throws checked
`ExecutionException` + `InterruptedException` — interop-friendly. Same
outcome, different ceremony.

## cancel() Does NOT Interrupt (source-verified)

```java
public boolean cancel(boolean mayInterruptIfRunning) {
    boolean cancelled = (result == null) &&
        internalComplete(new AltResult(new CancellationException()));
    postComplete();
    return cancelled || isCancelled();
}
```

`mayInterruptIfRunning` is **ignored** — there is no thread to interrupt
(CF doesn't own its runners). Cancel only wins if the future hasn't
completed yet; an already-running `supplyAsync` task runs to completion
regardless, and dependent stages see `CancellationException`. True
cancellation (interrupting a running task) requires owning the
`Thread`/`Future` from your own executor (`ExecutorService.submit` +
`future.cancel(true)`), not a CF chain.

## The Stack Gotchas

- **Default-pool blocking**: `supplyAsync(() -> blockingIO())` on the
  common pool + `join()` = pool starvation under load. Dedicated
  bounded executor for blocking stages.
- **`getNow(default)`** returns the value *or default if incomplete* — not
  "wait briefly"; confusing it with a timed get is a silent-skew bug.
- **`complete()` races**: first completion wins; late `complete()` calls
  return `false` and are dropped silently. Exactly-once completion needs
  external coordination.
- **Exception swallowing in `allOf` chains**: `allOf(...).join()` throws the
  *first-recorded* failure; sibling failures attach as suppressed — log the
  full `CompletionException`, not just `getMessage()`.
- **Recursive `*Async` self-submission to a tiny pool**: chain stages that
  `join()` inner futures on a 1-thread executor deadlock against themselves
  (thread waits for a stage that needs the same thread).

## Key Invariants

1. A stage runs in the completing thread (sync methods) or the designated
   executor (async methods) — never anywhere else.
2. `allOf` yields no values (`CF<Void>`); `anyOf` yields `Object`.
3. Cancel is a state race, not an interruption — running tasks finish.
4. The default executor is the common pool *when parallelism > 1*,
   thread-per-task otherwise.
5. First completion (value, exception, or cancellation) wins permanently.
