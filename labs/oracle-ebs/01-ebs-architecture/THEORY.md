# Lab 01: EBS Architecture — Theory

## The Scenario

A 2,000-user EBS 12.2 instance degrades sharply during month-end. Requests that
normally complete in minutes take hours. The database reports 60% utilisation.
The application tier reports 100% CPU. The Concurrent Manager log shows
`JTF_QUEUE_LOCK` contention.

This looks like a performance problem. It is actually a **tier diagnosis** — and
the two utilisation numbers are the whole clue.

## Principle 1: Utilisation is only meaningful per tier

A number without a denominator is noise.

- 60% database utilisation on a *dedicated Exadata* during month-end is
  unremarkable. Exadata is sized for peak; 60% is a healthy operating point.
- 100% application tier CPU is saturation. There is no headroom left, so
  everything arriving queues.

The asymmetry is the finding: **one tier is saturated while the other has
slack.** That is a capacity placement problem, not a query problem.

## Principle 2: The queue is the system under study

A single Standard Concurrent Manager handles every class of request:

```
              ┌──────────────────────────────────┐
  requests ──►│  Standard Manager (N processes)  │──► execute
              └──────────────────────────────────┘
                            ▲
              JTF_QUEUE_LOCK serialises calendar
              booking and conflict resolution
```

Two things follow:

1. **Report storms compete with interfaces.** A manager user generating
   200 reports does not queue behind them in a separate lane — it queues in the
   same one. An interface that must run every 5 minutes is delayed by reports
   that nobody is waiting on.
2. **`JTF_QUEUE_LOCK` contention** appears when many workers simultaneously
   attempt to reserve or claim work. Each waits on a row lock; throughput
   collapses while CPU stays high because threads are **spinning on locks,
   not working**.

High CPU + poor throughput = contention. That combination is the fingerprint.

## Principle 3: More processes on one node is not more capacity

The tempting fix is to raise the CM process count. This fails because:

- The node is already at 100% CPU. More processes add context switching, not
  throughput.
- All processes still contend on the same lock.
- Single-node capacity has a hard ceiling regardless of process count.

The fix has to **add nodes** (horizontal capacity) and **separate queues**
(removing the contention), in that order.

## Principle 4: Specialisation isolates blast radius

```
Node 1: Standard CM + Report Manager    (heavy SQL, long-running)
Node 2: Interface Manager               (high volume, latency-sensitive)
Node 3: Batch Manager                   (scheduled, throughput-oriented)
```

Now a report storm cannot delay an interface, because they do not share a
queue. Each workload is sized independently and can be tuned without affecting
the others.

## Principle 5: Work shifts shape capacity over time

Not all work is equally urgent. Work shifts let you give priority hours more
capacity and off-hours less:

| Shift | Window (DB time) | Capacity | Rationale |
|-------|-----------------|----------|-----------|
| US peak | 08:00–18:00 | High | Interactive demand |
| EMEA peak | 02:00–12:00 | Medium | Offset by timezone |
| APAC peak | 19:00–05:00 | Low | Small user base |

Non-critical scheduled work is scheduled into the trough rather than competing
with peak demand.

## Principle 6: JTF clustering is the missing piece

Once requests run on multiple nodes, two workers on different nodes can attempt
to schedule the same job. **JTF clustering** (via the `JTF_CLUSTER` parameter
and cluster membership) coordinates reservation across nodes so calendar-based
conflict resolution works globally rather than per-node.

Without it, node cloning trades contention for **duplicate execution**.

## Principle 7: Measure the fix, do not assume it

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| App tier CPU (peak) | 100% | <60% | <60% |
| Avg CM wait (min) | ~180 | <30 | <30 |
| Request completion (month-end) | 400% baseline | Baseline | ≤100% |
| DB utilisation | 60% | ~65% | Acceptable |

The database number rising slightly is **expected and healthy** — it means work
that was previously stuck in a queue is now actually executing.

## Diagnostic Order

1. Which tier is saturated? (Compare utilisation per tier.)
2. Is throughput actually poor? (Completion time, not just CPU.)
3. What is the queue doing? (Depth, wait time, distribution.)
4. What are workers waiting on? (Lock contention vs CPU.)
5. How many queues exist? (One = specialisation opportunity.)
6. What is the fix, and is it reversible?

## Anti-Patterns

- Scaling up CM processes on a saturated node.
- Adding nodes without enabling JTF clustering.
- Blaming the database because it is the interesting component.
- Treating `JTF_QUEUE_LOCK` as an error to suppress rather than a symptom.
- Rolling out nodes all at once with no per-node validation.

## Summary

Month-end degradation was never a database problem. It was a single queue
serving every workload on a saturated node. The diagnosis came from comparing
utilisation **per tier**; the fix came from adding capacity horizontally and
isolating workloads into specialised queues, with JTF clustering ensuring the
nodes cooperate rather than collide.