# Data Wrangling - Why It Matters

## Biased inputs, biased outputs

A model trained on silently deduplicated-skewed or mean-filled data inherits
every shortcut. Mean imputation shrinks variance, so confidence intervals
built downstream are too narrow and reject the truth too often. Listwise
deletion under MNAR selects the respondents who answered, not the population
you claim to describe.

## Cost arithmetic

An hour of profiling (missing rates, reject counts, fence flags) regularly
saves days of debugging a model that "mysteriously" drifts after a feed
change. Reject logs are an early-warning system: a sudden jump in `"N/A"`
sentinels means the upstream form changed, caught at ingest instead of at
the board meeting.

## Trust and audit

Regulated work (finance, health, public policy) must show the lineage from
raw cell to reported number. The receipts this lab emphasizes - parsed vs
rejected counts, keys removed, fill values with filled counts, fence bounds -
are the minimum viable audit trail.

## Concrete stakes in the lab examples

- Filling the NaN with 6.0 keeps the column mean at 6.0; filling with 0
  would drag it to 4.8 and punish every average built on it.
- Keeping both copies of `c7|2026-01-05` double-counts that order in any
  revenue sum.
- Treating `"3x"` as 3 instead of rejecting it invents 3 units of whatever
  is being measured.
- Deleting 60.0 without review throws away either a typo or the outage.

## Small examples, large habits

The lab arrays fit on an index card precisely so every number can be checked
by hand. Analysts who learn receipts on five rows keep the habit on five
million; analysts who learn shortcuts on five rows automate them at scale.
The stakes above (4.8 vs 6.0, double-counted revenue, invented units) all
have production analogues measured in money and trust.
