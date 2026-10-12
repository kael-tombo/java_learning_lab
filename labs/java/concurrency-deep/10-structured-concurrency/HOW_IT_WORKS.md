# How It Works: Scope Lifecycle End to End

## 1. Owner creates the scope

The thread that will consume the results constructs a
`StructuredTaskScope.ShutdownOnFailure` (or `ShutdownOnSuccess`) inside
`try`-with-resources. Construction records the creating thread as owner
and captures current scoped-value bindings for later fork checks.

## 2. Owner forks subtasks

Each `scope.fork(callable)` registers one subtask and starts its thread,
returning a `Subtask` handle in state `UNAVAILABLE`. Forks are
non-blocking: the owner collects handles first and waits later, which
is what creates the fan-out. Forking after `close()` is rejected with
`IllegalStateException`; forking under changed bindings raises
`StructureViolationException`.

## 3. Subtasks run concurrently

Every subtask executes its callable on its own thread — virtual threads
are the intended carrier. A subtask may itself open a nested scope and
fork grandchildren; that inner scope is owned by the subtask thread and
contained by the inner block, independent of the outer join.

## 4. Owner joins

`scope.join()` parks the owner until every subtask completes or the
policy shuts the scope down early. Under `ShutdownOnFailure` the first
`FAILED` completion triggers `shutdown()`, interrupting siblings; under
`ShutdownOnSuccess` the first `SUCCESS` does. Join defines what the
owner waits for — it is the rendezvous, not the cleanup.

## 5. Policy method reads the outcome

After `join()`, `ShutdownOnFailure` offers `throwIfFailed()`, which
rethrows the first failure (wrapping runtime causes appropriately) or
returns quietly when all succeeded; then each handle's `get()` is safe.
`ShutdownOnSuccess` offers `result()`, returning the first success or
throwing `ExecutionException` when failures arrived with no success.

## 6. Close contains everything

Exiting the `try` block calls `close()`, which waits for and shuts down
any subtask still live — even if `join()` was skipped, timed out, or
threw. This is the containment guarantee: control cannot leave the
block with threads still running. Explicit `join()` first remains the
idiom because it separates waiting intent from cleanup mechanics.

## 7. Bounded variant: joinUntil

`joinUntil(Instant)` joins with a deadline and throws `TimeoutException`
on expiry. The scope stays usable afterwards: `close()` still reaps the
lingering subtasks, and already-completed handles keep their states.
Deadlines bound the wait without breaking containment.

## 8. Cancellation path in detail

`shutdown()` sets the scope shut down and interrupts live subtask
threads. Interruptible blocking calls throw promptly; compute loops must
poll the interrupt flag to stop early. A subtask that ignores interrupts
still cannot escape — `close()` reaps it — but it delays block exit, so
honoring interruption is a correctness habit, not an optimization.
