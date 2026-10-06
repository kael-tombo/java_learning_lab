# Lab 01: JVM Memory & GC — Real World Project

## Scenario: "Black Friday at 14:02"

You are on the platform team for a mid-size e-commerce company. The JVM checkout service runs 24 pods on Kubernetes, 8 vCPU / 12 GB limit each, `-Xmx8g -XX:+UseG1GC`, JDK 17.

**The incident**: peak traffic Friday afternoon. p99 latency climbs from 60 ms to 4 s. Error rate hits 3% (gateway timeouts). Grafana shows `jvm_gc_pause_seconds` spiking to 1.9 s. Kubernetes begins OOM-killing pods. On-call restarts pods manually for 40 minutes. Revenue loss estimated at $310K. Postmortem action items: "engineer the GC story properly."

**Your job over 4 weeks**: produce a production-grade memory and GC posture for the checkout service, prove it under a Black-Friday-scale load test, and leave behind a system that detects the next recurrence automatically.

**Time**: 25–35 hours | **Difficulty**: Advanced

---

## Phase 1 — Forensics on the incident (Day 1–2)

Start from the artifacts you would actually have. If you do not have logs, reproduce them.

**Artifacts to reconstruct or generate:**
- 20 minutes of GC logs from a pod at peak (`-Xlog:gc*,safepoint:file=/var/log/app/gc.log`).
- Container metrics: RSS, cpu throttling (`container_cpu_cfs_throttled_seconds_total`), OOM-kill events.
- `kubectl describe pod` output showing `Last State: Terminated, Reason: OOMKilled`.
- The old JVM flags from the deployment manifest.

**Deliverable 1 — Incident GC report** (1 page):
- Decode the pause lines: live set trend, allocation rate, GC frequency, worst cause.
- State the single root cause in one sentence with the number that proves it.
- Name the two contributing factors you can prove from data (e.g. cgroup throttling, humongous allocations from a logging buffer).
- List what you *cannot* prove from available telemetry, and what instrumentation would fix that.

The typical honest finding: `Xmx8g` in a 12 GB container, live set already 6.5 GB after a heap growth bug in a session cache, plus `-XX:MaxRAMPercentage` unset so the JVM mis-sized on restart. Full GCs every 3–4 minutes once the cache saturated.

---

## Phase 2 — Sizing with evidence (Day 3–5)

Collect a proper live-set measurement at three load levels (baseline, 2x expected peak, 5x expected peak):

```bash
# Full-GC histogram at each level — this is your ground truth live set
jcmd <pod-pid> GC.class_histogram | head -30

# Heap generation breakdown (no GC, cheap)
jcmd <pod-pid> GC.heap_info

# Native memory (metaspace / code cache / thread stacks / direct)
jcmd <pod-pid> VM.native_memory baseline
jcmd <pod-pid> VM.native_memory summary.diff
```

**Deliverable 2 — Memory budget document**:
```
Container limit            : 12288 MB
  - heap (MaxRAMPercentage) : 8192 MB  (live set 5.1 GB x 1.6, rounded)
  - metaspace cap           :  256 MB
  - direct memory cap       :  512 MB
  - thread stacks           :  256 MB  (512 threads x 512 KB)
  - code cache + JVM/agent  :  512 MB
  - headroom                : 2560 MB
```

Then justify each line and state the monitoring signal that would tell you it is wrong.

---

## Phase 3 — Collector decision (Day 5–7)

Run the checkout service in a load-test environment with three collector configurations, holding everything else constant:

| Config | Flags |
|---|---|
| A (current) | `-Xmx8g -XX:+UseG1GC -XX:MaxGCPauseMillis=200` |
| B | `-Xmx8g -XX:+UseZGC` |
| C | `-Xmx14g -XX:+UseG1GC -XX:MaxGCPauseMillis=50 -XX:InitiatingHeapOccupancyPercent=35` |

Measure per config: p50/p99/p999 latency, GC pause total (sum over window), CPU used for GC, RSS, throughput at fixed error rate.

**Deliverable 3 — Collector decision record**, containing:
- The raw table of results with the test methodology (warmup, duration, request mix).
- Whether ZGC's CPU overhead is affordable at your price point (this is a cost question, not just a perf question).
- The chosen config, the rejected configs, and the specific trigger that would cause you to revisit.

---

## Phase 4 — Container and GC hardening (Week 2)

Manifest changes with rationale for every line:

```yaml
env:
  - name: JAVA_TOOL_OPTIONS
    value: >-
      -XX:MaxRAMPercentage=66
      -XX:InitialRAMPercentage=66
      -XX:+UseG1GC
      -XX:MaxGCPauseMillis=100
      -XX:InitiatingHeapOccupancyPercent=40
      -XX:+HeapDumpOnOutOfMemoryError
      -XX:HeapDumpPath=/var/dumps
      -XX:+ExitOnOutOfMemoryError
      -XX:MaxDirectMemorySize=512m
      -XX:MaxMetaspaceSize=256m
      -Xlog:gc*,safepoint:file=/var/log/app/gc.log:time,uptime,level,tags:filecount=5,filesize=50m
resources:
  requests: { cpu: "6", memory: "12Gi" }
  limits:   { cpu: "8",  memory: "12Gi" }
```

