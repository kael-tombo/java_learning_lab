# Lab 07: Kubernetes for Java Architects — Math Foundation

Kubernetes turns every resource decision into a division problem. These are the numbers you must be able to do in your head while reviewing a manifest.

---

## 1. Container memory budget (the OOM-kill formula)

```
memory_limit = heap + metaspace + code_cache + thread_stacks + direct + gc_structures + jvm_native
```

Worked example — Spring Boot REST service, 200 threads, Netty direct buffers:

```
heap            = 1,200 MB
metaspace       =   250 MB
code cache      =   200 MB
thread stacks   = 200 × 512 KB = 100 MB
direct buffers  =   300 MB
GC + JVM + agent=   250 MB
                        -------
total RSS                2,300 MB
```

Set `limits.memory: 2300Mi` (round to 2500Mi) and `requests.memory: 2500Mi`, then `-XX:MaxRAMPercentage=52` (1200/2300). Set it explicitly rather than as a percentage when the native share is known — percentages hide the reasoning.

**Verification**: NMT must account for the non-heap terms within ±10%:
```
jcmd 1 VM.native_memory summary
```

---

## 2. Heap-from-percentage back-calculation

Given a limit `L` and a target native overhead `N` (measured), solve for the percentage:

```
MaxRAMPercentage = 100 × (L − N) / L
```

`L = 2 Gi = 2048 MB`, `N = 700 MB` → `100 × 1348 / 2048 = 65.8%` → use `65`.

If you set `75` instead: heap = 1536 MB, leaving 512 MB for 700 MB of native → **guaranteed OOM-kill** even though the heap is only 40% full. This single arithmetic error is the lab's headline failure mode.

---

## 3. Pod density and scheduling feasibility

```
Σ (replicas_per_node × requests.memory) ≤ allocatable × headroom_factor
```

Node: 64 GB RAM total, ~61 GB allocatable. 8 pods/node, `requests.memory: 2.5Gi` each:

```
8 × 2.5 = 20 Gi per node   →  20 / 61 = 33% density  → fine
```

Now 24 pods/node (over-committed for latency reasons):

```
24 × 2.5 = 60 Gi  →  60 / 61 = 98% density  →  no room for anything; eviction begins at ~100%
```

**Rule**: keep Σ requests ≤ 70–80% of allocatable so eviction has somewhere to go. At 80% density, one OOM-killed pod's memory is immediately reclaimable; at 98%, it is not.

---

## 4. CPU requests, limits, and throttling

```
quota_per_period = limits.cpu × 0.1 s          (CFS period = 100 ms)
throttle_time    = max(0, cpu_burst_in_period − quota_per_period)
```

`limits.cpu: 1`, request handles 150 ms of CPU in one 100 ms period:

```
quota = 0.1 s ; used = 0.15 s  →  throttled for 0.05 s  →  50 ms involuntary stall
```

Little's Law converts that stall into extra concurrency:

```
ΔL = λ × ΔW
```

`λ = 800 req/s`, `ΔW = 0.05 s` → `ΔL = 40` extra in-flight requests, each holding a thread and a connection. At 20 concurrent throttle events/s that is 800 extra concurrent requests — a self-driving collapse. Fix: `requests.cpu == limits.cpu`.

---

## 5. Replica math from a capacity model

```
cores_per_pod = λ_per_pod × (W_cpu + W_io) / U_target
replicas      = ceil( λ_peak / cores_per_pod )
```

`λ_peak = 3,000/s`, `W_cpu = 3 ms`, `W_io = 15 ms`, `U = 0.6`:

```
W = 0.018 s
cores_per_req = 0.018 / 0.6 = 0.030 cores
cores needed  = 3,000 × 0.030 = 90 cores
4-core pods    →  90 / 4 = 22.5  →  23 replicas
```

Then memory: per-pod heap is fixed, so 23 replicas × 2.5 Gi = 57.5 Gi of *requests*. Spread over 8 nodes of 61 Gi allocatable that is 7.2 pods/node → `maxSurge: 1` during rollout pushes to 8.2 → **cannot schedule**. The rollout gets stuck until you add a node or lower `requests`. Capacity math must include surge and disruption headroom.

