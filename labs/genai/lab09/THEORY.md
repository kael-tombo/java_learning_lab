# Lab 09: LLM Evaluation & Benchmarks — Theory

## 1. Why Evaluation Is Harder Than It Looks

An LLM output is a free-form string. Evaluating it needs answers to three
questions, and confusing them is the most common source of nonsense in the field:

1. **Is it right?** (correctness / task accuracy)
2. **Is it faithful?** (grounded in the provided context, no fabrication)
3. **Is it good?** (helpful, harmless, well-written)

A benchmark answers only #1 on a narrow distribution. Production quality needs all
three, on your distribution, on your traffic.

## 2. Taxonomy of Evaluation

| Type | Question | Example |
|------|----------|---------|
| Exact match (EM) | Same string as gold | Classification, closed QA |
| F1 / token overlap | Partial lexical overlap | Open QA, summarization |
| BLEU | n-gram precision with brevity penalty | Machine translation |
| ROUGE-L / ROUGE-1/2 | Recall-oriented n-gram overlap | Summarization |
| METEOR | Unigram matching with stemming + synonyms | Translation |
| BERTScore | Embedding similarity of matched tokens | Robust to paraphrase |
| ChrF | Character n-grams | Morphologically rich languages |
| NLI / entailment | Is the answer entailed by the context | Faithfulness |
| Win rate | Blind pairwise against a baseline model | Preference |
| Rubric / LLM judge | Structured grading by a strong model | Open-ended quality |
| Human rating | Likert or pairwise with trained raters | Gold standard |
| Safety classifiers | Violation rate on red-team prompts | Safety |

## 3. BLEU

Modified n-gram precision with a brevity penalty:

```
p_n     = (sum_{g in cand} min(count_cand(g), count_ref(g))) / (sum_{g in cand} count_cand(g))
BP      = 1                    if |cand| > |ref|
        = exp(1 - |ref|/|cand|) otherwise
BLEU_k  = BP * exp( (1/k) * sum_{n=1..k} log p_n )
BLEU-4  uses k=4
```

Key properties and traps:
- BLEU is a **precision**-oriented metric with a brevity penalty — a candidate
  padded with extra words does not gain.
- BLEU correlates poorly with human judgment on tasks outside MT.
- BLEU is not comparable across **different tokenizers**: the candidate is the same
  string but token counts differ, so n-gram precision shifts. Always fix the tokenizer.
- Corpus-level BLEU (sum over all sentences) differs from sentence-level averaging;
  state which.

## 4. ROUGE

Recall-oriented n-gram overlap:

```
ROUGE-N  = (sum_{g in ref} min(count_cand(g), count_ref(g))) / (sum_{g in ref} count_ref(g))
ROUGE-L  = LCS-based F-measure with beta weighting
ROUGE-Lsum = ROUGE-L over sentence-level LCS, summed
```

ROUGE-1/ROUGE-2 = unigram/bigram recall; ROUGE-L = longest common subsequence.
ROUGE is a recall measure, so verbose candidates can score well — which is exactly
why summarization reports both ROUGE and a length statistic.

## 5. BERTScore

Contextual embeddings instead of exact tokens:

```
BERTScore = F1 over greedily matched tokens:
  for each token t in cand:  match to the most similar ref token, cosine sim r_t
  for each token t in ref:   match to the most similar cand token, cosine sim p_t
  P = (1/|cand|) sum r_t ;  R = (1/|ref|) sum p_t
  F1 = P*R / (alpha*P + (1-alpha)*R)
```

Handles paraphrase, which n-gram metrics cannot. Cost: one embedding pass per
candidate and reference. Also not a correctness measure — a fluent paraphrase of a
wrong answer scores well.

## 6. LLM-as-Judge

A strong model grades outputs using a rubric. Practical rules:

- **Position bias**: "A" and "B" are not equally likely to win. Randomize order per
  comparison and average (or run both orders and require consistency).
- **Verbosity bias**: longer answers score higher. Control for length or instruct the
  judge to ignore it — and verify it actually does.
- **Self-enhancement bias**: models prefer their own family's outputs. Mix
  generators, or use a judge from a different family.
- **Score distribution**: judges cluster on 3-4 values; 1-10 scales are mostly noise.
  Use pairwise or 2-4 scales.
