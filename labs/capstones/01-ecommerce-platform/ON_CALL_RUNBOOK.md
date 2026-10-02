# On-Call Runbook: E-Commerce Platform (Capstone 01)

> Scope: `OrderService`, `PaymentService`, `InventoryService`, `CatalogService`, `CartService`, `UserService`, `NotificationService`.
> Audience: on-call engineer for a team running this Java e-commerce platform in production.

## 1. Service Map & SLOs

| Component | SLO | Key Signal |
|---|---|---|
| `OrderService.createOrder` | p95 latency < 500 ms, error rate < 0.1% | HTTP 5xx rate, order queue depth |
| `PaymentService.charge` | p99 latency < 2 s, error rate < 0.05% | Payment gateway latency, decline rate |
| `InventoryService.reserve` | p95 latency < 200 ms, error rate < 0.1% | Reservation conflict rate, stock levels |
| `CatalogService.search` | p95 latency < 300 ms, error rate < 0.2% | Search index freshness, result relevance |
| `CartService` | p95 latency < 100 ms, availability 99.99% | Cart abandonment rate, session errors |
| `NotificationService` | Delivery < 30 s, success rate > 99% | Email/SMS queue depth, bounce rate |

## 2. Triage Decision Tree (first 5 minutes)

```
checkout failing or slow?
├─ YES → §3 Checkout Incident
├─ NO → payments failing?
│   ├─ YES → §4 Payment Processing Incident
│   └─ NO → inventory issues?
│       ├─ YES → §5 Inventory Sync Incident
│       └─ NO → search/catalog broken?
│           ├─ YES → §6 Catalog Search Degradation
│           └─ NO → check notifications → §7
```

Always note: affected service versions, recent deployments, feature flags, traffic patterns.

## 3. Runbook: Checkout Failures / Latency Spikes

**Symptoms:** `OrderService` 5xx spike, order queue backing up, `CartService` timeouts, user complaints.

**Diagnose (0–10 min):**
1. Check `OrderService` logs for exceptions: `InventoryReservationException`, `PaymentGatewayTimeout`, `ConcurrencyConflict`.
2. Check downstream dependencies: `InventoryService.reserve` latency, `PaymentService.charge` latency, `CatalogService` availability.
3. Verify database connection pool health (HikariCP metrics: active/idle/pending connections).
4. Check for distributed lock contention (Redis/ZooKeeper) on order ID or user ID.
5. Look for circuit breaker OPEN state on any downstream client.

**Mitigate (10–20 min):**
- If `InventoryService` slow: increase reservation timeout, enable async reservation with compensation.
- If `PaymentService` slow: fail fast with user-friendly message, queue payment for async retry.
- If database pool exhausted: scale read replicas, kill long-running queries, increase pool size temporarily.
- If lock contention: reduce lock granularity, add jitter to retry logic.
- **Do NOT:** disable inventory checks, process payments synchronously during incident, skip idempotency checks.

## 4. Runbook: Payment Processing Incidents

**Symptoms:** High payment decline rate, gateway timeouts, webhook delivery failures, reconciliation mismatches.

**Diagnose:**
1. Check payment gateway status page / API health endpoint.
2. Review `PaymentService` logs for: `GatewayTimeout`, `InvalidSignature`, `InsufficientFunds`, `FraudRejection`.
3. Verify webhook endpoint accessibility and idempotency key handling.
4. Check for duplicate charge attempts (idempotency key collision).

**Mitigate:**
- Gateway degraded: enable fallback gateway (if configured), increase timeout, queue for retry.
- Webhook failures: ensure idempotency, replay from DLQ after gateway recovery.
- Fraud spike: coordinate with fraud team, adjust rules temporarily, monitor false positive rate.
- Reconciliation drift: pause settlements, run reconciliation job, manual review for discrepancies.

## 5. Runbook: Inventory Sync / Reservation Issues

**Symptoms:** Overselling (negative stock), reservation timeouts, stuck reservations, catalog showing wrong availability.

**Diagnose:**
1. Check `InventoryService` reservation conflict metrics.
2. Compare `reserved_quantity` vs `available_quantity` in DB for hot SKUs.
3. Look for abandoned carts not releasing reservations (TTL expiry check).
4. Verify CDC / event pipeline from order → inventory is current.

**Mitigate:**
- Overselling detected: halt sales for affected SKUs, enable backorder mode, notify customers.
- Stuck reservations: run reservation cleanup job (expire > 30 min), force-release orphaned reservations.
- Catalog stale: trigger full re-index, invalidate CDN cache, check event processing lag.

## 6. Runbook: Catalog Search Degradation

**Symptoms:** Search latency spike, empty results, stale facets, relevance complaints.

**Diagnose:**
1. Check search cluster health (Elasticsearch/OpenSearch): cluster status, shard allocation, JVM heap.
2. Verify index freshness: last successful rebuild timestamp, incremental update lag.
3. Check query complexity: wildcard prefixes, deep pagination, expensive aggregations.
4. Look for hot shards or uneven distribution.

**Mitigate:**
- Latency spike: scale search nodes, enable query caching, reduce result size, disable heavy aggregations.
- Stale data: trigger incremental sync, check message queue lag (Kafka → indexer).
- Relevance issues: A/B test ranking changes, check synonym/analyzer config.

## 7. Runbook: Notification Delivery Failures

**Symptoms:** Email/SMS queue backup, bounce/spam complaints, template rendering errors.

**Diagnose:**
1. Check provider API status (SendGrid, Twilio, etc.).
2. Review `NotificationService` DLQ for failed deliveries.
3. Verify template variables and localization keys.

**Mitigate:**
- Provider outage: queue locally, retry with exponential backoff, alert if queue > threshold.
- High bounce rate: suppress bouncing addresses, verify list hygiene.
- Template errors: rollback template deploy, validate in staging.

## 8. Post-Incident Checklist

- [ ] Timeline captured with timestamps (detection, triage, mitigation, resolution)
- [ ] Affected orders/customers identified and notified
- [ ] Revenue impact estimated
- [ ] Root cause documented with "5 Whys"
- [ ] Action items: code fix, config change, capacity increase, monitoring improvement
- [ ] Runbook updated if gaps found
- [ ] Post-mortem scheduled within 5 business days

## 9. Key Dashboards & Alerts

| Dashboard | Purpose |
|---|---|
| E-Commerce Golden Signals | Request rate, error rate, latency, saturation (RED) |
| Order Funnel | Cart → Checkout → Payment → Confirmation conversion |
| Inventory Health | Stock levels, reservation rates, oversell incidents |
| Payment Gateway | Success rate, latency, decline codes, settlement lag |
| Search Cluster | Query latency, index freshness, cluster health |

## 10. Useful Commands

```bash
# Check order processing lag
kubectl exec -it order-service -- jcmd <pid> JFR.dump name=1

# Inspect inventory reservations for a SKU
kubectl exec -it inventory-service -- psql -c "SELECT * FROM reservations WHERE sku='ABC123' AND expires_at > NOW();"

# View payment gateway circuit breaker state
kubectl exec -it payment-service -- curl localhost:8080/actuator/circuitbreakers

# Check search index lag
curl -s elasticsearch:9200/_cat/indices?v | grep catalog
```