---

## 6. Probe timing budget

```
detection_time = failureThreshold × periodSeconds + timeoutSeconds
max_startup    = startup.failureThreshold × startup.periodSeconds
```

| Purpose | Desired | Config |
|---|---|---|
| Detect a wedged process | ≤ 30 s | `periodSeconds: 10`, `failureThreshold: 3` |
| Detect a lost listener | ≤ 10 s | `periodSeconds: 5`, `failureThreshold: 2` |
| Allow cold start | ≥ 2× observed worst start | `periodSeconds: 5`, `failureThreshold: 30` → 150 s |

Using `initialDelaySeconds: 120` on liveness to achieve a 120 s startup budget costs 120 s of *detection* latency for every subsequent wedge. A startup probe costs nothing at steady state — that asymmetry is the entire argument for it.

---

## 7. Rollout availability during a rolling update

```
available_pods = replicas − maxUnavailable
new_pods_needed = replicas − min(maxUnavailable, maxSurge)
```

With `replicas: 6`, `maxUnavailable: 1`, `maxSurge: 2`:

```
available at all times = 6 − 1 = 5   → 83.3% of full capacity throughout
peak pods              = 6 + 2 = 8   →  the memory/scheduler constraint that matters
```

With `maxUnavailable: 0`, `maxSurge: 1`:

```
available = 6 (100%), peak pods = 7, but the rollout takes ~2× longer
```

**Cost of zero downtime in this lab**: `1/6` extra nodes for the rollout duration, plus `minReadySeconds` × 6 sequential additions. That is a business decision, not a technical one — know both numbers before arguing for either.

---

## 8. Graceful shutdown / drain math

```
drain_time = max( in_flight / throughput , p99.9_request_time )
```

`in_flight = 400`, `throughput = 300/s`, `p99.9 = 12 s` (one slow dependency path):

```
drain = max( 400/300 , 12 ) = max(1.3 s, 12 s) = 12 s
terminationGracePeriodSeconds ≥ drain + preStop_sleep + slack
                          ≥ 12 + 10 + 5 = 27 s  →  use 45 s
```

Default is 30 s — barely enough here, catastrophically short for any service with a 30 s upstream timeout. Requests cut by SIGKILL become 502s attributed to "the deploy".

---

## 9. PDB and availability budget

```
unavailable_during_drain = floor( replicas × (1 − minAvailable/replicas) )   [minAvailable form]
                            maxUnavailable = replicas − minAvailable
```

`replicas: 6`, `minAvailable: 4` → at most 2 evicted at once (33%).

Drain time for a 60-node cluster, one node at a time, `maxUnavailable: 2`, ~90 s pod termination:

```
total_drain ≈ (60 nodes / 2 concurrent) × 90 s = 45 min
```

So a cluster upgrade is a 45-minute window in which you are permanently running at 67% capacity. If peak load needs 100%, you cannot upgrade in business hours without temporary extra nodes — plan for that rather than discovering it during the upgrade.

---

## 10. HPA replica math

```
desired_replicas = ceil( current_replicas × current_metric / target_metric )
```

`replicas: 6`, CPU 240 m average, target 200 m:

```
desired = ceil(6 × 240/200) = ceil(7.2) = 8
```

Next cycle at 210 m → `ceil(8 × 1.05) = 9`. At 190 m → `ceil(9 × 0.95) = 9`. The rounding to `ceil` plus a metric hovering at target produces the classic +1/−1 oscillation. Fixes:

- `stabilizationWindowSeconds: 300` on scale-down → picks the *highest* recommendation in the window.
- Raise the target above typical (e.g. 400 m) so the metric is not sitting on the trigger.
- Use a longer metric window (`KEDA` / external metric on 5-minute rate).

---

## 11. Ephemeral storage math

```
ephemeral_per_pod = emptyDir(sizeLimit) + writable_layer + log_volume
                   ≤ requests.ephemeral-storage   (else BestEffort→Burstable penalty & eviction)
```

