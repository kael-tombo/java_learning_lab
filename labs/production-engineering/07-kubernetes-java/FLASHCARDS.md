# Lab 07: Kubernetes for Java Architects — Flashcards

~60 cards. Most answers here are a number or a config field you must get right.

---

## Container & cgroup model

Q: What does a Kubernetes `resources.limits.memory` actually cap?
A: The container's cgroup memory (v1 `memory.limit_in_bytes` / v2 `memory.max`) — RSS plus page cache, *not* just the Java heap.

Q: Exit code 137 means?
A: SIGKILL (128 + 9). In practice: kernel OOM-kill or an escalated termination.

Q: Exit code 143 means?
A: SIGTERM (128 + 15) received and handled — a normal graceful shutdown.

Q: What is `memory.working_set` vs RSS?
A: Working set = RSS − inactive page cache; it is what the kubelet uses for eviction decisions and what OOM-kill logic weights.

Q: Container memory composition for a JVM?
A: Heap (touched) + metaspace + code cache + thread stacks + direct/native buffers + GC structures + JVM binary/agent + malloc arenas.

Q: Recommended heap share of the container limit?
A: 50–70%. Start at 60% for an I/O-heavy Spring service and refine with NMT.

Q: How do you measure the real native breakdown?
A: `-XX:NativeMemoryTracking=summary` then `jcmd <pid> VM.native_memory summary` (and `summary.diff` to watch it grow).

Q: What does `-XX:+UseContainerSupport` do?
A: (Default since JDK 10) makes the JVM read the cgroup memory/CPU limits rather than host values, so `MaxRAMPercentage` and GC ergonomics respect the container.

Q: How do you verify the JVM saw the cgroup limit?
A: `jcmd <pid> VM.flags`, `jcmd <pid> VM.system_properties`, and `Runtime.maxMemory()` from inside the pod.

Q: cgroup v2 files you actually read?
A: `/sys/fs/cgroup/memory.max`, `memory.current`, `memory.stat`, `cpu.stat` (`nr_throttled`, `throttled_usec`), `pids.current`.

Q: Why does `-Xmx == container limit` guarantee an OOM-kill?
A: Zero native headroom. Metaspace + code cache alone are commonly 400–500 MB; add thread stacks and direct buffers and you cross the cap with the heap nowhere near full.

Q: Direct buffers and `MaxDirectMemorySize`?
A: Netty/NIO direct buffers are native, outside `-Xmx`. Bound them explicitly or you get `OutOfMemoryError: Direct buffer memory` *or* a silent cgroup kill.

Q: Thread stack budget?
A: `threads × -Xss`. 400 threads × 512 KB = 200 MB native. Often the largest single native consumer in a blocking Spring service.

---

## Probes

Q: What does `livenessProbe` decide?
A: "Is this process wedged?" Failure → container is killed and restarted.

Q: What does `readinessProbe` decide?
A: "Should this pod receive traffic?" Failure → removed from Service endpoints, process untouched.

Q: What does `startupProbe` decide?
A: "Has the app finished starting?" Until it succeeds, liveness and readiness checks are skipped.

Q: Why does liveness never depend on a downstream?
A: A slow dependency fails liveness everywhere at once → simultaneous restart of all pods → no pod survives to serve or recover. Cascade.

Q: Recommended probe timings for a Spring Boot service?
A: startup: `failureThreshold: 30 × periodSeconds: 5` (150 s budget); readiness: `periodSeconds: 5`, `timeoutSeconds: 2`; liveness: `periodSeconds: 10`, `timeoutSeconds: 2`, `failureThreshold: 3` (~30 s to detect a wedge).

Q: `initialDelaySeconds` vs `startupProbe`?
A: Use `startupProbe` for warmup (JVM boot, class loading, JIT, cache fill) and keep `initialDelaySeconds: 0` on liveness so real hangs are detected quickly.

Q: `timeoutSeconds` on liveness should be?
A: Tight (1–2 s) and shorter than the probe period. A slow liveness endpoint under load causes false kills.

Q: Should the liveness endpoint be cheap?
A: Yes — no DB, no dependency fan-out, no serialization. Return 200 if the main loop is scheduled. `management.endpoint.health.livenessgroup` exists for this.

Q: Readiness that does real work — why risky?
A: If readiness checks a dependency, a dependency blip removes every pod from the endpoints and takes the service fully offline. Readiness should be "can I serve what I have", often with cached/degraded capability.

