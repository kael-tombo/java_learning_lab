# Vision: Load Balancing

## Direction

This lab covers spreading load across servers: consistent hashing for stable
key placement, rendezvous hashing for ring-free agreement, and
least-connections for cost-aware dispatch. The practical skill is matching the
method to the workload: stable membership favors rings, small pools favor
rendezvous, uneven request costs favor least-connections.

## What to learn

- Consistent hashing: ring, virtual nodes, O(log V) lookup, minimal remap.
- Rendezvous hashing: per-key scoring, O(N) lookup, no shared ring state.
- Least-connections: open-count dispatch; beats round-robin on skew.
- Measurement: remap fraction on membership change; max-to-mean load ratio.
- Failure behavior: what each method does when one node leaves abruptly.

## Non-coverage

- This lab does not cover L4/L7 proxy configuration or health checking.
- It does not cover weighted round-robin tuning for production fleets.
- It does not cover request hedging, retry budgets, or backoff policy.
- It does not cover data replication or consistency after remapping.
- Simulations here are single-process; no network or cluster is required.

## How to use this lab

Implement the ring from MOCK_INTERVIEW Q1, the rendezvous scorer from Q2,
and the least-connections loop from Q3. Then run MINI_PROJECT with a skewed
key distribution and compare max-to-mean ratios across the three methods.

## Pitfalls

- Using modulo hashing under membership churn.
- Skipping virtual nodes and accepting ring imbalance.
- Judging dispatch by mean load instead of max-to-mean ratio.

## Done when

- You can state each method's lookup cost and remap behavior from memory.
- You can explain virtual nodes and why they smooth ring imbalance.
- You can argue ring against rendezvous for a stated pool size.
- You can show least-connections beating round-robin on one skewed trace.
