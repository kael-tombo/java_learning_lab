# Model Monitoring - Reflection

## Core recall
- In one paragraph: Watching a deployed model and its data so regressions are caught after launch.
- Which of (data drift (input distribution changes), concept drift (the input-output relationship changes), label delay (ground truth arrives late so true quality is unknowable at first)) did you confuse before, and what distinguishes them now?
- Reproduce one snippet result from memory (value and reading), then check yourself.

## Decisions
- Name one decision you would now make differently: threshold, gate, rollout, or alert choice.
- What signal would tell you within a day whether that decision was right?
- What is the rollback path if it was wrong, and have you tested it?

## Tradeoffs
- What did you optimize, and what got worse as a side effect?
- Where is the capacity limit in your design: latency, reviewers, compute, or labels?
- Which simplifying assumption breaks first under ten times the load?

## Evidence
- Which numbers in your write-up are measured, and which are illustrative?
- What would you log to turn each illustrative number into a measured one?
- Write the follow-up question you still cannot answer; that is your next experiment.

## Transfer
- Name one idea from this lab that applies to a system you already operate.
- What is the smallest change that captures half the benefit?

## Monitoring-specific probes
- Define data drift, concept drift, and label delay without looking, with one example each.
- Write the PSI and KS definitions and state which needs binning.
- State the snippet values (PSI 0.0378, KS 0.250, P 0.300/R 0.750) and their readings.

## Alert audit
- List your paging rules and each rule's measured precision last month.
- Which rule would you demote to dashboard, and what re-promotes it?
- Which real incident had no page, and which monitor should have caught it?

## Slice coverage
- Name every slice you track and the owner who reads its chart.
- Which segment would break silently today? Add its microscope next.
- What cardinality cap keeps the comparator affordable at ten times volume?

## Maturity honesty
- Point at one provisional number you once quoted as official.
- What did it cost, and which maturity mark would have prevented it?
- Write the equal-maturity rule in one sentence for your runbook.
