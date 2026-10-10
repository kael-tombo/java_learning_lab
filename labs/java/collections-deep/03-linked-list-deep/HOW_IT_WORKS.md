# How It Works: LinkedList Deep Dive

`java.util.LinkedList` is a doubly-linked list of Node{item,next,prev} with first/last handles and size.

## Lookup
1. Compute position per node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.
2. Walk the local structure (chain / links / tree descent) using the
   identity rule in Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs).
3. Return the entry or null/absent per fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.

## Insert
1. Resolve position; handle the empty-store fast path (implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst).
2. Splice/link/rotate the node in; update size.
3. Run growth/rebalance work (no sentinel node: size==0 means first==last==null, every mutation branches on null) when its threshold trips.

## Remove
1. Locate as in lookup; unlink and patch neighbors/parents.
2. Clear the freed slot or rebalance (doubly-linked symmetry: node.next.prev == node.prev.next == node).
3. Views (ListItr / DescendingIterator) observe the removal immediately.

## Iteration
- Order follows the structure (insertion-neutral, index order, or sorted),
  and unsynchronized; structural change must flow through link/unlink (size+modCount).

## Worked trace
- Insert 3 small keys: store allocates per implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst, each key resolves via
  node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last, size becomes 3, no growth yet (no sentinel node: size==0 means first==last==null, every mutation branches on null not tripped).
- Core calls exercised: linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast.
- Lab note (03-linked-list-deep/HOW_IT_WORKS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/HOW_IT_WORKS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
