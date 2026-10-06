# Lab 03: Prompt Engineering Patterns — Math Foundation

## 1. Tokens, Not Words

A prompt's cost and context position are measured in tokens, not words. For
English, a common approximation:

```
tokens ≈ 0.75 * words ≈ 1.3 * characters
```

Consequences for prompt engineering:
- A "1,000-word document" is ~750 tokens, not 1,000.
- Non-English text can be far more expensive; some scripts are 2-3 tokens per
  character-equivalent for byte-level BPE.
- Budget calculations must use the real tokenizer. A `chars/4` heuristic is
  dangerous for code, JSON, and non-English text.

## 2. Next-Token Distribution Conditioning

A language model defines `p(x_t | x_<t, context)`. A prompt is a way of setting the
prefix so that the conditional distribution over the continuation is sharply peaked:

```
good prompt:  max_t p(target_t | prompt, x_<t)   -> high
bad prompt:   spread distribution                 -> low, so sampling wanders
```

Formally, the probability that greedy decoding produces the intended continuation `y`
is roughly the product of the per-step probabilities:

```
P(y | prompt) ≈ prod_t p(y_t | prompt, y_<t)
```

So prompt quality compounds: raising each step's probability from 0.9 to 0.95 over 10
tokens raises the whole-sequence probability from `0.9^10 = 0.35` to `0.95^10 = 0.60`.
This is the quantitative reason a well-specified format (high per-token probability)
matters more than a clever instruction.

## 3. Few-Shot Probability Boost

Empirically, k demonstrations multiply the target-token probability. A defensible
model of the effect:

```
log p(target | prompt + k demos)  ≈  log p(target | prompt)  +  k * gain
```

with `gain` larger for tokens where the demonstrations are informative. Two
implications:
- Diminishing returns: doubling k from 8 to 16 adds a smaller log-probability gain than
  0 to 8, so cost (linear in k) grows faster than benefit.
- Demonstration *quality* sets `gain`, not demonstration count. Boundary examples have
  a higher `gain` than redundant easy ones.

## 4. Log-Probability Accumulation for Parser Confidence

When parsing structured output, use the model's own confidence:

```
logprob(y) = sum_t log p(y_t | ...)
avg_logprob = logprob(y) / |y|
```

A parse with `avg_logprob` well below the observed distribution suggests the model was
guessing, which should lower trust or trigger a repair. Practical thresholds come from
your own data: measure the distribution of `avg_logprob` for successful parses and set
the repair threshold below the 5th percentile.

## 5. Few-Shot Budget Math

If the base instruction is `I` tokens, each demonstration is `D` tokens, and the
question is `Q` tokens:

```
prompt_tokens = I + k*D + Q
cost ratio vs zero-shot = 1 + k*D/I
```

With `I = 120`, `D = 90`, `Q = 40`:
- k=0: 160 tokens
- k=4: 520 tokens (3.25x)
- k=8: 880 tokens (5.5x)
- k=16: 1,600 tokens (10x)

If zero-shot accuracy is 0.70 and few-shot adds ~2 points per demonstration up to k=4
then ~0.5 points per demonstration beyond:

```
k=0: 0.70      k=4: 0.78      k=8: 0.805     k=16: 0.83
```

Cost per correct answer:
```
k=0:  160/0.70 = 229 tokens
k=4:  520/0.78 = 667
k=8:  880/0.805 = 1093
k=16: 1600/0.83 = 1928
```

The knee is around k=4. Beyond that you are buying diminishing accuracy at
compounding cost — and if prefix caching covers the demonstrations, re-run the numbers
with `D` discounted by the cached fraction, which moves the knee right.

## 6. Entropy of the Token Distribution

The average entropy of the next-token distribution is a prompt-quality proxy:

```
H_t = -sum_v p(v | x_<=t) log p(v | x_<=t)
```

A well-specified format has low entropy at the structural positions (where the next
character is constrained) and high entropy at content positions. Measure mean `H` over
a set of prompts:

```
mean_entropy = (1/T) sum_t H_t
```

Lower is better for extraction tasks; higher may be desirable for creative tasks. It is
also a useful debugging signal: if entropy is high where you expected a format token,
the instruction is under-specified.

## 7. Self-Consistency Accuracy

With k samples at temperature `T`, majority voting for a task with true class
probability `p` (and errors independent across samples):

```
P(majority correct) = sum_{j=(k+1)/2}^{k} C(k,j) p^j (1-p)^{j-1 ... }   (odd k)
```

For k=3, p=0.6: `0.648`. For k=5: `0.682`. For k=7: `0.710`.

Compare against the cost: `k` times generation. Self-consistency is worth it when the
task is high-stakes (math, multi-hop reasoning) and wrong answers are expensive. It is
usually not worth it for extraction, where a schema-constrained decode already
eliminates the variance.

The correct baseline comparison is against a *single* sample at temperature 0 with a
stronger model: k=5 samples of a weak model rarely beat one strong sample.

## 8. Tree-of-Thought Search Cost

For depth `T`, branching `b`, and evaluation cost `c_eval`:

```
nodes explored ~ b^T              (exponential)
if pruned to width w: ~ w*T
```

