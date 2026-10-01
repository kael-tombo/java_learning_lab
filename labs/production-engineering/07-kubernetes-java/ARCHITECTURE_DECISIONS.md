# ARCHITECTURE DECISIONS: Enterprise Kubernetes & Containerized Java Standards
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## ADR-01: Container Memory Sizing Standard & Non-Heap Headroom Protection

### Status: ACCEPTED

### Context
Production services frequently crashed with `Exit Code 137` (Linux cgroup OOM-Killer). In every incident, engineers had configured fixed heap sizes (`-Xmx4g`) identical to the container memory limit (`resources.limits.memory: 4Gi`). The JVM's non-heap memory (Metaspace, thread stacks, Code Cache, and Netty direct memory) breached the cgroup limit, causing immediate termination without an `OutOfMemoryError` or heap dump.

### Decision
1. **Mandatory Percentage-Based Sizing**:
   - Explicit `-Xmx` and `-Xms` flags are **strictly forbidden** in Kubernetes deployment manifests.
   - Sizing must use dynamic container awareness:
     ```bash
     -XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:InitialRAMPercentage=50.0
     ```
2. **Mandatory 25% Headroom Reservation**:
   - Exactly $25\%$ of the container memory limit is reserved for JVM non-heap structures and OS buffers.
3. **QoS Class Standard**:
   - To prevent memory overcommit and node evictions, `resources.requests.memory` must equal `resources.limits.memory` (Guaranteed QoS for memory).

### Consequences
- OOM-Killer crashes (Exit Code 137) due to non-heap expansion eliminated fleet-wide.
- Enables safe pod resizing by adjusting Helm values without modifying Java startup scripts.

---

## ADR-02: Zero-Downtime Deployment Standard (PreStop Sleep & Graceful Drain)

### Status: ACCEPTED

### Context
During every production rolling deployment, upstream API Gateways and ingress controllers logged hundreds of `502 Bad Gateway` and `Connection Refused` errors. Kubelet was sending `SIGTERM` to Java pods before Ingress controllers had fully removed the terminating pods from distributed routing tables.

### Decision
1. **Mandatory PreStop Sleep Hook**:
   - All production deployment manifests must define a `preStop` hook executing `sleep 15`:
     ```yaml
     lifecycle:
       preStop:
         exec:
           command: ["/bin/sh", "-c", "sleep 15"]
     ```
2. **Spring Boot Graceful Shutdown**:
   - All services must enable graceful shutdown in `application.yml`:
     ```yaml
     server:
       shutdown: graceful
     spring:
       lifecycle:
         timeout-per-shutdown-phase: 30s
     ```
3. **Termination Grace Period**:
   - `terminationGracePeriodSeconds` must be set to $\ge 60\text{ seconds}$ to provide adequate time for the 15s preStop sleep, in-flight request completion, and database pool termination.

### Consequences
- Zero `502 Bad Gateway` errors during rolling releases and node drains.
- Pod shutdown duration extends by 15 seconds — an acceptable trade-off for zero customer-facing drops.

---

## ADR-03: Startup, Liveness, and Readiness Probe Architecture Standard

### Status: ACCEPTED

### Context
A transient network disruption to PostgreSQL caused Spring Boot's aggregate `/actuator/health` liveness probe to fail across 60 pod replicas simultaneously. Kubernetes killed and restarted all 60 pods, creating a synchronized thundering herd of database connections on startup that crashed the database permanently.

### Decision
1. **Startup Probe Mandate for Slow-Starting Workloads**:
   - Workloads taking $> 10\text{s}$ to boot must configure a dedicated `startupProbe` to shield liveness probes from premature failure:
     ```yaml
     startupProbe:
       httpGet:
         path: /actuator/health/liveness
         port: 8080
       failureThreshold: 30
       periodSeconds: 2
     ```
2. **Liveness Probe Isolation**:
   - Liveness probes must query `/actuator/health/liveness` strictly.
   - Liveness probes **must never inspect external dependencies** (databases, queues, caches). They only verify that the JVM process itself is healthy and un-deadlocked.
3. **Readiness Probe for Dependency Traffic Gating**:
   - Readiness probes query `/actuator/health/readiness`.
   - If a database fails, readiness returns 503. Kubernetes removes the pod from endpoints **without restarting it**, preventing the restart death spiral.

### Consequences
- Transient dependency outages no longer cause mass pod restart cascades.
- Pods cleanly stop accepting traffic when dependencies are degraded and resume automatically upon recovery.

---

## ADR-04: CPU Limit Elimination & CFS Throttling Policy

### Status: ACCEPTED

### Context
Multi-threaded Java microservices experienced unexplained P99 latency spikes of $50 - 150\text{ms}$ during brief traffic bursts despite average node CPU utilization remaining below $40\%$. Investigation revealed Linux CFS quota throttling was freezing container execution whenever bursts exhausted the 100ms CFS quota.

### Decision
1. **Removal of CPU Limits**:
   - Production Java microservices **must not specify `resources.limits.cpu`** in Kubernetes manifests.
   - Resource scheduling and bin-packing guarantees are governed strictly by `resources.requests.cpu`.
2. **Exception Handling**:
   - If multi-tenant cluster policy mandates CPU limits, the limit must be configured with at least $4\times - 6\times$ burst headroom relative to the request.

### Consequences
- CFS quota throttling latency spikes reduced from $35\%$ of periods to $0\%$.
- P99 response times dropped by up to $70\%$ under bursty traffic patterns.

---

## ADR-05: Sub-Second Startup Strategy Selection: CRaC vs. GraalVM vs. AppCDS

### Status: ACCEPTED

### Context
Dynamic autoscaling in response to traffic spikes was hindered by 20–35 second JVM cold starts. Serverless and scale-from-zero workloads required sub-second cold starts.

### Decision Matrix & Selection Standard
The enterprise adopts a tiered strategy based on workload characteristics:

1. **Tier 1: High-Throughput Core Services $\rightarrow$ Standard OpenJDK 21 + AppCDS**:
   - Maximum sustained throughput, zero reflection restrictions, low operational complexity.
   - Startup time: $4 - 6\text{ seconds}$ (adequate for standard HPA).
2. **Tier 2: Scale-to-Zero & Event-Driven Workers $\rightarrow$ Project CRaC**:
   - Checkpoint-restore with CRIU delivers **$25 - 50\text{ms}$ cold start** while retaining full C2 JIT peak throughput.
   - Workloads must implement `org.crac.Resource` to coordinate connection lifecycle.
3. **Tier 3: CLI Tools & Small Serverless Functions $\rightarrow$ GraalVM Native Image**:
   - Ahead-of-Time compilation yields instant boot ($< 30\text{ms}$) and minimal base memory ($< 80\text{MB}$ RSS).
   - Only permitted for standalone services with static reflection reachability metadata.

### Consequences
- Standardized startup acceleration paths tailored to specific service SLAs.
- Eliminates brittle AOT workarounds on complex monolithic enterprise codebases.
