# Reflection: JIT Compilation

## What surprised you?

Most learners expect compilation to be one event. The log shows two
promotions (tier 3, then tier 4) separated by thousands of invocations.
Which of your mental benchmarks assumed a single "compiled" state, and
how does a two-stage pipeline change their warmup story?

## Threshold check

Without looking: which tier is C1 with profiling, and which number (200
or 5000) belongs to it? If you answered "tier 3, 200", the pipeline is
yours. If you hesitated, re-read the THEORY table before moving on —
every later file assumes that mapping.

## Your own hot spot

Name one method in a project you maintain that likely crosses tier 4 in
production (a serializer, a loop kernel, a predicate). What evidence
would confirm it — which flag, which log line, which column? What would
you do differently if the line never appears?

## Deoptimization in your words

Explain the uncommon-trap round trip (compiled -> interpreter ->
recompile) to a colleague in three sentences, naming the qualitative
cost (interpreter round trip plus recompile) without inventing timings.
Where in your system would a burst of traps most plausibly originate?

## One experiment you will run

Pick one: cap tiers at 1 and re-measure a service test, halve
`Tier4InvocationThreshold` and watch promotion order shift, or trace
deoptimization around a deploy. Write down the predicted log diff before
running — the habit of predicting the log is the skill this lab teaches.

## Thresholds from memory, then verified

Cover the table and recite: 200/5000 invocation pair, 60000/40000
back-edge pair, 2000/15000 compile-threshold scalers, 35/325 inline
budgets. Then run `PrintFlagsFinal` and check every digit. The point is
not memorization but learning which numbers live in flags (all of them)
and which live in folklore (none of them).
