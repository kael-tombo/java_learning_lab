# Why Sparse Tables Exist

## The Problem: Static Range Queries

For static arrays (no updates), segment trees O(log n) queries are suboptimal. If we can precompute answers, we can achieve O(1) queries.

## The Innovation

The sparse table precomputes answers for all intervals of length 2^k. Since any range can be covered by at most 2 such intervals (for idempotent operations), queries are O(1).

## When to Use

- Static arrays with no updates
- Idempotent operations (min, max, gcd, lcm)
- Many queries (> n log n)
- Memory is not constrained

## When Not to Use

- Dynamic arrays with updates (use segment tree)
- Non-idempotent operations (use disjoint sparse table)
- Memory-constrained environments (O(n log n) may be too large)
