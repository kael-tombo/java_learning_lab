# Vision: Caching Algorithms

## Direction

This lab covers eviction under fixed capacity: LRU (recency), LFU (frequency),
and Belady OPT as the offline lower bound. The practical skill is choosing an
eviction rule from measured access patterns and stating its cost: O(1) hit and
update for hash map plus linked-list or frequency bookkeeping, O(capacity)
memory, and miss ratio (faults over requests) as the comparison metric.

## What to learn

- LRU mechanics: access-ordered map plus recency list, O(1) get and put.
- LFU mechanics: per-key frequency counts, eviction of the minimum.
- Belady OPT: farthest-future eviction; optimal offline, online lower bound.
- Measurement: miss ratio curves across capacities; hit-rate SLOs.
- Competitive framing: LRU is k-competitive for paging with cache size k.

## Non-coverage

- This lab does not cover cache coherence protocols or CPU memory hierarchies.
- It does not cover distributed cache consistency or invalidation protocols.
- It does not cover admission policies in depth (TinyLFU, Bloom-filter gates).
- It does not cover TTL/expiration management; that belongs to a systems lab.
- Benchmarks here use synthetic reference strings, not production traces.

## How to use this lab

Work through THEORY for the three policies, implement LRU and LFU from
scratch, replicate the OPT simulation in MOCK_INTERVIEW, then complete
MINI_PROJECT with miss-ratio curves at several capacities.

## Pitfalls

- Sizing from defaults instead of miss-ratio curves.
- Using LRU on scanning workloads that defeat recency.
- Treating OPT as implementable; it bounds, never ships.

## Done when

- You can implement LRU and LFU without notes and state each cost.
- You can define Belady OPT and explain why it bounds online policies.
- You can plot miss ratio against capacity and read the knee of the curve.
- You can argue LRU against LFU for a given skew and shift pattern.
