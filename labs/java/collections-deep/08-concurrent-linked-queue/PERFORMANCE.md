# Performance: ConcurrentLinkedQueue

| Operation | Cost | Notes |
|---|---|---|
| offer (uncontended) | ~1 CAS + short walk | volatile reads, no lock |
| poll (uncontended) | ~1 CAS + dead-node skip | head lag adds null-item hops |
| peek | O(lag + 1) reads | no CAS at all |
| size() | O(n) walk | stale on return; avoid hot |
| isEmpty() | O(lag + 1) | first-live probe, cheaper |
| iterator step | O(1) amortized | skips dead/self-linked |

## Contention scaling

- vs `synchronized LinkedList`: uncontended both fast (thin locks vs one
  CAS); with many cores CLQ scales (CAS retries, no descheduling) while
  the mutex serializes + context-switches.
- Hot-spot reality: all offers CAS the *same* tail `next` — under extreme
  producer counts the tail line bounces. Slack-2 halves pointer CASes but
  the link CAS stays per-offer. For ultra-contended fan-in, consider
  sharding (per-producer queues + drain) or `LinkedBlockingQueue` with
  separate put/take locks.
- Dead-dummy drag: lagging head leaves null-item prefixes; poll walks them
  every call until head swings. Steady-state cost ≈ slack length (≤ ~2
  typical), not unbounded.

## Memory

Per-element `Node` allocation (two volatiles + header ≈ 24–32 bytes) —
GC churn per offer, unlike array heaps. Long chains of dummies await head
swing + GC; self-links keep them collectible, not pinned.
