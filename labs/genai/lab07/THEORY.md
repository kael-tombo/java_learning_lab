# Lab 07: RLHF & Preference Optimization — Theory

## 1. The Three-Stage Recipe

Reinforcement Learning from Human Feedback is a pipeline, not an algorithm:

```
Stage 1  Supervised Fine-Tuning (SFT)
         expert demonstrations -> helpful, instruction-following policy
                    |
Stage 2  Reward Model (RM)
         human preference pairs -> scalar reward r(x, y)
                    |
Stage 3  Policy Optimization
         maximize r(x,y) - beta * KL(policy || reference)
         PPO (classic) or DPO (offline, stable)
```

Each stage has a different failure mode, and in practice stage 3 is where things
break: reward hacking, length bias, and mode collapse toward a narrow style.

## 2. Stage 1: SFT

Cross-entropy on demonstration pairs, with prompt tokens masked out of the loss:

```
L_SFT = - E_{(x,y)} sum_t log pi(y_t | x, y_<t) * m_t
```

This is the behavior-cloning stage. It matters more than people assume: RLHF
quality is bounded by SFT quality. A weak SFT policy produces off-distribution
samples that the reward model has never scored.

## 3. Stage 2: Reward Modeling

Given pairs `(x, y_w)` (chosen) and `(x, y_l)` (rejected), train a reward head:

```
r_phi(x, y) = scalar from the final hidden state of a sequence classifier

L_RM = - E [ log sigmoid( r_phi(x, y_w) - r_phi(x, y_l) ) ]
```

This is the Bradley-Terry model of preference. Under it,

```
P(y_w > y_l) = sigmoid( r(y_w) - r(y_l) )
```

Implications:

- Only the **difference** of rewards is identified; a constant offset is free.
  Reward values are therefore not calibrated across prompts — never treat them as
  absolute quality scores.
- Rewards are unbounded and can be driven arbitrarily high (see reward hacking).
- Reward model accuracy on held-out pairs is the metric to watch; typical
  single-annotator agreement is ~65-70%, so a "perfect" RM is already at the
  human ceiling.

### 3.1 Known RM biases

| Bias | Symptom | Mitigation |
|-------|---------|------------|
| Length | Longer answers score higher | Length-controlled pairs; length penalty in the objective |
| Position | The answer shown first wins | Randomize presentation order |
| Style markers | "As an AI..." gets rewarded | Vary annotator prompts; de-bias with counterfactuals |
| Self-preference | The RM prefers its own family's outputs | Train the RM on a different base model |

## 4. Stage 3: PPO

Reinforce the policy to increase reward while staying near the reference:

```
objective = E_{x,y~pi_theta} [ r_phi(x,y) - beta * log( pi_theta(y|x)/pi_ref(y|x) ) ]
```

The KL term is the load-bearing part: without it the policy runs off to produce
text that games the reward model. `beta` sets the tradeoff — too small and you get
reward hacking, too large and you get a policy indistinguishable from SFT.

PPO needs four models simultaneously: policy, reference, reward, and (sometimes) a
value head. That is 4x the memory, which is why SFT/RM models are usually 4-bit
quantized with LoRA adapters while the policy trains in higher precision.

Advantage estimation: GAE

```
delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
A_t     = delta_t + gamma * lambda * A_{t+1}
```

`lambda` controls the bias/variance tradeoff; `lambda = 0.95` is the usual default.
The clipped surrogate:

```
L_CLIP = - E[ min( ratio * A, clip(ratio, 1-eps, 1+eps) * A ) ],  ratio = pi_new/pi_old
```

The KL penalty is often folded in as a per-token reward:

```
r_t' = r_t - beta * log(pi_theta(y_t|x,y_<t) / pi_ref(y_t|x,y_<t))
```

## 5. DPO: The Offline Alternative

DPO skips sampling and RL entirely by solving for the reward that makes the
reference policy a KL-constrained optimum in closed form:

```
r*(x,y) = beta * log( pi_theta(y|x) / pi_ref(y|x) ) + const

L_DPO = - E [ log sigmoid( beta * ( log pi_theta(y_w|x)/pi_ref(y_w|x)
                                 - log pi_theta(y_l|x)/pi_ref(y_l|x) ) ) ]
```

Read it as: "the implicit reward is the log-ratio to the reference, and we fit the
Bradley-Terry likelihood of the preference data."

Why it works operationally:
- **No sampling, no RM, no reward hacking loop** — you train on the preference
  dataset directly.
