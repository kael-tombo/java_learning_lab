# Architecture: CopyOnWriteArrayList

## Components

- `volatile Object[] array` — the entire state. Always non-null (starts
  `new Object[0]`). Never mutated in place after publication.
- `final Object lock` — guards writers only. Readers never touch it.
- `COWIterator` — holds `snapshot` + `cursor`; walks the frozen array.
- `CopyOnWriteArraySet` — thin wrapper using `addIfAbsent` for add.

## Data flow: add(e)

1. `synchronized (lock)`: `es = getArray()`, `Arrays.copyOf(es, len+1)`,
   `es[len] = e`, `setArray(es)` (volatile store). O(n) copy + allocate.

## Data flow: get(i)

`elementAt(getArray(), i)` — one volatile read, one bounds check, one
array load. No lock, no CAS, O(1). Concurrent writes replace the array
reference; in-flight reads keep walking the old one safely.

## Data flow: iterator()

Captures `getArray()` and never re-reads the field. Sees construction-time
state exactly: later adds invisible, later removes still visited. Length
fixed → terminates despite concurrent growth.

## Data flow: addIfAbsent / remove (optimistic)

1. Lock-free scan of a snapshot. Miss (remove) / hit (addIfAbsent) →
   return without locking.
2. Else lock, re-fetch current, revalidate the overlapping prefix
   (lost-race path: another writer changed the array mid-scan), then copy
   and publish.

## Boundaries

- Write-heavy or large-list mutation: O(n) copy per write dominates —
  use `synchronizedList(ArrayList)` or a concurrent queue instead.
- Every iterator pins its array: N long-lived iterators × M mutations = N
  retained arrays.
