# Naive Bayes Classifier - Code Deep Dive

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

## 1. Module Map

```text
src/com/ml/lab06/
  Main.java               driver: Iris-style continuous + small text corpus
  GaussianNB.java         per-class mean/variance, log-likelihood scoring
  MultinomialNB.java      token count maps, Laplace smoothing, log-space scores
  BernoulliNB.java        indicator model with document-length term
  TextVectorizer.java     vocabulary + counts fitted on the training split only
  Calibrator.java         Platt scaling on the log-odds score
```

All three variants share one scoring shape: build a per-class log likelihood, add the log prior, argmax. Keeping that skeleton identical is what makes the variants comparable in a benchmark.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `GaussianNB` | fit/predict/predictLogProb; per-class mu and sigma^2 arrays |
| `MultinomialNB` | per-class token->count maps plus smoothed log probabilities |
| `BernoulliNB` | per-class presence probabilities plus a document-length term |
| `TextVectorizer` | vocabulary, counts/indicators, fitted once on the training split |

---

## 3.1 Log-space scoring and the argmax that never underflows

Accumulate log likelihoods instead of products. The evidence term is dropped deliberately, with a comment saying so.

```java
public int predict(int[] tokenIds) {
    double[] score = new double[numClasses];
    for (int c = 0; c < numClasses; c++) score[c] = logPrior[c];
    for (int t : tokenIds) {                     // log space: sum, never product
        for (int c = 0; c < numClasses; c++) {
            Double lp = logProb[c].get(t);          // smoothed, so never null
            score[c] += (lp == null ? logUnseen : lp);
        }
    }
    int best = 0;                                  // argmax_c P(y=c)P(x|c); P(x) dropped
    for (int c = 1; c < numClasses; c++) if (score[c] > score[best]) best = c;
    return best;
}
```


---

## 3.2 Smoothing that keeps unseen tokens possible

Build the smoothed log-probability map once per class, including a single fallback value for tokens never seen in training.

```java
static Map<Integer, Double> smoothedLogProbs(Map<Integer, Integer> counts,
                                                   int totalTokens, int vocabSize,
                                                   double alpha) {
    Map<Integer, Double> out = new HashMap<>(counts.size() * 2);
    double denom = totalTokens + alpha * vocabSize;   // Laplace: (count + a)/(N + aV)
    for (Map.Entry<Integer, Integer> e : counts.entrySet())
        out.put(e.getKey(), Math.log((e.getValue() + alpha) / denom));
    return out;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Training, multinomial | `O(n·tokens)` | incrementally updatable as counts grow |
| Prediction, multinomial | `O(L·C)` | L = document length in tokens, C = classes |
| Gaussian NB prediction | `O(p·C)` | one quadratic term per feature per class |
| Training memory | `O(C·|V|)` | sparse maps; only observed tokens are stored |

## 5. Correctness and Numerics

- Always accumulate log-likelihoods; never multiply probabilities.
- Smooth with alpha = 1 and keep an explicit logUnseen fallback for unseen tokens.
- Guard zero variance in Gaussian NB (add a floor) or the likelihood explodes.
- Use n, not n−1, for per-class variance: the class is the population.
- Fit the vectoriser inside the training fold; a refitted vocabulary changes every score.

## 6. Test Strategy

- Predicting on training data returns the majority class at worst and perfect accuracy only if separable.
- A document containing a token absent from all training data still classifies without NaN.
- Log-space and probability-space scoring agree on a 3-token document to 1e-12.
- Vocabulary size is unchanged after refitting on a smaller corpus (no leakage).
- Predicting a 5,000-token document returns finite scores, not zeros.
- Bernoulli and multinomial variants produce different predictions on the same binary-flagged input.

## 7. Extension Points

- Add complement NB (which inverts the document order and often helps on imbalanced text).
- Implement NB-SVM: fit a logistic regression on the NB log-count ratio features.
- Add Platt calibration and report the ECE change.

## 8. Review Checklist

- [ ] Scoring happens in log space only
- [ ] Smoothing applied with a documented alpha and an unseen-value fallback
- [ ] Variant chosen explicitly, with the feature representation that requires
- [ ] Vectoriser fitted inside the training fold and versioned
- [ ] Per-class metrics reported, not only accuracy
- [ ] Posterior published only after calibration, or not at all
