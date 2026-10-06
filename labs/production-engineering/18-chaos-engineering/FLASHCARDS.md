# Lab 18: Chaos Engineering & Fault Injection — Flashcards

~60 cards. Most answers are a rule, a control, or a hypothesis.

---

## Method

Q: The four principles of chaos engineering?
A: (1) Understand the steady state, (2) Hypothesize steady behaviour under turbulence, (3) Try to disprove the hypotheses, (4) Establish new hypotheses. Verify, do not "observe".

Q: Experiment anatomy?
A: Hypothesis → precondition assertion (steady state) → inject → measure → abort on threshold → undo → verify return to steady state → record pass/fail.

Q: Hypothesis examples that are actually falsifiable?
A: "With `inventory` at 3 s, `checkout` p99 stays under 800 ms" (measurable); "A consumer kill produces no duplicate orders" (measurable); NOT "the system stays resilient" (unmeasurable).

Q: Pass condition stated before injection?
A: Always. Derived from an SLO or a documented expectation, expressed as a threshold on a named metric with a named window.

Q: Precondition assertion?
A: An automated check that key SLIs are within objective for the last N minutes; the tool refuses to inject otherwise. This prevents "the chaos found a pre-existing problem" confusion.

Q: Steady state definition?
A: SLI-based (error rate, latency, availability, plus domain metrics like orders created per minute), not "it looks fine" and not "no alerts firing".

Q: Steady-state duration before injection?
A: Long enough to have seen a normal traffic cycle — typically 15–30 minutes, or one full business cycle for business-hour-sensitive flows.

Q: Record everything?
A: Timeline with timestamps, the hypothesis, the pass condition, the metric series before/during/after, the abort behaviour, and the verdict. Same discipline as an incident review.

---

## Blast radius & abort

Q: What is blast radius?
A: The maximum fraction of requests/users/instances an experiment may affect. Bound by scope selector, percentage, time, and a hard abort.

Q: Smallest useful radius?
A: One pod or 1% of traffic. If the hypothesis cannot be tested at that radius, the hypothesis is not specific enough.

Q: Abort condition?
A: A machine-evaluated threshold on user-visible SLIs that halts the experiment and starts cleanup. Not a human.

Q: Why must abort be automated?
A: Nobody evaluates a metric reliably at 30-second intervals for an hour, and hesitation during a real degradation is the worst possible behaviour.

Q: Test the abort itself?
A: Yes — inject a controlled regression and verify the abort fires within its evaluation window and that cleanup restores the steady state. An untested abort is not a control.

Q: Automatic restore?
A: Required. Every injection has an inverse operation and a verification step on a timer. If you cannot state the inverse, you are not ready.

Q: When may chaos run in production?
A: After staging has validated the mechanics; only for hypotheses about production-only properties; with tiny radius, verified abort, dashboards open, and explicit business sign-off.

Q: Kill switch?
A: A single documented command or UI action that stops all experiments and restores, reachable by anyone in the room.

---

## Choosing injections

Q: Highest-value injection in most systems?
A: **Latency** on a dependency. It reproduces the incident shape you actually get (pool exhaustion, deadline misses, thread saturation) while requests still succeed.

Q: Packet loss vs latency vs connection close?
A: Latency → queue/occupancy bugs. Loss → retransmission, timeouts, retry storms. Connection close → connection-pool churn and reconnect storms. Different failure modes; run all three.

Q: DNS failure injection reveals?
A: Whether the JVM's DNS cache (`networkaddress.cache.ttl`) masks it, and whether a synchronised cache expiry causes a stampede. Verify the flag for your JVM.

Q: CPU saturation injection reveals?
A: CFS throttling, tail inflation hidden in the mean, GC starvation, queue growth, and whether the service sheds or collapses (Lab 07/15).

Q: Disk full injection reveals?
A: That your diagnostics depend on the disk: logs stop, heap dumps fail, temp files fail, and writes may fail silently. Under-tested and highly informative.

Q: Memory pressure / OOM injection reveals?
A: Whether the JVM fails fast (`ExitOnOutOfMemoryError`) or limps, and whether the pod restart is graceful for traffic.

Q: Dependency unavailability?
A: Circuit-breaker behaviour, fallback correctness, connection-pool retry behaviour, and whether the failure is contained to one path.

Q: Slow/throttled dependency (not down)?
A: The most realistic and most damaging. Often worse than a hard outage because every request is slow rather than failing, so retries amplify.

Q: Certificate expiry?
A: Whether expiry is *predicted* (alerted in advance) or *discovered* at expiry, and whether rotation is automated.

Q: Node/zone loss?
A: Replica spread, PDB effectiveness, cross-zone dependency assumptions, and whether capacity survives the loss (Lab 07 density).

Q: Clock skew?
A: Token expiry logic, cache TTL computation, and anything relying on wall-clock ordering. Rare and highly informative.

Q: Random response corruption / malformed payload?
A: Robustness of deserialisation, schema validation, and whether corruption becomes a 500 storm or a graceful degradation.

---

## Injection techniques

