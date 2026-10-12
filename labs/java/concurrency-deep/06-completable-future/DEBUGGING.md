# Debugging: CompletableFuture

## Identify the running thread

```java
stage.thenApply(v -> {
    System.out.println("stage runs in: " + Thread.currentThread().getName());
    return v;
});
```

`main` = completed-future inline run. `ForkJoinPool.commonPool-worker-N` =
default async. `finisher-thread` = whoever called `complete()`. If a blocking
stage prints a common-pool worker, move it to a dedicated executor.

## Hang diagnosis

- Chain never fires: the gate future was never completed — no stage runs
  without a completion event. Assert `gate.isDone()` at the hang point.
- `join()` never returns: upstream blocked (I/O on common pool) or a
  1-thread-pool self-join. Dump stacks: all workers in `WAITING` on the same
  future = the self-deadlock shape.
- `allOf` hangs: one input never completes — `allOf` needs *every* input.
  Print each `isDone()` to find the straggler.

## Exception forensics

```java
try { result.join(); }
catch (CompletionException e) {
    System.out.println("cause: " + e.getCause());
    for (Throwable s : e.getSuppressed()) System.out.println("suppressed: " + s);
}
```

`join` wraps in `CompletionException`; `get` wraps in `ExecutionException`.
`allOf` surfaces the first failure — siblings hide in `getSuppressed()`.
Unhandled async failures with no `join`/`get` vanish silently: terminate every
chain with `whenComplete` logging or an explicit join.

## Timeout vs stuck

`orTimeout` completing exceptionally with `TimeoutException` proves the
upstream exceeded the deadline — the upstream still runs (timeouts never
cancel). If work continues consuming resources after timeout, chain
`.orTimeout(...).whenComplete(...)` with explicit `upstream.cancel(false)`.

## Cancel vs complete races

`cancel()` returning `false` means something already completed the future
(value, exception, or earlier cancel). Log `isCancelled()` vs
`isCompletedExceptionally()` to distinguish — both make `join()` throw, with
different causes (`CancellationException` vs the real failure).

## Tooling

`jstack`: common-pool workers parked in blocking I/O = pool squatting.
JFR: `Java Monitor Blocked` + thread dumps correlate `join()` waits with the
holding stack. Assert `future.orTimeout(...) == future` in tests to lock the
in-place contract; assert thread names to lock executor placement.
