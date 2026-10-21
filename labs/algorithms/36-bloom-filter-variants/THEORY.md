# Theory of Bloom Filter Variants

## Counting Bloom Filter

A standard Bloom filter uses a single bit per position, making deletion impossible (clearing a bit may destroy evidence of other elements). The Counting Bloom Filter replaces each bit with a small counter (typically 3-4 bits). Add increments counters, remove decrements them, and check verifies all counters are nonzero. The space cost is roughly 4x the original, but the filter becomes deletable.

## Scalable Bloom Filter

When the number of elements exceeds the filter's designed capacity, the false positive rate degrades sharply. A Scalable Bloom Filter maintains a list of constituent filters, each with a tighter false positive bound (using a geometric tightening ratio). New elements are added to the newest filter; membership queries check all filters in order. The total false positive rate remains bounded by a geometric series: FP_total <= FP_0 + FP_1 + ... < FP_0 / (1 - r).

## Cuckoo Filter

Inspired by cuckoo hashing, the Cuckoo Filter stores a short fingerprint of each item in one of two candidate buckets. When both buckets are full, an existing fingerprint is displaced ("kicked") to its alternate location. This achieves high load factors (~95%) with lower false positive rates than Bloom filters for the same space. Operations are O(1) amortized.

## Quotient Filter

The Quotient Filter stores a fingerprint and uses linear probing with quotienting: the fingerprint is split into a quotient (bucket index) and a remainder. Three additional metadata bits per slot handle collisions via a variant of linear probing. It supports deletion and merging without rehashing.

## XOR Filter

The XOR Filter uses a system of three bit arrays and a hash function assignment technique to achieve minimal space (1.23n bits) with a single round of hashing per query. Construction is more expensive than a Bloom filter, but queries are faster and space usage is provably near optimal.

## Comparison Summary

| Variant | Deletion | Dynamic | Space/Element | False Positive |
|---|---|---|---|---|
| Bloom | No | No | ~1.44 log2(1/epsilon) | epsilon |
| Counting | Yes | No | ~4x Bloom | epsilon |
| Scalable | No | Yes | ~1.44 log2(1/epsilon) per layer | <= epsilon |
| Cuckoo | Yes | No | ~(2+epsilon) | <= epsilon |
| XOR | No | No | ~1.23 | epsilon |
