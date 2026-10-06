# Lab 05: Prompt Engineering at Scale — Mini Project

## Project: Prompt Registry with Gated Rollout and Paired Evaluation

Build a prompt management system in Java 21 — registry with immutable versions and
gated promotion, typed rendering, linting, experiment assignment, paired statistical
evaluation, canary rollout with auto rollback, and a per-version metrics dashboard.

## Goal

A system where no prompt can reach production without passing a gate, every experiment
reports an honest confidence interval, and rollback takes one call.

## Requirements

### Phase 1: Registry
- [ ] Immutable versions with content hash and spec hash.
- [ ] Owner and risk tier required; orphans auto-deprecated.
- [ ] `promote` gated (failing gate throws; missing metrics throw).
- [ ] `rollback` one call; render cache invalidated.
- [ ] Deprecation notices at promotion, 50%, deadline; auto-pin at deadline.

### Phase 2: Rendering
- [ ] Typed variables: STRING(n), ENUM, INT, BOOL.
- [ ] `assertNoUnfilled` and `assertTypes` at render time.
- [ ] Canonical section order enforced; prefix stability test.
- [ ] Render cache keyed by `sha256(id + version + rendered)`.

### Phase 3: Prompt Families
- [ ] Families: system, task, guardrail, fewshot, output.
- [ ] Bundle versioning; a partial update is rejected.
- [ ] Drift detector: mismatched bundle versions across families.

### Phase 4: Linting
- [ ] Rules: section order, unfilled vars, banned phrases, missing schema for
      high risk, no owner.
- [ ] Wire into a build; fix violations until clean.

### Phase 5: Experiments
- [ ] Stable user bucketing salted per experiment.
- [ ] Paired runner on identical items; one bootstrap over deltas.
- [ ] Wilson intervals for rates.
- [ ] Verify a fake improvement is reported as within noise.
- [ ] Per-category diffs with regression flags.

### Phase 6: Rollout
- [ ] Canary ladder 1/5/25/100 with gates.
- [ ] Automatic rollback on breach; missing metric is a breach.
- [ ] Shadow evaluation for low-traffic builds.
- [ ] Sample-size calculator and ladder-time estimator.

### Phase 7: Metrics
- [ ] Per version: accuracy, format validity, refusal, tokens/correct,
      cost/correct, latency percentiles, cache hit rate.
- [ ] Comparison view against a baseline with per-category deltas.
- [ ] Drift alert: quality drop with no version change.

### Phase 8: Optimizer
- [ ] Six mutation operators; hill-climb with patience.
- [ ] Held-out validation; confirm on a test set.
- [ ] Multi-seed confirmation; report val delta vs test delta.

## Directory Layout

```
lab05/
  src/com/aiengineering/lab05/{registry,template,lint,experiment,stats,rollout,metrics,optimizer}/
  prompts/*.md          prompt families
  suite/items.jsonl     eval suite
  out/experiments/
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — registry with hashing; immutability enforced.
2. **M2** — typed rendering; 6 validation tests green.
3. **M3** — gated promotion; a failing gate throws.
4. **M4** — families and bundles; partial update rejected.
5. **M5** — linter clean on all registered prompts.
6. **M6** — paired runner; fake improvement reported as noise.
7. **M7** — canary ladder; degraded candidate rolled back at 1%.
8. **M8** — shadow evaluation path.
9. **M9** — metrics dashboard with cost/correct.
10. **M10** — optimizer; val vs test delta divergence demonstrated.
11. **M11** — deprecation process exercised on one family.
12. **M12** — report written.

## Acceptance Criteria

- [ ] Versions immutable; owner and risk tier required.
- [ ] Missing gate metrics block promotion.
- [ ] Rollback completes in one call; cache invalidated.
- [ ] Prefix stability test passes across 100 renders.
- [ ] Paired CI excludes zero for a real effect and includes zero for a fake one.
- [ ] Per-category collapse localized, not averaged away.
- [ ] Canary rolls back a degraded candidate automatically.
- [ ] Multi-variant comparison reports its correction procedure.
- [ ] Optimizer test delta reported alongside val delta.
- [ ] Deprecation auto-pin tested.

## Stretch Goals

- [ ] Few-shot demonstration set optimizer with marginal-value reporting.
- [ ] Multi-model portability study: which optimizations transfer.
- [ ] Bundle-change impact prediction.
- [ ] Auto-routing between prompt families by intent.
- [ ] Reverse prompt engineering from I/O pairs.
- [ ] Prompt lint rules for performance (schema adjacency, length budgets).
- [ ] Migration tracker: consumers on deprecated versions.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Cache always missing | Volatile content in the prefix |
| Literal `{{var}}` in a prompt | Missing render assertion |
| Experiment inconclusive | Independent resampling in the bootstrap |
| Rollback slow | Re-render instead of a config call |
| Optimizer gains vanish | Tuned on the test set |
| Family drift | Partial bundle update |
| High-risk prompt promoted | Gate does not require the safety suite |
| Metrics missing at promote | Fail-open instead of fail-closed |
| Accuracy up, cost worse | Only accuracy reported |

## Definition of Done

`REPORT.md` contains: the lifecycle diagram, the registry design, the render validation
tests, the lint report, the family bundle model, one worked experiment with the paired CI
and per-category diff, the canary ladder results including an automatic rollback, the
shadow evaluation path, the metrics dashboard with cost/correct for every version, the
optimizer trajectory with val vs test deltas, the deprecation record, and a "which
metric do we gate on and why" conclusion.