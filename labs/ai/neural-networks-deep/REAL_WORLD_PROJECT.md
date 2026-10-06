# neural-networks-deep — Real-World Project

## Project: An In-Process Recommendation Ranker with a Latency Budget

Build a production recommendation ranker: a neural network scoring candidate items per
request, a training pipeline with point-in-time correctness, an exported artifact the
serving process loads without any ML runtime, a compression pipeline to hit a memory
budget, an online evaluation harness, and the drift and fairness monitoring that keeps it
honest.

## Context

A ranker is one of the few neural networks genuinely in the critical request path. It has a
hard latency budget, a memory ceiling, an offline metric that is easy to game, and a
feedback loop that can quietly degrade itself. This project builds all of it.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Deep Neural Networks for YouTube Recommendations" (Covington et al., submitted
  6 Sep 2016) — https://arxiv.org/abs/1606.07792 — takeaway for this lab: candidate
  generation and ranking are separate stages with separate budgets, and the ranking stage
  scores a few hundred candidates per request under a fixed serving cost; that split is
  the architecture here, and the watch-time-plus-satisfaction objective rather than click
  rate is the lesson that pure proxies get gamed.
- "Systematic Optimization of the DNN Training Pipeline" (Hugging Face learning course) —
  https://huggingface.co/learn — takeaway for this lab: production training is a pipeline
  of measurable stages with instrumentation between them, and the practical emphasis on
  reproducible seeds, pinned configs, and profiling before optimizing is what separates a
  training pipeline that can be debugged from one that cannot.

## System Architecture

```
  offline                                online
  -------                                ------
  event log --> feature store ---------->  feature fetch (point-in-time correct)
      |                                       |
  point-in-time join                     candidate generator (top 400)
      |                                       |
  training set                      +--------v---------+
      |                              | RANKER (in-process)   |
  train/validate by TIME           |  MLP + user/item towers |
      |                              |  int8 / fp16 artifact   |
  calibration, threshold           +--------+---------+
      |                                       |
  export artifact                     rank, apply diversity,
  (weights + schema + version)        log impressions
                                              |
  monitoring: metric drift,               +----v-----+
  feature drift, slice metrics,          decision log
  impression-coverage check                     |
  drift response ladder                        v
                                        feedback labels
```

## Component Specs

### 1. Candidate Generation and Ranking Split
- A cheap first stage (embeddings plus a dot product) reduces the catalogue to a few
  hundred candidates; the expensive network scores only those.
- Both stages have separate latency budgets and separate monitoring. The ranker's budget
  is a hard p99 target, not a guideline.
- Impression logging records **every candidate scored**, not only the served one. Without
  that, the training set cannot correct for the position and exposure bias the system
  itself created.

### 2. Feature Store With Point-In-Time Correctness
- Every feature carries an `as_of` timestamp; joins reject rows computed after the
  prediction time.
- Shared feature computation between training and serving — one implementation, no
  reimplementation in the serving path.
- A `fit`/`transform` discipline where any statistic (mean, quantile, embedding table
  update) is computed on a training window only.
- Schema versioned with the artifact; a mismatch fails the load rather than silently
  defaulting.

### 3. Model Architecture
- Two-tower structure (user tower, item tower) with a shared interaction layer, so item
  embeddings can be precomputed and cached — the single biggest serving lever.
- Residual MLP trunk with pre-normalization; width and depth chosen against the latency
  budget, not in isolation.
- Output: a sigmoid probability, calibrated. Ranking does not need probability, but
  thresholded business rules and exploration do.
- Auxiliary heads: a next-category prediction task and a short-horizon engagement head,
  which regularize the trunk.

### 4. Training Pipeline
- Time-based splits, always. A random split leaks the future into a trending catalogue and
  produces a model that looks excellent offline.
- Loss: a sampled softmax over in-batch negatives plus a pointwise binary term, so the
  training objective resembles the ranking task rather than raw next-click probability.
- Sampled negatives must be corrected for the sampling distribution; ignoring this is the
  most common silent bug in this exact setup.
