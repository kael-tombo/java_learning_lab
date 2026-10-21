# Mathematical Foundation: Multi-Tenancy

## Cost Analysis
Cost(N) = infra_cost + per_tenant_cost * N * isolation_factor
- DB-per-tenant: isolation_factor = 1.0 (maximum cost)
- Schema-per-tenant: isolation_factor = 0.3 (shared connection pool)
- Discriminator: isolation_factor = 0.1 (fully shared)

## Isolation Risk
P(data_leak) = 1 - product(isolation_effectiveness of each layer)
Database-per-tenant with network isolation: P(leak) â‰ˆ 0
Discriminator with single WHERE clause: P(leak) â‰ˆ P(developer mistake)
