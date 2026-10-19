# SQL Fundamentals — Vision

## Direction
Grow from first queries toward dependable judgment about constraints, keys, and day-to-day DML, measured by artifacts rather than hours studied.

## Why it matters here
- Command of these guardrails turns on-call database surprises into routine checklist work.
- Concretely: NOT NULL plus CHECK constraints reject bad data at the gate.
- Concretely: INSERT, UPDATE, and DELETE change data while SELECT only reads it.

## Growth path
1. Foundations: rebuild the mini project starting from an empty schema.
2. Depth: extend one item (the student table with primary key and email uniqueness) until a reviewer asks for simplification.
3. Production: the restore drill gets recorded alongside the real-world milestones.

## Honest assessment
- Strong after this lab: reasoning about which constraints catch which bad rows, because the gatekeeping rules are explicit.
- Strong after this lab: applying the read-versus-write split during statement reviews.
- Still fragile: duplicate emails slipping past a missing unique constraint remains the most likely incident for beginners.
- Still fragile: enrollments pointing at deleted students after an unguarded delete still needs a senior eye on the design.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the enrollments row-count reconciliation after each edit.
- Stop treating the CHECK constraint that bounds grades to a legal range as optional when the review depends on it.

## Non-coverage
- This lab does not cover advanced analytics and procedural SQL; treat those as separate tracks.
- It also skips physical tuning and plan analysis, which belong to optimization tracks.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] Rebuild the seed schema on a blank host without peeking at notes.
- [ ] Explain the enrollment foreign key with a documented delete rule to a peer without notes.
- [ ] Trigger half-applied multi-statement edits committed without a transaction in staging, and recover using the runbook.
- [ ] Say where this groundwork ends and advanced analytics and procedural SQL begin in a design review.

## How to use this lab
Items go in order, scripts stay rerunnable, and the non-coverage boundary above is not crossed.
