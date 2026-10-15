# Model Evaluation — Flashcards

Q: The four confusion-matrix cells?
A: TP label1/pred1, FP label0/pred1, TN label0/pred0, FN label1/pred0.
Demo: 4/1/4/1.

Q: Precision and recall formulas?
A: Precision = TP/(TP+FP) = 0.8; recall = TP/(TP+FN) = 0.8 on the demo.

Q: F1 formula and demo value?
A: F1 = 2PR/(P+R), harmonic mean of precision and recall; demo
0.8000000000000002 (fp representation of 0.8).

Q: Why harmonic instead of arithmetic mean?
A: It punishes a weak side harder: P=1.0, R=0.2 gives F1 0.33, not 0.6.

Q: What does ROC-AUC measure?
A: Ranking quality across all thresholds (1.0 perfect, 0.5 random) —
not quality at the operating threshold.

Q: Why do PR curves lead on imbalanced data?
A: FPR divides by the huge negative count and looks small; precision
divides by predicted positives and exposes weak detection.

Q: Log-loss and Brier formulas?
A: Log-loss = mean -[y log p + (1-y) log(1-p)]; Brier = mean (p-y)^2.
Demo: 0.23617/0.055 vs 0.69314/0.25 baseline.

Q: What does "proper scoring rule" mean?
A: Expected score is optimized by predicting true probabilities —
honest uncertainty scores best.

Q: What is calibration?
A: Predicted-q items are positive at rate q. Separate from sharpness
(confident, spread predictions).

Q: Stratified K-fold in one sentence?
A: Round-robin allocation per class so each fold keeps the overall
class ratio; demo preserves 0.4 positives in both folds.

Q: The leakage-via-preprocessing rule?
A: Fit preprocessing on train only; applying all-data-fitted
transforms to val/test inflates scores.
