# Monitoring and Alerting Guide — Deployment Rollback Incident Detection

## Lab 06: Production Deployment Rollback

This guide documents the monitoring and alerting configuration required to detect, diagnose, and automatically respond to bad deployment incidents. The monitoring stack uses Azure Monitor, Application Insights, and custom metrics from the Kubernetes cluster.

---

## 1. Deployment Health Monitoring

### Key Metrics to Track

| Metric | Source | Collection Method | Aggregation |
|--------|--------|-------------------|-------------|
| HTTP Error Rate (5xx) | Application Insights | Per-request logging | Rate per minute, per deployment |
| Request Latency (p50/p95/p99) | Application Insights | Distributed tracing | Percentile per minute |
| Active Sessions | Azure Load Balancer | Connection count | Average per node |
| Node Health Status | AKS / kubelet | Readiness/liveness probes | Count per deployment version |
| Pod Restart Count | AKS / kube-state-metrics | Event stream | Rate per deployment |
| Connection Draining Time | AKS / kubelet | PreStop hook duration | Average per pod |
| Deployment Progress | Azure DevOps API | Pipeline events | Status per stage |

### Azure Monitor Metric Alert Rules

#### Alert 1: Error Rate Spike (Immediate — Auto-Rollback Trigger)

```json
{
    "name": "Deployment-ErrorRate-Critical",
    "description": "Error rate exceeds 1% for 2 consecutive minutes — triggers automated rollback",
    "severity": 0,
    "enabled": true,
    "evaluationFrequency": "PT1M",
    "windowSize": "PT2M",
    "criteria": {
        "metricName": "requests/errors",
        "operator": "GreaterThan",
        "threshold": 1.0,
        "timeAggregation": "Average"
    },
    "actions": [
        {
            "actionGroupId": "AutoRollbackActionGroup",
            "webhookProperties": {
                "rollbackType": "automatic",
                "severity": "SEV1"
            }
        }
    ]
}
```

#### Alert 2: Canary Health Check Failure (Immediate)

```json
{
    "name": "Canary-HealthCheck-Failure",
    "description": "New deployment health checks failing — stop rollout immediately",
    "severity": 0,
    "enabled": true,
    "evaluationFrequency": "PT1M",
    "windowSize": "PT1M",
    "criteria": {
        "metricName": "healthcheck/failures",
        "operator": "GreaterThan",
        "threshold": 1
    }
}
```

#### Alert 3: Latency Degradation (High Priority)

```json
{
    "name": "Deployment-Latency-Degradation",
    "description": "p95 latency exceeds 200ms or 1.5x baseline",
    "severity": 1,
    "enabled": true,
    "evaluationFrequency": "PT1M",
    "windowSize": "PT5M",
    "criteria": {
        "metricName": "requests/duration",
        "operator": "GreaterThan",
        "threshold": 200,
        "timeAggregation": "Percentile_95"
    }
}
```

---

## 2. Application Performance Monitoring

### Application Insights Configuration

```xml
<!-- appinsights-config.xml -->
<ApplicationInsights xmlns="http://schemas.microsoft.com/ApplicationInsights/2013/Settings">
    <InstrumentationKey>${APPINSIGHTS_INSTRUMENTATIONKEY}</InstrumentationKey>
    <TelemetryModules>
        <Add type="com.microsoft.applicationinsights.web.extensibility.modules.WebRequestTrackingTelemetryModule"/>
        <Add type="com.microsoft.applicationinsights.web.extensibility.modules.WebRequestTrackingTelemetryModule"/>
    </TelemetryModules>
    <TelemetryInitializers>
        <Add type="com.microsoft.applicationinsights.web.extensibility.initializers.WebAppTelemetryInitializer"/>
    </TelemetryInitializers>
    <PerformanceCollector>
        <Add type="com.microsoft.applicationinsights.perfcounter.collectors.JvmPerformanceCountersCollector"/>
    </PerformanceCollector>
</ApplicationInsights>
```

### Custom Metric Reporting in Java

