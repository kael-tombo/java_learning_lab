# Refactoring: Thread Lifecycle

## 1. State polling -> latch
```java
// BEFORE: wasteful + racy
while (t.getState() != Thread.State.TERMINATED) Thread.sleep(10);
// AFTER: exact handoff, no polling
t.join(); // or doneLatch.await();
```

## 2. Interrupt-swallowing worker -> cancellable worker
```java
// BEFORE
try { queue.take(); } catch (InterruptedException e) { /* swallowed */ }
// AFTER
try { queue.take(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); return; }
```

## 3. Restart-by-start -> fresh task submission
```java
// BEFORE: t.start(); ... t.start(); // throws
// AFTER: executor.submit(task) per run; threads are single-use, tasks are reusable
```

## 4. synchronized-entry on hot virtual path -> ReentrantLock
```java
// BEFORE: virtual threads pin carriers in synchronized (through JDK 23)
// AFTER: Lock-based section parks (WAITING) and unmounts the carrier
lock.lock(); try { ... } finally { lock.unlock(); }
```

## Refactoring discipline
- Name the violated invariant from THEORY.md before touching code.
- Re-run EXERCISES.md probes after each change; contention bugs hide behind single-run luck.
