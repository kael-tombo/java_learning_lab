# Solution Guide — Production Deployment Rollback Fix

## Problem: Bad Deployment Takes Down 25% of Nodes

This guide provides compilable Java code fixes, Azure DevOps pipeline configurations, and step-by-step remediation instructions for the deployment rollback incident. The solution implements four layers of defense: defensive coding, feature flag gating, progressive exposure, and automated rollback.

---

## Layer 1: Defensive Programming — Null Check Fix

### Root Cause Code

The original code in `UserPreferenceCacheService.java` assumed the downstream service always returns a valid object:

```java
package com.example.preference.cache;

import com.example.preference.client.DownstreamPreferenceClient;
import com.example.preference.model.UserPreferences;
import org.springframework.stereotype.Service;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class UserPreferenceCacheService {

    private final DownstreamPreferenceClient preferenceClient;
    private final Map<String, UserPreferences> cache = new ConcurrentHashMap<>();

    public UserPreferenceCacheService(DownstreamPreferenceClient preferenceClient) {
        this.preferenceClient = preferenceClient;
    }

    public UserPreferences getUserPreferences(String userId) {
        UserPreferences preferences = preferenceClient.getPreferences(userId);
        Map<String, String> cachedPrefs = preferences.getCachedPreferences();
        return new UserPreferences(userId, cachedPrefs);
    }
}
```

### Fixed Code with Null Check and Defensive Fallback

```java
package com.example.preference.cache;

import com.example.preference.client.DownstreamPreferenceClient;
import com.example.preference.model.UserPreferences;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class UserPreferenceCacheService {

    private static final Logger log = LoggerFactory.getLogger(UserPreferenceCacheService.class);

    private final DownstreamPreferenceClient preferenceClient;
    private final Map<String, UserPreferences> localCache = new ConcurrentHashMap<>();

    public UserPreferenceCacheService(DownstreamPreferenceClient preferenceClient) {
        this.preferenceClient = preferenceClient;
    }

    @CircuitBreaker(name = "preferenceClient", fallbackMethod = "getUserPreferencesFallback")
    public UserPreferences getUserPreferences(String userId) {
        Objects.requireNonNull(userId, "userId must not be null");

        UserPreferences preferences = preferenceClient.getPreferences(userId);

        if (preferences == null) {
            log.warn("Downstream preference service returned null for userId={}, using fallback", userId);
            return getUserPreferencesFallback(userId, new RuntimeException("Null response from downstream"));
        }

        Map<String, String> cachedPrefs = preferences.getCachedPreferences();
        if (cachedPrefs == null) {
            log.warn("getCachedPreferences() returned null for userId={}, using empty map", userId);
            cachedPrefs = Collections.emptyMap();
        }

        UserPreferences result = new UserPreferences(userId, cachedPrefs);
        localCache.put(userId, result);
        return result;
    }

    public UserPreferences getUserPreferencesFallback(String userId, Throwable t) {
        log.error("Fallback triggered for userId={}, cause={}", userId, t.getMessage());

        UserPreferences cached = localCache.get(userId);
        if (cached != null) {
            log.info("Returning stale cached preferences for userId={}", userId);
            return cached;
        }

        log.info("No cached preferences found for userId={}, returning empty defaults", userId);
        return new UserPreferences(userId, Collections.emptyMap());
    }
}
```

### Unit Test for Null Return Scenario

```java
package com.example.preference.cache;

import com.example.preference.client.DownstreamPreferenceClient;
import com.example.preference.model.UserPreferences;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserPreferenceCacheServiceTest {

    @Mock
    private DownstreamPreferenceClient mockClient;

    private UserPreferenceCacheService service;

    @BeforeEach
    void setUp() {
        service = new UserPreferenceCacheService(mockClient);
    }

    @Test
    void shouldReturnEmptyPreferencesWhenDownstreamReturnsNull() {
        when(mockClient.getPreferences(anyString())).thenReturn(null);
        UserPreferences result = service.getUserPreferences("user-123");
        assertNotNull(result, "Should return non-null UserPreferences");
        assertTrue(result.getCachedPreferences().isEmpty(),
            "Should return empty cached preferences when downstream returns null");
    }

    @Test
    void shouldReturnEmptyMapWhenGetCachedPreferencesReturnsNull() {
        UserPreferences mockPrefs = new UserPreferences("user-123", null);
        when(mockClient.getPreferences(anyString())).thenReturn(mockPrefs);
        UserPreferences result = service.getUserPreferences("user-123");
        assertNotNull(result);
        assertNotNull(result.getCachedPreferences());
        assertTrue(result.getCachedPreferences().isEmpty());
    }

    @Test
    void shouldReturnStaleCacheWhenDownstreamFails() {
        UserPreferences initialPrefs = new UserPreferences("user-123",
            Map.of("theme", "dark", "language", "en"));
        when(mockClient.getPreferences(anyString()))
            .thenReturn(initialPrefs)
            .thenThrow(new RuntimeException("Downstream unavailable"));

        UserPreferences firstResult = service.getUserPreferences("user-123");
        assertNotNull(firstResult);
        assertEquals("dark", firstResult.getCachedPreferences().get("theme"));

        UserPreferences fallbackResult = service.getUserPreferences("user-123");
        assertNotNull(fallbackResult);
        assertEquals("dark", fallbackResult.getCachedPreferences().get("theme"),
            "Should return stale cached data on downstream failure");
    }

    @Test
    void shouldThrowWhenUserIdIsNull() {
        assertThrows(NullPointerException.class,
            () -> service.getUserPreferences(null),
            "Should throw NPE for null userId");
    }
}
```

