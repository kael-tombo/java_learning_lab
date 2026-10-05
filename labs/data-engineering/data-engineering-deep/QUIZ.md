# QUIZ — 15 Questions

Judgement, not recall. Where a question has more than one defensible answer,
the marking note says what the reasoning must contain.

---

**Q1.** A Flink job is doing 2.4TB of keyed state and its checkpoints take 40
seconds with frequent failures. The business needs state retained for 400 days.
Name the two changes with the biggest effect, in order.

<details><summary>Marking</summary>
(1) Reduce state, not increase the checkpoint interval. Replace history
(`ListState` of events, O(n) scans) with bucketed aggregates plus a TTL
(2.4TB to ~340GB in the referenced case). (2) Switch to an incremental
checkpointing state backend so checkpoint cost tracks changed state, not total.
Accepting a longer interval is the *consequence* of fixing those two, and
doing it first is the common mistake: it just means 40s of lost work per
failure.
</details>

---

**Q2.** A producer sets `acks=all` and RF=3, but a broker is 3 minutes behind
before a leader election. Is a write acknowledged by the old leader durable?

<details><summary>Marking</summary>
Not necessarily. `acks=all` means "all replicas in the current ISR". If the
lagging broker is not in the ISR, the write is acknowledged without it, and if
that broker later becomes leader you can lose the record. Durability here
requires `min.insync.replicas=2`, which forces the ISR to shrink and makes the
write fail rather than silently accept. The correct answer names the ISR
membership, not just "RF 3".
</details>

---

**Q3.** Your hourly revenue feed disagrees with billing by 4% at peak only,
0.1% off-peak. The code has not changed. Rank three hypotheses and give the
first test for the top one.

<details><summary>Marking</summary>
(1) Producer-dependent lateness: the ad/impression producer flushes on a
timer, so at peak the arrival-to-event lag grows beyond the watermark bound and
late records fall into the next window. Test: plot the distribution of
`arrival_time - event_time` at peak vs off-peak, and check whether the gap
moves when you widen the bound. (2) A peak-time filter or threshold in the
pipeline. (3) Back-pressure at peak causing partial consumption. Ranking
matters more than the list: the first test must discriminate hypothesis 1.
</details>

---

**Q4.** A `MERGE` on a 2.1B-row fact table takes 6 hours and blocks the hourly
refresh. Is this a tuning problem?

<details><summary>Marking</summary>
No. It is a scoping problem. The MERGE cannot state which files it will touch,
so it rewrites the table. The fix is to make the scope bounded: partition so
the predicate's leading key selects whole files, and pre-aggregate at the
source if the hot key is itself the result of missing an earlier sum. Tuning
the cluster makes it finish in 4 hours, not in minutes.
</details>

---

**Q5.** You replaced a processing-time job with an event-time job and the
reported numbers changed by 6%. Which is now correct?

<details><summary>Marking</summary>
Neither is automatically right; the event-time one is *more defensible*. The
processing-time job was silently mis-attributing late records to the wrong
period, which is a correctness bug, not a definition. The response must be to
reconcile: if the batch job also uses event time and agrees, the streaming job
was wrong before. If the batch also uses processing time, both were wrong in
the same direction and you have just found a systematic mis-attribution in
every historical report.
</details>

---

**Q6.** A topic has 1 partition and feeds a Flink job with parallelism 96. What
is the throughput ceiling, and what is the fix?

<details><summary>Marking</summary>
Ceiling is that of one partition: one producer-side append stream, one
consumer. The job runs at parallelism 1 and 95 slots are idle. The fix is more
partitions, which requires a key-preserving migration if ordering matters:
consume, re-key, produce, switch consumers. Note the trap: increasing consumer
count does nothing, and the common wrong fix is exactly that.
</details>

---

**Q7.** Your anomaly detector uses mean and standard deviation over 90 days of
history. Six months ago there was a 4x traffic spike. What is wrong now?

<details><summary>Marking</summary>
The spike is still in the window, so the standard deviation is inflated by a
one-off event and the threshold is now too loose to catch anything. The fix is
a robust scale: median absolute deviation times 1.4826, which is barely
affected by a single extreme value. This is a real and common failure: the
monitor's own history silently disabled it.
</details>

---

**Q8.** Two pipelines both derive revenue from the same source table and agree
exactly. Is that evidence the number is right?

