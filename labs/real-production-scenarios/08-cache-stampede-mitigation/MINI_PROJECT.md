# MINI PROJECT — Lab 08: Reproduce + Tame a Stampede

## Objective
Trigger TTL-expiry stampede locally, then fix with coalescing + jitter.

## Part A — Reproduce (30 min)
1. Seed Redis + app with 1 hot key TTL 30s fixed; fire 200 rps with k6/curl loop.
2. At expiry observe miss spike + DB (fake 100ms loader) queue + timeouts.
3. Record hit ratio cliff + loader call count (≈ rps × window).

## Part B — Detect (15 min)
1. Aggregate logs to name hot key; compute misses/s vs baseline.
2. Confirm DB-pool saturation as downstream effect, not root cause.

## Part C — Fix (35 min)
1. Add singleflight (assert loader calls ≈ 1 per expiry).
2. Add jitter ±15% + SWR 60s + negative cache 45s.
3. Re-run expiry minute; prove hit >95%, loader flat, p95 stable.

## Deliverables
- Before/after graphs (hit ratio, loader QPS, p95).
- Code diff + math (N→1 reduction, spread window).
- Correctness note: staleness bound per key type.

## Stretch
- Hot-key split 8 ways; fill semaphore cap demo.

## Grading
Repro (30%), correct diagnosis (20%), fix verified (35%), bounds note (15%).
