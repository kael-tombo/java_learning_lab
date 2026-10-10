# Math Foundation: LinkedList

## Nearer-end walk
- `node(i)`: `i < (size >> 1)` walks forward from `first`, else backward from
  `last`. Cost is `min(i, size-1-i)` hops: ends are O(1)-ish, middle is n/2.

## Expected walk for uniform random access
- E[min(i, n-1-i)] over uniform i = ~(n/4): half the indices cost <= n/4 from
  one end. So random get averages n/4 hops, worst case n/2 — still O(n), just
  with a 2-4x smaller constant than a singly-linked walk from the head.

## Per-element memory
- Node on 64-bit HotSpot with compressed oops: 12-byte header + 3 x 4-byte
  refs (item/next/prev) = 24 bytes, before the element itself. 1M elements ->
  ~24 MB of nodes plus elements; ArrayList holds 1M refs in one 4 MB array.

## Splice vs shift crossover
- `add(i,e)`: LinkedList pays min(i,n-i) cache-missing hops + O(1) pointer
  writes; ArrayList pays (n-i) contiguous-word shifts via System.arraycopy.
- Rule of thumb: head ops favor the list (O(1) vs O(n) shift); mid-list ops
  usually favor the array because one cache line holds ~16 refs and memcpy
  moves whole lines, while each hop risks a cache miss (~100ns vs ~1ns/word).

## Worked numbers
- n = 100K: middle get walks 50K hops (~ms with misses) vs ArrayList 1 load.
- addFirst x 1M: LinkedList ~O(1) each, no copies; ArrayList shifts 1M words
  per op -> ~10^12 word moves. This is the one workload where the list wins big.

## GC and scan consequences
- N nodes are N heap objects to trace; ArrayList is one object plus refs, so
  young-GC mark time and iterator allocation pressure both favor the array.
- ListIterator.add during a linear pass keeps position (no re-walk): the only
  mid-list insert pattern where LinkedList matches its textbook O(1) claim.
