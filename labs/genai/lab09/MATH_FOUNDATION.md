# Lab 09: LLM Evaluation & Benchmarks — Math Foundation

## 1. Precision / Recall / F1 with Multiset Counts

```
overlap(g) = sum_v min(count_cand(v), count_ref(v))
P = overlap / |cand|
R = overlap / |ref|
F1 = 2PR / (P + R)
```

Multiset (not set) counting matters: "the the the cat" vs "the cat" has overlap 2 for
"the" with set semantics giving 1 — and `sum_v min(...)` is exactly the multiset
intersection.

Relation to F-beta:

```
F_beta = (1 + beta^2) PR / (beta^2 P + R)
F1 is beta = 1
```

## 2. BLEU

Clipped n-gram precision:

```
p_n = ( sum_{g in cand_ngrams} min(count_cand(g), count_ref(g)) ) / ( sum_{g in cand_ngrams} count_cand(g) )
```

Brevity penalty (closest reference length `r`):

```
BP = 1                                if c > r
BP = exp(1 - r/c)                    if c <= r      (c = candidate length)
```

BLEU-4:

```
BLEU-4 = BP * exp( (1/4) * sum_{n=1..4} log p_n )
```

Two properties to derive:

1. **A candidate longer than the reference cannot exceed the unigram ceiling** —
   adding words only adds denominator, never numerator (clipped counts are capped by
   the reference).
2. **BLEU-4 = 1 requires exact 4-gram match** (`p_4 = 1` implies every 4-gram of the
   candidate appears in the reference), so BLEU-4 = 1 is essentially only reachable
   by a copy. Any diversity cost shows up immediately.

**Tokenization sensitivity.** Let the same string have `t_bpe` BPE tokens vs `t_word`
whitespace tokens. Then

```
p_1 = overlap_unigrams / t_tokenizer
```

Changing the tokenizer changes `p_1` for the identical string. Hence the rule: only
compare BLEU computed with the same tokenizer, and state which.

**Corpus vs sentence aggregation.** Corpus BLEU pools n-gram counts across all
sentences:

```
BLEU_corpus = BP * exp( sum_n log( P_n^corpus ) / 4 )
P_n^corpus = total overlap_n / total candidate_ngram_n
```

Sentence BLEU averages `BLEU(s_i)`. Jensen's inequality means
`mean(log p_n) <= log(mean p_n)`, so **sentence-average BLEU is systematically lower**
than corpus BLEU. Always label which one you report.

## 3. ROUGE

```
ROUGE-N = sum_{g in ref} min(count_cand(g), count_ref(g)) / sum_{g in ref} count_ref(g)
```

Denominator is over the **reference**, so recall-oriented: doubling the candidate
length cannot reduce the score below the reference-coverage level. This is why
ROUGE must be reported with candidate length.

ROUGE-L via LCS:

```
LCS(cand, ref) computed by DP: L[i][j] = L[i-1][j-1] + 1 if equal else max(L[i-1][j], L[i][j-1])
P_l = LCS / |cand|
R_l = LCS / |ref|
F_l = ((1 + beta^2) P_l R_l) / (R_l + beta^2 P_l)
```

`beta > 1` weights recall higher — standard for summarization, where the reference
is short.

ROUGE-Lsum decomposes by sentence: run LCS within each sentence, then

```
ROUGE-Lsum = (1 + beta^2) * sum_u LCS_sent(u) / sum_u |ref_sent(u)| ...
```

specifically `sum_u LCS_sent(u)` in the numerator and `sum_u |ref_sent(u)|` in the
denominator — a corpus-level recall-weighted aggregation.

## 4. BERTScore

```
r_t = max_{s in ref} cos(e_t, e_s)      precision side (t in cand)
p_s = max_{t in cand} cos(e_t, e_s)     recall side (s in ref)
P = (1/|cand|) sum_t r_t
R = (1/|ref|) sum_s p_s
F1 = (P R) / (alpha P + (1 - alpha) R)
```

With `alpha = 1`, `F1 = P`. Greedy matching is `O(|cand| * |ref|)` cosine
computisons, and `cos = dot/(|a||b|)` — cache `1/|a|`, `1/|b|` once.

## 5. Win Rate and Confidence

Paired win rate over `K` comparisons:

```
win_rate = W / K
SE (unpaired approx) = sqrt(p(1-p)/K)
```

For a **paired** design (same items, system A vs B) the variance comes from the
discordant pairs only:

```
b = #(A wins), c = #(B wins)
win_rate = b / (b + c)
SE = sqrt( (b/(b+c)) * (c/(b+c)) / (b + c) )
SE_paired = sqrt(b + c - (b - c)^2 / (b + c)) / (b + c)
```

