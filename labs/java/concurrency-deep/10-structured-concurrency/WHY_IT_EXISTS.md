# Why It Exists: The Unstructured Mess

## Fire-and-forget leaks

`thread.start()` and `executor.submit()` return immediately while the
work continues invisibly. The spawner moves on, the child outlives its
purpose, and shutdown order becomes archaeology. Every long-lived server
accumulates these strays until someone audits thread dumps at 2 a.m.

## Silent failures

An executor subtask that throws stores its exception in a `Future` nobody
may ever read. The parent reports success, the failed branch rots, and
the user sees half a page rendered with no error logged. Failure needs a
default route to the join point, not an opt-in `get()` call.

## Manual cancellation trees

Cancelling a fan-out by hand means tracking every `Future`, calling
`cancel(true)` on each, handling the ones already done, and racing the
late failures — latch plus atomics plus careful ordering. Most code
either skips cancellation (leak) or half-does it (interrupt storms,
missed branches). The policy should be three lines, not a framework.

## Split-brain error handling

`CompletableFuture` chains scatter error logic across `exceptionally`,
`handle`, and `whenComplete` stages owned by nobody in particular. Each
stage can fail, time out (`orTimeout` mutates the same stage in place —
it returns `this`, unlike the deriving combinators), or be abandoned,
and the question "who cancels the leftovers?" has no single answer.

## invokeAll is not structure

`ExecutorService.invokeAll` bounds one call's lifetime but composes
poorly: nesting it across methods rebuilds the same tracking each
level, and scoped values do not propagate lexically through raw pool
submissions. It solves the single-call case while leaving the
multi-level case manual.

## The design answer

Make the block the owner: subtasks cannot outlive their scope, the
first decisive completion shuts down the rest, and only the creating
thread drives the lifecycle. Structure becomes the default and
unstructured escape requires deliberate effort — the exact inversion of
the `start()`/`submit()` era.

## Why now: virtual threads

Thread-per-subtask was prohibitively expensive with platform threads,
which is why pools and sharing dominated. Virtual threads removed that
cost barrier, so the API can finally spend one thread per subtask and
buy back legibility, containment, and composable nesting at scale.
