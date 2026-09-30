# CODE DEEP DIVE: Incident Forensics & Automation
## Lab 14 | Production Engineering Academy

---

## Pattern 1: Automated Incident Forensic Bundle Generator (Bash/CLI)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Production incident snapshot collector
INCIDENT_ID=${1:-"inc-$(date +%Y%m%d-%H%M%S)"}
OUTPUT_DIR="/tmp/incident-forensics-${INCIDENT_ID}"
mkdir -p "${OUTPUT_DIR}"

echo "[*] Collecting Incident Forensics for ${INCIDENT_ID} to ${OUTPUT_DIR}..."

# 1. System metrics snapshot
top -b -n 1 > "${OUTPUT_DIR}/top.txt"
vmstat 1 5 > "${OUTPUT_DIR}/vmstat.txt"
iostat -xz 1 5 > "${OUTPUT_DIR}/iostat.txt" || true
netstat -s > "${OUTPUT_DIR}/netstat.txt"
ss -s > "${OUTPUT_DIR}/socket_summary.txt"

# 2. JVM Diagnostics (if Java PID exists)
JAVA_PID=$(pgrep -f "java.*app.jar" | head -n 1 || true)
if [ -n "${JAVA_PID}" ]; then
    echo "[*] Found Java PID: ${JAVA_PID}. Capturing thread and memory dumps..."
    jcmd "${JAVA_PID}" VM.version > "${OUTPUT_DIR}/jvm_version.txt"
    jcmd "${JAVA_PID}" VM.flags > "${OUTPUT_DIR}/jvm_flags.txt"
    jcmd "${JAVA_PID}" VM.uptime > "${OUTPUT_DIR}/jvm_uptime.txt"
    jcmd "${JAVA_PID}" Thread.print > "${OUTPUT_DIR}/thread_dump.txt"
    jcmd "${JAVA_PID}" GC.class_histogram > "${OUTPUT_DIR}/class_histogram.txt"
    jcmd "${JAVA_PID}" VM.native_memory detail > "${OUTPUT_DIR}/native_memory.txt" || true
fi

# 3. Kubernetes environment context
if command -v kubectl &> /dev/null; then
    echo "[*] Capturing Kubernetes cluster events..."
    kubectl get events --sort-by='.metadata.creationTimestamp' | tail -n 50 > "${OUTPUT_DIR}/k8s_events.txt"
fi

# 4. Compress bundle
tar -czf "${OUTPUT_DIR}.tar.gz" -C "/tmp" "incident-forensics-${INCIDENT_ID}"
echo "[+] Forensic bundle complete: ${OUTPUT_DIR}.tar.gz"
```

---

## Pattern 2: Spring Boot Incident Kill-Switch / Circuit Breaker Actuator

```java
package com.learning.production.lab14;

import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import org.springframework.boot.actuate.endpoint.annotation.ReadOperation;
import org.springframework.boot.actuate.endpoint.annotation.WriteOperation;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

@Component
@Endpoint(id = "emergency-circuit")
public class EmergencyIncidentCircuitEndpoint {

    private final Map<String, AtomicBoolean> circuits = new ConcurrentHashMap<>();

    public EmergencyIncidentCircuitEndpoint() {
        circuits.put("PAYMENT_GATEWAY", new AtomicBoolean(false));
        circuits.put("RECOMMENDATION_ENGINE", new AtomicBoolean(false));
        circuits.put("BACKGROUND_REPORTING", new AtomicBoolean(false));
    }

    @ReadOperation
    public Map<String, Boolean> listCircuits() {
        Map<String, Boolean> status = new ConcurrentHashMap<>();
        circuits.forEach((k, v) -> status.put(k, v.get()));
        return status;
    }

    @WriteOperation
    public String tripCircuit(String circuitName, boolean disabled) {
        AtomicBoolean flag = circuits.get(circuitName.toUpperCase());
        if (flag == null) {
            return "ERROR: Unknown circuit: " + circuitName;
        }
        flag.set(disabled);
        return String.format("CIRCUIT [%s] STATE UPDATED TO: %s", circuitName, disabled ? "DISABLED (SHED LOAD)" : "ACTIVE");
    }

    public boolean isFeatureDisabled(String circuitName) {
        AtomicBoolean flag = circuits.get(circuitName.toUpperCase());
        return flag != null && flag.get();
    }
}
```
