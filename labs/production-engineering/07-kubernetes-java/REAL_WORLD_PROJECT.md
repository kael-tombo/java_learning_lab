# Lab 07: Kubernetes for Java Architects — Real World Project

## Scenario: "The 2GB Limit That Kept Killing Us"

You are a platform architect for a fintech payments platform: 11 Spring Boot 3 services, Java 21, Kubernetes 1.30 on spot-backed node pools, 3 environments, ~180 pods in production.

**The incident** — Thursday 14:12, end-of-day batch. `settlement-engine` begins restarting repeatedly. The alert is `CrashLoopBackOff` with a 6-minute detection gap. Over 41 minutes:

1. `settlement-engine` (6 replicas) is `OOMKilled` in a loop. No `OutOfMemoryError` appears anywhere in the logs.
2. Because the pods restart, readiness flaps and the Service endpoints drop to 2–3 of 6. Settlement files stop being processed for 41 minutes.
3. Batch retry logic makes it worse: the downstream `ledger-writer` sees duplicate submission attempts and starts rate-limiting.
4. A human investigates for 38 minutes before finding `OOMKilled` in `kubectl describe`. The team assumed "heap leak" for most of that time.
5. A node in the same pool is `MemoryPressure=True` and is draining, so the restarted pods also cannot be rescheduled — the restart storm competes with the drain.

**Impact**: settlement backlog of 4.2M transactions, 6 hours of manual reconciliation, one late regulator filing. Direct cost: $610K. Nearest known cause: a Netty direct-buffer change shipped Tuesday that raised direct memory from 180 MB to 620 MB, with `MaxDirectMemorySize` unset and the container limit unchanged at 2 GB.

**Postmortem finding**: no service in the fleet had a verified memory budget. Every manifest set `-Xmx1g` and `limits.memory: 2Gi` by copy-paste from the template. 9 of 11 services were latent OOM-kill candidates.

**Your job over 4 weeks**: make container memory, probe semantics, resource requests, and shutdown behaviour a *measured, enforced* property of every service — and prove the platform survives the same event.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Reconstruct the failure (Day 1–3)

### 1.1 Build the causal chain

Reconstruct from `describe` output, events, and metrics the timeline: time → pod state → reason → exit code → downstream effect. Specifically account for:

- The RSS composition at the moment of each kill (heap touched vs metaspace vs code cache vs thread stacks vs direct buffers).
- Why detection took 6 minutes despite a hard failure.
- Why endpoints dropped to 2–3 instead of staying at 5–6 (restart duration vs probe timings).
- Why the duplicate-submission amplification happened (retry policy vs restart-induced idempotency-key loss).
- Why the MemoryPressure node drain turned a restart loop into an availability loss.

**Deliverable 1 — Causal analysis** with the timeline table, the arithmetic at each step, and an explicit list of what telemetry existed vs what you had to infer.

### 1.2 Fleet inventory

For all 11 services record: replicas (min/max), `-Xmx`, all `-XX:Max*` flags, `MaxDirectMemorySize`, `-Xss`, thread-pool ceilings, `requests`/`limits` for cpu/memory/ephemeral, probe configs, `terminationGracePeriodSeconds`, `preStop`, image size.

Compute per service: heap share of limit, native headroom, and node density at max replicas.

**Deliverable 2 — Fleet inventory table** plus a ranked list of latent OOM-kill candidates, each with its computed headroom in MB.

---

## Phase 2 — Measure, do not guess (Day 3–7)

### 2.1 NMT baseline per service class

Run each service class under production-representative load in staging with NMT enabled, and record actual RSS composition:

```bash
kubectl exec -it <pod> -- jcmd 1 VM.native_memory summary
kubectl exec -it <pod> -- jcmd 1 VM.native_memory baseline
# ...run load...
kubectl exec -it <pod> -- jcmd 1 VM.native_memory summary.diff
```

Produce a real table (not a rule of thumb):

| Service | Heap | Metaspace | Code | Stacks | Direct | Other | Total RSS | Limit | Headroom |
|---|---|---|---|---|---|---|---|---|---|

**Deliverable 3 — Measured memory budget per service class**, with the observed 95th-percentile total and the resulting `MaxRAMPercentage`.

### 2.2 Direct-buffer audit

Find every direct/native allocation site. For Netty: `io.netty.maxDirectMemory`, pooled vs unpooled allocators, `PlatformDependent.maxDirectMemory`, and whether `PooledByteBufAllocator` metrics show arenas growing past expectations.

**Deliverable 4 — Direct-memory audit** naming the code path in `settlement-engine` that caused the 180 → 620 MB growth, plus the guard (explicit `MaxDirectMemorySize`) and the code change.

### 2.3 Probe audit

For all 11 services: what does liveness actually assert, does readiness touch any dependency, what is the real cold-start distribution (p50/p99 from deploy history), and what is the current detection time for a wedge?

