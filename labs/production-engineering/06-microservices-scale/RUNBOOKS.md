# RUNBOOK: Microservices Traffic & Service Discovery Incidents
## Lab 06 | Production Engineering Academy

---

## RUNBOOK 01: Service Imbalance / Hot-Spotting Pod

**Severity**: P2  
**Symptom**: Out of 20 pods in a service deployment, 1 pod has 90% CPU and handles 80% of traffic, while 19 pods are idle.

### Diagnostic Steps
1. Verify pod distribution across target endpoints:
   ```bash
   kubectl get endpoints <service-name> -o wide
   ```
2. Check caller client keep-alive and connection reuse:
   - If callers use HTTP/2 or gRPC behind a standard Kubernetes L4 Service (`ClusterIP`), TCP connections are established once and persist indefinitely.
   - New pods joining the deployment receive ZERO traffic because old connections remain open to old pods.

### Immediate Mitigation
1. **Force Connection Rebalancing on Server**:
   Configure `maxConnectionAge` on the gRPC/Netty server so servers gracefully close long-lived connections after e.g. 5 minutes:
   ```java
   NettyServerBuilder.forPort(50051)
       .maxConnectionAge(5, TimeUnit.MINUTES)
       .maxConnectionAgeGrace(30, TimeUnit.SECONDS)
       .build();
   ```
2. **Temporary Emergency Pod Rolling Restart**:
   ```bash
   kubectl rollout restart deployment/<caller-service>
   ```

---

## RUNBOOK 02: Envoy / Istio Sidecar Out of Memory (OOMKill)

### Symptom
Application pod crashes with Exit Code 137. `kubectl describe pod` shows `OOMKilled` on `istio-proxy` / `envoy` container, not the Java container.

### Mitigation
1. Filter out unnecessary service discovery endpoints:
   By default, Istio pushes all cluster endpoints to every sidecar. Use `Sidecar` resource to restrict egress visibility:
   ```yaml
   apiVersion: networking.istio.io/v1alpha3
   kind: Sidecar
   metadata:
     name: default
     namespace: payments
   spec:
     egress:
       - hosts:
           - "./*"
           - "istio-system/*"
           - "orders/*"
   ```
2. Bump Envoy memory limit from default 256Mi to 512Mi.
