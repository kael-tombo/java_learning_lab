# Debugging: Structured Concurrency Failures

## WrongThreadException on join/close/result

Cause: a non-owner thread drove the scope. Fix: trace who constructed
the scope versus who called the method — the two must be the same
thread. Hand values out of the block; keep the scope handle local to
its creator. Intruder threads in tests reproduce this deterministically.

## IllegalStateException on fork

Cause: `fork()` after `close()`. Fix: check block structure — the fork
site must be lexically inside the `try` whose scope it uses. Loops that
retain a scope across iterations are the usual suspect; move
construction inside the loop or the block around it.

## StructureViolationException on fork

Cause: scoped-value bindings at fork time differ from creation time.
Fix: diff the binding frames — a `ScopedValue.runWhere` (or equivalent
rebinding) wrapped one fork but not the scope. Hoist the binding above
scope construction so creation and all forks share one frame.

## TimeoutException from joinUntil

Not a bug by itself: the deadline passed first. Debug by asking whether
the deadline or the subtasks are wrong — log completion instants per
handle via `state()` after the catch, then let `close()` reap. A scope
that always times out needs a longer deadline or faster subtasks, never
a swallowed exception.

## throwIfFailed wraps the wrong cause

`throwIfFailed()` rethrows the first failure, wrapped per the JDK 23
surface (expect `ExecutionException` carrying the cause). Unwrap with
`getCause()` and match against the subtask whose `state()` reads
`FAILED` — with several failures, only the first is reported, and the
rest are visible only through per-handle `exception()`.

## result() throws with no winner

Under `ShutdownOnSuccess`, `ExecutionException` means every completed
subtask failed; `IllegalStateException` means nothing completed at all.
Distinguish by printing all handle states: all-`FAILED` versus
all-`UNAVAILABLE`-at-join points at different root causes (bad replicas
versus an empty or instantly-shut-down scope).

## Block exit hangs

A subtask ignores interrupts (compute loop, non-interruptible I/O), so
`shutdown()` cannot stop it and `close()` waits. Thread-dump the scope:
the stuck subtask's stack shows the uninterruptible frame. Fix the
subtask to poll the flag or switch to an interruptible call — the scope
is working as designed.

## Sibling not cancelled after failure

Under `ShutdownOnFailure` the failing completion triggers `shutdown()`
automatically — if a sibling keeps running, it is either ignoring
interrupts or the policy is actually `ShutdownOnSuccess` where failures
do not trigger shutdown. Confirm the scope type first; it decides who
gets cancelled and when.

## Nondeterministic test outcomes

Two racing successes under `ShutdownOnSuccess` yield either winner —
asserting a specific one flakes. Make tests deterministic: exactly one
possible success per run, or assert membership ("result is one of")
rather than identity. Scheduler-dependent assertions are test bugs.
