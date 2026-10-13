# Common Mistakes: DCL Pattern

## 1. Dropping `volatile`

```java
static Helper instance;  // BROKEN: pre-2004 reorder returns
```

`new Helper()` is allocate, init fields, store reference — and without
`volatile` the store may publish before the field stores complete. A
racer passing check (1) reads non-null but half-constructed state. The
keyword is not extra safety; it is the entire correctness argument
(JSR-133 fix, Java 5). Delete it and the 2004 bug is back.

## 2. Dropping the locked recheck

```java
if (instance == null) {
    synchronized (X.class) {
        instance = new Helper();  // BROKEN: both racers init
    }
}
```

Two threads that both read null at check (1) serialize on the monitor
and each initialize: `constructions == 2` deterministically (this lab's
50 ms window proves it). Constructor side effects run twice; the first
instance is silently discarded. The recheck re-reads under the lock,
where the first thread's write is visible via the monitor edge.

## 3. Reading the volatile twice

```java
if (instance == null) {
    synchronized (X.class) {
        if (instance == null) ...  // second volatile read: extra fence
```

Beyond the wasted fence: between two reads the field could change, and
the method could return a different object than it checked. Use Bloch's
shape — `Helper h = instance` once, then test and return `h`.

## 4. Reaching for DCL first

DCL is subtle; the holder is not. `static class LazyHolder { static
final Helper INSTANCE = new Helper(); }` gives lazy exactly-once init
under JLS 12.4.2 with nothing to get wrong. Reserve DCL for parameters,
non-static scope, or framework constraints — and document why the holder
did not fit.

## 5. Serializing a DCL/holder singleton

Default deserialization creates a second instance: identity breaks
across the wire. Add `readResolve` returning the canonical instance, or
use an enum (identity guaranteed by the JVM, reflection-proof too).

## 6. Assuming the reorder is observable on demand

The half-constructed read needs adversarial timing and will not appear
in a casual test — which is why deletion-of-`volatile` demos assert the
guarantee (all snippets here assert `value == 42` / single instance)
rather than chase the stale read. Absence of observed breakage is not
evidence of correctness.

## 7. Synchronizing on the wrong monitor or a mutable lock

DCL's recheck is visible only if every path uses the same monitor for
the same field. Locking on `this` in one path and the class in another
(or on a reassignable lock object) silently forks the idiom into two
independent, each-broken halves.
