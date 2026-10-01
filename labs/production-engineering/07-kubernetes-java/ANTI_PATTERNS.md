# ANTI-PATTERNS: Kubernetes & Containerized Java Engineering
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## Anti-Pattern 1: Setting `-Xmx` Equal to the Container Memory Limit (Exit Code 137)

### The Mistake
```yaml
resources:
  limits:
    memory: "4Gi"
env:
  - name: JAVA_OPTS
    value: "-Xms4g -Xmx4g"  # Setting max heap equal to container RAM limit!
```

### Why It Fails
The JVM memory footprint is substantially larger than the Java heap alone:
$$\text{Total JVM Memory (RSS)} = \text{Heap } (-Xmx) + \text{Metaspace} + \text{Code Cache} + \text{Thread Stacks} + \text{Direct Memory} + \text{JVM Internal}$$

- **Heap**: 4,096 MB
- **Metaspace**: ~256 MB (loaded classes, method metadata)
- **Code Cache**: ~240 MB (JIT C1/C2 compiled native machine code)
- **Thread Stacks**: 300 platform threads $\times 1\text{ MB} = 300\text{ MB}$
- **Netty Direct Buffers**: ~512 MB (off-heap direct byte buffers)
- **GC Overhead & Native Structures**: ~200 MB

**The Crash**:
As soon as the JVM's actual resident set size reaches **4,097 MB**:
1. The Linux cgroup memory subsystem notices the container has breached `memory.max` (cgroups v2) or `memory.limit_in_bytes` (cgroups v1).
2. The Linux kernel invokes the **Out-Of-Memory Killer (`oom-killer`)**.
3. The kernel sends `SIGKILL` (signal 9) directly to PID 1.
4. The container terminates instantly with **`Exit Code 137`** ($128 + 9$).
5. No Java thread dump is generated, no `OutOfMemoryError` is thrown, and no log message appears in `catalina.out` or standard error!

### The Correct Production Fix
Use percentage-based container memory sizing with a **$25\%$ non-heap safety margin**:
```yaml
resources:
  requests:
    memory: "4Gi"
  limits:
    memory: "4Gi"
env:
  - name: JAVA_TOOL_OPTIONS
    value: "-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
```
Under a 4 GiB container limit, the JVM automatically allocates a 3 GiB heap, safely preserving 1 GiB for Metaspace, Code Cache, thread stacks, and off-heap direct buffers.

---

## Anti-Pattern 2: Missing PreStop Hook & Immediate SIGTERM Shutdown (502 Bad Gateway Cascades)

### The Mistake
Terminating the Spring Boot application immediately upon receiving `SIGTERM` without a PreStop sleep delay.

### Why It Fails
In Kubernetes, pod shutdown involves two concurrent asynchronous workflows:
1. **Control Plane Path**: Kubelet marks the pod as `Terminating` $\rightarrow$ EndpointSlice controller updates endpoints $\rightarrow$ `kube-proxy` rewrites iptables/IPVS rules across all worker nodes $\rightarrow$ Ingress/Envoy updates upstream router tables. **This takes 2 to 8 seconds across a production cluster.**
2. **Local Node Path**: Kubelet sends `SIGTERM` to the container process.

If the Java application intercepts `SIGTERM` and immediately stops accepting connections:
- For the next 2 to 8 seconds, Ingress controllers and upstream microservices **still believe the pod is healthy and ready**.
- Active incoming HTTP requests are routed to the container's terminated port.
- Upstream callers receive **`502 Bad Gateway`** or **`Connection Refused`** errors!
- Every rolling release produces a burst of client-facing errors.

### The Correct Production Fix
Implement a **15-second PreStop sleep** combined with Spring Boot's graceful shutdown:
```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: service
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 15"]
```
```yaml
# application.yml:
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```
During the 15-second sleep, Ingress safely removes the pod from active endpoints while Java continues serving requests. When `SIGTERM` finally arrives, all remaining in-flight requests complete cleanly before termination.

---

## Anti-Pattern 3: Coupling Liveness Probes to External Dependencies (The Death Spiral)

