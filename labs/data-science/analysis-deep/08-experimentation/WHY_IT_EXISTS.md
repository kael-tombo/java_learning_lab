# Why Experimentation Exists

Opinions about what users want are cheap and usually wrong - seniority
correlates poorly with predicting clicks. Before online testing, the
loudest voice or the prettiest mockup won, and failures were discovered
after full launch, at full cost.

Experimentation exists to replace authority with evidence at low risk:
expose 5% of traffic, measure the difference, decide with the interval.
Randomization manufactures the counterfactual (what these same users
would have done otherwise) that observational dashboards can never
supply, however large.

The surrounding machinery - guardrails, SRM checks, fixed horizons -
exists because the coin alone is not enough. Humans peek, slices get
trawled, splits break silently. Each practice in this lab patches one
observed way that smart teams fooled themselves with real experiments.

Without it, product development is fashion with analytics: trends,
gurus, and redesigns justified by before-after charts that credit every
tailwind to the change and every headwind to seasonality.

## A concrete scene

A checkout team ships one-click purchase on executive enthusiasm.
Conversion rises 2% - and refunds rise 9%, support tickets triple, and
the "win" costs more than it earns. No guardrails, no SRM check (a bot
filter misfired on control), no fixed horizon: three missing practices,
one expensive quarter.

## What method changes

Hypothesis pre-written, guardrails veto-powered, split checked before
metrics, horizon held past the novelty spike. The same feature then
reads correctly: +0.4pp conversion with flat guardrails - a modest ship
instead of a celebrated disaster followed by a quiet rollback.

## The alternative, priced

Full-launch failures cost migrations, apologies, and trust; botched
splits cost quarters of roadmap on phantom wins. A log row per test is
pennies against either - process is the cheap part, always.
