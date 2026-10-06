# Model Evaluation - Flashcards (60 cards)

**Track:** ml  |  **Lab:** lab10  |  **Level:** Intermediate

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
| 1 | Why is accuracy misleading on imbalanced data? | Predicting the majority class gives high accuracy while catching none of the rare positives. |
| 2 | Precision and recall describe what? | Precision: of those flagged, how many were right. Recall: of those positive, how many were caught. |
| 3 | When should you quote PR-AUC over ROC-AUC? | When positives are rare, because the false positive rate shrinks as the base rate falls and flatters ROC. |
| 4 | What does k-fold cross-validation assume? | Rows are i.i.d.; with time or groups you must split differently. |
| 5 | Why must preprocessing be fit inside the training fold? | Otherwise the test fold's distribution leaks into the model and the score is optimistic. |
| 6 | What is average precision? | The area under the PR curve computed from precision at each recall level; a better summary than AUC on rare positives. |
| 7 | How do you choose a classification threshold? | From the cost of each error type, not from 0.5 and not from the metric you report. |
| 8 | Why report an interval on a metric? | Because a 0.3% difference on 200 samples is usually noise; the interval tells you whether it is real. |
| 9 | What is The confusion matrix is the source of truth? | TP, FP, FN, TN determine every classification metric. |
| 10 | What is Why accuracy is a trap? | At a 1% fraud base rate, predicting 'never fraud' gives 99% accuracy and catches nothing. |
| 11 | What is ROC versus precision-recall? | ROC-AUC uses the false positive rate, which shrinks as the base rate falls, making ROC look optimistic on rare positives. |
| 12 | What is Cross-validation must match deployment? | k-fold assumes i. |
| 13 | What is Variance of your estimate? | A metric on 200 samples has a wide confidence interval. |
| 14 | What is Calibration versus discrimination? | AUC measures ranking. |
| 15 | In this lab, what does `Accuracy = (TP+TN)/N` mean? | Accuracy: misleading under imbalance |
| 16 | In this lab, what does `Precision = TP/(TP+FP)` mean? | Precision: of flagged, how many were right |
| 17 | In this lab, what does `Recall = TP/(TP+FN)` mean? | Recall / TPR: of true positives, how many were caught |
| 18 | In this lab, what does `F1 = 2PR/(P+R)` mean? | F1: harmonic mean; ignores TN |
| 19 | In this lab, what does `Fβ = (1+β²)PR/(β²P + R)` mean? | F-beta: weights recall when β > 1 |
| 20 | In this lab, what does `AUC = P(score_pos > score_neg)` mean? | ROC AUC: threshold-free ranking quality |
| 21 | In this lab, what does `AP = Σ (R_k − R_{k−1}) P_k` mean? | Average precision: PR summary; better than AUC when rare positives |
| 22 | In this lab, what does `CI ≈ metric ± 1.96 · SE` mean? | Normal CI for a proportion: rough interval on a metric estimate |
| 23 | You see 'Accuracy 99%, recall 0' in production. What is the cause and the fix? | 1% positive class and an untrained baseline Fix: always print the confusion matrix and compare with a trivial predictor |
| 24 | You see 'Validation score better than the holdout score' in production. What is the cause and the fix? | preprocessing or feature selection done before splitting Fix: move every fitted step inside the fold and assert it |
| 25 | You see 'Time-series CV score far above reality' in production. What is the cause and the fix? | shuffled folds let the model see the future Fix: use forward-chaining splits and a final future-only holdout |
| 26 | You see 'Model A wins by 0.3% and you ship it' in production. What is the cause and the fix? | no interval on the estimate Fix: use repeated CV or bootstrap intervals and require a consistent win |
| 27 | You see 'ROC-AUC 0.95 on a rare-positive task, terrible precision' in production. What is the cause and the fix? | FPR shrinks with the base rate Fix: quote PR-AUC and precision at the operating point instead |
| 28 | You see 'Published result not reproducible' in production. What is the cause and the fix? | no seed recorded for splits or model init Fix: record seeds, folds and version every artifact |
| 29 | Which Java API is the backbone of: the single source of truth for every metric | `int[] confusionMatrix(y, yHat)` |
| 30 | Which Java API is the backbone of: rank-based ROC and PR computation | `Arrays.sort on scored predictions` |
| 31 | Which Java API is the backbone of: reproducible folds | `SplittableRandom with a recorded seed` |
| 32 | Which Java API is the backbone of: explicit, inspectable, serialisable folds | `record Fold(int[] train, int[] test)` |
| 33 | Which Java API is the backbone of: group-aware partitioning by entity id | `Collectors.groupingBy for grouped splits` |
| 34 | Why does The confusion matrix is the source of truth matter operationally? | TP, FP, FN, TN determine every classification metric. |
| 35 | Why does Why accuracy is a trap matter operationally? | At a 1% fraud base rate, predicting 'never fraud' gives 99% accuracy and catches nothing. |
| 36 | Why does ROC versus precision-recall matter operationally? | ROC-AUC uses the false positive rate, which shrinks as the base rate falls, making ROC look optimistic on rare positives. |
| 37 | Why does Cross-validation must match deployment matter operationally? | k-fold assumes i. |
| 38 | Why does Variance of your estimate matter operationally? | A metric on 200 samples has a wide confidence interval. |
| 39 | Why does Calibration versus discrimination matter operationally? | AUC measures ranking. |
| 40 | In the Model Evaluation pipeline, what happens next? Define the metric from the cost matrix before you look at an... | Define the metric from the cost matrix before you look at any numbers. |
| 41 | In the Model Evaluation pipeline, what happens next? Split with a protocol matching deployment: stratified k-fold... | Split with a protocol matching deployment: stratified k-fold, grouped, or time-based. |
| 42 | In the Model Evaluation pipeline, what happens next? Fit every preprocessing step inside the training fold.... | Fit every preprocessing step inside the training fold. |
| 43 | In the Model Evaluation pipeline, what happens next? Compute the confusion matrix, then all metrics from it; prin... | Compute the confusion matrix, then all metrics from it; print all of them. |
| 44 | In the Model Evaluation pipeline, what happens next? Plot the ROC and PR curves, and choose a threshold from the ... | Plot the ROC and PR curves, and choose a threshold from the cost matrix on validation folds. |
| 45 | In the Model Evaluation pipeline, what happens next? Report an interval, a baseline comparison, and the protocol ... | Report an interval, a baseline comparison, and the protocol you used — all three. |
| 46 | Exercise focus: Build the metric suite from scratch | Every metric from the four counts, cross-checked by hand. |
| 47 | Exercise focus: ROC and PR, both curves | See the difference a rare positive rate makes. |
| 48 | Exercise focus: k-fold done correctly | The fold strategy is where numbers are won or lost. |
| 49 | Exercise focus: Grouped and time-based splits | Handle the cases where i.i.d. is a lie. |
| 50 | Exercise focus: Threshold selection from costs | Turn business costs into an operating point. |
| 51 | Exercise focus: Confidence intervals on a metric | Know when your difference is real. |
| 52 | State the From counts to metrics result for Model Evaluation. | TP = 90, FP = 10, FN = 40: precision = 0.90, recall = 0.69, F1 = 0.78. Accuracy on a 1,000-row set with TN = 860 would read 0.95 while recall is below 0.7. |
| 53 | State the Accuracy versus imbalance result for Model Evaluation. | 1% positives, 10,000 rows: trivial accuracy 0.99. A model with recall 0.3 and precision 0.6 has accuracy 0.966 — worse than trivial, but far more useful. Accuracy hides that entirely. |
| 54 | State the ROC and PR curves result for Model Evaluation. | 1,000 rows, 10 positives. At recall 0.8, ROC shows FPR = 0.001 (one FP) — excellent. PR shows precision = 0.62, which is the number a reviewer actually experiences. |
| 55 | State the Average precision result for Model Evaluation. | 10 positives in 1,000 rows: AP = 0.71 while AUC = 0.94. The gap is the story — the model ranks well but its top-of-list precision is mediocre. |
| 56 | State the Variance of a metric estimate result for Model Evaluation. | Precision 0.80 on n = 100: SE = 0.04, so the 95% interval is 0.72–0.88. A 0.3% improvement over another model is far inside that noise. |
| 57 | State the Cross-validation variance result for Model Evaluation. | 10-fold CV on 5,000 rows estimates accuracy within roughly ±1%. Ten-fold instead of five changes the mean by about 0.1–0.3%, but a repeated 5-fold with 5 seeds tightens the reported interval noticeably. |
| 58 | What is F-beta for? | Weighing recall more heavily than precision (β > 1) or the reverse (β < 1) in a single number. |
| 59 | What is calibration and why does it differ from AUC? | Predicted probabilities matching observed frequencies; AUC only measures ranking, so a model can be well-ranked and badly calibrated. |
| 60 | How do you validate a time series model? | Forward-chaining splits plus a final holdout that is strictly later than anything used in training. |

## Deck Notes

- Rows are generated from this lab's own concepts, equations, failure modes and Java APIs - if you disagree with a card, fix the card.
- The last block of cards is deliberately operational: they are the questions a staff engineer gets asked in a design review.
