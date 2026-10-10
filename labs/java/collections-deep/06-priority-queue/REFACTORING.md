# Refactoring: PriorityQueue Usage

## Replace sort-in-a-loop with a heap

Before — O(n log n) per extraction:

```java
List<Task> pending = ...;
pending.sort(comparing(Task::deadline));
Task next = pending.remove(0);   // O(n) shift + full sort each tick
```

After — O(log n) per extraction:

```java
PriorityQueue<Task> pending = new PriorityQueue<>(comparing(Task::deadline));
pending.addAll(tasks);           // O(n) heapify
Task next = pending.poll();      // O(log n), no shift
```

## Replace TreeSet-with-lossy-comparator

Before — distinct tasks compare 0, silently dropped:

```java
Set<Task> q = new TreeSet<>(comparingInt(Task::priority)); // dedups!
```

After — duplicates retained, tie broken explicitly:

```java
PriorityQueue<Task> q = new PriorityQueue<>(
    comparingInt(Task::priority).thenComparingLong(Task::seqNo));
```

## Replace remove+offer updates with lazy deletion

Before — O(n) remove per priority change:

```java
q.remove(job); job.setPriority(p); q.offer(job);
```

After — O(log n) stale-entry idiom:

```java
q.offer(new Entry(job, p));                 // new version
Entry e; do { e = q.poll(); } while (e != null && e.stale());
```

## Bulk-load through the collection constructor

Before — n × O(log n) offers. After — `new PriorityQueue<>(list)` for the
O(n) heapify path. Same result, ~10× less work at n = 10⁶.