With b=3, T=4: 81 nodes, versus 4 for linear CoT. The trade is justified when the
search space contains attractive-but-wrong branches, which is true for Sudoku, planning,
and constraint problems, and false for straightforward generation.

## 9. Prompt Injection Probability Model

Model the attacker as choosing among `A` attack templates, with the defender detecting a
fraction `d_A` of them. If the attacker can enumerate templates freely:

```
P(detected per attempt) = d_A
P(undetected after m independent attempts) = (1 - d_A)^m
```

With `d_A = 0.5` and `m = 10`: `0.00098`. So a single successful bypass attempt is
eventual against a determined attacker unless detection is systematic. This is the
quantitative argument for defense in depth (Lab 10): no single control reaches
`d = 1`, but layered controls compound the cost of *finding* an uncovered bypass.

## 10. Repair Attempt Probability

If a first-parse failure occurs with probability `p_fail`, and a repair attempt
succeeds with probability `s`:

```
P(success within k attempts) = 1 - ((1 - s) p_fail)^k
```

With `p_fail = 0.05`, `s = 0.7`, `k = 3`:
```
1 - (0.3 * 0.05)^3 = 1 - 0.015^3 ≈ 0.9999966
```
Practically 100%. So a small number of repair attempts is nearly always sufficient,
which justifies the bounded retry loop with a deterministic fallback (Exercise 6).

## 11. Prompt Length vs Recall

For a retrieval-style prompt with `n` context chunks, empirically:

```
recall(augmented) increases with n up to a knee, then flattens
attribution_error increases with n   (more chunks -> more misattribution)
```

Two effects fight each other. The optimum is typically 3-6 well-ranked chunks. Beyond
that, both recall and faithfulness degrade, and cost grows linearly. The knee is
measurable: sweep `k` and plot faithfulness (not just recall).

## 12. Context Caching Arithmetic

Let prompt length `P`, stable prefix `S`, cached-price fraction `alpha`, hit rate `h`:

```
cached_tokens_expected = S*h
billable = P - S*h*(1-alpha)
```

For a templated support product with `P = 800`, `S = 600`, `alpha = 0.1`, `h = 0.85`:
```
cached = 510, discounted saving = 459 tokens -> 57% of the prompt
```

If `h` drops to 0.4 (because a timestamp leaked into the prefix):
```
saving = 216 tokens -> 27%
```
The prefix fraction dominates the effect. If `S` is only 100 tokens of an 800-token
prompt, no cache strategy matters. Measure the prefix fraction before optimizing
caching.

## 13. Few-Shot Order Bias

Let `p_k` be the accuracy when the correct example is at position `k` of `n`. Empirically
accuracy declines toward the end for some models (recency competition with the
question). Averaging over `n!` orderings:

```
expected_accuracy = (1/n) sum_k p_k
```

with variance `Var = (1/n^2) sum_k (p_k - mean)^2`. So if position variance is 3 points
across a 5-shot prompt, a single ordering can move your measured accuracy by ±3 points —
enough to swamp a real 2-point improvement. **This is why A/B tests must average over
example orderings** (Exercise 4).

## 14. Selection Without Bias

If you select `k` demonstrations from `N` candidates, the number of possible subsets is
`C(N, k)`. To avoid cherry-picking the subset that happens to match the eval set:

```
select a random stratified subset with a FIXED seed
```

and re-run with several seeds to estimate the selection variance. If your improvement
falls within the selection variance, it is not an improvement.

## Worked Numbers

Extraction task, `I = 100`, `D = 60`, `Q = 30`.

| k | tokens | accuracy (model) | tokens/correct |
|---|--------|------------------|----------------|
| 0 | 130 | 0.86 | 151 |
| 2 | 250 | 0.89 | 281 |
| 4 | 370 | 0.905 | 409 |
| 8 | 610 | 0.92 | 663 |
| 16 | 1,090 | 0.925 | 1,178 |

With prefix caching at `h = 0.9`, `alpha = 0.1`, and the demonstrations inside the
stable prefix, the *marginal* cost per demonstration drops to `60 * 0.1 = 6` tokens, so
k=16 becomes cheap. Without caching, k=4 is the clear choice. **The optimal k depends on
your caching setup**, which is why prompt and infrastructure decisions have to be made
together.

Chain-of-thought variant: 4 reasoning tokens per step, 5 steps = 20 extra output tokens
(~$0.0003 at $15/M), and accuracy on multi-step arithmetic jumps from ~0.55 to ~0.85.
Cost per correct answer: `(130+20)/0.85 = 176` vs `(130+20)/0.55 = 273` — CoT *lowers*
cost per correct answer despite more tokens. The lesson: measure cost per correct
outcome, not cost per request.

## Self-Check Questions

1. Compute cost per correct answer for k=0, 4, 8 at 1.3 tokens/char on a 400-char prompt.
2. Derive `P(majority correct)` for k=9 and p=0.55.
3. Show that a 5-shot prompt with 3 points of position variance can swamp a 2-point improvement.
4. Compute the caching break-even prefix fraction for a 2x token reduction.
5. Explain why CoT can reduce cost per correct answer.