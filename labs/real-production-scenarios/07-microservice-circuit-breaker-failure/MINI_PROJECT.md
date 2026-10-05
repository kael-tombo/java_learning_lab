# MINI PROJECT — Lab 07: Reproduce + Contain a Cascade

## Objective
Simulate slow payment dep, watch cascade, contain via breaker tuning.

## Part A — Reproduce (30 min)
1. Run order→payment demo; inject 5s delay in payment endpoint.
2. With bad config (threshold 80, timeout 30s, shared pool 20), fire 50 rps → record pool exhaustion + error spread.
3. Save trace waterfall + thread-dump showing blocked threads.

## Part B — Detect (20 min)
1. Identify origin from traces (slowest leaf) + breaker state (still CLOSED = bug).
2. Compute L=λW for your load; show queue exceeds pool.

## Part C — Fix (30 min)
1. Apply fixed config (threshold 50, timeout 3s, bulkhead 5, retry max 2).
2. Force-open payment breaker; verify fallback (queued-for-review) + downstream QPS drop.
3. Remove delay; watch half-open→closed recovery; record MTTR.

## Deliverables
- Before/after: pool graphs, breaker states, error %, fallback %.
- Config diff + math justifying pool sizes.
- Prevention checklist for new deps.

## Stretch
- Add jittered backoff; compare retry QPS with/without.
- Alert on pool >80% firing during repro.

## Grading
Repro evidence (30%), correct origin (20%), containment (30%), prevention (20%).
