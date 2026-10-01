# CODE DEEP DIVE: Incident Response, Forensics & Automation Patterns
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Automated Production Forensic Snapshot Bundle Collector

```bash
#!/usr/bin/env bash
# ==============================================================================
# Enterprise Incident Forensic Snapshot Collector
# Collects comprehensive OS, JVM, and Kubernetes telemetry in < 45 seconds
# ==============================================================================
set -euo pipefail

INCIDENT_ID=${1:-"inc-$(date +%Y%m%d-%H%M%S)"}
OUTPUT_DIR="/tmp/forensics-${INCIDENT_ID}"
mkdir -p "${OUTPUT_DIR}"

echo "======================================================================"
echo "[Forensics] Capturing diagnostic snapshot for Incident: ${INCIDENT_ID}"
echo "======================================================================"

# 1. OS & Linux Kernel Metrics
echo "[*] Capturing OS hardware counters and cgroup state..."
top -b -n 1 > "${OUTPUT_DIR}/top.txt" 2>&1 || true
vmstat 1 5 > "${OUTPUT_DIR}/vmstat.txt" 2>&1 || true
iostat -xz 1 3 > "${OUTPUT_DIR}/iostat.txt" 2>&1 || true
netstat -s > "${OUTPUT_DIR}/netstat.txt" 2>&1 || true
ss -s > "${OUTPUT_DIR}/socket_summary.txt" 2>&1 || true

# Capture cgroup throttling statistics
if [ -f /sys/fs/cgroup/cpu.stat ]; then
    cat /sys/fs/cgroup/cpu.stat > "${OUTPUT_DIR}/cgroup_v2_cpu_stat.txt"
    cat /sys/fs/cgroup/memory.current > "${OUTPUT_DIR}/cgroup_v2_memory_current.txt" 2>&1 || true
elif [ -f /sys/fs/cgroup/cpu/cpu.stat ]; then
    cat /sys/fs/cgroup/cpu/cpu.stat > "${OUTPUT_DIR}/cgroup_v1_cpu_stat.txt"
    cat /sys/fs/cgroup/memory/memory.usage_in_bytes > "${OUTPUT_DIR}/cgroup_v1_memory_usage.txt" 2>&1 || true
fi

# 2. JVM Diagnostics (Non-Invasive)
JAVA_PID=$(pgrep -f "java.*" | head -n 1 || true)
if [ -n "${JAVA_PID}" ]; then
    echo "[*] Found Java PID: ${JAVA_PID}. Capturing thread dumps and class histograms..."
    jcmd "${JAVA_PID}" VM.version > "${OUTPUT_DIR}/jvm_version.txt" 2>&1 || true
    jcmd "${JAVA_PID}" VM.flags > "${OUTPUT_DIR}/jvm_flags.txt" 2>&1 || true
    jcmd "${JAVA_PID}" VM.uptime > "${OUTPUT_DIR}/jvm_uptime.txt" 2>&1 || true
    
    # Thread dump: critical for diagnosing deadlocks and connection pool starvation
    jcmd "${JAVA_PID}" Thread.print > "${OUTPUT_DIR}/thread_dump.txt" 2>&1 || true
    
    # Top 50 memory consumers by class
    jcmd "${JAVA_PID}" GC.class_histogram | head -n 55 > "${OUTPUT_DIR}/class_histogram_top50.txt" 2>&1 || true
    
    # Off-heap native memory tracking diff if enabled
    jcmd "${JAVA_PID}" VM.native_memory baseline > /dev/null 2>&1 || true
    jcmd "${JAVA_PID}" VM.native_memory detail > "${OUTPUT_DIR}/native_memory_tracking.txt" 2>&1 || true
fi

# 3. Kubernetes Context (if running inside container/cluster)
if command -v kubectl &> /dev/null; then
    echo "[*] Capturing Kubernetes cluster events..."
    kubectl get events --sort-by='.metadata.creationTimestamp' | tail -n 60 > "${OUTPUT_DIR}/k8s_events.txt" 2>&1 || true
fi

# 4. Bundle & Compress
TARBALL="/tmp/forensics-${INCIDENT_ID}.tar.gz"
tar -czf "${TARBALL}" -C "/tmp" "forensics-${INCIDENT_ID}"
rm -rf "${OUTPUT_DIR}"

echo "[+] Forensic bundle successfully created: ${TARBALL}"
echo "[+] Size: $(du -h "${TARBALL}" | cut -f1)"
```

