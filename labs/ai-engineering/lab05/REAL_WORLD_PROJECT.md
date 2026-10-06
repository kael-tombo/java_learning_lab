# Lab 05: Prompt Engineering at Scale — Real-World Project

## Project: Prompt Management and Experimentation Service

Design and build the organization-wide prompt platform: registry with governance,
templating, experimentation with statistical rigor, progressive rollout, per-version
observability, and the deprecation machinery that keeps a fleet of prompt families
manageable.

## Context

Organizations accumulate hundreds of prompts. Without a registry, every change is an
unreproducible incident; with one, prompt quality becomes measurable and improvement
becomes a process rather than a folklore.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Large Language Models are Few-Shot Learners" (Brown et al., submitted 28 May 2020;
  rev. 22 Sep 2021) — https://arxiv.org/abs/2005.14165 — takeaway for this lab:
  in-context demonstrations are the conditioning mechanism, so demonstration sets are
  versioned and evaluated as first-class assets here rather than embedded in template
  text.
- "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., submitted
  6 Jun 2023) — https://arxiv.org/abs/2306.05685 — takeaway for this lab: judge position
  and verbosity biases are documented and measurable, which is why this service uses
  paired blind comparison, randomizes order, tracks consistency, and re-measures
  judge-human agreement before trusting any prompt comparison.

## System Architecture

```
   PRODUCT TEAMS
        |
   +----v----------------------------------------------------------------+
   |  PROMPT SERVICE (render, validate, budget, cache)                   |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  PROMPT REGISTRY                                                    |
   |  families: system | tasks/* | guardrails/* | fewshot/* | output/*   |
   |  versions immutable | hash | owner | risk tier | bundle version    |
   |  lifecycle: draft -> evaluated -> canary -> active -> deprecated    |
   |  promotion gate | rollback (1 call) | deprecation + auto-pin      |
   +----+----------------------------------------------------------------+
        |
   +----v-------------------+     +------------------------+   +------+
   |  LINTER + BUILD GATE   |     |  EXPERIMENTATION       |   |  MESH |
   |  order, unfilled,      |     |  stable bucketing      |   |  DRIFT|
   |  banned, schema, owner |     |  paired runner         |   |  ------|
   +---------+--------------+     |  bootstrap CI          |   |  input|
             |                    |  per-category diff     |   |  dist |
   +---------v--------------+     |  power correction      |   +--+---+
   |  ROLLOUT ENGINE        |     +----------+-------------+      |
   |  shadow | 1/5/25/100   |<----------------+-------------------+
   |  auto gates | auto rollback                                     |
   +---------+--------------+                                            |
             |                                                          |
   +---------v----------------------------------------------------------v-+
   |  EVALUATION + OBSERVABILITY                                          |
   |  per version: accuracy | format validity | refusal | tokens/correct  |
   |  cost/correct | latency | cache hit | rollback | drift             |
   |  dashboards | alerts | audit trail                                       |
   +------------------------------------------------------------------------+
```

## Component Specs

### 1. Registry and Governance
- Immutable versions with content hash and spec hash (template + variable schema).
- **Owner and risk tier required**; orphaned prompts auto-deprecated.
- Families versioned in **bundles** so partial updates cannot create drift.
- Promotion requires a passing gate appropriate to the risk tier:
  - low: unit checks plus a spot check
  - medium: full offline suite
  - high: full suite + safety suite + named human reviewer
- Rollback is one config call and invalidates the render cache.
- Every response carries the prompt id, version, and bundle hash.

### 2. Templating and Budget
- Typed variables (`STRING(n)`, `ENUM`, `INT`, `BOOL`) validated at render time.
- `assertNoUnfilled`: a literal placeholder reaching the model is an error, not output.
- Canonical section order enforced; stable prefix verified by a test on every render.
- Token budgeting with truncation order: context first, never schema or question.
- Render cache keyed by `sha256(id + version + rendered)`; hit rate monitored.

### 3. Linting and the Build Gate
- Rules: section order, unfilled placeholders, banned phrases, missing output schema for
  high risk, missing owner, stale bundle references, over-long templates.
- CI fails on errors; warnings require an acknowledgement.
- Unversioned prompt text in application code is blocked at build time — this is what
  stops prompt sprawl from reappearing.

### 4. Experimentation
- Stable user bucketing salted per experiment; users see one variant per session.
- **Paired** evaluation on identical items; one bootstrap over deltas.
- Wilson intervals for rate metrics.
- Per-category diffs; a collapse in one intent must be visible.
- Multi-variant comparisons use Holm or BH correction, and the report states which.
- Shadow evaluation as the default path for low-volume products.
- Judge-human agreement re-measured monthly; judge metrics suspended below threshold.

