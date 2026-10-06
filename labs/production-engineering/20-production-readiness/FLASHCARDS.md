# Lab 20: Production Readiness & SLO Engineering — Flashcards

~60 cards. Most answers are a threshold, a number, or a yes/no with evidence.

---

## SLO design

Q: SLI / SLO / error budget?
A: SLI = measured user-visible property. SLO = target over a window. Error budget = allowed failure = `(1 − SLO) × window`.

Q: Error budget for 99.9% / 99.95% / 99.99% over 30 days?
A: 43.2 / 21.6 / 4.3 minutes.

Q: What dimensions should SLIs cover?
A: Success rate, latency (p50/p95/p99/p99.9), throughput, freshness/correctness (staleness, data loss), and availability of *dependencies as experienced by the user*.

Q: Why not one blended availability number?
A: It hides which dimension is failing, prevents targeted alerts, and maps to no runbook. Blend for reporting; decompose for operating.

Q: `good / valid` — what is `valid`?
A: All eligible events minus explicitly documented exclusions (client cancels, synthetic probes, allowlisted tenants). Write the exclusions down.

Q: Why write exclusions down?
A: Two people will otherwise compute different SLIs from the same data and argue about it during an incident.

Q: Minimum-valid-events floor?
A: Require `valid ≥ N` before evaluating, so a 3 a.m. single-request failure is not a 100% error rate.

Q: Which percentile for an SLO?
A: Usually p99 for a latency objective, but set the percentile from the user experience (a checkout flow where 1 in 100 users waits too long may need p95; a background job may need p99.9). State it explicitly.

Q: Should the SLO window be 28 or 30 days?
A: Either; 28 aligns with the SRE workbook convention and shifts smoothly. What matters is that it is long enough that one incident cannot exhaust the budget, and short enough to be actionable.

Q: Business-hours-only SLO?
A: Legitimate for internal tools, if stated. Never for customer-facing paths — excluding low-traffic hours to protect the number is a well-known SLO anti-pattern.

Q: What about data correctness SLIs?
A: The hardest and most neglected: count of detected vs undetected bad records, reconciliation mismatches, duplicate-effect rate. Consider adding them even at low precision.

---

## Burn-rate alerting

Q: Burn rate?
A: `observed_bad_fraction / allowed_bad_fraction`. `> 1` means the budget is being consumed faster than sustainable.

Q: Page vs ticket thresholds?
A: Page on fast burns (14.4× over 1 h with 5× over 6 h confirmation); ticket on slow burns (1× over 6 h and 1× over 3 d).

Q: Why two windows ANDed?
A: The short window gives fast detection; the long window prevents paging on self-healing blips.

Q: Why not alert on a raw threshold?
A: Threshold alerts are too sensitive normally (noise) and too insensitive during slow burns (missed degradation). Burn rate is tied to the promise.

Q: Every alert must have?
A: An owner, a severity, a runbook link, a dashboard link, and a stated expected action. An alert with no action is a ticket.

Q: Target pages per on-call shift?
A: ≤ 1–2 actionable.

Q: What about `forecast` alerts?
A: A useful complement: "at the current burn rate the budget will be exhausted in N days" catches slow burns before they become incidents.

---

## Capacity readiness

Q: What must a capacity plan contain?
A: `λ_peak` and its growth, `W` per endpoint class, CPU/memory per request, saturation point per resource, utilisation target, headroom that survives N+1 failure, and the forecast with a proactive-scaling trigger.

Q: Utilisation target for latency-critical paths?
A: 60–70% at peak, because queueing delay rises non-linearly above that.

Q: Headroom must survive what?
A: Loss of the largest node/AZ plus peak traffic. Not just peak.

Q: Autoscaling without a capacity model?
A: Reactive only; it fails at exactly the moment it is needed, and it may not reach the required replica count in time.

Q: What must be measured before launch?
A: A load test in a production-shaped environment at expected peak and at peak + headroom, with the saturation point identified.

Q: Dependencies' capacity?
A: Each dependency's capacity and your share of it: `replicas × pool ≤ dependency capacity`. Owning 70% of a dependency's capacity is an availability risk you created.

