# PRODUCTION SCENARIOS: Java in Kubernetes & Containers
## Lab 07 | Production Engineering Academy

---

## Scenario 1: The Zero-Downtime Rolling Deployment 502 Nightmare

### Context
E-commerce checkout API deployed on Kubernetes. Every time the team deployed a new release via `kubectl rollout restart`, Grafana dashboards lit up with 1,500+ HTTP 502 Bad Gateway errors.

### The Mystery
Readiness probes and liveness probes were configured correctly. Rolling update strategy had `maxUnavailable: 0` and `maxSurge: 25%`. Why were 502s occurring during container termination?

### Root Cause
1. Kubernetes sends `SIGTERM` to the container at the exact same moment it updates the Service endpoint list.
2. It takes 1.5 to 3.0 seconds for kube-proxy, CoreDNS, and AWS ALB Ingress controller to propagate the removal of the pod IP address from the routing table.
3. Spring Boot received `SIGTERM` and closed its Netty/Tomcat listening socket within 100 milliseconds.
4. For the next 2 seconds, the Ingress controller continued routing active client checkout requests to the terminated pod's closed port, resulting in immediate TCP `RST` packets and HTTP 502 errors.

### The Production Fix
```yaml
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]
```
And in `application.yml`:
```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```
During the 15-second `preStop` sleep, Kubernetes marks the pod as `Terminating` and removes it from all load balancer endpoints. No new requests arrive. Once the sleep ends, Spring Boot drains existing in-flight connections cleanly. 502 errors dropped to zero.

---

## Scenario 2: The Startup Probe Death Loop

### Context
A massive legacy Spring Boot service with 1,200 `@Component` beans, database migrations via Flyway, and Hibernate schema validation.

### Failure Mode
- Startup took 65 seconds on a busy Kubernetes node.
- Liveness probe had: `initialDelaySeconds: 30`, `periodSeconds: 10`, `failureThreshold: 3`.
- At $t=30\text{s}$, the liveness probe began firing. Spring Boot was still running Flyway migrations, returning connection refused.
- At $t=60\text{s}$ (3 failures), the kubelet concluded the pod was deadlocked and issued a `SIGKILL` restart!
- The pod was stuck in an infinite `CrashLoopBackOff`, restarting perpetually before it could finish starting up.

### The Fix: Dedicated `startupProbe`
```yaml
startupProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  failureThreshold: 30
  periodSeconds: 5  # Gives up to 150 seconds to start
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  periodSeconds: 10
  failureThreshold: 3
```
The liveness probe does not engage until the `startupProbe` passes for the first time.
