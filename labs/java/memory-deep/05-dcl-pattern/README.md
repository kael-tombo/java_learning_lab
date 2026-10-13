# Double-Checked Locking Pattern

## What this lab covers

Lazy singleton publication with one `volatile` read on the fast path
instead of a monitor acquisition per call. Three elements, each
load-bearing: the `volatile` field, the outer (unsynchronized) check,
and the locked recheck. Remove any one and the idiom breaks a different
way.

## The idiom (Bloch's shape)

```java
static Helper get() {
    Helper h = instance;                 // (1) one volatile read
    if (h == null) {
        synchronized (VolatileDcl.class) {
            if ((h = instance) == null)  // (2) recheck under lock
                h = instance = new Helper();
        }
    }
    return h;
}
```

The local `h` reads the volatile once per call instead of twice: one
fence, and no check-then-act skew between the two tests.

## What you will run

All snippets need only JDK 9+ (verified on JDK 23). Every stress uses
16 threads x 10k gets and asserts single instance plus `value == 42`:

1. `VolatileDcl` — the real idiom under race: 1 instance, fully
   constructed. The volatile write inside the lock orders construction
   before every later volatile read at check (1).
2. `HolderIdiom` — laziness via JLS 12.4.2 class-init lock:
   `constructions == 1`, no volatile, no synchronized, nothing to get
   wrong. Prefer this unless parameters force DCL.
3. `EnumSingleton` — eager, but reflection-proof (`newInstance` throws)
   and serialization-identical (identity preserved across deserialize).
4. `SyncBaseline` — `synchronized` accessor: obviously correct at one
   monitor pair per call (~20 ns vs ~1 ns volatile read framing).
5. `NoSecondCheck` — dropped recheck double-initializes
   deterministically: `constructions == 2` via the 50 ms wedged window.

## Failure modes by removed element

- No `volatile`: pre-2004 reorder — reference published before field
  stores complete; readers see half-constructed objects (JSR-133 fix).
- No recheck: double initialization — two racers serialize on the
  monitor and both construct; last publication wins, side effects double.
- No outer check: merely locking (correct but pointless — the fast path
  is gone).

## How to use this lab

Read THEORY.md for the three-element argument, CODE_DEEP_DIVE.md for
the five runnable demos, then work EXERCISES.md (keyword removal,
recheck removal, holder/enum comparisons). Reach for the holder first in
real code; reserve DCL for laziness with parameters or scope.
