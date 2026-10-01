# CODE DEEP DIVE: Kubernetes & Containerized Java Patterns
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Complete Zero-Downtime Kubernetes Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-orchestrator
  namespace: production
  labels:
    app.kubernetes.io/name: payment-orchestrator
    app.kubernetes.io/part-of: payment-platform
spec:
  replicas: 6
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0  # Guarantees zero capacity loss during rolling update
  selector:
    matchLabels:
      app: payment-orchestrator
  template:
    metadata:
      labels:
        app: payment-orchestrator
    spec:
      terminationGracePeriodSeconds: 60  # Allows 15s preStop + 30s Spring drain
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: "topology.kubernetes.io/zone"
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: payment-orchestrator
      containers:
        - name: app
          image: registry.corp.internal/payments/orchestrator:3.2.0
          imagePullPolicy: IfNotPresent
          resources:
            requests:
              cpu: "2000m"
              memory: "4Gi"
            limits:
              # Strict memory limit to guarantee node QoS
              memory: "4Gi"
              # Omit cpu limits to eliminate Linux CFS quota throttling latency spikes
          env:
            - name: JAVA_TOOL_OPTIONS
              value: >-
                -XX:+UseContainerSupport
                -XX:MaxRAMPercentage=75.0
                -XX:InitialRAMPercentage=50.0
                -XX:+UseG1GC
                -XX:MaxGCPauseMillis=150
                -Dnetworkaddress.cache.ttl=5
                -Dnetworkaddress.cache.negative.ttl=2
          ports:
            - containerPort: 8080
              name: http
          lifecycle:
            preStop:
              exec:
                # 15s sleep allows Ingress & kube-proxy routing tables to remove pod before SIGTERM
                command: ["/bin/sh", "-c", "sleep 15"]
          startupProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            failureThreshold: 30
            periodSeconds: 2
            timeoutSeconds: 2
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 2
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-orchestrator-pdb
  namespace: production
spec:
  minAvailable: 75%
  selector:
    matchLabels:
      app: payment-orchestrator
```

---

## Pattern 2: Spring Boot 3.x Graceful Drain & Probe Configuration

```yaml
# src/main/resources/application.yml
server:
  port: 8080
  shutdown: graceful # Enables graceful connection draining upon SIGTERM

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s # Time allocated to finish active in-flight requests

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      probes:
        enabled: true # Automatically configures /liveness and /readiness
      show-details: when_authorized
      group:
        liveness:
          include: livenessState # Checks JVM internal state ONLY (never inspects DB!)
        readiness:
          include: readinessState,db,redis # Checks DB; fails readiness if down without restarting pod
```

### Custom Readiness State Coordinator (Handling In-Flight Work)
```java
package com.learning.production.lab07;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.availability.AvailabilityChangeEvent;
import org.springframework.boot.availability.ReadinessState;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import jakarta.annotation.PreDestroy;

/**
 * Coordinates internal state transitions during pod shutdown.
 */
@Component
public class PodLifecycleCoordinator {

    private static final Logger log = LoggerFactory.getLogger(PodLifecycleCoordinator.class);
    private final ApplicationEventPublisher eventPublisher;

    public PodLifecycleCoordinator(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    @PreDestroy
    public void onShutdown() {
        log.info("🚨 SIGTERM received! Transitioning ReadinessState to REFUSING_TRAFFIC...");
        // Explicitly set readiness to REFUSING_TRAFFIC:
        AvailabilityChangeEvent.publish(eventPublisher, this, ReadinessState.REFUSING_TRAFFIC);
        log.info("Readiness set to REFUSING_TRAFFIC. Spring Boot graceful drain underway.");
    }

    @EventListener
    public void onReadinessChange(AvailabilityChangeEvent<ReadinessState> event) {
        log.info("Application Readiness state changed to: {}", event.getState());
    }
}
```

---

## Pattern 3: Project CRaC Lifecycle Coordinator for HikariCP & Netty

```java
package com.learning.production.lab07;

import com.zaxxer.hikari.HikariDataSource;
import org.crac.Context;
import org.crac.Core;
import org.crac.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

/**
 * Coordinates Project CRaC Checkpoint/Restore lifecycle.
 *
 * Sockets, open files, and database connection pools MUST be cleanly closed
 * prior to taking the checkpoint image, and re-initialized upon restore!
 */
@Component
public class CracDatabaseLifecycleResource implements Resource {

    private static final Logger log = LoggerFactory.getLogger(CracDatabaseLifecycleResource.class);
    private final HikariDataSource dataSource;

    public CracDatabaseLifecycleResource(HikariDataSource dataSource) {
        this.dataSource = dataSource;
    }

    @PostConstruct
    public void init() {
        // Register this resource with CRaC Global Context
        Core.getGlobalContext().register(this);
        log.info("[CRaC] Registered HikariCP lifecycle resource with CRaC global context.");
    }

    @Override
    public void beforeCheckpoint(Context<? extends Resource> context) throws Exception {
        log.info("📸 [CRaC] Pre-checkpoint triggered: Closing active HikariCP database connections...");
        // Suspend the connection pool and close physical TCP sockets to PostgreSQL
        dataSource.getHikariPoolMXBean().suspendPool();
        dataSource.getHikariPoolMXBean().softEvictConnections();
        log.info("📸 [CRaC] Database connections evicted cleanly. Ready for memory checkpoint snapshot.");
    }

