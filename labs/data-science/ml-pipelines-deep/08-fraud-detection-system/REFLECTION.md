# Fraud Detection System - Reflection

## Core recall
- In one paragraph: A worked system combining rules and a model to flag rare abusive transactions under tight latency.
- Which of (class imbalance (fraud is an order of magnitude rarer than legitimate traffic, far below 1% in typical settings), operating-point choice (threshold picked on precision/recall, not accuracy), cost asymmetry (a missed fraud generally costs more than one manual review, stated qualitatively)) did you confuse before, and what distinguishes them now?
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

## Fraud-specific probes
- Reproduce the snippet triple and cost ranking from memory, then verify.
- Write the expected-cost formula and name which term dominates each extreme.
- State the maturity curve endpoints and the equal-maturity comparison rule.

## Threshold audit
- Which threshold ships now, and which ratio and capacity bound chose it?
- What flag rate would overflow review, and which lever moves first?
- When was the ratio last refit, and whose numbers fed it?

## Adversarial readiness
- Which rule decayed last, and how fast did cover ship?
- Which shift would bypass every current rule, and what would catch it?
- When is the next scheduled rule and feature review, and who owns it?

## Latency honesty
- Which features ride inline versus async, and what each miss defaults to?
- What does decision p99 look like per class: block, review, pass?
- Which slow signal would you promote inline if the budget doubled?
