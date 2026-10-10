# Debugging: CopyOnWriteArrayList

## Stale data in iteration

Iterator sees removed elements / misses added ones — correct snapshot
behavior, not a bug, in 90% of reports. Confirm: create the iterator
*after* the writes and compare. If fresh iterators also disagree, suspect
in-place element mutation (mistake 7), not the list.

## UnsupportedOperationException from iterator

Stack shows `COWIterator.remove` — code written against ArrayList
iterators. Collect-then-mutate (gather targets in the loop, call
`list.remove` after) is the mechanical fix.

## GC pressure / allocation spikes

Profile allocation, not CPU: `Arrays.copyOf` frames from COW write paths
with byte rates scaling as n × write-rate. Remedy is structural (change
the collection or batch writes), not micro-tuning — confirm with a heap
dump showing multiple `Object[]` versions retained.

## Memory retention via iterators

Multiple large `Object[]` alive with one COW list: find GC roots — pinned
by open iterators/spliterators held in fields or long loops. Shorten scope
or materialize (`new ArrayList<>(cow)`) for extended processing.

## Lost update in check-then-act

`if (!list.contains(x)) list.add(x)` races — two threads both add. Use
`addIfAbsent` (atomic incl. the locked recheck), which exists precisely
for this. Same for remove-then-verify flows.

## Compound-action races

`get(size()-1)`-style pairs race with concurrent writes (index valid at
`size()`, stale at `get` → IndexOutOfBounds). Either catch and retry, use
indexed snapshots (`toArray` once, work on it), or pick a structure with
atomic compound ops.
