# Lab 14: LLMOps (LLM Operations) — Real-World Project

## Project: Production LLMOps Platform for an AI Product

Design and build the operational platform a production AI product runs on: release
management over the whole config bundle, automated evaluation gates, progressive
delivery, online quality and drift monitoring, cost attribution and governance,
incident response with tested runbooks, and feedback loops that keep the eval suite
representative.

## Context

This is the system that decides whether the AI product is trustworthy at 3am. Its
scope is larger than most teams first estimate, because the artifact is a bundle of
five versions and every one of them can cause an incident.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Holistic Evaluation of Language Models (HELM)" (Liang et al., submitted 16 Oct 2022;
  v7 Feb 2023) — https://arxiv.org/abs/2211.09110 — takeaway for this lab: transparent,
  multi-scenario, multi-metric evaluation with reproducible conditions is the standard
  for claims about model quality, which is why this platform treats evaluation
  configuration (scenarios, metrics, judge version) as part of the release manifest
  rather than a separate concern.
- "The Llama 3 Herd of Models" (Dubey et al., submitted 25 Apr 2024; v2 23 Jul 2024) —
  https://arxiv.org/abs/2407.21783 — takeaway for this lab: a production model release
  documents evaluation methodology, safety evaluation, and deployment practice as
  first-class content, which is the reporting and gating structure reproduced here.

## System Architecture

```
  +---------------------------------------------------------------------+
  |  RELEASE CONTROL                                                    |
  |  ReleaseManifest {model, prompt, index, tools, policy, gen config,   |
  |                   evaluator}  -> manifestHash -> pinned/rollback     |
  +---------------+-----------------------------------------+-----------+
                  |                                         |
   +--------------v---------------+           +-------------v-----------+
   |  CI EVALUATION GATE          |           |  PROGRESSIVE DELIVERY  |
   |  offline suite (Lab 09)      |           |  shadow | canary ladder|
   |  safety suite                |           |  auto-gated | rollback  |
   |  cost/latency budgets        |           +-------------+-----------+
   +--------------+---------------+                         |
                  |                                         v
   +--------------v-----------------------------------------v-----------+
   |  PRODUCTION RUNTIME                                                 |
   |  gateway | routing | batching | guardrails (Lab 10) | tools (L5) |
   +--------------+-----------------------------------------+-----------+
                  |
   +--------------v-----------+   +--------------------+   +------------+
   |  TELEMETRY               |   |  ONLINE EVAL        |   |  DRIFT     |
   |  latency | cost | errors |   |  100% cheap signals|   |  PSI on    |
   |  retry ratio | queue     |   |  sampled judging   |   |  inputs    |
   +--------------+-----------+   +----------+---------+   +----+-------+
                  |                      |                    |
                  +----------+-----------+--------------------+
                             |
                +------------v-------------+
                |  DECISION LAYER         |
                |  dashboards | alerts   |
                |  error budget | freeze  |
                +------------+-------------+
                             |
   +-------------------------v---------------------------+
   |  INCIDENT RESPONSE                                    |
   |  runbooks | safe mode | containment | game days      |
   +-------------------------+---------------------------+
                             |
   +-------------------------v---------------------------+
   |  FEEDBACK                                               |
   |  user signals -> review queue -> labels -> eval suite  |
   +---------------------------------------------------------+
```

## Component Specs

### 1. Release Management
- `ReleaseManifest` covering model, prompt template, retrieval index, tool registry,
  safety policy, generation config, and evaluator config. Hash covers all of them.
- Manifest hash in every response header and every trace.
- Registry with promote/rollback/pin/deprecate; never overwrite a published version.
- Release notes auto-generated: metric deltas (all Lab 09 metrics), cost impact,
  safety impact, known differences.
- **Every config change is a release**: prompt edits, index rebuilds, guardrail
  threshold changes, tool schema changes. No unversioned tweaks.
- Change freeze during incidents, enforced by the deploy pipeline.

### 2. Evaluation Gate (CI)
Blocking checks on every change:
- Task correctness per intent within budget, with a minimum sample size computed from
  the target resolution.
- Faithfulness, citation validity, abstention coverage/accuracy.
- Safety suite: refusal and over-refusal, jailbreak success, leakage (zero tolerance).
- Latency p95, throughput, cost per request within budget.
- Regression suite: golden traces; any change to a golden tool sequence requires review.
- Missing telemetry counts as a failure, not a pass.

### 3. Progressive Delivery
- Shadow mode available for every release: 100% mirrored, not served.
- Canary ladder 1/10/50/100 with per-step gates and minimum samples.
- Assignment by stable user hash, salted per experiment.
- Automatic rollback on breach; rollback is a config flip.
- Feature flags with independent kill switches for capability-level rollback
  (retrieval off, tools off, model pinned).
- Long dwell at 1% for low-traffic products; shadow eval to build sample size.

### 4. Online Quality Monitoring
- Tier 1 cheap signals on 100%: schema validity, refusal, length, PII, citation
  presence, tool-error count.
- Tier 2 judging on a stratified random sample (headline metric) plus targeted
  samples (all errors, all escalations, all signal disagreements) for the fix queue.
- Judge version in the manifest; judge-human agreement re-measured monthly; judge
  metrics suspended below threshold.
- Quality alerts with the manifest diff as the first investigation step.

### 5. Drift Monitoring
- PSI on intent mix, prompt length, language, retrieval top-score distribution,
  refusal rate.
