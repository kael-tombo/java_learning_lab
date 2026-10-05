# Math Foundation — DevOps

## Availability
- Single-component availability: `A = uptime / (uptime + downtime)`.
- Series components: `A_total = A1 * A2 * ... * An`.
- Parallel (redundant) components: `A_total = 1 - (1 - A1)(1 - A2)`.

Example: two nines (99%) in series with a 99.9% DB gives
`0.99 * 0.999 = 0.98901` — worse than either alone.

## Error budget
- For an SLO of `p` over window `T`, budget = `(1 - p) * T`.
- 99.9% monthly → ~43.2 minutes of allowed downtime.
- 99.95% monthly → ~21.6 minutes.
- 99.99% monthly → ~4.32 minutes.

## Burn rate
- `burn = observed_error_rate / allowed_error_rate`.
- At 99.9% SLO, allowed error rate = 0.1% → observed 1% error is 10x burn.
- If burn stays at 10x, budget (43.2 min) is gone in ~4.3 minutes of wall time... more precisely: budget_time = T_budget / burn.
  Monthly budget 43.2 min at 10x burn exhausts in 4.32 minutes of continuous degradation.

## Canary math
- Canary fraction `f`, error rate `e_c` on canary vs baseline `e_b`.
- Signal: sample traffic so that expected errors during observation
  exceed baseline noise: `f * N * e_c >= k` for some threshold of samples `k`.
- Rule of thumb: if baseline error is 0.1% and canary bug adds 1% to its
  5% slice, overall error rises to ~0.15% — often within noise. Prefer
  per-version golden signals over global averages.

## Retries and timeouts
- Expected latency with independent retries (no backoff):
  `E[T] = t * (1 + p + p^2 + ...)` truncated at max attempts.
- Without a timeout, worst-case latency is unbounded; always cap with
  `deadline` < caller's patience budget.

## Little's law (capacity)
- `L = λW`: number in system = arrival rate × average latency.
- If a service handles 200 req/s at 100 ms avg, expect ~20 in-flight.

## Sampling math for traces
- At 1% head sampling and 10k requests/day, only ~100 traces/day — enough
  for a rare endpoint? No: a 0.1% path sees ~0.1 trace/day. Use per-path
  or tail-based sampling for rare paths.

## Queueing intuition
- Utilization `ρ = λ / (c * μ)`. As `ρ -> 1`, latency blows up (M/M/1:
  `W = 1/(μ - λ)`). Keep headroom; 70% is a common soft target.

These calculations turn "feels slow/fragile" into arguments you can
defend in a design review.
