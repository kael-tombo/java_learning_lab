# Refactoring: Atomic Classes

## 1. Side-effecting lambda -> pure + post-commit
```java
// BEFORE: effect repeats per retry
ref.getAndUpdate(x -> { publish(x); return x + 1; });
// AFTER
int committed = ref.getAndUpdate(x -> x + 1) + 1; publish(committed);
```

## 2. Weak one-shot -> strong one-shot, weak in loops
```java
// BEFORE
if (a.weakCompareAndSet(e, n)) ...
// AFTER
if (a.compareAndSet(e, n)) ...            // one-shot verdict
// loops keep weak: while (!a.weakCompareAndSet(p, n)) p = a.get();
```

## 3. Hot AtomicLong -> LongAdder above ~2-4 writers
```java
// BEFORE
AtomicLong hits; hits.incrementAndGet(); // single-word retry storm
// AFTER
LongAdder hits; hits.increment(); // exact reads only where needed
```

## 4. Two-atomic commit -> single packed CAS or lock
```java
// BEFORE: a.set(x); b.set(y); // observable midway state
// AFTER
synchronized (guard) { aVal = x; bVal = y; } // or pack into one AtomicLong
```

## Refactoring discipline
- Name the violated invariant from THEORY.md before touching code.
- Re-run EXERCISES.md probes after each change; contention bugs hide behind single-run luck.
