# Reflection: Structured Concurrency

## Containment

Where in your current codebase could a child task outlive its spawner
today? Name one `start()` or `submit()` site and describe what
`close()`-guaranteed containment would change about its shutdown audit.

## Policy choice

Take a fan-out you own: is it conjunctive (every result needed) or
disjunctive (one answer suffices)? Which scope policy fits, and what
does the current hand-rolled equivalent do with the losing branches?

## Failure routing

When one branch of your fan-out fails, where does the exception go
right now — and who cancels the siblings? Compare that path, step by
step, with `join()` plus `throwIfFailed()` under `ShutdownOnFailure`.

## Ownership discipline

Do any of your helpers accept executors, futures, or latches they did
not create? What would break if those handles followed the scope rule
— creator drives, everyone else reads values — enforced by exception?

## Deadline posture

Which of your concurrent calls has an unbounded wait with no deadline?
What budget would you set for `joinUntil`, and what should the catch
block do with partial handle states when it fires?

## Interruption honesty

Do your subtasks honor thread interrupts, or would `shutdown()` leave
them running until reaped? Pick one compute loop and sketch the flag
poll that would make it cancellable.

## Nesting opportunities

Where do you repeat fan-out bookkeeping at multiple levels (service
calling services calling backends)? Sketch those levels as nested
scopes and state what each level's `throwIfFailed()` would mean.

## Carrier awareness

Are your fan-outs sized for platform or virtual threads? Estimate one
fan-out's thread count times per-thread stack cost and judge whether
the current carrier is defensible.

## Preview pragmatics

This API is preview (JDK 23 pin here, JEP 505 reshaping later). What is
your migration plan when the spelling moves — and which of the five
stable invariants would survive that move untouched in your code?

## Custom policy design

What quorum, threshold, or partial-result rule would serve your domain
better than all-or-first? Draft its `handleComplete` predicate in
words: what it counts, when it calls `shutdown()`, and what the owner
reads afterwards.
