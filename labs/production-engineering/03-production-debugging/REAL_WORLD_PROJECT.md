# Lab 03: Production Debugging — Real World Project

## Scenario: "The pod that died quietly at 02:47"

You are the on-call rotation lead for a subscription billing platform (Java 21 / Spring Boot 3, Kubernetes, 30 pods). You are also the person who gets paged.

**Two incidents in one week**:

**Incident A (02:47)** — A single pod in the `us-east-1b` AZ started returning `500`s at a 3% rate while every other pod was healthy. No deploy, no traffic spike, no dependency alert. The pod was restarted automatically by the liveness probe. It happened again 6 hours later. Classic "flaky pod" — the runbook says "restart and move on."

**Incident B (Thursday 11:20)** — During a routine partner-integration rollout, all pods began returning `503` with `OutOfMemoryError: unable to create new native thread`. CPU was at 25%. Heap metrics looked normal. It took 52 minutes to diagnose because the team kept looking at heap metrics.

**Your job over 4 weeks**: make this class of incident diagnosable in under 10 minutes, and remove the two specific failure modes.

**Time**: 25–35 hours | **Difficulty**: Advanced

---

## Phase 1 — Diagnose the incidents properly (Day 1–3)

### Incident A: the flaky pod

Hypotheses to test (do not assume; test each):
1. Connection-pool exhaustion from a leaked connection (e.g. a code path that doesn't close on error).
2. A node/zone network issue (MTU, conntrack, DNS).
3. Cert expiry or token refresh failing on that node only.
4. CPU throttling on that node.
5. Local disk / ephemeral storage exhaustion.
6. Something specific to that pod's identity (a config difference).

**Method**: work the evidence you actually have — previous-container logs, node metrics for that AZ, the liveness-probe failure history, and 500s by pod (`kubectl top pod -l app=billing`, error-rate-by-instance dashboards).

**Deliverable 1 — Incident A report** (1 page):
- The hypothesis you eliminated first, and the evidence that eliminated it.
- Root cause, with the metric that proves it.
- Why the liveness probe did not prevent the user impact (probe design review).
- The instrumentation gap that made this a 40-minute investigation instead of a 5-minute one.

### Incident B: native thread exhaustion

**Method**: reproduce faithfully in a staging namespace with the same partner-integration feature flag. Confirm with:
- `jcmd VM.native_memory summary.diff` — thread stacks category growth.
- `VM.classloader_stats` (unlikely for this one) and `jcmd Thread.print` counts.
- Container `pids.max` / `pids.current`, and JVM `Runtime.maxMemory()` vs cgroup limit.
- Verify no `OutOfMemoryError: Java heap space` appears anywhere (to exclude the heap hypothesis).

**Deliverable 2 — Incident B report**:
- The mechanism: which code path created threads, at what rate, and why they never died.
- The three misleading signals (CPU at 25%, heap normal, "it's a memory issue") and the single signal that would have identified it (`pids.current` trend, or thread-count-by-name metric).
- The fix and its verification test.

---

## Phase 2 — Instrument for the failure modes you now know exist (Day 3–7)

Ship metrics and dashboards derived from *actual incidents*, not hypotheticals:

**New metrics**
| Metric | Type | Why |
|---|---|---|
| `jvm_threads_live{state}` | gauge | Thread census by state — the primary signal for both incidents |
| `jvm_threads_daemon{owner="<name-family>"}` | gauge | Thread families, normalized — catches executor leaks |
| `jvm_thread_families_growth_1h` | gauge | Monotonic growth per family — the leak canary |
| `container_pids_current / pids_max` | gauge | Native thread/FD exhaustion before it becomes an OOME |
| `hikaricp_connections_pending` | gauge | Pool acquisition wait — the Incident A shape |
| `jvm_buffer_pool_used_bytes{pool="direct"}` | gauge | Direct memory trend |
| `http_client_in_flight{downstream}` | gauge | In-flight per dependency |
| `jvm_gc_pause_seconds` histogram | existing, tuned | Pause tail, not mean |

**Structured logging upgrade**: add `correlation_id`, `trace_id`, `pod`, `node`, `az`, `downstream`, and `attempt` to every log line. Enforce with a logback encoder + an ArchUnit-style test that fails the build if a log statement omits the MDC keys.

**Dashboards**: three, one per incident class, each with the panel that would have answered the question in under a minute. Time-to-diagnose is the acceptance metric, so design panels from the *question you actually asked*, not from the metrics that are easy to graph.

**Deliverable 3 — Observability change set**: metric list, log schema, dashboard links, and a "questions this answers" table mapping the two incident timelines onto panels.

---

## Phase 3 — Fix the root causes (Week 2)

### Incident A fix
- Correct the connection leak; add a test that runs the failing path 10,000 times under a pool of size 2 and asserts the pool returns to idle.
- Redesign the liveness/readiness probes: liveness must not depend on downstream health (a dependency outage should not restart pods); readiness must gate traffic correctly. Document the probe contract in `RUNBOOK_PROBES.md`.
- Add a `CONNECTION_POOL_EXHAUSTED` fast-fail error class with a distinct metric so the next occurrence is unambiguous.

### Incident B fix
- Fix the thread leak: no per-request executor, no unbounded async submission; use shared named pools with bounded queues.
- Add a `ThreadLocal` audit + `remove()` enforcement.
- Bound concurrency at the edge with a semaphore and a fast-fail `429`/`503` with `Retry-After`.
- Add a guardrail metric and alert: thread count > 600 for 5 minutes → warn; > 900 → page.

**Deliverable 4 — Fixes with verification**: before/after load-test traces showing thread count flat, plus the specific regression tests added.

---

## Phase 4 — Build the triage capability (Week 3)

### 4.1 One-command evidence capture

Deploy the `capture.sh` equivalent as a runnable (`kubectl exec`/`kubectl debug`) and wrap it in a Make target:

```bash
make debug PID=$(kubectl get pod -l app=billing -o jsonpath='{.items[0].metadata.name}') \
               POD=evidence/$(date +%s)
```

It must collect: thread dumps ×5, heap info, histogram ×2, classloader stats, NMT baseline + diff, a bounded 60s JFR recording, GC log tail, `/proc/<pid>/status`, `smaps_rollup`, and cgroup `cpu.stat` / `memory.max` / `memory.current` / `pids.*`. Then it tars the directory and prints the triage verdict from the analyzer.

### 4.2 Debug sidecar for crashed pods

A sidecar or CronJob that detects `OOMKilled` / crash-loop restarts, grabs previous-container logs plus the last GC log lines shipped to a volume, and files a ticket with the evidence attached and the suspected category filled in. This addresses the recurring complaint that crashed-pod evidence evaporates.

### 4.3 Debugging enablement

- `RUNBOOK_DEBUG.md`: symptom → command → confirmation, one page, tested by someone unfamiliar with the service.
- A "debugging dojo": four scenarios (pod-scoped 500s, native-thread OOME, GC-pause spike, pod-lock contention) each with a planted cause, where engineers must find it using only the runbook and `capture.sh`. Score on time-to-diagnose.
- Record the team's current time-to-diagnose for each scenario before and after the runbook; that number is your deliverable metric.

**Deliverable 5 — Capability package**: capture tooling, sidecar/ticket automation, runbook, and the dojo results with before/after timings.

---

## Phase 5 — Postmortem-driven observability backlog (Week 4)

Take your last 12 months of incidents (or construct a realistic set) and quantify:

```
time_to_detect  (alert → human aware)
time_to_diagnose (aware → root cause named)
time_to_mitigate (root cause → customer impact stopped)
```

Plot the distribution. For each incident, classify the gap: *no signal*, *signal not actionable*, *tool too slow*, *knowledge gap*. Rank instrumentation investments by total hours of delay recovered per engineering day spent.

Deliver a ranked backlog where the top three items are traceable to specific incidents, with an estimate of hours-of-delay recovered. This is the artifact that makes observability an investment rather than a cost.

**Deliverable 6 — Quantified backlog** with the three highest-ROI items and their justification.

---

## Phase 6 — Make it durable (Week 4)

CI/CD gates:
- A test that asserts every `ThreadPoolExecutor`/`Executors.*` creation is on an allowlist of named shared pools (ArchUnit rule).
- A test that fails if `new Thread(`, `Executors.newCachedThreadPool`, or an unbounded queue appears outside the allowlist.
- A log-schema test that fails the build on a missing correlation/MDC field.
- A staging load test in CI that asserts thread count returns to baseline after the suite — catches leaks at PR time, not at 02:47.

**Deliverable 7 — Gates** merged, with a documented bypass process (break-glass, with expiry).

---

## Deliverables checklist

- [ ] Phase 1 — Two incident reports with eliminated hypotheses, root cause with proof, and instrumentation gaps.
- [ ] Phase 2 — Metrics, log schema, dashboards, and a questions-this-answers mapping.
- [ ] Phase 3 — Root-cause fixes with before/after verification.
- [ ] Phase 4 — One-command evidence capture, crash-evidence automation, runbook, dojo results.
- [ ] Phase 5 — Quantified observability backlog (hours of delay recovered per day of work).
- [ ] Phase 6 — CI gates with a break-glass process.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "Restarted and it stopped" | Hypothesis list with elimination evidence, root cause proven by a metric |
| Instrumentation | "Added more logs" | Metrics and dashboards derived from actual incident questions, with cost considered |
| Tooling | Manual `jcmd` by hand during an incident | One-command capture, automated crash evidence, printed verdict |
| Enablement | Runbook nobody tested | Runbook validated by an unfamiliar engineer, with measured time-to-diagnose deltas |
| Durability | "Remember to check next time" | CI gates that fail the build on the exact defect classes found |
| Economics | "Observability is important" | Backlog ranked by hours-of-delay recovered per engineering day |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **JFR (`jdk.jfr` consumer) documentation for JDK 21** — https://docs.oracle.com/en/java/javase/21/jfapi/ — the authoritative list of events (`jdk.ExecutionSample`, `jdk.NativeMethodSample`, `jdk.JavaMonitorEnter`, `jdk.ThreadPark`, `jdk.SocketRead`, `jdk.FileRead`, `jdk.ObjectAllocationSample`) and `settings=profile` overhead characteristics. Verify event availability for your exact JDK before scripting against them.
2. **`jcmd` command reference (JDK 21)** — https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html — canonical syntax for `Thread.print -l`, `GC.heap_info`, `GC.class_histogram`, `GC.heap_dump`, `VM.native_memory`, `VM.classloader_stats`, and `JFR.start`. Confirm flags such as `-all` behavior against your version.

Also verify before citing: the container CPU throttling metric names in your specific cAdvisor/Prometheus setup, and cgroup v2 `memory.events` semantics for `oom_kill` counting on your kernel version.

---

## Reflection questions

1. Both incidents were invisible to the dashboard. What is the principle for deciding which panel to build?
2. What is the cost of "restart and move on" over a year, expressed in incident-hours?
3. Which CI gate would have caught each incident, and at what point in the pipeline?
4. If you could only keep one new metric forever, which one, and why?
5. How would you explain to a stakeholder why the observability backlog should outrank the next feature?
