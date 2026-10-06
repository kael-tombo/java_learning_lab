# Naive Bayes Classifier

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

## 1. The Problem This Solves

You have few labelled examples, many features, and you suspect the features are roughly independent given the class.

Naive Bayes is the text-classification workhorse it has always been, and the cleanest place to see what conditional independence buys and what it costs.

## 2. Learning Objectives

- State the three Naive Bayes variants and what each assumes about feature type
- Derive Gaussian, multinomial and Bernoulli likelihoods
- Explain why the naive step is a modelling choice, not an implementation shortcut
- Implement Laplace (add-α) smoothing and see why unsmoothed estimates break
- Use log-space arithmetic so products of small probabilities do not underflow
- Know where NB beats logistic regression (small data, text) and where it loses

## 3. Core Concepts

### 3.1 The generative shortcut

Bayes' theorem flips the problem: instead of modelling P(y|x) directly, model the class-conditional densities P(x|y) and the prior P(y). With a naive assumption over features, each density factorises, and classification becomes counting.

### 3.2 Three variants, three data types

Gaussian NB assumes each feature is normal within a class (continuous data). Multinomial NB models feature *counts* (bag-of-words). Bernoulli NB models presence/absence (a document is a set of indicators). Using multinomial NB on binary flags, or Bernoulli on raw counts, quietly changes the model.

### 3.3 What 'naive' actually assumes

Conditional independence: P(xᵢ | y) = ∏ᵢ P(xᵢ | y). This is almost never true — 'bank' and 'loan' co-occur. It still works because the discriminative ranking survives small errors in the likelihood. Treat it as a bias that costs calibration and some accuracy, not as a fatal flaw.

### 3.4 Laplace smoothing

P(xᵢ = v | y = c) = (count(c,v) + α) / (N_c + α|V|) with α = 1. Without it, an unseen value in a class gives probability 0 and that class is excluded forever. Smoothing is what makes the classifier handle new vocabulary at all.

### 3.5 Log-space arithmetic

Multiplying 5,000 probabilities of 0.01 underflows a double long before you reach the last row. Summing log probabilities is exactly equivalent and never overflows. If you see p = 0.0 or NaN, this is why.

### 3.6 NB gives a posterior, but a poorly calibrated one

The posterior is nominal, so users expect it to be a probability. It is not: NB posteriors are famously overconfident, especially with correlated features and small training sets. Platt scaling on the NB log-odds fixes most of it for a few lines.

## 4. Key Equations at a Glance

| Symbol | Name | Meaning |
|---|---|---|
| `P(y=c | x) ∝ P(y=c) · P(x | y=c)` | Bayes' rule (proportional) | drop the evidence constant for argmax |
| `P(x | y=c) = ∏ P(xᵢ | y=c)` | Naive independence | the assumption that costs accuracy |
| `P(xᵢ | y=c) = exp(−(xᵢ−μ_cᵢ)²/2σ_cᵢ²)/(σᵢc√2π)` | Gaussian likelihood | continuous features |
| `P(x | y=c) ∝ ∏ᵢ count(c, xᵢ)` | Multinomial likelihood | term counts per class |
| `P(xᵢ | y=c) = (count + α)/(N_c + α|V|)` | Laplace smoothing | keeps unseen values possible |
| `log P(c) + Σᵢ log P(xᵢ | c)` | Log-posterior score | argmax is identical, numerically safe |
| `confusion matrix metrics` | precision / recall / F1 | text classification is imbalanced in practice |

## 5. How the Pieces Fit Together

1. Vectorise the input to counts (multinomial) or indicators (Bernoulli); the choice is the model.

2. Split stratified; keep the vocabulary fitted on the training fold only.

3. Compute per-class priors and feature likelihoods with smoothing.

4. Score in log space: log prior + Σ log P(feature | class), pick the argmax.

5. Evaluate with precision/recall/F1 and a PR curve; report per class, not just accuracy.

6. If probabilities matter, Platt-calibrate the log-odds score on a validation split.

## 6. Assumptions and Invariants

- Features are conditionally independent given the class
- The chosen variant matches the feature type (counts vs indicators vs continuous)
- The training set is representative of the deployment distribution
- Class priors in training reflect deployment; re-estimate them if they drift
- Enough examples per class for the likelihood estimates to be stable
- Smoothing is applied — unsmoothed NB is undefined on unseen values

## 7. Failure Modes You Will Meet in Production

| Symptom | Root cause | Fix |
|---|---|---|
| All posteriors print as 1.0 or 0.0 | multiplying many probabilities underflows a double | compute in log space from the start |
| The class with an unseen word is never predicted | unsmoothed zero likelihood | apply Laplace smoothing with α = 1 |
| Accuracy collapses after preprocessing | scaler or TF-IDF refit on the full dataset | fit the vectoriser inside the training fold |
| NB underperforms badly on small numeric data | correlated continuous features break the independence assumption | use logistic regression or a tree ensemble instead |
| Probabilities are wildly overconfident | NB posteriors are not calibrated | Platt-scale the log-odds; or only use the argmax |
| Multiclass numbers look implausible | using multinomial NB on binary indicators | use Bernoulli for presence/absence features |

## 8. Java Building Blocks

| API / class | Why it earns its place here |
|---|---|
| `HashMap<Integer, Double>` | per-class token log-probability maps in sparse form |
| `Math.log / Math.log1p` | log-space likelihood accumulation |
| `double[] classPriors` | the log-prior vector, one entry per class |
| `record Example(double[] numeric, int[] tokens, int label)` | carries all three feature views so variants stay comparable |
| `PriorityQueue for top-k terms` | explain a document by its highest-weight tokens |

## 9. Where This Sits in the Larger System

- **Lab 02** is the discriminative counterpart — compare them on the same small dataset.
- **Lab 09** applies the same log-odds idea with a much stronger learner underneath.
- **Lab 04** replaces the generative model with a margin, buying accuracy at the cost of data efficiency.
- **Lab 10** gives the F1 and PR-curve protocol that text classification actually needs.

## 10. Self-Assessment Before You Ship Anything

Score yourself 0-2 on each. Any zero below means you are not ready to operate this in production.

- [ ] 0 — cannot yet — State the three Naive Bayes variants and what each assumes about feature type
- [ ] 0 — cannot yet — Derive Gaussian, multinomial and Bernoulli likelihoods
- [ ] 0 — cannot yet — Explain why the naive step is a modelling choice, not an implementation shortcut
- [ ] 0 — cannot yet — Implement Laplace (add-α) smoothing and see why unsmoothed estimates break
- [ ] 0 — cannot yet — Use log-space arithmetic so products of small probabilities do not underflow
- [ ] 0 — cannot yet — Know where NB beats logistic regression (small data, text) and where it loses

## 11. Summary Checklist

- [ ] I can state which independence assumption each variant makes
- [ ] I never compute a posterior in probability space
- [ ] I always smooth, and can explain what α does
- [ ] I choose multinomial vs Bernoulli from the feature representation
- [ ] I know NB posteriors are uncalibrated
- [ ] I report per-class F1, not just accuracy
