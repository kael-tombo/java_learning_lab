# Performance: LinkedList Deep Dive

## Hot-path costs (`java.util.LinkedList`)
| Op | Cost | Notes |
|----|------|-------|
| lookup | O(1) hash / O(n/2) linked walk / O(log n) tree | per node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last |
| insert | O(1) amortized / O(log n) tree | plus no sentinel node: size==0 means first==last==null, every mutation branches on null |
| remove | same as insert | slot hygiene: doubly-linked symmetry: node.next.prev == node.prev.next == node |
| iteration | O(n) | ListItr / DescendingIterator |

## Constants that dominate
- implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst: first-touch allocation or default sizing decides L1/cache behavior.
- Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs): threshold crossings are the latency spikes in profiles.
- Pointer chasing (linked/tree) vs contiguous scan (array): contiguous wins
  per element by ~4-16x in cache misses even at equal big-O.

## Sizing guidance
- Known n up front: presize once (initialCapacity / ensureCapacity / sizeCtl
  equivalent) to skip the geometric copy series (no sentinel node: size==0 means first==last==null, every mutation branches on null).
- Unknown n: accept amortized growth; call trimToSize/compact only after load.

## Concurrency cost
- unsynchronized; structural change must flow through link/unlink (size+modCount). Contended bucket/cell updates serialize; uncontended paths
  stay CAS-only or lock-free — see THEORY.md for the exact split.

## What to measure
- JMH put/get/remove at n = 10 / 10K / 1M; report p99, not just mean.
- GC logs during bulk load separate copy cost from collection pauses.
- Lab note (03-linked-list-deep/PERFORMANCE.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/PERFORMANCE.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
