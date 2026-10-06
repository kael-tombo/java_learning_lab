# Lab 09: AI Security — Math Foundation

## 1. Detection Probability Under Repeated Attempts

A single control with per-attempt detection `d` fails eventually:

```
P(undetected after m attempts) = (1 - d)^m
```

| d | m=1 | m=5 | m=10 | m=50 |
|---|-----|-----|------|------|
| 0.5 | 0.50 | 0.031 | 0.001 | ~0 |
| 0.8 | 0.20 | 0.00032 | 5e-6 | ~0 |
| 0.95 | 0.05 | 3e-11 | ~0 | ~0 |

**No single control reaches `d = 1`.** Layered controls with independent-ish
detection compound:

```
P(all layers miss) = prod_i (1 - d_i)
```

With four layers at `d = 0.7`: `0.3^4 = 0.0081` — 1 in 123 attempts gets through,
versus 50% with one layer. This is the arithmetic justification for defence in depth,
and it is why the residual risk is stated as a number rather than "we have guardrails".

Caveat: layers are **not independent**. A shared weakness (the same model judging
injection in both the input and output filter) destroys the compounding. Measure the
residual empirically, not analytically.

## 2. Base Rate Makes Precision Collapse

With disallowed fraction `pi`, recall `TPR`, and false-positive rate `FPR`:

```
precision = TPR*pi / (TPR*pi + FPR*(1-pi))
```

| pi | TPR | FPR | precision |
|----|-----|-----|-----------|
| 0.50 | 0.95 | 0.01 | 0.989 |
| 0.10 | 0.95 | 0.01 | 0.909 |
| 0.02 | 0.95 | 0.01 | 0.660 |
| 0.005 | 0.95 | 0.01 | 0.324 |
| 0.001 | 0.95 | 0.01 | 0.087 |

At a 0.1% disallowed rate, a 1% FPR means ~92% of flags are wrong. This is why a
single classifier over all traffic is the wrong architecture, and why tiered handling
exists: a cheap high-recall filter on everything, then a precise classifier on survivors.

## 3. Cost-Optimal Threshold

Assign `C_FN` (harm from a missed attack) and `C_FP` (cost of a false flag). For
score densities `f` (disallowed) and `g` (benign), the optimal threshold solves:

```
C_FN * pi * f(p*) = C_FP * (1 - pi) * g(p*)
```

With `f` and `g` approximately equal (overlapping score distributions), this reduces to
the prior odds balancing the cost ratio:

```
p* such that f(p*)/g(p*) = C_FP * (1-pi) / (C_FN * pi)
```

A 100x cost asymmetry with `pi = 0.01` requires an odds ratio of `C_FP/C_FN = 1/100`,
i.e. the threshold must sit **deep in the benign tail**. Concretely: a threshold chosen
at the equal-error point is far too permissive; a threshold chosen at equal precision is
far too aggressive. The threshold is a product decision expressed in maths.

## 4. Two-Stage Filtering Economics

```
stage 1: cheap, high recall    blocks 95% of harmful, 5% of benign    cost C1
stage 2: precise classifier    on the surviving 5%                    cost C2

cost per request = C1 + 0.05 * C2
```

With `C1 = $0.00002` and `C2 = $0.0004`: `$0.00004` versus `$0.0004` for stage 2
alone — a 10x reduction, at the price of a less precise decision on the survivors.
This is the same shape as retrieve-then-rerank and as a two-tier SLA.

## 5. Multi-Turn Accumulation

Per-turn detection probability `f`, payload split across `n` fragments:

```
P(detect) = 1 - (1 - f)^n
```

With `f = 0.02, n = 10`: `P(detect) = 0.183`. Per-turn filtering misses 82% of split
payloads. Stateful accumulation across a session is required, and it must be
distinguished from legitimate multi-turn workflows — which is why the stateful signal
weights a *sequence* of otherwise-benign turns rather than any single turn.

## 6. Canary Leak Probability

Canary tokens in the system prompt; per-token emission probability `q_c`; `n` generated
tokens:

```
P(leak over n tokens) = 1 - (1 - q_c)^n
```

| q_c | n=100 | n=1,000 | n=100,000 |
|-----|-------|---------|-----------|
| 1e-2 | 63% | 99.995% | ~100% |
| 1e-3 | 9.5% | 63% | ~100% |
| 5e-5 | 0.5% | 4.9% | 99.3% |
| 1e-6 | 0.01% | 0.1% | 9.5% |

Small per-token probabilities compound. Canary tests must therefore run at volume —
1,000 requests of 100 tokens each for a `q_c = 5e-5` target. This is the arithmetic
behind "test canaries at volume" and it is also why a single spot check proves nothing.

## 7. Hash-Chain Integrity

```
h_0 = 0
h_i = SHA256(h_{i-1} || record_i)
```