- Gradient clipping by global norm; learning rate from a range test, not a guess.
- Checkpoint every epoch with the config, the seed, and the data-window hash, so any run
  is resumable and attributable.

### 5. Offline Evaluation
- Ranking metrics: NDCG@k, MAP, MRR, recall@k — and the metric chosen must match the
  business objective. NDCG for graded relevance, MRR for a single relevant item.
- Segment the report: cold-start users, cold-start items, high-frequency users, long-tail
  items, and every monitored group. A headline number hides exactly the failures that
  matter.
- Counterfactual checks where possible: does the model's ordering of items the user never
  saw match editorial or business priorities?
- Calibration as a separate gate from ranking quality.
- **Guard against the proxy metric**: any objective correlated with the business metric can
  be gamed. Track a guardrail metric (session satisfaction, return rate, hide rate) and
  alert on it independently.

### 6. Artifact Export and In-Process Scoring
- Export: weights, architecture config, feature schema version, vocabulary, generation
  config, and a manifest hash. No Python or framework at serving time.
- Loader validates the hash and the schema version; a mismatch refuses to load.
- INT8 per-channel quantization as the default, with FP16 as the fallback; quantization
  chosen against the offline metric, not assumed lossless.
- The scoring path is allocation-light: preallocated buffers, no per-request object
  churn in the inner loop.
- Latency measured in the serving process, with a per-stage breakdown (feature fetch,
  tower forward, interaction, scoring, logging).

### 7. Compression Under a Budget
- Start from the trained FP32 model; prune, then quantize, then distill only if the budget
  still misses.
- Each step measured on the task metric and on latency — never on parameter count alone.
- If distillation is used, the teacher is the current production model and the student
  inherits its full logit distribution at temperature 2-4.
- Budget enforcement is a build failure: exceeding the memory or latency budget fails the
  pipeline rather than producing an artifact nobody can serve.

### 8. Online Evaluation and Guardrails
- Interleaving or a small randomized holdout for unbiased online measurement; a
  before/after comparison on different populations is not evidence.
- Exposure and coverage monitoring: how many distinct items get impressions, how many
  users see only head content.
- Latency and error budgets monitored per release with automatic rollback on breach.
- Guardrail metrics with hard thresholds: hide rate, report rate, session abandonment,
  diversity collapse.
- Every release carries the artifact hash into the impression log, so any metric movement
  is attributable.

### 9. Drift and Feedback Monitoring
- Feature drift on inputs and embeddings; score distribution drift against a frozen
  baseline.
- Embedding drift measured as a distribution distance on a periodic sample.
- **Feedback-loop detection**: compare the distribution of the training data against the
  distribution of items the *new* model surfaces. A model that only learns from its own
  output narrows the catalogue; this must be detected, not noticed later.
- Cold-start coverage metrics: what fraction of recommendations are for items with fewer
  than N impressions.
- Drift response ladder: investigate the feature pipeline first, then the exposure
  distribution, then retrain. Retraining last, because most drift is a pipeline bug.

### 10. Fairness and Exposure Governance
- Slice metrics for exposure, click, and engagement per monitored group.
- Exposure parity is the primary fairness metric for a ranker: whether an item's chance of
  being shown depends on whose feed it is in.
- A publisher-side check: small and new publishers' share of impressions, tracked so the
  objective cannot quietly starve the long tail.
- Changes to the objective or the ranking constraints reviewed as a code change with an
  approval record.
