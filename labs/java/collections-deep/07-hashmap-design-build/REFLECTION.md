# Reflection: Hash Table Design

## What surprised you?

Most learners expect deletion to be the easy op. In open addressing it is
the operation that constrains all the others. Write down why nulling a
slot corrupts lookups you have not performed yet.

## Check your model

1. Table n=8, A@1, B@1→2, C@2→3. Remove B (tombstone at 2). Trace
   `get(C)` slot by slot. Now remove A too — trace `get(C)` again.
2. Why does the resize trigger need tombstones in the numerator? Sketch a
   workload where `size/n = 0.4` but probes average 20+.
3. Your table vs HashMap on collide-all-keys input: what is each op's
   cost, and which structure notices first?

## Connect

- Where does your production code depend on iteration being O(live) vs
  O(capacity)? Would a sparse probing table hurt it?
- Which of your key classes has a `hashCode` with low-bit entropy? With
  high-bit-only entropy? (Check: print `h & 7` across sample keys.)

## The one-line takeaway

Probing trades graceful degradation for flat speed — and the price is paid
in deletion discipline, spread quality, and an honest load trigger. If any
of the three slips, the probe table tells you at the worst moment.
## One more probe

4. Backward-shift deletion (IdentityHashMap's `closeDeletion`) vs
   tombstones: which workloads favor each? Name one cost the shift pays
   per delete and one cost tombstones pay per probe.
5. Your table must reject or handle the full-table insert. List three
   options (fail-fast throw, forced resize, overwrite policy) and state
   which your implementation chose and what its observable behavior is.

Revisit the one-line takeaway: it should now name a concrete α cap and
the reason in probe counts, not just "cap early".
