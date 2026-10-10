# How the Lock-Free Queue Works

## Offer under contention

Threads T1, T2 both append at tail node P (P.next == null). Both CAS
`P.next: null → mine`. Hardware serializes the CASes: T1 wins, T2's CAS
fails, T2 sees `q = T1's node` (non-null) and loops — now appending after
T1's node. No lock, no waiting; the loser does one extra walk.

## Poll under contention

T1, T2 both at head node H with item X. Both `casItem(X, null)`. One wins
and returns X; the loser sees item now null, advances past H, tries the
next live node. No element returned twice, none skipped — the CAS is the
arbiter.

## Why stale tail is harmless

`offer` never trusts `tail`: it walks `next` pointers to the true end.
A tail three nodes stale just means a three-step walk. Updating tail on
every offer would CAS one hot cache line per op — the slack-2 rule (update
only when `p != t`, i.e. two hops observed) cuts tail-CASes roughly in
half while walks stay short.

## Self-links: garbage with a signpost

Dequeued node P gets `P.next = P`. Any thread walking into P sees
`p == q` — "you're on garbage" — and restarts from `head`. The self-link
also severs the chain so GC frees prefix nodes even while a straggler
thread still references one of them.

## Publication without locking

A new node's `item` is written relaxed *before* any thread can reach the
node; the `NEXT.compareAndSet` that links it is a volatile write, so every
thread that traverses to it happens-after sees the item. Visibility rides
the link CAS, not a lock.