Q: Probe path convention?
A: `/actuator/health/liveness`, `/actuator/health/readiness`, `/actuator/health/startup` with `management.endpoint.health.probes.enabled=true` and a non-`/` health base path.

---

## Resources, QoS, scheduling

Q: Three QoS classes?
A: Guaranteed (`requests == limits` for all containers), Burstable (some set), BestEffort (nothing set). Eviction order is BestEffort → Burstable → Guaranteed.

Q: CPU limits and CFS throttling period?
A: 100 ms. A burst that exceeds the quota inside one period is frozen for the remainder — an involuntary stall invisible to JVM tooling.

Q: Metric for throttling?
A: `container_cpu_cfs_throttled_seconds_total` (cAdvisor), `container_cpu_cfs_throttles_total`, or `cpu.stat` in cgroup v2.

Q: Recommendation for a latency-critical service?
A: `requests.cpu == limits.cpu` — the scheduler reserves instead of throttling. Do not do this for bursty batch jobs.

Q: Node density constraint?
A: `Σ (pods on node × memory requests) ≤ allocatable × headroom`. Requests are the scheduler's reservation; exceeding it evicts.

Q: `ephemeral-storage` request/limit?
A: Bound container writable layer + logs + `emptyDir`. `emptyDir` counts against the pod's ephemeral storage (or the node's if `sizeLimit` is set).

Q: What QoS class do most Java services accidentally land in?
A: Burstable — `requests.memory: 1Gi`, `limits.memory: 2Gi` — which means they are the *first* thing evicted under node memory pressure.

Q: HPA metrics that work better than CPU for JVM services?
A: Business-level per-request cost, queue/concurrency depth, p99 latency, or a KEDA/Kafka-lag scale target. CPU % over a small denominator is jumpy.

Q: HPA oscillation fix?
A: Correct `requests`, set `stabilizationWindowSeconds` (e.g. 300 down / 0 up), use a custom/external metric with a longer window, and add `behavior` scale-down stabilization.

Q: Proportional vs percent-based HPA?
A: Percent-based ignores pod size; with heterogeneous pods (canary 1x, stable 2x) use a resource metric with `target.averageValue` so one pod does not count the same as two.

---

## Availability & disruption

Q: What does a `PodDisruptionBudget` govern?
A: Voluntary evictions only (node drains, `kubectl drain`, autoscaler scale-down). In no way does it block OOM-kill or node loss.

Q: `minAvailable` vs `maxUnavailable`?
A: `minAvailable` is an absolute floor (stable under scale-up); `maxUnavailable` is a relative step (scales with replicas). Pick one and don't set both.

Q: Why `minAvailable` on a Deploy with HPA can block autoscaler scale-down?
A: The scale-down is a voluntary disruption; a PDB with a high `minAvailable` can deadlock it. Verify autoscaler behavior with PDBs at your min replica count.

Q: Topology spread constraint for?
A: Spreading replicas across zones/hosts so one zone or node failure cannot take all of them.

Q: Anti-affinity vs topology spread — which to prefer?
A: `topologySpreadConstraints` with `ScheduleAnyway` is generally simpler and handles uneven zone sizes; preferred anti-affinity is a reasonable alternative.

Q: Rolling update parameters that matter?
A: `maxUnavailable` / `maxSurge` (availability vs speed), `minReadySeconds` (wait for real readiness), `progressDeadlineSeconds` (fail the rollout rather than hang), `progressDeadlineSeconds` > startup-probe budget.

Q: Why `maxUnavailable: 0` with `maxSurge: 1`?
A: Zero-downtime: always add the new pod before removing the old. Costs one extra pod's resources for the rollout duration.

Q: What is a `PreStop` hook for?
A: It runs *before* SIGTERM. A `sleep 10` covers endpoint-removal propagation so the LB stops routing before the JVM stops accepting.

Q: Graceful shutdown checklist for Spring Boot?
A: `server.shutdown=graceful`, `spring.lifecycle.timeout-per-shutdown-phase`, a `ContextClosedEvent` listener to stop accepting + flush telemetry, `terminationGracePeriodSeconds` ≥ drain estimate.

---

## Failure & debugging

Q: `OOMKilled` vs `OutOfMemoryError`?
A: `OOMKilled` = cgroup limit crossed (no JVM error in logs). `OutOfMemoryError` = Java heap/metaspace/direct exhaustion. Different root causes, different fixes.

