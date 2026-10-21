# Internals: Multi-Tenancy

## Hibernate MultiTenancyStrategy
Three strategies:
- NONE: No multi-tenancy (default)
- SCHEMA: Different schemas in same DB
- DATABASE: Different physical databases
- DISCRIMINATOR: Same table with tenant column

## Connection Provider
For DATABASE strategy, AbstractDataSourceBasedMultiTenantConnectionProviderImpl maintains a Map<String, DataSource>. Each tenant DataSource has its own HikariCP pool.
