# REAL_WORLD_PROJECT — Exact Exponential Algorithms
> Exact route optimizer for ≤15 delivery stops with a heuristic fallback and a recorded optimality gap.

## System and inputs
- Nightly planner receives up to 15 stops with a road-distance matrix from the routing provider.
- Dispatcher UI shows the exact tour, its cost, and compute time; jobs over 15 stops route to the heuristic path automatically.
- Held-Karp result cached by (stop set hash, matrix version).

## Design
- Exact path: Held-Karp with bitmask DP, hard timeout of 120 s, memory cap sized from the O(n 2^n) table for n = 15.
- Fallback path: nearest-neighbor plus 2-opt repair; reported gap = (fallback - exact)/exact on instances where both ran.
- Cache keyed on sorted stop set; matrix updates invalidate by version.

## Metrics
- Exact-solve p95 latency at n = 12 and n = 15 (thresholds from the MINI_PROJECT table, not invented here).
- Fallback gap distribution (median and p95) over one month of mixed instances.
- Timeout rate and cache hit rate.
- Cost delta: exact tour distance vs previous manual plans, summed weekly.

## Failure modes
- 16th stop slips into the exact path: input guard counts stops and redirects before allocating the dp table.
- Asymmetric matrix from provider (one-ways): validation rejects non-square input; asymmetric instances take the fallback path only.
- Timeout mid-solve: partial best-tour (best insertion found so far) returned with an `exact=false` flag.
- Stale cache after road changes: matrix version mismatch forces recompute.

## Rollout
1. Shadow mode on historical stop sets; compare exact cost vs dispatched routes.
2. Enable for depots with ≤12 typical stops; watch timeout and gap dashboards.
3. Raise the cap to 15 after two clean weeks.

## Acceptance criteria
1. 4-city reference matrix solves to 80 through the full service path (API in, tour out).
2. A 16-stop request is redirected to fallback with a logged reason, never OOMs.
3. Timeout returns a flagged non-exact tour within the 120 s budget.
4. Gap dashboard shows median and p95 fallback gap over real instances.
5. Cache invalidation on matrix version change is covered by a test.

## Cost and contract notes
- Exact-solve compute budget: cap cost per job from the MINI table (n=15 row) times cloud price per vCPU-second.
- Dispatcher API: POST /tour with stop list returns (tour, cost, exact flag, ms); GET /tour/{id} replays the cached result.
- Fallback gap reported per depot weekly; depots above the agreed gap get stop-count reviews, not solver blame.
- Timeout responses always include the best tour found so far plus exact=false, never an empty body.
