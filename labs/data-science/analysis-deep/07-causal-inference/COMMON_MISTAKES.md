# Common Mistakes - Causal Inference

1. Reading correlation as causation. Co-movement is the start of the
   investigation, shared with two rival explanations, not its end.
2. Pooling over a confounder. Different case-mix across arms reverses
   verdicts - stratify first, pool never (until strata agree).
3. Matching on unmeasured hope. Propensity methods balance measured
   covariates; unmeasured ones ride through untouched.
4. Asserting parallel trends. Plot pre-periods; divergence falsifies,
   parallelism merely permits.
5. Conditioning on colliders/mediators. Adjusting for post-treatment
   variables or common effects manufactures bias.
6. Instrument without exclusion argument. Relevance alone is a strong
   predictor, not a valid instrument - exclusion needs subject matter.
7. Generalizing local effects. Discontinuity effects live at the cutoff;
   far populations need their own design.
8. Hiding fragility. If a mild unmeasured confounder erases the result,
   that fragility is a headline finding, not a footnote.
9. Confusing significance with causation. A tiny p-value on a confounded
   contrast measures precision of the wrong number.
10. Dropping the assumption sentence. Every causal claim ships with its
    license printed alongside - no exceptions, no appendices.

11. Stratifying on post-treatment variables. Recovery ward is caused by
    treatment - conditioning there reintroduces selection under a new name.
12. Quoting subgroup effects as population effects. Discontinuity and
    matched-subset estimates travel with their population label attached.

Rule of thumb: cover the assumption sentence and the claim must become
unreadable - if it still reads fine, the assumption was decoration.

13. Demanding mechanism before effect. Trials establish whether before
    why - refusing to act until the pathway is mapped stalls decisions
    the design already earned.
14. Asymmetric skepticism. Scrutinizing only unwelcome results while
    waving through congenial ones is advocacy with a checklist - apply
    the assumption audit to both.