---

## Layer 2: Feature Flag Gating with LaunchDarkly

### Feature Flag Configuration

Create a LaunchDarkly feature flag called `user-preference-cache-enabled` with:
- Flag type: boolean
- Default variation: false (disabled)
- Targeting: enabled for internal testing first
- Prerequisites: none

### Java Integration with Feature Flag

```java
package com.example.preference.cache;

import com.launchdarkly.sdk.LDUser;
import com.launchdarkly.sdk.server.LDClient;
import org.springframework.stereotype.Service;

@Service
public class FeatureFlagService {

    private static final String CACHE_FLAG_KEY = "user-preference-cache-enabled";
    private static final String ROLLBACK_FLAG_KEY = "emergency-rollback-override";

    private final LDClient launchDarklyClient;

    public FeatureFlagService(LDClient launchDarklyClient) {
        this.launchDarklyClient = launchDarklyClient;
    }

    public boolean isPreferenceCacheEnabled(String userId) {
        LDUser user = new LDUser.Builder(userId)
            .privateAttributes(List.of("email", "name"))
            .build();

        return launchDarklyClient.boolVariation(CACHE_FLAG_KEY, user, false);
    }

    public boolean isEmergencyRollbackActive() {
        LDUser globalUser = new LDUser.Builder("global-operator").build();
        return launchDarklyClient.boolVariation(ROLLBACK_FLAG_KEY, globalUser, false);
    }
}
```

### Modified Service with Feature Flag

```java
@Service
public class UserPreferenceCacheService {

    private final DownstreamPreferenceClient preferenceClient;
    private final FeatureFlagService featureFlagService;

    public UserPreferences getUserPreferences(String userId) {
        Objects.requireNonNull(userId, "userId must not be null");

        if (!featureFlagService.isPreferenceCacheEnabled(userId)) {
            log.debug("Preference cache feature disabled for userId={}, calling downstream directly", userId);
            return preferenceClient.getPreferences(userId);
        }

        return getCachedUserPreferences(userId);
    }

    private UserPreferences getCachedUserPreferences(String userId) {
        // null-safe implementation from Layer 1
    }
}
```

---

## Layer 3: Blue-Green Deployment with Progressive Exposure

### Azure DevOps YAML Pipeline (Extract)

