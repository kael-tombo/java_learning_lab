# Lab 15: Building a GenAI Platform — Math Foundation

## 1. Capacity Sizing

```
replicas = ceil( peak_rps / (service_rate_per_replica * target_utilization) )
```

Example: peak 400 rps, per-replica 12 rps at batch-optimal settings, `rho = 0.6`:

```
400 / (12 * 0.6) = 55.6 -> 56 replicas
```

Sensitivity to `rho`:

```
rho      replicas    tail latency impact
0.4          84      comfortable
0.6          56      target
0.8          42      p95 roughly doubles
0.9          38      p95 roughly 5x
0.99         34      unstable in practice
```

Why: mean wait `W = 1/(mu - lambda) = 1/(mu(1-rho))`. At `rho = 0.9`, `W = 10/mu`;
at `rho = 0.6`, `W = 2.5/mu`. A 4x tail-latency difference for a 1.5x capacity
difference — always buy the headroom.

## 2. Fallback Sizing

Fallback capacity must equal full peak, because it exists for the scenario where the
primary is entirely gone:

```
total_capacity >= peak_rps / target_utilization
fallback_capacity >= peak_rps / target_utilization     (independently)
```

With the numbers above: 56 primary + 56 fallback = 112 replicas to survive total
primary loss. This is expensive and often skipped. The cheaper alternative is a
*degraded* fallback: a smaller model that serves a reduced SLO. Then:

```
fallback_capacity = peak_rps * degraded_share / target_utilization
```

With `degraded_share = 0.4`: 23 replicas instead of 56, serving 40% of peak at
degraded quality. Choose explicitly, with the quality drop measured.

## 3. Availability of a Tiered Fleet

Per-request success probability across tiers:

```
P(success) = 1 - prod_i (1 - availability_i)
```

With independent tiers at 0.99, 0.98, 0.95:

```
P(success) = 1 - (0.01 * 0.02 * 0.05) = 1 - 0.00001 = 0.99999
```

But tiers are **not independent** — they share infrastructure (network, control
plane, deployment tooling). With a shared component of 0.999:

```
P(success) = 1 - (1-0.999)*(1-0.01)(1-0.02)(1-0.05)
           = 1 - 0.001 * 0.01 * 0.02 * 0.05   (approximate)
           = 1 - 1.0e-8  -> no measurable gain
```

The lesson: **independent redundancy does not beat correlated failure**. Reducing the
blast radius of the shared component (blast-radius limits from Lab 14) is worth more
than adding tiers.

## 4. Queueing Under Tier Routing

M/M/c with `c` servers, arrival `lambda`, service rate per server `mu`:

```
rho = lambda / (c * mu)
W = 1 / (c*mu - lambda) + 1/(2*c*mu)     (M/M/c approximation)
P(wait) = Erlang-C formula
```

Erlang-C for `lambda = 400`, `mu = 12`, `c = 56`:

```
offered load a = lambda/mu = 33.3 Erlangs
c = 56 servers, a = 33.3  ->  rho = 0.595
Erlang-C P(wait) ~ 0.28
```

So 28% of requests wait at all — which is why TTFT p95 is dominated by queueing,
not service time. An M/D/c queue (deterministic service, as in batched inference)
gives materially lower waits for the same `rho`.

## 5. Cost Per Team Attribution

```
team_cost = sum over requests of (in_tok*p_in + out_tok*p_out + gpu_ms*p_gpu)
```

With attribution accuracy `a` (fraction of requests correctly attributed):

```
reported_team_cost = true_team_cost * a + misattributed * (1 - a)
```

An accuracy of 0.95 with 10 teams means ~5% of each team's cost is noise. Teams will
dispute the numbers. Improve attribution completeness (tenant in every request
context, from the gateway) rather than arguing about rounding.

## 6. Quota Fairness

Weighted fair queueing: tenant `i` gets weight `w_i`, and under saturation its share is
`w_i / sum(w)`. Deficit round robin:

```
deficit_i += w_i * quantum
serve i if deficit_i >= 1; then deficit_i -= 1
```

Starvation risk: a tenant with tiny weight gets served slowly. Bound it with a
minimum-share guarantee:

```
min_share_i = alpha / n_tenants     (alpha e.g. 0.5)
```

Implementation: cap the deficit at `max_deficit` so a tenant can accumulate at most
`max_deficit` before being served. Simple, and prevents both starvation and one
tenant monopolizing.

## 7. Breaker Parameters

Failure rate limit `theta`, window `w`, half-open trial count `h`:

```
P(spurious trip) = P(F >= theta*n_failures | true failure rate p_true)
```

With `theta = 0.5`, 10 requests in window, `p_true = 0.05`: `P(F >= 5) ~ 0.0012` —
a 0.12% spurious trip rate per window. At 12 windows/minute across 50 models that is
~36 spurious trips/hour. Either raise the window size or require a minimum count
(`min_calls = 20`) before evaluating. Both are standard.

