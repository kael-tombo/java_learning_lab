# PL SQL Foundations — Vision

## Where this points
Grow from first queries toward dependable judgment about subprogram design and transaction boundaries, measured by artifacts rather than hours studied.

## Capabilities gained
- Command of these constructs turns on-call database surprises into routine checklist work.
- Concretely: procedures perform actions while functions compute and return values.
- Concretely: IN, OUT, and IN OUT modes define parameter direction.

## Sequence
1. Foundations: the mini project gets reproduced after clearing the schema.
2. Depth: extend one item (the shift procedure assigning one staff member explicitly) until a reviewer asks for simplification.
3. Production: deliver the real-world milestones and keep a restore drill on file.

## Honest assessment
- Strong after this lab: reasoning about the action-versus-computation split, since each subprogram type has one job.
- Strong after this lab: applying parameter-direction rules during call-site reviews.
- Still fragile: functions with hidden commits breaking caller transactions remains the most likely incident for beginners.
- Still fragile: OUT parameters masking failed computations with stale values still needs a senior eye on the design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the f_shifts row-count reconciliation after each change.
- Stop treating the parameter-mode table documenting each argument direction as optional when the review depends on it.

## Out of scope
- This lab does not cover advanced package hierarchies; treat those as separate tracks.
- It also skips version-specific compiler settings, which sit outside subprogram fundamentals.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host without peeking at notes.
- [ ] Explain the bonus function computing pay from shift count to a peer without notes.
- [ ] Trigger partial rosters persisting after a missing ROLLBACK in staging, and recover using the runbook.
- [ ] Say where subprogram fundamentals end and advanced package hierarchies begin in a design review.

## Study guidance
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
