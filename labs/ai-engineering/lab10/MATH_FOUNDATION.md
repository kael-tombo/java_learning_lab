# Lab 10: AI Deployment & CI/CD — Math Foundation

## 1. Replica Count From a Service Curve

A replica is a request/second budget, not a CPU percentage. If one replica sustains
`mu` requests/second at target utilization and the fleet must absorb `P_peak`:

```
replicas = ceil( P_peak / (mu * u_target) )
```

The `u_target` factor is the whole game. Utilization near 1.0 makes average latency look
fine and the tail explode, because queueing delay grows as `1/(1-rho)`:

```
W = S / (1 - rho)        S = service time at one replica, rho = mu_actual / P_arriving
```

| rho | W / S |
|-----|-------|
| 0.50 | 2.0 |
| 0.70 | 3.3 |
| 0.85 | 6.7 |
| 0.95 | 20 |
| 0.99 | 100 |

Going from `u_target = 0.95` to `0.60` raises the replica count by 1.6x and cuts tail
latency by an order of magnitude. **Latency SLOs are a capacity decision**, made long
before any incident.

## 2. Little's Law

For an interactive LLM service, arrivals `lambda`, average service time `E[S]`, and
average time in system `W`:

```
L = lambda * W        N = lambda * E[S]
```

Worked: 200 requests/second, 3.5 s mean time in system -> `L = 700` requests resident.
That number is queue depth, and it is what the autoscaler should watch, because it leads
utilization by roughly the service time. Scaling on GPU utilization means reacting 3.5
seconds late.

## 3. Autoscale Lag and Cold Start

A scaler that reacts after `T_detect` of load rise and takes `T_boot` to be useful
overshoots by design. If load grows as `P(t) = P0 * (1 + g*t)`:

```
replicas_uncovered(t) = max(0, (P(t) - capacity(t)) / mu)
```

Worst-case uncovered demand with 30 s detect, 45 s boot, `g = 0.1/s`, `mu = 20 rps`:
at `t = 75 s`, demand has risen `1 + 0.1*75 = 8.5x`; the fleet has added 0. Uncovered
traffic is `7.5 * P0` for 75 seconds. This is why the design answer is a warm pool held
permanently at baseline-plus-burst, not a scaler doing its best.

## 4. Recovery Time Objective Drives Replica Headroom

Let spare capacity `S` (replicas above current need) be lost abruptly at time 0.
Recovering a deficit of `D` replicas takes:

```
T_recovery = ceil( D * T_boot / S )
```

| spare S | boot 45 s | D=10 replicas to rebuild | T_recovery |
|---------|-----------|--------------------------|-------------|
| 0 | 45 s | 10 | never (single failure) |
| 2 | 45 s | 10 | 225 s |
| 4 | 45 s | 10 | 113 s |
| 6 | 45 s | 10 | 75 s |

This is why "we can scale back down" is a resilience decision. Headroom is idle capacity
by construction; its value is only realized during a recovery or a spike.

## 5. Canary Sample Size

Two versions with quality means `p_new` and `p_old`, and you want to detect a regression
of at least `delta` before shipping. With per-request Bernoulli outcomes, the number of
canary requests needed for roughly 80% power at significance 0.05 is approximately:

```
n >= ( z_{alpha} * sqrt(2*p(1-p)) + z_{beta} * sqrt(p0(1-p0) + p1(1-p1)) )^2 / delta^2
```

With `p0 = p1 + 0.02`, `delta = 0.01`, `p ~ 0.8`: `n ~ 3,000+` per arm. At 200
requests/second, 5% canary traffic delivers 10 requests/second, so a statistically
honest 5% step needs roughly **5 minutes of steady traffic**. Rules of thumb like
"watch it for two minutes" are decisions made on noise.

## 6. Sequential Testing Saves the Canary Window

With a two-sided z-test each peek inflates false-positive rate. Use an alpha-spending or
always-valid boundary, e.g. `m`-sequential:

```
alpha_spend(m) <= 2 * phi( z_{alpha/(2m)} - sqrt(m) * z_{beta} )
```

or simply fix the step in advance. Practical consequence: **decide the step sizes and
sample targets before the release**, then the gates are mechanical. A gate computed
after seeing the numbers is not a gate.

## 7. Expected Cost of a Bad Release

```
expected_cost = blast_radius * impact_per_request * requests_before_detection
              ≈ radius * impact * (lambda_affected * T_detect)
```

| radius | impact | T_detect | expected cost |
|--------|--------|----------|---------------|
| 0.01 | $3 | 5 min | $0.003 |
| 0.05 | $3 | 5 min | $0.015 |
| 0.25 | $3 | 5 min | $0.075 |
| 1.00 | $3 | 5 min | $0.300 |

100x from rollout design. `T_detect` is bounded by alerting quality and is the hardest
term to improve quickly, so **radius is the lever you actually own**, which is what
canary, flags, and kill switches are for.

## 8. Rollback as a Tail Bound

If rollback is an alias repoint with a measured duration `T_rb ~ LogNormal(mu, sigma)`,
users see the bad version for the sum of `T_detect + T_rb`. With median 60 s, sigma 0.6:

```
P(exposure > 5 min) ≈ 1 - Phi( (ln300 - ln60) / 0.6 ) ≈ 0.6%
P(exposure > 20 min) ≈ 1 - Phi( (ln1200 - ln60) / 0.6 ) ≈ 8%
```

A rollback that requires a rebuild has effectively infinite tail. Hence: previous
artifact warm, alias repoint, repoint effective next request, and the duration measured
as a release metric rather than assumed.

## 9. Risk Weighted by Change

