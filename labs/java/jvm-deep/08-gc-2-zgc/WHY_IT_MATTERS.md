# Why It Matters: ZGC

Measured STW handshakes of 0.010-0.026 ms sit roughly two orders of
magnitude below G1's 2-5 ms young pauses on comparable churn — the gap
snippet 3 of lab 09 quantifies as 10x-or-better with margin. For p99
budgets under a millisecond, that gap is the difference between meeting
the SLO with the collector and meeting it despite the collector.

Heap-size independence changes capacity planning: terabyte heaps stay
viable because pauses track root size, not heap size. The constraint
shifts to allocation headroom — sustained allocation past the concurrent
budget stalls, so size for relocation slack rather than minimal
footprint, and watch allocation-stall counters instead of pause charts.

Observability splits in two by design: `ZGC Minor/Major Pauses` beans for
latency dashboards, `ZGC Minor/Major Cycles` beans for reclamation rate.
A G1-keyed dashboard (`G1 Eden Space` pools) goes blind here; the lab's
`ZBeans` probe is the migration checklist for monitoring, showing the
young/old pool pair that replaces the Eden/Survivor/Old triple.

The warmup major and the timer are operational facts: expect one major at
every startup (commissioning, not pressure — do not page on it), and use
`ZCollectionInterval` deliberately for idle-between-bursts services while
leaving it off (default 0) everywhere else. Misreading either as
pathology causes the two most common false alarms in ZGC triage.

Headroom sizing is the capacity corollary: because stalls, not pauses,
are the failure mode, the plan tracks free slack and allocation rate
against concurrent drain rather than minimizing footprint. A ZGC heap at
80% steady occupancy with bursty producers is riskier than one at 50%
with smooth allocation — the occupancy number alone never tells the
story, and the stall counters exist to complete it.

Dashboards should therefore pair a Pauses panel (latency truth, tens of
microseconds) with a Cycles/stall panel (reclamation and headroom truth)
rather than averaging either into a single health number. Two panels, two
questions, no blended metric hiding the failure mode that actually bites.