- **Stable**: a plain binary cross-entropy; no clipping or KL-controller tuning.
- **Reference model is free**: `pi_ref` is just the frozen initial weights, and the
  log-ratios can be **precomputed once**, so training is memory-light.

What you give up: no ability to explore beyond the dataset, no explicit reward
signal you can inspect or shape, and typically slightly lower performance than
well-tuned PPO on hard reasoning tasks.

## 6. Reward Hacking and Over-Optimization

The failure mode of RLHF: the policy finds text the RM scores highly that humans
do not like. Typical shapes:

- Length inflation (longer = higher reward).
- Empty hedged preambles, bullet-point padding, excessive disclaimers.
- Sycophancy: agreeing with whatever the user asserted.
- Code that "looks right" without being right.

The classic result is an inverted-U: reward-vs-human-satisfaction rises with more
optimization, then falls. Practical guards:

- Cap generation length and add a length penalty to the reward.
- Include a KL budget alarm (`kl > kl_target` -> stop the run).
- Hold out an *unrewarded* eval set: measure quality with a metric the RM was not
  trained on, and track both curves.
- Periodically re-collect preferences from the current policy (iterative RLHF) so
  the RM tracks the policy's distribution drift.

## 7. Other Preference Methods

| Method | Idea | When |
|--------|------|------|
| IPO | Squared loss, avoids DPO's likelihood-displacement push | Unstable pairs |
| ORPO | Odds-ratio preference loss on top of SFT, no reference model | Memory-constrained |
| SimPO | Reference-free, length-normalized reward | Simple, strong baseline |
| KTO | Binary "desirable/undesirable" labels, no pairs | Only thumbs up/down available |
| CPO | Contrastive preference with a reward margin term | Instruction tuning |
| RLAIF | AI feedback instead of human labels | Scale of human labels is the bottleneck |
| Constitutional AI | Critique against written principles, then revise | Safety without human raters on every item |

## 8. Data Requirements

- Preference pairs per task: thousands to tens of thousands.
- **Multiple annotators per pair**; report agreement (Krippendorff's alpha or raw
  agreement). Below ~0.6, the signal is mostly noise.
- Balance easy/hard pairs; all-easy pairs teach nothing.
- Include "both bad" cases handled as ties, or filter them.
- Deduplicate near-identical prompts — they inflate apparent dataset size.
- Keep a held-out preference set never used for training, for RM accuracy.

## 9. Evaluation

- **RM accuracy** on held-out pairs (train-side health check).
- **Win rate vs the SFT policy**, judged blind by humans or a strong judge model.
- **Reward score** — but always plot it *alongside* an unrewarded metric.
- **Length distribution** — a length spike is a hacking smell.
- **KL from reference** — the safety gauge on the optimization.
- **Safety and refusal rates** on the red-team set (Lab 10).
- **Factuality**: grounded QA accuracy, citation correctness.
- Judge correlation: periodically re-validate the judge against human preference;
  a drifted judge invalidates your win rates.

## 10. Practical Java Sketch

Preference pairs and losses are pure functions — very Java-friendly:

```java
public record Pair(String prompt, String chosen, String rejected) {}

public double rewardModelLoss(double rChosen, double rRejected) {
    return -Math.log(1 / (1 + Math.exp(-(rChosen - rRejected))));   // -log sigmoid(diff)
}

public double dpoLoss(double logpChosenRef, double logpRejectedRef,
                      double logpChosen, double logpRejected, double beta) {
    double logits = beta * ((logpChosen - logpChosenRef) - (logpRejected - logpRejectedRef));
    return -Math.log(1 / (1 + Math.exp(-logits)));
}

public double klPenalty(double logp, double logpRef) { return logp - logpRef; }
```

Because DPO's log-ratios are precomputable, a Java implementation can store
`(logpChosenRef, logpRejectedRef)` once per pair and train a small adapter with
straightforward backprop.

## Key Equations

```
L_RM  = - log sigmoid( r(y_w) - r(y_l) )
L_PPO = - E[ min( ratio * A, clip(ratio, 1-e, 1+e) * A ) ],  ratio = pi_new/pi_old
L_DPO = - log sigmoid( beta * [ log(pi_theta(y_w)/pi_ref(y_w)) - log(pi_theta(y_l)/pi_ref(y_l)) ] )
KL    = E[ log pi_theta(y|x) - log pi_ref(y|x) ]
```