# PRODUCTION SCENARIOS: Kubernetes & Containerized Java War Stories
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## Scenario 1: The Black Friday Rolling Deployment 502 Cascade

### 1. Incident Context & Architecture
- **Event**: Black Friday e-commerce flash sale ($180,000/minute revenue).
- **Service**: `checkout-cart-service` (Spring Boot 3.x on AWS EKS).
- **Workload**: 25,000 requests/sec distributed across 40 pod replicas behind AWS ALB Ingress Controller.

### 2. The Disaster
At 00:05 UTC, a hotfix was rolled out via GitOps:
- As soon as the rolling update started, AWS ALB logged **over 4,200 HTTP 502 Bad Gateway responses**.
- Shoppers attempting to finalize purchases were kicked back to empty carts, resulting in over **$350,000 in lost revenue** within 90 seconds!
- The release was immediately rolled back, but the rollback itself caused another wave of 502 errors!

### 3. Root Cause Analysis
Traffic analysis revealed that terminating pods were receiving HTTP requests after the Java process had begun tearing down its network sockets:
1. **Asynchronous Routing Propagation Delay**:
   When Kubelet marked an old pod as `Terminating`, AWS ALB target group deregistration took **4.8 seconds** to propagate through AWS APIs and drain connections.
2. **Missing PreStop Hook**:
   The deployment manifest lacked a `preStop` hook. Kubelet sent `SIGTERM` to the container process at $T=0$.
3. **Immediate Server Socket Closure**:
   Spring Boot received `SIGTERM` and immediately closed its Tomcat listener socket (`server.port: 8080`).
4. **The Window of Failure**:
   For 4.8 seconds, ALB continued forwarding incoming customer checkout requests to a container with a closed TCP socket, resulting in immediate `TCP RST` and ALB `502 Bad Gateway` errors.

### 4. Production Remediation & Verification
```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: checkout-service
      lifecycle:
        preStop:
          exec:
            # 15s sleep delays SIGTERM until ALB deregistration completes
            command: ["/bin/sh", "-c", "sleep 15"]
```
```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```
*Verification*:
Under a synthetic load test of 30,000 requests/sec with `wrk`, a rolling deployment of 40 pods executed with **zero non-200 HTTP responses (100% zero-downtime)**.

---

## Scenario 2: The Database Failover Death Spiral (Coupled Liveness Probe Outage)

### 1. Incident Context & Architecture
- **Service**: `account-ledger-service` (60 replicas on GKE).
- **Database**: High-Availability Cloud SQL PostgreSQL instance.

### 2. The Disaster
At 03:15 UTC, Cloud SQL performed an automatic maintenance minor version failover (primary $\rightarrow$ standby replica, lasting ~12 seconds):
- Instead of resuming traffic after the 12-second failover, the **entire 60-pod microservice fleet entered a catastrophic CrashLoopBackOff death spiral**.
- Total outage duration: **48 minutes**!

### 3. Forensic Autopsy
Inspection of the deployment manifest revealed:
```yaml
livenessProbe:
  httpGet:
    path: /actuator/health  # Coupled to PostgreSQL via DataSourceHealthIndicator!
    port: 8080
  periodSeconds: 5
  failureThreshold: 2
```
**Timeline of the Collapse**:
- **T+00:00**: PostgreSQL begins failover; TCP connections drop for 10 seconds.
- **T+00:05**: Actuator `/actuator/health` returns `503 Service Unavailable` (`status: DOWN`).
- **T+00:10**: The liveness probe fails for the 2nd time on all 60 pods.
- **T+00:12**: PostgreSQL finishes failover and is healthy again.
- **T+00:13**: **Kubernetes kills all 60 Java pods simultaneously**!
- **T+00:20**: All 60 pods boot at the exact same moment. Every pod initializes Spring context and attempts to acquire 20 database connections (`HikariConfig.maximumPoolSize = 20` $\times$ 60 pods = **1,200 simultaneous connection requests**).
- **T+00:25**: PostgreSQL is overwhelmed by the thundering herd, maxing out `max_connections` and CPU.
- **T+00:30**: Startup probe times out; liveness probe fails again; Kubernetes kills all 60 pods again.
- The cycle repeated every 60 seconds indefinitely until engineers manually scaled the deployment to 0 replicas.