Tampering with record `j` changes `h_j` and every subsequent hash, so verification
fails at the first mismatch and the tampered index `j` is identified. Collision
resistance at 2^-256 per attempt under SHA-256.

Limitation: this detects tampering by **recomputation** against an append-only sink.
An attacker who controls the writer can rewrite the whole chain. The mitigation is
external anchoring — periodically publishing `h_n` to an immutable store, so the
rewritten chain is detectable by comparing anchors.

## 8. Blasts Radius

```
expected_cost(bad_release) = blast_radius * impact_per_request * detection_delay
```

With detection delay `D` roughly fixed by alerting quality, minimizing blast radius is
the highest-leverage release discipline:

| radius | impact | delay | expected cost |
|--------|--------|-------|---------------|
| 0.01 | $5 | 5 min | $0.004 |
| 0.10 | $5 | 5 min | $0.042 |
| 1.00 | $5 | 5 min | $0.417 |

A 100x difference from rollout design alone. Feature flags with independent kill
switches exist specifically to make the radius small.

## 9. Detection Rate and Residual Surface

```
detection_rate = 1 - uncaught / total
```

With `L` layers and `n` attack classes discovered, the uncaught set is the measured
attack surface. Reporting it is more honest than reporting a per-layer score, and a
**falling** detection rate is the clearest signal that the red-team programme is losing
to new attack families.

## 10. Refusal/Over-Refusal Trade-off

Let `c(p)` be compliance on disallowed prompts and `b(p)` the false-refusal rate on
benign ones. With weights `w_h, w_b`:

```
J(p) = w_h * c(p) + w_b * b(p)
```

Empirically `c(p)` and `b(p)` are both monotone in strictness, so `J` is minimized at a
single point that depends on the ratio `w_h/w_b`. With `w_h = 1, w_b = 0.1`
(cheap false refusals, expensive harm), the optimum sits at high strictness; with
`w_b = 1` the optimum is much looser. **The threshold is a business decision**, and a
team that cannot state the weights cannot justify its threshold.

## 11. Secret Rotation Blast

A leaked secret touches: LLM prompts, caches, KV cache (transient), trace payloads,
logs, evaluation artifacts, exported datasets, checkpoints, and third-party
subprocessors. If rotation takes `T_prop` to propagate:

```
P(secret still usable after rotation) ≈ exp(-T_rot / T_prop)
```

With a 6-hour propagation and a 1-hour rotation window: `e^{-0.167} = 85%`. **Rotation
is nearly meaningless without simultaneous invalidation everywhere**, which is why the
rotation runbook must enumerate every store that could hold the value — including the
ones nobody remembers.

## 12. Security Testing Diminishing Returns

If the suite has `n` cases and each finds bugs at rate `p` per case:

```
expected_findings = n * p
P(find nothing in n) = (1-p)^n
```

With `p = 0.02`: 50 cases -> 64% chance of finding nothing new; 200 cases -> 98% chance
of finding something. Sizing the suite against a discovery target rather than by feel
is what distinguishes a red-team programme that keeps up from one that does not.

## Worked Numbers

Platform with 1M requests/day, `pi = 0.5%` of traffic genuinely disallowed,
classifier TPR 0.97, FPR 0.004.

- Harmful requests reaching users: `5000 * 0.03 = 150/day`.
- Benign wrongly refused: `995,000 * 0.004 = 3,980/day` = 0.4% of all traffic. For a
  200k daily-user product that is roughly 2 legitimate refusals per user per day.
- Precision = `4850 / (4850 + 3980) = 0.549` — roughly half of all refusals are wrong.
- Two-stage: cheap filter catches 95% of harmful and 5% of benign; the precise
  classifier sees 50,000 requests/day and the false-refusal count drops to ~50,000*0.004
  = 200/day, a 20x improvement in the dominant harm.

- Canary: `q_c = 5e-5`, 1,000 requests x 100 tokens = 100,000 tokens -> `P(leak) =
  99.3%`. A 100-request spot check gives `1 - (1-5e-5)^10000 = 39%`. Still high; 10,000
  requests is needed to be confident.
- Blast radius: a bad prompt released to 100% with `$5` impact and a 5-minute detection
  delay: expected cost `$0.42` per incident. At a 1% canary: `$0.004`.
- Layered detection: four independent layers at `d = 0.7` -> `0.3^4 = 0.81%` residual;
  one layer -> 30%. With 200 test cases at `p = 0.02` discovery rate, a 98% chance the
  suite finds something the current controls miss.

## Self-Check Questions

1. Compute residual miss probability for three layers at `d = 0.8`.
2. Compute precision at `pi = 0.005`, TPR 0.95, FPR 0.01.
3. Compute `P(leak)` for `q_c = 1e-5` over 50,000 tokens.
4. Derive the score odds ratio required at `pi = 0.02`, `C_FN/C_FP = 50`.
5. Compute the expected cost of a bad release at 10% blast radius with a 30-minute
   detection delay and `$20` impact.