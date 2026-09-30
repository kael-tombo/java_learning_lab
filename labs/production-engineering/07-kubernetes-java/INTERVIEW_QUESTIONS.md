# INTERVIEW QUESTIONS: Java in Kubernetes & Containers
## Lab 07 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: What happens if a Java application container receives `SIGTERM` without a `preStop` hook during a Kubernetes rolling update?
**Answer**:
When a pod enters termination, the kubelet sends `SIGTERM` to the container while asynchronously removing the pod IP from EndpointSlices and load balancer routing. Because load balancer propagation takes 1–3 seconds, external traffic continues to arrive at the pod. If the Java process immediately shuts down upon receiving `SIGTERM`, clients attempting to connect receive TCP `RST` errors, manifesting as HTTP `502 Bad Gateway`. A `preStop` hook executing `sleep 15` ensures the pod remains accepting traffic during the routing withdrawal period before Java begins its shutdown sequence.

### Q2: Why does `Runtime.getRuntime().availableProcessors()` return an unexpected number in older Java versions inside Docker?
**Answer**:
Older JVMs (pre-8u191) queried `/proc/cpuinfo`, which reflects the host physical node's CPU core count (e.g. 64 or 128 cores), ignoring Docker's `--cpus=2` cgroup limit. This caused the JVM to initialize 64 GC threads, 64 JIT compiler threads, and 64 ForkJoinPool threads, causing catastrophic CPU context switching and thrashing inside a 2-core container limit. Modern JVMs with `-XX:+UseContainerSupport` read cgroup quotas to calculate the correct active processor count.

---

## Staff / Principal Level (8+ Years)

### Q3: How do you design Kubernetes Quality of Service (QoS) classes and CPU limits for ultra-low latency Java trading applications?
**Answer**:
- **QoS Class**: Guarantee **Guaranteed QoS** by setting `requests.cpu == limits.cpu` and `requests.memory == limits.memory` with static CPU management policy (`cpumanager=static`) to pin container threads to dedicated CPU cores, eliminating L1/L2 cache evictions and NUMA cross-node memory access.
- **CPU Limits Issue**: Setting CPU limits without CPU pinning engages Linux CFS throttling. If multiple threads spike simultaneously, they burn through the quota in the first few milliseconds of the 100ms window, resulting in artificial 80ms+ freezes. For latency-critical apps, omit CPU limits or pin to exclusive cores.
