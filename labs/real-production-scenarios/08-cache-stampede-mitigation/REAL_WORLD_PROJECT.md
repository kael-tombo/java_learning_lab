# REAL WORLD PROJECT — Lab 08: Stampede War-Room

## 1. War-Room Timeline
| T | Event | Owner |
|---|---|---|
| T+0 | Hot-key TTL mass expiry (flash sale) | — |
| T+1 | Hit 98→38%, misses 6k/s, DB pool 198/200 | Monitor pages |
| T+5 | IC SEV2; traces show same SELECT | SRE |
| T+8 | Enable stale-serve + singleflight flag | Ops |
| T+15 | Jitter deploy + fill cap 10; DB draining | Feature |
| T+25 | Hit back 96%, p95 normal | IC closes |

## 2. Triage Runbook
1. Name hot key (log agg). 2. Serve stale immediately. 3. Coalesce fills. 4. Cap fill concurrency. 5. Jitter TTLs; prewarm after.

## 3. Commands
```bash
redis-cli INFO stats | grep -E "hits|misses|expired"
redis-cli SLOWLOG GET 10
kubectl logs -l app=catalog --tail=500 | grep -oE "product:[0-9]+" | sort | uniq -c | sort -rn | head
curl -s localhost:8080/actuator/metrics/cache.hit.ratio | jq .
```

## 4. Metrics of Recovery
- Hit >95% 10 min; misses/s baseline; DB conns <50%; p95 ±10%.

## 5. Comms Template
> SEV2 stampede on product:88412. Stale-serve on, fills coalesced. ETA 15 min. Next :15.

## 6. Prevention
- Jitter all TTLs, singleflight standard, SWR for hot tier, miss-storm alerts, expiry-minute load tests, no FLUSHDB without warm-up.

## 7. Cost Template
Timeouts × conversion loss + DB scale-up + eng time; budget burn computed from error % × duration.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Redis persistence/latency and `INFO`/`SLOWLOG` reference: https://redis.io/docs/latest/commands/info/
- Kubernetes scaling under load: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- OWASP caching/DoS considerations: https://owasp.org/www-community/attacks/Denial_of_Service
