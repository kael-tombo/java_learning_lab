# Refactoring: Toward Lock-Free Handoff

## Replace synchronized queue with CLQ (non-blocking path)

Before — one monitor for producers + consumers:

```java
Queue<Task> q = Collections.synchronizedList(new LinkedList<>()) ...;
synchronized (q) { q.offer(t); }      // blocks consumers
```

After — no mutual exclusion:

```java
Queue<Task> q = new ConcurrentLinkedQueue<>();
q.offer(t);                            // single CAS, never blocks
Task next; while ((next = q.poll()) != null) handle(next);
```

## Replace isEmpty-then-poll with null-checked poll

Before — TOCTOU race:

```java
if (!q.isEmpty()) handle(q.poll());    // poll may still return null
```

After — one atomic step:

```java
Task t = q.poll();
if (t != null) handle(t);
```

## Replace poll-spin with blocking queue where waiting is needed

Before — burns a core:

```java
for (;;) { Task t = clq.poll(); if (t == null) continue; handle(t); }
```

After — parks the consumer:

```java
BlockingQueue<Task> q = new LinkedBlockingQueue<>();
handle(q.take());                      // conditions, no spin
```

## Replace per-task remove() cancellation with state flags

Before — O(n) CAS walk per cancel. After — `AtomicBoolean cancelled` per
task, checked at poll; `remove` reserved for rare cases.
