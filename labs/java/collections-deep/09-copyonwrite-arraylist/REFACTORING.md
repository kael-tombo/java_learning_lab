# Refactoring: Toward Copy-on-Write

## Replace lock-held notification with snapshot iteration

Before — CME/deadlock-prone:

```java
List<Listener> ls = Collections.synchronizedList(new ArrayList<>());
synchronized (ls) { for (Listener l : ls) l.onEvent(e); } // reentrant CME risk
```

After — lock-free notify, safe reentrancy:

```java
var ls = new CopyOnWriteArrayList<Listener>();
for (Listener l : ls) l.onEvent(e);   // snapshot; unregister mid-loop is safe
```

## Replace check-then-act with addIfAbsent

Before — duplicate-adding race:

```java
if (!list.contains(x)) list.add(x);
```

After — atomic incl. locked recheck:

```java
list.addIfAbsent(x);
```

## Replace per-notify clone with COW iteration

Before — O(n) copy per *read*:

```java
for (Listener l : new ArrayList<>(ls)) l.onEvent(e);
```

After — copy only per *write* (rare); reads walk the live array:

```java
for (Listener l : cowList) l.onEvent(e);
```

## Replace COW growth buffer with a queue

Before — per-request COW append (O(n) each, GC churn). After —
`ConcurrentLinkedQueue` + periodic batch drain into a plain list.
Writes become O(1) CAS appends; snapshots taken at drain points.
