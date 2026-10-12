# Common Mistakes: Synchronized Internals

## 1. Synchronizing on different objects, sharing fields
```java
// WRONG: two locks, one field — no mutual exclusion, no shared edge
synchronized (lockA) { shared++; }  ...  synchronized (lockB) { shared++; }
// RIGHT: one guard per invariant; document which object guards which fields
synchronized (guard) { shared++; }
```

## 2. Static vs instance confusion
```java
static synchronized void s() {}  // locks Clazz.class
synchronized void i() {}         // locks this — DISJOINT from above
// RIGHT: pick the monitor deliberately; static state needs the Class (or a named static guard)
```

## 3. wait() in if instead of while
```java
synchronized (o) { if (!ready) o.wait(); }          // WRONG: spurious/stolen wakeups proceed
synchronized (o) { while (!ready) o.wait(); }       // RIGHT: re-check after every return
```

## 4. notify() with multiple conditions on one monitor
One arbitrary waiter wakes; others sleep with met conditions. Prefer `notifyAll()` unless you prove exactly one waiter on exactly one condition can proceed.

## 5. Calling wait/notify without holding the monitor
`o.wait()` outside `synchronized (o)` throws `IllegalMonitorStateException` at runtime — the check is dynamic. Audit every call site for ownership.

## 6. Locking on interned/boxed/shared keys (string literals, Integer caches)
Unrelated code shares the same monitor -> mystery contention and exclusion. Lock on private final guard objects.

## 7. Alien calls inside synchronized (overridable methods, callbacks, listeners)
Reentrancy cannot save you from callbacks that re-enter your invariants inconsistently. Move alien calls outside the block or take a snapshot first.

## Review checklist
- Operands named (which thread/monitor/field/atomic)? Edges identified (MATH_FOUNDATION.md)?
- Every acquisition paired with release on all paths (exceptions, interrupts, timeouts)?
- No monitoring signal used as a control signal?