    @Override
    public void afterRestore(Context<? extends Resource> context) throws Exception {
        log.info("🚀 [CRaC] Post-restore triggered: Resuming HikariCP connection pool...");
        // Re-open connections after instantaneous memory image restore
        dataSource.getHikariPoolMXBean().resumePool();
        log.info("🚀 [CRaC] Database connection pool restored. Ready to serve in 25ms!");
    }
}
```

---

## Pattern 4: Enterprise Container JVM Bootstrap Wrapper Script

```bash
#!/usr/bin/env bash
# ==============================================================================
# Production JVM Container Bootstrap Wrapper Script
# Supports: Linux cgroups v1 & v2, dynamic core scaling, and non-heap safety
# ==============================================================================
set -euo pipefail

# 1. Detect Cgroups Version
if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
  CGROUP_VERSION="v2"
  MEM_LIMIT_RAW=$(cat /sys/fs/cgroup/memory.max)
  CPU_MAX_RAW=$(cat /sys/fs/cgroup/cpu.max)
else
  CGROUP_VERSION="v1"
  MEM_LIMIT_RAW=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
  CPU_MAX_RAW=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us 2>/dev/null || echo "-1")
fi

echo "[Bootstrap] Detected Linux Cgroups: ${CGROUP_VERSION}"

# 2. Compute Container Sizing Parameters
JVM_OPTS=(
  "-XX:+UseContainerSupport"
  "-XX:MaxRAMPercentage=75.0"
  "-XX:InitialRAMPercentage=50.0"
  "-XX:+ExitOnOutOfMemoryError"        # Fail fast so Kubelet immediately restarts the dead pod
  "-XX:+HeapDumpOnOutOfMemoryError"
  "-XX:HeapDumpPath=/dumps/heapdump.hprof"
)

# 3. DNS Caching Protection in Kubernetes
JVM_OPTS+=(
  "-Dnetworkaddress.cache.ttl=5"
  "-Dnetworkaddress.cache.negative.ttl=2"
)

# 4. Garbage Collector Selection Based on Detected Memory
if [ "$MEM_LIMIT_RAW" != "max" ] && [ "$MEM_LIMIT_RAW" -gt 0 ]; then
  MEM_LIMIT_MB=$((MEM_LIMIT_RAW / 1024 / 1024))
  echo "[Bootstrap] Container RAM limit: ${MEM_LIMIT_MB} MB"
  
  if [ "$MEM_LIMIT_MB" -le 2048 ]; then
    echo "[Bootstrap] Sizing for small container: Using SerialGC"
    JVM_OPTS+=("-XX:+UseSerialGC")
  elif [ "$MEM_LIMIT_MB" -gt 8192 ]; then
    echo "[Bootstrap] Sizing for large container: Using Generational ZGC"
    JVM_OPTS+=("-XX:+UseZGC" "-XX:+ZGenerational" "-XX:+ZUncommit")
  else
    echo "[Bootstrap] Sizing for standard container: Using G1GC"
    JVM_OPTS+=("-XX:+UseG1GC" "-XX:MaxGCPauseMillis=150")
  fi
fi

# 5. Handover Execution to Java Application as PID 1
echo "[Bootstrap] Executing application with options: ${JVM_OPTS[*]}"
exec java "${JVM_OPTS[@]}" -jar /app/app.jar "$@"
```

---

## Pattern 5: Prometheus CFS Throttling Exporter for Kubernetes Alerts

```java
package com.learning.production.lab07;

import io.prometheus.client.Counter;
import io.prometheus.client.Gauge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/**
 * Scrapes Linux cgroup cpu.stat to expose real-time CFS throttling metrics to Prometheus.
 */
public class CgroupThrottlingCollector {

    private static final Logger log = LoggerFactory.getLogger(CgroupThrottlingCollector.class);

    private static final Gauge CFS_THROTTLED_PERIODS_RATIO = Gauge.build()
            .name("jvm_cfs_throttled_periods_ratio")
            .help("Ratio of throttled CFS scheduling periods to total periods")
            .register();

    private static final Counter CFS_THROTTLED_TIME_SECONDS = Counter.build()
            .name("jvm_cfs_throttled_time_seconds_total")
            .help("Total time container threads spent frozen by Linux CFS scheduler")
            .register();

    private final Path cgroupStatPath;

    public CgroupThrottlingCollector() {
        Path v2Path = Path.of("/sys/fs/cgroup/cpu.stat");
        Path v1Path = Path.of("/sys/fs/cgroup/cpu/cpu.stat");
        this.cgroupStatPath = Files.exists(v2Path) ? v2Path : v1Path;
    }

    public void scrape() {
        if (!Files.exists(cgroupStatPath)) return;
        try {
            List<String> lines = Files.readAllLines(cgroupStatPath);
            long nrPeriods = 0, nrThrottled = 0, throttledUsec = 0;
            for (String line : lines) {
                String[] parts = line.split("\\s+");
                if (parts.length == 2) {
                    switch (parts[0]) {
                        case "nr_periods" -> nrPeriods = Long.parseLong(parts[1]);
                        case "nr_throttled" -> nrThrottled = Long.parseLong(parts[1]);
                        case "throttled_usec" -> throttledUsec = Long.parseLong(parts[1]);
                    }
                }
            }
            if (nrPeriods > 0) {
                double ratio = (double) nrThrottled / (double) nrPeriods;
                CFS_THROTTLED_PERIODS_RATIO.set(ratio);
            }
            CFS_THROTTLED_TIME_SECONDS.inc(throttledUsec / 1_000_000.0);
        } catch (IOException e) {
            log.debug("Failed to read cgroup cpu.stat: {}", e.getMessage());
        }
    }
}
```
