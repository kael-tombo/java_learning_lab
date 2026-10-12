# Exercises: Structured Concurrency (JDK 23 Preview)

All tasks compile with `javac --release 23 --enable-preview` and run
with `java --enable-preview`. Snippets are pinned to the JDK 23 surface
and must be re-verified — never assumed — on later releases, since this
API is still in preview, not final.

## 1. Fan-out pair, all results required

Fork two callables under `ShutdownOnFailure`, `join()`,
`throwIfFailed()`, combine both `get()` values. Predict the printed
combination before running; then make one callable throw and record
which exception `throwIfFailed()` surfaces and what the sibling's
`state()` reads afterwards.

## 2. Fail-fast timing proof

Fork a 5-second sleeper plus a 50 ms failure under
`ShutdownOnFailure`. Time the block: `join()` plus `throwIfFailed()`
must return far sooner than 5 seconds, proving the failure cancelled
the sibling. Print both subtask states to confirm `FAILED` versus
never-completed.

## 3. Hedged replicas, first success wins

Fork one failing fast replica and one slow successful replica under
`ShutdownOnSuccess<String>`. After `join()`, assert `result()` equals
the slow replica's answer. Swap the delays so both succeed at different
times and note that exactly one answer is possible per run only when a
single subtask can succeed — avoid asserting which racer wins.

## 4. Deadline with joinUntil

Fork a 5-second subtask under `ShutdownOnFailure` and call
`joinUntil(Instant.now().plusMillis(200))`. Catch the expected
`TimeoutException`, let `close()` run, and verify the process exits
promptly with no lingering threads. Compare against an unbounded
`join()` version and state when each shape is appropriate.

## 5. Ownership rejection

Create a scope on the main thread, fork one subtask, then start a
second thread that calls `scope.join()`. Record the exception class
(`WrongThreadException`) and confirm the owner can still `join()`
afterwards. Explain in one sentence why handing scope handles to other
threads is always wrong while handing result values is fine.

## 6. Fork-after-close

Open and close a scope with no forks, then call `fork()` on the closed
instance and record the `IllegalStateException`. Then verify the dual:
`close()` without any prior `join()` on a live subtask still cleans up
by timing block exit with a slow child inside.

## 7. State inspection drill

After a mixed join (one success, one failure, one cancelled sibling),
print `state()`, `get()`-or-throws, and `exception()` for every handle.
Match each handle to `SUCCESS` / `FAILED` / `UNAVAILABLE` and write down
which accessor is legal in each state before checking against the run.

## 8. Nested scopes compose

Write a recursive sum over 0..99 that forks left/right halves inside an
inner `ShutdownOnFailure` per level, with the whole computation inside
an outer scope. Assert the total equals 4950. Then inject a failure in
one leaf and trace how inner `throwIfFailed()` converts it into the
outer scope's single failed unit.

## 9. Custom quorum policy

Subclass `StructuredTaskScope` with a `handleComplete` override that
counts successes and calls `shutdown()` once two of three subtasks
succeed. Keep the override thread-safe (completions race), collect
partial values from `SUCCESS` handles after `join()`, and demonstrate
the third subtask's cancellation when the quorum lands early.
