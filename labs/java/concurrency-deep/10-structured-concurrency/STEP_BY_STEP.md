# Step by Step: First Scope to Nested Tree

## Step 1: Set up the JDK 23 preview build

Confirm `javac --version` reports 23, then compile every file here with
`javac --release 23 --enable-preview` and run with `java
--enable-preview`. A "cannot find symbol: StructuredTaskScope" error at
this stage always means the flags are missing, not the import.

## Step 2: Fork two calls, join, combine

Write a `main` that opens `ShutdownOnFailure` in `try`-with-resources,
forks a user fetch and an orders fetch, calls `join()` and
`throwIfFailed()`, and prints both `get()` values combined. Run it and
confirm the output reads like the sequential version of the same code.

## Step 3: Break one branch on purpose

Make the orders fetch throw `IllegalStateException`. Re-run: observe
`throwIfFailed()` surfacing that cause, the user handle no longer
`SUCCESS`, and block exit still prompt. This is fail-fast working.

## Step 4: Race two replicas for one answer

Rewrite the block as `ShutdownOnSuccess<String>`: fork a fast-failing
replica and a slow successful one, `join()`, print `result()`. Confirm
the slow answer wins and the failure never surfaces — the mirror image
of step 3's semantics.

## Step 5: Add a deadline

Wrap a 5-second sleeper in `ShutdownOnFailure` and replace `join()`
with `joinUntil(Instant.now().plusMillis(200))`. Catch
`TimeoutException`, print a one-line diagnosis, and confirm `close()`
reaps the sleeper with no hang. Decide which of your earlier blocks
deserve deadlines.

## Step 6: Prove ownership to yourself

From a second thread, call `join()` on a scope your main thread owns
and record the `WrongThreadException`. Then delete the intruder and
confirm the owner-only flow. Internalize: share values, never scopes.

## Step 7: Inspect every handle state

Build a three-subtask scope (success, failure, slow-cancelled) and
after `join()` print `state()`, `get()`-or-throws, and `exception()`
per handle. Match each line to `SUCCESS` / `FAILED` / `UNAVAILABLE`
before moving on — state literacy pays off in every later step.

## Step 8: Nest scopes recursively

Implement the 0..99 split-sum: each level opens an inner
`ShutdownOnFailure`, forks halves, joins, `throwIfFailed()`, adds the
halves; the whole run sits in an outer scope. Assert 4950, then inject
a leaf failure and watch it fold level by level into one outer failure.

## Step 9: Write one custom policy

Subclass the scope with a `handleComplete` override that shuts down
after two of three successes. Demonstrate the early shutdown, print the
cancelled third handle's state, and keep the override synchronized —
then compare its shape against the two built-ins you now know by heart.
