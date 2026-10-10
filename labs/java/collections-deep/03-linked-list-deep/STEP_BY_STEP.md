# Step by Step: LinkedList

Trace `add("a"); add("b"); add(1, "x"); removeFirst()` on an empty list.

## Step 1 — add("a") -> linkLast
- `first == null`, so linkLast sets both `first = last = newNode(a)`.
  Node: {prev=null, item=a, next=null}. size 0->1, modCount++.

## Step 2 — add("b") -> linkLast
- Non-empty: `last.next = newNode(b)`, `newNode.prev = old last`, `last` moves.
  Check symmetry: `first.next == last`, `last.prev == first`. size 1->2.

## Step 3 — add(1, "x") -> node(1) + linkBefore
- `node(1)`: `1 < (2>>1)=1`? No -> walk backward from last, 0 hops (it IS last).
- linkBefore(x, node_b): wire `x.prev = a-node`, `x.next = b-node`, patch both
  neighbors. Verify `a.next == x`, `x.prev == a`, `x.next == b`, `b.prev == x`.

## Step 4 — removeFirst() -> unlinkFirst
- Detach first (a-node): `first = a.next` (= x-node), `first.prev = null`,
  null out a-node's fields for GC. size 3->2, modCount++.

## Step 5 — Iterate and check fail-fast
- `it = list.listIterator(); list.add("z"); it.next()` -> must throw
  ConcurrentModificationException (modCount drifted).
- Redo with `it.add("z")` -> legal, expectedModCount updated.

## Step 6 — Deque face check
- `push("h")` lands at first (size 3->4); `poll()` removes it from the head
  via unlinkFirst; `offer(null)` succeeds — nulls are legal here, unlike
  ArrayDeque, so assert `contains(null)` is true afterward.

## Self-check
- After each step assert `first.prev == null`, `last.next == null`, size.
