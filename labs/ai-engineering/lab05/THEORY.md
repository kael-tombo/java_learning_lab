# Lab 05: Prompt Engineering at Scale — Theory

## 1. Prompts Are Code

A prompt is a versioned artifact with an owner, a test suite, and a rollback. Treat it
any other way and every change becomes an unreproducible incident.

```
prompt registry
  promptId      support.reply
  version       v7 (immutable, hash-addressed)
  owner         support-eng@
  risk tier     MEDIUM  (determines required gates)
  template      with typed variables
  evals         pass/fail per registered suite
  rollout       0% -> 5% -> 25% -> 100%
  changelog     what changed and why
```

## 2. Versioning and Lifecycle

```
draft -> evaluated -> canary -> active -> deprecated -> deleted
```

Rules:
- Versions are immutable. Editing an active version means creating a new one.
- Every version has an owner and a risk tier. Orphaned prompts are auto-deprecated.
- Promotion requires a passing gate on the registered suite.
- Rollback is a single config call that also invalidates the render cache.
- Every trace records the prompt version, so any response is attributable.

## 3. Template Management

Typed variables prevent the highest-frequency silent bug:

```
{vars: {customer_tier: ENUM[free,pro,enterprise], issue_summary: STRING<2000>}}
```

- `assertNoUnfilled` at render time: a literal `{{var}}` reaching the model is an error.
- Canonical section order (system, instructions, context, schema, question) makes prefix
  caching work and makes diffs readable.
- Stable/variable split is automatic from the section order; verified by a test.

## 4. A/B Testing at Scale

The discipline that matters: **paired comparison on identical items**.

```
delta_i = score_i(variant) - score_i(control)
CI_95   = bootstrap over delta_i
```

- Assign by stable user hash, salted per experiment.
- Per-category diffs, not just aggregates — a 20-point collapse in one intent can hide
  inside a flat average.
- Minimum sample size derived from the resolution you need: `n ≈ 960/d^2` for a
  `d`-point change on a rate near 0.5.
- "Within noise" is a valid, publishable outcome.
- Demonstration ordering averaged over seeds for few-shot prompts (position variance
  can exceed the effect).

## 5. Rollout Strategies

| Strategy | Split | Rollback | Use |
|----------|-------|----------|-----|
| Shadow | 100% mirrored, not served | n/a | Measuring at zero user risk |
| Canary | 1/5/25/100 | traffic flip | Most changes |
| Blue-green | 0 or 100 | instant | Config-only, needs instant revert |
| A/B | 50/50 by user | flip | Comparing two versions |

Automated gates at every step; automatic rollback on breach; a missing metric counts as
a breach.

## 6. Performance Metrics

Track per prompt version:

```
accuracy per intent          format validity      refusal rate
tokens/correct               cost per correct outcome
TTFT and total latency       cache hit rate       repair rate
```

`tokens/correct` and `cost per correct outcome` are the metrics that prevent
"optimization" that spends more to be slightly better.

## 7. Version Families

Large systems have prompt families that must stay consistent:

```
system/assistant   one shared system prompt
tasks/<intent>/    per-intent task prompts
guardrails/<rule>  safety instructions
fewshot/<intent>   demonstration sets
output/<intent>    output schemas
```

Version them together as a bundle when they must change atomically. Prompt drift — one
family updated, the rest stale — produces confusing, non-reproducible behaviour.

## 8. Governance

- **Risk tiers** determine the required gate: low (unit + spot check), medium (full
  offline suite), high (full suite + safety suite + human review).
- **Change control** identical to code: PR, review, eval result attached.
- **Deprecation**: notices at promotion, at 50% traffic, and at a deadline; auto-pin at
  the deadline with a compatibility shim.
- **Audit**: which prompt version produced which response, for how long.

## 9. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Unfilled variable | Literal `{{name}}` in a prompt | No render assertion | Throw at render |
| Prompt sprawl | Same instruction in 40 places | No registry | Registry + CI block |
| Cache always missing | Low prefix hit rate | Volatile content in the prefix | Layout audit |
| Change reverted silently | No changelog | No versioning | Registry |
| Over-gating | Teams bypass the platform | Too many required gates | Fast path for low risk |
| Optimizer overfits | Gain vanishes on a fresh set | Tuned on the test set | Held-out set, multi-seed |
| Length-driven win | Accuracy up, tokens up 3x | Accuracy reported alone | Report tokens/correct |
| Prompt families drift | Inconsistent behaviour | Partial updates | Bundle versioning |

## 10. Operations

- Dashboards per version: quality, cost, latency, cache hit rate, rollback events.
- Alerts: format validity drop, refusal spike, cost per correct rising, a version with
  no recent eval.
- Drift: if quality drops while the model is unchanged, suspect input drift first.
- Every prompt version reproducible from its spec: template, variables, sampling
  config, evaluator version.

## Key Equations

```
n_for_resolution = 960 / d^2              (d = desired point resolution)
tokens_per_correct = tokens_per_request / accuracy
cost_per_correct = cost_per_request / accuracy
CI_delta = bootstrap_ci(score_variant - score_control)
```