Also implement:
- A startup self-check that fails fast if `Runtime.maxMemory()` disagrees with the container limit by more than 5%.
- `HeapDumpOnOutOfMemoryError` wired to a sidecar that uploads `hprof` and pages the on-call only if a dump actually appears (dump files are large; paging on every OOM is noise).
- JVM crash-loop safety: with `ExitOnOutOfMemoryError`, confirm `CrashLoopBackOff` restarts are clean and the readiness probe holds traffic until the app is warm.

---

## Phase 5 — Black Friday load test (Week 3)

Re-run the incident at scale, twice:

1. **Baseline** — the original config at peak + 20%.
2. **Hardened** — your new config at peak + 20%, with a deliberate 3× live-set growth injection to see whether the system degrades gracefully or OOM-kills.

Also inject the specific faults that were invisible in the original incident: cgroup CPU throttling at 70%, metastaspace pressure via repeated context refresh, and a humongous-allocation regression (40 MB direct buffers).

**Deliverable 4 — Load test report**: SLO attainment (p99 < 250 ms, error < 0.1%), GC pause budget consumed per hour, time-to-recover after each injected fault, and the single configuration weakness you still have.

---

## Phase 6 — Automate detection (Week 4)

Ship these alerts (Prometheus/Actuator-style names):

| Alert | Expression (conceptual) | Severity |
|---|---|---|
| LiveSetRatioHigh | `jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.7` for 10m | warning |
| FullGCOccurred | `increase(jvm_gc_collection_seconds_count{action="end of major GC"}[15m]) > 0` | page |
| PauseBudgetBurned | `rate(jvm_gc_pause_seconds_sum[5m]) > 0.02` | warning |
| ThrottlingHigh | `rate(container_cpu_cfs_throttled_seconds_total[5m]) > 0.5` | warning |
| OOMKillDetected | pod restart reason == OOMKilled | page |
| AllocationRateSpike | derived allocation rate > 3x 7-day baseline | warning |
| MetaspacePressure | `jvm_memory_used_bytes{area="nonheap"}` approaching cap | warning |

Plus a **leak canary**: a nightly job that runs a synthetic 10-minute workload, forces a histogram, and diffs live-set-per-class against yesterday. Growth > 5% in any class → ticket.

---

## Phase 7 — Knowledge transfer (Week 4)

- `RUNBOOK_GC.md`: OOM triage flowchart by error type, pause-spike decision tree, collector rollback procedure.
- A 30-minute internal session: "Heap sizing with arithmetic," using your Phase 2 document as the worked example.
- A pair-programming exercise where a teammate diagnoses a deliberately broken config using only your runbook.

---

## Deliverables checklist

- [ ] Phase 1 incident GC report (1 page, root cause with numbers).
- [ ] Phase 2 memory budget with per-line justification and monitoring signal.
- [ ] Phase 3 collector decision record with raw A/B/C results.
- [ ] Phase 4 hardened manifest + startup self-check + dump sidecar.
- [ ] Phase 5 load test report with SLO attainment and injected-fault results.
- [ ] Phase 6 alert pack + nightly leak canary.
- [ ] Phase 7 runbook + teach-back session delivered.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "GC was slow" | Root cause named with the metric that proves it, plus unprovable gaps listed |
| Sizing | Flags copied from a blog | Arithmetic from measured live set, with sensitivity analysis |
| Collector choice | "G1 is best" | Trade-off table, cost considered, revisit trigger stated |
| Hardening | Manifest edit | Budget covers metaspace, direct, threads, code cache, and headroom |
| Detection | Dashboards only | Alerts with thresholds justified by SLO, plus an automated leak canary |
| Handover | "Ask the platform team" | Runbook an on-call stranger can execute at 3 a.m. |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

These are the primary sources behind the guidance in this lab. Re-check the current version before quoting numbers, since defaults and flag names change between JDK releases.

1. **Oracle HotSpot GC tuning guide** — https://docs.oracle.com/en/java/javase/21/gctuning/ — canonical reference for collector behavior, `MaxGCPauseMillis` heuristics, G1 sizing ergonomics, and `-XX:+UseContainerSupport`. Confirm the JDK version mapping before citing a specific default.
2. **OpenJDK JEP index (ZGC, Generational ZGC, Shenandoah, Epsilon, Container Support)** — https://openjdk.org/jeps/0 — the primary source for *why* each collector exists and what the pause/throughput goals are. Read JEP 439 (Generational ZGC) and JEP 379 (Shenandoah) directly; the JEP index page itself is a directory, not the specification.

Additional useful anchors (verify too): `jcmd` reference at https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html and JFR documentation at https://docs.oracle.com/en/java/javase/21/jfapi/.

---

## Reflection questions

1. Which single metric, if it had existed during the original incident, would have cut diagnosis time the most?
2. Your new config will be wrong eventually. What monitoring tells you *before* customers do?
3. If you could keep only one of {bigger heap, ZGC, leak canary, alert}, which one, and why?
4. What would you tell a team that wants to skip this and "just use the defaults"?
