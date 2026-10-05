# Distributed Caching (Deep) - Vision

## The Big Picture
Deep caching is coherence plus failure tolerance: many copies, one truth, no coordinator. This
lab goes past cache-aside into invalidation protocols, negative caching, and the arithmetic of
stampedes, hot keys, and eviction under memory pressure.

## Why This Matters
Caching is the most common performance intervention and the most common source of
correctness incidents. The gap between "we added Redis" and "we have a coherent cache" is
where the incidents live.

## The Vision for This Lab
This lab treats the cache as a distributed data structure with its own consistency contract.
You will implement invalidation protocols, prove that no single-message invalidation is
sufficient, and build the defences — single-flight, stale-while-revalidate, negative caching,
and bounded TTL — that make incoherence a measured window rather than an unbounded one.

## Learning Philosophy
1. There is no always-correct invalidation; there is a bounded staleness window
2. TTL is the backstop — invalidation is an optimisation, TTL is the guarantee
3. One popular key is one partition's problem, not a cache problem
4. Negative results are data too, and must be cached

## Future Path
- 08-cache-stampede-mitigation — the production incident version
- 02-consistency-models — cache coherence in the model vocabulary
- 08-partitioning-sharding — consistent hashing for cache placement

## Success Metrics
You have mastered deep distributed caching when you can:
- [ ] Implement two invalidation protocols and show why one fails
- [ ] Measure and eliminate stampede, penetration, and avalanche separately
- [ ] Size memory and eviction for a working set that changes
- [ ] Design a TTL policy from measured staleness tolerance

## The Distributed Mindset
> A cache does not remove a consistency requirement; it converts it into a promise about how
long you will tolerate being wrong. Write the number down, measure it, and let TTL enforce it
when invalidation inevitably fails.