Q: Storage growth forecast?
A: Yes — 12-month projection with the trigger for archiving, partitioning, or provisioning.

---

## Startup readiness

Q: What must be true before readiness passes?
A: The service can serve real traffic: caches warm or safely cold, connections established, migrations confirmed, downstream reachable.

Q: Startup probe required?
A: When cold start exceeds ~30 s (JVM warmup, class loading, JIT, cache fill), yes — otherwise liveness kills a warming JVM or `initialDelaySeconds` must be so long that real hangs go undetected for minutes.

Q: Does a warming pod consume capacity?
A: Yes, CPU. On a rollout, add warm-up pods to the capacity plan (`maxSurge` pods are JIT-competing with serving pods).

Q: Readiness that depends on a downstream?
A: A trap: a dependency blip removes every pod from the endpoints at once. Readiness should be "can I serve what I have".

Q: Migration confirmation at startup?
A: If the service applies migrations at boot, concurrent pods racing on the same migration is a classic launch incident. Use a lock/advisory mechanism, or a separate migration job.

---

## Shutdown readiness

Q: What must shutdown do?
A: Stop accepting, finish in-flight work within the grace period, flush telemetry, close connections, exit 0.

Q: Grace period derived from what?
A: The request timeout budget: `drain = max(in_flight/throughput, p99.9 request time)`, plus `preStop` sleep for endpoint propagation, plus slack.

Q: How is shutdown readiness *verified*?
A: Roll the deployment under load and count 5xx. Zero is the criterion.

Q: `maxUnavailable: 0`?
A: For zero-downtime, with `maxSurge: 1` — and verify the memory budget can absorb the extra pod.

Q: Does a `preStop` sleep really matter?
A: Yes — endpoint removal propagates asynchronously; without the delay, the LB keeps sending to a pod that has stopped accepting.

---

## Dependencies & failure modes

Q: What must be enumerated per dependency?
A: Timeout, retry policy (with budget), circuit breaker state, bulkhead, what happens when it is slow vs down, and whether the fallback is correct.

Q: Failure-mode inventory?
A: Every dependency, datastore, resource limit, lifecycle event, network shape, clock, and data condition. Target 15+ per service before launch.

Q: Must be tested before launch?
A: At least one failure injection per service: kill a pod under load, add dependency latency, revoke access. Evidence, not intent.

Q: What about `Chaos` requirements in readiness?
A: Top three failure modes from the inventory must have been exercised with a pass condition.

---

## Observability readiness

Q: Minimum dashboards?
A: Per service: SLI value vs SLO line, error budget remaining, burn rate, request volume, latency percentiles, error rate by status, saturation (pools, queue, thread), JVM (heap, GC pause rate), and dependency latency.

Q: Minimum logs?
A: Structured, with a correlation id (`trace_id`, `request_id`) on every line, sampled successes, full errors and slow requests, and no secrets or PII.

Q: Traces?
A: Enabled with W3C context propagation across the service boundary, with a sampling policy that retains errors and slow requests.

Q: What must be measured in the JVM?
A: Allocation rate and GC pause rate, not just heap usage. Heap usage alone is a lagging indicator.

Q: Alerting readiness?
A: Burn-rate alerts on each SLO, saturation alerts, and an alert for every SLO with a documented action.

Q: What is an "observable failure"?
A: If it fails, a dashboard or an alert tells you within the detection objective. Everything else is a hypothesis.

---

## Runbooks & on-call

Q: What makes a runbook ready?
A: Followed end to end by someone who did not write it, with every command verified and every expected output recorded.

Q: What must a runbook contain?
A: Symptom → first three commands → decision tree → expected output for each → mitigation options in order of safety → escalation → verification of recovery.

Q: How many runbooks?
A: One per paging alert, not one per service. Map alerts to runbooks and fail CI if a paging alert has none.

Q: On-call readiness?
A: A named rotation, a secondary, an escalation that reaches a human within 10 minutes, a written handoff, and a page budget.

Q: Flaky alert policy?
A: One re-notification, then a ticket. Never a page loop.

---

## Deployment & rollback readiness

Q: Build once and promote?
A: Yes — the same artifact digest moves through environments, verified at deploy.

