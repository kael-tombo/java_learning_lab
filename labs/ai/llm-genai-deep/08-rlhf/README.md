# 08-rlhf - RLHF
## Overview
Pipeline: supervised fine-tune, then reward-model training on human preference pairs (Bradley-Terry: P(A>B) = sigmoid(rA - rB)), then KL-penalized policy optimization (PPO) against the RM.
## Key formulas
- P(A>B) = 1/(1+e^-(rA-rB)); RM loss = -log P.
- PPO objective: reward minus KL penalty to the SFT policy.
## What the snippets show
- Lg08A: stage order with toy metric illustrations.
- Lg08B: exact 0.7311/0.3133 preference arithmetic.
## Try it
Widen the gap to 2.0 and confirm P rises to 0.8808.
## Formula reference
- BT model: P(A>B) = sigmoid(rA - rB); RM loss -log P over pairs.
- PPO: advantage-weighted updates with KL penalty beta*KL(pi||ref).
- SFT first: policy must follow instructions before preference shaping.
## Worked example
- Gap 1.0 -> sigmoid = 0.7311; loss -log = 0.3133.
- Gap 0 -> 0.5/0.6931 (coin flip, max loss); gap 2 -> 0.8808.
- Stage metrics toy: SFT halves loss 1.24->0.62 (illustration only).
## Pitfalls
- Reward hacking: policy games the RM; hold out judges, cap KL.
- Pair quality decides RM ceiling; audit annotator agreement.
- KL too high collapses gains; too low drifts off-distribution.
## Connections
- Preference math reuses logistic sigmoid from classical labs.
- Safety lab constrains what the optimized policy may output.
## Exercises
1. Gap 2.0; confirm P = 0.8808.
2. Gap 0; loss equals log 2.
3. Add KL 0.2; argue trade-off.