Q: `CrashLoopBackOff` first command?
A: `kubectl describe pod <p>` → `Last State: Terminated / Reason / Exit Code`, then `kubectl logs <p> --previous`.

Q: Exit 137 with `Reason: Error` (not `OOMKilled`) means?
A: Likely SIGKILL from a failed liveness probe or a grace-period escalation, not the memory OOM killer.

Q: `Pending` pod?
A: Scheduling failure: insufficient CPU/memory/ephemeral storage on any node, missing PVC, image pull, or affinity conflict. Read the `Events` at the bottom of `describe`.

Q: `ImagePullBackOff` + `ErrImagePull`?
A: Bad tag, registry auth, or rate limit. Verify the tag exists and the pull secret is valid.

Q: `ErrImagePull` with a valid tag but `toomanyrequests`?
A: Registry rate limit. Use immutable tags + a pull-through cache or mirror.

Q: `CreateContainerConfigError` mentioning secret name?
A: Referenced `env.valueFrom.secretKeyRef` does not exist in the namespace (common after a namespace migration).

Q: Node memory pressure eviction signal?
A: `kubectl get node` shows `MemoryPressure=True`; `kubectl get events --field-selector reason=Evicted`; pod status reason `Evicted` with message naming the resource.

Q: Debugging a stuck pod's JVM?
A: `kubectl exec -it <p> -- jcmd 1 Thread.print`, `VM.native_memory summary`, `jstat -gcutil 1 1000`, `jmap -histo:live 1`.

Q: Safe heap dump from a running pod?
A: `jcmd <pid> GC.heap_dump` to a mounted volume — the JVM must be able to write it or it will OOM-kill trying.

Q: Kubernetes Events TTL?
A: Default ~1 hour. Anything older is gone; export events to a durable store if you intend to use them for RCA.

Q: What is `kubectl debug` with an ephemeral container for?
A: Inspecting a running pod's filesystem, cgroup stats, and network namespace without changing the image or restarting it.

---

## Hardening & config defaults

Q: `securityContext` essentials for a Java container?
A: `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, `seccompProfile.type: RuntimeDefault`, `readOnlyRootFilesystem: true`.

Q: If `readOnlyRootFilesystem: true`, what must be mounted?
A: `java.io.tmpdir`, GC log directory, heap-dump directory — as `emptyDir` (bounded by `sizeLimit`) or a PVC.

Q: `automountServiceAccountToken`?
A: Set `false` unless the pod actually calls the Kubernetes API. Most services do not.

Q: JVM flags worth defaulting on in a container?
A: `-XX:+ExitOnOutOfMemoryError`, `-XX:+HeapDumpOnOutOfMemoryError`, `-XX:MaxDirectMemorySize`, `-XX:MaxMetaspaceSize`, `-Xss`, `-Xlog:gc*` with rotation, `-XX:+UseContainerSupport`.

Q: Multi-stage Dockerfile for a Java service?
A: Build stage with the full JDK (or a toolchain image) → distroless/JRE runtime stage with only the jar. Never ship a JDK in production.

Q: Pin the base image?
A: Pin by digest, not by floating tag. Reproducible rollbacks and no surprise CVEs or JVM changes.

Q: `-XX:+ExitOnOutOfMemoryError` — why not just log?
A: A process after OOME is usually corrupted (wedged GC, poisoned caches, half-released locks). A deterministic fast crash beats a limping process.

---

## Numbers to memorize

Q: CFS throttle period?
A: 100 ms.

Q: Recommended heap share of container limit?
A: 50–70% (60% is a defensible default; verify with NMT).

Q: Recommended `-Xss` for I/O services?
A: 512 KB; budget `threads × 512 KB` explicitly.

Q: Typical metaspace + code cache for a Spring Boot app?
A: ~250 MB metaspace, ~150–250 MB code cache. Add that before sizing the heap.

Q: Default `terminationGracePeriodSeconds`?
A: 30 s — which is why a 60 s request timeout guarantees cut-off requests on deploy.

Q: `preStop` sleep to use?
A: 5–15 s, sized to cover endpoint-removal propagation at your ingress/proxy.

Q: Safe node memory headroom?
A: Keep Σ requests ≤ ~70–80% of allocatable so eviction has somewhere to go.

Q: Startup-probe budget for a large Spring app?
A: 30 × 5 s = 150 s. Size it from your slowest observed cold start × 2.

Q: Probe weight to keep fast?
A: Readiness ~2 s (it gates traffic), liveness ~30 s detection (it kills pods). Getting these backwards causes outages either way.
