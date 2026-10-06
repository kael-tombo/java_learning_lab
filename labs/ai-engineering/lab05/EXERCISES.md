# Lab 05: Prompt Engineering at Scale — Exercises

Difficulty: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Prompt Registry with Immutable Versions (E)

Register versions with hash, owner, risk tier, changelog. Editing a version creates a
new one.

**Verify**: any content change yields a new hash; old versions remain retrievable.

---

## Exercise 2: Typed Template Rendering (E)

Render `{{var}}` substitutions with type validation and `assertNoUnfilled`.

**Verify**: missing variable throws; wrong type throws; undeclared variable throws.

---

## Exercise 3: Section Ordering and Prefix Stability (M)

Enforce canonical section order; assert the stable prefix hash is identical across 100
renders with different variables.

---

## Exercise 4: Gated Promotion (M)

`promote(id, version)` refuses a version whose gate failed. `rollback(id)` restores the
previous version in one call and invalidates the render cache.

---

## Exercise 5: Experiment Assignment (M)

Stable user bucketing salted per experiment; verify stability across restarts and
randomization across experiments.

---

## Exercise 6: Paired A/B Harness (H)

Run two prompt variants on an identical item set; compute paired win rate and a
bootstrap CI. Verify a fake improvement is reported as within noise.

---

## Exercise 7: Per-Category Diff (M)

Report metric deltas per category with regression flags. Verify a single-category
collapse is localized rather than averaged away.

---

## Exercise 8: Sample Size Calculator (E)

Compute `n = 960/d^2` for target resolutions; report the time to complete a ladder at a
given traffic rate.

---

## Exercise 9: Canary Controller (H)

Implement 1/5/25/100 with gates on accuracy, format validity, latency, cost; automatic
rollback; missing metric counts as a breach.

---

## Exercise 10: Shadow Evaluation (M)

Mirror traffic to a candidate without serving it; score both; report paired deltas at
zero user risk.

---

## Exercise 11: Prompt Families and Bundles (M)

Version a bundle of system + task + schema prompts atomically; verify a partial update
is rejected.

---

## Exercise 12: Rollout Ladder Sizing (H)

Compute total requests to complete a ladder at a given traffic rate; decide whether
shadow evaluation is mandatory.

---

## Exercise 13: Risk-Tiered Gates (M)

Define low/medium/high risk tiers with different gate requirements; verify a high-risk
prompt cannot be promoted with only a spot check.

---

## Exercise 14: Metrics Dashboard (M)

Per version: accuracy, format validity, refusal rate, tokens/correct, cost per correct,
latency percentiles, cache hit rate.

---

## Exercise 15: Deprecation Process (M)

Generate notices at promotion / 50% / deadline; auto-pin at the deadline; verify the
previous version resumes.

---

## Exercise 16: Prompt Optimizer (H)

Six mutation operators, hill-climbing with patience, held-out validation set, multi-seed
confirmation, tokens/correct reported.

---

## Exercise 17: Drift Detection on Prompt Performance (M)

Detect a quality drop with an unchanged prompt and model; attribute it to input drift
(intent mix, length).

---

## Exercise 18: Injection Canary (M)

8 attack fixtures against the registry renderer; verify detection and that untrusted
content is labelled data.

---

## Stretch A: Auto-Routing Between Prompt Families (M)

Route by intent/classifier; measure per-family accuracy and the routing error cost.

---

## Stretch B: Few-Shot Set Optimization (H)

Select demonstrations to maximize validation accuracy; report marginal contribution per
demo and the cost.

---

## Stretch C: Prompt Bundle Diff Impact (H)

Predict the quality impact of a bundle change from single-component evals; verify the
prediction against a combined run.

---

## Stretch D: Multi-Model Prompt Portability (H)

Run the same prompts against 3 model configurations; report which optimizations transfer
and which are model-specific.

---

## Stretch E: Linting (M)

Lint rules: section order, unfilled vars, banned phrases, missing schema, stale
version references. Wire into a build.

---

## Stretch F: Reverse Prompt Engineering (H)

Infer the prompt from input/output pairs; register the inferred prompt; verify whether
it reproduces observed behaviour.