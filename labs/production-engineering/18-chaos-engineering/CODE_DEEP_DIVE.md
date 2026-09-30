# CODE DEEP DIVE: Chaos Engineering & Fault Injection Patterns
## Lab 18 | Production Engineering Academy

---

## Pattern 1: Kubernetes Chaos Mesh Network Latency Injection Manifest

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: payment-latency-injection
  namespace: production
spec:
  action: delay
  mode: fixed
  value: '2' # Inject into exactly 2 pods
  selector:
    namespaces:
      - production
    labelSelectors:
      app: payment-service
  delay:
    latency: '1500ms' # 1.5 second latency
    jitter: '200ms'
    correlation: '50'
  duration: '5m' # Self-terminating safety timer (Dead man's switch)
  scheduler:
    cron: '@daily'
```

---

## Pattern 2: Chaos Monkey for Spring Boot Dynamic Endpoint Configuration

```java
package com.learning.production.lab18;

import de.codecentric.spring.boot.chaos.monkey.configuration.AssaultProperties;
import de.codecentric.spring.boot.chaos.monkey.configuration.ChaosMonkeySettings;
import org.springframework.boot.actuate.endpoint.annotation.Endpoint;
import org.springframework.boot.actuate.endpoint.annotation.WriteOperation;
import org.springframework.stereotype.Component;

@Component
@Endpoint(id = "chaos-controller")
public class DynamicChaosController {

    private final ChaosMonkeySettings settings;

    public DynamicChaosController(ChaosMonkeySettings settings) {
        this.settings = settings;
    }

    /**
     * Programmatically enable latency chaos on Spring service beans with automatic expiration.
     */
    @WriteOperation
    public String injectLatencyChaos(int latencyMs, int durationSeconds) {
        AssaultProperties assaults = settings.getAssaultProperties();
        assaults.setLatencyActive(true);
        assaults.setLatencyRangeStart(latencyMs);
        assaults.setLatencyRangeEnd(latencyMs + 500);
        assaults.setLevel(5); // 5 out of 10 requests assaulted

        // Automatic self-healing safety timer: disable chaos after duration
        Thread.ofVirtual().start(() -> {
            try {
                Thread.sleep(durationSeconds * 1000L);
            } catch (InterruptedException ignored) {}
            assaults.setLatencyActive(false);
        });

        return String.format("CHAOS INJECTED: %dms latency for %ds. Safety auto-reset armed.", latencyMs, durationSeconds);
    }
}
```
