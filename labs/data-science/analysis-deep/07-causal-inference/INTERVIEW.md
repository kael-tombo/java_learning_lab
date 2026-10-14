# Interview Q&A - Causal Inference

Q: RCT vs A/B test - same thing?
A: An A/B test is an RCT applied to product changes; the logic
(randomize, compare means) is identical, the discipline around
guardrails and peeking differs by field.

Q: Show me Simpson's paradox from memory.
A: Mild: A 90/100 vs B 190/200 (B better); severe: A 10/100 vs B 90/200
(B better); pooled: A 100/200 vs B 280/400 (A better). Case-mix reversal.

Q: When is matching the wrong tool?
A: With unmeasured confounding or no covariate overlap - matching then
either leaves bias or extrapolates where no comparable units exist.

Q: Explain DiD and its assumption.
A: Double difference removing shared trends; needs parallel trends -
groups would have moved together absent treatment.

Q: Instrument relevance vs exclusion?
A: Relevance is testable (Z predicts treatment); exclusion (Z affects
outcome only via treatment) is argued from subject matter, never proven
statistically.

Q: What is a collider and why care?
A: A common effect of treatment and outcome; conditioning on it induces
bias. Classic trap: analyzing only hospitalized/severe subgroups.

Q: How do you report a causal number?
A: Estimate plus assumption in one sentence, with a sensitivity note on
fragility. No assumption, no claim.

Q: Parallel trends look violated pre-treatment. Next?
A: Stop the causal read; report the divergence, seek another control
group or design instead of proceeding.

Q: No overlap: all young treated, all old control. Match anyway?
A: No - matching extrapolates where no comparable units exist. Report
the overlap failure and restrict claims to the overlapping range, or
find another design.

Q: Significant confounded contrast, huge n. Impressed?
A: No: n shrinks the interval around the wrong number. Precision without
identification is decoration - fix the design, not the sample size.