### 4. Production Remediation
1. Decoupled liveness from external dependencies using Spring Boot dedicated probes:
   ```yaml
   livenessProbe:
     httpGet:
       path: /actuator/health/liveness  # Inspects JVM process only
       port: 8080
   readinessProbe:
     httpGet:
       path: /actuator/health/readiness # Inspects DB; removes from LB without restarting pod!
       port: 8080
   ```
2. Added startup probe with 60-second window to protect boot phases.
3. *Outcome*: During subsequent database maintenance failovers, pods temporarily marked themselves not ready, held their processes stable, and resumed serving traffic immediately upon DB reconnection without a single container restart.

---

## Scenario 3: The Silent CFS Quota Throttling Latency Spike

### 1. Incident Context & Symptom
- **Service**: `search-query-service` (Java 21, Netty-based).
- **Symptom**: P99 latency jumped from 14ms to 110ms whenever query volume increased by just 15%.
- **Initial Misdiagnosis**: The team suspected GC pause spikes. However, GC logs showed P99 pause times were under **2.8ms**.

### 2. Deep Dive: Linux Kernel CFS Quotas
The engineering team checked the Linux cgroup metrics on the pod:
```bash
cat /sys/fs/cgroup/cpu.stat
# Output:
nr_periods 80000
nr_throttled 29600  (37% of periods throttled!)
throttled_usec 982000000
```
**Root Cause**:
- The pod manifest specified `resources.limits.cpu: "2000m"`.
- Netty ran 16 event loop worker threads.
- During a burst of search queries, all 16 threads processed requests concurrently.
- Each thread ran for only 13ms:
  $$16 \text{ threads} \times 13\text{ ms} = 208\text{ ms CPU time}$$
- The 200ms quota for the 100ms period was exhausted in the **first 13 milliseconds**!
- For the remaining **87 milliseconds**, the Linux kernel suspended all threads.
- The 87ms freeze occurred inside the kernel runqueue — invisible to the JVM and GC logs!

### 3. Production Remediation
Removed `limits.cpu` from the deployment manifest, leaving only `requests.cpu: "2000m"`.
*Outcome*: Throttling dropped to **0.0%**; P99 latency flattened to **8.9ms** across all traffic tiers.

---

## Scenario 4: The Exit Code 137 Netty Direct Memory Leak Outage

### 1. Incident Context
- **Service**: `realtime-push-gateway` (20 replicas handling 300,000 SSE/WebSocket connections).
- **Incident**: Every 4 to 6 hours, a pod was abruptly terminated by Kubernetes with `Exit Code 137`. Java heap utilization was only **1.2 GiB out of 4 GiB container limit**.

### 2. Forensic Investigation via Native Memory Tracking (NMT)
Launched pod with `-XX:NativeMemoryTracking=detail`:
```bash
jcmd 1 VM.native_memory detail.diff
```
*Diff Analysis*:
```text
-    Internal (reserved=2890MB +1420MB, committed=2890MB +1420MB)
              (malloc=2890MB +1420MB #42890 +18200)
```
The non-heap memory allocated via `malloc` (Netty off-heap direct byte buffers) was expanding by 150MB per hour!

### 3. Root Cause: Unreleased DirectByteBuf in Exception Handler
```java
public void channelRead(ChannelHandlerContext ctx, Object msg) {
    ByteBuf buffer = (ByteBuf) msg;
    try {
        validatePayload(buffer); // Throws IllegalArgumentException on malformed JSON!
        ctx.fireChannelRead(msg);
    } catch (IllegalArgumentException e) {
        // BUG: Logged exception but failed to release DirectByteBuf!
        // Off-heap memory allocated via jemalloc was permanently leaked!
        log.warn("Malformed payload dropped: {}", e.getMessage());
    }
}
```
Because `ReferenceCountUtil.release(msg)` was missed in the exception catch block, bad client payloads leaked off-heap direct memory until the Linux kernel terminated the container with `Exit Code 137`.

### 4. Production Remediation
1. Wrapped all Netty read handlers in strict `try-finally` blocks calling `ReferenceCountUtil.release(msg)`.
2. Sized container memory limit with a $25\%$ safety buffer and added `-XX:MaxDirectMemorySize=1g` to force an in-JVM `OutOfMemoryError` (which generates a stack trace) rather than an un-diagnosable kernel SIGKILL.
