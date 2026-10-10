# Why It Matters: LinkedList Deep Dive

## Everyday impact
- Nearly every request path touches `java.util.LinkedList` (caches, indexes, params, models).
  node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last is why those lookups stay flat as data grows.

## Cost impact
- no sentinel node: size==0 means first==last==null, every mutation branches on null; implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst. One presize decision at startup can remove the only
  latency spikes the structure ever produces.

## Correctness impact
- Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs); fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal. Getting either wrong silently corrupts lookups —
  entries that exist but never match.

## Concurrency impact
- unsynchronized; structural change must flow through link/unlink (size+modCount). Choosing the wrong variant turns a fast map into a race log.

## Interview signal
- Stating node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last + Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs) + no sentinel node: size==0 means first==last==null, every mutation branches on null with the numbers (8/6/64,
  0.75/16, 1.5x/2x, RED=false/BLACK=true as applicable) separates recall
  from understanding. Extra credit: doubly-linked symmetry: node.next.prev == node.prev.next == node.
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_MATTERS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
