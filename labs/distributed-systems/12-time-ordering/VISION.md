# Time Ordering (Deep) - Vision

## The Big Picture
No clock is trustworthy enough to order events, so systems encode order in the message. This
lab goes deeper than the intro course: hybrid logical clocks, causal broadcast, version
vectors for offline-first sync, and the real reason ordering is hard — it is not the clock, it
is retries.

## Why This Matters
The moment you have two services writing to one entity, ordering becomes a correctness
problem. Without an ordering mechanism in the message itself you are relying on network
luck, and "it works in testing" is a statement about latency, not about correctness.

## The Vision for This Lab
This lab builds a causal broadcast layer that *enforces* delivery order per session and
*detects* violations, then adds version vectors for concurrent editing, and finally puts a
bounded skew on everything so you can reason about what "recent" means.

## Learning Philosophy
1. Encode causality in the payload; never in the timestamp
2. A clock that can go backwards is not a clock
3. Deliver-after-deliver is the only guarantee that is actually achievable cheaply
4. Concurrent edits need merge semantics, not a total order

## Future Path
- 15-gossip-protocols — clocks ride on gossip state
- 17-distributed-filesystems — version vectors for offline sync
- 13-kafka-consumer-lag-incident — ordering violated in practice

## Success Metrics
You have mastered time ordering when you can:
- [ ] Implement HLC with monotonicity and bounded skew
- [ ] Build causal broadcast and show naive broadcast violates it
- [ ] Implement version vectors and detect concurrent offline edits
- [ ] Explain why a monotonic clock alone cannot solve ordering

## The Distributed Mindset
> Ordering is a property of the message, not of the medium. Build it once, in the envelope,
and every consumer inherits correctness for free. Trust the network and you inherit a
production incident instead.