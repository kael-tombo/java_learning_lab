# CODE DEEP DIVE: Production Readiness Automation
## Lab 20 | Capstone | Production Engineering Academy

---

## Pattern 1: Automated Production Readiness Linter (CI/CD Pipeline Gate)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Automated PRR Gate Linter for Kubernetes manifests and JVM configuration
MANIFEST_FILE=${1:-"k8s/deployment.yaml"}
FAILURES=0

echo "=== RUNNING AUTOMATED PRODUCTION READINESS REVIEW (PRR) ON ${MANIFEST_FILE} ==="

check_rule() {
    local rule_name="$1"
    local condition="$2"
    if eval "${condition}"; then
        echo "  [PASS] ${rule_name}"
    else
        echo "  [FAIL] ${rule_name}"
        FAILURES=$((FAILURES + 1))
    fi
}

# 1. Non-Root Security
check_rule "Security: Container must run as non-root" \
    "grep -q 'runAsNonRoot: true' ${MANIFEST_FILE} || grep -q 'runAsUser: [1-9]' ${MANIFEST_FILE}"

# 2. Lifecycle PreStop Hook
check_rule "Resilience: preStop sleep hook must be configured" \
    "grep -A 5 'lifecycle:' ${MANIFEST_FILE} | grep -q 'sleep'"

# 3. Probes Configuration
check_rule "Availability: startupProbe must be configured" \
    "grep -q 'startupProbe:' ${MANIFEST_FILE}"

check_rule "Availability: livenessProbe must be configured" \
    "grep -q 'livenessProbe:' ${MANIFEST_FILE}"

check_rule "Availability: readinessProbe must be configured" \
    "grep -q 'readinessProbe:' ${MANIFEST_FILE}"

# 4. Resource Sizing
check_rule "Capacity: Memory requests and limits must be defined" \
    "grep -A 4 'resources:' ${MANIFEST_FILE} | grep -q 'memory:'"

# 5. High Availability Constraints
check_rule "Reliability: topologySpreadConstraints or podAntiAffinity configured" \
    "grep -q -E 'topologySpreadConstraints|podAntiAffinity' ${MANIFEST_FILE}"

# 6. JVM Heap Dump Volume
check_rule "Diagnostics: /dumps volume mounted for OOM forensic analysis" \
    "grep -q '/dumps' ${MANIFEST_FILE}"

echo "========================================================================"
if [ ${FAILURES} -gt 0 ]; then
    echo "PRR FAILED: ${FAILURES} critical operational safety rule(s) violated!"
    echo "Service cannot be deployed to Production until all gates pass."
    exit 1
else
    echo "PRR PASSED: All automated production readiness gates verified!"
    exit 0
fi
```

---

## Pattern 2: Spring Boot Complete Production Readiness Health Indicator

```java
package com.learning.production.lab20;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.Statement;

@Component("deepProductionHealth")
public class DeepProductionHealthIndicator implements HealthIndicator {

    private final DataSource dataSource;

    public DeepProductionHealthIndicator(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public Health health() {
        // Fast non-blocking check for Readiness probe
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.setQueryTimeout(1); // 1-second timeout guard
            stmt.execute("SELECT 1");
            return Health.up()
                    .withDetail("database", "ONLINE")
                    .withDetail("thread_count", Thread.activeCount())
                    .build();
        } catch (Exception ex) {
            return Health.down()
                    .withDetail("database", "OFFLINE")
                    .withDetail("error", ex.getMessage())
                    .build();
        }
    }
}
```
