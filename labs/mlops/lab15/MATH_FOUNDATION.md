# Production ML Architecture - Mathematical Foundations

**Track:** mlops  |  **Lab:** lab15  |  **Level:** Advanced

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## Notation

| Symbol | Meaning |
|---|---|
| `p99_end_to_end = p99_features + p99_inference + p99_queue` | Latency budget - every term needs a number |
| `availability = prod(availability_i) over the required path` | Availability - the weakest link dominates |
| `error_budget_burn = observed / allowed` | Burn rate - drives the alerting threshold |
| `degradation_ladder = (full, reduced, baseline, reject)` | Fallback order - explicit, not accidental |
| `feedback_delay = now - decision_time` | Label lag - bounds how fast drift can be seen |
| `cost_per_1k_decisions = infra + compute_amortised` | Unit economics - the number leadership cares about |

## Why the Math Matters

System architecture is budgeting and failure analysis: tail latencies add, availability multiplies, and detection time bounds what any fallback can achieve.


---

## 1. End-to-end latency budget

```text
p99_total = p99_features + p99_inference + p99_queue + p99_overhead
allocate budget to each term, then enforce per term
tail sums, so a p99 per term compounds at the total
```

Tail latencies add, so a 50 ms budget split across three terms is not 50 ms each. Budgets must be allocated per dependency and enforced with timeouts, or the tail eats the whole allowance.

**Worked example.** Budget 60 ms: features 20, inference 25, queue 10, overhead 5. If features p99 slips to 45 without a timeout, the total becomes 85 and the SLO is missed while every component's dashboard looks individually acceptable.


---

## 2. Availability along the read path

```text
availability = prod of component availabilities (series path)
A(0.999) x A(0.9999) = 0.9989
for a path with four components at 0.999: ~0.996
```

Series composition means availability is set by the weakest few components. Adding a fourth dependency to a read path costs more availability than it usually buys in functionality.

**Worked example.** Registry 0.999, feature store 0.999, compute 0.9995, network 0.9999: product is about 0.9974, or 26 minutes of downtime a month. Removing the registry from the hot path by caching the model locally lifts it to 0.9985.


---

## 3. Degradation ladder and blast radius

```text
ladder: full model -> cached model -> baseline model -> rules -> reject
cost = quality_loss at each rung
ladder must be shorter than the detection time
```

Each rung trades quality for availability, so the ladder should be ordered by that trade. A ladder that takes longer to traverse than your alerting cycle never helps.

**Worked example.** Detection 4 minutes: cached model in 200 ms, baseline in 50 ms, rules in 20 ms. All three rungs are reachable inside detection, so the ladder is useful; a 10-minute 'warm standby' rung would not be.


---

## 4. Feedback delay and detection bound

```text
detection_time >= feedback_delay
drift detection (PSI) is immediate; concept drift detection waits for labels
plan monitoring around the slower signal
```

Concept drift cannot be detected faster than the labels arrive, which sets a hard floor on your quality-detection latency. Designing monitoring without accounting for it produces dashboards that look empty for weeks.

**Worked example.** 30-day churn labels: quality monitoring has a floor of 30 days. Feature PSI can alert same-day, so the architecture needs both, with the understanding that PSI is the early warning and quality is the truth.


---

## Cheat Sheet

- `p99_end_to_end = p99_features + p99_inference + p99_queue` - Latency budget
- `availability = prod(availability_i) over the required path` - Availability
- `error_budget_burn = observed / allowed` - Burn rate
- `degradation_ladder = (full, reduced, baseline, reject)` - Fallback order
- `feedback_delay = now - decision_time` - Label lag
- `cost_per_1k_decisions = infra + compute_amortised` - Unit economics

## Numerical Traps

- Adding per-term p99 values and assuming the total is the mean.
- Ignoring that availability multiplies along a series path.
- Designing a degradation ladder slower than the detection cycle.
- Promising concept drift detection faster than the label latency.
- Reporting model quality without the cost per decision.

## Self-Check Problems

1. Allocate a 60 ms latency budget across four terms and compute the p99 if one slips.
2. Compute availability for a read path and evaluate the effect of caching the model locally.
3. Design a degradation ladder for a 4-minute detection cycle and justify the ordering.
4. For a 30-day label lag, design a monitoring plan with the fastest available signals.
5. Produce a unit economics model for a service with given traffic, hardware and amortised training cost.
