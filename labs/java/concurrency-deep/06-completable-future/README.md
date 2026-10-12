# Lab 06 — CompletableFuture: README

## What this lab covers

`CompletableFuture<T>` is a writable future plus a pipeline: stages
(`thenApply`, `thenCompose`, `thenCombine`, `allOf`, `anyOf`, `exceptionally`,
`handle`, `whenComplete`) fire when the upstream completes. The thread rule
governs everything: sync stages run in the *completing thread*; `*Async`
stages run in the common pool (default) or your executor.

## Core contracts (from THEORY.md)

- `thenApply` = map (`T → U`); `thenCompose` = flatMap (`T → CF<U>`).
  `thenApply` with a future-returning function nests `CF<CF<U>>` — a bug.
- `allOf(...)` → `CF<Void>` (no values; `join` each input after); `anyOf`
  → `CF<Object>` (first completion wins, value or exception).
- `exceptionally` (fallback on failure) vs `handle` (unify both paths) vs
  `whenComplete` (peek, cannot change outcome).
- `cancel()` ignores `mayInterruptIfRunning` — a state race, not interruption.
- `orTimeout`/`completeOnTimeout` return `this` (in-place deadline, Java 9+).
- `join` (unchecked `CompletionException`) vs `get` (checked
  `ExecutionException` + `InterruptedException`).
- Default async executor is the common pool only when parallelism > 1
  (`USE_COMMON_POOL`); on 1-CPU targets it degrades to thread-per-task.

## Map of this lab

- `THEORY.md` + `CODE_DEEP_DIVE.md` — thread rule, map/flatMap, combining,
  handler contracts, cancel source, timeouts (ground truth, already done)
- `HOW_IT_WORKS.md`, `ARCHITECTURE.md`, `INTERNALS.md` — stage firing,
  pipeline topology, completion mechanics
- `MATH_FOUNDATION.md` — pipeline latency arithmetic, pool-sizing math
- `STEP_BY_STEP.md`, `EXERCISES.md` — build fetch→parse→combine chains
- `PERFORMANCE.md`, `DEBUGGING.md`, `COMMON_MISTAKES.md`, `REFACTORING.md`
- `QUIZ.md`, `FLASHCARDS.md`, `HISTORY.md`, `REFERENCES.md`, reflection pair

## Prerequisites

- Lab 05 (AQS parking — CF stages park/wake on completion the same way)
- 07-fork-join-pool common-pool notes (the default executor CF borrows)
- Lambdas and generics (`CF<CF<U>>` must read as an error at sight)

## Starter snippet

```java
CompletableFuture.supplyAsync(() -> fetchUser(42))
    .thenApply(u -> u.name())          // runs in completing thread
    .thenCompose(name -> fetchOrders(name)) // flatMap: T -> CF<U>
    .orTimeout(2, TimeUnit.SECONDS)    // in place, returns THIS
    .exceptionally(ex -> List.of());   // fallback on any failure
```

## Exit criteria

You can state where any stage runs, pick map vs flatMap blind, extract values
after `allOf`, choose the right error handler, explain why `cancel(true)`
does not stop a running `supplyAsync`, and keep blocking stages off the
common pool.
