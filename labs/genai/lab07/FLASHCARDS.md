# Lab 07: RLHF & Preference Optimization — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | RLHF | SFT -> reward model -> policy optimization |
| 2 | Stage 1 | SFT / behavior cloning on demonstrations |
| 3 | SFT loss | Masked cross-entropy on assistant tokens |
| 4 | RLHF ceiling | Bounded by SFT policy quality |
| 5 | Preference pair | (prompt, chosen, rejected) |
| 6 | Bradley-Terry | `P(y_w > y_l) = sigmoid(r_w - r_l)` |
| 7 | RM loss | `-log sigmoid(r_w - r_l)` |
| 8 | RM loss at tie | `ln 2` with gradients `+/-0.5` |
| 9 | RM identifiability | Only reward *differences*; offset is free |
| 10 | Never do | Treat reward as absolute quality across prompts |
| 11 | Human agreement ceiling | ~65-70% on pairwise judgments |
| 12 | RM accuracy metric | Held-out pair accuracy |
| 13 | Length bias | Longer answers score higher |
| 14 | Position bias | The answer shown first wins |
| 15 | Position fix | Randomize presentation order |
| 16 | Length control | Length penalty `r' = r - lambda*len` |
| 17 | Style bias | "As an AI..." markers rewarded |
| 18 | Self-preference | RM favors its own family's outputs |
| 19 | RM fix | Train on a different base model |
| 20 | PPO objective | `E[ r(x,y) - beta * KL(pi || pi_ref) ]` |
| 21 | KL purpose | Anchor the policy; prevent reward hacking |
| 22 | beta small | Reward hacking |
| 23 | beta large | No movement from SFT |
| 24 | Four models in PPO | policy, reference, reward, value head |
| 25 | Memory trick | Quantize RM/ref, train policy with LoRA |
| 26 | TD residual | `delta_t = r_t + gamma*V(s_{t+1}) - V(s_t)` |
| 27 | GAE | `A_t = delta_t + gamma*lambda*A_{t+1}` |
| 28 | GAE lambda | Bias/variance tradeoff; 0.95 typical |
| 29 | lambda = 0 | Monte-Carlo-ish TD only (one-step residual) |
| 30 | lambda = 1 | Advantage equals value (low variance, high bias) |
| 31 | PPO ratio | `pi_new(y)/pi_old(y)` |
| 32 | PPO clip eps | 0.1-0.2 typical |
| 33 | PPO clipped gradient | Zero when ratio exceeds band in improving direction |
| 34 | KL as token reward | `r_t' = r_t - beta * log(pi_theta/pi_ref)` |
| 35 | Advantage normalization | Normalize within batch to stabilize scale |
| 36 | DPO loss | `-log sigmoid(beta * (logp_w - logp_w_ref) - ...)` |
| 37 | DPO implicit reward | `beta*log(pi_theta/pi_ref) + const` |
| 38 | DPO advantage | Offline: no sampling, no reward model |
| 39 | DPO memory | Reference log-ratios precomputable once |
| 40 | DPO weakness | No exploration beyond the dataset |
| 41 | DPO weakness | No inspectable reward signal |
| 42 | IPO | Squared loss; less likelihood displacement |
| 43 | ORPO | Reference-free; SFT + odds-ratio term |
| 44 | SimPO | Reference-free, length-normalized reward |
| 45 | KTO | Binary desirable/undesirable labels, no pairs |
| 46 | CPO | Contrastive preference with reward margin |
| 47 | RLAIF | AI feedback substitutes for human labels |
| 48 | Constitutional AI | Critique against written principles, then revise |
| 49 | Reward hacking | Policy exploits RM; humans dislike the result |
| 50 | Hacking symptom 1 | Length inflation |
| 51 | Hacking symptom 2 | Hedged preambles and disclaimers |
| 52 | Hacking symptom 3 | Sycophancy toward user assertions |
| 53 | Hacking symptom 4 | Fluent but wrong code and citations |
| 54 | Over-optimization curve | Inverted U for human satisfaction |
| 55 | Early stopping rule | Stop at KL budget, not at reward target |
| 56 | Unrewarded eval | Held-out metric the RM never saw |
| 57 | Plot both | Reward and unrewarded metric on one chart |
| 58 | Iterative RLHF | Re-collect preferences from the current policy |
| 59 | Why | Reward model drifts off-distribution |
| 60 | Data scale | Thousands to tens of thousands of pairs |
| 61 | Agreement metric | Krippendorff's alpha or raw agreement |
| 62 | Below 0.6 | Signal is mostly noise |
| 63 | Easy pairs | Teach nothing; balance with hard pairs |
| 64 | Both-bad pairs | Handle as ties or filter out |
| 65 | Near-duplicate prompts | Inflate apparent dataset size; dedupe |
| 66 | Held-out pairs | Never trained on; used for RM accuracy |
| 67 | Win rate | Judge-blind comparison against the SFT policy |
| 68 | KL from reference | The safety gauge on optimization |
| 69 | Refusal rate | Safety metric on the red-team set |
| 70 | Rule-based judge | Useful when human labels are the bottleneck |

## Self-Check

55+ = solid, 45-54 = redo Exercises 1 and 10, below that reread THEORY 2-7.