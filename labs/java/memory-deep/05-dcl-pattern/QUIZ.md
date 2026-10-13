# Quiz: DCL Pattern

## Q1: Write the three elements of correct DCL. What breaks if each is
## removed?
**A:** `volatile` field + outer check + locked recheck. No `volatile`:
half-constructed publication (pre-2004 reorder). No recheck: double
initialization (`constructions == 2`, deterministic). No outer check:
merely a locked accessor — correct but pointless.

## Q2: Two threads race through recheck-less DCL with a 50 ms
## constructor sleep. What is `constructions`, and why deterministic?
**A:** 2. The sleep wedges the window so both threads provably read
null at check (1) before either publishes, then each serializes through
the monitor and initializes. Side effects double; last write wins.

## Q3: Why does the lab use `Helper h = instance` instead of reading
## the field twice?
**A:** Bloch's shape: one volatile read (one fence) instead of two, and
the checked object is provably the returned object — no check-then-act
skew between two distinct reads.

## Q4: The holder version prints `constructions == 1` with no volatile
## and no synchronized in user code. Which lock did the work?
**A:** The JVM's class-initialization lock (JLS 12.4.2): `LazyHolder`
initializes exactly once, lazily on first active use, under the JVM's
own recursive lock.

## Q5: The enum version survives serialization round-trip with identity
## intact. Why? What must DCL/holder singletons add for the same?
**A:** The JVM guarantees enum deserialization identity (plus
reflection immunity: `newInstance` on enums throws). DCL and holder
singletons need an explicit `readResolve` returning the canonical
instance.

## Q6: Deleting `volatile` still prints 1 instance in casual runs. Verdict?
**A:** Still broken. The reorder needs adversarial timing; green runs
are luck. The finding is the missing write/read edge (JSR-133 argument),
not an observation — restore the keyword.

## Q7: When should the synchronized accessor ship instead of DCL?
**A:** Below high call rates: identical assertions (single instance,
`value == 42`) at ~20 ns/call vs ~1 ns, with obvious correctness. DCL's
subtlety must earn its keep; no lab benchmark fixes the crossover.
