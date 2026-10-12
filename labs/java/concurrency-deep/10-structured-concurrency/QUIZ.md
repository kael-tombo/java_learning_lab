# Quiz: Structured Concurrency

## Q1: Which flags build the JDK 23 preview snippets?
A: `javac --release 23 --enable-preview` to compile, `java
--enable-preview` to run. Without them the preview types are invisible
and the error mimics a missing import.

## Q2: A scope forks two backends and needs both answers. Which policy
and which calls?
A: `ShutdownOnFailure`: `fork` both, `join()`, `throwIfFailed()`, then
`get()` each handle. First failure cancels the sibling automatically.

## Q3: Three replicas race; any single answer suffices. Which policy
and which call reads the winner?
A: `ShutdownOnSuccess<T>`: `fork` all three, `join()`, then `result()`.
The first `SUCCESS` triggers shutdown of the losers.

## Q4: A helper thread calls scope.join() and gets an exception. Name
it and state the rule.
A: `WrongThreadException`. Only the creating (owner) thread may
`join()`, `close()`, or `result()`; subtask threads may only own nested
scopes, never drive the outer one.

## Q5: Code forks a subtask after the try block closed. What happens?
A: `fork()` throws `IllegalStateException` immediately and starts no
thread. Closed means closed — create a new scope for new work.

## Q6: Forks happen after scoped values were rebound. What happens?
A: `StructureViolationException`. Fork-time bindings must match the
bindings captured at scope creation; subtasks inherit lexically.

## Q7: After join(), handle X is SUCCESS, Y is FAILED, Z never finished.
Give each state and one legal accessor.
A: X is `SUCCESS` — `get()` returns the value. Y is `FAILED` —
`exception()` returns the cause, `get()` throws. Z is `UNAVAILABLE` —
only `state()` is meaningful; `get()` throws.

## Q8: joinUntil(Instant.now().plusMillis(200)) expires with a slow child
running. What is thrown, and does anything leak?
A: `TimeoutException` to the owner; nothing leaks because `close()` on
block exit still waits for and shuts down the slow child.

## Q9: Why did a compute-loop subtask delay block exit after shutdown()?
A: It ignored thread interrupts, so shutdown's interruption had no
effect until `close()` reaped it. Loops must poll the interrupt flag;
blocking calls already throw on interrupt.

## Q10: When is thread-per-subtask with platform threads a mistake?
A: Large fan-outs: each platform thread costs roughly a megabyte of
stack, so hundreds of subtasks waste memory. Virtual threads are the
intended carrier; nesting depth scales with them, not with platform
threads.