```java
package com.example.preference.monitoring;

import com.microsoft.applicationinsights.TelemetryClient;
import com.microsoft.applicationinsights.telemetry.DurationTelemetry;
import org.springframework.stereotype.Component;
import java.util.HashMap;
import java.util.Map;

@Component
public class DeploymentMetricsReporter {

    private final TelemetryClient telemetryClient;

    public DeploymentMetricsReporter(TelemetryClient telemetryClient) {
        this.telemetryClient = telemetryClient;
    }

    public void reportDeploymentMetric(String metricName, double value, String deploymentVersion) {
        Map<String, String> properties = new HashMap<>();
        properties.put("deploymentVersion", deploymentVersion);
        properties.put("metricName", metricName);
        properties.put("source", "user-preference-service");

        telemetryClient.trackMetric(metricName, value, 1, null, properties);
    }

    public void reportErrorRate(String deploymentVersion, double errorRate) {
        reportDeploymentMetric("errorRate", errorRate, deploymentVersion);

        if (errorRate > 1.0) {
            Map<String, String> alertProps = new HashMap<>();
            alertProps.put("deploymentVersion", deploymentVersion);
            alertProps.put("errorRate", String.valueOf(errorRate));
            alertProps.put("threshold", "1.0");
            telemetryClient.trackEvent("ErrorRateThresholdBreached", alertProps, null);

            telemetryClient.trackTrace(
                String.format("CRITICAL: Error rate %.2f%% exceeded 1%% threshold for deployment %s",
                    errorRate, deploymentVersion),
                SeverityLevel.Critical,
                alertProps
            );
        }
    }

    public void reportHealthCheckStatus(String deploymentVersion, boolean healthy, String reason) {
        Map<String, String> props = new HashMap<>();
        props.put("deploymentVersion", deploymentVersion);
        props.put("healthy", String.valueOf(healthy));
        if (reason != null) {
            props.put("failureReason", reason);
        }
        telemetryClient.trackEvent("HealthCheckResult", props, null);
    }

    public void reportCanaryMetric(
        String metricName,
        double canaryValue,
        double baselineValue,
        String deploymentVersion
    ) {
        Map<String, String> props = new HashMap<>();
        props.put("deploymentVersion", deploymentVersion);
        props.put("canaryValue", String.valueOf(canaryValue));
        props.put("baselineValue", String.valueOf(baselineValue));
        props.put("delta", String.valueOf(canaryValue - baselineValue));

        telemetryClient.trackEvent("CanaryMetricComparison", props, null);
    }
}
```

### Kubernetes Health Probe Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: user-preference-service
  labels:
    app: user-preference-service
    version: v2.3.45
spec:
  containers:
  - name: user-preference-service
    image: prodacr2026.azurecr.io/user-preference-service:v2.3.45
    ports:
    - containerPort: 8080
      name: http
    - containerPort: 8081
      name: management
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8081
      initialDelaySeconds: 30
      periodSeconds: 15
      failureThreshold: 3
      timeoutSeconds: 5
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8081
      initialDelaySeconds: 15
      periodSeconds: 10
      failureThreshold: 2
      timeoutSeconds: 3
    startupProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8081
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 30
      timeoutSeconds: 3
```

---

## 3. Feature Flag Monitoring

### LaunchDarkly Metric Integration

```java
package com.example.preference.monitoring;

import com.launchdarkly.sdk.server.LDClient;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import org.springframework.stereotype.Component;
import javax.annotation.PostConstruct;

@Component
public class FeatureFlagMetricsExporter {

    private final LDClient launchDarklyClient;
    private final MeterRegistry meterRegistry;

    private Counter flagEvaluationCounter;
    private Counter flagErrorCounter;
    private Counter flagKillSwitchCounter;

    public FeatureFlagMetricsExporter(LDClient launchDarklyClient, MeterRegistry meterRegistry) {
        this.launchDarklyClient = launchDarklyClient;
        this.meterRegistry = meterRegistry;
    }

    @PostConstruct
    public void init() {
        flagEvaluationCounter = meterRegistry.counter("featureflag.evaluations.total");
        flagErrorCounter = meterRegistry.counter("featureflag.evaluations.errors");
        flagKillSwitchCounter = meterRegistry.counter("featureflag.killswitch.activated");
    }

    public void recordFlagEvaluation(String flagKey, boolean result, boolean success) {
        if (success) {
            flagEvaluationCounter.increment();
            meterRegistry.counter("featureflag.evaluations.by_flag",
                "flag", flagKey,
                "result", String.valueOf(result)
            ).increment();
        } else {
            flagErrorCounter.increment();
            meterRegistry.counter("featureflag.evaluations.errors.by_flag",
                "flag", flagKey
            ).increment();
        }
    }

