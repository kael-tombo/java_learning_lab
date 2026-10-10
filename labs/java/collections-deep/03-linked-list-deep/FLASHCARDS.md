# Flashcards: LinkedList Deep Dive

Q: What is `java.util.LinkedList` structurally?
A: doubly-linked list of Node{item,next,prev} with first/last handles and size.

Q: State the position rule.
A: node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.

Q: What are the tree/growth thresholds?
A: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs).

Q: How does growth/rebalance work?
A: no sentinel node: size==0 means first==last==null, every mutation branches on null.

Q: What are the null rules?
A: fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal.

Q: What is the default sizing / allocation behavior?
A: implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst.

Q: Which ops form the hot path?
A: linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast.

Q: How do views/iterators behave?
A: ListItr / DescendingIterator; unsynchronized; structural change must flow through link/unlink (size+modCount).

Q: Name one extra invariant from the source.
A: doubly-linked symmetry: node.next.prev == node.prev.next == node.

Q: Where is the authoritative behavior defined?
A: `java.util.LinkedList` + THEORY.md / CODE_DEEP_DIVE.md in this lab.
