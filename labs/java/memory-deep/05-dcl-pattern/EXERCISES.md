# Exercises: DCL Pattern

All snippets run on JDK 9+ with no dependencies. Stress shape
throughout: 16 threads x 10k gets, `CountDownLatch` start gate, assert
single instance plus `value == 42`. Keep `println` output pure ASCII.

## 1. Volatile DCL under race (baseline)

Run `VolatileDcl` as given. Expect:

```
distinct instances: 1
single instance: true
fully constructed (value==42): true
```

Vary thread count (4, 16, 32) and confirm the assertions hold at each
level. The guarantee is structural (volatile + monitor edges), never
timing luck.

## 2. Delete `volatile` (reasoning exercise)

Remove `volatile` from the field and re-run several times. Note that it
will likely still print 1 instance here — the reorder needs adversarial
timing you cannot summon on demand. Write the paragraph the run cannot:
which edge disappeared (volatile write hb later volatile read), and why
the green output is evidence of nothing. Restore the keyword.

## 3. Drop the recheck (deterministic break)

Run `NoSecondCheck` as given (50 ms constructor sleep, two threads
behind one gate). Expect:

```
constructions = 2
double initialization without recheck: true
surviving instance constructed: true
```

Then restore the locked recheck and show `constructions == 1`. State
which edge the recheck uses (monitor: first thread's write visible to
the second thread's locked re-read).

## 4. Bloch local-variable shape

Rewrite the getter to read `instance` twice (once per check, no local)
and confirm identical assertions — then explain what the local buys:
one fence instead of two, and no check-then-act skew if the field were
ever reassigned. Keep the local shape in all later exercises.

## 5. Holder comparison

Run `HolderIdiom` and confirm `constructions == 1` with no volatile and
no synchronized in user code. Then answer: which lock did the work (JLS
12.4.2 class-initialization lock, first active use of `LazyHolder`)?
Name one scenario where you would still need DCL (parameterized
construction).

## 6. Enum comparison

Run `EnumSingleton`: confirm 1 instance, `lookup works: true`, and
`deserialization returns same instance: true`. Then serialize a DCL
singleton without `readResolve` and show identity forking — the second
classic singleton killer the enum gets for free (first: reflection,
where `Constructor.newInstance` on enums throws).

## 7. Synchronized baseline framing

Run `SyncBaseline` and confirm identical assertions. Time both getters
roughly (framework: ~1 ns volatile read vs ~20 ns uncontended monitor —
no asserted crossover). Write the shipping rule: below millions of
calls/second/thread, take the obviously correct accessor.
