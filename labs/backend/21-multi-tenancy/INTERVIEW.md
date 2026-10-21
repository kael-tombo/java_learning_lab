# Interview: Multi-Tenancy

Q: Compare multi-tenant patterns? A: DB-per-tenant (best isolation, most resources), Schema-per-tenant (good isolation, shared pool), Discriminator (simplest, least isolation).

Q: How to propagate tenant context to async tasks? A: Use ThreadLocal with @Async decorator or propagate via Mapped Diagnostic Context (MDC).

Q: How to test tenant isolation? A: Create integration tests that run same operation as different tenants and verify data separation.
