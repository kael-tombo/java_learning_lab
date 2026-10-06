# Lab 01: EBS Architecture — Flashcards

## Diagnosis

---
**Q**: App tier 100% CPU, database 60%. What does that mean?
**A**: The app tier is the constraint. One tier saturated, one with headroom = tier-level finding, not a SQL problem.

---
**Q**: High CPU plus poor throughput = ?
**A**: Lock contention. Workers are spinning, not working.

---
**Q**: What is `JTF_QUEUE_LOCK`?
**A**: The table where CM workers coordinate work reservation. Contention there means many workers racing to claim the same work.

---
**Q**: Why does throughput collapse when CPU is 100%?
**A**: Zero headroom — every new arrival must wait for a release. Response time rises non-linearly as U → 1.

---

## Concurrency Model

---
**Q**: Little's Law?
**A**: `L = λ × W`. Queue length = arrival rate × average time in system.

---
**Q**: Arrivals fixed, wait drops 6×. Queue length?
**A**: Drops 6×. You improved W, not λ.

---
**Q**: Response time multiplier at U = 0.9?
**A**: ~10× (roughly `1/(1-U)`). At 0.95 it's ~20×.

---
**Q**: 20 workers on one lock — useful work?
**A**: ~5%. ~95% of CPU is wasted spinning.

---
**Q**: Practical utilisation ceiling for interactive workloads?
**A**: 70–80%. Above that, queueing explodes.

---

## Remediation

---
**Q**: Why not raise CM process count on a saturated node?
**A**: No CPU headroom, and workers still share one lock. Adds contention, not throughput.

---
**Q**: What does specialisation do?
**A**: Puts each workload class in its own queue so report storms can't delay interfaces.

---
**Q**: Why horizontal scale before vertical?
**A**: A node at 100% has a hard ceiling. Nodes add independent capacity and isolate blast radius.

---
**Q**: What must be enabled after cloning nodes?
**A**: JTF clustering — otherwise two nodes can schedule the same job.

---
**Q**: What does work shifts do?
**A**: Shapes CM capacity over time so non-critical work is scheduled into demand troughs.

---
**Q**: Where must work shift times be expressed?
**A**: The database/server time zone. Local time misplaces capacity.

---

## Quick Reference

| Task | Command / Query |
|------|-----------------|
| Queue depth + wait | `fnd_concurrent_requests` where `phase_code='P' AND hold_flag='N'` |
| Single-queue check | `fnd_concurrent_queues` where `specialized_flag='N'` |
| Stop a manager | `$AD_TOP/bin/fndlmsrv -g APPL -n QUEUE -M STOP` |
| Create queue | `FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE(...)` |
| Create shift | `FND_CONCURRENT_QUEUE_PUB.CREATE_SHIFT(...)` |
| Lock wait | `v$active_session_history` + `blocking_session` |
| Forms sessions/node | `fnd_forms_sessions` group by `apps_node_name` |
| One-query diagnosis | standard queue count + pending count + wait, `FROM dual` |

---

## Sizing

| Resource | Rule | 5,000 users |
|----------|------|-------------|
| Forms processes | 1 : 50 | 100 |
| OAF threads | 1 : 100 + overhead | ~80 |
| CM workers | from queue depth | sized to <30 min wait |

---

## Time Zone Offsets from EST

| Region | Local 08–18 | EST equivalent |
|--------|-------------|----------------|
| US | 08:00–18:00 | 08:00–18:00 |
| EMEA (CET) | 08:00–18:00 | 02:00–12:00 |
| APAC (SGT) | 08:00–18:00 | 19:00–05:00 (wraps) |

---

## Anti-Patterns

1. Scaling up processes on a saturated node.
2. Cloning nodes without JTF clustering.
3. Blaming the database because it is the interesting component.
4. Suppressing `JTF_QUEUE_LOCK` as an "error" rather than diagnosing it.
5. Rolling out all nodes at once with no per-node validation.

---

## Study Tips
1. Draw the single-queue vs specialised-queue diagrams from memory.
2. Be able to compute the wasted-CPU fraction for any worker count.
3. Convert regional peak times to EST without a calculator.
4. Explain why DB utilisation rising after a fix is good news.