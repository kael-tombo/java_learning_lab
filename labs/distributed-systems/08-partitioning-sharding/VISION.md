# Partitioning and Sharding - Vision

## The Big Picture
Sharding splits a dataset across nodes so that no node holds all of it. That single decision
determines your ceiling, your rebalancing cost, your query capabilities, and every future
migration. It is the least reversible choice in most systems.

## Why This Matters
A bad shard key is discovered when traffic is 100x what it was at launch, and it is
discovered because one shard is hot while the rest idle. Unlike a slow query, this cannot be
fixed with an index.

## The Vision for This Lab
This lab covers placement, not distribution of concern. You will implement range and hash
partitioning, show consistent hashing's remap advantage, and then confront the part everyone
underestimates: rebalancing while traffic is live, and the queries that partitioning breaks.

## Learning Philosophy
1. **Shard key choice is the architecture** — it decides query patterns forever
2. **Hash for distribution, range for locality** — know which you are buying
3. **Virtual nodes buy balance** — and cost remap work
4. **Cross-shard queries are a design cost** — budget for them explicitly

## Future Path
- 05-distributed-caching — consistent hashing places cache shards
- 12-design-url-shortener — sharding a key-space to a URL
- 06-microservices-scale — shard-per-tenant vs shard-per-entity

## Success Metrics
You have mastered partitioning when you can:
- [ ] Implement range and hash partitioning and describe each failure skew
- [ ] Explain consistent hashing's remap advantage with numbers (1/3 vs 1/N)
- [ ] Choose a partition count from data volume and growth headroom
- [ ] Implement rebalancing with bounded data movement under live writes

## The Distributed Mindset
> A shard key is a promise about your access patterns made today, binding forever. Choose the
one your queries can live with, because you cannot choose a new one cheaply later.