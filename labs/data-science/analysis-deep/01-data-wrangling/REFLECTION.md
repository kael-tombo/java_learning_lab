# Data Wrangling - Reflection

## Check your judgment, not just your code

1. The column `{2, 4, NaN, 8, 10}` has mean-fill 6.0 and median-fill 6.0.
   Construct a 5-element column (one NaN) where mean-fill and median-fill
   differ by more than 5, and explain which fill you would defend.
2. Your IQR screen flags 60.0 but the z > 2 screen (with a larger sd) does
   not. Which do you trust, and what single plot would settle it?
3. A product manager asks to "just delete all rows with any missing cell"
   on a survey where income nonresponse tracks age. Write the two-sentence
   refusal, naming the mechanism.
4. The dedup key `(customer, date)` collapses a genuine double purchase.
   How would you detect this from the data, and what key change fixes it
   while still catching true reloads?

## Self-check answers (sketch)

1. Any right-skewed set works, e.g. `{1, 2, NaN, 3, 100}`: mean-fill 26.5
   vs median-fill 2.5. Defend the median unless the estimand explicitly
   needs the mean - the mean follows the 100.
2. Trust the IQR flag as the detection signal; the z-score suffers masking.
   A dot plot / strip plot of the ten values settles it in one glance.
3. "That deletion assumes MCAR, but nonresponse tracks observed age (MAR),
   so dropping rows selects younger respondents and biases income upward."
4. Same-key rows with different amounts, times, or line-item ids signal real
   doubles. Extend the key with the distinguishing field (amount, timestamp,
   line id) and log both outcomes before/after.

## Habits worth keeping

- Profile before touching anything; write the receipts after.
- Name the missingness mechanism in one sentence before choosing a remedy.
- Keep one example (like the 60.0) where you investigated a flag and were
  surprised - that memory prevents future auto-deletion.

## One more prompt

5. Your reject log shows `"N/A"` jumping from 1% to 30% overnight. List the
three most likely upstream causes in order, and state which single check
distinguishes a format change from a genuine nonresponse wave. (Answer
sketch: form/sentinel change, encoding or export change, real wave; compare
the jump against an unaffected column from the same source.)
