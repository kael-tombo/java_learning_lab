# Final Field Semantics

## What this lab covers

JLS 17.5 initialization safety: an object built without leaking `this`
publishes its `final` fields safely through ANY path, including a data
race. No `volatile`, no lock, no fence on the read path.

## The freeze rule in one paragraph

For a final write `w`, the freeze `f` at constructor end, a publication
action `a`, a reference read `r1`, and a final read `r2`:

```
w ->hb f ->hb a ->mc r1 ->dc r2  ==>  r2 observes w
```

The memory chain (`mc`) and dereference chain (`dc`) carry the ordering
through the reference itself. That is the whole guarantee: the reference
may race, the finals may not appear stale.

## What you will run

All snippets need only JDK 9+ (verified on JDK 23), no dependencies:

1. `FinalViaRace` — plain racy static, 3000 rounds, `a`/`s`/`arr[0..1]`
   exact every round, including the transitive array contents.
2. `RecordViaRace` — record components are finals; same 3000-round exact
   result. Caveat: a record holding a mutable `ArrayList` publishes the
   reference safely and leaves the contents racy (`List.of` is safe
   because it is itself immutable).
3. `ThisEscape` — `published = this` before the store plus a 300 ms
   construction window: the early read deterministically sees default 0.
4. `MutableControl` — identical shape minus `final`: passes 3000 rounds
   on x86 by accident (TSO + coherence), guaranteed nowhere.
5. `StringSharing` — `String` (`final byte[] value` + `final byte coder`)
   shared unsynchronized for 3000 rounds, always intact, contents included.

## Key boundaries

- Finals cover initialization only, not later mutation. A `final`
  reference to a mutable object publishes the pointer, not the contents.
- `this` escape before the stores voids the freeze for early readers.
- Reflective and `Unsafe` post-construction writes to finals sit outside
  the memory model; behavior is unspecified and version-dependent.

## How to use this lab

Read THEORY.md for the precise rule, CODE_DEEP_DIVE.md for the five
runnable demos, then work EXERCISES.md (freeze races, escape windows,
record and String variants). Use QUIZ.md and FLASHCARDS.md to check
understanding, and COMMON_MISTAKES.md before writing constructors that
publish.