<details><summary>Marking</summary>
No. Agreement proves only that they do not disagree. If they share a library,
a helper function, or a rounding convention, a common bug produces agreement.
Reconciliation is only evidence against an *independent* source — a different
system with different code. This is why the payment-processor settlement file
is the check that matters, and why "two jobs agree" is not a control.
</details>

---

**Q9.** A GDPR erasure request covers 14 copy types. Which is hardest to get
right, and why?

<details><summary>Marking</summary>
The snapshot/backup copies, because deleting them may not be possible within
the deadline and because a logical delete is not deletion — a flag or a
filtered query leaves the data present. The right answer is physical removal
where possible, a purge scheduled well inside the statutory deadline, and
evidence (a verification query per copy) that can be shown later. Also note
that "temporary" debug copies and vendor exports are usually the ones missed.
</details>

---

**Q10.** A dashboard takes 22 minutes. The first thing you change is a
materialized view. When is that the wrong first move?

<details><summary>Marking</summary>
When the query scans far more data than it needs to. A materialized view over a
badly partitioned table can inherit the problem: it still scans the same
partition layout. Partitioning/clustering and the filter columns are the
cheaper, more general fix, and they help every query, not just this one. Order:
measure bytes scanned, fix pruning, then consider pre-aggregation.
</details>

---

**Q11.** You cannot backfill 90 days safely. What does that tell you, and what
is the minimum change to fix it?

<details><summary>Load-bearing concept</summary>
It tells you the pipeline is not deployable, regardless of how well it works
today — a backfill is the test that surfaces non-determinism, point-in-time
bugs, and non-idempotent writes. The minimum change is a shadow target plus a
reconciliation step: write to a date-suffixed table, compare against
production, promote only on a match. That gives isolation, verification, and
a safe promote, in that order.
</details>

---

**Q12.** A feature store serves 320 features per decision at 40k rps. Budget
is 3ms. Your first change is?

<details><summary>Marking</summary>
Batch the read into a single multi-key fetch, and pack the features into one
serialized value rather than 320 hash fields. At a 0.4ms round trip, 320
sequential reads is 128ms; one pipelined read is ~1ms. Caching, replication
tuning, and faster hardware are all worse first moves because they do not
remove the round trips.
</details>

---

**Q13.** Access review covers 100% of grants, 71% auto-cleared, 29% to humans.
What is the risk you have accepted?

<details><summary>Marking</summary>
The 71% rests on specific attestations (manager matches the approver, access
was actually exercised, the role still needs it, no cross-jurisdiction
access). If any attestation is weak, 71% of reviews are rubber stamps at
scale. The accepted risk is real and should be stated: automated clearance
trades human judgement for coverage, and coverage without judgement is
worse than sampling. The mitigation is a labeled appeal feed back into the
rules, plus periodic human audits of the auto-cleared set.
</details>

---

**Q14.** Your alert fired on a 30% volume drop at 02:00. The partition was
simply not expected yet. What should have been different?

<details><summary>Marking</summary>
Expected-by times must be per-partition and derived from the source's own SLA,
not from a schedule assumption. A global "daily by 02:00" is wrong for
partitions that arrive weekly, and wrong for sources with their own cadence.
The deeper point: an alert that fires on correct behaviour trains people to
mute the channel, which is the failure mode that kills monitoring programs.
</details>

---

**Q15.** You own a pipeline that is 4% under-reporting revenue. The batch job
agrees with you. What do you do first?

<details><summary>Marking</summary>
Find an independent authority, not another pipeline. Until you know which
side is right, a fix is a coin flip — and a rewrite that changes the number
without explaining the old one destroys the ability to learn. Concretely:
reconcile against the payment processor or the ledger, quantify the
discrepancy by dimension and time, and only then decide whether the streaming
path or the batch path is wrong.
</details>

---

## Scoring

| Score | Interpretation |
|---|---|
| 13-15 | Ready to design and review production systems. Move to `REAL_WORLD_PROJECT.md`. |
| 10-12 | Solid. Re-read `THEORY.md` sections 1, 2, and 7, then retake. |
| 7-9 | Mechanics are fine; the judgement questions are where the gaps are. Do `EXERCISES.md` level 2 and 3. |
| below 7 | Read `THEORY.md` fully and work `EXERCISES.md` in order. |
