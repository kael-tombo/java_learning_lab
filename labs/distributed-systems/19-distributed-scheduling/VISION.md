# Distributed Scheduling - Vision

## The Big Picture
Scheduling means deciding *where* and *when* work runs. Distributed scheduling adds two
hard problems: exactly-once execution across a fleet that is not coordinating, and a
misfire policy when the scheduler itself is down and nobody noticed.

## Why This Matters
A scheduler is trusted infrastructure. When it silently skips a run, the failure surfaces days
later in a report nobody ran; when it double-runs, the failure surfaces as corrupted data.
Both are avoidable with claim semantics and a misfire policy.

## The Vision for This Lab
This lab builds scheduling the way production does — atomic claims, misfire policy, jitter, and
catch-up — and treats "the scheduler was down at 03:00" as a first-class scenario rather than
an edge case.

## Learning Philosophy
1. Claims, not locks — the database prevents double execution
2. Misfire policy is a business decision, stated per job
3. Jitter is a correctness feature for clustered schedulers
4. A scheduler with no state is a cron runner; a scheduler with state is a workflow engine

## Future Path
- 14-distributed-locks — what scheduling should avoid using
- 18-distributed-queues — the execution substrate
- 27-kafka-streams — stateful stream processing with its own scheduling

## Success Metrics
You have mastered distributed scheduling when you can:
- [ ] Implement atomic claim with no double execution under N schedulers
- [ ] Implement misfire policy: skip, fire-once, or catch-up-all, per job
- [ ] Add jitter and show the thundering-herd reduction
- [ ] Recover correctly after the scheduler is down past a fire time

## The Distributed Mindset
> Every fire time your scheduler misses is a decision you deferred. Write the misfire policy
next to the cron expression, not in a wiki nobody reads, and test the case where you were
asleep.