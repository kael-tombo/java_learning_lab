# Lab 07: AI Testing & Evaluation — Real-World Project

## Project: Continuous Evaluation Platform

Design and build the evaluation system a production AI product runs on: golden suites
maintained from real traffic, CI gates, safety suites, sampled online scoring,
statistically sound experiments, and reporting that product teams trust.

## Context

Evaluation is the difference between shipping improvements and shipping noise. This
platform exists so that every change is measurable, every regression is caught before
users see it, and every claim about quality comes with an interval.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Holistic Evaluation of Language Models (HELM)" (Liang et al., submitted 16 Oct 2022;
  v7 Feb 2023) — https://arxiv.org/abs/2211.09110 — takeaway for this lab: reproducible,
  multi-scenario, multi-metric evaluation with published conditions is the defensible
  standard, which is why this platform keys every report to a scenario set, metric set,
  and manifest hash.
- "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (Zheng et al., submitted
  6 Jun 2023) — https://arxiv.org/abs/2306.05685 — takeaway for this lab: judge position,
  verbosity, and self-enhancement biases are measurable, which is why this platform
  randomizes order, tracks consistency, uses multiple judge families, and re-measures
  judge-human agreement before trusting any judge-derived metric.

## System Architecture

```
   PRODUCTION SIGNALS                     CURATED ASSETS
  +----------------------+              +--------------------------+
  | sampled queries      |              | golden set (frozen)     |
  | thumbs up/down       |              | unanswerable set        |
  | escalations          |              | safety red-team set     |
  | retries, abandon     |              | fairness cohort set     |
  +----------+-----------+              | latency/cost suite      |
             |                          +------------+-------------+
             |                                       |
             +------------------+--------------------+
                                v
                    +---------------------------+
                    |  Data Ops                 |
                    |  PII scrub | dedupe        |
                    |  stratify | version | hash |
                    +-------------+-------------+
                                  |
        +-------------------------+--------------------------+
        |                         |                          |
        v                         v                          v
  +-----------+            +---------------+         +---------------+
  | OFFLINE   |            | ONLINE SAMPLE |         | PERIODIC      |
  | CI gate   |            | 1-5% async    |         | AUDIT         |
  | per commit|            | cheap 100%    |         | fairness,     |
  | / merge   |            | judge on sample|        | safety, drift |
  +-----+-----+            +-------+-------+         +-------+-------+
        |                          |                         |
        +--------------------------+-------------------------+
                                   v
                      +------------------------+
                      |  Metric & Judge Layer  |
                      |  proxies (100%)         |
                      |  judges (sampled)       |
                      |  bias-corrected,        |
                      |  calibrated, versioned  |
                      +-----------+------------+
                                  |
                      +-----------v------------+
                      |  Statistics Layer      |
                      |  paired bootstrap, CIs |
                      |  multiple comparisons  |
                      +-----------+------------+
                                  |
              +-------------------+-------------------+
              |                                       |
      +-------v--------+                   +---------v---------+
      | RELEASE GATE    |                   | DASHBOARDS /     |
      | block regress-  |                   | EXPERIMENT REPORT|
      | ionals          |                   +-------------------+
      +-----------------+
```

## Component Specs

### 1. Data Ops
- **Sampling**: stratified by intent, language, tenant tier, session length, estimated
  difficulty. A fixed canary slice never rotates.
- **PII scrub** before any evaluation artifact is stored; raw user content never enters
  the benchmark repository.
- **Deduplication**: near-duplicate clustering; dedup rate reported (a high rate means
  the benchmark is smaller than it looks).
- **Versioning**: immutable dataset versions with content hashes; every report states the
  dataset hash.
- **Split discipline**: by user/session, never by query.

### 2. Golden Suites
- **Generic capability suite**: the standard scenarios used for every model comparison.
- **Product suites**: per product, owned by the product team, required for promotion.
- **Unanswerable subset**: >= 15% of every suite.
- **Safety suite**: disallowed, benign lookalikes, jailbreak families, refusal
  consistency.
- **Fairness suite**: per-group and intersectional cases.
- **Operational suite**: latency, throughput, cost, memory.
- Every incident adds a case. Every case carries provenance and label date.

### 3. Offline CI Gate
Tiers: fast (commit), full (merge), safety + production (release).

Blocking rules:
- Correctness regression beyond a stated tolerance **in any category**.
- Safety regression of any size — zero tolerance.
- Latency p95 or cost per request regression beyond budget.
- Golden-trace change requiring review.
- **Missing telemetry counts as a failure.**
Every block prints the per-category diff, never just an aggregate.

### 4. Online Sampled Evaluation
- 1-5% of traffic scored asynchronously, cost-bounded.
- 100% cheap signals: schema validity, refusal, length, PII, citation presence, tool
  errors.
