# CompletableFuture Internals

## Result encoding

One field decides everything: `result == null` means incomplete. Otherwise it
holds the value (possibly `null` legitimately — wrapped), or an `AltResult`
carrying the exception (`ExecutionException`-style cause,
`CancellationException`, or timeout). First CAS wins; every later `complete`,
`completeExceptionally`, or `cancel` returns `false`.

## Dependent stack (`postComplete` shape)

```text
complete(v):
  CAS result: null -> v (lose -> return false)
  postComplete():
    pop Completion c from stack
    c.tryFire(SYNC, v)   // sync stages run HERE, depth-first
    c.tryFire(ASYNC, v)  // async stages submitted to executor
```

Sync dependents execute inline — a 10K-stage chain on one completion is a
10K-deep call stack in the completing thread (long chains want an `*Async`
break or batching).

## Uni vs Bi completions

- `UniApply` (`thenApply`): one upstream, fires once with its value.
- `UniCompose` (`thenCompose`): fires the function, then *links* to the
  returned inner CF — the outer completes when the inner does (two-hop fire).
- `BiApply` (`thenCombine`): waits for both upstreams; fires in the thread of
  the *second* completion.
- `AnyOf`/`AllOf`: counter- or first-win-based firing over N inputs.

## Async supply mechanics

`supplyAsync(s)` wraps `s` in a `ForkJoinTask`-adapted runnable submitted to
the default executor: common pool iff `USE_COMMON_POOL`
(`commonPoolParallelism > 1`), else `new Thread(task).start()` per submission.
That fallback is why single-CPU containers show unbounded thread growth under
`supplyAsync` storms — same bytecode, different machine.

## Timeout internals

`orTimeout(t, unit)` schedules a task on the shared `ScheduledExecutor`
(`Delayer`): on expiry it calls `internalComplete(TimeoutException)` on
*this*. `completeOnTimeout(v, t)` does the same with value `v`. No derived
stage exists — identity check `f.orTimeout(...) == f` is `true`.

## Cancel source shape

```java
public boolean cancel(boolean mayInterruptIfRunning) {
    boolean cancelled = (result == null) &&
        internalComplete(new AltResult(new CancellationException()));
    postComplete();
    return cancelled || isCancelled();
}
```

`mayInterruptIfRunning` never appears in the body. Contrast
`FutureTask.cancel(true)`, which interrupts its runner thread — CF has no
runner to interrupt, only a `result` to race for.

## Join vs get unwrapping

`join()`: incomplete→wait; failure→unchecked `CompletionException(cause)`.
`get()`: same wait; failure→checked `ExecutionException(cause)` plus
`InterruptedException` on interrupt. `getNow(d)`: no wait — `d` if incomplete.
