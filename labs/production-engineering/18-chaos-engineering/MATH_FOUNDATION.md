# Lab 18: Chaos Engineering & Fault Injection — Math Foundation

Chaos experiments are quantitative in two ways: the physics of the fault (Little's Law on queueing, Little's Law on resources) and the economics of the programme (what it costs to run, what it saves). Both need arithmetic.

---

## 1. Why latency injection is the highest-value experiment

Queue occupancy under increased service time:

```
L = λ × W       →   ΔL = λ × ΔW
```

`λ = 2,000 req/s`, `W` normally `40 ms`:
```
L_normal = 80
```
Dependency delayed to `3 s` (no code change, requests still succeed):
```
L_degraded = 2,000 × 3.0 = 6,000 concurrent
ΔL = 5,920   →  74× the normal concurrency
```

What breaks at 6,000 concurrent:
```
thread pool 200        → 5,800 requests queued in-process; p99 = queue_wait + 3 s
Hikari pool 45         → 5,955 wait for a connection; acquire timeout at 3 s → errors
```

Now packet loss at 2% (requests still mostly succeed, each taking +1 RTT):
```
W_effective = 0.040 + 0.02 × 2 × 0.050 (retransmit) ≈ 0.042 s
ΔL = 2,000 × 0.002 = 4   →  negligible
```

**Conclusion**: 2% loss produces a 5% latency increase and ~no queueing. A 3 s dependency delay produces 6,000 concurrent requests and total collapse. Latency injection is 2–3 orders of magnitude more informative per unit of risk.

---

## 2. Retry amplification under latency

```
effective_load = λ × (1 + β)
latency_amplification under a slow dependency ≈ (retries are triggered by slowness)
```

`λ = 2,000`, downstream p99 rises to 1.2 s, client timeout `2 s`, 2 retries with backoff:
```
P(retry) ≈ P(W > 0.6 s) = 0.05 (estimate)
effective_load = 2,000 × (1 + 0.05 × 2) = 2,200
```
But the *thread occupancy* amplification is worse than the request-rate amplification:
```
mean service time under retry = 0.040 + 0.05 × (0.6 + 1.2) = 0.13 s
L = 2,200 × 0.13 = 286 concurrent   vs  80 baseline   →  3.6×
```
With a 200-thread pool this is the difference between 40% occupancy and a saturated pool.

Chaos conclusion: **the experiment that matters for a retry-heavy client is dependency latency, because retries are triggered by slowness.** Packet loss with fast timeouts triggers far fewer retries.

---

## 3. Blast radius as exposure

```
users_exposed = fraction_of_traffic × users_in_window
expected_damage = P(failure) × users_exposed × cost_per_user
```

2M daily users, uniform arrival, experiment at 1% for 20 minutes:
```
fraction_of_day = 20/1440 = 1.39%
users_exposed_at_1% = 2M × 0.0139 × 0.01 = 278 users
at 10%:  2,780 users
at 100% (whole environment): 27,800 users
```
Expected damage at `P(failure) = 0.05` and `$12` per affected user:
```
1%:   278 × 0.05 × 12 = $167
10%:  2,780 × 0.05 × 12 = $1,668
100%: 27,800 × 0.05 × 12 = $16,680
```
**Conclusion**: the radius parameter is a linear cost control. Starting at 1% and doubling on success is the correct escalation, and it is also what keeps the programme approvable by the business.

---

## 4. Abort window and detection latency

```
abort_detection_time ≤ 2 × evaluation_interval + metric_aggregation_lag + tool_propagation
```

`evaluation_interval = 15 s`, `rate()` over a 1-minute window, tool propagation 5 s:
```
abort ≤ 30 + 60 + 5 = 95 s of degradation at most
```
At 1% blast radius and `λ = 2,000`:
```
requests during worst-case abort = 20 rps × 95 s = 1,900 requests
```
At 10% radius: 19,000 requests. **The abort window times the radius — that is the arithmetic reason small radius matters.**

Use `rate(...[30s])` for the abort metric rather than `[5m]`, so the abort is governed by a 30-second lag instead of a 5-minute one.

