# Refactoring: Synchronized Internals

## 1. Split guards per invariant
```java
// BEFORE: one lock, unrelated fields contend
synchronized (big) { a++; }  ...  synchronized (big) { b++; }
// AFTER: independent guards
synchronized (guardA) { a++; }  ...  synchronized (guardB) { b++; }
```

## 2. if-wait -> while-wait + notifyAll
```java
// BEFORE
synchronized (o) { if (!ready) o.wait(); o.notify(); }
// AFTER
synchronized (o) { while (!ready) o.wait(); ready = false; o.notifyAll(); }
```

## 3. Public-lock exposure -> private guard
```java
// BEFORE: clients can hold your monitor
public synchronized void m() {}
// AFTER
private final Object guard = new Object();
public void m() { synchronized (guard) { ... } }
```

## 4. Alien call inside -> snapshot outside
```java
// BEFORE
synchronized (guard) { listener.onChange(state); }
// AFTER
Snapshot s; synchronized (guard) { s = state.copy(); } listener.onChange(s);
```

## Refactoring discipline
- Name the violated invariant from THEORY.md before touching code.
- Re-run EXERCISES.md probes after each change; contention bugs hide behind single-run luck.
