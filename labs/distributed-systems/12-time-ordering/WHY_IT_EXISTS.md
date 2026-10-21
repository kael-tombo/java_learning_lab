# Why Time Ordering Exists

No node has complete knowledge of system state. Information travels at light speed or slower. By the time you learn about an event, it's in the past.

Wall clocks fail because:
- Quartz drifts 1s/115 days
- NTP residual skew 1-50ms
- Light takes 40ms across Atlantic

Lamport's insight: only causally-related events need ordering. Concurrent events don't need ordering. This lets us build correct systems without perfect clock sync.
