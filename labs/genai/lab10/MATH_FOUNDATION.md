# Lab 10: LLM Safety & Alignment — Math Foundation

## 1. Classifier Threshold Trade-off

For a safety classifier with score `s(x)` and threshold `p`:

```
refusal_rate(p)     = P(s(x) >= p  | x disallowed)      -> want high
over_refusal(p)     = P(s(x) >= p  | x benign)         -> want low
```

Detection metrics:

```
TPR(p) = refusal_rate
FPR(p) = over_refusal
precision(p) = TPR * pi / (TPR * pi + FPR * (1 - pi))   with pi = P(disallowed)
```

With `pi = 0.02` (2% of traffic is genuinely disallowed), `TPR = 0.95`, `FPR = 0.01`:

```
precision = 0.95*0.02 / (0.95*0.02 + 0.01*0.98) = 0.019 / 0.0288 = 0.66
```

Only two thirds of refusals were justified. The base rate is why precision matters
here even at high recall.

## 2. Expected Cost Minimization

Assign costs: `C_FN` for letting a harmful request through, `C_FP` for over-refusal,
`C_review` for escalating to a human.

```
expected_cost(p) = pi*C_FN*(1-TPR(p)) + (1-pi)*C_FP*FPR(p) + reviewed*pi*C_review
```

The optimal threshold satisfies (for a monotone score):

```
C_FN * pi * f(p*) = C_FP * (1 - pi) * g(p*)
where f = pdf of disallowed scores, g = pdf of benign scores
```

This is the Neyman-Pearson form: the threshold balances the two densities weighted by
costs. Practically it says the threshold is **not** 0.5 and **not** fixed — it
depends on the base rate and the cost ratio.

## 3. Base-Rate Sensitivity

With `FPR = 0.01` fixed, vary the disallowed fraction:

```
pi        TPR     FPR     precision
0.50      0.95    0.01    0.989
0.10      0.95    0.01    0.909
0.02      0.95    0.01    0.660
0.005     0.95    0.01    0.324
0.001     0.95    0.01    0.087
```

At a 0.1% disallowed rate, a 1% false-positive rate produces ~92% of flags being
wrong. This is the quantitative argument for tiered handling: a strict low-recall
filter on *everything*, plus a high-precision classifier on the flagged subset.

## 4. Two-Stage Filtering Economics

```
stage 1 (cheap, high recall):  blocks 95% of harmful, 5% of benign
stage 2 (expensive classifier): on the surviving 5%
  -> analyzes at cost C2 << C1 per call
volume seen by stage 2 = 5% of traffic
cost per request = C1 + 0.05*C2  instead of  C2
```

This is why real systems run a cheap first pass and pay for the accurate classifier
only on what survives — and it is the same shape as the retrieve-then-rerank pattern
from Lab 04.

## 5. Multi-Turn Attack Accumulation

Let each turn `i` carry a payload fragment with probability of triggering a per-turn
filter `f`:

```
P(detect) = 1 - (1 - f)^n     for n fragments
```

With `f = 0.02` (rarely triggers on a fragment) and `n = 10` fragments:
`P(detect) = 1 - 0.98^10 = 0.183`. Per-turn filtering misses 82% of split-payload
attacks. This is the quantitative justification for stateful accumulation.

## 6. Encoding Attack Coverage

An attack family has `k` variants. A filter detecting one pattern catches a fraction
`c` of the family:

```
coverage = 1 - (1 - c)^k   for k independent-looking variants
```

With `c = 0.3` and `k = 12` (base64, hex, ROT13, leetspeak, reversal, spacing, ...):
`coverage = 1 - 0.7^12 = 0.986`. But variants are **not** independent — they share a
semantic core — so real coverage is far lower. Treat any coverage estimate from
independent assumptions as an upper bound.

## 7. Hash-Chain Integrity

```
h_0 = 0
h_i = SHA256(h_{i-1} || record_i)
```

Tampering with record `j` changes `h_j`, which propagates to `h_{j+1..n}`. Verification:

```
verify: h_0 == 0 and h_i == SHA256(h_{i-1} || record_i) for all i
```

Probability of an undetected arbitrary forgery without the key: `2^-256` per attempt,
assuming SHA-256. Note this detects tampering by *recomputation*; it does not prevent
an attacker who controls the writer from rewriting the whole chain. For that you need
an external append-only sink.

