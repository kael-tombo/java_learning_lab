# CODE DEEP DIVE: Cloud Cost Engineering & FinOps Production Patterns
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Kubernetes Topology-Aware Routing & Cost-Optimal Pod Sizing

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-processing-service
  namespace: production
  labels:
    app.kubernetes.io/name: order-processing-service
    finops.cost-center: "trade-execution-104"
spec:
  replicas: 12
  selector:
    matchLabels:
      app: order-processing-service
  template:
    metadata:
      labels:
        app: order-processing-service
    spec:
      # Spread pods evenly across Availability Zones to balance capacity
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: "topology.kubernetes.io/zone"
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: order-processing-service
      containers:
        - name: app
          image: registry.corp.internal/finops/order-service:2.4.0-arm64
          resources:
            # Sized strictly to 1:4 CPU-to-Memory ratio to match Graviton instances
            requests:
              cpu: "1000m"
              memory: "4Gi"
            limits:
              # Guaranteed QoS on memory to prevent node thrashing / OOM
              memory: "4Gi"
              # Intentionally omit CPU limit to prevent Linux CFS quota throttling latency spikes
          env:
            - name: JAVA_TOOL_OPTIONS
              value: >-
                -XX:+UseContainerSupport
                -XX:MaxRAMPercentage=75.0
                -XX:+UseZGC
                -XX:+ZGenerational
                -XX:+ZUncommit
                -XX:ZUncommitDelay=300
          ports:
            - containerPort: 8080
              name: http
---
apiVersion: v1
kind: Service
metadata:
  name: order-processing-service
  namespace: production
  annotations:
    # Restricts routing to endpoints in the same AZ, slashing cross-AZ egress bills by >85%
    service.kubernetes.io/topology-mode: Auto
spec:
  type: ClusterIP
  selector:
    app: order-processing-service
  ports:
    - name: http
      port: 8080
      targetPort: 8080
```

---

## Pattern 2: Cloud Cost-Optimized JVM Startup Wrapper Script

```bash
#!/usr/bin/env bash
# ==============================================================================
# Enterprise FinOps JVM Bootstrap Script for ARM64 Graviton / Container Runtimes
# ==============================================================================
set -euo pipefail

# 1. Detect Container Limits
TOTAL_MEM_MB=$(cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null || echo "0")
if [ "$TOTAL_MEM_MB" != "max" ] && [ "$TOTAL_MEM_MB" -gt 0 ]; then
  TOTAL_MEM_GB=$((TOTAL_MEM_MB / 1024 / 1024 / 1024))
  echo "[FinOps] Container memory constraint detected: ${TOTAL_MEM_GB} GiB"
fi

# 2. JVM Heap Allocation Strategy
# MaxRAMPercentage=75.0 reserves 25% of container RAM for Metaspace, CodeCache,
# Netty off-heap direct buffers, and OS thread stacks to prevent Linux OOM-killer.
FINOPS_JVM_FLAGS=(
  "-XX:+UseContainerSupport"
  "-XX:MaxRAMPercentage=75.0"
  "-XX:InitialRAMPercentage=25.0" # Start lean, expand elastically on demand
)

# 3. Dynamic Heap Uncommit (Generational ZGC)
# Returns idle physical memory pages back to the Linux kernel via madvise(MADV_DONTNEED)
FINOPS_JVM_FLAGS+=(
  "-XX:+UseZGC"
  "-XX:+ZGenerational"
  "-XX:+ZUncommit"
  "-XX:ZUncommitDelay=300" # 5 minutes of idle uncommits memory to OS
)

# 4. Enforce Compressed OOPs Boundary
# Prevents switching to expensive 64-bit pointers (which doubles pointer overhead)
FINOPS_JVM_FLAGS+=(
  "-XX:+UseCompressedOops"
  "-XX:+UseCompressedClassPointers"
)

# 5. String Deduplication to save 10-15% heap space on repetitive JSON payloads
FINOPS_JVM_FLAGS+=(
  "-XX:+UseStringDeduplication"
)

# 6. Execute Application
echo "[FinOps] Launching JVM with optimized flags: ${FINOPS_JVM_FLAGS[*]}"
exec java "${FINOPS_JVM_FLAGS[@]}" -jar /app/application.jar "$@"
```

---

## Pattern 3: Spot Interruption Daemon & Java Graceful Drain Hook

```java
package com.learning.production.lab16;

import com.sun.net.httpserver.HttpServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Spot Instance Interruption Watcher.
 * 
 * Periodically polls AWS EC2 Instance Metadata Service (IMDSv2) for the 2-minute
 * Spot Interruption Notice. When detected, triggers a deterministic graceful
 * shutdown sequence before the cloud hypervisor forcefully terminates the node.
 */
public class SpotInterruptionWatcher implements AutoCloseable {

    private static final Logger log = LoggerFactory.getLogger(SpotInterruptionWatcher.class);
    private static final String IMDS_TOKEN_URL = "http://169.254.169.254/latest/api/token";
    private static final String IMDS_SPOT_NOTICE_URL = "http://169.254.169.254/latest/meta-data/spot/instance-action";

    private final HttpClient httpClient;
    private final ScheduledExecutorService scheduler;
    private final Runnable gracefulDrainTask;
    private final AtomicBoolean interruptionTriggered = new AtomicBoolean(false);
    private volatile String imdsToken = null;

