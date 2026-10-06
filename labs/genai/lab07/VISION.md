# Lab 07: RLHF & Preference Optimization — Vision

## The Three-Stage Pipeline

```
STAGE 1: SFT (behavior cloning)
  expert demos (x, y*)
        |
        v
  pi_sft: cross-entropy, prompt tokens MASKED
        |
        v
  pi_sft  =  pi_ref   (the frozen reference policy IS the SFT policy)
        |
        v
STAGE 2: Reward Model
  pairs (x, y_w) (x, y_l)
        |
        v
  L = -log sigmoid( r(y_w) - r(y_l) )
        |
        v
  reward head r(x,y)  [separate model, often quantized]
        |
        v
STAGE 3: Policy Optimization
  sample y ~ pi_theta        <-- the ONLY stage that samples
        |
        +--> r(x,y)  --> GAE advantages A_t (needs a value head)
        +--> KL penalty per token: -beta*(log pi_theta - log pi_ref)
        |
        v
  PPO clipped update  (or DPO: offline, no sampling)
```

## DPO vs PPO — The Structural Difference

```
PPO (online)                          DPO (offline)
  preference pairs (x, y_w, y_l)        preference pairs (x, y_w, y_l)
        |                                      |
        |  SAMPLES FROM THE POLICY            |  precompute log pi_ref(y_w), log pi_ref(y_l)
        v                                      v
  r(x,y)  [reward model]                 u = beta*[ (log pi_theta(y_w) - logp_ref_w)
        |                                        - (log pi_theta(y_l) - logp_ref_l) ]
        v                                      |
  A_t via GAE [value head]                        v
        |                               L = -log sigmoid(u)
  ratio = pi_new/pi_old                          |
        |                                         v
  min(ratio*A, clip(ratio)*A)              gradient on logp only
        |                                    NO sampling
  4 models in memory                       NO reward model
  NO sampling, NO reward model,
  reward model CAN be inspected/tuned      reference log-ratios computed ONCE
```

## Reward Hacking Visual

```
training step ->

  reward (RM score)     ^
       |                |                    ********
       |                |              ******
       |                |         ******
       |                |     ****
       |                |  ***
       |                | *
       |                +----------------------------> steps
       |
       |  human satisfaction / true quality
       |         \                            ......
       |          \                     .....
       |           \              .....
       |            \        ....
       |             \   ...
       |              \.
       +------------------------------------------------> steps

  THE OPTIMUM IS THE VERTICAL LINE, NOT THE PEAK OF REWARD.

  what the policy learns past the line:
    +---------------------------------------------+
    | "Certainly! Here is a comprehensive,        |
    |  detailed answer that thoroughly addresses   |
    |  every aspect of your question, while        |
    |  noting that as an AI I should clarify..."   |
    +---------------------------------------------+
      verbose  * hedged  * redundant * disclaimer-padded
      (all of these raise RM score, none raise human score)
```

## Length Bias Mechanism

```
correlation between chosen and rejected length in the dataset
   rho = +0.4  (chosen answers tend to be longer)

   RM fit:
     r_hat = w_len * len + w_rest * content
     w_len absorbs the length preference from the annotators
     (they *thought* they preferred quality)

   at inference: policy learns
     "longer -> higher r -> sampled more"

   visible symptom:
     mean output tokens: 180 (SFT) -> 410 (RLHF)
     win rate vs human:  flat or down

   fix:  r' = r - lambda * sqrt(tokens)      lambda chosen by sweep
         held-out pair accuracy vs mean length  ->  a visible Pareto frontier
```

## Over-Optimization Cross-Over Chart

```
metric
  ^
  |  proxy reward     ............. (keeps rising)
  |              .....
  |          ....
  |       ...
  |     ..
  |   ..
  |  .                                   <-- reward hacking begins
  | .:.
  |   :
  |  :..                                <-- true quality
  |    :.. 
  |      :...
  |         ....
  +--------------|--------------------------> optimization steps
                 KL budget
              (stop HERE, not at the reward peak)

  guard metrics to plot every eval:
    - held-out unrewarded quality
    - distinct_2 (diversity)
    - mean output length
    - KL from reference
    - safety refusal rate
```

## Preference Pair Anatomy and Biases

```
ideal pair                          biased pair (chosen shown first)
  prompt: "how do I reset my pw?"     prompt: "how do I reset my pw?"
  chosen: "Open Settings > Security,   chosen: "Open Settings > Security,
    click Reset. You'll get an           click Reset. You'll get an
    email to confirm."                   email to confirm."
  rejected: "click the thing"          rejected: "you can find it in
                                           the menu somewhere"
                                              (vaguely correct)

  content differs clearly             RM can also learn "the one on top
  -> learnable signal                 is always right" -> position bias

length-biased pair:
  chosen:   312 tokens, adds a worked example after the answer
  rejected:  48 tokens, correct but terse
  -> annotator preference == length preference

both-bad pair:
  chosen and rejected are both wrong
  -> treat as a tie, or filter out; otherwise you teach noise
```

## Beta / KL Trade-off

```
reward achieved
  ^
  |  *  beta = 0     -> runs away, KL explodes, quality collapses
  |      *
  |        *
  |  o      o  beta = 0.1
  |            o
  |              o   o  beta = 1.0
  |                    o  o   o  beta = 10  (barely moves from SFT)
  +------------------------------------------------> steps
                         |
                  sweet spot: max reward
                  subject to KL <= budget

  practical rule: STOP at KL_budget, not at reward plateau.
  the reward plateau and the KL budget are different events,
  and the KL budget is the one that is enforceable.
```

## Training Loop Anatomy

```
  preference dataset (or on-policy samples)
        |
        v
  [1] tokenize chosen / rejected
        |
        v
  [2] forward policy -> logp_chosen, logp_rejected
      (reference log-ratios: CACHED, not recomputed)
        |
        v
  [3] u = beta * [ (logp_w - ref_w) - (logp_l - ref_l) ]
        |
        v
  [4] L = softplus(-u)          <-- numerically stable, no sigmoid saturation
        |
        v
  [5] backward on logp only
        |
        v
  [6] grad clip by global norm; log PRE-clip value
        |
        v
  [7] AdamW step (decay excluded on LoRA B)
        |
        v
  [8] EVAL EVERY N STEPS -> log:
        reward, unrewarded quality, mean length, distinct_2, KL, refusal rate
        |
        v
  [9] if KL > kl_budget -> STOP and quarantine
```

## Pair Quality Gate

```
incoming dataset
   |
   +-- annotator agreement >= 0.6 ?   NO -> reject dataset (mostly noise)
   |
   +-- chosenLenRatio <= 1.5 ?         NO -> length-balance or add length penalty
   |
   +-- baseWinRate <= 0.95 ?           NO -> too easy; mix in hard pairs
   |
   +-- dupRate <= 0.05 ?               NO -> dedupe; dataset size is inflated
   |
   +-- both-bad rate <= 0.05 ?         NO -> filter or mark as ties
   |
   v
 ready for RM training
```

## Self-Check

- [ ] `L = softplus(-u)` rather than `-log(sigmoid(u))`.
- [ ] Reference log-ratios precomputed once.
- [ ] Reward and unrewarded quality plotted together, always.
- [ ] Stop rule is the KL budget, not the reward curve.
- [ ] Distinct-2 tracked to catch mode collapse.
- [ ] Pair quality gates enforced before training.