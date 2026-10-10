# Common Mistakes: CopyOnWriteArrayList

## 1. Writing frequently or at large n

Per-request `add` on a 100k list = 100k-ref copy per request. Symptom: GC
churn with no hot method. Fix: `synchronizedList(ArrayList)`,
`ConcurrentLinkedQueue`, or batching.

## 2. Calling iterator().remove()

`COWIterator.remove/set/add` throw `UnsupportedOperationException` —
mutation goes through the list, never the iterator. Restructure to collect
targets during iteration, mutate after.

## 3. Expecting iterators to see fresh writes

Snapshot iterators never reflect post-construction mutations — by design.
Code that adds then continues an old iteration silently processes stale
data. Re-acquire the iterator after writes.

## 4. Holding iterators open

Long-lived iterators pin full arrays across mutations — silent retention
scaling with write count. Scope iterators tightly; copy needed elements
out for long processing.

## 5. Synchronizing externally on the list

`synchronized (cowList)` doesn't exclude writers (they lock the internal
`lock` field). Compound actions need the list's own atomic methods, not
client-side locking.

## 6. Using COWArraySet at scale

`CopyOnWriteArraySet.add` = `addIfAbsent` = O(n) scan + O(n) copy.
Correct for small sets (dozens); quadratic-feeling past thousands. Use
`ConcurrentHashMap.newKeySet()` instead.

## 7. Storing mutables and "editing in place"

Mutating an element's fields after publication is visible to all snapshot
holders unevenly (no happens-before per element) — the array is frozen,
its contents' fields are not. Publish new element objects instead.
