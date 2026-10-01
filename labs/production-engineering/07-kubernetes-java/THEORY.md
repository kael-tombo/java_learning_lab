# THEORY: Kubernetes & Container Engineering for Mission-Critical Java
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Linux Cgroups (v1 vs. v2) and JVM Container Ergonomics

Containers are not lightweight virtual machines; they are standard Linux processes executing within isolated kernel namespaces (`pid`, `net`, `ipc`, `mnt`, `uts`, `user`) and constrained by **Linux Control Groups (cgroups)**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Linux Kernel Host                             │
├────────────────────────────────────────────────────────────────────────┤
│                          Cgroups Subsystem                             │
│                                                                        │
│   ┌──────────────────────────────┐    ┌────────────────────────────┐   │
│   │       cgroups v1             │    │         cgroups v2         │   │
│   │  (Legacy Multi-Hierarchy)    │    │   (Unified Single Hierarchy│   │
│   ├──────────────────────────────┤    ├────────────────────────────┤   │
│   │ /sys/fs/cgroup/cpu/cpu.stat  │    │ /sys/fs/cgroup/cpu.stat    │   │
│   │ /sys/fs/cgroup/memory/...    │    │ /sys/fs/cgroup/memory.max  │   │
│   │ memory.limit_in_bytes        │    │ memory.current             │   │
│   │ cpu.cfs_quota_us             │    │ cpu.max                    │   │
│   └──────────────┬───────────────┘    └──────────────┬─────────────┘   │
└──────────────────┼───────────────────────────────────┼─────────────────┘
                   │                                   │
                   ▼                                   ▼
        ┌────────────────────────────────────────────────────────┐
        │       OpenJDK 17 / 21 JVM Ergonomics Engine            │
        │             (-XX:+UseContainerSupport)                 │
        ├────────────────────────────────────────────────────────┤
        │ • os::active_processor_count()                         │
        │ • MaxRAMPercentage (Heap = Container RAM × 75%)        │
        │ • Garbage Collector Thread Sizing (ParallelGCThreads)  │
        │ • JIT Compiler Thread Pool Sizing (CICompilerCount)    │
        └────────────────────────────────────────────────────────┘
```

### 1.1 Cgroup CPU Accounting Mechanics
The Linux Completely Fair Scheduler (CFS) enforces CPU bandwidth through two metrics:
- **`cpu.cfs_period_us` (v1) / `cpu.max` period (v2)**: The enforcement tracking window (default $100,000\mu\text{s} = 100\text{ms}$).
- **`cpu.cfs_quota_us` (v1) / `cpu.max` quota (v2)**: Total CPU execution time allowed across all threads within that period.

$$\text{Effective vCPUs} = \frac{\text{cfs\_quota\_us}}{\text{cfs\_period\_us}} = \frac{200{,}000\mu\text{s}}{100{,}000\mu\text{s}} = 2.0\text{ vCPUs}$$

### 1.2 Cgroup Memory Accounting & The Linux OOM-Killer
In cgroups v1:
$$\text{Container Memory} = \text{RSS (Anonymous)} + \text{Page Cache (File-backed)} + \text{Swap}$$
In cgroups v2, accounting is unified:
- `memory.current`: Total active memory.
- `memory.max`: Hard limit. When crossed, the Linux kernel invokes the Out-Of-Memory Killer (`oom-killer`) to terminate the highest badness process (Exit Code 137).
- `memory.high`: Throttling boundary before hard kill.

### 1.3 JVM Container Awareness (`-XX:+UseContainerSupport`)
Enabled by default in modern OpenJDK (17 and 21):
1. **CPU Count Detection**: HotSpot determines `Runtime.getRuntime().availableProcessors()` by calculating:
   $$\text{Processors} = \max\left(1, \left\lfloor \frac{\text{quota}}{\text{period}} \right\rfloor \right)$$
   This dictates the sizing of `ForkJoinPool.commonPool()`, Parallel GC threads, and JIT compilation worker threads.
2. **RAM Sizing**: Instead of reading physical host DRAM (`/proc/meminfo`), HotSpot sizes default heap based on container memory limits:
   $$\text{Default Max Heap} = \text{Container Memory Limit} \times \frac{\text{MaxRAMPercentage}}{100}$$

---

## 2. CFS CPU Quota Throttling: The Multi-Threaded Latency Collapse

Configuring `resources.limits.cpu` in Kubernetes manifests introduces Linux CFS throttling into multi-threaded Java applications:

```
CFS Period = 100ms (Total quota = 200ms for 2 cores limit)
Time (ms): 0ms               25ms                                        100ms
           ┌──────────────────┬────────────────────────────────────────────┐
8 Threads: │ 8 × 25ms = 200ms │       THROTTLED! KERNEL FREEZES ALL        │
Active     │ Quota Exhausted! │       THREADS FOR 75 MILLISECONDS          │
           └──────────────────┴────────────────────────────────────────────┘
                              ▲
                              └─ Client requests experience 75ms stall!
```

### The Mathematics of Throttling
Assume a Spring Boot application running on Tomcat or Netty with 16 worker threads:
- Container limit: `2000m` (2 vCPUs $\rightarrow 200\text{ms}$ quota per 100ms period).
- A burst of 10 incoming HTTP requests causes 16 threads to wake up.
- Each thread performs 12.5ms of work (JSON parsing, auth verification, DB query preparation):
  $$\text{CPU Time Used} = 16 \text{ threads} \times 12.5\text{ms} = 200\text{ms}$$
- In just **12.5ms of real wall-clock time**, the container has consumed its entire 200ms quota for the 100ms period!
- For the remaining **87.5ms**, the Linux CFS scheduler removes the container's threads from the CPU runqueue.
- **The Consequence**: Every concurrent client request experiences an $87.5\text{ms}$ stall, driving P99 latency through the roof, even though host node CPU is $80\%$ idle!

**FinOps & Production Standard**:
Omit `resources.limits.cpu` on production Java workloads. Enforce QoS via `resources.requests.cpu` to guarantee scheduling slots while allowing unthrottled CPU bursting during micro-spikes.

---

## 3. Kubernetes Pod Termination Lifecycle & Zero-Downtime Drain

When Kubernetes deletes a pod (during rolling updates, node drains, or HPA scale-downs), a critical race condition occurs between the **API plane** and the **data plane**:

```
                       [T=0s: Pod Deletion Initiated]
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         ▼                                                       ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│ Control Plane (Async Network)   │             │ Kubelet (Local Node Execution)  │
├─────────────────────────────────┤             ├─────────────────────────────────┤
│ 1. EndpointSlice controller     │             │ 1. Executes PreStop Hook        │
│    marks pod not ready          │             │    (e.g., sleep 15s)            │
│ 2. kube-proxy updates iptables  │             │ 2. Kubelet sends SIGTERM        │
│ 3. Ingress / Envoy updates      │             │ 3. Spring Boot graceful drain   │
│    upstream cluster endpoints   │             │ 4. Kubelet sends SIGKILL        │
│ [Duration: 2.0 to 8.0 seconds!] │             │    after terminationGracePeriod │
└─────────────────────────────────┘             └─────────────────────────────────┘
```

### 3.1 The 502 Bad Gateway Race Condition
If Java handles `SIGTERM` by immediately terminating the embedded HTTP server:
- Kubelet initiates shutdown at $T=0$.
- Java stops accepting connections at $T+0.2\text{s}$.
- Meanwhile, Ingress/Envoy or upstream services take **2 to 5 seconds** to propagate the removal through distributed etcd and kube-proxy iptables rules.
- Any request dispatched by Ingress between $T+0.2\text{s}$ and $T+5.0\text{s}$ reaches a dead socket, generating **`502 Bad Gateway` / `Connection Refused`** errors for active users!

### 3.2 The Bulletproof Production PreStop Pattern
```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: app
      lifecycle:
        preStop:
          exec:
            # 15s sleep allows Ingress/kube-proxy routing tables to drain before SIGTERM
            command: ["/bin/sh", "-c", "sleep 15"]
```
**Sequence of Events**:
1. At $T=0$, pod is marked `Terminating`.
2. EndpointSlice controller removes pod from endpoints. Ingress removes pod from upstream load balancing pools.
3. The pod's `preStop` hook executes `sleep 15`. During this 15 seconds, **Java continues accepting and processing requests**.
4. By $T=8\text{s}$, all Ingress routers have purged the pod. No new traffic arrives.
5. At $T=15\text{s}$, `sleep` exits and kubelet sends `SIGTERM`.
6. Spring Boot catches `SIGTERM`, activates `server.shutdown: graceful`, finishes active in-flight requests, and cleanly closes DB connection pools.
7. Zero dropped requests; $100\%$ zero-downtime rolling deploys.

---

## 4. Sub-Second Startup: GraalVM Native Image vs. CRaC vs. AppCDS

Java applications traditionally exhibit slow startup and high warmup latency ("JIT warmup tax") due to class loading, bytecode verification, and tiered compilation (C1 $\rightarrow$ C2). In dynamic Kubernetes autoscaling (KEDA / HPA), cold starts of 15–30 seconds lead to request queuing.

```
Startup Latency Spectrum (Spring Boot 3.x / Java 21):
┌────────────────────────────────────────────────────────────────────────┐
│ Standard JIT:           15,000 - 30,000 ms (15 - 30s)                  │
├────────────────────────────────────────────────────────────────────────┤
│ AppCDS (Class Sharing):  4,000 -  8,000 ms (4 - 8s)                   │
├────────────────────────────────────────────────────────────────────────┤
│ GraalVM Native Image:       30 -    100 ms (Sub-second)                │
├────────────────────────────────────────────────────────────────────────┤
│ CRaC (Checkpoint/Restore):  15 -     40 ms (Near-instantaneous)        │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1 GraalVM Native Image (Ahead-Of-Time Compilation)
- **Mechanism**: Compiles Java bytecode directly into a standalone architecture-specific native machine ELF binary using closed-world analysis.
- **Advantages**: $30\text{ms}$ startup, tiny base memory footprint (50–100MB RSS).
- **Trade-offs**: Closed-world assumption breaks dynamic runtime reflection, serialization, and dynamic class loading without extensive reachability metadata. Peak sustained throughput is often $5\% - 15\%$ lower than C2 JIT because AOT cannot optimize for live runtime profiling and hardware topology.

### 4.2 Project CRaC (Coordinated Restore at Checkpoint)
- **Mechanism**: Leverages Linux kernel **CRIU (Checkpoint/Restore in Userspace)**.
- **Workflow**:
  1. Boot the JVM on standard OpenJDK, warm up JIT compilers, execute synthetic warmup traffic.
  2. Take a memory and process snapshot using `jcmd JDK.checkpoint`. The JVM serializes its entire heap, JIT-compiled native code, and Metaspace to disk.
  3. When scaling up pods in Kubernetes, boot from the saved checkpoint:
     ```bash
     java -XX:CRaCRestoreFrom=/opt/crac-checkpoint
     ```
  4. The JVM restores in **15 to 40 milliseconds** with **already fully-warmed C2 JIT optimized code**!
- **Trade-offs**: Requires coordinated lifecycle callbacks (`Resource.beforeCheckpoint()` / `afterRestore()`) to close and reopen open file descriptors, network sockets, and database connections.

### 4.3 AppCDS (Application Class Data Sharing)
- Dumps pre-processed class metadata into a memory-mapped archive (`.jsa`), cutting startup time by $40\% - 50\%$ without any code modifications or reflection limitations.

---

## 5. Kubernetes DNS Resolution Architecture & The `ndots:5` Penalty

In high-throughput microservices, internal DNS lookups to CoreDNS frequently become a major latency bottleneck.

### 5.1 The `ndots:5` Resolution Explosion
By default, Kubernetes configures `/etc/resolv.conf` in pods with:
```text
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local c.project.internal
options ndots:5
```
**The Mechanics**:
If a hostname contains fewer than 5 dots (e.g. `order-service` or external `api.stripe.com` which has 2 dots), the resolver sequentially appends each domain in the search path before attempting the query as an absolute FQDN:
1. `api.stripe.com.default.svc.cluster.local` $\rightarrow$ NXDOMAIN (CoreDNS query 1)
2. `api.stripe.com.svc.cluster.local` $\rightarrow$ NXDOMAIN (CoreDNS query 2)
3. `api.stripe.com.cluster.local` $\rightarrow$ NXDOMAIN (CoreDNS query 3)
4. `api.stripe.com.c.project.internal` $\rightarrow$ NXDOMAIN (CoreDNS query 4)
5. `api.stripe.com.` $\rightarrow$ SUCCESS (CoreDNS query 5)

**Every single external HTTP call triggers 5 distinct UDP round-trips to CoreDNS!**
Under 10,000 requests/sec, this floods CoreDNS, causing packet drops, DNS timeouts (5-second default glibc timeout), and catastrophic service degradation.

### 5.2 The JVM DNS Cache TTL Trap
HotSpot JVM caches DNS lookups forever by default if a security manager was present, or for 30 seconds:
- If a Kubernetes Service IP shifts or pod endpoints roll, stale JVM DNS caches route traffic to dead IP addresses.
- **Production Standard**:
  ```bash
  -Dnetworkaddress.cache.ttl=5
  -Dnetworkaddress.cache.negative.ttl=2
  ```

### 5.3 DNS Pod-Level Optimization
Use Fully Qualified Domain Names with a trailing dot (`api.stripe.com.`) or tune `dnsConfig`:
```yaml
dnsConfig:
  options:
    - name: ndots
      value: "2"
```

---

## 6. Sizing Garbage Collectors for Containers

| Container Memory Limit | Recommended GC | Heap Ratio (`-XX:MaxRAMPercentage`) | Architectural Rationale |
|:---|:---:|:---:|:---|
| **$\le 2.0\text{ GiB}$** | **SerialGC** | $70.0\%$ | Parallel/G1 threads consume too much memory and CPU overhead in tiny pods |
| **$2.0 - 8.0\text{ GiB}$** | **G1GC** | $75.0\%$ | Balanced pause time ($< 200\text{ms}$) with low thread footprint and region compaction |
| **$> 8.0\text{ GiB}$** | **Generational ZGC** | $75.0\%$ | Sub-millisecond pause times ($\le 1\text{ms}$) with active heap uncommit back to OS |

**Rule of Thumb for Memory Margins**:
Always reserve **$25\%$ of the container's memory limit** for non-heap allocations (Metaspace, thread stacks, Code Cache, and Netty direct memory buffers) to prevent the Linux kernel from terminating the pod with Exit Code 137.
