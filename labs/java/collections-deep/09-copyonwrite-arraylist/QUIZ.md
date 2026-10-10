# Quiz: CopyOnWriteArrayList

## Q1. What single field carries all cross-thread visibility?

**A.** `private transient volatile Object[] array`. Writers publish via
`setArray` (volatile write); readers sample via `getArray` (volatile
read). No reader locking.

## Q2. Why can readers skip locking entirely?

**A.** Published arrays are never mutated in place; the reference swap is
atomic, so a reader always walks one complete, frozen version. The
volatile edge guarantees the version is fully built.

## Q3. What does a COWIterator see, and what does it forbid?

**A.** Exactly the array at construction (later adds invisible, removed
elements still visited). `remove`/`set`/`add` throw UOE; no CME is
possible (no modCount).

## Q4. Why does set() publish even when oldvalue == element?

**A.** The volatile write is a memory-barrier heartbeat (source comment:
"Ensure volatile write semantics..."), broadcasting ordering progress
rather than data change.

## Q5. What is the lost-race recheck in remove/addIfAbsent?

**A.** Lock-free scan first (skip the lock on remove-miss / add-hit);
on the mutation path, lock and re-scan the overlapping prefix because a
concurrent writer may have shifted indices. Acting on the stale index
could delete/insert the wrong element.

## Q6. Cost table: get / add / iterator?

**A.** get O(1) no lock; add O(n) copy+alloc under lock; iterator O(1)
pin, O(1) steps, never locks.

## Q7. When is COW the wrong structure?

**A.** Write-heavy or large-n mutation (O(n) copy per write → GC churn),
long-lived iterators pinning versions, sets past dozens of elements (use
`ConcurrentHashMap.newKeySet()`).
