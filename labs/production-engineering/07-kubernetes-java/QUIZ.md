# Lab 07: Kubernetes for Java Architects — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. A JVM pod with `-Xmx1g` and a 2GB container memory limit keeps getting OOMKilled. Why?**
- A) The heap is leaking
- B) Container memory = heap + metaspace + code cache + thread stacks + direct buffers + JVM/native overhead, so ~2.2GB of RSS against a 2GB cgroup cap is an OOM-kill with no `OutOfMemoryError`
- C) `-Xmx1g` is invalid syntax
- D) The image is too large

**Answer: B** — You must budget native memory explicitly. Heap ≈ 60–70% of the limit; verify with NMT (`jcmd VM.native_memory`) and `-XX:+ExitOnOutOfMemoryError`.

---

**Q2. `CrashLoopBackOff` with exit code 137 most likely means?**
- A) A `ClassNotFoundException`
- B) SIGKILL from the kernel OOM killer (or a liveness failure) — check `kubectl describe pod` `Last State: Reason`
- C) An unhandled exception in `main`
- D) A failed readiness probe

**Answer: B** — 137 = 128 + 9 (SIGKILL). If `OOMKilled` is the reason, it is a memory budget problem; if the reason is `Error` from a probe, it is probe configuration.

---

**Q3. Why must a slow-starting Spring Boot service use a `startupProbe` rather than only a liveness probe?**
- A) Startup probes are cheaper
- B) Liveness `initialDelaySeconds` must cover worst-case warmup, which delays real crash detection; a startup probe disables liveness until the app is warm, then hands off precisely
- C) Kubernetes forbids liveness probes without a startup probe
- D) Startup probes are required for JVM services only

**Answer: B** — A 90-second JVM warmup with a fixed `initialDelaySeconds: 120` means a 30-second failure is undetected for 2 minutes. A startup probe with a tight `failureThreshold` gives both fast detection and a generous budget.

---

**Q4. A liveness probe that checks a downstream database causes a fleet-wide outage because?**
- A) Liveness must not touch the database at all, ever
- B) When the DB degrades, every pod fails liveness simultaneously and is killed — including the pods that could have served cached/degraded traffic — so there is nothing left to recover
- C) Probes cannot reach external hosts
- D) Kubernetes restarts healthy pods

**Answer: B** — Liveness answers "is this process wedged?" only. Downstream health belongs in readiness (and in an alert), never liveness.

---

**Q5. Difference between `readinessProbe` failing and `livenessProbe` failing?**
- A) None; both restart the pod
- B) Readiness failure removes the pod from Service endpoints (traffic stops, process lives); liveness failure kills and restarts the container
- C) Liveness is checked less frequently
- D) Readiness only works for Deployments

**Answer: B** — This distinction is the backbone of zero-downtime deploys: readiness gates traffic during startup *and* graceful shutdown.

---

**Q6. CPU `requests: 100m` / `limits: 2` for a JVM service produces?**
- A) Faster throughput
- B) CFS throttling in 100 ms periods whenever the process bursts — latency spikes invisible in average CPU; plus node overcommit and steal time for neighbors
- C) Guaranteed 2 cores
- D) Automatic HPA scale-up

**Answer: B** — Either set `requests == limits` (Guaranteed QoS, reservation not throttling) or leave CPU limits off and rely on requests.

---

**Q7. `PodDisruptionBudget` with `minAvailable: 1` on a 3-replica deployment does what during a node drain?**
- A) Prevents all drains
- B) Allows at most 2 of 3 pods to be voluntarily evicted at once, so voluntary disruptions respect capacity; note it does **not** stop involuntary events like node failure
- C) Guarantees zero downtime
- D) Scales the deployment to 3 replicas

**Answer: B** — PDBs govern *voluntary* eviction only. They are ignored by the OOM killer and by hardware failure — which is exactly why they cannot be your only availability control.

---

**Q8. Why does a rolling update need `preStop` sleep plus `terminationGracePeriodSeconds`?**
- A) It is a Kubernetes requirement for all workloads
- B) SIGTERM arrives and endpoints are removed asynchronously; without a delay, in-flight requests on the still-listed endpoint get 502s during the removal propagation window
- C) It improves readiness accuracy
- D) It reduces image size

