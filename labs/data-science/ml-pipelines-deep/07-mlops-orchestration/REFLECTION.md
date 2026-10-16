# MLOps Orchestration - Reflection

## Core recall
- In one paragraph: Scheduling and connecting the steps that retrain, validate, and promote models.
- Which of (DAG orchestration (tasks as a directed acyclic graph with dependencies), scheduling (cron for fixed cadence, event triggers for new-data or metric-based runs), artifact lineage (pointers to data version, code commit, and parameters for every run)) did you confuse before, and what distinguishes them now?
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

## Orchestration-specific probes
- Draw the ingest-to-promote DAG from memory with triggers on each entry edge.
- Write the backoff formula and the gate conjunction without looking.
- State the four lineage pointers and what breaks when each is missing.

## Replay audit
- Which rerun diverged, and which unpinned input caused it?
- Which backfill touched a live path, and what versioning would have prevented it?
- Which validation failure retried instead of failing fast, and what did it cost?

## Gate calibration
- Which gate last vetoed a promotion, and was the veto correct?
- Which slice bar is tightest, and does its strictness match incident history?
- What single gate addition would have caught your last production surprise?

## Trigger fitness
- Which staleness bound governs each retrained model: clock or detection?
- Which arrival still races its cron tick, and what event would gate it?
- What zombie schedule might be running now, and how would you check?
