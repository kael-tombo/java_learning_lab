# Mental Models: LinkedList Deep Dive

## 1. Slots plus overflow
Think of `java.util.LinkedList` as numbered slots plus an overflow strategy: doubly-linked list of Node{item,next,prev} with first/last handles and size.
Position first (node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last), then resolve the few items that share it.

## 2. Thresholds as tripwires
Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs) — each is a tripwire that converts a cheap shape into a
scalable one (no sentinel node: size==0 means first==last==null, every mutation branches on null). Below the wire, linear scan is fine; above it,
you pay for structure once and save on every later op.

## 3. Views as windows, not photos
`ListItr / DescendingIterator` is a window into the live store. Writing through the
window writes the room. Copy when you need a photo.

## 4. Nulls as contract, not accident
fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal. The rule exists so "absent" stays distinguishable from
"present" under the class's concurrency/ordering guarantees.

## 5. Growth cost as rent
implements Deque: permits null elements (unlike ArrayDeque); push/pop = addFirst/removeFirst; no sentinel node: size==0 means first==last==null, every mutation branches on null. You pay rent (copies/rotations) rarely and in bulk;
steady-state ops stay cheap. Presizing is paying a year up front.

## 6. The extra gear
doubly-linked symmetry: node.next.prev == node.prev.next == node. That detail is what separates a passing interview answer
from one that matches `java.util.LinkedList`.
- Lab note (03-linked-list-deep/MENTAL_MODELS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/MENTAL_MODELS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/MENTAL_MODELS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/MENTAL_MODELS.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