Q: Boundary vs in-code injection?
A: Boundary (sidecar/proxy such as Toxiproxy, or a service mesh fault filter) exercises the real client stack: retries, timeouts, pools, TLS. In-code (`@InjectableFault`) reaches specific business paths. Prefer boundary for infrastructure faults; label in-code so nobody mistakes one for the other.

Q: Toxiproxy gives you?
A: Latency, jitter, bandwidth, reset/close, and timeout on a per-listener basis, with a simple HTTP/control API — a precise, reversible, scriptable injection.

Q: Spring Boot Chaos Monkey / CM4SB gives you?
A: Scheduled exceptions/timeouts/latency at annotated points in your own code. Convenient for business-path experiments; does not exercise the client stack.

Q: Resilience4j integration?
A: Circuit breaker, retry, and bulkhead metrics are your primary evidence. Every experiment should assert on *those* metrics, not only on the end-to-end SLI.

Q: Injected fault must be?
A: Deterministic (a known fraction of requests at a known location), reversible, labelled in telemetry, and observable — so you can prove the fault was actually applied.

Q: How do you prove the fault applied?
A: A dedicated metric or log (`fault_injected_total{type, location}`) and an end-to-end SLI change. Without proof of application you cannot interpret a null result.

---

## Kubernetes-specific

Q: Kill a pod mid-request?
A: Tests graceful shutdown, `preStop`, grace periods, and whether in-flight work is lost or retried safely. Inverse: nothing (the controller recreates it); verify by steady-state recovery.

Q: Evict a node?
A: PDB compliance, drain behaviour, and whether voluntary disruptions respect capacity (Lab 07).

Q: Make a node `NotReady`?
A: Pod eviction timing, control-plane behaviour, and how quickly endpoint removal propagates.

Q: Throttle a pod's CPU with a cgroup?
A: Precise CFS throttling with a known quota — more controlled than a CPU burner, and it produces the exact Lab 07/15 signature.

Q: Delete a pod's service account token?
A: Whether your least-privilege assumption holds, and whether the failure is graceful.

Q: Delete a ConfigMap/Secret?
A: What your service does with missing configuration: fail fast at boot, or start and fail at first use (the worst option).

---

## GameDays

Q: Chaos experiment vs GameDay?
A: Chaos tests one technical hypothesis about one fault. A GameDay tests the human system: command, runbooks, escalation, communication, decisions under uncertainty, with several coordinated injections.

Q: What do GameDays find most often?
A: Mundane gaps: a runbook command that no longer exists, a dashboard behind a VPN, an escalation path to someone who left, an alert routed to an empty rotation, a missing permission.

Q: GameDay safety?
A: Non-production or production-shaped staging, pre-announced window, named observer, pre-written abort, explicit business sign-off for production, and a rule that any participant can call stop.

Q: Coordinate injections with the story?
A: Yes — a scheduled GameDay works best as a scenario: a deploy at 09:00, a dependency degrading at 09:15, a failed failover at 09:40. It exercises escalation as well as resilience.

Q: Measure what?
A: Time to detect, time to declare, time to first correct hypothesis, time to mitigate, runbook usability, and every point a human was blocked.

---

## Operational discipline

Q: Who may run an experiment?
A: Anyone in the team, with the required controls in place. Restricting it to a "chaos team" defeats the purpose.

Q: Experiment registry?
A: A catalogue of hypotheses, results, and findings, searchable so you do not repeat an experiment and so findings are tracked to fixes.

Q: Finding → action?
A: Every finding becomes a tracked action with an owner and a date, exactly like a postmortem. Chaos findings that are not tracked are wasted.

Q: Run it as an incident or fix it in the branch?
A: As an incident. Let detection, command, diagnosis, and communication run for real, then postmortem. That is where the organisational learning is.

Q: Minimum viable experiment?
A: One hypothesis, one fault, one service, staging, automated abort and undo, and a written pass/fail result. Start there.

Q: How many experiments to start?
A: One per week, all of them small. Consistency and trust matter more than volume.

Q: Record the *time to detect* from every experiment?
A: Yes. That number is usually the most actionable output, and it converts directly into alert work.

---

## Numbers and defaults to memorize

Q: Steady-state window before injection?
A: 15–30 minutes, or a full business cycle for business-hour flows.

Q: Initial blast radius?
A: One pod or 1% of traffic.

Q: Abort evaluation interval?
A: 10–30 seconds per evaluation; abort must fire within two evaluation windows.

Q: Max experiment duration?
A: 15–30 minutes. Long enough to be meaningful, short enough to bound exposure.

Q: Restore verification window?
A: 5–10 minutes of steady-state metrics after undo, asserted automatically.

Q: Experiments per team per month?
A: Four or more small ones — consistency builds the trust that makes production experiments approvable.

Q: Expected finding rate per GameDay?
A: ~5–6 concrete defects (see the Lab 14 arithmetic).

Q: Proportion of findings that are non-technical?
A: A large majority — runbooks, access, dashboards, escalation.

Q: Chaos-as-a-percentage-of-incidents goal?
A: Reduce the proportion of incidents caused by *unknown* behaviour; increase the proportion you have already proven.

Q: Minimum before production chaos?
A: Every injection validated in staging, abort tested, and steady-state assertion automated.
