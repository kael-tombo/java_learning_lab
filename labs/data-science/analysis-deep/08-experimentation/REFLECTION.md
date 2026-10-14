# Reflection - Experimentation

## Self-check prompts

- Can I write the two-proportion SE from memory and explain each term?
- Given d with a CI, do I decide from the interval's low end, not p?
- Do I run the SRM check before any metric, every time?
- Can I state the 1/sqrt(n) law and what it costs to halve an MDE?
- Do I pre-commit horizon and ship threshold before launch?

## What surprised you

Many learners expect 2x traffic to halve error; it quarters the need
(4x halves). Write two sentences on how the SampleSize table changed
your intuition for test planning.

## Peeking audit

Recall a time you (or a dashboard) watched a metric "until it crossed."
Rewrite that episode with a fixed horizon and an SRM gate - what would
have changed about the decision and its credibility?

## Next step

Pick one: run the peeking simulation (Exercise 4) and quote your
observed false-positive fraction, or size a real upcoming test from its
smallest shippable effect. Numbers first, opinions after.

## Teach-back test

Explain the 4x-for-half law to a colleague using only the SampleSize
rows (0.0376 at 1000 down to 0.0047 at 64000) and the telescope metaphor.
If they can price a halved MDE in traffic before you finish, it landed.

## Commitment line

Write one sentence starting "In my next test I will..." naming one guard
(SRM first, fixed horizon, CI-based decision). Sign and date it; vague
resolutions do not count.

## Mistake journal

Log every testing mistake with the violated checklist item and its cost
in traffic-days. After ten entries the costliest item owns your next
month - usually peeking or skipped SRM, priced honestly at last.
