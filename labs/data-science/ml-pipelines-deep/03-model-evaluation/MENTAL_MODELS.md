# Model Evaluation — Mental Models

## 1. Matrix first, rates second
The matrix is the receipt; rates are summaries of the receipt. Anyone
quoting F1 without the four counts is asking you to trust their
summarization of your error distribution.

## 2. Two questions, two metrics
Precision asks "when you cried wolf, was there a wolf?" Recall asks
"when there was a wolf, did you cry?" F1 refuses to let one good
answer excuse a bad one — that is the harmonic mean doing its job.

## 3. Ranking vs deciding
ROC-AUC grades the whole ranking across thresholds; the operating
threshold decides who gets flagged tonight. A great ranking with a bad
threshold still fails the shift. Evaluate both.

## 4. Honest uncertainty scores best
Proper scores are lie detectors for probabilities: hedging toward the
truth pays, bluffing costs. In this lab's demo the modest forecaster
beats the confident one by 0.642 in log-loss (1.0657 vs 0.4240) — the
price of one confident error, measured, not argued.

## 5. Locks on the test set

## 5. Locks on the test set
The test set is a safe with one opening per candidate. Validation is
the workshop where you iterate freely. Preprocessing fitted on test
data is picking the lock from the inside — and the safe knows.
Count openings; budget them like any scarce resource.
