# Interview Q&A - Experimentation

Q: Walk me through your A/B anatomy.
A: Hypothesis, randomization unit, control, goal metrics to decide,
guardrails to veto, fixed horizon, SRM gate before readout.

Q: p = 0.04 - ship it?
A: Show me the CI and the MDE first: 0.04 with CI [0.0001, 0.05] is a
maybe-tiny effect; the p-value alone never ships.

Q: What is peeking and why does it matter?
A: Repeated interim looks with early stopping inflate false positives
(single 0.05 looks compound toward ~26% at six independent peeks).

Q: SRM flagged but goals look great. Call?
A: Void the test: broken assignment breaks the causal license no matter
how pretty the metrics are. Fix the split, re-run.

Q: How do you size a test?
A: Smallest meaningful effect -> MDE -> n via 2.8*SE at 80%/5%;
convert n to days from traffic, negotiate scope before launch.

Q: Novelty effect suspected. Handle?
A: Extend past the spike, segment veterans vs newcomers, require the
effect in the veteran cohort.

Q: Goal up, guardrail red. Ship?
A: No: guardrails veto. A conversion win with surging refunds or
latency is a loss wearing a costume.

Q: Slice shows significance after overall null?
A: Treat as hypothesis for the next test, not a rescue - multiplicity
accounting applies before any claim.

Q: Ramp 90/10, SRM computed vs 50/50 flags. Bug?
A: Yes in the check, not the traffic: E must come from the planned 90/10
ratio. Recompute against plan before touching the assignment code.

Q: Both arms convert 0/5000 after a tracking deploy. Readout?
A: No readout: zero information, not a zero effect. Fix tracking, then
relaunch - a p-value over broken telemetry measures nothing.
