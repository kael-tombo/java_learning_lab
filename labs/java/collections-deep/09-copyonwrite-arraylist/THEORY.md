# CopyOnWriteArrayList Deep Dive — Theoretical Foundation

## Core Concept

`java.util.concurrent.CopyOnWriteArrayList<E>` is a `List` where **every
mutation copies the entire backing array** and publishes the copy through a
single `volatile` write:

```java
private transient volatile Object[] array;

public boolean add(E e) {
    synchronized (lock) {
        Object[] es = getArray();
        es = Arrays.copyOf(es, len + 1);
        es[len] = e;
        setArray(es);          // the volatile publication
        return true;
    }
}
```

Reads never take the lock: `get(i)` is `elementAt(getArray(), index)` — one
volatile read plus one array load. The price of a write is O(n) copy; the
price of a read is O(1) with zero contention.

## The Read/Write Asymmetry Is the Whole Point

| Operation | Cost | Locking |
|-----------|------|---------|
| get(i) | O(1) — volatile read + array load | none |
| add(e) | O(n) copy + allocate | `synchronized (lock)` |
| set(i, e) | O(n) clone + write | `synchronized (lock)` |
| remove(o) | O(n) scan + O(n) copy | `synchronized (lock)` |
| iterator() | O(1) — captures array reference | none |
| iteration step | O(1) array walk | none, ever |

This wins exactly when **reads dominate writes by orders of magnitude**:
listener lists, configuration snapshots, routing tables — structures mutated
rarely and traversed constantly, often by many threads at once.

## Snapshot Iterators: No CME by Construction

`iterator()` captures `getArray()` at construction and walks *that array*
forever:

```java
public Iterator<E> iterator() {
    return new COWIterator<E>(getArray(), 0);
}
```

Consequences:

- **Never throws `ConcurrentModificationException`** — there is no `modCount`
  check because there is nothing to check against; the array it walks is
  immutable by convention (no writer ever mutates a published array in place;
  writers always replace it).
- **Sees exactly the state at construction** — elements added later are
  invisible; elements removed later are still visited.
- **Does not support `remove`/`set`/`add`** — `COWIterator` throws
  `UnsupportedOperationException` for all three. Mutation goes through the
  list, never the iterator.

This is *stronger* than `ConcurrentLinkedQueue`'s weak consistency: a COW
iterator is a true point-in-time snapshot, not a fuzzy concurrent walk.

## The Volatile Publication Protocol

The single `volatile Object[] array` field carries all cross-thread
visibility:

1. Writer builds the new array **entirely under `synchronized (lock)`**.
2. `setArray(newArray)` — one volatile write — publishes it.
3. Readers' `getArray()` — one volatile read — sees either the old or the new
   array, never a mixture (array references are atomic; contents are safely
   published because everything before the volatile write happens-before
   everything after the matching volatile read).

Note `set(i, e)` with an *equal* element still calls `setArray(es)` — the
source comment says why: "Ensure volatile write semantics even when oldvalue
== element." The write isn't about the value; it's a memory-barrier heartbeat
so that threads blocked on stale reads observe *some* ordering progress.

## The Lost-Race Optimization in addIfAbsent/remove

`remove(Object)` doesn't lock immediately. It snapshots, scans lock-free, and
only then locks and **revalidates**:

```java
public boolean remove(Object o) {
    Object[] snapshot = getArray();
    int index = indexOfRange(o, snapshot, 0, snapshot.length);
    return index >= 0 && remove(o, snapshot, index);   // locks inside
}
```

Inside the lock, if `snapshot != current` (someone else mutated first), it
re-scans the overlapping prefix rather than trusting the stale index — the
"lost race" path. `addIfAbsent` does the same: lock-free `indexOf` first, lock
and recheck second. The pattern is optimistic concurrency *within* a lock:
avoid paying for the lock on the overwhelmingly common miss path... actually
no — both still lock on a hit. The saving is avoiding the lock when the
element is absent (for `remove`) or present (for `addIfAbsent`)? Read it
precisely: `addIfAbsent` returns false without locking if the lock-free scan
finds the element; `remove` returns false without locking if the scan misses.
The lock is only taken when mutation is actually needed.

## When NOT to Use It

- **Write-heavy workloads**: each write copies n references. A list with 1M
  elements costs ~8MB allocation *per add* — GC churn dominates everything.
- **Large lists with frequent mutation**: `Collections.synchronizedList(new
  ArrayList<>())` (in-place mutation under a lock, O(1) amortized add) or
  `ConcurrentLinkedQueue` (lock-free, no copies) both beat it.
- **Memory-sensitive snapshots**: every iterator holds its array alive. N
  long-lived iterators across M mutations pin N arrays — a silent memory leak
  shaped like "correct" code.
- **`CopyOnWriteArraySet`** is a thin wrapper (`addIfAbsent` for add) — same
  costs, set semantics at O(n) per contains.

## Ordering and Equality Semantics

- Iteration order is insertion order *of the snapshot* — stable and
  predictable, unlike any hash-based structure.
- `equals` follows `AbstractList.equals` (element-wise) — a COW list equals an
  ArrayList with the same elements.
- Null elements are **allowed** (unlike the concurrent queues) — `add(null)`
  works; `indexOf` uses `equals` with null handling.

## Key Invariants

1. The published array is never mutated in place — every writer replaces it
   wholesale under `synchronized (lock)`.
2. `array` is always non-null (constructed as empty `new Object[0]`, never
   assigned null).
3. Readers observe a prefix-consistent history: each `getArray()` returns some
   array that was *the* current array at a real instant; arrays are totally
   ordered by publication time.
4. Iterators pin exactly one array version and terminate (the array's length
   is fixed, so no concurrent growth can extend an iteration).
