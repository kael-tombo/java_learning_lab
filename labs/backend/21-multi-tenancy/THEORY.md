# Theory: Multi-Tenancy

## Tenancy Models

Multi-tenancy means one deployment serves many customers (tenants). The three
classic models, in increasing isolation and cost:

1. **Silo**: each tenant gets its own database (or schema). Strongest
   isolation, easiest per-tenant backup/restore, worst density. Typical for
   regulated/enterprise tiers.
2. **Pool**: all tenants share tables with a `tenant_id` column on every row.
   Best density, hardest correctness problem — every query must carry the
   tenant predicate.
3. **Bridge**: a few shared tables plus per-tenant tables, or a mix of the two
   above (e.g. small tenants pooled, large tenants siloed). Real products
   almost always end up here.

## Tenant Resolution and Context

The request must be bound to a tenant before any repository runs: resolve from
a JWT claim, a subdomain, or a header, then store it in a thread-local
`TenantContext`. Two rules make or break pool-model deployments:

- The context is cleared in a `finally`/interceptor `afterCompletion`, or a
  reused request thread leaks tenant A's id into tenant B's next request.
- Async boundaries (`@Async`, `CompletableFuture`, reactive chains) drop
  thread-locals. Either copy the tenant into the task, or use a scoped value
  (`ScopedValue` on JDK 21+) instead.

## Row-Level Isolation Mechanisms

- **Hibernate `@Filter`** or **row-level security (RLS)** in Postgres: the
  database/ORM appends `AND tenant_id = ?` automatically, so a query that
  forgets the predicate still can't leak. Hibernate's
  `CurrentTenantIdentifierResolver` + `MultiTenantConnectionProvider` push
  this down to schema selection in the silo model.
- **Tenant id in every index**: pooled tables need composite unique keys
  `(tenant_id, id)`, or tenant A's `id=7` collides with tenant B's.
- **Schema-per-tenant** (silo at schema level): `SET search_path TO tenant_42`
  per connection — pooled JDBC connections must set/reset it reliably, and
  prepared-statement caching across tenants has bitten many teams.

## Noisy Neighbor and Fairness

One tenant's 100k-row report can starve others. Mitigations: per-tenant
connection pool sizing, query timeouts, bulkheads (separate executors per
tenant tier), rate limits, and Postgres RLS combined with per-role quotas.

## Failure Modes in Production

- **Cross-tenant leak**: a native SQL report query bypasses the Hibernate
  filter — the single worst incident class in SaaS; every query path,
  including read replicas and analytics exports, needs the predicate.
- **Leaked context on async**: a `@Async` pool that inherits the caller's
  thread-local without clearing.
- **Migration skew**: silo model with per-tenant schemas — a migration that
  touches 10k schemas fails partway, leaving a fleet of different schemas;
  need per-tenant version tracking and idempotent migrations.
- **Tenant deletion**: pool model requires `DELETE ... WHERE tenant_id` sweeps
  plus vacuum strategy; silo model is a `DROP DATABASE` but backups must
  confirm the right one.
- **Cache key collision**: Redis keys without tenant prefix, so one tenant
  reads another's cached entity.

## References

- Microsoft SaaS Tenant Isolation decision guide
- Hibernate ORM User Guide, "Multitenancy" chapter
