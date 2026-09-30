# THEORY: Running Java Applications on Kubernetes & Containers
## Lab 07 | Production Engineering Academy

---

## 1. Linux Cgroups (v1 vs v2) and JVM Container Ergonomics

### Cgroup Mechanics
Containers do not have a private kernel; they are isolated Linux processes governed by Control Groups (`cgroups`):
- **CPU Quota (`cpu.cfs_quota_us` / `cpu.cfs_period_us`)**: Enforces how much CPU time in microseconds the process is allowed within each scheduling period (default $100,000\mu\text{s} = 100\text{ms}$).
  $$\text{vCPU} = \frac{\text{quota}}{\text{period}}$$
- **Memory Limit (`memory.limit_in_bytes` in v1, `memory.max` in v2)**: Hard limit on physical memory RSS + page cache.

### JVM Container Awareness
Prior to Java 8u191 and Java 10, the JVM was unaware of cgroups. It queried `/proc/meminfo` and `/proc/cpuinfo`, seeing the **host node's total RAM (e.g. 256 GB) and 64 cores** instead of the container's 4 GB limit! This caused default heap allocations ($256 / 4 = 64\text{ GB}$) to immediately trigger the Linux OOM Killer.

Modern OpenJDK (17 and 21) includes native `-XX:+UseContainerSupport`:
- It reads `/sys/fs/cgroup/memory` or `/sys/fs/cgroup/cgroup.controllers`.
- Calculates available processors via `os::active_processor_count()`.
- Sets default heap based on `-XX:MaxRAMPercentage`.

---

## 2. CFS CPU Quota Throttling: The Silent Latency Killer

When a Kubernetes deployment specifies:
```yaml
resources:
  limits:
    cpu: "2" # 200,000us per 100ms period
```
If a Java service with 32 active threads bursts simultaneously, it consumes $32 \times 6.25\text{ms} = 200\text{ms}$ of CPU within the first **7 milliseconds** of the 100ms CFS period!
For the remaining **93 milliseconds**, the Linux kernel suspends all threads in the container.
- Result: Severe p99 latency spikes (requests pause for 90ms+ without any JVM GC pause).
- Solution: Avoid aggressive CPU limits on latency-sensitive Java applications or ensure thread pools are sized strictly to CPU quota.

---

## 3. Kubernetes Pod Lifecycle & Graceful Shutdown Sequence

When Kubernetes terminates a pod (e.g., during a rolling deployment):
1. **Endpoint Removal & SIGTERM happen IN PARALLEL**:
   - The kubelet sends `SIGTERM` to the container process (PID 1).
   - The EndpointSlice controller updates endpoints, and kube-proxy / ingress controllers update routing tables.
2. **The Race Condition**:
   - If Java stops listening immediately upon `SIGTERM`, clients in-flight from Ingress will receive `502 Bad Gateway` because iptables / Envoy takes 2-5 seconds to remove the dead pod from routing!
3. **The Production PreStop Hook & Graceful Shutdown**:
   ```yaml
   lifecycle:
     preStop:
       exec:
         command: ["/bin/sh", "-c", "sleep 15"]
   ```
   During the 15s sleep, Ingress removes the pod from endpoints while Java continues serving active connections. Then `SIGTERM` fires, and Spring Boot initiates graceful drain via `server.shutdown: graceful`.