### 5. Rollout Engine
- Ladder 1 / 5 / 25 / 100 with per-step minimum sample sizes derived from the target
  resolution.
- Gates: accuracy (per category), format validity, refusal rate, p95 latency,
  cost/correct, cache hit rate.
- **Missing metric counts as a breach.**
- Automatic rollback; the previous version is already warm, so no rebuild.
- Canary dwell times published so teams can plan their promotion schedule.

### 6. Deprecation
- Notices at promotion, at 50% traffic, and at the deadline.
- Migration tracker: which consumers still reference a deprecated version.
- Auto-pin at the deadline plus a compatibility shim; every auto-pin is audited.
- Grace periods per risk tier (longer for high risk).

### 7. Observability
- Per version: accuracy, format validity, refusal rate, tokens/correct,
  cost/correct, latency percentiles, cache hit rate, repair rate.
- Rollback and canary-breach rates per prompt family.
- Drift: quality drop with no version change implies input drift; alert separately.
- Every prompt usage recorded with id, version, and bundle hash.
- Alerts: format validity drop, refusal spike, cost/correct rising, cache hit collapse,
  version with no recent eval, deprecated version still receiving traffic.

### 8. Adoption
- Self-service: teams register prompts, run the gate, and promote to shadow without a
  platform bottleneck.
- Opinionated defaults (a recommended template family) so the common case is the safe
  one.
- Documentation and examples kept current; office hours.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Prompts with an owner | 100% |
| Prompts passing the linter | 100% of registered prompts |
| Unfilled placeholders in production | 0 |
| Rollback time | < 60 s |
| Time to promote (gated, small change) | < 1 business day |
| Experiments reporting paired CIs | 100% |
| Judge-human agreement | >= 0.80 |
| Accuracy regression shipped | 0 (gate blocks) |
| Deprecated versions still in traffic at deadline | 0 |
| Render cache hit rate | > 70% on templated routes |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Prompt tweak ships ungated | Build gate | Unversioned prompt text blocked |
| Cache always missing | Prefix hit rate | Layout lint |
| Experiment inconclusive | CI width | Paired design; larger n |
| Optimizer overfits | Test delta divergence | Held-out set; multi-seed |
| High-risk prompt skipped safety | Gate audit | Risk-tier enforcement in the API |
| Rollback slow | Rollback time metric | Config flip with warm prior |
| Family drift | Bundle consistency check | Atomic bundle versioning |
| Judge drift | Monthly agreement | Suspend judge metrics |
| Volume teams route around | Adoption metrics | Fast path; self-service |
| Auto-pin surprises a caller | Migration tracker | Notices + grace periods |
| Nobody updates a prompt | Stale-version metric | Owner dashboard |
| Multi-variant false positives | Correction recorded | Holm / BH correction |

## Milestones

- **M1** — registry with hashing, ownership, risk tiers, gated promotion, rollback.
- **M2** — templating with typed variables and budget enforcement.
- **M3** — families and bundle versioning.
- **M4** — linter plus build gate; unversioned prompt text blocked.
- **M5** — experimentation service with paired statistics and corrections.
- **M6** — rollout engine with shadow, canary, auto rollback.
- **M7** — deprecation with migration tracker and auto-pin.
- **M8** — observability dashboards and alerts.
- **M9** — self-service onboarding; first 10 teams registered.
- **M10** — game day: break prefix stability and verify the alert fires.

## Deliverables

1. Prompt registry, templating, linting, and build gate.
2. Experimentation and rollout services.
3. Deprecation machinery.
4. Dashboards and alerts.
5. `REPORT.md` — adoption, promotion throughput, rollback rate, quality over time,
   cost per correct over time.
6. `PROMPT_STYLE.md` — conventions enforced by the linter.

## Definition of Done

- [ ] 100% of production prompts registered with an owner and risk tier.
- [ ] Unfilled placeholders impossible (render-time assertion).
- [ ] A failing gate blocks promotion; verified by a deliberate regression.
- [ ] Rollback under 60 seconds.
- [ ] Every experiment reports paired CIs with a stated correction procedure.
- [ ] Deprecated versions receive no traffic at the deadline (auto-pin verified).
- [ ] Cache hit collapse detected within one alert window of a deliberate break.
- [ ] 10 teams onboarded without platform intervention.