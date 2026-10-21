# How It Works: Multi-Tenancy

When a request arrives, a filter extracts the tenant ID from a header/subdomain/JWT and stores it in ThreadLocal. The tenant resolver reads this ThreadLocal for every database operation. Hibernate uses either a different DataSource (DB-per-tenant) or a different schema (schema-per-tenant) based on the tenant ID. This ensures complete data isolation without changing application code.
