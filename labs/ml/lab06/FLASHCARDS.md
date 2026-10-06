# Naive Bayes Classifier - Flashcards (60 cards)

**Track:** ml  |  **Lab:** lab06  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

**Format.** Question (front) -> answer (back). Use for spaced repetition: day 0, day 1, day 3, day 7, day 21. Do not read the answer first.

| # | Front | Back |
|---|---|---|
| 1 | Why is it called naive? | It assumes features are conditionally independent given the class, which is almost never true but is a useful bias. |
| 2 | Which NB variant fits TF counts? | Multinomial NB, which models the counts of terms per class. |
| 3 | Which variant fits document presence/absence? | Bernoulli NB, which models each term as an indicator and also uses document length. |
| 4 | Why compute in log space? | Multiplying thousands of small probabilities underflows to zero; summing logs is mathematically identical and numerically safe. |
| 5 | What does Laplace smoothing prevent? | A zero likelihood for an unseen value, which would permanently exclude that class. |
| 6 | Why is NB posteriors overconfident? | The independence assumption makes the likelihood product too sharp, so the posterior piles up near 0 and 1. |
| 7 | When does NB beat logistic regression? | Small training sets, high-dimensional text, and a need for a fast, stable, cheap baseline. |
| 8 | What is the evidence term P(x) and why is it dropped? | It is constant across classes for a given x, so it cannot change the argmax. |
| 9 | What is The generative shortcut? | Bayes' theorem flips the problem: instead of modelling P(y\|x) directly, model the class-conditional densities P(x\|y) and the prior P(y). |
| 10 | What is Three variants, three data types? | Gaussian NB assumes each feature is normal within a class (continuous data). |
| 11 | What is What 'naive' actually assumes? | Conditional independence: P(xᵢ \| y) = ∏ᵢ P(xᵢ \| y). |
| 12 | What is Laplace smoothing? | P(xᵢ = v \| y = c) = (count(c,v) + α) / (N_c + α\|V\|) with α = 1. |
| 13 | What is Log-space arithmetic? | Multiplying 5,000 probabilities of 0. |
| 14 | What is NB gives a posterior, but a poorly calibrated one? | The posterior is nominal, so users expect it to be a probability. |
| 15 | In this lab, what does `P(y=c \| x) ∝ P(y=c) · P(x \| y=c)` mean? | Bayes' rule (proportional): drop the evidence constant for argmax |
| 16 | In this lab, what does `P(x \| y=c) = ∏ P(xᵢ \| y=c)` mean? | Naive independence: the assumption that costs accuracy |
| 17 | In this lab, what does `P(xᵢ \| y=c) = exp(−(xᵢ−μ_cᵢ)²/2σ_cᵢ²)/(σᵢc√2π)` mean? | Gaussian likelihood: continuous features |
| 18 | In this lab, what does `P(x \| y=c) ∝ ∏ᵢ count(c, xᵢ)` mean? | Multinomial likelihood: term counts per class |
| 19 | In this lab, what does `P(xᵢ \| y=c) = (count + α)/(N_c + α\|V\|)` mean? | Laplace smoothing: keeps unseen values possible |
| 20 | In this lab, what does `log P(c) + Σᵢ log P(xᵢ \| c)` mean? | Log-posterior score: argmax is identical, numerically safe |
| 21 | In this lab, what does `confusion matrix metrics` mean? | precision / recall / F1: text classification is imbalanced in practice |
| 22 | You see 'All posteriors print as 1.0 or 0.0' in production. What is the cause and the fix? | multiplying many probabilities underflows a double Fix: compute in log space from the start |
| 23 | You see 'The class with an unseen word is never predicted' in production. What is the cause and the fix? | unsmoothed zero likelihood Fix: apply Laplace smoothing with α = 1 |
| 24 | You see 'Accuracy collapses after preprocessing' in production. What is the cause and the fix? | scaler or TF-IDF refit on the full dataset Fix: fit the vectoriser inside the training fold |
| 25 | You see 'NB underperforms badly on small numeric data' in production. What is the cause and the fix? | correlated continuous features break the independence assumption Fix: use logistic regression or a tree ensemble instead |
| 26 | You see 'Probabilities are wildly overconfident' in production. What is the cause and the fix? | NB posteriors are not calibrated Fix: Platt-scale the log-odds; or only use the argmax |
| 27 | You see 'Multiclass numbers look implausible' in production. What is the cause and the fix? | using multinomial NB on binary indicators Fix: use Bernoulli for presence/absence features |
| 28 | Which Java API is the backbone of: per-class token log-probability maps in sparse form | `HashMap<Integer, Double>` |
| 29 | Which Java API is the backbone of: log-space likelihood accumulation | `Math.log / Math.log1p` |
| 30 | Which Java API is the backbone of: the log-prior vector, one entry per class | `double[] classPriors` |
| 31 | Which Java API is the backbone of: carries all three feature views so variants stay comparable | `record Example(double[] numeric, int[] tokens, int label)` |
| 32 | Which Java API is the backbone of: explain a document by its highest-weight tokens | `PriorityQueue for top-k terms` |
| 33 | Why does The generative shortcut matter operationally? | Bayes' theorem flips the problem: instead of modelling P(y\|x) directly, model the class-conditional densities P(x\|y) and the prior P(y). |
| 34 | Why does Three variants, three data types matter operationally? | Gaussian NB assumes each feature is normal within a class (continuous data). |
| 35 | Why does What 'naive' actually assumes matter operationally? | Conditional independence: P(xᵢ \| y) = ∏ᵢ P(xᵢ \| y). |
| 36 | Why does Laplace smoothing matter operationally? | P(xᵢ = v \| y = c) = (count(c,v) + α) / (N_c + α\|V\|) with α = 1. |
| 37 | Why does Log-space arithmetic matter operationally? | Multiplying 5,000 probabilities of 0. |
| 38 | Why does NB gives a posterior, but a poorly calibrated one matter operationally? | The posterior is nominal, so users expect it to be a probability. |
| 39 | In the Naive Bayes Classifier pipeline, what happens next? Vectorise the input to counts (multinomial) or indicators (B... | Vectorise the input to counts (multinomial) or indicators (Bernoulli); the choice is the model. |
| 40 | In the Naive Bayes Classifier pipeline, what happens next? Split stratified; keep the vocabulary fitted on the training... | Split stratified; keep the vocabulary fitted on the training fold only. |
| 41 | In the Naive Bayes Classifier pipeline, what happens next? Compute per-class priors and feature likelihoods with smooth... | Compute per-class priors and feature likelihoods with smoothing. |
| 42 | In the Naive Bayes Classifier pipeline, what happens next? Score in log space: log prior + Σ log P(feature \| class), pi... | Score in log space: log prior + Σ log P(feature \| class), pick the argmax. |
| 43 | In the Naive Bayes Classifier pipeline, what happens next? Evaluate with precision/recall/F1 and a PR curve; report per... | Evaluate with precision/recall/F1 and a PR curve; report per class, not just accuracy. |
| 44 | In the Naive Bayes Classifier pipeline, what happens next? If probabilities matter, Platt-calibrate the log-odds score ... | If probabilities matter, Platt-calibrate the log-odds score on a validation split. |
| 45 | Exercise focus: Derive the multinomial NB score | Get from Bayes to the log-space scoring formula by hand. |
| 46 | Exercise focus: Prove the underflow | Show why probability-space scoring fails on real documents. |
| 47 | Exercise focus: Laplace smoothing end to end | See exactly what unsmoothed NB does with an unseen word. |
| 48 | Exercise focus: Implement all three variants | Compare them on data that suits each. |
| 49 | Exercise focus: Calibration for NB probabilities | Make the posterior publishable. |
| 50 | Exercise focus: Class imbalance and complements | Handle the case where the minority class matters. |
| 51 | State the Bayes' theorem and dropping the evidence result for Naive Bayes Classifier. | Two classes with prior-weighted likelihoods of 3.0 and 1.2: the argmax is class A. The actual posterior needs P(x) = 4.2, giving 0.714 — which is the only number you may publish. |
| 52 | State the Conditional independence result for Naive Bayes Classifier. | In spam data, P('free' and 'money' \| spam) ≈ 0.08, while the independent product gives 0.10. A 25% relative error per pair compounds across tokens, which is why NB overconfident. |
| 53 | State the Gaussian NB parameters result for Naive Bayes Classifier. | Class with x = 5, mu = 3, sigma = 2: -0.5 log(2 pi · 4) - 4/8 = -1.2655 - 0.5 = -1.7655. Class with sigma = 0.5: the same x becomes a much worse fit, which is why variance matters. |
| 54 | State the Multinomial NB with smoothing result for Naive Bayes Classifier. | Class with 100 tokens and vocabulary 50,000: an unseen token has theta = 1/50100 with alpha = 1, not 0. Without smoothing the class loses forever. |
| 55 | State the Underflow and log-space scoring result for Naive Bayes Classifier. | A 500-token document: probability-space product returns 0.0 for all classes. Log-space returns -4702.3 vs -4801.1 — a clear, correct difference. |
| 56 | State the Calibration error result for Naive Bayes Classifier. | Bins with confidence 0.95 average accuracy 0.80: ECE ≈ 0.15. After Platt scaling the same bins sit near the diagonal with ECE ≈ 0.02. |
| 57 | How do you get a calibrated probability from NB? | Platt-scale the log-odds score: fit a 1-D logistic regression on (log-odds, label) from a validation split. |
| 58 | Why does NB training cost nothing per feature? | Sufficient statistics: per-class totals and per-class feature counts. New data means incrementing counts. |
| 59 | What breaks if you mix up Gaussian and Multinomial NB? | Continuous values passed to a count model produce nonsense likelihoods; the model is silently wrong, not loudly. |
| 60 | How do you explain a NB decision? | Show the highest and lowest log-likelihood contributions per feature — the tokens that pushed the score each way. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