### The Mistake
```yaml
livenessProbe:
  httpGet:
    path: /actuator/health  # Returns DOWN if PostgreSQL or Redis is unreachable!
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Why It Fails
Spring Boot's aggregate `/actuator/health` endpoint checks the health of **all registered dependencies** (Database, Redis, Kafka, RabbitMQ).

**The Cascading Collapse**:
1. PostgreSQL experiences a temporary network hiccup or connection pool saturation.
2. The `/actuator/health` endpoint on all 50 replicas returns `503 Service Unavailable` (`status: DOWN`).
3. Kubernetes evaluates the **liveness probe** failure.
4. Kubernetes immediately **kills and restarts all 50 Java pods simultaneously**!
5. 50 pods reboot at the exact same moment:
   - JIT cache is gone; cold-start CPU spikes to 100%.
   - Every pod bombards the already-struggling database with connection requests during startup!
6. The database crashes completely, locking the entire cluster into an unrecoverable **CrashLoopBackOff death spiral**.

### The Correct Production Fix
Decouple **Liveness** from **Readiness** using Spring Boot 2.3+ / 3.x dedicated probes:
- **Liveness Probe**: Checks ONLY if the JVM internal process is alive and not deadlocked:
  ```yaml
  livenessProbe:
    httpGet:
      path: /actuator/health/liveness  # Checks internal application state only
      port: 8080
    periodSeconds: 10
    failureThreshold: 3
  ```
- **Readiness Probe**: Checks if the pod is ready to accept user traffic:
  ```yaml
  readinessProbe:
    httpGet:
      path: /actuator/health/readiness # Fails if DB is down, removing pod from LB WITHOUT restarting it!
      port: 8080
    periodSeconds: 5
  ```

---

## Anti-Pattern 4: Setting Strict CPU Limits (The CFS Quota Throttling Latency Spike)

### The Mistake
```yaml
resources:
  requests:
    cpu: "2000m"
  limits:
    cpu: "2000m"  # Strict 2-core CPU limit
```

### Why It Fails
- A limit of `2000m` sets `cpu.cfs_quota_us = 200000` per 100ms period.
- Java is inherently multi-threaded. A sudden burst of requests causes 16 worker threads to process tasks concurrently.
- If each thread executes for only 13ms:
  $$16 \text{ threads} \times 13\text{ ms} = 208\text{ ms of CPU time}$$
- The 200ms quota is exhausted in the **first 13ms** of the 100ms window!
- The Linux kernel freezes all threads in the container for the remaining **87ms**.
- Client requests stall, P99 latency breaches 100ms, and engineers mistakenly assume the service is CPU-bound.

### The Correct Production Fix
Omit `limits.cpu` on latency-sensitive Java workloads, or set it $4\times - 6\times$ higher than requests:
```yaml
resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    memory: "4Gi"  # Enforce hard memory limit to protect node
    # No CPU limit: allow pod to burst into idle node cycles
```

---

## Anti-Pattern 5: The `ndots:5` CoreDNS Explosion

### The Mistake
Making frequent external HTTP API calls (e.g. `https://api.stripe.com/v1/charges`) inside a Kubernetes pod with default `/etc/resolv.conf`.

### Why It Fails
Because `api.stripe.com` contains only 2 dots, which is less than the default `ndots:5` setting, the Linux resolver attempts every search domain in `/etc/resolv.conf` before querying the FQDN:
1. `api.stripe.com.production.svc.cluster.local` $\rightarrow$ CoreDNS NXDOMAIN
2. `api.stripe.com.svc.cluster.local` $\rightarrow$ CoreDNS NXDOMAIN
3. `api.stripe.com.cluster.local` $\rightarrow$ CoreDNS NXDOMAIN
4. `api.stripe.com.ec2.internal` $\rightarrow$ CoreDNS NXDOMAIN
5. `api.stripe.com.` $\rightarrow$ SUCCESS

Under 5,000 requests/sec, this generates **25,000 UDP DNS queries per second** to CoreDNS. CoreDNS runs out of CPU, drops UDP packets, and triggers client-side 5-second DNS lookup timeouts!

### The Correct Production Fix
1. Append a trailing dot to external domain names to indicate an absolute FQDN: `https://api.stripe.com./v1/charges`.
2. Or configure `dnsConfig` in the pod spec:
   ```yaml
   spec:
     dnsConfig:
       options:
         - name: ndots
           value: "2"
   ```

---

## Anti-Pattern 6: Stale JVM DNS Cache (`networkaddress.cache.ttl=infinity`)

### The Mistake
Relying on default JVM DNS caching behavior when communicating with internal or external services.

### Why It Fails
- Historically, if a security manager was active, OpenJDK cached DNS lookups **forever** (`ttl = -1`). In modern OpenJDK without a security manager, the default is 30 seconds.
- In dynamic cloud and Kubernetes environments:
  - Load balancers, RDS Aurora failovers, and Service IPs shift dynamically.
  - If a database instance fails over and changes IP, a JVM caching DNS indefinitely continues attempting to connect to the dead IP address forever until the pod is restarted!

### The Correct Production Fix
Explicitly configure JVM network address cache TTL at startup:
```bash
-Dnetworkaddress.cache.ttl=5
-Dnetworkaddress.cache.negative.ttl=2
```
Or configure in `$JAVA_HOME/conf/security/java.security`:
```properties
networkaddress.cache.ttl=5
networkaddress.cache.negative.ttl=2
```
This guarantees the JVM picks up endpoint shifts within 5 seconds without flooding CoreDNS.
