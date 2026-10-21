# Performance: Multi-Tenancy

- Database-per-tenant: Separate connection pools per tenant, no shared contention
- Schema-per-tenant: Shared connection pool, schema switching overhead
- Discriminator: Single connection pool, all data shares resources
- Monitor connection pool size per tenant
- Cache tenant-specific data separately
- Consider read replicas for reporting tenants
