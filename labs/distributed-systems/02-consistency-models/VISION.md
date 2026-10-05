# Consistency Models - Vision

## The Big Picture
A consistency model is a contract: it tells you what a read is allowed to return after a
write. Everything above linearizable consistency is a deliberate weakening of that contract
in exchange for latency, throughput, and availability. The engineering skill is choosing
the weakest model your feature can survive.

## Why This Matters
The most expensive class of distributed-systems bug is not a crash. It is a read that
returns a value the user already superseded — an order created before the discount applied,
a permission revoked five minutes ago still granting access. Consistency models are how you
prevent that class by construction rather than by bug reports.

## The Vision for This Lab
This lab is a ladder. You implement linearizable consistency first and watch its cost, then
step down through sequential, causal, read-your-writes, monotonic reads, and eventual —
each rung losing a specific, nameable guarantee. By the last rung you can defend why your
feature chose it.

## Learning Philosophy
1. **Guarantees, not adjectives** — name the anomaly each model permits
2. **Anomalies over vibes** — write the interleaving that breaks your model
3. **Session thinking** — users experience consistency as a session, not a table
4. **Cheapest sufficient model** — always start at the bottom and go up

## Future Path
- 10-time-ordering — the clocks that make causal ordering checkable
- 07-replication-strategies — where the model is physically configured
- 01-cap-theorem — the partition-time limits of every rung

## Success Metrics
You have mastered consistency models when you can:
- [ ] Produce a non-linearizable read/write interleaving
- [ ] Implement read-your-writes with a session token
- [ ] Explain why a cache invalidation is a consistency decision
- [ ] Pick a model per endpoint for one real application

## The Distributed Mindset
> Consistency is a spectrum of promises you make to a user who cannot see your topology.
Weakest sufficient promise, stated out loud, beats strongest implied promise.