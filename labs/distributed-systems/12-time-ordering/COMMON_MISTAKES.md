# Common Mistakes — Time Ordering

1. Assuming C(a) < C(b) implies causality (Lamport)
2. Forgetting +1 in receive: max(counter, ts) + 1
3. Not handling clock rollback from NTP adjustments
4. Mutable clock values shared without synchronization
5. Fixed-size vectors in dynamic clusters
6. Ignoring message delivery guarantees for causal broadcast
7. Mixing physical and logical time without HLC
