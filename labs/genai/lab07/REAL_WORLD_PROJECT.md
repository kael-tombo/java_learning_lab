# Lab 07: RLHF & Preference Optimization — Real-World Project

## Project: Production Preference Optimization Pipeline

Build the system a real team uses to take a model from a base checkpoint to a
deployed, preference-optimized model: preference data operations, reward modeling,
policy optimization with safety constraints, offline + online evaluation, and a
deployment gate that blocks regressions.

## Context

Preference optimization is where model quality is won and where quality is lost.
The engineering burden is in the surroundings: assembling trustworthy preference
data, detecting reward hacking automatically, coordinating four models on limited
GPUs, and proving to stakeholders that the new model is better on the metrics that
matter rather than on the reward that was optimized.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
  (Rafailov et al., submitted 30 May 2023; v4 7 Feb 2024) —
  https://arxiv.org/abs/2305.18290 — takeaway for this lab: the closed-form implicit
  reward `beta*log(pi_theta/pi_ref)` removes the need for an explicit reward model and
  online sampling, which is why DPO is the default offline stage in this pipeline and
  why reference log-ratios are precomputed once per pair.
- "Constitutional AI: Harmlessness from AI Feedback" (Bai et al., submitted 1 Dec 2022;
  rev. 21 Dec 2024) — https://arxiv.org/abs/2212.08073 — takeaway for this lab: a
  written set of principles plus AI-generated critique and revision can replace human
  preference labels on safety items, which is what makes the safety-preference dataset
  in this pipeline producible at scale — and why the constitution itself is versioned
  and gated like any other prompt asset.

## System Architecture

```
   preference sources                       labelling
  +-------------------+                +-------------------+
  | product feedback  |                | human raters      |
  | support tickets   |--------------->| AI judge (RLAIF)  |
  | expert demos      |                | constitution rules |
  | synthetic tasks   |                +---------+---------+
  +-------------------+                          |
                                                v
                                   +------------------------+
                                   | Preference Data Ops     |
                                   | dedupe, length-balance |
                                   | order randomization    |
                                   | agreement filtering    |
                                   | split train/held-out   |
                                   +-----------+------------+
                                               |
   base checkpoint                          v
   +---------------+              +------------------------+
   |  pi_sft       |------------->|  Stage 1: SFT           |
   | (frozen ref)  |              |  pi_ref := pi_sft        |
   +---------------+              +-----------+------------+
                                               |
                              +----------------+----------------+
                              |                                 |
                              v                                 v
                   +--------------------+          +------------------------+
                   | Stage 2: Reward    |          | Stage 2': DPO        |
                   | model (pairwise)   |          | (offline, no RM)     |
                   | + length control   |          +-----------+------------+
                   +---------+----------+                      |
                             |                                 v
                             |                    +----------------------------+
                             |                    | Stage 3: PPO / iterative  |
                             |                    | KL-budgeted, gated        |
                             +--------->----------+  reward hacking detector  |
                                                  |  safety constraints       |
                                                  +-------------+--------------+
                                                                |
                                       +------------------------+------------------------+
                                       |                                                 |
                              +--------v---------+                              +--------v---------+
                              | Offline eval     |                              | Online / canary |
                              | win rate, safety,|                              | traffic, monitor|
                              | factuality, KL  |                              | reward + quality|
                              +--------+---------+                              +--------+--------+
                                       |                                                 |
                                       +------------------------+------------------------+
                                                                v
                                                   +-----------------------------+
                                                   | Deployment gate (promote?)  |
                                                   | quality AND safety AND cost |
                                                   +-------------+---------------+
                                                                 |
                                                        +--------v--------+
                                                        |  Model registry|
                                                        |  + rollback    |
                                                        +-----------------+
```

## Component Specs

### 1. Preference Data Ops
- Every pair records: source, annotator id, rubric version, order presented,
  agreement flags, `contentHash`, timestamps.
- **Deduplicate** near-identical prompts (embedding cosine > 0.95) — inflated
  dataset size is a silent quality problem.
- **Length balance**: sample so `chosenLenRatio` distribution centers near 1.0;
  otherwise the RM learns length.
- **Order randomization** enforced at labelling time; verified post-hoc by checking
  that the position of the chosen answer is ~50%.
- **Agreement gates**: drop items below per-task agreement thresholds; quarantine
  tasks below 0.6 agreement entirely.
- **Hard-pair mining**: oversample pairs the base policy finds ambiguous.
- Splits by **prompt**, never by pair — the same prompt in train and test leaks.

### 2. Reward Model Service
- Trained on the preference set; served for evaluation and for PPO rollouts.
- **Bias audits** on held-out slices: length-only, position-only, style-marker-only
  synthetic probes. Report the accuracy of each probe; a length probe above 70% means
  the RM is a length detector.
- Calibration: report reward distribution percentiles per task so drift is visible.
- Ensemble option: 3 disjoint splits averaged, for the final gating run.

### 3. Policy Optimization
- PPO with the reference, reward, and value models quantized; the policy trains with
  LoRA so optimizer state stays small.
