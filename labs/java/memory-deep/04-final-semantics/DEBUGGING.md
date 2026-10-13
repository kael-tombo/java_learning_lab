# Debugging: Final Field Semantics

## Symptom: a reader sees 0 or null in a final field

A `final int` observed as 0 (or a `final` reference as null) after
construction almost always means one of two things: the reference was
obtained through a pre-freeze window (`this` escape), or the write came
from outside the constructor path (reflection, `Unsafe`, deserialization
fill). Check constructor publication order first.

## Step 1: audit the constructor for publication

Search the constructor (and anything it calls) for:

- Assignments to statics (`published = this`, registry installs).
- `this` passed to other objects (listeners, callbacks, executors).
- `thread.start()` or executor submissions.
- Calls to overridable methods.

Any of these before the final stores is the prime suspect. Move all of
them after the stores, or out of the constructor entirely.

## Step 2: reproduce with a wedged window

Make the suspect deterministic instead of timing-dependent: insert a
sleep between the suspected escape and the final store (as the lab's
`ThisEscape` does with 300 ms), publish a reader that spins on the
reference, and read the final inside the window. If the reader sees the
default value, the escape is confirmed, not hypothesized.

## Step 3: distinguish escape from reflective writes

If no constructor escape exists, look for post-construction writes:

- `Field.set(...)` on final fields via `setAccessible(true)`.
- `Unsafe.putXxx` / VarHandle writes to final storage.
- Deserialization or cloning paths that fill fields without running the
  constructor.

These produce stale-or-torn observations that no constructor fix cures;
the fix is to stop writing finals after construction.

## Step 4: distinguish guarantee from hardware luck

A passing stress run of a *mutable* twin proves nothing on x86: TSO
hides missing ordering. To tell theorem from weather, compare against
the final version under the identical harness. If the final version is
exact for 3000 rounds *by rule* (JLS 17.5) and the mutable version is
exact only *by observation*, the mutable one still ships as a data race.

## Step 5: check transitivity, not just the field

When a final reference looks right but its contents look stale (array
element wrong, list entry stale), the contents were likely mutated after
publication or aliased from a caller-owned structure. Copy mutable
inputs into freshly allocated final storage inside the constructor.

## Logging tips

Log the observed value plus construction state: print the final read,
whether the reader obtained the reference before constructor end, and
the publication path. `println` output must stay pure ASCII so the
harness console decodes it; keep any non-ASCII notation in prose only.
