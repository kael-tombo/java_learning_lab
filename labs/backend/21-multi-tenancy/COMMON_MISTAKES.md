# Common Mistakes: Multi-Tenancy

1. Tenant ID not propagated to async operations
2. Forgetting to clear ThreadLocal (memory leak)
3. Missing tenant filter in middleware calls
4. Cross-tenant data leak in shared tables (discriminator)
5. Not testing tenant isolation
6. Slow tenant resolution (DNS lookups per request)
7. Inconsistent tenant ID format across services
