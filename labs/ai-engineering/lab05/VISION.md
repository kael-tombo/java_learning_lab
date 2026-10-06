# Lab 05: Prompt Engineering at Scale — Vision

## Prompt Lifecycle

```
   draft
     |  lint (order, unfilled vars, banned phrases, schema, owner)
     v
   evaluated ── gate failed ──> rejected (recorded so it is not re-proposed)
     | gate passed
     v
   canary  1% ──> 5% ──> 25% ──> 100%      auto rollback on any breach
     |                                              |
     v                                              v
   active ─────────────────────────────────────> deprecated
     |                                              |
     | rollback (1 call, invalidates cache)          | notices: promotion, 50%, deadline
     v                                              v
   previous known-good                      auto-pin at deadline + shim

  RULE: a missing gate metric counts as a BREACH.
        broken telemetry must not be able to promote anything.
```

## Why Paired Testing Wins

```
  100 items, two systems, per-item scores

  UNPAIRED:
     system A 0.80 +- 0.08 (independent)
     system B 0.75 +- 0.08
     intervals overlap -> "no significant difference"

  PAIRED (same items):
     per-item deltas d_i = a_i - b_i
     sd(d)^2 = sd(a)^2 + sd(b)^2 - 2*rho*sd(a)*sd(b)
     rho = 0.8  ->  sd(d) = 0.632 * sd(a)
     SE ratio = sqrt(0.4/2) = 0.447

     the SAME DATA yields a decisive interval.

  => always evaluate a candidate against the incumbent on identical items.
     independent resampling in the bootstrap destroys this and makes
     every experiment inconclusive.
```

## Sample Sizing Reality

```
  to resolve a change on an ABSOLUTE scale:

  SE = sqrt( p1(1-p1)/n + p2(1-p2)/n )
  n  = (1.96 * SE_target_differential / delta)^2 / (p1(1-p1)+p2(1-p2))
     ~ (1.96/delta)^2 * (p1(1-p1)+p2(1-p2))

  base 0.80 -> 0.85 :  n ~ 440        5 points
  base 0.80 -> 0.83 :  n ~ 2,000      3 points
  base 0.80 -> 0.82 :  n ~ 18,000     2 points

  LADDER TIME at n=440, steps 1/5/25/100:
     requests = 440 * (100 + 20 + 4 + 1) = 55,000
     50k/day  ->  1.1 days
      2k/day  -> 27.5 days    => shadow evaluation is MANDATORY
```

## Accuracy Is Not the Decision Metric

```
  variant        $/req   accuracy   $/correct    verdict
  ------------------------------------------------------------------
  current        0.0040   0.80       0.00500      baseline
  A              0.0045   0.83       0.00542      ACCURACY WIN, COST LOSS
  B              0.0035   0.81       0.00432      the actual winner

  A looks better on the metric teams report by default and is worse
  on the metric finance cares about.

  ALWAYS report (accuracy, cost) together. the efficient frontier,
  not the accuracy leader, is what ships.
```

## Multi-Variant False Positives

```
  8 variants vs one control at alpha = 0.05

  P(any false positive) = 1 - 0.95^8 = 0.34

  three in ten comparisons look significant by pure chance.

  Bonferroni: alpha/8 = 0.00625  (conservative)
  Holm step-down: tighter, still valid
  BH-FDR: controls expected false discovery RATE, appropriate for sweeps

  and report which procedure was used. "we tested 8 prompts" with an
  uncorrected alpha is not a result.
```

## Prefix Cache as a Deploy Bug Detector

```
  template v6:
     [system][few-shot] [docs] [query]
     ^^^^^^^^^^^^^^^^  stable, cacheable

  template v7 (a well-meaning edit):
     [system + "Today: {{date}}"][few-shot] [docs] [query]
     ^^^^^^^^^^^^^^^^^^^^  NOT stable

  hit rate: 0.85  ->  0.00   overnight, with no error anywhere

  => monitor prefix hit rate as an alert. a sudden collapse is the
     fastest signal that a template edit put volatile content in the
     cached region.
```

## Prompt Families and Drift

```
  families:
    system/assistant          shared identity + policy
    tasks/<intent>/           per-intent instructions
    guardrails/<rule>         safety clauses
    fewshot/<intent>/         demonstration sets
    output/<intent>           schemas

  DANGER: tasks/refund updated to v5 while fewshot/refund is still v3.
           the demo teaches the old behaviour; the instruction says the
           new one. results are unreproducible and unexplainable.

  FIX: bundle versioning. system + task + schema + fewshot move atomically
       with one bundle hash in the manifest.
```

## Rollout Decision Tree

```
  change ready
     |
     +-- low risk tier, spot check only?
     |     -> 5% -> 25% -> 100%      (fast path)
     |
     +-- otherwise
           |
           +-- traffic < 2k/day?   -> SHADOW first (build sample size)
           |
           v
           1%  --[gate: accuracy, format validity, refusal,
                 p95 latency, cost/correct]
                 |
                 breach -> AUTOMATIC rollback, alert, post-mortem
                 |
                 ok -> 5% -> 25% -> 100%
                 |
                 every step needs n samples; a step that cannot reach
                 n does NOT advance. patience is the point.
```

## Judge Agreement as a Correction Factor

```
  judge agrees with humans at rate p_j
  observed_delta ~ true_delta * (2*p_j - 1)

  p_j = 0.80  ->  observed = 0.6 * true
  a measured 6-point win is ~10 points of true delta

  p_j = 0.65 (human ceiling territory)
       ->  observed = 0.3 * true      (win rates become almost uninformative)

  => judge-human agreement is not a pass/fail gate, it is a CORRECTION
     on effect size. re-measure monthly; suspend judge metrics when it drops.
```

## Self-Check

- [ ] Versions immutable; owner and risk tier required.
- [ ] Promotion gated; missing metrics count as breaches.
- [ ] Rollback is one call and invalidates the render cache.
- [ ] Experiments paired on identical items with a single bootstrap.
- [ ] Sample size derived from the resolution needed.
- [ ] Accuracy and cost reported together.
- [ ] Multi-variant comparisons corrected.
- [ ] Prompt families versioned as bundles.
- [ ] Prefix hit rate monitored as a deploy alarm.