Not every commit deserves the same ceremony. With per-change-type expected impact
`I_t`, detection ease `D_t`, and frequency `f_t`:

```
portfolio_risk = sum_t f_t * I_t / D_t
```

| change type | freq | impact | detect | risk |
|-------------|------|--------|--------|------|
| prompt wording | 40/wk | 1 | 10 | 4.0 |
| model swap | 1/qtr | 50 | 5 | 10.0 |
| index rebuild | 2/wk | 8 | 4 | 4.0 |
| tool schema | 6/wk | 20 | 3 | 40.0 |
| retrieval top-k | 3/wk | 6 | 6 | 3.0 |

Tool schema changes dominate. Worth knowing where to spend review capacity — this table
is the argument for schema diffs being a required review artifact.

## 10. Rollout Time Versus Exposure

Given ladder weights `w_1..w_m` and per-step gate durations `T_i`, time to 100%:

```
T_full = sum_i T_i
```

Adding steps shortens exposure but lengthens time-to-100%. With a 5-minute detection
window, every extra step at a small weight is nearly free insurance:

| ladder | T_full | exposure during a mid-ladder failure |
|--------|--------|----------------------------------------|
| 1 → 100 | 10 min | 100% * 5 min |
| 1 → 5 → 25 → 100 | 20 min | 25% * 5 min |
| 1 → 5 → 25 → 50 → 100 | 30 min | 50% * 5 min |

The exposure column is the number that matters; the extra ten minutes of release time is
cheap.

## 11. Latency Budget Arithmetic

An end-to-end p95 budget of 2500 ms must be *allocated*, not discovered:

```
budget = t_queue + t_prefill + t_decode + t_retrieval + t_guardrails + t_network
```

Allocation: queue 300, prefill 200, decode 1500 (100 output tokens at 15 ms/token),
retrieval 250, guardrails 150, network 100 = 2500 ms. A change that adds 200 ms to
retrieval is invisible in aggregate and a gate violation for that component — which is
why per-stage budgets exist in CI rather than only in a dashboard.

## 12. Cost Per Successful Request

Raw token cost hides waste. Define:

```
cost_per_success = total_spend / successful_requests
                 = cost_per_request / success_rate
```

Success rate 0.95 -> 1.053x. Success rate 0.80 -> **1.25x**. A change that adds 0.5 cents
of compute but drops success from 0.95 to 0.85 raises total cost per success while every
per-token dashboard still looks fine. Budgets must be on the ratio.

## 13. Environment Parity Divergence

Score a staging/prod parity mismatch set with weights. Any mismatch in model or prompt
version is a hard fail regardless of score:

```
parity = 1 - sum_i w_i * indicator(mismatch_i)
```

with `w = {model 1.0, prompt 1.0, index 0.8, gen-config 0.5, secrets 0.0, data 0.6}`.
Hard-fail on `model`, `prompt`, and `index` because those three have historically been
the causes of staging-green-prod-red.

## 14. Drift Detection Sensitivity

Under a distribution shift, the mean of a monitored statistic moves by `d` standard
errors after `n` samples:

```
z = d * sqrt(n)
```

To detect a 1-sigma shift at `z >= 3`, `n >= 9` — but that is per single test. With
`m` metrics checked, the family-wise false alarm rate at `alpha = 0.001` per metric is
`1 - (1-0.001)^m`: at 50 metrics, 4.9% per window. Hence sequential/CUSUM monitoring for
drift and a corrected threshold, rather than 50 independent alarms.

## 15. Rollback Drills

Success probability of a rollback drill is the product of per-step successes. Five manual
steps at 0.9 each -> `0.59`. Two documented, automated, rehearsed steps at 0.95 each ->
`0.90`. **Automating the path you rely on during an incident** is the single highest-value
change to rollback design, and it is arithmetic.

## Worked Numbers

Platform: 200 rps peak, 40 ms mean service time per replica, `mu = 25 rps`.

- Required replicas: `ceil(200 / (25 * 0.60)) = ceil(13.3) = 14`. At `u = 0.95` it would
  have been 9 — the "cheap" configuration with 20x queueing delay.
- Little's law at `u = 0.60`: `rho = 200/(14*25) = 0.571`, `W = 40ms/0.429 = 93 ms` mean
  time in system from queueing alone. At `u = 0.95` with 9 replicas: `rho = 0.889`,
  `W = 40/0.111 = 360 ms`.
- Canary: 5% of 200 rps = 10 rps; detecting a 2-point drop with 80% power needs ~3,000
  samples per arm -> 300 s. So the 5% step is a five-minute gate, not a glance.
- Exposure: a regression that only appears at the 25% step costs `0.25 * 200 * 5 * 60 =
  15,000 bad requests` at 3 cents = $450 expected. At 100% direct it is $1,800.
- Recovery: headroom of 4 warm replicas rebuilds 10 lost replicas in
  `ceil(10*45/4) = 113 s` — inside the 5-minute rollback objective.
- Cost per success: a change adding $0.005/request while success drops 0.95 -> 0.85
  multiplies `0.005/0.95 = 0.00526` into `0.005/0.85 = 0.00588`, an 11.8% increase in
  cost per *successful* request.

## Self-Check Questions

1. Compute required replicas at 350 rps, `mu = 20`, `u = 0.55`.
2. Compute `W/S` at `rho = 0.9` and at `rho = 0.98`.
3. With 4 warm replicas and 60 s boot, how long to rebuild 20 lost replicas?
4. Estimate canary sample size per arm for a 1-point drop at 80% power.
5. Compute expected cost of a release that reaches 50% before a 10-minute detection.
6. Give the budget breakdown for a 2000 ms p95 with 80 output tokens at 12 ms/token.