## 8. Canary Leak Probability

Plant `c` canary tokens in the system prompt. If the model emits a canary token with
per-token probability `q_c`:

```
P(leak over n generated tokens) = 1 - (1 - q_c)^n
```

If `q_c` is even `1e-4` and `n = 500`, `P(leak) = 4.9%`. Small per-token probabilities
compound into a real incident rate over enough requests. This is why canary tests must
run at volume (Exercise 4 in the real-world project uses 1,000 requests).

## 9. Cost-Benefit of Rate Limiting

Enumeration attack: attacker probes `k` values. With a token bucket of capacity `C`
and refill `r` per second, a sustained attack rate above `r` accumulates debt:

```
debt(t) = max(0, debt(t-1) + (rate - r) * dt)
allowed if debt <= C
```

Detection signal: sustained positive debt with no corresponding legitimate traffic.
Permitting `N` attempts per window bounds the search to `N` probes per window instead
of unlimited.

## 10. False-Negative Impact Model

Let a harmful output cause expected harm `H` if it reaches a user. With the guardrail
in place:

```
E[harm] = (1 - TPR) * H * exposure
```

Raising `TPR` from 0.90 to 0.99 cuts harm by 90%. But raising `TPR` typically raises
`FPR`:

```
E[cost of over-refusal] = FPR * n_benign * C_per_refusal
```

With `n_benign = 1000 * traffic`, even `FPR = 0.005` produces 5 refused legitimate
requests per 1,000. Frustrated users churn. Both terms must be in the decision.

## 11. Defense Attribution

When a suite finds a failure, attribute it to a layer. With `L` layers and test cases
that fail at layer `i` if all layers up to `i` pass:

```
attribution(i) = # failures first detected at layer i / total failures
```

Sum equals 1 by construction. Reporting this tells you which layer to invest in next.
A suite where 70% of failures land at L4 (output) means the earlier layers are not
doing their job.

## 12. Entailment for Grounding Verification

Given answer claims `c_1..c_m` and context `p`:

```
support(c_i) = P(NLI_entails(p, c_i))
faithful     = (1/m) sum_i 1[support(c_i) >= tau]
```

Risk-weighted, weighting by claim information content (`-log p(c_i)`):

```
faithful_w = sum_i I(c_i) * 1[support >= tau] / sum_i I(c_i)
```

Numeric claims deserve disproportionate weight — a wrong number in an otherwise
faithful answer is the failure that causes real damage. Implement a numeric-claim
detector and verify those against the context exactly.

## 13. Rate of Discovery vs Rate of Fixing

If the red team discovers `d` new bypass classes per week and each takes `f` days to
fix, the backlog grows when `d * f > 7` class-days... concretely:

```
backlog_growth_per_week = d - 7/f
sustainable requires d <= 7/f
```

With `f = 2` days, sustainable discovery is `d <= 3.5` new bypass classes per week.
Teams that discover 20 per week have a permanent, growing attack surface. This is an
underrated metric: measure it.

## Worked Numbers

A guardrail sees 1M requests/day. 0.5% (5,000) are disallowed. Classifier: TPR 0.97,
FPR 0.004.

- Harmful requests reaching users: `5000 * 0.03 = 150/day`.
- Benign requests wrongly refused: `995,000 * 0.004 = 3,980/day` = 0.4% of all traffic.
  For a 200k daily-user product, that is ~2 refused legitimate requests per user per day.
- Precision = `4850 / (4850 + 3980) = 0.549`. Roughly half of all refusals are wrong.
- Lowering FPR to 0.001 cuts false refusals to 995/day but lets 150 -> 175 harmful
  through. Whether that trade is right depends on `H` versus `C_per_refusal` — which
  is a product decision, not an engineering one. Write down which one you chose and why.

## Self-Check Questions

1. Compute precision at `pi = 0.01`, `TPR = 0.95`, `FPR = 0.004`.
2. Solve for `p` that minimizes expected cost with `C_FN = 10`, `C_FP = 1`,
   `pi = 0.05`, and disjoint score distributions centered at 0.8 and 0.2.
3. Compute `P(detect)` for 20 fragments at `f = 0.01`.
4. Show canary leak probability for `q_c = 5e-5`, `n = 1000`.
5. Given 8 new bypass classes discovered weekly and a 3-day mean fix time, is the
   program sustainable?