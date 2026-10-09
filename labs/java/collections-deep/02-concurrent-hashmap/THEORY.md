# ConcurrentHashMap — Theoretical Foundation

## Core Concept

`java.util.concurrent.ConcurrentHashMap` (CHM) is a lock-striped hash table where
**buckets, not the map, are the unit of locking**. Reads are almost entirely
lock-free; writes lock only the first node of one bucket. Since Java 8 it shares
HashMap's `Node[]` layout — the old Java 7 `Segment` array is gone, and
`concurrencyLevel` survives only as a constructor parameter that is ignored.

## The put Path (JDK 23 source order)

```
put(key, value):
  1. initTable()                    // lazy; sizes via sizeCtl
  2. i = (n-1) & hash; f = tabAt(tab, i)
  3. f == null  -> casTabAt(tab, i, null, Node)   // EMPTY BIN: pure CAS, no lock
  4. f.hash == MOVED -> helpTransfer(tab, f)      // resize in progress: help out
  5. onlyIfAbsent && key matches   -> return old value without locking (fast read)
  6. else synchronized (f) { ... }  // lock ONLY the first node of this bucket
```

Step 3 is why uncontended inserts into fresh buckets never touch a monitor. Step 6
locks on the *node* `f`, not the map — two puts to different buckets proceed in
parallel, two puts to the same bucket serialize.

## Counting: LongAdder-Style, Not Atomic

A single `AtomicLong size` would be the contention hotspot of the whole map. CHM
instead copies `LongAdder`:

```java
sumCount() = baseCount + Σ counterCells[i].value
```

Each increment first CASes `baseCount`; on contention it hashes the thread's probe
to a `CounterCell` and CASes *that*. Contention splits across cells, so the sum is
cheap under load — at the cost that `size()` is a **snapshot approximation** that
may be stale the moment it returns.

`size()` clamps the result into `[0, Integer.MAX_VALUE]`.

## Resizing: Cooperative Transfer

Resize doubles capacity (power of two, like HashMap). The differences:

- **No thread owns the resize alone.** The thread that trips the threshold installs
  a `ForwardingNode` (hash = `MOVED`) marking a bucket as moved; every other thread
  that meets `MOVED` calls `helpTransfer` and joins the work. A stuck resize is
  therefore unlikely even if the triggering thread pauses.
- Resize triggers when `sumCount() >= sizeCtl` (not on load factor per bucket).
- The **old table stays readable** during transfer: readers hitting a moved bucket
  follow the forwarding node to the new table, so no read ever blocks on resize.

`initialCapacity` and `loadFactor` are consumed **once**, in the constructor:
`size = 1.0 + initialCapacity / loadFactor`, rounded up to a power of two. After
that, load factor plays no role in growth decisions — `sizeCtl` becomes the
next-threshold marker.

## Treeification

Identical thresholds to HashMap: bins treeify at **TREEIFY_THRESHOLD = 8**, only in
tables ≥ **MIN_TREEIFY_CAPACITY = 64**, and untreeify on resize-split at
**UNTREEIFY_THRESHOLD = 6**. The treeified bin locks its `TreeBin` root — and
`TreeBin` may briefly lock/unlock to maintain balancing, so a reader can see a
lock retry loop rather than blocking indefinitely.

## Why null Is Banned

CHM rejects null keys **and** null values (`throw new NullPointerException()`).
`get(k) == null` must unambiguously mean "absent": if null were a storable value,
every `putIfAbsent`, `compute`, and `merge` would need a second probe to
disambiguate. HashMap permits null because it has no concurrency ambiguity to
resolve; CHM chose total clarity instead.

## Visibility: volatile + Unsafe, Not synchronized Reads

Bucket heads are read through `tabAt` (an `Unsafe` volatile load) and written
through `casTabAt`. Node fields `val` and `next` are `volatile`. So:

- A reader sees any completed write to `val` without locking — `replace(k, old, new)`
  and `get` work lock-free.
- The happens-before edge comes from volatile/CAS, not from monitors, which is what
  keeps read throughput close to a plain HashMap under read-heavy load.

## Iteration and Weak Consistency

Iterators are **weakly consistent**: they never throw
`ConcurrentModificationException`, never block, and may or may not reflect
concurrent updates. `size()`, `isEmpty()`, `containsValue()` are all snapshots of a
moving target — fine for monitoring, wrong for logic that needs a consistent view
(for that, take a lock or copy under `synchronized`).

## Complexity Summary

| Operation | Cost |
|-----------|------|
| get | O(1) expected, lock-free |
| put (empty bucket) | O(1) expected, one CAS |
| put (contended bucket) | O(1) expected, one monitor on that bucket |
| size() | O(#cells), snapshot, approximate |
| iteration | O(N), weakly consistent |

## Key Invariants

1. Capacity is a power of two; `(n-1) & hash` is the only index computation.
2. A bucket is locked only via `synchronized (firstNode)` — never the table or map.
3. Any bucket whose head has hash `MOVED` must be skipped by readers and completed
   by writers via `helpTransfer`.
4. `sumCount()` equals total structural increments if no cell CAS fails mid-flight;
   transient undercount during contention is accepted and self-corrects.
5. Null keys and values are impossible, so presence tests are single-probe.