**Answer: B** — Endpoint removal propagates through kube-proxy/ingress asynchronously (hundreds of ms to seconds). A 5–15 s `preStop` sleep covers the gap so the load balancer stops sending before the JVM closes the listener.

---

**Q9. A pod is evicted with reason `The node was low on resource: ephemeral-storage`. What is the actual problem?**
- A) The node ran out of disk
- B) The container's writable layer and `emptyDir`/log volume exceeded the node's allocatable ephemeral storage — often unlogged GC files, heap dumps, or verbose app logs
- C) The pod exceeded its memory limit
- D) The image registry was unreachable

**Answer: B** — Set `resources.requests.ephemeral-storage`, cap log file counts/sizes, and write heap dumps to a mounted volume.

---

**Q10. HPA on CPU for a JVM service oscillates between 2 and 20 replicas. The likely causes are?**
- A) The cluster is too small
- B) CPU-based scaling on a JVM dominated by GC/jitter with no stabilization window, plus `requests` set at a fraction of real need so utilization % swings on a tiny denominator
- C) HPA cannot scale above 10 replicas
- D) The GC is misconfigured

**Answer: B** — Fix `requests`, set `stabilizationWindowSeconds`, use a more stable metric (queue depth or per-request CPU), and add a scale-up/down asymmetry.

---

**Q11. `-XX:MaxRAMPercentage=75` with a 4GB container limit sets the heap to 3GB. What is the risk?**
- A) The JVM refuses to start
- B) Only ~1GB remains for metaspace + code cache + thread stacks + direct buffers + JVM overhead — any direct-buffer growth or thread leak OOM-kills the pod
- C) GC pauses get shorter automatically
- D) `MaxRAMPercentage` ignores the cgroup limit

**Answer: B** — Budget from a measured NMT breakdown, not from a percentage rule of thumb. Common safe range is 50–65% for I/O-heavy Spring services.

---

**Q12. `kubectl get pod` shows `STATUS: Running` but `READY: 0/1` for 4 minutes after rollout. What does that mean?**
- A) The container is broken
- B) The process is up but readiness is failing — the Service is correctly excluding it; find the readiness endpoint response in `describe`/logs
- C) The image is being pulled
- D) The pod is Pending

**Answer: B** — `Running` = container alive, `Ready` = passing probes. A permanently-not-ready pod during rollout means the readiness gate is too strict or the app is genuinely unhealthy.

---

**Q13. Why does a `JVM` container need `terminationGracePeriodSeconds` ≥ the longest realistic in-flight request?**
- A) To let the JVM flush heap dumps
- B) Kubernetes escalates SIGTERM to SIGKILL at the grace period; anything in flight beyond it is cut off, producing the 502s users see on every deploy
- C) To allow the readiness probe to fail first
- D) Required for `preStop`

**Answer: B** — Set it from the request timeout budget (e.g. `p99.9 + drain estimate`), not from a round number.

---

**Q14. `readOnlyRootFilesystem: true` with no writable volume breaks the JVM because?**
- A) The JVM needs `/tmp` and log/dump directories; you must mount an `emptyDir` or PVC at those paths
- B) Kubernetes forbids read-only filesystems
- C) The JVM binary is not executable on a read-only mount
- D) Only applies to Node images

**Answer: A** — Set `-Djava.io.tmpdir`, `-Xlog:...:file=...`, and `HeapDumpPath` onto mounted volumes.

---

**Q15. The single most common reason a Java service fails under Kubernetes scale-out is?**
- A) Not enough replicas
- B) The container memory budget was not recomputed, so each new pod's heap + native share pushes per-node density past allocatable and triggers eviction/OOM-kill cascades
- C) The ingress controller
- D) Insufficient CPU requests

**Answer: B** — Density (`Σ requests / allocatable`) is the real constraint. Adding replicas adds memory *requests*; if the node cannot hold them, you get eviction cascades instead of capacity.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and deploy a real service.
- 12–10: revisit cgroup memory accounting and probe semantics; redo EXERCISES 2–5.
- <10: re-read THEORY + CODE_DEEP_DIVE cold and retake in 48 hours.