---

## 5. Steady-state assertion window

```
precondition_confidence = 1 − (1 − p_within_SLO)^N_windows
```
`p_within_SLO = 0.99` per minute, 15-minute window:
```
1 − 0.01^15 = 1 − 1e-30  →  essentially certain the system is healthy
```
5-minute window:
```
1 − 0.01^5 = 0.99999  →  also fine
```
1-minute window:
```
1 − 0.01^1 = 0.99  →  1% chance of injecting on top of an existing problem
```
**Conclusion**: 10–15 minutes is the sweet spot; longer is theatre, shorter risks injecting on top of a pre-existing incident. If the precondition assertion fails, **wait** — do not proceed.

---

## 6. Queue growth and drain time

```
lag_growth_rate = λ_in − λ_out
drain_time      = backlog / (λ_out − λ_in)     for λ_out > λ_in
```

Consumer processing at 800 msg/s, producer at 1,000 msg/s, backlog 4M:
```
growth = 200/s  →  after 10 min backlog = 4M + 120k = 4.12M
recovery at full capacity 1,200 msg/s:  drain = 4.12M / 200 = 20,600 s = 5.7 h
```
Chaos conclusion: **a partition experiment on a consumer whose drain rate is close to its arrival rate is a multi-hour exposure.** Compute the drain time before injecting a partition, and if it exceeds your abort window, the experiment is not safe at that radius.

---

## 7. Cost of an experiment programme

```
programme_cost = experiments_per_week × (prep_hours + run_hours + analysis_hours) × engineer_rate
value = findings_that_became_fixed_actions × P(fix_prevents_incident) × expected_incident_cost
```

`4 experiments/week × 3 h × $110/h = $1,320/week = $68,640/year`.

Findings per experiment: `~1.5` (a mix of null results, which are still evidence, and real findings). Actions that reach fix: 60%. Each prevents an incident-class recurrence with `P = 0.4`, and the platform's incident cost is `~$45,000`:
```
value = 52 experiments/yr × 1.5 × 0.6 × 0.4 × 45,000 = $842,400/yr expected value
```
Ratio: `~12:1`. **Even with aggressive discounting of both the value and the cost, the programme pays.** The honest version of that calculation requires stating the discounting assumptions.

---

## 8. GameDay economics

```
cost_per_game_day = participants × hours × rate
findings_per_game_day ≈ 5.75   (measured; see Lab 14)
cost_per_finding = cost_per_game_day / findings
```

12 people × 4 h × `$110/h` = `$5,280` per GameDay:
```
cost_per_finding = 5,280 / 5.75 = $918
```
Compare to the cost of one incident caused by an undocumented runbook gap:
```
45,000  →  the GameDay is ~49× cheaper per finding than one such incident
```

---

## 9. Fault-detection probability

A fault that produces a measurable signature with signal-to-noise ratio `SNR` over an evaluation window:

```
P(detect in n windows) = 1 − (1 − p)^n,   p ≈ Φ(SNR)
```

`SNR = 2` (`p = 0.023`), `n = 6` windows of 30 s over a 3-minute experiment:
```
P(detect) = 1 − 0.977^6 = 13%    →  most experiments would look "fine"
```
`SNR = 4` (`p = 0.00013`):
```
P(detect) = 1 − 0.99987^6 = 0.08%  →  effectively never
```
**Conclusion**: a chaos experiment cannot detect what the instrumentation cannot see. This is the quantitative reason the observability work in Lab 08 must come first, and why the experiment's pass condition must be a metric that exists.

---

## 10. Retry budget and chaos interaction

During a chaos experiment, the retry budget is what keeps the fault contained:
```
load_during_fault = λ_healthy × (1 + β) + λ_faulted × (1 + β)
sustainable iff λ_healthy × (1 + β) ≤ λ_capacity_remaining
```