- Model card, approval trail, and a deprecation ladder for the artifact format.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Ranker latency p99 | < 25 ms in-process, measured in the serving process |
| Candidate stage latency p99 | < 5 ms |
| End-to-end p99 | < 60 ms |
| Memory per replica | Under the stated budget; enforced at build time |
| NDCG@10 | >= published baseline, with a stated improvement |
| MRR@10 | Reported alongside, not instead of NDCG |
| Calibration ECE | <= 0.02 |
| Cold-start item exposure share | Not below the published floor |
| Publisher concentration (top-1 share) | < stated threshold |
| Guardrail: hide rate | No increase beyond the agreed delta |
| Guardrail: abandonment | No increase beyond the agreed delta |
| Latency breach | Automatic rollback |
| Artifact hash in every impression | 100% |
| Point-in-time correctness | Enforced; a violating join fails the build |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Random split on trending data | Offline score far above online | Time-based splits only |
| Feature computed after prediction time | Point-in-time test | `as_of` enforced in the store |
| Sampled negatives not corrected | Model over-ranks popular items | LogQ correction or full softmax |
| Ranker exceeds latency budget | p99 monitor | Precompute item embeddings; prune; quantize; build gate |
| Quantization collapses quality | Offline metric drop | Per-channel scales; QAT fallback; ship FP16 |
| Model starves the long tail | Exposure share monitor | Publisher-side constraint in the objective |
| Training data drifts from served data | Distribution comparison | Exposure-coverage monitoring; drift ladder |
| Feedback loop narrows the catalogue | Item-impression diversity metric | Exploration budget; popularity-debiasing |
| Only served items logged | Coverage of impressions | Log every scored candidate |
| Latency regression reaches users | p99 alert + auto-rollback | Canary with a latency gate |
| Proxy metric gamed | Guardrail metric alert | Independent guardrail thresholds |
| Serving feature skew | Shadow feature comparison | Shared implementation |
| Cold-start quality collapses | Slice metric drop | Cold-start towers and priors |
| Framework version drift | Pinned environment hash | Container pinning; artifact manifest |
| Missing telemetry | Instrumentation check | Blocks release |
| Memory budget exceeded in prod | Build-time enforcement | Fail the pipeline, do not ship |

## Milestones

- **M1** — event log, point-in-time feature store, temporal splits.
- **M2** — candidate generation stage with its own budget and monitoring.
- **M3** — two-tower ranker trained with sampled softmax and logQ correction.
- **M4** — calibration and a threshold for downstream business rules.
- **M5** — offline evaluation suite with NDCG, MRR, recall, and slice segmentation.
- **M6** — artifact export with a manifest hash and a strict loader.
- **M7** — in-process serving with per-stage latency instrumentation.
- **M8** — compression pipeline under an enforced memory and latency budget.
- **M9** — online interleaving harness with unbiased measurement.
- **M10** — guardrail metrics with hard thresholds.
- **M11** — drift monitoring including feedback-loop detection.
- **M12** — fairness and exposure governance with publisher-side checks.
- **M13** — model card, approval trail, deprecation ladder.

## Deliverables

1. Training pipeline with time-based splits and point-in-time-correct features.
2. Two-stage recommendation system: candidate generation plus an in-process neural ranker.
3. Exported artifact with manifest hash, schema validation, and a strict loader.
4. Compression pipeline with per-step accuracy and latency attribution.
5. Offline and online evaluation with slice segmentation and guardrail metrics.
6. Drift, exposure, and fairness monitoring.
7. `REPORT.md` — the platform posture: ranking metrics overall and per slice, calibration,
   latency at every stage, compression attribution, exposure and concentration, drift
   sensitivity, and residual risks accepted with reasons.

## Definition of Done

- [ ] Point-in-time correctness test fails when a feature timestamp is after the prediction
      time.
- [ ] Every scored candidate appears in the impression log with the artifact hash.
- [ ] Offline report includes NDCG@10, MRR@10, and recall@k with slice segmentation.
- [ ] Sampled-softmax training with logQ correction beats an uncorrected baseline.
- [ ] ECE at or below 0.02.
- [ ] Ranker p99 under 25 ms measured in the serving process, with a per-stage breakdown.
- [ ] Compression stays within the memory budget and reports per-step accuracy deltas.
- [ ] Latency breach triggers automatic rollback, verified by a deliberate regression.
- [ ] Long-tail exposure share not below the floor after the release.
- [ ] Feedback-loop metric computed and monitored, with an exploration budget.
- [ ] Guardrail metric regression blocks promotion.
- [ ] Artifact loader refuses a schema or hash mismatch.
- [ ] Model card, approval trail, and deprecation ladder complete.
