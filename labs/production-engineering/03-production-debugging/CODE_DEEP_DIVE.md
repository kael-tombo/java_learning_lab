# CODE DEEP DIVE: Production Debugging & Diagnostics
## Lab 03 | Production Engineering Academy

---

## Pattern 1: Programmatic Java Flight Recorder (JFR) Trigger on SLA Breach

### Context
In high-throughput microservices, running continuous heavy profiling creates overhead or logs too much noise. The optimal production pattern is to keep continuous in-memory flight recording active in a circular buffer and only dump the recording to disk when a tail latency spike or abnormal error threshold occurs.

```java
package com.learning.production.lab03;

import jdk.jfr.Configuration;
import jdk.jfr.Recording;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.ParseException;
import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Production-ready dynamic JFR trigger.
 * Maintains an in-memory rolling 2-minute buffer with <1% overhead.
 * Automatically dumps to disk when p99 SLA is violated.
 */
public class DynamicJfrEmergencyRecorder implements AutoCloseable {
    private static final Logger log = LoggerFactory.getLogger(DynamicJfrEmergencyRecorder.class);
    
    private final Recording recording;
    private final Path dumpDirectory;
    private final AtomicBoolean isDumping = new AtomicBoolean(false);

    public DynamicJfrEmergencyRecorder(String serviceName, Path dumpDirectory) throws IOException, ParseException {
        this.dumpDirectory = dumpDirectory;
        if (!Files.exists(dumpDirectory)) {
            Files.createDirectories(dumpDirectory);
        }

        // Load built-in profiling configuration (low overhead, ~1%)
        Configuration config = Configuration.getConfiguration("profile");
        this.recording = new Recording(config);
        
        // Circular buffer: keep only the last 2 minutes or max 128 MB in memory
        this.recording.setName(serviceName + "-Emergency-Buffer");
        this.recording.setMaxAge(Duration.ofMinutes(2));
        this.recording.setMaxSize(128 * 1024 * 1024L);
        this.recording.setToDisk(true);
        this.recording.start();
        
        log.info("JFR Rolling Flight Recording started. MaxAge=2m, MaxSize=128MB");
    }

    /**
     * Trigger an asynchronous snapshot dump when an anomaly is detected.
     */
    public void triggerEmergencyDump(String triggerReason, long latencyMs) {
        if (!isDumping.compareAndSet(false, true)) {
            log.warn("Dump already in progress. Skipping trigger for reason: {}", triggerReason);
            return;
        }

        Thread.ofVirtual().name("jfr-emergency-dumper").start(() -> {
            try {
                String filename = String.format("jfr-incident-%s-%dms-%s.jfr",
                        triggerReason.replaceAll("[^a-zA-Z0-9.-]", "_"),
                        latencyMs,
                        Instant.now().toString().replace(':', '-'));
                
                Path targetPath = dumpDirectory.resolve(filename);
                log.error("CRITICAL SLA BREACH [{}ms > SLA]: Capturing rolling JFR to {}", latencyMs, targetPath);
                
                // Copy the rolling snapshot without stopping recording
                recording.dump(targetPath);
                
                log.info("Emergency JFR snapshot successfully written ({} bytes). Send to SRE/Architect.",
                        Files.size(targetPath));
            } catch (Exception e) {
                log.error("Failed to dump emergency JFR recording", e);
            } finally {
                // Cool down for 30 seconds before allowing another dump
                try {
                    Thread.sleep(30_000);
                } catch (InterruptedException ignored) {}
                isDumping.set(false);
            }
        });
    }

    @Override
    public void close() {
        if (recording != null) {
            recording.stop();
            recording.close();
            log.info("JFR Emergency Recorder stopped.");
        }
    }
}
```

---

## Pattern 2: Custom JFR Event for Latency Correlation

### Context
Correlating custom application business metrics (e.g. database query, external payment call, lock acquisition) directly into the JVM timeline alongside GC pauses and CPU sample spikes.

