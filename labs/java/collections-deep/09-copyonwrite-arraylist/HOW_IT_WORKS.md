# How Copy-on-Write Works

## A write, concretely

List `[A, B]`, thread calls `add(C)`:

1. Lock. Snapshot `es = [A, B]`. Copy → `[A, B, _]`, set slot 2 → C.
2. `setArray([A,B,C])` — one volatile write. Unlock.
3. A reader that loaded the old reference before step 2 finishes its whole
   traversal on `[A, B]` — valid data, just older. No torn reads: array
   *references* are atomic and the old array is immutable by convention.

## A snapshot iterator, concretely

`it = list.iterator()` pins `[A, B]`. Then `add(C)`, `remove(A)` publish
`[B, C]`. `it` still walks `[A, B]` — visits A although "removed".
Meanwhile a new iterator sees `[B, C]`. Both correct: each sees the list
as of its own construction instant.

## The volatile heartbeat in set()

`set(0, sameValue)` still calls `setArray(es)` — even though nothing
changed. The store's purpose is the memory barrier: it orders this write
against other threads' reads ("oldvalue == element" comment in source).
Without it, readers could observe arbitrarily stale orderings with no
progress marker.

## The lost-race recheck

`remove(X)`: lock-free scan finds X at index 2 of snapshot S. Before
locking, another thread removes index 0 and publishes S'. Now X sits at 1
in S'. The locked path detects `snapshot != current` and re-scans the
common prefix instead of trusting index 2 — which in S' holds a different
element. Trusting the stale index would delete the wrong item.
