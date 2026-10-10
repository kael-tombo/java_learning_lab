# Internals: LinkedList Deep Dive

Source: `java.util.LinkedList`. Field-level behavior verified in CODE_DEEP_DIVE.md.

## Store layout
- doubly-linked list of Node{item,next,prev} with first/last handles and size.
- Size/capacity counters kept incrementally; implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.

## Position computation
- Rule: node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.
- Thresholds: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs).

## Mutation mechanics
- Growth/rebalance: no sentinel node: size==0 means first==last==null, every mutation branches on null.
- Slot hygiene: doubly-linked symmetry: node.next.prev == node.prev.next == node.
- Null handling: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.

## Concurrency/visibility
- unsynchronized; structural change must flow through link/unlink (size+modCount).
- Hot path: linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast; views: ListItr / DescendingIterator.

## Invariants (must hold after every public op)
1. Position rule (node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last) resolves every live entry.
2. Size equals live-entry count; freed slots hold no stale refs.
3. Thresholds (Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs)) trigger before the next op, never lazily skipped.
4. Growth (no sentinel node: size==0 means first==last==null, every mutation branches on null) preserves all entries exactly once.
- Lab note (03-linked-list-deep/INTERNALS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/INTERNALS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/INTERNALS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/INTERNALS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