**Deliverable 5 — Probe audit** with a per-service fix list (add startup probe, split readiness, tighten timeout) and the before/after detection-time arithmetic.

---

## Phase 3 — Fix the platform (Week 2)

### 3.1 Memory and container config

Replace the copy-paste template with a measured per-class standard:

```yaml
env:
- name: JAVA_OPTS
  value: >-
    -Xms1200m -Xmx1200m -Xss512k
    -XX:+UseContainerSupport
    -XX:MaxRAMPercentage=55
    -XX:MaxMetaspaceSize=256m
    -XX:MaxDirectMemorySize=256m
    -XX:+ExitOnOutOfMemoryError
    -XX:+HeapDumpOnOutOfMemoryError
    -XX:HeapDumpPath=/dumps
    -XX:+NativeMemoryTracking=summary
    -Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags:filecount=5,filesize=50m
resources:
  requests: { cpu: "2", memory: "2300Mi", ephemeral-storage: "4Gi" }
  limits:   { cpu: "2", memory: "2300Mi", ephemeral-storage: "5Gi" }
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"] }
  seccompProfile: { type: RuntimeDefault }
  readOnlyRootFilesystem: true
automountServiceAccountToken: false
```

Volumes for `/tmp`, `/logs`, `/dumps` with `sizeLimit`. Heap dumps to a PVC, not ephemeral storage.

### 3.2 Shutdown and rollout

- `server.shutdown=graceful`, `timeout-per-shutdown-phase` sized per service.
- `preStop: sleep 15`, `terminationGracePeriodSeconds` derived from each service's `p99.9 + drain estimate + slack`.
- `maxUnavailable: 0`, `maxSurge: 1`, `minReadySeconds: 10`, `progressDeadlineSeconds` > startup budget.
- PDBs with `minAvailable` chosen per service and verified not to deadlock HPA scale-down.
- `topologySpreadConstraints` across zones and hosts.

### 3.3 Autoscaling

Replace CPU-percent HPA with a concurrency/queue-depth target for I/O services and per-request CPU for compute services, with `stabilizationWindowSeconds` and a down-scaling policy.

**Deliverable 6 — Standard manifest + diff**: before/after for all 11 services, per-line rationale, canaried 24 h at 5% per service with rollback ready.

---

## Phase 4 — Enforce in CI (Week 2–3)

Build gates that make the incident class unrepeatable:

1. **Memory budget gate**: fail if computed `heap + measured native floor` ≥ 85% of the limit, or if `MaxDirectMemorySize`/`MaxMetaspaceSize` are unset, or `-Xmx` ≥ limit.
2. **Requests/limits gate**: fail if `requests` is missing (BestEffort/Burstable), or if `requests.cpu != limits.cpu` for latency-critical tiers, or if `ephemeral-storage` requests are absent.
3. **Probe gate**: fail if liveness touches a dependency, if a service with observed cold start > 30 s lacks a startup probe, if `timeoutSeconds` ≥ `periodSeconds`, or if `terminationGracePeriodSeconds` < the service's declared max request timeout.
4. **Security-context gate**: fail if `runAsNonRoot`, capability drop, or seccomp are absent; fail if `readOnlyRootFilesystem: true` without writable `/tmp`, log, and dump mounts.
5. **Density gate**: fail the rollout if `Σ pods × requests` exceeds allocatable × 0.8 on any node, using the scheduler's own estimate.
6. **Golden path**: canary deploy 5% → 25% → 100% with automated SLO comparison; auto-halt on regression.
7. **Break-glass**: documented, time-boxed, with an expiry date per exception.

**Deliverable 7 — CI gates** merged, with the measured native-memory floors as a reviewed registry artifact.

---

## Phase 5 — Prove it (Week 3)

Replay the real event in a production-shaped staging cluster:

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Baseline end-of-day batch | p99 < 250 ms, error < 0.1%, no evictions |
| S2 | Replay Tuesday's direct-buffer growth (`MaxDirectMemorySize` unset, 620 MB) | pod survives; `Direct buffer memory` OOME fails fast; no cgroup kill |
| S3 | Forcible memory pressure — fill node memory to evictable threshold | Guaranteed QoS pods evicted last; no settlement loss; PDB respected |
| S4 | `pricing`/`ledger-writer` slow at 8 s with readiness depending on it | readiness fails, liveness does **not**; no restart cascade |
| S5 | Node drain while batch is running | graceful shutdown completes; no in-flight 502s; backlog continues |
| S6 | Rollout during batch peak at max replicas | rollout completes or is auto-halted; 0 errors |
| S7 | Pod kill during in-flight request | retry + idempotency key prevents duplicate settlement |

**Deliverable 8 — Resilience test report** with all seven scenarios, criteria met/missed, and fixes for anything missed.

---

## Phase 6 — Operate it (Week 3–4)

