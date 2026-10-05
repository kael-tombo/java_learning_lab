# REAL WORLD PROJECT — Lab 07: Cascade War-Room

## 1. War-Room Timeline (94-min SEV1)
| T | Event | Owner |
|---|---|---|
| T+0 | payment p99 50ms→5s (pool exhaustion downstream) | Monitor |
| T+2 | order threads 20/20 blocked; breaker CLOSED | Ops |
| T+5 | Gateway queuing; 8 services impacted | IC declares SEV1 |
| T+9 | Page: multi-service 78% errors | SRE |
| T+12 | Trace pins payment leaf; force-open payment breaker | Ops |
| T+30 | Pools drained; fallbacks serving queued-review | Feature |
| T+45 | Sick pool fixed; half-open probes succeed | DB/SRE |
| T+94 | All 15 healthy; CLOSED everywhere | IC closes |

## 2. Triage Runbook
1. Traces → slowest leaf. 2. `breaker state` per edge — CLOSED-on-sick = misconfig.
3. Force-open sick edge; cut retries to 1 upstream. 4. Drain + scale edge. 5. Fix leaf, half-open verify.

## 3. Commands
```bash
curl -s localhost:8080/actuator/circuitbreakers | jq .
curl -X POST localhost:8080/actuator/circuitbreakers/payment/force-open
kubectl logs -l app=order-service --tail=200 | grep -E "Timeout|Bulkhead|fallback"
```

## 4. Metrics of Recovery
- Breaker payment: OPEN→HALF→CLOSED; fallback rate 90%→<1%.
- Pool active <50%; p99 <500ms; errors <0.5% for 15 min.

## 5. Comms Template
> SEV1 cascade from payment latency. Breaker forced open, fallbacks on. ETA 30 min. Next :15. Bridge <link>.

## 6. Prevention
- Threshold 50/window 20/timeout 3s/bulkhead-per-dep/skip-if-OPEN standard; review gate blocks merges without fallback; monthly chaos slow-dep drill.

## 7. Cost Template
2.1M failed × conv-loss + $120k/h × 1.5h ≈ $180k+ direct.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Resilience4j circuit breaker + bulkhead guides: https://resilience4j.readme.io/docs/circuitbreaker
- Azure Circuit Breaker pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- Kubernetes service scaling during incidents: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