- Judged sample: stratified random (headline metric) plus targeted strata (all errors,
  all escalations, all signal disagreements) for the fix queue. Never averaged together.
- Drift monitoring: intent mix, query length, language, retrieval top-score, refusal
  rate — compared against a reference window.

### 5. Judge Layer
- **Position correction**: both-order comparison; inconsistent pairs excluded and
  counted.
- **Verbosity control**: length-stratified win rates published.
- **Multiple families**: at least two judges; inter-judge agreement reported.
- **Calibration**: a human-labelled set re-scored monthly; judge metrics suspended below
  threshold; agreement reported as an attenuation factor on effect size.
- **Rubric versioning**: a rubric change invalidates historical comparisons and is noted.

### 6. Statistics
- Paired comparisons against the incumbent on identical items.
- Bootstrap CIs on every delta; multiple-comparison correction for sweeps, with the
  procedure named.
- Minimum sample sizes derived from the resolution required; ladder feasibility checked
  against actual traffic.
- "Within noise" is a first-class, publishable outcome.

### 7. Contamination and Integrity
- N-gram overlap detection between the benchmark and public training corpora.
- Canary items that must never be answered.
- Provenance for every item: source, labeler, date, rubric version.
- Eval-set drift detection: does the suite still represent traffic?

### 8. Reporting and Governance
- Dashboard: quality per intent, safety per category, latency, cost, drift,
  judge agreement, suite freshness.
- Experiment report template: hypothesis, dataset hash, config hashes, metrics with CIs,
  per-category diff, cost delta, decision, approver.
- Suite ownership: one team per suite; freshness reported.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Golden suite size | >= 1,000 items across top intents |
| Unanswerable fraction | >= 15% |
| CI full-suite runtime | < 30 min |
| Safety regression tolerance | 0 |
| Judge-human agreement | >= 0.80 |
| Position consistency | >= 95% |
| Online sample rate | 1-5%, within budget |
| Online score freshness | < 30 min |
| Offline block precision | Investigated blocks that were real > 80% |
| Suite freshness | Refreshed within 30 days |
| Experiment verdict turnaround | < 1 working day |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Suite unrepresentative | Intent-mix vs traffic comparison | Resample from traffic |
| Benchmark too small | CI width alert | Grow the set; prefer paired tests |
| Duplicate leakage | Dedup report | User-level splits |
| Contaminated benchmarks | N-gram overlap | Own the benchmark from traffic |
| Judge bias uncorrected | Consistency counter, length bands | Both-order comparison |
| Judge drift | Monthly agreement | Suspend judge metrics |
| Blocking on noise | CI includes zero | Warn-only on quality |
| Passing on noise | CIs too tight | Safety blocks; quality warns |
| Fairness hidden | Intersectional audit | Never report marginal parity alone |
| Refusal tuning breaks benign use | Over-refusal metric | Report both numbers |
| Stale suite | Suite freshness metric | Monthly refresh |
| Eval cost blowout | Cost per eval | Tiered suites; sampling |
| Rubric change breaks comparability | Rubric version in report | Version and note |
| Canary rubber-stamped | No gates | Automated gates, missing = breach |

## Milestones

- **M1** — Data Ops: sampling, scrub, dedupe, versioning, user-level splits.
- **M2** — generic and product golden suites with unanswerable subsets.
- **M3** — metrics and statistics layer with paired bootstrap and corrections.
- **M4** — CI gate with per-category diffs and exit codes.
- **M5** — judge layer with position correction and calibration.
- **M6** — online sampled evaluation with separated strata.
- **M7** — safety suite and red-team intake process.
- **M8** — fairness suite and intersectional auditing.
- **M9** — drift monitoring and eval-set freshness.
- **M10** — dashboards and the experiment report template.
- **M11** — game day: ship a regressed model; confirm the gate blocks.

## Deliverables

1. Evaluation platform with suites, runners, and gates.
2. Judge layer with calibration.
3. Online sampling and drift monitoring.
4. Safety and fairness suites.
5. `REPORT.md` — quality trend, safety trend, cost per evaluation, block precision.
6. `EVAL_SOPS.md` — how suites are built, refreshed, and gated.

## Definition of Done

- [ ] A deliberately regressed model is blocked with a per-category diff.
- [ ] A deliberately regressed safety category is blocked with zero tolerance.
- [ ] Judge-human agreement >= 0.80 published with an attenuation factor.
- [ ] Position consistency >= 95%.
- [ ] Unanswerable subset >= 15% with decline and false-decline tracked.
- [ ] Every experiment reports CIs and states "within noise" where true.
- [ ] Suite refreshed within 30 days of a drift alert.
- [ ] Eval cost per release within budget.