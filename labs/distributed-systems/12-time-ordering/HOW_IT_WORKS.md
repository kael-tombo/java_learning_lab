# How Time Ordering Works

The core challenge: distributed systems run on machines with independent clocks that drift. NTP helps but can't eliminate skew.

Instead of asking "when did this happen?" we ask "what caused what?" — the happens-before relation.

1. **Lamport Clocks**: A counter that increments on each event. Cheap but loses causality.
2. **Vector Clocks**: Each process keeps a counter per process. Expensive but preserves causality.
3. **Hybrid Logical Clocks**: Uses physical time when synced, falls back to logical counters otherwise. Best of both worlds.

Real-world impact:
- DynamoDB uses vector clocks for conflict resolution
- Spanner uses TrueTime with uncertainty intervals
- Cassandra uses version vectors for lightweight transactions
- CRDTs use causal ordering for automatic conflict resolution