---

## Pattern 2: Spring Boot 3.x Emergency Load Shedding Kill-Switch Actuator

```java
package com.learning.production.lab14;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import org.springframework.boot.actuate.endpoint.annotation.ReadOperation;
import org.springframework.boot.actuate.endpoint.annotation.Selector;
import org.springframework.boot.actuate.endpoint.annotation.WriteOperation;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Emergency Incident Load Shedding Controller.
 * 
 * Exposes /actuator/emergency-circuit to allow on-call engineers
 * to shed non-critical features instantly during database degradation or peak surges.
 */
@Component
@Endpoint(id = "emergency-circuit")
public class EmergencyLoadSheddingEndpoint {

    private static final Logger log = LoggerFactory.getLogger(EmergencyLoadSheddingEndpoint.class);

    // Feature circuit breakers: true = DISABLED (Shedded), false = ACTIVE (Normal)
    private final Map<String, AtomicBoolean> circuits = new ConcurrentHashMap<>();

    public EmergencyLoadSheddingEndpoint() {
        circuits.put("RECOMMENDATIONS", new AtomicBoolean(false));
        circuits.put("LOYALTY_POINTS", new AtomicBoolean(false));
        circuits.put("REALTIME_ANALYTICS", new AtomicBoolean(false));
        circuits.put("EXTERNAL_FRAUD_CHECK", new AtomicBoolean(false));
    }

    @ReadOperation
    public Map<String, Boolean> getCircuits() {
        Map<String, Boolean> status = new ConcurrentHashMap<>();
        circuits.forEach((name, shedded) -> status.put(name, shedded.get()));
        return status;
    }

    @WriteOperation
    public Map<String, Object> updateCircuit(String circuitName, boolean shedded) {
        String key = circuitName.toUpperCase();
        AtomicBoolean state = circuits.get(key);
        if (state == null) {
            return Map.of("error", "Unknown circuit: " + circuitName, "available", circuits.keySet());
        }

        boolean previous = state.getAndSet(shedded);
        log.warn("🚨 [INCIDENT ACTION] Emergency Circuit [{}] toggled: {} -> {} (SHEDDED={})",
                key, previous ? "DISABLED" : "ACTIVE", shedded ? "DISABLED" : "ACTIVE", shedded);

        return Map.of(
                "circuit", key,
                "previousState", previous ? "SHEDDED" : "ACTIVE",
                "newState", shedded ? "SHEDDED" : "ACTIVE",
                "timestamp", System.currentTimeMillis()
        );
    }

    public boolean isFeatureShedded(String circuitName) {
        AtomicBoolean flag = circuits.get(circuitName.toUpperCase());
        return flag != null && flag.get();
    }
}
```

---

## Pattern 3: Adaptive Concurrency Limits (Vegas / AIMD) for Overload Protection

