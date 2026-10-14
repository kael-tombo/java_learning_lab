# Data Wrangling - Theory

## 1. Missingness mechanisms

Let R be a response indicator (1 = observed, 0 = missing) and Y the data.

- **MCAR (missing completely at random):** P(R = 0) is independent of all
  data, observed or not. Dropping incomplete rows keeps estimates unbiased
  but wastes information.
- **MAR (missing at random):** P(R = 0) depends only on observed data.
  Example: income missing more often for young respondents, and age is
  recorded. Analyses conditioned on the observed predictors stay valid.
- **MNAR (missing not at random):** P(R = 0) depends on the missing value
  itself. Example: high earners skip the income question. No generic fix
  works; the mechanism itself must be modelled.

## 2. Imputation estimators

- **Mean imputation:** fill with the observed mean. Preserves the mean but
  shrinks variance and understates uncertainty.
- **Median imputation:** robust to skew and outliers; standard for long-tailed
  money variables.
- **Mode imputation:** the categorical analogue; fill with the most frequent
  level.
- **Forward-fill:** carry the last observation forward; only valid for ordered
  (usually time-indexed) data where persistence is plausible.
- **Deletion:** listwise deletion is unbiased only under MCAR.

## 3. Deduplication keys

A dedup key is a set of columns that functionally identifies one real-world
event, e.g. `(customer_id, order_date)`. Exact duplicates share the full key;
near-duplicates need normalized keys (trimmed, case-folded, canonical dates).
First-seen order is kept with an insertion-ordered map.

## 4. Type coercion

Parsing turns text into numbers under a strict grammar: optional whitespace,
optional sign, digits, at most one decimal point. Anything else - `"3x"`,
blanks, sentinels like `"N/A"` - is rejected and counted, never silently
dropped or coerced to zero.

## 5. Outlier rules

- **Tukey fences:** with quartiles Q1, Q3 and IQR = Q3 - Q1, flag values
  outside `[Q1 - 1.5 x IQR, Q3 + 1.5 x IQR]`.
- **z-score screen:** flag `|x - mean| / sd > k` (commonly k = 2 or 3).
  z-scores use the mean and sd themselves, so a huge outlier inflates the
  sd and can mask itself; the IQR rule resists this.

## 6. Guiding rule

Every cleaning choice changes the estimand. Record the rule, the count of
affected rows, and the before/after summary so the wrangling is auditable.
