# Time and Ordering - Vision

## The Big Picture
Nodes cannot share a clock, so distributed systems do not order events by time — they order
them by causality. Logical clocks encode "this happened after that" without needing a
physically accurate clock, and physical-clock discipline (TrueTime, PTP) is needed only when
you must talk about real elapsed time.

## Why This Matters
Every non-trivial distributed bug is an ordering bug wearing a costume: a cache that serves
an older value after a newer one, a session that appears to go backwards, a message that
arrives before the message that caused it. Causal order is the invariant being violated.

## The Vision for This Lab
This lab walks the full clock hierarchy — Lamport, vector, hybrid logical, and TrueTime —
implementing each and constructing the specific anomaly it prevents. The payoff is a system
that can *detect* causality violations instead of hoping it never violates them.

## Learning Philosophy
1. Causality is about happens-before, not about timestamps
2. Lamport gives total order cheaply but cannot detect concurrency
3. Vector clocks detect concurrency at O(N) cost — that is the real tradeoff
4. Physical time is a last resort, with real infrastructure cost

## Future Path
- 12-time-ordering — the same material with HLC and causal broadcast
- 03-distributed-consensus — Raft terms are logical clocks
- 17-distributed-filesystems — version vectors for offline sync

## Success Metrics
You have mastered time and ordering when you can:
- [ ] Implement Lamport and vector clocks and explain what each cannot express
- [ ] Construct two concurrent events and detect them with vector clocks
- [ ] Implement an HLC that stays within a bound of physical time
- [ ] Explain why TrueTime needs GPS and PTP and what that costs

## The Distributed Mindset
> Timestamps lie. Causality does not. If your system needs events in the right order, encode
the order in the event and let the timestamp be a display detail.