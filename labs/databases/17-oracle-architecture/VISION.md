# Oracle Architecture — Vision

## Trajectory
Grow from first queries toward dependable judgment about what stops and what persists, measured by artifacts rather than hours studied.

## Payoff
- Command of the memory-and-files split turns on-call database surprises into routine checklist work.
- Concretely: the instance means memory plus processes while the database means files on disk.
- Concretely: tablespaces map logical segments onto physical data files.

## Milestones
1. Foundations: reproduce the mini project, beginning with a blank schema.
2. Depth: extend one item (the instance-versus-database diagram labeling memory and files) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about instance stop versus data loss, because the two meanings are now separated.
- Strong after this lab: applying the segment-to-file mapping during layout reviews.
- Still fragile: tablespace-full errors freezing employee inserts remains the most likely incident for beginners.
- Still fragile: instance-versus-database confusion during outage triage still needs a senior eye on the runbook.

## Anti-patterns to drop
- Do not reuse canned snippets until their results have been reproduced locally.
- Stop skipping the o_depts row-count reconciliation after each change.
- Stop treating the SGA-role note assigning caching duties to shared memory as optional when the review depends on it.

## Not covered
- This lab does not cover version-specific parameter names; treat those as separate tracks.
- It also skips proprietary dictionary view names, which differ by edition.
- The deliberate omissions: invented benchmarks, version trivia, and view names not our own.

## Checkable milestones
- [ ] Blank host first, then rebuild the seed schema from memory.
- [ ] Explain the tablespace map placing employee segments on named stores to a peer without notes.
- [ ] Trigger undersized shared memory starving concurrent sessions in staging, and recover using the runbook.
- [ ] Say where layout reasoning ends and version-specific parameter names begin in a design review.

## Working agreement
Follow the items in sequence, keep scripts rerunnable, and respect the non-coverage boundary stated above.
