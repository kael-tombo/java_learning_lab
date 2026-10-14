# How A/B Testing Works

## 1. Write the hypothesis and the decision rule

One sentence on what changes and which goal metric moves, plus the
ship threshold (e.g. "+1pp conversion with no guardrail regression").
Unwritten rules get rewritten after seeing data - that is p-hacking.

## 2. Size the test

Pick the smallest meaningful effect, set 80% power / 5% significance
by convention, and convert to runtime from traffic. If the calendar
says six weeks for a 0.5pp MDE, negotiate scope now, not mid-test.

## 3. Randomize and monitor health only

Launch 50/50 (or the planned ratio), watch guardrails and the SRM
check - never the goal p-value. A broken experience or a skewed split
stops the test; a promising p-value does not.

## 4. Hold the horizon

Run the pre-planned duration covering weekly cycles. Novelty spikes in
week one and weekend effects both punish early readers; the fixed
horizon is what makes the final p-value mean what it says.

## 5. Analyze once, with intervals

Compute d, SE, p, and the 95% CI. Check SRM first: a flagged split
voids everything below it. Then read goal vs guardrails jointly - a
conversion win with a refund surge is not a win.

## 6. Segment to explain, not to rescue

Cut by platform or cohort to understand a result, never to hunt a
significant slice after an overall null. Each slice claim needs its own
multiplicity accounting.

## 7. Ship, iterate, or kill - with a log

Record hypothesis, dates, n, MDE, result, decision. The log compounds
into institutional memory: which ideas move metrics and which
"almost worked" three times running.

## Worked trace on AbTest numbers

Planned 50/50 at n = 10000/arm, MDE ~0.013. Observed split passes SRM,
d = 0.012 with CI [0.0028, 0.0212]: significant, but the low end misses
a +1pp ship threshold - decision: iterate, not ship. The interval, not
the p-value, made the call.

## When to stop arguing

Stop when the CI sits wholly above threshold (ship), wholly below (kill),
or straddles it after full horizon (declare null, log, move on). A fourth
option - "run longer until it crosses" - is peeking, explicitly banned.
