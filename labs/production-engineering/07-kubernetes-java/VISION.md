# VISION — Lab 07: Kubernetes for Java Architects

> From "it works on my machine" to "the cluster is part of the design."

---

## The Arc

1. **The cgroup reality** — what a container memory limit actually caps, and why `-Xmx` is only one term in the equation.
2. **JVM in a container** — heap share, native budget, NMT verification, container-aware ergonomics.
3. **Resource model** — requests vs limits, CFS throttling, QoS classes, density, schedulability.
4. **Probes as control theory** — liveness vs readiness vs startup, and why each mistake is a fleet-wide incident.
5. **Disruption** — PDBs, topology spread, rolling update parameters, surge vs speed.
6. **Shutdown and startup** — `preStop`, grace periods, drain math, zero-downtime rollout.
7. **Autoscaling** — HPA signals for JVM workloads, oscillation, custom metrics.
8. **Failure forensics** — exit codes, pod states, `describe`/`--previous`, ephemeral storage, eviction.

---

## Why this lab exists

A JVM that is comfortable on a laptop will be killed by a cluster, and it will be killed *silently* — no `OutOfMemoryError`, no stack trace, just a pod that restarts. The reason is arithmetic that most teams never perform: heap is 40% of the memory a Java process actually consumes.

The specific goal here: **you can take any deployment manifest and compute whether it can actually run, drain correctly, and stay alive.** Not "is it valid YAML" — will it work at peak, during a rollout, and at 03:00 when the node dies.

---

## Milestones (checkable)

- [ ] M1: Take a Deployment manifest and produce a complete container memory budget with NMT-verified numbers.
- [ ] M2: Explain a specific `OOMKilled` pod by reconstructing the RSS composition at the moment of the kill.
- [ ] M3: Design liveness/readiness/startup probes for a service with a 75 s cold start and a 12 s p99.9, with justification for each number.
- [ ] M4: Compute node density for a 23-replica service and determine whether a rollout with `maxSurge: 2` can schedule.
- [ ] M5: Derive `terminationGracePeriodSeconds` from the request timeout budget and show why the 30 s default produces deploy-time 502s.
- [ ] M6: Diagnose four pod states (`Pending`, `CrashLoopBackOff`, `OOMKilled`, `Evicted`) from `describe` output alone.
- [ ] M7: Replace a CPU-based HPA with a queue-depth or latency signal and demonstrate the elimination of oscillation.

---

## Anti-Goals

- `-Xmx` equal to the container memory limit.
- Liveness probes that touch a downstream dependency.
- No `requests` (BestEffort) on a production service.
- PDBs treated as a guarantee rather than a voluntary-drain constraint.
- Probes with `timeoutSeconds` longer than the probe period.
- Dumping heap to ephemeral storage on a busy node.
- Rolling updates without `minReadySeconds` and a `progressDeadlineSeconds`.

---

## Interview Lens

- "Your pod is OOMKilled with no OOM in the logs. Walk me through it."
- "How do you size a JVM for a container?"
- "Why is my liveness probe causing outages?"
- "Tell me why your deployment can't roll out at peak traffic."
- "How do you know the cluster will schedule 25 replicas?"

---

## 30-Day Plan

- **Week 1** — THEORY + CODE_DEEP_DIVE: cgroup memory, JVM flags, probe semantics; hands-on with `kubectl describe`, cgroup files, `jcmd`. M1–M3.
- **Week 2** — EXERCISES: density math, drain math, HPA oscillation; QUIZ to 13/15; FLASHCARDS daily. M4–M5.
- **Week 3** — MINI_PROJECT: deploy, break, and fix a real Spring service; reproduce OOM-kill, probe cascade, and rollout stall. M6–M7.
- **Week 4** — REAL_WORLD_PROJECT war story; produce a manifest audit for a real deployment; teach-back: "why this manifest survives peak, drain, and node loss" in 10 minutes.

---

## Artifacts you should be able to show

1. A container memory budget table with NMT evidence.
2. A probe design document with detection-time and startup-budget arithmetic.
3. A density/schedulability calculation for a real deployment at peak plus surge.
4. A drain/grace-period derivation tied to the request timeout budget.
5. A pod-failure triage runbook keyed on exit code and container state.

---

## Done = You Can

- Read a manifest and tell whether it will run, and what will kill it first.
- Design probes that detect wedges fast without cascading restarts.
- Compute whether a rollout can schedule, and price the zero-downtime option.
- Triage a failing pod from `kubectl describe` output in under two minutes.
