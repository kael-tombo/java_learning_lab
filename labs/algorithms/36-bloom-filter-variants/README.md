# Bloom Filter Variants — Overview

This lab explores advanced probabilistic data structures derived from the classic Bloom filter: Counting Bloom Filter, Scalable Bloom Filter, Cuckoo Filter, Quotient Filter, and XOR Filter. Each variant addresses specific limitations of the original—deletion support, dynamic resizing, higher space efficiency, and faster membership queries. Students implement each variant from scratch, compare their performance, and understand the tradeoffs between false positive rate, memory usage, and operational complexity.

## Learning Objectives

- Implement a Counting Bloom Filter with multi-bit counters for deletion
- Build a Scalable Bloom Filter that grows dynamically while bounding false positives
- Construct a Cuckoo Filter using fingerprint-based bucket storage
- Benchmark and analyze tradeoffs across all variants

## Prerequisites

- Basic hash set knowledge
- Understanding of the standard Bloom filter
- Java bitwise operations

## Estimated Time

- **Theory**: 90 minutes
- **Practice**: 120 minutes
- **Exercises**: 90 minutes
- **Total**: 5-6 hours