```java
package com.learning.production.lab03;

import jdk.jfr.*;

@Name("com.learning.OrderProcessingEvent")
@Label("Order Processing Operation")
@Category({"E-Commerce", "Order Service"})
@Description("Tracks high-level order fulfillment timing and state transitions")
@StackTrace(false) // Disable stack trace capture for micro-benchmarks to minimize overhead
public class OrderProcessingEvent extends Event {

    @Label("Order ID")
    private String orderId;

    @Label("Customer Tier")
    private String customerTier;

    @Label("Payment Gateway")
    private String gateway;

    @Label("Success")
    private boolean successful;

    public void setOrderId(String orderId) { this.orderId = orderId; }
    public void setCustomerTier(String customerTier) { this.customerTier = customerTier; }
    public void setGateway(String gateway) { this.gateway = gateway; }
    public void setSuccessful(boolean successful) { this.successful = successful; }

    // Convenience execution wrapper
    public static void measure(String orderId, String tier, String gateway, Runnable action) {
        OrderProcessingEvent event = new OrderProcessingEvent();
        if (event.isEnabled()) {
            event.setOrderId(orderId);
            event.setCustomerTier(tier);
            event.setGateway(gateway);
            event.begin();
        }
        
        boolean ok = false;
        try {
            action.run();
            ok = true;
        } finally {
            if (event.isEnabled()) {
                event.setSuccessful(ok);
                event.commit(); // Writes event with duration directly to JVM flight record buffer
            }
        }
    }
}
```

---

## Pattern 3: Automated Thread Dump Diagnostics & Lock Contention Analyzer

### Context
When threads are stuck or CPU is pegging at 100%, taking a thread dump via `ThreadMXBean` programmatically inside the running container allows the service to detect deadlocks or thread pool saturation and emit structured log events before crashing.

```java
package com.learning.production.lab03;

import java.lang.management.ManagementFactory;
import java.lang.management.ThreadInfo;
import java.lang.management.ThreadMXBean;
import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ThreadPoolHealthDiagnostics {
    private static final Logger log = LoggerFactory.getLogger(ThreadPoolHealthDiagnostics.class);
    private static final ThreadMXBean THREAD_BEAN = ManagementFactory.getThreadMXBean();

    /**
     * Inspects JVM for deadlocks and thread state distributions.
     */
    public static DiagnosticsReport inspectThreads() {
        long[] deadlockedThreadIds = THREAD_BEAN.findDeadlockedThreads();
        List<String> deadlocks = new ArrayList<>();
        
        if (deadlockedThreadIds != null && deadlockedThreadIds.length > 0) {
            ThreadInfo[] infos = THREAD_BEAN.getThreadInfo(deadlockedThreadIds, true, true);
            for (ThreadInfo info : infos) {
                deadlocks.add(String.format("Thread '%s' (ID %d) BLOCKED on lock %s owned by '%s' (ID %d)",
                        info.getThreadName(),
                        info.getThreadId(),
                        info.getLockInfo(),
                        info.getLockOwnerName(),
                        info.getLockOwnerId()));
            }
        }

        // Aggregate thread states across all active threads
        ThreadInfo[] allThreads = THREAD_BEAN.dumpAllThreads(false, false);
        Map<Thread.State, Integer> stateCounts = new EnumMap<>(Thread.State.class);
        for (Thread.State state : Thread.State.values()) {
            stateCounts.put(state, 0);
        }
        
        for (ThreadInfo info : allThreads) {
            Thread.State s = info.getThreadState();
            stateCounts.put(s, stateCounts.get(s) + 1);
        }

        return new DiagnosticsReport(allThreads.length, stateCounts, deadlocks);
    }

    public record DiagnosticsReport(
            int totalThreads,
            Map<Thread.State, Integer> states,
            List<String> deadlockDetails
    ) {
        public boolean hasDeadlocks() {
            return !deadlockDetails.isEmpty();
        }

        public String summary() {
            return String.format("Total: %d | RUNNABLE: %d, WAITING: %d, TIMED_WAITING: %d, BLOCKED: %d | Deadlocks: %d",
                    totalThreads,
                    states.getOrDefault(Thread.State.RUNNABLE, 0),
                    states.getOrDefault(Thread.State.WAITING, 0),
                    states.getOrDefault(Thread.State.TIMED_WAITING, 0),
                    states.getOrDefault(Thread.State.BLOCKED, 0),
                    deadlockDetails.size());
        }
    }
}
```