Q: Rollback must be?
A: Drilled, timed, and declared available or unavailable per service. If unavailable, a fix-forward playbook exists.

Q: Time-to-rollback as a readiness criterion?
A: Yes, with a published target (e.g. < 10 minutes) and a measured value.

Q: Progressive delivery?
A: Canary with pre-declared analysis (error rate, latency, saturation) and automatic rollback.

Q: Database migration safety?
A: `lock_timeout`, expand-and-contract for shape changes, and a rollback-validity table.

Q: Feature flags?
A: Present where needed for operational kill switches, locally evaluated, with an owner and an expiry.

---

## Data & recovery

Q: What must be true about backups?
A: Tested restores on a schedule, with measured RTO and RPO compared against stated objectives.

Q: RTO / RPO?
A: RTO = maximum acceptable recovery time; RPO = maximum acceptable data loss. Both must be measured, not documented.

Q: Retention?
A: Per data store, with a lifecycle job, and erasure propagation where personal data is involved.

Q: Data loss budget?
A: A maximum acceptable data-loss rate, with an alert. Zero data loss is not a plan.

Q: Restore test cadence?
A: Quarterly for tier-1, and after any change to the backup or storage mechanism.

---

## PRR process

Q: When does a PRR happen?
A: Before any production traffic, with a named sign-off, and repeated on material change (new dependency, new store, scaling change, failure-model change).

Q: The eight evidence areas?
A: SLIs/SLOs, capacity, startup/shutdown, dependencies and failure modes, observability and alerting, runbooks and on-call, deployment and rollback, data and recovery.

Q: Who signs off?
A: A named owner per area, plus an overall accountable owner. "The team approved it" is not a sign-off.

Q: What kills a PRR?
A: Evidence from a non-representative environment: one pod, no load, no injection, no peak. "Green dashboard" is the most common false signal.

Q: What is the "hardest question" in a PRR?
A: "If this broke completely at 02:00 right now, what would we see, and would we know within our detection objective?"

Q: How long should a PRR take?
A: 2–4 hours, evidence prepared beforehand. A review that runs longer is a design review, not a readiness review.

Q: What is the exit condition?
A: Every area has evidence, or an accepted risk with an owner and an expiry. "Not applicable" is allowed only with a reason.

---

## Numbers and defaults to memorize

Q: Error budget 99.9% / 30 days?
A: 43.2 minutes.

Q: Page burn threshold?
A: 14.4× over 1 h confirmed by 5× over 6 h.

Q: Ticket burn threshold?
A: 1× over 6 h confirmed by 1× over 3 d.

Q: Target utilisation at peak?
A: 60–70%.

Q: Headroom to survive?
A: N+1 failure plus peak, not peak alone.

Q: Startup probe budget?
A: 2× the slowest observed cold start; e.g. 75 s observed → 150 s.

Q: Grace period?
A: `max(in_flight/throughput, p99.9) + preStop + slack`; ≥ 45 s for a typical Java service.

Q: `maxSurge`?
A: 1 pod with `maxUnavailable: 0`, verified against the memory budget.

Q: Pages per shift?
A: ≤ 1–2 actionable.

Q: Restore test cadence?
A: Quarterly for tier-1.

Q: Minimum valid events for an SLI?
A: ~100 per evaluation window.

Q: Error-budget policy thresholds?
A: > 50% ship freely; 25–50% canary-only; < 25% freeze non-essential changes.

---

## The eight readiness questions

Q: 1. What does the user experience when this works?
A: The happy path, and the numbers for it (latency, throughput).

Q: 2. How do we know it is working?
A: SLI, dashboard, alert, and the detection objective.

Q: 3. How do we know it is *not* working?
A: The failure signals, and how long each takes to detect.

Q: 4. What happens when it does not work?
A: The user-visible degradation, and whether it is safe.

Q: 5. What do we do about it?
A: The runbook, the mitigation options in safety order, and the kill switch.

Q: 6. Can we get back to a good state?
A: Rollback (drilled and timed) or a fix-forward playbook.

Q: 7. What did we decide to accept?
A: The accepted risks, with owner and expiry.

Q: 8. What would hurt us most, and would we notice?
A: The single most damaging failure mode, and whether the current observability would catch it inside the detection objective.
