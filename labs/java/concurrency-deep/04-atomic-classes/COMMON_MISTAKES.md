# Common Mistakes: Atomic Classes

## 1. Side-effecting update functions
```java
// WRONG: runs ~3x under contention in this lab's measurements
atomic.getAndUpdate(x -> { log(x); return x + 1; }); // log fires repeatedly
// RIGHT: pure function inside; effects after the CAS commits
int v = atomic.getAndUpdate(x -> x + 1); log(v + 1);
```

## 2. One-shot weakCompareAndSet
```java
if (atomic.weakCompareAndSet(e, x)) { ... } // WRONG: spurious failure misread as contention
// RIGHT: weak CAS only in `while` retry loops; one-shot tests use compareAndSet
```

## 3. Two atomics as a transaction
```java
a.set(1); b.set(2); // WRONG: observers see (1, old) midway
// RIGHT: guard multi-variable invariants with a lock, or pack both into one AtomicLong CAS
```

## 4. Ignoring the witness
```java
do { p = atomic.get(); } while (!atomic.compareAndSet(p, f(p))); // fine but re-reads
// BETTER: int w = atomic.compareAndExchange(p, f(p)); retry from w on failure
```

## 5. Bare CAS where ABA matters
Treiber-stack pops with node reuse: A->B->A fools `compareAndSet`. Use fresh allocation, `AtomicStampedReference`, or `AtomicMarkableReference` where identity history matters.

## 6. AtomicLong as a contended counter
One CAS word under many writers collapses into retry burn. Above ~2-4 writers prefer `LongAdder`; reserve `sum()` for metrics (it is fuzzy, not atomic).

## 7. sum() as an exact total
`adder.sum()` concurrent with increments may miss or double-count. Never drive money, quotas, or loop bounds from it; use `sumThenReset()` only at quiescent points.

## Review checklist
- Operands named (which thread/monitor/field/atomic)? Edges identified (MATH_FOUNDATION.md)?
- Every acquisition paired with release on all paths (exceptions, interrupts, timeouts)?
- No monitoring signal used as a control signal?
