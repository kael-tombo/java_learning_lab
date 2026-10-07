# Real-World Project — Shop Service (Catalog + Orders + Auth)

## Problem
Production shop slice: catalog search, order placement with tx, JWT auth, observable.

## Architecture
```
Client → JAX-RS (catalog, orders) → CDI services → JPA (Postgres)
  → messaging (order events) → health/metrics/tracing
Auth: OIDC/JWT; Config: env; DB pool 20;pool timeout 5s
```

## Milestones
1. **M1 Catalog**: entities + search (ILIKE + pagination), OpenAPI published.
2. **M2 Orders**: tx placement (stock decrement + order insert atomic), idempotency key.
3. **M3 Security**: JWT roles customer/admin; `@RolesAllowed` + 401/403 tests.
4. **M4 Resilience**: @Retry/@Timeout on payment client; DLQ for failed events.
5. **M5 Ops**: Docker + K8s (probes, HPA), Grafana (RPS/p99/DB pool), alert tx rollback spike.

## Key Config
```properties
quarkus.datasource.jdbc.max-size=20
quarkus.http.port=8080
mp.jwt.verify.publickey.location=public.pem
```
Run: `java -Xmx512m -jar shop-runner.jar` or `docker run -p 8080:8080 shop:1.0`.

## Testing
- Contract: Postman/newman collection green; k6 200rps p99 < 200ms.
- Chaos: DB kill → readiness DOWN, traffic shifted; no half-orders (tx test).

## Ops
- K8s 1Gi/1CPU×3, PDB 1, HPA 60% CPU; backup Postgres daily.

## Interview Angles
- Tx boundary choice? N+1 proof? JWT vs session? Idempotency design?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Jakarta EE docs: (link removed)
- Quarkus guides: https://quarkus.io/guides/
- Spring vs Jakarta comparison: https://spring.io/projects/spring-framework
