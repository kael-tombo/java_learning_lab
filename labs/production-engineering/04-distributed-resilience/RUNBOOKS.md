# RUNBOOK: Distributed Systems Cascading Failure Mitigation
## Lab 04 | Production Engineering Academy

---

## RUNBOOK 01: Mitigating an Active Cascading Retry Storm

**Severity**: P1 (Catastrophic Outage)  
**Primary Indicator**: Upstream services failing with 504 Gateway Timeout; downstream services experiencing 300%+ traffic spike with 100% CPU.

### Emergency Triage Steps (T+0 to T+5 minutes):
1. **Disable Upstream Retries Dynamically**:
   Update feature flag or dynamic config (Spring Cloud Config / Consul / LaunchDarkly):
   ```bash
   # Emergency curl to actuator or config server:
   curl -X POST http://api-gateway:8080/actuator/env -d '{"name":"resilience.retry.maxAttempts","value":"1"}' -H "Content-Type: application/json"
   curl -X POST http://api-gateway:8080/actuator/refresh
   ```
2. **Apply Ingress Rate Limiting / Shed Load**:
   Throttle non-critical traffic at the API gateway or Cloudflare/Envoy layer to allow the downstream system to recover:
   ```bash
   # Shed 50% of incoming traffic at Envoy / Ingress
   kubectl apply -f /k8s/emergency-rate-limit-shed.yaml
   ```
3. **Trip Circuit Breakers Manually**:
   If an external dependency is dead and holding connections open:
   ```bash
   # Force circuit breaker OPEN to instantly fail fast with static fallback:
   curl -X POST http://order-service:8081/actuator/circuitbreakers/payment-service-cb/transition/to-open
   ```

---

## RUNBOOK 02: Resolving Downstream Network Partition / Latency Degradation

1. Verify network latency between pods:
   ```bash
   kubectl exec -it <pod-a> -- traceroute <service-b>
   kubectl exec -it <pod-a> -- curl -w "@curl-format.txt" -o /dev/null -s https://<service-b>/health
   ```
2. Check TCP retransmits and socket queue drop counts on node:
   ```bash
   netstat -s | grep -i retrans
   ss -s
   ```
3. If MTU mismatch or cloud route flap is detected, isolate the affected availability zone (AZ evacuation).
