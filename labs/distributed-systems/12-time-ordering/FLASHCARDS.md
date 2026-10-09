# Flashcards — Time Ordering

1. Q: Happens-before relation? A: Partial order, a->b if same process or msg send/recv, transitive.

2. Q: Lamport clock guarantees? A: If a->b then C(a) < C(b). Not converse.

3. Q: Vector clock storage? A: O(n) per process.

4. Q: Concurrent events condition? A: Neither V1<=V2 nor V2<=V1.

5. Q: HLC components? A: Physical time + logical counter.

6. Q: Causal broadcast ensures? A: Causally related messages delivered in order.

7. Q: Version vectors solve? A: Conflict detection in replicated stores.

8. Q: NTP accuracy on LAN? A: 1-50ms.

9. Q: PTP accuracy? A: Sub-microsecond with HW timestamping.

10. Q: Spanner time system? A: TrueTime, GPS + atomic clocks with uncertainty.