```java
package com.learning.production.lab14;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Adaptive Concurrency Limiter based on the TCP Vegas congestion control algorithm.
 * Dynamically adjusts maximum in-flight requests to prevent queue bloat and latency collapse.
 */
public class AdaptiveConcurrencyLimiter {

    private static final Logger log = LoggerFactory.getLogger(AdaptiveConcurrencyLimiter.class);

    private final AtomicInteger inFlight = new AtomicInteger(0);
    private volatile double currentLimit;
    private final double minLimit;
    private final double maxLimit;
    private final AtomicLong rttEstimateNs = new AtomicLong(TimeUnitToNanos(20)); // Baseline: 20ms

    public AdaptiveConcurrencyLimiter(double initialLimit, double minLimit, double maxLimit) {
        this.currentLimit = initialLimit;
        this.minLimit = minLimit;
        this.maxLimit = maxLimit;
    }

    /**
     * Acquire permission to execute request. Returns false if shed.
     */
    public boolean tryAcquire() {
        int active = inFlight.incrementAndGet();
        if (active > (int) currentLimit) {
            inFlight.decrementAndGet();
            return false; // Shed load! Return 429 Too Many Requests immediately
        }
        return true;
    }

    /**
     * Release permission and adjust dynamic concurrency limit based on measured latency.
     */
    public void release(long durationNs) {
        inFlight.decrementAndGet();
        adjustLimit(durationNs);
    }

    private synchronized void adjustLimit(long durationNs) {
        long currentRtt = rttEstimateNs.get();
        if (durationNs < currentRtt) {
            // New best baseline RTT detected
            rttEstimateNs.set(durationNs);
        }

        // Additive Increase / Multiplicative Decrease (AIMD)
        double queueSize = currentLimit * (1.0 - (double) currentRtt / (double) durationNs);

        if (queueSize <= 3.0) {
            // Healthy latency: gently increase capacity limit (+1)
            currentLimit = Math.min(maxLimit, currentLimit + 1.0);
        } else if (queueSize > 6.0) {
            // Backpressure: queues are backing up! Cut capacity by 15%
            currentLimit = Math.max(minLimit, currentLimit * 0.85);
            log.warn("🚨 [Load Shedding] Queue bloat detected! Contracted concurrency limit to: {}", currentLimit);
        }
    }

    private static long TimeUnitToNanos(long millis) {
        return millis * 1_000_000L;
    }

    public int getInFlight() {
        return inFlight.get();
    }

    public double getCurrentLimit() {
        return currentLimit;
    }
}
```

---

## Pattern 4: Real-Time Incident War Room Structured Logger

```java
package com.learning.production.lab14;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.time.Instant;

/**
 * Emits structured JSON event logs during an active incident to facilitate
 * automated post-mortem timeline generation.
 */
public class IncidentTimelineLogger {

    private static final Logger log = LoggerFactory.getLogger("INCIDENT_TIMELINE");

    public static void logMilestone(String incidentId, String actor, String action, String outcome) {
        try (var idMdc = MDC.putCloseable("incident_id", incidentId);
             var actorMdc = MDC.putCloseable("actor", actor);
             var actionMdc = MDC.putCloseable("action", action);
             var outcomeMdc = MDC.putCloseable("outcome", outcome);
             var timeMdc = MDC.putCloseable("timestamp_iso", Instant.now().toString())) {

            log.info("TIMELINE_EVENT: [{}] by [{}] -> Action: [{}] -> Outcome: [{}]",
                    incidentId, actor, action, outcome);
        }
    }
}
```

---

## Pattern 5: Standardized Executive Incident Broadcast Template

```markdown
# INCIDENT UPDATE BRIEFING TEMPLATE

**Incident ID**: INC-84920
**Severity**: P1 - High Impact
**Incident Commander**: Sarah Chen (Staff SRE)
**Communications Lead**: Alex Rivera
**Technical Lead**: Marcus Vance

---

### Current Status: [MITIGATING]
- [ ] Investigating: Identifying failure domain
- [x] Mitigating: Applying active mitigation actions
- [ ] Monitoring: Verifying telemetry recovery
- [ ] Resolved: Normal operations restored

### Customer Impact Summary
- **Impacted Systems**: Payment Processing & Checkout Cart
- **User Symptoms**: Approximately 18% of European card payments receiving "Payment Declined" (HTTP 504)
- **Financial Run-Rate**: Estimated $12,000/minute in delayed orders

### Actions Taken So Far
- **14:15 UTC**: Alert fired for P99 latency breach on payment-orchestrator.
- **14:22 UTC**: Incident Command established. Hypothesis: Database connection pool exhaustion.
- **14:28 UTC**: Executed emergency circuit kill-switch `/actuator/emergency-circuit` disabling non-critical recommendation queries.
- **14:32 UTC**: Active database connection pool utilization dropped from 100% to 62%.

### Next Planned Action
- Initiating canary rollback of `payment-orchestrator` to revision 48 to remove unindexed transaction query.

**Next Briefing Scheduled At**: 14:50 UTC (15-minute cadence)
```
