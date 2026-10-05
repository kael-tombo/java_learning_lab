# VISION — Lab 08: On-Call Excellence for Caching

## What Great Looks Like
- Hot-key dashboard + hit-ratio SLI; stampede page names the key.
- Singleflight + jitter + SWR are defaults, not incident follow-ups.
- On-call serves stale confidently within documented bounds.

## Habits
1. Check hit ratio before DB CPU on latency spikes.
2. Know top-10 hot keys and their TTLs.
3. Never FLUSHDB in prod without warm-up plan.
4. Require loader timeout + stale path in review.
5. Load-test expiry minute, not just steady state.

## Anti-Habits
- Fixed TTLs everywhere; retry-on-miss; unbounded fill concurrency.

## Maturity Ladder
L0 naive TTL → L1 jitter → L2 singleflight → L3 SWR + split + throttle → L4 hot-key auto-detect + prewarm.

## Interview Signal
Explain 5000→1 coalescing math + jitter spread + stale correctness bound.