- **KL budget is the stop rule**, not reward plateau. `KL > kl_budget` halts the run
  and quarantines the checkpoint.
- Length penalty active from step 0, with `lambda` set from the length-Pareto sweep.
- Safety constraints enforced during optimization (blocklist rewards, refusal
  margin), not only post-hoc.
- Checkpoints every N steps with the full metric snapshot attached, so the best
  checkpoint can be chosen by the *right* metric later.

### 4. Reward Hacking Detector (automated, blocking)
Per checkpoint, compute and store:
```
proxyReward, unrewardedQuality, meanLength, distinct2, KLfromRef,
refusalRate, factualityScore, canaryRecall
```
Gate rules:
- `unrewardedQuality` must not drop more than the agreed delta from SFT.
- `meanLength` growth above the agreed threshold (e.g. +25%) -> flag for review.
- `distinct2` drop below threshold -> mode collapse flag.
- `KLfromRef` over budget -> automatic stop.
- Rising reward with falling unrewarded quality across 3 consecutive evals ->
  hacking alert, run quarantined.

### 5. Evaluation
- **Offline**: win rate vs the current production model, blind pairwise, judged by
  validated humans and by a judge model. Judge-human agreement re-measured monthly;
  below threshold, the judge is suspended.
- **Safety**: red-team suite refusal/forbidden-content rates.
- **Factuality**: grounded QA accuracy and citation correctness.
- **General capability**: fixed probe suite with delta tracking.
- **Cost**: tokens and dollars per task, before and after.
- **Latency**: p50/p95 for the shipped artifact.

### 6. Deployment and Rollback
- Model registry with versions, metrics, and artifact hashes.
- Canary at 1% -> 10% -> 50% -> 100% with automated metric gates at each step.
- Automatic rollback if quality or safety metric breaches the gate.
- Shadow mode for scoring before serving responses.

### 7. Observability
- Dashboard: reward, unrewarded quality, length, KL, refusal rate over steps and
  over production time.
- Alerting: KL budget, hacking heuristic, judge-human agreement, canary metric breach.
- Cost dashboard per optimization run (GPU hours) tied to quality delta.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| RM held-out pair accuracy | >= 0.75 and >= human ceiling - 3 pts |
| Length-probe accuracy | <= 0.60 (RM is not just a length detector) |
| Annotator agreement per task | >= 0.65 |
| Win rate vs production | >= 0.55 blind pairwise |
| Safety regression | <= 0 pts on the red-team suite |
| General capability delta | >= -1 pt on probes |
| KL at ship time | <= kl_budget |
| Mean length growth | <= +15% vs SFT |
| Rollback time | < 5 min |
| Pipeline cost | recorded per run, tied to quality delta |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Reward hacking | Hacking heuristic across checkpoints | KL stop, length gate, unrewarded metric |
| Length bias learned | Length-only probe accuracy | Length-balanced data + reward-side penalty |
| Position bias learned | Position-only probe accuracy | Randomize order; verify 50/50 after labeling |
| Data leakage | Prompt-hash overlap check between splits | Split by prompt |
| Judge drift | Periodic judge-vs-human agreement | Suspend judge below threshold |
| Safety regression | Red-team suite in gate | Hard gate, no exceptions |
| Capability regression | Probe suite delta | Gate with agreed tolerance |
| KL budget exceeded | Per-step KL metric | Automatic stop and quarantine |
| Mode collapse | Distinct-2 threshold | Flag; consider diversity term in reward |
| Canary failure | Automated stage gates | Auto-rollback |
| Labeling bottleneck | Throughput and cost metrics | RLAIF + constitution for safety items |
| Cost overrun | Per-run GPU hours | Early stop when quality plateaus AND KL budget used |

## Milestones

- **M1** — preference data ops with dedupe, length balance, order verification.
- **M2** — reward model with bias probes published as a metric.
- **M3** — SFT stage producing the frozen reference.
- **M4** — DPO stage (offline) with precomputed reference log-ratios.
- **M5** — PPO stage with KL budget stop and checkpoint metric snapshots.
- **M6** — automated hacking detector wired into the pipeline.
- **M7** — full evaluation suite (win rate, safety, factuality, probes, cost).
- **M8** — registry, canary gates, automated rollback.
- **M9** — game day: inject a deliberately hacked checkpoint and verify quarantine.

## Deliverables

1. Data ops tooling and the labeling rubric with agreement reporting.
2. Reward model training with bias-probe suite.
3. DPO and PPO optimization workers with KL budget enforcement.
4. Hacking detector with the metric snapshot schema.
5. `REPORT.md` — quality/cost table per optimization run, with the shipped
   checkpoint chosen by the right metric.
6. `runbook.md` — quarantine triage, rollback, judge recalibration.

## Definition of Done

- [ ] A deliberately hacked checkpoint is automatically quarantined in the game day.
- [ ] Length-probe accuracy <= 0.60 on the shipped reward model.
- [ ] Win rate >= 0.55 vs production with safety regression of 0 points.
- [ ] Every published model is reproducible from its data version + spec.
- [ ] Canary rollback completes in under 5 minutes.
- [ ] Judge-human agreement measured and above threshold at ship time.