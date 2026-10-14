# Data Wrangling - How It Works

## The cleaning pipeline in order

1. **Profile first.** Count rows, count missing per column, list distinct
   types seen in each text column. Nothing is changed yet.
2. **Audit missingness.** For each column compute the missing rate and ask
   which mechanism (MCAR, MAR, MNAR) is plausible given how the data was
   collected. The mechanism picks the remedy.
3. **Coerce types.** Parse text to numbers or dates with a strict grammar.
   Rejects are collected with reasons, and the accepted/rejected counts are
   reported. Parsing happens before imputation because a reject is itself
   a form of missingness.
4. **Deduplicate.** Build the composite key per row and keep the first row
   per key. Report `input rows`, `unique keys`, `removed`.
5. **Impute.** Fill remaining gaps with the chosen estimator (mean, median,
   mode, forward-fill). Fit the estimator on observed values only.
6. **Triage outliers.** Apply the 1.5 x IQR fences, then a z-score screen as
   a second opinion. Flags are reviewed, not auto-deleted: a flag can be a
   data error or the most interesting row in the file.
7. **Validate.** Recompute row counts, missing counts (should be zero or
   explicitly accepted), and summary statistics. Compare before/after means.

## Why this order matters

Dedup before imputation, because duplicated rows would overweight the mean
used for filling. Coercion before missingness counts, because rejects add to
the missing tally. Validation closes the loop: the pipeline output must show
its own receipts (counts at every stage).

## State carried between stages

- The reject log (value plus reason) from coercion.
- The set of seen dedup keys.
- The fitted fill value (e.g. mean 6.0) plus how many cells it filled.
- The fence bounds and the flagged values for review.
