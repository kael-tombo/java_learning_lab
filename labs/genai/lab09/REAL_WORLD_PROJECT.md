# Lab 09: LLM Evaluation & Benchmarks — Real-World Project

## Project: Production Evaluation Platform for an LLM Product

Design and build the evaluation system a product team runs continuously: a
traffic-derived benchmark, offline gates in CI, online quality monitoring, judge
calibration, safety tracking, fairness auditing, and experiment reporting with
statistical discipline.

## Context

Shipping LLM features without an evaluation platform means shipping on vibes. This
system makes every change measurable, every regression detectable before users see
it, and every "the model is better now" claim statistically defensible.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Holistic Evaluation of Language Models (HELM)" (Liang et al., submitted 16 Oct
  2022; v7 Feb 2023) — https://arxiv.org/abs/2211.09110 — takeaway for this lab:
  evaluation across many scenarios and metrics simultaneously, rather than a single
  number, is the standard this platform implements; the multi-metric scenario matrix
  and transparent reporting shape the report structure here.
- "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., submitted
  6 Jun 2023) — https://arxiv.org/abs/2306.05685 — takeaway for this lab: judge
  position, verbosity, and self-enhancement biases are documented and measurable,
  which is why this platform randomizes order, tracks consistency, and re-measures
  judge-human agreement before trusting any judge-derived metric.

## System Architecture

```
   PRODUCTION SIGNALS                     CURATED EVAL ASSETS
  +----------------------+             +------------------------+
  | sampled user queries |             | golden set (labeled)   |
  | thumbs up/down       |             | unanswerable set       |
  | escalation tickets   |             | safety red-team set    |
  | retries / abandons   |             | fairness cohort set    |
  +----------+-----------+             +-----------+------------+
             |                                     |
             +------------------+------------------+
                                v
                    +-----------------------+
                    |  Data Ops             |
                    |  PII scrub, dedupe    |
                    |  stratify by intent   |
                    |  difficulty estimate  |
                    |  version + hash       |
                    +-----------+-----------+
                                |
     +--------------------------+--------------------------+
     |                          |                          |
     v                          v                          v
+----------+            +----------------+          +------------------+
| OFFLINE  |            | ONLINE         |          | PERIODIC AUDIT  |
| eval in  |            | monitoring     |          | fairness, bias,  |
| CI       |            | (sampled)      |          | safety, drift    |
+----------+            +----------------+          +------------------+
     |                          |                          |
     +------------+-------------+-------------+------------+
                               v
                   +------------------------+
                   | Metric & Judge Layer   |
                   |  overlap metrics       |
                   |  faithfulness / abstain|
                   |  bias-corrected judge  |
                   |  safety classifiers    |
                   |  fairness metrics      |
                   +-----------+------------+
                               |
                    +----------v-----------+
                    |  Statistics Layer    |
                    |  paired bootstrap    |
                    |  CIs, multiple comps |
                    +----------+-----------+
                               |
              +----------------+-----------------+
              |                                 |
      +-------v--------+              +---------v---------+
      | Release Gate    |              | Dashboards /      |
      | block on regress|              | Experiment Report |
      +-----------------+              +-------------------+
```

## Component Specs

### 1. Data Ops
- **Sampling**: stratified by intent, language, tenant tier, session length, and
  estimated difficulty. Include a fixed "canary" slice that never rotates.
- **PII scrub**: names, emails, phone numbers, account numbers, addresses removed
  before any evaluation artifact is stored. Raw user content never enters the
  benchmark repo.
- **Deduplication**: near-duplicate queries clustered by embedding similarity; keep
  the representative. Report the dedup rate — a high rate means your benchmark is
  smaller than it looks.
- **Versioning**: every dataset gets an immutable version and content hash;
  evaluation reports state the dataset hash so results are reproducible.
- **Split discipline**: splits by user/session, never by query.

### 2. Offline Evaluation (CI gate)
Run on every model, prompt, retrieval, or configuration change:

```
correctness:    exact match / task accuracy per intent
faithfulness:   per-claim support rate; abstention coverage & accuracy
quality:        bias-corrected win rate vs the production baseline
safety:         refusal, over-refusal, jailbreak success, toxicity
retrieval:      recall@k, nDCG@k, citation validity (Lab 04 metrics)
operational:    p50/p95 latency, tokens, cost per request
```

Gate policy (configurable, explicit):
- Block on correctness regression beyond a stated tolerance **in any category**.
- Block on safety regression of any size (no tolerance).
- Block on latency or cost regression beyond budget.
- Warn (do not block) on quality win-rate deltas whose CI includes zero.
- Every block prints the per-category diff, not just the aggregate.

### 3. Online Monitoring
- Sample 1-5% of production traffic into the evaluation queue (configurable by cost).
- Score asynchronously; results lag minutes, not hours.
- Track quality proxies available at scale: thumbs up/down, regeneration rate, copy
  rate, escalation rate, session abandonment, and "user asked again" rate.
- Watch **input drift**: intent mix, query length distribution, language mix,
  retrieval-hit-rate distribution, refusal rate. A shift in any of these is an early
  signal that the model is out of distribution.
- Alert on: refusal rate spike, error rate spike, cost per request spike, cache hit
  collapse, latency p95 breach.

### 4. Judge Layer
- **Position correction**: both-order comparison; inconsistent pairs counted and
  excluded from the win rate (with the count published).
- **Verbosity control**: length-stratified evaluation; report win rate per length
  band to expose verbosity bias.
