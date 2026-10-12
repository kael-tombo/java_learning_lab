# History: CompletableFuture

## FutureTask era (Java 5, JSR-166, 2004)

Doug Lea's JSR-166 gave `Future`/`FutureTask`: blocking `get()`, explicit
`cancel(true)` that *does* interrupt its runner. Composition meant manual
threads and latches — workable, thread-hungry, exception-hostile.

## The composition gap (2004–2014)

Guava's `ListenableFuture` (2009+) proved demand: callbacks on completion
instead of blocking waits. The JDK had no standard composable future; every
async HTTP client and service mesh invented its own chaining layer.

## CompletableFuture (Java 8, 2014)

CF shipped as a writable + monadic future: `complete`/`completeExceptionally`
from producers, `thenApply`/`thenCompose`/`thenCombine`/`allOf`/`anyOf` for
consumers. Sync stages run in the completing thread (zero-hop fast path);
`*Async` defaults to the shared common `ForkJoinPool`. The `cancel()` contract
broke from `FutureTask`: no owned thread exists, so `mayInterruptIfRunning`
is ignored by design (source-verified to this day).

## Deadlines (Java 9, 2017)

`orTimeout` and `completeOnTimeout` added in-place bounds on waiting — both
return `this`, completing the same future via the shared `Delayer` scheduler.
No wrapper stage, no new object identity.

## Stack discipline lessons (Java 8–present)

Deep sync-only chains execute depth-first in the completing thread
(`postComplete` recursion) — long pipelines learned to break with `*Async`.
Blocking stages on the default pool caused the well-known common-pool
starvation incidents, hardening the rule: I/O pipelines bring their own
executor.

## What endures

The thread rule (completing thread vs named executor) and the map/flatMap
split (`thenApply` vs `thenCompose`) are unchanged since Java 8. Every later
addition — timeouts, `copy()`, `completeAsync` — reuses the same completion-
stack mechanics.
