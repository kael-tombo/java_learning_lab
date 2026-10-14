# Descriptive Statistics - Why It Matters

## Decisions ride on these numbers

Pricing bands use means, risk limits use sds, SLAs use quantiles, feature
selection screens on correlations. A variance computed with n instead of
n - 1 understates uncertainty by ~8% here (5.55 vs 6.00) - and every control
limit, interval, and capital buffer built on it inherits the shortfall.

## Skew changes the recommended action

Mean 10.57 says "typical is ten and a half"; median 9.0 says "half the cases
are nine or less". For capacity planning, staffing, or budgeting, the median
plus IQR (9.0, 6.5) is the operable pair when the tail (the 21) cannot be
served by average provisioning.

## Correlation screens features - and fools

r = 0.99 makes y nearly redundant given x: keep one, or combine them. But
the same 0.99 on curved or outlier-driven data would bless a false
relationship. The number matters because pipelines act on it automatically;
the scatter check matters because the number cannot see shape.

## Audit value of double reporting

Publishing mean with median, sd with IQR, r with n costs one line and buys
falsifiability: any reader can spot skew, tails, or small-sample hype. Teams
that standardize the pair-reporting rule catch distributional surprises in
review instead of production.

## The divisor line item

At n = 7 the n vs n - 1 choice moves variance 30.82 to 35.95, a 17% swing in
every interval and limit built on it. At n = 10,000 the swing is 0.01% and
nobody cares - which is exactly why the habit must form on small data, where
the mistake is big enough to see and the correction cheap enough to learn.

## Shape literacy compounds

Every later lab (EDA shape reading, feature skew, outlier triage) assumes
you can glance at mean/median/IQR/skew and picture the distribution. That
fluency is built here, on one dataset, until 10.57/9.0/6.5/0.58 reads as a
picture the way words read as meaning.

## Correlation gatekeeping

Automated pipelines select features, trigger alerts, and recommend actions
on r-like numbers. Knowing that 0.99 on n = 5 is suggestive - and that the
same 0.99 can hide curvature - is the difference between operating the dial
and being operated by it.