- **Runbooks**: `RUNBOOK_OOMKILLED.md`, `RUNBOOK_CRASHLOOPBACKOFF.md`, `RUNBOOK_EVICTION.md`, `RUNBOOK_POD_PENDING.md`, `RUNBOOK_ROLLOUT_STALL.md`. Each with symptom → first three commands → decision tree.
- **Alerts** derived from the measurement, not convention:
  - `memory.current / limits.memory > 0.85` for 5 min → warn
  - `Direct buffer memory` OOME or heap OOME occurrence → page
  - `restart_count` increase in 5 min → page (with `kubectl describe` link)
  - `readiness_failures` high but `liveness_failures` zero → warn (dependency degradation)
  - `liveness_failures > 0` → page (real wedge, needs human)
  - `kube_pod_status_ready` != expected replicas for 3 min → warn
  - Node `MemoryPressure=True` → page
  - `container_memory_working_set_bytes` > 90% of limit → warn
- **Game day**: execute S2–S5 with on-call in business hours, with a written exercise and a kill switch.
- **Admission policy** (or equivalent lint) so new pods inherit the standard.

**Deliverable 9 — Operational package**: runbooks, model-derived alert thresholds, game-day report.

---

## Phase 7 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Services with a verified memory budget | 0 / 11 | 11 / 11 |
| Latent OOM-kill candidates | 9 | 0 |
| OOM-kill MTTD | 6 min | < 60 s |
| OOM-kill MTTR | 38 min | < 5 min |
| Restart cascade from a slow dependency | 6/6 pods | 0 restarts |
| Deploy-time 502s per rollout | ~140 | 0 |
| Rollback-to-known-good | ~22 min (build+roll) | < 3 min (digest revert) |
| Node density at peak | 94% | 71% |
| Incident cost (this class, annualized) | $610K | ~0 |

Institutionalize: memory floors into the service template; `MaxDirectMemorySize` mandatory in the platform base image; "container memory budget" as a required section in service design review; quarterly re-measurement because library upgrades move native usage; a dashboard per service showing RSS composition.

**Deliverable 10 — Business case + institutionalization**, presented to engineering leadership with the numbers above.

---

## Deliverables checklist

- [ ] Phase 1 causal analysis + fleet inventory with computed headroom.
- [ ] Phase 2 measured NMT budgets, direct-memory audit, probe audit.
- [ ] Phase 3 memory/container/shutdown/autoscaling fixes, canaried.
- [ ] Phase 4 six CI gates + native-floor registry.
- [ ] Phase 5 seven-scenario resilience report.
- [ ] Phase 6 runbooks, model-derived alerts, game day.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "It was an OOM" | RSS composition reconstructed from NMT, timeline, telemetry gaps named |
| Measurement | "Used 70% of memory" | Measured per-class budgets with the native floor documented and re-measurable |
| Fix | Raised the memory limit | Explicit per-class budgets + bounded direct/metaspace + fast-fail OOM handling |
| Probes | Increased `initialDelaySeconds` | Split readiness/liveness, startup probes, detection-time arithmetic |
| Enforcement | "Documented guidelines" | Six CI gates with a reviewed registry and break-glass |
| Proof | Staging happy path | Replays the actual event shape, memory pressure, drain during batch, rollout at peak |
| Operations | Watch the dashboards | Runbooks + alerts derived from measurement + game day |
| Economics | Technical only | Before/after dollars + institutionalized template and quarterly re-measurement |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Kubernetes — `configure-pod-container/configure-liveness-readiness-startup-probes`** — https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ — the canonical reference for the three probe types, and the authoritative statement that a failing liveness probe triggers a restart *while* a failing readiness probe only removes the pod from Service endpoints. Also the source for the `startupProbe` gating semantics and the guidance that probes should be fast and inexpensive.
2. **Kubernetes — `configure-pod-container/assign-memory-resource/` and `manage-resources-containers`** — https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/ — the authoritative container memory model: `limits.memory` becomes the cgroup limit, exceeding it means the kernel OOM-killer terminates the container, and requests drive scheduling (QoS class and eviction order). Verify the cgroup v1 vs v2 file names against your node's runtime before citing specific paths.

Additional anchors worth verifying: the exact `securityContext` field set and seccomp support for your Kubernetes version, `topologySpreadConstraints` `minDomains`/`nodeAffinityPolicy` defaults (these have changed across releases), and whether your JVM version's container ergonomics differ from the assumptions above.

---

## Reflection questions

1. Which term in the RSS composition would you never have found without NMT, and how long did it take to find?
2. The team assumed "heap leak" for 38 minutes. What single dashboard panel would have ended that in 30 seconds?
3. If you could only fix one of the six CI gates this quarter, which one, and what class of incident does the arithmetic say it prevents?
4. What is the operational cost of the read-only root filesystem and bounded `emptyDir` workarounds, and would you accept it?
5. The Tuesday direct-buffer change was a normal dependency upgrade. What would have caught it before 41 minutes of settlement backlog — a test, a gate, or an alert?
