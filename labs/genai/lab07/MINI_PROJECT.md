# Lab 07: RLHF & Preference Optimization — Mini Project

## Project: Preference Optimization Pipeline on a Tiny Language Model

Build the whole three-stage stack in Java 21: an SFT stage on demonstrations, a
reward model trained on synthetic preference pairs, and a policy optimization stage
implementing both PPO (on a toy discrete policy) and DPO (on the LM), with a full
metric harness that can *detect reward hacking*.

## Goal

A runnable pipeline that produces a policy, plots the reward-vs-quality
over-optimization curve, demonstrates the length bias, and shows DPO as the
memory-light alternative to PPO.

## Requirements

### Phase 1: Toy Environment
- [ ] Discrete policy over 16 tokens, context vector of dimension 8.
- [ ] "Prompts" as random context vectors; "responses" as length-3 token sequences.
- [ ] `trueQuality(prompt, response)` — an unrewarded, hand-written ground-truth
      function (e.g. requires specific token combos at specific positions).
- [ ] `proxyReward(prompt, response)` — a deliberately hackable function rewarding
      verbosity and keyword density.

### Phase 2: SFT Stage
- [ ] Generate demonstrations from a near-optimal policy on the toy task.
- [ ] Implement masked cross-entropy and train the SFT policy.
- [ ] Record SFT loss curve; assert it plateaus below the uniform baseline.

### Phase 3: Reward Model
- [ ] Feature extractor (length, keyword density, position match, distinct-2).
- [ ] Linear + hidden-layer reward models; Bradley-Terry loss with `softplus`.
- [ ] Train on 2,000 synthetic pairs; report held-out pair accuracy.
- [ ] Print learned weights to expose the length bias.
- [ ] Length-penalty sweep producing a Pareto plot.

### Phase 4: PPO Stage
- [ ] GAE with configurable `gamma`, `lambda`; advantage normalization.
- [ ] Clipped surrogate with gradient cases covered.
- [ ] Value head trained on returns.
- [ ] KL as per-token reward; adaptive `beta` controller.
- [ ] Train for 300 steps; log reward, KL, mean length every 10 steps.
- [ ] **Stop rule**: stop at `kl_budget`, not at reward plateau.

### Phase 5: DPO Stage
- [ ] `DpoLoss` with stable sigmoid; `LogRatioStore` precomputation.
- [ ] Train a small LM policy (reuse Lab 02) with DPO on the same preference data.
- [ ] Extract implicit rewards and verify Bradley-Terry consistency.
- [ ] Memory comparison table: PPO (4 models) vs DPO (2).

### Phase 6: Detection and Analysis
- [ ] `OverfitCurve` producing reward, unrewarded quality, mean length,
      distinct-2, KL per checkpoint.
- [ ] Identify the over-optimization crossover point programmatically.
- [ ] Side-by-side sample dumps at 4 checkpoints showing the degradation.
- [ ] Report the best checkpoint by unrewarded quality and confirm it is *not*
      the best by reward.

### Phase 7: Alternatives
- [ ] ORPO (reference-free) and SimPO (length-normalized) losses.
- [ ] Best-of-N selection with the reward model, compared at equal token cost.
- [ ] Pair quality analyzer: agreement, length ratio, base win rate, duplicates.

## Directory Layout

```
lab07/
  src/com/genai/lab07/{env,sft,rm,ppo,dpo,eval,data}/
  out/curves/reward_vs_quality.csv
  out/curves/length_pareto.csv
  out/samples/step_0000.txt, step_0050.txt, ...
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — toy env with separate `trueQuality` and `proxyReward`; sanity-check both.
2. **M2** — SFT converges; loss curve plateau verified.
3. **M3** — reward model trained; held-out accuracy reported; weights inspected
      for the length bias.
4. **M4** — GAE and PPO unit tests (limit cases verified analytically).
5. **M5** — PPO run produces a reward curve and a KL curve; KL stop rule fires.
6. **M6** — reward hacking demonstrated; crossover point located.
7. **M7** — DPO training on the LM; implicit rewards verified.
8. **M8** — ORPO/SimPO comparisons; best-of-N comparison at equal cost.
9. **M9** — `REPORT.md` written with all curves and the "ship which checkpoint" argument.

## Acceptance Criteria

- [ ] `L_RM` equals `ln 2` with gradients `+/-0.5` at zero reward difference.
- [ ] GAE matches `V(s_t)` for `gamma=1, lambda=1` and `delta_t` for `lambda=0`.
- [ ] PPO gradient is exactly zero for `ratio=1.3, A=+1, eps=0.2`.
- [ ] Reward hacking demonstrated with at least 3 concrete symptoms.
- [ ] The reward-best checkpoint differs from the quality-best checkpoint.
- [ ] Implicit rewards from DPO reproduce observed preference probabilities.
- [ ] Length-penalty sweep produces a non-monotone accuracy-vs-length curve.

## Stretch Goals

- [ ] Iterative RLHF: 3 rounds of policy -> new pairs -> RM refresh.
- [ ] RLHF on the LM itself (not just the toy policy) and compare to DPO output.
- [ ] Reward model ensemble (3 disjoint splits) and the accuracy gain.
- [ ] Constitution-style critique/revise with 3 written principles.
- [ ] KTO-style binary-feedback training when no pairs exist.
- [ ] Judge calibration: judge vs ground truth on the toy task.
- [ ] Unlearning via preference; measure recall drop and collateral capability.
- [ ] Prompt-level reward shaping and its effect on the hacking surface.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| RM accuracy stuck at 0.5 | Learning rate too low, or features carry no signal |
| RM weight on length dominates | Length bias in the data; add length penalty |
| PPO loss NaN | `exp` overflow; use `softplus`/`clamp` |
| PPO makes no progress | Advantage not normalized, or clip too tight |
| KL explodes | `beta` too low; controller not wired |
| DPO loss flat at `ln 2` | Reference log-ratios equal policy log-ratios (ref not frozen) |
| DPO improves reward, drops quality | Same hacking curve; you need the unrewarded metric |
| Quality best == reward best | Reward is not hackable in your toy setup — make it so |

## Definition of Done

`REPORT.md` contains: the pipeline diagram, the reward/quality crossover plot with
the marked optimum, length Pareto frontier, PPO vs DPO memory and quality table,
five sample generations at four checkpoints, and an explicit statement of which
checkpoint you would ship and which metric justified it.