## 8. Rollback Blast Radius

```
blast_radius = fraction of requests served by the changed component version
```

If a retrieval index change affects one tenant, radius is 1/N. If it affects the shared
embedding model, radius is 1.0. The cost of a bad release:

```
expected_cost = blast_radius * impact_per_affected_request * detection_delay
```

Since impact is roughly constant and detection delay is roughly fixed (Lab 14),
**minimizing blast radius is the highest-leverage release discipline**. Feature flags
with independent kill switches exist to make radius small.

## 9. Canary Promotion Math

To promote at each step with a `d`-point resolution:

```
n_step = 960 / d^2
total = n_step * (1/f1 + 1/f2 + ... + 1/fk)
```

For steps 1%, 10%, 50%, 100% and `d = 5`:

```
n = 384;  total = 384 * (100 + 10 + 2 + 1) = 43,392 requests
```

At 50k rps/day traffic: 21 hours. At 2k/day: 22 days. For low-volume products, use
shadow evaluation:

```
shadow_sample = n_step           (sampled from full traffic, not served)
```

Shadow cuts the ladder requirement to a single evaluation of `n` samples.

## 10. Evaluation Cost

Judge calls per release:

```
eval_cost = n_items * c_judge * n_passes
```

With `n = 1000`, `c_judge = $0.02`, `n_passes = 3` (baseline, candidate, rerun):
`$60` per release. With 20 releases/week: `$5,200/week`. Worth it. With `n = 20,000`
per pass and 10 passes: `$4,000` per release — also fine at that scale. Between those,
sample smartly: full suite on the main branch, sampled suite per pull request.

## 11. Adoption Funnel

```
  teams requesting access      N
  teams completing quickstart  N1
  teams passing first eval     N2
  teams shipping to production N3
  teams still shipping at 90d  N4

  conversion = N1/N, N2/N1, N3/N2, N4/N3

  biggest drop = the stage to invest in
  time_to_first_success = median(t_production - t_request)
```

A platform with `N/N1 = 0.3` has an onboarding problem, not a capability problem. This
funnel is the platform team's product analytics, and it is the SLI most teams forget.

## 12. Shared vs Dedicated Capacity

Let `u_t` be tenant utilization, `N` tenants, `c_shared` shared servers, `c_ded_j`
per tenant:

```
P(shared works) ~ 1 if sum_t u_t < c_shared   else contention
dedicated cost  = N * ceil(u_max / (mu * rho))
```

Shared capacity is far more efficient (statistical multiplexing) but tail latency for
one tenant depends on the others. Dedicated is predictable and expensive. Practical
split: shared tier for batch and low-risk, dedicated or reserved capacity for
interactive SLOs. Reserve floor:

```
reserved = interactive_peak_rps / (mu * rho)
shared   = total_peak / (mu * rho) - reserved
```

## 13. Deprecation Migration

Old version at traffic share `p(t)` decaying; new version must reach `p < 0.01`:

```
exponential decay:  p(t) = p0 * e^(-k t)
```

Choose `k` from the deadline `T`: `k = ln(p0/p_target) / T`. With `p0 = 0.5`,
target `0.01`, deadline 60 days: `k = ln(50)/60 = 0.065/day`, half-life 10.6 days.
Send notices at `p0`, `p0/2`, and at `T/3`; auto-pin remaining traffic at `T` with a
compatibility shim.

## Worked Numbers

Peak 400 rps, per-replica 12 rps.

- Primary at `rho = 0.6`: 56 replicas.
- Fallback (degraded, 40% of primary capacity): 23 replicas.
- Total 79 versus 112 for a full-capacity fallback: 29% cheaper.
- Erlang-C at 33.3 Erlangs with 56 servers: ~28% of requests wait.
  With 84 servers (`rho = 0.4`): Erlang-C drops sharply and p95 TTFT improves
  materially for ~50% more capacity.
- Canary with `d = 5`: 43,392 requests, 21 hours at 50k/day, 22 days at 2k/day.
- Eval cost with 1,000 items x 3 passes x $0.02: $60 per release.
- Attributed cost per team with 95% attribution accuracy and 10 teams:
  5% of every team's number is noise. Teams will file disputes. Fix attribution at the
  gateway, not in the spreadsheet.

## Self-Check Questions

1. Size replicas at peak 250 rps, service rate 15 rps, `rho = 0.6`.
2. Show why correlated failure erases the benefit of extra tiers.
3. Compute the breaker spurious-trip rate for `theta = 0.5`, 10 calls, `p = 0.05`.
4. Derive `k` for a deprecation from 50% to 1% in 45 days.
5. Size the shared and reserved split for 100 interactive rps and 400 batch rps.