The paired SE is far smaller when the two systems agree often — which is exactly why
evaluating a new model against the incumbent is the right design.

## 6. Bootstrap Confidence Interval

Resample items with replacement `B = 10000` times:

```
for b in 1..B:  I_b = {random indices};  stat_b = mean(score[I_b])
CI_95 = percentile_2.5(stat), percentile_97.5(stat)
```

For **paired deltas**, resample and compute `mean(delta[I_b])`. Differences of 3
points on 100 items routinely produce a CI spanning zero; a 10-point difference does
not. This is the sanity check before claiming an improvement.

## 7. Hallucination / Faithfulness

Per-claim entailment score with `m` claims:

```
faithfulness = (1/m) sum_i 1[ entail(p, c_i) >= tau ]
```

Support-weighted variant (penalize long unsupported claims more):

```
faithfulness_w = sum_i len(c_i) * 1[entail >= tau] / sum_i len(c_i)
```

## 8. Abstention Trade-off

With threshold `p` on a confidence score:

```
coverage(p)   = (1/N) * sum 1[conf_i >= p]
accuracy(p)   = (1/|answered|) * sum_{conf_i>=p} correct_i
E[correct](p) = coverage(p) * accuracy(p)
```

Maximize `E[correct]` over `p`, and report the operating point's coverage and
accuracy together — never coverage alone.

## 9. Fairness Metrics

For binary outcome `Y` and prediction `Yhat`, protected attribute `A`:

```
demographic parity:  P(Yhat=1|A=0) = P(Yhat=1|A=1)
equal opportunity:   P(Yhat=1|Y=1,A=0) = P(Yhat=1|Y=1,A=1)
calibration:         P(Y=1|Yhat=1,A) = P(Y=1|Yhat=1,A')
bias ratio:          max_g P(Yhat=1|g) / min_g P(Yhat=1|g)
```

Why they can conflict. With groups having base rates `pi_g = P(Y=1|g)` and equal TPR
`T` under equal opportunity, we get `P(Yhat=1|g) = T*pi_g + (1-T)(1-pi_g)`. Demographic
parity therefore forces equal `pi_g` — so **equal opportunity and demographic parity
are simultaneously satisfiable only when the base rates are already equal**. That is
the exact statement behind Quiz 15: equal opportunity holds, parity fails.

## 10. Intersectional Analysis

With attributes `A` and `B`, four groups. Write the per-group rate as

```
rate(A=a, B=b) = mu + alpha_a + beta_b + gamma_{ab}
```

A "Simpson's paradox" configuration has `alpha_a = 0` and `beta_b = 0` (all marginal
gaps vanish) while some `gamma_{ab} != 0` (large within-group gap). Constructing
this is the point of Exercise 12.

## 11. Cost-Quality Frontier

For configurations `c` with cost `K_c` and quality `Q_c`, the efficient frontier is
the upper-left convex hull. Choose the knee: the point maximizing

```
utility(c) = Q_c - lambda * K_c
```

for the organization's exchange rate `lambda`. Reporting the frontier makes the
tradeoff a business decision rather than an engineering argument.

## 12. Effective Sample Size with Multiple Judgments

With `k` independent judgments per item and true accuracy `p`, the mean accuracy
across all `N*k` judgments has

```
SE = sqrt(p(1-p) / (N*k)) / k_adjustment
```

Judgments on the same item are correlated (same gold, similar prompt), so the
effective `k` is far below `k`. Measure it: compute the intraclass correlation
coefficient and report the *effective* number of judgments, not the raw count.

## Worked Numbers

Task: 100 paired items, system A vs system B, token F1.

- A: `mean = 0.62`, B: `mean = 0.59`. Unpaired CI on A: `+-1.96*sqrt(.62*.38/100) = +-0.095`.
- The difference is `0.03` — inside A's own interval. **Not significant.**
- Paired deltas: `b = 38` (A better), `c = 22` (B better), 40 ties.
  `win_rate = 38/60 = 0.633`, `SE_paired = sqrt(60 - 256/60)/60 = sqrt(55.7)/60 = 0.124`.
  95% CI = `[0.39, 0.88]` — excludes 0.5, so A is better.
- Conclusion: the paired test detects an effect the unpaired test could not. Same
  data, different design, opposite verdicts.

## Self-Check Questions

1. Show that adding words to a candidate cannot raise BLEU's clipped precision.
2. Compute BLEU-4 for candidate `"a b c"` vs reference `"a b c d"`.
3. Explain the Jensen inequality direction for corpus vs sentence BLEU.
4. Construct a group configuration where equal opportunity holds and parity fails.
5. Recompute the paired SE in the worked example with 20 ties instead of 40.