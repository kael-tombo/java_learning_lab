# Debugging: DCL Pattern

## Symptom: two instances where one was promised

Collect identities across threads (`ConcurrentHashMap.newKeySet`,
16 threads x 10k gets as in this lab). `seen.size() == 2` with a DCL
getter means exactly one thing: the locked recheck is missing or reads
a different field/monitor than the write path. Confirm with a
construction counter (`AtomicInteger constructions`): recheck-less DCL
shows `constructions == 2` deterministically once the race window is
wedged (50 ms constructor sleep).

## Symptom: partially constructed object (`value != 42`)

A reader obtaining a non-null instance whose `final int value` is 0 (or
whose fields are default) points at a missing or mismatched `volatile`:
the publication edge that should order construction before the check-(1)
read is absent. Verify the field declaration first — `static Helper`
without `volatile` reproduces the pre-2004 bug regardless of how correct
the locking looks.

## Step 1: check the three elements mechanically

For the getter under suspicion, confirm literally:

1. Field declared `static volatile Helper instance`.
2. First check outside any lock, reading a local (`Helper h =
   instance; if (h == null)`).
3. Second check inside `synchronized` on the canonical monitor,
   re-reading into the same local (`if ((h = instance) == null)`).

Any deviation is the diagnosis; DCL has no harmless variations.

## Step 2: confirm the monitor is canonical

All writers and the recheck must synchronize on the same object (here
`VolatileDcl.class`). Mixed monitors (`this` vs class, or an instance
field lock) break the monitor edge that makes the first thread's write
visible to the recheck. Grep every `synchronized` touching the field.

## Step 3: wedge the window, don't chase timing

Race hypotheses need deterministic windows: a `CountDownLatch` start
gate for all racers plus a constructor sleep (50 ms, as in
`NoSecondCheck`) so both threads provably pass check (1) on null before
either publishes. If `constructions == 2` appears only with the sleep,
the recheck is still missing — the sleep proved it, timing didn't hide it.

## Step 4: separate DCL bugs from serialization forks

If singletons duplicate across serialization (not across threads), the
DCL itself may be fine: default deserialization builds a second
instance. Round-trip through `ObjectOutputStream`/`ObjectInputStream`
and compare identity; add `readResolve` or switch to enum if it forks.

## Logging tips

Print `distinct instances`, the construction count, and `value == 42`
on the shared instance — the same three lines every snippet in this lab
emits. Keep `println` output pure ASCII for harness decoding.