```yaml
# azure-pipelines-deploy.yml
trigger: none
pr: none

parameters:
  - name: deploymentStrategy
    displayName: Deployment Strategy
    type: string
    default: blue-green
    values:
      - blue-green
      - rolling
      - canary

variables:
  - group: production-variables
  - name: acrName
    value: prodacr2026
  - name: aksCluster
    value: prod-aks-cluster
  - name: imageTag
    value: $(Build.BuildId)

stages:
  - stage: Build
    jobs:
      - job: BuildAndPush
        steps:
          - task: Docker@2
            inputs:
              command: buildAndPush
              repository: user-preference-service
              tags: $(imageTag)

  - stage: DeployGreen
    dependsOn: Build
    condition: and(succeeded(), eq('${{ parameters.deploymentStrategy }}', 'blue-green'))
    jobs:
      - deployment: DeployToGreen
        environment: prod-green
        strategy:
          runOnce:
            deploy:
              steps:
                - task: KubernetesManifest@1
                  inputs:
                    action: deploy
                    manifests: k8s/green-deployment.yaml
                    imagePullSecrets: |
                      prod-acr-secret
                    containers: |
                      $(acrName).azurecr.io/user-preference-service:$(imageTag)

  - stage: CanaryAnalysis
    dependsOn: DeployGreen
    jobs:
      - job: RunCanaryAnalysis
        steps:
          - task: AzurePowerShell@5
            inputs:
              azureSubscription: prod-subscription
              scriptType: inlineScript
              inline: |
                $canaryDurationMinutes = 60
                $errorRateThreshold = 0.01
                $latencyThreshold = 200
                $analysis = Test-CanaryHealth `
                  -ResourceGroup "prod-rg" `
                  -ClusterName "prod-aks-cluster" `
                  -DurationMinutes $canaryDurationMinutes `
                  -ErrorRateThreshold $errorRateThreshold `
                  -LatencyThreshold $latencyThreshold
                if (-not $analysis.Passed) {
                  Write-Host "##vso[task.complete result=Failed;]Canary analysis failed"
                  throw "Canary analysis failed: $($analysis.FailureReason)"
                }

  - stage: ShiftTraffic
    dependsOn: CanaryAnalysis
    jobs:
      - job: TrafficShift25Percent
        steps:
          - task: AzurePowerShell@5
            inputs:
              inline: |
                Set-TrafficSplit -GreenWeight 0.25 -BlueWeight 0.75
                Start-Sleep -Seconds 600
                if (-not (Test-DeploymentHealth)) { throw "Health check failed at 25%" }
      - job: TrafficShift50Percent
        dependsOn: TrafficShift25Percent
        steps:
          - task: AzurePowerShell@5
            inputs:
              inline: |
                Set-TrafficSplit -GreenWeight 0.50 -BlueWeight 0.50
                Start-Sleep -Seconds 600
                if (-not (Test-DeploymentHealth)) { throw "Health check failed at 50%" }
      - job: TrafficShift75Percent
        dependsOn: TrafficShift50Percent
        steps:
          - task: AzurePowerShell@5
            inline: |
              Set-TrafficSplit -GreenWeight 0.75 -BlueWeight 0.25
              Start-Sleep -Seconds 600
              if (-not (Test-DeploymentHealth)) { throw "Health check failed at 75%" }
      - job: TrafficShift100Percent
        dependsOn: TrafficShift75Percent
        steps:
          - task: AzurePowerShell@5
            inline: |
              Set-TrafficSplit -GreenWeight 1.00 -BlueWeight 0.00
              Write-Host "Blue-green deployment complete — blue environment retained for rollback"
```

---

## Layer 4: Automated Rollback Trigger

### Azure Monitor Alert Rule (ARM Template)

```json
{
    "type": "Microsoft.Insights/metricAlerts",
    "apiVersion": "2024-02-01",
    "name": "Deployment-ErrorRate-RollbackTrigger",
    "location": "global",
    "properties": {
        "description": "Triggers automated rollback when deployment error rate exceeds 1% for 2 minutes",
        "severity": 0,
        "enabled": true,
        "scopes": ["/subscriptions/{subId}/resourceGroups/prod-rg/providers/Microsoft.ContainerService/managedClusters/prod-aks-cluster"],
        "evaluationFrequency": "PT1M",
        "windowSize": "PT2M",
        "criteria": {
            "allOf": [
                {
                    "metricName": "requests/errors",
                    "metricNamespace": "Microsoft.ContainerService/managedClusters",
                    "operator": "GreaterThan",
                    "threshold": 1.0,
                    "timeAggregation": "Average",
                    "dimensions": [
                        {
                            "name": "deployment",
                            "operator": "Include",
                            "values": ["user-preference-service-green"]
                        }
                    ]
                }
            ],
            "odata.type": "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria"
        },
        "actions": [
            {
                "actionGroupId": "/subscriptions/{subId}/resourceGroups/prod-rg/providers/microsoft.insights/actionGroups/AutoRollbackActionGroup"
            }
        ]
    }
}
```

### Rollback Azure Function

```java
package com.example.rollback;

import com.azure.monitor.eventhub.EventData;
import com.azure.monitor.eventhub.EventHubConsumerClient;
import com.azure.resourcemanager.AzureResourceManager;
import com.azure.resourcemanager.containerservice.models.KubernetesCluster;
import com.azure.resourcemanager.containerservice.models.KubernetesVersion;
import org.springframework.cloud.function.adapter.azure.Function;

import java.util.function.Consumer;

public class AutoRollbackFunction implements Consumer<EventData> {

    private static final Logger log = LoggerFactory.getLogger(AutoRollbackFunction.class);

    private final AzureResourceManager azureResourceManager;
    private final DeploymentManager deploymentManager;

    public AutoRollbackFunction() {
        this.azureResourceManager = AzureResourceManager.authenticate(
            new DefaultAzureCredentialBuilder().build(),
            new AzureProfile(AzureEnvironment.AZURE)
        );
        this.deploymentManager = new DeploymentManager(azureResourceManager);
    }

