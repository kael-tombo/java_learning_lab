# Why It Exists: LinkedList Deep Dive

`java.util.LinkedList` exists because one access pattern dominates real code: resolve a
position fast, then touch only that neighborhood.

- Arrays give O(1) indexing but fixed size; chains/links/trees (doubly-linked list of Node{item,next,prev} with first/last handles and size)
  add growth without giving up the fast path (node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last).
- The 1998 Collections framework (Josh Bloch) needed a general map/list/set
  trio; `java.util.LinkedList` filled the slot its shape fits: doubly-linked list of Node{item,next,prev} with first/last handles and size.
- Later pressure hardened it: hash-flooding forced Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs), multicore
  forced the concurrency split in unsynchronized; structural change must flow through link/unlink (size+modCount), large heaps forced no sentinel node: size==0 means first==last==null, every mutation branches on null.

Without it you reimplement the same three ideas badly: position
(node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last), scale (no sentinel node: size==0 means first==last==null, every mutation branches on null), null/ordering contract (fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal).
The JDK version just has the edge cases — doubly-linked symmetry: node.next.prev == node.prev.next == node — already handled.
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/WHY_IT_EXISTS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