- **Rubric specificity**: concrete criteria beat "rate 1-10 on quality". Include
  reference answers when available.
- **Calibration**: periodically measure judge-human agreement. A judge whose
  agreement drifts is silently invalidating every metric computed with it.

## 7. Hallucination Detection

Two distinct failure families, requiring different defenses:

**Intrinsic** — contradicts the provided context. Detect with NLI:
```
entail(p, a) = P(NLI model says a follows from p)
faithful = fraction of atomic claims with entail >= 0.5
```

**Extrinsic** — factually wrong, unverifiable against provided text. Detect with:
- Self-consistency across samples: claim a fact if k samples agree.
- Chain-of-verification: split into atomic claims, ask "is this supported by
  evidence?", revise or drop unsupported ones.
- Retrieval-grounded checks: verify against a trusted corpus.
- Attributed uncertainty: "I don't know" is a valid and cheap win.

Crucially, `unanswerable` questions are the highest-value evaluation set: a model
that answers them confidently is worse than one that abstains.

## 8. Bias and Fairness

| Metric | Definition | Use |
|--------|-----------|-----|
| Demographic parity | P(y=1 \| A=0) = P(y=1 \| A=1) | Hiring, moderation, ad targeting |
| Equal opportunity | P(yhat=1 \| y=1, A=0) = ... \| A=1) | Performance-sensitive tasks |
| Equalized odds | Combines calibration and TPR/FNR parity | Classification generally |
| Bias ratio | max / min group rate | Simple comparative reporting |
| Gap | difference between group rates | Reporting |

Practical notes:
- Report every metric **per group**, never a single "fairness score".
- Intersectional groups matter; aggregate parity can hide large within-group gaps.
- Bias in the benchmark can be *measurement* bias rather than model bias — check a
  strong baseline first.
- Bias metrics on open-ended generation are ill-defined; use classifiers on extracted
  attributes, and report the classifier's own accuracy.

## 9. Safety Evaluation

- **Refusal rate** on disallowed prompts; **over-refusal** on benign lookalikes.
  These move in opposite directions — one number cannot summarize safety.
- **Harmful continuation rate**: given a partial harmful prompt, does the model
  comply?
- **Jailbreak success rate** on an adversarial suite (prefix injection, role play,
  encoding tricks, many-shot).
- **Refusal consistency**: same request, paraphrased 5 ways.
- **Toxicity** on generations: classifier score distribution, plus human review of
  the tail.

## 10. Benchmark Design (Your Own)

The only benchmark that matters is the one built from your traffic.

```
1. Sample real queries (with PII scrubbed) stratified by intent and difficulty.
2. Label with: expected behavior, ideal answer or answer key, allowed sources,
   unanswerable flag, and category tags.
3. Split by USER or SESSION, not by query — otherwise near-duplicates leak.
4. Fix the judge, fix the seed, fix the decoding parameters; version all of them.
5. Every model or prompt change runs the full suite; publish the delta.
6. Add regression cases the moment production surprises you.
```

Minimum viable suite: 200-500 items covering the top intents, plus 50-100
unanswerable items, plus the safety red-team set.

## 11. Statistical Discipline

- Report **confidence intervals**, not point estimates. For 300 items, a 5-point
  difference is roughly within noise.
- Paired comparisons (same items, two systems) have far lower variance than
  unpaired — always pair.
- Multiple comparisons: comparing 10 models on one benchmark needs correction
  (Bonferroni or at minimum an acknowledgment).
- Fix randomness: seed, temperature, prompt version, model version. Log all of them.
- Beware benchmark contamination: if the model was trained on public benchmark data,
  its score is not a capability measure.

## 12. Performance and Operational Metrics

Correctness is only half. Also track:

```
TTFT, TPOT, p50/p95/p99 latency
tokens in/out per request, cost per request
throughput (tokens/s) under load, queue depth
cache hit rate, error rate by class
refusal rate, retry rate, timeout rate
drift: input length distribution, intent mix, language mix
```

## Key Equations

```
BLEU-4 = BP * exp( (1/4) sum_{n=1..4} log p_n )
ROUGE-N = sum_g min(count_cand(g), count_ref(g)) / sum_g count_ref(g)
F1     = 2PR / (P + R)
win_rate(a vs b) = #(a preferred) / #(comparisons)
bias_ratio = max_g rate(g) / min_g rate(g)
```