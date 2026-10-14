# Common Mistakes - Experimentation

1. Peeking to an early stop. The first p < 0.05 in a daily check is
   often noise auditioning - hold the horizon or use sequential bounds.
2. Reading metrics before the SRM check. Broken splits produce
   beautiful, meaningless wins. Split first, always.
3. Sizing from hoped effects. Plan n from the smallest shippable effect;
   hope sizes underpowered tests.
4. p-value-only shipping. Without the CI you cannot tell +0.3pp from
   +2pp - report the range, decide on its low end.
5. Rescuing nulls by slicing. Post-hoc significant segments are
   hypotheses, not findings, until re-tested.
6. Ignoring the randomization unit. Session-level analysis of
   user-level randomization fakes precision - aggregate to the unit.
7. Shipping novelty spikes. Week-one curiosity is not product-market
   fit; require veteran-cohort persistence.
8. Goal tunnel vision. Guardrails veto: latency, refunds, abuse metrics
   outrank goal wins when they regress.
9. Moving the horizon mid-test. Extending "until significant" is peeking
   with extra steps - pre-commit or sequentially adjust.
10. No experiment log. Unlogged tests decay into folklore; log
    hypothesis, MDE, result, decision every time.

11. Sizing from the observed effect. Post-hoc "we had 90% power for what
    we saw" is circular - power plans the next test from the smallest
    meaningful effect, never justifies the last one.
12. Treating the CI as a probability. [0.0028, 0.0212] does not mean "95%
    chance the truth is inside" - it means the procedure covers 95% of the
    time. Decide from the range, not from a misreading.

Rule of thumb: if the log row (STEP_BY_STEP.md step 7) cannot be filled,
the test was theater - fill it or rerun it.

13. Averaging ratios across segments. Segment rates with different
    denominators do not average - aggregate counts first, then divide.
