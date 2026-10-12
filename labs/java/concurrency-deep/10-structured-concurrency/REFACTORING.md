# Refactoring: Toward Scopes

## From manual threads to ShutdownOnFailure

Before: `start()` two threads, `join()` both, hand-rolled first-error
slot, forgotten interrupt on failure paths. After: fork both in a
`ShutdownOnFailure` scope, `join()`, `throwIfFailed()`, read both
`get()` values. Delete the error slot, the cancel loop, and the stray
daemon audit — containment replaces all three.

## From ExecutorService.invokeAll to scopes

`invokeAll` bounds one call but leaves nesting and scoped-value flow
manual. When the same fan-out appears at multiple levels, lift each
level into its own scope: inner scopes own their children, inner
`throwIfFailed()` folds child failure into one unit, and the outer
scope sees clean per-branch outcomes instead of future lists.

## From CompletableFuture chains to scopes

Chains ending in `allOf(...).join()` with `exceptionally` handlers map
to `ShutdownOnFailure` directly: each stage becomes a forked callable,
the exceptionally logic becomes either `throwIfFailed()` propagation or
explicit per-handle `exception()` inspection. Timeout stages using
`orTimeout` (in-place, returns `this`) become `joinUntil(Instant)` on
the scope — one deadline for the whole fan-out instead of per-stage
timers.

## From anyOf races to ShutdownOnSuccess

`CompletableFuture.anyOf` plus manual cancellation of losers maps to
`ShutdownOnSuccess`: fork each alternative, `join()`, `result()`. The
loser-cancel loop disappears — first success triggers `shutdown()`
inside the policy. Keep the alternatives' failure semantics in mind:
unlike `anyOf`, scope failures never surface when a success exists.

## Introducing a custom quorum

When "all" is too strict and "any" too loose (2-of-3 backends agree),
subclass the scope and override `handleComplete` to count successes and
`shutdown()` at quorum. Refactor incrementally: start from a working
`ShutdownOnFailure` scope, move the completion counting into the hook,
and keep the fork/join/close skeleton untouched.

## Splitting an oversized scope

A scope forking unrelated work groups (billing plus search plus mail)
splits into nested scopes per group inside one outer scope. Each inner
scope gets the policy fitting its group; the outer scope (usually
`ShutdownOnFailure`) folds group outcomes. Failure attribution improves
because each group's `throwIfFailed()` names its own culprit.

## Moving deadlines outward

Per-subtask timeouts scattered across callables consolidate into one
`joinUntil` deadline at the scope. The refactor removes timer code from
every leaf, makes the budget visible at the block header, and keeps
cleanup uniform — `close()` reaps whatever the deadline cut off.

## Carrier migration: platform to virtual

Scopes written with platform-thread subtasks migrate by changing the
thread factory to virtual threads, then raising fan-out to match the
new budget. Re-measure block latency and thread count after the switch;
the same scope shape that was wasteful at 200 platform threads is
routine at 200 virtual ones. No policy or join logic changes.