- Compare rolling window to reference window; quantile bins.
- Drift alert triggers investigation and eval-set review, not automatic rollback.
- Separate alert for eval-set drift (does the suite still represent traffic?).
- Error budget on quality and safety metrics, with burn-rate freeze.

### 6. Cost Governance
- Cost per request by tenant, feature, route, model version, cache status.
- Cost per successful outcome as the north-star metric.
- Reconciliation against the provider invoice monthly; discrepancy above 2% alerts.
- Per-tenant and per-feature budgets with alerts at 50/80/100% and a trajectory
  forecast (not just the fact).
- Denial-of-wallet protection: per-user caps, anomalous volume alerts.
- Monthly unit-economics report reviewed with finance.

### 7. Incident Response
- Alert classes: latency, errors, quality, safety/refusal, cost, drift, injection.
- Each alert has: an owner, a first question, a decision tree, tested containment.
- Containment menu: safe mode, disable a tool, disable retrieval, pin the previous
  manifest, shed load, roll back.
- Safe mode: strict policy, tools off, retrieval off, previous manifest pinned,
  graceful degradation (still answers).
- Game days quarterly; measure time-to-detect and time-to-contain every time.
- Post-incident review within a week; the eval suite gains a case before closure.

### 8. Feedback Loop
- Ingest: thumbs, regenerate, copy, abandon, escalate, implicit corrections, support
  tickets.
- Review queue prioritized by user value x severity x recency.
- Labeling uses the Lab 09 schema (category, unanswerable flag, allowed sources).
- Monthly eval-set refresh; freshness of the suite reported.
- Sampled production traces scored offline continuously; failures enter the suite.

### 9. Operational Practice
- Runbook quality scored mechanically; gaps tracked as work items.
- Toil analysis each quarter; automation candidates prioritized.
- Deploy (mechanical) separated from release (a decision with an owner).
- Every release has a named owner who is accountable for the first 24 hours.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Release manifest coverage | 100% of production responses |
| Canary promotion accuracy | 0 bad releases reach 100% |
| Rollback time | < 5 min, config only |
| Safety regressions shipped | 0 |
| Quality gate sample size | Resolves the stated delta |
| Drift alert precision | Investigated alerts that were real > 70% |
| Time to detect (drill) | < 15 min |
| Time to contain (drill) | < 60 min |
| Meter vs invoice | < 2% discrepancy |
| Cost per successful outcome | Tracked and improving |
| Budget overrun | 0 (alerts at 80%) |
| Eval suite freshness | Refreshed monthly |
| Runbook quality | 100% of entries scored 100 |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Prompt tweak ships unversioned | Manifest audit | CI blocks unversioned config changes |
| Bad release reaches 100% | Canary gates | Auto rollback; missing metric = breach |
| Quality incident misdiagnosed | Manifest diff | Diff first; index/prompt ranked highest |
| Blind rollback hides cause | Change log | Freeze and investigate; pin for comparison |
| Slow rollback | Rollback time metric | Config flip with warm prior pool |
| Judge drift invalidates metrics | Monthly agreement | Suspend judge metrics below threshold |
| Drift alert fatigue | Alert precision metric | Drift triggers investigation, not rollback |
| Cost spike unnoticed | Cost per request alert | Same urgency as latency |
| Retry storm | attempts/requests metric | Three-condition detector |
| Cache hit collapse | Hit-rate alert | Treat as a deployment bug signal |
| Eval set stale | Eval-set drift metric | Monthly refresh from traffic |
| Budget overrun | Forecast alert | Alert at 80% and on trajectory |
| Silent safety regression | Safety suite in CI | Zero-tolerance block |
| Incident with no owner | Runbook scoring | Owner is a scored field |
| Blast radius too large | Feature flags | Independent kill switches |

## Milestones

- **M1** — release manifest, registry, hash in every response and trace.
- **M2** — CI evaluation gate with budget-based sample sizes.
- **M3** — progressive delivery: shadow, canary ladder, auto rollback.
- **M4** — online quality monitoring with separated samples.
- **M5** — drift monitoring and error budgets.
- **M6** — cost governance with reconciliation and budgets.
- **M7** — incident runbooks with owners, trees, and tested containment.
- **M8** — feedback loop: signals to queue to labels to eval suite.
- **M9** — runbook scoring and toil analysis.
- **M10** — first game day; measure time-to-detect and time-to-contain.
- **M11** — monthly unit-economics report with finance.

## Deliverables

1. Release management and gating pipeline.
2. Progressive delivery controller.
3. Online quality and drift monitoring with dashboards.
4. Cost attribution and budget enforcement.
5. Incident runbooks plus drill reports.
6. `REPORT.md` — release cadence, quality over time, cost trajectory, incident history.
7. `RUNBOOK.md` — per-alert decision trees, owned and tested.
8. `EVAL_SOPS.md` — how the eval suite is built, refreshed, and gated.

## Definition of Done

- [ ] Every production response carries a manifest hash; 100% coverage verified.
- [ ] Zero bad releases reach 100% traffic in the drill period.
- [ ] Rollback completes in under 5 minutes with no rebuild.
- [ ] A deliberate quality regression is blocked by the CI gate.
- [ ] A deliberate safety regression is blocked with zero tolerance.
- [ ] Time-to-detect and time-to-contain measured in a game day and documented.
- [ ] Meter reconciles with invoices within 2%.
- [ ] Eval suite refreshed from traffic within the last 30 days.
- [ ] All runbook entries scored 100 with executed containment actions.