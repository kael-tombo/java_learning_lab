# Lab 07: AI Testing & Evaluation — Math Foundation

## 1. Sample Size for Proportions

Observed rate `p̂` from `n` samples, Wald 95% half-width:

```
h = 1.96 * sqrt(p̂(1-p̂)/n)
```

Worst case `p̂ = 0.5` gives `h = 0.98/sqrt(n)`, so `n ≈ 960/h²` for a resolution `h` in
proportion units.

| Resolution | n (Wald, worst case) |
|-----------|----------------------|
| 10 pts | 96 |
| 5 pts | 384 |
| 3 pts | 1,067 |
| 2 pts | 2,400 |
| 1 pt | 9,600 |

For detecting an **absolute** change from `p1` to `p2`:

```
SE_diff = sqrt( p1(1-p1)/n + p2(1-p2)/n )
n = (z * SE_diff_target_factor / delta)^2
```

The practical form: `n = 2 * p(1-p) * (z/delta)^2` for similar rates. At `p = 0.8,
delta = 0.05, z = 1.96`: `n ≈ 430`.

**Wilson intervals** are preferred for small `n` or extreme `p̂`, where Wald produces
bounds outside `[0,1]`:

```
centre = (p + z^2/(2n)) / (1 + z^2/n)
margin = z/(1 + z^2/n) * sqrt( p(1-p)/n + z^2/(4n^2) )
```

## 2. Paired Variance Reduction

Per-item deltas `d_i = a_i - b_i`:

```
sd(d)^2 = sd(a)^2 + sd(b)^2 - 2*rho*sd(a)*sd(b)
```

For `sd(a) = sd(b) = s` and correlation `rho`:

```
sd(d) = s * sqrt(2(1-rho))
SE_ratio (unpaired -> paired) = sqrt(2(1-rho)/2) = sqrt(1-rho)
```

| rho | SE ratio | Items saved |
|-----|----------|-------------|
| 0.0 | 1.000 | 0% |
| 0.4 | 0.775 | 40% |
| 0.6 | 0.632 | 60% |
| 0.8 | 0.447 | 80% |
| 0.9 | 0.316 | 91% |

The higher the agreement between systems, the more the paired design saves. Comparing a
new model against the incumbent on identical items therefore routinely needs 3-5x fewer
items for the same interval width.

## 3. pass@k

With `n` samples of which `c` are correct:

```
pass@k = 1 - C(n - c, k) / C(n, k)
```

Closed form avoiding huge binomials:

```
pass@k = 1 - prod_{i=n-c+1}^{n} (1 - k/i)
```

| c / n | pass@1 | pass@5 | pass@10 |
|-------|--------|--------|---------|
| 1/10 | 0.100 | 0.409 | 0.651 |
| 2/10 | 0.200 | 0.624 | 0.802 |
| 5/10 | 0.500 | 0.936 | 0.999 |

Interpretation: with a single sample the model looks weak; with 5 samples it looks
strong. **A pass@1 comparison against another model's pass@5 is meaningless** — always
state `k`.

## 4. Retrieval Metrics

```
recall@k = (1/|Q|) * sum_q [gold_q ⊆ topk(q)]
precision@k = (1/|Q|) * sum_q |gold_q ∩ topk(q)| / k
MRR = (1/|Q|) * sum_q 1/rank_of_first_hit(q)
DCG@k = sum_{i=1..k} rel_i / log2(i+1)
nDCG@k = DCG@k / IDCG@k
```

For a graded relevance set, DCG with `rel_i ∈ {0, 0.5, 1}` and `log2(i+1)` discounting is
standard. Note that `recall@k` can be 1.0 while `precision@k` is `1/k` when exactly one
gold item exists and it ranks last — report both.

## 5. Multi-Stage Reliability Product

```
P(correct) = prod_i p_i
```

Retrieval 0.95 x rerank-preservation 0.99 x grounded-answer 0.93 x parse-ok 0.99:
`0.865`. A 5-point drop anywhere costs 5 points overall. Because the stages are also
correlated, real-world values run lower.

## 6. Judge Agreement as a Correction

If a judge agrees with humans at rate `p_j`, observed effect sizes are attenuated:

```
observed_delta ≈ true_delta * (2*p_j - 1)
```

| p_j | attenuation factor |
|-----|-------------------|
| 0.90 | 0.80 |
| 0.80 | 0.60 |
| 0.70 | 0.40 |
| 0.65 | 0.30 |

At `p_j = 0.70` (a realistic single-annotator ceiling) a measured 4-point improvement
corresponds to roughly 10 points of true delta, and a 1-point measured difference is
almost certainly noise. Agreement is a **correction factor on effect size**, not merely a
pass/fail gate.