Three dependencies fail one at a time, `β = 0.1`, `λ = 2,000` each, capacity 5,000:
```
healthy load while one dep fails = 4,000 × 1.1 = 4,400 ≤ 5,000  ✓
healthy load while two fail      = 2,000 × 1.1 = 2,200 ≤ 5,000  ✓
```
With `β = 0.5` and the same setup:
```
two deps failing = 2,000 × 1.5 = 3,000 ≤ 5,000  ✓ but p99 already degraded
```
With `β = 2` (three attempts per hop, compounded):
```
two deps failing = 2,000 × 3 = 6,000 > 5,000  →  capacity exceeded by the retries themselves
```
**Conclusion**: without a retry budget, a two-dependency fault breaches capacity purely through amplification. Chaos verifies the budget.

---

## 11. Chaos coverage as a metric

```
chaos_coverage = (hypotheses_tested / declared_failure_modes)
```

Declare 24 failure modes across a 10-service platform (dependencies, datastores, network shapes, resource exhaustion, certificate/lifecycle, deployment, clock, data):
```
after a quarter at 4 experiments/week = 52 experiments
coverage = 52/24 > 1  →  but with duplicates and invalidated hypotheses, effective coverage ≈ 0.6
```
The honest metric is not raw count:
```
effective_coverage = distinct_failure_modes_with_a_passing_experiment / declared_failure_modes
```
Track the *pass* rate per mode: a failure mode that has passed an experiment is "known-good"; one that has failed is "known-bad and tracked"; one never tested is "unknown".

---

## 12. Steady-state drift detection

Experiments also detect slow degradation. Baseline the steady state across a week, then before each experiment check drift:
```
drift = |current_SLI − baseline_SLI| / baseline_SLI
refuse to inject if drift > 5% on any guarded SLI
```
This prevents two confusions: attributing pre-existing degradation to the fault, and normalising a real regression because it has been happening for weeks.

---

## 13. Quick drills

1. `λ=2,000`, `W` 40 ms → 3 s dependency delay. Concurrency? **Answer: 80 → 6,000. ΔL = 5,920.**
2. 2% packet loss, +50 ms retransmit. Concurrency change? **Answer: ~negligible (ΔL ≈ 4). Latency injection is the higher-value experiment.**
3. 2M daily users, 1% radius, 20 min. Users exposed? **Answer: 278. At 10%: 2,780.**
4. Abort interval 15 s, `[1m]` rate, 5 s propagation. Max degradation window? **Answer: ~95 s. Use `[30s]` to cut it to ~50 s.**
5. Steady-state assertion window, `p=0.99`/min. 1 min vs 15 min? **Answer: 1% vs ~1e-30 chance of injecting on a bad system. Use 10–15 min.**
6. Consumer 800/s, producer 1,000/s, backlog 4M. Drain time at 1,200/s? **Answer: ~5.7 h. A partition experiment is unsafe at that rate.**
7. 4 experiments/week × 3 h × $110. Annual cost? **Answer: $68,640. Against ~$842k expected value ≈ 12:1.**
8. 12 people × 4 h GameDay, 5.75 findings. Cost per finding? **Answer: $918, versus ~$45,000 for one incident from a runbook gap.**
9. SNR=2 fault, 6 windows. P(detect)? **Answer: 13%. The instrumentation must be able to see the fault.**
10. Two of three deps fail, `β=0.1`, capacity 5,000. Sustainable? **Answer: 2,000 × 1.1 = 2,200 ≤ 5,000 ✓. With β=2: 6,000 > 5,000 ✗.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `ΔL = λ × ΔW` | why latency injection is the priority experiment |
| `users_exposed = fraction × users_in_window` | blast radius as a cost control |
| `abort_window ≤ 2 × eval_interval + agg_lag` | how to bound exposure |
| `drain_time = backlog/(λ_out − λ_in)` | whether a partition experiment is safe |
| `P(detect) = 1 − (1−p)^n` | whether your metrics can see the fault |
| `load = λ × (1+β)` | retry budget containment during a fault |
| `cost_per_finding = programme_cost / findings` | programme business case |
| `effective_coverage = distinct_modes_with_passing_experiment / modes` | the honest chaos metric |
| `drift = |current − baseline|/baseline` | precondition assertion |
| `healthy_load × (1+β) ≤ capacity_remaining` | multi-fault survivability |

