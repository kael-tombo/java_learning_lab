# CHECKLIST: Kubernetes & Containerized Java Production Readiness
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Container Memory & JVM Sizing Standards

- [ ] **Percentage-Based Sizing**:
  - [ ] Explicit `-Xmx` / `-Xms` flags eliminated from all Kubernetes deployment manifests.
  - [ ] Heap configured via dynamic container awareness: `-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0`.
  - [ ] At least $25\%$ of container memory limit reserved for non-heap allocations (Metaspace, thread stacks, Code Cache, Netty direct memory).
- [ ] **QoS Class & Node Protection**:
  - [ ] `resources.requests.memory` configured exactly equal to `resources.limits.memory` (Guaranteed QoS) to prevent node memory overcommit and evictions.
  - [ ] JVM failure flags configured to handle unrecoverable heap exhaustion immediately:
    ```bash
    -XX:+ExitOnOutOfMemoryError
    -XX:+HeapDumpOnOutOfMemoryError
    -XX:HeapDumpPath=/dumps/heapdump.hprof
    ```
- [ ] **Off-Heap Direct Memory Cap**:
  - [ ] Netty / gRPC direct memory capped explicitly (`-XX:MaxDirectMemorySize=1g`) to force JVM-level stack traces before the Linux kernel triggers a silent `Exit Code 137` SIGKILL.

---

## 2. Pod Lifecycle & Zero-Downtime Deployment Standards

- [ ] **PreStop Sleep Delay**:
  - [ ] Deployment defines a `lifecycle.preStop` hook executing `sleep 15` to allow distributed Ingress and kube-proxy routing tables to remove the pod before shutdown begins.
  - [ ] `terminationGracePeriodSeconds` set to $\ge 60\text{ seconds}$ to accommodate the 15s sleep, in-flight request completion, and database pool termination.
- [ ] **Graceful Application Drain**:
  - [ ] Spring Boot configured with `server.shutdown: graceful` and `spring.lifecycle.timeout-per-shutdown-phase: 30s`.
  - [ ] Kafka consumer loops catch `SIGTERM` and call `consumer.wakeup()` followed by atomic offset commits.
  - [ ] HikariCP database connection pool configured to soft-evict active connections during context closure.
- [ ] **Rolling Update Strategy**:
  - [ ] Deployment specifies `maxUnavailable: 0` and `maxSurge: 25%` to guarantee zero reduction in active serving capacity during rolling upgrades.
  - [ ] `PodDisruptionBudget` (PDB) deployed with `minAvailable: 75%` to protect against node drains and maintenance evictions.

---

## 3. Health Checks & Probe Architecture

- [ ] **Dedicated Probe Endpoints**:
  - [ ] Spring Boot actuator configured with `management.endpoint.health.probes.enabled: true`.
  - [ ] `livenessProbe` points strictly to `/actuator/health/liveness` (inspects internal JVM state ONLY; never checks databases or caches).
  - [ ] `readinessProbe` points to `/actuator/health/readiness` (inspects external dependencies; removes from load balancers on failure without restarting the container).
- [ ] **Startup Probe Protection**:
  - [ ] Applications taking $> 10\text{s}$ to boot configure a dedicated `startupProbe` with generous threshold (`failureThreshold: 30`, `periodSeconds: 2`) to prevent premature liveness kills during JIT warmup.

---

## 4. CPU Scheduling & CFS Quota Throttling

- [ ] **CPU Limit Policy**:
  - [ ] Strict `resources.limits.cpu` omitted from latency-sensitive production deployments, or configured with $\ge 4\times$ burst headroom relative to requests.
  - [ ] Scheduling reservations guaranteed via `resources.requests.cpu`.
  - [ ] Verified `nr_throttled / nr_periods < 1%` in `/sys/fs/cgroup/cpu.stat` under peak traffic load.
- [ ] **Thread Pool Sizing**:
  - [ ] Worker thread pools (Tomcat, Netty, ForkJoinPool) sized to match container CPU requests, or migrated to Java 21 Virtual Threads (Project Loom) for high-concurrency I/O workloads.

---

## 5. Networking & DNS Resolution Hygiene

- [ ] **CoreDNS Protection & Search Path**:
  - [ ] External HTTP/gRPC endpoints use Fully Qualified Domain Names with a trailing dot (`api.stripe.com.`).
  - [ ] Pod spec configures `dnsConfig.options` with `ndots: 2` for high-throughput egress workloads.
- [ ] **JVM DNS Cache Expiration**:
  - [ ] Explicit DNS cache TTL configured at startup to handle dynamic cloud endpoint shifts:
    ```bash
    -Dnetworkaddress.cache.ttl=5
    -Dnetworkaddress.cache.negative.ttl=2
    ```
- [ ] **Zone Topology Distribution**:
  - [ ] Pods evenly distributed across Availability Zones using `topologySpreadConstraints` with `maxSkew: 1`.
  - [ ] Services annotated with `service.kubernetes.io/topology-mode: Auto` to eliminate cross-AZ egress charges.