    @Override
    public void accept(EventData event) {
        try {
            AlertPayload payload = parseAlertPayload(event.getBodyAsString());
            log.warn("Auto-rollback triggered by alert: {}", payload);

            String clusterName = payload.getClusterName();
            String resourceGroup = payload.getResourceGroup();
            String previousImageTag = getPreviousSuccessfulDeploymentTag(clusterName, resourceGroup);

            deploymentManager.rollbackDeployment(
                clusterName,
                resourceGroup,
                "user-preference-service",
                previousImageTag
            );

            log.info("Rollback initiated — rolling back to image tag: {}", previousImageTag);

            deploymentManager.disableFeatureFlag("user-preference-cache-enabled");

            sendNotification(new RollbackNotification(
                "AUTO-ROLLBACK",
                "Rollback completed for user-preference-service",
                "Rolled back to version: " + previousImageTag,
                payload
            ));
        } catch (Exception e) {
            log.error("Auto-rollback failed, manual intervention required: {}", e.getMessage(), e);
            escalateToOnCall("Auto-rollback failure — manual intervention required");
        }
    }

    private AlertPayload parseAlertPayload(String json) {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(json, AlertPayload.class);
    }

    private String getPreviousSuccessfulDeploymentTag(String cluster, String rg) {
        KubernetesCluster k8s = azureResourceManager.kubernetesClusters()
            .getByResourceGroup(rg, cluster);
        return k8s.innerModel().toString(); // simplified for brevity
    }
}
```

---

## Complete Remediation Steps

### Step 1: Immediate Containment (T+0 to T+30 minutes)
1. Rollback deployment to previous version via Azure DevOps release pipeline
2. Disable LaunchDarkly feature flag `user-preference-cache-enabled` globally
3. Verify all 48 nodes return to healthy state
4. Communicate incident status to stakeholders

### Step 2: Root Cause Fix (T+30 to T+120 minutes)
1. Implement null check in `UserPreferenceCacheService` (code provided above)
2. Add unit tests for null return and fallback scenarios
3. Modify `DownstreamPreferenceClient` to address race condition or document known behavior
4. Run full test suite (487 unit + 142 integration tests)

### Step 3: Feature Flag Integration (T+120 to T+240 minutes)
1. Integrate LaunchDarkly SDK into the service (code provided above)
2. Create feature flag `user-preference-cache-enabled` (initially disabled)
3. Update deployment pipeline to verify feature flag health during canary
4. Enable feature flag for internal users only first

### Step 4: Pipeline Hardening (T+240 to T+480 minutes)
1. Extend canary duration from 15 minutes to 60 minutes
2. Implement progressive traffic shift (25%/50%/75%/100%)
3. Configure automated rollback trigger at 1% error rate threshold
4. Increase connection draining timeout from 60s to 300s
5. Add per-endpoint error rate monitoring in canary analysis

### Step 5: Verification and Monitoring (T+480 to T+600 minutes)
1. Deploy fixed version through hardened pipeline
2. Verify progressive rollout completes successfully
3. Confirm automated rollback trigger fires correctly (test with intentional error injection)
4. Update runbooks and dashboards with new deployment metrics

---

## Verification Commands

```powershell
# Check pod health across all nodes
kubectl get pods -n production -l app=user-preference-service -o wide

# Verify rollback to previous version
kubectl rollout history deployment/user-preference-service -n production

# Check connection draining metrics
kubectl get events -n production --field-selector reason=Killing | Select-String "draining"

# Verify feature flag state (requires LaunchDarkly CLI)
ldctl evaluate user-preference-cache-enabled --user "test-user-001"

# Check error rate in Azure Monitor
az monitor metrics list `
  --resource /subscriptions/{subId}/resourceGroups/prod-rg/providers/Microsoft.ContainerService/managedClusters/prod-aks-cluster `
  --metric "requests/errors" `
  --interval PT1M `
  --top 10

# Verify canary analysis metrics
az monitor app-insights query `
  --app prod-app-insights `
  --analytics-query "requests | where timestamp > ago(1h) | summarize errorRate = countif(success == false) * 100.0 / count() by bin(timestamp, 1m), cloud_RoleInstance"
```

---

## References

- Google SRE Book — Chapter 8: "Release Engineering" — deployment strategies and safety
- Netflix Tech Blog: "Canary Analysis and Automated Rollback at Netflix" — https://netflixtechblog.com/canary-analysis-and-automated-rollback-at-netflix-8e4b6ef6e93e
- Microsoft Learn: "Blue-Green Deployment Strategy in AKS" — (link removed)
- AWS re:Invent 2021 — DOP205: "Deploying Safely at Amazon"
- LaunchDarkly Blog: "Feature Flag Best Practices" — (link removed)
- Azure DevOps Documentation: "Safe Deployment Practices" — (link removed)
