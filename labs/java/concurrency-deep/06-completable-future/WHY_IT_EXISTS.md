# Why CompletableFuture Exists

## The `Future` ceiling (Java 5)

`Future.get()` blocks one thread per wait; combining two futures needs manual
threads, latches, and exception plumbing. Fan-out ("fetch user AND orders,
then merge") and fallback ("on failure use cache") were hand-rolled state
machines — verbose, exception-hostile, and thread-hungry.

## The CF answer (Java 8)

A future you can *complete by hand* (`complete`, `completeExceptionally`) with
*dependent stages* that fire on completion — no thread waits for another.
`thenApply`/`thenCompose`/`thenCombine` express pipelines declaratively; the
completing thread runs sync dependents for free (no pool hop); `*Async`
variants name their executor explicitly.

## What each combinator solves

- `thenApply` (map): pure transform chained without blocking.
- `thenCompose` (flatMap): sequencing async calls without `CF<CF<U>>` nesting.
- `thenCombine`: merging two independent futures with a function.
- `allOf`: barrier over N futures (results pulled via `join` after).
- `anyOf`: hedged race — first completion wins.
- `exceptionally`/`handle`/`whenComplete`: fallback, unify, observe.
- `orTimeout`/`completeOnTimeout` (Java 9): in-place deadlines, no wrapper stage.

## What it deliberately does not do

- No interruption: `cancel()` cannot stop a running `supplyAsync` body — CF
  owns no threads to interrupt.
- No values in `allOf`: the barrier carries completion only; value flow stays
  in the inputs.
- No executor magic: the default is the shared common pool, with its CPU-count
  sizing and parallelism->1 thread-per-task edge — blocking pipelines must
  bring their own pool.
