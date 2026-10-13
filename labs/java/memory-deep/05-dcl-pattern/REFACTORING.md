# Refactoring: DCL Pattern

## 1. Add the missing `volatile` (the 2004 fix)

Before:

```java
static Helper instance;
```

After:

```java
static volatile Helper instance;
```

No other change repairs publication-ahead-of-construction: construction
hb volatile write hb later volatile reads. Any DCL-shaped getter on a
plain field is the pre-2004 bug, regardless of locking.

## 2. Restore the dropped recheck

Before:

```java
if (instance == null) {
    synchronized (X.class) {
        instance = new Helper();
    }
}
```

After:

```java
Helper h = instance;
if (h == null) {
    synchronized (X.class) {
        if ((h = instance) == null)
            h = instance = new Helper();
    }
}
```

The re-read under the monitor sees the first thread's write:
`constructions` goes from 2 back to 1.

## 3. Collapse double reads into Bloch's local

Replace every re-read of the field with the single local `h`: one
acquire per call, and the checked object is the returned object.

## 4. Replace DCL with the holder (lazy, parameterless)

Before: full DCL getter for a no-arg singleton.

After:

```java
static class LazyHolder {
    static final Helper INSTANCE = new Helper();
}
static Helper get() { return LazyHolder.INSTANCE; }
```

JLS 12.4.2 supplies laziness + exactly-once. Delete the volatile, the
lock, and the review burden together.

## 5. Replace with enum (eager + serialization-safe)

Before: DCL singleton that crosses serialization without `readResolve`.

After:

```java
enum Directory { INSTANCE; final int value = 42; ... }
```

Reflection and serialization killers handled by JVM rule. Accept
eagerness explicitly; document it.