## 7. Multiple Comparisons

Testing `m` variants at level `alpha`:

```
P(any false positive) = 1 - (1 - alpha)^m
```

| m | alpha=0.05 |
|---|-----------|
| 3 | 0.143 |
| 5 | 0.226 |
| 8 | 0.337 |
| 10 | 0.401 |
| 20 | 0.642 |

Corrections: Bonferroni (`alpha/m`, conservative), Holm step-down (tighter, still
family-wise valid), Benjamini-Hochberg (controls false discovery rate, appropriate for
sweeps where many true positives are expected). State which was used.

## 8. Flakiness Measurement

For a test run `R` times, with `f_i ∈ {0,1}` outcomes:

```
flakiness = |distinct outcomes| / R       (0 = deterministic, 1 = coin flip)
```

Target: `flakiness = 0` for all deterministic tests. A test with `flakiness > 0`
indicates hidden nondeterminism — a clock, a hash ordering, concurrency, or shared state
— and it erodes trust in the entire suite.

## 9. Mutation Score

```
mutation_score = killed_mutations / total_mutants
```

A suite with a score below 0.8 is not meaningfully testing the mutated behaviour. For AI
code, the highest-value mutants are the ones that encode domain invariants:

| Mutant | Invariant broken |
|--------|------------------|
| LoRA `B` random init | adapted model must equal the base at step 0 |
| Mask applied after softmax | future tokens must have exactly zero weight |
| RRF rank off by one | fusion ordering |
| `additionalProperties` dropped | injection defence |
| Sentinel not enforced | abstention |
| Truncation order swapped | schema must never be truncated |

## 10. Property Test Shrinking

Random input generation finds a failure; **shrinking** finds the minimal case. Given a
failing input, repeatedly try removing or simplifying elements:

```
while failure persists and input can be simplified:
    try removing one element; if it still fails, keep the removal
```

A failing case that shrinks from 4 KB of text to `""` or `null` is a bug report. One that
cannot shrink past 400 characters usually indicates a data-dependent bug worth
investigating rather than an API misuse.

## 11. Abstention Metrics

```
decline_rate         = declined / unanswerable
false_decline_rate   = declined_but_answerable / answerable
E[correct]           = coverage * accuracy
```

With a 15% unanswerable set and 85% answerable, a policy that declines everything gets
`decline_rate = 1.0` and `false_decline_rate = 0.85`. Reporting `decline_rate` alone
would make it look perfect.

## 12. Safety Metric Trade-off

A guardrail tuned to reduce harmful compliance by tightening a classifier:

```
harmful_compliance(p)  decreases with stricter p
benign_refusal(p)      increases with stricter p
```

The joint objective is

```
minimize   w_h * harmful_compliance + w_b * benign_refusal
```

so the operating point depends on the **weights**, which are a product decision. Neither
metric alone identifies a good setting, and tuning one to a target almost always
violates the other.

## Worked Numbers

Suite of 300 items, baseline accuracy 0.78.

**Detecting a 4-point improvement** (`0.78 -> 0.82`, paired):
```
n = 2 * p(1-p) * (1.96/0.04)^2  ~  2 * 0.17 * 2401 = 816
```
So roughly 800 items needed unpaired; paired with `rho = 0.7` the requirement drops to
`800 * 0.3 = 240` (since `SE_ratio = sqrt(0.3) = 0.548`, so `n_paired = 800 * 0.548^2 =
240`). Paired design cuts the requirement by 70%.

**Judge attenuation**: at `p_j = 0.78`, factor `0.56`. A measured 3.4-point delta
corresponds to `3.4/0.56 = 6.1` points of true delta.

**Multi-variant sweep**: 8 variants at `alpha = 0.05` -> 34% chance of at least one
false positive. With Holm, the family-wise rate holds at 5%.

**Flakiness audit**: 200 tests over 20 runs; 4 tests show `flakiness = 1.0` (fully
unstable). Those 4 are removed from the blocking suite until their nondeterminism is
fixed — an unstable blocking test is worse than no test.

**Mutation testing**: 12 domain mutants, 10 killed, mutation score 0.83. The two
survivors (sentinel enforcement, truncation order) get new tests immediately.

## Self-Check Questions

1. Compute `n` to detect a 6-point change from 0.70 to 0.76 at 95%.
2. Show that paired testing with `rho = 0.85` needs 27% of the unpaired items.
3. Compute `pass@5` for `n = 20, c = 2`.
4. Compute the attenuation factor at `p_j = 0.72`.
5. Compute the family-wise error for 12 comparisons at `alpha = 0.05`.