`emptyDir: 2Gi`, GC logs `filecount=5, filesize=100m` = 500 MB, heap dump worst case ≈ heap = 1.2 GB, image layer writes ~50 MB:

```
total ≈ 2 + 0.5 + 1.2 + 0.05 = 3.75 Gi  →  set requests.ephemeral-storage: 4Gi, sizeLimit on emptyDir: 1Gi
```

Heap dumps to ephemeral storage are how a single OOM turns into an eviction cascade on a busy node. Mount a PVC with a real sizeLimit.

---

## 12. Availability of the deployment itself

```
A_service = 1 − Π (1 − A_i)      over independent components
```

Replica-level availability with `unavailable_budget` during a normal period (no rollout):

```
A = (replicas − unavailable) / replicas = 5/6 = 83.3%
```

Kubernetes cluster-level availability is a product of control-plane and node failure rates, so it is high in practice — but the number that matters for a Java service is *schedulability at peak*: if `replicas × requests` exceeds allocatable, `A` collapses to zero regardless of node hardware.

---

## 13. Resource requests per-request cost (better HPA signal)

```
cpu_per_request_millis = Δcpu_millis_total / Δrequests_total
custom_metric_value    = queue_depth + inflight − target_concurrency
```

At steady state `cpu_per_request = 30 ms` and `queue_depth` is far smoother than CPU %. An HPA on `queue_depth` targeting 200 with `replicas: 6` and observed 240:

```
desired = ceil(6 × 240/200) = 8
```

Because queue depth reflects *work waiting* rather than instantaneous CPU, it does not spike on GC pauses or on a JIT compilation burst — it measures the thing you actually want to scale.

---

## 14. Quick drills

1. `limits: 2Gi`, `-Xmx1g`, 250 MB metaspace, 200 code cache, 200 threads × 512 KB, 300 MB direct, 250 MB JVM. Does it fit? **Answer: RSS ≈ 2.2 GB > 2 GB → OOM-kill. Set `MaxRAMPercentage≈50`, or raise the limit to 2.5Gi.**
2. Node 61 Gi allocatable, 8 pods × 2.5 Gi requests. Density? **Answer: 20/61 = 33%. Safe.**
3. `limits.cpu: 1`, burst of 150 ms CPU in a period. Stall? **Answer: 50 ms. At λ=800/s that is +40 concurrent requests.**
4. `replicas: 6`, `maxUnavailable: 1`, `maxSurge: 2`. Available and peak pods? **Answer: 5 available (83%), 8 peak.**
5. `in_flight 400`, throughput 300/s, `p99.9 = 12s`, `preStop` 10 s. Grace period? **Answer: ≥27 s → use 45 s.**
6. Cold start 75 s observed. Startup probe config? **Answer: `periodSeconds: 5, failureThreshold: 30` (150 s) — double the worst observed.**
7. HPA at 6 replicas, metric 240 m, target 200 m. **Answer: desired 8, and expect rounding-driven oscillation → add stabilization.**

---

## 15. Formulas worth memorizing

| Formula | Use |
|---|---|
| `memory_limit = heap + metaspace + code + stacks + direct + native` | container sizing; the OOM-kill equation |
| `MaxRAMPercentage = 100 × (L − N) / L` | derive heap share from measured native overhead |
| `Σ pods × requests ≤ allocatable × 0.75` | scheduling feasibility and density headroom |
| `quota = limits.cpu × 0.1 s`, `ΔL = λ × ΔW_throttle` | CFS throttling → latency incident |
| `replicas = λ_peak × (W_cpu+W_io) / (U × cores_per_pod)` | capacity model |
| `detection = failureThreshold × period` | probe timing |
| `available = replicas − maxUnavailable` | rollout availability |
| `drain = max(in_flight/throughput, p99.9)` | `terminationGracePeriodSeconds` |
| `desired = ceil(current × metric/target)` | HPA; watch for rounding oscillation |
| `A = (replicas − unavailable)/replicas` | availability from replica budget |
