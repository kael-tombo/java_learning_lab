# Common Mistakes: Volatile Semantics

## 1. volatile++ as a counter
```java
volatile int count; count++; // WRONG: read-modify-write race; increments lost
// RIGHT: AtomicInteger/LongAdder for counters
```

## 2. DCL without volatile
```java
Helper h; // WRONG: reference can publish before construction completes
if (h == null) { synchronized (this) { if (h == null) h = new Helper(); } }
// RIGHT: declare `volatile Helper h;` — or use holder idiom / enum singleton
```

## 3. Volatile array elements
```java
volatile int[] a; a[0] = 1; // WRONG: reference is volatile, elements are plain
// RIGHT: AtomicIntegerArray or VarHandle element access with volatile semantics
```

## 4. Assuming volatile gives mutual exclusion over several fields
Volatile orders single accesses; multi-field invariants torn across two writes need a lock or a single packed CAS. Pair the writes or take the lock.

## 5. 64-bit tearing assumptions
```java
long bits; // WRONG to assume atomicity: JLS 17.7 permits word tearing
// RIGHT: `volatile long` (or AtomicLong) where atomic access matters
```

## 6. Piggybacking on the wrong flag
Publication works only if the payload writes precede the volatile write *in program order* and the reads follow the volatile read. A flag written too early (or read too late) orders nothing.

## 7. Reaching for VarHandle opaque/weak modes by default
Cheaper modes drop edges you probably need. Stay with plain volatile until a profiler or a sequence-barrier algorithm forces you down.

## Review checklist
- Operands named (which thread/monitor/field/atomic)? Edges identified (MATH_FOUNDATION.md)?
- Every acquisition paired with release on all paths (exceptions, interrupts, timeouts)?
- No monitoring signal used as a control signal?
