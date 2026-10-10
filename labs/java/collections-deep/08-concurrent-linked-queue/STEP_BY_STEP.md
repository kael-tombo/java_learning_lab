# Step by Step: Lock-Free Offer and Poll

Queue: head → H(dummy, item=null) → A(1) → B(2), tail → H (stale by 2).

## offer(C)

1. Snapshot `t = tail = H`. `p = t = H`.
2. `q = p.next = A` (non-null) → advance `p = A`, `q = B` → advance
   `p = B`, `q = null`. True end found.
3. `CAS(B.next: null → C)` succeeds — C is now a member (linearized).
4. `p (B) != t (H)` → `casTail(H, B)` — hop two at a time; tail now B
   (still one behind C — allowed).
5. State: H → A → B → C. Tail at B. Next offer walks one step. Fine.

## poll()

1. Snapshot `h = head = H`. `p = H`: item null (dummy) → advance, `q = A`.
2. `p = A`: item 1, live → `casItem(1, null)`. Suppose success → return 1.
3. `p (A) != h (H)` → `updateHead(H, A)`; self-link H (`H.next = H`) so
   stragglers restart and GC reclaims H.
4. State: head → A(dead) → B(2) → C. Next poll skips A (null item).

## Contended poll drill

Two threads at B simultaneously: both read item 2, both `casItem(2,null)`.
Hardware admits one. Winner returns 2; loser sees null, advances to C.
Neither blocks; loser's cost is one extra node visit.

## Self-link restart drill

A straggler holding H walks `H.next = H` → `p == q` → abandons the walk,
re-reads `head` (now A), continues from live chain. No infinite loop, no
use-after-free.
