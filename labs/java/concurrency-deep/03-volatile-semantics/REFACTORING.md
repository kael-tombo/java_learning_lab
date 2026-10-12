# Refactoring: Volatile Semantics

## 1. Volatile counter -> adder
```java
// BEFORE: loses updates
volatile long hits; hits++;
// AFTER
LongAdder hits = new LongAdder(); hits.increment(); // sum() for metrics
```

## 2. Broken DCL -> volatile DCL or holder
```java
// BEFORE
Helper h; ... if (h == null) { synchronized (this) { if (h == null) h = new Helper(); } }
// AFTER
volatile Helper h; // same shape, now correct — or holder idiom / enum singleton
```

## 3. Volatile array -> atomic array
```java
// BEFORE
volatile int[] cells; cells[i] = v; // plain element store
// AFTER
AtomicIntegerArray cells; cells.set(i, v); // volatile semantics per element
```

## 4. Scattered flags -> single publication point
```java
// BEFORE: payload and flag written in an order no edge protects
// AFTER: all payload writes, then ONE volatile write; readers test that write first
data = 42; meta = m; ready = true; // ready volatile, written last
```

## Refactoring discipline
- Name the violated invariant from THEORY.md before touching code.
- Re-run EXERCISES.md probes after each change; contention bugs hide behind single-run luck.
