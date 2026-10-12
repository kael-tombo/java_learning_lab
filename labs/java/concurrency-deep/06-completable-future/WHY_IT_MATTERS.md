# Why CompletableFuture Matters

## Everyday code that depends on it

- Service fan-out: fetch profile + orders + recommendations, merge with
  `thenCombine`/`allOf`, bound with `orTimeout`.
- Hedged reads: `anyOf(primary, replica)` for tail-latency cuts.
- Async HTTP clients and reactive bridges that expose CF-returning APIs.
- Fallback chains: `exceptionally(ex -> cached)` keeping pages alive when a
  dependency fails.
- Test gates: `CompletableFuture.allOf(...)` joining parallel setup tasks.

## The bug classes it removes

- Thread-per-wait: dependents run in the completing thread — no blocked waiter
  thread per dependency.
- Nested-callback pyramids: `thenCompose` flattens sequential async calls the
  way `flatMap` flattens streams.
- Lost exceptions: `handle`/`exceptionally` route failures through the
  pipeline instead of dying in a worker thread.

## The bug classes it introduces

- Common-pool squatting: `supplyAsync(() -> blockingIO())` starves parallel
  streams sharing the pool — the classic "everything hung" incident.
- `CF<CF<U>>` nesting: `thenApply` with a future-returning lambda compiles
  and never yields the inner value.
- Silent drops: late `complete()` returns `false` and vanishes; `getNow(d)`
  misread as a timed wait skews data.
- `join()` inside a 1-thread pool stage: the thread waits for work that needs
  the same thread — self-deadlock.

## Interview-grade one-liners

- "Sync stages run in the completing thread; `*Async` defaults to the common pool."
- "`thenApply` is map, `thenCompose` is flatMap."
- "`allOf` is `CF<Void>` with no values; `anyOf` is `CF<Object>`."
- "`cancel()` ignores `mayInterruptIfRunning` — running tasks finish."
- "`orTimeout`/`completeOnTimeout` return `this`, in place."
