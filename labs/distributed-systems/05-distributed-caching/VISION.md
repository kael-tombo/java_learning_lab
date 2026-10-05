# Distributed Caching - Vision

## The Big Picture
A distributed cache is a second, smaller, faster copy of data you already have — and copies
go stale. The entire discipline of caching is choosing what to copy, how long to trust the
copy, and how to notice when you were wrong.

## Why This Matters
Caching is the highest-leverage latency change available and the highest-frequency source of
production incidents. The same mechanism that takes p99 from 40ms to 2ms will eventually
serve a user another user's cached response, or melt the origin during a stampede.

## The Vision for This Lab
This lab treats caching as a consistency problem wearing a performance costume. You implement
the placement patterns (cache-aside, write-through, write-behind), then the failure modes
(stampede, penetration, avalanche, invalidation races), then the fix for each — because the
pattern without its failure mode is a liability.

## Learning Philosophy
1. **Measure before caching** — never add a cache to hide an unexamined query
2. **TTL is a correctness decision** — it is how long you are willing to be wrong
3. **Warm the cache on miss** — single-flight is not optional in production
4. **Cache keys are API** — version them or you will ship a breaking change

## Future Path
- 02-consistency-models — invalidation is a consistency choice
- 08-partitioning-sharding — consistent hashing places cache shards
- 08-cache-stampede-mitigation — the production incident lab

## Success Metrics
You have mastered distributed caching when you can:
- [ ] Implement cache-aside with single-flight and negative caching
- [ ] Reproduce a cache stampede under load and eliminate it
- [ ] Choose a TTL by measuring the staleness users actually tolerate
- [ ] Explain why write-behind can lose data and when that is acceptable

## The Distributed Mindset
> A cache is a promise to serve data you did not check. Every TTL is a number in that promise.
Choose it deliberately, measure the cost of being wrong, and never make it twice.