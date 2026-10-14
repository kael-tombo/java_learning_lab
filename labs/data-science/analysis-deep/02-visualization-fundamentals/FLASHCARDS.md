# Visualization Fundamentals - Flashcards

## Q1. Which chart for one categorical variable?

A: Bar chart of counts/proportions with a zero baseline; length encodes
value against a common origin.

## Q2. Which chart for one continuous variable?

A: Histogram (binned counts) for larger n; dot plot when every value can be
shown individually.

## Q3. What is the Anscombe lesson in one sentence?

A: Four datasets share mean x 9, mean y 7.5, correlation 0.816 yet graph
utterly differently - summaries underdetermine shape, so plot first.

## Q4. Why must bar axes start at zero?

A: Otherwise equal lengths misrepresent unequal values; truncation turned
5.8 vs 6.1 (5% apart) into visual drama.

## Q5. Why avoid dual y-axes?

A: Each axis rescales independently, so crossings and leads are artifacts of
the chosen ranges, not findings.

## Q6. Name three overplotting mitigations.

A: Alpha blending (transparency shows density), jitter (separates ties),
binning into counts or cell means.

## Q7. What do the lab histogram counts sum to, and why check?

A: 1+5+3+0+1 = 10 = n. Reconciliation proves every value landed in exactly
one bin.

## Q8. Why print empty bins?

A: The zero-count [6,8) bin shows the gap between bulk and outlier; hiding
it deletes a finding.

## Q9. What are binned means estimating?

A: E[y | x in cell]: the cell averages 3.0, 4.5, 6.5, 8.0 trace the trend
like a regressogram.

## Q10. Same mean 6.0, sds 0 / 3.16 / 5.66 - what does the sd tell you?

A: Spread differs (flat, slope, outlier pair), but only plotting resolves
which shape produced the spread.

## Q11. When is a log scale appropriate?

A: Multiplicative relationships spanning orders of magnitude - labelled
loudly, since equal distances mean multiplication.

## Q12. Proportion plus what?

A: Always the denominator: 3/8, not 37.5% alone, so the reader sees n = 8
behind the estimate.

## Q13. What breaks if bin edges change between compared groups?

A: Comparability - different binnings manufacture shape differences, so fix
one scale for all panels.

## Q14. How do text charts stay honest?

A: Edges, counts, and n are printed explicitly - no hidden defaults for a
library to choose silently.
