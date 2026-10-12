# Reflection: CompletableFuture

## Check your model

1. Without looking: where do `thenApply`, `thenApplyAsync(f)`, and
   `thenApplyAsync(f, exec)` each run? What changes when the future is already
   complete?
2. A teammate writes `thenApply(x -> fetchAsync(x))`. What type results, what
   breaks downstream, and what is the one-word fix?
3. `allOf(a, b, c)` completes. Where are the values, and why is `join()` safe
   there?
4. Why does `cancel(true)` not stop a running `supplyAsync` body? What would
   you need instead for true interruption?
5. `f.orTimeout(2, SECONDS)` — is the result the same object? Does the
   upstream stop on expiry? What must you cancel by hand?

## Connect to your code

1. Find one blocking `Future.get()` chain. Rewrite it as `thenCompose`/
   `thenCombine` and name the executor each stage runs on.
2. Find one `supplyAsync` without an explicit executor. Is its body blocking?
   If yes, which pool must it move to and how large?
3. Find one `anyOf` or hedged call. Are losers cancelled? If not, add it.

## Predict, then verify

1. Predict the thread name printed by `completedFuture("x").thenApply(...)`
   vs `.thenApplyAsync(...)`. Run the EXERCISES.md probe and compare.
2. Predict `f.orTimeout(...) == f`. Assert identity in a test.
3. Predict `join()` vs `get()` exception types on one failing future. Catch
   both and record the actual classes.

## One-paragraph write-up

Explain the CF thread rule to a junior using completing-thread, common pool,
and named executor — with one example each of a stage that belongs in each
place. No generic filler ("powerful," "seamless"): method names and thread
names only.