    public void recordKillSwitchActivation(String flagKey) {
        flagKillSwitchCounter.increment();
        meterRegistry.counter("featureflag.killswitch.by_flag",
            "flag", flagKey
        ).increment();
    }
}
```

### Feature Flag Monitoring Dashboard (Azure Dashboard JSON Extract)

```json
{
    "properties": {
        "lenses": [
            {
                "order": 0,
                "parts": [
                    {
                        "position": { "x": 0, "y": 0 },
                        "metadata": {
                            "type": "Extension/HubsExtension/PartType/MonitorChartPart",
                            "settings": {
                                "content": {
                                    "metrics": [
                                        { "resourceMetadata": { "id": "{app-insights-id}" },
                                          "name": "featureflag.evaluations.total",
                                          "aggregationType": 1 }
                                    ],
                                    "title": "Feature Flag Evaluation Rate"
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }
}
```

---

## 4. Canary Analysis Monitoring

### Automated Canary Health Check (PowerShell)

```powershell
function Test-CanaryHealth {
    param(
        [string]$ResourceGroup,
        [string]$ClusterName,
        [int]$DurationMinutes = 60,
        [double]$ErrorRateThreshold = 0.01,
        [int]$LatencyThreshold = 200
    )

    $startTime = (Get-Date).AddMinutes(-$DurationMinutes)
    $endTime = Get-Date

    $query = @"
    requests
    | where timestamp >= datetime($($startTime.ToString('yyyy-MM-dd HH:mm:ss')))
    | where timestamp <= datetime($($endTime.ToString('yyyy-MM-dd HH:mm:ss')))
    | where cloud_RoleInstance contains "green"
    | summarize
        TotalRequests = count(),
        ErrorCount = countif(success == false),
        ErrorRate = (countif(success == false) * 100.0) / count(),
        P95Latency = percentile(duration, 95)
    | project ErrorRate, P95Latency, TotalRequests
"@

    $result = az monitor app-insights query `
        --app prod-app-insights `
        --analytics-query $query `
        --offset $DurationMinutes`m | ConvertFrom-Json

    $passed = $true
    $failureReasons = @()

    if ($result.ErrorRate -gt $ErrorRateThreshold) {
        $passed = $false
        $failureReasons += "Error rate $($result.ErrorRate)% exceeds threshold $($ErrorRateThreshold)%"
    }

    if ($result.P95Latency -gt $LatencyThreshold) {
        $passed = $false
        $failureReasons += "P95 latency $($result.P95Latency)ms exceeds threshold ${LatencyThreshold}ms"
    }

    if ($result.TotalRequests -lt 10000) {
        $passed = $false
        $failureReasons += "Insufficient sample size: $($result.TotalRequests) requests (minimum 10000)"
    }

    return @{
        Passed = $passed
        FailureReason = ($failureReasons -join "; ")
        ErrorRate = $result.ErrorRate
        P95Latency = $result.P95Latency
        TotalRequests = $result.TotalRequests
    }
}
```

---

## 5. Dashboard Layout

### Deployment Health Dashboard (Azure Dashboard)

**Row 1 — High-Level Overview**
- Total requests per minute (line chart, split by deployment version)
- Error rate percentage (line chart, with threshold line at 1%)
- Active sessions count (area chart)
- Healthy/unhealthy node count (stacked bar chart)

**Row 2 — Performance Metrics**
- P50/P95/P99 latency (multi-line chart, with baseline reference)
- Request duration distribution (heatmap)
- CPU/Memory utilization per node (multi-line chart)

**Row 3 — Deployment-Specific**
- Deployment progress indicator (pipeline stage timeline)
- Canary analysis metrics (side-by-side comparison bars)
- Feature flag evaluation rate (line chart)
- Rollback trigger status (single value: armed/disarmed)

**Row 4 — Alert History**
- Active alerts list
- Alert firing frequency (last 24 hours)
- MTTR (Mean Time to Resolve) chart

---

## 6. Logging Configuration

### Logback Configuration for Deployment Tracking

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="AIAppender" class="com.microsoft.applicationinsights.logback.ApplicationInsightsAppender">
        <instrumentationKey>${APPINSIGHTS_INSTRUMENTATIONKEY}</instrumentationKey>
    </appender>

    <logger name="com.example.preference.cache" level="DEBUG">
        <appender-ref ref="AIAppender"/>
    </logger>

    <logger name="com.example.preference.client" level="DEBUG">
        <appender-ref ref="AIAppender"/>
    </logger>

    <root level="INFO">
        <appender-ref ref="AIAppender"/>
    </root>
</configuration>
```

### Structured Logging Fields

Every log entry should include:
- `deploymentVersion` — current deployment tag
- `featureFlagState` — state of relevant feature flags
- `userId` — anonymized user identifier
- `traceId` — distributed trace correlation ID
- `component` — service name
- `severity` — log level (DEBUG/INFO/WARN/ERROR/FATAL)

---

## 7. Alert Response Runbook

### When Auto-Rollback Triggers

1. **Do NOT re-enable the deployment** — the automated rollback has already reverted to the previous version
2. Check the auto-rollback notification for the trigger metric (error rate, latency, health check)
3. Examine Application Insights for the failing deployment's error distribution
4. Review the feature flag status — has it been disabled automatically?
5. Check that all pods returned to healthy state (kubectl get pods)
6. Investigate root cause before attempting re-deployment

### When Canary Fails (Non-Auto-Rollback)

1. Review canary analysis comparison metrics
2. Check per-endpoint error rates — is the failure isolated to specific endpoints?
3. Determine if the failure is transient or persistent (check traffic patterns)
4. Manually initiate rollback if not already triggered
5. Disable associated feature flags
6. Notify feature team the deployment has failed canary

### When Error Rate Spike Occurs (No Deployment Active)

1. This indicates a non-deployment-related issue — follow standard incident response
2. Check for upstream/downstream service degradation
3. Review recent configuration changes (feature flag changes, config map updates)
4. Check for infrastructure issues (node failures, network partitions)

---

## References

- Google SRE Book — Chapter 10: "Practical Alerting"
- Microsoft Azure Documentation: "Monitor AKS with Azure Monitor" — https://learn.microsoft.com/en-us/azure/aks/monitor-aks
- Netflix Tech Blog: "Metrics at Netflix" — https://netflixtechblog.com/metrics-at-netflix-4e6c7a8b4f5b
- LaunchDarkly Documentation: "Monitoring Feature Flag Performance" — (link removed)
- AWS re:Invent 2019 — "Monitoring and Observability at Amazon" (OPS205)
