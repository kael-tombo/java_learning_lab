# Lab 07: RLHF & Preference Optimization — Math Foundation

## 1. Bradley-Terry Model

```
P(i beats j) = exp(r_i) / (exp(r_i) + exp(r_j)) = sigmoid(r_i - r_j)
```

Negative log-likelihood of observed preferences:

```
L = - E [ log sigmoid(r_w - r_l) ]
```

Gradient:

```
dL/dr_w = -sigmoid(-(r_w - r_l)) = -(1 - sigma(d))
dL/dr_l = +sigmoid(-(r_w - r_l)) =  +(1 - sigma(d))
```

At `d = 0`: `L = ln 2`, `dL/dr_w = -1/2`, `dL/dr_l = +1/2`.

Identifiability: `r -> r + c` for all `r` leaves every `sigmoid` unchanged. So the
RM is defined only up to an additive constant — exactly like a softmax. Any
downstream use of absolute reward values is unjustified.

## 2. Expected Accuracy Given RM Noise

If true preference has probability `p` of the chosen answer and the RM outputs the
sign of a difference corrupted by symmetric noise `epsilon`, accuracy is

```
acc = p(1-eps) + (1-p)*eps
```

With human disagreement `eps ~ 0.3` and `p = 1.0` (annotators always prefer the
chosen), `acc = 0.7`. A 70%-accurate "RM" can be perfectly aligned with the humans —
you cannot exceed the ceiling.

## 3. Length Bias Model

Assume reward decomposes:

```
r = r_content + c_len * log(len)
```

Fitting on a dataset with a length correlation `rho = corr(len_w, len_l) > 0` yields
an estimator that absorbs part of `c_len` into the content term. The resulting bias
on equal-content pairs is approximately `c_len * E[log len_w] - c_len * E[log len_l]`,
which is nonzero whenever the chosen answers are systematically longer. Length
control fixes this by removing `c_len * log(len)` before fitting.

## 4. KL Divergence Between Policies

```
KL(pi || pi_ref) = E_{y~pi}[ log pi(y|x) - log pi_ref(y|x) ]
```

Approximated per-token as `sum_t log pi(y_t|...) - log pi_ref(y_t|...)`. The sequence
KL for a product policy decomposes into a sum of token log-ratios, which is why the
KL is easy to compute token-wise and to use as a per-token reward.

## 5. RLHF Objective

```
J(theta) = E_{x, y~pi_theta}[ r_phi(x,y) ] - beta * E_{x, y~pi_theta}[ KL ]
```

Gradient (REINFORCE with the KL term folded in):

```
grad = E[ ( r(x,y) + beta * sum_t(log pi_ref - log pi_theta) ) * grad log pi_theta(y|x) ]
```

Note the sign: decreasing the KL term pushes `pi_theta` toward `pi_ref`.

## 6. GAE Derivation Sketch

TD residual: `delta_t = r_t + gamma V_{t+1} - V_t`.

GAE with weights `(gamma*lambda)^k`:

```
A_t = sum_{k>=0} (gamma*lambda)^k delta_{t+k}
```

- `lambda = 0`: `A_t = delta_t` — one-step TD, low variance, high bias.
- `lambda = 1`: `A_t = sum_k gamma^k delta_{t+k} = V_t - V_T` (with `gamma=1`) —
  Monte Carlo, unbiased, high variance.
- `lambda = 0.95`: the standard compromise.

Variance of the estimator decreases with lambda; bias increases. Mean advantage is
conventionally normalized per batch to zero mean and unit variance so the policy
gradient step size is comparable across batches.

## 7. PPO Clipped Objective

```
L_CLIP(theta) = - E[ min( r_t(theta) * A_t, clip(r_t(theta), 1-eps, 1+eps) * A_t ) ]
r_t(theta) = pi_theta(y_t) / pi_old(y_t)
```

Piecewise gradient:

- If `A_t > 0` (want to increase probability): gradient is **zero** when
  `r_t > 1 + eps` — no incentive to push further.
- If `A_t < 0` (want to decrease): gradient is **zero** when `r_t < 1 - eps`.

This removes the incentive for a single update to move the probability far, which
is what makes PPO stable.

## 8. DPO Derivation

Start from the KL-constrained RL optimum:

```
max_pi  E[ r(x,y) ] - beta * KL(pi || pi_ref)
```