    public SpotInterruptionWatcher(Runnable gracefulDrainTask) {
        this.gracefulDrainTask = gracefulDrainTask;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(500))
                .build();
        this.scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "spot-interruption-watcher");
            t.setDaemon(true);
            return t;
        });
    }

    public void start() {
        refreshImdsToken();
        // Poll every 5 seconds for Spot Interruption Notice
        scheduler.scheduleWithFixedDelay(this::checkForInterruption, 5, 5, TimeUnit.SECONDS);
        log.info("[FinOps] Spot Interruption Watcher started successfully.");
    }

    private void refreshImdsToken() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(IMDS_TOKEN_URL))
                    .header("X-aws-ec2-metadata-token-ttl-seconds", "21600")
                    .PUT(HttpRequest.BodyPublishers.noBody())
                    .timeout(Duration.ofMillis(800))
                    .build();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                this.imdsToken = response.body();
            }
        } catch (Exception e) {
            log.debug("IMDSv2 token fetch failed (not running on AWS EC2 or local test): {}", e.getMessage());
        }
    }

    private void checkForInterruption() {
        if (interruptionTriggered.get() || imdsToken == null) {
            return;
        }
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(IMDS_SPOT_NOTICE_URL))
                    .header("X-aws-ec2-metadata-token", imdsToken)
                    .GET()
                    .timeout(Duration.ofMillis(800))
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() == 200) {
                // 200 OK means AWS has scheduled this Spot instance for termination!
                if (interruptionTriggered.compareAndSet(false, true)) {
                    log.warn("🚨 [FinOps] SPOT INTERRUPTION NOTICE DETECTED! Body: {}", response.body());
                    triggerDrainSequence();
                }
            } else if (response.statusCode() == 401) {
                refreshImdsToken();
            }
        } catch (Exception ignored) {
            // 404 Not Found is normal (no pending interruption)
        }
    }

    private void triggerDrainSequence() {
        CompletableFuture.runAsync(() -> {
            log.info("Executing 60-second graceful application drain sequence...");
            try {
                gracefulDrainTask.run();
                log.info("Graceful drain completed cleanly ahead of Spot deadline.");
            } catch (Exception e) {
                log.error("Error during graceful drain: ", e);
            }
        });
    }

    @Override
    public void close() {
        scheduler.shutdownNow();
    }
}
```

---

## Pattern 4: High-Throughput Wire Compression for Kafka & gRPC

```java
package com.learning.production.lab16;

import io.grpc.ClientInterceptor;
import io.grpc.CallOptions;
import io.grpc.Channel;
import io.grpc.ClientCall;
import io.grpc.MethodDescriptor;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;

/**
 * Enterprise Wire Compression Standards.
 * Slashes network egress charges by 65-80% across Availability Zones and Regions.
 */
public class FinOpsWireCompression {

    /**
     * Kafka Producer Configuration Standard:
     * - Uses LZ4: high-throughput, near-zero CPU compression.
     * - Batch size & linger.ms: amortizes compression block headers.
     */
    public static Properties createCostOptimizedKafkaConfig(String bootstrapServers) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // Mandatory FinOps Compression Flags:
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");       // 65-70% payload size reduction
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);            // 64 KB batches for optimal compression ratio
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10);                // 10ms wait to accumulate dense compression blocks
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

        return props;
    }

    /**
     * gRPC Client Interceptor: Enforces Gzip or Snappy frame compression on all outbound RPC calls.
     */
    public static ClientInterceptor createCompressedGrpcInterceptor() {
        return new ClientInterceptor() {
            @Override
            public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
                    MethodDescriptor<ReqT, RespT> method,
                    CallOptions callOptions,
                    Channel next) {
                // Request Gzip compression from client to server
                return next.newCall(method, callOptions.withCompression("gzip"));
            }
        };
    }
}
```

---

## Pattern 5: JVM Memory Rightsizing Prometheus Collector for FinOps Auditing

```java
package com.learning.production.lab16;

import io.prometheus.client.Gauge;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;

/**
 * Exposes real-time JVM memory metrics to Prometheus / Kubecost
 * to identify stranded capacity and recommend pod rightsizing.
 */
public class FinOpsMemoryMetricsExporter {

    private static final Gauge HEAP_COMMITTED_BYTES = Gauge.build()
            .name("finops_jvm_heap_committed_bytes")
            .help("JVM heap physical bytes committed to OS")
            .register();

    private static final Gauge HEAP_USED_BYTES = Gauge.build()
            .name("finops_jvm_heap_used_bytes")
            .help("Actual live data size in JVM heap")
            .register();

    private static final Gauge HEAP_WASTED_HEADROOM_RATIO = Gauge.build()
            .name("finops_jvm_heap_waste_ratio")
            .help("Ratio of committed but unused memory: (committed - used) / committed")
            .register();

    private final MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();

    public void scrape() {
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        long committed = heapUsage.getCommitted();
        long used = heapUsage.getUsed();

        HEAP_COMMITTED_BYTES.set(committed);
        HEAP_USED_BYTES.set(used);

        if (committed > 0) {
            double wasteRatio = (double) (committed - used) / (double) committed;
            HEAP_WASTED_HEADROOM_RATIO.set(wasteRatio);
        }
    }
}
```
