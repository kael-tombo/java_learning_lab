# Reflection: LinkedList Deep Dive

## What did you actually learn?
- Write the position rule from memory: node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last.
- Write the thresholds: Node costs 24 bytes on 64-bit HotSpot w/ compressed oops (12 header + 3x4 refs). When do they *not* apply?

## Where did you get surprised?
- Growth (no sentinel node: size==0 means first==last==null, every mutation branches on null) vs your prior assumption — what changed?
- Null behavior (fail-fast iterators via modCount/expectedModCount; ListIterator.set/remove legal) — did you predict it correctly before testing?

## Transfer check
- Given a new structure with the same shape (doubly-linked list of Node{item,next,prev} with first/last handles and size), which invariant
  would you verify first, and how?
- Extra detail to retain: doubly-linked symmetry: node.next.prev == node.prev.next == node.

## Calibration
- Rate 1-5: can you explain `linkFirst/linkLast/linkBefore + unlink/unlinkFirst/unlinkLast` at the field level without notes?
- If below 4: redo EXERCISES.md #1 and #6, then re-take QUIZ.md.

## One-line synthesis
- `java.util.LinkedList`: position via node(index) walks from nearer end: index < (size>>1) ? forward from first : backward from last, scale via no sentinel node: size==0 means first==last==null, every mutation branches on null, iterate via
  ListItr / DescendingIterator — everything else is commentary.
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
- Lab note (03-linked-list-deep/REFLECTION.md): doubly-linked symmetry: node.next.prev == node.prev.next == node