- **Cross-family judges**: at least two judges from different model families;
  aggregate and report inter-judge agreement.
- **Calibration**: 100-item human-labeled calibration set re-scored monthly.
  Publish judge-human agreement; suspend judge-derived metrics below threshold.
- **Rubric versioning**: rubric changes are versioned; a rubric change invalidates
  historical comparisons and must be noted in the report.

### 5. Faithfulness and Hallucination
- Per-claim support against retrieved context (intrinsic) plus NLI where
  contradictions matter.
- **Unanswerable subset**: the highest-value items. Track decline rate and
  false-decline rate separately.
- Extrinsic hallucination proxy: self-consistency agreement rate across samples,
  sampled on a small fraction of traffic.
- Alert when the hallucination rate for a top intent doubles.

### 6. Safety Evaluation
- Red-team suite versioned and expanded after every incident.
- Four numbers always together: refusal rate, over-refusal rate, jailbreak success
  rate, refusal consistency (same ask paraphrased).
- Toxicity on generations: classifier distribution plus periodic human review of the
  worst decile.
- New-attack intake process: any user-reported jailbreak becomes a permanent test
  case within one business day.

### 7. Fairness and Bias Audit
- Per-group metrics for every model that generates user-facing content.
- Demographic parity, equal opportunity, and bias ratio per task; report the
  conflict when parity and opportunity disagree rather than picking the convenient one.
- Intersectional tables; marginal parity is never reported alone.
- Bias in generation measured with attribute classifiers; report the classifier's
  own accuracy so a weak classifier is visible.
- Quarterly audit published to an independent reviewer.

### 8. Statistics and Reporting
- Paired comparisons against the incumbent on identical items.
- Bootstrap 95% CIs on every delta; multiple-comparison correction when comparing
  several variants.
- Experiment report template: hypothesis, dataset hash, config hashes, metrics with
  CIs, per-category diff, cost delta, decision, and who approved.
- Verdicts of the form "within noise" are a first-class outcome. Writing them takes
  discipline and saves everyone from shipping noise.

### 9. Contamination and Integrity
- n-gram overlap detection between the benchmark and public training corpora.
- Prompt-injection canary items that must never be answered.
- Provenance for every evaluation item: source, labeler, label date, rubric version.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Benchmark size | >= 1,000 labeled items across top intents |
| Unanswerable items | >= 15% of the suite |
| Online sampling | 1-5% of traffic, cost within budget |
| Judge-human agreement | >= 0.80, re-measured monthly |
| Position consistency | >= 95% of pairs order-consistent |
| Offline gate runtime | < 30 min in CI |
| Report turnaround | Experiment verdict within 1 working day |
| Safety regression | 0 tolerance |
| P95 latency | no regression beyond 5% |
| Cost per request | no regression beyond 5% |
| Online metric freshness | < 30 min |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Benchmark too small for small deltas | CI width alert | Grow the set; prefer paired tests |
| Benchmark unrepresentative | Intent-mix vs traffic comparison | Resample from traffic each quarter |
| Near-duplicate leakage | Dedup report; prompt paraphrase check | Split by user/session |
| Judge bias uncorrected | Consistency counter, length-band table | Both-order comparison, stratification |
| Judge drift | Monthly human-labeled agreement | Suspend judge metrics below threshold |
| Rubric change breaks comparability | Rubric version in report | Version and note invalidations |
| Blocking on noise | CI includes zero | Policy: block only outside the CI |
| Passing on noise | CIs too tight | Warn-only on quality; block only on safety |
| Fairness hidden by marginals | Intersectional audit | Never report marginal parity alone |
| Refusal tuning breaks benign use | Over-refusal metric | Report refusal and over-refusal as a pair |
| Online score lags reality | Freshness SLO | Async pipeline with freshness alert |
| Contaminated public benchmarks | n-gram overlap detector | Own benchmark from traffic |
| New jailbreak not tested | Intake process | Permanent test case within one business day |

## Milestones

- **M1** — Data Ops: sampling, PII scrub, dedupe, versioning.
- **M2** — metrics + statistics layer with paired bootstrap.
- **M3** — offline CI gate with per-category diff and exit codes.
- **M4** — judge layer with position correction, stratification, calibration.
- **M5** — faithfulness, abstention, and unanswerable subset.
- **M6** — safety suite with the four-number report and intake process.
- **M7** — online monitoring with drift and cost alerts.
- **M8** — fairness audit incl. intersectional tables.
- **M9** — experiment report template + dashboard.
- **M10** — game day: ship a deliberately regressed model and confirm the gate blocks.

## Deliverables

1. Data Ops tooling and benchmark versioning.
2. Evaluation runner, metrics layer, statistics layer.
3. Judge layer with calibration harness.
4. Safety suite and red-team intake process.
5. Fairness audit report.
6. `REPORT_TEMPLATE.md` and the first three experiment reports.
7. `runbook.md` — what to do when each alert fires.

## Definition of Done

- [ ] A deliberately regressed model is blocked by the CI gate with a per-category diff.
- [ ] Judge-human agreement >= 0.80 measured and published.
- [ ] Position consistency >= 95%.
- [ ] Unanswerable subset >= 15%; decline and false-decline both tracked.
- [ ] Safety regression blocks release with zero tolerance.
- [ ] Every experiment report contains CIs and states "within noise" where true.
- [ ] Fairness audit reviewed by someone outside the team.