The maximizer is `pi*(y|x) = pi_ref(y|x) * exp(r(x,y)/beta) / Z(x)`. Solve for `r`:

```
r(x,y) = beta * log( pi*(y|x) / pi_ref(y|x) ) + beta * log Z(x)
```

Substituting the Bradley-Terry likelihood over preferences and dropping `Z` (constant
in the args):

```
L_DPO = -E[ log sigmoid( beta * [ log(pi_theta(y_w)/pi_ref(y_w)) - log(pi_theta(y_l)/pi_ref(y_l)) ] ) ]
```

Define the implicit reward:

```
r*(x,y) = beta * log(pi_theta(y|x)/pi_ref(y|x))
```

Recovery check: substituting `r*` back gives
`log sigmoid(r*(y_w) - r*(y_l))`, so recovered rewards are consistent with the
observed preference probabilities — exactly Exercise 11's assertion.

## 9. DPO Gradient

Let `u = beta * [ (logp_w - logp_ref_w) - (logp_l - logp_ref_l) ]`. Then

```
dL/du = -(1 - sigmoid(u))
dL/dlogp_w      = -beta * (1 - sigmoid(u))
dL/dlogp_l      = +beta * (1 - sigmoid(u))
```

Reference log-ratios are constants w.r.t. theta — precomputable, which is the
memory win.

## 10. Odds Ratio (ORPO)

For a sequence, `log odds(y) = log pi(y|x) - log(1 - pi(y|x))` is only tractable at
the sequence level, so implementations approximate with mean token log-probabilities.
Loss:

```
L_ORPO = L_SFT + lambda * L_odds
L_odds = -log sigmoid( log O(y_w) - log O(y_l) )
```

Benefit: single model, no reference, no negative log-likelihood over a sampled
distribution.

## 11. Length-Normalized Reward (SimPO-style)

```
r(y) = (beta / |y|) * log pi_theta(y|x) - gamma
```

Length normalization removes the systematic reward-per-token trend, letting a fixed
`beta` work across tasks of different output lengths. `gamma` sets the target margin.

## 12. Best-of-N Selection

Sample `N` outputs, select `argmax r_phi`. With per-sample reward accuracy advantage
`q = P(rank 1 among the top)`:

```
E[quality of BoN(N)] grows ~ log N when rewards are near-independent and well-calibrated
```

Cost is `N`x generation. Compare against DPO's single-sample win rate at equal token
budget — that is the real trade-off, and it is close more often than people expect.

## 13. KL Budget as a Stopping Rule

Track cumulative KL:

```
KL_t = (1/T) sum_{i<=t} E[ log pi_theta(i)/pi_ref(i) ]
stop when KL_t > kl_budget   (do NOT stop when reward plateaus)
```

Since `beta` trades reward for KL, an observed KL over budget means the policy has
consumed its entire regularization budget and further steps are effectively
unregularized reward maximization.

## 14. Diversity Collapse

Optimizing a preference objective sharpens the output distribution. A usable proxy:

```
distinct_n(answer) = unique n-grams / total n-grams
```

Watch this alongside win rate: rising win rate with falling `distinct_2` is the
signature of mode collapse to a generic high-scoring style.

## Worked Numbers

Two-token sequence, rewards `r_w = 2.0`, `r_l = 1.0`, `beta = 0.1`.

- `P(y_w beats y_l) = sigmoid(1.0) = 0.731`.
- `L_RM = -ln 0.731 = 0.313`.
- Gradients: `dL/dr_w = -(1-0.731) = -0.269`, `dL/dr_l = +0.269`.
- DPO: if the policy prefers the rejected answer by `delta = 0.5` log-prob,
  `u = 0.1*(-0.5) = -0.05`, `L = -ln sigmoid(-0.05) = 0.681`, and the gradient on
  `logp_w` is `-0.1*(1-sigmoid(-0.05)) = -0.0488` — a small but nonzero push.

## Self-Check Questions

1. Show `r -> r + c` leaves the Bradley-Terry probability unchanged.
2. Compute `P(win)` and loss for `r_w = 0.5`, `r_l = -0.5`, `beta` irrelevant.
3. With `gamma=0.95, lambda=0.95`, is GAE biased or unbiased at the horizon edge?
4. Derive `dL/dlogp_l` for DPO from the definition.
5. Explain why `beta` at 0 makes over-optimization inevitable.