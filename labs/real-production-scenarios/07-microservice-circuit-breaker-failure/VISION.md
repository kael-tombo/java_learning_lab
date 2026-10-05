# VISION — Lab 07: On-Call Excellence with Cascades

## What Great Looks Like
- Breaker opens in seconds, fallback serves degraded, page says which edge + state.
- On-call force-opens sick edge without waiting for permission; traces prove origin.
- No retry storm: global backoff policy enforced in code review.

## Habits
1. Check breaker-state dashboard before error-rate alone.
2. Know force-open/close actuator endpoints for your tier.
3. Require fallback + bulkhead in every new downstream call (review gate).
4. Chaos-test one slow-dep monthly.
5. Track fallback rate as first-class SLI.

## Anti-Habits
- Bumping timeouts to "fix" timeouts.
- Shared pools for mixed-latency deps.
- Retrying on OPEN circuits.

## Maturity Ladder
L0 none → L1 defaults, no fallback → L2 tuned + fallback → L3 per-dep + bulkhead + chaos → L4 auto-tune, coordinated retry, <2-min containment.

## Interview Signal
Walk a cascade: origin trace, L=λW math, force-open command, fallback design, prevention config diff.
